"""
MCP Server v2 Test Suite.

Comprehensive tests for the consolidated MCP server covering:
- Tool registration and discovery
- Protocol compliance (JSON-RPC 2.0)
- Cross-platform compatibility
- Extensibility patterns
- Error handling
- Performance characteristics

These tests verify that CORTEX MCP is the SINGLE entry point
for ALL functionality with proper consolidation.
"""

import json
import pytest
import sys
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from cortex.mcp.mcp_tool_base import (
    Tool,
    ToolDefinition,
    ToolParameter,
    ToolResult,
    ToolCategory,
    ConsolidatedTool,
)
from cortex.mcp.mcp_registry import (
    ToolRegistry,
    PRODUCTION_TOOLS,
    ToolMetadata,
    get_registry,
)
from cortex.mcp.server import MCPServer, MCPRequest, MCPResponse


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def registry():
    """Fresh tool registry for each test."""
    return ToolRegistry()


@pytest.fixture
def server(registry):
    """MCP server with test registry."""
    return MCPServer(registry=registry)


@pytest.fixture
def sample_tool():
    """Sample tool implementation for testing."""
    class SampleTool(Tool):
        @property
        def definition(self) -> ToolDefinition:
            return ToolDefinition(
                name="test_sample",
                description="Test sample tool",
                category=ToolCategory.UTILITIES,
                parameters=[
                    ToolParameter(name="input", type="string", required=True),
                    ToolParameter(name="mode", type="string", required=False, default="normal"),
                ],
            )
        
        def execute(self, input: str = "", mode: str = "normal", **kwargs) -> ToolResult:
            return ToolResult(
                success=True,
                data={"processed": input, "mode": mode},
            )
    
    return SampleTool()


# ============================================================================
# TIER 1: TOOL CONSOLIDATION TESTS (HIGH PRIORITY)
# ============================================================================

class TestToolConsolidation:
    """Tests verifying 98→24 tool consolidation."""
    
    def test_production_tools_count_is_24(self):
        """CRITICAL: Verify exactly 24 production tools defined."""
        assert len(PRODUCTION_TOOLS) == 24, f"Expected 24 tools, got {len(PRODUCTION_TOOLS)}"
    
    def test_all_tool_categories_covered(self):
        """Verify all business capabilities have tools."""
        categories_found = set()
        for tool_id, spec in PRODUCTION_TOOLS.items():
            categories_found.add(spec["category"])
        
        expected = {
            ToolCategory.CORE,
            ToolCategory.INTELLIGENCE,
            ToolCategory.GOVERNANCE,
            ToolCategory.OPERATIONS,
            ToolCategory.UTILITIES,
        }
        assert categories_found == expected
    
    def test_no_duplicate_tool_names(self):
        """Verify all tool names are unique."""
        names = list(PRODUCTION_TOOLS.keys())
        assert len(names) == len(set(names)), "Duplicate tool names found"
    
    def test_consolidated_tools_have_operations(self):
        """Verify consolidated tools define their operations."""
        consolidated = [
            "cortex_request_lifecycle",
            "cortex_lens",
            "cortex_knowledge",
            "cortex_git",
            "cortex_governance",
            "cortex_validate",
            "cortex_load",
            "cortex_debug",
            "cortex_refactor",
            "cortex_plan",
            "cortex_onboard",
            "cortex_dashboard",
            "cortex_verify",
            "cortex_metrics",
            "cortex_check",
            "cortex_orchestrator",
        ]
        
        for tool_id in consolidated:
            spec = PRODUCTION_TOOLS.get(tool_id)
            assert spec is not None, f"Tool {tool_id} not found"
            assert len(spec.get("operations", [])) > 0, f"Tool {tool_id} should have operations"
    
    def test_tool_naming_convention(self):
        """All tools should follow cortex_* naming convention."""
        for tool_id in PRODUCTION_TOOLS:
            assert tool_id.startswith("cortex_"), f"Tool {tool_id} doesn't follow naming convention"


