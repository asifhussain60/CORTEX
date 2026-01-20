"""
Phase State Machine Implementation (AC-STATE-002-06).

Atomic phase state transitions with FSM validation, conflict resolution,
and comprehensive audit trail.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


class PhaseState(Enum):
    """Valid phase states."""
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    LOCKED = "LOCKED"


@dataclass
class TransitionEntry:
    """Audit entry for state transition."""
    timestamp: str
    from_state: Optional[PhaseState]
    to_state: PhaseState


@dataclass
class PhaseInfo:
    """Phase state information."""
    phase_id: str
    current_state: PhaseState
    version: int = 1
    history: List[TransitionEntry] = field(default_factory=list)


@dataclass
class StateMachineMetrics:
    """State machine metrics."""
    total_transitions: int = 0
    invalid_transitions: int = 0


class InvalidTransitionError(Exception):
    """Raised when invalid state transition attempted."""
    pass


class PhaseNotFoundError(Exception):
    """Raised when phase does not exist."""
    pass


class PhaseStateMachine:
    """
    Finite state machine for phase lifecycle management.
    
    Valid transitions:
    - PLANNED → IN_PROGRESS
    - IN_PROGRESS → COMPLETED
    - COMPLETED → LOCKED
    
    All other transitions are invalid and will raise InvalidTransitionError.
    """
    
    # Valid state transition matrix
    _VALID_TRANSITIONS = {
        PhaseState.PLANNED: {PhaseState.IN_PROGRESS},
        PhaseState.IN_PROGRESS: {PhaseState.COMPLETED, PhaseState.IN_PROGRESS},  # Idempotent
        PhaseState.COMPLETED: {PhaseState.LOCKED, PhaseState.COMPLETED},  # Idempotent
        PhaseState.LOCKED: {PhaseState.LOCKED},  # Idempotent only
    }
    
    def __init__(self):
        """Initialize phase state machine."""
        self._phases: Dict[str, PhaseInfo] = {}
        self._lock = threading.RLock()
        self._metrics = StateMachineMetrics()
    
    def create_phase(self, phase_id: str) -> None:
        """
        Create new phase in PLANNED state.
        
        Args:
            phase_id: Unique phase identifier
        """
        with self._lock:
            if phase_id in self._phases:
                return  # Idempotent
            
            phase = PhaseInfo(
                phase_id=phase_id,
                current_state=PhaseState.PLANNED,
                history=[
                    TransitionEntry(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        from_state=None,
                        to_state=PhaseState.PLANNED,
                    )
                ],
            )
            self._phases[phase_id] = phase
    
    def transition(self, phase_id: str, new_state: PhaseState) -> None:
        """
        Transition phase to new state (atomic CAS operation).
        
        Args:
            phase_id: Phase to transition
            new_state: Target state
            
        Raises:
            PhaseNotFoundError: If phase doesn't exist
            InvalidTransitionError: If transition invalid
        """
        with self._lock:
            if phase_id not in self._phases:
                raise PhaseNotFoundError(f"Phase '{phase_id}' not found")
            
            phase = self._phases[phase_id]
            current_state = phase.current_state
            
            # Check if transition is valid
            if new_state not in self._VALID_TRANSITIONS.get(current_state, set()):
                self._metrics.invalid_transitions += 1
                raise InvalidTransitionError(
                    f"Invalid transition: {current_state.value} → {new_state.value}"
                )
            
            # Idempotent: if already in target state, just return
            if current_state == new_state:
                return
            
            # Atomic state change with version increment
            phase.current_state = new_state
            phase.version += 1
            phase.history.append(
                TransitionEntry(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    from_state=current_state,
                    to_state=new_state,
                )
            )
            
            self._metrics.total_transitions += 1
    
    def get_state(self, phase_id: str) -> PhaseState:
        """
        Get current phase state.
        
        Args:
            phase_id: Phase identifier
            
        Returns:
            Current phase state
            
        Raises:
            PhaseNotFoundError: If phase doesn't exist
        """
        with self._lock:
            if phase_id not in self._phases:
                raise PhaseNotFoundError(f"Phase '{phase_id}' not found")
            return self._phases[phase_id].current_state
    
    def get_history(self, phase_id: str) -> List[Dict[str, str]]:
        """
        Get phase transition history.
        
        Args:
            phase_id: Phase identifier
            
        Returns:
            List of transition entries
        """
        with self._lock:
            if phase_id not in self._phases:
                raise PhaseNotFoundError(f"Phase '{phase_id}' not found")
            
            phase = self._phases[phase_id]
            return [
                {
                    "timestamp": entry.timestamp,
                    "from_state": entry.from_state.value if entry.from_state else None,
                    "to_state": entry.to_state.value,
                }
                for entry in phase.history
            ]
    
    def list_phases_by_state(self, state: PhaseState) -> List[str]:
        """
        List all phases in given state.
        
        Args:
            state: State to filter by
            
        Returns:
            List of phase IDs
        """
        with self._lock:
            return [
                phase_id
                for phase_id, phase in self._phases.items()
                if phase.current_state == state
            ]
    
    def get_metrics(self) -> Dict[str, int]:
        """
        Get state machine metrics.
        
        Returns:
            Metrics dictionary
        """
        return {
            "total_phases": len(self._phases),
            "total_transitions": self._metrics.total_transitions,
            "invalid_transitions": self._metrics.invalid_transitions,
        }
