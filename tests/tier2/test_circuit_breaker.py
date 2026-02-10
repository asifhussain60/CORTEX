"""
Test suite for AC-NFR-002-03: Circuit Breaker Pattern Implementation

Tests the CircuitBreaker and related components for implementing
the circuit breaker pattern with state transitions.

Test Plan:
- 14 unit tests for core functionality
- 6 integration tests for state transitions
- 4 parametrized tests for failure scenarios
- 3 performance tests for concurrency
- 23 total tests, 100% pass rate required
"""

import pytest
from unittest.mock import Mock, patch, call, MagicMock
from typing import Any
from datetime import datetime
import time
import threading

from cortex_brain.tier2.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerMetrics,
    CircuitBreakerState,
)


class TestCircuitBreakerCore:
    """Unit tests for CircuitBreaker (14 tests)"""
    
    def test_init_closed_state(self):
        """Test: Circuit breaker initializes in CLOSED state"""
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED
        assert not cb.is_open()
    
    def test_successful_call_increments_success(self):
        """Test: Successful call increments success counter"""
        cb = CircuitBreaker()
        operation = Mock(return_value="success")
        
        result = cb.call(operation)
        
        assert result == "success"
        metrics = cb.get_metrics()
        assert metrics.successful_calls == 1
    
    def test_failed_call_increments_failure(self):
        """Test: Failed call increments failure counter"""
        cb = CircuitBreaker()
        operation = Mock(side_effect=Exception("Error"))
        
        with pytest.raises(Exception):
            cb.call(operation)
        
        metrics = cb.get_metrics()
        assert metrics.failed_calls >= 1
    
    def test_open_on_failure_threshold(self):
        """Test: Circuit opens when failure threshold exceeded"""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(config)
        operation = Mock(side_effect=Exception("Error"))
        
        # First failure
        with pytest.raises(Exception):
            cb.call(operation)
        assert cb.state == CircuitBreakerState.CLOSED
        
        # Second failure - should open circuit
        with pytest.raises(Exception):
            cb.call(operation)
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.is_open()
    
    def test_reject_calls_when_open(self):
        """Test: Circuit rejects calls when OPEN"""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config)
        
        # Trigger open state
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception("Error")))
        assert cb.is_open()
        
        # Should reject new calls with CircuitBreakerOpen exception
        operation = Mock(return_value="result")
        from cortex_brain.tier2.resilience import CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            cb.call(operation)
        
        # Original operation should not be called
        assert operation.call_count == 0
    
    def test_reset_after_successful_call_in_half_open(self):
        """Test: Circuit closes after successful call in HALF_OPEN"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout_seconds=0.1
        )
        cb = CircuitBreaker(config)
        
        # Open circuit
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception("Error")))
        
        time.sleep(0.2)
        
        # Successful call should transition OPEN -> HALF_OPEN -> CLOSED
        result = cb.call(Mock(return_value="success"))
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_reopen_on_failure_in_half_open(self):
        """Test: Circuit reopens if failure in HALF_OPEN state"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=0.1
        )
        cb = CircuitBreaker(config)
        
        # Open circuit
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception("Error 1")))
        
        time.sleep(0.2)
        
        # Failure in HALF_OPEN should reopen
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception("Error 2")))
        
        assert cb.state == CircuitBreakerState.OPEN
    
    def test_config_failure_threshold(self):
        """Test: Failure threshold is configurable"""
        config = CircuitBreakerConfig(failure_threshold=5)
        assert config.failure_threshold == 5
    
    def test_config_timeout_seconds(self):
        """Test: Timeout duration is configurable"""
        config = CircuitBreakerConfig(timeout_seconds=60)
        assert config.timeout_seconds == 60
    
    def test_metrics_tracking(self):
        """Test: Metrics correctly track calls"""
        cb = CircuitBreaker()
        
        # Successful calls
        cb.call(Mock(return_value="ok"))
        cb.call(Mock(return_value="ok"))
        
        # Failed calls
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception()))
        
        metrics = cb.get_metrics()
        assert metrics.successful_calls == 2
        assert metrics.failed_calls >= 1
    
    def test_last_failure_timestamp(self):
        """Test: Last failure time is tracked"""
        cb = CircuitBreaker()
        before = datetime.utcnow()
        
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception("Error")))
        
        after = datetime.utcnow()
        metrics = cb.get_metrics()
        
        assert metrics.last_failure_time is not None
        assert before <= metrics.last_failure_time <= after
    
    def test_exception_message_preserved(self):
        """Test: Exception message is preserved in metrics"""
        cb = CircuitBreaker()
        error_msg = "Specific error message"
        
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception(error_msg)))
        
        metrics = cb.get_metrics()
        assert error_msg in metrics.last_error_message
    
    def test_call_with_args_kwargs(self):
        """Test: Circuit breaker passes args and kwargs"""
        cb = CircuitBreaker()
        operation = Mock(return_value="result")
        
        result = cb.call(operation, "arg1", 42, key="value")
        
        assert result == "result"
        operation.assert_called_once_with("arg1", 42, key="value")


