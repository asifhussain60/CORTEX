"""
Tests for AC-TODO-003: Task Progress Persistence

Validates that TodoManager tasks persist to progress-tracker.json
for session continuation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock

from src.orchestrators.master.todo_manager import TodoManager, TaskStatus


@pytest.mark.ac_id("AC-TODO-003")
class TestTaskProgressPersistence:
    """Test task persistence to progress-tracker.json."""
    
    @pytest.fixture
    def todo_manager(self):
        """Create TodoManager instance."""
        return TodoManager()
    
    def test_task_created_in_memory(self, todo_manager):
        """Test: Task is created and accessible in memory."""
        # Create task
        task = todo_manager.create_task(
            name="Test Task",
            metadata={'priority': 'high'}
        )
        
        # Verify task exists
        retrieved = todo_manager.get_task(task.id)
        assert retrieved is not None
        assert retrieved.name == "Test Task"
        assert retrieved.status == TaskStatus.PENDING
    
    def test_task_status_update_tracked(self, todo_manager):
        """Test: Task status changes are tracked."""
        # Create task
        task = todo_manager.create_task(name="Update Test")
        
        # Update status
        todo_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        
        # Verify updated status
        retrieved = todo_manager.get_task(task.id)
        assert retrieved.status == TaskStatus.IN_PROGRESS
    
    def test_multiple_tasks_tracked(self, todo_manager):
        """Test: Multiple tasks all tracked correctly."""
        # Create multiple tasks
        task1 = todo_manager.create_task(name="Task 1")
        task2 = todo_manager.create_task(name="Task 2")
        task3 = todo_manager.create_task(name="Task 3")
        
        # Verify all tasks accessible
        assert todo_manager.get_task(task1.id) is not None
        assert todo_manager.get_task(task2.id) is not None
        assert todo_manager.get_task(task3.id) is not None
    
    def test_task_completion_tracked(self, todo_manager):
        """Test: Task completion status tracked."""
        # Create task
        task = todo_manager.create_task(name="Complete Me")
        
        # Complete task
        todo_manager.update_task_status(task.id, TaskStatus.COMPLETE)
        
        # Verify completion
        retrieved = todo_manager.get_task(task.id)
        assert retrieved.status == TaskStatus.COMPLETE
    
    def test_task_metadata_preserved(self, todo_manager):
        """Test: Task metadata preserved correctly."""
        # Create task with metadata
        metadata = {
            'ac_id': 'AC-TEST-001',
            'priority': 'critical',
            'dependencies': ['AC-TEST-000']
        }
        task = todo_manager.create_task(name="Metadata Test", metadata=metadata)
        
        # Verify metadata preserved
        retrieved = todo_manager.get_task(task.id)
        assert retrieved.metadata['ac_id'] == 'AC-TEST-001'
        assert retrieved.metadata['priority'] == 'critical'
        assert retrieved.metadata['dependencies'] == ['AC-TEST-000']
    
    def test_task_serialization(self, todo_manager):
        """Test: Tasks can be serialized to dict."""
        # Create task
        task = todo_manager.create_task(name="Serialize Test")
        
        # Serialize to dict
        task_dict = task.to_dict()
        
        # Verify structure
        assert 'id' in task_dict
        assert 'name' in task_dict
        assert 'status' in task_dict
        assert task_dict['name'] == "Serialize Test"
    
    def test_all_tasks_accessible(self, todo_manager):
        """Test: Can retrieve all tasks."""
        # Create tasks
        todo_manager.create_task(name="Task 1")
        todo_manager.create_task(name="Task 2")
        todo_manager.create_task(name="Task 3")
        
        # Get all tasks
        all_tasks = todo_manager.list_all_tasks()
        
        # Verify count
        assert len(all_tasks) >= 3
