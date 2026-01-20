"""Onboarding Orchestrator

Author: CORTEX Framework
"""

from enum import Enum

class JourneyState(str, Enum):
    """Onboarding journey states."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


from dataclasses import dataclass


@dataclass
class Result:
    """Onboarding result."""
    success: bool
    message: str
    state: JourneyState = JourneyState.NOT_STARTED


@dataclass
class JourneyProgress:
    """Onboarding journey progress."""
    current_step: int
    total_steps: int
    state: JourneyState
    completion_percentage: float = 0.0



class OnboardingOrchestrator:
    """Orchestrate onboarding journey."""
    
    def start_journey(self) -> JourneyState:
        """Start onboarding."""
        return JourneyState.IN_PROGRESS
    
    def get_state(self) -> JourneyState:
        """Get journey state."""
        return JourneyState.NOT_STARTED

__all__ = ["JourneyState", "OnboardingOrchestrator"]
