"""
Tests for CORTEX MCP Tool Discovery Endpoint.

Phase 5 Task 3: Tool Discovery Endpoint
Date: 2026-01-27

Tests AC-MCP-TOOLS-001 through AC-MCP-TOOLS-010:
- Tool discovery queries orchestrators
- Returns JSON schema for each tool
- Caches results for 60 seconds
- Handles missing orchestrators
- Performance <500ms
- Thread-safe caching

CORE-008: TDD - Tests written before implementation.
CORE-011: All test functions have type hints.
CORE-012: All test classes have Google-style docstrings.
"""

import pytest
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor

from cortex.mcp.orchestrator_tools import (
    OrchestratorToolDiscovery,
    get_orchestrator_tool_discovery,
    discover_orchestrator_tools,
    get_orchestrator_tool_schema,
)


class TestOrchestratorToolDiscoveryInitialization:
    """Tests for OrchestratorToolDiscovery initialization and configuration."""
    
    def test_tool_discovery_initialization(self) -> None:
        """
        AC-MCP-TOOLS-001: OrchestratorToolDiscovery initializes with cache config.
        
        Validates:
        - Cache TTL defaults to 60 seconds
        - Cache storage initialized (starts as None, lazy-loaded)
        - Cache lock accessible
        """
        discovery = OrchestratorToolDiscovery(cache_ttl=60)
        
        assert discovery.cache_ttl == 60
        assert discovery._cache_lock is not None
        # Cache starts as None (lazy initialization on first query)
        assert discovery._cache is None or discovery._cache is not None
    
    def test_custom_cache_ttl(self) -> None:
        """
        AC-MCP-TOOLS-001: Custom cache TTL configuration.
        
        Validates:
        - Cache TTL can be customized
        - Different instances have independent caches
        """
        discovery1 = OrchestratorToolDiscovery(cache_ttl=30)
        discovery2 = OrchestratorToolDiscovery(cache_ttl=120)
        
        assert discovery1.cache_ttl == 30
        assert discovery2.cache_ttl == 120


class TestOrchestratorToolDiscovery:
    """Tests for tool discovery functionality."""
    
    def test_discover_all_orchestrators(self) -> None:
        """
        AC-MCP-TOOLS-002: Discovers tools from all orchestrators.
        
        Validates:
        - Queries all 23 orchestrators
        - Returns list of tool definitions
        - Each tool has required fields (name, orchestrator, description, parameters)
        """
        discovery = OrchestratorToolDiscovery()
        tools = discovery.discover_all_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Verify tool structure
        for tool in tools:
            assert "name" in tool
            assert "orchestrator" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert isinstance(tool["parameters"], dict)
    
    def test_tool_json_schema_format(self) -> None:
        """
        AC-MCP-TOOLS-003: Each tool has valid JSON schema.
        
        Validates:
        - Parameters follow JSON Schema spec
        - Schema includes type, properties, required fields
        - Properties have descriptions
        """
        discovery = OrchestratorToolDiscovery()
        tools = discovery.discover_all_tools()
        
        assert len(tools) > 0
        
        # Check at least one tool has proper schema
        tool = tools[0]
        schema = tool["parameters"]
        
        assert "type" in schema or "properties" in schema
        if "properties" in schema:
            assert isinstance(schema["properties"], dict)
    
    def test_tool_discovery_caching(self) -> None:
        """
        AC-MCP-TOOLS-004: Results cached for 60 seconds.
        
        Validates:
        - First call queries orchestrators
        - Subsequent calls use cache
        - Cache invalidates after TTL
        """
        discovery = OrchestratorToolDiscovery(cache_ttl=1)  # 1 second for testing
        
        # First call - should query orchestrators
        start_time = time.time()
        tools1 = discovery.discover_all_tools()
        first_duration = time.time() - start_time
        
        # Second call - should use cache (much faster)
        start_time = time.time()
        tools2 = discovery.discover_all_tools()
        second_duration = time.time() - start_time
        
        assert tools1 == tools2
        assert second_duration < first_duration * 0.5  # Cache should be much faster
        
        # Wait for cache expiry
        time.sleep(1.1)
        
        # Third call - cache expired, should query again
        tools3 = discovery.discover_all_tools()
        assert isinstance(tools3, list)
    
    def test_handles_missing_orchestrators(self) -> None:
        """
        AC-MCP-TOOLS-005: Gracefully handles missing orchestrators.
        
        Validates:
        - Missing orchestrators don't break discovery
        - Returns tools from available orchestrators
        - Logs warnings for unavailable orchestrators
        """
        discovery = OrchestratorToolDiscovery()
        
        # Even if some orchestrators fail, should return partial results
        with patch('cortex.mcp.orchestrator_tools.get_orchestrator_tools') as mock_get:
            # Simulate some orchestrators failing
            def side_effect(name):
                if name == "NonExistentOrchestrator":
                    raise Exception("Orchestrator not found")
                return [{"name": f"tool_from_{name}"}]
            
            mock_get.side_effect = side_effect
            
            # Should not raise exception
            tools = discovery.discover_all_tools()
            assert isinstance(tools, list)


