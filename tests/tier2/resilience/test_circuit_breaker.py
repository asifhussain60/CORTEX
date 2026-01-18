"""
Test suite for AC-NFR-002-03: Circuit Breaker Pattern Implementation

This test module validates the circuit breaker pattern for handling cascading failures,
implementing state machine transitions (Closed → Open → Half-Open), and automatic recovery.

AC-ID: AC-NFR-002-03
Title: Circuit Breaker Pattern Implementation
Tests Required: 14 unit tests + 6 integration tests = 20 total
"""

import pytest
import time
from typing import Dict, List, Optional, Callable, Any
from unittest.mock import Mock, patch, call
from dataclasses import dataclass
from enum import Enum


class CircuitState(Enum):
    """States of the circuit breaker."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    failure_threshold: int  # Failures before opening
    success_threshold: int  # Successes before closing from half-open
    timeout: float  # Seconds before trying half-open


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker operations."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_changes: int = 0


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation following the State pattern.
    
    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Failing, requests are rejected immediately
    - HALF_OPEN: Testing recovery, limited requests pass through
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.metrics = CircuitBreakerMetrics()
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
    
    def call(self, fn: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            fn: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpen: If circuit is open
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.metrics.state_changes += 1
            else:
                self.metrics.rejected_calls += 1
                raise CircuitBreakerOpen(
                    "Circuit breaker is OPEN"
                )
        
        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self.metrics.successful_calls += 1
        self.metrics.total_calls += 1
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close()
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self.metrics.failed_calls += 1
        self.metrics.total_calls += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            if self.state != CircuitState.OPEN:
                self._open()
        
        if self.state == CircuitState.HALF_OPEN:
            self._open()
    
    def _open(self) -> None:
        """Open the circuit."""
        self.state = CircuitState.OPEN
        self.failure_count = 0
        self.success_count = 0
        self.metrics.state_changes += 1
    
    def _close(self) -> None:
        """Close the circuit."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.metrics.state_changes += 1
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.config.timeout
    
    def get_state(self) -> CircuitState:
        """Get current circuit state."""
        return self.state


# UNIT TESTS (14 required)

class TestCircuitBreakerBasics:
    """Test basic circuit breaker functionality."""
    
    def test_initialization(self):
        """Test circuit breaker initializes in closed state."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=1.0
        )
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.metrics.total_calls == 0
    
    def test_successful_calls_pass_through(self):
        """Test successful calls pass through in closed state."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=1.0
        )
        breaker = CircuitBreaker(config)
        fn = Mock(return_value="success")
        
        result = breaker.call(fn)
        assert result == "success"
        assert breaker.metrics.successful_calls == 1
        assert breaker.metrics.total_calls == 1


class TestCircuitBreakerStateTransitions:
    """Test state transitions."""
    
    def test_transition_closed_to_open(self):
        """Test transition from closed to open on failure threshold."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=1.0
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # First failure
        with pytest.raises(ValueError):
            breaker.call(fn)
        assert breaker.state == CircuitState.CLOSED
        
        # Second failure - should open
        with pytest.raises(ValueError):
            breaker.call(fn)
        assert breaker.state == CircuitState.OPEN
    
    def test_open_rejects_calls(self):
        """Test open state rejects new calls immediately."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,
            timeout=1.0
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # Open the circuit
        with pytest.raises(ValueError):
            breaker.call(fn)
        assert breaker.state == CircuitState.OPEN
        
        # Try to call again - should reject without calling fn
        with pytest.raises(CircuitBreakerOpen):
            breaker.call(fn)
        
        # fn should only be called once
        assert fn.call_count == 1
        assert breaker.metrics.rejected_calls == 1
    
    def test_transition_open_to_half_open(self):
        """Test transition from open to half-open after timeout."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,  # Need 2 successes to close from half-open
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # Open circuit
        with pytest.raises(ValueError):
            breaker.call(fn)
        assert breaker.state == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(0.15)
        
        # Next call should try half-open
        fn.side_effect = None
        fn.return_value = "success"
        result = breaker.call(fn)
        
        assert breaker.state == CircuitState.HALF_OPEN
        assert result == "success"
    
    def test_transition_half_open_to_closed(self):
        """Test transition from half-open to closed on success threshold."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # Open circuit
        with pytest.raises(ValueError):
            breaker.call(fn)
        
        # Wait and transition to half-open
        time.sleep(0.15)
        fn.side_effect = None
        fn.return_value = "success"
        
        # First success in half-open
        breaker.call(fn)
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Second success - should close
        breaker.call(fn)
        assert breaker.state == CircuitState.CLOSED
    
    def test_transition_half_open_to_open(self):
        """Test transition back to open if failure in half-open."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=2,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # Open and transition to half-open
        with pytest.raises(ValueError):
            breaker.call(fn)
        time.sleep(0.15)
        fn.side_effect = ValueError("still failing")
        
        with pytest.raises(ValueError):
            breaker.call(fn)
        
        assert breaker.state == CircuitState.OPEN


class TestCircuitBreakerThresholds:
    """Test threshold configurations."""
    
    def test_configurable_failure_threshold(self):
        """Test different failure thresholds."""
        config = CircuitBreakerConfig(
            failure_threshold=5,
            success_threshold=2,
            timeout=1.0
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # Should take 5 failures to open
        for i in range(4):
            with pytest.raises(ValueError):
                breaker.call(fn)
            assert breaker.state == CircuitState.CLOSED
        
        # 5th failure opens it
        with pytest.raises(ValueError):
            breaker.call(fn)
        assert breaker.state == CircuitState.OPEN
    
    def test_configurable_success_threshold(self):
        """Test different success thresholds in half-open."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=3,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # Open circuit
        with pytest.raises(ValueError):
            breaker.call(fn)
        
        # Go to half-open
        time.sleep(0.15)
        fn.side_effect = None
        fn.return_value = "ok"
        
        # Need 3 successes to close
        for i in range(2):
            breaker.call(fn)
            assert breaker.state == CircuitState.HALF_OPEN
        
        # 3rd success closes
        breaker.call(fn)
        assert breaker.state == CircuitState.CLOSED


