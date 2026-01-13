"""
AC-LIFECYCLE-001: Lifecycle State Management
7-state orchestrator lifecycle with transition validation and quarantine.
"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional


class LifecycleState(Enum):
    """7-state orchestrator lifecycle."""
    IDLE = "idle"
    SPEC = "spec"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    VERIFIED = "verified"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


@dataclass
class TransitionResult:
    """Result of state transition attempt."""
    success: bool
    from_state: LifecycleState
    to_state: LifecycleState
    message: str
    timestamp: datetime


class LifecycleManager:
    """
    Manages orchestrator lifecycle state transitions.
    
    Valid transitions:
    - IDLE → SPEC
    - SPEC → IMPLEMENTED
    - IMPLEMENTED → TESTED
    - TESTED → VERIFIED
    - VERIFIED → ACTIVE
    - ACTIVE → DEPRECATED
    - ACTIVE → QUARANTINE (auto, on error threshold)
    """
    
    VALID_TRANSITIONS = {
        LifecycleState.IDLE: [LifecycleState.SPEC],
        LifecycleState.SPEC: [LifecycleState.IMPLEMENTED],
        LifecycleState.IMPLEMENTED: [LifecycleState.TESTED],
        LifecycleState.TESTED: [LifecycleState.VERIFIED],
        LifecycleState.VERIFIED: [LifecycleState.ACTIVE],
        LifecycleState.ACTIVE: [LifecycleState.DEPRECATED],
        LifecycleState.DEPRECATED: [],
    }
    
    ERROR_THRESHOLD = 0.10  # 10% error rate triggers quarantine
    
    def __init__(self):
        self.current_state = LifecycleState.IDLE
        self._state_history: List[Dict] = []
        self._error_count = 0
        self._success_count = 0
        self.is_quarantined = False
    
    def transition_to(self, target_state: LifecycleState) -> TransitionResult:
        """
        Attempt state transition with validation.
        
        Args:
            target_state: Desired lifecycle state
            
        Returns:
            TransitionResult with success status
        """
        from_state = self.current_state
        
        # Check if transition is valid
        valid_targets = self.VALID_TRANSITIONS.get(from_state, [])
        if target_state not in valid_targets:
            return TransitionResult(
                success=False,
                from_state=from_state,
                to_state=target_state,
                message=f"Invalid transition: {from_state.value} → {target_state.value}",
                timestamp=datetime.utcnow()
            )
        
        # Execute transition
        self.current_state = target_state
        
        # Log to audit trail
        self._state_history.append({
            'from_state': from_state.value.upper(),
            'to_state': target_state.value.upper(),
            'timestamp': datetime.utcnow().isoformat(),
            'success': True
        })
        
        return TransitionResult(
            success=True,
            from_state=from_state,
            to_state=target_state,
            message=f"Transition successful: {from_state.value} → {target_state.value}",
            timestamp=datetime.utcnow()
        )
    
    def record_error(self):
        """Record operation error and check quarantine threshold."""
        self._error_count += 1
        self._check_quarantine()
    
    def record_success(self):
        """Record successful operation."""
        self._success_count += 1
        self._check_quarantine()
    
    def _check_quarantine(self):
        """Auto-quarantine if error rate exceeds threshold."""
        total_ops = self._error_count + self._success_count
        if total_ops > 0:
            error_rate = self._error_count / total_ops
            if error_rate > self.ERROR_THRESHOLD:
                self.is_quarantined = True
    
    def get_state_history(self) -> List[Dict]:
        """Return state transition history for audit."""
        return self._state_history.copy()