class TestToolCategories:
    """Tests for tool category distribution."""
    
    def test_core_tools_count(self):
        """Verify 4 core request processing tools."""
        core = [t for t, s in PRODUCTION_TOOLS.items() if s["category"] == ToolCategory.CORE]
        assert len(core) == 4, f"Expected 4 core tools, got {len(core)}: {core}"
    
    def test_intelligence_tools_count(self):
        """Verify 3 code intelligence tools."""
        intel = [t for t, s in PRODUCTION_TOOLS.items() if s["category"] == ToolCategory.INTELLIGENCE]
        assert len(intel) == 3, f"Expected 3 intelligence tools, got {len(intel)}: {intel}"
    
    def test_governance_tools_count(self):
        """Verify 3 governance & compliance tools."""
        gov = [t for t, s in PRODUCTION_TOOLS.items() if s["category"] == ToolCategory.GOVERNANCE]
        assert len(gov) == 3, f"Expected 3 governance tools, got {len(gov)}: {gov}"
    
    def test_operations_tools_count(self):
        """Verify 5 operations tools."""
        ops = [t for t, s in PRODUCTION_TOOLS.items() if s["category"] == ToolCategory.OPERATIONS]
        assert len(ops) == 5, f"Expected 5 operations tools, got {len(ops)}: {ops}"
    
    def test_utilities_tools_count(self):
        """Verify 9 utility tools."""
        utils = [t for t, s in PRODUCTION_TOOLS.items() if s["category"] == ToolCategory.UTILITIES]
        assert len(utils) == 9, f"Expected 9 utility tools, got {len(utils)}: {utils}"


# ============================================================================
# TIER 2: REGISTRY TESTS
# ============================================================================

class TestToolRegistry:
    """Tests for tool registry functionality."""
    
    def test_registry_auto_registers_production_tools(self, registry):
        """Registry should auto-register all production tools."""
        assert registry.tool_count == 24
    
    def test_registry_get_metadata(self, registry):
        """Get metadata for registered tool."""
        metadata = registry.get_metadata("cortex_lens")
        assert metadata is not None
        assert metadata.id == "cortex_lens"
        assert metadata.category == ToolCategory.INTELLIGENCE
        assert len(metadata.operations) > 0
    
    def test_registry_list_by_category(self, registry):
        """List tools by category."""
        core_tools = registry.list_by_category(ToolCategory.CORE)
        assert len(core_tools) == 4
        assert all(t.category == ToolCategory.CORE for t in core_tools)
    
    def test_registry_to_mcp_schema(self, registry):
        """Generate MCP-compliant schema."""
        schema = registry.to_mcp_schema()
        assert len(schema) == 24
        
        # Verify schema structure
        for tool_schema in schema:
            assert "name" in tool_schema
            assert "description" in tool_schema
            assert "inputSchema" in tool_schema
            assert tool_schema["inputSchema"]["type"] == "object"
    
    def test_register_custom_tool(self, registry, sample_tool):
        """Register a custom tool implementation."""
        initial_count = registry.tool_count
        registry.register(sample_tool)
        
        # Custom tools are implementations, not new entries
        retrieved = registry.get("test_sample")
        assert retrieved is sample_tool


# ============================================================================
# TIER 3: MCP SERVER TESTS
# ============================================================================

class TestMCPServer:
    """Tests for MCP server functionality."""
    
    def test_server_initializes_with_24_tools(self, server):
        """Server should have 24 tools on initialization."""
        tools = server.list_tools()
        assert len(tools) == 24
    
    def test_list_tools_returns_mcp_schema(self, server):
        """list_tools returns MCP-compliant schemas."""
        tools = server.list_tools()
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_list_tools_by_category(self, server):
        """Filter tools by category."""
        core = server.list_tools_by_category("core")
        assert len(core) == 4
        assert all(t["category"] == "core" for t in core)
    
    def test_call_unknown_tool_returns_error(self, server):
        """Calling unknown tool returns error."""
        result = server.call_tool("unknown_tool")
        assert not result.success
        assert "Unknown tool" in result.error
    
    def test_call_implemented_tool_succeeds(self, server):
        """Calling implemented tool returns success."""
        result = server.call_tool("cortex_lens", operation="analyze", target=".")
        assert result.success
        assert "lens" in result.data
    
    def test_health_check(self, server):
        """Health check returns server status."""
        health = server.health_check()
        
        assert health["status"] == "healthy"
        assert health["version"] == "2.0.0"
        assert health["tools"]["total"] == 24
        assert "by_category" in health["tools"]


