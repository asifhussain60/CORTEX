"""
Tests for Circuit Breaker middleware.

This module provides comprehensive tests for circuit breaker pattern including:
- State transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Failure threshold detection
- Timeout and recovery
- Success rate tracking

Author: CORTEX
Feature: feat05-resilience Phase 2
Correlation ID: FEAT05-P2-T2.1
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

from src.orchestrators.middleware.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerConfig,
    CircuitBreakerOpen,
    CircuitBreakerError
)


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = CircuitBreakerConfig()
        
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout_seconds == 60
        assert config.half_open_max_calls == 1
        
    def test_custom_config(self):
        """Test custom configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            success_threshold=3,
            timeout_seconds=120,
            half_open_max_calls=2
        )
        
        assert config.failure_threshold == 10
        assert config.success_threshold == 3
        assert config.timeout_seconds == 120
        assert config.half_open_max_calls == 2
        
    def test_validate_config(self):
        """Test configuration validation."""
        # Valid config
        config = CircuitBreakerConfig()
        config.validate()
        
        # Invalid failure threshold
        with pytest.raises(ValueError, match="failure_threshold must be positive"):
            CircuitBreakerConfig(failure_threshold=0).validate()
            
        # Invalid success threshold
        with pytest.raises(ValueError, match="success_threshold must be positive"):
            CircuitBreakerConfig(success_threshold=0).validate()
            
        # Invalid timeout
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            CircuitBreakerConfig(timeout_seconds=-1).validate()


