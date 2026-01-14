"""
Tests for execution queue and progress tracking (Phase 4, tasks 2.4.2 and 2.4.3).
"""

import pytest
from pathlib import Path

from src.orchestrators.core.todo_orchestrator import TodoOrchestrator, TodoStatus, Priority
from src.orchestrators.state_manager import StateManager
from src.orchestrators.audit_logger import EnterpriseAuditLogger


@pytest.fixture
def orchestrator(tmp_path: Path) -> TodoOrchestrator:
    """Create a TodoOrchestrator instance for testing."""
    state_mgr = StateManager(state_file=str(tmp_path / "test.db"))
    audit_logger = EnterpriseAuditLogger(log_dir=str(tmp_path / "logs"))
    return TodoOrchestrator(state_manager=state_mgr, audit_logger=audit_logger)


# ==============================================================================
# EXECUTION QUEUE TESTS (task-2.4.2)
# ==============================================================================

def test_get_next_tasks(orchestrator: TodoOrchestrator):
    """Test getting next tasks in priority order."""
    # Create tasks with different priorities
    task1 = orchestrator.create_todo(
        title="Critical Task",
        priority=Priority.P0_CRITICAL
    )
    task2 = orchestrator.create_todo(
        title="Medium Task",
        priority=Priority.P2_MEDIUM
    )
    task3 = orchestrator.create_todo(
        title="High Task",
        priority=Priority.P1_HIGH
    )
    
    # Transition all to READY
    orchestrator.transition_status(task1, TodoStatus.READY)
    orchestrator.transition_status(task2, TodoStatus.READY)
    orchestrator.transition_status(task3, TodoStatus.READY)
    
    # Get next tasks
    next_tasks = orchestrator.get_next_tasks()
    
    # Should be prioritized: P0 > P1 > P2
    assert len(next_tasks) == 3
    assert next_tasks[0].priority == Priority.P0_CRITICAL
    assert next_tasks[1].priority == Priority.P1_HIGH
    assert next_tasks[2].priority == Priority.P2_MEDIUM


def test_execute_task(orchestrator: TodoOrchestrator):
    """Test executing a task."""
    task_id = orchestrator.create_todo(
        title="Test Task",
        description="Test description",
        priority=Priority.P0_CRITICAL
    )
    
    # Transition to READY
    orchestrator.transition_status(task_id, TodoStatus.READY)
    
    # Execute task
    result = orchestrator.execute_task(task_id)
    
    # Verify result
    assert result["task_id"] == task_id
    assert result["title"] == "Test Task"
    assert "started_at" in result
    
    # Verify status changed
    todo = orchestrator.read_todo(task_id)
    assert todo.status == TodoStatus.IN_PROGRESS


def test_execute_task_not_ready(orchestrator: TodoOrchestrator):
    """Test that executing a non-ready task raises an error."""
    task_id = orchestrator.create_todo(
        title="Blocked Task",
        priority=Priority.P0_CRITICAL
    )
    
    # Try to execute NOT_STARTED task
    with pytest.raises(ValueError, match="not ready"):
        orchestrator.execute_task(task_id)


def test_mark_complete(orchestrator: TodoOrchestrator):
    """Test marking a task as complete."""
    task_id = orchestrator.create_todo(title="Task")
    orchestrator.transition_status(task_id, TodoStatus.READY)
    orchestrator.execute_task(task_id)
    
    # Mark complete
    result = {"output": "success"}
    todo = orchestrator.mark_complete(task_id, result)
    
    # Verify status
    assert todo.status == TodoStatus.COMPLETED
    assert todo.data["result"] == result


def test_mark_failed(orchestrator: TodoOrchestrator):
    """Test marking a task as failed."""
    task_id = orchestrator.create_todo(title="Task")
    orchestrator.transition_status(task_id, TodoStatus.READY)
    orchestrator.execute_task(task_id)
    
    # Mark failed
    error = "Something went wrong"
    todo = orchestrator.mark_failed(task_id, error)
    
    # Verify status
    assert todo.status == TodoStatus.FAILED
    assert todo.data["error"] == error
    assert "failed_at" in todo.data


def test_priority_ordering(orchestrator: TodoOrchestrator):
    """Test that execution queue respects priority ordering."""
    # Create tasks in reverse priority order
    low = orchestrator.create_todo(title="Low", priority=Priority.P3_LOW)
    medium = orchestrator.create_todo(title="Medium", priority=Priority.P2_MEDIUM)
    high = orchestrator.create_todo(title="High", priority=Priority.P1_HIGH)
    critical = orchestrator.create_todo(title="Critical", priority=Priority.P0_CRITICAL)
    
    # Make all ready
    for task_id in [low, medium, high, critical]:
        orchestrator.transition_status(task_id, TodoStatus.READY)
    
    # Get next tasks
    next_tasks = orchestrator.get_next_tasks()
    
    # Verify ordering
    priorities = [t.priority for t in next_tasks]
    expected = [Priority.P0_CRITICAL, Priority.P1_HIGH, Priority.P2_MEDIUM, Priority.P3_LOW]
    assert priorities == expected


