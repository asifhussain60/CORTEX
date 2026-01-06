"""
Integration Test: TodoManager with manage_todo_list

Verifies TodoManager can integrate with GitHub Copilot's manage_todo_list tool.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from src.orchestrators.master import TodoManager, Task


def test_todo_manager_creation(tmp_path):
    """Test TodoManager initialization."""
    manager = TodoManager(plan_dir=tmp_path)
    assert manager.registry_path.exists()
    assert len(manager.tasks) == 0


def test_create_and_retrieve_task(tmp_path):
    """Test creating and retrieving tasks."""
    manager = TodoManager(plan_dir=tmp_path)
    
    task_id = manager.create_task(
        title="Test Task",
        description="This is a test task",
        priority=1
    )
    
    assert task_id == 1
    task = manager.get_task(task_id)
    assert task is not None
    assert task.title == "Test Task"
    assert task.status == "not-started"


def test_task_status_workflow(tmp_path):
    """Test task status transitions."""
    manager = TodoManager(plan_dir=tmp_path)
    
    task_id = manager.create_task("Workflow Test", "Test status changes")
    
    # not-started → in-progress
    assert manager.start_task(task_id)
    task = manager.get_task(task_id)
    assert task.status == "in-progress"
    
    # in-progress → completed
    assert manager.complete_task(task_id)
    task = manager.get_task(task_id)
    assert task.status == "completed"
    assert task.completed_at is not None


def test_copilot_format(tmp_path):
    """Test GitHub Copilot format conversion."""
    manager = TodoManager(plan_dir=tmp_path)
    
    manager.create_task("Task 1", "First task", status="completed")
    manager.create_task("Task 2", "Second task", status="in-progress")
    manager.create_task("Task 3", "Third task", status="not-started")
    
    copilot_tasks = manager.get_copilot_format()
    
    assert len(copilot_tasks) == 3
    assert all('id' in t for t in copilot_tasks)
    assert all('title' in t for t in copilot_tasks)
    assert all('description' in t for t in copilot_tasks)
    assert all('status' in t for t in copilot_tasks)
    
    # Verify status values
    statuses = [t['status'] for t in copilot_tasks]
    assert 'completed' in statuses
    assert 'in-progress' in statuses
    assert 'not-started' in statuses


def test_progress_summary(tmp_path):
    """Test progress summary calculation."""
    manager = TodoManager(plan_dir=tmp_path)
    
    manager.create_task("Task 1", "Desc 1", status="completed")
    manager.create_task("Task 2", "Desc 2", status="completed")
    manager.create_task("Task 3", "Desc 3", status="in-progress")
    manager.create_task("Task 4", "Desc 4", status="not-started")
    
    summary = manager.get_progress_summary()
    
    assert summary['total_tasks'] == 4
    assert summary['completed'] == 2
    assert summary['in_progress'] == 1
    assert summary['not_started'] == 1
    assert summary['progress_percentage'] == 50.0


def test_task_dependencies(tmp_path):
    """Test task dependency tracking."""
    manager = TodoManager(plan_dir=tmp_path)
    
    task1_id = manager.create_task("Setup", "Setup environment")
    task2_id = manager.create_task("Build", "Build project", dependencies=[task1_id])
    
    task2 = manager.get_task(task2_id)
    assert task1_id in task2.dependencies


def test_persistence(tmp_path):
    """Test task persistence across manager instances."""
    # Create and save tasks
    manager1 = TodoManager(plan_dir=tmp_path)
    manager1.create_task("Persistent Task", "Should survive reload")
    
    # Load in new instance
    manager2 = TodoManager(plan_dir=tmp_path)
    assert len(manager2.tasks) == 1
    task = manager2.get_task(1)
    assert task.title == "Persistent Task"


def test_list_tasks_filtering(tmp_path):
    """Test task listing with filters."""
    manager = TodoManager(plan_dir=tmp_path)
    
    manager.create_task("High Priority", "Urgent", priority=1, status="completed")
    manager.create_task("Medium Priority", "Normal", priority=2, status="in-progress")
    manager.create_task("Low Priority", "Later", priority=3, status="not-started")
    
    # Filter by status
    in_progress = manager.list_tasks(status="in-progress")
    assert len(in_progress) == 1
    assert in_progress[0].title == "Medium Priority"
    
    # Filter by priority
    high_priority = manager.list_tasks(priority=1)
    assert len(high_priority) == 1
    assert high_priority[0].title == "High Priority"


def test_clear_completed(tmp_path):
    """Test clearing completed tasks."""
    manager = TodoManager(plan_dir=tmp_path)
    
    manager.create_task("Done 1", "Finished", status="completed")
    manager.create_task("Done 2", "Finished", status="completed")
    manager.create_task("Active", "Still working", status="in-progress")
    
    cleared_count = manager.clear_completed()
    
    assert cleared_count == 2
    assert len(manager.tasks) == 1
    assert manager.get_task(3).title == "Active"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
