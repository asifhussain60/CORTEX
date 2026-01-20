"""
AC-MCP-COMPLIANCE-003: Tool Registry Implementation Test Suite.

Tests for centralized tool registry supporting:
- Tool registration and deregistration
- Tool discovery by name, category, tags
- Tool versioning and updates
- Tool inventory management
- Registry state management
"""

import pytest
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time

from src.mcp.protocol import ToolDefinition, ToolParameter


@dataclass
class RegistryEntry:
    """Entry in the tool registry."""
    tool: ToolDefinition
    registered_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    
    def mark_accessed(self) -> None:
        """Mark this tool as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


class ToolRegistry:
    """Centralized registry for MCP tools."""
    
    def __init__(self) -> None:
        """Initialize registry."""
        self._tools: Dict[str, RegistryEntry] = {}
        self._tags_index: Dict[str, List[str]] = {}  # tag -> tool names
        self._categories: Dict[str, List[str]] = {}  # category -> tool names
    
    def register(self, tool: ToolDefinition) -> Tuple[bool, str]:
        """Register a tool. Returns (success, message)."""
        if tool.name in self._tools:
            return False, f"Tool '{tool.name}' already registered"
        
        if not tool.name:
            return False, "Tool name cannot be empty"
        
        entry = RegistryEntry(tool=tool, tags=tool.tags)
        self._tools[tool.name] = entry
        
        # Index by tags
        for tag in tool.tags:
            if tag not in self._tags_index:
                self._tags_index[tag] = []
            self._tags_index[tag].append(tool.name)
        
        return True, f"Tool '{tool.name}' registered successfully"
    
    def unregister(self, tool_name: str) -> Tuple[bool, str]:
        """Unregister a tool. Returns (success, message)."""
        if tool_name not in self._tools:
            return False, f"Tool '{tool_name}' not found"
        
        entry = self._tools.pop(tool_name)
        
        # Remove from tag index
        for tag in entry.tags:
            if tag in self._tags_index and tool_name in self._tags_index[tag]:
                self._tags_index[tag].remove(tool_name)
        
        return True, f"Tool '{tool_name}' unregistered successfully"
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get a tool by name and mark as accessed."""
        if tool_name in self._tools:
            entry = self._tools[tool_name]
            entry.mark_accessed()
            return entry.tool
        return None
    
    def find_by_tag(self, tag: str) -> List[ToolDefinition]:
        """Find all tools with a specific tag."""
        if tag not in self._tags_index:
            return []
        
        tools = []
        for tool_name in self._tags_index[tag]:
            if tool_name in self._tools:
                tools.append(self._tools[tool_name].tool)
        return tools
    
    def find_by_name_pattern(self, pattern: str) -> List[ToolDefinition]:
        """Find tools matching name pattern."""
        tools = []
        for tool_name, entry in self._tools.items():
            if pattern.lower() in tool_name.lower():
                tools.append(entry.tool)
        return tools
    
    def list_all(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return [entry.tool for entry in self._tools.values()]
    
    def list_by_category(self, category: str) -> List[ToolDefinition]:
        """List all tools in a category."""
        if category not in self._categories:
            return []
        return [self._tools[name].tool for name in self._categories[category]
                if name in self._tools]
    
    def count(self) -> int:
        """Get total number of registered tools."""
        return len(self._tools)
    
    def is_registered(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in self._tools
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        total_accesses = sum(entry.access_count for entry in self._tools.values())
        return {
            "total_tools": len(self._tools),
            "total_accesses": total_accesses,
            "unique_tags": len(self._tags_index),
            "unique_categories": len(self._categories),
        }
    
    def update_tool(self, tool_name: str, tool: ToolDefinition) -> Tuple[bool, str]:
        """Update an existing tool."""
        if tool_name not in self._tools:
            return False, f"Tool '{tool_name}' not found"
        
        old_entry = self._tools[tool_name]
        
        # Remove old tag associations
        for tag in old_entry.tags:
            if tag in self._tags_index and tool_name in self._tags_index[tag]:
                self._tags_index[tag].remove(tool_name)
        
        # Create new entry preserving access stats
        new_entry = RegistryEntry(
            tool=tool,
            tags=tool.tags,
            access_count=old_entry.access_count,
            last_accessed=old_entry.last_accessed
        )
        self._tools[tool_name] = new_entry
        
        # Add new tag associations
        for tag in tool.tags:
            if tag not in self._tags_index:
                self._tags_index[tag] = []
            self._tags_index[tag].append(tool_name)
        
        return True, f"Tool '{tool_name}' updated successfully"


class TestToolRegistry:
    """Test tool registry functionality."""
    
    def test_registry_initialization(self) -> None:
        """Test registry can be initialized."""
        registry = ToolRegistry()
        assert registry.count() == 0
        assert registry.list_all() == []
    
    def test_register_single_tool(self) -> None:
        """Test registering a single tool."""
        registry = ToolRegistry()
        tool = ToolDefinition(
            id="tool_001",
            name="test_tool",
            description="Test tool"
        )
        
        success, msg = registry.register(tool)
        assert success is True
        assert registry.count() == 1
        assert registry.is_registered("test_tool")
    
    def test_register_duplicate_tool(self) -> None:
        """Test registering duplicate tool fails."""
        registry = ToolRegistry()
        tool = ToolDefinition(
            id="tool_001",
            name="test_tool",
            description="Test tool"
        )
        
        registry.register(tool)
        success, msg = registry.register(tool)
        assert success is False
        assert "already registered" in msg
    
    def test_unregister_tool(self) -> None:
        """Test unregistering a tool."""
        registry = ToolRegistry()
        tool = ToolDefinition(
            id="tool_001",
            name="test_tool",
            description="Test tool"
        )
        
        registry.register(tool)
        assert registry.count() == 1
        
        success, msg = registry.unregister("test_tool")
        assert success is True
        assert registry.count() == 0
        assert not registry.is_registered("test_tool")
    
    def test_get_tool(self) -> None:
        """Test retrieving a tool by name."""
        registry = ToolRegistry()
        tool = ToolDefinition(
            id="tool_001",
            name="process_data",
            description="Process data"
        )
        
        registry.register(tool)
        retrieved = registry.get_tool("process_data")
        
        assert retrieved is not None
        assert retrieved.name == "process_data"
        assert retrieved.id == "tool_001"
    
    def test_get_nonexistent_tool(self) -> None:
        """Test getting non-existent tool returns None."""
        registry = ToolRegistry()
        result = registry.get_tool("nonexistent")
        assert result is None
    
    def test_register_multiple_tools(self) -> None:
        """Test registering multiple tools."""
        registry = ToolRegistry()
        tools = [
            ToolDefinition(id=f"tool_{i}", name=f"tool_{i}", description=f"Tool {i}")
            for i in range(5)
        ]
        
        for tool in tools:
            registry.register(tool)
        
        assert registry.count() == 5
        assert len(registry.list_all()) == 5
    
    def test_tool_tagging(self) -> None:
        """Test tools are indexed by tags."""
        registry = ToolRegistry()
        tool1 = ToolDefinition(
            id="tool_001",
            name="json_processor",
            description="Process JSON",
            tags=["data", "json"]
        )
        tool2 = ToolDefinition(
            id="tool_002",
            name="xml_processor",
            description="Process XML",
            tags=["data", "xml"]
        )
        
        registry.register(tool1)
        registry.register(tool2)
        
        data_tools = registry.find_by_tag("data")
        assert len(data_tools) == 2
        
        json_tools = registry.find_by_tag("json")
        assert len(json_tools) == 1
        assert json_tools[0].name == "json_processor"
    
    def test_find_by_name_pattern(self) -> None:
        """Test finding tools by name pattern."""
        registry = ToolRegistry()
        tools = [
            ToolDefinition(id="tool_001", name="process_json", description=""),
            ToolDefinition(id="tool_002", name="process_xml", description=""),
            ToolDefinition(id="tool_003", name="validate_schema", description=""),
        ]
        
        for tool in tools:
            registry.register(tool)
        
        process_tools = registry.find_by_name_pattern("process")
        assert len(process_tools) == 2
        
        all_tools = registry.find_by_name_pattern("")
        assert len(all_tools) == 3
    
    def test_access_tracking(self) -> None:
        """Test tool access is tracked."""
        registry = ToolRegistry()
        tool = ToolDefinition(
            id="tool_001",
            name="tracked_tool",
            description="Tracked"
        )
        
        registry.register(tool)
        
        # Access tool multiple times
        for _ in range(3):
            registry.get_tool("tracked_tool")
        
        stats = registry.get_stats()
        assert stats["total_accesses"] == 3
    
    def test_registry_statistics(self) -> None:
        """Test registry statistics."""
        registry = ToolRegistry()
        tools = [
            ToolDefinition(
                id=f"tool_{i}",
                name=f"tool_{i}",
                description="",
                tags=["category_a", "common"]
            )
            for i in range(3)
        ]
        
        for tool in tools:
            registry.register(tool)
        
        stats = registry.get_stats()
        assert stats["total_tools"] == 3
        assert stats["unique_tags"] >= 1
    
    def test_update_tool(self) -> None:
        """Test updating a tool in registry."""
        registry = ToolRegistry()
        tool_v1 = ToolDefinition(
            id="tool_001",
            name="updatable_tool",
            description="Version 1",
            version="1.0.0"
        )
        
        registry.register(tool_v1)
        
        tool_v2 = ToolDefinition(
            id="tool_001",
            name="updatable_tool",
            description="Version 2",
            version="2.0.0"
        )
        
        success, msg = registry.update_tool("updatable_tool", tool_v2)
        assert success is True
        
        updated = registry.get_tool("updatable_tool")
        assert updated.version == "2.0.0"
        assert updated.description == "Version 2"
    
    def test_update_nonexistent_tool(self) -> None:
        """Test updating non-existent tool fails."""
        registry = ToolRegistry()
        tool = ToolDefinition(id="tool", name="tool", description="")
        
        success, msg = registry.update_tool("nonexistent", tool)
        assert success is False
    
    def test_tool_versioning(self) -> None:
        """Test managing tool versions."""
        registry = ToolRegistry()
        
        # Register different version
        tool = ToolDefinition(
            id="versioned_tool",
            name="versioned_tool",
            description="Tool with version",
            version="1.0.0"
        )
        registry.register(tool)
        
        retrieved = registry.get_tool("versioned_tool")
        assert retrieved.version == "1.0.0"
    
    def test_bulk_operations(self) -> None:
        """Test bulk registry operations."""
        registry = ToolRegistry()
        
        # Bulk register
        tools = [
            ToolDefinition(
                id=f"bulk_{i}",
                name=f"bulk_tool_{i}",
                description=f"Bulk tool {i}",
                tags=["bulk"]
            )
            for i in range(10)
        ]
        
        for tool in tools:
            registry.register(tool)
        
        assert registry.count() == 10
        
        bulk_tools = registry.find_by_tag("bulk")
        assert len(bulk_tools) == 10
    
    def test_registry_isolation(self) -> None:
        """Test multiple registries are isolated."""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()
        
        tool = ToolDefinition(id="tool", name="test", description="")
        registry1.register(tool)
        
        assert registry1.count() == 1
        assert registry2.count() == 0
    
    def test_empty_tag_search(self) -> None:
        """Test searching for non-existent tags."""
        registry = ToolRegistry()
        tool = ToolDefinition(
            id="tool",
            name="test",
            description="",
            tags=["existing"]
        )
        registry.register(tool)
        
        result = registry.find_by_tag("nonexistent")
        assert result == []


class TestToolDiscovery:
    """Test tool discovery functionality."""
    
    def test_simple_discovery(self) -> None:
        """Test simple tool discovery."""
        registry = ToolRegistry()
        
        tools = [
            ToolDefinition(
                id=f"tool_{i}",
                name=f"tool_{i}",
                description=f"Tool {i}",
                tags=["processing"]
            )
            for i in range(3)
        ]
        
        for tool in tools:
            registry.register(tool)
        
        # Discover all tools
        all_tools = registry.list_all()
        assert len(all_tools) == 3
        
        # Discover by tag
        processing_tools = registry.find_by_tag("processing")
        assert len(processing_tools) == 3
    
    def test_advanced_discovery(self) -> None:
        """Test advanced discovery patterns."""
        registry = ToolRegistry()
        
        tools = [
            ToolDefinition(
                id="tool_001",
                name="process_json_data",
                description="Process JSON",
                tags=["data", "json", "processing"]
            ),
            ToolDefinition(
                id="tool_002",
                name="validate_json_schema",
                description="Validate schema",
                tags=["validation", "json"]
            ),
            ToolDefinition(
                id="tool_003",
                name="transform_xml_data",
                description="Transform XML",
                tags=["data", "xml", "processing"]
            ),
        ]
        
        for tool in tools:
            registry.register(tool)
        
        # Find by multiple criteria
        json_tools = registry.find_by_tag("json")
        assert len(json_tools) == 2
        
        processing_tools = registry.find_by_tag("processing")
        assert len(processing_tools) == 2
        
        data_tools = registry.find_by_tag("data")
        assert len(data_tools) == 2
    
    def test_discovery_performance(self) -> None:
        """Test discovery is efficient."""
        registry = ToolRegistry()
        
        # Register many tools
        for i in range(100):
            tool = ToolDefinition(
                id=f"tool_{i:03d}",
                name=f"tool_{i:03d}",
                description="",
                tags=["batch"] if i % 2 == 0 else ["other"]
            )
            registry.register(tool)
        
        # Fast discovery
        import time
        start = time.time()
        batch_tools = registry.find_by_tag("batch")
        elapsed = time.time() - start
        
        assert len(batch_tools) == 50
        assert elapsed < 0.1  # Should be very fast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
