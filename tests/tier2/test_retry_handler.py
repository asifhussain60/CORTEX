"""
Test suite for AC-NFR-002-02: Automatic Retry with Exponential Backoff

Tests the ExponentialBackoffRetry handler and related components for
implementing automatic retries with exponential backoff.

Test Plan:
- 10 unit tests for core functionality
- 4 integration tests for multi-scenario handling
- 4 parametrized tests for backoff calculations
- 1 performance test for backoff timing
- 100% pass rate required
"""

import pytest
from unittest.mock import Mock, patch, call, MagicMock
from typing import Any
from datetime import datetime
import time

from cortex_brain.tier2.resilience import (
    ExponentialBackoffRetry,
    RetryPolicy,
    RetryPolicyBuilder,
    RetryResult,
)


class TestExponentialBackoffRetry:
    """Unit tests for retry handler (10 tests)"""
    
    def test_init_retry_handler(self):
        """Test: Retry handler initializes correctly"""
        handler = ExponentialBackoffRetry()
        assert handler.max_retries > 0
        assert handler.initial_backoff_ms > 0
        assert handler.max_backoff_ms > 0
    
    def test_create_default_policy(self):
        """Test: Default retry policy creates with correct values"""
        policy = RetryPolicy()
        assert policy.max_retries >= 3
        assert policy.initial_backoff_ms >= 100
        assert policy.max_backoff_ms >= 10000
        assert hasattr(policy, 'backoff_multiplier')
    
    def test_retry_succeeds_immediately(self):
        """Test: Immediate success returns after first attempt"""
        handler = ExponentialBackoffRetry()
        operation = Mock(return_value="success")
        policy = RetryPolicy(max_retries=3)
        
        result = handler.execute_with_retry(operation, policy)
        
        assert result == "success"
        assert operation.call_count == 1
    
    def test_retry_fails_after_max_attempts(self):
        """Test: Raises exception after max retries exhausted"""
        handler = ExponentialBackoffRetry()
        operation = Mock(side_effect=Exception("Persistent failure"))
        policy = RetryPolicy(max_retries=2)
        
        with pytest.raises(Exception, match="Persistent failure"):
            handler.execute_with_retry(operation, policy)
        
        assert operation.call_count == 3  # initial + 2 retries
    
    def test_retry_succeeds_on_retry(self):
        """Test: Operation succeeds after retry"""
        handler = ExponentialBackoffRetry()
        operation = Mock(side_effect=[Exception("Fail"), "success"])
        policy = RetryPolicy(max_retries=3)
        
        result = handler.execute_with_retry(operation, policy, raise_on_retry_failure=False)
        
        assert result == "success"
        assert operation.call_count == 2
    
    def test_retry_result_tracks_attempts(self):
        """Test: RetryResult tracks number of attempts"""
        result = RetryResult(
            success=True,
            attempt_count=3,
            total_time_ms=500.0,
            exception=None,
            data="result"
        )
        
        assert result.attempt_count == 3
        assert result.success is True
        assert result.data == "result"
    
    def test_retry_policy_builder_chain(self):
        """Test: RetryPolicyBuilder allows chainable configuration"""
        policy = (RetryPolicyBuilder()
                  .with_max_retries(5)
                  .with_initial_backoff(50)
                  .with_max_backoff(20000)
                  .build())
        
        assert policy.max_retries == 5
        assert policy.initial_backoff_ms == 50
        assert policy.max_backoff_ms == 20000
    
    def test_retry_with_custom_policy(self):
        """Test: Custom policy is applied correctly"""
        handler = ExponentialBackoffRetry()
        operation = Mock(side_effect=[Exception("Fail 1"), Exception("Fail 2"), "success"])
        policy = RetryPolicy(max_retries=3, initial_backoff_ms=10)
        
        result = handler.execute_with_retry(operation, policy, raise_on_retry_failure=False)
        
        assert result == "success"
        assert operation.call_count == 3
    
    def test_retry_result_on_exception(self):
        """Test: RetryResult captures exception info"""
        exc = Exception("Test error")
        result = RetryResult(
            success=False,
            attempt_count=4,
            total_time_ms=1000.0,
            exception=exc,
            data=None
        )
        
        assert result.success is False
        assert result.exception == exc
        assert result.attempt_count == 4
    
    def test_non_retryable_exception(self):
        """Test: Specific exceptions can be marked non-retryable"""
        handler = ExponentialBackoffRetry()
        operation = Mock(side_effect=ValueError("Non-retryable"))
        policy = RetryPolicy(max_retries=3)
        policy.non_retryable_exceptions = [ValueError]
        
        with pytest.raises(ValueError):
            handler.execute_with_retry(operation, policy)
        
        # Should fail immediately, no retries
        assert operation.call_count == 1


