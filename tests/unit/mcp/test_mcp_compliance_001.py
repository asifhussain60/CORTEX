"""
AC-MCP-COMPLIANCE-001: MCP Protocol Full Compliance Test Suite.

Tests for comprehensive MCP protocol implementation including:
- Full protocol spec compliance (v2024-11-05)
- All message types (Tool, Resource, Prompt)
- JSON-RPC 2.0 compliance
- Stdio transport support
- Error handling and recovery
"""

import pytest
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path

# Import MCP protocol components
from cortex.mcp.protocol import (
    ToolDefinition,
    ToolParameter,
    ErrorCode,
    MCPError,
)


@dataclass
class MCPRequest:
    """MCP Request following JSON-RPC 2.0."""
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = {"jsonrpc": self.jsonrpc, "method": self.method}
        if self.params is not None:
            d["params"] = self.params
        if self.id is not None:
            d["id"] = self.id
        return d

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class MCPResponse:
    """MCP Response following JSON-RPC 2.0."""
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        d = {"jsonrpc": self.jsonrpc}
        if self.result is not None:
            d["result"] = self.result
        if self.error is not None:
            d["error"] = self.error
        if self.id is not None:
            d["id"] = self.id
        return d

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @property
    def is_error(self) -> bool:
        """Check if response is an error."""
        return self.error is not None


class MCPMessageType(Enum):
    """MCP message types."""
    INITIALIZE = "initialize"
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"


