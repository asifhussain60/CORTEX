"""
Tests for Retry Handler with Exponential Backoff

AC-NFR-002-02: Automatic retry with exponential backoff
"""

import pytest
import time
from src.infrastructure.retry_handler import (
    RetryHandler,
    RetryConfig,
    RetryPolicy,
    RetryResult,
)


@pytest.fixture
def handler():
    """Create a fresh retry handler."""
    return RetryHandler()


class TestRetryConfig:
    """Test retry configuration validation."""
    
    def test_default_config_valid(self):
        """Test default config is valid."""
        config = RetryConfig()
        config.validate()  # Should not raise
    
    def test_invalid_max_attempts(self):
        """Test invalid max attempts."""
        config = RetryConfig(max_attempts=0)
        with pytest.raises(ValueError):
            config.validate()
    
    def test_invalid_initial_delay(self):
        """Test invalid initial delay."""
        config = RetryConfig(initial_delay=-1)
        with pytest.raises(ValueError):
            config.validate()
    
    def test_invalid_max_delay(self):
        """Test max_delay < initial_delay."""
        config = RetryConfig(initial_delay=10, max_delay=5)
        with pytest.raises(ValueError):
            config.validate()
    
    def test_invalid_backoff_multiplier(self):
        """Test invalid backoff multiplier."""
        config = RetryConfig(backoff_multiplier=1.0)
        with pytest.raises(ValueError):
            config.validate()


class TestRetryHandler:
    """Test retry handler functionality."""
    
    def test_immediate_success(self, handler):
        """Test function that succeeds immediately."""
        def success_fn():
            return "success"
        
        result = handler.execute_with_retry(success_fn)
        assert result.success
        assert result.data == "success"
        assert result.attempts == 1
        assert result.total_delay_seconds == 0.0
    
    def test_success_after_retries(self, handler):
        """Test function that succeeds after failures."""
        attempt_count = 0
        
        def sometimes_fails():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        config = RetryConfig(max_attempts=5, initial_delay=0.01)
        result = handler.execute_with_retry(sometimes_fails, config=config)
        assert result.success
        assert result.data == "success"
        assert result.attempts == 3
    
    def test_exhaust_retries(self, handler):
        """Test function that always fails."""
        def always_fails():
            raise ValueError("Permanent failure")
        
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        result = handler.execute_with_retry(always_fails, config=config)
        assert not result.success
        assert result.attempts == 3
        assert isinstance(result.final_exception, ValueError)
    
    def test_non_retryable_exception(self, handler):
        """Test non-retryable exception stops immediately."""
        def raises_type_error():
            raise TypeError("Non-retryable")
        
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.01,
            retryable_exceptions=(ValueError,)
        )
        result = handler.execute_with_retry(raises_type_error, config=config)
        assert not result.success
        assert result.attempts == 1  # Should stop immediately


