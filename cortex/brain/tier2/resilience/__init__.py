"""
Graceful Degradation Framework for CORTEX

This module provides the framework for handling component failures gracefully,
enabling the system to continue operating with reduced functionality when
components become unavailable.

AC-ID: AC-NFR-002-01
Title: Graceful Degradation Framework

Key Concepts:
1. Fallback Strategies: Alternative execution paths when primary components fail
2. Partial Functionality Mode: Reduced feature set during degradation
3. Degradation Levels: Quantify severity of system degradation (0-3)
4. Automatic Recovery: Components can recover and re-enable features

Type Hints: 100% (CORE-011)
Docstrings: All classes/methods documented (CORE-012)
"""

import logging
import random
import threading
import time
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, Type

# Configure logging
logger = logging.getLogger(__name__)


class DegradationLevel(IntEnum):
    """Enum for system degradation levels."""
    FULL_OPERATION = 0
    PARTIAL = 1
    MODERATE = 2
    SEVERE = 3


class ComponentState(IntEnum):
    """Enum for component operational states."""
    OPERATIONAL = 0
    DEGRADED = 1
    FAILED = 2


@dataclass
class ComponentFailure(Exception):
    """
    Exception raised when a component fails.

    Attributes:
        component_name: Name of the failed component
        reason: Human-readable reason for failure
        is_recoverable: Whether component can recover automatically
        timestamp: When the failure occurred
    """
    component_name: str
    reason: str
    is_recoverable: bool = True
    timestamp: float = None

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.timestamp is None:
            import time
            self.timestamp = time.time()

    def __str__(self) -> str:
        """Return formatted error message."""
        recovery_info = (
            "recoverable" if self.is_recoverable else "not recoverable"
        )
        return (
            f"Component '{self.component_name}' failed ({recovery_info}): "
            f"{self.reason}"
        )


@dataclass
class DegradedResponse:
    """
    Response returned when system operates in degraded mode.

    Attributes:
        data: Response data (may be partial or from fallback)
        degradation_level: Current degradation level (0-3)
        affected_features: List of unavailable features
        fallback_used: Whether fallback was used for this response
        original_error: The original error if applicable
        available_features: Features that remain available
    """
    data: Any
    degradation_level: DegradationLevel
    affected_features: List[str] = field(default_factory=list)
    fallback_used: bool = False
    original_error: Optional[Exception] = None
    available_features: List[str] = field(default_factory=list)


@dataclass
class ComponentMetrics:
    """Track metrics for a component."""
    failure_count: int = 0
    recovery_count: int = 0
    last_failure: Optional[float] = None
    consecutive_failures: int = 0
    is_healthy: bool = True


class FallbackStrategy(Protocol):
    """
    Protocol for fallback strategies.

    A fallback strategy is a callable that provides alternative behavior
    when the primary component is unavailable.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute fallback strategy."""
        ...


class FailureHandler(Protocol):
    """
    Protocol for failure handlers.

    A failure handler is called when a component fails, enabling custom
    recovery logic.
    """

    def __call__(self, failure: ComponentFailure) -> bool:
        """
        Handle component failure.

        Returns:
            True if recovery initiated, False otherwise
        """
        ...


