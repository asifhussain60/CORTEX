# AC-ID: AC-TDD-INCREMENTAL-02 - MCP Todo Tool Implementation
"""
TodoTool - MCP-exposed todo list management.

Provides CRUD operations for todo list management, exposed via MCP
for client consumption (GitHub Copilot, Cursor, CLI).

Key Features:
- Create todo list from subtasks
- Update todo status (not-started → in-progress → completed)
- Get progress tracking
- MCP tool interface compliant

Governance:
- CORE-008: TDD (tests in test_todo_tool.py)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings

Author: Asif Hussain
Date: 2026-02-02
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.core.result import Result, Ok, Err

logger = logging.getLogger(__name__)


class TodoStatus(Enum):
    """Todo item status."""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


@dataclass
class TodoItem:
    """Single todo item."""
    
    id: str
    title: str
    description: str
    status: TodoStatus = TodoStatus.NOT_STARTED
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TodoList:
    """Collection of todo items."""
    
    items: List[TodoItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TodoTool:
    """
    MCP-exposed todo list management tool.
    
    Provides CRUD operations for tracking implementation subtasks.
    Designed for MCP client integration (GitHub Copilot, Cursor, etc.).
    
    Example:
        >>> tool = TodoTool()
        >>> result = tool.create_todo_list([
        ...     {"id": "1", "title": "Write tests", "description": "..."}
        ... ])
        >>> tool.update_todo_status("1", "completed")
        >>> progress = tool.get_progress()
    
    AC-TDD-INCREMENTAL-02: MCP todo tool implementation
    """

    def __init__(self) -> None:
        """
        Initialize TodoTool.
        
        AC-TDD-INCREMENTAL-02-01: Initialization
        """
        self._todo_list: TodoList = TodoList()
        logger.info("TodoTool initialized")

    def create_todo_list(
        self,
        todos: List[Dict[str, Any]]
    ) -> Result[TodoList]:
        """
        Create todo list from subtask specifications.
        
        Replaces any existing todo list.
        
        Args:
            todos: List of todo specifications with id, title, description
            
        Returns:
            Result with TodoList or error
            
        AC-TDD-INCREMENTAL-02-02: Create todo list
        """
        try:
            # Validate todo structure
            for todo in todos:
                if "id" not in todo or "title" not in todo or "description" not in todo:
                    return Err(
                        f"Todo missing required fields (id, title, description): {todo.get('id', 'unknown')}"
                    )

            # Create todo items
            items = []
            for todo in todos:
                status_str = todo.get("status", "not-started")
                
                try:
                    status = TodoStatus(status_str)
                except ValueError:
                    status = TodoStatus.NOT_STARTED

                item = TodoItem(
                    id=todo["id"],
                    title=todo["title"],
                    description=todo["description"],
                    status=status,
                    metadata=todo.get("metadata", {})
                )
                items.append(item)

            # Replace existing list
            self._todo_list = TodoList(items=items)

            logger.info(f"Created todo list with {len(items)} items")

            return Ok(self._todo_list)

        except Exception as e:
            logger.error(f"Failed to create todo list: {e}", exc_info=True)
            return Err(f"Failed to create todo list: {e}")

    def update_todo_status(
        self,
        todo_id: str,
        status: str
    ) -> Result[TodoItem]:
        """
        Update status of a todo item.
        
        Args:
            todo_id: Todo item ID
            status: New status (not-started, in-progress, completed)
            
        Returns:
            Result with updated TodoItem or error
            
        AC-TDD-INCREMENTAL-02-03: Update todo status
        """
        try:
            # Find todo
            todo = self.get_todo_by_id(todo_id)
            
            if todo is None:
                return Err(f"Todo with id '{todo_id}' not found")

            # Validate and set status
            try:
                new_status = TodoStatus(status)
            except ValueError:
                valid_statuses = [s.value for s in TodoStatus]
                return Err(
                    f"Invalid status '{status}'. Valid statuses: {', '.join(valid_statuses)}"
                )

            todo.status = new_status

            logger.info(f"Updated todo {todo_id} status to {status}")

            return Ok(todo)

        except Exception as e:
            logger.error(f"Failed to update todo status: {e}", exc_info=True)
            return Err(f"Failed to update todo status: {e}")

    def get_progress(self) -> Dict[str, Any]:
        """
        Get todo list progress.
        
        Returns:
            Dictionary with total, completed, and percentage
            
        AC-TDD-INCREMENTAL-02-04: Get todo progress
        """
        total = len(self._todo_list.items)
        
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "in_progress": 0,
                "not_started": 0,
                "percentage": 0.0
            }

        completed = sum(
            1 for item in self._todo_list.items
            if item.status == TodoStatus.COMPLETED
        )
        in_progress = sum(
            1 for item in self._todo_list.items
            if item.status == TodoStatus.IN_PROGRESS
        )
        not_started = total - completed - in_progress

        percentage = (completed / total) * 100.0

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "percentage": round(percentage, 2)
        }

    def get_all_todos(self) -> List[TodoItem]:
        """
        Get all todo items.
        
        Returns:
            List of TodoItem objects
            
        AC-TDD-INCREMENTAL-02-05: Get all todos
        """
        return self._todo_list.items

    def get_todo_by_id(self, todo_id: str) -> Optional[TodoItem]:
        """
        Get todo item by ID.
        
        Args:
            todo_id: Todo item ID
            
        Returns:
            TodoItem if found, None otherwise
        """
        for item in self._todo_list.items:
            if item.id == todo_id:
                return item
        return None

    # =========================================================================
    # MCP Tool Interface
    # =========================================================================

    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Get MCP tool definition.
        
        Returns:
            Tool definition dictionary
            
        AC-TDD-INCREMENTAL-02-06: MCP interface
        """
        return {
            "name": "cortex_manage_todo",
            "description": "Manage todo list for incremental TDD implementation",
            "operations": {
                "create_todo_list": {
                    "description": "Create or replace todo list",
                    "parameters": {
                        "todos": "List of todo items with id, title, description"
                    }
                },
                "update_todo_status": {
                    "description": "Update status of a todo item",
                    "parameters": {
                        "todo_id": "Todo item ID",
                        "status": "New status (not-started, in-progress, completed)"
                    }
                },
                "get_progress": {
                    "description": "Get todo list progress",
                    "parameters": {}
                },
                "get_all_todos": {
                    "description": "Get all todo items",
                    "parameters": {}
                }
            }
        }

    def execute_tool(
        self,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Result[Any]:
        """
        Execute tool operation via MCP interface.
        
        Args:
            operation: Operation name
            parameters: Operation parameters
            
        Returns:
            Result with operation result or error
        """
        try:
            if operation == "create_todo_list":
                return self.create_todo_list(parameters.get("todos", []))
            
            elif operation == "update_todo_status":
                todo_id = parameters.get("todo_id")
                status = parameters.get("status")
                
                if not todo_id or not status:
                    return Err("Missing required parameters: todo_id, status")
                
                return self.update_todo_status(todo_id, status)
            
            elif operation == "get_progress":
                return Ok(self.get_progress())
            
            elif operation == "get_all_todos":
                return Ok(self.get_all_todos())
            
            else:
                return Err(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            return Err(f"Tool execution failed: {e}")


__all__ = [
    "TodoTool",
    "TodoItem",
    "TodoList",
    "TodoStatus",
]
