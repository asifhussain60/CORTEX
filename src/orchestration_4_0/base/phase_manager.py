"""
Phase Manager for CORTEX 4.0 Orchestrators

Handles phase transitions, validation, and state management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
import logging


class PhaseStatus(Enum):
    """Phase execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Phase:
    """
    Represents a single phase in an orchestrator workflow.
    
    Attributes:
        name: Phase identifier (e.g., "analyze", "transform")
        description: Human-readable phase description
        required: Whether phase must complete successfully
        validation: Optional validation function to run before phase
        cleanup: Optional cleanup function to run after phase
    """
    name: str
    description: str
    required: bool = True
    validation: Optional[Callable[[], bool]] = None
    cleanup: Optional[Callable[[], None]] = None
    status: PhaseStatus = PhaseStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


@dataclass
class PhaseTransition:
    """
    Represents a transition between phases.
    
    Attributes:
        from_phase: Source phase name
        to_phase: Target phase name
        condition: Optional condition function (must return True to transition)
        timestamp: When transition occurred
    """
    from_phase: str
    to_phase: str
    condition: Optional[Callable[[], bool]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PhaseManager:
    """
    Manages phase execution and transitions for orchestrators.
    
    Features:
    - Phase registration and ordering
    - Validation before phase execution
    - State tracking (pending → in_progress → completed/failed)
    - Transition history
    - Rollback support
    """
    
    def __init__(self, orchestrator_name: str):
        """
        Initialize phase manager.
        
        Args:
            orchestrator_name: Name of owning orchestrator
        """
        self.orchestrator_name = orchestrator_name
        self.phases: List[Phase] = []
        self.current_phase: Optional[Phase] = None
        self.transitions: List[PhaseTransition] = []
        self.logger = logging.getLogger(f"cortex.orchestration.{orchestrator_name}.phases")
    
    def register_phase(
        self,
        name: str,
        description: str,
        required: bool = True,
        validation: Optional[Callable[[], bool]] = None,
        cleanup: Optional[Callable[[], None]] = None
    ) -> Phase:
        """
        Register a new phase.
        
        Args:
            name: Phase identifier
            description: Human-readable description
            required: Whether phase must complete successfully
            validation: Optional pre-phase validation
            cleanup: Optional post-phase cleanup
            
        Returns:
            Registered Phase object
        """
        phase = Phase(
            name=name,
            description=description,
            required=required,
            validation=validation,
            cleanup=cleanup
        )
        self.phases.append(phase)
        self.logger.debug(f"Registered phase: {name} (required={required})")
        return phase
    
    def start_phase(self, phase_name: str) -> None:
        """
        Start execution of a phase.
        
        Args:
            phase_name: Name of phase to start
            
        Raises:
            ValueError: If phase not found or already started
        """
        phase = self._get_phase(phase_name)
        
        if phase.status == PhaseStatus.IN_PROGRESS:
            raise ValueError(f"Phase {phase_name} already in progress")
        
        if phase.status == PhaseStatus.COMPLETED:
            raise ValueError(f"Phase {phase_name} already completed")
        
        # Run validation if provided
        if phase.validation:
            self.logger.debug(f"Running validation for phase: {phase_name}")
            if not phase.validation():
                raise ValueError(f"Validation failed for phase: {phase_name}")
        
        # Record transition
        if self.current_phase:
            transition = PhaseTransition(
                from_phase=self.current_phase.name,
                to_phase=phase_name
            )
            self.transitions.append(transition)
            self.logger.info(f"🎭 Phase transition: {self.current_phase.name} → {phase_name}")
        else:
            self.logger.info(f"🎭 Starting first phase: {phase_name}")
        
        # Update phase state
        phase.status = PhaseStatus.IN_PROGRESS
        phase.started_at = datetime.now()
        self.current_phase = phase
    
    def complete_phase(self, phase_name: str, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark phase as completed.
        
        Args:
            phase_name: Name of phase to complete
            result: Optional result data
            
        Raises:
            ValueError: If phase not in progress
        """
        phase = self._get_phase(phase_name)
        
        if phase.status != PhaseStatus.IN_PROGRESS:
            raise ValueError(f"Phase {phase_name} not in progress")
        
        phase.status = PhaseStatus.COMPLETED
        phase.completed_at = datetime.now()
        phase.result = result
        
        duration = (phase.completed_at - phase.started_at).total_seconds()
        self.logger.info(f"✅ Phase completed: {phase_name} ({duration:.2f}s)")
        
        # Run cleanup if provided
        if phase.cleanup:
            self.logger.debug(f"Running cleanup for phase: {phase_name}")
            phase.cleanup()
    
    def fail_phase(self, phase_name: str, error: str) -> None:
        """
        Mark phase as failed.
        
        Args:
            phase_name: Name of phase that failed
            error: Error message
            
        Raises:
            ValueError: If phase not in progress
        """
        phase = self._get_phase(phase_name)
        
        if phase.status != PhaseStatus.IN_PROGRESS:
            raise ValueError(f"Phase {phase_name} not in progress")
        
        phase.status = PhaseStatus.FAILED
        phase.completed_at = datetime.now()
        phase.error = error
        
        duration = (phase.completed_at - phase.started_at).total_seconds()
        self.logger.error(f"❌ Phase failed: {phase_name} ({duration:.2f}s) - {error}")
    
    def skip_phase(self, phase_name: str, reason: str) -> None:
        """
        Mark phase as skipped.
        
        Args:
            phase_name: Name of phase to skip
            reason: Why phase was skipped
        """
        phase = self._get_phase(phase_name)
        phase.status = PhaseStatus.SKIPPED
        phase.error = reason
        self.logger.info(f"⏭️  Phase skipped: {phase_name} - {reason}")
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current progress through phases.
        
        Returns:
            Dictionary with progress metrics
        """
        total = len(self.phases)
        completed = sum(1 for p in self.phases if p.status == PhaseStatus.COMPLETED)
        failed = sum(1 for p in self.phases if p.status == PhaseStatus.FAILED)
        skipped = sum(1 for p in self.phases if p.status == PhaseStatus.SKIPPED)
        in_progress_count = sum(1 for p in self.phases if p.status == PhaseStatus.IN_PROGRESS)
        
        return {
            "total_phases": total,
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "in_progress": in_progress_count,
            "pending": total - completed - failed - skipped - in_progress_count,
            "progress_percent": (completed / total * 100) if total > 0 else 0,
            "current_phase": self.current_phase.name if self.current_phase else None
        }
    
    def get_phase_status(self, phase_name: str) -> PhaseStatus:
        """Get status of a specific phase"""
        phase = self._get_phase(phase_name)
        return phase.status
    
    def _get_phase(self, phase_name: str) -> Phase:
        """Get phase by name"""
        for phase in self.phases:
            if phase.name == phase_name:
                return phase
        raise ValueError(f"Phase not found: {phase_name}")
    
    def reset(self) -> None:
        """Reset all phases to pending state"""
        for phase in self.phases:
            phase.status = PhaseStatus.PENDING
            phase.started_at = None
            phase.completed_at = None
            phase.error = None
            phase.result = None
        self.current_phase = None
        self.transitions.clear()
        self.logger.info("🔄 Phase manager reset")
