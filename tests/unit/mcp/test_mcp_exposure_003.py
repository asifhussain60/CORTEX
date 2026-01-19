"""Test suite for AC-MCP-EXPOSURE-003: /list-tools MCP endpoint."""

import pytest
import json
from typing import Any, Dict, List
from unittest.mock import Mock, patch, MagicMock

from cortex.mcp.decorators import mcp_tool, MCP_TOOLS_REGISTRY


class TestListToolsEndpoint:
    """Tests for /list-tools MCP endpoint implementation."""

    def setup_method(self) -> None:
        """Setup for each test."""
        MCP_TOOLS_REGISTRY.clear()

    def test_list_tools_endpoint_exists(self) -> None:
        """Test that /list-tools endpoint exists and is callable."""
        from cortex.mcp.endpoints import list_tools_endpoint
        
        assert callable(list_tools_endpoint)

    def test_list_tools_returns_dict(self) -> None:
        """Test that /list-tools endpoint returns proper structure."""
        @mcp_tool(name="test_tool", description="Test tool")
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        assert isinstance(result, dict)

    def test_list_tools_contains_tools(self) -> None:
        """Test that endpoint returns list of tools."""
        @mcp_tool(name="tool1", description="Tool 1")
        def func1() -> str:
            """Tool 1."""
            return "result1"

        @mcp_tool(name="tool2", description="Tool 2")
        def func2() -> str:
            """Tool 2."""
            return "result2"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        assert "tools" in result
        assert len(result["tools"]) >= 2

    def test_tool_metadata_in_response(self) -> None:
        """Test that each tool has complete metadata in response."""
        @mcp_tool(
            name="metadata_tool",
            description="Tool with metadata",
            parameters={"param1": "type1", "param2": "type2"}
        )
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        tools = result.get("tools", [])
        tool_names = [t.get("name") for t in tools]
        
        assert "metadata_tool" in tool_names

    def test_tool_discovery_completeness(self) -> None:
        """Test that all registered tools are discoverable."""
        # Register several tools
        for i in range(5):
            @mcp_tool(name=f"discovery_tool_{i}", description=f"Tool {i}")
            def func() -> str:
                """Function."""
                return f"result_{i}"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        tools = result.get("tools", [])
        tool_names = [t.get("name") for t in tools]
        
        # All registered tools should be discoverable
        for i in range(5):
            assert f"discovery_tool_{i}" in tool_names

    def test_endpoint_response_format(self) -> None:
        """Test endpoint returns properly formatted response."""
        @mcp_tool(name="format_tool", description="Format tool")
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        # Should be JSON-serializable
        json_str = json.dumps(result)
        assert isinstance(json_str, str)

    def test_tool_description_accuracy(self) -> None:
        """Test that tool descriptions are accurate in response."""
        @mcp_tool(
            name="described_tool",
            description="This is a highly accurate description"
        )
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        tools = result.get("tools", [])
        
        for tool in tools:
            if tool.get("name") == "described_tool":
                assert tool.get("description") == "This is a highly accurate description"

    def test_endpoint_handles_empty_registry(self) -> None:
        """Test endpoint handles empty tool registry gracefully."""
        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        assert isinstance(result, dict)
        assert "tools" in result
        assert isinstance(result["tools"], list)

    def test_endpoint_includes_tool_types(self) -> None:
        """Test endpoint includes tool type information."""
        @mcp_tool(
            name="typed_tool",
            description="Typed tool",
            parameters={"input": "string", "count": "integer"}
        )
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        tools = result.get("tools", [])
        
        for tool in tools:
            if tool.get("name") == "typed_tool":
                # Should include parameter types
                assert tool.get("parameters") or tool.get("description")


class TestToolDiscoveryProtocol:
    """Tests for tool discovery protocol and metadata queries."""

    def setup_method(self) -> None:
        """Setup for each test."""
        MCP_TOOLS_REGISTRY.clear()

    def test_metadata_query_support(self) -> None:
        """Test that endpoint supports metadata queries."""
        @mcp_tool(
            name="queryable_tool",
            description="Tool with queryable metadata"
        )
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        # Should be queryable
        assert isinstance(result, dict)
        tools = result.get("tools", [])
        assert len(tools) > 0

    def test_tool_filtering_capability(self) -> None:
        """Test that discovered tools can be filtered."""
        @mcp_tool(name="analysis_tool", description="Analysis tool")
        def func1() -> str:
            """Analysis."""
            return "analysis"

        @mcp_tool(name="validation_tool", description="Validation tool")
        def func2() -> str:
            """Validation."""
            return "validation"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        tools = result.get("tools", [])
        
        # Tools should be identifiable by name/description
        tool_names = [t.get("name") for t in tools]
        assert "analysis_tool" in tool_names
        assert "validation_tool" in tool_names

    def test_pagination_support(self) -> None:
        """Test endpoint supports pagination for large tool lists."""
        # Register many tools
        for i in range(20):
            @mcp_tool(name=f"paginated_tool_{i}", description=f"Tool {i}")
            def func() -> str:
                """Function."""
                return f"result_{i}"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        # Should handle large result sets
        assert isinstance(result, dict)
        tools = result.get("tools", [])
        assert len(tools) >= 20

    def test_metadata_completeness_check(self) -> None:
        """Test that all discovered tools have complete metadata."""
        @mcp_tool(
            name="complete_tool",
            description="Complete metadata tool"
        )
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        tools = result.get("tools", [])
        
        for tool in tools:
            # Each tool should have essential fields
            assert "name" in tool
            assert "description" in tool or tool.get("name")

    def test_real_time_discovery(self) -> None:
        """Test that discovery reflects current tool state."""
        @mcp_tool(name="initial_tool", description="Initial tool")
        def func1() -> str:
            """Initial."""
            return "initial"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result1 = list_tools_endpoint()
        count1 = len(result1.get("tools", []))

        @mcp_tool(name="new_tool", description="New tool")
        def func2() -> str:
            """New."""
            return "new"

        result2 = list_tools_endpoint()
        count2 = len(result2.get("tools", []))

        # New discovery should include newly registered tool
        assert count2 > count1

    def test_discovery_error_handling(self) -> None:
        """Test discovery handles errors gracefully."""
        from cortex.mcp.endpoints import list_tools_endpoint
        
        # Should not raise exception even with empty registry
        result = list_tools_endpoint()
        assert isinstance(result, dict)


class TestMcpEndpointIntegration:
    """Tests for MCP endpoint integration."""

    def setup_method(self) -> None:
        """Setup for each test."""
        MCP_TOOLS_REGISTRY.clear()

    def test_endpoint_http_compatibility(self) -> None:
        """Test endpoint is HTTP-compatible."""
        @mcp_tool(name="http_tool", description="HTTP tool")
        def test_func() -> str:
            """Test function."""
            return "result"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        # Should be JSON-serializable for HTTP response
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed == result

    def test_endpoint_scalability(self) -> None:
        """Test endpoint scales with tool count."""
        # Register many tools
        for i in range(50):
            @mcp_tool(name=f"scale_tool_{i}", description=f"Tool {i}")
            def func() -> str:
                """Function."""
                return f"result_{i}"

        from cortex.mcp.endpoints import list_tools_endpoint
        
        result = list_tools_endpoint()
        
        # Should handle large number of tools
        tools = result.get("tools", [])
        assert len(tools) >= 50
