"""
Tests for Exponential Backoff Retry Strategy.

AC-INFRA-001-04: Retry Logic with Exponential Backoff and Jitter
Tests intelligent retry with exponential backoff, jitter, max attempts,
and idempotency detection.
"""

import pytest
import time
from typing import Callable
from unittest.mock import Mock

from cortex.infrastructure.retry_strategy import (
    RetryStrategy,
    RetryConfig,
    RetryExhaustedError,
    NonRetriableError,
    IdempotencyToken,
)


@pytest.fixture
def retry_config() -> RetryConfig:
    """Create a standard retry configuration."""
    return RetryConfig(
        max_attempts=5,
        initial_delay_ms=100,
        max_delay_ms=5000,
        backoff_multiplier=2.0,
        jitter_factor=0.25,
    )


@pytest.fixture
def retry_strategy(retry_config: RetryConfig) -> RetryStrategy:
    """Create a retry strategy instance."""
    return RetryStrategy(config=retry_config)


class TestRetryConfigValidation:
    """Test retry configuration validation."""

    def test_valid_config(self, retry_config: RetryConfig) -> None:
        """Valid config should pass validation."""
        retry_config.validate()  # Should not raise

    def test_invalid_max_attempts(self) -> None:
        """Max attempts must be positive."""
        with pytest.raises(ValueError, match="max_attempts"):
            RetryConfig(max_attempts=0)

    def test_invalid_delays(self) -> None:
        """Delays must be positive."""
        with pytest.raises(ValueError, match="initial_delay_ms"):
            RetryConfig(initial_delay_ms=0)
        
        with pytest.raises(ValueError, match="max_delay_ms"):
            RetryConfig(max_delay_ms=-1)

    def test_invalid_backoff_multiplier(self) -> None:
        """Backoff multiplier must be >= 1."""
        with pytest.raises(ValueError, match="backoff_multiplier"):
            RetryConfig(backoff_multiplier=0.5)


class TestExponentialBackoff:
    """Test exponential backoff timing."""

    def test_backoff_sequence(self, retry_strategy: RetryStrategy) -> None:
        """Backoff should follow exponential sequence."""
        attempt = 0
        call_count = 0
        
        def flaky_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 4:
                raise ConnectionError("Transient failure")
            return "success"
        
        start = time.time()
        result = retry_strategy.execute(flaky_operation)
        elapsed = time.time() - start
        
        # Should have retried 3 times with exponential backoff
        # 100ms, 200ms, 400ms = ~700ms minimum (but jitter can reduce)
        assert elapsed >= 0.5  # Account for jitter reducing delays
        assert result == "success"
        assert call_count == 4

    def test_delay_doubles_each_attempt(self, retry_strategy: RetryStrategy) -> None:
        """Each retry delay should approximately double."""
        delays = []
        
        for attempt in range(4):
            delay = retry_strategy._calculate_delay(attempt)
            delays.append(delay)
        
        # Check that each delay is roughly double the previous
        # (accounting for jitter which can be ±25%)
        for i in range(1, len(delays)):
            ratio = delays[i] / delays[i-1]
            # Jitter can cause ratios from ~1.2 to ~3.2
            assert 1.0 < ratio < 3.5, f"Delay ratio {ratio} out of range"

    def test_max_delay_enforced(self, retry_strategy: RetryStrategy) -> None:
        """Delay should not exceed maximum."""
        for attempt in range(10):
            delay = retry_strategy._calculate_delay(attempt)
            assert delay <= retry_strategy.config.max_delay_ms / 1000


class TestJitterRandomization:
    """Test jitter prevents thundering herd."""

    def test_jitter_adds_randomness(self, retry_strategy: RetryStrategy) -> None:
        """Same attempt should produce different delays due to jitter."""
        delays = [retry_strategy._calculate_delay(2) for _ in range(10)]
        
        # All delays should be different (very high probability)
        unique_delays = len(set(delays))
        assert unique_delays >= 8, "Jitter should produce varied delays"

    def test_jitter_within_bounds(self, retry_strategy: RetryStrategy) -> None:
        """Jitter should stay within configured factor."""
        base_delay = 400  # ms for attempt 2
        jitter_factor = retry_strategy.config.jitter_factor
        
        delays = [retry_strategy._calculate_delay(2) for _ in range(100)]
        
        for delay in delays:
            delay_ms = delay * 1000
            # Should be within ±25% of base delay
            assert base_delay * (1 - jitter_factor) <= delay_ms <= base_delay * (1 + jitter_factor)


class TestRetriableExceptions:
    """Test transient vs permanent failure detection."""

    def test_retries_transient_errors(self, retry_strategy: RetryStrategy) -> None:
        """Should retry transient errors like ConnectionError."""
        call_count = 0
        
        def flaky_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient")
            return "success"
        
        result = retry_strategy.execute(flaky_operation)
        assert result == "success"
        assert call_count == 3

    def test_retries_timeout_errors(self, retry_strategy: RetryStrategy) -> None:
        """Should retry timeout errors."""
        call_count = 0
        
        def slow_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("Service slow")
            return "success"
        
        result = retry_strategy.execute(slow_operation)
        assert result == "success"
        assert call_count == 2

    def test_does_not_retry_permanent_errors(self, retry_strategy: RetryStrategy) -> None:
        """Should not retry permanent errors like ValueError."""
        call_count = 0
        
        def bad_input_operation() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid input")
        
        with pytest.raises(NonRetriableError, match="Invalid input"):
            retry_strategy.execute(bad_input_operation)
        
        assert call_count == 1  # No retries

    def test_does_not_retry_authentication_errors(self, retry_strategy: RetryStrategy) -> None:
        """Should not retry authentication errors."""
        call_count = 0
        
        def auth_operation() -> str:
            nonlocal call_count
            call_count += 1
            raise PermissionError("Unauthorized")
        
        with pytest.raises(NonRetriableError, match="Unauthorized"):
            retry_strategy.execute(auth_operation)
        
        assert call_count == 1


