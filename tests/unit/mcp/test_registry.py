"""Tests for Tool Registry (AC-MCP-COMPLIANCE-003)."""
import pytest
from datetime import datetime
from unittest.mock import Mock

from src.mcp.protocol import ToolParameter, ToolDefinition, MCPTool
from src.mcp.registry import ToolRegistry, ToolEntry

@pytest.fixture
def registry():
    """Create tool registry."""
    return ToolRegistry()

@pytest.fixture
def mock_tool():
    """Create mock tool."""
    tool = Mock(spec=MCPTool)
    definition = ToolDefinition(
        id="mock_tool_001",
        name="mock_operation",
        description="Mock tool for testing",
        tags=["mock", "test"]
    )
    tool.get_definition.return_value = definition
    tool.execute.return_value = {"status": "success"}
    return tool

# Unit Tests - Registration
def test_registry_creation():
    """Test registry creation."""
    reg = ToolRegistry()
    assert len(reg.tools) == 0
    assert len(reg.by_tag) == 0

def test_register_tool(registry, mock_tool):
    """Test tool registration."""
    result = registry.register(mock_tool)
    assert result is True
    assert "mock_tool_001" in registry.tools

def test_register_duplicate_tool(registry, mock_tool):
    """Test registering duplicate tool."""
    registry.register(mock_tool)
    result = registry.register(mock_tool)
    assert result is False  # Should fail on duplicate

def test_unregister_tool(registry, mock_tool):
    """Test tool unregistration."""
    registry.register(mock_tool)
    result = registry.unregister("mock_tool_001")
    assert result is True
    assert "mock_tool_001" not in registry.tools

def test_unregister_nonexistent_tool(registry):
    """Test unregistering nonexistent tool."""
    result = registry.unregister("nonexistent")
    assert result is False

def test_get_tool(registry, mock_tool):
    """Test getting registered tool."""
    registry.register(mock_tool)
    tool = registry.get_tool("mock_tool_001")
    assert tool is not None
    assert tool == mock_tool

def test_get_nonexistent_tool(registry):
    """Test getting nonexistent tool."""
    tool = registry.get_tool("nonexistent")
    assert tool is None

def test_get_definition(registry, mock_tool):
    """Test getting tool definition."""
    registry.register(mock_tool)
    definition = registry.get_definition("mock_tool_001")
    assert definition is not None
    assert definition.id == "mock_tool_001"

def test_list_tools(registry, mock_tool):
    """Test listing all tools."""
    registry.register(mock_tool)
    tools = registry.list_tools()
    assert len(tools) == 1
    assert tools[0].id == "mock_tool_001"

# Tag-based discovery
def test_tag_indexing(registry, mock_tool):
    """Test tag indexing during registration."""
    registry.register(mock_tool)
    assert "mock" in registry.by_tag
    assert "test" in registry.by_tag

def test_find_by_tag(registry, mock_tool):
    """Test finding tools by tag."""
    registry.register(mock_tool)
    results = registry.find_by_tag("mock")
    assert len(results) == 1
    assert results[0].id == "mock_tool_001"

def test_find_by_tag_no_results(registry):
    """Test finding tools by tag - no results."""
    results = registry.find_by_tag("nonexistent")
    assert len(results) == 0

# Search functionality
def test_search_by_name(registry, mock_tool):
    """Test searching tools by name."""
    registry.register(mock_tool)
    results = registry.search("mock")
    assert len(results) > 0

def test_search_by_description(registry, mock_tool):
    """Test searching tools by description."""
    registry.register(mock_tool)
    results = registry.search("testing")
    assert len(results) > 0

def test_search_case_insensitive(registry, mock_tool):
    """Test search is case insensitive."""
    registry.register(mock_tool)
    results_lower = registry.search("mock")
    results_upper = registry.search("MOCK")
    assert len(results_lower) == len(results_upper)

# Statistics and tracking
def test_record_execution_success(registry, mock_tool):
    """Test recording successful execution."""
    registry.register(mock_tool)
    registry.record_execution("mock_tool_001", True)
    entry = registry.tools["mock_tool_001"]
    assert entry.execution_count == 1
    assert entry.error_count == 0

def test_record_execution_failure(registry, mock_tool):
    """Test recording failed execution."""
    registry.register(mock_tool)
    registry.record_execution("mock_tool_001", False)
    entry = registry.tools["mock_tool_001"]
    assert entry.execution_count == 1
    assert entry.error_count == 1

def test_get_statistics(registry, mock_tool):
    """Test getting tool statistics."""
    registry.register(mock_tool)
    registry.record_execution("mock_tool_001", True)
    registry.record_execution("mock_tool_001", False)
    
    stats = registry.get_statistics("mock_tool_001")
    assert stats["execution_count"] == 2
    assert stats["error_count"] == 1
    assert stats["error_rate"] == 0.5

def test_usage_count_tracking(registry, mock_tool):
    """Test usage count tracking."""
    registry.register(mock_tool)
    registry.get_tool("mock_tool_001")
    registry.get_tool("mock_tool_001")
    
    entry = registry.tools["mock_tool_001"]
    assert entry.usage_count == 2

# Event listeners
def test_register_listener(registry, mock_tool):
    """Test registering event listener."""
    events = []
    
    def listener(event, tool_id):
        events.append((event, tool_id))
    
    registry.subscribe(listener)
    registry.register(mock_tool)
    
    assert len(events) == 1
    assert events[0] == ("tool_registered", "mock_tool_001")

def test_unregister_listener(registry, mock_tool):
    """Test unregistering event listener."""
    events = []
    
    def listener(event, tool_id):
        events.append((event, tool_id))
    
    registry.subscribe(listener)
    registry.register(mock_tool)
    registry.unsubscribe(listener)
    registry.unregister("mock_tool_001")
    
    assert len(events) == 1  # Only registration event

def test_multiple_listeners(registry, mock_tool):
    """Test multiple event listeners."""
    events1 = []
    events2 = []
    
    registry.subscribe(lambda e, t: events1.append((e, t)))
    registry.subscribe(lambda e, t: events2.append((e, t)))
    registry.register(mock_tool)
    
    assert len(events1) == 1
    assert len(events2) == 1

# Integration Tests
def test_multiple_tools_registry(registry):
    """Test registry with multiple tools."""
    tools = []
    for i in range(5):
        tool = Mock(spec=MCPTool)
        definition = ToolDefinition(
            id=f"tool_{i}",
            name=f"operation_{i}",
            description=f"Tool {i}",
            tags=[f"tag_{i % 2}"]
        )
        tool.get_definition.return_value = definition
        tools.append(tool)
        registry.register(tool)
    
    assert len(registry.tools) == 5
    all_tools = registry.list_tools()
    assert len(all_tools) == 5

def test_deprecated_tools_excluded(registry):
    """Test deprecated tools are excluded from listings."""
    tool = Mock(spec=MCPTool)
    definition = ToolDefinition(
        id="deprecated_tool",
        name="old_operation",
        description="Deprecated tool",
        deprecated=True
    )
    tool.get_definition.return_value = definition
    registry.register(tool)
    
    tools = registry.list_tools()
    assert len(tools) == 0  # Deprecated excluded

def test_tool_entry_metadata(registry, mock_tool):
    """Test tool entry metadata."""
    registry.register(mock_tool)
    entry = registry.tools["mock_tool_001"]
    
    assert entry.definition.id == "mock_tool_001"
    assert entry.registered_at is not None
    assert isinstance(entry.registered_at, datetime)
    assert entry.usage_count == 0