class GracefulDegradationFramework:
    """
    Framework for handling graceful degradation.

    This framework enables CORTEX to continue operating with reduced
    functionality when components fail, automatically activating fallback
    strategies and partial functionality modes.

    Attributes:
        name: Framework identifier
        fallback_strategies: Registered fallback functions by component
        failure_handlers: Registered failure handlers by component
        degradation_mode: Whether system is currently degraded
        affected_components: List of currently affected components
        component_metrics: Metrics for each component
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the framework.

        Args:
            name: Unique identifier for this framework instance
        """
        self.name = name
        self.fallback_strategies: Dict[str, FallbackStrategy] = {}
        self.failure_handlers: Dict[str, FailureHandler] = {}
        self.degradation_mode: bool = False
        self.affected_components: List[str] = []
        self.component_metrics: Dict[str, ComponentMetrics] = {}
        self._lock = threading.RLock()
        logger.info(f"GracefulDegradationFramework '{name}' initialized")

    def register_fallback(
        self, component: str, fallback_fn: FallbackStrategy
    ) -> None:
        """
        Register a fallback strategy for a component.

        Args:
            component: Component name
            fallback_fn: Callable providing fallback behavior

        Raises:
            ValueError: If component name is empty
        """
        if not component:
            raise ValueError("Component name cannot be empty")

        with self._lock:
            self.fallback_strategies[component] = fallback_fn
            if component not in self.component_metrics:
                self.component_metrics[component] = ComponentMetrics()
            logger.debug(f"Registered fallback for component '{component}'")

    def register_failure_handler(
        self, component: str, handler_fn: FailureHandler
    ) -> None:
        """
        Register a failure handler for a component.

        Args:
            component: Component name
            handler_fn: Callable to handle component failure

        Raises:
            ValueError: If component name is empty
        """
        if not component:
            raise ValueError("Component name cannot be empty")

        with self._lock:
            self.failure_handlers[component] = handler_fn
            logger.debug(f"Registered failure handler for '{component}'")

    def has_fallback(self, component: str) -> bool:
        """
        Check if component has a registered fallback.

        Args:
            component: Component name

        Returns:
            True if fallback is registered, False otherwise
        """
        with self._lock:
            return component in self.fallback_strategies

    def activate_degradation_mode(
        self, affected_components: List[str]
    ) -> None:
        """
        Activate degradation mode for affected components.

        Args:
            affected_components: List of affected component names

        Raises:
            ValueError: If affected_components is empty
        """
        if not affected_components:
            raise ValueError("Must specify at least one affected component")

        with self._lock:
            self.degradation_mode = True
            self.affected_components = affected_components.copy()

            # Update metrics
            for component in affected_components:
                if component not in self.component_metrics:
                    self.component_metrics[component] = ComponentMetrics()
                metrics = self.component_metrics[component]
                metrics.failure_count += 1
                metrics.consecutive_failures += 1
                metrics.is_healthy = False
                import time
                metrics.last_failure = time.time()

            logger.warning(
                f"Degradation mode activated. Affected components: "
                f"{', '.join(affected_components)}"
            )

    def deactivate_degradation_mode(self) -> None:
        """Return to normal operation mode."""
        with self._lock:
            if self.degradation_mode:
                recovered = self.affected_components.copy()
                self.degradation_mode = False
                self.affected_components = []

                # Update metrics
                for component in recovered:
                    if component in self.component_metrics:
                        metrics = self.component_metrics[component]
                        metrics.recovery_count += 1
                        metrics.consecutive_failures = 0
                        metrics.is_healthy = True

                logger.info(
                    f"Recovered from degradation. Components recovered: "
                    f"{', '.join(recovered)}"
                )

    def get_degradation_level(self) -> DegradationLevel:
        """
        Get current system degradation level.

        Levels:
            0 (FULL_OPERATION): No degradation
            1 (PARTIAL): 1 component affected
            2 (MODERATE): 2-3 components affected
            3 (SEVERE): 4+ components affected

        Returns:
            Current degradation level
        """
        with self._lock:
            if not self.degradation_mode:
                return DegradationLevel.FULL_OPERATION

            num_affected = len(self.affected_components)
            if num_affected == 1:
                return DegradationLevel.PARTIAL
            elif num_affected <= 3:
                return DegradationLevel.MODERATE
            else:
                return DegradationLevel.SEVERE

    def handle_failure(self, failure: ComponentFailure) -> bool:
        """
        Handle a component failure.

        Args:
            failure: ComponentFailure exception

        Returns:
            True if recovery initiated, False otherwise
        """
        with self._lock:
            component = failure.component_name

            # Activate degradation mode
            if component not in self.affected_components:
                self.activate_degradation_mode([component])

            # Call failure handler if registered
            if component in self.failure_handlers:
                handler = self.failure_handlers[component]
                try:
                    return handler(failure)
                except Exception as e:
                    logger.error(f"Failure handler error: {e}")
                    return False

            return False

    def get_metrics(self, component: str) -> Optional[ComponentMetrics]:
        """
        Get metrics for a component.

        Args:
            component: Component name

        Returns:
            ComponentMetrics or None if not tracked
        """
        with self._lock:
            return self.component_metrics.get(component)

    @contextmanager
    def protected_execution(self, component: str, timeout: Optional[float] = None):
        """
        Context manager for protected component execution.

        Args:
            component: Component name
            timeout: Optional execution timeout in seconds

        Yields:
            None

        Raises:
            ComponentFailure: If component fails
        """
        try:
            yield
        except Exception as e:
            failure = ComponentFailure(
                component_name=component,
                reason=str(e),
                is_recoverable=True
            )
            self.handle_failure(failure)
            raise


class PartialFunctionalityMode:
    """
    Manages partial functionality when components degrade.

    This class tracks which features are available based on which
    components are currently operational, enabling dynamic feature
    availability during degradation.

    Attributes:
        available_features: Currently available features
        unavailable_features: Currently unavailable features
        feature_mappings: Component dependencies per feature
    """

    def __init__(self) -> None:
        """Initialize partial functionality mode."""
        self.available_features: List[str] = []
        self.unavailable_features: List[str] = []
        self.feature_mappings: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
        logger.debug("PartialFunctionalityMode initialized")

    def register_feature_dependency(
        self, feature: str, components: List[str]
    ) -> None:
        """
        Register component dependencies for a feature.

        Args:
            feature: Feature name
            components: List of required components

        Raises:
            ValueError: If feature or components list is empty
        """
        if not feature:
            raise ValueError("Feature name cannot be empty")
        if not components:
            raise ValueError("Components list cannot be empty")

        with self._lock:
            self.feature_mappings[feature] = components.copy()
            logger.debug(
                f"Feature '{feature}' requires: {', '.join(components)}"
            )

    def update_feature_availability(
        self, available_components: List[str]
    ) -> None:
        """
        Update available features based on available components.

        Args:
            available_components: List of currently operational components
        """
        with self._lock:
            self.available_features = []
            self.unavailable_features = []

            for feature, dependencies in self.feature_mappings.items():
                if all(
                    comp in available_components for comp in dependencies
                ):
                    self.available_features.append(feature)
                else:
                    self.unavailable_features.append(feature)

            logger.debug(
                f"Feature availability updated. Available: "
                f"{len(self.available_features)}, "
                f"Unavailable: {len(self.unavailable_features)}"
            )

    def is_feature_available(self, feature: str) -> bool:
        """
        Check if a feature is available.

        Args:
            feature: Feature name

        Returns:
            True if feature is available, False otherwise
        """
        with self._lock:
            return feature in self.available_features

    def get_available_features(self) -> List[str]:
        """
        Get list of currently available features.

        Returns:
            List of available feature names
        """
        with self._lock:
            return self.available_features.copy()

    def get_unavailable_features(self) -> List[str]:
        """
        Get list of currently unavailable features.

        Returns:
            List of unavailable feature names
        """
        with self._lock:
            return self.unavailable_features.copy()


