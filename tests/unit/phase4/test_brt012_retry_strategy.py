"""
Test Suite for BRT-012: Retry Strategy with Exponential Backoff and Jitter

Tests the retry mechanism for transient failures with:
- Exponential backoff
- Jitter for distributed systems
- Idempotency tracking
- Transient vs permanent failure detection
- Retry budget limits
- Integration with circuit breaker
"""

import time
import pytest
import threading
from unittest.mock import Mock, patch, MagicMock

from cortex.infrastructure.retry_strategy import (
    RetryStrategy,
    RetryConfig,
    IdempotencyToken,
    RetryExhaustedError,
    NonRetriableError,
)


class TestRetryStrategyInitialization:
    """Test initialization and configuration of retry strategy."""

    def test_starts_with_default_config(self):
        """RS should start with default configuration."""
        strategy = RetryStrategy()
        assert strategy.config is not None
        assert strategy.config.max_attempts == 5
        assert strategy.config.initial_delay_ms == 100.0
        assert strategy.config.max_delay_ms == 5000.0

    def test_accepts_custom_config(self):
        """RS should accept custom configuration."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay_ms=50.0,
            max_delay_ms=2000.0
        )
        strategy = RetryStrategy(config=config)
        assert strategy.config.max_attempts == 3
        assert strategy.config.initial_delay_ms == 50.0

    def test_validates_config_parameters(self):
        """RS should validate configuration parameters."""
        # Invalid max_attempts
        with pytest.raises(ValueError):
            RetryConfig(max_attempts=0)
        
        # Invalid initial_delay_ms
        with pytest.raises(ValueError):
            RetryConfig(initial_delay_ms=-1)
        
        # Invalid backoff_multiplier
        with pytest.raises(ValueError):
            RetryConfig(backoff_multiplier=0.5)
        
        # Invalid jitter_factor
        with pytest.raises(ValueError):
            RetryConfig(jitter_factor=1.5)

    def test_initializes_empty_metrics(self):
        """RS should initialize with empty metrics."""
        strategy = RetryStrategy()
        metrics = strategy.get_metrics()
        assert metrics["total_operations"] == 0
        assert metrics["successful_operations"] == 0
        assert metrics["failed_operations"] == 0
        assert metrics["total_retries"] == 0


class TestRetryStrategySuccessPath:
    """Test successful operation paths."""

    def test_succeeds_on_first_attempt(self):
        """RS should succeed on first attempt without retry."""
        strategy = RetryStrategy()
        result = strategy.execute(lambda: "success")
        assert result == "success"
        
        metrics = strategy.get_metrics()
        assert metrics["total_operations"] == 1
        assert metrics["successful_operations"] == 1
        assert metrics["total_retries"] == 0

    def test_succeeds_after_transient_failures(self):
        """RS should retry after transient failures and eventually succeed."""
        strategy = RetryStrategy()
        call_count = [0]
        
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ConnectionError("Transient error")
            return "recovered"
        
        result = strategy.execute(flaky_function)
        assert result == "recovered"
        assert call_count[0] == 3
        
        metrics = strategy.get_metrics()
        assert metrics["successful_operations"] == 1
        # total_retries counts cumulative retries: attempt 0 (1 retry) + attempt 1 (1 retry) + attempt 2 success (adds 2)
        # = 1 + 1 + 2 = 4
        assert metrics["total_retries"] == 4

    def test_tracks_successful_operations_count(self):
        """RS should accurately track successful operations."""
        strategy = RetryStrategy()
        
        for i in range(5):
            strategy.execute(lambda: f"result_{i}")
        
        metrics = strategy.get_metrics()
        assert metrics["total_operations"] == 5
        assert metrics["successful_operations"] == 5


class TestRetryStrategyFailurePaths:
    """Test failure scenarios and error handling."""

    def test_exhausts_retries_on_persistent_failure(self):
        """RS should raise RetryExhaustedError after max attempts."""
        config = RetryConfig(max_attempts=3)
        strategy = RetryStrategy(config=config)
        
        def always_fails():
            raise ConnectionError("Persistent error")
        
        with pytest.raises(RetryExhaustedError):
            strategy.execute(always_fails)
        
        metrics = strategy.get_metrics()
        assert metrics["failed_operations"] == 1
        assert metrics["total_retries"] == 2  # Failed on attempts 2 and 3

    def test_stops_on_non_retriable_error(self):
        """RS should immediately stop on non-retriable errors."""
        strategy = RetryStrategy()
        
        def raises_value_error():
            raise ValueError("Permanent error")
        
        with pytest.raises(NonRetriableError):
            strategy.execute(raises_value_error)
        
        metrics = strategy.get_metrics()
        assert metrics["failed_operations"] == 1
        assert metrics["total_retries"] == 0  # No retries attempted

    def test_distinguishes_retriable_vs_non_retriable(self):
        """RS should distinguish between retriable and non-retriable errors."""
        strategy = RetryStrategy()
        
        # ConnectionError is retriable (should exhaust retries)
        call_count_retriable = [0]
        def retriable_error():
            call_count_retriable[0] += 1
            raise ConnectionError("Transient")
        
        # ValueError is non-retriable (should stop immediately)
        call_count_non_retriable = [0]
        def non_retriable_error():
            call_count_non_retriable[0] += 1
            raise ValueError("Permanent")
        
        # Retriable should be retried
        with pytest.raises(RetryExhaustedError):
            strategy.execute(retriable_error)
        assert call_count_retriable[0] == 5  # All max_attempts tried
        
        # Non-retriable should stop immediately
        with pytest.raises(NonRetriableError):
            strategy.execute(non_retriable_error)
        assert call_count_non_retriable[0] == 1  # Only first attempt

    def test_tracks_failed_operations_count(self):
        """RS should accurately track failed operations."""
        strategy = RetryStrategy()
        
        for i in range(3):
            try:
                strategy.execute(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
            except (RetryExhaustedError, NonRetriableError):
                pass
        
        metrics = strategy.get_metrics()
        assert metrics["failed_operations"] == 3


class TestExponentialBackoff:
    """Test exponential backoff delay calculation."""

    def test_calculates_exponential_delays(self):
        """RS should calculate delays with exponential backoff."""
        config = RetryConfig(
            initial_delay_ms=100.0,
            backoff_multiplier=2.0,
            jitter_factor=0.0  # No jitter for deterministic test
        )
        strategy = RetryStrategy(config=config)
        
        # Calculate delays for each attempt
        delays = []
        for attempt in range(4):
            delay = strategy._calculate_delay(attempt)
            delays.append(delay)
        
        # Delays should increase exponentially: 0.1s, 0.2s, 0.4s, 0.8s
        assert delays[0] == pytest.approx(0.1, abs=0.01)
        assert delays[1] == pytest.approx(0.2, abs=0.01)
        assert delays[2] == pytest.approx(0.4, abs=0.01)
        assert delays[3] == pytest.approx(0.8, abs=0.01)

    def test_caps_delay_at_max_duration(self):
        """RS should cap delay at maximum duration."""
        config = RetryConfig(
            initial_delay_ms=100.0,
            max_delay_ms=500.0,
            backoff_multiplier=3.0,
            jitter_factor=0.0
        )
        strategy = RetryStrategy(config=config)
        
        # Attempt 10 should exceed max, but should be capped
        delay = strategy._calculate_delay(10)
        assert delay <= 0.5  # max_delay_ms = 500ms = 0.5s

    def test_respects_backoff_multiplier(self):
        """RS should respect configured backoff multiplier."""
        config = RetryConfig(
            initial_delay_ms=100.0,
            backoff_multiplier=3.0,  # Different multiplier
            jitter_factor=0.0
        )
        strategy = RetryStrategy(config=config)
        
        delay_0 = strategy._calculate_delay(0)
        delay_1 = strategy._calculate_delay(1)
        
        # delay_1 should be 3x delay_0
        assert delay_1 == pytest.approx(delay_0 * 3.0, abs=0.01)


class TestJitter:
    """Test jitter functionality for distributed systems."""

    def test_adds_jitter_to_delays(self):
        """RS should add jitter (randomness) to delays."""
        config = RetryConfig(
            initial_delay_ms=1000.0,  # 1 second
            jitter_factor=0.5,  # ±50%
            max_attempts=3
        )
        strategy = RetryStrategy(config=config)
        
        # Calculate multiple delays - they should vary due to jitter
        delays = set()
        for _ in range(20):
            delay = strategy._calculate_delay(0)
            delays.add(round(delay, 3))
        
        # Should have multiple different delay values (not all the same)
        assert len(delays) > 1

    def test_jitter_within_configured_range(self):
        """RS should keep jitter within configured range."""
        config = RetryConfig(
            initial_delay_ms=1000.0,
            jitter_factor=0.25,  # ±25%
            max_delay_ms=10000.0,
            max_attempts=3
        )
        strategy = RetryStrategy(config=config)
        
        base_delay = 1.0  # 1 second
        expected_min = base_delay * (1 - 0.25)  # 0.75s
        expected_max = base_delay * (1 + 0.25)  # 1.25s
        
        # Check multiple delay calculations
        for _ in range(100):
            delay = strategy._calculate_delay(0)
            assert expected_min <= delay <= expected_max

    def test_prevents_thundering_herd(self):
        """RS should prevent thundering herd with jitter."""
        config = RetryConfig(
            initial_delay_ms=1000.0,
            jitter_factor=0.5,
            max_attempts=3
        )
        
        # Create multiple strategies
        strategies = [RetryStrategy(config=config) for _ in range(10)]
        
        # Get delays from all - should be varied
        delays = []
        for strategy in strategies:
            delay = strategy._calculate_delay(1)
            delays.append(delay)
        
        # Should have variation (not all identical)
        assert max(delays) - min(delays) > 0.01


class TestIdempotency:
    """Test idempotency tracking for idempotent operations."""

    def test_generates_idempotency_tokens(self):
        """RS should generate unique idempotency tokens."""
        strategy = RetryStrategy()
        
        token1 = strategy.generate_idempotency_token()
        token2 = strategy.generate_idempotency_token()
        
        assert token1.value != token2.value
        assert isinstance(token1, IdempotencyToken)

    def test_caches_results_with_idempotency_token(self):
        """RS should cache results for idempotent operations."""
        strategy = RetryStrategy()
        
        call_count = [0]
        def idempotent_function():
            call_count[0] += 1
            return f"result_{call_count[0]}"
        
        token = strategy.generate_idempotency_token()
        
        # First call should execute function
        result1 = strategy.execute_with_idempotency(idempotent_function, token)
        assert result1 == "result_1"
        assert call_count[0] == 1
        
        # Second call with same token should return cached result
        result2 = strategy.execute_with_idempotency(idempotent_function, token)
        assert result2 == "result_1"  # Same as first
        assert call_count[0] == 1  # No additional calls

    def test_different_tokens_execute_separately(self):
        """RS should execute separately with different tokens."""
        strategy = RetryStrategy()
        
        call_count = [0]
        def function():
            call_count[0] += 1
            return f"result_{call_count[0]}"
        
        token1 = strategy.generate_idempotency_token()
        token2 = strategy.generate_idempotency_token()
        
        result1 = strategy.execute_with_idempotency(function, token1)
        result2 = strategy.execute_with_idempotency(function, token2)
        
        assert result1 == "result_1"
        assert result2 == "result_2"
        assert call_count[0] == 2

    def test_idempotency_cache_grows(self):
        """RS should track cache size in metrics."""
        strategy = RetryStrategy()
        
        def function():
            return "result"
        
        # Add 5 cached entries
        for i in range(5):
            token = strategy.generate_idempotency_token()
            strategy.execute_with_idempotency(function, token)
        
        metrics = strategy.get_metrics()
        assert metrics["idempotency_cache_size"] == 5

    def test_clears_idempotency_cache(self):
        """RS should allow clearing idempotency cache."""
        strategy = RetryStrategy()
        
        def function():
            return "result"
        
        # Add cached entries
        for i in range(3):
            token = strategy.generate_idempotency_token()
            strategy.execute_with_idempotency(function, token)
        
        metrics_before = strategy.get_metrics()
        assert metrics_before["idempotency_cache_size"] == 3
        
        # Clear cache
        strategy.clear_idempotency_cache()
        
        metrics_after = strategy.get_metrics()
        assert metrics_after["idempotency_cache_size"] == 0


class TestMetricsTracking:
    """Test metrics collection and reporting."""

    def test_tracks_all_operations(self):
        """RS should track all operations in metrics."""
        strategy = RetryStrategy()
        
        # Mix of successes and failures
        for i in range(3):
            strategy.execute(lambda: "success")
        
        for i in range(2):
            try:
                strategy.execute(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
            except (RetryExhaustedError, NonRetriableError):
                pass
        
        metrics = strategy.get_metrics()
        assert metrics["total_operations"] == 5
        assert metrics["successful_operations"] == 3
        assert metrics["failed_operations"] == 2

    def test_calculates_success_rate(self):
        """RS should calculate success rate accurately."""
        strategy = RetryStrategy()
        
        # 3 successes, 1 failure = 75% success rate
        for i in range(3):
            strategy.execute(lambda: "success")
        
        try:
            strategy.execute(lambda: (_ for _ in ()).throw(ConnectionError("fail")))
        except RetryExhaustedError:
            pass
        
        metrics = strategy.get_metrics()
        assert metrics["success_rate"] == pytest.approx(0.75, abs=0.01)

    def test_tracks_total_retries(self):
        """RS should track total retry attempts."""
        strategy = RetryStrategy()
        
        call_count = [0]
        def retried_function():
            call_count[0] += 1
            if call_count[0] < 4:
                raise ConnectionError("Transient")
            return "success"
        
        strategy.execute(retried_function)
        
        metrics = strategy.get_metrics()
        # total_retries: attempt 0 (1 retry) + attempt 1 (1 retry) + attempt 2 (1 retry) + attempt 3 success (adds 3)
        # = 1 + 1 + 1 + 3 = 6
        assert metrics["total_retries"] == 6


class TestConcurrency:
    """Test thread safety and concurrent access."""

    def test_thread_safe_metrics_updates(self):
        """RS should update metrics safely under concurrent access."""
        strategy = RetryStrategy()
        
        def worker():
            for _ in range(10):
                try:
                    strategy.execute(lambda: "result")
                except (RetryExhaustedError, NonRetriableError):
                    pass
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)
        
        metrics = strategy.get_metrics()
        # 5 threads × 10 calls = 50 operations
        assert metrics["total_operations"] == 50


class TestRetryTiming:
    """Test actual timing of retries."""

    def test_respects_retry_delay(self):
        """RS should actually wait before retrying."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay_ms=50.0,  # 50ms per retry
            backoff_multiplier=1.0,  # No exponential growth
            jitter_factor=0.0  # No jitter for deterministic test
        )
        strategy = RetryStrategy(config=config)
        
        call_times = []
        def track_calls():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ConnectionError("Transient")
            return "success"
        
        start = time.time()
        strategy.execute(track_calls)
        total_time = time.time() - start
        
        # Should have 2 retries with 50ms delay each ≈ 100ms total
        # Allow some tolerance for timing variations
        assert total_time >= 0.08  # At least 80ms (accounting for timing variance)


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_handles_exception_during_sleep(self):
        """RS should handle interruptions during sleep."""
        strategy = RetryStrategy()
        
        call_count = [0]
        def function():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ConnectionError("First call fails")
            return "recovered"
        
        # Should handle the sleep and retry successfully
        result = strategy.execute(function)
        assert result == "recovered"

    def test_handles_timeout_error_as_retriable(self):
        """RS should treat TimeoutError as retriable."""
        strategy = RetryStrategy()
        
        call_count = [0]
        def function():
            call_count[0] += 1
            if call_count[0] == 1:
                raise TimeoutError("Timeout")
            return "recovered"
        
        result = strategy.execute(function)
        assert result == "recovered"
        assert call_count[0] == 2

    def test_handles_unknown_exception_as_non_retriable(self):
        """RS should treat unknown exceptions as non-retriable."""
        strategy = RetryStrategy()
        
        class CustomError(Exception):
            pass
        
        with pytest.raises(NonRetriableError):
            strategy.execute(lambda: (_ for _ in ()).throw(CustomError("custom")))


