"""
Tests for JSON-RPC 2.0 Server Implementation (MCP)

Test-Driven Development for Model Context Protocol's JSON-RPC 2.0 server.
Tests MUST fail first (RED phase), then implementation makes them pass (GREEN phase).

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P1-T1.1
"""

import pytest
import json
from typing import Dict, Any, Optional
from pathlib import Path


class TestJSONRPCMessage:
    """Test JSON-RPC 2.0 message formatting"""
    
    def test_request_message_structure(self):
        """RED: Request message must have jsonrpc, method, params, id"""
        from src.mcp.jsonrpc_server import JSONRPCRequest
        
        request = JSONRPCRequest(
            method="initialize",
            params={"clientInfo": {"name": "test"}},
            id=1
        )
        
        data = request.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "initialize"
        assert data["params"] == {"clientInfo": {"name": "test"}}
        assert data["id"] == 1
    
    def test_response_message_structure(self):
        """RED: Response message must have jsonrpc, result, id"""
        from src.mcp.jsonrpc_server import JSONRPCResponse
        
        response = JSONRPCResponse(
            result={"status": "initialized"},
            id=1
        )
        
        data = response.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["result"] == {"status": "initialized"}
        assert data["id"] == 1
        assert "error" not in data
    
    def test_error_response_structure(self):
        """RED: Error response must have jsonrpc, error (code, message), id"""
        from src.mcp.jsonrpc_server import JSONRPCError, JSONRPCResponse
        
        error = JSONRPCError(code=-32601, message="Method not found")
        response = JSONRPCResponse(error=error, id=1)
        
        data = response.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["error"]["code"] == -32601
        assert data["error"]["message"] == "Method not found"
        assert data["id"] == 1
        assert "result" not in data
    
    def test_notification_message_no_id(self):
        """RED: Notification must not have id field"""
        from src.mcp.jsonrpc_server import JSONRPCNotification
        
        notification = JSONRPCNotification(
            method="progress",
            params={"percent": 50}
        )
        
        data = notification.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "progress"
        assert data["params"] == {"percent": 50}
        assert "id" not in data


class TestJSONRPCErrorCodes:
    """Test JSON-RPC 2.0 standard error codes"""
    
    def test_parse_error(self):
        """RED: Parse error code -32700"""
        from src.mcp.jsonrpc_server import JSONRPCErrorCode
        
        assert JSONRPCErrorCode.PARSE_ERROR == -32700
    
    def test_invalid_request(self):
        """RED: Invalid request code -32600"""
        from src.mcp.jsonrpc_server import JSONRPCErrorCode
        
        assert JSONRPCErrorCode.INVALID_REQUEST == -32600
    
    def test_method_not_found(self):
        """RED: Method not found code -32601"""
        from src.mcp.jsonrpc_server import JSONRPCErrorCode
        
        assert JSONRPCErrorCode.METHOD_NOT_FOUND == -32601
    
    def test_invalid_params(self):
        """RED: Invalid params code -32602"""
        from src.mcp.jsonrpc_server import JSONRPCErrorCode
        
        assert JSONRPCErrorCode.INVALID_PARAMS == -32602
    
    def test_internal_error(self):
        """RED: Internal error code -32603"""
        from src.mcp.jsonrpc_server import JSONRPCErrorCode
        
        assert JSONRPCErrorCode.INTERNAL_ERROR == -32603


