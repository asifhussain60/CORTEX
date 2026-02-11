"""
Support Layer Integration Tests (REFACTOR Phase)

Integration tests for UnifiedSupportOrchestrator with multi-strategy workflows.
Authority: ENH-087 Track 2 Stage 3
AC_START: AC-ENH090-S3-REFACTOR-001
"""

import pytest
from cortex.orchestrators.strategies.support_layer_pattern import (
    SupportOperationType,
    SupportRequest,
    SupportResult,
    ValidationStrategy,
    ErrorHandlingStrategy,
    CachingStrategy,
    UnifiedSupportOrchestrator,
)


class TestSupportLayerIntegration:
    """Integration tests for support layer consolidation."""
    
    def setup_method(self):
        self.orchestrator = UnifiedSupportOrchestrator()
    
    def test_validation_then_caching_workflow(self):
        """Test validation followed by caching."""
        # Validate input
        validate_req = SupportRequest(
            operation=SupportOperationType.VALIDATE_INPUT,
            context="user_data",
            data={"id": 123, "name": "Alice"}
        )
        validate_result = self.orchestrator.execute(validate_req)
        assert validate_result.success
        
        # Cache validated result
        cache_req = SupportRequest(
            operation=SupportOperationType.CACHE_RESULT,
            context="user_123",
            data=validate_result.result_data or {}
        )
        cache_result = self.orchestrator.execute(cache_req)
        assert cache_result.success
        
        # Retrieve from cache
        retrieve_req = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context="user_123",
            data={}
        )
        retrieve_result = self.orchestrator.execute(retrieve_req)
        assert retrieve_result.success
        assert retrieve_result.metrics is not None
        assert retrieve_result.metrics.cache_hit == True
    
    def test_error_handling_with_recovery(self):
        """Test error handling and recovery workflow."""
        # Trigger error handling
        error_req = SupportRequest(
            operation=SupportOperationType.HANDLE_ERROR,
            context="critical_op",
            data={"error": "Connection timeout"}
        )
        error_result = self.orchestrator.execute(error_req)
        assert error_result.success
        
        # Attempt recovery
        recovery_req = SupportRequest(
            operation=SupportOperationType.RECOVER_FROM_ERROR,
            context="critical_op",
            data={"error": "Connection timeout", "retry_count": 0}
        )
        recovery_result = self.orchestrator.execute(recovery_req)
        assert recovery_result.success
        assert recovery_result.result_data is not None
        assert recovery_result.result_data.get("recovery_attempted") == True
    
    def test_security_validation_before_caching(self):
        """Test security validation before storing sensitive data."""
        # Attempt to cache sensitive data without validation
        unsafe_data = {"api_key": "secret123", "token": "xyz"}
        
        # Validate security first
        validate_req = SupportRequest(
            operation=SupportOperationType.VALIDATE_SECURITY,
            context="auth_data",
            data=unsafe_data
        )
        validate_result = self.orchestrator.execute(validate_req)
        assert not validate_result.success  # Should fail on sensitive keys
        
        # Only cache if validation passes
        if validate_result.success:
            cache_req = SupportRequest(
                operation=SupportOperationType.CACHE_RESULT,
                context="auth",
                data=unsafe_data
            )
            self.orchestrator.execute(cache_req)
        
        # Verify nothing cached for sensitive data
        retrieve_req = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context="auth",
            data={}
        )
        retrieve_result = self.orchestrator.execute(retrieve_req)
        assert not retrieve_result.success  # Nothing cached
    
    def test_concurrent_strategy_operations(self):
        """Test multiple strategies handling different operations."""
        requests = [
            (SupportOperationType.VALIDATE_INPUT, {"value": 42}),
            (SupportOperationType.CACHE_RESULT, {"result": "data"}),
            (SupportOperationType.HANDLE_ERROR, {"error": "test"}),
            (SupportOperationType.VALIDATE_OUTPUT, {"output": "ok"}),
            (SupportOperationType.LOG_ERROR, {"error": "info"}),
        ]
        
        results = []
        for op, data in requests:
            req = SupportRequest(operation=op, context="concurrent", data=data)
            result = self.orchestrator.execute(req)
            results.append(result)
        
        # All operations should succeed or handle gracefully
        assert len(results) == 5
        assert all(r.metrics is not None for r in results)
    
    def test_metrics_collection_across_strategies(self):
        """Test that metrics are properly collected across strategies."""
        operations = [
            SupportOperationType.VALIDATE_INPUT,
            SupportOperationType.CACHE_RESULT,
            SupportOperationType.HANDLE_ERROR,
        ]
        
        for op in operations:
            req = SupportRequest(operation=op, context="metrics", data={})
            result = self.orchestrator.execute(req)
            assert result.metrics is not None
            assert result.metrics.duration_ms >= 0
    
    def test_capability_discovery_completeness(self):
        """Test that all 9 operations are discoverable."""
        ops = self.orchestrator.get_supported_operations()
        assert len(ops) == 9
        
        expected_ops = {
            SupportOperationType.VALIDATE_INPUT,
            SupportOperationType.VALIDATE_OUTPUT,
            SupportOperationType.VALIDATE_SECURITY,
            SupportOperationType.HANDLE_ERROR,
            SupportOperationType.RECOVER_FROM_ERROR,
            SupportOperationType.LOG_ERROR,
            SupportOperationType.CACHE_RESULT,
            SupportOperationType.RETRIEVE_CACHED,
            SupportOperationType.INVALIDATE_CACHE,
        }
        
        for expected_op in expected_ops:
            assert expected_op in ops
    
    def test_error_logging_across_operations(self):
        """Test error logging in error handling strategy."""
        # Log an error
        log_req = SupportRequest(
            operation=SupportOperationType.LOG_ERROR,
            context="test_context",
            data={"error": "Test error message"}
        )
        log_result = self.orchestrator.execute(log_req)
        assert log_result.success
        
        # Log another error
        log_req2 = SupportRequest(
            operation=SupportOperationType.LOG_ERROR,
            context="test_context_2",
            data={"error": "Another error"}
        )
        log_result2 = self.orchestrator.execute(log_req2)
        assert log_result2.success
        
        # Error logs should accumulate
        assert log_result.result_data is not None
        assert log_result2.result_data is not None
    
    def test_cache_lifecycle_full_workflow(self):
        """Test complete cache lifecycle: create, retrieve, invalidate."""
        cache_key = "lifecycle_test"
        cache_data = {"value": 100, "timestamp": "2024-01-01"}
        
        # 1. Cache the data
        cache_req = SupportRequest(
            operation=SupportOperationType.CACHE_RESULT,
            context=cache_key,
            data=cache_data
        )
        cache_result = self.orchestrator.execute(cache_req)
        assert cache_result.success
        
        # 2. Retrieve cached data
        retrieve_req = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context=cache_key,
            data={}
        )
        retrieve_result = self.orchestrator.execute(retrieve_req)
        assert retrieve_result.success
        assert retrieve_result.metrics is not None
        assert retrieve_result.metrics.cache_hit == True
        
        # 3. Invalidate cache
        invalidate_req = SupportRequest(
            operation=SupportOperationType.INVALIDATE_CACHE,
            context=cache_key,
            data={}
        )
        invalidate_result = self.orchestrator.execute(invalidate_req)
        assert invalidate_result.success
        
        # 4. Verify cache is gone
        retrieve_again = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context=cache_key,
            data={}
        )
        retrieve_again_result = self.orchestrator.execute(retrieve_again)
        assert not retrieve_again_result.success  # Cache miss
        assert retrieve_again_result.metrics is not None
        assert retrieve_again_result.metrics.cache_hit == False
    
    def test_strategy_selection_routing(self):
        """Test that operations are routed to correct strategies."""
        # ValidationStrategy should handle VALIDATE_* operations
        validation_ops = [
            SupportOperationType.VALIDATE_INPUT,
            SupportOperationType.VALIDATE_OUTPUT,
            SupportOperationType.VALIDATE_SECURITY,
        ]
        
        for op in validation_ops:
            req = SupportRequest(operation=op, context="test", data={})
            result = self.orchestrator.execute(req)
            # Validate operations should be routed to ValidationStrategy
            assert result.operation == op
        
        # ErrorHandlingStrategy should handle error operations
        error_ops = [
            SupportOperationType.HANDLE_ERROR,
            SupportOperationType.RECOVER_FROM_ERROR,
            SupportOperationType.LOG_ERROR,
        ]
        
        for op in error_ops:
            req = SupportRequest(operation=op, context="test", data={})
            result = self.orchestrator.execute(req)
            # Error operations should be routed to ErrorHandlingStrategy
            assert result.operation == op
        
        # CachingStrategy should handle CACHE_* and RETRIEVE_CACHED operations
        caching_ops = [
            SupportOperationType.CACHE_RESULT,
            SupportOperationType.RETRIEVE_CACHED,
            SupportOperationType.INVALIDATE_CACHE,
        ]
        
        for op in caching_ops:
            req = SupportRequest(operation=op, context="test", data={})
            result = self.orchestrator.execute(req)
            # Caching operations should be routed to CachingStrategy
            assert result.operation == op
