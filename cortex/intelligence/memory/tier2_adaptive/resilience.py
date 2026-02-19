"""
Graceful Degradation Framework (AC-NFR-002-01)

Enables the system to continue operating with reduced functionality when
components fail. Provides fallback strategies and partial functionality mode.

Key Components:
- GracefulDegradationFramework: Main orchestrator
- FallbackStrategy: Encapsulates fallback strategies
- PartialFunctionalityMode: Manages degraded operation
- ComponentFailure: Exception for component failure
- DegradedResponse: Response wrapper with degradation metadata

Governance Compliance:
✓ CORE-008: TDD Pattern
✓ CORE-011: 100% Type Hints
✓ CORE-012: 100% Docstrings
✓ CORE-024: Audit Logging
✓ CORE-028: Portable Paths
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple, Generic, TypeVar
from datetime import datetime
from threading import RLock
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class ComponentFailure(Exception):
    """
    Exception raised when a component fails and cannot recover.
    
    Contains context about the failure including component name,
    number of strategies tried, and the last exception encountered.
    
    Attributes:
        component_name: Name of the failed component
        reason: Reason for failure
        strategies_tried: Number of fallback strategies attempted
        last_exception: The exception that caused final failure
    """
    
    def __init__(
        self,
        component_name: str,
        reason: str,
        strategies_tried: int = 0,
        last_exception: Optional[Exception] = None,
    ) -> None:
        """
        Initialize ComponentFailure exception.
        
        Args:
            component_name: Name of component that failed
            reason: Human-readable reason for failure
            strategies_tried: How many fallback strategies were attempted
            last_exception: The exception that caused final failure
        """
        self.component_name: str = component_name
        self.reason: str = reason
        self.strategies_tried: int = strategies_tried
        self.last_exception: Optional[Exception] = last_exception
        
        message = (
            f"Component '{component_name}' failed: {reason}. "
            f"Tried {strategies_tried} fallback strategies."
        )
        super().__init__(message)
        
        logger.error(
            "ComponentFailure",
            extra={
                "component": component_name,
                "reason": reason,
                "strategies_tried": strategies_tried,
                "last_exception": str(last_exception) if last_exception else None,
            },
        )


T = TypeVar("T")


class DegradedResponse(Generic[T]):
    """
    Wraps a response with degradation metadata.
    
    Indicates that the response came from degraded operation mode
    (fallback strategy or partial functionality).
    
    Type Parameters:
        T: Type of wrapped response data
    
    Attributes:
        data: Response data
        degradation_reason: Why degradation occurred
        mode: Which mode returned this data (primary/fallback_N/degraded)
        original_request_id: ID of original request (for tracking)
    """
    
    def __init__(
        self,
        data: T,
        degradation_reason: str,
        mode: str,
        original_request_id: Optional[str] = None,
    ) -> None:
        """
        Initialize degraded response wrapper.
        
        Args:
            data: Response data from the execution
            degradation_reason: Why degradation occurred
            mode: Execution mode (primary/fallback_1/etc)
            original_request_id: ID of original request (optional)
        """
        self._data: T = data
        self._degradation_reason: str = degradation_reason
        self._mode: str = mode
        self._original_request_id: Optional[str] = original_request_id
        self._created_at: datetime = datetime.utcnow()
    
    def get_data(self) -> T:
        """
        Get wrapped response data.
        
        Returns:
            The response data of type T
        """
        return self._data
    
    def is_degraded(self) -> bool:
        """
        Check if response is from degraded operation.
        
        Returns:
            True if mode is not "primary", False otherwise
        """
        return self._mode != "primary"
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get degradation metadata.
        
        Returns:
            Dictionary with degradation context:
            - degradation_reason: str
            - mode: str (primary/fallback_1/etc)
            - original_request_id: str or None
            - created_at: datetime of response
        """
        return {
            "degradation_reason": self._degradation_reason,
            "mode": self._mode,
            "original_request_id": self._original_request_id,
            "created_at": self._created_at.isoformat(),
        }