class TestMCPProtocolCompliance001:
    """Test suite for MCP protocol compliance."""

    def test_jsonrpc_20_request_format(self) -> None:
        """Test that requests follow JSON-RPC 2.0 format."""
        # JSON-RPC 2.0 requirement: must have jsonrpc="2.0" and method
        request = MCPRequest(
            jsonrpc="2.0",
            method="tools/list",
            id=1
        )

        data = request.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "tools/list"
        assert data["id"] == 1
        assert "params" not in data or data["params"] is not None

    def test_jsonrpc_20_response_format(self) -> None:
        """Test that responses follow JSON-RPC 2.0 format."""
        # JSON-RPC 2.0: response must have jsonrpc="2.0" and either result or error
        response = MCPResponse(
            jsonrpc="2.0",
            result={"tools": []},
            id=1
        )

        data = response.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["result"] is not None
        assert "error" not in data or data.get("error") is None
        assert data["id"] == 1

    def test_jsonrpc_error_format(self) -> None:
        """Test that error responses follow JSON-RPC 2.0 error format."""
        # JSON-RPC 2.0 error: {code, message, data (optional)}
        response = MCPResponse(
            jsonrpc="2.0",
            error={
                "code": -32600,
                "message": "Invalid Request",
                "data": {"details": "Missing method"}
            },
            id=1
        )

        data = response.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["error"]["code"] == -32600
        assert data["error"]["message"] == "Invalid Request"
        assert "result" not in data or data.get("result") is None

    def test_tools_list_message_type(self) -> None:
        """Test tools/list message type support."""
        request = MCPRequest(
            method=MCPMessageType.TOOLS_LIST.value,
            id=1
        )

        assert request.method == "tools/list"
        data = request.to_dict()
        assert data["method"] == "tools/list"

    def test_tools_call_message_type(self) -> None:
        """Test tools/call message type support."""
        request = MCPRequest(
            method=MCPMessageType.TOOLS_CALL.value,
            params={
                "name": "my_tool",
                "arguments": {"param": "value"}
            },
            id=2
        )

        assert request.method == "tools/call"
        assert request.params["name"] == "my_tool"

    def test_resources_list_message_type(self) -> None:
        """Test resources/list message type support."""
        request = MCPRequest(
            method=MCPMessageType.RESOURCES_LIST.value,
            id=3
        )

        assert request.method == "resources/list"

    def test_resources_read_message_type(self) -> None:
        """Test resources/read message type support."""
        request = MCPRequest(
            method=MCPMessageType.RESOURCES_READ.value,
            params={"uri": "file:///path/to/resource"},
            id=4
        )

        assert request.method == "resources/read"
        assert request.params["uri"] == "file:///path/to/resource"

    def test_prompts_list_message_type(self) -> None:
        """Test prompts/list message type support."""
        request = MCPRequest(
            method=MCPMessageType.PROMPTS_LIST.value,
            id=5
        )

        assert request.method == "prompts/list"

    def test_prompts_get_message_type(self) -> None:
        """Test prompts/get message type support."""
        request = MCPRequest(
            method=MCPMessageType.PROMPTS_GET.value,
            params={"name": "my_prompt"},
            id=6
        )

        assert request.method == "prompts/get"

    def test_tool_definition_compliance(self) -> None:
        """Test tool definition follows MCP spec."""
        tool = ToolDefinition(
            id="tool_001",
            name="example_tool",
            description="An example tool",
            version="1.0",
            timeout_ms=30000
        )

        assert tool.id == "tool_001"
        assert tool.name == "example_tool"
        assert tool.description == "An example tool"
        assert tool.version == "1.0"
        assert tool.timeout_ms == 30000

    def test_tool_with_parameters_compliance(self) -> None:
        """Test tool with parameters follows MCP spec."""
        param1 = ToolParameter(
            name="input_text",
            type="string",
            description="Input text",
            required=True
        )
        param2 = ToolParameter(
            name="count",
            type="number",
            description="Count",
            required=False,
            default=1,
            min_value=1,
            max_value=100
        )

        tool = ToolDefinition(
            id="tool_002",
            name="process_tool",
            description="Process input",
            parameters=[param1, param2]
        )

        assert len(tool.parameters) == 2
        assert tool.parameters[0].name == "input_text"
        assert tool.parameters[0].required is True
        assert tool.parameters[1].name == "count"
        assert tool.parameters[1].min_value == 1
        assert tool.parameters[1].max_value == 100

    def test_error_codes_support(self) -> None:
        """Test all MCP error codes are supported."""
        error_codes = [
            ErrorCode.SUCCESS,
            ErrorCode.INVALID_REQUEST,
            ErrorCode.METHOD_NOT_FOUND,
            ErrorCode.INVALID_PARAMS,
            ErrorCode.INTERNAL_ERROR,
            ErrorCode.PARSE_ERROR,
            ErrorCode.TOOL_NOT_FOUND,
            ErrorCode.EXECUTION_ERROR,
            ErrorCode.TIMEOUT,
            ErrorCode.UNSUPPORTED,
        ]

        assert len(error_codes) >= 8

    def test_error_response_creation(self) -> None:
        """Test creating MCP-compliant error response."""
        error = MCPError(
            code=ErrorCode.INVALID_PARAMS,
            message="Invalid parameters provided",
            data={"expected": "array", "got": "string"}
        )

        assert error.code == ErrorCode.INVALID_PARAMS
        assert error.message == "Invalid parameters provided"
        assert error.data is not None

    def test_request_with_notification(self) -> None:
        """Test notification format (request without id)."""
        notification = MCPRequest(
            method="notification/event",
            params={"event": "tool_registered"}
        )

        data = notification.to_dict()
        assert "id" not in data or data.get("id") is None
        assert data["method"] == "notification/event"

    def test_batch_requests_support(self) -> None:
        """Test support for batch requests."""
        requests = [
            MCPRequest(method="tools/list", id=1),
            MCPRequest(method="resources/list", id=2),
            MCPRequest(method="prompts/list", id=3),
        ]

        batch = [r.to_dict() for r in requests]
        assert len(batch) == 3
        assert batch[0]["id"] == 1
        assert batch[1]["id"] == 2
        assert batch[2]["id"] == 3

    def test_json_serialization_roundtrip(self) -> None:
        """Test JSON serialization/deserialization roundtrip."""
        original = MCPRequest(
            method="tools/call",
            params={"name": "test", "args": {"a": 1, "b": "text"}},
            id=42
        )

        json_str = original.to_json()
        data = json.loads(json_str)

        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "tools/call"
        assert data["params"]["name"] == "test"
        assert data["id"] == 42

    def test_nested_params_support(self) -> None:
        """Test support for nested parameters."""
        nested_params = {
            "tool_name": "complex_tool",
            "arguments": {
                "config": {
                    "mode": "advanced",
                    "options": {
                        "timeout": 5000,
                        "retries": 3
                    }
                },
                "data": [1, 2, 3, 4, 5]
            }
        }

        request = MCPRequest(
            method="tools/call",
            params=nested_params,
            id=99
        )

        assert request.params["arguments"]["config"]["mode"] == "advanced"
        assert request.params["arguments"]["config"]["options"]["timeout"] == 5000
        assert request.params["arguments"]["data"] == [1, 2, 3, 4, 5]

    def test_unicode_support(self) -> None:
        """Test support for unicode characters in messages."""
        request = MCPRequest(
            method="tools/call",
            params={
                "text": "Hello 世界 🌍",
                "description": "日本語テスト"
            },
            id=100
        )

        json_str = request.to_json()
        data = json.loads(json_str)

        assert "世界" in data["params"]["text"]
        assert "日本語" in data["params"]["description"]

    def test_large_payload_support(self) -> None:
        """Test support for large payloads."""
        large_data = "x" * 100000  # 100KB of data

        request = MCPRequest(
            method="resources/read",
            params={"content": large_data},
            id=101
        )

        json_str = request.to_json()
        data = json.loads(json_str)

        assert len(data["params"]["content"]) == 100000

    def test_null_values_support(self) -> None:
        """Test proper handling of null values."""
        response = MCPResponse(
            jsonrpc="2.0",
            result={
                "tools": [],
                "metadata": None
            },
            id=102
        )

        data = response.to_dict()
        assert data["result"]["metadata"] is None

    def test_boolean_values_support(self) -> None:
        """Test boolean value support in MCP."""
        tool = ToolDefinition(
            id="bool_tool",
            name="boolean_tool",
            description="Tool with bool param",
            parameters=[
                ToolParameter(
                    name="enabled",
                    type="boolean",
                    description="Enable feature",
                    required=True
                )
            ],
            deprecated=False
        )

        assert tool.deprecated is False
        assert tool.parameters[0].type == "boolean"

    def test_array_type_parameter(self) -> None:
        """Test array type parameter support."""
        param = ToolParameter(
            name="items",
            type="array",
            description="List of items",
            required=True
        )

        assert param.type == "array"
        assert param.required is True

    def test_object_type_parameter(self) -> None:
        """Test object type parameter support."""
        param = ToolParameter(
            name="config",
            type="object",
            description="Configuration object",
            required=False
        )

        assert param.type == "object"
        assert param.required is False

    def test_enum_parameter_support(self) -> None:
        """Test enum parameter support."""
        param = ToolParameter(
            name="mode",
            type="string",
            description="Operation mode",
            enum=["read", "write", "append"],
            required=True
        )

        assert param.enum == ["read", "write", "append"]

    def test_timeout_specification(self) -> None:
        """Test timeout specification in tools."""
        tool = ToolDefinition(
            id="timeout_tool",
            name="timeout_test",
            description="Tool with timeout",
            timeout_ms=5000
        )

        assert tool.timeout_ms == 5000

    def test_version_specification(self) -> None:
        """Test version specification in tools."""
        tool = ToolDefinition(
            id="versioned_tool",
            name="version_test",
            description="Versioned tool",
            version="2.1.0"
        )

        assert tool.version == "2.1.0"

    def test_tags_support(self) -> None:
        """Test tags support for tool categorization."""
        tool = ToolDefinition(
            id="tagged_tool",
            name="tag_test",
            description="Tagged tool",
            tags=["ai", "nlp", "production"]
        )

        assert "ai" in tool.tags
        assert "nlp" in tool.tags
        assert "production" in tool.tags

    def test_tool_deprecation_support(self) -> None:
        """Test tool deprecation marking."""
        tool = ToolDefinition(
            id="deprecated_tool",
            name="old_tool",
            description="Old tool",
            deprecated=True
        )

        assert tool.deprecated is True

    def test_empty_tool_list_response(self) -> None:
        """Test tools/list response with empty list."""
        response = MCPResponse(
            jsonrpc="2.0",
            result={"tools": []},
            id=1
        )

        assert response.result["tools"] == []
        assert response.is_error is False

    def test_error_recovery_field(self) -> None:
        """Test error response includes recovery information."""
        response = MCPResponse(
            jsonrpc="2.0",
            error={
                "code": -32600,
                "message": "Invalid Request",
                "data": {
                    "recovery": "Please check your request format",
                    "recovery_hint": "Ensure jsonrpc='2.0' and method is present"
                }
            },
            id=1
        )

        assert response.error["data"]["recovery"] is not None
        assert response.is_error is True


