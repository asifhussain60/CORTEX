"""
State Machine Engine for CORTEX 4.0 Orchestrators

Provides finite state machine (FSM) validation for orchestrator workflows.
Enforces valid state transitions, guard conditions, and action hooks.

Author: Asif Hussain
Date: December 10, 2025
"""

from enum import Enum
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TransitionResult(Enum):
    """Result of a state transition attempt."""
    SUCCESS = "success"
    GUARD_FAILED = "guard_failed"
    INVALID_TRANSITION = "invalid_transition"
    ACTION_FAILED = "action_failed"


@dataclass
class StateTransition:
    """Defines a valid transition between states."""
    from_state: str
    to_state: str
    guard_conditions: List[Callable[[], bool]] = field(default_factory=list)
    actions: List[Callable[[], None]] = field(default_factory=list)
    
    def can_transition(self) -> bool:
        """Check if all guard conditions pass."""
        return all(guard() for guard in self.guard_conditions)
    
    def execute_actions(self) -> bool:
        """Execute all transition actions."""
        try:
            for action in self.actions:
                action()
            return True
        except Exception as e:
            logger.error(f"Action failed during transition: {e}")
            return False


@dataclass
class StateHistoryEntry:
    """Records a state change in history."""
    from_state: str
    to_state: str
    timestamp: datetime
    transition_result: TransitionResult
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateMachine:
    """
    Finite State Machine for orchestrator workflow validation.
    
    Ensures orchestrators follow valid state transitions and don't skip phases.
    """
    
    def __init__(self, initial_state: str, orchestrator_name: str):
        """
        Initialize state machine.
        
        Args:
            initial_state: Starting state name
            orchestrator_name: Name of orchestrator using this FSM
        """
        self.current_state = initial_state
        self.orchestrator_name = orchestrator_name
        self.transitions: Dict[tuple, StateTransition] = {}
        self.history: List[StateHistoryEntry] = []
        self.checkpoints: List[str] = []  # Recovery checkpoints
        
        logger.info(f"StateMachine initialized for {orchestrator_name} at state: {initial_state}")
    
    def register_transition(
        self,
        from_state: str,
        to_state: str,
        guard_conditions: Optional[List[Callable[[], bool]]] = None,
        actions: Optional[List[Callable[[], None]]] = None
    ) -> None:
        """
        Register a valid state transition.
        
        Args:
            from_state: Source state
            to_state: Destination state
            guard_conditions: Optional list of guard functions (must all return True)
            actions: Optional list of action functions to execute during transition
        """
        transition_key = (from_state, to_state)
        self.transitions[transition_key] = StateTransition(
            from_state=from_state,
            to_state=to_state,
            guard_conditions=guard_conditions or [],
            actions=actions or []
        )
        logger.debug(f"Registered transition: {from_state} -> {to_state}")
    
    def can_transition_to(self, to_state: str) -> tuple[bool, Optional[str]]:
        """
        Check if transition to target state is valid.
        
        Args:
            to_state: Target state to transition to
            
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        transition_key = (self.current_state, to_state)
        
        # Check if transition is registered
        if transition_key not in self.transitions:
            return False, f"No transition defined from {self.current_state} to {to_state}"
        
        # Check guard conditions
        transition = self.transitions[transition_key]
        if not transition.can_transition():
            return False, f"Guard conditions failed for transition {self.current_state} -> {to_state}"
        
        return True, None
    
    def transition_to(
        self,
        to_state: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TransitionResult:
        """
        Attempt to transition to a new state.
        
        Args:
            to_state: Target state
            metadata: Optional metadata to record with this transition
            
        Returns:
            TransitionResult indicating success or failure reason
        """
        from_state = self.current_state
        transition_key = (from_state, to_state)
        
        # Validate transition exists
        if transition_key not in self.transitions:
            logger.error(
                f"{self.orchestrator_name}: Invalid transition attempted: "
                f"{from_state} -> {to_state}"
            )
            self._record_history(from_state, to_state, TransitionResult.INVALID_TRANSITION, metadata)
            return TransitionResult.INVALID_TRANSITION
        
        transition = self.transitions[transition_key]
        
        # Check guard conditions
        if not transition.can_transition():
            logger.warning(
                f"{self.orchestrator_name}: Guard conditions failed for "
                f"{from_state} -> {to_state}"
            )
            self._record_history(from_state, to_state, TransitionResult.GUARD_FAILED, metadata)
            return TransitionResult.GUARD_FAILED
        
        # Execute transition actions
        if not transition.execute_actions():
            logger.error(
                f"{self.orchestrator_name}: Actions failed during "
                f"{from_state} -> {to_state}"
            )
            self._record_history(from_state, to_state, TransitionResult.ACTION_FAILED, metadata)
            return TransitionResult.ACTION_FAILED
        
        # Successful transition
        self.current_state = to_state
        self._record_history(from_state, to_state, TransitionResult.SUCCESS, metadata)
        
        logger.info(
            f"{self.orchestrator_name}: Transitioned {from_state} -> {to_state}"
        )
        
        return TransitionResult.SUCCESS
    
    def create_checkpoint(self) -> None:
        """Create a recovery checkpoint at current state."""
        self.checkpoints.append(self.current_state)
        logger.debug(f"{self.orchestrator_name}: Checkpoint created at {self.current_state}")
    
    def rollback_to_checkpoint(self) -> bool:
        """
        Rollback to last checkpoint.
        
        Returns:
            True if rollback successful, False if no checkpoints exist
        """
        if not self.checkpoints:
            logger.warning(f"{self.orchestrator_name}: No checkpoints available for rollback")
            return False
        
        checkpoint_state = self.checkpoints.pop()
        self.current_state = checkpoint_state
        logger.info(f"{self.orchestrator_name}: Rolled back to checkpoint: {checkpoint_state}")
        return True
    
    def get_history(self) -> List[StateHistoryEntry]:
        """Get complete state transition history."""
        return self.history.copy()
    
    def get_valid_next_states(self) -> List[str]:
        """Get list of valid states that can be transitioned to from current state."""
        return [
            to_state 
            for (from_state, to_state) in self.transitions.keys()
            if from_state == self.current_state
        ]
    
    def reset(self, new_initial_state: Optional[str] = None) -> None:
        """
        Reset state machine to initial state.
        
        Args:
            new_initial_state: Optional new initial state (uses original if not provided)
        """
        if new_initial_state:
            self.current_state = new_initial_state
        else:
            # Find the first state from history or keep current
            if self.history:
                self.current_state = self.history[0].from_state
        
        self.history.clear()
        self.checkpoints.clear()
        logger.info(f"{self.orchestrator_name}: State machine reset to {self.current_state}")
    
    def _record_history(
        self,
        from_state: str,
        to_state: str,
        result: TransitionResult,
        metadata: Optional[Dict[str, Any]]
    ) -> None:
        """Record state transition in history."""
        entry = StateHistoryEntry(
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(),
            transition_result=result,
            metadata=metadata or {}
        )
        self.history.append(entry)
    
    def __repr__(self) -> str:
        """String representation of state machine."""
        return (
            f"StateMachine(orchestrator={self.orchestrator_name}, "
            f"current_state={self.current_state}, "
            f"transitions={len(self.transitions)}, "
            f"history={len(self.history)})"
        )


class OrchestratorStates:
    """Common orchestrator states used across all orchestrators."""
    
    # Universal states
    INITIALIZED = "INITIALIZED"
    VALIDATING_DOR = "VALIDATING_DOR"
    EXECUTING = "EXECUTING"
    VALIDATING_DOD = "VALIDATING_DOD"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
    # Common execution states
    GATHERING_CONTEXT = "GATHERING_CONTEXT"
    PROCESSING = "PROCESSING"
    PERSISTING_RESULTS = "PERSISTING_RESULTS"
    
    @classmethod
    def get_all_states(cls) -> List[str]:
        """Get list of all common states."""
        return [
            value for name, value in vars(cls).items()
            if not name.startswith('_') and isinstance(value, str)
        ]


def create_basic_orchestrator_fsm(
    orchestrator_name: str,
    additional_states: Optional[List[str]] = None
) -> StateMachine:
    """
    Create a basic orchestrator FSM with standard transitions.
    
    Args:
        orchestrator_name: Name of orchestrator
        additional_states: Optional list of orchestrator-specific states
        
    Returns:
        Configured StateMachine instance
    """
    fsm = StateMachine(
        initial_state=OrchestratorStates.INITIALIZED,
        orchestrator_name=orchestrator_name
    )
    
    # Register standard transitions
    fsm.register_transition(
        OrchestratorStates.INITIALIZED,
        OrchestratorStates.VALIDATING_DOR
    )
    
    fsm.register_transition(
        OrchestratorStates.VALIDATING_DOR,
        OrchestratorStates.EXECUTING
    )
    
    fsm.register_transition(
        OrchestratorStates.VALIDATING_DOR,
        OrchestratorStates.FAILED
    )
    
    fsm.register_transition(
        OrchestratorStates.EXECUTING,
        OrchestratorStates.VALIDATING_DOD
    )
    
    fsm.register_transition(
        OrchestratorStates.EXECUTING,
        OrchestratorStates.FAILED
    )
    
    fsm.register_transition(
        OrchestratorStates.VALIDATING_DOD,
        OrchestratorStates.COMPLETED
    )
    
    fsm.register_transition(
        OrchestratorStates.VALIDATING_DOD,
        OrchestratorStates.FAILED
    )
    
    logger.info(f"Created basic FSM for {orchestrator_name} with standard transitions")
    
    return fsm
