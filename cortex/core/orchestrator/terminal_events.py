"""Terminal Events

STUB IMPLEMENTATION - To be completed in Phase E.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass


@dataclass
class UserCancelledEvent:
    """Event for user cancellation."""
    event_id: str
    reason: str = "user_cancelled"
    timestamp: str = ""


@dataclass
class PhaseCompletedEvent:
    """Event fired when a phase completes."""
    event_id: str
    phase: str
    success: bool
    timestamp: str = ""


@dataclass
class MaxTurnsReachedEvent:
    """Event fired when maximum turns reached."""
    event_id: str
    max_turns: int
    current_turn: int
    timestamp: str = ""


@dataclass
class ErrorOccurredEvent:
    """Event fired when error occurs."""
    event_id: str
    error_message: str
    error_type: str = "unknown"
    timestamp: str = ""


@dataclass
class TokenLimitEvent:
    """Event fired when token limit is reached."""
    event_id: str
    current_tokens: int
    max_tokens: int
    timestamp: str = ""


@dataclass
class TerminalEvent:
    """Base terminal event."""
    event_id: str
    event_type: str
    timestamp: str = ""


@dataclass
class GovernanceViolationEvent:
    """Event fired when governance violation occurs."""
    event_id: str
    violation_type: str
    severity: str = "medium"
    timestamp: str = ""


@dataclass
class UserApprovalRejectedEvent:
    """Event fired when user rejects approval."""
    event_id: str
    reason: str = ""
    timestamp: str = ""


class EventListener:
    """Event listener interface."""
    
    def on_event(self, event: TerminalEvent) -> None:
        """Handle terminal event."""
        pass


class EventRegistry:
    """Registry for event listeners."""
    
    def __init__(self):
        self.listeners = []
    
    def register(self, listener: EventListener) -> None:
        """Register event listener."""
        self.listeners.append(listener)

__all__ = ["UserCancelledEvent", "PhaseCompletedEvent", "MaxTurnsReachedEvent", "ErrorOccurredEvent", "TokenLimitEvent", "TerminalEvent", "GovernanceViolationEvent", "UserApprovalRejectedEvent", "EventListener", "EventRegistry"]
