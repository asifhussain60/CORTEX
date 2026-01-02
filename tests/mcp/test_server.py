"""
Comprehensive tests for MCP Server implementation.

Tests cover protocol compliance, tool registration, request handling,
error scenarios, and metrics tracking.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import time
from src.mcp.server import (
    MCPServer,
    MCPRequest,
    MCPResponse,
    mcp_tool,
    MCPVersion,
    RequestStatus
)


class TestMCPRequest:
    """Test MCPRequest dataclass."""
    
    def test_request_creation(self):
        """Create request with required fields."""
        req = MCPRequest(
            version="1.0",
            tool="test_tool",
            parameters={"param1": "value1"}
        )
        assert req.version == "1.0"
        assert req.tool == "test_tool"
        assert req.parameters == {"param1": "value1"}
        assert req.timestamp is not None
    
    def test_request_with_optional_fields(self):
        """Create request with optional fields."""
        req = MCPRequest(
            version="1.0",
            tool="test_tool",
            parameters={},
            request_id="req-123",
            timestamp=1234567890.0
        )
        assert req.request_id == "req-123"
        assert req.timestamp == 1234567890.0


class TestMCPResponse:
    """Test MCPResponse dataclass."""
    
    def test_success_response(self):
        """Create successful response."""
        resp = MCPResponse(
            status=RequestStatus.SUCCESS,
            tool="test_tool",
            result={"data": "value"}
        )
        assert resp.status == RequestStatus.SUCCESS
        assert resp.result == {"data": "value"}
        assert resp.error is None
    
    def test_error_response(self):
        """Create error response."""
        resp = MCPResponse(
            status=RequestStatus.ERROR,
            tool="test_tool",
            error="Something went wrong"
        )
        assert resp.status == RequestStatus.ERROR
        assert resp.error == "Something went wrong"
        assert resp.result is None
    
    def test_response_to_dict(self):
        """Convert response to dictionary."""
        resp = MCPResponse(
            status=RequestStatus.SUCCESS,
            tool="test_tool",
            result={"data": "value"},
            request_id="req-123"
        )
        d = resp.to_dict()
        assert "status" in d
        assert "tool" in d
        assert "result" in d
        assert "request_id" in d
        # error key may be omitted if None, or included with None value
        assert d.get("error") is None


class TestMCPServerInitialization:
    """Test MCPServer initialization and lifecycle."""
    
    def test_server_creation(self):
        """Create MCP server with default version."""
        server = MCPServer()
        assert server.version == MCPVersion.V1_0
        assert len(server.tools) == 0
        assert not server.is_running()
    
    def test_server_custom_version(self):
        """Create server with custom version."""
        server = MCPServer(version="1.0")
        assert server.version == "1.0"
    
    def test_server_start_stop(self):
        """Start and stop server."""
        server = MCPServer()
        
        assert not server.is_running()
        
        server.start()
        assert server.is_running()
        
        server.stop()
        assert not server.is_running()
    
    def test_server_double_start(self):
        """Starting already running server."""
        server = MCPServer()
        server.start()
        server.start()  # Should log warning, not crash
        assert server.is_running()
        server.stop()
    
    def test_server_double_stop(self):
        """Stopping already stopped server."""
        server = MCPServer()
        server.stop()  # Should log warning, not crash
        assert not server.is_running()


class TestToolRegistration:
    """Test tool registration and management."""
    
    def test_register_tool(self):
        """Register a tool handler."""
        server = MCPServer()
        
        def my_tool(param1: str) -> dict:
            return {"result": param1}
        
        server.register_tool("my_tool", my_tool)
        assert "my_tool" in server.list_tools()
        assert len(server.list_tools()) == 1
    
    def test_register_duplicate_tool(self):
        """Cannot register same tool twice."""
        server = MCPServer()
        
        def my_tool():
            return {}
        
        server.register_tool("my_tool", my_tool)
        
        with pytest.raises(ValueError, match="already registered"):
            server.register_tool("my_tool", my_tool)
    
    def test_unregister_tool(self):
        """Unregister a tool."""
        server = MCPServer()
        
        def my_tool():
            return {}
        
        server.register_tool("my_tool", my_tool)
        assert "my_tool" in server.list_tools()
        
        server.unregister_tool("my_tool")
        assert "my_tool" not in server.list_tools()
    
    def test_unregister_nonexistent_tool(self):
        """Cannot unregister tool that doesn't exist."""
        server = MCPServer()
        
        with pytest.raises(KeyError, match="not registered"):
            server.unregister_tool("nonexistent")
    
    def test_list_tools_empty(self):
        """List tools when none registered."""
        server = MCPServer()
        assert server.list_tools() == []
    
    def test_list_tools_multiple(self):
        """List multiple registered tools."""
        server = MCPServer()
        
        server.register_tool("tool1", lambda: {})
        server.register_tool("tool2", lambda: {})
        server.register_tool("tool3", lambda: {})
        
        tools = server.list_tools()
        assert len(tools) == 3
        assert "tool1" in tools
        assert "tool2" in tools
        assert "tool3" in tools


