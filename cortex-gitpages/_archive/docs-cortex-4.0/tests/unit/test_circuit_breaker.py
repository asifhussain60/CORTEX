"""
Tests for Circuit Breaker Pattern

AC-NFR-002-03: Circuit breaker pattern implemented
"""

import pytest
import time
from src.infrastructure.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitBreakerMetrics,
    CircuitBreakerResult,
)


@pytest.fixture
def config():
    """Create a circuit breaker config for testing."""
    return CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=1.0
    )


@pytest.fixture
def breaker(config):
    """Create a circuit breaker for testing."""
    return CircuitBreaker("test_breaker", config)


class TestCircuitBreakerConfig:
    """Test circuit breaker configuration."""
    
    def test_default_config_valid(self):
        """Test default config is valid."""
        config = CircuitBreakerConfig()
        config.validate()  # Should not raise
    
    def test_invalid_failure_threshold(self):
        """Test invalid failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=0)
        with pytest.raises(ValueError):
            config.validate()
    
    def test_invalid_success_threshold(self):
        """Test invalid success threshold."""
        config = CircuitBreakerConfig(success_threshold=0)
        with pytest.raises(ValueError):
            config.validate()
    
    def test_invalid_timeout(self):
        """Test invalid timeout."""
        config = CircuitBreakerConfig(timeout_seconds=0)
        with pytest.raises(ValueError):
            config.validate()


class TestCircuitBreakerStates:
    """Test circuit breaker state transitions."""
    
    def test_initial_state_closed(self, breaker):
        """Test circuit starts in CLOSED state."""
        assert breaker.get_state() == CircuitState.CLOSED
    
    def test_transition_to_open_on_failures(self, breaker):
        """Test circuit opens after threshold failures."""
        def failing_fn():
            raise ValueError("Service error")
        
        # Cause failures below threshold
        for _ in range(2):
            breaker.call(failing_fn)
        assert breaker.get_state() == CircuitState.CLOSED
        
        # Cause failure that reaches threshold
        breaker.call(failing_fn)
        assert breaker.get_state() == CircuitState.OPEN
    
    def test_reject_calls_when_open(self, breaker):
        """Test calls are rejected when circuit is open."""
        def failing_fn():
            raise ValueError("Service error")
        
        # Open the circuit
        for _ in range(breaker.config.failure_threshold):
            breaker.call(failing_fn)
        assert breaker.get_state() == CircuitState.OPEN
        
        # Subsequent calls should be rejected without executing
        result = breaker.call(lambda: "success")
        assert not result.success
        assert result.call_rejected
        assert result.circuit_state == CircuitState.OPEN
    
    def test_transition_to_half_open_after_timeout(self, breaker):
        """Test circuit goes to HALF_OPEN after timeout."""
        def failing_fn():
            raise ValueError("Service error")
        
        # Open the circuit
        for _ in range(breaker.config.failure_threshold):
            breaker.call(failing_fn)
        assert breaker.get_state() == CircuitState.OPEN
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Next call attempt should transition to HALF_OPEN
        breaker.call(lambda: "success")
        assert breaker.get_state() == CircuitState.HALF_OPEN
    
    def test_transition_to_closed_from_half_open(self, breaker):
        """Test circuit closes after successful calls in HALF_OPEN."""
        def failing_fn():
            raise ValueError("Service error")
        
        def success_fn():
            return "success"
        
        # Open the circuit
        for _ in range(breaker.config.failure_threshold):
            breaker.call(failing_fn)
        assert breaker.get_state() == CircuitState.OPEN
        
        # Force to HALF_OPEN for testing
        breaker.force_state(CircuitState.HALF_OPEN)
        
        # Successful calls should close circuit
        for _ in range(breaker.config.success_threshold):
            result = breaker.call(success_fn)
            assert result.success
        
        assert breaker.get_state() == CircuitState.CLOSED
    
    def test_reopen_from_half_open_on_failure(self, breaker):
        """Test circuit reopens from HALF_OPEN on failure."""
        def failing_fn():
            raise ValueError("Service error")
        
        # Open circuit
        for _ in range(breaker.config.failure_threshold):
            breaker.call(failing_fn)
        
        # Force to HALF_OPEN
        breaker.force_state(CircuitState.HALF_OPEN)
        assert breaker.get_state() == CircuitState.HALF_OPEN
        
        # Failure should reopen circuit
        result = breaker.call(failing_fn)
        assert not result.success
        assert breaker.get_state() == CircuitState.OPEN


class TestCircuitBreakerMetrics:
    """Test circuit breaker metrics."""
    
    def test_metrics_track_calls(self, breaker):
        """Test metrics track successful/failed calls."""
        def success_fn():
            return "success"
        
        def failing_fn():
            raise ValueError("Error")
        
        breaker.call(success_fn)
        breaker.call(success_fn)
        
        try:
            breaker.call(failing_fn)
        except:
            pass
        
        metrics = breaker.get_metrics()
        assert metrics.total_calls == 3
        assert metrics.successful_calls == 2
    
    def test_metrics_track_rejections(self, breaker):
        """Test metrics track rejected calls."""
        def failing_fn():
            raise ValueError("Error")
        
        # Open circuit
        for _ in range(breaker.config.failure_threshold):
            breaker.call(failing_fn)
        
        # Rejected call
        breaker.call(lambda: "success")
        
        metrics = breaker.get_metrics()
        assert metrics.rejected_calls == 1
    
    def test_metrics_track_state_changes(self, breaker):
        """Test metrics track state transitions."""
        metrics = breaker.get_metrics()
        assert metrics.current_state == CircuitState.CLOSED
        
        initial_timestamp = metrics.state_change_timestamp
        
        def failing_fn():
            raise ValueError("Error")
        
        # Trigger state change
        for _ in range(breaker.config.failure_threshold):
            breaker.call(failing_fn)
        
        metrics = breaker.get_metrics()
        assert metrics.current_state == CircuitState.OPEN
        assert metrics.state_change_timestamp > initial_timestamp
    
    def test_metrics_track_failure_reason(self, breaker):
        """Test metrics track last failure reason."""
        def failing_fn():
            raise ValueError("Specific error message")
        
        breaker.call(failing_fn)
        
        metrics = breaker.get_metrics()
        assert "Specific error message" in metrics.last_failure_reason
        assert metrics.last_failure_time is not None


class TestCircuitBreakerReset:
    """Test circuit breaker reset functionality."""
    
    def test_manual_reset(self, breaker):
        """Test manually resetting circuit breaker."""
        def failing_fn():
            raise ValueError("Error")
        
        # Open circuit
        for _ in range(breaker.config.failure_threshold):
            breaker.call(failing_fn)
        assert breaker.get_state() == CircuitState.OPEN
        
        # Reset
        breaker.reset()
        assert breaker.get_state() == CircuitState.CLOSED
        assert breaker.get_metrics().total_calls == 0
    
    def test_force_state(self, breaker):
        """Test forcing circuit to specific state."""
        breaker.force_state(CircuitState.HALF_OPEN)
        assert breaker.get_state() == CircuitState.HALF_OPEN
        
        breaker.force_state(CircuitState.CLOSED)
        assert breaker.get_state() == CircuitState.CLOSED


class TestCircuitBreakerExceptionHandling:
    """Test exception handling in circuit breaker."""
    
    def test_monitored_exceptions_only(self):
        """Test only monitored exceptions trigger circuit opening."""
        # Create breaker with only ValueError as monitored
        config = CircuitBreakerConfig(
            failure_threshold=2,
            monitored_exceptions=(ValueError,)
        )
        breaker = CircuitBreaker("monitored_breaker", config)
        
        def raises_monitored():
            raise ValueError("Monitored error")
        
        def raises_unmonitored():
            raise RuntimeError("Unmonitored error")
        
        # Monitored exception should track failure
        result = breaker.call(raises_monitored)
        assert not result.success
        assert breaker.get_metrics().failed_calls > 0
        
        # Reset for clean test
        breaker.reset()
        
        # Unmonitored exception should not track failure
        with pytest.raises(RuntimeError):
            breaker.call(raises_unmonitored)
        assert breaker.get_metrics().failed_calls == 0
    
    def test_custom_monitored_exceptions(self):
        """Test with custom monitored exception types."""
        class CustomError(Exception):
            pass
        
        config = CircuitBreakerConfig(
            failure_threshold=2,
            monitored_exceptions=(CustomError,)
        )
        breaker = CircuitBreaker("custom_breaker", config)
        
        def raises_custom():
            raise CustomError("Custom error")
        
        # Should track custom exceptions
        breaker.call(raises_custom)
        assert breaker.get_metrics().failed_calls == 1


class TestCircuitBreakerResult:
    """Test CircuitBreakerResult."""
    
    def test_result_success(self):
        """Test successful result."""
        result = CircuitBreakerResult(
            success=True,
            data="test_data",
            circuit_state=CircuitState.CLOSED
        )
        assert result.success
        assert result.data == "test_data"
        assert not result.call_rejected
    
    def test_result_rejected(self):
        """Test rejected result."""
        result = CircuitBreakerResult(
            success=False,
            error="Circuit OPEN",
            circuit_state=CircuitState.OPEN,
            call_rejected=True
        )
        assert not result.success
        assert result.call_rejected
        assert result.circuit_state == CircuitState.OPEN


class TestCircuitBreakerConcurrency:
    """Test circuit breaker with concurrent-like scenarios."""
    
    def test_consecutive_successes_in_half_open(self, breaker):
        """Test tracking consecutive successes."""
        def success_fn():
            return "success"
        
        # Start in HALF_OPEN
        breaker.force_state(CircuitState.HALF_OPEN)
        
        # Track consecutive successes
        for i in range(1, 4):
            breaker.call(success_fn)
            if i < breaker.config.success_threshold:
                assert breaker.get_state() == CircuitState.HALF_OPEN
            else:
                assert breaker.get_state() == CircuitState.CLOSED
