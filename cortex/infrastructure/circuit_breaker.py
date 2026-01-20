"""
Circuit Breaker Pattern for CORTEX

Implements the circuit breaker pattern to prevent cascading failures
by failing fast when a component is experiencing issues.

AC-NFR-002-03: Circuit breaker pattern implemented
"""

import logging
import time
from typing import Any, Callable, Optional, TypeVar
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """States for the circuit breaker."""
    CLOSED = "CLOSED"           # Normal operation
    OPEN = "OPEN"               # Fail fast
    HALF_OPEN = "HALF_OPEN"     # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5          # Failures before opening
    success_threshold: int = 2          # Successes in half-open before closing
    timeout_seconds: float = 60.0       # Time before trying again
    monitored_exceptions: tuple = (Exception,)
    
    def validate(self):
        """Validate circuit breaker configuration."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")


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
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing fast, requests rejected immediately
    - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.config.validate()
        self.metrics = CircuitBreakerMetrics()
    
    def call(
        self,
        fn: Callable[..., T],
        *args,
        **kwargs
    ) -> CircuitBreakerResult:
        """
        Execute function through circuit breaker.
        
        Args:
            fn: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            CircuitBreakerResult with result or circuit state info
        """
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
    
    def _on_success(self):
        """Handle successful call."""
        self.metrics.successful_calls += 1
        self.metrics.consecutive_failures = 0
        self.metrics.consecutive_successes += 1
        
        # Transition from half-open to closed after threshold successes
        if self.metrics.current_state == CircuitState.HALF_OPEN:
            if self.metrics.consecutive_successes >= self.config.success_threshold:
                self._transition_to_closed()
                logger.info(f"Circuit breaker '{self.name}' transitioning to CLOSED")
    
    def _on_failure(self, reason: str):
        """Handle failed call."""
        self.metrics.failed_calls += 1
        self.metrics.consecutive_failures += 1
        self.metrics.consecutive_successes = 0
        self.metrics.last_failure_time = datetime.now(timezone.utc)
        self.metrics.last_failure_reason = reason
        
        # Transition to open if threshold exceeded
        if self.metrics.consecutive_failures >= self.config.failure_threshold:
            self._transition_to_open()
            logger.warning(
                f"Circuit breaker '{self.name}' transitioning to OPEN "
                f"(failures: {self.metrics.consecutive_failures})"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.metrics.current_state != CircuitState.OPEN:
            return False
        
        timeout = timedelta(seconds=self.config.timeout_seconds)
        return datetime.now(timezone.utc) - self.metrics.state_change_timestamp > timeout
    
    def _transition_to_closed(self):
        """Transition circuit to closed state."""
        self.metrics.current_state = CircuitState.CLOSED
        self.metrics.state_change_timestamp = datetime.now(timezone.utc)
        self.metrics.consecutive_successes = 0
        self.metrics.consecutive_failures = 0
    
    def _transition_to_open(self):
        """Transition circuit to open state."""
        self.metrics.current_state = CircuitState.OPEN
        self.metrics.state_change_timestamp = datetime.now(timezone.utc)
    
    def _transition_to_half_open(self):
        """Transition circuit to half-open state."""
        self.metrics.current_state = CircuitState.HALF_OPEN
        self.metrics.state_change_timestamp = datetime.now(timezone.utc)
        self.metrics.consecutive_successes = 0
        self.metrics.consecutive_failures = 0
        logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
    
    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.metrics.current_state
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get circuit breaker metrics."""
        return self.metrics
    
    def reset(self):
        """Manually reset circuit breaker."""
        self.metrics = CircuitBreakerMetrics()
        logger.info(f"Circuit breaker '{self.name}' manually reset")
    
    def force_state(self, state: CircuitState):
        """Force circuit to a specific state (for testing)."""
        self.metrics.current_state = state
        self.metrics.state_change_timestamp = datetime.now(timezone.utc)
        logger.warning(f"Circuit breaker '{self.name}' forced to {state.value}")
