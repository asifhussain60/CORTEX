"""Terminal Events - Event types for terminal/CLI interactions.

Defines event models and handlers for terminal-based operations and
user interactions.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime


class EventType(Enum):
    """Terminal event types."""

    INPUT = "input"
    OUTPUT = "output"
    ERROR = "error"
    STATUS = "status"
    COMMAND = "command"
    RESPONSE = "response"


@dataclass
class TerminalEvent:
    """Terminal event.

    Attributes:
        event_type: Type of event.
        message: Event message.
        timestamp: When event occurred.
        metadata: Additional metadata.
    """

    event_type: EventType
    message: str
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class EventHandler:
    """Handles terminal events."""

    def __init__(self) -> None:
        """Initialize event handler."""
        self.events: list = []
        self.handlers: Dict[EventType, list] = {}

    def register_handler(self, event_type: EventType, callback: callable) -> None:
        """Register a handler for an event type.

        Args:
            event_type: Type of event to handle.
            callback: Callback function.
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(callback)

    def emit(self, event: TerminalEvent) -> None:
        """Emit an event.

        Args:
            event: TerminalEvent to emit.
        """
        self.events.append(event)
        
        # Call registered handlers
        if event.event_type in self.handlers:
            for handler in self.handlers[event.event_type]:
                try:
                    handler(event)
                except Exception:
                    pass

    def get_events(self) -> list:
        """Get all events.

        Returns:
            List of events.
        """
        return self.events.copy()

    def clear_events(self) -> None:
        """Clear event history."""
        self.events.clear()


class EventRegistry:
    """Registry for event handlers and subscriptions."""

    def __init__(self) -> None:
        """Initialize event registry."""
        self.handlers: Dict[EventType, list] = {}

    def register(self, event_type: EventType, callback: callable) -> None:
        """Register an event handler.

        Args:
            event_type: Type of event to handle.
            callback: Callback function.
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(callback)

    def unregister(self, event_type: EventType, callback: callable) -> None:
        """Unregister an event handler.

        Args:
            event_type: Type of event.
            callback: Callback to remove.
        """
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(callback)
            except ValueError:
                pass

    def get_handlers(self, event_type: EventType) -> list:
        """Get handlers for an event type.

        Args:
            event_type: Type of event.

        Returns:
            List of registered handlers.
        """
        return self.handlers.get(event_type, []).copy()


__all__ = [
    "TerminalEvent",
    "EventType",
    "EventHandler",
    "EventRegistry",
]