# ==============================================================================
# PROGRESS TRACKING TESTS (task-2.4.3)
# ==============================================================================

def test_get_progress(orchestrator: TodoOrchestrator):
    """Test getting overall progress."""
    # Create some tasks
    task1 = orchestrator.create_todo(title="Task 1")
    task2 = orchestrator.create_todo(title="Task 2")
    task3 = orchestrator.create_todo(title="Task 3")
    
    # Complete one
    orchestrator.transition_status(task1, TodoStatus.READY)
    orchestrator.execute_task(task1)
    orchestrator.mark_complete(task1)
    
    # Get progress
    progress = orchestrator.get_progress()
    
    # Verify metrics
    assert progress["total_tasks"] == 3
    assert progress["completed_tasks"] == 1
    assert progress["percentage"] == pytest.approx(33.33, rel=0.01)
    assert progress["in_progress_tasks"] == 0


def test_get_progress_empty(orchestrator: TodoOrchestrator):
    """Test progress with no tasks."""
    progress = orchestrator.get_progress()
    
    assert progress["total_tasks"] == 0
    assert progress["percentage"] == 0.0


def test_get_feature_progress(orchestrator: TodoOrchestrator):
    """Test getting feature-specific progress."""
    # Create tasks for a feature
    task1 = orchestrator.create_todo(
        title="Feature Task 1",
        data={"feature_id": "feat01"}
    )
    task2 = orchestrator.create_todo(
        title="Feature Task 2",
        data={"feature_id": "feat01"}
    )
    task3 = orchestrator.create_todo(
        title="Other Task",
        data={"feature_id": "feat02"}
    )
    
    # Complete one feat01 task
    orchestrator.transition_status(task1, TodoStatus.READY)
    orchestrator.execute_task(task1)
    orchestrator.mark_complete(task1)
    
    # Get feature progress
    progress = orchestrator.get_feature_progress("feat01")
    
    assert progress["feature_id"] == "feat01"
    assert progress["total_tasks"] == 2
    assert progress["completed_tasks"] == 1
    assert progress["percentage"] == 50.0


def test_get_phase_progress(orchestrator: TodoOrchestrator):
    """Test getting phase-specific progress."""
    # Create tasks for a phase
    task1 = orchestrator.create_todo(
        title="Phase Task 1",
        data={"feature_id": "feat01", "phase_id": 1}
    )
    task2 = orchestrator.create_todo(
        title="Phase Task 2",
        data={"feature_id": "feat01", "phase_id": 1}
    )
    task3 = orchestrator.create_todo(
        title="Other Phase Task",
        data={"feature_id": "feat01", "phase_id": 2}
    )
    
    # Complete one phase 1 task
    orchestrator.transition_status(task1, TodoStatus.READY)
    orchestrator.execute_task(task1)
    orchestrator.mark_complete(task1)
    
    # Get phase progress
    progress = orchestrator.get_phase_progress("feat01", 1)
    
    assert progress["feature_id"] == "feat01"
    assert progress["phase_id"] == 1
    assert progress["total_tasks"] == 2
    assert progress["completed_tasks"] == 1
    assert progress["percentage"] == 50.0


def test_update_progress(orchestrator: TodoOrchestrator):
    """Test that progress updates as tasks complete."""
    # Create tasks
    task1 = orchestrator.create_todo(title="Task 1")
    task2 = orchestrator.create_todo(title="Task 2")
    
    # Initial progress
    progress1 = orchestrator.get_progress()
    assert progress1["completed_tasks"] == 0
    assert progress1["percentage"] == 0.0
    
    # Complete first task
    orchestrator.transition_status(task1, TodoStatus.READY)
    orchestrator.execute_task(task1)
    orchestrator.mark_complete(task1)
    
    progress2 = orchestrator.get_progress()
    assert progress2["completed_tasks"] == 1
    assert progress2["percentage"] == 50.0
    
    # Complete second task
    orchestrator.transition_status(task2, TodoStatus.READY)
    orchestrator.execute_task(task2)
    orchestrator.mark_complete(task2)
    
    progress3 = orchestrator.get_progress()
    assert progress3["completed_tasks"] == 2
    assert progress3["percentage"] == 100.0
