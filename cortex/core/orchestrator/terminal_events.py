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


__all__ = ["UserCancelledEvent"]
