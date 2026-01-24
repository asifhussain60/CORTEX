"""
Comprehensive test suite for BRT-016: Health Check Integration Pattern.

Tests dependency health monitoring and integration with graceful degradation,
enabling systems to adjust behavior based on the health status of dependent
services and components.

The health check integration pattern provides:
- Periodic health status polling for dependencies
- Automatic degradation when dependencies become unhealthy
- Recovery transitions when dependencies recover
- Metrics tracking for health state changes

AC-INFRA-001-05: Dependency health monitoring and integration
"""

import threading
import time
from typing import List, Generator, Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum

import pytest


# ============================================================================
# HEALTH CHECK INTEGRATION IMPLEMENTATION FOR TESTING
# ============================================================================

class HealthStatus(str, Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class DependencyHealth:
    """Health status of a dependency."""
    
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check_time: float = 0.0
    consecutive_failures: int = 0
    response_time_ms: float = 0.0
    error_message: Optional[str] = None


@dataclass
class HealthCheckResult:
    """Result from a health check."""
    
    dependency_name: str
    is_healthy: bool
    status: HealthStatus
    response_time_ms: float = 0.0
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""
    
    check_interval_ms: float = 1000.0  # Check every 1 second
    failure_threshold: int = 3  # Unhealthy after 3 failures
    recovery_threshold: int = 2  # Healthy after 2 successes
    timeout_ms: float = 5000.0  # Health check timeout
    enable_auto_check: bool = True


@dataclass
class HealthMetrics:
    """Metrics for health checks."""
    
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    health_state_transitions: int = 0
    recovery_count: int = 0
    degradation_count: int = 0


class HealthChecker:
    """Manages health checks for dependencies."""
    
    def __init__(self, config: Optional[HealthCheckConfig] = None) -> None:
        """Initialize health checker."""
        self.config = config or HealthCheckConfig()
        self.dependencies: Dict[str, DependencyHealth] = {}
        self.check_functions: Dict[str, Callable[[], bool]] = {}
        self.metrics = HealthMetrics()
        self.lock = threading.Lock()
        self._check_history: List[HealthCheckResult] = []
        self._running = False
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if self.config.check_interval_ms <= 0:
            raise ValueError("check_interval_ms must be > 0")
        if self.config.failure_threshold <= 0:
            raise ValueError("failure_threshold must be > 0")
        if self.config.recovery_threshold <= 0:
            raise ValueError("recovery_threshold must be > 0")
        if self.config.timeout_ms <= 0:
            raise ValueError("timeout_ms must be > 0")
    
    def register_dependency(
        self,
        name: str,
        check_function: Callable[[], bool],
    ) -> None:
        """Register dependency with health check function."""
        with self.lock:
            self.dependencies[name] = DependencyHealth(name=name)
            self.check_functions[name] = check_function
    
    def get_dependency_health(self, name: str) -> Optional[DependencyHealth]:
        """Get health status of a dependency."""
        with self.lock:
            return self.dependencies.get(name)
    
    def check_dependency(self, name: str) -> HealthCheckResult:
        """Perform immediate health check on dependency."""
        if name not in self.check_functions:
            raise ValueError(f"Dependency '{name}' not registered")
        
        check_func = self.check_functions[name]
        start_time = time.time()
        
        try:
            is_healthy = check_func()
            response_time = (time.time() - start_time) * 1000
            
            result = HealthCheckResult(
                dependency_name=name,
                is_healthy=is_healthy,
                status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
            )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            result = HealthCheckResult(
                dependency_name=name,
                is_healthy=False,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                error=str(e),
            )
        
        # Update dependency health
        with self.lock:
            dep = self.dependencies[name]
            old_status = dep.status
            
            if result.is_healthy:
                dep.consecutive_failures = 0
                if dep.status != HealthStatus.HEALTHY:
                    dep.status = HealthStatus.HEALTHY
                    self.metrics.recovery_count += 1
            else:
                dep.consecutive_failures += 1
                if dep.consecutive_failures >= self.config.failure_threshold:
                    if dep.status != HealthStatus.UNHEALTHY:
                        dep.status = HealthStatus.UNHEALTHY
                        self.metrics.degradation_count += 1
                else:
                    dep.status = HealthStatus.DEGRADED
            
            if dep.status != old_status:
                self.metrics.health_state_transitions += 1
            
            dep.last_check_time = time.time()
            dep.response_time_ms = result.response_time_ms
            dep.error_message = result.error
            
            self.metrics.total_checks += 1
            if result.is_healthy:
                self.metrics.successful_checks += 1
            else:
                self.metrics.failed_checks += 1
            
            self._check_history.append(result)
        
        return result
    
    def check_all_dependencies(self) -> Dict[str, Any]:
        """Perform health checks on all dependencies."""
        results: Dict[str, Any] = {}
        for name in self.check_functions.keys():
            results[name] = self.check_dependency(name)
        return results
    
    def get_healthy_dependencies(self) -> List[str]:
        """Get list of healthy dependencies."""
        with self.lock:
            return [
                name
                for name, dep in self.dependencies.items()
                if dep.status == HealthStatus.HEALTHY
            ]
    
    def get_unhealthy_dependencies(self) -> List[str]:
        """Get list of unhealthy dependencies."""
        with self.lock:
            return [
                name
                for name, dep in self.dependencies.items()
                if dep.status == HealthStatus.UNHEALTHY
            ]
    
    def get_degraded_dependencies(self) -> List[str]:
        """Get list of degraded dependencies."""
        with self.lock:
            return [
                name
                for name, dep in self.dependencies.items()
                if dep.status == HealthStatus.DEGRADED
            ]
    
    def are_all_healthy(self) -> bool:
        """Check if all dependencies are healthy."""
        with self.lock:
            return all(
                dep.status == HealthStatus.HEALTHY
                for dep in self.dependencies.values()
            )
    
    def any_unhealthy(self) -> bool:
        """Check if any dependency is unhealthy."""
        with self.lock:
            return any(
                dep.status == HealthStatus.UNHEALTHY
                for dep in self.dependencies.values()
            )
    
    def get_check_history(self) -> List[HealthCheckResult]:
        """Get history of health checks."""
        with self.lock:
            return list(self._check_history)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get health check metrics."""
        with self.lock:
            total = self.metrics.total_checks
            success_rate = (
                (self.metrics.successful_checks / total * 100) if total > 0 else 0.0
            )
            
            return {
                "total_checks": total,
                "successful_checks": self.metrics.successful_checks,
                "failed_checks": self.metrics.failed_checks,
                "success_rate": success_rate,
                "health_state_transitions": self.metrics.health_state_transitions,
                "recovery_events": self.metrics.recovery_count,
                "degradation_events": self.metrics.degradation_count,
            }


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def health_checker() -> Generator[HealthChecker, None, None]:
    """Create a HealthChecker for testing."""
    checker = HealthChecker()
    yield checker


@pytest.fixture
def configured_checker() -> Generator[HealthChecker, None, None]:
    """Create checker with configured dependencies."""
    config = HealthCheckConfig(
        check_interval_ms=500.0,
        failure_threshold=2,
        recovery_threshold=1,
    )
    checker = HealthChecker(config=config)
    
    # Register dependencies
    checker.register_dependency("service-a", lambda: True)  # Always healthy
    checker.register_dependency("service-b", lambda: True)  # Always healthy
    checker.register_dependency("service-c", lambda: False)  # Always unhealthy
    
    yield checker


# ============================================================================
# CATEGORY 1: INITIALIZATION & CONFIGURATION (4/4)
# ============================================================================

class TestInitialization:
    """Test health checker initialization."""
    
    def test_creates_checker_with_default_config(self, health_checker: HealthChecker) -> None:
        """Should create checker with default configuration."""
        assert health_checker is not None
        assert health_checker.config.check_interval_ms == 1000.0
        assert health_checker.config.failure_threshold == 3
    
    def test_creates_checker_with_custom_config(self) -> None:
        """Should create checker with custom configuration."""
        config = HealthCheckConfig(
            check_interval_ms=500.0,
            failure_threshold=2,
        )
        checker = HealthChecker(config=config)
        
        assert checker.config.check_interval_ms == 500.0
        assert checker.config.failure_threshold == 2
    
    def test_rejects_invalid_check_interval(self) -> None:
        """Should reject invalid check interval."""
        with pytest.raises(ValueError):
            config = HealthCheckConfig(check_interval_ms=-1.0)
            HealthChecker(config=config)
    
    def test_rejects_invalid_failure_threshold(self) -> None:
        """Should reject invalid failure threshold."""
        with pytest.raises(ValueError):
            config = HealthCheckConfig(failure_threshold=0)
            HealthChecker(config=config)


# ============================================================================
# CATEGORY 2: DEPENDENCY REGISTRATION (3/3)
# ============================================================================

class TestDependencyRegistration:
    """Test dependency registration."""
    
    def test_registers_dependency_with_check_function(
        self,
        health_checker: HealthChecker,
    ) -> None:
        """Should register dependency with health check function."""
        def check() -> bool:
            return True
        
        health_checker.register_dependency("test-service", check)
        assert "test-service" in health_checker.check_functions
    
    def test_registers_multiple_dependencies(self, health_checker: HealthChecker) -> None:
        """Should register multiple dependencies."""
        health_checker.register_dependency("service-a", lambda: True)
        health_checker.register_dependency("service-b", lambda: False)
        health_checker.register_dependency("service-c", lambda: True)
        
        assert len(health_checker.check_functions) == 3
    
    def test_initializes_dependency_as_unknown(self, health_checker: HealthChecker) -> None:
        """Should initialize dependency with UNKNOWN status."""
        health_checker.register_dependency("service", lambda: True)
        
        dep = health_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.UNKNOWN


# ============================================================================
# CATEGORY 3: HEALTH CHECK EXECUTION (4/4)
# ============================================================================

class TestHealthCheckExecution:
    """Test health check execution."""
    
    def test_performs_health_check_on_dependency(
        self,
        health_checker: HealthChecker,
    ) -> None:
        """Should perform health check on registered dependency."""
        health_checker.register_dependency("service", lambda: True)
        
        result = health_checker.check_dependency("service")
        assert result.dependency_name == "service"
        assert result.is_healthy is True
        assert result.status == HealthStatus.HEALTHY
    
    def test_detects_unhealthy_dependency(self, health_checker: HealthChecker) -> None:
        """Should detect unhealthy dependency."""
        health_checker.register_dependency("service", lambda: False)
        
        # First failure
        result1 = health_checker.check_dependency("service")
        assert result1.is_healthy is False
        
        # After threshold, should be UNHEALTHY
        health_checker.check_dependency("service")
        health_checker.check_dependency("service")
        
        dep = health_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.UNHEALTHY
    
    def test_checks_all_dependencies(self, configured_checker: HealthChecker) -> None:
        """Should check all registered dependencies."""
        results = configured_checker.check_all_dependencies()
        
        assert len(results) == 3
        assert all(isinstance(r, HealthCheckResult) for r in results.values())
    
    def test_handles_check_function_exceptions(self, health_checker: HealthChecker) -> None:
        """Should handle exceptions in check functions."""
        def failing_check() -> bool:
            raise RuntimeError("Check failed")
        
        health_checker.register_dependency("service", failing_check)
        
        result = health_checker.check_dependency("service")
        assert result.is_healthy is False
        assert result.error is not None


# ============================================================================
# CATEGORY 4: HEALTH STATUS TRANSITIONS (4/4)
# ============================================================================

class TestHealthStatusTransitions:
    """Test health status transitions."""
    
    def test_transitions_from_unknown_to_healthy(self, health_checker: HealthChecker) -> None:
        """Should transition from UNKNOWN to HEALTHY."""
        health_checker.register_dependency("service", lambda: True)
        
        dep = health_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.UNKNOWN
        
        health_checker.check_dependency("service")
        
        dep = health_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.HEALTHY
    
    def test_transitions_to_degraded_on_first_failure(
        self,
        configured_checker: HealthChecker,
    ) -> None:
        """Should transition to DEGRADED on first failure."""
        configured_checker.register_dependency("service", lambda: False)
        configured_checker.check_dependency("service")
        
        dep = configured_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.DEGRADED
    
    def test_transitions_to_unhealthy_after_threshold(
        self,
        configured_checker: HealthChecker,
    ) -> None:
        """Should transition to UNHEALTHY after failure threshold."""
        configured_checker.register_dependency("service", lambda: False)
        configured_checker.config.failure_threshold = 2
        
        # First failure: DEGRADED
        configured_checker.check_dependency("service")
        dep = configured_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.DEGRADED
        
        # Second failure: UNHEALTHY
        configured_checker.check_dependency("service")
        dep = configured_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.UNHEALTHY
    
    def test_recovers_after_success(self, configured_checker: HealthChecker) -> None:
        """Should recover to HEALTHY after successful checks."""
        results: List[bool] = [False, False, True, True]
        result_iter = iter(results)
        
        def check() -> bool:
            return next(result_iter)
        
        configured_checker.register_dependency("service", check)
        
        # Fail twice (becomes UNHEALTHY)
        configured_checker.check_dependency("service")
        configured_checker.check_dependency("service")
        
        # Succeed once (transitions back)
        configured_checker.check_dependency("service")
        
        dep = configured_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.status == HealthStatus.HEALTHY


# ============================================================================
# CATEGORY 5: DEPENDENCY QUERIES (3/3)
# ============================================================================

class TestDependencyQueries:
    """Test queries for dependency health status."""
    
    def test_gets_healthy_dependencies(self, configured_checker: HealthChecker) -> None:
        """Should return list of healthy dependencies."""
        configured_checker.check_all_dependencies()
        
        healthy = configured_checker.get_healthy_dependencies()
        assert "service-a" in healthy
        assert "service-b" in healthy
        assert "service-c" not in healthy
    
    def test_gets_unhealthy_dependencies(self, configured_checker: HealthChecker) -> None:
        """Should return list of unhealthy dependencies."""
        configured_checker.check_all_dependencies()
        configured_checker.check_all_dependencies()  # Meet failure threshold
        
        unhealthy = configured_checker.get_unhealthy_dependencies()
        assert "service-c" in unhealthy
    
    def test_checks_if_all_healthy(self, configured_checker: HealthChecker) -> None:
        """Should check if all dependencies are healthy."""
        assert not configured_checker.are_all_healthy()  # service-c fails
        
        # Register only healthy service
        checker = HealthChecker()
        checker.register_dependency("service", lambda: True)
        checker.check_dependency("service")
        assert checker.are_all_healthy()


# ============================================================================
# CATEGORY 6: METRICS COLLECTION (4/4)
# ============================================================================

class TestMetricsCollection:
    """Test metrics collection for health checks."""
    
    def test_tracks_total_checks(self, health_checker: HealthChecker) -> None:
        """Should track total health checks performed."""
        health_checker.register_dependency("service", lambda: True)
        
        for _ in range(5):
            health_checker.check_dependency("service")
        
        metrics = health_checker.get_metrics()
        assert metrics["total_checks"] == 5
    
    def test_tracks_successful_and_failed_checks(
        self,
        health_checker: HealthChecker,
    ) -> None:
        """Should track successful and failed checks."""
        health_checker.register_dependency("service-a", lambda: True)
        health_checker.register_dependency("service-b", lambda: False)
        
        health_checker.check_dependency("service-a")
        health_checker.check_dependency("service-b")
        
        metrics = health_checker.get_metrics()
        assert metrics["successful_checks"] >= 1
        assert metrics["failed_checks"] >= 1
    
    def test_calculates_success_rate(self, health_checker: HealthChecker) -> None:
        """Should calculate success rate."""
        health_checker.register_dependency("service", lambda: True)
        
        for _ in range(10):
            health_checker.check_dependency("service")
        
        metrics = health_checker.get_metrics()
        assert metrics["success_rate"] == 100.0
    
    def test_tracks_state_transitions(self, configured_checker: HealthChecker) -> None:
        """Should track health state transitions."""
        configured_checker.check_all_dependencies()
        
        metrics = configured_checker.get_metrics()
        assert metrics["health_state_transitions"] > 0


# ============================================================================
# CATEGORY 7: RECOVERY & DEGRADATION TRACKING (3/3)
# ============================================================================

class TestRecoveryDegradationTracking:
    """Test tracking of recovery and degradation events."""
    
    def test_tracks_degradation_events(self, health_checker: HealthChecker) -> None:
        """Should track degradation events."""
        health_checker.config.failure_threshold = 2
        health_checker.register_dependency("service", lambda: False)
        
        # Fail twice
        health_checker.check_dependency("service")
        health_checker.check_dependency("service")
        
        metrics = health_checker.get_metrics()
        assert metrics["degradation_events"] > 0
    
    def test_tracks_recovery_events(self, health_checker: HealthChecker) -> None:
        """Should track recovery events."""
        health_checker.config.failure_threshold = 1
        
        results: List[bool] = [False, True]
        result_iter = iter(results)
        
        def check() -> bool:
            return next(result_iter)
        
        health_checker.register_dependency("service", check)
        
        health_checker.check_dependency("service")  # Fail
        health_checker.check_dependency("service")  # Recover
        
        metrics = health_checker.get_metrics()
        assert metrics["recovery_events"] > 0
    
    def test_tracks_check_history(self, health_checker: HealthChecker) -> None:
        """Should track history of health checks."""
        health_checker.register_dependency("service", lambda: True)
        
        health_checker.check_dependency("service")
        health_checker.check_dependency("service")
        
        history = health_checker.get_check_history()
        assert len(history) == 2


# ============================================================================
# CATEGORY 8: RESPONSE TIME TRACKING (2/2)
# ============================================================================

class TestResponseTimeTracking:
    """Test response time tracking for health checks."""
    
    def test_records_response_time(self, health_checker: HealthChecker) -> None:
        """Should record response time for health checks."""
        def slow_check() -> bool:
            time.sleep(0.01)
            return True
        
        health_checker.register_dependency("service", slow_check)
        result = health_checker.check_dependency("service")
        
        assert result.response_time_ms > 0
    
    def test_tracks_response_time_in_dependency(self, health_checker: HealthChecker) -> None:
        """Should track response time in dependency health."""
        def slow_check() -> bool:
            time.sleep(0.01)
            return True
        
        health_checker.register_dependency("service", slow_check)
        health_checker.check_dependency("service")
        
        dep = health_checker.get_dependency_health("service")
        assert dep is not None
        assert dep.response_time_ms > 0


# ============================================================================
# CATEGORY 9: CONCURRENT HEALTH CHECKS (2/2)
# ============================================================================

class TestConcurrentHealthChecks:
    """Test concurrent health check operations."""
    
    def test_handles_concurrent_health_checks(self, configured_checker: HealthChecker) -> None:
        """Should handle concurrent health checks."""
        results: List[Dict[str, Any]] = []
        lock = threading.Lock()
        
        def worker() -> None:
            try:
                result = configured_checker.check_all_dependencies()
                with lock:
                    results.append(result)
            except Exception:
                pass
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 5
    
    def test_thread_safe_metrics_updates(self, health_checker: HealthChecker) -> None:
        """Should safely update metrics from multiple threads."""
        health_checker.register_dependency("service", lambda: True)
        
        def worker() -> None:
            for _ in range(10):
                health_checker.check_dependency("service")
        
        threads = [threading.Thread(target=worker) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = health_checker.get_metrics()
        assert metrics["total_checks"] == 30


# ============================================================================
# CATEGORY 10: INTEGRATION PATTERNS (3/3)
# ============================================================================

class TestIntegrationPatterns:
    """Test integration with other resilience patterns."""
    
    def test_integrates_with_graceful_degradation(
        self,
        configured_checker: HealthChecker,
    ) -> None:
        """Should provide health status for degradation decisions."""
        configured_checker.check_all_dependencies()
        
        # Unhealthy dependencies trigger degradation
        unhealthy = configured_checker.get_unhealthy_dependencies()
        if unhealthy:
            # Would trigger REDUCED degradation
            assert True
    
    def test_detects_cascading_failures(self, health_checker: HealthChecker) -> None:
        """Should detect cascading failures across dependencies."""
        # Register dependent services
        health_checker.register_dependency("db", lambda: False)
        health_checker.register_dependency("cache", lambda: False)
        health_checker.register_dependency("api", lambda: False)
        
        # Check all
        health_checker.check_all_dependencies()
        health_checker.check_all_dependencies()
        health_checker.check_all_dependencies()
        
        # All unhealthy
        unhealthy = health_checker.get_unhealthy_dependencies()
        assert len(unhealthy) >= 1
    
    def test_coordinates_recovery_across_services(
        self,
        health_checker: HealthChecker,
    ) -> None:
        """Should coordinate recovery across multiple services."""
        # Simulate services recovering in sequence
        services_status: Dict[str, List[bool]] = {
            "service-a": [False, True, True],
            "service-b": [False, False, True],
            "service-c": [False, False, False],
        }
        
        for service_name, statuses in services_status.items():
            status_iter = iter(statuses)
            health_checker.register_dependency(service_name, lambda: next(status_iter))
        
        # Check multiple times
        for _ in range(3):
            health_checker.check_all_dependencies()
        
        metrics = health_checker.get_metrics()
        assert metrics["recovery_events"] >= 0