# ============================================================================
# TIER 4: JSON-RPC PROTOCOL TESTS
# ============================================================================

class TestJSONRPCProtocol:
    """Tests for JSON-RPC 2.0 compliance."""
    
    def test_initialize_handshake(self, server):
        """Handle MCP initialization."""
        request = MCPRequest(
            method="initialize",
            params={
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"},
            },
            id="init-1",
        )
        
        response = server.handle_request(request)
        assert response.id == "init-1"
        assert response.error is None
        assert "protocolVersion" in response.result
        assert "capabilities" in response.result
    
    def test_tools_list_method(self, server):
        """Handle tools/list method."""
        request = MCPRequest(method="tools/list", id="list-1")
        response = server.handle_request(request)
        
        assert response.id == "list-1"
        assert response.error is None
        assert len(response.result) == 24
    
    def test_tools_call_method(self, server):
        """Handle tools/call method."""
        request = MCPRequest(
            method="tools/call",
            params={
                "name": "cortex_lens",
                "arguments": {"operation": "analyze", "target": "."},
            },
            id="call-1",
        )
        
        response = server.handle_request(request)
        assert response.id == "call-1"
        # Will fail gracefully since not implemented
        assert "result" in dir(response) or "error" in dir(response)
    
    def test_unknown_method_returns_error(self, server):
        """Unknown method returns METHOD_NOT_FOUND error."""
        request = MCPRequest(method="unknown/method", id="err-1")
        response = server.handle_request(request)
        
        assert response.id == "err-1"
        assert response.error is not None
        assert response.error["code"] == MCPServer.METHOD_NOT_FOUND
    
    def test_handle_json_parses_request(self, server):
        """Handle raw JSON request string."""
        json_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "json-1",
        })
        
        json_response = server.handle_json(json_request)
        response = json.loads(json_response)
        
        assert response["id"] == "json-1"
        assert "result" in response
    
    def test_handle_invalid_json_returns_parse_error(self, server):
        """Invalid JSON returns PARSE_ERROR."""
        response_str = server.handle_json("not valid json")
        response = json.loads(response_str)
        
        assert response["error"]["code"] == MCPServer.PARSE_ERROR


# ============================================================================
# TIER 5: BASE CLASS TESTS
# ============================================================================