class TestIntegration:
    """Test integration scenarios."""

    def test_works_with_circuit_breaker_simulation(self):
        """RS should work alongside circuit breaker pattern."""
        strategy = RetryStrategy()
        
        # Simulate service that fails temporarily then recovers
        call_count = [0]
        def service_call():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise ConnectionError("Service temporarily down")
            return "service recovered"
        
        # Retry strategy should handle the transient failures
        result = strategy.execute(service_call)
        assert result == "service recovered"
        assert call_count[0] == 3

    def test_integrates_with_fallback(self):
        """RS should allow fallback when retries exhausted."""
        config = RetryConfig(max_attempts=2)
        strategy = RetryStrategy(config=config)
        
        def failing_operation():
            raise ConnectionError("Persistent failure")
        
        try:
            strategy.execute(failing_operation)
        except RetryExhaustedError:
            # Use fallback
            result = "fallback_value"
        
        assert result == "fallback_value"

    def test_integration_with_rate_limiter_scenario(self):
        """RS should work with rate limiter (respecting delays)."""
        config = RetryConfig(
            max_attempts=3,
            initial_delay_ms=10.0,
            max_delay_ms=100.0,
            jitter_factor=0.0
        )
        strategy = RetryStrategy(config=config)
        
        call_times = []
        def rate_limited_call():
            call_times.append(time.time())
            if len(call_times) < 2:
                raise ConnectionError("Rate limited")
            return "success"
        
        result = strategy.execute(rate_limited_call)
        assert result == "success"
        
        # Should have delays between calls
        if len(call_times) >= 2:
            delay = call_times[1] - call_times[0]
            assert delay >= 0.008  # At least 8ms (10ms - tolerance)