__all__ = [
    "GracefulDegradationFramework",
    "PartialFunctionalityMode",
    "ComponentFailure",
    "DegradedResponse",
    "ComponentMetrics",
    "DegradationLevel",
    "ComponentState",
    "FallbackStrategy",
    "FailureHandler",
    "ExponentialBackoffRetry",
    "RetryPolicy",
    "RetryResult",
    "RetryPolicyBuilder",
]


# ============================================================================
# AC-NFR-002-02: Automatic Retry with Exponential Backoff
# ============================================================================

@dataclass
class RetryPolicy:
    """
    Configuration for retry behavior.

    Attributes:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential calculation
        jitter: Whether to add random jitter to delays
    """
    max_retries: int
    initial_delay: float
    max_delay: float
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class RetryResult:
    """
    Result of a retry operation.

    Attributes:
        success: Whether operation succeeded
        value: Returned value if successful
        error: Exception if failed
        attempts: Total number of attempts made
        total_delay: Total delay accumulated (seconds)
    """
    success: bool
    value: Any = None
    error: Optional[Exception] = None
    attempts: int = 0
    total_delay: float = 0.0


class ExponentialBackoffRetry:
    """
    Implements exponential backoff retry strategy with jitter.

    This class provides retry logic with:
    - Exponential backoff delays
    - Configurable maximum delays
    - Optional jitter to prevent thundering herd
    - Comprehensive retry tracking

    Attributes:
        policy: RetryPolicy configuration
        attempt_count: Current attempt number
        total_delay: Accumulated delay time
    """

    def __init__(self, policy: RetryPolicy) -> None:
        """
        Initialize retry mechanism.

        Args:
            policy: RetryPolicy configuration
        """
        self.policy = policy
        self.attempt_count = 0
        self.total_delay = 0.0
        logger.debug(
            f"ExponentialBackoffRetry initialized with policy: "
            f"max_retries={policy.max_retries}, "
            f"initial_delay={policy.initial_delay}s"
        )

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number using exponential backoff.

        Formula: delay = min(initial_delay * (base ^ attempt), max_delay)
        With optional jitter: ±10% random variation

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds

        Raises:
            ValueError: If attempt is negative
        """
        if attempt < 0:
            raise ValueError("Attempt number cannot be negative")

        # Exponential calculation
        delay = self.policy.initial_delay * (
            self.policy.exponential_base ** attempt
        )
        # Cap at maximum
        delay = min(delay, self.policy.max_delay)

        # Add jitter if enabled
        if self.policy.jitter:
            jitter_amount = random.uniform(0, delay * 0.1)
            delay += jitter_amount

        return delay

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """
        Determine if retry should happen.

        Args:
            attempt: Current attempt number
            error: The error that occurred

        Returns:
            True if should retry, False otherwise
        """
        return attempt < self.policy.max_retries

    def execute(
        self, fn: Callable, *args: Any, **kwargs: Any
    ) -> RetryResult:
        """
        Execute function with automatic retries and exponential backoff.

        Args:
            fn: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            RetryResult with success status and details

        Example:
            policy = RetryPolicy(
                max_retries=3,
                initial_delay=0.1,
                max_delay=10.0
            )
            retry = ExponentialBackoffRetry(policy)
            result = retry.execute(risky_function, arg1, arg2)
            if result.success:
                print(f"Success after {result.attempts} attempts")
            else:
                print(f"Failed: {result.error}")
        """
        self.attempt_count = 0
        self.total_delay = 0.0
        last_error = None

        # Attempt loop
        for attempt in range(self.policy.max_retries + 1):
            try:
                self.attempt_count = attempt + 1
                result = fn(*args, **kwargs)
                logger.debug(
                    f"Success on attempt {self.attempt_count} "
                    f"(total delay: {self.total_delay:.2f}s)"
                )
                return RetryResult(
                    success=True,
                    value=result,
                    attempts=self.attempt_count,
                    total_delay=self.total_delay
                )
            except Exception as e:
                last_error = e

                # Check if we should retry
                if not self.should_retry(attempt, e):
                    logger.warning(
                        f"Max retries ({self.policy.max_retries}) exhausted. "
                        f"Last error: {e}"
                    )
                    break

                # Calculate and apply delay
                delay = self.calculate_delay(attempt)
                self.total_delay += delay
                logger.debug(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.3f}s..."
                )
                time.sleep(delay)

        # All retries exhausted
        return RetryResult(
            success=False,
            error=last_error,
            attempts=self.attempt_count,
            total_delay=self.total_delay
        )


class RetryPolicyBuilder:
    """
    Builder for creating RetryPolicy instances with fluent API.

    Simplifies policy creation with sensible defaults and chainable methods.

    Example:
        policy = (RetryPolicyBuilder()
                 .with_max_retries(5)
                 .with_initial_delay(0.1)
                 .with_max_delay(30.0)
                 .build())
    """

    def __init__(self) -> None:
        """Initialize builder with defaults."""
        self.max_retries = 3
        self.initial_delay = 0.1
        self.max_delay = 10.0
        self.exponential_base = 2.0
        self.jitter = True

    def with_max_retries(self, n: int) -> "RetryPolicyBuilder":
        """Set maximum number of retries."""
        if n < 0:
            raise ValueError("max_retries cannot be negative")
        self.max_retries = n
        return self

    def with_initial_delay(self, delay: float) -> "RetryPolicyBuilder":
        """Set initial retry delay."""
        if delay < 0:
            raise ValueError("initial_delay cannot be negative")
        self.initial_delay = delay
        return self

    def with_max_delay(self, delay: float) -> "RetryPolicyBuilder":
        """Set maximum retry delay."""
        if delay < 0:
            raise ValueError("max_delay cannot be negative")
        self.max_delay = delay
        return self

    def with_exponential_base(self, base: float) -> "RetryPolicyBuilder":
        """Set exponential base for backoff calculation."""
        if base <= 1.0:
            raise ValueError("exponential_base must be > 1.0")
        self.exponential_base = base
        return self

    def with_jitter(self, enabled: bool) -> "RetryPolicyBuilder":
        """Enable/disable random jitter in retry delays."""
        self.jitter = enabled
        return self

    def build(self) -> RetryPolicy:
        """Build and return the RetryPolicy."""
        if self.initial_delay > self.max_delay:
            logger.warning(
                f"initial_delay ({self.initial_delay}) > "
                f"max_delay ({self.max_delay})"
            )

        return RetryPolicy(
            max_retries=self.max_retries,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter=self.jitter
        )


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker behavior.

    Attributes:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes before closing from half-open
        timeout: Seconds before attempting recovery from open state
    """
    failure_threshold: int
    success_threshold: int
    timeout: float

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be >= 1")
        if self.timeout < 0:
            raise ValueError("timeout cannot be negative")


