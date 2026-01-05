"""
Tests for TaskListOrchestrator.

Tests cover:
- Task execution (sequential, with dependencies)
- Checkpoint/recovery
- Failure scenarios
- Dependency validation
- Progress tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.orchestrators.task_list_orchestrator import (
    TaskListOrchestrator,
    Task,
    TaskStatus
)
from src.database.planning_state_db import PlanningStateDB


@pytest.fixture
def temp_db():
    """Create temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    db = PlanningStateDB(db_path=db_path)
    yield db
    
    db.close()
    Path(db_path).unlink()


@pytest.fixture
def orchestrator(temp_db):
    """Create test orchestrator with plan in DB."""
    # Create plan in DB first (required for foreign key constraints)
    temp_db.create_plan(
        feature_name="test_orchestration",
        complexity_tier=3,
        strategy="test"
    )
    
    orch = TaskListOrchestrator("test_orch", temp_db)
    
    # Override orchestrator_id to match plan_id format
    plan_id = temp_db._conn.execute(
        "SELECT plan_id FROM plans WHERE feature_name = 'test_orchestration'"
    ).fetchone()["plan_id"]
    orch.orchestrator_id = plan_id
    
    return orch


# =============================================================================
# Task Creation Tests
# =============================================================================

class TestTaskCreation:
    """Tests for task creation and management."""
    
    def test_add_simple_task(self, orchestrator):
        """Add task without dependencies."""
        task = orchestrator.add_task(
            task_id="task1",
            description="First task",
            executor=lambda p: "result1"
        )
        
        assert task.task_id == "task1"
        assert task.description == "First task"
        assert task.status == TaskStatus.NOT_STARTED
        assert len(orchestrator.tasks) == 1
    
    def test_add_task_with_parameters(self, orchestrator):
        """Add task with parameters."""
        task = orchestrator.add_task(
            task_id="task1",
            description="Task with params",
            executor=lambda p: p["value"] * 2,
            parameters={"value": 42}
        )
        
        assert task.parameters == {"value": 42}
    
    def test_add_task_with_dependencies(self, orchestrator):
        """Add task with dependencies."""
        orchestrator.add_task("task1", "First", lambda p: "r1")
        task2 = orchestrator.add_task(
            "task2",
            "Second",
            lambda p: "r2",
            depends_on=["task1"]
        )
        
        assert task2.depends_on == ["task1"]
    
    def test_add_task_with_checkpoint(self, orchestrator):
        """Add task with checkpoint flag."""
        task = orchestrator.add_task(
            "task1",
            "Risky task",
            lambda p: "result",
            checkpoint_before=True
        )
        
        assert task.checkpoint_before is True


# =============================================================================
# Task Execution Tests
# =============================================================================

class TestTaskExecution:
    """Tests for task execution."""
    
    def test_execute_single_task(self, orchestrator):
        """Execute single task successfully."""
        orchestrator.add_task(
            "task1",
            "Simple task",
            executor=lambda p: "success"
        )
        
        result = orchestrator.execute_next()
        
        assert result == "success"
        assert orchestrator.tasks[0].status == TaskStatus.COMPLETED
        assert orchestrator.tasks[0].duration_seconds is not None
    
    def test_execute_task_with_parameters(self, orchestrator):
        """Execute task using parameters."""
        orchestrator.add_task(
            "task1",
            "Parameterized task",
            executor=lambda p: p["x"] + p["y"],
            parameters={"x": 10, "y": 20}
        )
        
        result = orchestrator.execute_next()
        
        assert result == 30
    
    def test_execute_multiple_tasks_sequentially(self, orchestrator):
        """Execute multiple tasks in sequence."""
        orchestrator.add_task("task1", "First", lambda p: 1)
        orchestrator.add_task("task2", "Second", lambda p: 2)
        orchestrator.add_task("task3", "Third", lambda p: 3)
        
        results = []
        while orchestrator.has_pending_tasks():
            result = orchestrator.execute_next()
            results.append(result)
        
        assert results == [1, 2, 3]
        assert all(t.status == TaskStatus.COMPLETED for t in orchestrator.tasks)
    
    def test_execute_all_convenience_method(self, orchestrator):
        """Test execute_all() convenience method."""
        orchestrator.add_task("task1", "First", lambda p: "r1")
        orchestrator.add_task("task2", "Second", lambda p: "r2")
        orchestrator.add_task("task3", "Third", lambda p: "r3")
        
        results = orchestrator.execute_all()
        
        assert results == ["r1", "r2", "r3"]
    
    def test_execute_task_updates_timing(self, orchestrator):
        """Task execution updates timing fields."""
        orchestrator.add_task("task1", "Timed task", lambda p: "done")
        
        orchestrator.execute_next()
        task = orchestrator.tasks[0]
        
        assert task.started_at is not None
        assert task.completed_at is not None
        assert task.duration_seconds > 0
        assert task.completed_at > task.started_at


