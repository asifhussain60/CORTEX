"""
State Machine - Lifecycle and Transition Management (AC-FR-003)

Implements deterministic state transitions for:
- AC lifecycle (DRAFT → ACTIVE → REVIEWING → LOCKED)
- Phase state tracking (PLANNING → IMPLEMENTING → VALIDATING → COMPLETE)
- Atomic transition guarantees (validate → lock → commit)

Features:
- Atomic transitions (all-or-nothing)
- Invalid transition rejection with audit trail
- State history tracking (previous → current → next)
- Transition validation with governance checks
- Recovery from interrupted transitions

Author: Asif Hussain
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from cortex.brain.core.result import Err, Ok, Result


class ACState(Enum):
    """Lifecycle states for Acceptance Criteria."""
    DRAFT = auto()
    ACTIVE = auto()
    REVIEWING = auto()
    LOCKED = auto()


class PhaseState(Enum):
    """Lifecycle states for Phases."""
    PLANNING = auto()
    IMPLEMENTING = auto()
    VALIDATING = auto()
    COMPLETE = auto()


class TransitionType(Enum):
    """Types of transitions for audit trail."""
    NORMAL = auto()
    ROLLBACK = auto()
    EMERGENCY = auto()


@dataclass
class StateTransition:
    """Records a state transition in the history."""
    timestamp: str
    from_state: str
    to_state: str
    transition_type: TransitionType
    ac_id: Optional[str] = None
    phase_id: Optional[str] = None
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    transition_hash: Optional[str] = None


@dataclass
class StateSnapshot:
    """Snapshot of current state."""
    current_state: str
    previous_state: Optional[str]
    next_allowed_states: List[str]
    last_transition_time: str
    transition_count: int
    is_locked: bool


class StateMachine:
    """
    Deterministic state machine for AC and Phase lifecycle.

    Thread-safe singleton managing:
    - Atomic state transitions
    - Invalid transition rejection
    - History tracking for compliance
    """

    _instance: Optional['StateMachine'] = None
    _lock = threading.Lock()

    # State transition rules
    AC_TRANSITIONS = {
        ACState.DRAFT: [ACState.ACTIVE],
        ACState.ACTIVE: [ACState.REVIEWING, ACState.DRAFT],
        ACState.REVIEWING: [ACState.LOCKED, ACState.ACTIVE],
        ACState.LOCKED: [],  # Terminal state
    }

    PHASE_TRANSITIONS = {
        PhaseState.PLANNING: [PhaseState.IMPLEMENTING],
        PhaseState.IMPLEMENTING: [PhaseState.VALIDATING, PhaseState.PLANNING],
        PhaseState.VALIDATING: [PhaseState.COMPLETE, PhaseState.IMPLEMENTING],
        PhaseState.COMPLETE: [],  # Terminal state
    }

    def __init__(self):
        """
        Initialize state machine.
        """
        self._ac_states: Dict[str, ACState] = {}
        self._phase_states: Dict[str, PhaseState] = {}
        self._transition_history: List[StateTransition] = []
        self._state_lock = threading.Lock()

    @classmethod
    def instance(cls) -> 'StateMachine':
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None

    def initialize_ac(self, ac_id: str, initial_state: ACState = ACState.DRAFT) -> Result[None]:
        """
        Initialize AC state machine.

        Args:
            ac_id: Acceptance Criteria ID
            initial_state: Initial state (defaults to DRAFT)

        Returns:
            Result indicating success or error
        """
        with self._state_lock:
            if ac_id in self._ac_states:
                return Err(f"AC {ac_id} already initialized")

            self._ac_states[ac_id] = initial_state

            # Record initialization as first transition
            transition = StateTransition(
                timestamp=datetime.now(timezone.utc).isoformat(),
                from_state="NONE",
                to_state=initial_state.name,
                transition_type=TransitionType.NORMAL,
                ac_id=ac_id,
                reason="Initialization",
            )
            self._transition_history.append(transition)

            return Ok(None)

    def initialize_phase(self, phase_id: str, initial_state: PhaseState = PhaseState.PLANNING) -> Result[None]:
        """
        Initialize Phase state machine.

        Args:
            phase_id: Phase ID
            initial_state: Initial state (defaults to PLANNING)

        Returns:
            Result indicating success or error
        """
        with self._state_lock:
            if phase_id in self._phase_states:
                return Err(f"Phase {phase_id} already initialized")

            self._phase_states[phase_id] = initial_state

            # Record initialization
            transition = StateTransition(
                timestamp=datetime.now(timezone.utc).isoformat(),
                from_state="NONE",
                to_state=initial_state.name,
                transition_type=TransitionType.NORMAL,
                phase_id=phase_id,
                reason="Initialization",
            )
            self._transition_history.append(transition)

            return Ok(None)

    def transition_ac(
        self,
        ac_id: str,
        to_state: ACState,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[StateSnapshot]:
        """
        Perform atomic AC state transition.

        AC-FR-003-01: Atomic transitions (validate → lock → commit)

        Args:
            ac_id: Acceptance Criteria ID
            to_state: Target state
            reason: Optional reason for transition
            metadata: Optional transition metadata

        Returns:
            Result containing StateSnapshot if successful
        """
        with self._state_lock:
            # Validate AC exists
            if ac_id not in self._ac_states:
                return Err(f"AC {ac_id} not found")

            current_state = self._ac_states[ac_id]

            # Validate transition is allowed
            allowed_states = self.AC_TRANSITIONS.get(current_state, [])
            if to_state not in allowed_states:
                return Err(
                    f"Invalid transition: {current_state.name} → {to_state.name}. "
                    f"Allowed: {[s.name for s in allowed_states]}"
                )

            # Perform atomic transition (lock already held)
            previous_state = current_state
            self._ac_states[ac_id] = to_state

            # Record transition
            transition = StateTransition(
                timestamp=datetime.now(timezone.utc).isoformat(),
                from_state=previous_state.name,
                to_state=to_state.name,
                transition_type=TransitionType.NORMAL,
                ac_id=ac_id,
                reason=reason,
                metadata=metadata or {},
            )
            self._transition_history.append(transition)

            # Persist to database if available
            if self._db:
                persist_result = self._persist_transition(transition)
                if persist_result.is_err():
                    # Rollback transition
                    self._ac_states[ac_id] = previous_state
                    self._transition_history.pop()
                    return persist_result

            # Return snapshot
            next_allowed = self.AC_TRANSITIONS.get(to_state, [])
            snapshot = StateSnapshot(
                current_state=to_state.name,
                previous_state=previous_state.name,
                next_allowed_states=[s.name for s in next_allowed],
                last_transition_time=transition.timestamp,
                transition_count=len([t for t in self._transition_history if t.ac_id == ac_id]),
                is_locked=to_state == ACState.LOCKED,
            )

            return Ok(snapshot)

    def transition_phase(
        self,
        phase_id: str,
        to_state: PhaseState,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[StateSnapshot]:
        """
        Perform atomic Phase state transition.

        Args:
            phase_id: Phase ID
            to_state: Target state
            reason: Optional reason for transition
            metadata: Optional transition metadata

        Returns:
            Result containing StateSnapshot if successful
        """
        with self._state_lock:
            # Validate phase exists
            if phase_id not in self._phase_states:
                return Err(f"Phase {phase_id} not found")

            current_state = self._phase_states[phase_id]

            # Validate transition is allowed
            allowed_states = self.PHASE_TRANSITIONS.get(current_state, [])
            if to_state not in allowed_states:
                return Err(
                    f"Invalid transition: {current_state.name} → {to_state.name}. "
                    f"Allowed: {[s.name for s in allowed_states]}"
                )

            # Perform atomic transition
            previous_state = current_state
            self._phase_states[phase_id] = to_state

            # Record transition
            transition = StateTransition(
                timestamp=datetime.now(timezone.utc).isoformat(),
                from_state=previous_state.name,
                to_state=to_state.name,
                transition_type=TransitionType.NORMAL,
                phase_id=phase_id,
                reason=reason,
                metadata=metadata or {},
            )
            self._transition_history.append(transition)

            # Persist to database
            if self._db:
                persist_result = self._persist_transition(transition)
                if persist_result.is_err():
                    # Rollback
                    self._phase_states[phase_id] = previous_state
                    self._transition_history.pop()
                    return persist_result

            # Return snapshot
            next_allowed = self.PHASE_TRANSITIONS.get(to_state, [])
            snapshot = StateSnapshot(
                current_state=to_state.name,
                previous_state=previous_state.name,
                next_allowed_states=[s.name for s in next_allowed],
                last_transition_time=transition.timestamp,
                transition_count=len([t for t in self._transition_history if t.phase_id == phase_id]),
                is_locked=to_state == PhaseState.COMPLETE,
            )

            return Ok(snapshot)

    def get_ac_state(self, ac_id: str) -> Result[StateSnapshot]:
        """
        Get current AC state.

        Args:
            ac_id: Acceptance Criteria ID

        Returns:
            Result containing current state snapshot
        """
        with self._state_lock:
            if ac_id not in self._ac_states:
                return Err(f"AC {ac_id} not found")

            current_state = self._ac_states[ac_id]
            previous_transitions = [t for t in self._transition_history if t.ac_id == ac_id]
            previous_state = previous_transitions[-2].to_state if len(previous_transitions) > 1 else None

            next_allowed = self.AC_TRANSITIONS.get(current_state, [])

            snapshot = StateSnapshot(
                current_state=current_state.name,
                previous_state=previous_state,
                next_allowed_states=[s.name for s in next_allowed],
                last_transition_time=previous_transitions[-1].timestamp if previous_transitions else "",
                transition_count=len(previous_transitions),
                is_locked=current_state == ACState.LOCKED,
            )

            return Ok(snapshot)

    def get_phase_state(self, phase_id: str) -> Result[StateSnapshot]:
        """
        Get current Phase state.

        Args:
            phase_id: Phase ID

        Returns:
            Result containing current state snapshot
        """
        with self._state_lock:
            if phase_id not in self._phase_states:
                return Err(f"Phase {phase_id} not found")

            current_state = self._phase_states[phase_id]
            previous_transitions = [t for t in self._transition_history if t.phase_id == phase_id]
            previous_state = previous_transitions[-2].to_state if len(previous_transitions) > 1 else None

            next_allowed = self.PHASE_TRANSITIONS.get(current_state, [])

            snapshot = StateSnapshot(
                current_state=current_state.name,
                previous_state=previous_state,
                next_allowed_states=[s.name for s in next_allowed],
                last_transition_time=previous_transitions[-1].timestamp if previous_transitions else "",
                transition_count=len(previous_transitions),
                is_locked=current_state == PhaseState.COMPLETE,
            )

            return Ok(snapshot)

    def get_transition_history(self, ac_id: Optional[str] = None, phase_id: Optional[str] = None) -> Result[List[StateTransition]]:
        """
        AC-FR-003-03: State history tracking

        Get transition history filtered by AC-ID or Phase-ID.

        Args:
            ac_id: Optional AC-ID filter
            phase_id: Optional Phase-ID filter

        Returns:
            Result containing list of transitions
        """
        with self._state_lock:
            history = self._transition_history

            if ac_id:
                history = [t for t in history if t.ac_id == ac_id]
            elif phase_id:
                history = [t for t in history if t.phase_id == phase_id]

            return Ok(history)

    def _persist_transition(self, transition: StateTransition) -> Result[None]:
        """
        Persist transition to database.

        Args:
            transition: Transition to persist

        Returns:
            Result indicating success or error
        """
        if not self._db:
            return Ok(None)

        try:
            target_id = transition.ac_id or transition.phase_id

            result = self._db.insert_audit(
                operation="STATE_TRANSITION",
                component="state_machine",
                level="AUDIT",
                message=f"Transition: {transition.from_state} → {transition.to_state}",
                ac_id=transition.ac_id,
                metadata={
                    "from_state": transition.from_state,
                    "to_state": transition.to_state,
                    "transition_type": transition.transition_type.name,
                    "reason": transition.reason,
                    "phase_id": transition.phase_id,
                    "details": transition.metadata,
                },
            )

            return result
        except Exception as e:
            return Err(f"Failed to persist transition: {str(e)}")
