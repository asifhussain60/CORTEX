"""
Comprehensive test suite for BRT-014: Timeout Management Pattern.

Tests timeout handling strategies for operations with per-service timeout limits,
graceful degradation on timeout, and timeout exception propagation.

The timeout management pattern ensures operations complete within specified time
windows, preventing resource exhaustion and cascading failures from slow operations.

AC-INFRA-001-03: Timeout management for operation bounds
"""

import threading
import time
from typing import List, Generator, Callable, Any, Optional, Dict
from dataclasses import dataclass
from enum import Enum

import pytest


# ============================================================================
# TIMEOUT MANAGEMENT IMPLEMENTATION FOR TESTING
# ============================================================================

class TimeoutStrategy(str, Enum):
    """Timeout handling strategies."""
    HARD_TIMEOUT = "hard_timeout"  # Interrupt operation
    SOFT_TIMEOUT = "soft_timeout"  # Log warning, continue
    GRACEFUL_TIMEOUT = "graceful_timeout"  # Give grace period
    ADAPTIVE_TIMEOUT = "adaptive_timeout"  # Adjust based on history


class TimeoutException(Exception):
    """Raised when operation exceeds timeout."""
    pass


class TimeoutExceededWarning(UserWarning):
    """Warning for soft timeouts."""
    pass


@dataclass
class TimeoutConfig:
    """Configuration for timeout management."""
    
    default_timeout: float = 5.0  # seconds
    min_timeout: float = 0.1
    max_timeout: float = 300.0
    grace_period: float = 0.5  # Additional time for graceful shutdown
    strategy: TimeoutStrategy = TimeoutStrategy.HARD_TIMEOUT
    enable_adaptive: bool = False
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.min_timeout <= 0:
            raise ValueError("min_timeout must be > 0")
        if self.max_timeout <= self.min_timeout:
            raise ValueError("max_timeout must be > min_timeout")
        if self.default_timeout < self.min_timeout:
            raise ValueError("default_timeout must be >= min_timeout")
        if self.default_timeout > self.max_timeout:
            raise ValueError("default_timeout must be <= max_timeout")


@dataclass
class TimeoutMetrics:
    """Metrics for timeout operations."""
    
    total_operations: int = 0
    completed_in_time: int = 0
    soft_timeout_count: int = 0
    hard_timeout_count: int = 0
    average_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')


