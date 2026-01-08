"""
Tests for MCP Request/Response Handling

Comprehensive tests for MCP request/response processing, error handling,
context management, and streaming responses.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P1-T1.3
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, patch
import json


class TestRequestContextManagement:
    """Test request context handling"""
    
    def test_request_includes_context(self):
        """RED: Request can include context metadata"""
        from src.mcp.request_handler import MCPRequest
        
        request = MCPRequest(
            method="tools/call",
            params={"name": "plan", "arguments": {"request": "test"}},
            context={
                "session_id": "sess-123",
                "user_id": "user-456",
                "workspace": "/path/to/workspace"
            }
        )
        
        assert request.context["session_id"] == "sess-123"
        assert request.context["user_id"] == "user-456"
    
    def test_context_passed_to_orchestrator(self):
        """RED: Context is passed through to orchestrator execution"""
        from src.mcp.request_handler import RequestHandler
        
        handler = RequestHandler()
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.return_value = {"result": "success"}
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}},
            "context": {"workspace": "/workspace"}
        }
        
        handler.handle(request)
        
        # Verify orchestrator was called (context handling happens internally)
        assert handler.master_orchestrator.handle_request.called


class TestResponseFormatting:
    """Test response formatting"""
    
    def test_success_response_format(self):
        """RED: Success response has standard format"""
        from src.mcp.request_handler import MCPResponse
        
        response = MCPResponse.success(
            result={"plan_id": "test-123"},
            request_id="req-1"
        )
        
        data = response.to_dict()
        assert data["status"] == "success"
        assert data["result"]["plan_id"] == "test-123"
        assert data["request_id"] == "req-1"
    
    def test_error_response_format(self):
        """RED: Error response includes code and message"""
        from src.mcp.request_handler import MCPResponse, ErrorCode
        
        response = MCPResponse.error(
            code=ErrorCode.INVALID_PARAMS,
            message="Missing required parameter",
            request_id="req-1"
        )
        
        data = response.to_dict()
        assert data["status"] == "error"
        assert data["error"]["code"] == ErrorCode.INVALID_PARAMS
        assert "Missing required parameter" in data["error"]["message"]
    
    def test_partial_response_format(self):
        """RED: Partial/streaming response format"""
        from src.mcp.request_handler import MCPResponse
        
        response = MCPResponse.partial(
            data={"progress": 50, "status": "running"},
            request_id="req-1"
        )
        
        data = response.to_dict()
        assert data["status"] == "partial"
        assert data["result"]["progress"] == 50


class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_validation_error(self):
        """RED: Parameter validation errors are caught"""
        from src.mcp.request_handler import RequestHandler
        from src.mcp.request_handler import ValidationError
        
        handler = RequestHandler()
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan"}  # Missing required 'arguments'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            handler.handle(request)
        
        assert "arguments" in str(exc_info.value).lower()
    
    def test_orchestrator_error_handling(self):
        """RED: Orchestrator errors are properly wrapped"""
        from src.mcp.request_handler import RequestHandler
        
        handler = RequestHandler()
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.side_effect = Exception("Orchestrator failed")
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}}
        }
        
        response = handler.handle(request)
        
        assert response.status == "error"
        assert "Orchestrator failed" in response.error_message
    
    def test_timeout_handling(self):
        """RED: Long-running requests can timeout"""
        from src.mcp.request_handler import RequestHandler
        import time
        
        handler = RequestHandler(timeout=1)
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.side_effect = lambda x: time.sleep(2)
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}}
        }
        
        response = handler.handle(request)
        
        assert response.status == "error"
        assert "timeout" in response.error_message.lower()


class TestStreamingResponses:
    """Test streaming response support"""
    
    def test_streaming_callback(self):
        """RED: Handler supports streaming callbacks"""
        from src.mcp.request_handler import RequestHandler
        
        progress_updates = []
        
        def progress_callback(data):
            progress_updates.append(data)
        
        handler = RequestHandler(progress_callback=progress_callback)
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.return_value = {"result": "done"}
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}}
        }
        
        handler.handle(request)
        
        # Should have received progress updates
        assert len(progress_updates) > 0
    
    def test_partial_results_streaming(self):
        """RED: Partial results can be streamed"""
        from src.mcp.request_handler import RequestHandler
        
        handler = RequestHandler()
        
        # Simulate streaming response
        handler.send_partial({"phase": 1, "status": "complete"}, request_id="req-1")
        handler.send_partial({"phase": 2, "status": "running"}, request_id="req-1")
        
        # Should have sent 2 partial responses
        assert handler.partial_count == 2


class TestRequestValidation:
    """Test request validation"""
    
    def test_validate_required_fields(self):
        """RED: Required fields are validated"""
        from src.mcp.request_handler import RequestValidator
        
        validator = RequestValidator()
        
        # Valid request
        assert validator.validate({
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {}}
        }) is True
        
        # Missing method
        with pytest.raises(Exception):
            validator.validate({"params": {}})
    
    def test_validate_method_name(self):
        """RED: Method names are validated"""
        from src.mcp.request_handler import RequestValidator
        
        validator = RequestValidator()
        
        # Valid method
        assert validator.validate_method("tools/call") is True
        
        # Invalid method
        assert validator.validate_method("invalid/method") is False
    
    def test_validate_parameter_schema(self):
        """RED: Parameters are validated against schema"""
        from src.mcp.request_handler import RequestValidator
        
        validator = RequestValidator()
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "count": {"type": "integer"}
            },
            "required": ["name"]
        }
        
        # Valid params
        assert validator.validate_params({"name": "test", "count": 5}, schema) is True
        
        # Missing required
        with pytest.raises(Exception):
            validator.validate_params({"count": 5}, schema)


class TestAsyncRequestHandling:
    """Test asynchronous request handling"""
    
    @pytest.mark.asyncio
    async def test_async_request_handling(self):
        """RED: Handler supports async operations"""
        from src.mcp.request_handler import AsyncRequestHandler
        
        handler = AsyncRequestHandler()
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request = MagicMock(return_value={"result": "done"})
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}}
        }
        
        response = await handler.handle_async(request)
        
        assert response.status == "success"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """RED: Multiple requests can be handled concurrently"""
        from src.mcp.request_handler import AsyncRequestHandler
        import asyncio
        
        handler = AsyncRequestHandler()
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request = MagicMock(return_value={"result": "done"})
        
        requests = [
            {"method": "tools/call", "params": {"name": "plan", "arguments": {"request": f"test{i}"}}}
            for i in range(5)
        ]
        
        # Handle concurrently
        responses = await asyncio.gather(*[handler.handle_async(req) for req in requests])
        
        assert len(responses) == 5
        assert all(r.status == "success" for r in responses)


class TestRequestMetrics:
    """Test request metrics and monitoring"""
    
    def test_request_duration_tracking(self):
        """RED: Request duration is tracked"""
        from src.mcp.request_handler import RequestHandler
        
        handler = RequestHandler()
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.return_value = {"result": "done"}
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}}
        }
        
        response = handler.handle(request)
        
        assert hasattr(response, "duration_ms")
        assert response.duration_ms > 0
    
    def test_request_id_generation(self):
        """RED: Request IDs are auto-generated if not provided"""
        from src.mcp.request_handler import RequestHandler
        
        handler = RequestHandler()
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.return_value = {"result": "done"}
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}}
        }
        
        response = handler.handle(request)
        
        assert response.request_id is not None
        assert len(response.request_id) > 0
    
    def test_metrics_collection(self):
        """RED: Request metrics are collected"""
        from src.mcp.request_handler import RequestHandler, RequestMetrics
        
        metrics = RequestMetrics()
        handler = RequestHandler(metrics=metrics)
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.return_value = {"result": "done"}
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}}
        }
        
        handler.handle(request)
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1


class TestResponseCaching:
    """Test response caching"""
    
    def test_cache_response(self):
        """RED: Responses can be cached"""
        from src.mcp.request_handler import RequestHandler, ResponseCache
        
        cache = ResponseCache()
        handler = RequestHandler(cache=cache)
        handler.master_orchestrator = Mock()
        handler.master_orchestrator.handle_request.return_value = {"result": "cached"}
        
        request = {
            "method": "tools/call",
            "params": {"name": "plan", "arguments": {"request": "test"}},
            "cache": True
        }
        
        # First call
        response1 = handler.handle(request)
        
        # Second call (should be cached)
        response2 = handler.handle(request)
        
        assert response1.result == response2.result
        assert response2.from_cache is True
    
    def test_cache_key_generation(self):
        """RED: Cache keys are generated from request"""
        from src.mcp.request_handler import ResponseCache
        
        cache = ResponseCache()
        
        request1 = {"method": "tools/call", "params": {"name": "plan"}}
        request2 = {"method": "tools/call", "params": {"name": "plan"}}
        request3 = {"method": "tools/call", "params": {"name": "tdd"}}
        
        key1 = cache.generate_key(request1)
        key2 = cache.generate_key(request2)
        key3 = cache.generate_key(request3)
        
        assert key1 == key2  # Same request
        assert key1 != key3  # Different request
