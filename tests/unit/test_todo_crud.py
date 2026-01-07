"""
CORTEX 6.0 - TodoOrchestrator CRUD Tests
========================================
Tests for Create, Read, Update, Delete operations.

Author: Asif Hussain
Version: 6.0.0
Created: 2026-01-07
Task: task-2.2.3 (Implement TODO CRUD operations)
TDD Phase: GREEN (implementing to pass these tests)
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from src.orchestrators.core.todo_orchestrator import (
    TodoOrchestrator,
    Priority,
    TodoStatus,
    TodoNotFoundError,
    TodoValidationError,
)
from src.database.state_manager import StateManager
from src.orchestrators.audit_logger import EnterpriseAuditLogger


class TestTodoCRUD:
    """Test suite for TODO CRUD operations."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_state.db"
            yield db_path
    
    @pytest.fixture
    def state_manager(self, temp_db):
        """Create StateManager instance."""
        sm = StateManager(temp_db)
        sm.initialize()
        yield sm
        sm.close()
    
    @pytest.fixture
    def orchestrator(self, state_manager):
        """Create TodoOrchestrator instance with unique name for isolation."""
        import uuid
        audit_logger = EnterpriseAuditLogger()
        return TodoOrchestrator(
            state_manager=state_manager,
            audit_logger=audit_logger,
            name=f"test-orchestrator-{uuid.uuid4().hex[:8]}"
        )
    
    # ==========================================================================
    # CREATE TESTS
    # ==========================================================================
    
    def test_create_todo(self, orchestrator):
        """Test creating a TODO with minimal parameters."""
        todo_id = orchestrator.create_todo(
            title="Test Task",
            priority=Priority.P0_CRITICAL
        )
        
        # Verify TODO was created
        assert todo_id is not None
        assert isinstance(todo_id, str)
        assert len(todo_id) > 0
        
        # Verify TODO exists in storage
        assert todo_id in orchestrator.todos
        
        # Verify TODO details
        todo = orchestrator.todos[todo_id]
        assert todo.title == "Test Task"
        assert todo.priority == Priority.P0_CRITICAL
        assert todo.status == TodoStatus.NOT_STARTED
        assert todo.description == ""
        assert len(todo.tags) == 0
    
    def test_create_todo_with_all_parameters(self, orchestrator):
        """Test creating a TODO with all parameters."""
        todo_id = orchestrator.create_todo(
            title="Complete Task",
            description="This is a detailed task",
            priority=Priority.P1_HIGH,
            tags={"backend", "api", "urgent"},
            dependencies=[],
            data={"custom_field": "value"}
        )
        
        # Verify TODO details
        todo = orchestrator.todos[todo_id]
        assert todo.title == "Complete Task"
        assert todo.description == "This is a detailed task"
        assert todo.priority == Priority.P1_HIGH
        assert todo.tags == {"backend", "api", "urgent"}
        assert todo.data == {"custom_field": "value"}
    
    def test_create_todo_with_dependencies(self, orchestrator):
        """Test creating a TODO with dependencies."""
        # Create parent TODO
        parent_id = orchestrator.create_todo(
            title="Parent Task",
            priority=Priority.P0_CRITICAL
        )
        
        # Create child TODO with dependency
        child_id = orchestrator.create_todo(
            title="Child Task",
            priority=Priority.P1_HIGH,
            dependencies=[parent_id]
        )
        
        # Verify dependency relationship
        child = orchestrator.todos[child_id]
        assert parent_id in child.dependencies
        
        # Verify DAG relationship
        dependents = orchestrator.dag.get_dependents(parent_id)
        assert child_id in dependents
    
    def test_create_todo_with_invalid_dependency(self, orchestrator):
        """Test creating a TODO with non-existent dependency fails."""
        with pytest.raises(TodoValidationError, match="Dependency .* not found"):
            orchestrator.create_todo(
                title="Task",
                priority=Priority.P0_CRITICAL,
                dependencies=["non-existent-id"]
            )
    
    def test_create_todo_with_empty_title(self, orchestrator):
        """Test creating a TODO with empty title fails."""
        with pytest.raises(TodoValidationError, match="Title cannot be empty"):
            orchestrator.create_todo(
                title="",
                priority=Priority.P0_CRITICAL
            )
    
    def test_create_todo_with_whitespace_title(self, orchestrator):
        """Test creating a TODO with whitespace-only title fails."""
        with pytest.raises(TodoValidationError, match="Title cannot be empty"):
            orchestrator.create_todo(
                title="   ",
                priority=Priority.P0_CRITICAL
            )
    
    # ==========================================================================
    # READ TESTS
    # ==========================================================================
    
    def test_read_todo(self, orchestrator):
        """Test reading an existing TODO."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Read Test",
            description="Test reading",
            priority=Priority.P2_MEDIUM,
            tags={"test"}
        )
        
        # Read TODO
        todo = orchestrator.read_todo(todo_id)
        
        # Verify details
        assert todo.id == todo_id
        assert todo.title == "Read Test"
        assert todo.description == "Test reading"
        assert todo.priority == Priority.P2_MEDIUM
        assert todo.tags == {"test"}
        assert todo.status == TodoStatus.NOT_STARTED
    
    def test_read_nonexistent_todo(self, orchestrator):
        """Test reading a non-existent TODO fails."""
        with pytest.raises(TodoNotFoundError, match="TODO .* not found"):
            orchestrator.read_todo("non-existent-id")
    
    def test_read_todo_preserves_timestamps(self, orchestrator):
        """Test reading a TODO preserves timestamp information."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Timestamp Test",
            priority=Priority.P0_CRITICAL
        )
        
        # Read TODO
        todo = orchestrator.read_todo(todo_id)
        
        # Verify timestamps
        assert todo.created_at is not None
        assert isinstance(todo.created_at, datetime)
        assert todo.updated_at is not None
        assert isinstance(todo.updated_at, datetime)
        assert todo.started_at is None
        assert todo.completed_at is None
    
    # ==========================================================================
    # UPDATE TESTS
    # ==========================================================================
    
    def test_update_todo(self, orchestrator):
        """Test updating a TODO's basic fields."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Original Title",
            description="Original description",
            priority=Priority.P3_LOW
        )
        
        # Update TODO
        updated_todo = orchestrator.update_todo(
            todo_id,
            title="Updated Title",
            description="Updated description",
            priority=Priority.P0_CRITICAL
        )
        
        # Verify updates
        assert updated_todo.title == "Updated Title"
        assert updated_todo.description == "Updated description"
        assert updated_todo.priority == Priority.P0_CRITICAL
        
        # Verify persistence
        todo = orchestrator.read_todo(todo_id)
        assert todo.title == "Updated Title"
    
    def test_update_todo_partial(self, orchestrator):
        """Test updating only some fields of a TODO."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Original",
            description="Description",
            priority=Priority.P2_MEDIUM,
            tags={"original"}
        )
        
        # Update only title
        orchestrator.update_todo(todo_id, title="New Title")
        
        # Verify only title changed
        todo = orchestrator.read_todo(todo_id)
        assert todo.title == "New Title"
        assert todo.description == "Description"
        assert todo.priority == Priority.P2_MEDIUM
        assert todo.tags == {"original"}
    
    def test_update_todo_tags(self, orchestrator):
        """Test updating TODO tags."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Tag Test",
            priority=Priority.P1_HIGH,
            tags={"old", "tag"}
        )
        
        # Update tags
        orchestrator.update_todo(todo_id, tags={"new", "tag", "set"})
        
        # Verify tags replaced
        todo = orchestrator.read_todo(todo_id)
        assert todo.tags == {"new", "tag", "set"}
    
    def test_update_todo_data(self, orchestrator):
        """Test updating TODO custom data."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Data Test",
            priority=Priority.P1_HIGH,
            data={"field1": "value1", "field2": "value2"}
        )
        
        # Update data (should merge)
        orchestrator.update_todo(
            todo_id,
            data={"field2": "updated", "field3": "new"}
        )
        
        # Verify data merged
        todo = orchestrator.read_todo(todo_id)
        assert todo.data["field1"] == "value1"
        assert todo.data["field2"] == "updated"
        assert todo.data["field3"] == "new"
    
    def test_update_nonexistent_todo(self, orchestrator):
        """Test updating a non-existent TODO fails."""
        with pytest.raises(TodoNotFoundError, match="TODO .* not found"):
            orchestrator.update_todo("non-existent-id", title="New Title")
    
    def test_update_todo_updates_timestamp(self, orchestrator):
        """Test updating a TODO updates the updated_at timestamp."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Timestamp Test",
            priority=Priority.P0_CRITICAL
        )
        
        # Get original timestamp
        original_todo = orchestrator.read_todo(todo_id)
        original_updated_at = original_todo.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        # Update TODO
        orchestrator.update_todo(todo_id, title="New Title")
        
        # Verify timestamp updated
        updated_todo = orchestrator.read_todo(todo_id)
        assert updated_todo.updated_at > original_updated_at
    
    # ==========================================================================
    # DELETE TESTS
    # ==========================================================================
    
    def test_delete_todo(self, orchestrator):
        """Test deleting a TODO."""
        # Create TODO
        todo_id = orchestrator.create_todo(
            title="Delete Me",
            priority=Priority.P2_MEDIUM
        )
        
        # Verify exists
        assert todo_id in orchestrator.todos
        
        # Delete TODO
        result = orchestrator.delete_todo(todo_id)
        
        # Verify deleted
        assert result is True
        assert todo_id not in orchestrator.todos
    
    def test_delete_nonexistent_todo(self, orchestrator):
        """Test deleting a non-existent TODO fails."""
        with pytest.raises(TodoNotFoundError, match="TODO .* not found"):
            orchestrator.delete_todo("non-existent-id")
    
    def test_delete_todo_with_active_dependents(self, orchestrator):
        """Test deleting a TODO with active dependents fails."""
        # Create parent and child
        parent_id = orchestrator.create_todo(
            title="Parent",
            priority=Priority.P0_CRITICAL
        )
        child_id = orchestrator.create_todo(
            title="Child",
            priority=Priority.P1_HIGH,
            dependencies=[parent_id]
        )
        
        # Try to delete parent (should fail)
        with pytest.raises(TodoValidationError, match="Cannot delete TODO with active dependents"):
            orchestrator.delete_todo(parent_id)
        
        # Verify parent still exists
        assert parent_id in orchestrator.todos
    
    def test_delete_todo_with_completed_dependents(self, orchestrator):
        """Test deleting a TODO with completed dependents succeeds."""
        # Create parent and child
        parent_id = orchestrator.create_todo(
            title="Parent",
            priority=Priority.P0_CRITICAL
        )
        child_id = orchestrator.create_todo(
            title="Child",
            priority=Priority.P1_HIGH,
            dependencies=[parent_id]
        )
        
        # Complete child
        orchestrator.transition_status(child_id, TodoStatus.IN_PROGRESS)
        orchestrator.transition_status(child_id, TodoStatus.COMPLETED)
        
        # Delete parent (should succeed)
        result = orchestrator.delete_todo(parent_id)
        
        # Verify deleted
        assert result is True
        assert parent_id not in orchestrator.todos
    
    # ==========================================================================
    # LIST TESTS
    # ==========================================================================
    
    def test_list_todos_all(self, orchestrator):
        """Test listing all TODOs."""
        # Create multiple TODOs
        id1 = orchestrator.create_todo(title="Task 1", priority=Priority.P0_CRITICAL)
        id2 = orchestrator.create_todo(title="Task 2", priority=Priority.P1_HIGH)
        id3 = orchestrator.create_todo(title="Task 3", priority=Priority.P2_MEDIUM)
        
        # List all
        todos = orchestrator.list_todos()
        
        # Verify all returned
        assert len(todos) == 3
        todo_ids = {todo.id for todo in todos}
        assert todo_ids == {id1, id2, id3}
    
    def test_list_todos_by_status(self, orchestrator):
        """Test listing TODOs filtered by status."""
        # Create TODOs with different statuses
        id1 = orchestrator.create_todo(title="Task 1", priority=Priority.P0_CRITICAL)
        id2 = orchestrator.create_todo(title="Task 2", priority=Priority.P1_HIGH)
        orchestrator.transition_status(id2, TodoStatus.IN_PROGRESS)
        
        # List only NOT_STARTED
        not_started = orchestrator.list_todos(status=TodoStatus.NOT_STARTED)
        assert len(not_started) == 1
        assert not_started[0].id == id1
        
        # List only IN_PROGRESS
        in_progress = orchestrator.list_todos(status=TodoStatus.IN_PROGRESS)
        assert len(in_progress) == 1
        assert in_progress[0].id == id2
    
    def test_list_todos_by_priority(self, orchestrator):
        """Test listing TODOs filtered by priority."""
        # Create TODOs with different priorities
        id1 = orchestrator.create_todo(title="Critical", priority=Priority.P0_CRITICAL)
        id2 = orchestrator.create_todo(title="High", priority=Priority.P1_HIGH)
        id3 = orchestrator.create_todo(title="Medium", priority=Priority.P2_MEDIUM)
        
        # List only P0_CRITICAL
        critical = orchestrator.list_todos(priority=Priority.P0_CRITICAL)
        assert len(critical) == 1
        assert critical[0].id == id1
    
    def test_list_todos_by_tags(self, orchestrator):
        """Test listing TODOs filtered by tags."""
        # Create TODOs with different tags
        id1 = orchestrator.create_todo(
            title="Backend Task",
            priority=Priority.P0_CRITICAL,
            tags={"backend", "api"}
        )
        id2 = orchestrator.create_todo(
            title="Frontend Task",
            priority=Priority.P1_HIGH,
            tags={"frontend", "ui"}
        )
        id3 = orchestrator.create_todo(
            title="Full Stack Task",
            priority=Priority.P2_MEDIUM,
            tags={"backend", "frontend", "api"}
        )
        
        # List TODOs with "backend" tag
        backend = orchestrator.list_todos(tags={"backend"})
        assert len(backend) == 2
        backend_ids = {todo.id for todo in backend}
        assert backend_ids == {id1, id3}
        
        # List TODOs with both "backend" AND "api" tags
        backend_api = orchestrator.list_todos(tags={"backend", "api"})
        assert len(backend_api) == 2
        backend_api_ids = {todo.id for todo in backend_api}
        assert backend_api_ids == {id1, id3}
    
    def test_list_todos_combined_filters(self, orchestrator):
        """Test listing TODOs with multiple filters."""
        # Create various TODOs
        id1 = orchestrator.create_todo(
            title="Target Task",
            priority=Priority.P0_CRITICAL,
            tags={"backend", "urgent"}
        )
        id2 = orchestrator.create_todo(
            title="Non-Match 1",
            priority=Priority.P1_HIGH,
            tags={"backend", "urgent"}
        )
        id3 = orchestrator.create_todo(
            title="Non-Match 2",
            priority=Priority.P0_CRITICAL,
            tags={"frontend"}
        )
        
        # List with combined filters
        results = orchestrator.list_todos(
            status=TodoStatus.NOT_STARTED,
            priority=Priority.P0_CRITICAL,
            tags={"backend"}
        )
        
        # Only id1 should match all filters
        assert len(results) == 1
        assert results[0].id == id1
    
    def test_list_todos_empty(self, orchestrator):
        """Test listing TODOs when none exist."""
        todos = orchestrator.list_todos()
        assert len(todos) == 0
        assert todos == []
