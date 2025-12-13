"""
Test suite for ErrorRecoveryOrchestrator

Tests error recovery mechanisms, retry policies, and fallback strategies:
- Exponential backoff retry with jitter
- Circuit breaker pattern implementation
- Fallback strategy chains
- Error pattern recognition and classification
- Recovery statistics and reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Feature: Orchestrator Enhancement Plan v2.0 - Feature 17
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch


class TestRetryPolicies:
    """Test suite for retry policies with exponential backoff"""
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        # Disable jitter for deterministic testing
        recovery = ErrorRecoveryOrchestrator(jitter=False)
        
        # Test exponential growth: 2^attempt seconds
        assert recovery.calculate_backoff(0) == 1.0  # 2^0 = 1
        assert recovery.calculate_backoff(1) == 2.0  # 2^1 = 2
        assert recovery.calculate_backoff(2) == 4.0  # 2^2 = 4
        assert recovery.calculate_backoff(3) == 8.0  # 2^3 = 8
    
    @pytest.mark.asyncio
    async def test_retry_with_success_on_second_attempt(self):
        """Test retry succeeds on second attempt"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise TimeoutError("First attempt times out")
            return "success"
        
        result = await recovery.retry_with_backoff(flaky_operation, max_attempts=3)
        
        assert result == "success"
        assert attempt_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_exhausts_attempts(self):
        """Test retry fails after max attempts"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        async def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            await recovery.retry_with_backoff(always_fails, max_attempts=3)


class TestCircuitBreaker:
    """Test suite for circuit breaker pattern"""
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        operation_name = "flaky_service"
        
        # Record failures
        for _ in range(5):
            recovery.record_failure(operation_name)
        
        # Circuit should be open
        assert recovery.is_circuit_open(operation_name) is True
    
    def test_circuit_breaker_half_open_after_timeout(self):
        """Test circuit breaker transitions to half-open after timeout"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator(circuit_timeout=0.1)
        
        operation_name = "test_service"
        
        # Open circuit
        for _ in range(5):
            recovery.record_failure(operation_name)
        
        import time
        time.sleep(0.2)  # Wait for timeout
        
        # Should be half-open (allowing test request)
        assert recovery.is_circuit_open(operation_name) is False


class TestFallbackStrategies:
    """Test suite for fallback strategy chains"""
    
    @pytest.mark.asyncio
    async def test_fallback_chain_first_succeeds(self):
        """Test fallback chain when first strategy succeeds"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        async def primary():
            return "primary_result"
        
        async def secondary():
            return "secondary_result"
        
        result = await recovery.execute_with_fallback([primary, secondary])
        
        assert result == "primary_result"
    
    @pytest.mark.asyncio
    async def test_fallback_chain_second_succeeds(self):
        """Test fallback chain falls back to second strategy"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        async def primary():
            raise ValueError("Primary failed")
        
        async def secondary():
            return "secondary_result"
        
        result = await recovery.execute_with_fallback([primary, secondary])
        
        assert result == "secondary_result"
    
    @pytest.mark.asyncio
    async def test_fallback_chain_all_fail(self):
        """Test fallback chain when all strategies fail"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        async def primary():
            raise ValueError("Primary failed")
        
        async def secondary():
            raise ValueError("Secondary failed")
        
        with pytest.raises(ValueError):
            await recovery.execute_with_fallback([primary, secondary])


class TestErrorClassification:
    """Test suite for error pattern recognition"""
    
    def test_classify_transient_error(self):
        """Test classification of transient errors"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        # Network timeout - transient
        error = TimeoutError("Connection timeout")
        category = recovery.classify_error(error)
        
        assert category == "transient"
    
    def test_classify_permanent_error(self):
        """Test classification of permanent errors"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        # Value error - permanent
        error = ValueError("Invalid input")
        category = recovery.classify_error(error)
        
        assert category == "permanent"
    
    def test_retryable_error_check(self):
        """Test checking if error is retryable"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        # Transient errors should be retryable
        assert recovery.is_retryable(TimeoutError("timeout")) is True
        assert recovery.is_retryable(ConnectionError("connection")) is True
        
        # Permanent errors should not be retryable
        assert recovery.is_retryable(ValueError("value")) is False
        assert recovery.is_retryable(TypeError("type")) is False


class TestRecoveryStatistics:
    """Test suite for recovery statistics tracking"""
    
    def test_track_recovery_attempt(self):
        """Test tracking recovery attempts"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        recovery.track_recovery_attempt(
            operation="test_op",
            attempt=1,
            success=False,
            error_type="TimeoutError"
        )
        
        stats = recovery.get_recovery_stats("test_op")
        
        assert stats is not None
        assert stats["total_attempts"] >= 1
        assert stats["failures"] >= 1
    
    def test_get_global_recovery_stats(self):
        """Test getting global recovery statistics"""
        from src.operations.utilities.error_recovery_orchestrator import ErrorRecoveryOrchestrator
        
        recovery = ErrorRecoveryOrchestrator()
        
        # Track multiple operations
        recovery.track_recovery_attempt("op1", 1, True, None)
        recovery.track_recovery_attempt("op2", 1, False, "Error")
        recovery.track_recovery_attempt("op2", 2, True, None)
        
        global_stats = recovery.get_global_stats()
        
        assert global_stats is not None
        assert "total_operations" in global_stats
        assert "total_recoveries" in global_stats
        assert "success_rate" in global_stats