class TestExponentialBackoff:
    """Test exponential backoff strategy."""
    
    def test_exponential_backoff_delays(self, handler):
        """Test exponential backoff calculation."""
        config = RetryConfig(
            max_attempts=4,
            initial_delay=0.5,
            backoff_multiplier=2.0,
            policy=RetryPolicy.EXPONENTIAL_BACKOFF
        )
        
        expected_delays = [0.5, 1.0, 2.0]
        for attempt, expected_delay in enumerate(expected_delays, start=1):
            delay = handler._calculate_delay(attempt, config)
            assert delay == expected_delay
    
    def test_exponential_backoff_max_cap(self, handler):
        """Test exponential backoff respects max delay."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=5.0,
            policy=RetryPolicy.EXPONENTIAL_BACKOFF
        )
        
        delay = handler._calculate_delay(5, config)
        assert delay == 5.0  # Capped at max_delay
    
    def test_exponential_total_delay(self, handler):
        """Test total delay accumulated in exponential backoff."""
        attempt_count = 0
        
        def fails_twice():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= 2:
                raise ValueError("Failure")
            return "success"
        
        config = RetryConfig(
            max_attempts=4,
            initial_delay=0.05,
            backoff_multiplier=2.0,
            policy=RetryPolicy.EXPONENTIAL_BACKOFF
        )
        
        result = handler.execute_with_retry(fails_twice, config=config)
        assert result.success
        # Expected delays: 0.05 + 0.1 = 0.15 seconds
        assert result.attempts == 3
        assert result.total_delay_seconds >= 0.14  # Some tolerance


class TestLinearBackoff:
    """Test linear backoff strategy."""
    
    def test_linear_backoff_delays(self, handler):
        """Test linear backoff calculation."""
        config = RetryConfig(
            max_attempts=4,
            initial_delay=0.5,
            policy=RetryPolicy.LINEAR_BACKOFF
        )
        
        expected_delays = [0.5, 1.0, 1.5]
        for attempt, expected_delay in enumerate(expected_delays, start=1):
            delay = handler._calculate_delay(attempt, config)
            assert delay == expected_delay


class TestFixedBackoff:
    """Test fixed delay strategy."""
    
    def test_fixed_delay(self, handler):
        """Test fixed delay calculation."""
        config = RetryConfig(
            max_attempts=4,
            initial_delay=0.5,
            policy=RetryPolicy.FIXED_DELAY
        )
        
        for attempt in range(1, 4):
            delay = handler._calculate_delay(attempt, config)
            assert delay == 0.5


class TestRetryHistory:
    """Test retry history tracking."""
    
    def test_history_recorded(self, handler):
        """Test retry history is recorded."""
        attempt_count = 0
        
        def fails_once():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary")
            return "success"
        
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        handler.execute_with_retry(fails_once, config=config)
        
        history = handler.get_retry_history()
        assert len(history) == 1
        assert history[0][0] == 1  # Attempt number
        assert isinstance(history[0][2], ValueError)
    
    def test_history_cleared(self, handler):
        """Test clearing retry history."""
        attempt_count = 0
        
        def fails_once():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary")
            return "success"
        
        config = RetryConfig(max_attempts=3, initial_delay=0.01)
        handler.execute_with_retry(fails_once, config=config)
        
        assert len(handler.get_retry_history()) > 0
        handler.clear_history()
        assert len(handler.get_retry_history()) == 0


class TestRetryConfigFactories:
    """Test retry config factory methods."""
    
    def test_exponential_config_factory(self):
        """Test exponential config factory."""
        config = RetryHandler.create_exponential_config(
            max_attempts=5,
            initial_delay=0.2
        )
        assert config.policy == RetryPolicy.EXPONENTIAL_BACKOFF
        assert config.max_attempts == 5
        assert config.initial_delay == 0.2
    
    def test_linear_config_factory(self):
        """Test linear config factory."""
        config = RetryHandler.create_linear_config(
            max_attempts=4,
            initial_delay=0.3
        )
        assert config.policy == RetryPolicy.LINEAR_BACKOFF
        assert config.max_attempts == 4
        assert config.initial_delay == 0.3
    
    def test_fixed_config_factory(self):
        """Test fixed config factory."""
        config = RetryHandler.create_fixed_config(
            max_attempts=3,
            delay=0.5
        )
        assert config.policy == RetryPolicy.FIXED_DELAY
        assert config.max_attempts == 3
        assert config.initial_delay == 0.5


class TestRetryResult:
    """Test RetryResult dataclass."""
    
    def test_result_has_timestamp(self):
        """Test result has timestamp."""
        result = RetryResult(success=True)
        assert result.timestamp is not None
    
    def test_result_with_exception(self):
        """Test result stores exception."""
        exc = ValueError("test error")
        result = RetryResult(
            success=False,
            error="test error",
            final_exception=exc,
            attempts=3
        )
        assert result.final_exception is exc
        assert result.attempts == 3