class FallbackStrategy:
    """
    Represents a single fallback strategy with retry capability.
    
    Encapsulates a callable with priority, max retries, and execution logic.
    
    Attributes:
        callable: Function to execute
        priority: Strategy priority (lower = higher priority)
        max_retries: Maximum retry attempts before giving up
    """
    
    def __init__(
        self,
        callable: Callable[..., Any],
        priority: int = 0,
        max_retries: int = 1,
    ) -> None:
        """
        Initialize fallback strategy.
        
        Args:
            callable: Function to execute as fallback
            priority: Strategy priority (0 = highest)
            max_retries: Maximum retry attempts (default 1)
        """
        self.callable: Callable[..., Any] = callable
        self.priority: int = priority
        self.max_retries: int = max_retries
        self._execution_count: int = 0
        self._last_exception: Optional[Exception] = None
    
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute this strategy with retries.
        
        Args:
            *args: Positional arguments for the callable
            **kwargs: Keyword arguments for the callable
        
        Returns:
            Result of successful execution
        
        Raises:
            StrategyExecutionException: If all retries exhausted
        """
        last_exc: Optional[Exception] = None
        
        for attempt in range(self.max_retries):
            try:
                self._execution_count += 1
                result: Any = self.callable(*args, **kwargs)
                
                logger.debug(
                    f"Strategy {self.priority} succeeded on attempt {attempt + 1}"
                )
                return result
            except Exception as e:
                last_exc = e
                self._last_exception = e
                logger.warning(
                    f"Strategy {self.priority} attempt {attempt + 1} failed: {str(e)}"
                )
        
        raise StrategyExecutionException(
            f"Strategy {self.priority} failed after {self.max_retries} attempts",
            last_exc,
        )


class StrategyExecutionException(Exception):
    """Raised when a strategy execution fails after all retries."""
    
    def __init__(self, message: str, last_exception: Optional[Exception] = None) -> None:
        """Initialize strategy execution exception."""
        self.last_exception: Optional[Exception] = last_exception
        super().__init__(message)


class PartialFunctionalityMode:
    """
    Manages system operation with reduced functionality.
    
    Tracks which features are available/disabled and provides
    status reporting for degraded operation.
    
    Attributes:
        _features: Dictionary of feature names to availability status
        _feature_reasons: Dictionary of feature names to disable reasons
    """
    
    def __init__(self) -> None:
        """Initialize with all features enabled by default."""
        self._features: Dict[str, bool] = {}
        self._feature_reasons: Dict[str, str] = {}
        self._lock: RLock = RLock()
    
    def disable_feature(self, feature_name: str, reason: str) -> None:
        """
        Disable a feature.
        
        Args:
            feature_name: Name of feature to disable
            reason: Reason for disablement
        """
        with self._lock:
            self._features[feature_name] = False
            self._feature_reasons[feature_name] = reason
            
            logger.warning(
                f"Feature disabled: {feature_name} - {reason}"
            )
    
    def enable_feature(self, feature_name: str) -> None:
        """
        Re-enable a previously disabled feature.
        
        Args:
            feature_name: Name of feature to enable
        """
        with self._lock:
            self._features[feature_name] = True
            self._feature_reasons.pop(feature_name, None)
            
            logger.info(f"Feature enabled: {feature_name}")
    
    def is_feature_available(self, feature_name: str) -> bool:
        """
        Check if feature is available.
        
        Args:
            feature_name: Name of feature to check
        
        Returns:
            True if available (enabled), False if disabled
        """
        with self._lock:
            return self._features.get(feature_name, True)
    
    def get_available_features(self) -> List[str]:
        """
        Get list of currently available features.
        
        Returns:
            List of feature names that are enabled
        """
        with self._lock:
            return [
                name for name, available in self._features.items()
                if available
            ]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all features.
        
        Returns:
            Dictionary with feature names as keys and status as values
        """
        with self._lock:
            return {
                name: self._features.get(name, True)
                for name in self._features.keys()
            }


