"""
Test Suite: Autonomous Execution Engine

Tests for autonomous_execution_engine.py
- Phase state machine transitions
- Pause/resume functionality
- Rollback mechanisms
- Timeout enforcement

AC-AUTONOMOUS-001 through 004
"""

import asyncio
import pytest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from cortex.orchestrators.domain.autonomous_execution_engine import (
    AutonomousExecutionEngine,
    PlanSpecification,
    PhaseDefinition,
    PhaseState,
    ExecutionEventType,
    ExecutionEvent,
)


class TestAutonomousExecutionEngine:
    """Test suite for AutonomousExecutionEngine"""

    @pytest.fixture
    def engine(self, tmp_path: Path) -> AutonomousExecutionEngine:
        """Create test engine instance"""
        state_file = tmp_path / "execution_state.json"
        return AutonomousExecutionEngine(state_file, timeout_per_phase=1800)

    @pytest.fixture
    def sample_plan(self) -> PlanSpecification:
        """Create sample plan for testing"""
        phase1 = PhaseDefinition(
            phase_num=0,
            name="Dependency Analysis",
            description="Analyze dependencies",
            duration_estimate=60,
            tdd_cycles=["RED", "GREEN", "REFACTOR"],
            governance_checks=["CORE-030"],
            deliverables=["dependency_map.json"],
        )

        phase2 = PhaseDefinition(
            phase_num=1,
            name="Naming Utilities",
            description="Implement naming utilities",
            duration_estimate=90,
            tdd_cycles=["RED", "GREEN", "REFACTOR"],
            governance_checks=["CORE-008", "CORE-011", "CORE-012"],
            deliverables=["naming_utilities.py"],
            dependencies=[0],
        )

        return PlanSpecification(
            plan_id="AC-PLAN-001",
            name="Planning Orchestrator Implementation",
            description="Complete autonomous planning orchestrator",
            created_at=datetime.now().isoformat(),
            total_phases=2,
            phases=[phase1, phase2],
            governance_rules=["CORE-008", "CORE-011", "CORE-012", "CORE-026"],
        )

    @pytest.mark.asyncio
    async def test_initialize_engine(self, engine: AutonomousExecutionEngine):
        """Test engine initialization"""
        assert engine is not None
        assert engine.timeout_per_phase == 1800
        assert engine._is_running is False

    @pytest.mark.asyncio
    async def test_execute_plan_autonomously(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test autonomous plan execution"""
        events: List[ExecutionEvent] = []

        def capture_event(event: ExecutionEvent) -> None:
            events.append(event)

        # Execute plan
        result = await engine.execute_plan_autonomously(
            plan=sample_plan,
            progress_callback=capture_event,
        )

        # Verify execution
        assert result.is_ok()
        summary = result.unwrap()
        assert summary["status"] == "COMPLETE"
        assert summary["phases_completed"] == sample_plan.total_phases

        # Verify events were emitted
        assert len(events) > 0
        assert events[-1].event_type == ExecutionEventType.EXECUTION_COMPLETE

    @pytest.mark.asyncio
    async def test_pause_execution(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test pause functionality"""
        events: List[ExecutionEvent] = []

        def capture_event(event: ExecutionEvent) -> None:
            events.append(event)

        # Start execution
        task = asyncio.create_task(
            engine.execute_plan_autonomously(
                plan=sample_plan,
                progress_callback=capture_event,
            )
        )

        # Let it start
        await asyncio.sleep(0.1)

        # Request pause
        pause_result = await engine.pause_execution("User requested pause")

        # Verify pause
        assert pause_result.is_ok()

        # Wait for task to complete
        await task

        # Verify execution was paused
        assert engine._current_execution is not None
        assert engine._current_execution.status == "PAUSED"

    @pytest.mark.asyncio
    async def test_resume_execution(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test resume functionality"""
        # First, create a paused execution
        events: List[ExecutionEvent] = []

        def capture_event(event: ExecutionEvent) -> None:
            events.append(event)

        # Simulate pause state
        await engine.pause_execution("Test pause")

        # Resume execution
        resume_result = await engine.resume_execution(
            updated_plan=None,
            progress_callback=capture_event,
        )

        # Verify resume
        assert resume_result.is_ok()
        summary = resume_result.unwrap()
        assert summary["status"] == "RESUMED"

    @pytest.mark.asyncio
    async def test_checkpoint_persistence(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test checkpoint persistence"""
        events: List[ExecutionEvent] = []

        def capture_event(event: ExecutionEvent) -> None:
            events.append(event)

        # Execute and pause
        task = asyncio.create_task(
            engine.execute_plan_autonomously(
                plan=sample_plan,
                progress_callback=capture_event,
            )
        )

        await asyncio.sleep(0.1)
        await engine.pause_execution("Test checkpoint")
        await task

        # Verify checkpoint was saved
        assert engine.execution_state_path.exists()

        # Load and verify
        import json

        with open(engine.execution_state_path) as f:
            saved_state = json.load(f)

        assert saved_state["plan_id"] == sample_plan.plan_id
        assert saved_state["status"] == "PAUSED"

    @pytest.mark.asyncio
    async def test_rollback_to_phase(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test rollback functionality"""
        events: List[ExecutionEvent] = []

        def capture_event(event: ExecutionEvent) -> None:
            events.append(event)

        # Execute plan partially
        task = asyncio.create_task(
            engine.execute_plan_autonomously(
                plan=sample_plan,
                progress_callback=capture_event,
            )
        )

        await asyncio.sleep(0.2)

        # Request rollback
        rollback_result = await engine.rollback_to_phase(0, "Test rollback")

        # Verify rollback
        assert rollback_result.is_ok()

        await task

    @pytest.mark.asyncio
    async def test_governance_enforcement_pre_phase(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test pre-phase governance checks"""
        phase = sample_plan.phases[0]

        result = await engine._pre_phase_governance_check(phase, None)

        assert result.is_ok()

    @pytest.mark.asyncio
    async def test_governance_enforcement_post_phase(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test post-phase governance checks"""
        phase = sample_plan.phases[0]

        result = await engine._post_phase_governance_check(phase, None)

        assert result.is_ok()

    @pytest.mark.asyncio
    async def test_tdd_cycle_execution(
        self,
        engine: AutonomousExecutionEngine,
        sample_plan: PlanSpecification,
    ):
        """Test TDD cycle execution"""
        phase = sample_plan.phases[0]
        events: List[ExecutionEvent] = []

        def capture_event(event: ExecutionEvent) -> None:
            events.append(event)

        result = await engine._execute_tdd_cycle("RED", phase, capture_event)

        assert result.is_ok()
        assert len(events) > 0

    def test_phase_definition_serialization(self, sample_plan: PlanSpecification):
        """Test phase definition serialization"""
        phase = sample_plan.phases[0]
        phase_dict = phase.to_dict()

        assert phase_dict["phase_num"] == 0
        assert phase_dict["name"] == "Dependency Analysis"
        assert "deliverables" in phase_dict

    def test_plan_specification_serialization(self, sample_plan: PlanSpecification):
        """Test plan specification serialization"""
        plan_dict = sample_plan.to_dict()

        assert plan_dict["plan_id"] == "AC-PLAN-001"
        assert plan_dict["total_phases"] == 2
        assert len(plan_dict["phases"]) == 2


class TestExecutionEvent:
    """Test suite for ExecutionEvent"""

    def test_event_creation(self):
        """Test event creation and serialization"""
        event = ExecutionEvent(
            event_type=ExecutionEventType.PHASE_STARTED,
            phase_num=0,
            message="Phase started",
            data={"phase_name": "Test"},
            elapsed_seconds=0,
        )

        assert event.event_type == ExecutionEventType.PHASE_STARTED
        assert event.phase_num == 0

        # Test serialization
        event_dict = event.to_dict()
        assert event_dict["event_type"] == "phase_started"
        assert event_dict["phase_num"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