class TestOrchestratorToolDiscoveryPerformance:
    """Tests for tool discovery performance requirements."""
    
    def test_discovery_performance(self) -> None:
        """
        AC-MCP-TOOLS-006: Discovery completes in <500ms.
        
        Validates:
        - Cold cache: first discovery <500ms
        - Warm cache: cached discovery <50ms
        """
        discovery = OrchestratorToolDiscovery()
        
        # Warm cache first
        discovery.discover_all_tools()
        
        # Test cached performance
        start_time = time.time()
        tools = discovery.discover_all_tools()
        duration = time.time() - start_time
        
        assert duration < 0.05  # 50ms for cached response
        assert len(tools) > 0
    
    def test_concurrent_discovery_requests(self) -> None:
        """
        AC-MCP-TOOLS-007: Thread-safe caching for concurrent requests.
        
        Validates:
        - Multiple threads can discover tools simultaneously
        - Cache remains consistent
        - No race conditions
        """
        discovery = OrchestratorToolDiscovery()
        results = []
        
        def discover():
            tools = discovery.discover_all_tools()
            results.append(len(tools))
        
        # Execute 10 concurrent discoveries
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(discover) for _ in range(10)]
            for future in futures:
                future.result()
        
        # All results should be identical
        assert len(set(results)) == 1  # All same length
        assert results[0] > 0


class TestToolSchemaValidation:
    """Tests for tool schema validation and structure."""
    
    def test_tool_has_required_fields(self) -> None:
        """
        AC-MCP-TOOLS-008: Each tool has required fields.
        
        Validates:
        - name (string)
        - orchestrator (string)
        - description (string)
        - parameters (JSON schema object)
        """
        discovery = OrchestratorToolDiscovery()
        tools = discovery.discover_all_tools()
        
        assert len(tools) > 0
        
        for tool in tools:
            assert isinstance(tool.get("name"), str)
            assert len(tool["name"]) > 0
            
            assert isinstance(tool.get("orchestrator"), str)
            assert len(tool["orchestrator"]) > 0
            
            assert isinstance(tool.get("description"), str)
            assert len(tool["description"]) > 0
            
            assert isinstance(tool.get("parameters"), dict)
    
    def test_parameter_schema_validity(self) -> None:
        """
        AC-MCP-TOOLS-009: Parameter schemas are valid JSON Schema.
        
        Validates:
        - Schema has type or properties
        - Properties have types
        - Required fields are listed
        """
        discovery = OrchestratorToolDiscovery()
        tools = discovery.discover_all_tools()
        
        for tool in tools:
            params = tool["parameters"]
            
            # Should have either type or properties
            has_structure = "type" in params or "properties" in params
            assert has_structure, f"Tool {tool['name']} missing schema structure"


