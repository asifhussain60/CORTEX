"""Master Orchestrator Package

Provides unified orchestration services for autonomous CORTEX operations.

Components:
- todo_manager: Task tracking with GitHub Copilot integration
"""

from .todo_manager import TodoManager, Task, TaskStatus, create_todo_manager

__all__ = ["TodoManager", "Task", "TaskStatus", "create_todo_manager"]
