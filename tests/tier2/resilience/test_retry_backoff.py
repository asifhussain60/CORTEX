"""
Test suite for AC-NFR-002-02: Automatic Retry with Exponential Backoff

This test module validates automatic retry mechanisms with exponential backoff,
configurable retry policies, and maximum retry limits.

AC-ID: AC-NFR-002-02
Title: Automatic Retry with Exponential Backoff
Tests Required: 10 unit tests + 4 integration tests = 14 total
"""

import pytest
import time
from typing import Dict, List, Optional, Callable, Any
from unittest.mock import Mock, patch, call
from dataclasses import dataclass
import random


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""
    max_retries: int
    initial_delay: float  # seconds
    max_delay: float  # seconds
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class RetryResult:
    """Result of a retry operation."""
    success: bool
    value: Any = None
    error: Optional[Exception] = None
    attempts: int = 0
    total_delay: float = 0.0


class ExponentialBackoffRetry:
    """Implements exponential backoff retry strategy."""
    
    def __init__(self, policy: RetryPolicy):
        self.policy = policy
        self.attempt_count = 0
        self.total_delay = 0.0
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = self.policy.initial_delay * (
            self.policy.exponential_base ** attempt
        )
        delay = min(delay, self.policy.max_delay)
        
        if self.policy.jitter:
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """
        Determine if retry should happen.
        
        Args:
            attempt: Current attempt number
            error: The error that occurred
            
        Returns:
            True if should retry, False otherwise
        """
        return attempt < self.policy.max_retries
    
    def execute(self, fn: Callable, *args, **kwargs) -> RetryResult:
        """
        Execute function with retries.
        
        Args:
            fn: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            RetryResult with outcome
        """
        self.attempt_count = 0
        self.total_delay = 0.0
        last_error = None
        
        for attempt in range(self.policy.max_retries + 1):
            try:
                self.attempt_count = attempt + 1
                result = fn(*args, **kwargs)
                return RetryResult(
                    success=True,
                    value=result,
                    attempts=self.attempt_count,
                    total_delay=self.total_delay
                )
            except Exception as e:
                last_error = e
                
                if not self.should_retry(attempt, e):
                    break
                
                delay = self.calculate_delay(attempt)
                self.total_delay += delay
                time.sleep(delay)
        
        return RetryResult(
            success=False,
            error=last_error,
            attempts=self.attempt_count,
            total_delay=self.total_delay
        )


class RetryPolicyBuilder:
    """Builder for creating retry policies."""
    
    def __init__(self):
        self.max_retries = 3
        self.initial_delay = 0.1
        self.max_delay = 10.0
        self.exponential_base = 2.0
        self.jitter = True
    
    def with_max_retries(self, n: int) -> "RetryPolicyBuilder":
        self.max_retries = n
        return self
    
    def with_initial_delay(self, delay: float) -> "RetryPolicyBuilder":
        self.initial_delay = delay
        return self
    
    def with_max_delay(self, delay: float) -> "RetryPolicyBuilder":
        self.max_delay = delay
        return self
    
    def with_exponential_base(self, base: float) -> "RetryPolicyBuilder":
        self.exponential_base = base
        return self
    
    def with_jitter(self, enabled: bool) -> "RetryPolicyBuilder":
        self.jitter = enabled
        return self
    
    def build(self) -> RetryPolicy:
        return RetryPolicy(
            max_retries=self.max_retries,
            initial_delay=self.initial_delay,
            max_delay=self.max_delay,
            exponential_base=self.exponential_base,
            jitter=self.jitter
        )


# UNIT TESTS (10 required)

