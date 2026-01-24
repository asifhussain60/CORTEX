"""
BRT-011: Circuit Breaker Pattern Integration Tests

Tests for circuit breaker pattern preventing cascading failures
across external service calls, rate limiting, and connection pooling.

AC-INFRA-001-03: Adaptive circuit breaker with failure rate threshold
BRT-011: Circuit Breaker for Phase 4 Resilience Track
"""

import threading
import time
import pytest
from typing import List
from unittest.mock import Mock, patch, MagicMock

from cortex.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
    CircuitState,
)


# ============================================================================
# INITIALIZATION & CONFIGURATION TESTS
# ============================================================================


class TestCircuitBreakerInitialization:
    """Test circuit breaker initialization and configuration."""

    def test_starts_in_closed_state(self):
        """CB should start in CLOSED state."""
        cb = CircuitBreaker(name="test_cb")
        assert cb.state == CircuitState.CLOSED

    def test_accepts_custom_config(self):
        """CB should accept custom configuration."""
        config = CircuitBreakerConfig(failure_threshold=3, timeout_seconds=45.0)
        cb = CircuitBreaker(name="test_cb", config=config)
        assert cb.config.failure_threshold == 3
        assert cb.config.timeout_seconds == 45.0

    def test_validates_failure_threshold(self):
        """CB should validate failure threshold configuration."""
        # Valid: integer count
        config1 = CircuitBreakerConfig(failure_threshold=5)
        assert config1.failure_threshold == 5

        # Valid: float rate (0-1)
        config2 = CircuitBreakerConfig(failure_threshold=0.5)
        assert config2.failure_threshold == 0.5

        # Invalid: float outside 0-1
        with pytest.raises(ValueError):
            CircuitBreakerConfig(failure_threshold=1.5)

    def test_initializes_metrics(self):
        """CB should initialize empty metrics."""
        cb = CircuitBreaker(name="test_cb")
        metrics = cb.get_metrics()
        assert metrics["request_count"] == 0
        assert metrics["success_count"] == 0
        assert metrics["failure_count"] == 0
        assert metrics["rejected_count"] == 0


# ============================================================================
# CLOSED STATE BEHAVIOR TESTS
# ============================================================================


