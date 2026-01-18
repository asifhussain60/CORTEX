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

from typing import Dict, List, Any, Optional, Callable, Type, Protocol
from dataclasses import dataclass, field
from enum import IntEnum
import logging
from contextlib import contextmanager
import threading
from pathlib import Path
import random
import time

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
