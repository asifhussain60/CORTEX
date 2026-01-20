"""
AC-MCP-001-01: MCP SDK Server Implementation Tests

Tests for MCP protocol server with JSON-RPC 2.0 and stdio transport.
Verifies:
- JSON-RPC 2.0 protocol compliance
- Stdio transport support
- Tool registration and listing
- Tool invocation
- Error handling
- Request/response formatting

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import pytest
import asyncio
import json
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from cortex.mcp.decorator import mcp_tool, get_registered_tools, clear_tools, get_tool
from cortex.mcp.server_sdk import CORTEXMCPServer, MCPRequest, MCPResponse


class TestMCPServerInitialization:
    """Test MCP server initialization."""
    
    def test_server_creation(self) -> None:
        """Test that server can be instantiated."""
        server = CORTEXMCPServer(
            server_name="test-cortex",
            server_version="1.0.0"
        )
        
        assert server.server_name == "test-cortex"
        assert server.server_version == "1.0.0"
        assert isinstance(server, CORTEXMCPServer)
    
    def test_server_default_params(self) -> None:
        """Test server creation with default parameters."""
        server = CORTEXMCPServer()
        
        assert server.server_name == "cortex-mcp"
        assert server.server_version == "1.0.0"


class TestToolRegistration:
    """Test tool registration and decorator."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_mcp_tool_decorator_basic(self) -> None:
        """Test basic @mcp_tool decorator."""
        @mcp_tool()
        def test_tool(param1: str) -> str:
            """Test tool description."""
            return f"Result: {param1}"
        
        tools = get_registered_tools()
        assert "test_tool" in tools
        assert tools["test_tool"].description == "Test tool description."
    
    def test_mcp_tool_decorator_custom_name(self) -> None:
        """Test @mcp_tool with custom name."""
        @mcp_tool(name="custom_name")
        def test_tool() -> None:
            """Test tool."""
            pass
        
        tools = get_registered_tools()
        assert "custom_name" in tools
        assert "test_tool" not in tools
    
    def test_mcp_tool_decorator_category(self) -> None:
        """Test @mcp_tool with category."""
        @mcp_tool(category="orchestrator")
        def test_tool() -> None:
            """Test tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["test_tool"].category == "orchestrator"
    
    def test_mcp_tool_decorator_version(self) -> None:
        """Test @mcp_tool with version."""
        @mcp_tool(version="2.0.0")
        def test_tool() -> None:
            """Test tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["test_tool"].version == "2.0.0"
    
    def test_tool_parameter_extraction_string(self) -> None:
        """Test parameter schema extraction for string type."""
        @mcp_tool()
        def test_tool(name: str, optional_param: str = "default") -> str:
            """Test tool with parameters."""
            return name
        
        tools = get_registered_tools()
        schema = tools["test_tool"].parameters
        
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert schema["properties"]["name"]["type"] == "string"
        assert "name" in schema["required"]
        assert "optional_param" not in schema["required"]
    
    def test_tool_parameter_extraction_int(self) -> None:
        """Test parameter schema extraction for int type."""
        @mcp_tool()
        def test_tool(count: int) -> int:
            """Test tool with int parameter."""
            return count
        
        tools = get_registered_tools()
        schema = tools["test_tool"].parameters
        
        assert schema["properties"]["count"]["type"] == "integer"
    
    def test_tool_parameter_extraction_float(self) -> None:
        """Test parameter schema extraction for float type."""
        @mcp_tool()
        def test_tool(value: float) -> float:
            """Test tool with float parameter."""
            return value
        
        tools = get_registered_tools()
        schema = tools["test_tool"].parameters
        
        assert schema["properties"]["value"]["type"] == "number"
    
    def test_tool_parameter_extraction_bool(self) -> None:
        """Test parameter schema extraction for bool type."""
        @mcp_tool()
        def test_tool(enabled: bool) -> bool:
            """Test tool with bool parameter."""
            return enabled
        
        tools = get_registered_tools()
        schema = tools["test_tool"].parameters
        
        assert schema["properties"]["enabled"]["type"] == "boolean"
    
    def test_tool_parameter_extraction_dict(self) -> None:
        """Test parameter schema extraction for dict type."""
        @mcp_tool()
        def test_tool(config: dict) -> str:
            """Test tool with dict parameter."""
            return str(config)
        
        tools = get_registered_tools()
        schema = tools["test_tool"].parameters
        
        assert schema["properties"]["config"]["type"] == "object"
    
    def test_tool_parameter_extraction_list(self) -> None:
        """Test parameter schema extraction for list type."""
        @mcp_tool()
        def test_tool(items: list) -> int:
            """Test tool with list parameter."""
            return len(items)
        
        tools = get_registered_tools()
        schema = tools["test_tool"].parameters
        
        assert schema["properties"]["items"]["type"] == "array"
    
    def test_get_tool(self) -> None:
        """Test getting a specific tool."""
        @mcp_tool()
        def test_tool() -> None:
            """Test tool."""
            pass
        
        tool = get_tool("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"
        assert tool.func == test_tool
    
    def test_get_tool_not_found(self) -> None:
        """Test getting a non-existent tool."""
        tool = get_tool("nonexistent")
        assert tool is None


class TestListToolsHandler:
    """Test list_tools handler."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    @pytest.mark.asyncio
    async def test_list_tools_empty(self) -> None:
        """Test listing tools when none are registered."""
        server = CORTEXMCPServer()
        response = await server.handle_tools_list()
        
        assert "tools" in response
        assert response["tools"] == []
    
    @pytest.mark.asyncio
    async def test_list_tools_with_registered_tools(self) -> None:
        """Test that registered tools are listed."""
        @mcp_tool(category="test")
        def tool1(param: str) -> str:
            """Tool 1 description."""
            return param
        
        @mcp_tool(category="test")
        def tool2(value: int) -> int:
            """Tool 2 description."""
            return value
        
        server = CORTEXMCPServer()
        response = await server.handle_tools_list()
        
        tools = response["tools"]
        assert len(tools) == 2
        
        tool_names = [t["name"] for t in tools]
        assert "tool1" in tool_names
        assert "tool2" in tool_names
    
    @pytest.mark.asyncio
    async def test_tool_schema_in_list(self) -> None:
        """Test that tool schemas are included in list."""
        @mcp_tool()
        def process(name: str, count: int) -> str:
            """Process items."""
            return f"{name}:{count}"
        
        server = CORTEXMCPServer()
        response = await server.handle_tools_list()
        
        tool = response["tools"][0]
        assert "name" in tool
        assert "description" in tool
        assert "inputSchema" in tool
        
        schema = tool["inputSchema"]
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "count" in schema["properties"]


class TestToolInvocation:
    """Test tool invocation functionality."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    @pytest.mark.asyncio
    async def test_handle_tools_call_success(self) -> None:
        """Test successful tool invocation."""
        @mcp_tool()
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        server = CORTEXMCPServer()
        response = await server.handle_tools_call({
            "name": "add",
            "arguments": {"a": 5, "b": 3}
        })
        
        assert "content" in response
        assert response["content"][0]["type"] == "text"
        assert response["content"][0]["text"] == "8"
    
    @pytest.mark.asyncio
    async def test_handle_tools_call_string_return(self) -> None:
        """Test tool invocation with string return."""
        @mcp_tool()
        def greet(name: str) -> str:
            """Greet a person."""
            return f"Hello, {name}!"
        
        server = CORTEXMCPServer()
        response = await server.handle_tools_call({
            "name": "greet",
            "arguments": {"name": "Alice"}
        })
        
        assert response["content"][0]["text"] == "Hello, Alice!"
    
    @pytest.mark.asyncio
    async def test_handle_tools_call_dict_return(self) -> None:
        """Test tool invocation returning a dictionary."""
        @mcp_tool()
        def create_result(status: str) -> Dict[str, Any]:
            """Create result dictionary."""
            return {"status": status, "code": 200}
        
        server = CORTEXMCPServer()
        response = await server.handle_tools_call({
            "name": "create_result",
            "arguments": {"status": "success"}
        })
        
        result_text = response["content"][0]["text"]
        result = json.loads(result_text)
        assert result["status"] == "success"
        assert result["code"] == 200
    
    @pytest.mark.asyncio
    async def test_handle_tools_call_invalid_tool(self) -> None:
        """Test tool invocation with invalid tool name."""
        server = CORTEXMCPServer()
        
        with pytest.raises(ValueError):
            await server.handle_tools_call({
                "name": "nonexistent_tool",
                "arguments": {}
            })
    
    @pytest.mark.asyncio
    async def test_handle_tools_call_missing_required_param(self) -> None:
        """Test tool invocation with missing required parameter."""
        @mcp_tool()
        def process(required_param: str) -> str:
            """Process something."""
            return required_param
        
        server = CORTEXMCPServer()
        
        with pytest.raises(ValueError):
            await server.handle_tools_call({
                "name": "process",
                "arguments": {}
            })
    
    def test_tool_function_preserved(self) -> None:
        """Test that @mcp_tool preserves original function."""
        @mcp_tool()
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        # Function should still be callable
        result = add(2, 3)
        assert result == 5


class TestErrorHandling:
    """Test error handling in MCP server."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_missing_required_parameter(self) -> None:
        """Test handling of missing required parameter."""
        @mcp_tool()
        def process(required_param: str) -> str:
            """Process something."""
            return required_param
        
        # This should work - calling with parameter
        result = process("value")
        assert result == "value"
        
        # Without parameter should raise TypeError
        with pytest.raises(TypeError):
            process()  # type: ignore
    
    def test_parameter_type_mismatch(self) -> None:
        """Test handling of parameter type mismatch."""
        @mcp_tool()
        def add_numbers(a: int, b: int) -> int:
            """Add two integers."""
            return a + b
        
        # Python won't enforce type hints at runtime, but we can test with wrong types
        result = add_numbers("5", "3")  # type: ignore
        # This will fail at runtime because of string concatenation
        assert result == "53"


class TestJSONRPC2Compliance:
    """Test JSON-RPC 2.0 compliance."""
    
    def test_mcp_request_to_dict(self) -> None:
        """Test MCPRequest conversion to dictionary."""
        request = MCPRequest(
            method="tools/list",
            params=None,
            id=1
        )
        
        d = request.to_dict()
        assert d["jsonrpc"] == "2.0"
        assert d["method"] == "tools/list"
        assert d["id"] == 1
        assert "params" not in d
    
    def test_mcp_request_to_json(self) -> None:
        """Test MCPRequest conversion to JSON."""
        request = MCPRequest(
            method="tools/call",
            params={"name": "test_tool"},
            id=2
        )
        
        json_str = request.to_json()
        data = json.loads(json_str)
        
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "tools/call"
        assert data["params"]["name"] == "test_tool"
        assert data["id"] == 2
    
    def test_mcp_request_from_json(self) -> None:
        """Test MCPRequest creation from JSON."""
        json_str = '{"jsonrpc": "2.0", "method": "initialize", "id": 1}'
        request = MCPRequest.from_json(json_str)
        
        assert request.jsonrpc == "2.0"
        assert request.method == "initialize"
        assert request.id == 1
    
    def test_mcp_response_to_dict(self) -> None:
        """Test MCPResponse conversion to dictionary."""
        response = MCPResponse(
            result={"tools": []},
            id=1
        )
        
        d = response.to_dict()
        assert d["jsonrpc"] == "2.0"
        assert d["result"]["tools"] == []
        assert d["id"] == 1
        assert "error" not in d
    
    def test_mcp_response_error_to_dict(self) -> None:
        """Test MCPResponse error conversion to dictionary."""
        response = MCPResponse(
            error={"code": -32601, "message": "Method not found"},
            id=1
        )
        
        d = response.to_dict()
        assert d["jsonrpc"] == "2.0"
        assert d["error"]["code"] == -32601
        assert "result" not in d
    
    def test_mcp_response_to_json(self) -> None:
        """Test MCPResponse conversion to JSON."""
        response = MCPResponse(
            result={"tools": []},
            id=1
        )
        
        json_str = response.to_json()
        data = json.loads(json_str)
        
        assert data["jsonrpc"] == "2.0"
        assert data["result"]["tools"] == []
    
    def test_tool_parameters_are_json_serializable(self) -> None:
        """Test that tool parameters can be JSON serialized."""
        @mcp_tool()
        def test_tool(
            name: str,
            count: int,
            enabled: bool,
            config: dict,
            items: list
        ) -> str:
            """Test tool with various parameters."""
            return str((name, count, enabled, config, items))
        
        tools = get_registered_tools()
        schema = tools["test_tool"].parameters
        
        # Should be JSON serializable
        json_str = json.dumps(schema)
        assert json_str is not None
        
        # Should deserialize back correctly
        deserialized = json.loads(json_str)
        assert deserialized["type"] == "object"
        assert "properties" in deserialized


class TestInitializeHandler:
    """Test initialize handler."""
    
    @pytest.mark.asyncio
    async def test_handle_initialize(self) -> None:
        """Test initialize request handling."""
        server = CORTEXMCPServer(
            server_name="test-cortex",
            server_version="2.0.0"
        )
        response = await server.handle_initialize()
        
        assert "protocolVersion" in response
        assert "capabilities" in response
        assert "serverInfo" in response
        
        server_info = response["serverInfo"]
        assert server_info["name"] == "test-cortex"
        assert server_info["version"] == "2.0.0"


class TestRequestHandling:
    """Test request handling."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    @pytest.mark.asyncio
    async def test_handle_initialize_request(self) -> None:
        """Test handling initialize request."""
        server = CORTEXMCPServer()
        request = MCPRequest(
            method="initialize",
            id=1
        )
        
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert response.id == 1
    
    @pytest.mark.asyncio
    async def test_handle_tools_list_request(self) -> None:
        """Test handling tools/list request."""
        @mcp_tool()
        def test_tool() -> str:
            """Test tool."""
            return "test"
        
        server = CORTEXMCPServer()
        request = MCPRequest(
            method="tools/list",
            id=2
        )
        
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert "tools" in response.result
    
    @pytest.mark.asyncio
    async def test_handle_tools_call_request(self) -> None:
        """Test handling tools/call request."""
        @mcp_tool()
        def multiply(x: int, y: int) -> int:
            """Multiply two numbers."""
            return x * y
        
        server = CORTEXMCPServer()
        request = MCPRequest(
            method="tools/call",
            params={"name": "multiply", "arguments": {"x": 3, "y": 4}},
            id=3
        )
        
        response = await server.handle_request(request)
        
        assert response.result is not None
        assert response.error is None
        assert "content" in response.result
    
    @pytest.mark.asyncio
    async def test_handle_unknown_method(self) -> None:
        """Test handling unknown method."""
        server = CORTEXMCPServer()
        request = MCPRequest(
            method="unknown/method",
            id=4
        )
        
        response = await server.handle_request(request)
        
        assert response.error is not None
        assert response.result is None
        assert response.error["code"] == -32603


class TestMCPServerConfiguration:
    """Test MCP server configuration."""
    
    def test_server_names_configurable(self) -> None:
        """Test that server name and version are configurable."""
        server1 = CORTEXMCPServer(
            server_name="cortex-v1",
            server_version="1.0.0"
        )
        server2 = CORTEXMCPServer(
            server_name="cortex-v2",
            server_version="2.0.0"
        )
        
        assert server1.server_name != server2.server_name
        assert server1.server_version != server2.server_version


class TestDecoratorDoesNotModifyFunction:
    """Test that @mcp_tool doesn't modify function behavior."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_decorated_function_same_as_original(self) -> None:
        """Test that decorated function behaves identically."""
        def original_add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        @mcp_tool()
        def decorated_add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b
        
        # Both should produce same result
        assert original_add(5, 3) == decorated_add(5, 3)
        assert original_add(10, -2) == decorated_add(10, -2)
    
    def test_decorated_function_with_side_effects(self) -> None:
        """Test that decorated function preserves side effects."""
        call_count = 0
        
        @mcp_tool()
        def increment() -> int:
            """Increment counter."""
            nonlocal call_count
            call_count += 1
            return call_count
        
        assert increment() == 1
        assert increment() == 2
        assert increment() == 3


class TestToolDiscovery:
    """Test tool discovery and iteration."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_get_registered_tools_returns_copy(self) -> None:
        """Test that get_registered_tools returns a copy."""
        @mcp_tool()
        def tool1() -> None:
            """Tool 1."""
            pass
        
        tools1 = get_registered_tools()
        tools2 = get_registered_tools()
        
        # Should be equal but not same object
        assert tools1 == tools2
        assert tools1 is not tools2
    
    def test_multiple_tools_registered(self) -> None:
        """Test registering multiple tools."""
        @mcp_tool(category="orchestrator")
        def orchestrator_tool() -> str:
            """Orchestrator tool."""
            return "orchestrator"
        
        @mcp_tool(category="validator")
        def validator_tool() -> str:
            """Validator tool."""
            return "validator"
        
        @mcp_tool(category="analyzer")
        def analyzer_tool() -> str:
            """Analyzer tool."""
            return "analyzer"
        
        tools = get_registered_tools()
        assert len(tools) == 3
        assert tools["orchestrator_tool"].category == "orchestrator"
        assert tools["validator_tool"].category == "validator"
        assert tools["analyzer_tool"].category == "analyzer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