class GracefulDegradationFramework:
    """
    Orchestrates graceful degradation when components fail.
    
    Manages fallback strategies and partial functionality modes
    to enable system continuation with reduced functionality.
    
    Key Features:
    - Component registration with primary and fallback strategies
    - Automatic fallback on primary strategy failure
    - Degradation status tracking
    - Thread-safe concurrent access
    - Structured logging and audit trail
    """
    
    def __init__(self) -> None:
        """Initialize framework with empty component registry."""
        self._components: Dict[str, Dict[str, Any]] = {}
        self._component_states: Dict[str, Dict[str, Any]] = {}
        self._lock: RLock = RLock()
        
        logger.info("GracefulDegradationFramework initialized")
    
    def register_component(
        self,
        name: str,
        primary_strategy: Callable[..., Any],
        fallback_strategies: List[Callable[..., Any]],
    ) -> None:
        """
        Register a component with fallback strategies.
        
        Args:
            name: Component identifier
            primary_strategy: Callable providing primary functionality
            fallback_strategies: List of Callables for fallback (ordered by priority)
        
        Raises:
            ValueError: If component already registered
        """
        with self._lock:
            if name in self._components:
                raise ValueError(f"Component '{name}' already registered")
            
            # Store component configuration
            self._components[name] = {
                "primary": primary_strategy,
                "fallbacks": fallback_strategies,
            }
            
            # Initialize component state
            self._component_states[name] = {
                "current_mode": "primary",
                "is_degraded": False,
                "failure_count": 0,
                "last_failure": None,
                "last_failure_reason": None,
                "registered_at": datetime.utcnow(),
            }
            
            logger.info(
                f"Component registered: {name} "
                f"(primary + {len(fallback_strategies)} fallbacks)"
            )
    
    def execute_with_degradation(
        self,
        component_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> Tuple[Any, str]:
        """
        Execute component with automatic fallback on failure.
        
        Attempts execution in this order:
        1. Primary strategy
        2. Fallback strategies (in order)
        3. Raises ComponentFailure if all fail
        
        Args:
            component_name: Name of registered component
            *args: Positional arguments for component
            **kwargs: Keyword arguments for component
        
        Returns:
            Tuple of (result, mode_name) where mode_name is:
            - "primary" if primary strategy succeeded
            - "fallback_1", "fallback_2", etc. if fallback succeeded
            - "degraded" if no strategies worked
        
        Raises:
            ComponentFailure: If all strategies exhausted
        """
        with self._lock:
            if component_name not in self._components:
                raise ValueError(f"Component '{component_name}' not registered")
            
            component = self._components[component_name]
            state = self._component_states[component_name]
        
        # Try primary strategy
        primary_exc: Optional[Exception] = None
        try:
            result: Any = component["primary"](*args, **kwargs)
            
            with self._lock:
                state["current_mode"] = "primary"
                state["is_degraded"] = False
                state["failure_count"] = 0
            
            logger.debug(f"Component '{component_name}' executed in primary mode")
            return result, "primary"
        
        except Exception as exc:
            primary_exc = exc
            logger.warning(
                f"Component '{component_name}' primary strategy failed: {str(primary_exc)}"
            )
            with self._lock:
                state["failure_count"] += 1
                state["last_failure"] = datetime.utcnow()
                state["last_failure_reason"] = str(primary_exc)
        
        # Try fallback strategies
        fallbacks: List[Callable[..., Any]] = component["fallbacks"]
        last_exception: Optional[Exception] = primary_exc
        
        for fallback_index, fallback in enumerate(fallbacks, start=1):
            try:
                result = fallback(*args, **kwargs)
                
                with self._lock:
                    state["current_mode"] = f"fallback_{fallback_index}"
                    state["is_degraded"] = True
                
                logger.info(
                    f"Component '{component_name}' using fallback_{fallback_index}"
                )
                return result, f"fallback_{fallback_index}"
            
            except Exception as fallback_exc:
                logger.warning(
                    f"Component '{component_name}' fallback_{fallback_index} failed: "
                    f"{str(fallback_exc)}"
                )
                last_exception = fallback_exc
        
        # All strategies failed
        with self._lock:
            state["current_mode"] = "degraded"
            state["is_degraded"] = True
        
        raise ComponentFailure(
            component_name=component_name,
            reason="All fallback strategies exhausted",
            strategies_tried=len(fallbacks) + 1,  # primary + all fallbacks
            last_exception=last_exception,
        )
    
    def is_degraded(self, component_name: str) -> bool:
        """
        Check if component is currently in degraded mode.
        
        Args:
            component_name: Name of component to check
        
        Returns:
            True if in degraded mode, False if operating normally
        """
        with self._lock:
            if component_name not in self._component_states:
                return False
            return self._component_states[component_name]["is_degraded"]
    
    def get_degradation_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all registered components.
        
        Returns:
            Dictionary with component names as keys and status dicts as values:
            {
                "component_name": {
                    "current_mode": str,
                    "is_degraded": bool,
                    "failure_count": int,
                    "last_failure": datetime,
                    "last_failure_reason": str
                }
            }
        """
        with self._lock:
            return {
                name: {
                    "current_mode": state["current_mode"],
                    "is_degraded": state["is_degraded"],
                    "failure_count": state["failure_count"],
                    "last_failure": state["last_failure"],
                    "last_failure_reason": state["last_failure_reason"],
                }
                for name, state in self._component_states.items()
            }


# ===== AC-NFR-002-02: Automatic Retry with Exponential Backoff =====

class RetryPolicy:
    """
    Configuration for retry behavior with exponential backoff.
    
    Defines how many times to retry, backoff parameters, and which
    exceptions should trigger retries.
    
    Attributes:
        max_retries: Maximum number of retry attempts
        initial_backoff_ms: Initial backoff duration in milliseconds
        max_backoff_ms: Maximum backoff duration in milliseconds
        backoff_multiplier: Multiplier for exponential backoff
        use_jitter: Whether to add randomness to backoff
        non_retryable_exceptions: Exceptions to not retry on
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff_ms: int = 100,
        max_backoff_ms: int = 32000,
        backoff_multiplier: float = 2.0,
        use_jitter: bool = False,
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum number of retries (3 by default)
            initial_backoff_ms: Initial backoff in ms (100 by default)
            max_backoff_ms: Maximum backoff in ms (32s by default)
            backoff_multiplier: Multiplier for exponential backoff (2.0 by default)
            use_jitter: Add randomness to backoff (False by default)
        """
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self.backoff_multiplier = backoff_multiplier
        self.use_jitter = use_jitter
        self.non_retryable_exceptions: List[type] = []
    
    def calculate_backoff(self, attempt: int) -> float:
        """
        Calculate backoff time for given attempt number.
        
        Args:
            attempt: Attempt number (1-based)
        
        Returns:
            Backoff time in milliseconds
        """
        import random
        
        backoff = self.initial_backoff_ms * (self.backoff_multiplier ** (attempt - 1))
        backoff = min(backoff, self.max_backoff_ms)
        
        if self.use_jitter:
            jitter = random.uniform(0, backoff * 0.1)
            backoff += jitter
        
        return backoff


class RetryPolicyBuilder:
    """
    Builder for creating RetryPolicy instances with fluent API.
    
    Allows chainable configuration of retry behavior.
    """
    
    def __init__(self):
        """Initialize builder with default values."""
        self._max_retries = 3
        self._initial_backoff = 100
        self._max_backoff = 32000
        self._multiplier = 2.0
        self._use_jitter = False
    
    def with_max_retries(self, max_retries: int) -> RetryPolicyBuilder:
        """
        Set maximum number of retries.
        
        Args:
            max_retries: Maximum retry count
        
        Returns:
            Self for chaining
        """
        self._max_retries = max_retries
        return self
    
    def with_initial_backoff(self, backoff_ms: int) -> RetryPolicyBuilder:
        """
        Set initial backoff duration.
        
        Args:
            backoff_ms: Initial backoff in milliseconds
        
        Returns:
            Self for chaining
        """
        self._initial_backoff = backoff_ms
        return self
    
    def with_max_backoff(self, backoff_ms: int) -> RetryPolicyBuilder:
        """
        Set maximum backoff duration.
        
        Args:
            backoff_ms: Maximum backoff in milliseconds
        
        Returns:
            Self for chaining
        """
        self._max_backoff = backoff_ms
        return self
    
    def with_multiplier(self, multiplier: float) -> RetryPolicyBuilder:
        """
        Set backoff multiplier.
        
        Args:
            multiplier: Exponential backoff multiplier
        
        Returns:
            Self for chaining
        """
        self._multiplier = multiplier
        return self
    
    def with_jitter(self, use_jitter: bool) -> RetryPolicyBuilder:
        """
        Enable/disable jitter in backoff.
        
        Args:
            use_jitter: Whether to add jitter
        
        Returns:
            Self for chaining
        """
        self._use_jitter = use_jitter
        return self
    
    def build(self) -> RetryPolicy:
        """
        Build the RetryPolicy instance.
        
        Returns:
            Configured RetryPolicy
        """
        policy = RetryPolicy(
            max_retries=self._max_retries,
            initial_backoff_ms=self._initial_backoff,
            max_backoff_ms=self._max_backoff,
            backoff_multiplier=self._multiplier,
            use_jitter=self._use_jitter,
        )
        return policy


class RetryResult:
    """
    Result of a retry operation.
    
    Captures success status, number of attempts, timing, and any exception.
    
    Attributes:
        success: Whether operation succeeded
        attempt_count: Number of attempts made
        total_time_ms: Total time spent in retries
        exception: Exception if failed (None if succeeded)
        data: Returned data if successful (None if failed)
    """
    
    def __init__(
        self,
        success: bool,
        attempt_count: int,
        total_time_ms: float,
        exception: Optional[Exception] = None,
        data: Any = None,
    ):
        """
        Initialize retry result.
        
        Args:
            success: Whether retry succeeded
            attempt_count: Total attempts made
            total_time_ms: Total time in milliseconds
            exception: Exception if failed
            data: Result data if successful
        """
        self.success = success
        self.attempt_count = attempt_count
        self.total_time_ms = total_time_ms
        self.exception = exception
        self.data = data
    
    def is_success(self) -> bool:
        """
        Check if operation succeeded.
        
        Returns:
            True if successful, False otherwise
        """
        return self.success
    
    def get_data(self) -> Any:
        """
        Get result data.
        
        Returns:
            Data from successful operation
        """
        return self.data
    
    def get_exception(self) -> Optional[Exception]:
        """
        Get exception if failed.
        
        Returns:
            Exception or None
        """
        return self.exception


class ExponentialBackoffRetry:
    """
    Retry handler with exponential backoff strategy.
    
    Executes operations with automatic retries on failure, using
    exponential backoff between attempts. Thread-safe with RLock.
    
    Provides:
    - Configurable retry policies
    - Exponential backoff with optional jitter
    - Non-retryable exception handling
    - Comprehensive retry tracking
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_backoff_ms: int = 100,
        max_backoff_ms: int = 32000,
    ):
        """
        Initialize retry handler.
        
        Args:
            max_retries: Default maximum retries (3)
            initial_backoff_ms: Default initial backoff (100ms)
            max_backoff_ms: Default maximum backoff (32s)
        """
        self.max_retries = max_retries
        self.initial_backoff_ms = initial_backoff_ms
        self.max_backoff_ms = max_backoff_ms
        self._lock = RLock()
        self._retry_count: Dict[str, int] = {}
        
        logger.debug(
            f"ExponentialBackoffRetry initialized: "
            f"max_retries={max_retries}, initial_backoff_ms={initial_backoff_ms}"
        )
    
    def execute_with_retry(
        self,
        operation: Callable[..., Any],
        policy: Optional[RetryPolicy] = None,
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        raise_on_retry_failure: bool = True,
    ) -> Any:
        """
        Execute operation with retry and exponential backoff.
        
        Args:
            operation: Callable to execute
            policy: RetryPolicy to apply (None = use defaults)
            args: Positional arguments for operation
            kwargs: Keyword arguments for operation
            raise_on_retry_failure: Whether to raise on all failures
        
        Returns:
            Result from operation on success
        
        Raises:
            Exception: If operation fails after all retries (when raise_on_retry_failure=True)
        """
        import time
        
        if policy is None:
            policy = RetryPolicy(
                max_retries=self.max_retries,
                initial_backoff_ms=self.initial_backoff_ms,
                max_backoff_ms=self.max_backoff_ms,
            )
        
        if kwargs is None:
            kwargs = {}
        
        last_exception: Optional[Exception] = None
        start_time = time.time()
        
        for attempt in range(policy.max_retries + 1):
            try:
                result = operation(*args, **kwargs)
                
                elapsed_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"Operation succeeded on attempt {attempt + 1}, "
                    f"elapsed: {elapsed_ms:.2f}ms"
                )
                
                return result
            
            except Exception as exc:
                last_exception = exc
                
                # Check if exception should not be retried
                if any(isinstance(exc, exc_type) for exc_type in policy.non_retryable_exceptions):
                    logger.warning(
                        f"Non-retryable exception on attempt {attempt + 1}: {type(exc).__name__}: {exc}"
                    )
                    raise
                
                # If this was the last attempt, stop
                if attempt >= policy.max_retries:
                    elapsed_ms = (time.time() - start_time) * 1000
                    logger.error(
                        f"Operation failed after {attempt + 1} attempts, "
                        f"total time: {elapsed_ms:.2f}ms"
                    )
                    
                    if raise_on_retry_failure:
                        raise
                    else:
                        return None
                
                # Calculate backoff before next attempt
                backoff_ms = policy.calculate_backoff(attempt + 1)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {exc}. "
                    f"Retrying in {backoff_ms:.2f}ms..."
                )
                
                # Wait before retry
                time.sleep(backoff_ms / 1000.0)
        
        # Should not reach here
        if raise_on_retry_failure and last_exception:
            raise last_exception
        
        return None


