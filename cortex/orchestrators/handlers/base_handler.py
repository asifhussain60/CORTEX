"""Base handler class for orchestrator handlers.

All specialized handlers inherit from BaseHandler to provide consistent
interface and error handling patterns.

AC-REM-HIGH-001: Handler extraction pattern
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class BaseHandler(ABC, Generic[T]):
    """Base class for all orchestrator handlers."""

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> T:
        """
        Execute handler logic.

        Returns:
            Handler-specific result type
        """
        pass


class HandlerRegistry:
    """Registry for managing handler instances."""

    def __init__(self) -> None:
        """Initialize empty handler registry."""
        self._handlers: dict[str, BaseHandler] = {}

    def register(self, name: str, handler: BaseHandler) -> None:
        """
        Register a handler.

        Args:
            name: Handler identifier
            handler: Handler instance
        """
        self._handlers[name] = handler

    def get(self, name: str) -> Optional[BaseHandler]:
        """
        Get a registered handler.

        Args:
            name: Handler identifier

        Returns:
            Handler instance or None if not found
        """
        return self._handlers.get(name)

    def list_handlers(self) -> list[str]:
        """List all registered handler names."""
        return list(self._handlers.keys())