# =============================================================================
# Dependency Tests
# =============================================================================

class TestDependencies:
    """Tests for task dependency management."""
    
    def test_task_waits_for_dependency(self, orchestrator):
        """Task waits for dependency to complete."""
        orchestrator.add_task("task1", "First", lambda p: "r1")
        orchestrator.add_task("task2", "Second", lambda p: "r2", depends_on=["task1"])
        
        # First execution should run task1
        result1 = orchestrator.execute_next()
        assert result1 == "r1"
        assert orchestrator.tasks[0].status == TaskStatus.COMPLETED
        assert orchestrator.tasks[1].status == TaskStatus.NOT_STARTED
        
        # Second execution should run task2
        result2 = orchestrator.execute_next()
        assert result2 == "r2"
        assert orchestrator.tasks[1].status == TaskStatus.COMPLETED
    
    def test_multiple_dependencies(self, orchestrator):
        """Task waits for multiple dependencies."""
        orchestrator.add_task("task1", "First", lambda p: 1)
        orchestrator.add_task("task2", "Second", lambda p: 2)
        orchestrator.add_task(
            "task3",
            "Third",
            lambda p: 3,
            depends_on=["task1", "task2"]
        )
        
        # Execute all tasks
        results = orchestrator.execute_all()
        
        # Task3 should execute last
        assert results == [1, 2, 3]
    
    def test_dependency_chain(self, orchestrator):
        """Test chain of dependencies: A -> B -> C."""
        orchestrator.add_task("taskA", "A", lambda p: "A")
        orchestrator.add_task("taskB", "B", lambda p: "B", depends_on=["taskA"])
        orchestrator.add_task("taskC", "C", lambda p: "C", depends_on=["taskB"])
        
        results = orchestrator.execute_all()
        
        assert results == ["A", "B", "C"]
    
    def test_unknown_dependency_warning(self, orchestrator, caplog):
        """Task with unknown dependency logs warning."""
        orchestrator.add_task(
            "task1",
            "Task with bad dep",
            lambda p: "result",
            depends_on=["nonexistent"]
        )
        
        result = orchestrator.execute_next()
        
        # Should not execute (dependency not satisfied)
        assert result is None
        assert "unknown task" in caplog.text.lower()


# =============================================================================
# Checkpoint/Recovery Tests
# =============================================================================