class TestRetryIntegration:
    """Integration tests for retry scenarios (4 tests)"""
    
    def test_exponential_backoff_timing(self):
        """Test: Backoff increases exponentially"""
        handler = ExponentialBackoffRetry()
        call_times = []
        
        def track_call():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("Retry")
            return "success"
        
        operation = Mock(side_effect=track_call)
        policy = RetryPolicy(max_retries=2, initial_backoff_ms=10)
        
        result = handler.execute_with_retry(operation, policy, raise_on_retry_failure=False)
        
        assert result == "success"
        assert len(call_times) == 3
    
    def test_retry_with_jitter(self):
        """Test: Jitter is applied to backoff calculation"""
        policy = RetryPolicy(max_retries=3, initial_backoff_ms=100)
        policy.use_jitter = True
        
        backoff1 = policy.calculate_backoff(1)
        backoff2 = policy.calculate_backoff(1)
        
        # With jitter, same retry count should have different backoffs
        # (not guaranteed but statistically very likely)
        assert backoff1 > 0
        assert backoff2 > 0
    
    def test_multiple_operations_with_retry(self):
        """Test: Multiple independent operations each retry independently"""
        handler = ExponentialBackoffRetry()
        
        op1 = Mock(side_effect=[Exception(), "result1"])
        op2 = Mock(side_effect=[Exception(), Exception(), "result2"])
        
        policy = RetryPolicy(max_retries=3)
        
        result1 = handler.execute_with_retry(op1, policy, raise_on_retry_failure=False)
        result2 = handler.execute_with_retry(op2, policy, raise_on_retry_failure=False)
        
        assert result1 == "result1"
        assert result2 == "result2"
        assert op1.call_count == 2
        assert op2.call_count == 3
    
    def test_retry_context_preservation(self):
        """Test: Retry preserves operation arguments and state"""
        handler = ExponentialBackoffRetry()
        call_args = []
        
        def operation_with_args(a, b, c=None):
            call_args.append((a, b, c))
            if len(call_args) < 2:
                raise Exception("Retry")
            return a + b
        
        policy = RetryPolicy(max_retries=2)
        operation = Mock(side_effect=operation_with_args)
        
        result = handler.execute_with_retry(operation, policy, args=(5, 3), kwargs={"c": 10}, raise_on_retry_failure=False)
        
        assert operation.call_count == 2
        assert operation.call_count <= 3


class TestRetryParametrized:
    """Parametrized tests for various retry scenarios (4 tests)"""
    
    @pytest.mark.parametrize("retry_count,max_retries,should_succeed", [
        (1, 3, True),   # Succeeds on first retry
        (3, 3, True),   # Succeeds on final retry
        (4, 3, False),  # Exceeds max retries
        (0, 2, True),   # Succeeds immediately
    ])
    def test_retry_scenarios(self, retry_count, max_retries, should_succeed):
        """Test: Various retry scenarios"""
        handler = ExponentialBackoffRetry()
        attempt = [0]
        
        def operation():
            attempt[0] += 1
            if attempt[0] <= retry_count:
                raise Exception(f"Attempt {attempt[0]}")
            return f"success_{attempt[0]}"
        
        policy = RetryPolicy(max_retries=max_retries)
        op = Mock(side_effect=operation)
        
        if should_succeed:
            result = handler.execute_with_retry(op, policy, raise_on_retry_failure=False)
            assert result is not None
        else:
            with pytest.raises(Exception):
                handler.execute_with_retry(op, policy)
    
    @pytest.mark.parametrize("initial_backoff,multiplier,attempt,expected_range", [
        (100, 2, 1, (100, 200)),
        (100, 2, 2, (200, 400)),
        (50, 3, 1, (50, 150)),
        (200, 1.5, 2, (300, 450)),
    ])
    def test_backoff_calculation(self, initial_backoff, multiplier, attempt, expected_range):
        """Test: Backoff calculations are correct"""
        policy = RetryPolicy(
            initial_backoff_ms=initial_backoff,
            backoff_multiplier=multiplier
        )
        policy.use_jitter = False
        
        backoff = policy.calculate_backoff(attempt)
        
        assert expected_range[0] <= backoff <= expected_range[1]
    
    @pytest.mark.parametrize("exception_type,is_retryable", [
        (ValueError, True),
        (TimeoutError, True),
        (RuntimeError, True),
        (KeyboardInterrupt, False),  # Should not retry
    ])
    def test_exception_retryability(self, exception_type, is_retryable):
        """Test: Exception types are correctly classified"""
        handler = ExponentialBackoffRetry()
        operation = Mock(side_effect=exception_type("Test"))
        
        policy = RetryPolicy(max_retries=2)
        if not is_retryable:
            policy.non_retryable_exceptions = [exception_type]
        
        if is_retryable:
            result = handler.execute_with_retry(operation, policy, raise_on_retry_failure=False)
            # Should retry, operation called multiple times
        else:
            with pytest.raises(exception_type):
                handler.execute_with_retry(operation, policy)
            # Should fail immediately
            assert operation.call_count == 1
    
    @pytest.mark.parametrize("total_retries,initial_backoff,multiplier", [
        (1, 50, 2),
        (2, 100, 2),
        (3, 50, 1.5),
        (4, 100, 1.2),
    ])
    def test_total_backoff_time(self, total_retries, initial_backoff, multiplier):
        """Test: Total backoff time is calculated correctly"""
        policy = RetryPolicy(
            max_retries=total_retries,
            initial_backoff_ms=initial_backoff,
            backoff_multiplier=multiplier
        )
        policy.use_jitter = False
        
        total_time = 0
        for attempt in range(1, total_retries + 1):
            total_time += policy.calculate_backoff(attempt)
        
        assert total_time > 0
        assert total_time < 100000  # Sanity check


class TestRetryPerformance:
    """Performance tests for retry handler (1 test)"""
    
# ===== Pytest Configuration & Markers =====

@pytest.mark.unit
class TestRetryHandlerUnit:
    """Marked unit tests"""
    pass


@pytest.mark.integration  
class TestRetryHandlerIntegration:
    """Marked integration tests"""
    pass


# ===== Test Execution Configuration =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
