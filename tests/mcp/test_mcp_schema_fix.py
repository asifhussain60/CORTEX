"""
Tests for MCP schema generation fix.

Verifies that tool schemas include all required metadata including category.
"""

import pytest
from cortex.mcp.mcp_registry import get_registry, ToolRegistry
from cortex.mcp.mcp_tool_base import ToolCategory


class TestMCPSchemaGeneration:
    """Test MCP schema generation with category metadata."""
    
    def test_schema_includes_category(self):
        """Verify each tool schema includes category field."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()
        
        assert len(schemas) == 26, "Should have 26 tool schemas"
        
        for schema in schemas:
            assert "name" in schema, f"Schema missing 'name': {schema}"
            assert "description" in schema, f"Schema missing 'description': {schema}"
            assert "category" in schema, f"Schema missing 'category': {schema['name']}"
            assert "inputSchema" in schema, f"Schema missing 'inputSchema': {schema}"
            
            # Verify category is a valid enum value
            category = schema["category"]
            valid_categories = [c.value for c in ToolCategory]
            assert category in valid_categories, (
                f"Tool {schema['name']} has invalid category: {category}. "
                f"Valid: {valid_categories}"
            )
    
    def test_schema_categories_distribution(self):
        """Verify tools are properly distributed across categories."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()
        
        # Count tools per category
        category_counts = {}
        for schema in schemas:
            category = schema["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Expected distribution (based on PRODUCTION_TOOLS)
        assert category_counts.get("core") == 4, "Should have 4 core tools"
        assert category_counts.get("intelligence") == 4, "Should have 4 intelligence tools"
        assert category_counts.get("governance") == 4, "Should have 4 governance tools"
        assert category_counts.get("operations") == 5, "Should have 5 operations tools"
        assert category_counts.get("utilities") == 9, "Should have 9 utilities tools"
    
    def test_schema_operations_included(self):
        """Verify consolidated tools include operations list."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()
        
        # Find consolidated tools (those with operations)
        consolidated_tools = [s for s in schemas if "operations" in s and s["operations"]]
        
        assert len(consolidated_tools) > 0, "Should have consolidated tools with operations"
        
        # Verify cortex.lens has operations
        lens_schema = next((s for s in schemas if s["name"] == "cortex.lens"), None)
        assert lens_schema is not None, "cortex.lens should exist"
        assert "operations" in lens_schema, "cortex.lens should have operations field"
        assert len(lens_schema["operations"]) == 5, "cortex.lens should have 5 operations"
    
    def test_schema_json_serializable(self):
        """Verify schemas can be serialized to JSON."""
        import json
        
        registry = get_registry()
        schemas = registry.to_mcp_schema()
        
        # Should not raise exception
        json_output = json.dumps(schemas, default=str)
        assert len(json_output) > 0
        
        # Should be able to parse back
        parsed = json.loads(json_output)
        assert len(parsed) == 26
    
    def test_core_tools_have_correct_category(self):
        """Verify core tools are marked as core category."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()
        
        core_tool_names = [
            "cortex_process_request",
            "cortex_challenge",
            "cortex_classify",
            "cortex_request_lifecycle"
        ]
        
        for tool_name in core_tool_names:
            schema = next((s for s in schemas if s["name"] == tool_name), None)
            assert schema is not None, f"Core tool {tool_name} not found"
            assert schema["category"] == "core", (
                f"Tool {tool_name} should have category 'core', got '{schema.get('category')}'"
            )
    
    def test_intelligence_tools_have_correct_category(self):
        """Verify intelligence tools are marked as intelligence category."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()
        
        intelligence_tool_names = ["cortex.lens", "cortex_knowledge", "cortex_git"]
        
        for tool_name in intelligence_tool_names:
            schema = next((s for s in schemas if s["name"] == tool_name), None)
            assert schema is not None, f"Intelligence tool {tool_name} not found"
            assert schema["category"] == "intelligence", (
                f"Tool {tool_name} should have category 'intelligence', "
                f"got '{schema.get('category')}'"
            )
