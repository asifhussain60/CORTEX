"""
AC-MCP-COMPLIANCE-004: Tool Discovery Mechanism Test Suite.

Tests for dynamic tool discovery with:
- Multiple discovery patterns
- Query-based discovery
- Performance optimization
- Discovery filters and sorting
- Real-time tool availability checking
"""

import pytest
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

from cortex.mcp.protocol import ToolDefinition, ToolParameter


class DiscoveryPattern(Enum):
    """Supported tool discovery patterns."""
    BY_NAME = "by_name"
    BY_TAG = "by_tag"
    BY_CATEGORY = "by_category"
    BY_CAPABILITY = "by_capability"
    ALL_AVAILABLE = "all"
    PATTERN_MATCH = "pattern"


@dataclass
class DiscoveryQuery:
    """Tool discovery query specification."""
    pattern: DiscoveryPattern
    criteria: Optional[str] = None
    include_deprecated: bool = False
    sort_by: str = "name"  # name, access_count, created_at
    limit: Optional[int] = None
    offset: int = 0


@dataclass
class DiscoveryResult:
    """Result of a discovery operation."""
    tools: List[ToolDefinition]
    total_count: int
    query_time_ms: float
    result_cache_key: Optional[str] = None


class DiscoveryFilter:
    """Tool discovery filtering."""
    
    @staticmethod
    def filter_by_capability(tools: List[ToolDefinition], 
                            required_params: List[str]) -> List[ToolDefinition]:
        """Filter tools that have all required parameters."""
        result = []
        for tool in tools:
            param_names = {p.name for p in tool.parameters}
            if all(param in param_names for param in required_params):
                result.append(tool)
        return result
    
    @staticmethod
    def filter_deprecated(tools: List[ToolDefinition], 
                         include: bool = False) -> List[ToolDefinition]:
        """Filter deprecated tools."""
        if include:
            return tools
        return [t for t in tools if not t.deprecated]
    
    @staticmethod
    def filter_by_timeout(tools: List[ToolDefinition], 
                         max_timeout_ms: int) -> List[ToolDefinition]:
        """Filter tools by maximum timeout."""
        return [t for t in tools if t.timeout_ms <= max_timeout_ms]


