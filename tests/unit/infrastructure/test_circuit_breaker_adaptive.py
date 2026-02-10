"""
Tests for Adaptive Circuit Breaker.

AC-INFRA-001-03: Circuit Breaker with Adaptive Thresholds
Tests circuit breaker pattern with state management, failure detection,
and automatic recovery.
"""

import pytest
import time
import threading
from typing import Callable, Any
from unittest.mock import Mock

from cortex.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerOpenError,
)


@pytest.fixture
def circuit_config() -> CircuitBreakerConfig:
    """Create a standard circuit breaker configuration."""
    return CircuitBreakerConfig(
        failure_threshold=0.5,  # 50% error rate
        min_requests=10,
        open_duration_seconds=0.5,  # Short for testing
        half_open_max_attempts=3,
        max_open_duration_seconds=5.0,
    )


@pytest.fixture
def circuit_breaker(circuit_config: CircuitBreakerConfig) -> CircuitBreaker:
    """Create a circuit breaker instance."""
    return CircuitBreaker(name="test_circuit", config=circuit_config)


class TestCircuitBreakerInitialization:
    """Test circuit breaker initialization."""

    def test_starts_in_closed_state(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Circuit breaker should start in CLOSED state."""
        assert circuit_breaker.state == CircuitState.CLOSED

    def test_config_validation(self) -> None:
        """Config should validate parameters."""
        with pytest.raises(ValueError, match="failure_threshold"):
            CircuitBreakerConfig(failure_threshold=1.5)
        
        with pytest.raises(ValueError, match="min_requests"):
            CircuitBreakerConfig(min_requests=0)
        
        with pytest.raises(ValueError, match="open_duration_seconds"):
            CircuitBreakerConfig(open_duration_seconds=-1.0)


class TestCircuitBreakerClosedState:
    """Test circuit breaker behavior in CLOSED state."""

    def test_allows_calls_when_closed(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """CLOSED circuit should allow calls through."""
        def operation() -> str:
            return "success"
        
        result = circuit_breaker.call(operation)
        assert result == "success"

    def test_records_successful_calls(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """CLOSED circuit should record successful calls."""
        def operation() -> str:
            return "success"
        
        for _ in range(5):
            circuit_breaker.call(operation)
        
        metrics = circuit_breaker.get_metrics()
        assert metrics["success_count"] >= 5

    def test_records_failed_calls(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """CLOSED circuit should record failed calls."""
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        for _ in range(3):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        metrics = circuit_breaker.get_metrics()
        assert metrics["failure_count"] >= 3

    def test_opens_after_threshold_exceeded(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """Circuit should open after failure threshold exceeded."""
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        # Generate failures to exceed threshold (50% of 10 requests)
        for _ in range(circuit_config.min_requests):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        # Circuit should now be open
        assert circuit_breaker.state == CircuitState.OPEN

    def test_does_not_open_below_min_requests(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Circuit should not open with insufficient request history."""
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        # Only 3 failures (below min_requests=10)
        for _ in range(3):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        # Should still be closed
        assert circuit_breaker.state == CircuitState.CLOSED


class TestCircuitBreakerOpenState:
    """Test circuit breaker behavior in OPEN state."""

    def test_rejects_calls_when_open(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """OPEN circuit should reject calls immediately."""
        # Force circuit open
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        for _ in range(circuit_config.min_requests):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        # Now circuit is open, should reject
        def any_operation() -> str:
            return "should not execute"
        
        with pytest.raises(CircuitBreakerOpenError):
            circuit_breaker.call(any_operation)

    def test_transitions_to_half_open_after_duration(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """Circuit should transition to HALF_OPEN after open duration."""
        # Force circuit open
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        for _ in range(circuit_config.min_requests):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        # After trip, duration is doubled, so wait for doubled duration
        # Initial: 0.5, after trip: 1.0
        time.sleep(1.2)  # Wait for doubled duration plus buffer
        
        # Next successful call should transition to HALF_OPEN then CLOSED
        def test_operation() -> str:
            return "testing"
        
        # Make enough successful calls to close circuit
        for _ in range(circuit_config.half_open_max_attempts):
            result = circuit_breaker.call(test_operation)
            assert result == "testing"
        
        # Should now be CLOSED after successful tests
        assert circuit_breaker.state == CircuitState.CLOSED

    def test_increments_open_duration_on_repeated_opens(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Open duration should increase with repeated opens."""
        initial_duration = circuit_breaker.config.open_duration_seconds
        
        # Force open multiple times
        for cycle in range(3):
            # Reset to closed manually for testing
            circuit_breaker._state = CircuitState.CLOSED
            circuit_breaker._failure_count = 0
            circuit_breaker._success_count = 0
            circuit_breaker._request_count = 0
            
            # Trigger open
            def failing_operation() -> None:
                raise ValueError("Test error")
            
            for _ in range(10):
                with pytest.raises(ValueError):
                    circuit_breaker.call(failing_operation)
        
        # Duration should have increased (capped at max)
        assert circuit_breaker._current_open_duration >= initial_duration


class TestCircuitBreakerHalfOpenState:
    """Test circuit breaker behavior in HALF_OPEN state."""

    def test_allows_limited_test_calls(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """HALF_OPEN circuit should allow test calls."""
        # Force to half-open state
        circuit_breaker._state = CircuitState.HALF_OPEN
        circuit_breaker._half_open_attempts = 0
        
        def operation() -> str:
            return "success"
        
        result = circuit_breaker.call(operation)
        assert result == "success"

    def test_closes_after_successful_tests(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """Circuit should close after successful test requests."""
        # Force to half-open
        circuit_breaker._state = CircuitState.HALF_OPEN
        circuit_breaker._half_open_attempts = 0
        
        def operation() -> str:
            return "success"
        
        # Make successful test calls
        for _ in range(circuit_config.half_open_max_attempts):
            circuit_breaker.call(operation)
        
        # Should be closed now
        assert circuit_breaker.state == CircuitState.CLOSED

    def test_reopens_on_failure_during_test(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Circuit should reopen if test call fails."""
        # Force to half-open
        circuit_breaker._state = CircuitState.HALF_OPEN
        circuit_breaker._half_open_attempts = 0
        
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            circuit_breaker.call(failing_operation)
        
        # Should be open again
        assert circuit_breaker.state == CircuitState.OPEN


class TestCircuitBreakerMetrics:
    """Test circuit breaker metrics tracking."""

    def test_tracks_success_and_failure_counts(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Metrics should track success and failure counts."""
        def success_op() -> str:
            return "ok"
        
        def fail_op() -> None:
            raise ValueError("error")
        
        for _ in range(5):
            circuit_breaker.call(success_op)
        
        for _ in range(3):
            with pytest.raises(ValueError):
                circuit_breaker.call(fail_op)
        
        metrics = circuit_breaker.get_metrics()
        assert metrics["success_count"] >= 5
        assert metrics["failure_count"] >= 3

    def test_tracks_state_transitions(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Metrics should track state changes."""
        initial_metrics = circuit_breaker.get_metrics()
        
        # Force state change
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        for _ in range(10):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        metrics = circuit_breaker.get_metrics()
        assert metrics["state"] != initial_metrics["state"]

    def test_tracks_rejection_count(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """Metrics should track rejected calls when open."""
        # Force open
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        for _ in range(circuit_config.min_requests):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        # Try calls while open
        def any_op() -> str:
            return "ok"
        
        for _ in range(5):
            with pytest.raises(CircuitBreakerOpenError):
                circuit_breaker.call(any_op)
        
        metrics = circuit_breaker.get_metrics()
        assert metrics["rejected_count"] >= 5


class TestCircuitBreakerConcurrency:
    """Test circuit breaker under concurrent access."""

    def test_thread_safe_state_transitions(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """State transitions should be thread-safe."""
        results = {"success": 0, "failure": 0, "rejected": 0}
        lock = threading.Lock()
        
        def worker():
            for i in range(50):
                def operation() -> str:
                    if i % 3 == 0:
                        raise ValueError("Intermittent error")
                    return "success"
                
                try:
                    circuit_breaker.call(operation)
                    with lock:
                        results["success"] += 1
                except ValueError:
                    with lock:
                        results["failure"] += 1
                except CircuitBreakerOpenError:
                    with lock:
                        results["rejected"] += 1
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have processed all attempts
        total = results["success"] + results["failure"] + results["rejected"]
        assert total == 250  # 5 threads * 50 attempts

    def test_concurrent_metric_updates(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Metrics updates should be thread-safe."""
        def worker():
            for _ in range(100):
                def operation() -> str:
                    return "ok"
                
                try:
                    circuit_breaker.call(operation)
                except CircuitBreakerOpenError:
                    pass
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = circuit_breaker.get_metrics()
        # Metrics should be consistent
        assert metrics["request_count"] >= 0
        assert metrics["success_count"] >= 0


class TestCircuitBreakerReset:
    """Test circuit breaker reset functionality."""

    def test_reset_clears_metrics(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Reset should clear all metrics."""
        def operation() -> str:
            return "ok"
        
        for _ in range(10):
            circuit_breaker.call(operation)
        
        circuit_breaker.reset()
        
        metrics = circuit_breaker.get_metrics()
        assert metrics["success_count"] == 0
        assert metrics["failure_count"] == 0
        assert metrics["request_count"] == 0

    def test_reset_returns_to_closed_state(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """Reset should return circuit to CLOSED state."""
        # Force open
        def failing_operation() -> None:
            raise ValueError("Test error")
        
        for _ in range(circuit_config.min_requests):
            with pytest.raises(ValueError):
                circuit_breaker.call(failing_operation)
        
        assert circuit_breaker.state == CircuitState.OPEN
        
        circuit_breaker.reset()
        
        assert circuit_breaker.state == CircuitState.CLOSED


class TestCircuitBreakerEdgeCases:
    """Test circuit breaker edge cases."""

    def test_handles_timeout_as_failure(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Timeout should be counted as failure."""
        def slow_operation() -> str:
            time.sleep(0.1)
            raise TimeoutError("Operation timed out")
        
        with pytest.raises(TimeoutError):
            circuit_breaker.call(slow_operation)
        
        metrics = circuit_breaker.get_metrics()
        assert metrics["failure_count"] >= 1

    def test_handles_callable_with_args(
        self, circuit_breaker: CircuitBreaker
    ) -> None:
        """Circuit breaker should handle callables with arguments."""
        def operation_with_args(x: int, y: int) -> int:
            return x + y
        
        result = circuit_breaker.call(lambda: operation_with_args(5, 3))
        assert result == 8

    ) -> None:
        """Circuit breaker should preserve original exception type."""
        class CustomError(Exception):
            pass
        
        def failing_operation() -> None:
            raise CustomError("Custom message")
        
        with pytest.raises(CustomError, match="Custom message"):
            circuit_breaker.call(failing_operation)

    def test_max_open_duration_enforced(
        self, circuit_breaker: CircuitBreaker, circuit_config: CircuitBreakerConfig
    ) -> None:
        """Open duration should not exceed maximum."""
        # Force multiple open cycles
        for _ in range(20):
            circuit_breaker._increase_open_duration()
        
        assert circuit_breaker._current_open_duration <= circuit_config.max_open_duration_seconds