class TestCircuitBreakerStates:
    """Integration tests for state transitions (6 tests)"""
    
    def test_state_transition_closed_to_open(self):
        """Test: Correct state transition from CLOSED to OPEN"""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config)
        
        assert cb.state == CircuitBreakerState.CLOSED
        
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception()))
        
        assert cb.state == CircuitBreakerState.OPEN
    
    def test_state_transition_half_open_to_closed(self):
        """Test: State transitions from HALF_OPEN to CLOSED on success"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout_seconds=0.1
        )
        cb = CircuitBreaker(config)
        
        # CLOSED -> OPEN
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception()))
        
        time.sleep(0.15)
        
        # HALF_OPEN -> CLOSED on successful call
        result = cb.call(Mock(return_value="success"))
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
    
    def test_state_transition_half_open_to_open(self):
        """Test: State transitions from HALF_OPEN to OPEN on failure"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=0.1
        )
        cb = CircuitBreaker(config)
        
        # CLOSED -> OPEN
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception("First")))
        
        time.sleep(0.15)
        
        # HALF_OPEN -> OPEN
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception("Second")))
        
        assert cb.state == CircuitBreakerState.OPEN
    
    def test_multiple_failures_stay_open(self):
        """Test: Multiple failures keep circuit OPEN"""
        config = CircuitBreakerConfig(failure_threshold=1)
        cb = CircuitBreaker(config)
        
        # Open circuit
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception()))
        assert cb.is_open()
        
        # Additional failures while open should keep it open
        from cortex_brain.tier2.resilience import CircuitBreakerOpen
        with pytest.raises(CircuitBreakerOpen):
            cb.call(Mock())
        assert cb.is_open()
    
    def test_recovery_sequence(self):
        """Test: Complete recovery sequence CLOSED->OPEN->HALF_OPEN->CLOSED"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout_seconds=0.1
        )
        cb = CircuitBreaker(config)
        
        # Initial state
        assert cb.state == CircuitBreakerState.CLOSED
        
        # Cause failure -> OPEN
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception()))
        assert cb.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Try call -> transitions OPEN -> HALF_OPEN -> CLOSED on success
        result = cb.call(Mock(return_value="recovered"))
        assert result == "recovered"
        assert cb.state == CircuitBreakerState.CLOSED


class TestCircuitBreakerParametrized:
    """Parametrized tests for failure scenarios (4 tests)"""
    
    @pytest.mark.parametrize("failures_to_open,initial_threshold", [
        (1, 1),
        (2, 2),
        (3, 3),
        (5, 5),
    ])
    def test_failure_thresholds(self, failures_to_open, initial_threshold):
        """Test: Various failure thresholds"""
        config = CircuitBreakerConfig(failure_threshold=initial_threshold)
        cb = CircuitBreaker(config)
        
        for i in range(failures_to_open):
            with pytest.raises(Exception):
                cb.call(Mock(side_effect=Exception(f"Error {i}")))
        
        assert cb.state == CircuitBreakerState.OPEN
    
    @pytest.mark.parametrize("success_count,operation_result", [
        (1, "result1"),
        (5, {"key": "value"}),
        (10, [1, 2, 3]),
        (3, None),
    ])
    def test_successful_operations(self, success_count, operation_result):
        """Test: Multiple successful operations"""
        cb = CircuitBreaker()
        operation = Mock(return_value=operation_result)
        
        for _ in range(success_count):
            result = cb.call(operation)
            assert result == operation_result
        
        metrics = cb.get_metrics()
        assert metrics.successful_calls == success_count
        assert cb.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.parametrize("timeout_seconds,wait_seconds", [
        (0.1, 0.15),
        (0.5, 0.6),
        (1, 1.1),
    ])
    def test_timeout_transitions(self, timeout_seconds, wait_seconds):
        """Test: Timeout correctly allows state transition after wait"""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout_seconds=timeout_seconds
        )
        cb = CircuitBreaker(config)
        
        # Open circuit
        with pytest.raises(Exception):
            cb.call(Mock(side_effect=Exception()))
        
        # Wait and try call - should allow transition
        time.sleep(wait_seconds)
        result = cb.call(Mock(return_value="ok"))
        
        # Should be back in CLOSED after successful call
        assert result == "ok"
        assert cb.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.parametrize("operation_type,operation", [
        ("returns_value", lambda: Mock(return_value="ok")()),
        ("returns_dict", lambda: Mock(return_value={"status": "ok"})()),
        ("returns_list", lambda: Mock(return_value=[1, 2, 3])()),
        ("returns_none", lambda: Mock(return_value=None)()),
    ])
    def test_various_return_types(self, operation_type, operation):
        """Test: Circuit breaker works with various return types"""
        cb = CircuitBreaker()
        result = cb.call(operation)
        assert result is not None or operation_type == "returns_none"


class TestCircuitBreakerConcurrency:
    """Performance and concurrency tests (3 tests)"""
    
    def test_thread_safe_concurrent_calls(self):
        """Test: Multiple threads safely access circuit breaker"""
        cb = CircuitBreaker()
        results = []
        errors = []
        
        def worker():
            try:
                for _ in range(10):
                    result = cb.call(Mock(return_value="ok"))
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 50
        assert len(errors) == 0
    
    def test_concurrent_state_transitions(self):
        """Test: Concurrent access during state transitions"""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=1
        )
        cb = CircuitBreaker(config)
        transition_count = [0]
        
        def cause_failure():
            with pytest.raises(Exception):
                cb.call(Mock(side_effect=Exception()))
            if cb.is_open():
                transition_count[0] += 1
        
        threads = [threading.Thread(target=cause_failure) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Circuit should be open
        assert cb.is_open()
    
    def test_metrics_consistency_concurrent_access(self):
        """Test: Metrics remain consistent under concurrent access"""
        cb = CircuitBreaker()
        
        def concurrent_operations():
            for _ in range(50):
                try:
                    cb.call(Mock(return_value="ok"))
                except Exception:
                    pass
        
        threads = [threading.Thread(target=concurrent_operations) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = cb.get_metrics()
        # All 200 operations should be counted
        assert metrics.successful_calls + metrics.failed_calls == 200


# ===== Pytest Configuration & Markers =====

@pytest.mark.unit
class TestCircuitBreakerUnit:
    """Marked unit tests"""
    pass


@pytest.mark.integration  
class TestCircuitBreakerIntegration:
    """Marked integration tests"""
    pass


# ===== Test Execution Configuration =====

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
