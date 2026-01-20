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
class TerminalEvent:
    """Base terminal event."""
    event_id: str
    event_type: str
    timestamp: str = ""

__all__ = ["UserCancelledEvent", "PhaseCompletedEvent", "MaxTurnsReachedEvent", "TerminalEvent"]
