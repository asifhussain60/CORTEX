# AC-ID: AC-TDD-INCREMENTAL-02 - MCP Todo Tool Tests
"""
Tests for cortex_manage_todo MCP tool.

Validates CRUD operations for todo list management exposed via MCP.

Governance:
- CORE-008: TDD (tests first)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings

Author: Asif Hussain
Date: 2026-02-02
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch

from cortex.mcp.tools.todo_tool import (
    TodoTool,
    TodoItem,
    TodoList,
    TodoStatus,
)
from cortex.core.result import Ok, Err


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def todo_tool() -> TodoTool:
    """Create TodoTool instance."""
    return TodoTool()


@pytest.fixture
def sample_todos() -> List[Dict[str, Any]]:
    """Create sample todo items."""
    return [
        {
            "id": "1",
            "title": "Write tests for authentication",
            "description": "Create unit tests for auth service",
            "status": "not-started"
        },
        {
            "id": "2",
            "title": "Implement authentication logic",
            "description": "Add JWT token generation",
            "status": "not-started"
        },
        {
            "id": "3",
            "title": "Add authorization checks",
            "description": "Role-based access control",
            "status": "not-started"
        }
    ]


# =============================================================================
# AC-TDD-INCREMENTAL-02-01: Todo Tool Initialization
# =============================================================================

class TestTodoToolInitialization:
    """Tests for TodoTool initialization."""

    def test_initialization(self, todo_tool: TodoTool) -> None:
        """Initializes with empty todo list.

        AC-TDD-INCREMENTAL-02-01-01: Empty initial state
        """
        assert todo_tool.get_all_todos() == []
        assert todo_tool.get_progress() == {"total": 0, "completed": 0, "percentage": 0.0}


# =============================================================================
# AC-TDD-INCREMENTAL-02-02: Create Todo List Tests
# =============================================================================

class TestCreateTodoList:
    """Tests for creating todo lists."""

    def test_create_todo_list_success(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Creates todo list from subtasks.

        AC-TDD-INCREMENTAL-02-02-01: Create from subtask list
        """
        result = todo_tool.create_todo_list(sample_todos)

        assert result.is_ok()
        todo_list = result.unwrap()
        assert len(todo_list.items) == 3
        assert all(item.status == TodoStatus.NOT_STARTED for item in todo_list.items)

    def test_create_todo_list_with_existing_todos(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Replaces existing todo list.

        AC-TDD-INCREMENTAL-02-02-02: Replace on create
        """
        # Create first list
        todo_tool.create_todo_list(sample_todos[:2])
        
        # Create second list (should replace)
        result = todo_tool.create_todo_list(sample_todos)

        assert result.is_ok()
        assert len(todo_tool.get_all_todos()) == 3

    def test_create_todo_list_validates_structure(
        self,
        todo_tool: TodoTool
    ) -> None:
        """Validates todo item structure.

        AC-TDD-INCREMENTAL-02-02-03: Input validation
        """
        invalid_todos = [
            {"id": "1"}  # Missing title, description
        ]

        result = todo_tool.create_todo_list(invalid_todos)

        assert result.is_err()
        assert "title" in result.error.lower() or "description" in result.error.lower()


# =============================================================================
# AC-TDD-INCREMENTAL-02-03: Update Todo Status Tests
# =============================================================================

class TestUpdateTodoStatus:
    """Tests for updating todo status."""

    def test_update_status_to_in_progress(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Updates todo status to in-progress.

        AC-TDD-INCREMENTAL-02-03-01: Mark as in-progress
        """
        todo_tool.create_todo_list(sample_todos)

        result = todo_tool.update_todo_status("1", "in-progress")

        assert result.is_ok()
        todo = todo_tool.get_todo_by_id("1")
        assert todo.status == TodoStatus.IN_PROGRESS

    def test_update_status_to_completed(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Updates todo status to completed.

        AC-TDD-INCREMENTAL-02-03-02: Mark as completed
        """
        todo_tool.create_todo_list(sample_todos)

        result = todo_tool.update_todo_status("1", "completed")

        assert result.is_ok()
        todo = todo_tool.get_todo_by_id("1")
        assert todo.status == TodoStatus.COMPLETED

    def test_update_status_nonexistent_todo_fails(
        self,
        todo_tool: TodoTool
    ) -> None:
        """Returns error for nonexistent todo.

        AC-TDD-INCREMENTAL-02-03-03: Validate todo exists
        """
        result = todo_tool.update_todo_status("999", "completed")

        assert result.is_err()
        assert "not found" in result.error.lower()

    def test_update_status_invalid_status_fails(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Returns error for invalid status.

        AC-TDD-INCREMENTAL-02-03-04: Validate status value
        """
        todo_tool.create_todo_list(sample_todos)

        result = todo_tool.update_todo_status("1", "invalid-status")

        assert result.is_err()


# =============================================================================
# AC-TDD-INCREMENTAL-02-04: Get Todo Progress Tests
# =============================================================================

class TestGetTodoProgress:
    """Tests for getting todo progress."""

    def test_get_progress_empty_list(
        self,
        todo_tool: TodoTool
    ) -> None:
        """Returns zero progress for empty list.

        AC-TDD-INCREMENTAL-02-04-01: Empty list progress
        """
        progress = todo_tool.get_progress()

        assert progress["total"] == 0
        assert progress["completed"] == 0
        assert progress["percentage"] == 0.0

    def test_get_progress_partial_completion(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Calculates progress with partial completion.

        AC-TDD-INCREMENTAL-02-04-02: Partial completion calculation
        """
        todo_tool.create_todo_list(sample_todos)
        todo_tool.update_todo_status("1", "completed")
        todo_tool.update_todo_status("2", "in-progress")

        progress = todo_tool.get_progress()

        assert progress["total"] == 3
        assert progress["completed"] == 1
        assert progress["percentage"] == pytest.approx(33.33, rel=0.1)

    def test_get_progress_full_completion(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Returns 100% for fully completed list.

        AC-TDD-INCREMENTAL-02-04-03: Full completion
        """
        todo_tool.create_todo_list(sample_todos)
        for todo in sample_todos:
            todo_tool.update_todo_status(todo["id"], "completed")

        progress = todo_tool.get_progress()

        assert progress["percentage"] == 100.0


# =============================================================================
# AC-TDD-INCREMENTAL-02-05: Get All Todos Tests
# =============================================================================

class TestGetAllTodos:
    """Tests for retrieving all todos."""

    def test_get_all_todos_returns_list(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Returns all todos as list.

        AC-TDD-INCREMENTAL-02-05-01: Return all todos
        """
        todo_tool.create_todo_list(sample_todos)

        todos = todo_tool.get_all_todos()

        assert len(todos) == 3
        assert all(isinstance(todo, TodoItem) for todo in todos)

    def test_get_all_todos_preserves_order(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Preserves todo order.

        AC-TDD-INCREMENTAL-02-05-02: Order preservation
        """
        todo_tool.create_todo_list(sample_todos)

        todos = todo_tool.get_all_todos()

        assert todos[0].id == "1"
        assert todos[1].id == "2"
        assert todos[2].id == "3"


# =============================================================================
# AC-TDD-INCREMENTAL-02-06: MCP Tool Integration Tests
# =============================================================================

class TestMCPToolIntegration:
    """Tests for MCP tool interface."""

    def test_exposes_mcp_tool_interface(
        self,
        todo_tool: TodoTool
    ) -> None:
        """Exposes standard MCP tool interface.

        AC-TDD-INCREMENTAL-02-06-01: MCP interface
        """
        assert hasattr(todo_tool, 'get_tool_definition')
        assert hasattr(todo_tool, 'execute_tool')

    def test_tool_definition_includes_operations(
        self,
        todo_tool: TodoTool
    ) -> None:
        """Tool definition includes all CRUD operations.

        AC-TDD-INCREMENTAL-02-06-02: Complete tool definition
        """
        definition = todo_tool.get_tool_definition()

        assert "create_todo_list" in str(definition)
        assert "update_todo_status" in str(definition)
        assert "get_progress" in str(definition)

    def test_execute_tool_via_mcp_interface(
        self,
        todo_tool: TodoTool,
        sample_todos: List[Dict[str, Any]]
    ) -> None:
        """Executes operations via MCP interface.

        AC-TDD-INCREMENTAL-02-06-03: MCP execution
        """
        result = todo_tool.execute_tool(
            "create_todo_list",
            {"todos": sample_todos}
        )

        assert result.is_ok()