class TestRetryPolicyConfiguration:
    """Test retry policy configuration."""
    
    def test_policy_initialization(self):
        """Test creating a retry policy."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.1,
            max_delay=10.0
        )
        assert policy.max_retries == 3
        assert policy.initial_delay == 0.1
        assert policy.max_delay == 10.0
    
    def test_policy_builder(self):
        """Test building policy with builder."""
        policy = (RetryPolicyBuilder()
                 .with_max_retries(5)
                 .with_initial_delay(0.05)
                 .build())
        
        assert policy.max_retries == 5
        assert policy.initial_delay == 0.05
    
    def test_builder_chainable(self):
        """Test builder fluent API."""
        policy = (RetryPolicyBuilder()
                 .with_max_retries(4)
                 .with_initial_delay(0.2)
                 .with_max_delay(5.0)
                 .with_exponential_base(3.0)
                 .build())
        
        assert policy.max_retries == 4
        assert policy.initial_delay == 0.2
        assert policy.max_delay == 5.0
        assert policy.exponential_base == 3.0


class TestExponentialBackoffCalculation:
    """Test exponential backoff delay calculations."""
    
    def test_initial_delay_first_attempt(self):
        """Test delay for first retry."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.1,
            max_delay=10.0,
            jitter=False
        )
        retry = ExponentialBackoffRetry(policy)
        delay = retry.calculate_delay(0)
        assert delay == pytest.approx(0.1, rel=0.01)
    
    def test_exponential_growth(self):
        """Test exponential delay growth."""
        policy = RetryPolicy(
            max_retries=5,
            initial_delay=0.1,
            max_delay=100.0,
            exponential_base=2.0,
            jitter=False
        )
        retry = ExponentialBackoffRetry(policy)
        
        delays = [retry.calculate_delay(i) for i in range(5)]
        
        # Verify exponential growth: 0.1, 0.2, 0.4, 0.8, 1.6
        assert delays[0] == pytest.approx(0.1)
        assert delays[1] == pytest.approx(0.2)
        assert delays[2] == pytest.approx(0.4)
        assert delays[3] == pytest.approx(0.8)
        assert delays[4] == pytest.approx(1.6)
    
    def test_max_delay_cap(self):
        """Test that delays cap at max_delay."""
        policy = RetryPolicy(
            max_retries=10,
            initial_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=False
        )
        retry = ExponentialBackoffRetry(policy)
        
        # After several attempts, should hit max_delay
        delays = [retry.calculate_delay(i) for i in range(10)]
        assert all(d <= 5.0 for d in delays)
        assert delays[-1] == pytest.approx(5.0)
    
    def test_jitter_adds_variance(self):
        """Test that jitter adds variance to delays."""
        policy = RetryPolicy(
            max_retries=5,
            initial_delay=1.0,
            max_delay=10.0,
            jitter=True
        )
        retry = ExponentialBackoffRetry(policy)
        
        delays = [retry.calculate_delay(2) for _ in range(10)]
        
        # With jitter, delays should vary
        assert len(set(delays)) > 1
        # But should still be in reasonable range
        assert all(d >= 4.0 and d <= 4.4 for d in delays)


class TestRetryExecution:
    """Test retry execution logic."""
    
    def test_successful_first_attempt(self):
        """Test function succeeds on first try."""
        policy = RetryPolicy(max_retries=3, initial_delay=0.01, max_delay=1.0)
        retry = ExponentialBackoffRetry(policy)
        
        fn = Mock(return_value="success")
        result = retry.execute(fn)
        
        assert result.success
        assert result.value == "success"
        assert result.attempts == 1
        assert result.total_delay == 0.0
        fn.assert_called_once()
    
    def test_succeeds_after_retries(self):
        """Test function succeeds after multiple attempts."""
        policy = RetryPolicy(max_retries=5, initial_delay=0.01, max_delay=1.0, jitter=False)
        retry = ExponentialBackoffRetry(policy)
        
        # Fail twice, then succeed
        fn = Mock(side_effect=[ValueError("fail1"), ValueError("fail2"), "success"])
        result = retry.execute(fn)
        
        assert result.success
        assert result.value == "success"
        assert result.attempts == 3
        assert fn.call_count == 3
    
    def test_fails_after_max_retries(self):
        """Test function fails after exhausting retries."""
        policy = RetryPolicy(max_retries=3, initial_delay=0.01, max_delay=1.0)
        retry = ExponentialBackoffRetry(policy)
        
        error = ValueError("persistent failure")
        fn = Mock(side_effect=error)
        result = retry.execute(fn)
        
        assert not result.success
        assert result.error == error
        assert result.attempts == 4  # initial + 3 retries
        assert fn.call_count == 4
    
    def test_should_retry_logic(self):
        """Test retry decision logic."""
        policy = RetryPolicy(max_retries=2, initial_delay=0.1, max_delay=10.0)
        retry = ExponentialBackoffRetry(policy)
        
        assert retry.should_retry(0, ValueError())
        assert retry.should_retry(1, ValueError())
        assert not retry.should_retry(2, ValueError())