class ToolDiscoveryEngine:
    """Engine for discovering available tools."""
    
    def __init__(self) -> None:
        """Initialize discovery engine."""
        self._tools: List[ToolDefinition] = []
        self._categories: Dict[str, List[ToolDefinition]] = {}
        self._capabilities_index: Dict[str, List[ToolDefinition]] = {}
        self._discovery_cache: Dict[str, DiscoveryResult] = {}
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool for discovery."""
        self._tools.append(tool)
        
        # Index by parameters (capabilities)
        for param in tool.parameters:
            if param.name not in self._capabilities_index:
                self._capabilities_index[param.name] = []
            self._capabilities_index[param.name].append(tool)
    
    def discover(self, query: DiscoveryQuery) -> DiscoveryResult:
        """Execute a discovery query."""
        start_time = time.time()
        
        # Check cache
        cache_key = self._make_cache_key(query)
        if cache_key in self._discovery_cache:
            return self._discovery_cache[cache_key]
        
        # Execute discovery
        tools = self._execute_discovery(query)
        
        # Apply filtering
        if not query.include_deprecated:
            tools = DiscoveryFilter.filter_deprecated(tools)
        
        # Sort
        tools = self._sort_results(tools, query.sort_by)
        
        # Apply pagination
        total_count = len(tools)
        if query.limit:
            tools = tools[query.offset:query.offset + query.limit]
        
        query_time = (time.time() - start_time) * 1000  # ms
        result = DiscoveryResult(
            tools=tools,
            total_count=total_count,
            query_time_ms=query_time,
            result_cache_key=cache_key
        )
        
        # Cache result
        self._discovery_cache[cache_key] = result
        
        return result
    
    def _execute_discovery(self, query: DiscoveryQuery) -> List[ToolDefinition]:
        """Execute discovery based on pattern."""
        if query.pattern == DiscoveryPattern.ALL_AVAILABLE:
            return self._tools.copy()
        
        elif query.pattern == DiscoveryPattern.BY_NAME:
            return [t for t in self._tools if t.name == query.criteria]
        
        elif query.pattern == DiscoveryPattern.BY_TAG:
            return [t for t in self._tools if query.criteria in t.tags]
        
        elif query.pattern == DiscoveryPattern.BY_CATEGORY:
            return self._categories.get(query.criteria, [])
        
        elif query.pattern == DiscoveryPattern.PATTERN_MATCH:
            return [t for t in self._tools if query.criteria.lower() in t.name.lower()]
        
        elif query.pattern == DiscoveryPattern.BY_CAPABILITY:
            return self._capabilities_index.get(query.criteria, [])
        
        return []
    
    def _sort_results(self, tools: List[ToolDefinition], sort_by: str) -> List[ToolDefinition]:
        """Sort discovery results."""
        if sort_by == "name":
            return sorted(tools, key=lambda t: t.name)
        elif sort_by == "version":
            return sorted(tools, key=lambda t: t.version, reverse=True)
        return tools
    
    def _make_cache_key(self, query: DiscoveryQuery) -> str:
        """Create cache key for discovery query."""
        return f"{query.pattern.value}:{query.criteria}:{query.include_deprecated}:{query.sort_by}"
    
    def clear_cache(self) -> None:
        """Clear discovery cache."""
        self._discovery_cache.clear()
    
    def get_tool_count(self) -> int:
        """Get total registered tools."""
        return len(self._tools)
    
    def get_available_tools(self, include_deprecated: bool = False) -> List[ToolDefinition]:
        """Get all available tools."""
        if include_deprecated:
            return self._tools.copy()
        return [t for t in self._tools if not t.deprecated]
    
    def suggest_tools(self, partial_name: str, limit: int = 5) -> List[ToolDefinition]:
        """Suggest tools based on partial name."""
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.PATTERN_MATCH,
            criteria=partial_name,
            limit=limit
        )
        result = self.discover(query)
        return result.tools


class TestToolDiscoveryMechanism:
    """Test tool discovery functionality."""
    
    def test_discovery_initialization(self) -> None:
        """Test discovery engine can be initialized."""
        engine = ToolDiscoveryEngine()
        assert engine.get_tool_count() == 0
    
    def test_register_tool_for_discovery(self) -> None:
        """Test registering a tool for discovery."""
        engine = ToolDiscoveryEngine()
        tool = ToolDefinition(
            id="tool_001",
            name="discover_me",
            description="Discoverable tool"
        )
        
        engine.register_tool(tool)
        assert engine.get_tool_count() == 1
    
    def test_discover_all_tools(self) -> None:
        """Test discovering all available tools."""
        engine = ToolDiscoveryEngine()
        
        for i in range(5):
            tool = ToolDefinition(
                id=f"tool_{i}",
                name=f"tool_{i}",
                description=""
            )
            engine.register_tool(tool)
        
        query = DiscoveryQuery(pattern=DiscoveryPattern.ALL_AVAILABLE)
        result = engine.discover(query)
        
        assert result.total_count == 5
        assert len(result.tools) == 5
    
    def test_discover_by_name(self) -> None:
        """Test discovering tool by exact name."""
        engine = ToolDiscoveryEngine()
        
        tools = [
            ToolDefinition(id="tool_1", name="json_processor", description=""),
            ToolDefinition(id="tool_2", name="xml_processor", description=""),
            ToolDefinition(id="tool_3", name="data_validator", description=""),
        ]
        
        for tool in tools:
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.BY_NAME,
            criteria="json_processor"
        )
        result = engine.discover(query)
        
        assert result.total_count == 1
        assert result.tools[0].name == "json_processor"
    
    def test_discover_by_tag(self) -> None:
        """Test discovering tools by tag."""
        engine = ToolDiscoveryEngine()
        
        tools = [
            ToolDefinition(
                id="tool_1",
                name="json_proc",
                description="",
                tags=["data", "json"]
            ),
            ToolDefinition(
                id="tool_2",
                name="xml_proc",
                description="",
                tags=["data", "xml"]
            ),
            ToolDefinition(
                id="tool_3",
                name="validator",
                description="",
                tags=["validation"]
            ),
        ]
        
        for tool in tools:
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.BY_TAG,
            criteria="data"
        )
        result = engine.discover(query)
        
        assert result.total_count == 2
    
    def test_discover_by_pattern(self) -> None:
        """Test discovering tools by name pattern."""
        engine = ToolDiscoveryEngine()
        
        tools = [
            ToolDefinition(id="tool_1", name="process_json", description=""),
            ToolDefinition(id="tool_2", name="process_xml", description=""),
            ToolDefinition(id="tool_3", name="validate_schema", description=""),
        ]
        
        for tool in tools:
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.PATTERN_MATCH,
            criteria="process"
        )
        result = engine.discover(query)
        
        assert result.total_count == 2
    
    def test_discover_by_capability(self) -> None:
        """Test discovering tools by capability (parameter)."""
        engine = ToolDiscoveryEngine()
        
        tools = [
            ToolDefinition(
                id="tool_1",
                name="tool_with_input",
                description="",
                parameters=[ToolParameter("input", "string", "")]
            ),
            ToolDefinition(
                id="tool_2",
                name="tool_without",
                description="",
                parameters=[]
            ),
        ]
        
        for tool in tools:
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.BY_CAPABILITY,
            criteria="input"
        )
        result = engine.discover(query)
        
        assert result.total_count == 1
        assert result.tools[0].name == "tool_with_input"
    
    def test_exclude_deprecated_tools(self) -> None:
        """Test filtering out deprecated tools."""
        engine = ToolDiscoveryEngine()
        
        tools = [
            ToolDefinition(
                id="tool_1",
                name="active_tool",
                description="",
                deprecated=False
            ),
            ToolDefinition(
                id="tool_2",
                name="deprecated_tool",
                description="",
                deprecated=True
            ),
        ]
        
        for tool in tools:
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.ALL_AVAILABLE,
            include_deprecated=False
        )
        result = engine.discover(query)
        
        assert result.total_count == 1
        assert result.tools[0].name == "active_tool"
    
    def test_include_deprecated_tools(self) -> None:
        """Test including deprecated tools when requested."""
        engine = ToolDiscoveryEngine()
        
        tools = [
            ToolDefinition(id="tool_1", name="active", description="", deprecated=False),
            ToolDefinition(id="tool_2", name="old", description="", deprecated=True),
        ]
        
        for tool in tools:
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.ALL_AVAILABLE,
            include_deprecated=True
        )
        result = engine.discover(query)
        
        assert result.total_count == 2
    
    def test_result_sorting(self) -> None:
        """Test discovery results are sorted."""
        engine = ToolDiscoveryEngine()
        
        for name in ["zebra_tool", "alpha_tool", "beta_tool"]:
            tool = ToolDefinition(id=name, name=name, description="")
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.ALL_AVAILABLE,
            sort_by="name"
        )
        result = engine.discover(query)
        
        names = [t.name for t in result.tools]
        assert names == ["alpha_tool", "beta_tool", "zebra_tool"]
    
    def test_pagination(self) -> None:
        """Test paginating discovery results."""
        engine = ToolDiscoveryEngine()
        
        for i in range(10):
            tool = ToolDefinition(id=f"tool_{i}", name=f"tool_{i:02d}", description="")
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.ALL_AVAILABLE,
            limit=3,
            offset=0
        )
        result = engine.discover(query)
        
        assert result.total_count == 10
        assert len(result.tools) == 3
        
        # Get next page
        query.offset = 3
        result2 = engine.discover(query)
        assert len(result2.tools) == 3
    
    def test_discovery_caching(self) -> None:
        """Test discovery results are cached."""
        engine = ToolDiscoveryEngine()
        
        tool = ToolDefinition(id="tool", name="test", description="")
        engine.register_tool(tool)
        
        query = DiscoveryQuery(pattern=DiscoveryPattern.ALL_AVAILABLE)
        
        # First query
        result1 = engine.discover(query)
        assert result1.result_cache_key is not None
        
        # Second query should return cached result
        result2 = engine.discover(query)
        assert result2.result_cache_key == result1.result_cache_key
    
    def test_cache_invalidation(self) -> None:
        """Test clearing discovery cache."""
        engine = ToolDiscoveryEngine()
        tool = ToolDefinition(id="tool", name="test", description="")
        engine.register_tool(tool)
        
        query = DiscoveryQuery(pattern=DiscoveryPattern.ALL_AVAILABLE)
        result1 = engine.discover(query)
        cache_key1 = result1.result_cache_key
        
        engine.clear_cache()
        result2 = engine.discover(query)
        
        # Cache should be repopulated
        assert result2.result_cache_key == cache_key1
    
    def test_suggest_tools(self) -> None:
        """Test tool suggestions based on partial name."""
        engine = ToolDiscoveryEngine()
        
        tools = [
            ToolDefinition(id="1", name="process_json", description=""),
            ToolDefinition(id="2", name="process_xml", description=""),
            ToolDefinition(id="3", name="validate_json", description=""),
            ToolDefinition(id="4", name="execute_query", description=""),
        ]
        
        for tool in tools:
            engine.register_tool(tool)
        
        suggestions = engine.suggest_tools("process", limit=5)
        
        assert len(suggestions) >= 1
        assert any("process" in t.name for t in suggestions)
    
    def test_discovery_performance(self) -> None:
        """Test discovery is performant."""
        engine = ToolDiscoveryEngine()
        
        # Register many tools
        for i in range(100):
            tool = ToolDefinition(
                id=f"tool_{i:03d}",
                name=f"tool_{i:03d}",
                description="",
                tags=["batch"] if i % 2 == 0 else []
            )
            engine.register_tool(tool)
        
        query = DiscoveryQuery(
            pattern=DiscoveryPattern.BY_TAG,
            criteria="batch"
        )
        result = engine.discover(query)
        
        # Should be fast (< 100ms)
        assert result.query_time_ms < 100
        assert result.total_count == 50
    
    def test_multiple_tag_discovery(self) -> None:
        """Test discovering tools with multiple matching tags."""
        engine = ToolDiscoveryEngine()
        
        tool = ToolDefinition(
            id="tool",
            name="multi_tag_tool",
            description="",
            tags=["processing", "data", "analytics"]
        )
        engine.register_tool(tool)
        
        for tag in ["processing", "data", "analytics"]:
            query = DiscoveryQuery(
                pattern=DiscoveryPattern.BY_TAG,
                criteria=tag
            )
            result = engine.discover(query)
            assert result.total_count == 1


class TestDiscoveryFiltering:
    """Test discovery filtering capabilities."""
    
    def test_filter_by_capability(self) -> None:
        """Test filtering tools by required capabilities."""
        tools = [
            ToolDefinition(
                id="1",
                name="full_tool",
                description="",
                parameters=[
                    ToolParameter("input", "string", ""),
                    ToolParameter("format", "string", ""),
                ]
            ),
            ToolDefinition(
                id="2",
                name="partial_tool",
                description="",
                parameters=[ToolParameter("input", "string", "")]
            ),
        ]
        
        filtered = DiscoveryFilter.filter_by_capability(tools, ["input", "format"])
        assert len(filtered) == 1
        assert filtered[0].name == "full_tool"
    
    def test_filter_by_timeout(self) -> None:
        """Test filtering tools by timeout."""
        tools = [
            ToolDefinition(id="1", name="fast", description="", timeout_ms=5000),
            ToolDefinition(id="2", name="slow", description="", timeout_ms=120000),
        ]
        
        fast_tools = DiscoveryFilter.filter_by_timeout(tools, 30000)
        assert len(fast_tools) == 1
        assert fast_tools[0].name == "fast"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