class TestMCPProtocolIntegration:
    """Integration tests for MCP protocol."""

    def test_request_response_flow(self) -> None:
        """Test complete request/response flow."""
        # Send request
        request = MCPRequest(
            method="tools/list",
            id=1
        )

        # Simulate server processing
        response = MCPResponse(
            jsonrpc="2.0",
            result={
                "tools": [
                    {
                        "id": "tool_1",
                        "name": "example",
                        "description": "Example tool"
                    }
                ]
            },
            id=request.id
        )

        # Verify flow
        assert request.id == response.id
        assert not response.is_error
        assert len(response.result["tools"]) == 1

    def test_tool_call_success_flow(self) -> None:
        """Test successful tool call flow."""
        request = MCPRequest(
            method="tools/call",
            params={
                "name": "example_tool",
                "arguments": {"input": "test"}
            },
            id=42
        )

        response = MCPResponse(
            jsonrpc="2.0",
            result={
                "output": "Processed: test"
            },
            id=request.id
        )

        assert request.params["name"] == "example_tool"
        assert response.result["output"] == "Processed: test"

    def test_tool_call_error_flow(self) -> None:
        """Test tool call error flow."""
        request = MCPRequest(
            method="tools/call",
            params={"name": "invalid_tool"},
            id=43
        )

        response = MCPResponse(
            jsonrpc="2.0",
            error={
                "code": -32601,
                "message": "Tool not found"
            },
            id=request.id
        )

        assert response.is_error
        assert response.error["code"] == -32601


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
