"""
Resilience models — shared data classes and exceptions.

Phase 103-f: extracted from resilience.py (1,876L) god-object.
AC_START: AC-P103F-RES-001
AC_COMPLETE: AC-P103F-RES-001 ✅
"""
from __future__ import annotations

import logging
from datetime import datetime
from threading import RLock
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ComponentFailure(Exception):
    """Exception raised when a component fails and cannot recover."""

    def __init__(
        self,
        component_name: str,
        reason: str,
        strategies_tried: int = 0,
        last_exception: Optional[Exception] = None,
    ) -> None:
        """Initialize ComponentFailure exception."""
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


class DegradedResponse(Generic[T]):
    """Wraps a response with degradation metadata."""

    def __init__(
        self,
        data: T,
        degradation_reason: str,
        mode: str,
        original_request_id: Optional[str] = None,
    ) -> None:
        """Initialize degraded response wrapper."""
        self._data: T = data
        self._degradation_reason: str = degradation_reason
        self._mode: str = mode
        self._original_request_id: Optional[str] = original_request_id
        self._created_at: datetime = datetime.utcnow()

    def get_data(self) -> T:
        """Get wrapped response data."""
        return self._data

    def is_degraded(self) -> bool:
        """Check if response is from degraded operation."""
        return self._mode != "primary"

    def get_metadata(self) -> Dict[str, Any]:
        """Get degradation metadata."""
        return {
            "degradation_reason": self._degradation_reason,
            "mode": self._mode,
            "original_request_id": self._original_request_id,
            "created_at": self._created_at.isoformat(),
        }


class StrategyExecutionException(Exception):
    """Raised when a strategy execution fails after all retries."""

    def __init__(self, message: str, last_exception: Optional[Exception] = None) -> None:
        """Initialize strategy execution exception."""
        self.last_exception: Optional[Exception] = last_exception
        super().__init__(message)


class FallbackStrategy:  # CORE-035-scoped — domain-specific fallback strategy model
    """Represents a single fallback strategy with retry capability."""

    def __init__(
        self,
        callable: Callable[..., Any],
        priority: int = 0,
        max_retries: int = 1,
    ) -> None:
        """Initialize fallback strategy."""
        self.callable: Callable[..., Any] = callable
        self.priority: int = priority
        self.max_retries: int = max_retries
        self._execution_count: int = 0
        self._last_exception: Optional[Exception] = None

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute this strategy with retries."""
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                self._execution_count += 1
                result: Any = self.callable(*args, **kwargs)
                logger.debug(f"Strategy {self.priority} succeeded on attempt {attempt + 1}")
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


class PartialFunctionalityMode:
    """Manages system operation with reduced functionality."""

    def __init__(self) -> None:
        """Initialize with all features enabled by default."""
        self._features: Dict[str, bool] = {}
        self._feature_reasons: Dict[str, str] = {}
        self._lock: RLock = RLock()

    def disable_feature(self, feature_name: str, reason: str) -> None:
        """Disable a feature."""
        with self._lock:
            self._features[feature_name] = False
            self._feature_reasons[feature_name] = reason
            logger.warning(f"Feature disabled: {feature_name} - {reason}")

    def enable_feature(self, feature_name: str) -> None:
        """Re-enable a previously disabled feature."""
        with self._lock:
            self._features[feature_name] = True
            self._feature_reasons.pop(feature_name, None)
            logger.info(f"Feature enabled: {feature_name}")

    def is_feature_available(self, feature_name: str) -> bool:
        """Check if feature is available."""
        with self._lock:
            return self._features.get(feature_name, True)

    def get_available_features(self) -> List[str]:
        """Get list of currently available features."""
        with self._lock:
            return [name for name, available in self._features.items() if available]

    def get_status(self) -> Dict[str, Any]:
        """Get status of all features."""
        with self._lock:
            return {name: self._features.get(name, True) for name in self._features.keys()}
