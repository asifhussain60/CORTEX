"""
Onboarding Orchestrator & Flow Engine Implementation.

Provides the OnboardingOrchestrator class managing user onboarding journeys
with async/await patterns, state machine, Result[T] error handling, and
comprehensive audit logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class JourneyState(Enum):
    """Enumeration of journey states."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Result:
    """Generic result type for error handling."""
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class JourneyProgress:
    """Tracks journey progress."""
    journey_id: str
    user_id: str
    state: JourneyState
    activities_completed: int
    total_activities: int
    started_at: datetime
    completed_at: Optional[datetime] = None


class OnboardingOrchestrator:
    """Core orchestrator for managing user onboarding journeys."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.journeys: Dict[str, Dict[str, Any]] = {}
        self.user_progress: Dict[str, JourneyProgress] = {}
        self.audit_log: List[Dict[str, Any]] = []
    
    def create_journey(
        self,
        journey_id: str,
        user_id: str,
        activities: List[str]
    ) -> Result:
        """
        Create a new user onboarding journey.
        
        Args:
            journey_id: Unique journey identifier
            user_id: User identifier
            activities: List of activities in the journey
            
        Returns:
            Result[JourneyProgress] indicating success or failure
        """
        try:
            if journey_id in self.journeys:
                return Result(
                    success=False,
                    error=f"Journey {journey_id} already exists"
                )
            
            progress = JourneyProgress(
                journey_id=journey_id,
                user_id=user_id,
                state=JourneyState.NEW,
                activities_completed=0,
                total_activities=len(activities),
                started_at=datetime.now()
            )
            
            self.journeys[journey_id] = {
                'user_id': user_id,
                'activities': activities,
                'progress': progress
            }
            
            self._log_event('journey_created', journey_id, user_id)
            
            return Result(success=True, value=progress)
        
        except Exception as e:
            return Result(success=False, error=str(e))
    
    def start_journey(self, journey_id: str) -> Result:
        """
        Start an onboarding journey.
        
        Args:
            journey_id: Journey identifier
            
        Returns:
            Result[JourneyProgress] indicating success or failure
        """
        try:
            if journey_id not in self.journeys:
                return Result(
                    success=False,
                    error=f"Journey {journey_id} not found"
                )
            
            progress = self.journeys[journey_id]['progress']
            
            if progress.state != JourneyState.NEW:
                return Result(
                    success=False,
                    error=f"Journey already in state {progress.state.value}"
                )
            
            progress.state = JourneyState.IN_PROGRESS
            self._log_event('journey_started', journey_id, progress.user_id)
            
            return Result(success=True, value=progress)
        
        except Exception as e:
            return Result(success=False, error=str(e))
    
    def complete_activity(
        self,
        journey_id: str,
        activity_index: int
    ) -> Result:
        """
        Mark an activity as completed in a journey.
        
        Args:
            journey_id: Journey identifier
            activity_index: Index of the activity to complete
            
        Returns:
            Result[JourneyProgress] indicating success or failure
        """
        try:
            if journey_id not in self.journeys:
                return Result(
                    success=False,
                    error=f"Journey {journey_id} not found"
                )
            
            journey = self.journeys[journey_id]
            progress = journey['progress']
            
            if progress.state != JourneyState.IN_PROGRESS:
                return Result(
                    success=False,
                    error=f"Journey not in progress (state: {progress.state.value})"
                )
            
            if activity_index >= progress.total_activities:
                return Result(
                    success=False,
                    error=f"Activity index {activity_index} out of range"
                )
            
            progress.activities_completed += 1
            self._log_event(
                'activity_completed',
                journey_id,
                progress.user_id,
                {'activity_index': activity_index}
            )
            
            return Result(success=True, value=progress)
        
        except Exception as e:
            return Result(success=False, error=str(e))
    
    def complete_journey(self, journey_id: str) -> Result:
        """
        Mark an onboarding journey as completed.
        
        Args:
            journey_id: Journey identifier
            
        Returns:
            Result[JourneyProgress] indicating success or failure
        """
        try:
            if journey_id not in self.journeys:
                return Result(
                    success=False,
                    error=f"Journey {journey_id} not found"
                )
            
            journey = self.journeys[journey_id]
            progress = journey['progress']
            
            if progress.state != JourneyState.IN_PROGRESS:
                return Result(
                    success=False,
                    error=f"Journey not in progress (state: {progress.state.value})"
                )
            
            progress.state = JourneyState.COMPLETED
            progress.completed_at = datetime.now()
            self._log_event('journey_completed', journey_id, progress.user_id)
            
            return Result(success=True, value=progress)
        
        except Exception as e:
            return Result(success=False, error=str(e))
    
    def get_journey_progress(self, journey_id: str) -> Result:
        """
        Get the current progress of a journey.
        
        Args:
            journey_id: Journey identifier
            
        Returns:
            Result[JourneyProgress] containing journey progress
        """
        try:
            if journey_id not in self.journeys:
                return Result(
                    success=False,
                    error=f"Journey {journey_id} not found"
                )
            
            progress = self.journeys[journey_id]['progress']
            return Result(success=True, value=progress)
        
        except Exception as e:
            return Result(success=False, error=str(e))
    
    def _log_event(
        self,
        event_type: str,
        journey_id: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an onboarding event to the audit log.
        
        Args:
            event_type: Type of event
            journey_id: Journey identifier
            user_id: User identifier
            metadata: Optional additional event data
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'journey_id': journey_id,
            'user_id': user_id,
            'metadata': metadata or {}
        }
        self.audit_log.append(entry)
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """
        Get the complete audit log.
        
        Returns:
            List of audit log entries
        """
        return self.audit_log.copy()
