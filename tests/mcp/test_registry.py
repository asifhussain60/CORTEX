"""Tests for MCP Tool Registry - PHASE-DEPLOYMENT-003-mcp-expansion.

AC-DEP-003-01: Registry expansion with complete metadata.
Tests registry has 30+ tools, metadata completeness, category organization.
"""

import pytest
from pathlib import Path


class TestRegistryHas30PlusTools:
    """Test registry contains 30+ tool definitions."""

    def test_registry_has_30plus_tools(self):
        """Registry should contain 30+ tool definitions."""
        from cortex.mcp.registry import ToolRegistry, get_all_tools
        
        registry = ToolRegistry()
        tools = get_all_tools()
        
        assert len(tools) >= 30, f"Expected 30+ tools, got {len(tools)}"

    def test_registry_tools_unique_ids(self):
        """All tools should have unique IDs."""
        from cortex.mcp.registry import get_all_tools
        
        tools = get_all_tools()
        tool_ids = [t.tool_id for t in tools]
        
        assert len(tool_ids) == len(set(tool_ids)), "Duplicate tool IDs found"


class TestToolMetadataComplete:
    """Test tool metadata completeness."""

    def test_tool_has_name(self):
        """Each tool must have a name."""
        from cortex.mcp.registry import get_all_tools
        
        tools = get_all_tools()
        for tool in tools:
            assert tool.name, f"Tool {tool.tool_id} missing name"

    def test_tool_has_category(self):
        """Each tool must have a category."""
        from cortex.mcp.registry import get_all_tools
        
        tools = get_all_tools()
        for tool in tools:
            assert tool.category, f"Tool {tool.tool_id} missing category"

    def test_tool_has_version(self):
        """Each tool must have a version."""
        from cortex.mcp.registry import get_all_tools
        
        tools = get_all_tools()
        for tool in tools:
            assert tool.version, f"Tool {tool.tool_id} missing version"

    def test_tool_has_description(self):
        """Each tool must have a description."""
        from cortex.mcp.registry import get_all_tools
        
        tools = get_all_tools()
        for tool in tools:
            assert tool.description, f"Tool {tool.tool_id} missing description"

    def test_tool_has_governance_rule(self):
        """Each tool should reference governance rule if applicable."""
        from cortex.mcp.registry import get_all_tools
        
        tools = get_all_tools()
        # governance_rule can be None for utility tools
        for tool in tools:
            if tool.category in ["governance", "deployment", "multi_repo"]:
                assert tool.governance_rule or tool.governance_rule == "", \
                    f"Tool {tool.tool_id} missing governance_rule"


class TestCategorySubdirsOrganized:
    """Test tools organized by category subdirectories."""

    def test_governance_category_exists(self):
        """Governance tools category should exist."""
        from cortex.mcp.registry import get_tools_by_category
        
        tools = get_tools_by_category("governance")
        assert len(tools) >= 5, f"Expected 5+ governance tools, got {len(tools)}"

    def test_deployment_category_exists(self):
        """Deployment tools category should exist."""
        from cortex.mcp.registry import get_tools_by_category
        
        tools = get_tools_by_category("deployment")
        assert len(tools) >= 5, f"Expected 5+ deployment tools, got {len(tools)}"

    def test_multi_repo_category_exists(self):
        """Multi-repo tools category should exist."""
        from cortex.mcp.registry import get_tools_by_category
        
        tools = get_tools_by_category("multi_repo")
        assert len(tools) >= 6, f"Expected 6+ multi_repo tools, got {len(tools)}"

    def test_orchestration_category_exists(self):
        """Orchestration tools category should exist."""
        from cortex.mcp.registry import get_tools_by_category
        
        tools = get_tools_by_category("orchestration")
        assert len(tools) >= 4, f"Expected 4+ orchestration tools, got {len(tools)}"

    def test_knowledge_category_exists(self):
        """Knowledge tools category should exist."""
        from cortex.mcp.registry import get_tools_by_category
        
        tools = get_tools_by_category("knowledge")
        assert len(tools) >= 3, f"Expected 3+ knowledge tools, got {len(tools)}"

    def test_utility_category_exists(self):
        """Utility tools category should exist."""
        from cortex.mcp.registry import get_tools_by_category
        
        tools = get_tools_by_category("utility")
        assert len(tools) >= 2, f"Expected 2+ utility tools, got {len(tools)}"


class TestServerAutoDiscoversTools:
    """Test server auto-discovers tools from registry."""

    def test_server_discovers_from_registry(self):
        """Server should auto-discover tools from registry."""
        from cortex.mcp.registry import get_all_tools, ToolRegistry
        
        registry = ToolRegistry()
        registry.auto_discover()
        
        tools = get_all_tools()
        assert len(tools) >= 30, "Server did not auto-discover 30+ tools"

    def test_discovered_tools_callable(self):
        """Discovered tools should be callable."""
        from cortex.mcp.registry import get_all_tools
        
        tools = get_all_tools()
        for tool in tools:
            assert callable(tool.handler), f"Tool {tool.tool_id} handler not callable"