class TestRequestValidation:
    """Test request validation logic."""
    
    def test_valid_request(self):
        """Validate well-formed request."""
        server = MCPServer()
        server.register_tool("test_tool", lambda: {})
        
        request_data = {
            "version": "1.0",
            "tool": "test_tool",
            "parameters": {"param1": "value1"}
        }
        
        req = server.validate_request(request_data)
        assert isinstance(req, MCPRequest)
        assert req.version == "1.0"
        assert req.tool == "test_tool"
    
    def test_missing_version(self):
        """Request missing version field."""
        server = MCPServer()
        
        request_data = {
            "tool": "test_tool",
            "parameters": {}
        }
        
        with pytest.raises(ValueError, match="Missing required fields"):
            server.validate_request(request_data)
    
    def test_missing_tool(self):
        """Request missing tool field."""
        server = MCPServer()
        
        request_data = {
            "version": "1.0",
            "parameters": {}
        }
        
        with pytest.raises(ValueError, match="Missing required fields"):
            server.validate_request(request_data)
    
    def test_missing_parameters(self):
        """Request missing parameters field."""
        server = MCPServer()
        server.register_tool("test_tool", lambda: {})
        
        request_data = {
            "version": "1.0",
            "tool": "test_tool"
        }
        
        with pytest.raises(ValueError, match="Missing required fields"):
            server.validate_request(request_data)
    
    def test_wrong_version(self):
        """Request with unsupported version."""
        server = MCPServer(version="1.0")
        server.register_tool("test_tool", lambda: {})
        
        request_data = {
            "version": "2.0",
            "tool": "test_tool",
            "parameters": {}
        }
        
        with pytest.raises(ValueError, match="Unsupported protocol version"):
            server.validate_request(request_data)
    
    def test_unknown_tool(self):
        """Request for unregistered tool."""
        server = MCPServer()
        
        request_data = {
            "version": "1.0",
            "tool": "nonexistent_tool",
            "parameters": {}
        }
        
        with pytest.raises(ValueError, match="Unknown tool"):
            server.validate_request(request_data)
    
    def test_invalid_parameters_type(self):
        """Parameters must be a dictionary."""
        server = MCPServer()
        server.register_tool("test_tool", lambda: {})
        
        request_data = {
            "version": "1.0",
            "tool": "test_tool",
            "parameters": "not a dict"
        }
        
        with pytest.raises(ValueError, match="Parameters must be a dictionary"):
            server.validate_request(request_data)


class TestRequestHandling:
    """Test request handling and execution."""
    
    def test_successful_request(self):
        """Handle successful request."""
        server = MCPServer()
        
        def echo_tool(message: str) -> dict:
            return {"echo": message}
        
        server.register_tool("echo", echo_tool)
        
        request_data = {
            "version": "1.0",
            "tool": "echo",
            "parameters": {"message": "hello"}
        }
        
        response = server.handle_request(request_data)
        assert response.status == RequestStatus.SUCCESS
        assert response.result == {"echo": "hello"}
        assert response.error is None
        assert response.execution_time is not None
    
    def test_request_with_id(self):
        """Request ID is preserved in response."""
        server = MCPServer()
        server.register_tool("test", lambda: {"data": "value"})
        
        request_data = {
            "version": "1.0",
            "tool": "test",
            "parameters": {},
            "request_id": "req-abc-123"
        }
        
        response = server.handle_request(request_data)
        assert response.request_id == "req-abc-123"
    
    def test_tool_execution_error(self):
        """Tool raises exception during execution."""
        server = MCPServer()
        
        def failing_tool():
            raise RuntimeError("Tool failed")
        
        server.register_tool("failing", failing_tool)
        
        request_data = {
            "version": "1.0",
            "tool": "failing",
            "parameters": {}
        }
        
        response = server.handle_request(request_data)
        assert response.status == RequestStatus.ERROR
        assert "Tool execution failed" in response.error
        assert "Tool failed" in response.error
    
    def test_malformed_request(self):
        """Malformed request returns error response."""
        server = MCPServer()
        
        request_data = {
            "version": "1.0"
            # Missing tool and parameters
        }
        
        response = server.handle_request(request_data)
        assert response.status == RequestStatus.ERROR
        assert "Invalid request" in response.error


