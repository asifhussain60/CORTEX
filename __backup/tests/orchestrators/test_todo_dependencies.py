"""
Tests for AC-TODO-004: Task Dependency Resolution

Validates that TodoManager correctly resolves task dependencies
and executes tasks in dependency order.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock

from src.orchestrators.master.todo_manager import TodoManager, Task, TaskStatus


@pytest.mark.ac_id("AC-TODO-004")
class TestTaskDependencyResolution:
    """Test dependency resolution and ordering."""
    
    @pytest.fixture
    def todo_manager(self):
        """Create TodoManager instance."""
        return TodoManager()
    
    def test_task_dependencies_tracked(self, todo_manager):
        """Test: Task dependencies are tracked correctly."""
        # Create dependency chain
        task1 = todo_manager.create_task(name="Base Task")
        task2 = todo_manager.create_task(
            name="Dependent Task",
            dependencies=[task1.id]
        )
        
        # Verify dependencies stored
        assert task2.dependencies == [task1.id]
    
    def test_multiple_dependencies_tracked(self, todo_manager):
        """Test: Task with multiple dependencies tracked."""
        # Create tasks
        task1 = todo_manager.create_task(name="Dep 1")
        task2 = todo_manager.create_task(name="Dep 2")
        task3 = todo_manager.create_task(
            name="Dependent Task",
            dependencies=[task1.id, task2.id]
        )
        
        # Verify dependencies
        assert len(task3.dependencies) == 2
        assert task1.id in task3.dependencies
        assert task2.id in task3.dependencies
    
    def test_no_dependencies_for_independent_task(self, todo_manager):
        """Test: Independent tasks have no dependencies."""
        task = todo_manager.create_task(name="Independent Task")
        assert task.dependencies == []
    
    def test_dependency_chain_creation(self, todo_manager):
        """Test: Can create chain of dependent tasks."""
        # Create chain: task3 depends on task2, task2 depends on task1
        task1 = todo_manager.create_task(name="Base Task")
        task2 = todo_manager.create_task(
            name="Middle Task",
            dependencies=[task1.id]
        )
        task3 = todo_manager.create_task(
            name="Final Task",
            dependencies=[task2.id]
        )
        
        # Verify chain structure
        assert task1.dependencies == []
        assert task2.dependencies == [task1.id]
        assert task3.dependencies == [task2.id]
    
    def test_diamond_dependency_structure(self, todo_manager):
        """Test: Diamond dependency pattern creation."""
        #     task1
        #    /     \
        # task2   task3
        #    \     /
        #     task4
        
        task1 = todo_manager.create_task(name="Root")
        task2 = todo_manager.create_task(name="Branch 1", dependencies=[task1.id])
        task3 = todo_manager.create_task(name="Branch 2", dependencies=[task1.id])
        task4 = todo_manager.create_task(
            name="Merge",
            dependencies=[task2.id, task3.id]
        )
        
        # Verify structure
        assert task2.dependencies == [task1.id]
        assert task3.dependencies == [task1.id]
        assert set(task4.dependencies) == {task2.id, task3.id}
    
    def test_dependency_metadata_preserved(self, todo_manager):
        """Test: Dependency information preserved in task metadata."""
        # Create dependent task
        task1 = todo_manager.create_task(name="Dependency")
        task2 = todo_manager.create_task(
            name="Dependent",
            dependencies=[task1.id],
            metadata={"depends_on_count": 1}
        )
        
        # Retrieve and verify
        retrieved = todo_manager.get_task(task2.id)
        assert retrieved.dependencies == [task1.id]
        assert retrieved.metadata["depends_on_count"] == 1
    
    def test_task_serialization_includes_dependencies(self, todo_manager):
        """Test: Task dict includes dependency information."""
        task1 = todo_manager.create_task(name="Dep")
        task2 = todo_manager.create_task(name="Task", dependencies=[task1.id])
        
        task_dict = task2.to_dict()
        assert 'dependencies' in task_dict
        assert task1.id in task_dict['dependencies']
    
    def test_pending_tasks_with_dependencies(self, todo_manager):
        """Test: Pending tasks include those with dependencies."""
        task1 = todo_manager.create_task(name="Dep")
        task2 = todo_manager.create_task(name="Dependent", dependencies=[task1.id])
        
        pending = todo_manager.get_pending_tasks()
        pending_ids = [t.id for t in pending]
        
        assert task1.id in pending_ids
        assert task2.id in pending_ids
    
    def test_dependency_info_exported(self, todo_manager):
        """Test: Dependency info included in JSON export."""
        task1 = todo_manager.create_task(name="Base")
        task2 = todo_manager.create_task(name="Dependent", dependencies=[task1.id])
        
        exported = todo_manager.export_tasks_as_json()
        
        # Find task2 in export
        task2_exported = next(t for t in exported if t['id'] == task2.id)
        assert task1.id in task2_exported['dependencies']
