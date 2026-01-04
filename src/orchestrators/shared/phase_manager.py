"""
Phase Manager - State machine for phase transitions and execution flow

Manages phase lifecycle, state transitions, and execution coordination
for both planning and ADO orchestrators.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PhaseState(Enum):
    """Phase execution states."""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    DEFERRED = "deferred"
    SKIPPED = "skipped"


class PhaseTransition(Enum):
    """Valid phase transitions."""
    START = "start"  # not-started -> in-progress
    COMPLETE = "complete"  # in-progress -> completed
    FAIL = "fail"  # in-progress -> failed
    BLOCK = "block"  # not-started/in-progress -> blocked
    UNBLOCK = "unblock"  # blocked -> not-started/in-progress
    DEFER = "defer"  # not-started/in-progress -> deferred
    SKIP = "skip"  # not-started -> skipped
    RETRY = "retry"  # failed -> not-started


@dataclass
class PhaseTransitionEvent:
    """Event representing a phase state transition."""
    phase_number: int
    from_state: PhaseState
    to_state: PhaseState
    transition: PhaseTransition
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PhaseExecution:
    """Execution context for a phase."""
    phase_number: int
    phase_name: str
    state: PhaseState = PhaseState.NOT_STARTED
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    transitions: List[PhaseTransitionEvent] = field(default_factory=list)
    
    def can_transition(self, transition: PhaseTransition) -> bool:
        """Check if transition is valid from current state."""
        valid_transitions = {
            PhaseState.NOT_STARTED: [
                PhaseTransition.START,
                PhaseTransition.BLOCK,
                PhaseTransition.DEFER,
                PhaseTransition.SKIP
            ],
            PhaseState.IN_PROGRESS: [
                PhaseTransition.COMPLETE,
                PhaseTransition.FAIL,
                PhaseTransition.BLOCK,
                PhaseTransition.DEFER
            ],
            PhaseState.COMPLETED: [],  # Terminal state
            PhaseState.BLOCKED: [
                PhaseTransition.UNBLOCK
            ],
            PhaseState.FAILED: [
                PhaseTransition.RETRY,
                PhaseTransition.DEFER
            ],
            PhaseState.DEFERRED: [
                PhaseTransition.START
            ],
            PhaseState.SKIPPED: []  # Terminal state
        }
        
        return transition in valid_transitions.get(self.state, [])
    
    def transition_to(
        self,
        transition: PhaseTransition,
        reason: Optional[str] = None,
        **metadata
    ) -> bool:
        """
        Execute state transition.
        
        Returns:
            True if transition successful, False otherwise
        """
        if not self.can_transition(transition):
            logger.warning(
                f"Invalid transition {transition.value} from state {self.state.value} "
                f"for phase {self.phase_number}"
            )
            return False
        
        # Determine target state
        state_map = {
            PhaseTransition.START: PhaseState.IN_PROGRESS,
            PhaseTransition.COMPLETE: PhaseState.COMPLETED,
            PhaseTransition.FAIL: PhaseState.FAILED,
            PhaseTransition.BLOCK: PhaseState.BLOCKED,
            PhaseTransition.UNBLOCK: PhaseState.NOT_STARTED,
            PhaseTransition.DEFER: PhaseState.DEFERRED,
            PhaseTransition.SKIP: PhaseState.SKIPPED,
            PhaseTransition.RETRY: PhaseState.NOT_STARTED
        }
        
        old_state = self.state
        new_state = state_map[transition]
        
        # Record transition
        event = PhaseTransitionEvent(
            phase_number=self.phase_number,
            from_state=old_state,
            to_state=new_state,
            transition=transition,
            reason=reason,
            metadata=metadata
        )
        self.transitions.append(event)
        
        # Update state
        self.state = new_state
        
        # Update timestamps
        if transition == PhaseTransition.START:
            self.started_at = datetime.now().isoformat()
        elif transition == PhaseTransition.COMPLETE:
            self.completed_at = datetime.now().isoformat()
        elif transition == PhaseTransition.FAIL:
            self.failed_at = datetime.now().isoformat()
        elif transition == PhaseTransition.RETRY:
            self.retry_count += 1
            self.failed_at = None
            self.error = None
        
        logger.info(
            f"Phase {self.phase_number} transitioned: {old_state.value} -> {new_state.value}"
        )
        
        return True


class PhaseManager:
    """
    Orchestrator phase manager.
    
    Coordinates phase execution, enforces state transitions,
    and manages phase dependencies.
    """
    
    def __init__(self, orchestrator_name: str):
        """Initialize phase manager."""
        self.orchestrator_name = orchestrator_name
        self.phases: Dict[int, PhaseExecution] = {}
        self.current_phase: Optional[int] = None
        self.hooks: Dict[str, List[Callable]] = {
            "before_phase": [],
            "after_phase": [],
            "on_error": [],
            "on_complete": []
        }
    
    def register_phase(self, phase_number: int, phase_name: str, max_retries: int = 3) -> None:
        """Register a phase with the manager."""
        self.phases[phase_number] = PhaseExecution(
            phase_number=phase_number,
            phase_name=phase_name,
            max_retries=max_retries
        )
    
    def get_phase(self, phase_number: int) -> Optional[PhaseExecution]:
        """Get phase execution context."""
        return self.phases.get(phase_number)
    
    def start_phase(self, phase_number: int, reason: Optional[str] = None) -> bool:
        """
        Start phase execution.
        
        Returns:
            True if started successfully
        """
        phase = self.get_phase(phase_number)
        if not phase:
            logger.error(f"Phase {phase_number} not registered")
            return False
        
        # Run before hooks
        self._run_hooks("before_phase", phase)
        
        success = phase.transition_to(PhaseTransition.START, reason)
        if success:
            self.current_phase = phase_number
        
        return success
    
    def complete_phase(self, phase_number: int, reason: Optional[str] = None, **metadata) -> bool:
        """
        Mark phase as completed.
        
        Returns:
            True if completed successfully
        """
        phase = self.get_phase(phase_number)
        if not phase:
            return False
        
        success = phase.transition_to(PhaseTransition.COMPLETE, reason, **metadata)
        
        if success:
            # Run after hooks
            self._run_hooks("after_phase", phase)
            
            # Check if all phases complete
            if self.is_all_complete():
                self._run_hooks("on_complete", phase)
        
        return success
    
    def fail_phase(self, phase_number: int, error: str, **metadata) -> bool:
        """
        Mark phase as failed.
        
        Returns:
            True if marked failed successfully
        """
        phase = self.get_phase(phase_number)
        if not phase:
            return False
        
        phase.error = error
        success = phase.transition_to(PhaseTransition.FAIL, error, **metadata)
        
        if success:
            # Run error hooks
            self._run_hooks("on_error", phase)
        
        return success
    
    def retry_phase(self, phase_number: int) -> bool:
        """
        Retry failed phase.
        
        Returns:
            True if retry successful, False if max retries exceeded
        """
        phase = self.get_phase(phase_number)
        if not phase:
            return False
        
        if phase.retry_count >= phase.max_retries:
            logger.warning(
                f"Phase {phase_number} exceeded max retries ({phase.max_retries})"
            )
            return False
        
        return phase.transition_to(PhaseTransition.RETRY, "Retrying after failure")
    
    def block_phase(self, phase_number: int, reason: str) -> bool:
        """Block phase execution."""
        phase = self.get_phase(phase_number)
        if not phase:
            return False
        
        return phase.transition_to(PhaseTransition.BLOCK, reason)
    
    def unblock_phase(self, phase_number: int) -> bool:
        """Unblock phase execution."""
        phase = self.get_phase(phase_number)
        if not phase:
            return False
        
        return phase.transition_to(PhaseTransition.UNBLOCK, "Unblocking phase")
    
    def defer_phase(self, phase_number: int, reason: str) -> bool:
        """Defer phase for later execution."""
        phase = self.get_phase(phase_number)
        if not phase:
            return False
        
        return phase.transition_to(PhaseTransition.DEFER, reason)
    
    def skip_phase(self, phase_number: int, reason: str) -> bool:
        """Skip phase execution."""
        phase = self.get_phase(phase_number)
        if not phase:
            return False
        
        return phase.transition_to(PhaseTransition.SKIP, reason)
    
    def get_next_phase(self) -> Optional[PhaseExecution]:
        """Get next phase to execute (first not completed)."""
        for phase_num in sorted(self.phases.keys()):
            phase = self.phases[phase_num]
            if phase.state in [PhaseState.NOT_STARTED, PhaseState.IN_PROGRESS]:
                return phase
        return None
    
    def is_all_complete(self) -> bool:
        """Check if all phases are completed."""
        return all(
            p.state in [PhaseState.COMPLETED, PhaseState.SKIPPED]
            for p in self.phases.values()
        )
    
    def get_progress_percentage(self) -> int:
        """Calculate overall progress percentage."""
        if not self.phases:
            return 0
        
        completed = sum(
            1 for p in self.phases.values()
            if p.state in [PhaseState.COMPLETED, PhaseState.SKIPPED]
        )
        
        return int((completed / len(self.phases)) * 100)
    
    def register_hook(self, hook_type: str, callback: Callable) -> None:
        """
        Register lifecycle hook.
        
        Args:
            hook_type: One of "before_phase", "after_phase", "on_error", "on_complete"
            callback: Callable taking PhaseExecution as argument
        """
        if hook_type in self.hooks:
            self.hooks[hook_type].append(callback)
    
    def _run_hooks(self, hook_type: str, phase: PhaseExecution) -> None:
        """Run registered hooks."""
        for callback in self.hooks.get(hook_type, []):
            try:
                callback(phase)
            except Exception as e:
                logger.error(f"Hook {hook_type} failed: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        states = {}
        for state in PhaseState:
            states[state.value] = sum(
                1 for p in self.phases.values() if p.state == state
            )
        
        return {
            "orchestrator": self.orchestrator_name,
            "total_phases": len(self.phases),
            "current_phase": self.current_phase,
            "progress_percentage": self.get_progress_percentage(),
            "phase_states": states,
            "is_complete": self.is_all_complete()
        }