class TestMetrics:
    """Test metrics collection and reporting."""
    
    def test_initial_metrics(self):
        """Server starts with zero metrics."""
        server = MCPServer()
        metrics = server.get_metrics()
        
        assert metrics["total_requests"] == 0
        assert metrics["successful_requests"] == 0
        assert metrics["failed_requests"] == 0
        assert metrics["average_execution_time"] == 0.0
        assert metrics["success_rate"] == 0.0
    
    def test_metrics_after_success(self):
        """Metrics updated after successful request."""
        server = MCPServer()
        server.register_tool("test", lambda: {"data": "value"})
        
        request_data = {
            "version": "1.0",
            "tool": "test",
            "parameters": {}
        }
        
        server.handle_request(request_data)
        metrics = server.get_metrics()
        
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["failed_requests"] == 0
        assert metrics["success_rate"] == 1.0
        assert metrics["average_execution_time"] > 0.0
    
    def test_metrics_after_failure(self):
        """Metrics updated after failed request."""
        server = MCPServer()
        
        request_data = {
            "version": "1.0",
            "tool": "nonexistent",
            "parameters": {}
        }
        
        server.handle_request(request_data)
        metrics = server.get_metrics()
        
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 0
        assert metrics["failed_requests"] == 1
        assert metrics["success_rate"] == 0.0
    
    def test_metrics_mixed_requests(self):
        """Metrics track mixed success/failure."""
        server = MCPServer()
        server.register_tool("success", lambda: {"ok": True})
        server.register_tool("fail", lambda: 1/0)  # Will raise ZeroDivisionError
        
        # 3 successful requests
        for _ in range(3):
            server.handle_request({
                "version": "1.0",
                "tool": "success",
                "parameters": {}
            })
        
        # 2 failed requests
        for _ in range(2):
            server.handle_request({
                "version": "1.0",
                "tool": "fail",
                "parameters": {}
            })
        
        metrics = server.get_metrics()
        assert metrics["total_requests"] == 5
        assert metrics["successful_requests"] == 3
        assert metrics["failed_requests"] == 2
        assert metrics["success_rate"] == 0.6
    
    def test_reset_metrics(self):
        """Reset metrics to zero."""
        server = MCPServer()
        server.register_tool("test", lambda: {})
        
        # Generate some metrics
        server.handle_request({
            "version": "1.0",
            "tool": "test",
            "parameters": {}
        })
        
        assert server.get_metrics()["total_requests"] == 1
        
        # Reset
        server.reset_metrics()
        metrics = server.get_metrics()
        
        assert metrics["total_requests"] == 0
        assert metrics["successful_requests"] == 0
        assert metrics["failed_requests"] == 0


class TestMCPToolDecorator:
    """Test @mcp_tool decorator."""
    
    def test_decorator_marks_function(self):
        """Decorator adds _is_mcp_tool attribute."""
        @mcp_tool
        def my_tool():
            return {}
        
        assert hasattr(my_tool, "_is_mcp_tool")
        assert my_tool._is_mcp_tool is True
    
    def test_decorated_function_works(self):
        """Decorated function executes normally."""
        @mcp_tool
        def add_numbers(a: int, b: int) -> dict:
            return {"sum": a + b}
        
        result = add_numbers(5, 3)
        assert result == {"sum": 8}


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_complete_workflow(self):
        """Complete server lifecycle with multiple requests."""
        server = MCPServer()
        
        # Register tools
        @mcp_tool
        def calculator(operation: str, a: int, b: int) -> dict:
            ops = {
                "add": a + b,
                "subtract": a - b,
                "multiply": a * b
            }
            return {"result": ops.get(operation, 0)}
        
        server.register_tool("calculator", calculator)
        server.start()
        
        # Execute requests
        response1 = server.handle_request({
            "version": "1.0",
            "tool": "calculator",
            "parameters": {"operation": "add", "a": 10, "b": 5},
            "request_id": "calc-1"
        })
        
        response2 = server.handle_request({
            "version": "1.0",
            "tool": "calculator",
            "parameters": {"operation": "multiply", "a": 3, "b": 7},
            "request_id": "calc-2"
        })
        
        # Validate responses
        assert response1.status == RequestStatus.SUCCESS
        assert response1.result["result"] == 15
        assert response1.request_id == "calc-1"
        
        assert response2.status == RequestStatus.SUCCESS
        assert response2.result["result"] == 21
        assert response2.request_id == "calc-2"
        
        # Check metrics
        metrics = server.get_metrics()
        assert metrics["total_requests"] == 2
        assert metrics["successful_requests"] == 2
        assert metrics["success_rate"] == 1.0
        
        server.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
