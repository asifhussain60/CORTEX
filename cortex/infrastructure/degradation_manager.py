"""
Graceful Degradation Framework.

AC-INFRA-001-05: Provides fallback strategies for partial failures,
allowing system to continue with reduced functionality through
FULL → PARTIAL → MINIMAL degradation levels.
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional


class DegradationLevel(Enum):
    """System degradation levels."""
    FULL = 3  # Full functionality
    PARTIAL = 2  # Read-only or cached operations
    MINIMAL = 1  # Default values only


@dataclass
class DegradationConfig:
    """Configuration for degradation manager."""
    health_check_interval_seconds: float = 30.0
    recovery_threshold: int = 3  # Consecutive successes to recover
    degradation_threshold: int = 2  # Consecutive failures to degrade
    cache_staleness_warning_seconds: float = 300.0  # 5 minutes


@dataclass
class ServiceHealth:
    """Health status for a service."""
    name: str
    consecutive_successes: int = 0
    consecutive_failures: int = 0
    last_check: float = field(default_factory=time.time)
    is_healthy: bool = True


class FallbackStrategy:
    """Encapsulates fallback logic."""

    def __init__(
        self,
        fresh_fn: Callable[[], Any],
        cached_value: Optional[Any] = None,
        default_value: Optional[Any] = None,
        cache_timestamp: Optional[float] = None,
    ):
        """
        Initialize fallback strategy.

        Args:
            fresh_fn: Function to fetch fresh data
            cached_value: Cached fallback value
            default_value: Default fallback value
            cache_timestamp: When cache was created
        """
        self.fresh_fn = fresh_fn
        self.cached_value = cached_value
        self.default_value = default_value
        self.cache_timestamp = cache_timestamp or time.time()


class DegradationManager:
    """
    Manages graceful degradation with automatic fallback.

    Provides three-level degradation:
    - FULL: Fresh data from services
    - PARTIAL: Cached data (read-only)
    - MINIMAL: Default/safe values

    Thread-safe for concurrent access.
    """

    def __init__(self, config: Optional[DegradationConfig] = None):
        """
        Initialize degradation manager.

        Args:
            config: Degradation configuration
        """
        self.config = config or DegradationConfig()
        self._current_level = DegradationLevel.FULL
        self._lock = threading.RLock()
        self._services: Dict[str, ServiceHealth] = {}
        self._manual_override = False

        # Metrics
        self._total_degradations = 0
        self._total_recoveries = 0
        self._degradation_start_time: Optional[float] = None
        self._total_time_degraded = 0.0

    @property
    def current_level(self) -> DegradationLevel:
        """Get current degradation level."""
        with self._lock:
            return self._current_level

    def record_success(self, service_name: str) -> None:
        """
        Record successful service operation.

        Args:
            service_name: Name of service
        """
        with self._lock:
            service = self._get_or_create_service(service_name)
            service.consecutive_successes += 1
            service.consecutive_failures = 0
            service.last_check = time.time()
            service.is_healthy = True

            # Check for recovery
            if not self._manual_override:
                self._check_recovery()

    def record_failure(self, service_name: str) -> None:
        """
        Record failed service operation.

        Args:
            service_name: Name of service
        """
        with self._lock:
            service = self._get_or_create_service(service_name)
            service.consecutive_failures += 1
            service.consecutive_successes = 0
            service.last_check = time.time()
            service.is_healthy = False

            # Check for degradation
            if not self._manual_override:
                self._check_degradation()

    def execute_with_fallback(
        self,
        fresh_fn: Callable[[], Any],
        cached_value: Optional[Any] = None,
        default_value: Optional[Any] = None,
        cache_timestamp: Optional[float] = None,
        raise_on_all_failed: bool = False,
    ) -> Any:
        """
        Execute operation with automatic fallback based on degradation level.

        Args:
            fresh_fn: Function to fetch fresh data
            cached_value: Cached fallback value
            default_value: Default fallback value
            cache_timestamp: When cache was created
            raise_on_all_failed: Raise exception if all fallbacks fail

        Returns:
            Result from appropriate source based on degradation level

        Raises:
            Exception: If raise_on_all_failed=True and all sources fail
        """
        level = self.current_level

        # Try fresh data at FULL level
        if level == DegradationLevel.FULL:
            try:
                return fresh_fn()
            except Exception:
                # Fall through to cached/default
                pass

        # Try cached data at PARTIAL level
        if level in [DegradationLevel.FULL, DegradationLevel.PARTIAL]:
            if cached_value is not None:
                # Check staleness
                if cache_timestamp:
                    age = time.time() - cache_timestamp
                    if age > self.config.cache_staleness_warning_seconds:
                        # Log warning but still serve
                        pass
                return cached_value

        # Try default value at MINIMAL level
        if default_value is not None:
            return default_value

        # All fallbacks exhausted
        if raise_on_all_failed:
            raise RuntimeError("All fallback strategies exhausted")

        return None

    def set_level(self, level: DegradationLevel, manual: bool = False) -> None:
        """
        Manually set degradation level.

        Args:
            level: Target degradation level
            manual: Whether this is a manual override
        """
        with self._lock:
            old_level = self._current_level
            self._current_level = level
            self._manual_override = manual

            if level.value < old_level.value:
                self._total_degradations += 1
                if self._degradation_start_time is None:
                    self._degradation_start_time = time.time()
            elif level.value > old_level.value:
                self._total_recoveries += 1
                if level == DegradationLevel.FULL and self._degradation_start_time:
                    self._total_time_degraded += time.time() - self._degradation_start_time
                    self._degradation_start_time = None

    def get_health(self) -> Dict[str, Any]:
        """
        Get current health status.

        Returns:
            Health status including level and services
        """
        with self._lock:
            return {
                "level": self._current_level.value,
                "status": "healthy" if self._current_level == DegradationLevel.FULL else "degraded",
                "manual_override": self._manual_override,
                "services": {
                    name: {
                        "healthy": svc.is_healthy,
                        "consecutive_successes": svc.consecutive_successes,
                        "consecutive_failures": svc.consecutive_failures,
                        "last_check": svc.last_check,
                    }
                    for name, svc in self._services.items()
                }
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get degradation metrics.

        Returns:
            Metrics including degradation counts and time
        """
        with self._lock:
            time_degraded = self._total_time_degraded
            if self._degradation_start_time:
                time_degraded += time.time() - self._degradation_start_time

            return {
                "current_level": self._current_level.value,
                "total_degradations": self._total_degradations,
                "total_recoveries": self._total_recoveries,
                "time_degraded_seconds": time_degraded,
                "services_count": len(self._services),
            }

    def _get_or_create_service(self, name: str) -> ServiceHealth:
        """Get or create service health tracker."""
        if name not in self._services:
            self._services[name] = ServiceHealth(name=name)
        return self._services[name]

    def _check_degradation(self) -> None:
        """Check if system should degrade."""
        # Count unhealthy services
        unhealthy_count = sum(
            1 for svc in self._services.values()
            if svc.consecutive_failures >= self.config.degradation_threshold
        )

        if unhealthy_count == 0:
            return

        # Degrade based on severity - single service can degrade through all levels
        old_level = self._current_level

        # For single service, degrade progressively based on failure count
        if len(self._services) == 1:
            service = list(self._services.values())[0]
            if service.consecutive_failures >= 4 and self._current_level != DegradationLevel.MINIMAL:
                self.set_level(DegradationLevel.MINIMAL)
            elif service.consecutive_failures >= 2 and self._current_level == DegradationLevel.FULL:
                self.set_level(DegradationLevel.PARTIAL)
        else:
            # Multiple services: degrade based on count
            if unhealthy_count >= 3 and self._current_level != DegradationLevel.MINIMAL:
                self.set_level(DegradationLevel.MINIMAL)
            elif unhealthy_count >= 1 and self._current_level == DegradationLevel.FULL:
                self.set_level(DegradationLevel.PARTIAL)

    def _check_recovery(self) -> None:
        """Check if system can recover."""
        # Count healthy services
        healthy_count = sum(
            1 for svc in self._services.values()
            if svc.consecutive_successes >= self.config.recovery_threshold
        )

        if healthy_count == 0:
            return

        # Recover gradually
        total_services = len(self._services)
        if total_services == 0:
            return

        health_ratio = healthy_count / total_services

        if health_ratio >= 0.8 and self._current_level != DegradationLevel.FULL:
            self.set_level(DegradationLevel.FULL)
        elif health_ratio >= 0.5 and self._current_level == DegradationLevel.MINIMAL:
            self.set_level(DegradationLevel.PARTIAL)