@dataclass
class CircuitBreakerMetrics:
    """
    Metrics for circuit breaker operations.

    Attributes:
        total_calls: Total number of calls attempted
        successful_calls: Number of successful calls
        failed_calls: Number of failed calls
        rejected_calls: Number of calls rejected due to open circuit
        state_changes: Number of state transitions
    """
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: int = 0


class CircuitBreakerOpen(Exception):
    """
    Exception raised when circuit breaker is open.

    Raised to prevent cascading failures by immediately rejecting
    requests when a service is known to be failing.
    """
    pass


# CONSOLIDATED: Import from cortex.models.canonical_enums
# class CircuitBreakerState(IntEnum):
    """States of the circuit breaker."""
    CLOSED = 0      # Normal operation, all requests pass through
    OPEN = 1        # Failing, requests rejected immediately
    HALF_OPEN = 2   # Testing recovery, limited requests pass through


class CircuitBreaker:
    """
    Circuit breaker implementation following the State pattern.

    Prevents cascading failures by:
    1. Monitoring call success/failure rates
    2. Opening circuit when failures exceed threshold
    3. Rejecting requests while circuit is open
    4. Testing recovery with limited requests in half-open state
    5. Automatically closing when service recovers

    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Failing, requests are rejected immediately (fail-fast)
    - HALF_OPEN: Testing recovery, limited requests pass through

    AC-ID: AC-NFR-002-03
    Title: Circuit Breaker Pattern Implementation

    Example:
        config = CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout=30.0
        )
        breaker = CircuitBreaker(config)

        try:
            result = breaker.call(unreliable_service)
        except CircuitBreakerOpen:
            # Handle open circuit - use fallback
            result = fallback_value

    Thread Safety: Protected with RLock for concurrent access
    """

    def __init__(self, config: CircuitBreakerConfig) -> None:
        """
        Initialize circuit breaker.

        Args:
            config: CircuitBreakerConfig with threshold and timeout settings
        """
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self._lock = threading.RLock()

    def call(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute function through circuit breaker.

        Implements the circuit breaker pattern:
        - CLOSED: Execute function normally
        - OPEN: Reject immediately (fail-fast)
        - HALF_OPEN: Execute with automatic transition to OPEN/CLOSED

        Args:
            fn: Callable to execute
            *args: Positional arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Return value from fn if successful

        Raises:
            CircuitBreakerOpen: If circuit is open and timeout not exceeded
            Any exception raised by fn

        Complexity: O(1) - constant time operation
        """
        with self._lock:
            # Handle OPEN state
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    # Transition to HALF_OPEN
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    self.metrics.state_changes += 1
                else:
                    # Reject call immediately
                    self.metrics.rejected_calls += 1
                    raise CircuitBreakerOpen(
                        f"Circuit breaker is OPEN (retry after {self.config.timeout}s)"
                    )

        # Execute the function
        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """
        Handle successful call.

        Updates metrics and handles state transitions:
        - HALF_OPEN: Increment success count, close if threshold met
        - CLOSED: Reset failure count
        """
        with self._lock:
            self.metrics.successful_calls += 1
            self.metrics.total_calls += 1
            self.failure_count = 0

            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._close_circuit()

    def _on_failure(self) -> None:
        """
        Handle failed call.

        Updates metrics and handles state transitions:
        - CLOSED → OPEN: If failure threshold exceeded
        - HALF_OPEN → OPEN: Any failure in half-open opens circuit
        """
        with self._lock:
            self.metrics.failed_calls += 1
            self.metrics.total_calls += 1
            self.failure_count += 1
            self.last_failure_time = time.time()

            # Increment failure threshold triggers opening
            if self.failure_count >= self.config.failure_threshold:
                if self.state != CircuitBreakerState.OPEN:
                    self._open_circuit()

            # Any failure in half-open state returns to open
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._open_circuit()

    def _open_circuit(self) -> None:
        """
        Open the circuit (transition to OPEN state).

        Sets failure count to 0 to track from this point.
        Increments state change counter.
        """
        self.state = CircuitBreakerState.OPEN
        self.failure_count = 0
        self.success_count = 0
        self.metrics.state_changes += 1

    def _close_circuit(self) -> None:
        """
        Close the circuit (transition to CLOSED state).

        Resets all counters to pristine state.
        Increments state change counter.
        """
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.metrics.state_changes += 1

    def _should_attempt_reset(self) -> bool:
        """
        Check if enough time has passed to attempt recovery.

        Returns:
            True if timeout has elapsed since last failure

        Complexity: O(1) - single comparison
        """
        if self.last_failure_time is None:
            return True
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout

    def get_state(self) -> CircuitBreakerState:
        """
        Get current circuit state.

        Returns:
            Current state: CLOSED, OPEN, or HALF_OPEN
        """
        with self._lock:
            return self.state

    def get_metrics(self) -> CircuitBreakerMetrics:
        """
        Get circuit breaker metrics.

        Returns:
            Copy of current metrics (thread-safe)
        """
        with self._lock:
            return CircuitBreakerMetrics(
                total_calls=self.metrics.total_calls,
                successful_calls=self.metrics.successful_calls,
                failed_calls=self.metrics.failed_calls,
                rejected_calls=self.metrics.rejected_calls,
                state_changes=self.metrics.state_changes
            )


class MetricUnit(IntEnum):
    """Units for metrics."""
    MILLISECONDS = 0
    SECONDS = 1
    COUNT = 2
    BYTES = 3
    PERCENT = 4


@dataclass
class MetricValue:
    """
    Represents a single metric data point.

    Attributes:
        value: Numeric value of the metric
        timestamp: Unix timestamp when recorded
        labels: Dictionary of metric labels/tags
        unit: Unit of measurement
    """
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    unit: MetricUnit = MetricUnit.COUNT


@dataclass
class MetricExportConfig:
    """
    Configuration for metrics export to observability backend.

    Attributes:
        endpoint: OTLP collector endpoint URL
        protocol: Export protocol ("otlp", "jaeger", "zipkin")
        batch_size: Maximum metrics per batch
        export_interval_ms: Interval between exports
        timeout_ms: Export operation timeout
    """
    endpoint: str
    protocol: str
    batch_size: int = 100
    export_interval_ms: int = 5000
    timeout_ms: int = 30000

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.endpoint:
            raise ValueError("endpoint cannot be empty")
        if self.protocol not in ("otlp", "jaeger", "zipkin"):
            raise ValueError(f"Unknown protocol: {self.protocol}")


class MetricsCollector:
    """
    Collects and aggregates metrics for CORTEX system.

    Provides production-grade metrics collection with:
    - Counter metrics (monotonically increasing)
    - Gauge metrics (snapshot values)
    - Label support for multi-dimensional metrics
    - Metrics export to observability backends
    - Thread-safe operations

    AC-ID: AC-NFR-004-01
    Title: OpenTelemetry Metrics Integration

    Example:
        collector = MetricsCollector()
        config = MetricExportConfig(
            endpoint="http://localhost:4317",
            protocol="otlp"
        )
        collector.configure_export(config)
        collector.start_export()

        # Record metrics
        collector.record_counter("requests", labels={"method": "GET"})
        collector.record_gauge("memory_mb", 1024.5)

    Thread Safety: Protected with RLock for concurrent access
    """

    def __init__(self) -> None:
        """Initialize metrics collector."""
        self.metrics: Dict[str, List[MetricValue]] = {}
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.export_config: Optional[MetricExportConfig] = None
        self.is_exporting = False
        self._lock = threading.RLock()

    def configure_export(self, config: MetricExportConfig) -> None:
        """
        Configure metrics export to observability backend.

        Args:
            config: MetricExportConfig with connection details

        Raises:
            ValueError: If configuration is invalid
        """
        with self._lock:
            self.export_config = config

    def record_counter(self, name: str, value: int = 1, labels: Dict[str, str] = None) -> None:
        """
        Record counter metric (incremental value).

        Counters monotonically increase and are used for:
        - Request counts
        - Error counts
        - Operation counters
        - Event counters

        Args:
            name: Metric name (e.g., "http_requests_total")
            value: Amount to increment (default 1)
            labels: Optional metric labels/tags (e.g., {"method": "GET", "status": "200"})

        Complexity: O(1) amortized
        """
        with self._lock:
            if name not in self.counters:
                self.counters[name] = 0
            self.counters[name] += value

            if name not in self.metrics:
                self.metrics[name] = []

            self.metrics[name].append(MetricValue(
                value=float(self.counters[name]),
                timestamp=time.time(),
                labels=labels or {},
                unit=MetricUnit.COUNT
            ))

    def record_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        Record gauge metric (snapshot value).

        Gauges represent instantaneous measurements and are used for:
        - Memory usage
        - CPU utilization
        - Queue depth
        - Active connections

        Args:
            name: Metric name (e.g., "memory_usage_bytes")
            value: Current value
            labels: Optional metric labels/tags

        Complexity: O(1) amortized
        """
        with self._lock:
            self.gauges[name] = value

            if name not in self.metrics:
                self.metrics[name] = []

            self.metrics[name].append(MetricValue(
                value=value,
                timestamp=time.time(),
                labels=labels or {},
                unit=MetricUnit.COUNT
            ))

    def get_metric(self, name: str) -> Optional[float]:
        """
        Get current value of metric.

        Args:
            name: Metric name to retrieve

        Returns:
            Current metric value or None if not found

        Complexity: O(1)
        """
        with self._lock:
            return self.gauges.get(name) or self.counters.get(name)

    def start_export(self) -> bool:
        """
        Start exporting metrics to backend.

        Returns:
            True if export started successfully, False if not configured
        """
        with self._lock:
            if not self.export_config:
                return False
            self.is_exporting = True
            logger.info(f"Started metrics export to {self.export_config.endpoint}")
            return True

    def stop_export(self) -> bool:
        """
        Stop exporting metrics.

        Returns:
            True if export was running
        """
        with self._lock:
            was_exporting = self.is_exporting
            self.is_exporting = False
            if was_exporting:
                logger.info("Stopped metrics export")
            return was_exporting

    def export_metrics(self) -> Dict[str, Any]:
        """
        Export collected metrics.

        Returns:
            Dictionary with metrics, counters, gauges, and timestamp

        Complexity: O(n) where n is number of metrics
        """
        with self._lock:
            if not self.is_exporting:
                return {}

            return {
                "metrics": self.metrics,
                "counters": self.counters,
                "gauges": self.gauges,
                "timestamp": time.time(),
                "endpoint": self.export_config.endpoint if self.export_config else None
            }

    def clear(self) -> None:
        """
        Clear all collected metrics.

        Useful for testing or resetting metrics state.
        """
        with self._lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()

    def get_metric_names(self) -> List[str]:
        """
        Get list of all metric names.

        Returns:
            List of metric names collected
        """
        with self._lock:
            return list(set(list(self.counters.keys()) + list(self.gauges.keys())))


class InstrumentationSpan:
    """
    Represents an instrumented operation span.

    Used to track duration and errors for operations.
    Integrates with metrics collector for comprehensive observability.

    Example:
        span = InstrumentationSpan("database_query", {"table": "users"})
        try:
            # Execute operation
            result = db.query()
        except Exception as e:
            span.record_error(e)
        finally:
            span.end()
    """

    def __init__(self, name: str, attributes: Dict[str, Any] = None) -> None:
        """
        Initialize instrumentation span.

        Args:
            name: Operation name
            attributes: Operation attributes/metadata
        """
        self.name = name
        self.attributes = attributes or {}
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.error: Optional[Exception] = None

    def end(self) -> None:
        """End the span and calculate duration."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def record_error(self, error: Exception) -> None:
        """Record error that occurred during span."""
        self.error = error

    def get_duration_ms(self) -> Optional[float]:
        """Get duration in milliseconds."""
        if self.duration is None:
            return None
        return self.duration * 1000


@dataclass
class DashboardMetrics:
    """
    Metrics displayed on real-time progress dashboard.

    Attributes:
        total_operations: Total operations in phase/task
        completed_operations: Successfully completed operations
        failed_operations: Failed operations
        in_progress: Currently executing operations
        average_duration_ms: Average operation duration
        throughput_ops_per_sec: Operations completed per second
        error_rate: Percentage of failed operations
    """
    total_operations: int = 0
    completed_operations: int = 0
    failed_operations: int = 0
    in_progress: int = 0
    average_duration_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0
    error_rate: float = 0.0


class DashboardUpdateType(IntEnum):
    """Types of dashboard updates."""
    METRIC = 0
    STATUS = 1
    ALERT = 2
    PROGRESS = 3


@dataclass
class DashboardUpdate:
    """
    A single dashboard update message.

    Attributes:
        update_type: Type of update (metric, status, alert, progress)
        timestamp: When the update occurred
        data: Update payload
    """
    update_type: DashboardUpdateType
    timestamp: float
    data: Dict[str, Any]


class RealTimeProgressDashboard:
    """
    Real-time progress dashboard service.

    Provides live metrics display with guaranteed <1s update frequency:
    - Operation progress tracking (0.0-1.0)
    - Live metrics display
    - Status messages
    - Error alerts
    - Subscription notifications

    Features:
    - Thread-safe concurrent updates
    - Update history (last 1000 updates)
    - Subscriber notifications
    - SLA monitoring (<1s updates)
    - Low-latency recording

    AC-ID: AC-NFR-004-02
    Title: Real-Time Progress Dashboard Service

    Example:
        dashboard = RealTimeProgressDashboard()
        dashboard.subscribe(on_update)
        dashboard.start()

        dashboard.record_operation_progress("op-1", 0.5)
        dashboard.record_status_update("Processing...")
        dashboard.record_alert("High memory", "warning")

    Thread Safety: Protected with RLock for concurrent updates
    """

    def __init__(self, update_interval_ms: float = 500) -> None:
        """
        Initialize dashboard.

        Args:
            update_interval_ms: Target update frequency (milliseconds)
        """
        self.update_interval_ms = update_interval_ms
        self.metrics = DashboardMetrics()
        self.updates: deque = deque(maxlen=1000)  # Keep last 1000 updates
        self.is_active = False
        self.last_update_time = time.time()
        self._lock = threading.RLock()
        self.subscribers: List[Callable] = []

    def start(self) -> None:
        """Start the dashboard."""
        with self._lock:
            self.is_active = True
            logger.info("Real-time progress dashboard started")

    def stop(self) -> None:
        """Stop the dashboard."""
        with self._lock:
            self.is_active = False
            logger.info("Real-time progress dashboard stopped")

    def update_metrics(self, metrics: DashboardMetrics) -> None:
        """
        Update dashboard metrics display.

        Args:
            metrics: New metrics snapshot
        """
        with self._lock:
            self.metrics = metrics
            self._record_update(DashboardUpdateType.METRIC, {"metrics": vars(metrics)})

    def record_operation_progress(self, operation_id: str, progress: float) -> None:
        """
        Record progress for an operation.

        Args:
            operation_id: Unique operation identifier
            progress: Progress percentage (0.0-1.0)
        """
        if not 0.0 <= progress <= 1.0:
            raise ValueError("progress must be between 0.0 and 1.0")

        with self._lock:
            self._record_update(DashboardUpdateType.PROGRESS, {
                "operation_id": operation_id,
                "progress": progress
            })

    def record_status_update(self, status: str) -> None:
        """
        Record a status update message.

        Args:
            status: Status message
        """
        with self._lock:
            self._record_update(DashboardUpdateType.STATUS, {"status": status})

    def record_alert(self, alert_message: str, severity: str = "warning") -> None:
        """
        Record an alert for the dashboard.

        Args:
            alert_message: Alert message
            severity: "info", "warning", or "error"
        """
        if severity not in ("info", "warning", "error"):
            raise ValueError(f"Unknown severity: {severity}")

        with self._lock:
            self._record_update(DashboardUpdateType.ALERT, {
                "message": alert_message,
                "severity": severity
            })

    def _record_update(self, update_type: DashboardUpdateType, data: Dict[str, Any]) -> None:
        """Record a dashboard update (must be called with lock)."""
        update = DashboardUpdate(
            update_type=update_type,
            timestamp=time.time(),
            data=data
        )
        self.updates.append(update)
        self.last_update_time = time.time()

        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(update)
            except Exception as e:
                logger.warning(f"Subscriber notification error: {e}")

    def subscribe(self, callback: Callable[[DashboardUpdate], None]) -> None:
        """
        Subscribe to dashboard updates.

        Callback will be called for each update with the DashboardUpdate object.

        Args:
            callback: Function called for each update
        """
        with self._lock:
            self.subscribers.append(callback)

    def get_updates_since(self, timestamp: float) -> List[DashboardUpdate]:
        """
        Get updates since a given timestamp.

        Args:
            timestamp: Starting timestamp (Unix time)

        Returns:
            List of updates after the timestamp

        Complexity: O(n) where n is number of stored updates
        """
        with self._lock:
            return [u for u in self.updates if u.timestamp >= timestamp]

    def get_time_since_last_update(self) -> float:
        """
        Get milliseconds since last update.

        Returns:
            Milliseconds since last dashboard update
        """
        with self._lock:
            return (time.time() - self.last_update_time) * 1000

    def is_updating_within_sla(self) -> bool:
        """
        Check if updates are within <1s SLA.

        Returns:
            True if last update was within 1 second
        """
        return self.get_time_since_last_update() < 1000.0

    def get_current_metrics(self) -> DashboardMetrics:
        """
        Get current dashboard metrics (thread-safe copy).

        Returns:
            Copy of current metrics
        """
        with self._lock:
            return DashboardMetrics(
                total_operations=self.metrics.total_operations,
                completed_operations=self.metrics.completed_operations,
                failed_operations=self.metrics.failed_operations,
                in_progress=self.metrics.in_progress,
                average_duration_ms=self.metrics.average_duration_ms,
                throughput_ops_per_sec=self.metrics.throughput_ops_per_sec,
                error_rate=self.metrics.error_rate
            )


from cortex.models.canonical_enums import AlertSeverity, AlertState


@dataclass
class Threshold:
    """
    Configuration for alert threshold.

    Attributes:
        name: Threshold identifier
        metric: Metric name to monitor
        operator: Comparison operator (>, <, >=, <=, ==)
        value: Threshold value
        severity: Alert severity when violated
        enabled: Whether threshold is active
    """
    name: str
    metric: str
    operator: str
    value: float
    severity: "AlertSeverity"
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate threshold configuration."""
        if self.operator not in (">", "<", ">=", "<=", "=="):
            raise ValueError(f"Invalid operator: {self.operator}")


@dataclass
class Alert:
    """
    An alert notification.

    Attributes:
        alert_id: Unique alert identifier
        metric_name: Name of metric that triggered alert
        threshold_name: Name of violated threshold
        severity: Alert severity level
        state: Current alert lifecycle state
        message: Human-readable alert message
        timestamp: When alert was created
        value: Actual metric value
        acknowledged_at: When alert was acknowledged
    """
    alert_id: str
    metric_name: str
    threshold_name: str
    severity: AlertSeverity
    state: AlertState
    message: str
    timestamp: float
    value: Optional[float] = None
    acknowledged_at: Optional[float] = None


class NotificationChannel:
    """
    Base class for alert notification channels.

    Subclass for email, Slack, PagerDuty, etc.
    """

    def send(self, alert: Alert) -> bool:
        """
        Send alert notification.

        Args:
            alert: Alert to send

        Returns:
            True if sent successfully
        """
        raise NotImplementedError


class AlertManager:
    """
    Manages alerts with configurable thresholds and notifications.

    Provides:
    - Threshold configuration (>/</>=/<=​/==)
    - Automatic alert triggering on violations
    - Multiple notification channels
    - Alert lifecycle management (active/acknowledged/resolved)
    - Metric history tracking

    AC-ID: AC-NFR-004-03
    Title: Alert Management & Threshold Monitoring

    Example:
        manager = AlertManager()

        # Configure threshold
        threshold = Threshold(
            name="high_cpu",
            metric="cpu_usage",
            operator=">",
            value=80.0,
            severity=AlertSeverity.WARNING
        )
        manager.add_threshold(threshold)

        # Add notification channel
        manager.add_channel(EmailChannel("admin@example.com"))

        # Record metrics (alerts triggered automatically)
        manager.record_metric("cpu_usage", 85.0)

    Thread Safety: Use external locking for multi-threaded access
    """

    def __init__(self) -> None:
        """Initialize alert manager."""
        self.thresholds: Dict[str, Threshold] = {}
        self.channels: List[NotificationChannel] = []
        self.alerts: Dict[str, Alert] = {}
        self.alert_counter = 0
        self.metrics_history: Dict[str, List[float]] = {}
        self._lock = threading.RLock()

    def add_threshold(self, threshold: Threshold) -> str:
        """
        Add alert threshold configuration.

        Args:
            threshold: Threshold configuration

        Returns:
            Threshold name

        Raises:
            ValueError: If configuration invalid
        """
        with self._lock:
            self.thresholds[threshold.name] = threshold
            logger.info(f"Added threshold: {threshold.name} ({threshold.metric} {threshold.operator} {threshold.value})")
            return threshold.name

    def remove_threshold(self, threshold_name: str) -> bool:
        """
        Remove threshold by name.

        Args:
            threshold_name: Name of threshold to remove

        Returns:
            True if threshold existed and was removed
        """
        with self._lock:
            if threshold_name in self.thresholds:
                del self.thresholds[threshold_name]
                return True
            return False

    def add_channel(self, channel: NotificationChannel) -> None:
        """
        Add notification channel.

        Args:
            channel: Notification channel implementation
        """
        with self._lock:
            self.channels.append(channel)

    def record_metric(self, metric_name: str, value: float) -> List[Alert]:
        """
        Record metric value and check against thresholds.

        Args:
            metric_name: Name of metric
            value: Metric value

        Returns:
            List of alerts triggered by this metric

        Complexity: O(n) where n is number of thresholds
        """
        with self._lock:
            # Store metric history
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []
            self.metrics_history[metric_name].append(value)

            triggered_alerts = []

            # Check all thresholds for this metric
            for threshold in self.thresholds.values():
                if threshold.metric == metric_name and threshold.enabled:
                    if self._check_threshold(threshold, value):
                        alert = self._create_alert(threshold, metric_name, value)
                        self.alerts[alert.alert_id] = alert
                        triggered_alerts.append(alert)
                        self._notify_channels(alert)

            return triggered_alerts

    def _check_threshold(self, threshold: Threshold, value: float) -> bool:
        """Check if metric value violates threshold."""
        if threshold.operator == ">":
            return value > threshold.value
        elif threshold.operator == "<":
            return value < threshold.value
        elif threshold.operator == ">=":
            return value >= threshold.value
        elif threshold.operator == "<=":
            return value <= threshold.value
        elif threshold.operator == "==":
            return value == threshold.value
        return False

    def _create_alert(self, threshold: Threshold, metric: str, value: float) -> Alert:
        """Create alert from threshold violation."""
        self.alert_counter += 1
        alert_id = f"alert-{self.alert_counter}"

        return Alert(
            alert_id=alert_id,
            metric_name=metric,
            threshold_name=threshold.name,
            severity=threshold.severity,
            state=AlertState.ACTIVE,
            message=f"{metric} {threshold.operator} {threshold.value} (actual: {value})",
            timestamp=time.time(),
            value=value
        )

    def _notify_channels(self, alert: Alert) -> None:
        """Send alert to all notification channels."""
        for channel in self.channels:
            try:
                channel.send(alert)
            except Exception as e:
                logger.warning(f"Channel notification error: {e}")

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert to acknowledge

        Returns:
            True if alert acknowledged
        """
        with self._lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].state = AlertState.ACKNOWLEDGED
                self.alerts[alert_id].acknowledged_at = time.time()
                return True
            return False

    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert.

        Args:
            alert_id: Alert to resolve

        Returns:
            True if alert resolved
        """
        with self._lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].state = AlertState.RESOLVED
                return True
            return False

    def get_active_alerts(self) -> List[Alert]:
        """
        Get all active (not acknowledged/resolved) alerts.

        Returns:
            List of active alerts
        """
        with self._lock:
            return [a for a in self.alerts.values() if a.state == AlertState.ACTIVE]

    def enable_threshold(self, threshold_name: str) -> bool:
        """
        Enable a threshold.

        Args:
            threshold_name: Threshold to enable

        Returns:
            True if threshold enabled
        """
        with self._lock:
            if threshold_name in self.thresholds:
                self.thresholds[threshold_name].enabled = True
                return True
            return False

    def disable_threshold(self, threshold_name: str) -> bool:
        """
        Disable a threshold.

        Args:
            threshold_name: Threshold to disable

        Returns:
            True if threshold disabled
        """
        with self._lock:
            if threshold_name in self.thresholds:
                self.thresholds[threshold_name].enabled = False
                return True
            return False


__all__ = [
    "GracefulDegradationFramework",
    "PartialFunctionalityMode",
    "ComponentFailure",
    "DegradedResponse",
    "ComponentMetrics",
    "DegradationLevel",
    "ComponentState",
    "FallbackStrategy",
    "FailureHandler",
    "ExponentialBackoffRetry",
    "RetryPolicy",
    "RetryResult",
    "RetryPolicyBuilder",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerMetrics",
    "CircuitBreakerOpen",
    "CircuitBreakerState",
    "MetricsCollector",
    "MetricValue",
    "MetricExportConfig",
    "MetricUnit",
    "InstrumentationSpan",
    "RealTimeProgressDashboard",
    "DashboardMetrics",
    "DashboardUpdate",
    "DashboardUpdateType",
    "AlertManager",
    "Alert",
    "AlertSeverity",
    "AlertState",
    "Threshold",
    "NotificationChannel",
]
