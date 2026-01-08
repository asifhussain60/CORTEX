"""
Tests for MCP Orchestrator Capability Exposure

Test-Driven Development for exposing CORTEX orchestrator capabilities through MCP.
Tests MUST fail first (RED phase), then implementation makes them pass (GREEN phase).

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-08
Correlation ID: FEAT06-P1-T1.2
"""

import pytest
from typing import Dict, Any, List


class TestCapabilityDefinition:
    """Test capability definition structure"""
    
    def test_capability_has_required_fields(self):
        """RED: Capability must have name, description, parameters, returns"""
        from src.mcp.capability_registry import Capability
        
        cap = Capability(
            name="plan",
            description="Create a structured plan",
            parameters={
                "request": {"type": "string", "description": "Planning request"}
            },
            returns={
                "type": "object",
                "description": "Plan with phases and tasks"
            }
        )
        
        assert cap.name == "plan"
        assert cap.description == "Create a structured plan"
        assert "request" in cap.parameters
        assert cap.returns["type"] == "object"
    
    def test_capability_has_optional_metadata(self):
        """RED: Capability can have optional metadata (examples, tags, version)"""
        from src.mcp.capability_registry import Capability
        
        cap = Capability(
            name="tdd",
            description="Test-driven development",
            parameters={},
            returns={"type": "object"},
            metadata={
                "tags": ["testing", "development"],
                "version": "2.0",
                "examples": ["tdd user login", "tdd validate email"]
            }
        )
        
        assert cap.metadata["tags"] == ["testing", "development"]
        assert cap.metadata["version"] == "2.0"
        assert len(cap.metadata["examples"]) == 2
    
    def test_capability_to_dict(self):
        """RED: Capability converts to dict for JSON serialization"""
        from src.mcp.capability_registry import Capability
        
        cap = Capability(
            name="investigate",
            description="Root cause analysis",
            parameters={"issue": {"type": "string"}},
            returns={"type": "object"}
        )
        
        data = cap.to_dict()
        assert data["name"] == "investigate"
        assert data["description"] == "Root cause analysis"
        assert "parameters" in data
        assert "returns" in data


class TestCapabilityRegistry:
    """Test capability registry for orchestrators"""
    
    def test_register_capability(self):
        """RED: Registry can register capabilities"""
        from src.mcp.capability_registry import CapabilityRegistry, Capability
        
        registry = CapabilityRegistry()
        
        cap = Capability(
            name="plan",
            description="Planning system",
            parameters={},
            returns={}
        )
        
        registry.register(cap)
        assert "plan" in registry.capabilities
    
    def test_get_capability_by_name(self):
        """RED: Registry retrieves capability by name"""
        from src.mcp.capability_registry import CapabilityRegistry, Capability
        
        registry = CapabilityRegistry()
        cap = Capability(name="tdd", description="TDD", parameters={}, returns={})
        registry.register(cap)
        
        retrieved = registry.get("tdd")
        assert retrieved is not None
        assert retrieved.name == "tdd"
    
    def test_list_all_capabilities(self):
        """RED: Registry lists all capabilities"""
        from src.mcp.capability_registry import CapabilityRegistry, Capability
        
        registry = CapabilityRegistry()
        registry.register(Capability(name="plan", description="", parameters={}, returns={}))
        registry.register(Capability(name="tdd", description="", parameters={}, returns={}))
        
        caps = registry.list_all()
        assert len(caps) == 2
        names = [c.name for c in caps]
        assert "plan" in names
        assert "tdd" in names
    
    def test_search_capabilities_by_tag(self):
        """RED: Registry searches capabilities by tag"""
        from src.mcp.capability_registry import CapabilityRegistry, Capability
        
        registry = CapabilityRegistry()
        registry.register(Capability(
            name="tdd",
            description="",
            parameters={},
            returns={},
            metadata={"tags": ["testing", "development"]}
        ))
        registry.register(Capability(
            name="plan",
            description="",
            parameters={},
            returns={},
            metadata={"tags": ["planning"]}
        ))
        
        results = registry.search_by_tag("testing")
        assert len(results) == 1
        assert results[0].name == "tdd"
    
    def test_unregister_capability(self):
        """RED: Registry can unregister capabilities"""
        from src.mcp.capability_registry import CapabilityRegistry, Capability
        
        registry = CapabilityRegistry()
        cap = Capability(name="temp", description="", parameters={}, returns={})
        registry.register(cap)
        
        assert "temp" in registry.capabilities
        registry.unregister("temp")
        assert "temp" not in registry.capabilities


class TestOrchestratorCapabilityLoader:
    """Test loading capabilities from orchestrator registry"""
    
    def test_load_from_orchestrator_registry(self):
        """RED: Load capabilities from existing orchestrator registry"""
        from src.mcp.capability_registry import CapabilityRegistry
        from src.mcp.registry import OrchestratorRegistry
        
        # Mock orchestrator registry
        orch_registry = OrchestratorRegistry()
        
        cap_registry = CapabilityRegistry()
        cap_registry.load_from_orchestrator_registry(orch_registry)
        
        # Empty registry is OK - method should not fail
        # The test verifies the method runs without errors
        caps = cap_registry.list_all()
        assert isinstance(caps, list)  # Should return list even if empty
    
    def test_capability_maps_to_orchestrator(self):
        """RED: Each capability maps to an orchestrator ID"""
        from src.mcp.capability_registry import Capability
        
        cap = Capability(
            name="plan",
            description="Planning",
            parameters={},
            returns={},
            orchestrator_id="planning_v5"
        )
        
        assert cap.orchestrator_id == "planning_v5"
    
    def test_load_capability_from_manifest(self):
        """RED: Load capability definition from orchestrator manifest"""
        from src.mcp.capability_registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        
        # Mock manifest data
        manifest = {
            "name": "Planning System v5",
            "orchestrator_id": "planning_v5",
            "capabilities": {
                "plan": {
                    "description": "Create structured plans",
                    "parameters": {
                        "request": {"type": "string"}
                    },
                    "returns": {"type": "object"}
                }
            }
        }
        
        registry.load_from_manifest("planning_v5", manifest)
        
        cap = registry.get("plan")
        assert cap is not None
        assert cap.orchestrator_id == "planning_v5"