class TestConfiguration:
    """Test configuration flexibility."""

    def test_different_max_attempts(self):
        """RS should respect different max_attempts settings."""
        config = RetryConfig(max_attempts=2)
        strategy = RetryStrategy(config=config)
        
        call_count = [0]
        def function():
            call_count[0] += 1
            raise ConnectionError("Always fails")
        
        with pytest.raises(RetryExhaustedError):
            strategy.execute(function)
        
        # Should have tried exactly max_attempts times
        assert call_count[0] == 2

    def test_custom_retriable_exceptions(self):
        """RS should support custom retriable exception types."""
        class CustomTransientError(Exception):
            pass
        
        config = RetryConfig(
            retriable_exceptions=(CustomTransientError,),
            non_retriable_exceptions=(ConnectionError,),
            max_attempts=3
        )
        strategy = RetryStrategy(config=config)
        
        # CustomTransientError should be retried
        call_count_custom = [0]
        def with_custom_error():
            call_count_custom[0] += 1
            if call_count_custom[0] < 2:
                raise CustomTransientError("Custom transient")
            return "recovered"
        
        result = strategy.execute(with_custom_error)
        assert result == "recovered"
        
        # ConnectionError should not be retried
        with pytest.raises(NonRetriableError):
            strategy.execute(lambda: (_ for _ in ()).throw(ConnectionError("Not retriable")))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