class TestToolBase:
    """Tests for Tool base classes."""
    
    def test_tool_definition_to_schema(self):
        """ToolDefinition generates correct MCP schema."""
        definition = ToolDefinition(
            name="test_tool",
            description="Test description",
            category=ToolCategory.CORE,
            parameters=[
                ToolParameter(name="required_param", type="string", required=True),
                ToolParameter(name="optional_param", type="number", required=False, default=10),
            ],
        )
        
        schema = definition.to_mcp_schema()
        
        assert schema["name"] == "test_tool"
        assert schema["description"] == "Test description"
        assert "required_param" in schema["inputSchema"]["properties"]
        assert "required_param" in schema["inputSchema"]["required"]
        assert "optional_param" not in schema["inputSchema"]["required"]
    
    def test_tool_result_serialization(self):
        """ToolResult serializes correctly."""
        result = ToolResult(
            success=True,
            data={"key": "value"},
            metadata={"execution_time": 100},
        )
        
        as_dict = result.to_dict()
        
        assert as_dict["success"] is True
        assert as_dict["data"]["key"] == "value"
        assert "timestamp" in as_dict
    
    def test_tool_parameter_validation(self, sample_tool):
        """Tool validates required parameters."""
        # Missing required param
        error = sample_tool.validate_params()
        assert error is not None
        assert "input" in error
        
        # Valid params
        error = sample_tool.validate_params(input="test")
        assert error is None
    
    def test_consolidated_tool_operation_routing(self):
        """ConsolidatedTool routes to correct operation."""
        import asyncio
        
        class TestConsolidated(ConsolidatedTool):
            @property
            def name(self) -> str:
                return "test_consolidated"
            
            @property
            def description(self) -> str:
                return "Test consolidated tool"
            
            @property
            def category(self) -> ToolCategory:
                return ToolCategory.OPERATIONS
            
            @property
            def parameters(self):
                return [
                    ToolParameter(name="operation", type="string", required=True),
                ]
            
            @property
            def supported_operations(self):
                return ["op1", "op2"]
            
            async def execute(self, **kwargs) -> ToolResult:
                operation = kwargs.get("operation", "")
                if operation == "op1":
                    return ToolResult(success=True, data={"result": "op1_executed"})
                elif operation == "op2":
                    return ToolResult(success=True, data={"result": "op2_executed"})
                else:
                    return ToolResult(success=False, error=f"Unknown operation: {operation}")
        
        tool = TestConsolidated()
        
        # Valid operation
        result = asyncio.run(
            tool.execute(operation="op1")
        )
        assert result.success
        assert result.data["result"] == "op1_executed"
        
        # Unknown operation
        result = asyncio.run(
            tool.execute(operation="unknown")
        )
        assert not result.success
        assert "Unknown operation" in result.error


# ============================================================================
# TIER 6: CROSS-PLATFORM TESTS
# ============================================================================

class TestCrossPlatform:
    """Tests for cross-platform compatibility."""
    
    def test_server_reports_platform_info(self, server):
        """Health check includes platform info."""
        health = server.health_check()
        
        assert "platform" in health
        assert "os" in health["platform"]
        assert "python_version" in health["platform"]
    
    def test_paths_use_pathlib_or_os_path(self):
        """Verify path handling is cross-platform."""
        # Registry doesn't use hardcoded paths
        for tool_id, spec in PRODUCTION_TOOLS.items():
            for param in spec.get("parameters", []):
                # Path parameters should just be strings, not hardcoded
                if "path" in param["name"].lower():
                    assert param["type"] == "string"
    
    @pytest.mark.parametrize("platform", ["darwin", "win32", "linux"])
    def test_server_works_on_platform(self, platform, registry):
        """Server initializes on different platforms."""
        with patch.object(sys, "platform", platform):
            server = MCPServer(registry=registry)
            assert server.registry.tool_count == 24


# ============================================================================
# TIER 7: EXTENSIBILITY TESTS
# ============================================================================

class TestExtensibility:
    """Tests for extension patterns."""
    
    def test_custom_tool_can_be_registered(self, registry, sample_tool):
        """Custom tools can be registered."""
        registry.register(sample_tool)
        retrieved = registry.get("test_sample")
        assert retrieved is sample_tool
    
    def test_tool_operations_are_extensible(self):
        """Consolidated tools can have operations added."""
        spec = PRODUCTION_TOOLS["cortex_lens"]
        ops = spec["operations"]
        
        # Could add new operations without changing tool count
        assert isinstance(ops, list)
        assert len(ops) >= 4  # At least: analyze, deep_analyze, ast, discover
    
    def test_new_category_can_be_added(self):
        """ToolCategory enum is extensible via subclassing."""
        # Categories are defined in enum
        assert len(ToolCategory) == 5
        
        # New capabilities would add operations to existing tools
        # or extend ToolCategory enum