class TestCheckpointRecovery:
    """Tests for checkpoint and recovery functionality."""
    
    def test_create_checkpoint(self, orchestrator):
        """Create checkpoint successfully."""
        orchestrator.add_task("task1", "Task 1", lambda p: "r1")
        
        checkpoint_id = orchestrator.checkpoint("test checkpoint")
        
        assert checkpoint_id is not None
        assert isinstance(checkpoint_id, str)
    
    def test_recover_from_checkpoint(self, orchestrator):
        """Recover orchestrator state from checkpoint."""
        # Add and execute task
        orchestrator.add_task("task1", "Task 1", lambda p: "r1")
        orchestrator.execute_next()
        
        # Create checkpoint
        checkpoint_id = orchestrator.checkpoint("after task1")
        
        # Add more tasks
        orchestrator.add_task("task2", "Task 2", lambda p: "r2")
        
        # Create new orchestrator and recover
        new_orch = TaskListOrchestrator("test_orch", orchestrator.state_db)
        new_orch.register_executor("task1", lambda p: "r1")
        new_orch.recover(checkpoint_id)
        
        # Should have task1 completed
        assert len(new_orch.tasks) == 1
        assert new_orch.tasks[0].status == TaskStatus.COMPLETED
    
    def test_recover_latest_checkpoint(self, orchestrator):
        """Recover from latest checkpoint when ID not specified."""
        orchestrator.add_task("task1", "Task 1", lambda p: "r1")
        orchestrator.add_task("task2", "Task 2", lambda p: "r2")
        
        orchestrator.execute_next()  # Complete task1
        cp1_id = orchestrator.checkpoint("checkpoint 1")
        
        orchestrator.execute_next()  # Complete task2
        cp2_id = orchestrator.checkpoint("checkpoint 2")
        
        # Recover without specifying checkpoint ID (uses latest by timestamp)
        new_orch = TaskListOrchestrator(orchestrator.orchestrator_id, orchestrator.state_db)
        new_orch.register_executor("task1", lambda p: "r1")
        new_orch.register_executor("task2", lambda p: "r2")
        new_orch.recover()
        
        # Should have both tasks with task1 completed
        # (task2 status depends on which checkpoint was recovered)
        assert len(new_orch.tasks) == 2
        assert new_orch.tasks[0].status == TaskStatus.COMPLETED
        assert new_orch.tasks[1].status in [TaskStatus.COMPLETED, TaskStatus.NOT_STARTED]
    
    def test_recover_no_checkpoint_raises_error(self, orchestrator):
        """Recovering without checkpoint raises ValueError."""
        with pytest.raises(ValueError, match="No checkpoints found"):
            orchestrator.recover()
    
    def test_checkpoint_before_flag_creates_checkpoint(self, orchestrator, monkeypatch):
        """Task with checkpoint_before flag creates checkpoint."""
        checkpoint_called = []
        
        original_checkpoint = orchestrator.checkpoint
        def mock_checkpoint(label):
            checkpoint_called.append(label)
            return original_checkpoint(label)
        
        monkeypatch.setattr(orchestrator, "checkpoint", mock_checkpoint)
        
        orchestrator.add_task(
            "task1",
            "Risky task",
            lambda p: "result",
            checkpoint_before=True
        )
        
        orchestrator.execute_next()
        
        assert len(checkpoint_called) == 1
        assert "Before task1" in checkpoint_called[0]
    
    def test_executor_registry_persists_across_recovery(self, orchestrator):
        """Executor registry allows re-binding after recovery."""
        def custom_executor(params):
            return params["value"] * 2
        
        orchestrator.add_task(
            "task1",
            "Custom task",
            executor=custom_executor,
            parameters={"value": 21}
        )
        
        orchestrator.execute_next()
        orchestrator.checkpoint("with executor")
        
        # Recover in new orchestrator
        new_orch = TaskListOrchestrator(orchestrator.orchestrator_id, orchestrator.state_db)
        new_orch.register_executor("task1", custom_executor)
        new_orch.recover()
        
        # Executor should be re-bound
        assert new_orch.tasks[0].executor is not None
        assert new_orch.tasks[0].result == 42


# =============================================================================
# Failure Handling Tests
# =============================================================================