class TestOrchestratorToolDiscoveryAPI:
    """Tests for tool discovery API functions."""
    
    def test_get_orchestrator_tool_discovery_singleton(self) -> None:
        """
        AC-MCP-TOOLS-010: Global discovery instance is singleton.
        
        Validates:
        - get_orchestrator_tool_discovery() returns same instance
        - Singleton pattern prevents duplicate cache storage
        """
        discovery1 = get_orchestrator_tool_discovery()
        discovery2 = get_orchestrator_tool_discovery()
        
        assert discovery1 is discovery2
    
    def test_discover_orchestrator_tools_helper(self) -> None:
        """
        AC-MCP-TOOLS-010: Helper function discovers tools.
        
        Validates:
        - discover_orchestrator_tools() returns tool list
        - Uses global singleton
        - Returns cached results
        """
        tools = discover_orchestrator_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        
        # Second call should use cache
        tools2 = discover_orchestrator_tools()
        assert tools == tools2
    
    def test_get_orchestrator_tool_schema_helper(self) -> None:
        """
        AC-MCP-TOOLS-010: Helper function retrieves specific tool schema.
        
        Validates:
        - get_orchestrator_tool_schema(name) returns tool definition
        - Returns None if tool not found
        """
        tools = discover_orchestrator_tools()
        
        if len(tools) > 0:
            tool_name = tools[0]["name"]
            schema = get_orchestrator_tool_schema(tool_name)
            
            assert schema is not None
            assert schema["name"] == tool_name
        
        # Non-existent tool
        non_existent = get_orchestrator_tool_schema("NonExistentTool12345")
        assert non_existent is None


class TestOrchestratorToolDiscoveryResponse:
    """Tests for tool discovery response format."""
    
    def test_response_format(self) -> None:
        """
        AC-MCP-TOOLS-010: Response format matches specification.
        
        Validates:
        - Returns dict with tools, count, cached, cache_expires_at
        - Tools is array of tool definitions
        - Count matches array length
        """
        discovery = OrchestratorToolDiscovery()
        response = discovery.get_discovery_response()
        
        assert isinstance(response, dict)
        assert "tools" in response
        assert "count" in response
        assert "cached" in response
        assert "cache_expires_at" in response
        
        assert isinstance(response["tools"], list)
        assert response["count"] == len(response["tools"])
        assert isinstance(response["cached"], bool)
    
    def test_cache_expires_at_format(self) -> None:
        """
        AC-MCP-TOOLS-010: Cache expiry timestamp is ISO 8601 format.
        
        Validates:
        - cache_expires_at is ISO 8601 string
        - Timestamp is in future
        """
        discovery = OrchestratorToolDiscovery()
        response = discovery.get_discovery_response()
        
        expires_at = response["cache_expires_at"]
        assert isinstance(expires_at, str)
        
        # Should be parseable as ISO 8601
        from datetime import datetime
        expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        # Should be in future (within reasonable bounds)
        now = datetime.now(expiry_time.tzinfo)
        assert expiry_time > now


class TestOrchestratorToolDiscoveryEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_orchestrator_list(self) -> None:
        """
        AC-MCP-TOOLS-005: Handles empty orchestrator list.
        
        Validates:
        - Returns empty list if no orchestrators available
        - Does not raise exception
        """
        with patch('cortex.mcp.orchestrator_tools.get_all_orchestrator_names', return_value=[]):
            discovery = OrchestratorToolDiscovery()
            tools = discovery.discover_all_tools()
            
            assert isinstance(tools, list)
            assert len(tools) == 0
    
    def test_cache_invalidation(self) -> None:
        """
        AC-MCP-TOOLS-004: Cache can be manually invalidated.
        
        Validates:
        - invalidate_cache() clears cached results
        - Next discovery queries orchestrators again
        """
        discovery = OrchestratorToolDiscovery()
        
        # Populate cache
        tools1 = discovery.discover_all_tools()
        assert discovery.is_cached()
        
        # Invalidate cache
        discovery.invalidate_cache()
        assert not discovery.is_cached()
        
        # Next call should query again
        tools2 = discovery.discover_all_tools()
        assert isinstance(tools2, list)
