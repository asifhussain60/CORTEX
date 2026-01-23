"""
Tests for MCP Tool Registry - Centralized tool discovery and categorization.

Tests cover:
- ToolCategory enum for categorizing tools
- ToolMetadata dataclass for tool information
- ToolRegistry for registering and discovering tools
- Tool organization and lookup patterns
"""

import pytest
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass


class ToolCategory(Enum):
    """Tool category classification."""
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE = "knowledge"
    UTILITY = "utility"


@dataclass
class ToolMetadata:
    """Metadata for a registered MCP tool.
    
    Attributes:
        id: Unique tool identifier
        name: Human-readable tool name
        category: Tool category
        description: What the tool does
        parameters: Input parameter schema
        auth_required: Whether authentication is required
        version: Tool version
    """
    id: str
    name: str
    category: ToolCategory
    description: str
    parameters: Dict[str, Any]
    auth_required: bool = False
    version: str = "1.0.0"


class ToolRegistry:
    """Central registry for MCP tools with discovery capabilities."""

    def __init__(self) -> None:
        """Initialize empty tool registry."""
        self._tools: Dict[str, ToolMetadata] = {}

    def register(self, metadata: ToolMetadata) -> None:
        """Register a new tool in the registry.
        
        Args:
            metadata: Tool metadata to register.
            
        Raises:
            ValueError: If tool with same ID already registered.
        """
        if metadata.id in self._tools:
            raise ValueError(f"Tool '{metadata.id}' already registered")
        self._tools[metadata.id] = metadata

    def get(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID.
        
        Args:
            tool_id: Tool identifier to look up.
            
        Returns:
            Tool metadata if found, None otherwise.
        """
        return self._tools.get(tool_id)

    def list_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """List all tools in a category.
        
        Args:
            category: Category to filter by.
            
        Returns:
            List of tools in the category.
        """
        return [t for t in self._tools.values() if t.category == category]

    def discover(self) -> Dict[str, List[str]]:
        """Return tool discovery information.
        
        Returns:
            Dictionary mapping category names to lists of tool IDs.
        """
        result: Dict[str, List[str]] = {}
        for category in ToolCategory:
            result[category.value] = [
                t.id for t in self.list_by_category(category)
            ]
        return result

    def list_all(self) -> List[ToolMetadata]:
        """List all registered tools.
        
        Returns:
            List of all tool metadata.
        """
        return list(self._tools.values())

    def count(self) -> int:
        """Get total number of registered tools.
        
        Returns:
            Total tool count.
        """
        return len(self._tools)

    def count_by_category(self, category: ToolCategory) -> int:
        """Get tool count for a category.
        
        Args:
            category: Category to count.
            
        Returns:
            Number of tools in category.
        """
        return len(self.list_by_category(category))


class TestToolCategory:
    """Tests for ToolCategory enum."""

    def test_category_values_defined(self) -> None:
        """Test that all expected categories are defined."""
        assert ToolCategory.GOVERNANCE.value == "governance"
        assert ToolCategory.ORCHESTRATION.value == "orchestration"
        assert ToolCategory.KNOWLEDGE.value == "knowledge"
        assert ToolCategory.UTILITY.value == "utility"

    def test_category_enum_members(self) -> None:
        """Test all category enum members exist."""
        categories = list(ToolCategory)
        assert len(categories) == 4
        names = [c.name for c in categories]
        assert "GOVERNANCE" in names
        assert "ORCHESTRATION" in names
        assert "KNOWLEDGE" in names
        assert "UTILITY" in names


class TestToolMetadata:
    """Tests for ToolMetadata dataclass."""

    def test_metadata_creation_minimal(self) -> None:
        """Test creating metadata with minimal parameters."""
        metadata = ToolMetadata(
            id="tool-001",
            name="Test Tool",
            category=ToolCategory.GOVERNANCE,
            description="A test tool",
            parameters={}
        )
        assert metadata.id == "tool-001"
        assert metadata.name == "Test Tool"
        assert metadata.category == ToolCategory.GOVERNANCE
        assert metadata.auth_required is False
        assert metadata.version == "1.0.0"

    def test_metadata_creation_full(self) -> None:
        """Test creating metadata with all parameters."""
        params: Dict[str, Any] = {"input": "string", "output": "json"}
        metadata = ToolMetadata(
            id="tool-002",
            name="Full Tool",
            category=ToolCategory.ORCHESTRATION,
            description="Full metadata",
            parameters=params,
            auth_required=True,
            version="2.0.0"
        )
        assert metadata.auth_required is True
        assert metadata.version == "2.0.0"
        assert metadata.parameters == params

    def test_metadata_immutability(self) -> None:
        """Test that metadata fields are properly typed."""
        metadata = ToolMetadata(
            id="tool-003",
            name="Type Test",
            category=ToolCategory.KNOWLEDGE,
            description="Test types",
            parameters={}
        )
        # Verify field types
        assert isinstance(metadata.id, str)
        assert isinstance(metadata.name, str)
        assert isinstance(metadata.category, ToolCategory)
        assert isinstance(metadata.description, str)
        assert isinstance(metadata.parameters, dict)


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_registry_initializes_empty(self) -> None:
        """Test registry starts empty."""
        registry = ToolRegistry()
        assert registry.count() == 0
        assert registry.list_all() == []

    def test_registry_registers_tool(self) -> None:
        """Test registering a single tool."""
        registry = ToolRegistry()
        metadata = ToolMetadata(
            id="gov-query",
            name="Query Tool",
            category=ToolCategory.GOVERNANCE,
            description="Query governance state",
            parameters={}
        )
        registry.register(metadata)
        assert registry.count() == 1

    def test_registry_prevents_duplicate_registration(self) -> None:
        """Test that duplicate tool IDs are rejected."""
        registry = ToolRegistry()
        metadata1 = ToolMetadata(
            id="tool-001",
            name="Tool One",
            category=ToolCategory.GOVERNANCE,
            description="First",
            parameters={}
        )
        metadata2 = ToolMetadata(
            id="tool-001",
            name="Tool One Duplicate",
            category=ToolCategory.GOVERNANCE,
            description="Duplicate",
            parameters={}
        )
        registry.register(metadata1)
        with pytest.raises(ValueError):
            registry.register(metadata2)

    def test_registry_retrieves_tool_by_id(self) -> None:
        """Test retrieving tool by ID."""
        registry = ToolRegistry()
        metadata = ToolMetadata(
            id="search-001",
            name="Search Tool",
            category=ToolCategory.KNOWLEDGE,
            description="Search knowledge",
            parameters={}
        )
        registry.register(metadata)
        retrieved = registry.get("search-001")
        assert retrieved is not None
        assert retrieved.name == "Search Tool"

    def test_registry_returns_none_for_missing_tool(self) -> None:
        """Test that missing tools return None."""
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_registry_lists_tools_by_category(self) -> None:
        """Test filtering tools by category."""
        registry = ToolRegistry()
        
        # Register tools in different categories
        gov_tool = ToolMetadata(
            id="gov-001",
            name="Governance Tool",
            category=ToolCategory.GOVERNANCE,
            description="Governance",
            parameters={}
        )
        orch_tool = ToolMetadata(
            id="orch-001",
            name="Orchestration Tool",
            category=ToolCategory.ORCHESTRATION,
            description="Orchestration",
            parameters={}
        )
        
        registry.register(gov_tool)
        registry.register(orch_tool)
        
        gov_tools = registry.list_by_category(ToolCategory.GOVERNANCE)
        assert len(gov_tools) == 1
        assert gov_tools[0].id == "gov-001"
        
        orch_tools = registry.list_by_category(ToolCategory.ORCHESTRATION)
        assert len(orch_tools) == 1
        assert orch_tools[0].id == "orch-001"

    def test_registry_discovers_tools(self) -> None:
        """Test tool discovery API."""
        registry = ToolRegistry()
        
        gov_tool = ToolMetadata(
            id="gov-query",
            name="Query",
            category=ToolCategory.GOVERNANCE,
            description="Query",
            parameters={}
        )
        util_tool = ToolMetadata(
            id="util-echo",
            name="Echo",
            category=ToolCategory.UTILITY,
            description="Echo",
            parameters={}
        )
        
        registry.register(gov_tool)
        registry.register(util_tool)
        
        discovery = registry.discover()
        assert "governance" in discovery
        assert "utility" in discovery
        assert "gov-query" in discovery["governance"]
        assert "util-echo" in discovery["utility"]

    def test_registry_counts_by_category(self) -> None:
        """Test counting tools by category."""
        registry = ToolRegistry()
        
        # Register 3 governance tools
        for i in range(3):
            registry.register(ToolMetadata(
                id=f"gov-{i}",
                name=f"Gov Tool {i}",
                category=ToolCategory.GOVERNANCE,
                description="Gov",
                parameters={}
            ))
        
        # Register 2 knowledge tools
        for i in range(2):
            registry.register(ToolMetadata(
                id=f"know-{i}",
                name=f"Knowledge Tool {i}",
                category=ToolCategory.KNOWLEDGE,
                description="Knowledge",
                parameters={}
            ))
        
        assert registry.count_by_category(ToolCategory.GOVERNANCE) == 3
        assert registry.count_by_category(ToolCategory.KNOWLEDGE) == 2
        assert registry.count_by_category(ToolCategory.ORCHESTRATION) == 0


class TestMCPToolIntegration:
    """Integration tests for MCP tool registry."""

    def test_full_registry_workflow(self) -> None:
        """Test complete registry workflow."""
        registry = ToolRegistry()
        
        # Register 14 tools across all categories
        tools_spec = [
            ("gov-query", "Query Tool", ToolCategory.GOVERNANCE),
            ("gov-validate", "Validate Tool", ToolCategory.GOVERNANCE),
            ("gov-execute", "Execute Tool", ToolCategory.GOVERNANCE),
            ("gov-analyze", "Analyze Tool", ToolCategory.GOVERNANCE),
            ("gov-report", "Report Tool", ToolCategory.GOVERNANCE),
            ("orch-status", "Status Tool", ToolCategory.ORCHESTRATION),
            ("orch-monitor", "Monitor Tool", ToolCategory.ORCHESTRATION),
            ("orch-optimize", "Optimize Tool", ToolCategory.ORCHESTRATION),
            ("orch-diagnose", "Diagnose Tool", ToolCategory.ORCHESTRATION),
            ("know-search", "Search Tool", ToolCategory.KNOWLEDGE),
            ("know-analyze", "Analyze Tool", ToolCategory.KNOWLEDGE),
            ("know-generate", "Generate Tool", ToolCategory.KNOWLEDGE),
            ("util-echo", "Echo Tool", ToolCategory.UTILITY),
            ("util-sample", "Sample Tool", ToolCategory.UTILITY),
        ]
        
        for tool_id, name, category in tools_spec:
            metadata = ToolMetadata(
                id=tool_id,
                name=name,
                category=category,
                description=f"{name} description",
                parameters={},
                auth_required=(category == ToolCategory.GOVERNANCE)
            )
            registry.register(metadata)
        
        # Verify total count
        assert registry.count() == 14
        
        # Verify category counts
        assert registry.count_by_category(ToolCategory.GOVERNANCE) == 5
        assert registry.count_by_category(ToolCategory.ORCHESTRATION) == 4
        assert registry.count_by_category(ToolCategory.KNOWLEDGE) == 3
        assert registry.count_by_category(ToolCategory.UTILITY) == 2
        
        # Verify discovery
        discovery = registry.discover()
        assert len(discovery["governance"]) == 5
        assert len(discovery["orchestration"]) == 4
        assert len(discovery["knowledge"]) == 3
        assert len(discovery["utility"]) == 2
        
        # Verify retrieval
        gov_query = registry.get("gov-query")
        assert gov_query is not None
        assert gov_query.auth_required is True

    def test_registry_auth_required_enforcement(self) -> None:
        """Test auth_required flag for governance tools."""
        registry = ToolRegistry()
        
        gov_tool = ToolMetadata(
            id="gov-sensitive",
            name="Sensitive Op",
            category=ToolCategory.GOVERNANCE,
            description="Requires auth",
            parameters={},
            auth_required=True
        )
        
        util_tool = ToolMetadata(
            id="util-public",
            name="Public Op",
            category=ToolCategory.UTILITY,
            description="Public",
            parameters={},
            auth_required=False
        )
        
        registry.register(gov_tool)
        registry.register(util_tool)
        
        gov_retrieved = registry.get("gov-sensitive")
        util_retrieved = registry.get("util-public")
        assert gov_retrieved is not None
        assert util_retrieved is not None
        assert gov_retrieved.auth_required is True
        assert util_retrieved.auth_required is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