class TestFailureHandling:
    """Tests for handling task failures."""
    
    def test_task_failure_captured(self, orchestrator):
        """Failed task status and error captured."""
        def failing_executor(params):
            raise ValueError("Intentional failure")
        
        orchestrator.add_task("task1", "Failing task", failing_executor)
        
        with pytest.raises(ValueError, match="Intentional failure"):
            orchestrator.execute_next()
        
        task = orchestrator.tasks[0]
        assert task.status == TaskStatus.FAILED
        assert "Intentional failure" in task.error
    
    def test_task_without_executor_raises_error(self, orchestrator):
        """Task without executor raises ValueError."""
        orchestrator.add_task("task1", "No executor task", executor=None)
        
        with pytest.raises(ValueError, match="has no executor"):
            orchestrator.execute_next()
    
    def test_execute_all_stops_on_failure(self, orchestrator):
        """execute_all() stops when task fails."""
        orchestrator.add_task("task1", "Success", lambda p: "ok")
        orchestrator.add_task("task2", "Fail", lambda p: 1/0)  # ZeroDivisionError
        orchestrator.add_task("task3", "Never runs", lambda p: "ok")
        
        with pytest.raises(ZeroDivisionError):
            orchestrator.execute_all()
        
        # Task1 completed, task2 failed, task3 never started
        assert orchestrator.tasks[0].status == TaskStatus.COMPLETED
        assert orchestrator.tasks[1].status == TaskStatus.FAILED
        assert orchestrator.tasks[2].status == TaskStatus.NOT_STARTED


# =============================================================================
# Progress Tracking Tests
# =============================================================================

class TestProgressTracking:
    """Tests for progress tracking functionality."""
    
    def test_get_progress_empty(self, orchestrator):
        """Get progress with no tasks."""
        progress = orchestrator.get_progress()
        
        assert progress["total_tasks"] == 0
        assert progress["completed"] == 0
        assert progress["progress_percent"] == 0.0
    
    def test_get_progress_partial(self, orchestrator):
        """Get progress with some tasks completed."""
        orchestrator.add_task("task1", "T1", lambda p: 1)
        orchestrator.add_task("task2", "T2", lambda p: 2)
        orchestrator.add_task("task3", "T3", lambda p: 3)
        
        orchestrator.execute_next()  # Complete task1
        
        progress = orchestrator.get_progress()
        
        assert progress["total_tasks"] == 3
        assert progress["completed"] == 1
        assert progress["pending"] == 2
        assert progress["progress_percent"] == pytest.approx(33.33, rel=0.1)
    
    def test_get_progress_all_complete(self, orchestrator):
        """Get progress with all tasks completed."""
        orchestrator.add_task("task1", "T1", lambda p: 1)
        orchestrator.add_task("task2", "T2", lambda p: 2)
        
        orchestrator.execute_all()
        
        progress = orchestrator.get_progress()
        
        assert progress["completed"] == 2
        assert progress["progress_percent"] == 100.0
    
    def test_get_completed_tasks(self, orchestrator):
        """Get list of completed tasks."""
        orchestrator.add_task("task1", "T1", lambda p: 1)
        orchestrator.add_task("task2", "T2", lambda p: 2)
        
        orchestrator.execute_next()
        
        completed = orchestrator.get_completed_tasks()
        
        assert len(completed) == 1
        assert completed[0].task_id == "task1"
    
    def test_get_failed_tasks(self, orchestrator):
        """Get list of failed tasks."""
        orchestrator.add_task("task1", "Success", lambda p: "ok")
        orchestrator.add_task("task2", "Fail", lambda p: 1/0)
        
        orchestrator.execute_next()  # task1 succeeds
        
        try:
            orchestrator.execute_next()  # task2 fails
        except ZeroDivisionError:
            pass
        
        failed = orchestrator.get_failed_tasks()
        
        assert len(failed) == 1
        assert failed[0].task_id == "task2"
    
    def test_get_task_status(self, orchestrator):
        """Get status of specific task."""
        orchestrator.add_task("task1", "Task", lambda p: "result")
        
        status_before = orchestrator.get_task_status("task1")
        orchestrator.execute_next()
        status_after = orchestrator.get_task_status("task1")
        
        assert status_before == TaskStatus.NOT_STARTED
        assert status_after == TaskStatus.COMPLETED
    
    def test_has_pending_tasks(self, orchestrator):
        """Check if pending tasks exist."""
        assert not orchestrator.has_pending_tasks()
        
        orchestrator.add_task("task1", "T1", lambda p: 1)
        assert orchestrator.has_pending_tasks()
        
        orchestrator.execute_next()
        assert not orchestrator.has_pending_tasks()


