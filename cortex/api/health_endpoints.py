"""
Comprehensive health and readiness checks endpoints (AC-OPS-004-04).

Implements liveness checks, readiness checks, component health verification,
and detailed health status endpoints for production operations.

Classes:
    HealthStatus: Enumeration of health status values.
    ComponentHealth: Health status of individual components.
    HealthCheckResponse: Complete health check response.
    HealthCheckConfig: Configuration for health checks.
    HealthChecksCollector: Main health checks coordinator.
"""

import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

# CONSOLIDATED: Import from cortex.models.canonical_enums
from cortex.models.canonical_enums import HealthStatus


@dataclass
class ComponentHealth:
    """Health status of individual component.

    Args:
        status: Current health status.
        latency_ms: Response time in milliseconds.
        reason: Optional reason for degraded/unhealthy status.
        error_message: Detailed error message if unhealthy.
        last_check_time: Timestamp of last check.
    """

    status: HealthStatus
    latency_ms: Optional[float] = None
    reason: Optional[str] = None
    error_message: Optional[str] = None
    last_check_time: float = field(default_factory=time.time)


@dataclass
class HealthCheckResponse:
    """Complete health check response.

    Args:
        status: Overall system health status.
        timestamp: ISO-8601 timestamp of check.
        version: Service version.
        uptime_seconds: Service uptime in seconds.
        components: Dictionary of component health statuses.
    """

    status: HealthStatus
    timestamp: str
    version: str
    uptime_seconds: int
    components: Dict[str, ComponentHealth] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for JSON serialization.

        Returns:
            Dictionary representation of health check response.
        """
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "version": self.version,
            "uptime_seconds": self.uptime_seconds,
            "components": {
                name: {
                    "status": health.status.value,
                    "latency_ms": health.latency_ms,
                    "reason": health.reason,
                }
                for name, health in self.components.items()
            },
        }


@dataclass
class HealthCheckConfig:
    """Configuration for health checks.

    Args:
        service_name: Name of the service.
        version: Service version.
        component_timeout_seconds: Timeout for individual component checks.
        retry_failed_checks: Whether to retry failed checks.
        retry_count: Number of retries for failed checks.
    """

    service_name: str
    version: str
    component_timeout_seconds: float = 5.0
    retry_failed_checks: bool = True
    retry_count: int = 3


class HealthChecksCollector:
    """Main coordinator for health checks.

    Manages liveness checks, readiness checks, component health verification,
    and detailed health status responses.
    """

    def __init__(self, config: HealthCheckConfig) -> None:
        """Initialize health checks collector.

        Args:
            config: Health check configuration.
        """
        self.config = config
        self._component_checks: Dict[str, Callable[[], Any]] = {}
        self._start_time = time.time()
        self._lock = threading.Lock()
        self._component_results_cache: Dict[str, ComponentHealth] = {}
        self._cache_expiry: Dict[str, float] = {}

    def register_component_check(
        self,
        name: str,
        check_fn: Callable[[], Any],
    ) -> None:
        """Register a component health check function.

        Args:
            name: Component name.
            check_fn: Function that returns ComponentHealth or HealthStatus.
        """
        with self._lock:
            self._component_checks[name] = check_fn

    def get_component_checks(self) -> Dict[str, Callable[[], Any]]:
        """Get all registered component checks.

        Returns:
            Dictionary of component_name -> check_function.
        """
        with self._lock:
            return dict(self._component_checks)

    def liveness_check(self) -> HealthCheckResponse:
        """Check if service is alive (process running).

        This is a quick check that should always respond in <100ms.

        Returns:
            HealthCheckResponse indicating if process is alive.
        """
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow().isoformat(),
            version=self.config.version,
            uptime_seconds=int(time.time() - self._start_time),
        )
        return response

    def readiness_check(self) -> HealthCheckResponse:
        """Check if service is ready to accept traffic.

        Returns:
            HealthCheckResponse indicating readiness.
        """
        # Quick readiness check - no component details
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow().isoformat(),
            version=self.config.version,
            uptime_seconds=int(time.time() - self._start_time),
        )
        return response

    def deep_health_check(self) -> HealthCheckResponse:
        """Perform comprehensive health check including all components.

        This includes:
        - Database connectivity and latency
        - Cache connectivity and latency
        - Governance system health
        - Other component-level checks

        Returns:
            HealthCheckResponse with detailed component status.
        """
        components = {}
        overall_status = HealthStatus.HEALTHY

        with self._lock:
            component_checks = dict(self._component_checks)

        for name, check_fn in component_checks.items():
            try:
                result = self._run_component_check_with_retry(name, check_fn)

                if isinstance(result, ComponentHealth):
                    components[name] = result
                else:
                    # Assume HealthStatus was returned
                    components[name] = ComponentHealth(status=result, latency_ms=None)

                # Update overall status
                if components[name].status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif (
                    components[name].status == HealthStatus.DEGRADED
                    and overall_status != HealthStatus.UNHEALTHY
                ):
                    overall_status = HealthStatus.DEGRADED
            except Exception as e:
                # Component check failed
                components[name] = ComponentHealth(
                    status=HealthStatus.UNHEALTHY,
                    reason="Check failed",
                    error_message=str(e),
                )
                overall_status = HealthStatus.UNHEALTHY

        response = HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            version=self.config.version,
            uptime_seconds=int(time.time() - self._start_time),
            components=components,
        )
        return response

    def _run_component_check_with_retry(
        self,
        name: str,
        check_fn: Callable[[], Any],
    ) -> Any:
        """Run component check with retry logic.

        Args:
            name: Component name.
            check_fn: Check function to run.

        Returns:
            Result from check function.
        """
        if not self.config.retry_failed_checks:
            return check_fn()

        for attempt in range(self.config.retry_count):
            try:
                result = check_fn()
                if isinstance(result, ComponentHealth):
                    if result.status == HealthStatus.HEALTHY:
                        return result
                else:
                    return result
            except Exception:
                if attempt == self.config.retry_count - 1:
                    raise
                time.sleep(0.01)  # Brief delay before retry

        return check_fn()

    def get_http_status_code(self, response: HealthCheckResponse) -> int:
        """Get appropriate HTTP status code for health check response.

        Args:
            response: HealthCheckResponse.

        Returns:
            HTTP status code (200 for healthy, 503 for degraded/unhealthy).
        """
        if response.status == HealthStatus.HEALTHY:
            return 200
        else:
            return 503

    def get_uptime_seconds(self) -> int:
        """Get service uptime in seconds.

        Returns:
            Uptime in seconds since service start.
        """
        return int(time.time() - self._start_time)
