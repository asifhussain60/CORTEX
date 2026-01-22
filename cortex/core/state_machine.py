
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum
from datetime import datetime


class TransitionType(Enum):
    """Types of state transitions."""
    FORWARD = "forward"
    VALIDATE = "validate"
    LOCK = "lock"
    COMMIT = "commit"
    ROLLBACK = "rollback"
    RESUME = "resume"


@dataclass
class StateSnapshot:
    """Snapshot of a state at a point in time."""
    entity_id: str
    current_state: str
    previous_state: Optional[str] = None
    is_locked: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StateTransition:
    """Represents a state transition."""
    from_state: str
    to_state: str
    transition_type: TransitionType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ACState:
    """AC State management."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    COMMITTED = "COMMITTED"
    REVERTED = "REVERTED"


class PhaseState:
    """Phase State management."""
    PLANNING = "PLANNING"
    EXECUTION = "EXECUTION"
    VALIDATION = "VALIDATION"
    COMPLETE = "COMPLETE"


class Result:
    """Result type for operations."""
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
    
    def is_ok(self) -> bool:
        return self.error is None
    
    def is_err(self) -> bool:
        return self.error is not None
    
    def unwrap(self):
        if self.is_ok():
            return self.value
        raise Exception(self.error)


class StateMachine:
    """State machine for managing AC and Phase states."""
    
    def __init__(self):
        self.ac_states: Dict[str, StateSnapshot] = {}
        self.phase_states: Dict[str, StateSnapshot] = {}
        self.transitions: List[StateTransition] = []
    
    def initialize_ac(self, ac_id: str) -> Result:
        """Initialize AC in DRAFT state."""
        snapshot = StateSnapshot(entity_id=ac_id, current_state=ACState.DRAFT)
        self.ac_states[ac_id] = snapshot
        return Result(value=snapshot)
    
    def initialize_phase(self, phase_id: str) -> Result:
        """Initialize Phase in PLANNING state."""
        snapshot = StateSnapshot(entity_id=phase_id, current_state=PhaseState.PLANNING)
        self.phase_states[phase_id] = snapshot
        return Result(value=snapshot)
    
    def get_ac_state(self, ac_id: str) -> Result:
        """Get AC state."""
        if ac_id not in self.ac_states:
            return Result(error=f"AC {ac_id} not found")
        return Result(value=self.ac_states[ac_id])
    
    def get_phase_state(self, phase_id: str) -> Result:
        """Get Phase state."""
        if phase_id not in self.phase_states:
            return Result(error=f"Phase {phase_id} not found")
        return Result(value=self.phase_states[phase_id])
    
    def transition_ac(self, ac_id: str, to_state: str, transition_type: TransitionType, metadata: Optional[Dict[str, Any]] = None) -> Result:
        """Transition AC to new state."""
        if ac_id not in self.ac_states:
            return Result(error=f"AC {ac_id} not found")
        
        snapshot = self.ac_states[ac_id]
        from_state = snapshot.current_state
        
        # Record transition
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            transition_type=transition_type,
            metadata=metadata or {}
        )
        self.transitions.append(transition)
        
        # Update state
        snapshot.previous_state = from_state
        snapshot.current_state = to_state
        
        return Result(value=snapshot)
    
    def transition_phase(self, phase_id: str, to_state: str, transition_type: TransitionType) -> Result:
        """Transition Phase to new state."""
        if phase_id not in self.phase_states:
            return Result(error=f"Phase {phase_id} not found")
        
        snapshot = self.phase_states[phase_id]
        from_state = snapshot.current_state
        
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            transition_type=transition_type
        )
        self.transitions.append(transition)
        
        snapshot.previous_state = from_state
        snapshot.current_state = to_state
        
        return Result(value=snapshot)
    
    def lock_ac(self, ac_id: str) -> Result:
        """Lock AC state."""
        if ac_id not in self.ac_states:
            return Result(error=f"AC {ac_id} not found")
        self.ac_states[ac_id].is_locked = True
        return Result(value=self.ac_states[ac_id])
    
    def unlock_ac(self, ac_id: str) -> Result:
        """Unlock AC state."""
        if ac_id not in self.ac_states:
            return Result(error=f"AC {ac_id} not found")
        self.ac_states[ac_id].is_locked = False
        return Result(value=self.ac_states[ac_id])
    
    def get_transition_history(self, ac_id: str = None) -> Result:
        """Get transition history for AC."""
        if ac_id:
            history = [t for t in self.transitions if ac_id in [t.from_state, t.to_state]]
        else:
            history = [t for t in self.transitions]
        return Result(value=history)
    
    def validate_transition(self, from_state: str, to_state: str) -> Result:
        """Validate if transition is allowed."""
        valid_transitions = {
            ACState.DRAFT: [ACState.ACTIVE],
            ACState.ACTIVE: [ACState.LOCKED, ACState.REVERTED],
            ACState.LOCKED: [ACState.COMMITTED, ACState.REVERTED],
            ACState.COMMITTED: [],
            ACState.REVERTED: [ACState.DRAFT],
            PhaseState.PLANNING: [PhaseState.EXECUTION],
            PhaseState.EXECUTION: [PhaseState.VALIDATION],
            PhaseState.VALIDATION: [PhaseState.COMPLETE],
            PhaseState.COMPLETE: [],
        }
        
        if from_state not in valid_transitions:
            return Result(error=f"Unknown state: {from_state}")
        
        if to_state in valid_transitions[from_state]:
            return Result(value=True)
        
        return Result(error=f"Invalid transition: {from_state} -> {to_state}")


__all__ = [
    "StateMachine",
    "ACState",
    "PhaseState",
    "StateSnapshot",
    "StateTransition",
    "TransitionType",
    "Result",
]