class TestRetryPolicies:
    """Test different retry policy configurations."""
    
    def test_aggressive_retry_policy(self):
        """Test aggressive retry policy (more retries)."""
        policy = (RetryPolicyBuilder()
                 .with_max_retries(10)
                 .with_initial_delay(0.01)
                 .build())
        
        assert policy.max_retries == 10
    
    def test_conservative_retry_policy(self):
        """Test conservative retry policy (fewer retries)."""
        policy = (RetryPolicyBuilder()
                 .with_max_retries(1)
                 .with_initial_delay(0.5)
                 .build())
        
        assert policy.max_retries == 1
    
    def test_no_retry_policy(self):
        """Test policy with zero retries."""
        policy = (RetryPolicyBuilder()
                 .with_max_retries(0)
                 .build())
        
        retry = ExponentialBackoffRetry(policy)
        fn = Mock(side_effect=ValueError("fail"))
        result = retry.execute(fn)
        
        assert not result.success
        assert result.attempts == 1


# INTEGRATION TESTS (4 required)

class TestRetryIntegration:
    """Integration tests for retry mechanism."""
    
    def test_retries_with_exponential_backoff(self):
        """Test complete retry with exponential backoff."""
        policy = RetryPolicy(
            max_retries=3,
            initial_delay=0.01,
            max_delay=0.1,
            exponential_base=2.0,
            jitter=False
        )
        retry = ExponentialBackoffRetry(policy)
        
        # Track timing
        call_times = []
        def tracked_fn():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("fail")
            return "success"
        
        result = retry.execute(tracked_fn)
        
        assert result.success
        assert len(call_times) == 3
        # Verify increasing delays between calls
        assert call_times[1] - call_times[0] >= 0.01
        assert call_times[2] - call_times[1] >= 0.02
    
    def test_retry_with_different_exceptions(self):
        """Test retry with various exception types."""
        policy = RetryPolicy(max_retries=5, initial_delay=0.01, max_delay=1.0)
        retry = ExponentialBackoffRetry(policy)
        
        exceptions = [
            ValueError("error 1"),
            RuntimeError("error 2"),
            TimeoutError("error 3"),
            "success"
        ]
        fn = Mock(side_effect=exceptions)
        
        result = retry.execute(fn)
        
        assert result.success
        assert result.value == "success"
        assert result.attempts == 4
    
    def test_retry_respects_max_delay(self):
        """Test that retry respects max delay limit."""
        policy = RetryPolicy(
            max_retries=10,
            initial_delay=1.0,
            max_delay=2.0,
            exponential_base=2.0,
            jitter=False
        )
        retry = ExponentialBackoffRetry(policy)
        
        fn = Mock(side_effect=ValueError("fail"))
        result = retry.execute(fn)
        
        # Should stop early due to max delays
        assert not result.success
        assert result.total_delay < 25.0  # Would be much higher without cap
    
    def test_configurable_policies_produce_different_behaviors(self):
        """Test different policies produce different retry behaviors."""
        aggressive = (RetryPolicyBuilder()
                     .with_max_retries(5)
                     .with_initial_delay(0.01)
                     .build())
        
        conservative = (RetryPolicyBuilder()
                       .with_max_retries(1)
                       .with_initial_delay(0.5)
                       .build())
        
        aggressive_retry = ExponentialBackoffRetry(aggressive)
        conservative_retry = ExponentialBackoffRetry(conservative)
        
        fn = Mock(side_effect=ValueError("fail"))
        
        result_aggressive = aggressive_retry.execute(fn)
        aggressive_attempts = result_aggressive.attempts
        
        fn.reset_mock()
        result_conservative = conservative_retry.execute(fn)
        conservative_attempts = result_conservative.attempts
        
        assert aggressive_attempts > conservative_attempts


# Performance test

class TestRetryPerformance:
    """Performance tests for retry mechanism."""
    
    def test_delay_calculation_performance(self):
        """Test delay calculation is fast."""
        import time
        policy = RetryPolicy(
            max_retries=100,
            initial_delay=0.1,
            max_delay=10.0
        )
        retry = ExponentialBackoffRetry(policy)
        
        start = time.time()
        for i in range(10000):
            retry.calculate_delay(i % 100)
        elapsed = time.time() - start
        
        assert elapsed < 1.0  # Should complete in < 1 second


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