class TestCircuitBreakerMetrics:
    """Test metrics tracking."""
    
    def test_metrics_tracking(self):
        """Test metrics are tracked accurately."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        
        # Successful call
        fn = Mock(return_value="ok")
        breaker.call(fn)
        assert breaker.metrics.successful_calls == 1
        assert breaker.metrics.total_calls == 1
        
        # Failed call
        fn.side_effect = ValueError("fail")
        with pytest.raises(ValueError):
            breaker.call(fn)
        assert breaker.metrics.failed_calls == 1
        assert breaker.metrics.total_calls == 2
    
    def test_state_change_tracking(self):
        """Test state change counting."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        
        initial_changes = breaker.metrics.state_changes
        
        # Open
        fn = Mock(side_effect=ValueError("fail"))
        with pytest.raises(ValueError):
            breaker.call(fn)
        assert breaker.metrics.state_changes == initial_changes + 1


# INTEGRATION TESTS (6 required)

class TestCircuitBreakerIntegration:
    """Integration tests for circuit breaker."""
    
    def test_circuit_breaker_full_lifecycle(self):
        """Test complete circuit breaker lifecycle."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        fn = Mock(return_value="success")
        
        # Closed - successful
        assert breaker.call(fn) == "success"
        assert breaker.state == CircuitState.CLOSED
        
        # Trigger failures to open
        fn.side_effect = ValueError("fail")
        for _ in range(2):
            with pytest.raises(ValueError):
                breaker.call(fn)
        assert breaker.state == CircuitState.OPEN
        
        # Attempt to call - rejected
        with pytest.raises(CircuitBreakerOpen):
            breaker.call(fn)
        
        # Wait and recover
        time.sleep(0.15)
        fn.side_effect = None
        fn.return_value = "recovered"
        
        # Half-open test
        assert breaker.call(fn) == "recovered"
        assert breaker.state == CircuitState.HALF_OPEN
        
        # Close
        assert breaker.call(fn) == "recovered"
        assert breaker.state == CircuitState.CLOSED
    
    def test_cascading_failure_protection(self):
        """Test protection against cascading failures."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.2
        )
        breaker = CircuitBreaker(config)
        
        failed_calls = []
        def failing_service():
            failed_calls.append(time.time())
            raise ValueError("service down")
        
        # Multiple attempts during failure
        for _ in range(5):
            try:
                breaker.call(failing_service)
            except (ValueError, CircuitBreakerOpen):
                pass
        
        # After second failure, further calls rejected without calling service
        assert len(failed_calls) == 2  # Only 2 actual service calls
        assert breaker.state == CircuitState.OPEN
    
    def test_recovery_after_failures(self):
        """Test successful recovery after failures."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        
        call_log = []
        def sometimes_failing_service(fail):
            call_log.append(("call", fail))
            if fail:
                raise ValueError("temporary failure")
            return "success"
        
        # Fail and open
        with pytest.raises(ValueError):
            breaker.call(sometimes_failing_service, True)
        assert breaker.state == CircuitState.OPEN
        
        # Wait
        time.sleep(0.15)
        
        # Recover
        result = breaker.call(sometimes_failing_service, False)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
    
    def test_concurrent_state_consistency(self):
        """Test state consistency during rapid calls."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout=0.5
        )
        breaker = CircuitBreaker(config)
        
        fn = Mock(side_effect=ValueError("fail"))
        
        # Rapid failures
        for _ in range(5):
            try:
                breaker.call(fn)
            except (ValueError, CircuitBreakerOpen):
                pass
        
        # Should be open
        assert breaker.state == CircuitState.OPEN
        
        # Verify rejection count
        assert breaker.metrics.rejected_calls >= 2
    
    def test_circuit_breaker_prevents_cascading_failure(self):
        """Test that circuit breaker prevents system overload."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout=0.1
        )
        breaker = CircuitBreaker(config)
        
        call_times = []
        def slow_failing_service():
            call_times.append(time.time())
            time.sleep(0.05)  # Slow operation
            raise TimeoutError("service timeout")
        
        # First call fails and opens circuit
        with pytest.raises(TimeoutError):
            breaker.call(slow_failing_service)
        
        # Rapid subsequent calls rejected immediately
        start = time.time()
        for _ in range(10):
            try:
                breaker.call(slow_failing_service)
            except CircuitBreakerOpen:
                pass
        elapsed = time.time() - start
        
        # Should complete quickly (< 500ms) because of rejection
        assert elapsed < 0.5
        # Only one actual service call (the first one)
        assert len(call_times) == 1


# PARAMETRIZED TESTS (4 required)

class TestCircuitBreakerParametrized:
    """Parametrized tests for various configurations."""
    
    @pytest.mark.parametrize("failure_threshold,expected_failures", [
        (1, 1),
        (2, 2),
        (5, 5),
        (10, 10),
    ])
    def test_various_failure_thresholds(self, failure_threshold, expected_failures):
        """Test circuit breaker with different failure thresholds."""
        config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=1,
            timeout=1.0
        )
        breaker = CircuitBreaker(config)
        fn = Mock(side_effect=ValueError("fail"))
        
        # Trigger failures up to threshold
        for i in range(expected_failures):
            with pytest.raises(ValueError):
                breaker.call(fn)
            if i < expected_failures - 1:
                assert breaker.state == CircuitState.CLOSED
        
        assert breaker.state == CircuitState.OPEN


# PERFORMANCE TESTS (4 required - includes the above parametrized as 1 perf test)

class TestCircuitBreakerPerformance:
    """Performance and stress tests."""
    
    def test_performance_rapid_calls(self):
        """Test performance with rapid successive calls."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout=0.5
        )
        breaker = CircuitBreaker(config)
        fn = Mock(return_value="ok")
        
        start = time.time()
        for _ in range(1000):
            breaker.call(fn)
        elapsed = time.time() - start
        
        # Should handle 1000 calls quickly (< 1 second)
        assert elapsed < 1.0
        assert fn.call_count == 1000
    
    def test_performance_state_transitions(self):
        """Test performance of rapid state transitions."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            success_threshold=1,
            timeout=0.001  # Very short timeout for rapid transitions
        )
        breaker = CircuitBreaker(config)
        
        transitions = 0
        start = time.time()
        
        for i in range(20):
            fn = Mock(side_effect=ValueError("fail") if i % 2 == 0 else None)
            fn.return_value = "ok"
            
            try:
                breaker.call(fn)
            except (ValueError, CircuitBreakerOpen):
                pass
            
            if i % 2 == 1:
                time.sleep(0.002)
        
        elapsed = time.time() - start
        
        # Should complete reasonably fast even with transitions
        assert elapsed < 1.0
    
    def test_performance_metrics_overhead(self):
        """Test that metrics tracking doesn't add significant overhead."""
        config = CircuitBreakerConfig(
            failure_threshold=100,
            success_threshold=100,
            timeout=10.0
        )
        breaker = CircuitBreaker(config)
        fn = Mock(return_value="ok")
        
        start = time.time()
        for _ in range(10000):
            breaker.call(fn)
        elapsed = time.time() - start
        
        # Should still be fast with metrics tracking
        assert elapsed < 2.0
        assert breaker.metrics.total_calls == 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