class TestJSONRPCServer:
    """Test JSON-RPC 2.0 server request handling"""
    
    def test_parse_valid_request(self):
        """RED: Server parses valid JSON-RPC request"""
        from src.mcp.jsonrpc_server import JSONRPCServer
        
        server = JSONRPCServer()
        raw_message = '{"jsonrpc": "2.0", "method": "test", "params": {}, "id": 1}'
        
        request = server.parse_request(raw_message)
        assert request.method == "test"
        assert request.id == 1
    
    def test_parse_invalid_json_returns_error(self):
        """RED: Invalid JSON returns parse error"""
        from src.mcp.jsonrpc_server import JSONRPCServer, JSONRPCErrorCode
        
        server = JSONRPCServer()
        raw_message = '{"invalid json'
        
        response = server.handle_message(raw_message)
        assert response.error is not None
        assert response.error.code == JSONRPCErrorCode.PARSE_ERROR
    
    def test_missing_jsonrpc_field_returns_error(self):
        """RED: Missing jsonrpc field returns invalid request error"""
        from src.mcp.jsonrpc_server import JSONRPCServer, JSONRPCErrorCode
        
        server = JSONRPCServer()
        raw_message = '{"method": "test", "id": 1}'
        
        response = server.handle_message(raw_message)
        assert response.error is not None
        assert response.error.code == JSONRPCErrorCode.INVALID_REQUEST
    
    def test_method_handler_registration(self):
        """RED: Server registers method handlers"""
        from src.mcp.jsonrpc_server import JSONRPCServer
        
        server = JSONRPCServer()
        
        def test_handler(params):
            return {"result": "success"}
        
        server.register_method("test_method", test_handler)
        assert "test_method" in server.methods
    
    def test_call_registered_method(self):
        """RED: Server calls registered method and returns result"""
        from src.mcp.jsonrpc_server import JSONRPCServer
        
        server = JSONRPCServer()
        
        def echo_handler(params):
            return params
        
        server.register_method("echo", echo_handler)
        
        raw_message = '{"jsonrpc": "2.0", "method": "echo", "params": {"msg": "hello"}, "id": 1}'
        response = server.handle_message(raw_message)
        
        assert response.error is None
        assert response.result == {"msg": "hello"}
        assert response.id == 1
    
    def test_unregistered_method_returns_error(self):
        """RED: Calling unregistered method returns method not found error"""
        from src.mcp.jsonrpc_server import JSONRPCServer, JSONRPCErrorCode
        
        server = JSONRPCServer()
        raw_message = '{"jsonrpc": "2.0", "method": "unknown", "params": {}, "id": 1}'
        
        response = server.handle_message(raw_message)
        assert response.error is not None
        assert response.error.code == JSONRPCErrorCode.METHOD_NOT_FOUND
    
    def test_notification_no_response(self):
        """RED: Notifications (no id) should not generate response"""
        from src.mcp.jsonrpc_server import JSONRPCServer
        
        server = JSONRPCServer()
        
        def log_handler(params):
            return {"logged": True}
        
        server.register_method("log", log_handler)
        
        raw_message = '{"jsonrpc": "2.0", "method": "log", "params": {"msg": "test"}}'
        response = server.handle_message(raw_message)
        
        assert response is None  # Notifications don't return responses
    
    def test_batch_request_support(self):
        """RED: Server handles batch requests (array of requests)"""
        from src.mcp.jsonrpc_server import JSONRPCServer
        
        server = JSONRPCServer()
        
        def add_handler(params):
            return params["a"] + params["b"]
        
        server.register_method("add", add_handler)
        
        raw_message = '''[
            {"jsonrpc": "2.0", "method": "add", "params": {"a": 1, "b": 2}, "id": 1},
            {"jsonrpc": "2.0", "method": "add", "params": {"a": 3, "b": 4}, "id": 2}
        ]'''
        
        responses = server.handle_batch(raw_message)
        assert len(responses) == 2
        assert responses[0].result == 3
        assert responses[1].result == 7


class TestStdioTransport:
    """Test stdin/stdout transport layer for MCP"""
    
    def test_read_message_from_stdin(self):
        """RED: Transport reads newline-delimited messages from stdin"""
        from src.mcp.jsonrpc_server import StdioTransport
        from io import StringIO
        
        stdin_mock = StringIO('{"jsonrpc": "2.0", "method": "test", "id": 1}\n')
        transport = StdioTransport(stdin=stdin_mock)
        
        message = transport.read_message()
        assert message == '{"jsonrpc": "2.0", "method": "test", "id": 1}'
    
    def test_write_message_to_stdout(self):
        """RED: Transport writes newline-delimited messages to stdout"""
        from src.mcp.jsonrpc_server import StdioTransport
        from io import StringIO
        
        stdout_mock = StringIO()
        transport = StdioTransport(stdout=stdout_mock)
        
        transport.write_message('{"jsonrpc": "2.0", "result": {}, "id": 1}')
        
        output = stdout_mock.getvalue()
        assert output == '{"jsonrpc": "2.0", "result": {}, "id": 1}\n'
    
    def test_transport_closes_gracefully(self):
        """RED: Transport closes stdin/stdout gracefully"""
        from src.mcp.jsonrpc_server import StdioTransport
        from io import StringIO
        
        stdin_mock = StringIO()
        stdout_mock = StringIO()
        transport = StdioTransport(stdin=stdin_mock, stdout=stdout_mock)
        
        transport.close()
        assert stdin_mock.closed
        assert stdout_mock.closed


class TestMCPServerIntegration:
    """Integration tests for MCP server with JSON-RPC"""
    
    def test_server_with_stdio_transport(self):
        """RED: Server integrates with stdio transport"""
        from src.mcp.jsonrpc_server import JSONRPCServer, StdioTransport
        from io import StringIO
        
        stdin_mock = StringIO('{"jsonrpc": "2.0", "method": "ping", "id": 1}\n')
        stdout_mock = StringIO()
        
        server = JSONRPCServer()
        transport = StdioTransport(stdin=stdin_mock, stdout=stdout_mock)
        
        def ping_handler(params):
            return {"pong": True}
        
        server.register_method("ping", ping_handler)
        
        # Process one message
        message = transport.read_message()
        response = server.handle_message(message)
        transport.write_message(response.to_json())
        
        output = json.loads(stdout_mock.getvalue().strip())
        assert output["result"] == {"pong": True}
        assert output["id"] == 1