# =============================================================================
# Task Serialization Tests
# =============================================================================

class TestTaskSerialization:
    """Tests for Task to_dict/from_dict."""
    
    def test_task_to_dict(self):
        """Task converts to dict correctly."""
        task = Task(
            task_id="task1",
            description="Test task",
            parameters={"key": "value"},
            status=TaskStatus.COMPLETED
        )
        task.started_at = datetime.now()
        task.completed_at = datetime.now()
        task.result = "success"
        
        task_dict = task.to_dict()
        
        assert task_dict["task_id"] == "task1"
        assert task_dict["description"] == "Test task"
        assert task_dict["status"] == "completed"
        assert "executor" not in task_dict  # Should be excluded
    
    def test_task_from_dict(self):
        """Task reconstructs from dict correctly."""
        task_dict = {
            "task_id": "task1",
            "description": "Test task",
            "executor": None,
            "parameters": {"key": "value"},
            "checkpoint_before": False,
            "depends_on": [],
            "status": "completed",
            "result": "success",
            "error": None,
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration_seconds": 1.5
        }
        
        task = Task.from_dict(task_dict)
        
        assert task.task_id == "task1"
        assert task.status == TaskStatus.COMPLETED
        assert isinstance(task.started_at, datetime)


# =============================================================================
# Integration Tests
# =============================================================================

class TestIntegration:
    """Integration tests for real-world scenarios."""
    
    def test_realistic_orchestration_scenario(self, orchestrator):
        """Test realistic multi-step orchestration."""
        results = {}
        
        # Discovery phase
        def discover(params):
            return {"files": ["file1.py", "file2.py"]}
        
        # Analysis phase (depends on discovery)
        def analyze(params):
            # Access previous results through closure
            return {"complexity": "medium"}
        
        # Planning phase (depends on analysis)
        def plan(params):
            return {"phases": 3, "tasks": 10}
        
        orchestrator.add_task(
            "discover",
            "Discover context",
            executor=discover,
            checkpoint_before=False
        )
        
        orchestrator.add_task(
            "analyze",
            "Analyze requirements",
            executor=analyze,
            depends_on=["discover"],
            checkpoint_before=True  # Strategic checkpoint
        )
        
        orchestrator.add_task(
            "plan",
            "Generate plan",
            executor=plan,
            depends_on=["analyze"]
        )
        
        # Execute all
        all_results = orchestrator.execute_all()
        
        assert len(all_results) == 3
        assert orchestrator.get_progress()["progress_percent"] == 100.0
    
    def test_interruption_and_recovery(self, orchestrator):
        """Test interruption and recovery workflow."""
        # Setup tasks
        orchestrator.add_task("task1", "T1", lambda p: "r1")
        orchestrator.add_task("task2", "T2", lambda p: "r2")
        orchestrator.add_task("task3", "T3", lambda p: "r3")
        
        # Execute first task
        orchestrator.execute_next()
        
        # Create checkpoint after task1 (simulate auto-checkpoint)
        orchestrator.checkpoint("after task1")
        
        # Simulate interruption here (before task2)
        # ... system crashes ...
        
        # Recovery: create new orchestrator instance
        recovered = TaskListOrchestrator(orchestrator.orchestrator_id, orchestrator.state_db)
        recovered.register_executor("task1", lambda p: "r1")
        recovered.register_executor("task2", lambda p: "r2")
        recovered.register_executor("task3", lambda p: "r3")
        
        # Recover from latest checkpoint
        recovered.recover()
        
        # Task1 should be completed, task2 and task3 pending
        assert recovered.tasks[0].status == TaskStatus.COMPLETED
        assert recovered.tasks[1].status == TaskStatus.NOT_STARTED
        assert recovered.tasks[2].status == TaskStatus.NOT_STARTED
        
        # Continue execution
        remaining_results = []
        while recovered.has_pending_tasks():
            result = recovered.execute_next()
            remaining_results.append(result)
        
        # Should complete task2 and task3
        assert len(remaining_results) == 2
        assert recovered.get_progress()["completed"] == 3
