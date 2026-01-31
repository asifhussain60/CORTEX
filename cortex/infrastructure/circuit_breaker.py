"""
Circuit Breaker Pattern for CORTEX

Implements the circuit breaker pattern to prevent cascading failures
by failing fast when a component is experiencing issues.

AC-NFR-002-03: Circuit breaker pattern implemented (legacy)
AC-INFRA-001-03: Adaptive circuit breaker with failure rate threshold
"""

import logging
import threading
import time
from typing import Any, Callable, Optional, TypeVar, Dict, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

T = TypeVar("T")


# Local enum for this module (different values than canonical CircuitBreakerState)
class CircuitState(str, Enum):
    """States for the circuit breaker."""
    CLOSED = "CLOSED"           # Normal operation
    OPEN = "OPEN"               # Fail fast
    HALF_OPEN = "HALF_OPEN"     # Testing if recovered


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejects calls."""
    pass


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker.
    
    Supports both legacy (count-based) and new (rate-based) thresholds.
    """
    # Legacy parameters (AC-NFR-002-03)
    failure_threshold: Union[int, float] = 5    # Failures before opening (int) or failure rate (float 0-1)
    success_threshold: int = 2                  # Successes in half-open before closing (legacy)
    timeout_seconds: float = 60.0               # Time before trying again
    monitored_exceptions: tuple = (Exception,)
    
    # New parameters (AC-INFRA-001-03)
    min_requests: int = 10                      # Minimum requests before rate calculation
    open_duration_seconds: float = 30.0         # Initial open duration
    half_open_max_attempts: int = 3             # Successful attempts to close
    max_open_duration_seconds: float = 300.0    # Maximum open duration (5 min)
    
    def __post_init__(self) -> None:
        """Validate configuration parameters."""
        # Convert legacy to new format if needed
        if isinstance(self.failure_threshold, int) and self.failure_threshold >= 1:
            # Legacy count-based threshold - keep as is
            pass
        elif isinstance(self.failure_threshold, float):
            if not 0 < self.failure_threshold <= 1.0:
                raise ValueError("failure_threshold must be between 0 and 1")
        else:
            raise ValueError("failure_threshold must be int >= 1 or float 0-1")
        
        if self.min_requests <= 0:
            raise ValueError("min_requests must be positive")
        if self.open_duration_seconds <= 0:
            raise ValueError("open_duration_seconds must be positive")
    
    def validate(self):
        """Legacy validation method."""
        self.__post_init__()


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    current_state: CircuitState = CircuitState.CLOSED
    state_change_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_failure_time: Optional[datetime] = None
    last_failure_reason: Optional[str] = None
    consecutive_successes: int = 0
    consecutive_failures: int = 0