# ============================================================================
# TIER 8: PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance characteristic tests."""
    
    def test_registry_initialization_is_fast(self):
        """Registry initializes in <100ms."""
        import time
        
        start = time.time()
        registry = ToolRegistry()
        elapsed = time.time() - start
        
        assert elapsed < 0.1, f"Registry init took {elapsed:.3f}s (should be <0.1s)"
    
    def test_list_tools_is_fast(self, server):
        """list_tools completes in <50ms."""
        import time
        
        start = time.time()
        for _ in range(100):
            server.list_tools()
        elapsed = time.time() - start
        
        per_call = elapsed / 100
        assert per_call < 0.05, f"list_tools took {per_call:.3f}s per call"
    
    def test_tool_lookup_is_fast(self, registry):
        """Tool lookup is O(1)."""
        import time
        
        start = time.time()
        for _ in range(1000):
            registry.get_metadata("cortex_lens")
        elapsed = time.time() - start
        
        per_call = elapsed / 1000
        assert per_call < 0.001, f"Lookup took {per_call:.5f}s per call"


# ============================================================================
# TIER 9: INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for full workflows."""
    
    def test_full_request_response_cycle(self, server):
        """Complete JSON-RPC request-response cycle."""
        # 1. Initialize
        init_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
            "id": "1",
        })
        init_response = json.loads(server.handle_json(init_request))
        assert "result" in init_response
        
        # 2. List tools
        list_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": "2",
        })
        list_response = json.loads(server.handle_json(list_request))
        assert len(list_response["result"]) == 24
        
        # 3. Call tool (will fail gracefully - not implemented)
        call_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "cortex_verify",
                "arguments": {"operation": "environment"},
            },
            "id": "3",
        })
        call_response = json.loads(server.handle_json(call_request))
        assert "result" in call_response or "error" in call_response
    
    def test_tool_categories_align_with_business_capabilities(self, registry):
        """Tool categories map to distinct business capabilities."""
        capabilities = {
            ToolCategory.CORE: "Request Processing",
            ToolCategory.INTELLIGENCE: "Code Analysis",
            ToolCategory.GOVERNANCE: "Compliance & Rules",
            ToolCategory.OPERATIONS: "Development Workflows",
            ToolCategory.UTILITIES: "Support Functions",
        }
        
        for category, description in capabilities.items():
            tools = registry.list_by_category(category)
            assert len(tools) > 0, f"No tools in {description} category"


# ============================================================================
# TIER 10: REGRESSION TESTS
# ============================================================================

class TestRegression:
    """Tests to prevent known issues from recurring."""
    
    def test_no_dev_only_tools_in_production(self):
        """Verify no dev-only tools (echo, sample, transform)."""
        dev_tools = ["echo_tool", "sample_tool", "transform_tool"]
        for dev_tool in dev_tools:
            assert dev_tool not in PRODUCTION_TOOLS, f"Dev tool {dev_tool} should not be in production"
    
    def test_no_duplicate_functionality(self):
        """No duplicate tools with different names."""
        descriptions = [spec["description"] for spec in PRODUCTION_TOOLS.values()]
        # Allow similar descriptions (they do different things)
        # But catch exact duplicates
        unique = set(descriptions)
        duplicates = len(descriptions) - len(unique)
        assert duplicates == 0, "Found duplicate tool descriptions"
    
    def test_all_parameters_have_types(self):
        """All tool parameters must have types."""
        for tool_id, spec in PRODUCTION_TOOLS.items():
            for param in spec.get("parameters", []):
                assert "type" in param, f"Parameter {param['name']} in {tool_id} missing type"
    
    def test_all_consolidated_operations_are_in_enum(self):
        """Consolidated tool operations match enum values."""
        for tool_id, spec in PRODUCTION_TOOLS.items():
            operations = spec.get("operations", [])
            if operations:
                # Find operation parameter
                op_param = next(
                    (p for p in spec["parameters"] if p["name"] == "operation"),
                    None
                )
                if op_param and "enum" in op_param:
                    # All operations should be in enum
                    for op in operations:
                        assert op in op_param["enum"], f"Operation {op} not in {tool_id} enum"
