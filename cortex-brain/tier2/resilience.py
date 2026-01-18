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
        try:
            result: Any = component["primary"](*args, **kwargs)
            
            with self._lock:
                state["current_mode"] = "primary"
                state["is_degraded"] = False
                state["failure_count"] = 0
            
            logger.debug(f"Component '{component_name}' executed in primary mode")
            return result, "primary"
        
        except Exception as primary_exc:
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
