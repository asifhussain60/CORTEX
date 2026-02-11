"""
Support Layer Implementation Tests (GREEN Phase)

Tests UnifiedSupportOrchestrator and all strategies.
Authority: ENH-087 Track 2 Stage 3
AC_START: AC-ENH090-S3-GREEN-002
"""

import pytest
from cortex.orchestrators.strategies.support_layer_pattern import (
    SupportOperationType,
    SupportRequest,
    SupportResult,
    SupportMetrics,
    ValidationStrategy,
    ErrorHandlingStrategy,
    CachingStrategy,
    UnifiedSupportOrchestrator,
)


class TestValidationStrategy:
    """Test ValidationStrategy implementation."""
    
    def setup_method(self):
        self.strategy = ValidationStrategy()
    
    def test_initialization(self):
        assert self.strategy.name == "ValidationStrategy"
        assert len(self.strategy.supported_operations) == 3
    
    def test_validate_input_success(self):
        req = SupportRequest(
            operation=SupportOperationType.VALIDATE_INPUT,
            context="input_check",
            data={"value": 42, "name": "test"}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("validated") == True
    
    def test_validate_input_fails_on_none(self):
        req = SupportRequest(
            operation=SupportOperationType.VALIDATE_INPUT,
            context="input_check",
            data={"value": 42, "name": None}
        )
        result = self.strategy.execute(req)
        assert not result.success  # Validation should fail when required field is None
        assert result.result_data is not None
        assert result.result_data.get("validated") == False
    
    def test_validate_output_success(self):
        req = SupportRequest(
            operation=SupportOperationType.VALIDATE_OUTPUT,
            context="output_check",
            data={"result": "success", "status": 200}
        )
        result = self.strategy.execute(req)
        assert result.success
    
    def test_validate_security_fails_on_sensitive_keys(self):
        req = SupportRequest(
            operation=SupportOperationType.VALIDATE_SECURITY,
            context="security_check",
            data={"api_key": "secret123", "user": "john"}
        )
        result = self.strategy.execute(req)
        assert not result.success  # Security validation should fail on sensitive keys
        assert result.result_data is not None
        assert result.result_data.get("validated") == False
    
    def test_validate_security_success_safe_data(self):
        req = SupportRequest(
            operation=SupportOperationType.VALIDATE_SECURITY,
            context="security_check",
            data={"user": "john", "email": "john@example.com"}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("validated") == True


class TestErrorHandlingStrategy:
    """Test ErrorHandlingStrategy implementation."""
    
    def setup_method(self):
        self.strategy = ErrorHandlingStrategy()
    
    def test_initialization(self):
        assert self.strategy.name == "ErrorHandlingStrategy"
        assert len(self.strategy.supported_operations) == 3
    
    def test_handle_error(self):
        req = SupportRequest(
            operation=SupportOperationType.HANDLE_ERROR,
            context="error_context",
            data={"error": "Database connection failed"}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("action") == "escalate"
    
    def test_log_error(self):
        req = SupportRequest(
            operation=SupportOperationType.LOG_ERROR,
            context="error_context",
            data={"error": "Test error", "context": "unit_test"}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("logged") == True
        assert self.strategy.error_log  # Check log exists
    
    def test_recover_from_error(self):
        req = SupportRequest(
            operation=SupportOperationType.RECOVER_FROM_ERROR,
            context="recovery",
            data={"error": "Network timeout", "retry_count": 0}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("recovery_attempted") == True
        assert result.result_data.get("retry_count") == 1


class TestCachingStrategy:
    """Test CachingStrategy implementation."""
    
    def setup_method(self):
        self.strategy = CachingStrategy()
    
    def test_initialization(self):
        assert self.strategy.name == "CachingStrategy"
        assert len(self.strategy.supported_operations) == 3
    
    def test_cache_result(self):
        req = SupportRequest(
            operation=SupportOperationType.CACHE_RESULT,
            context="user_123",
            data={"name": "John", "email": "john@example.com"}
        )
        result = self.strategy.execute(req)
        assert result.success
        assert result.result_data is not None
        assert result.result_data.get("cached") == True
    
    def test_retrieve_cached_hit(self):
        # First cache a result
        cache_req = SupportRequest(
            operation=SupportOperationType.CACHE_RESULT,
            context="user_456",
            data={"name": "Jane"}
        )
        self.strategy.execute(cache_req)
        
        # Then retrieve it
        retrieve_req = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context="user_456",
            data={}
        )
        result = self.strategy.execute(retrieve_req)
        assert result.success
        assert result.metrics is not None
        assert result.metrics.cache_hit == True
        assert result.result_data is not None
        assert result.result_data.get("name") == "Jane"
    
    def test_retrieve_cached_miss(self):
        req = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context="nonexistent",
            data={}
        )
        result = self.strategy.execute(req)
        assert not result.success
        assert result.metrics is not None
        assert result.metrics.cache_hit == False
    
    def test_invalidate_cache(self):
        # Cache something
        cache_req = SupportRequest(
            operation=SupportOperationType.CACHE_RESULT,
            context="temp_data",
            data={"value": 100}
        )
        self.strategy.execute(cache_req)
        
        # Invalidate it
        invalidate_req = SupportRequest(
            operation=SupportOperationType.INVALIDATE_CACHE,
            context="temp_data",
            data={}
        )
        result = self.strategy.execute(invalidate_req)
        assert result.success
        
        # Verify it's gone
        retrieve_req = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context="temp_data",
            data={}
        )
        retrieve_result = self.strategy.execute(retrieve_req)
        assert not retrieve_result.success


class TestUnifiedSupportOrchestrator:
    """Test UnifiedSupportOrchestrator consolidation."""
    
    def setup_method(self):
        self.orchestrator = UnifiedSupportOrchestrator()
    
    def test_initialization(self):
        assert len(self.orchestrator.strategies) == 3
    
    def test_get_supported_operations(self):
        ops = self.orchestrator.get_supported_operations()
        assert len(ops) == 9  # 3 validation + 3 error + 3 caching
    
    def test_route_validation_operations(self):
        req = SupportRequest(
            operation=SupportOperationType.VALIDATE_INPUT,
            context="test",
            data={"value": 42}
        )
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_route_error_handling_operations(self):
        req = SupportRequest(
            operation=SupportOperationType.HANDLE_ERROR,
            context="test",
            data={"error": "test error"}
        )
        result = self.orchestrator.execute(req)
        assert result.success
    
    def test_route_caching_operations(self):
        # Cache
        cache_req = SupportRequest(
            operation=SupportOperationType.CACHE_RESULT,
            context="key1",
            data={"data": "value"}
        )
        cache_result = self.orchestrator.execute(cache_req)
        assert cache_result.success
        
        # Retrieve
        retrieve_req = SupportRequest(
            operation=SupportOperationType.RETRIEVE_CACHED,
            context="key1",
            data={}
        )
        retrieve_result = self.orchestrator.execute(retrieve_req)
        assert retrieve_result.success
    
    def test_metrics_collection(self):
        req = SupportRequest(
            operation=SupportOperationType.VALIDATE_INPUT,
            context="metrics_test",
            data={"value": 1}
        )
        result = self.orchestrator.execute(req)
        assert result.metrics is not None
        assert result.metrics.duration_ms > 0
    
    def test_consolidation_all_9_operations_discoverable(self):
        ops = self.orchestrator.get_supported_operations()
        
        # Verify validation operations
        assert SupportOperationType.VALIDATE_INPUT in ops
        assert SupportOperationType.VALIDATE_OUTPUT in ops
        assert SupportOperationType.VALIDATE_SECURITY in ops
        
        # Verify error operations
        assert SupportOperationType.HANDLE_ERROR in ops
        assert SupportOperationType.RECOVER_FROM_ERROR in ops
        assert SupportOperationType.LOG_ERROR in ops
        
        # Verify caching operations
        assert SupportOperationType.CACHE_RESULT in ops
        assert SupportOperationType.RETRIEVE_CACHED in ops
        assert SupportOperationType.INVALIDATE_CACHE in ops
    
    def test_multiple_strategy_executions(self):
        # Execute different strategies in sequence
        requests = [
            (SupportOperationType.VALIDATE_INPUT, {"value": 1}),
            (SupportOperationType.CACHE_RESULT, {"data": "test"}),
            (SupportOperationType.HANDLE_ERROR, {"error": "test"}),
        ]
        
        for op, data in requests:
            req = SupportRequest(operation=op, context="test", data=data)
            result = self.orchestrator.execute(req)
            assert result.success or (op == SupportOperationType.HANDLE_ERROR)