class TestCircuitBreakerStates:
    """Tests for circuit breaker state transitions."""
    
    @pytest.fixture
    def breaker(self):
        """Create circuit breaker with short timeout for testing."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=1
        )
        return CircuitBreaker("test_service", config)
        
    def test_initial_state_closed(self, breaker):
        """Test circuit breaker starts in CLOSED state."""
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        
    def test_closed_to_open_on_failures(self, breaker):
        """Test transition from CLOSED to OPEN after threshold failures."""
        # Record failures up to threshold
        for _ in range(3):
            breaker.record_failure()
            
        assert breaker.state == CircuitBreakerState.OPEN
        
    def test_open_state_rejects_calls(self, breaker):
        """Test OPEN state rejects calls."""
        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()
            
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Should raise exception
        with pytest.raises(CircuitBreakerOpen):
            breaker.call(lambda: "test")
            
    def test_open_to_half_open_after_timeout(self, breaker):
        """Test transition from OPEN to HALF_OPEN after timeout."""
        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()
            
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Check if can transition to HALF_OPEN
        assert breaker.can_attempt() is True
        
    def test_half_open_to_closed_on_success(self, breaker):
        """Test transition from HALF_OPEN to CLOSED after successes."""
        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()
            
        # Wait for timeout
        time.sleep(1.1)
        
        # Transition to HALF_OPEN and record successes
        breaker._state = CircuitBreakerState.HALF_OPEN
        breaker.record_success()
        breaker.record_success()
        
        assert breaker.state == CircuitBreakerState.CLOSED
        
    def test_half_open_to_open_on_failure(self, breaker):
        """Test transition from HALF_OPEN back to OPEN on failure."""
        # Trip the breaker
        for _ in range(3):
            breaker.record_failure()
            
        # Wait and transition to HALF_OPEN
        time.sleep(1.1)
        breaker._state = CircuitBreakerState.HALF_OPEN
        
        # Record failure
        breaker.record_failure()
        
        assert breaker.state == CircuitBreakerState.OPEN


class TestCircuitBreakerCalls:
    """Tests for circuit breaker call execution."""
    
    @pytest.fixture
    def breaker(self):
        """Create circuit breaker for testing."""
        config = CircuitBreakerConfig(failure_threshold=3)
        return CircuitBreaker("test_service", config)
        
    def test_successful_call(self, breaker):
        """Test successful call execution."""
        result = breaker.call(lambda: "success")
        
        assert result == "success"
        assert breaker.success_count == 1
        assert breaker.failure_count == 0
        
    def test_failed_call(self, breaker):
        """Test failed call execution."""
        def failing_func():
            raise ValueError("Test error")
            
        with pytest.raises(ValueError):
            breaker.call(failing_func)
            
        assert breaker.failure_count == 1
        assert breaker.success_count == 0
        
    def test_call_with_args(self, breaker):
        """Test call with arguments."""
        def add(a, b):
            return a + b
            
        result = breaker.call(add, 2, 3)
        assert result == 5
        
    def test_call_with_kwargs(self, breaker):
        """Test call with keyword arguments."""
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
            
        result = breaker.call(greet, "World", greeting="Hi")
        assert result == "Hi, World!"
        
    def test_decorator_success(self, breaker):
        """Test circuit breaker as decorator."""
        @breaker.protect
        def protected_func():
            return "protected"
            
        result = protected_func()
        assert result == "protected"
        
    def test_decorator_failure(self, breaker):
        """Test circuit breaker decorator with failure."""
        @breaker.protect
        def failing_func():
            raise RuntimeError("Failure")
            
        with pytest.raises(RuntimeError):
            failing_func()
            
        assert breaker.failure_count == 1


class TestCircuitBreakerMetrics:
    """Tests for circuit breaker metrics and statistics."""
    
    @pytest.fixture
    def breaker(self):
        """Create circuit breaker for testing."""
        return CircuitBreaker("test_service")
        
    def test_get_stats(self, breaker):
        """Test getting circuit breaker statistics."""
        breaker.record_success()
        breaker.record_success()
        breaker.record_failure()
        
        stats = breaker.get_stats()
        
        assert stats["state"] == CircuitBreakerState.CLOSED.value
        assert stats["failure_count"] == 1
        assert stats["success_count"] == 2
        assert "failure_rate" in stats
        
    def test_failure_rate_calculation(self, breaker):
        """Test failure rate calculation."""
        breaker.record_success()
        breaker.record_success()
        breaker.record_failure()
        
        stats = breaker.get_stats()
        
        # 1 failure out of 3 total = 33.33%
        assert abs(stats["failure_rate"] - 0.333) < 0.01
        
    def test_reset_stats(self, breaker):
        """Test resetting statistics."""
        breaker.record_failure()
        breaker.record_failure()
        
        assert breaker.failure_count == 2
        
        breaker.reset()
        
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
        assert breaker.state == CircuitBreakerState.CLOSED


class TestCircuitBreakerConcurrency:
    """Tests for concurrent access to circuit breaker."""
    
    def test_concurrent_calls(self):
        """Test concurrent calls through circuit breaker."""
        breaker = CircuitBreaker("test_service")
        results = []
        
        def worker(worker_id):
            result = breaker.call(lambda: f"worker_{worker_id}")
            results.append(result)
            
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        assert len(results) == 10
        assert breaker.success_count == 10
        
    def test_concurrent_state_transitions(self):
        """Test state transitions under concurrent load."""
        config = CircuitBreakerConfig(failure_threshold=5)
        breaker = CircuitBreaker("test_service", config)
        
        def failing_worker():
            try:
                breaker.call(lambda: 1/0)
            except:
                pass
                
        threads = [threading.Thread(target=failing_worker) for _ in range(10)]
        
        for t in threads:
            t.start()
            
        for t in threads:
            t.join()
            
        # Should have tripped
        assert breaker.state == CircuitBreakerState.OPEN


class TestCircuitBreakerError:
    """Tests for CircuitBreakerError exception."""
    
    def test_error_creation(self):
        """Test error creation with details."""
        error = CircuitBreakerError(
            message="Circuit breaker error",
            service="test_service",
            state=CircuitBreakerState.OPEN
        )
        
        assert str(error) == "Circuit breaker error"
        assert error.service == "test_service"
        assert error.state == CircuitBreakerState.OPEN
        
    def test_circuit_breaker_open_error(self):
        """Test CircuitBreakerOpen specific error."""
        error = CircuitBreakerOpen(
            service="api_service",
            retry_after_seconds=60.0
        )
        
        assert "api_service" in str(error)
        assert error.retry_after_seconds == 60.0


class TestIntegration:
    """Integration tests for circuit breaker."""
    
    def test_full_lifecycle(self):
        """Test complete circuit breaker lifecycle."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=1
        )
        breaker = CircuitBreaker("test_service", config)
        
        # Start CLOSED - allow calls
        assert breaker.state == CircuitBreakerState.CLOSED
        breaker.call(lambda: "ok")
        
        # Trip to OPEN
        for _ in range(3):
            try:
                breaker.call(lambda: 1/0)
            except:
                pass
                
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Wait for timeout
        time.sleep(1.1)
        
        # Should allow HALF_OPEN attempt
        breaker._state = CircuitBreakerState.HALF_OPEN
        
        # Recover with successes
        breaker.call(lambda: "ok")
        breaker.call(lambda: "ok")
        
        assert breaker.state == CircuitBreakerState.CLOSED
        
    def test_realistic_api_scenario(self):
        """Test realistic API failure scenario."""
        config = CircuitBreakerConfig(failure_threshold=5, timeout_seconds=2)
        breaker = CircuitBreaker("external_api", config)
        
        call_count = 0
        
        def flaky_api():
            nonlocal call_count
            call_count += 1
            if call_count <= 5:
                raise ConnectionError("API unavailable")
            return "success"
            
        # First 5 calls fail - trips breaker
        for _ in range(5):
            with pytest.raises(ConnectionError):
                breaker.call(flaky_api)
                
        assert breaker.state == CircuitBreakerState.OPEN
        
        # Breaker blocks further calls
        with pytest.raises(CircuitBreakerOpen):
            breaker.call(flaky_api)
            
        # API recovers but breaker still OPEN (no timeout yet)
        assert call_count == 5  # No additional calls made
