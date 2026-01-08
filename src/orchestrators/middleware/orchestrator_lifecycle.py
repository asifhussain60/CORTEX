"""
Orchestrator Lifecycle Management
==================================
Manages lifecycle states, transitions, and health checks for orchestrators.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Task: 1.4
TDD Phase: GREEN
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Set
from datetime import datetime
import traceback

from ..audit_logger import get_audit_logger, AuditCategory, AuditLevel


# =============================================================================
# Enums
# =============================================================================

class LifecycleState(Enum):
    """Orchestrator lifecycle states"""
    INITIALIZED = "initialized"  # Just created, not ready
    READY = "ready"             # Ready to execute
    RUNNING = "running"         # Currently executing
    PAUSED = "paused"           # Paused execution
    STOPPED = "stopped"         # Cleanly stopped
    ERROR = "error"             # Error state


class HealthStatus(Enum):
    """Health check statuses"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LifecycleTransition:
    """Represents a lifecycle state transition"""
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: datetime
    error: Optional[str] = None


@dataclass
class HealthCheck:
    """Health check result"""
    overall_status: HealthStatus
    checks: Dict[str, HealthStatus] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Exceptions
# =============================================================================

class LifecycleError(Exception):
    """Raised when lifecycle operation fails"""
    pass


# =============================================================================
# Orchestrator Lifecycle Manager
# =============================================================================

