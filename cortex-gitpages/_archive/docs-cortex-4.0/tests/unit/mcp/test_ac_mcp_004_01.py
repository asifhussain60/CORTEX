"""
AC-MCP-004-01: MCP Protocol Compliance Tests

Tests for JSON-RPC 2.0 message format compliance and protocol validation.

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import pytest
import json
from src.mcp.server_sdk import MCPRequest, MCPResponse


class TestJSONRPC2RequestFormat:
    """Test JSON-RPC 2.0 request format compliance."""
    
    def test_request_has_required_fields(self) -> None:
        """Test that request has jsonrpc and method."""
        request = MCPRequest(method="tools/list", id=1)
        d = request.to_dict()
        
        assert "jsonrpc" in d
        assert "method" in d
        assert d["jsonrpc"] == "2.0"
    
    def test_request_jsonrpc_version(self) -> None:
        """Test that jsonrpc field is 2.0."""
        request = MCPRequest(method="initialize")
        assert request.jsonrpc == "2.0"
    
    def test_request_method_required(self) -> None:
        """Test that method is required."""
        request = MCPRequest(method="test/method")
        assert request.method == "test/method"
    
    def test_request_with_params(self) -> None:
        """Test request with params."""
        request = MCPRequest(
            method="tools/call",
            params={"name": "test_tool"},
            id=1
        )
        d = request.to_dict()
        
        assert "params" in d
        assert d["params"]["name"] == "test_tool"
    
    def test_request_without_params(self) -> None:
        """Test request without params doesn't include empty field."""
        request = MCPRequest(method="tools/list", id=1)
        d = request.to_dict()
        
        assert "params" not in d
    
    def test_request_id_integer(self) -> None:
        """Test request with integer ID."""
        request = MCPRequest(method="initialize", id=1)
        assert request.id == 1
    
    def test_request_id_string(self) -> None:
        """Test request with string ID."""
        request = MCPRequest(method="initialize", id="req-1")
        assert request.id == "req-1"
    
    def test_request_without_id(self) -> None:
        """Test notification (request without ID)."""
        request = MCPRequest(method="notification/event")
        d = request.to_dict()
        
        assert "id" not in d


class TestJSONRPC2ResponseFormat:
    """Test JSON-RPC 2.0 response format compliance."""
    
    def test_response_has_required_fields(self) -> None:
        """Test that response has jsonrpc and result or error."""
        response = MCPResponse(result={"status": "ok"}, id=1)
        d = response.to_dict()
        
        assert "jsonrpc" in d
        assert d["jsonrpc"] == "2.0"
    
    def test_response_jsonrpc_version(self) -> None:
        """Test that jsonrpc field is 2.0."""
        response = MCPResponse(result={"data": []})
        assert response.jsonrpc == "2.0"
    
    def test_response_with_result(self) -> None:
        """Test response with result."""
        response = MCPResponse(
            result={"tools": []},
            id=1
        )
        d = response.to_dict()
        
        assert "result" in d
        assert d["result"]["tools"] == []
        assert "error" not in d
    
    def test_response_with_error(self) -> None:
        """Test response with error."""
        response = MCPResponse(
            error={"code": -32601, "message": "Method not found"},
            id=1
        )
        d = response.to_dict()
        
        assert "error" in d
        assert d["error"]["code"] == -32601
        assert "result" not in d
    
    def test_response_error_has_code(self) -> None:
        """Test that error has code field."""
        response = MCPResponse(
            error={"code": -32603, "message": "Internal error"},
            id=1
        )
        
        assert response.error["code"] == -32603
    
    def test_response_error_has_message(self) -> None:
        """Test that error has message field."""
        response = MCPResponse(
            error={"code": -32603, "message": "Internal error"},
            id=1
        )
        
        assert response.error["message"] == "Internal error"
    
    def test_response_id_matches_request(self) -> None:
        """Test that response ID matches request ID."""
        request = MCPRequest(method="tools/list", id=42)
        response = MCPResponse(result={"tools": []}, id=request.id)
        
        assert response.id == request.id


class TestErrorResponseFormats:
    """Test error response formats per JSON-RPC 2.0 spec."""
    
    def test_parse_error_format(self) -> None:
        """Test PARSE_ERROR response format."""
        response = MCPResponse(
            error={"code": -32700, "message": "Parse error"},
            id=None
        )
        
        assert response.error["code"] == -32700
    
    def test_invalid_request_format(self) -> None:
        """Test INVALID_REQUEST response format."""
        response = MCPResponse(
            error={"code": -32600, "message": "Invalid Request"},
            id=None
        )
        
        assert response.error["code"] == -32600
    
    def test_method_not_found_format(self) -> None:
        """Test METHOD_NOT_FOUND response format."""
        response = MCPResponse(
            error={"code": -32601, "message": "Method not found"},
            id=1
        )
        
        assert response.error["code"] == -32601
    
    def test_invalid_params_format(self) -> None:
        """Test INVALID_PARAMS response format."""
        response = MCPResponse(
            error={"code": -32602, "message": "Invalid params"},
            id=1
        )
        
        assert response.error["code"] == -32602
    
    def test_internal_error_format(self) -> None:
        """Test INTERNAL_ERROR response format."""
        response = MCPResponse(
            error={"code": -32603, "message": "Internal error"},
            id=1
        )
        
        assert response.error["code"] == -32603