# ===== AC-NFR-002-03: Circuit Breaker Pattern =====

from enum import Enum
from cortex.models.canonical_enums import AlertSeverity, CircuitBreakerState




class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is OPEN."""
    
    def __init__(self, component_name: str = "unknown"):
        """Initialize exception."""
        self.component_name = component_name
        super().__init__(f"Circuit breaker is OPEN for {component_name}")


class CircuitBreakerMetrics:
    """Metrics for circuit breaker."""
    
    def __init__(self):
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
    ):
        """
        Initialize circuit breaker configuration.
        
        Args:
            failure_threshold: Failures before opening (5)
            success_threshold: Successes in HALF_OPEN to close (2)
            timeout_seconds: Timeout before OPEN->HALF_OPEN (60)
            name: Circuit breaker name
        """
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.name = name


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.
    
    Protects against cascading failures by monitoring operation outcomes
    and failing fast when systems are unavailable.
    
    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Failures exceeded, calls rejected fast
    - HALF_OPEN: Testing recovery, limited calls allowed
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.
        
        Args:
            config: CircuitBreakerConfig instance
        """
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
        """
        Execute operation through circuit breaker.
        
        Args:
            operation: Callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result from operation
        
        Raises:
            CircuitBreakerOpen: If circuit is OPEN
            Exception: From operation if failed
        """
        # Check state and potentially transition
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    # Allow transition to HALF_OPEN
                    self.state = CircuitBreakerState.HALF_OPEN
                    self._success_count = 0
                    self._failure_count = 0
                    logger.info(
                        f"CircuitBreaker '{self.config.name}' transitioned "
                        f"OPEN -> HALF_OPEN (timeout elapsed)"
                    )
                else:
                    # Reject calls while still OPEN
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
                logger.debug(f"CircuitBreaker '{self.config.name}': Success in CLOSED")
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self._success_count += 1
                
                if self._success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    self.metrics.reset()
                    logger.info(
                        f"CircuitBreaker '{self.config.name}' transitioned "
                        f"HALF_OPEN -> CLOSED (recovered)"
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
                logger.warning(
                    f"CircuitBreaker '{self.config.name}': Failure {self._failure_count}"
                    f"/{self.config.failure_threshold}"
                )
                
                if self._failure_count >= self.config.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    logger.error(
                        f"CircuitBreaker '{self.config.name}' transitioned "
                        f"CLOSED -> OPEN (failure threshold exceeded)"
                    )
            
            elif self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.OPEN
                self._failure_count = 0
                self._success_count = 0
                logger.error(
                    f"CircuitBreaker '{self.config.name}' transitioned "
                    f"HALF_OPEN -> OPEN (recovery failed)"
                )
    
    def is_open(self) -> bool:
        """
        Check if circuit is OPEN.
        
        Returns:
            True if OPEN, False otherwise
        """
        with self._lock:
            return self.state == CircuitBreakerState.OPEN
    
    def is_closed(self) -> bool:
        """
        Check if circuit is CLOSED.
        
        Returns:
            True if CLOSED, False otherwise
        """
        with self._lock:
            return self.state == CircuitBreakerState.CLOSED
    
    def is_half_open(self) -> bool:
        """
        Check if circuit is HALF_OPEN.
        
        Returns:
            True if HALF_OPEN, False otherwise
        """
        with self._lock:
            return self.state == CircuitBreakerState.HALF_OPEN
    
    def get_metrics(self) -> CircuitBreakerMetrics:
        """
        Get current metrics.
        
        Returns:
            Copy of current metrics
        """
        with self._lock:
            metrics_copy = CircuitBreakerMetrics()
            metrics_copy.successful_calls = self.metrics.successful_calls
            metrics_copy.failed_calls = self.metrics.failed_calls
            metrics_copy.rejected_calls = self.metrics.rejected_calls
            metrics_copy.last_failure_time = self.metrics.last_failure_time
            metrics_copy.last_error_message = self.metrics.last_error_message
            return metrics_copy
    
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


# ===== AC-NFR-004-01: OpenTelemetry Metrics Integration =====

class MetricUnit(Enum):
    """Standard metric units."""
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    BYTES = "bytes"
    REQUESTS = "requests"
    PERCENTAGE = "percentage"


class MetricValue:
    """Encapsulates a metric measurement with metadata."""
    
    def __init__(
        self,
        value: float,
        unit: MetricUnit,
        timestamp: Optional[datetime] = None,
        labels: Optional[Dict[str, Any]] = None,
    ):
        """Initialize metric value."""
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.utcnow()
        self.labels = labels or {}


class MetricExportConfig:
    """Configuration for metric export."""
    
    def __init__(
        self,
        endpoint: str = "http://localhost:9090",
        batch_size: int = 100,
        flush_interval_ms: int = 5000,
    ):
        """Initialize export configuration."""
        self.endpoint = endpoint
        self.batch_size = batch_size
        self.flush_interval_ms = flush_interval_ms


class InstrumentationSpan:
    """Represents a span for tracing and instrumentation."""
    
    def __init__(
        self,
        name: str,
        operation: str = "default",
        resource_name: str = "unknown",
    ):
        """Initialize instrumentation span."""
        self.name = name
        self.operation = operation
        self.resource_name = resource_name
        self._attributes: Dict[str, Any] = {}
        self._events: List[str] = []
        self._start_time = datetime.utcnow()
    
    def add_attribute(self, key: str, value: Any) -> None:
        """Add attribute to span."""
        self._attributes[key] = value
    
    def add_event(self, event: str) -> None:
        """Record event in span."""
        self._events.append(event)
        logger.debug(f"Span '{self.name}' event: {event}")
    
    def get_attributes(self) -> Dict[str, Any]:
        """Get all span attributes."""
        return self._attributes.copy()
    
    def get_events(self) -> List[str]:
        """Get all span events."""
        return self._events.copy()


class MetricsCollector:
    """
    Collects and exports metrics to observability backends.
    
    Supports counter, gauge, and histogram metrics with labels
    and dimensional data for observability.
    """
    
    def __init__(self, config: Optional[MetricExportConfig] = None):
        """Initialize metrics collector."""
        self.config = config or MetricExportConfig()
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = RLock()
        logger.debug(f"MetricsCollector initialized with endpoint: {self.config.endpoint}")
    
    def counter(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Record counter metric (monotonically increasing).
        
        Args:
            metric_name: Name of the metric
            value: Amount to increment
            labels: Optional labels for dimensional data
        """
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {
                    "type": "counter",
                    "value": 0,
                    "labels": labels or {},
                }
            self._metrics[metric_name]["value"] += value
        logger.debug(f"Counter '{metric_name}' incremented by {value}")
    
    def gauge(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Record gauge metric (snapshot value).
        
        Args:
            metric_name: Name of the metric
            value: Current value
            labels: Optional labels for dimensional data
        """
        with self._lock:
            self._metrics[metric_name] = {
                "type": "gauge",
                "value": value,
                "labels": labels or {},
                "timestamp": datetime.utcnow(),
            }
        logger.debug(f"Gauge '{metric_name}' set to {value}")
    
    def histogram(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Record histogram metric (distribution of values).
        
        Args:
            metric_name: Name of the metric
            value: Value to record
            labels: Optional labels for dimensional data
        """
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {
                    "type": "histogram",
                    "values": [],
                    "labels": labels or {},
                }
            self._metrics[metric_name]["values"].append(value)
        logger.debug(f"Histogram '{metric_name}' recorded value {value}")
    
    def summary(
        self,
        metric_name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Record summary metric (similar to histogram).
        
        Args:
            metric_name: Name of the metric
            value: Value to record
            labels: Optional labels for dimensional data
        """
        with self._lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = {
                    "type": "summary",
                    "values": [],
                    "labels": labels or {},
                }
            self._metrics[metric_name]["values"].append(value)
        logger.debug(f"Summary '{metric_name}' recorded value {value}")
    
    def get_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all collected metrics.
        
        Returns:
            Dictionary of metrics with their values and metadata
        """
        with self._lock:
            return self._metrics.copy()
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()
        logger.info("MetricsCollector reset")


# ===== AC-NFR-004-02: Real-Time Progress Dashboard =====

class DashboardUpdateType(Enum):
    """Types of dashboard updates."""
    PROGRESS = "progress"
    STATUS = "status"
    ERROR = "error"
    ALERT = "alert"


class DashboardUpdate:
    """Represents a single dashboard update."""
    
    def __init__(
        self,
        operation_id: str,
        update_type: DashboardUpdateType,
        value: Any,
        timestamp: Optional[datetime] = None,
    ):
        """Initialize dashboard update."""
        self.operation_id = operation_id
        self.update_type = update_type
        self.value = value
        self.timestamp = timestamp or datetime.utcnow()


class DashboardMetrics:
    """Metrics for a single operation on the dashboard."""
    
    def __init__(
        self,
        operation_id: str,
        progress: float = 0.0,
        status: str = "Idle",
        start_time: Optional[datetime] = None,
    ):
        """Initialize dashboard metrics."""
        self.operation_id = operation_id
        self.progress = max(0.0, min(1.0, progress))  # Bound 0.0-1.0
        self.status = status
        self.start_time = start_time or datetime.utcnow()
        self.errors: List[str] = []
        self.alerts: List[Dict[str, Any]] = []


class RealTimeProgressDashboard:
    """
    Real-time progress dashboard for live operation monitoring.
    
    Provides sub-second update frequency for displaying operation
    progress, status, errors, and alerts to subscribers.
    """
    
    def __init__(self):
        """Initialize dashboard."""
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._subscribers: List[Any] = []
        self._history: List[DashboardUpdate] = []
        self._lock = RLock()
        logger.debug("RealTimeProgressDashboard initialized")
    
    def update_progress(
        self,
        operation_id: str,
        progress: float,
    ) -> None:
        """
        Update operation progress (0.0-1.0).
        
        Args:
            operation_id: Unique operation identifier
            progress: Progress value 0.0 to 1.0
        """
        # Bound progress to 0.0-1.0
        progress = max(0.0, min(1.0, progress))
        
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": "Idle",
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            
            self._metrics[operation_id]["progress"] = progress
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            
            # Record in history
            update = DashboardUpdate(
                operation_id=operation_id,
                update_type=DashboardUpdateType.PROGRESS,
                value=progress,
            )
            self._history.append(update)
        
        self._notify_subscribers(operation_id)
        logger.debug(f"Operation '{operation_id}' progress: {progress * 100:.1f}%")
    
    def update_status(
        self,
        operation_id: str,
        status: str,
    ) -> None:
        """
        Update operation status message.
        
        Args:
            operation_id: Unique operation identifier
            status: Status message
        """
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": status,
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            else:
                self._metrics[operation_id]["status"] = status
            
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            
            update = DashboardUpdate(
                operation_id=operation_id,
                update_type=DashboardUpdateType.STATUS,
                value=status,
            )
            self._history.append(update)
        
        self._notify_subscribers(operation_id)
        logger.debug(f"Operation '{operation_id}' status: {status}")
    
    def record_error(
        self,
        operation_id: str,
        error_message: str,
    ) -> None:
        """
        Record operation error.
        
        Args:
            operation_id: Unique operation identifier
            error_message: Error description
        """
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": "Error",
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            
            self._metrics[operation_id]["errors"].append(error_message)
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            
            update = DashboardUpdate(
                operation_id=operation_id,
                update_type=DashboardUpdateType.ERROR,
                value=error_message,
            )
            self._history.append(update)
        
        self._notify_subscribers(operation_id)
        logger.error(f"Operation '{operation_id}' error: {error_message}")
    
    def record_alert(
        self,
        operation_id: str,
        alert_message: str,
        severity: str = "info",
    ) -> None:
        """
        Record operation alert.
        
        Args:
            operation_id: Unique operation identifier
            alert_message: Alert description
            severity: Alert severity (info, warning, error)
        """
        with self._lock:
            if operation_id not in self._metrics:
                self._metrics[operation_id] = {
                    "progress": 0.0,
                    "status": "Idle",
                    "start_time": datetime.utcnow(),
                    "errors": [],
                    "alerts": [],
                }
            
            alert = {
                "message": alert_message,
                "severity": severity,
                "timestamp": datetime.utcnow(),
            }
            self._metrics[operation_id]["alerts"].append(alert)
            self._metrics[operation_id]["last_update"] = datetime.utcnow()
            
            update = DashboardUpdate(
                operation_id=operation_id,
                update_type=DashboardUpdateType.ALERT,
                value=alert,
            )
            self._history.append(update)
        
        self._notify_subscribers(operation_id)
        logger.warning(f"Operation '{operation_id}' alert ({severity}): {alert_message}")
    
    def subscribe(self, callback: Any) -> None:
        """
        Subscribe to dashboard updates.
        
        Args:
            callback: Function called on updates
        """
        with self._lock:
            self._subscribers.append(callback)
        logger.debug("New subscriber added to dashboard")
    
    def _notify_subscribers(self, operation_id: str) -> None:
        """Notify all subscribers of update."""
        with self._lock:
            subscribers = self._subscribers.copy()
        
        for subscriber in subscribers:
            try:
                subscriber(operation_id, self._metrics.get(operation_id, {}))
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    def get_current_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get current metrics for all operations.
        
        Returns:
            Dictionary of operation metrics
        """
        with self._lock:
            return self._metrics.copy()
    
    def get_history(self, max_entries: int = 1000) -> List[DashboardUpdate]:
        """
        Get update history.
        
        Args:
            max_entries: Maximum history entries to return
        
        Returns:
            List of dashboard updates
        """
        with self._lock:
            return self._history[-max_entries:].copy()


# ===== AC-NFR-004-03: Alert Management System =====



class ThresholdOperator(Enum):
    """Threshold comparison operators."""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL = "=="
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="


class Threshold:
    """
    Threshold definition with operator and value.
    """
    
    def __init__(
        self,
        operator: ThresholdOperator,
        value: float,
    ):
        """Initialize threshold."""
        self.operator = operator
        self.value = value
    
    def evaluate(self, current_value: float) -> bool:
        """
        Evaluate if current value breaches threshold.
        
        Args:
            current_value: Value to check
        
        Returns:
            True if threshold breached
        """
        if self.operator == ThresholdOperator.GREATER_THAN:
            return current_value > self.value
        elif self.operator == ThresholdOperator.LESS_THAN:
            return current_value < self.value
        elif self.operator == ThresholdOperator.EQUAL:
            return current_value == self.value
        elif self.operator == ThresholdOperator.GREATER_EQUAL:
            return current_value >= self.value
        elif self.operator == ThresholdOperator.LESS_EQUAL:
            return current_value <= self.value
        
        return False


class Alert:
    """
    Represents a single alert instance.
    """
    
    def __init__(
        self,
        alert_id: str,
        metric_name: str,
        severity: AlertSeverity,
        threshold: float,
        current_value: float,
        created_at: Optional[datetime] = None,
    ):
        """Initialize alert."""
        self.alert_id = alert_id
        self.metric_name = metric_name
        self.severity = severity
        self.threshold = threshold
        self.current_value = current_value
        self.created_at = created_at or datetime.utcnow()
        self.status = "active"  # active, acknowledged, resolved
        self.acknowledged_at: Optional[datetime] = None
        self.resolved_at: Optional[datetime] = None
    
    def acknowledge(self) -> None:
        """Acknowledge the alert."""
        self.status = "acknowledged"
        self.acknowledged_at = datetime.utcnow()
        logger.info(f"Alert {self.alert_id} acknowledged")
    
    def resolve(self) -> None:
        """Resolve the alert."""
        self.status = "resolved"
        self.resolved_at = datetime.utcnow()
        logger.info(f"Alert {self.alert_id} resolved")


class NotificationChannel:
    """
    Base class for notification channels.
    """
    
    def notify(self, alert: Alert) -> None:
        """
        Send notification for alert.
        
        Args:
            alert: Alert to notify about
        """
        raise NotImplementedError


class AlertManager:
    """
    Manages alert rules and triggering based on metrics.
    
    Supports threshold-based alerting with multiple notification
    channels and alert lifecycle management.
    """
    
    def __init__(self):
        """Initialize alert manager."""
        self._rules: Dict[str, List[Dict[str, Any]]] = {}
        self._active_alerts: List[Alert] = []
        self._alert_history: List[Alert] = []
        self._channels: Dict[str, NotificationChannel] = {}
        self._lock = RLock()
        logger.debug("AlertManager initialized")
    
    def register_rule(
        self,
        metric_name: str,
        threshold: Threshold,
        severity: AlertSeverity,
    ) -> None:
        """
        Register an alert rule for a metric.
        
        Args:
            metric_name: Name of metric to monitor
            threshold: Threshold definition
            severity: Alert severity level
        """
        with self._lock:
            if metric_name not in self._rules:
                self._rules[metric_name] = []
            
            self._rules[metric_name].append({
                "threshold": threshold,
                "severity": severity,
            })
        
        logger.info(f"Alert rule registered for {metric_name}")
    
    def check_metric(
        self,
        metric_name: str,
        value: float,
    ) -> List[Alert]:
        """
        Check metric against registered rules.
        
        Args:
            metric_name: Metric to check
            value: Current metric value
        
        Returns:
            List of triggered alerts
        """
        triggered = []
        
        with self._lock:
            if metric_name not in self._rules:
                return triggered
            
            for rule in self._rules[metric_name]:
                threshold = rule["threshold"]
                severity = rule["severity"]
                
                if threshold.evaluate(value):
                    # Check if alert already exists for this metric
                    existing = None
                    for alert in self._active_alerts:
                        if (alert.metric_name == metric_name and
                            alert.status == "active"):
                            existing = alert
                            break
                    
                    if not existing:
                        alert_id = f"alert_{metric_name}_{int(datetime.utcnow().timestamp() * 1000)}"
                        alert = Alert(
                            alert_id=alert_id,
                            metric_name=metric_name,
                            severity=severity,
                            threshold=threshold.value,
                            current_value=value,
                        )
                        self._active_alerts.append(alert)
                        self._alert_history.append(alert)
                        triggered.append(alert)
                        logger.warning(
                            f"Alert triggered for {metric_name}: "
                            f"{value} ({severity.value})"
                        )
        
        return triggered
    
    def add_channel(
        self,
        channel_name: str,
        channel: NotificationChannel,
    ) -> None:
        """
        Add a notification channel.
        
        Args:
            channel_name: Name of channel
            channel: Channel instance
        """
        with self._lock:
            self._channels[channel_name] = channel
        logger.debug(f"Notification channel added: {channel_name}")
    
    def notify_all_channels(self) -> None:
        """Notify all channels of active alerts."""
        with self._lock:
            alerts = self._active_alerts.copy()
            channels = self._channels.copy()
        
        for channel_name, channel in channels.items():
            try:
                for alert in alerts:
                    if alert.status == "active":
                        channel.notify(alert)
            except Exception as e:
                logger.error(
                    f"Error notifying channel {channel_name}: {e}"
                )
    
    def get_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get registered alert rules.
        
        Returns:
            Dictionary of metric rules
        """
        with self._lock:
            return self._rules.copy()
    
    def get_channels(self) -> Dict[str, NotificationChannel]:
        """
        Get registered notification channels.
        
        Returns:
            Dictionary of channels
        """
        with self._lock:
            return self._channels.copy()
    
    def get_alert_history(self) -> List[Alert]:
        """
        Get alert history.
        
        Returns:
            List of all alerts
        """
        with self._lock:
            return self._alert_history.copy()