class OrchestratorLifecycle:
    """Manages orchestrator lifecycle"""
    
    # Valid state transitions
    VALID_TRANSITIONS: Dict[LifecycleState, Set[LifecycleState]] = {
        LifecycleState.INITIALIZED: {
            LifecycleState.READY,
            LifecycleState.ERROR,
            LifecycleState.STOPPED
        },
        LifecycleState.READY: {
            LifecycleState.RUNNING,
            LifecycleState.STOPPED,
            LifecycleState.ERROR
        },
        LifecycleState.RUNNING: {
            LifecycleState.PAUSED,
            LifecycleState.STOPPED,
            LifecycleState.ERROR
        },
        LifecycleState.PAUSED: {
            LifecycleState.RUNNING,
            LifecycleState.STOPPED,
            LifecycleState.ERROR
        },
        LifecycleState.STOPPED: {
            LifecycleState.INITIALIZED,
            LifecycleState.ERROR
        },
        LifecycleState.ERROR: {
            LifecycleState.INITIALIZED,
            LifecycleState.STOPPED
        }
    }
    
    def __init__(self, orchestrator_id: str):
        """
        Initialize lifecycle manager
        
        Args:
            orchestrator_id: Unique identifier for orchestrator
        """
        self.orchestrator_id = orchestrator_id
        self.logger = get_audit_logger()
        
        # State management
        self.current_state = LifecycleState.INITIALIZED
        self.previous_state: Optional[LifecycleState] = None
        self.last_error: Optional[str] = None
        
        # Timestamps
        self.created_at = datetime.now()
        self.state_entry_times: Dict[LifecycleState, datetime] = {
            LifecycleState.INITIALIZED: self.created_at
        }
        
        # History
        self.transition_history: List[LifecycleTransition] = []
        
        # Callbacks
        self.state_change_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Health checks
        self.health_checks: Dict[str, Callable] = {}
        
        # Audit tracking
        self.last_audit_entry: Optional[str] = None
    
    def transition_to(
        self,
        new_state: LifecycleState,
        error: Optional[str] = None
    ) -> None:
        """
        Transition to a new state
        
        Args:
            new_state: Target state
            error: Optional error message (for ERROR state)
            
        Raises:
            LifecycleError: If transition is invalid
        """
        # Validate transition
        if not self.can_transition_to(new_state):
            raise LifecycleError(
                f"Invalid transition from {self.current_state.value} "
                f"to {new_state.value}"
            )
        
        # Record transition
        old_state = self.current_state
        transition = LifecycleTransition(
            from_state=old_state,
            to_state=new_state,
            timestamp=datetime.now(),
            error=error
        )
        self.transition_history.append(transition)
        
        # Update state
        self.previous_state = self.current_state
        self.current_state = new_state
        self.state_entry_times[new_state] = transition.timestamp
        
        # Store error if provided
        if error:
            self.last_error = error
        
        # Log transition
        self._log_transition(old_state, new_state, error)
        
        # Invoke callbacks
        self._invoke_state_change_callbacks(old_state, new_state)
        
        # Invoke error callbacks if transitioning to ERROR
        if new_state == LifecycleState.ERROR and error:
            self._invoke_error_callbacks(error)
    
    def resume(self) -> None:
        """Resume from PAUSED state"""
        if self.current_state != LifecycleState.PAUSED:
            raise LifecycleError(
                f"Cannot resume from {self.current_state.value} state"
            )
        self.transition_to(LifecycleState.RUNNING)
    
    def can_transition_to(self, new_state: LifecycleState) -> bool:
        """
        Check if transition to new state is valid
        
        Args:
            new_state: Target state
            
        Returns:
            True if transition is valid
        """
        valid_next_states = self.VALID_TRANSITIONS.get(self.current_state, set())
        return new_state in valid_next_states
    
    def get_valid_transitions(
        self,
        from_state: Optional[LifecycleState] = None
    ) -> Set[LifecycleState]:
        """
        Get valid transitions from a state
        
        Args:
            from_state: Source state (defaults to current state)
            
        Returns:
            Set of valid target states
        """
        state = from_state or self.current_state
        return self.VALID_TRANSITIONS.get(state, set())
    
    def get_next_allowed_states(self) -> Set[LifecycleState]:
        """Get allowed next states from current state"""
        return self.get_valid_transitions()
    
    # -------------------------------------------------------------------------
    # Callbacks
    # -------------------------------------------------------------------------
    
    def on_state_change(self, callback: Callable) -> None:
        """
        Register state change callback
        
        Args:
            callback: Function(old_state, new_state)
        """
        self.state_change_callbacks.append(callback)
    
    def on_error(self, callback: Callable) -> None:
        """
        Register error callback
        
        Args:
            callback: Function(error_message)
        """
        self.error_callbacks.append(callback)
    
    def _invoke_state_change_callbacks(
        self,
        old_state: LifecycleState,
        new_state: LifecycleState
    ) -> None:
        """Invoke all state change callbacks"""
        for callback in self.state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                self.logger.error(
                    category=AuditCategory.EXECUTION,
                    component='orchestrator_lifecycle',
                    operation='invoke_callback',
                    message=f'State change callback failed: {e}',
                    context={
                        'orchestrator_id': self.orchestrator_id,
                        'old_state': old_state.value,
                        'new_state': new_state.value
                    }
                )
    
    def _invoke_error_callbacks(self, error: str) -> None:
        """Invoke all error callbacks"""
        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                self.logger.error(
                    category=AuditCategory.EXECUTION,
                    component='orchestrator_lifecycle',
                    operation='invoke_error_callback',
                    message=f'Error callback failed: {e}',
                    context={
                        'orchestrator_id': self.orchestrator_id,
                        'original_error': error
                    }
                )
    
    # -------------------------------------------------------------------------
    # Health Checks
    # -------------------------------------------------------------------------
    
    def register_health_check(
        self,
        name: str,
        check: Callable[[], HealthStatus]
    ) -> None:
        """
        Register a health check
        
        Args:
            name: Health check name
            check: Function returning HealthStatus
        """
        self.health_checks[name] = check
    
    def get_health(self) -> HealthCheck:
        """
        Get current health status
        
        Returns:
            HealthCheck with overall and individual check statuses
        """
        results = {}
        
        for name, check in self.health_checks.items():
            try:
                status = check()
                results[name] = status
            except Exception as e:
                self.logger.warning(
                    category=AuditCategory.VALIDATION,
                    component='orchestrator_lifecycle',
                    operation='health_check',
                    message=f'Health check {name} failed: {e}',
                    context={'orchestrator_id': self.orchestrator_id}
                )
                results[name] = HealthStatus.UNHEALTHY
        
        # Determine overall status
        if not results:
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in results.values()):
            overall = HealthStatus.UNHEALTHY
        elif any(s == HealthStatus.DEGRADED for s in results.values()):
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.HEALTHY
        
        return HealthCheck(
            overall_status=overall,
            checks=results,
            timestamp=datetime.now()
        )
    
    # -------------------------------------------------------------------------
    # Timestamps & Duration
    # -------------------------------------------------------------------------
    
    def get_state_entry_time(self, state: LifecycleState) -> Optional[datetime]:
        """Get timestamp when state was entered"""
        return self.state_entry_times.get(state)
    
    def get_time_in_current_state(self) -> float:
        """Get seconds in current state"""
        entry_time = self.state_entry_times.get(self.current_state)
        if not entry_time:
            return 0.0
        return (datetime.now() - entry_time).total_seconds()
    
    def get_uptime(self) -> float:
        """Get total uptime in seconds"""
        return (datetime.now() - self.created_at).total_seconds()
    
    # -------------------------------------------------------------------------
    # History
    # -------------------------------------------------------------------------
    
    def get_history(self) -> List[LifecycleTransition]:
        """Get transition history"""
        return self.transition_history.copy()
    
    # -------------------------------------------------------------------------
    # Audit Logging
    # -------------------------------------------------------------------------
    
    def _log_transition(
        self,
        old_state: LifecycleState,
        new_state: LifecycleState,
        error: Optional[str] = None
    ) -> None:
        """Log state transition to audit log"""
        level = AuditLevel.ERROR if new_state == LifecycleState.ERROR else AuditLevel.INFO
        
        message = f"{old_state.value} → {new_state.value}"
        if error:
            message += f": {error}"
        
        self.logger.log(
            level=level,
            category=AuditCategory.EXECUTION,
            component='orchestrator_lifecycle',
            operation='state_transition',
            message=message,
            context={
                'orchestrator_id': self.orchestrator_id,
                'from_state': old_state.value,
                'to_state': new_state.value,
                'error': error
            },
            correlation_id=f"LIFECYCLE-{self.orchestrator_id}"
        )
        
        self.last_audit_entry = message
