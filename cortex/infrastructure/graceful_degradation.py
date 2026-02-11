"""
Graceful Degradation Handler for CORTEX

Implements fallback strategies when components fail, ensuring
system continues to operate with reduced functionality rather than
complete failure.

AC-NFR-002-01: Graceful degradation on component failure
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DegradationLevel(Enum):
    """Levels of service degradation."""
    FULL = "FULL"           # Full functionality
    DEGRADED = "DEGRADED"   # Reduced functionality
    CRITICAL = "CRITICAL"   # Essential only
    UNAVAILABLE = "UNAVAILABLE"  # Service down


@dataclass
class FallbackResult:
    """Result of a fallback operation."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    degradation_level: DegradationLevel = DegradationLevel.FULL
    fallback_used: bool = False
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class FallbackStrategy:
    """Base class for fallback strategies."""

    def __init__(self, name: str, degradation_level: DegradationLevel):
        self.name = name
        self.degradation_level = degradation_level

    def execute(self, *args, **kwargs) -> FallbackResult:
        """Execute the fallback strategy."""
        raise NotImplementedError


class CacheFallbackStrategy(FallbackStrategy):
    """Use cached data as fallback when primary operation fails."""

    def __init__(self, cache: dict, degradation_level: DegradationLevel = DegradationLevel.DEGRADED):
        super().__init__("CacheFallback", degradation_level)
        self.cache = cache

    def execute(self, key: str) -> FallbackResult:
        """Retrieve cached value for key."""
        if key in self.cache:
            logger.warning(f"Using cached fallback for key: {key}")
            return FallbackResult(
                success=True,
                data=self.cache[key],
                degradation_level=self.degradation_level,
                fallback_used=True
            )
        return FallbackResult(
            success=False,
            error=f"No cached value for key: {key}",
            degradation_level=self.degradation_level
        )


class DefaultValueFallbackStrategy(FallbackStrategy):
    """Use default value as fallback."""

    def __init__(self, default_value: Any, degradation_level: DegradationLevel = DegradationLevel.DEGRADED):
        super().__init__("DefaultValueFallback", degradation_level)
        self.default_value = default_value

    def execute(self) -> FallbackResult:
        """Return default value."""
        logger.warning(f"Using default fallback value: {self.default_value}")
        return FallbackResult(
            success=True,
            data=self.default_value,
            degradation_level=self.degradation_level,
            fallback_used=True
        )


class GracefulDegradationHandler:
    """
    Manages graceful degradation by applying fallback strategies
    when components fail.
    """

    def __init__(self):
        self.fallback_strategies: dict[str, list[FallbackStrategy]] = {}
        self.current_degradation: DegradationLevel = DegradationLevel.FULL
        self.failure_count: dict[str, int] = {}
        self.failure_threshold: int = 3

    def register_fallback(self, component: str, strategy: FallbackStrategy):
        """Register a fallback strategy for a component."""
        if component not in self.fallback_strategies:
            self.fallback_strategies[component] = []
        self.fallback_strategies[component].append(strategy)
        logger.info(f"Registered fallback '{strategy.name}' for component '{component}'")

    def execute_with_fallback(
        self,
        component: str,
        primary_fn: Callable[..., T],
        *args,
        **kwargs
    ) -> FallbackResult:
        """
        Execute primary function with fallback strategies.

        If primary function fails, tries fallback strategies in order.
        """
        try:
            result = primary_fn(*args, **kwargs)
            self.failure_count[component] = 0
            self.current_degradation = DegradationLevel.FULL
            return FallbackResult(
                success=True,
                data=result,
                degradation_level=DegradationLevel.FULL,
                fallback_used=False
            )
        except Exception as e:
            logger.error(f"Primary operation failed for {component}: {str(e)}")
            self.failure_count[component] = self.failure_count.get(component, 0) + 1
            return self._try_fallbacks(component, *args, **kwargs)

    def _try_fallbacks(self, component: str, *args, **kwargs) -> FallbackResult:
        """Try fallback strategies in order."""
        if component not in self.fallback_strategies:
            logger.error(f"No fallback strategies registered for {component}")
            self.current_degradation = DegradationLevel.UNAVAILABLE
            return FallbackResult(
                success=False,
                error=f"No fallback for {component}",
                degradation_level=DegradationLevel.UNAVAILABLE
            )

        for strategy in self.fallback_strategies[component]:
            try:
                result = strategy.execute(*args, **kwargs)
                if result.success:
                    self.current_degradation = strategy.degradation_level
                    logger.info(f"Fallback succeeded using {strategy.name} for {component}")
                    return result
            except Exception as e:
                logger.warning(f"Fallback strategy {strategy.name} failed: {str(e)}")
                continue

        logger.error(f"All fallback strategies exhausted for {component}")
        self.current_degradation = DegradationLevel.UNAVAILABLE
        return FallbackResult(
            success=False,
            error=f"All fallbacks exhausted for {component}",
            degradation_level=DegradationLevel.UNAVAILABLE
        )

    def is_degraded(self) -> bool:
        """Check if system is operating in degraded mode."""
        return self.current_degradation != DegradationLevel.FULL

    def get_degradation_level(self) -> DegradationLevel:
        """Get current degradation level."""
        return self.current_degradation

    def reset(self):
        """Reset degradation state."""
        self.current_degradation = DegradationLevel.FULL
        self.failure_count.clear()
        logger.info("Graceful degradation handler reset")
