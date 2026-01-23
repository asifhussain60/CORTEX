"""
Terminal Events and Break Condition Handlers - Production Implementation

Defines terminal events for orchestrator workflows:
- Phase completion
- User cancellation  
- Turn/token limits
- Error conditions
- Governance violations
- Approval rejections

Features:
- Dataclass-based event definitions
- Timestamp auto-generation
- EventListener interface
- EventRegistry pattern

Author: Asif Hussain
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Callable, List, Any
from abc import ABC, abstractmethod


@dataclass
class TerminalEvent:
    """Base terminal event class."""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PhaseCompletedEvent(TerminalEvent):
    """Event fired when a phase completes successfully."""
    operation: str = ""
    result: str = ""
    turn_number: int = 0
    
    def get_continuation_reason(self) -> 'ContinuationReason':
        """Maps to COMPLETION."""
        from cortex.core.orchestrator.continuation_decision import ContinuationReason
        return ContinuationReason.COMPLETION


@dataclass
class UserCancelledEvent(TerminalEvent):
    """Event fired when user cancels operation."""
    reason: str = ""
    turn_number: int = 0


@dataclass
class MaxTurnsReachedEvent(TerminalEvent):
    """Event fired when maximum turns limit reached."""
    turn_number: int = 0
    max_turns: int = 0
    current_turn: int = 0
    reason: str = "Safety limit enforced"
    
    def get_continuation_reason(self) -> 'ContinuationReason':
        """Maps to MAX_ROUNDS_REACHED."""
        from cortex.core.orchestrator.continuation_decision import ContinuationReason
        return ContinuationReason.MAX_ROUNDS_REACHED


@dataclass
class ErrorOccurredEvent(TerminalEvent):
    """Event fired when error occurs during execution."""
    error_message: str = ""
    error_type: str = "unknown"
    turn_number: int = 0
    recoverable: bool = True


@dataclass
class TokenLimitEvent(TerminalEvent):
    """Event fired when token limit is approached or reached."""
    tokens_used: int = 0
    token_limit: int = 0
    percentage_used: float = 0.0
    turn_number: int = 0


@dataclass
class GovernanceViolationEvent(TerminalEvent):
    """Event fired when governance rule is violated."""
    rule_id: str = ""
    violation_message: str = ""
    turn_number: int = 0


@dataclass
class UserApprovalRejectedEvent(TerminalEvent):
    """Event fired when user rejects required approval."""
    approval_request: str = ""
    rejection_reason: str = ""
    turn_number: int = 0


class EventListener:
    """Base class for event listeners."""
    
    def on_event(self, event: TerminalEvent) -> bool:
        """
        Handle terminal event.
        
        Args:
            event: Terminal event
        
        Returns:
            True to continue, False to break/halt
        """
        return True


class EventRegistry:
    """Registry pattern for managing event listeners."""
    
    def __init__(self):
        """Initialize registry."""
        self.listeners: List[EventListener] = []
        self._event_log: List[TerminalEvent] = []
    
    def register_listener(
        self,
        event_type: Optional[type],
        handler: Callable[[TerminalEvent], bool],
    ) -> None:
        """
        Register event listener.
        
        Args:
            event_type: Event type to listen for (None for all types)
            handler: Callable handler function
        """
        listener = _CallableListener(event_type, handler)
        self.listeners.append(listener)
    
    def fire_event(self, event: TerminalEvent) -> bool:
        """
        Fire event to all listeners.
        
        Args:
            event: Event to fire
        
        Returns:
            True if all listeners approved, False if any rejected
        """
        self._event_log.append(event)
        
        for listener in self.listeners:
            if not listener.on_event(event):
                return False
        
        return True
    
    def get_events(self) -> List[TerminalEvent]:
        """Get all fired events."""
        return self._event_log.copy()
    
    def get_listener_count(self, event_type: Optional[type] = None) -> int:
        """Get count of listeners for event type.
        
        Args:
            event_type: Event type to count listeners for (None for all)
        
        Returns:
            Number of listeners
        """
        if event_type is None:
            return len(self.listeners)
        return sum(1 for listener in self.listeners if listener.event_type == event_type or listener.event_type is None)
    
    def clear(self) -> None:
        """Clear registry and log."""
        self.listeners.clear()
        self._event_log.clear()


class _CallableListener(EventListener):
    """Internal wrapper for callable event handlers."""
    
    def __init__(
        self,
        event_type: Optional[type],
        handler: Callable[[TerminalEvent], bool],
    ):
        """Initialize callable listener."""
        self.event_type = event_type
        self.handler = handler
    
    def on_event(self, event: TerminalEvent) -> bool:
        """Handle event with callable."""
        if self.event_type is None or isinstance(event, self.event_type):
            return self.handler(event)
        return True


__all__ = [
    "TerminalEvent",
    "PhaseCompletedEvent",
    "UserCancelledEvent",
    "MaxTurnsReachedEvent",
    "ErrorOccurredEvent",
    "TokenLimitEvent",
    "GovernanceViolationEvent",
    "UserApprovalRejectedEvent",
    "EventListener",
    "EventRegistry",
]
