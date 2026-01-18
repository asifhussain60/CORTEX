"""
Health monitoring for CORTEX system components.

Provides health checks for databases, caches, APIs, and other critical
components with status aggregation and caching.

Attributes:
    DEFAULT_CACHE_TTL: Default cache TTL in seconds (30)
    DEFAULT_CHECK_TIMEOUT: Default check timeout in seconds (5)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime, timedelta
from enum import Enum
import logging
import time


class HealthStatusLevel(Enum):
    """Health status levels.
    
    Attributes:
        HEALTHY: All checks passing
        DEGRADED: Some checks failing
        UNHEALTHY: Critical checks failing
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a single health check.
    
    Attributes:
        name: Check name
        passed: Whether check passed
        duration_ms: Execution time in milliseconds
        message: Optional message
        timestamp: When check was performed
    """
    name: str
    passed: bool
    duration_ms: float
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with check result
        """
        return {
            "name": self.name,
            "passed": self.passed,
            "duration_ms": self.duration_ms,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HealthStatus:
    """Overall system health status.
    
    Attributes:
        status: Overall status (healthy, degraded, unhealthy)
        healthy: Whether system is healthy
        timestamp: When status was calculated
        checks: Individual check results
    """
    status: HealthStatusLevel
    healthy: bool
    timestamp: datetime
    checks: Dict[str, HealthCheckResult] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.
        
        Returns:
            Dictionary with health status
        """
        return {
            "status": self.status.value,
            "healthy": self.healthy,
            "timestamp": self.timestamp.isoformat(),
            "checks": {
                name: check.to_dict()
                for name, check in self.checks.items()
            },
        }


class HealthMonitor:
    """Monitors health of CORTEX system components.
    
    Executes periodic health checks, aggregates results, and provides
    status reporting with caching.
    
    Attributes:
        checks: Dictionary of registered health checks
        cache_ttl_seconds: How long to cache results
        check_timeout_seconds: Timeout for individual checks
    """
    
    def __init__(
        self,
        cache_ttl_seconds: int = 30,
        check_timeout_seconds: int = 5,
    ) -> None:
        """Initialize health monitor.
        
        Args:
            cache_ttl_seconds: Cache duration in seconds
            check_timeout_seconds: Check timeout in seconds
        """
        self.checks: Dict[str, Callable[[], bool]] = {}
        self.cache_ttl_seconds = cache_ttl_seconds
        self.check_timeout_seconds = check_timeout_seconds
        
        self._cached_status: Optional[HealthStatus] = None
        self._cache_timestamp: Optional[datetime] = None
        self._logger: logging.Logger = logging.getLogger(__name__)

    def register_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a health check function.
        
        Args:
            name: Check name
            check_func: Callable that returns True if healthy
        """
        self.checks[name] = check_func
        self._logger.info(f"Registered health check: {name}")

    def deregister_check(self, name: str) -> None:
        """Deregister a health check.
        
        Args:
            name: Check name to remove
        """
        if name in self.checks:
            del self.checks[name]
            self._logger.info(f"Deregistered health check: {name}")

    def get_registered_checks(self) -> List[str]:
        """Get list of registered check names.
        
        Returns:
            List of check names
        """
        return list(self.checks.keys())

    def get_status(self) -> HealthStatus:
        """Get current system health status.
        
        Returns:
            HealthStatus with current status
        """
        # Check cache
        if self._cached_status is not None and self._cache_timestamp is not None:
            age = (datetime.utcnow() - self._cache_timestamp).total_seconds()
            if age < self.cache_ttl_seconds:
                return self._cached_status
        
        # Run checks
        check_results: Dict[str, HealthCheckResult] = {}
        failed_count = 0
        
        for name, check_func in self.checks.items():
            result = self._run_check(name, check_func)
            check_results[name] = result
            
            if not result.passed:
                failed_count += 1
        
        # Determine overall status
        if failed_count == 0:
            overall_status = HealthStatusLevel.HEALTHY
            healthy = True
        elif failed_count < len(self.checks) / 2:
            overall_status = HealthStatusLevel.DEGRADED
            healthy = False
        else:
            overall_status = HealthStatusLevel.UNHEALTHY
            healthy = False
        
        # Create status object
        status = HealthStatus(
            status=overall_status,
            healthy=healthy,
            timestamp=datetime.utcnow(),
            checks=check_results,
        )
        
        # Cache result
        self._cached_status = status
        self._cache_timestamp = datetime.utcnow()
        
        return status

    def _run_check(self, name: str, check_func: Callable[[], bool]) -> HealthCheckResult:
        """Run a single health check.
        
        Args:
            name: Check name
            check_func: Check function
            
        Returns:
            HealthCheckResult with check outcome
        """
        start_time = time.time()
        
        try:
            # Execute check with timeout
            result = self._execute_with_timeout(check_func, self.check_timeout_seconds)
            duration_ms = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                name=name,
                passed=result,
                duration_ms=duration_ms,
                message="OK" if result else "Check failed",
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            self._logger.error(f"Health check {name} failed: {e}")
            
            return HealthCheckResult(
                name=name,
                passed=False,
                duration_ms=duration_ms,
                message=f"Exception: {str(e)}",
            )

    @staticmethod
    def _execute_with_timeout(
        func: Callable[[], bool],
        timeout_seconds: int,
    ) -> bool:
        """Execute function with timeout.
        
        Args:
            func: Callable to execute
            timeout_seconds: Timeout in seconds
            
        Returns:
            Function result
        """
        # Simple implementation - in production, use multiprocessing/threading
        import signal
        
        def timeout_handler(signum: int, frame: Any) -> None:
            raise TimeoutError(f"Check exceeded {timeout_seconds}s timeout")
        
        # Set signal handler (Unix-like systems only)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                return func()
            finally:
                signal.alarm(0)
        except (AttributeError, ValueError):
            # signal.alarm not available on Windows
            return func()

    def get_check_result(self, check_name: str) -> Optional[HealthCheckResult]:
        """Get last result for a specific check.
        
        Args:
            check_name: Name of check
            
        Returns:
            HealthCheckResult or None if not found
        """
        status = self.get_status()
        return status.checks.get(check_name)

    def clear_cache(self) -> None:
        """Clear cached status."""
        self._cached_status = None
        self._cache_timestamp = None

    def get_stats(self) -> Dict[str, Any]:
        """Get health monitor statistics.
        
        Returns:
            Dictionary with health stats
        """
        status = self.get_status()
        
        passed_count = sum(1 for c in status.checks.values() if c.passed)
        failed_count = len(status.checks) - passed_count
        
        return {
            "overall_status": status.status.value,
            "healthy": status.healthy,
            "total_checks": len(status.checks),
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "check_details": {
                name: result.to_dict()
                for name, result in status.checks.items()
            },
        }