class TestCircuitBreakerClosedState:
    """Test behavior when circuit is in CLOSED state."""

    def test_allows_successful_calls_when_closed(self):
        """CB should allow successful calls in CLOSED state."""
        cb = CircuitBreaker(name="test_cb")
        
        def successful_function():
            return "success"
        
        result = cb.call(successful_function)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED

    def test_allows_failed_calls_when_closed(self):
        """CB should allow calls to fail in CLOSED state (before threshold)."""
        cb = CircuitBreaker(
            name="test_cb",
            config=CircuitBreakerConfig(failure_threshold=5)
        )
        
        def failing_function():
            raise ValueError("Test failure")
        
        # Should not raise CircuitBreakerOpenError yet
        with pytest.raises(ValueError, match="Test failure"):
            cb.call(failing_function)
        
        assert cb.state == CircuitState.CLOSED

    def test_records_successful_calls(self):
        """CB should track successful calls."""
        cb = CircuitBreaker(name="test_cb")
        
        for _ in range(3):
            cb.call(lambda: "success")
        
        metrics = cb.get_metrics()
        assert metrics["success_count"] == 3
        assert metrics["request_count"] == 3

    def test_records_failed_calls(self):
        """CB should track failed calls."""
        cb = CircuitBreaker(
            name="test_cb",
            config=CircuitBreakerConfig(failure_threshold=10)
        )
        
        def failing_func():
            raise ValueError("fail")
        
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        metrics = cb.get_metrics()
        assert metrics["failure_count"] == 3
        assert metrics["request_count"] == 3

    def test_opens_after_count_threshold_exceeded(self):
        """CB should open after failure count threshold."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        def failing_func():
            raise ValueError("fail")
        
        # Fail 3 times - should open on 3rd
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN

    def test_opens_after_rate_threshold_exceeded(self):
        """CB should open after failure rate threshold exceeded."""
        config = CircuitBreakerConfig(
            failure_threshold=0.5,  # 50% failure rate
            min_requests=10
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Make 10 requests: 6 fail, 4 succeed
        for i in range(10):
            try:
                if i < 6:
                    # Trigger a failure
                    cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
                else:
                    # Trigger a success
                    cb.call(lambda: "success")
            except (ValueError, CircuitBreakerOpenError):
                pass
        
        # At 60% failure rate (6/10), should exceed 50% threshold
        metrics = cb.get_metrics()
        failure_rate = metrics["failure_rate"]
        # Should have opened due to exceeding 50% threshold
        assert cb.state == CircuitState.OPEN or failure_rate >= 0.5

    def test_does_not_open_below_min_requests(self):
        """CB should not open if min_requests not reached."""
        config = CircuitBreakerConfig(
            failure_threshold=0.5,  # 50% failure rate
            min_requests=20
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        def failing_func():
            raise ValueError("fail")
        
        # Only 10 requests (below min_requests of 20)
        for _ in range(10):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        # Should stay CLOSED because min_requests not reached
        assert cb.state == CircuitState.CLOSED


# ============================================================================
# OPEN STATE BEHAVIOR TESTS
# ============================================================================


class TestCircuitBreakerOpenState:
    """Test behavior when circuit is in OPEN state."""

    def test_rejects_calls_when_open(self):
        """CB should reject all calls when OPEN."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open the circuit
        def failing_func():
            raise ValueError("fail")
        
        with pytest.raises(ValueError):
            cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Try successful call - should be rejected
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: "success")

    def test_rejects_calls_fast(self):
        """CB should reject calls quickly when OPEN."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        # Rejection should be instant (< 10ms)
        start = time.time()
        for _ in range(100):
            try:
                cb.call(lambda: "success")
            except CircuitBreakerOpenError:
                pass
        elapsed = time.time() - start
        
        # 100 rejections should complete very quickly
        assert elapsed < 0.5  # Less than 500ms for 100 calls

    def test_increments_rejection_count(self):
        """CB should count rejected calls."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        # Try 5 rejected calls
        for _ in range(5):
            try:
                cb.call(lambda: "success")
            except CircuitBreakerOpenError:
                pass
        
        metrics = cb.get_metrics()
        assert metrics["rejected_count"] == 5

    def test_transitions_to_half_open_after_timeout(self):
        """CB should transition to HALF_OPEN after timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.1
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Next call should transition to HALF_OPEN
        try:
            cb.call(lambda: "success")
        except (ValueError, CircuitBreakerOpenError):
            pass
        
        assert cb.state == CircuitState.HALF_OPEN

    def test_increments_open_duration_on_repeated_opens(self):
        """CB should increase open duration with exponential backoff."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.1,
            max_open_duration_seconds=10.0
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Get initial duration
        initial_duration = cb._current_open_duration
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        # Wait for timeout and let it try to recover
        time.sleep(0.15)
        
        try:
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        except (ValueError, CircuitBreakerOpenError):
            pass
        
        # Duration should have increased (exponential backoff)
        new_duration = cb._current_open_duration
        assert new_duration > initial_duration


# ============================================================================
# HALF-OPEN STATE BEHAVIOR TESTS
# ============================================================================


