"""Tests for PlanExecutionLoop + PlanStabilizationInjector (CAPE sub-phase 136-d).

TDD RED phase — imports fail until implementation exists.
"""
import os
import tempfile

import pytest
import yaml

from cortex.orchestrators.core.plan_execution_loop import PlanExecutionLoop
from cortex.orchestrators.domain.plan_stabilization_injector import (
    PlanStabilizationInjector,
)


# ---------------------------------------------------------------------------
# PlanExecutionLoop — topological ordering
# ---------------------------------------------------------------------------

class TestPlanExecutionLoopTopological:

    def test_topological_order_linear(self) -> None:
        """A depends on B depends on C → order is [C, B, A]."""
        loop = PlanExecutionLoop()
        phases = [
            {"id": "A", "depends_on": ["B"]},
            {"id": "B", "depends_on": ["C"]},
            {"id": "C", "depends_on": []},
        ]
        order = loop.topological_order(phases)
        assert order.index("C") < order.index("B") < order.index("A")

    def test_topological_order_diamond(self) -> None:
        """A depends on B and C; B and C both depend on D → D first, A last."""
        loop = PlanExecutionLoop()
        phases = [
            {"id": "A", "depends_on": ["B", "C"]},
            {"id": "B", "depends_on": ["D"]},
            {"id": "C", "depends_on": ["D"]},
            {"id": "D", "depends_on": []},
        ]
        order = loop.topological_order(phases)
        assert order[0] == "D"
        assert order[-1] == "A"

    def test_topological_order_cycle_detected(self) -> None:
        """Circular depends_on must raise ValueError."""
        loop = PlanExecutionLoop()
        phases = [
            {"id": "A", "depends_on": ["B"]},
            {"id": "B", "depends_on": ["A"]},
        ]
        with pytest.raises(ValueError, match="[Cc]ycl"):
            loop.topological_order(phases)

    def test_topological_order_no_deps(self) -> None:
        """Phases with no deps can be in any order."""
        loop = PlanExecutionLoop()
        phases = [
            {"id": "X", "depends_on": []},
            {"id": "Y", "depends_on": []},
        ]
        order = loop.topological_order(phases)
        assert set(order) == {"X", "Y"}
        assert len(order) == 2


# ---------------------------------------------------------------------------
# PlanExecutionLoop — has_plan / should_continue
# ---------------------------------------------------------------------------

class TestPlanExecutionLoopControl:

    def test_has_plan_true(self) -> None:
        loop = PlanExecutionLoop()
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            f.write(b"id: test\n")
            path = f.name
        try:
            assert loop.has_plan(path) is True
        finally:
            os.unlink(path)

    def test_has_plan_false(self) -> None:
        loop = PlanExecutionLoop()
        assert loop.has_plan("/nonexistent/path/phase.yaml") is False

    def test_should_continue_halt_policy(self) -> None:
        loop = PlanExecutionLoop()
        assert loop.should_continue(gate_passed=False, policy="HALT") is False

    def test_should_continue_continue_policy(self) -> None:
        loop = PlanExecutionLoop()
        assert loop.should_continue(gate_passed=False, policy="CONTINUE") is True

    def test_should_continue_gate_passed_always_continues(self) -> None:
        loop = PlanExecutionLoop()
        assert loop.should_continue(gate_passed=True, policy="HALT") is True


# ---------------------------------------------------------------------------
# PlanExecutionLoop — move_to_completed
# ---------------------------------------------------------------------------

class TestPlanExecutionLoopMoveToCompleted:

    def test_move_to_completed_updates_status(self) -> None:
        loop = PlanExecutionLoop()
        with tempfile.TemporaryDirectory() as tmpdir:
            planned = os.path.join(tmpdir, "planned")
            completed = os.path.join(tmpdir, "completed")
            os.makedirs(planned)
            os.makedirs(completed)

            src = os.path.join(planned, "phase-test.yaml")
            with open(src, "w") as f:
                f.write("id: phase-test\nstatus: PLANNED\ntitle: Test\n")

            dest = loop.move_to_completed(src_path=src, completed_dir=completed)
            assert os.path.isfile(dest)
            assert not os.path.isfile(src)

            with open(dest) as f:
                data = yaml.safe_load(f)
            assert data["status"] == "COMPLETE"


# ---------------------------------------------------------------------------
# PlanStabilizationInjector
# ---------------------------------------------------------------------------

class TestPlanStabilizationInjector:

    @pytest.fixture()
    def injector(self) -> PlanStabilizationInjector:
        return PlanStabilizationInjector()

    @pytest.fixture()
    def sample_phases(self) -> list:
        return [
            {"id": "ph-a", "title": "Phase A", "depends_on": []},
            {"id": "ph-b", "title": "Phase B", "depends_on": ["ph-a"]},
        ]

    def test_inject_stabilization_adds_cleanup(
        self, injector: PlanStabilizationInjector, sample_phases: list
    ) -> None:
        result = injector.inject_stabilization(sample_phases)
        cleanup_phases = [p for p in result if "cleanup" in p["id"]]
        # one cleanup sub-phase per implementation phase
        assert len(cleanup_phases) >= len(sample_phases)

    def test_inject_stabilization_adds_holistic_final(
        self, injector: PlanStabilizationInjector, sample_phases: list
    ) -> None:
        result = injector.inject_stabilization(sample_phases)
        holistic_phases = [p for p in result if "holistic" in p["id"]]
        assert len(holistic_phases) == 1

    def test_holistic_stabilization_depends_on_all(
        self, injector: PlanStabilizationInjector, sample_phases: list
    ) -> None:
        result = injector.inject_stabilization(sample_phases)
        holistic = next(p for p in result if "holistic" in p["id"])
        # holistic phase depends_on all predecessor IDs
        predecessor_ids = {p["id"] for p in result if "holistic" not in p["id"]}
        for pid in predecessor_ids:
            assert pid in holistic["depends_on"]

    def test_holistic_stabilization_has_9_checks(
        self, injector: PlanStabilizationInjector, sample_phases: list
    ) -> None:
        result = injector.inject_stabilization(sample_phases)
        holistic = next(p for p in result if "holistic" in p["id"])
        checks = holistic.get("checks", [])
        assert len(checks) == 9