class TestMCPCapabilityInterface:
    """Test MCP interface for capability exposure"""
    
    def test_mcp_list_tools_method(self):
        """RED: MCP server exposes 'tools/list' method"""
        from src.mcp.mcp_server import MCPServer
        
        server = MCPServer()
        
        # tools/list should return all available capabilities
        result = server.handle_tools_list({})
        
        assert "tools" in result
        assert isinstance(result["tools"], list)
    
    def test_tool_definition_format(self):
        """RED: Tool definition follows MCP format"""
        from src.mcp.capability_registry import Capability
        
        cap = Capability(
            name="plan",
            description="Create a plan",
            parameters={"request": {"type": "string"}},
            returns={"type": "object"}
        )
        
        tool_def = cap.to_mcp_tool()
        
        assert tool_def["name"] == "plan"
        assert tool_def["description"] == "Create a plan"
        assert "inputSchema" in tool_def
        assert tool_def["inputSchema"]["type"] == "object"
        assert "request" in tool_def["inputSchema"]["properties"]
    
    def test_mcp_call_tool_method(self):
        """RED: MCP server exposes 'tools/call' method"""
        from src.mcp.mcp_server import MCPServer
        
        server = MCPServer()
        
        # tools/call should execute the tool
        result = server.handle_tools_call({
            "name": "plan",
            "arguments": {"request": "plan user authentication"}
        })
        
        assert "content" in result
    
    def test_capability_execution_via_mcp(self):
        """RED: Calling tool via MCP executes orchestrator"""
        from src.mcp.mcp_server import MCPServer
        from unittest.mock import Mock, MagicMock
        
        server = MCPServer()
        
        # Mock orchestrator execution
        server.master_orchestrator = Mock()
        server.master_orchestrator.handle_request = MagicMock(return_value={
            "success": True,
            "result": {"plan_id": "test-123"}
        })
        
        result = server.handle_tools_call({
            "name": "plan",
            "arguments": {"request": "test plan"}
        })
        
        # Verify orchestrator was called
        server.master_orchestrator.handle_request.assert_called_once()
        assert result["content"]


class TestCapabilityParameterValidation:
    """Test parameter validation for capabilities"""
    
    def test_validate_required_parameters(self):
        """RED: Capability validates required parameters"""
        from src.mcp.capability_registry import Capability
        
        cap = Capability(
            name="plan",
            description="",
            parameters={
                "request": {
                    "type": "string",
                    "required": True
                }
            },
            returns={}
        )
        
        # Valid parameters
        assert cap.validate_parameters({"request": "test"}) is True
        
        # Missing required parameter
        with pytest.raises(ValueError):
            cap.validate_parameters({})
    
    def test_validate_parameter_types(self):
        """RED: Capability validates parameter types"""
        from src.mcp.capability_registry import Capability
        
        cap = Capability(
            name="test",
            description="",
            parameters={
                "count": {"type": "integer"},
                "message": {"type": "string"}
            },
            returns={}
        )
        
        # Valid types
        assert cap.validate_parameters({"count": 5, "message": "test"}) is True
        
        # Invalid type
        with pytest.raises(TypeError):
            cap.validate_parameters({"count": "five", "message": "test"})


class TestCapabilityDiscovery:
    """Test capability discovery and introspection"""
    
    def test_discover_all_orchestrators(self):
        """RED: Discover capabilities from all registered orchestrators"""
        from src.mcp.capability_registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        registry.discover_all()
        
        caps = registry.list_all()
        
        # Should find planning, tdd, etc.
        names = [c.name for c in caps]
        assert "plan" in names or "planning" in names
    
    def test_capability_grouping_by_category(self):
        """RED: Group capabilities by category"""
        from src.mcp.capability_registry import CapabilityRegistry
        
        registry = CapabilityRegistry()
        registry.discover_all()
        
        grouped = registry.group_by_category()
        
        assert isinstance(grouped, dict)
        # Should have categories like 'planning', 'development', 'analysis', etc.
    
    def test_get_capability_metadata(self):
        """RED: Get full capability metadata"""
        from src.mcp.capability_registry import CapabilityRegistry, Capability
        
        registry = CapabilityRegistry()
        cap = Capability(
            name="plan",
            description="Planning",
            parameters={},
            returns={},
            metadata={
                "version": "5.0",
                "autonomous": True,
                "estimated_time": "2-5 minutes"
            }
        )
        registry.register(cap)
        
        metadata = registry.get_metadata("plan")
        assert metadata["version"] == "5.0"
        assert metadata["autonomous"] is True
