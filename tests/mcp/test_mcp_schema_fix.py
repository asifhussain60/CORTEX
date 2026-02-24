"""
Tests for MCP schema generation fix.

Verifies that tool schemas include all required metadata including category.

Tool count updated: Phase 65 added CortexIntelligenceMatrix (intelligence).
Toolkit Phase 63 added cortex_scan, cortex_batch_transform, cortex_enrich,
cortex_workflow, cortex_scaffold_files (operations).
Current live count: 28 registered tools (class-based + function wrappers may vary).
"""

import pytest
from cortex.mcp.mcp_registry import get_registry, ToolRegistry
from cortex.mcp.mcp_tool_base import ToolCategory


# Live tool count — updated each time tools are added.
# Run: python3 -c "from cortex.mcp.mcp_registry import get_registry; print(len(get_registry().to_mcp_schema()))"
_EXPECTED_TOOL_COUNT = 28

# Expected category distribution (Phase 65 actuals)
_EXPECTED_DISTRIBUTION = {
    "core": 3,
    "intelligence": 3,   # cortex_generate_tests, cortex_git, cortex_knowledge
    "governance": 4,
    "operations": 9,
    "utilities": 9,
}


class TestMCPSchemaGeneration:
    """Test MCP schema generation with category metadata."""

    def test_schema_includes_category(self):
        """Verify each tool schema includes category field."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()

        assert len(schemas) == _EXPECTED_TOOL_COUNT, (
            f"Expected {_EXPECTED_TOOL_COUNT} tool schemas, got {len(schemas)}. "
            "Update _EXPECTED_TOOL_COUNT when adding/removing tools."
        )

        for schema in schemas:
            assert "name" in schema, f"Schema missing 'name': {schema}"
            assert "description" in schema, f"Schema missing 'description': {schema}"
            assert "category" in schema, f"Schema missing 'category': {schema['name']}"
            assert "inputSchema" in schema, f"Schema missing 'inputSchema': {schema}"

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

        category_counts = {}
        for schema in schemas:
            cat = schema["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for cat, expected in _EXPECTED_DISTRIBUTION.items():
            assert category_counts.get(cat) == expected, (
                f"Category '{cat}': expected {expected}, got {category_counts.get(cat)}. "
                f"Full distribution: {category_counts}"
            )

    def test_schema_operations_included(self):
        """Verify consolidated tools include operations list."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()

        consolidated_tools = [s for s in schemas if "operations" in s and s["operations"]]

        assert len(consolidated_tools) > 0, "Should have consolidated tools with operations"

        git_schema = next((s for s in schemas if s["name"] == "cortex_git"), None)
        assert git_schema is not None, "cortex_git should exist"
        assert "operations" in git_schema, "cortex_git should have operations field"

    def test_schema_json_serializable(self):
        """Verify schemas can be serialized to JSON."""
        import json

        registry = get_registry()
        schemas = registry.to_mcp_schema()

        json_output = json.dumps(schemas, default=str)
        assert len(json_output) > 0

        parsed = json.loads(json_output)
        assert len(parsed) == _EXPECTED_TOOL_COUNT, (
            f"Expected {_EXPECTED_TOOL_COUNT} tools in JSON, got {len(parsed)}."
        )

    def test_core_tools_have_correct_category(self):
        """Verify core tools are marked as core category."""
        registry = get_registry()
        schemas = registry.to_mcp_schema()

        core_tool_names = [
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
        
        # cortex_lens removed — deleted per architect spec; remaining intelligence tools:
        intelligence_tool_names = ["cortex_knowledge", "cortex_git", "cortex_generate_tests"]
        
        for tool_name in intelligence_tool_names:
            schema = next((s for s in schemas if s["name"] == tool_name), None)
            assert schema is not None, f"Intelligence tool {tool_name} not found"
            assert schema["category"] == "intelligence", (
                f"Tool {tool_name} should have category 'intelligence', "
                f"got '{schema.get('category')}'"
            )