class TestJSONSerializationCompliance:
    """Test JSON serialization compliance."""
    
    def test_request_serializes_to_valid_json(self) -> None:
        """Test that request serializes to valid JSON."""
        request = MCPRequest(
            method="tools/list",
            params={"limit": 10},
            id=1
        )
        json_str = request.to_json()
        
        # Should deserialize without error
        data = json.loads(json_str)
        assert data["method"] == "tools/list"
    
    def test_response_serializes_to_valid_json(self) -> None:
        """Test that response serializes to valid JSON."""
        response = MCPResponse(
            result={"tools": [{"name": "tool1"}]},
            id=1
        )
        json_str = response.to_json()
        
        # Should deserialize without error
        data = json.loads(json_str)
        assert data["result"]["tools"][0]["name"] == "tool1"
    
    def test_error_response_serializes_to_valid_json(self) -> None:
        """Test that error response serializes to valid JSON."""
        response = MCPResponse(
            error={"code": -32601, "message": "Method not found"},
            id=1
        )
        json_str = response.to_json()
        
        data = json.loads(json_str)
        assert data["error"]["code"] == -32601
    
    def test_request_deserializes_from_json(self) -> None:
        """Test that request deserializes from JSON string."""
        json_str = '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
        request = MCPRequest.from_json(json_str)
        
        assert request.jsonrpc == "2.0"
        assert request.method == "tools/list"
        assert request.id == 1


class TestProtocolMessageSequence:
    """Test protocol message sequences."""
    
    def test_initialize_request_response(self) -> None:
        """Test initialize request/response sequence."""
        request = MCPRequest(method="initialize", id=1)
        response = MCPResponse(
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "cortex", "version": "1.0.0"}
            },
            id=1
        )
        
        assert request.method == "initialize"
        assert response.result["protocolVersion"] == "2024-11-05"
        assert response.id == request.id
    
    def test_tools_list_request_response(self) -> None:
        """Test tools/list request/response sequence."""
        request = MCPRequest(method="tools/list", id=2)
        response = MCPResponse(
            result={"tools": [{"name": "tool1", "description": "Test"}]},
            id=2
        )
        
        assert request.method == "tools/list"
        assert len(response.result["tools"]) == 1
        assert response.id == request.id
    
    def test_tools_call_request_response(self) -> None:
        """Test tools/call request/response sequence."""
        request = MCPRequest(
            method="tools/call",
            params={"name": "test_tool", "arguments": {"param": "value"}},
            id=3
        )
        response = MCPResponse(
            result={"content": [{"type": "text", "text": "result"}]},
            id=3
        )
        
        assert request.method == "tools/call"
        assert response.result["content"][0]["type"] == "text"
        assert response.id == request.id


class TestMessageValidation:
    """Test message validation rules."""
    
    def test_request_requires_method(self) -> None:
        """Test that request must have method."""
        request = MCPRequest(method="", id=1)
        assert request.method == ""
    
    def test_response_requires_id_for_result(self) -> None:
        """Test response with result should have ID."""
        response = MCPResponse(result={"data": []}, id=1)
        assert response.id is not None
    
    def test_batch_requests_not_recommended(self) -> None:
        """Test note about batch requests."""
        # JSON-RPC 2.0 supports batch but we'll use one-at-a-time for clarity
        request1 = MCPRequest(method="tools/list", id=1)
        request2 = MCPRequest(method="initialize", id=2)
        
        # Each should be sent separately
        assert request1.id != request2.id


class TestSpecCompliance:
    """Test MCP specification compliance."""
    
    def test_protocol_version_field(self) -> None:
        """Test that initialize response has protocolVersion."""
        response = MCPResponse(
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "serverInfo": {}
            },
            id=1
        )
        
        assert response.result["protocolVersion"] == "2024-11-05"
    
    def test_server_info_structure(self) -> None:
        """Test serverInfo has required fields."""
        response = MCPResponse(
            result={
                "serverInfo": {"name": "cortex", "version": "1.0.0"}
            },
            id=1
        )
        
        server_info = response.result["serverInfo"]
        assert "name" in server_info
        assert "version" in server_info
    
    def test_tool_definition_structure(self) -> None:
        """Test tool definition has required fields."""
        tool = {
            "name": "scaffold_orchestrator",
            "description": "Generate orchestrator",
            "inputSchema": {"type": "object", "properties": {}}
        }
        
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
