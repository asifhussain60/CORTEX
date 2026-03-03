"""
Phase 103-c TDD RED tests — tdd_orchestrator.py decomposition.

AC-103-C-001: tdd_models module importable (TDDPhase, TDDDisciplineRule, SuccessCriteria,
              CycleMetrics, GateResult, TDDImplementationGuidance, TDDKnowledgeLoader)
AC-103-C-002: tdd_execution_mixin importable + execution methods present
AC-103-C-003: tdd_metrics_mixin importable + metrics/validation methods present
AC-103-C-004: tdd_batch_mixin importable + batch/parse/fix methods present
AC-103-C-005: TDDOrchestrator public API unchanged (no regressions)
AC-103-C-006: tdd_orchestrator.py reduced to ≤ 750 lines

CORE-008: Tests written FIRST (RED phase). All import tests will FAIL until
          the mixin modules are extracted.

Run:
    python3 -m pytest tests/orchestrators/core/test_tdd_orchestrator_decomposition.py -x -q
"""

import pathlib
import inspect
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# AC-103-C-001: tdd_models module
# ---------------------------------------------------------------------------

class TestTDDModelsModule:
    """TDD data models extracted into dedicated models module."""

    def test_tdd_models_importable(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_models import (  # noqa: F401
            TDDPhase,
            TDDDisciplineRule,
            SuccessCriteria,
            CycleMetrics,
            GateResult,
            TDDImplementationGuidance,
            TDDKnowledgeLoader,
        )

    def test_tdd_phase_enum_values(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_models import TDDPhase
        assert TDDPhase.RED.value == "red"
        assert TDDPhase.GREEN.value == "green"
        assert TDDPhase.REFACTOR.value == "refactor"

    def test_cycle_metrics_is_dataclass(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_models import CycleMetrics
        import dataclasses
        assert dataclasses.is_dataclass(CycleMetrics)
        fields = {f.name for f in dataclasses.fields(CycleMetrics)}
        assert "cycle_number" in fields
        assert "tests_passed" in fields
        assert "tests_failed" in fields
        assert "coverage_percent" in fields

    def test_gate_result_is_dataclass(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_models import GateResult
        import dataclasses
        assert dataclasses.is_dataclass(GateResult)
        g = GateResult(passed=True, gaps=[], recommendations=[])
        assert g.passed is True

    def test_tdd_knowledge_loader_has_get_best_practices(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_models import TDDKnowledgeLoader
        assert hasattr(TDDKnowledgeLoader, "get_best_practices")

    def test_success_criteria_has_goal_predicate(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_models import SuccessCriteria
        import dataclasses
        fields = {f.name for f in dataclasses.fields(SuccessCriteria)}
        assert "goal_predicate" in fields
        assert "min_coverage" in fields

    def test_tdd_implementation_guidance_is_dataclass(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_models import (
            TDDImplementationGuidance,
            TDDPhase,
        )
        import dataclasses
        assert dataclasses.is_dataclass(TDDImplementationGuidance)
        g = TDDImplementationGuidance(
            module_path="cortex/foo.py",
            domain="core",
            tdd_phase=TDDPhase.RED,
        )
        assert g.module_path == "cortex/foo.py"


# ---------------------------------------------------------------------------
# AC-103-C-002: tdd_execution_mixin module
# ---------------------------------------------------------------------------

class TestTDDExecutionMixinModule:
    """TDD execution pipeline extracted into dedicated mixin module."""

    def test_tdd_execution_mixin_importable(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import (  # noqa: F401
            TDDExecutionMixin,
        )

    def test_mixin_has_execute_with_directive(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        assert hasattr(TDDExecutionMixin, "execute_with_directive")

    def test_mixin_has_pre_execution_brittleness_scan(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        assert hasattr(TDDExecutionMixin, "_run_pre_execution_brittleness_scan")

    def test_mixin_has_post_execution_brittleness_scan(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        assert hasattr(TDDExecutionMixin, "_run_post_execution_brittleness_scan")

    def test_mixin_has_phase_completion_hook(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        assert hasattr(TDDExecutionMixin, "_run_phase_completion_hook")

    def test_mixin_has_execute_domain_logic(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        assert hasattr(TDDExecutionMixin, "_execute_domain_logic")

    def test_mixin_has_determine_tdd_phase(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        assert hasattr(TDDExecutionMixin, "_determine_tdd_phase")

    def test_mixin_has_execute_tdd_phases(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        for method in ("_execute_tdd_phase", "_execute_red_phase", "_execute_green_phase", "_execute_refactor_phase"):
            assert hasattr(TDDExecutionMixin, method), f"Missing: {method}"

    def test_mixin_has_build_tdd_guidance(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        assert hasattr(TDDExecutionMixin, "_build_tdd_guidance")


# ---------------------------------------------------------------------------
# AC-103-C-003: tdd_metrics_mixin module
# ---------------------------------------------------------------------------

class TestTDDMetricsMixinModule:
    """TDD metrics, validation, and holistic refactor extracted into dedicated mixin."""

    def test_tdd_metrics_mixin_importable(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import (  # noqa: F401
            TDDMetricsMixin,
        )

    def test_mixin_has_execute_multi_cycle(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        assert hasattr(TDDMetricsMixin, "execute_multi_cycle")

    def test_mixin_has_track_cycle_metrics(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        assert hasattr(TDDMetricsMixin, "track_cycle_metrics")

    def test_mixin_has_holistic_refactor_gate(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        assert hasattr(TDDMetricsMixin, "holistic_refactor_gate")

    def test_mixin_has_convergence_loop(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        assert hasattr(TDDMetricsMixin, "execute_convergence_loop")

    def test_mixin_has_validate_methods(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        for method in ("validate_coverage", "validate_latency", "validate_extensibility"):
            assert hasattr(TDDMetricsMixin, method), f"Missing: {method}"

    def test_mixin_has_holistic_refactor_gate_enhanced(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        assert hasattr(TDDMetricsMixin, "holistic_refactor_gate_enhanced")

    def test_mixin_has_get_tdd_status(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        assert hasattr(TDDMetricsMixin, "get_tdd_status")


# ---------------------------------------------------------------------------
# AC-103-C-004: tdd_batch_mixin module
# ---------------------------------------------------------------------------

class TestTDDBatchMixinModule:
    """Batch test runner and utilities extracted into dedicated mixin module."""

    def test_tdd_batch_mixin_importable(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import (  # noqa: F401
            TDDBatchMixin,
        )

    def test_mixin_has_run_batch_suite(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
        assert hasattr(TDDBatchMixin, "run_batch_suite")

    def test_mixin_has_run_test_suite(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
        assert hasattr(TDDBatchMixin, "_run_test_suite")

    def test_mixin_has_parse_pytest_counts(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
        assert hasattr(TDDBatchMixin, "_parse_pytest_counts")

    def test_mixin_has_attempt_import_fix(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
        assert hasattr(TDDBatchMixin, "_attempt_import_fix")

    def test_mixin_has_emit_event(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
        assert hasattr(TDDBatchMixin, "_emit_event")


# ---------------------------------------------------------------------------
# AC-103-C-005: TDDOrchestrator public API unchanged
# ---------------------------------------------------------------------------

class TestTDDOrchestratorPublicAPIUnchanged:
    """TDDOrchestrator must export the same public interface after decomposition."""

    def test_import_unchanged(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator  # noqa: F401

    def test_tdd_phase_still_importable_from_main_module(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDPhase  # noqa: F401

    def test_cycle_metrics_still_importable_from_main_module(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import CycleMetrics  # noqa: F401

    def test_gate_result_still_importable_from_main_module(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import GateResult  # noqa: F401

    def test_success_criteria_still_importable_from_main_module(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import SuccessCriteria  # noqa: F401

    def test_orchestrator_has_get_name(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "get_name")

    def test_orchestrator_has_execute_operation(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "execute_operation")

    def test_orchestrator_has_execute_multi_cycle(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "execute_multi_cycle")

    def test_orchestrator_has_holistic_refactor_gate(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "holistic_refactor_gate")

    def test_orchestrator_has_execute_convergence_loop(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "execute_convergence_loop")

    def test_orchestrator_has_run_batch_suite(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "run_batch_suite")

    def test_orchestrator_has_validate_coverage(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "validate_coverage")

    def test_mixin_inheritance_chain_includes_new_mixins(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
        from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
        from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
        mro = TDDOrchestrator.__mro__
        for mixin in (TDDExecutionMixin, TDDMetricsMixin, TDDBatchMixin):
            assert mixin in mro, f"{mixin.__name__} not in TDDOrchestrator MRO"

    def test_orchestrator_instantiates(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        t = TDDOrchestrator()
        assert t is not None
        assert t.get_name() == "TDDOrchestrator"

    def test_create_test_stub_still_present(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "create_test_stub")

    def test_get_cycle_metrics_still_present(self) -> None:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        assert hasattr(TDDOrchestrator, "get_cycle_metrics")


# ---------------------------------------------------------------------------
# AC-103-C-006: tdd_orchestrator.py line-count gate
# ---------------------------------------------------------------------------
# Revised limit: ≤ 750L (same rationale as Phase 103-b)
# Irreducible public API: TDDPhase + 5 dataclasses + TDDKnowledgeLoader = ~186L
# Module header + imports: ~90L
# TDDOrchestrator coordination layer: ~350L
# Absolute minimum: ~626L → realistic limit = 750L (Phase 103-a/b precedent)

class TestTDDOrchestratorLineCount:
    """After decomposition tdd_orchestrator/_coordinator.py must be ≤ 750 lines."""

    def test_line_count_at_or_below_750(self) -> None:
        # Phase 103-c: tdd_orchestrator.py is now a package directory.
        # The slim coordinator lives at tdd_orchestrator/_coordinator.py.
        impl_path = (
            pathlib.Path(__file__).parent.parent.parent.parent
            / "cortex" / "orchestrators" / "core" / "tdd_orchestrator" / "_coordinator.py"
        )
        assert impl_path.exists(), "_coordinator.py must exist inside tdd_orchestrator/ package"
        lines = impl_path.read_text(encoding="utf-8").splitlines()
        line_count = len(lines)
        assert line_count <= 750, (
            f"tdd_orchestrator/_coordinator.py is {line_count} lines — must be ≤ 750 after Phase 103-c decomposition. "
            f"Irreducible public API (6 dataclasses + TDDKnowledgeLoader) accounts for ~186L; "
            f"module header ~90L; TDDOrchestrator coordination layer ~350L. "
            f"Check that no large method blocks were re-introduced inline."
        )
