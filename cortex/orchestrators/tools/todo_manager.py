"""todo_manager.py — Todo Manager stub."""
from __future__ import annotations
from typing import Any


class TodoManager:
    """Manages orchestrator todo items."""

    def __init__(self) -> None:
        """Initialise with empty todo list."""
        self._todos: list[dict[str, Any]] = []

    def add(self, item: str, priority: str = "normal") -> None:
        """Add a todo item.

        Args:
            item: Description of the todo.
            priority: Priority level (low/normal/high).
        """
        self._todos.append({"item": item, "priority": priority, "done": False})

    def complete(self, index: int) -> None:
        """Mark a todo item as complete.

        Args:
            index: Index of the item to complete.
        """
        if 0 <= index < len(self._todos):
            self._todos[index]["done"] = True

    def pending(self) -> list[dict[str, Any]]:
        """Return all pending (not done) todos."""
        return [t for t in self._todos if not t["done"]]