@dataclass
class CircuitBreakerResult:
    """Result of a circuit breaker operation."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    circuit_state: CircuitState = CircuitState.CLOSED
    call_rejected: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CircuitBreaker:
    """
    Implements the circuit breaker pattern to prevent cascading failures.
    
    Supports both legacy (count-based) and adaptive (rate-based) thresholds.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing fast, requests rejected immediately
    - HALF_OPEN: Testing if service recovered
    
    Example:
        >>> cb = CircuitBreaker(name="api_call")
        >>> def risky_operation():
        ...     return call_external_api()
        >>> try:
        ...     result = cb.call(risky_operation)
        ... except CircuitBreakerOpenError:
        ...     result = fallback_value()
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            name: Unique name for this circuit breaker
            config: Configuration (uses defaults if None)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.config.validate()
        self.metrics = CircuitBreakerMetrics()
        
        # New adaptive tracking (AC-INFRA-001-03)
        self._lock = threading.RLock()
        self._state = CircuitState.CLOSED
        self._request_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._rejected_count = 0
        self._opened_at: Optional[float] = None
        self._current_open_duration = self.config.open_duration_seconds
        self._half_open_attempts = 0
        self._consecutive_successes = 0
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._lock:
            return self._state
    
    def call(
        self,
        fn: Callable[..., T],
        *args,
        **kwargs
    ) -> Union[T, 'CircuitBreakerResult']:
        """
        Execute function through circuit breaker.
        
        Supports both old (returns CircuitBreakerResult) and new (returns T or raises) API.
        
        Args:
            fn: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result from fn (new API) or CircuitBreakerResult (legacy API)
            
        Raises:
            CircuitBreakerOpenError: If circuit is open (new API)
        """
        # Detect if using new API (callable takes no args) vs legacy API
        use_new_api = not args and not kwargs
        
        if use_new_api:
            return self._call_new_api(fn)
        else:
            return self._call_legacy_api(fn, *args, **kwargs)
    
    def _call_new_api(self, func: Callable[[], T]) -> T:
        """New API: Execute function, raise on open circuit."""
        # Check if we should transition from OPEN to HALF_OPEN
        should_execute = False
        with self._lock:
            self._request_count += 1
            
            if self._state == CircuitState.OPEN:
                # Check if enough time has passed
                if self._opened_at is not None:
                    elapsed = time.time() - self._opened_at
                    if elapsed >= self._current_open_duration:
                        self._state = CircuitState.HALF_OPEN
                        self._half_open_attempts = 0
                        self._consecutive_successes = 0
                        should_execute = True
                    else:
                        self._rejected_count += 1
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker '{self.name}' is OPEN"
                        )
                else:
                    self._rejected_count += 1
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN"
                    )
            else:
                # CLOSED or HALF_OPEN state, execute normally
                should_execute = True
        
        # Execute the call if allowed
        if not should_execute:
            raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func()
            self._on_success_new()
            return result
        except Exception as e:
            self._on_failure_new()
            raise
    
    def _call_legacy_api(
        self,
        fn: Callable[..., T],
        *args,
        **kwargs
    ) -> CircuitBreakerResult:
        """Legacy API: Execute function, return CircuitBreakerResult."""
        self.metrics.total_calls += 1
        
        # Check if circuit should be opened due to timeout
        if self._should_attempt_reset():
            self._transition_to_half_open()
        
        # Reject calls if circuit is open
        if self.metrics.current_state == CircuitState.OPEN:
            self.metrics.rejected_calls += 1
            return CircuitBreakerResult(
                success=False,
                error=f"Circuit breaker is OPEN for {self.name}",
                circuit_state=CircuitState.OPEN,
                call_rejected=True
            )
        
        # Execute the function
        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return CircuitBreakerResult(
                success=True,
                data=result,
                circuit_state=self.metrics.current_state
            )
        except self.config.monitored_exceptions as e:
            self._on_failure(str(e))
            return CircuitBreakerResult(
                success=False,
                error=str(e),
                circuit_state=self.metrics.current_state
            )
    
    def _on_success_new(self) -> None:
        """Handle successful call (new API)."""
        with self._lock:
            self._success_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                self._consecutive_successes += 1
                self._half_open_attempts += 1
                
                # Close if enough successful tests
                if self._consecutive_successes >= self.config.half_open_max_attempts:
                    self._state = CircuitState.CLOSED
                    self._reset_counts()
                    # Reset open duration on successful recovery
                    self._current_open_duration = self.config.open_duration_seconds
    
    def _on_failure_new(self) -> None:
        """Handle failed call (new API)."""
        with self._lock:
            self._failure_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open reopens the circuit with exponential backoff
                self._trip_breaker(is_reopen=True)
            elif self._state == CircuitState.CLOSED:
                # Check if failure threshold exceeded
                if isinstance(self.config.failure_threshold, float):
                    # Rate-based threshold
                    if self._request_count >= self.config.min_requests:
                        failure_rate = self._failure_count / self._request_count
                        if failure_rate >= self.config.failure_threshold:
                            self._trip_breaker(is_reopen=False)
                else:
                    # Count-based threshold (legacy)
                    if self._failure_count >= self.config.failure_threshold:
                        self._trip_breaker(is_reopen=False)
    
    def _trip_breaker(self, is_reopen: bool = False) -> None:
        """
        Trip the circuit breaker to OPEN state.
        
        Args:
            is_reopen: True if reopening from HALF_OPEN (apply exponential backoff)
        """
        self._state = CircuitState.OPEN
        self._opened_at = time.time()
        if is_reopen:
            # Apply exponential backoff on reopens
            self._increase_open_duration()
    
    def _increase_open_duration(self) -> None:
        """Increase open duration with exponential backoff."""
        # Double the duration, capped at maximum
        self._current_open_duration = min(
            self._current_open_duration * 2,
            self.config.max_open_duration_seconds
        )
    
    def _reset_counts(self) -> None:
        """Reset request counters."""
        self._request_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._consecutive_successes = 0
    
    def _on_success(self):
        """Handle successful call (legacy API)."""
        self.metrics.successful_calls += 1
        self.metrics.consecutive_failures = 0
        self.metrics.consecutive_successes += 1
        
        # Transition from half-open to closed after threshold successes
        if self.metrics.current_state == CircuitState.HALF_OPEN:
            if self.metrics.consecutive_successes >= self.config.success_threshold:
                self._transition_to_closed()
                logger.info(f"Circuit breaker '{self.name}' transitioning to CLOSED")
    
    def _on_failure(self, reason: str):
        """Handle failed call (legacy API)."""
        self.metrics.failed_calls += 1
        self.metrics.consecutive_failures += 1
        self.metrics.consecutive_successes = 0
        self.metrics.last_failure_time = datetime.now(timezone.utc)
        self.metrics.last_failure_reason = reason
        
        # Transition to open if threshold exceeded
        if isinstance(self.config.failure_threshold, int):
            threshold = self.config.failure_threshold
        else:
            threshold = 5  # Default for legacy
        
        if self.metrics.consecutive_failures >= threshold:
            self._transition_to_open()
            logger.warning(
                f"Circuit breaker '{self.name}' transitioning to OPEN "
                f"(failures: {self.metrics.consecutive_failures})"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        # New API check
        if hasattr(self, '_state') and self._state == CircuitState.OPEN and self._opened_at is not None:
            elapsed = time.time() - self._opened_at
            if elapsed >= self._current_open_duration:
                return True
        
        # Legacy API check
        if hasattr(self, 'metrics') and self.metrics.current_state == CircuitState.OPEN:
            timeout = timedelta(seconds=self.config.timeout_seconds)
            if datetime.now(timezone.utc) - self.metrics.state_change_timestamp > timeout:
                return True
        
        return False
    
    def _transition_to_closed(self):
        """Transition circuit to closed state."""
        self.metrics.current_state = CircuitState.CLOSED
        self.metrics.state_change_timestamp = datetime.now(timezone.utc)
        self.metrics.consecutive_successes = 0
        self.metrics.consecutive_failures = 0
        
        # Sync new API state
        self._state = CircuitState.CLOSED
    
    def _transition_to_open(self):
        """Transition circuit to open state."""
        self.metrics.current_state = CircuitState.OPEN
        self.metrics.state_change_timestamp = datetime.now(timezone.utc)
        
        # Sync new API state
        self._state = CircuitState.OPEN
        if self._opened_at is None:
            self._opened_at = time.time()
    
    def _transition_to_half_open(self):
        """Transition circuit to half-open state."""
        self.metrics.current_state = CircuitState.HALF_OPEN
        self.metrics.state_change_timestamp = datetime.now(timezone.utc)
        self.metrics.consecutive_successes = 0
        self.metrics.consecutive_failures = 0
        logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
        
        # Sync new API state
        self._state = CircuitState.HALF_OPEN
    
    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state if hasattr(self, '_state') else self.metrics.current_state
    
    def get_metrics(self) -> Union[Dict[str, Any], 'CircuitBreakerMetrics']:
        """
        Get circuit breaker metrics.
        
        Returns:
            Dictionary (new API) or CircuitBreakerMetrics (legacy API)
        """
        # Return new format with additional metrics
        with self._lock if hasattr(self, '_lock') else threading.RLock():
            failure_rate = 0.0
            if self._request_count > 0:
                failure_rate = self._failure_count / self._request_count
            
            return {
                "name": self.name,
                "state": self._state.value,
                "request_count": self._request_count,
                "success_count": self._success_count,
                "failure_count": self._failure_count,
                "rejected_count": self._rejected_count,
                "failure_rate": failure_rate,
                "half_open_attempts": self._half_open_attempts,
                "current_open_duration": self._current_open_duration,
                # Legacy metrics
                "total_calls": self.metrics.total_calls,
                "successful_calls": self.metrics.successful_calls,
                "failed_calls": self.metrics.failed_calls,
                "rejected_calls": self.metrics.rejected_calls,
            }
    
    def reset(self):
        """
        Reset circuit breaker to initial state.
        
        Clears all metrics and returns to CLOSED state.
        """
        with self._lock if hasattr(self, '_lock') else threading.RLock():
            # Reset new API state
            self._state = CircuitState.CLOSED
            self._request_count = 0
            self._success_count = 0
            self._failure_count = 0
            self._rejected_count = 0
            self._opened_at = None
            self._current_open_duration = self.config.open_duration_seconds
            self._half_open_attempts = 0
            self._consecutive_successes = 0
            
            # Reset legacy state
            self.metrics = CircuitBreakerMetrics()
            logger.info(f"Circuit breaker '{self.name}' manually reset")
    
    def force_state(self, state: CircuitState):
        """Force circuit to a specific state (for testing)."""
        with self._lock if hasattr(self, '_lock') else threading.RLock():
            self._state = state
            self.metrics.current_state = state
            self.metrics.state_change_timestamp = datetime.now(timezone.utc)
            logger.warning(f"Circuit breaker '{self.name}' forced to {state.value}")
