"""Onboarding Orchestrator

Author: CORTEX Framework
"""

from enum import Enum

class JourneyState(str, Enum):
    """Onboarding journey states."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

__all__ = ["JourneyState"]