class TestMaxAttemptsExhaustion:
    """Test retry budget exhaustion."""

    def test_raises_after_max_attempts(self, retry_strategy: RetryStrategy) -> None:
        """Should raise RetryExhaustedError after max attempts."""
        call_count = 0
        
        def always_fails() -> str:
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")
        
        with pytest.raises(RetryExhaustedError) as exc_info:
            retry_strategy.execute(always_fails)
        
        assert call_count == retry_strategy.config.max_attempts
        assert "exhausted" in str(exc_info.value).lower()

    def test_preserves_last_exception(self, retry_strategy: RetryStrategy) -> None:
        """RetryExhaustedError should preserve original exception."""
        def fails_with_message() -> str:
            raise ConnectionError("Specific error message")
        
        with pytest.raises(RetryExhaustedError) as exc_info:
            retry_strategy.execute(fails_with_message)
        
        assert exc_info.value.__cause__ is not None
        assert "Specific error message" in str(exc_info.value.__cause__)


class TestIdempotencyTracking:
    """Test idempotency token handling."""

    def test_generates_idempotency_token(self, retry_strategy: RetryStrategy) -> None:
        """Should generate unique idempotency tokens."""
        token1 = retry_strategy.generate_idempotency_token()
        token2 = retry_strategy.generate_idempotency_token()
        
        assert token1 != token2
        assert len(token1.value) > 0

    def test_tracks_idempotent_operations(self, retry_strategy: RetryStrategy) -> None:
        """Should track operations by idempotency token."""
        call_count = 0
        token = retry_strategy.generate_idempotency_token()
        
        def idempotent_operation(idempotency_token: IdempotencyToken) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient")
            return f"success-{idempotency_token.value}"
        
        result = retry_strategy.execute_with_idempotency(
            lambda: idempotent_operation(token),
            token
        )
        
        assert "success" in result
        assert call_count == 3

    def test_prevents_duplicate_operations(self, retry_strategy: RetryStrategy) -> None:
        """Should detect and prevent duplicate operations."""
        token = retry_strategy.generate_idempotency_token()
        
        def operation(idempotency_token: IdempotencyToken) -> str:
            return f"result-{idempotency_token.value}"
        
        # First call
        result1 = retry_strategy.execute_with_idempotency(
            lambda: operation(token),
            token
        )
        
        # Second call with same token should return cached result
        result2 = retry_strategy.execute_with_idempotency(
            lambda: operation(token),
            token
        )
        
        assert result1 == result2


class TestCustomRetryPolicies:
    """Test custom retry policies."""

    def test_custom_retriable_exceptions(self) -> None:
        """Should respect custom retriable exceptions."""
        config = RetryConfig(
            retriable_exceptions=(RuntimeError,)
        )
        strategy = RetryStrategy(config=config)
        
        call_count = 0
        
        def custom_error_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("Custom retriable")
            return "success"
        
        result = strategy.execute(custom_error_operation)
        assert result == "success"
        assert call_count == 2

    def test_custom_max_attempts(self) -> None:
        """Should respect custom max attempts."""
        config = RetryConfig(max_attempts=2)
        strategy = RetryStrategy(config=config)
        
        call_count = 0
        
        def always_fails() -> str:
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Fail")
        
        with pytest.raises(RetryExhaustedError):
            strategy.execute(always_fails)
        
        assert call_count == 2


class TestRetryMetrics:
    """Test retry metrics tracking."""

    def test_tracks_successful_retries(self, retry_strategy: RetryStrategy) -> None:
        """Should track successful retry operations."""
        call_count = 0
        
        def flaky_operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient")
            return "success"
        
        retry_strategy.execute(flaky_operation)
        
        metrics = retry_strategy.get_metrics()
        assert metrics["total_operations"] >= 1
        assert metrics["successful_operations"] >= 1
        assert metrics["total_retries"] >= 2

    def test_tracks_failed_operations(self, retry_strategy: RetryStrategy) -> None:
        """Should track failed operations."""
        def always_fails() -> str:
            raise ConnectionError("Permanent failure")
        
        try:
            retry_strategy.execute(always_fails)
        except RetryExhaustedError:
            pass
        
        metrics = retry_strategy.get_metrics()
        assert metrics["failed_operations"] >= 1


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_immediate_success(self, retry_strategy: RetryStrategy) -> None:
        """Should handle operations that succeed on first try."""
        call_count = 0
        
        def succeeds_immediately() -> str:
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = retry_strategy.execute(succeeds_immediately)
        assert result == "success"
        assert call_count == 1

    def test_handles_callable_with_return_none(self, retry_strategy: RetryStrategy) -> None:
        """Should handle operations that return None."""
        call_count = 0
        
        def returns_none() -> None:
            nonlocal call_count
            call_count += 1
        
        result = retry_strategy.execute(returns_none)
        assert result is None
        assert call_count == 1

    def test_preserves_exception_traceback(self, retry_strategy: RetryStrategy) -> None:
        """Should preserve original exception traceback."""
        def operation_with_traceback() -> str:
            def inner_function():
                raise ConnectionError("Deep error")
            inner_function()
        
        try:
            retry_strategy.execute(operation_with_traceback)
        except RetryExhaustedError as e:
            # Should have cause chain
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ConnectionError)
