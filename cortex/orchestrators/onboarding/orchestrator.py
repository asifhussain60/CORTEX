"""Onboarding Orchestrator.

DEPRECATED: Use cortex.config.UnifiedOnboarding instead.
This module is maintained for backward compatibility only.
See cortex/orchestrators/onboarding/__init__.py for the canonical import.

Author: CORTEX Framework
Date: 2025
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Union

T = TypeVar('T')


class JourneyState(str, Enum):
    """Onboarding journey states."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


from cortex.brain.core.result import Err, Ok, Result


@dataclass
class Journey:
    """Onboarding journey data.

    Attributes:
        journey_id: Unique journey identifier
        user_id: User identifier
        activities: List of activity identifiers
        state: Current journey state
        activities_completed: Number of completed activities
        total_activities: Total number of activities
        _completed_indices: Set of completed activity indices (internal)
        created_at: Journey creation timestamp
        started_at: Journey start timestamp
        completed_at: Journey completion timestamp
    """
    journey_id: str
    user_id: str
    activities: List[str]
    state: JourneyState = JourneyState.NEW
    activities_completed: int = 0
    total_activities: int = 0
    _completed_indices: set = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize total_activities after creation."""
        if self.total_activities == 0:
            self.total_activities = len(self.activities)


@dataclass
class JourneyProgress:
    """Journey progress information.

    Attributes:
        state: Current journey state
        activities_completed: Number of completed activities
        total_activities: Total number of activities
    """
    state: JourneyState
    activities_completed: int
    total_activities: int


class OnboardingOrchestrator:
    """Orchestrate user onboarding journeys.

    Manages the creation, progression, and completion of user onboarding
    journeys with state tracking and audit logging.

    Attributes:
        journeys: Dictionary of journey_id to Journey objects
        audit_log: List of audit log entries
    """

    def __init__(self) -> None:
        """Initialize the onboarding orchestrator."""
        self.journeys: Dict[str, Journey] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def create_journey(
        self,
        journey_id: str,
        user_id: str,
        activities: List[str]
    ) -> Result[Journey]:
        """Create a new onboarding journey.

        Args:
            journey_id: Unique journey identifier
            user_id: User identifier
            activities: List of activity identifiers

        Returns:
            Result containing the created Journey or error
        """
        if journey_id in self.journeys:
            return Err(f"Journey '{journey_id}' already exists")

        journey = Journey(
            journey_id=journey_id,
            user_id=user_id,
            activities=activities
        )

        self.journeys[journey_id] = journey

        self._log_event(
            event_type='journey_created',
            journey_id=journey_id,
            user_id=user_id,
            metadata={'total_activities': len(activities)}
        )

        return Ok(journey)

    def start_journey(self, journey_id: str) -> Result[Journey]:
        """Start an onboarding journey.

        Args:
            journey_id: Journey identifier

        Returns:
            Result containing the updated Journey or error
        """
        journey = self.journeys.get(journey_id)
        if not journey:
            return Err(f"Journey '{journey_id}' not found")

        if journey.state != JourneyState.NEW:
            return Err(f"Journey '{journey_id}' already in state {journey.state.value}")

        journey.state = JourneyState.IN_PROGRESS
        journey.started_at = datetime.now()

        self._log_event(
            event_type='journey_started',
            journey_id=journey_id,
            user_id=journey.user_id
        )

        return Ok(journey)

    def complete_activity(
        self,
        journey_id: str,
        activity_index: int
    ) -> Result[Journey]:
        """Complete an activity in the journey.

        Args:
            journey_id: Journey identifier
            activity_index: Zero-based index of the activity

        Returns:
            Result containing the updated Journey or error
        """
        journey = self.journeys.get(journey_id)
        if not journey:
            return Err(f"Journey '{journey_id}' not found")

        if journey.state != JourneyState.IN_PROGRESS:
            return Err(f"Journey '{journey_id}' not in progress")

        if activity_index < 0 or activity_index >= len(journey.activities):
            return Err(f"Activity index {activity_index} out of range")

        # Track internally and update count
        if activity_index not in journey._completed_indices:
            journey._completed_indices.add(activity_index)
            journey.activities_completed = len(journey._completed_indices)

        self._log_event(
            event_type='activity_completed',
            journey_id=journey_id,
            user_id=journey.user_id,
            metadata={'activity_index': activity_index}
        )

        return Ok(journey)

    def complete_journey(self, journey_id: str) -> Result[Journey]:
        """Complete an onboarding journey.

        Args:
            journey_id: Journey identifier

        Returns:
            Result containing the updated Journey or error
        """
        journey = self.journeys.get(journey_id)
        if not journey:
            return Err(f"Journey '{journey_id}' not found")

        if journey.state != JourneyState.IN_PROGRESS:
            return Err(f"Journey '{journey_id}' not in progress")

        journey.state = JourneyState.COMPLETED
        journey.completed_at = datetime.now()

        self._log_event(
            event_type='journey_completed',
            journey_id=journey_id,
            user_id=journey.user_id
        )

        return Ok(journey)

    def get_journey_progress(self, journey_id: str) -> Result[JourneyProgress]:
        """Get progress information for a journey.

        Args:
            journey_id: Journey identifier

        Returns:
            Result containing JourneyProgress or error
        """
        journey = self.journeys.get(journey_id)
        if not journey:
            return Err(f"Journey '{journey_id}' not found")

        progress = JourneyProgress(
            state=journey.state,
            activities_completed=len(journey._completed_indices),
            total_activities=len(journey.activities)
        )

        return Ok(progress)

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get the audit log entries.

        Returns:
            List of audit log entries
        """
        return self.audit_log

    def _log_event(
        self,
        event_type: str,
        journey_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an audit event.

        Args:
            event_type: Type of event
            journey_id: Journey identifier
            user_id: User identifier
            metadata: Optional event metadata
        """
        log_entry = {
            'event_type': event_type,
            'journey_id': journey_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.audit_log.append(log_entry)


__all__ = [
    "JourneyState",
    "Result",
    "Ok",
    "Err",
    "Journey",
    "JourneyProgress",
    "OnboardingOrchestrator"
]
