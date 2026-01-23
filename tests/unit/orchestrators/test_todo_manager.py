"""
Tests for TodoManager - Multi-phase task tracking with governance integration.
AC-IDs tested: AC-FR-TODO-001, AC-FR-TODO-002, AC-FR-TODO-003, AC-FR-TODO-004

Implements phase-based task decomposition with:
- Multi-phase execution with dependencies
- Real-time progress tracking and status updates
- Automatic phase advancement based on completion criteria
- Governance validation at each phase transition
- Rollback support for failed phases
- Audit trail for all phase changes

"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from cortex.orchestrators.tools.todo_manager import (
    TodoManager,
    Task,
    Phase,
    PhaseStatus,
    TaskState,
    TaskStatus,
)


class TestPhaseModel:
    """Tests for Phase data model."""

    def test_phase_creation(self) -> None:
        """Test AC-FR-TODO-001: Phase creation with ID and title."""
        phase = Phase(
            id=1,
            title="Design",
            description="Design phase",
            dependencies=[],
        )
        assert phase.id == 1
        assert phase.title == "Design"
        assert phase.status == PhaseStatus.NOT_STARTED
        assert phase.dependencies == []

    def test_phase_with_dependencies(self) -> None:
        """Test AC-FR-TODO-001: Phase dependencies specification."""
        phase = Phase(
            id=2,
            title="Implementation",
            description="Implement feature",
            dependencies=[1],
        )
        assert phase.dependencies == [1]
        assert phase.status == PhaseStatus.NOT_STARTED

    def test_phase_status_transitions(self) -> None:
        """Test AC-FR-TODO-002: Phase status state machine."""
        phase = Phase(
            id=1,
            title="Phase 1",
            description="Test phase",
            dependencies=[],
        )

        # Transition to in-progress
        phase.status = PhaseStatus.IN_PROGRESS
        assert phase.status == PhaseStatus.IN_PROGRESS

        # Transition to completed
        phase.status = PhaseStatus.COMPLETED
        assert phase.status == PhaseStatus.COMPLETED


class TestTaskModel:
    """Tests for Task data model."""

    def test_task_creation(self) -> None:
        """Test AC-FR-TODO-003: Task creation with phases."""
        phases = [
            Phase(id=1, title="Design", description="Design", dependencies=[]),
            Phase(id=2, title="Impl", description="Implement", dependencies=[1]),
        ]
        task = Task(
            task_id="IMPL-FEATURE-001",
            description="Implement feature",
            phases=phases,
        )
        assert task.task_id == "IMPL-FEATURE-001"
        assert len(task.phases) == 2
        assert task.status == TaskState.NOT_STARTED

    def test_task_phase_count(self) -> None:
        """Test AC-FR-TODO-003: Task tracks phase count."""
        phases = [
            Phase(id=i, title=f"Phase {i}", description="", dependencies=[])
            for i in range(1, 6)
        ]
        task = Task(
            task_id="TASK-001",
            description="Multi-phase task",
            phases=phases,
        )
        assert len(task.phases) == 5


class TestTodoManager:
    """Tests for TodoManager - Multi-phase task orchestration."""

    @pytest.fixture
    def manager(self) -> TodoManager:
        """Create TodoManager instance."""
        return TodoManager()

    @pytest.fixture
    def sample_phases(self) -> List[Dict[str, Any]]:
        """Sample phases for testing."""
        return [
            {"id": 1, "title": "Design", "dependencies": []},
            {"id": 2, "title": "Implementation", "dependencies": [1]},
            {"id": 3, "title": "Testing", "dependencies": [2]},
            {"id": 4, "title": "Governance Review", "dependencies": [3]},
            {"id": 5, "title": "Deployment", "dependencies": [4]},
        ]

    def test_create_task(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-001: Create task with multiple phases."""
        task = manager.create_task(
            task_id="TEST-001",
            description="Test task",
            phases=sample_phases,
        )

        assert task.task_id == "TEST-001"
        assert len(task.phases) == 5
        assert task.status == TaskState.NOT_STARTED

    def test_mark_phase_in_progress(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-002: Mark phase as in-progress."""
        task = manager.create_task(
            task_id="TEST-002",
            description="Test task",
            phases=sample_phases,
        )

        manager.mark_phase(task_id=task.task_id, phase_id=1, status="in-progress")
        updated_task = manager.get_task(task.task_id)

        assert updated_task.phases[0].status == PhaseStatus.IN_PROGRESS

    def test_mark_phase_completed(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-002: Mark phase as completed."""
        task = manager.create_task(
            task_id="TEST-003",
            description="Test task",
            phases=sample_phases,
        )

        manager.mark_phase(task_id=task.task_id, phase_id=1, status="completed")
        updated_task = manager.get_task(task.task_id)

        assert updated_task.phases[0].status == PhaseStatus.COMPLETED

    def test_mark_phase_failed(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-002: Mark phase as failed with error."""
        task = manager.create_task(
            task_id="TEST-004",
            description="Test task",
            phases=sample_phases,
        )

        error_msg = "Test error"
        manager.mark_phase(
            task_id=task.task_id,
            phase_id=1,
            status="failed",
            error=error_msg,
        )
        updated_task = manager.get_task(task.task_id)

        assert updated_task.phases[0].status == PhaseStatus.FAILED
        assert updated_task.phases[0].error == error_msg

    def test_mark_phase_blocked(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-002: Mark phase as blocked with violations."""
        task = manager.create_task(
            task_id="TEST-005",
            description="Test task",
            phases=sample_phases,
        )

        violations = ["CORE-013: Bare except found", "CORE-011: Missing type hint"]
        manager.mark_phase(
            task_id=task.task_id,
            phase_id=1,
            status="blocked",
            violations=violations,
        )
        updated_task = manager.get_task(task.task_id)

        assert updated_task.phases[0].status == PhaseStatus.BLOCKED
        assert updated_task.phases[0].violations == violations

    def test_get_task_status(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-004: Get task status with progress metrics."""
        task = manager.create_task(
            task_id="TEST-006",
            description="Test task",
            phases=sample_phases,
        )

        # Mark some phases as completed
        manager.mark_phase(task_id=task.task_id, phase_id=1, status="completed")
        manager.mark_phase(task_id=task.task_id, phase_id=2, status="in-progress")

        status = manager.get_task_status(task.task_id)

        assert status.task_id == "TEST-006"
        assert status.completed_phases == 1
        assert status.total_phases == 5
        assert status.current_phase == 2

    def test_dependency_validation(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-001: Phase dependencies are respected."""
        task = manager.create_task(
            task_id="TEST-007",
            description="Test task",
            phases=sample_phases,
        )

        # Phase 2 depends on Phase 1
        # Try to complete phase 2 without phase 1 complete
        result = manager.can_advance_to_phase(task.task_id, 2)

        # Should return False since dependency not met
        assert result is False

    def test_can_advance_with_met_dependencies(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-001: Can advance when dependencies complete."""
        task = manager.create_task(
            task_id="TEST-008",
            description="Test task",
            phases=sample_phases,
        )

        # Complete phase 1
        manager.mark_phase(task_id=task.task_id, phase_id=1, status="completed")

        # Now should be able to advance to phase 2
        result = manager.can_advance_to_phase(task.task_id, 2)

        assert result is True

    def test_rollback_to_phase(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-004: Rollback phase state on failure."""
        task = manager.create_task(
            task_id="TEST-009",
            description="Test task",
            phases=sample_phases,
        )

        # Mark phases 1-3 as completed
        for phase_id in [1, 2, 3]:
            manager.mark_phase(task_id=task.task_id, phase_id=phase_id, status="completed")

        # Rollback to phase 2
        manager.rollback_to_phase(task.task_id, 2)

        updated_task = manager.get_task(task.task_id)

        # Phase 3 should be reset to not-started
        assert updated_task.phases[2].status == PhaseStatus.NOT_STARTED
        # Phase 2 should still be completed
        assert updated_task.phases[1].status == PhaseStatus.COMPLETED

    def test_get_completed_phases(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-004: Query completed phases."""
        task = manager.create_task(
            task_id="TEST-010",
            description="Test task",
            phases=sample_phases,
        )

        # Mark phases 1 and 2 as completed
        manager.mark_phase(task_id=task.task_id, phase_id=1, status="completed")
        manager.mark_phase(task_id=task.task_id, phase_id=2, status="completed")

        completed = manager.get_completed_phases(task.task_id)

        assert len(completed) == 2
        assert completed[0].id == 1
        assert completed[1].id == 2

    def test_get_blocked_phases(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-004: Query blocked phases."""
        task = manager.create_task(
            task_id="TEST-011",
            description="Test task",
            phases=sample_phases,
        )

        violations = ["CORE-013: Bare except"]
        manager.mark_phase(
            task_id=task.task_id,
            phase_id=1,
            status="blocked",
            violations=violations,
        )

        blocked = manager.get_blocked_phases(task.task_id)

        assert len(blocked) == 1
        assert blocked[0].violations == violations

    def test_audit_trail_creation(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-004: Audit trail for phase changes."""
        task = manager.create_task(
            task_id="TEST-012",
            description="Test task",
            phases=sample_phases,
        )

        manager.mark_phase(task_id=task.task_id, phase_id=1, status="in-progress")
        manager.mark_phase(task_id=task.task_id, phase_id=1, status="completed")

        audit = manager.get_audit_trail(task.task_id, phase_id=1)

        assert len(audit) >= 2
        assert audit[-2]["status"] == "in-progress"
        assert audit[-1]["status"] == "completed"

    def test_task_with_zero_dependencies(
        self, manager: TodoManager
    ) -> None:
        """Test AC-FR-TODO-001: Phase with no dependencies."""
        phases = [
            {"id": 1, "title": "Independent", "dependencies": []},
        ]
        task = manager.create_task(
            task_id="TEST-013",
            description="Single phase",
            phases=phases,
        )

        result = manager.can_advance_to_phase(task.task_id, 1)

        # Should be able to advance to first phase
        assert result is True

    def test_update_phase_metadata(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-004: Update phase metadata during execution."""
        task = manager.create_task(
            task_id="TEST-014",
            description="Test task",
            phases=sample_phases,
        )

        manager.mark_phase(
            task_id=task.task_id,
            phase_id=1,
            status="in-progress",
            metadata={"duration_seconds": 45, "executor": "unit_test"},
        )

        updated_task = manager.get_task(task.task_id)
        phase = updated_task.phases[0]

        assert phase.metadata.get("duration_seconds") == 45
        assert phase.metadata.get("executor") == "unit_test"

    def test_complete_entire_task_flow(
        self, manager: TodoManager, sample_phases: List[Dict[str, Any]]
    ) -> None:
        """Test AC-FR-TODO-001,2,3,4: Complete workflow from start to finish."""
        task = manager.create_task(
            task_id="TEST-015",
            description="Complete workflow",
            phases=sample_phases,
        )

        # Execute phases sequentially
        for phase_id in range(1, 6):
            # Start phase
            manager.mark_phase(
                task_id=task.task_id,
                phase_id=phase_id,
                status="in-progress",
            )

            # Complete phase
            manager.mark_phase(
                task_id=task.task_id,
                phase_id=phase_id,
                status="completed",
            )

        final_status = manager.get_task_status(task.task_id)

        assert final_status.completed_phases == 5
        assert final_status.total_phases == 5
        assert final_status.task_status == TaskState.COMPLETED


class TestTodoManagerIntegration:
    """Integration tests with MasterOrchestrator."""

    @pytest.fixture
    def manager(self) -> TodoManager:
        """Create TodoManager instance."""
        return TodoManager()

    def test_integration_with_orchestrator_context(
        self, manager: TodoManager
    ) -> None:
        """Test TodoManager integration with orchestrator execution context."""
        phases = [
            {"id": 1, "title": "Analysis", "dependencies": []},
            {"id": 2, "title": "Implementation", "dependencies": [1]},
            {"id": 3, "title": "Validation", "dependencies": [2]},
        ]

        task = manager.create_task(
            task_id="ORCH-001",
            description="Orchestrator-driven task",
            phases=phases,
        )

        # Simulate orchestrator execution
        for phase_id in [1, 2, 3]:
            can_advance = manager.can_advance_to_phase(task.task_id, phase_id)
            if can_advance:
                manager.mark_phase(
                    task_id=task.task_id,
                    phase_id=phase_id,
                    status="completed",
                )

        status = manager.get_task_status(task.task_id)
        assert status.completed_phases == 3
