"""
Tests for MCP Tool Registry Singleton - Production implementation.

Tests the actual production implementation of ToolRegistry with:
- Singleton pattern for get_mcp_tool_registry()
- Tool registration and retrieval
- Category-based organization
- Integration with MCP server

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Phase: MCP Server Fix (Holistic)
"""

import pytest
from typing import Dict, Any


def test_get_mcp_tool_registry_returns_singleton() -> None:
    """Verify get_mcp_tool_registry() returns the same instance."""
    from cortex.mcp.tool_registry import get_mcp_tool_registry
    
    registry1 = get_mcp_tool_registry()
    registry2 = get_mcp_tool_registry()
    
    assert registry1 is registry2, "Should return same instance (singleton)"


def test_tool_registry_basic_operations() -> None:
    """Verify ToolRegistry supports register, get, and list operations."""
    from cortex.mcp.tool_registry import get_mcp_tool_registry, ToolMetadata, ToolCategory
    
    registry = get_mcp_tool_registry()
    
    # Register a test tool
    metadata = ToolMetadata(
        id="test_tool_001",
        name="Test Tool",
        category=ToolCategory.UTILITY,
        description="A test tool",
        parameters={"param1": {"type": "string", "required": True}},
        auth_required=False,
        version="1.0.0"
    )
    
    registry.register(metadata)
    
    # Retrieve it
    retrieved = registry.get("test_tool_001")
    assert retrieved is not None
    assert retrieved.id == "test_tool_001"
    assert retrieved.name == "Test Tool"
    
    # List all tools
    all_tools = registry.list_all()
    assert len(all_tools) >= 1
    assert any(t.id == "test_tool_001" for t in all_tools)


def test_tool_registry_list_by_category() -> None:
    """Verify ToolRegistry can filter tools by category."""
    from cortex.mcp.tool_registry import get_mcp_tool_registry, ToolMetadata, ToolCategory
    
    registry = get_mcp_tool_registry()
    
    # Register tools in different categories
    gov_tool = ToolMetadata(
        id="gov_tool_001",
        name="Governance Tool",
        category=ToolCategory.GOVERNANCE,
        description="A governance tool",
        parameters={},
    )
    
    util_tool = ToolMetadata(
        id="util_tool_001",
        name="Utility Tool",
        category=ToolCategory.UTILITY,
        description="A utility tool",
        parameters={},
    )
    
    registry.register(gov_tool)
    registry.register(util_tool)
    
    # List by category
    gov_tools = registry.list_by_category(ToolCategory.GOVERNANCE)
    util_tools = registry.list_by_category(ToolCategory.UTILITY)
    
    assert any(t.id == "gov_tool_001" for t in gov_tools)
    assert any(t.id == "util_tool_001" for t in util_tools)
    assert not any(t.id == "util_tool_001" for t in gov_tools)


def test_tool_registry_count_by_category() -> None:
    """Verify ToolRegistry can count tools per category."""
    from cortex.mcp.tool_registry import get_mcp_tool_registry, ToolCategory
    
    registry = get_mcp_tool_registry()
    
    # Count should be non-negative
    count = registry.count_by_category(ToolCategory.UTILITY)
    assert count >= 0
    assert isinstance(count, int)


def test_tool_category_enum_values() -> None:
    """Verify ToolCategory has expected values."""
    from cortex.mcp.tool_registry import ToolCategory
    
    expected_categories = ["GOVERNANCE", "ORCHESTRATION", "KNOWLEDGE", "UTILITY"]
    
    for cat_name in expected_categories:
        assert hasattr(ToolCategory, cat_name), f"ToolCategory missing {cat_name}"
        
    # Check enum values
    assert ToolCategory.GOVERNANCE.value == "governance"
    assert ToolCategory.ORCHESTRATION.value == "orchestration"
    assert ToolCategory.KNOWLEDGE.value == "knowledge"
    assert ToolCategory.UTILITY.value == "utility"


def test_tool_metadata_structure() -> None:
    """Verify ToolMetadata has required fields."""
    from cortex.mcp.tool_registry import ToolMetadata, ToolCategory
    
    metadata = ToolMetadata(
        id="test",
        name="Test",
        category=ToolCategory.UTILITY,
        description="Test description",
        parameters={"param1": {"type": "string"}},
    )
    
    # Required fields
    assert metadata.id == "test"
    assert metadata.name == "Test"
    assert metadata.category == ToolCategory.UTILITY
    assert metadata.description == "Test description"
    assert metadata.parameters == {"param1": {"type": "string"}}
    
    # Optional fields with defaults
    assert metadata.auth_required == False
    assert metadata.version == "1.0.0"


def test_tool_registry_duplicate_registration_fails() -> None:
    """Verify ToolRegistry prevents duplicate tool IDs."""
    from cortex.mcp.tool_registry import get_mcp_tool_registry, ToolMetadata, ToolCategory
    
    registry = get_mcp_tool_registry()
    
    metadata1 = ToolMetadata(
        id="duplicate_test",
        name="First",
        category=ToolCategory.UTILITY,
        description="First",
        parameters={},
    )
    
    metadata2 = ToolMetadata(
        id="duplicate_test",  # Same ID
        name="Second",
        category=ToolCategory.UTILITY,
        description="Second",
        parameters={},
    )
    
    registry.register(metadata1)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register(metadata2)
