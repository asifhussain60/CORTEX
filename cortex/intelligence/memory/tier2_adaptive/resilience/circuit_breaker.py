"""
Circuit breaker pattern — CircuitBreaker, CircuitBreakerConfig, CircuitBreakerMetrics.

Phase 103-f: extracted from resilience.py (1,876L) god-object.
"""
from __future__ import annotations

import logging
from datetime import datetime
from threading import RLock
from typing import Any, Callable, Optional

from cortex.models.canonical_enums import CircuitBreakerState

logger = logging.getLogger(__name__)


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is OPEN."""

    def __init__(self, component_name: str = "unknown") -> None:
        """Initialize exception."""
        self.component_name = component_name
        super().__init__(f"Circuit breaker is OPEN for {component_name}")


class CircuitBreakerMetrics:
    """Metrics for circuit breaker."""

    def __init__(self) -> None:
        """Initialize metrics."""
        self.successful_calls: int = 0
        self.failed_calls: int = 0
        self.rejected_calls: int = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_error_message: str = ""

    def reset(self) -> None:
        """Reset all metrics."""
        self.successful_calls = 0
        self.failed_calls = 0
        self.rejected_calls = 0
        self.last_failure_time = None
        self.last_error_message = ""


class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: float = 60,
        name: str = "circuit_breaker",
    ) -> None:
        """Initialize circuit breaker configuration."""
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.name = name


class CircuitBreaker:  # CORE-035-scoped — domain-specific circuit breaker — independent implementations
    """
    Circuit Breaker pattern implementation.

    States: CLOSED (normal), OPEN (fail-fast), HALF_OPEN (testing recovery).
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None) -> None:
        """Initialize circuit breaker."""
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self._lock = RLock()
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._last_exception: Optional[Exception] = None
        logger.debug(f"CircuitBreaker '{self.config.name}' initialized in CLOSED state")

    def call(
        self,
        operation: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute operation through circuit breaker."""
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self._success_count = 0
                    self._failure_count = 0
                    logger.info(
                        f"CircuitBreaker '{self.config.name}' OPEN -> HALF_OPEN"
                    )
                else:
                    self.metrics.rejected_calls += 1
                    raise CircuitBreakerOpen(self.config.name)
        try:
            result = operation(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure(exc)
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if timeout has elapsed to allow HALF_OPEN attempt."""
        if not self._last_failure_time:
            return False
        elapsed = (datetime.utcnow() - self._last_failure_time).total_seconds()
        return elapsed >= self.config.timeout_seconds

    def _on_success(self) -> None:
        """Handle successful operation."""
        with self._lock:
            self.metrics.successful_calls += 1
            if self.state == CircuitBreakerState.CLOSED:
                self._failure_count = 0
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self.metrics.reset()
                    logger.info(
                        f"CircuitBreaker '{self.config.name}' HALF_OPEN -> CLOSED"
                    )

    def _on_failure(self, exc: Exception) -> None:
        """Handle failed operation."""
        with self._lock:
            self.metrics.failed_calls += 1
            self.metrics.last_error_message = str(exc)
            self.metrics.last_failure_time = datetime.utcnow()
            self._last_failure_time = datetime.utcnow()
            self._last_exception = exc
            if self.state == CircuitBreakerState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.config.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    logger.error(
                        f"CircuitBreaker '{self.config.name}' CLOSED -> OPEN"
                    )
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                self._failure_count = 0
                self._success_count = 0
                logger.error(
                    f"CircuitBreaker '{self.config.name}' HALF_OPEN -> OPEN"
                )

    def is_open(self) -> bool:
        """Check if circuit is OPEN."""
        with self._lock:
            return self.state == CircuitBreakerState.OPEN

    def is_closed(self) -> bool:
        """Check if circuit is CLOSED."""
        with self._lock:
            return self.state == CircuitBreakerState.CLOSED

    def is_half_open(self) -> bool:
        """Check if circuit is HALF_OPEN."""
        with self._lock:
            return self.state == CircuitBreakerState.HALF_OPEN

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics."""
        with self._lock:
            m = CircuitBreakerMetrics()
            m.successful_calls = self.metrics.successful_calls
            m.failed_calls = self.metrics.failed_calls
            m.rejected_calls = self.metrics.rejected_calls
            m.last_failure_time = self.metrics.last_failure_time
            m.last_error_message = self.metrics.last_error_message
            return m

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.metrics.reset()
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = None
            self._last_exception = None
            logger.info(f"CircuitBreaker '{self.config.name}' reset to CLOSED")