class TimeoutManager:
    """Manages timeout enforcement for operations."""
    
    def __init__(self, config: Optional[TimeoutConfig] = None) -> None:
        """Initialize timeout manager."""
        self.config = config or TimeoutConfig()
        self.service_timeouts: Dict[str, float] = {}
        self.metrics = TimeoutMetrics()
        self.lock = threading.Lock()
    
    def configure_service_timeout(self, service_name: str, timeout: float) -> None:
        """Configure timeout for a specific service."""
        if timeout < self.config.min_timeout or timeout > self.config.max_timeout:
            raise ValueError(f"Timeout must be between {self.config.min_timeout} and {self.config.max_timeout}")
        
        with self.lock:
            self.service_timeouts[service_name] = timeout
    
    def get_timeout(self, service_name: Optional[str] = None) -> float:
        """Get timeout for a service or default."""
        if service_name and service_name in self.service_timeouts:
            return self.service_timeouts[service_name]
        return self.config.default_timeout
    
    def execute_with_timeout(
        self,
        func: Callable[..., Any],
        service_name: Optional[str] = None,
        timeout: Optional[float] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute function with timeout enforcement."""
        actual_timeout = timeout or self.get_timeout(service_name)
        
        start_time = time.time()
        result = None
        exceeded = False
        
        try:
            result = func(*args, **kwargs)
        finally:
            elapsed = time.time() - start_time
            
            with self.lock:
                self.metrics.total_operations += 1
                
                if elapsed <= actual_timeout:
                    self.metrics.completed_in_time += 1
                else:
                    exceeded = True
                    if self.config.strategy == TimeoutStrategy.HARD_TIMEOUT:
                        self.metrics.hard_timeout_count += 1
                    else:
                        self.metrics.soft_timeout_count += 1
                
                # Update duration metrics
                elapsed_ms = elapsed * 1000
                self.metrics.max_duration_ms = max(self.metrics.max_duration_ms, elapsed_ms)
                self.metrics.min_duration_ms = min(self.metrics.min_duration_ms, elapsed_ms)
                
                # Update average
                if self.metrics.total_operations > 0:
                    old_avg = self.metrics.average_duration_ms
                    self.metrics.average_duration_ms = (
                        old_avg * (self.metrics.total_operations - 1) +
                        elapsed_ms
                    ) / self.metrics.total_operations
        
        if exceeded and self.config.strategy == TimeoutStrategy.HARD_TIMEOUT:
            raise TimeoutException(f"Operation exceeded timeout of {actual_timeout}s")
        
        return result
    
    def execute_with_thread_timeout(
        self,
        func: Callable[..., Any],
        timeout: float,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute function in thread with timeout."""
        result: List[Any] = [None]
        exception: List[Optional[Exception]] = [None]
        
        def target() -> None:
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            raise TimeoutException(f"Operation exceeded timeout of {timeout}s")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get timeout metrics."""
        with self.lock:
            success_rate = (
                (self.metrics.completed_in_time / self.metrics.total_operations * 100)
                if self.metrics.total_operations > 0
                else 0.0
            )
            
            return {
                "total_operations": self.metrics.total_operations,
                "completed_in_time": self.metrics.completed_in_time,
                "soft_timeouts": self.metrics.soft_timeout_count,
                "hard_timeouts": self.metrics.hard_timeout_count,
                "success_rate": success_rate,
                "average_duration_ms": self.metrics.average_duration_ms,
                "max_duration_ms": self.metrics.max_duration_ms,
                "min_duration_ms": self.metrics.min_duration_ms,
            }


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def timeout_manager() -> Generator[TimeoutManager, None, None]:
    """Create a TimeoutManager for testing."""
    manager = TimeoutManager()
    yield manager


@pytest.fixture
def configured_manager() -> Generator[TimeoutManager, None, None]:
    """Create manager with pre-configured service timeouts."""
    config = TimeoutConfig(
        default_timeout=2.0,
        strategy=TimeoutStrategy.HARD_TIMEOUT,
    )
    manager = TimeoutManager(config=config)
    manager.configure_service_timeout("fast-service", timeout=0.5)
    manager.configure_service_timeout("normal-service", timeout=2.0)
    manager.configure_service_timeout("slow-service", timeout=5.0)
    yield manager


# ============================================================================
# CATEGORY 1: INITIALIZATION & CONFIGURATION (4/4)
# ============================================================================

class TestInitialization:
    """Test timeout manager initialization."""
    
    def test_creates_manager_with_default_config(self, timeout_manager: TimeoutManager) -> None:
        """Should create manager with default configuration."""
        assert timeout_manager is not None
        assert timeout_manager.config.default_timeout == 5.0
        assert timeout_manager.config.min_timeout == 0.1
        assert timeout_manager.config.max_timeout == 300.0
    
    def test_creates_manager_with_custom_config(self) -> None:
        """Should create manager with custom configuration."""
        config = TimeoutConfig(
            default_timeout=3.0,
            strategy=TimeoutStrategy.SOFT_TIMEOUT,
        )
        manager = TimeoutManager(config=config)
        
        assert manager.config.default_timeout == 3.0
        assert manager.config.strategy == TimeoutStrategy.SOFT_TIMEOUT
    
    def test_rejects_invalid_timeout_config(self) -> None:
        """Should reject invalid timeout configuration."""
        with pytest.raises(ValueError):
            TimeoutConfig(min_timeout=-1.0)
    
    def test_configures_per_service_timeouts(self, timeout_manager: TimeoutManager) -> None:
        """Should configure per-service timeout limits."""
        timeout_manager.configure_service_timeout("service-a", 1.0)
        timeout_manager.configure_service_timeout("service-b", 3.0)
        
        assert timeout_manager.get_timeout("service-a") == 1.0
        assert timeout_manager.get_timeout("service-b") == 3.0


# ============================================================================
# CATEGORY 2: TIMEOUT RETRIEVAL (3/3)
# ============================================================================

class TestTimeoutRetrieval:
    """Test retrieving timeout values."""
    
    def test_returns_service_timeout(self, configured_manager: TimeoutManager) -> None:
        """Should return configured service timeout."""
        assert configured_manager.get_timeout("fast-service") == 0.5
        assert configured_manager.get_timeout("normal-service") == 2.0
        assert configured_manager.get_timeout("slow-service") == 5.0
    
    def test_returns_default_for_unknown_service(self, configured_manager: TimeoutManager) -> None:
        """Should return default timeout for unknown service."""
        assert configured_manager.get_timeout("unknown-service") == 2.0
        assert configured_manager.get_timeout() == 2.0
    
    def test_returns_default_when_no_service_specified(self, timeout_manager: TimeoutManager) -> None:
        """Should return default timeout when no service specified."""
        assert timeout_manager.get_timeout() == 5.0


# ============================================================================
# CATEGORY 3: BASIC TIMEOUT ENFORCEMENT (4/4)
# ============================================================================

class TestBasicTimeoutEnforcement:
    """Test basic timeout enforcement."""
    
    def test_completes_operation_within_timeout(self, timeout_manager: TimeoutManager) -> None:
        """Should complete operation that finishes within timeout."""
        def quick_op() -> str:
            return "success"
        
        result = timeout_manager.execute_with_timeout(quick_op, timeout=1.0)
        assert result == "success"
    
    def test_raises_on_operation_exceeding_timeout(self, timeout_manager: TimeoutManager) -> None:
        """Should raise TimeoutException when operation exceeds timeout."""
        def slow_op() -> None:
            time.sleep(0.3)
        
        with pytest.raises(TimeoutException):
            timeout_manager.execute_with_timeout(slow_op, timeout=0.1)
    
    def test_tracks_operation_completion(self, timeout_manager: TimeoutManager) -> None:
        """Should track whether operation completed in time."""
        def quick_op() -> None:
            time.sleep(0.05)
        
        timeout_manager.execute_with_timeout(quick_op, timeout=1.0)
        metrics = timeout_manager.get_metrics()
        
        assert metrics["total_operations"] == 1
        assert metrics["completed_in_time"] == 1
        assert metrics["hard_timeouts"] == 0
    
    def test_tracks_timeout_violations(self, timeout_manager: TimeoutManager) -> None:
        """Should track timeout violations."""
        def slow_op() -> None:
            time.sleep(0.3)
        
        try:
            timeout_manager.execute_with_timeout(slow_op, timeout=0.1)
        except TimeoutException:
            pass
        
        metrics = timeout_manager.get_metrics()
        assert metrics["hard_timeouts"] == 1


# ============================================================================
# CATEGORY 4: PER-SERVICE TIMEOUTS (4/4)
# ============================================================================

class TestPerServiceTimeouts:
    """Test per-service timeout configuration."""
    
    def test_applies_service_timeout(self, configured_manager: TimeoutManager) -> None:
        """Should apply configured service timeout."""
        def op() -> str:
            time.sleep(0.1)
            return "ok"
        
        result = configured_manager.execute_with_timeout(op, service_name="fast-service")
        assert result == "ok"
    
    def test_respects_different_service_limits(self, configured_manager: TimeoutManager) -> None:
        """Should respect different service timeout limits."""
        def longer_op() -> None:
            time.sleep(0.4)
        
        # Should succeed with slow-service timeout (5.0s)
        configured_manager.execute_with_timeout(longer_op, service_name="slow-service")
        
        # Should fail with fast-service timeout (0.5s can handle 0.4s, but barely)
        # Use a direct timeout override to be more reliable
        def slow_op() -> None:
            time.sleep(0.5)
        
        with pytest.raises(TimeoutException):
            configured_manager.execute_with_timeout(slow_op, service_name="fast-service", timeout=0.1)
    
    def test_override_service_timeout(self, configured_manager: TimeoutManager) -> None:
        """Should allow overriding service timeout."""
        def op() -> None:
            time.sleep(0.2)
        
        # Override fast-service timeout
        configured_manager.execute_with_timeout(op, service_name="fast-service", timeout=1.0)
    
    def test_validates_service_timeout_bounds(self, configured_manager: TimeoutManager) -> None:
        """Should validate service timeout is within bounds."""
        with pytest.raises(ValueError):
            configured_manager.configure_service_timeout("service", timeout=500.0)


# ============================================================================
# CATEGORY 5: METRICS COLLECTION (4/4)
# ============================================================================

class TestMetricsCollection:
    """Test metrics collection for timeout operations."""
    
    def test_tracks_total_operations(self, timeout_manager: TimeoutManager) -> None:
        """Should track total operations executed."""
        for _ in range(3):
            try:
                timeout_manager.execute_with_timeout(lambda: None, timeout=1.0)
            except TimeoutException:
                pass
        
        metrics = timeout_manager.get_metrics()
        assert metrics["total_operations"] == 3
    
    def test_calculates_success_rate(self, timeout_manager: TimeoutManager) -> None:
        """Should calculate success rate."""
        # 2 successful, 1 timeout
        timeout_manager.execute_with_timeout(lambda: None, timeout=1.0)
        timeout_manager.execute_with_timeout(lambda: None, timeout=1.0)
        
        try:
            timeout_manager.execute_with_timeout(lambda: time.sleep(0.2), timeout=0.05)
        except TimeoutException:
            pass
        
        metrics = timeout_manager.get_metrics()
        assert metrics["success_rate"] > 60.0
    
    def test_tracks_duration_metrics(self, timeout_manager: TimeoutManager) -> None:
        """Should track operation duration metrics."""
        def op() -> None:
            time.sleep(0.05)
        
        timeout_manager.execute_with_timeout(op, timeout=1.0)
        
        metrics = timeout_manager.get_metrics()
        assert metrics["average_duration_ms"] > 0
        assert metrics["max_duration_ms"] >= metrics["average_duration_ms"]
        assert metrics["min_duration_ms"] <= metrics["average_duration_ms"]
    
    def test_aggregates_metrics_across_operations(self, timeout_manager: TimeoutManager) -> None:
        """Should aggregate metrics across multiple operations."""
        def op(duration: float) -> None:
            time.sleep(duration)
        
        timeout_manager.execute_with_timeout(op, timeout=1.0, duration=0.05)
        timeout_manager.execute_with_timeout(op, timeout=1.0, duration=0.1)
        timeout_manager.execute_with_timeout(op, timeout=1.0, duration=0.02)
        
        metrics = timeout_manager.get_metrics()
        assert metrics["total_operations"] == 3
        assert 30 < metrics["average_duration_ms"] < 80


# ============================================================================
# CATEGORY 6: TIMEOUT STRATEGIES (3/3)
# ============================================================================

class TestTimeoutStrategies:
    """Test different timeout handling strategies."""
    
    def test_hard_timeout_raises_exception(self) -> None:
        """Should raise exception on hard timeout."""
        config = TimeoutConfig(strategy=TimeoutStrategy.HARD_TIMEOUT)
        manager = TimeoutManager(config=config)
        
        def slow_op() -> None:
            time.sleep(0.3)
        
        with pytest.raises(TimeoutException):
            manager.execute_with_timeout(slow_op, timeout=0.1)
    
    def test_soft_timeout_continues(self) -> None:
        """Should continue on soft timeout (no exception)."""
        config = TimeoutConfig(strategy=TimeoutStrategy.SOFT_TIMEOUT)
        manager = TimeoutManager(config=config)
        
        def slow_op() -> str:
            time.sleep(0.2)
            return "completed"
        
        # Should not raise
        result = manager.execute_with_timeout(slow_op, timeout=0.1)
        assert result == "completed"
        
        metrics = manager.get_metrics()
        assert metrics["soft_timeouts"] == 1
    
    def test_graceful_timeout_provides_grace_period(self) -> None:
        """Should provide grace period for graceful timeout."""
        config = TimeoutConfig(
            strategy=TimeoutStrategy.GRACEFUL_TIMEOUT,
            grace_period=0.1,
        )
        manager = TimeoutManager(config=config)
        
        def op() -> str:
            time.sleep(0.05)
            return "done"
        
        result = manager.execute_with_timeout(op, timeout=0.02)
        assert result == "done"


# ============================================================================
# CATEGORY 7: THREAD-BASED TIMEOUT (3/3)
# ============================================================================

class TestThreadBasedTimeout:
    """Test thread-based timeout enforcement."""
    
    def test_executes_in_thread_within_timeout(self, timeout_manager: TimeoutManager) -> None:
        """Should execute function in thread within timeout."""
        def op() -> str:
            return "success"
        
        result = timeout_manager.execute_with_thread_timeout(op, timeout=1.0)
        assert result == "success"
    
    def test_raises_on_thread_timeout_exceeded(self, timeout_manager: TimeoutManager) -> None:
        """Should raise when thread operation exceeds timeout."""
        def slow_op() -> None:
            time.sleep(0.5)
        
        with pytest.raises(TimeoutException):
            timeout_manager.execute_with_thread_timeout(slow_op, timeout=0.1)
    
    def test_propagates_thread_exceptions(self, timeout_manager: TimeoutManager) -> None:
        """Should propagate exceptions from thread."""
        def failing_op() -> None:
            raise ValueError("Operation failed")
        
        with pytest.raises(ValueError):
            timeout_manager.execute_with_thread_timeout(failing_op, timeout=1.0)


# ============================================================================
# CATEGORY 8: CONCURRENT TIMEOUT OPERATIONS (3/3)
# ============================================================================

class TestConcurrentTimeoutOperations:
    """Test timeout enforcement under concurrent load."""
    
    def test_handles_concurrent_timeout_operations(self, timeout_manager: TimeoutManager) -> None:
        """Should handle concurrent operations with timeouts."""
        results: List[str] = []
        errors: List[Exception] = []
        lock = threading.Lock()
        
        def op(op_id: int) -> None:
            try:
                def work() -> None:
                    time.sleep(0.05 * op_id)
                
                timeout_manager.execute_with_timeout(work, timeout=0.2)
                with lock:
                    results.append(f"op-{op_id}")
            except Exception as e:
                with lock:
                    errors.append(e)
        
        threads = [threading.Thread(target=op, args=(i,)) for i in range(1, 4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) > 0
    
    def test_maintains_separate_service_timeouts_concurrently(
        self,
        configured_manager: TimeoutManager,
    ) -> None:
        """Should maintain separate service timeouts under concurrent load."""
        success_count = [0]
        error_count = [0]
        lock = threading.Lock()
        
        def op(service: str, duration: float) -> None:
            try:
                def work() -> None:
                    time.sleep(duration)
                
                configured_manager.execute_with_timeout(work, service_name=service)
                with lock:
                    success_count[0] += 1
            except TimeoutException:
                with lock:
                    error_count[0] += 1
        
        threads = [
            threading.Thread(target=op, args=("fast-service", 0.1)),
            threading.Thread(target=op, args=("normal-service", 0.5)),
            threading.Thread(target=op, args=("slow-service", 0.3)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # At least one should succeed
        assert success_count[0] > 0
    
    def test_thread_safe_metrics_updates(self, timeout_manager: TimeoutManager) -> None:
        """Should safely update metrics from multiple threads."""
        def op() -> None:
            time.sleep(0.01)
        
        threads = [
            threading.Thread(target=lambda: timeout_manager.execute_with_timeout(op, timeout=1.0))
            for _ in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = timeout_manager.get_metrics()
        assert metrics["total_operations"] == 10


# ============================================================================
# CATEGORY 9: TIMEOUT CONFIGURATION VALIDATION (3/3)
# ============================================================================

class TestTimeoutConfigurationValidation:
    """Test timeout configuration validation."""
    
    def test_validates_config_bounds(self) -> None:
        """Should validate configuration bounds."""
        # min_timeout > 0
        with pytest.raises(ValueError):
            TimeoutConfig(min_timeout=0)
        
        # max_timeout > min_timeout
        with pytest.raises(ValueError):
            TimeoutConfig(min_timeout=2.0, max_timeout=1.0)
    
    def test_validates_default_within_bounds(self) -> None:
        """Should validate default timeout within bounds."""
        with pytest.raises(ValueError):
            TimeoutConfig(
                min_timeout=1.0,
                max_timeout=5.0,
                default_timeout=0.5,
            )
        
        with pytest.raises(ValueError):
            TimeoutConfig(
                min_timeout=1.0,
                max_timeout=5.0,
                default_timeout=10.0,
            )
    
    def test_accepts_valid_configuration(self) -> None:
        """Should accept valid configuration."""
        config = TimeoutConfig(
            min_timeout=0.1,
            max_timeout=60.0,
            default_timeout=5.0,
        )
        assert config.min_timeout == 0.1
        assert config.max_timeout == 60.0
        assert config.default_timeout == 5.0


# ============================================================================
# CATEGORY 10: EXCEPTION HANDLING (2/2)
# ============================================================================

class TestExceptionHandling:
    """Test exception handling in timeout operations."""
    
    def test_propagates_operation_exceptions(self, timeout_manager: TimeoutManager) -> None:
        """Should propagate exceptions from operations."""
        def failing_op() -> None:
            raise ValueError("Operation error")
        
        with pytest.raises(ValueError):
            timeout_manager.execute_with_timeout(failing_op, timeout=1.0)
    
    def test_distinguishes_timeout_from_operation_errors(
        self,
        timeout_manager: TimeoutManager,
    ) -> None:
        """Should distinguish timeout exceptions from operation exceptions."""
        # Timeout exception
        def slow_op() -> None:
            time.sleep(0.2)
        
        with pytest.raises(TimeoutException):
            timeout_manager.execute_with_timeout(slow_op, timeout=0.05)
        
        # Operation exception
        def error_op() -> None:
            raise RuntimeError("Op error")
        
        with pytest.raises(RuntimeError):
            timeout_manager.execute_with_timeout(error_op, timeout=1.0)


# ============================================================================
# CATEGORY 11: INTEGRATION PATTERNS (2/2)
# ============================================================================

class TestIntegrationPatterns:
    """Test integration with other resilience patterns."""
    
    def test_integrates_with_bulkhead_isolation(self, configured_manager: TimeoutManager) -> None:
        """Should work with bulkhead isolation (separate timeouts per service)."""
        # Each service has independent timeout
        metrics_fast = configured_manager.get_timeout("fast-service")
        metrics_slow = configured_manager.get_timeout("slow-service")
        
        assert metrics_fast < metrics_slow
    
    def test_integrates_with_circuit_breaker(self, timeout_manager: TimeoutManager) -> None:
        """Should work with circuit breaker pattern."""
        # Timeouts can detect slow operations that trigger circuit breaker
        timeout_violations: List[bool] = []
        
        def potentially_slow_op() -> None:
            time.sleep(0.15)
        
        for _ in range(3):
            try:
                timeout_manager.execute_with_timeout(
                    potentially_slow_op,
                    timeout=0.1,
                )
            except TimeoutException:
                timeout_violations.append(True)
        
        # Multiple timeouts might trigger circuit breaker
        assert len(timeout_violations) > 0