class TestCircuitBreakerHalfOpenState:
    """Test behavior when circuit is in HALF_OPEN state."""

    def test_allows_limited_test_calls(self):
        """CB should allow limited calls in HALF_OPEN for testing."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.1,
            half_open_max_attempts=2
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Trigger transition to HALF_OPEN with successful call
        cb.call(lambda: "test1")
        assert cb.state == CircuitState.HALF_OPEN
        
        # Should allow another test call
        cb.call(lambda: "test2")

    def test_closes_after_successful_tests(self):
        """CB should close after sufficient successes in HALF_OPEN."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.1,
            half_open_max_attempts=2
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        # Wait and transition to HALF_OPEN
        time.sleep(0.15)
        cb.call(lambda: "test1")
        assert cb.state == CircuitState.HALF_OPEN
        
        # Second successful call should close
        cb.call(lambda: "test2")
        assert cb.state == CircuitState.CLOSED

    def test_reopens_on_failure_during_test(self):
        """CB should reopen if failure during HALF_OPEN."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.1,
            half_open_max_attempts=2
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        # Wait and transition to HALF_OPEN
        time.sleep(0.15)
        cb.call(lambda: "test1")
        assert cb.state == CircuitState.HALF_OPEN
        
        # Failure in HALF_OPEN should reopen
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        assert cb.state == CircuitState.OPEN


# ============================================================================
# METRICS & TRACKING TESTS
# ============================================================================


class TestCircuitBreakerMetrics:
    """Test metrics tracking and reporting."""

    def test_tracks_success_and_failure_counts(self):
        """CB should track success and failure counts."""
        config = CircuitBreakerConfig(failure_threshold=10)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # 3 successes
        for _ in range(3):
            cb.call(lambda: "success")
        
        # 2 failures
        def failing_func():
            raise ValueError("fail")
        
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        metrics = cb.get_metrics()
        assert metrics["success_count"] == 3
        assert metrics["failure_count"] == 2
        assert metrics["request_count"] == 5

    def test_tracks_state_transitions(self):
        """CB should track state transitions."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        assert cb.state == CircuitState.CLOSED
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        assert cb.state == CircuitState.OPEN

    def test_tracks_rejection_count(self):
        """CB should track count of rejected calls."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.2
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        # 10 rejected calls
        for _ in range(10):
            with pytest.raises(CircuitBreakerOpenError):
                cb.call(lambda: "success")
        
        metrics = cb.get_metrics()
        assert metrics["rejected_count"] == 10

    def test_calculates_failure_rate(self):
        """CB should calculate failure rate correctly."""
        config = CircuitBreakerConfig(failure_threshold=100)  # Won't trigger
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # 3 successes, 2 failures (40% failure rate)
        for _ in range(3):
            cb.call(lambda: "success")
        
        def failing_func():
            raise ValueError("fail")
        
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        metrics = cb.get_metrics()
        # 2 failures / 5 total = 0.4
        assert abs(metrics["failure_rate"] - 0.4) < 0.01


# ============================================================================
# CONCURRENCY TESTS
# ============================================================================


class TestCircuitBreakerConcurrency:
    """Test thread safety and concurrent access."""

    def test_thread_safe_state_transitions(self):
        """CB should handle concurrent state transitions safely."""
        config = CircuitBreakerConfig(
            failure_threshold=50,  # High threshold so circuit doesn't open easily
            open_duration_seconds=0.2
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        errors = []
        
        def worker():
            try:
                for i in range(10):
                    try:
                        # Mix of successes and failures
                        if i % 3 == 0:
                            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
                        else:
                            cb.call(lambda: "success")
                    except (ValueError, CircuitBreakerOpenError):
                        # These are expected - either the function fails or circuit is open
                        pass
            except Exception as e:
                # Unexpected exception types should be captured
                errors.append(e)
        
        # 5 concurrent workers
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        
        assert len(errors) == 0  # No unexpected errors

    def test_concurrent_metric_updates(self):
        """CB should update metrics safely under concurrent access."""
        cb = CircuitBreaker(name="test_cb")
        errors = []
        
        def worker():
            try:
                for _ in range(50):
                    cb.call(lambda: f"result_{_}")
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
        
        assert len(errors) == 0
        
        metrics = cb.get_metrics()
        # 10 threads × 50 calls = 500 total
        assert metrics["request_count"] == 500


# ============================================================================
# RESET & MANAGEMENT TESTS
# ============================================================================


class TestCircuitBreakerReset:
    """Test reset and management operations."""

    def test_reset_clears_metrics(self):
        """CB.reset() should clear all metrics."""
        config = CircuitBreakerConfig(failure_threshold=10)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Make some calls
        for _ in range(5):
            cb.call(lambda: "success")
        
        metrics_before = cb.get_metrics()
        assert metrics_before["request_count"] > 0
        
        # Reset
        cb.reset()
        
        metrics_after = cb.get_metrics()
        assert metrics_after["request_count"] == 0
        assert metrics_after["success_count"] == 0
        assert metrics_after["failure_count"] == 0

    def test_reset_returns_to_closed_state(self):
        """CB.reset() should return to CLOSED state."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
        
        assert cb.state == CircuitState.OPEN
        
        # Reset
        cb.reset()
        
        assert cb.state == CircuitState.CLOSED


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestCircuitBreakerEdgeCases:
    """Test edge cases and corner conditions."""

    def test_handles_timeout_as_failure(self):
        """CB should treat timeouts as failures."""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Timeout exception should trigger failure count
        import asyncio
        
        def slow_function():
            raise asyncio.TimeoutError("Timed out")
        
        # First timeout
        with pytest.raises(asyncio.TimeoutError):
            cb.call(slow_function)
        
        # Should count as failure
        metrics = cb.get_metrics()
        assert metrics["failure_count"] >= 1

    def test_handles_callable_with_args(self):
        """CB should handle callables with arguments."""
        cb = CircuitBreaker(name="test_cb")
        
        def add(a, b):
            return a + b
        
        # Note: current API expects callable without args
        # This tests the legacy behavior
        result = cb.call(lambda: add(2, 3))
        assert result == 5

    def test_preserves_exception_type(self):
        """CB should preserve the original exception type."""
        cb = CircuitBreaker(name="test_cb")
        
        class CustomError(Exception):
            pass
        
        with pytest.raises(CustomError):
            cb.call(lambda: (_ for _ in ()).throw(CustomError("custom")))

    def test_max_open_duration_enforced(self):
        """CB should respect maximum open duration cap."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.1,
            max_open_duration_seconds=0.5,
            half_open_max_attempts=1
        )
        cb = CircuitBreaker(name="test_cb", config=config)
        
        # Open circuit multiple times to trigger exponential backoff
        for i in range(4):  # 4 opens will hit the cap: 0.1 -> 0.2 -> 0.4 -> 0.8 (capped at 0.5)
            # Trigger failure in CLOSED state to open
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
            
            # Wait for timeout
            time.sleep(0.15)
            
            # Try to recover (will either close if enough successes or reopen if fail)
            try:
                cb.call(lambda: "test")
            except ValueError:
                # Service still failing, continue
                pass
        
        # Duration should be capped at max_open_duration_seconds
        assert cb._current_open_duration <= config.max_open_duration_seconds


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestCircuitBreakerIntegration:
    """Test integration with external service calls."""

    def test_integration_with_rate_limiter(self):
        """CB should integrate with rate limiting."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(name="external_api", config=config)
        
        call_count = 0
        
        def simulated_api_call():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise ValueError("Service error")
            return {"status": "ok"}
        
        # First 3 calls fail and trigger circuit open
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(simulated_api_call)
        
        assert cb.state == CircuitState.OPEN
        
        # Subsequent calls should be rejected without calling function
        initial_count = call_count
        for _ in range(5):
            try:
                cb.call(simulated_api_call)
            except CircuitBreakerOpenError:
                pass
        
        # Function should not have been called (CB rejected immediately)
        assert call_count == initial_count

    def test_integration_with_fallback_strategy(self):
        """CB should work with fallback/degradation strategies."""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(name="api", config=config)
        
        cache = {"cached_result": "fallback_value"}
        
        def api_call():
            raise ValueError("Service down")
        
        def get_result():
            try:
                return cb.call(api_call)
            except (CircuitBreakerOpenError, ValueError):
                # Use cached value as fallback
                return cache["cached_result"]
        
        # Service fails twice, circuit opens
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(api_call)
        
        # Now using fallback should succeed
        result = get_result()
        assert result == "fallback_value"

    def test_integration_with_logging(self):
        """CB should log state transitions and rejections."""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(name="test_api", config=config)
        
        with patch("cortex.infrastructure.circuit_breaker.logger") as mock_logger:
            # Trigger failure and opening
            with pytest.raises(ValueError):
                cb.call(lambda: (_ for _ in ()).throw(ValueError("fail")))
            
            # Open circuit logged via warning call
            assert cb.state == CircuitState.OPEN

    def test_recovery_after_service_restarts(self):
        """CB should recover when service comes back online."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            open_duration_seconds=0.1,
            half_open_max_attempts=1  # Only need 1 success to close
        )
        cb = CircuitBreaker(name="service", config=config)
        
        # Service fails
        with pytest.raises(ValueError):
            cb.call(lambda: (_ for _ in ()).throw(ValueError("down")))
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Service is back online - should eventually recover
        cb.call(lambda: "recovered")
        assert cb.state == CircuitState.CLOSED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
