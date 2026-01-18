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
]
