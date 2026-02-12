"""
Comprehensive MCP integration tests.

Tests the entire MCP stack end-to-end.
"""

import pytest
import json
from cortex.mcp.server import MCPServer
from cortex.mcp.registry import get_registry
from cortex.mcp.base import ToolCategory


class TestMCPIntegration:
    """End-to-end MCP integration tests."""
    
    def test_server_initialization(self):
        """Test MCP server initializes correctly."""
        server = MCPServer()
        
        assert server is not None
        assert server.registry is not None
        assert server.registry.tool_count == 24
    
    def test_tools_list_complete(self):
        """Test tools/list returns all 24 tools with metadata."""
        server = MCPServer()
        tools = server.list_tools()
        
        assert len(tools) == 24
        
        # Verify each tool has required fields
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "category" in tool
            assert "inputSchema" in tool
            assert tool["name"].startswith("cortex_")
    
    def test_tools_by_category(self):
        """Test category filtering works."""
        server = MCPServer()
        
        # Test each category
        core_tools = server.list_tools_by_category("core")
        assert len(core_tools) == 4
        
        intelligence_tools = server.list_tools_by_category("intelligence")
        assert len(intelligence_tools) == 3
        
        governance_tools = server.list_tools_by_category("governance")
        assert len(governance_tools) == 3
        
        operations_tools = server.list_tools_by_category("operations")
        assert len(operations_tools) == 5
        
        utilities_tools = server.list_tools_by_category("utilities")
        assert len(utilities_tools) == 9
    
    def test_tool_execution_verify_environment(self):
        """Test executing cortex_verify tool."""
        server = MCPServer()
        result = server.call_tool("cortex_verify", operation="environment")
        
        assert result is not None
        assert result.success is True
        assert result.data is not None
    
    def test_tool_execution_invalid_tool(self):
        """Test error handling for unknown tool."""
        server = MCPServer()
        result = server.call_tool("cortex_nonexistent")
        
        assert result is not None
        assert result.success is False
        assert result.error is not None
        assert "Unknown tool" in result.error
        assert "available_tools" in result.metadata
    
    def test_tool_execution_missing_params(self):
        """Test parameter validation."""
        server = MCPServer()
        # cortex_lens requires 'operation' and 'target'
        result = server.call_tool("cortex_lens")
        
        assert result is not None
        assert result.success is False
        assert result.error is not None
        assert "Missing required parameter" in result.error
    
    def test_registry_metadata_consistency(self):
        """Test registry metadata matches implementation."""
        registry = get_registry()
        
        # Check all metadata has matching implementation
        for tool_id in registry._tools.keys():
            metadata = registry.get_metadata(tool_id)
            assert metadata is not None
            assert metadata.id == tool_id
            assert isinstance(metadata.category, ToolCategory)
    
    def test_schema_json_output(self):
        """Test schema can be serialized for MCP protocol."""
        server = MCPServer()
        tools = server.list_tools()
        
        # Should serialize without errors
        json_output = json.dumps(tools, default=str)
        assert len(json_output) > 0
        
        # Should parse back
        parsed = json.loads(json_output)
        assert len(parsed) == 24
        
        # Verify structure
        for tool in parsed:
            assert isinstance(tool["name"], str)
            assert isinstance(tool["description"], str)
            assert isinstance(tool["category"], str)
            assert isinstance(tool["inputSchema"], dict)
    
    def test_consolidated_tools_have_operations(self):
        """Test consolidated tools expose operations."""
        server = MCPServer()
        tools = server.list_tools()
        
        # Find cortex_lens (consolidated tool)
        lens = next((t for t in tools if t["name"] == "cortex_lens"), None)
        assert lens is not None
        assert "operations" in lens
        assert len(lens["operations"]) == 5
        assert "analyze" in lens["operations"]
        assert "deep_analyze" in lens["operations"]
        
        # Find cortex_debug (consolidated tool)
        debug = next((t for t in tools if t["name"] == "cortex_debug"), None)
        assert debug is not None
        assert "operations" in debug
        assert len(debug["operations"]) == 7
    
    def test_all_core_tools_present(self):
        """Verify all 4 core tools are registered."""
        server = MCPServer()
        tools = server.list_tools()
        tool_names = [t["name"] for t in tools]
        
        core_tools = [
            "cortex_process_request",
            "cortex_challenge",
            "cortex_classify",
            "cortex_request_lifecycle"
        ]
        
        for tool_name in core_tools:
            assert tool_name in tool_names, f"Missing core tool: {tool_name}"
    
    def test_category_distribution_matches_design(self):
        """Verify tool distribution matches architectural design."""
        server = MCPServer()
        tools = server.list_tools()
        
        # Count by category
        by_category = {}
        for tool in tools:
            cat = tool["category"]
            by_category[cat] = by_category.get(cat, 0) + 1
        
        # Expected: 4 core, 3 intelligence, 3 governance, 5 operations, 9 utilities
        assert by_category["core"] == 4
        assert by_category["intelligence"] == 3
        assert by_category["governance"] == 3
        assert by_category["operations"] == 5
        assert by_category["utilities"] == 9
        
        # Total should be 24
        assert sum(by_category.values()) == 24
