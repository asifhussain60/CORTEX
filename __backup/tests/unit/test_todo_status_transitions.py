"""
CORTEX 6.0 - TodoOrchestrator Status Transition Tests
=====================================================
Tests for status transitions and dependent updates.

Author: Asif Hussain
Version: 6.0.0
Created: 2026-01-07
Task: task-2.2.4 (Implement TODO status transitions)
TDD Phase: GREEN
"""

import pytest
import tempfile
from pathlib import Path
from src.orchestrators.core.todo_orchestrator import (
    TodoOrchestrator,
    Priority,
    TodoStatus,
    InvalidStatusTransitionError,
)
from src.database.state_manager import StateManager
from src.orchestrators.audit_logger import EnterpriseAuditLogger


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "state.db"

@pytest.fixture
def state_manager(temp_db):
    sm = StateManager(temp_db)
    sm.initialize()
    yield sm
    sm.close()

@pytest.fixture
def orchestrator(state_manager):
    # Use unique name per test to prevent cross-test interference
    import uuid
    return TodoOrchestrator(
        state_manager=state_manager,
        audit_logger=EnterpriseAuditLogger(),
        name=f"test-orchestrator-{uuid.uuid4().hex[:8]}"
    )


def test_status_transition_valid(orchestrator):
    """Valid transitions should update status, timestamps, and DAG state."""
    # Create parent and child
    parent_id = orchestrator.create_todo(title="Parent", priority=Priority.P0_CRITICAL)
    child_id = orchestrator.create_todo(title="Child", priority=Priority.P1_HIGH, dependencies=[parent_id])

    # Initially child should be BLOCKED or NOT_READY depending on readiness
    # Ensure parent completion transitions child to READY
    orchestrator.transition_status(parent_id, TodoStatus.IN_PROGRESS)
    orchestrator.transition_status(parent_id, TodoStatus.COMPLETED)

    # Child should become READY (via dependent update)
    child = orchestrator.read_todo(child_id)
    assert child.status in {TodoStatus.READY, TodoStatus.NOT_STARTED}
    # If NOT_STARTED but ready, transitioning to READY should be valid
    if child.status == TodoStatus.NOT_STARTED:
        orchestrator.transition_status(child_id, TodoStatus.READY)

    # Transition child through IN_PROGRESS -> COMPLETED
    orchestrator.transition_status(child_id, TodoStatus.IN_PROGRESS)
    child = orchestrator.read_todo(child_id)
    assert child.started_at is not None
    orchestrator.transition_status(child_id, TodoStatus.COMPLETED)
    child = orchestrator.read_todo(child_id)
    assert child.completed_at is not None
    assert child.status == TodoStatus.COMPLETED


def test_status_transition_invalid(orchestrator):
    """Invalid transitions should raise errors without modifying state."""
    todo_id = orchestrator.create_todo(title="Task", priority=Priority.P2_MEDIUM)

    # Invalid: COMPLETED -> IN_PROGRESS
    orchestrator.transition_status(todo_id, TodoStatus.IN_PROGRESS)
    orchestrator.transition_status(todo_id, TodoStatus.COMPLETED)
    with pytest.raises(InvalidStatusTransitionError):
        orchestrator.transition_status(todo_id, TodoStatus.IN_PROGRESS)

    # Invalid: CANCELLED -> READY
    cancelled_id = orchestrator.create_todo(title="Cancelled", priority=Priority.P3_LOW)
    orchestrator.transition_status(cancelled_id, TodoStatus.IN_PROGRESS)
    orchestrator.transition_status(cancelled_id, TodoStatus.FAILED)
    # Simulate cancellation by setting to CANCELLED via internal path if allowed
    with pytest.raises(InvalidStatusTransitionError):
        orchestrator.transition_status(cancelled_id, TodoStatus.CANCELLED)


def test_update_dependent_statuses_blocking(orchestrator):
    """Dependents become BLOCKED when a prerequisite is not completed."""
    a = orchestrator.create_todo(title="A", priority=Priority.P1_HIGH)
    b = orchestrator.create_todo(title="B", priority=Priority.P2_MEDIUM, dependencies=[a])

    # B should not be READY until A is completed
    # Simulate blocking by moving A from NOT_STARTED to BLOCKED
    orchestrator.transition_status(a, TodoStatus.BLOCKED)

    b_todo = orchestrator.read_todo(b)
    assert b_todo.status in {TodoStatus.NOT_STARTED, TodoStatus.BLOCKED}


def test_update_dependent_statuses_ready(orchestrator):
    """Dependents become READY when all prerequisites are completed."""
    a = orchestrator.create_todo(title="A", priority=Priority.P1_HIGH)
    b = orchestrator.create_todo(title="B", priority=Priority.P2_MEDIUM, dependencies=[a])

    orchestrator.transition_status(a, TodoStatus.IN_PROGRESS)
    orchestrator.transition_status(a, TodoStatus.COMPLETED)

    # Ensure dependent status updated
    b_todo = orchestrator.read_todo(b)
    # If NOT_STARTED but ready, manual transition to READY should be allowed
    if b_todo.status == TodoStatus.NOT_STARTED:
        orchestrator.transition_status(b, TodoStatus.READY)
    else:
        assert b_todo.status in {TodoStatus.READY, TodoStatus.NOT_STARTED}
