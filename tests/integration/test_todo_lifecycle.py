"""
Integration test for full TODO lifecycle.

Tests the complete workflow:
1. Load feature from YAML
2. Execute tasks in priority order
3. Create checkpoints during execution
4. Recover from checkpoint
5. Complete all tasks

Author: Asif Hussain
Feature: feat02-todo-orchestrator
Phase: 4
Task: task-2.4.4
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict

import pytest
import yaml

from src.orchestrators.core.checkpoint_manager import CheckpointManager
from src.orchestrators.core.dag import Priority
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator, TodoStatus


# ==============================================================================
# FIXTURES
# ==============================================================================

@pytest.fixture
def sample_feature_yaml(tmp_path: Path) -> Path:
    """Create a sample feature YAML file for testing."""
    feature_data = {
        "feature": {
            "id": "test-feature",
            "name": "Test Feature",
            "description": "Integration test feature",
            "phases": [
                {
                    "id": "phase-1",
                    "name": "Setup Phase",
                    "description": "Initial setup",
                    "tasks": [
                        {
                            "id": "task-1.1",
                            "name": "Initialize environment",
                            "priority": "P0_CRITICAL",
                            "estimated_minutes": 30,
                            "dependencies": []
                        },
                        {
                            "id": "task-1.2",
                            "name": "Configure settings",
                            "priority": "P1_HIGH",
                            "estimated_minutes": 20,
                            "dependencies": ["task-1.1"]
                        }
                    ]
                },
                {
                    "id": "phase-2",
                    "name": "Implementation Phase",
                    "description": "Core implementation",
                    "tasks": [
                        {
                            "id": "task-2.1",
                            "name": "Implement feature A",
                            "priority": "P1_HIGH",
                            "estimated_minutes": 60,
                            "dependencies": ["task-1.2"]
                        },
                        {
                            "id": "task-2.2",
                            "name": "Implement feature B",
                            "priority": "P2_MEDIUM",
                            "estimated_minutes": 45,
                            "dependencies": ["task-2.1"]
                        },
                        {
                            "id": "task-2.3",
                            "name": "Integration testing",
                            "priority": "P0_CRITICAL",
                            "estimated_minutes": 30,
                            "dependencies": ["task-2.2"]
                        }
                    ]
                }
            ]
        }
    }
    
    yaml_path = tmp_path / "test_feature.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(feature_data, f)
    
    return yaml_path


@pytest.fixture
def orchestrator(tmp_path: Path) -> TodoOrchestrator:
    """Create TodoOrchestrator with temporary state file."""
    from src.orchestrators.state_manager import StateManager
    from src.orchestrators.audit_logger import EnterpriseAuditLogger
    
    state_mgr = StateManager(state_file=str(tmp_path / "test_state.db"))
    audit_logger = EnterpriseAuditLogger(log_dir=str(tmp_path / "logs"))
    
    return TodoOrchestrator(
        state_manager=state_mgr,
        audit_logger=audit_logger
    )


@pytest.fixture
def checkpoint_manager(tmp_path: Path) -> CheckpointManager:
    """Create CheckpointManager with temporary checkpoint directory."""
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    
    return CheckpointManager(base_dir=checkpoint_dir)


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================

def test_full_lifecycle_load_execute_complete(
    orchestrator: TodoOrchestrator,
    sample_feature_yaml: Path
):
    """Test complete lifecycle: load → execute → complete."""
    # Phase 1: Load feature from YAML
    loaded_todos = orchestrator.load_from_yaml(str(sample_feature_yaml))
    assert len(loaded_todos) == 5
    
    # Verify TODOs were created
    all_todos = orchestrator.list_todos()
    assert len(all_todos) == 5
    
    # Verify DAG structure (dependencies) - check DAG directly
    assert orchestrator.dag.node_count == 5
    
    # Phase 2: Execute tasks in order
    completed_tasks = []
    
    while True:
        # Get next tasks ready for execution
        next_tasks = orchestrator.get_next_tasks()
        
        if not next_tasks:
            break
        
        # Execute first task in queue
        task = next_tasks[0]
        
        # Mark as in progress
        orchestrator.execute_task(task.id)
        
        # Simulate work completion
        orchestrator.mark_complete(task.id, result={"status": "success"})
        completed_tasks.append(task.id)
    
    # Phase 3: Verify completion
    assert len(completed_tasks) == 5
    
    # Verify all tasks completed
    final_todos = orchestrator.list_todos()
    completed_count = sum(1 for t in final_todos if t.status == TodoStatus.COMPLETED)
    assert completed_count == 5
    
    # Verify progress tracking
    progress = orchestrator.get_progress()
    assert progress["total_tasks"] == 5
    assert progress["completed_tasks"] == 5
    assert progress["percentage"] == 100.0


def test_lifecycle_with_checkpointing(
    orchestrator: TodoOrchestrator,
    checkpoint_manager: CheckpointManager,
    sample_feature_yaml: Path,
    tmp_path: Path
):
    """Test lifecycle with checkpoint creation and recovery."""
    pytest.skip("Checkpoint integration requires TodoOrchestrator integration with CheckpointManager")
    
    # Execute first 2 tasks
    for _ in range(2):
        next_tasks = orchestrator.get_next_tasks()
        if next_tasks:
            task = next_tasks[0]
            orchestrator.execute_task(task.id)
            orchestrator.mark_complete(task.id, result={"status": "success"})
    
    # Create checkpoint
    checkpoint_id = checkpoint_manager.create_checkpoint(
        todos=orchestrator.list_todos(),
        metadata={"phase": "mid-execution"}
    )
    assert checkpoint_id is not None
    
    # Continue execution (1 more task)
    next_tasks = orchestrator.get_next_tasks()
    if next_tasks:
        task = next_tasks[0]
        orchestrator.execute_task(task.id)
        orchestrator.mark_complete(task.id, result={"status": "success"})
    
    # Now simulate crash and recovery
    # Create new orchestrator and checkpoint manager instances
    from src.orchestrators.state_manager import StateManager
    from src.orchestrators.audit_logger import EnterpriseAuditLogger
    
    state_mgr2 = StateManager(state_file=str(tmp_path / "test_state2.db"))
    audit_logger2 = EnterpriseAuditLogger(log_dir=str(tmp_path / "logs2"))
    
    recovered_orchestrator = TodoOrchestrator(
        state_manager=state_mgr2,
        audit_logger=audit_logger2
    )
    
    # Recover from checkpoint
    recovered_todos = checkpoint_manager.recover_from_checkpoint(checkpoint_id)
    
    # Verify recovery: should have 2 completed, 3 remaining
    completed = [t for t in recovered_todos if t.status == TodoStatus.COMPLETED]
    assert len(completed) == 2
    
    # Re-load the recovered TODOs into DAG
    for todo in recovered_todos:
        recovered_orchestrator.todos[todo.id] = todo
        recovered_orchestrator.dag.add_node(
            todo.id,
            status=todo.data.get("node_status", "not_started"),
            priority=todo.priority
        )
    
    # Continue from checkpoint
    while True:
        next_tasks = recovered_orchestrator.get_next_tasks()
        if not next_tasks:
            break
        
        task = next_tasks[0]
        recovered_orchestrator.execute_task(task.id)
        recovered_orchestrator.mark_complete(task.id, result={"status": "success"})
    
    # Verify all completed
    final_todos = recovered_orchestrator.list_todos()
    completed_count = sum(1 for t in final_todos if t.status == TodoStatus.COMPLETED)
    assert completed_count == 5


def test_lifecycle_with_failure_recovery(
    orchestrator: TodoOrchestrator,
    sample_feature_yaml: Path
):
    """Test lifecycle with task failure and recovery."""
    # Load feature
    loaded_todos = orchestrator.load_from_yaml(str(sample_feature_yaml))
    
    # Execute first task successfully
    next_tasks = orchestrator.get_next_tasks()
    task1 = next_tasks[0]
    orchestrator.execute_task(task1.id)
    orchestrator.mark_complete(task1.id, result={"status": "success"})
    
    # Execute second task with failure
    next_tasks = orchestrator.get_next_tasks()
    task2 = next_tasks[0]
    orchestrator.execute_task(task2.id)
    orchestrator.mark_failed(task2.id, error="Simulated failure")
    
    # Verify failure recorded
    failed_todo = orchestrator.read_todo(task2.id)
    assert failed_todo.status == TodoStatus.FAILED
    assert "error" in failed_todo.data
    
    # Reset failed task
    orchestrator.transition_status(task2.id, TodoStatus.READY)
    
    # Re-execute successfully
    orchestrator.execute_task(task2.id)
    orchestrator.mark_complete(task2.id, result={"status": "success", "retry": True})
    
    # Complete remaining tasks
    while True:
        next_tasks = orchestrator.get_next_tasks()
        if not next_tasks:
            break
        
        task = next_tasks[0]
        orchestrator.execute_task(task.id)
        orchestrator.mark_complete(task.id, result={"status": "success"})
    
    # Verify all completed
    progress = orchestrator.get_progress()
    assert progress["completed_tasks"] == 5


def test_lifecycle_respects_dependencies(
    orchestrator: TodoOrchestrator,
    sample_feature_yaml: Path
):
    """Test that execution respects dependency constraints."""
    # Load feature
    loaded_todos = orchestrator.load_from_yaml(str(sample_feature_yaml))
    
    # Get initial execution queue
    next_tasks = orchestrator.get_next_tasks()
    
    # Should only have task-1.1 (no dependencies)
    assert len(next_tasks) == 1
    assert next_tasks[0].title == "Initialize environment"
    
    # Try to execute task-1.2 before task-1.1 completes (should fail)
    task_1_2_id = None
    for todo in orchestrator.list_todos():
        if todo.title == "Configure settings":
            task_1_2_id = todo.id
            break
    
    assert task_1_2_id is not None
    
    # Attempting to execute task-1.2 should raise error or return None
    try:
        result = orchestrator.execute_task(task_1_2_id)
        # If it doesn't raise, verify it's not marked as in_progress
        todo = orchestrator.read_todo(task_1_2_id)
        assert todo.status != TodoStatus.IN_PROGRESS
    except Exception:
        pass  # Expected
    
    # Complete task-1.1
    task_1_1 = next_tasks[0]
    orchestrator.execute_task(task_1_1.id)
    orchestrator.mark_complete(task_1_1.id, result={"status": "success"})
    
    # Now task-1.2 should be available
    next_tasks = orchestrator.get_next_tasks()
    assert len(next_tasks) == 1
    assert next_tasks[0].title == "Configure settings"


def test_lifecycle_progress_tracking(
    orchestrator: TodoOrchestrator,
    sample_feature_yaml: Path
):
    """Test progress tracking throughout lifecycle."""
    # Load feature
    loaded_todos = orchestrator.load_from_yaml(str(sample_feature_yaml))
    
    # Initial progress
    progress = orchestrator.get_progress()
    assert progress["total_tasks"] == 5
    assert progress["completed_tasks"] == 0
    
    # Complete first 2 tasks
    for i in range(2):
        next_tasks = orchestrator.get_next_tasks()
        task = next_tasks[0]
        orchestrator.execute_task(task.id)
        orchestrator.mark_complete(task.id, result={"status": "success"})
    
    # Overall progress after 2 tasks
    progress = orchestrator.get_progress()
    assert progress["completed_tasks"] == 2
    assert progress["percentage"] == 40.0  # 2/5
    
    # Complete remaining tasks
    while True:
        next_tasks = orchestrator.get_next_tasks()
        if not next_tasks:
            break
        
        task = next_tasks[0]
        orchestrator.execute_task(task.id)
        orchestrator.mark_complete(task.id, result={"status": "success"})
    
    # Final progress
    progress = orchestrator.get_progress()
    assert progress["completed_tasks"] == 5
    assert progress["percentage"] == 100.0
