"""
AC-MCP-007-01: Enhanced Tool Discovery Tests

Tests for comprehensive tool discovery with:
- Tool categories
- Parameter validation hints
- Usage examples
- Version information

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import pytest
import json
from typing import Dict, Any, List
from src.mcp.decorator import mcp_tool, get_registered_tools, clear_tools


class TestToolCategoryDiscovery:
    """Test tool discovery with categories."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_tools_grouped_by_category(self) -> None:
        """Test that tools can be grouped by category."""
        @mcp_tool(category="orchestrator")
        def tool1() -> None:
            """Tool 1."""
            pass
        
        @mcp_tool(category="orchestrator")
        def tool2() -> None:
            """Tool 2."""
            pass
        
        @mcp_tool(category="validator")
        def tool3() -> None:
            """Tool 3."""
            pass
        
        tools = get_registered_tools()
        
        orchestrator_tools = [t for t in tools.values() if t.category == "orchestrator"]
        validator_tools = [t for t in tools.values() if t.category == "validator"]
        
        assert len(orchestrator_tools) == 2
        assert len(validator_tools) == 1
    
    def test_category_discovery_from_tool_list(self) -> None:
        """Test that categories are discoverable from tools/list."""
        @mcp_tool(category="orchestrator")
        def tool1() -> None:
            """Tool 1."""
            pass
        
        tools = get_registered_tools()
        
        # Extract all categories
        categories = {t.category for t in tools.values()}
        assert "orchestrator" in categories


class TestParameterDiscovery:
    """Test parameter discovery and validation hints."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_parameters_discoverable(self) -> None:
        """Test that tool parameters are discoverable."""
        @mcp_tool()
        def tool(param1: str, param2: int, param3: bool) -> None:
            """Tool with parameters."""
            pass
        
        tools = get_registered_tools()
        schema = tools["tool"].parameters
        
        assert "param1" in schema["properties"]
        assert "param2" in schema["properties"]
        assert "param3" in schema["properties"]
    
    def test_parameter_types_discoverable(self) -> None:
        """Test that parameter types are discoverable."""
        @mcp_tool()
        def tool(
            name: str,
            count: int,
            enabled: bool,
            options: dict,
            items: list
        ) -> None:
            """Tool with typed parameters."""
            pass
        
        tools = get_registered_tools()
        props = tools["tool"].parameters["properties"]
        
        assert props["name"]["type"] == "string"
        assert props["count"]["type"] == "integer"
        assert props["enabled"]["type"] == "boolean"
        assert props["options"]["type"] == "object"
        assert props["items"]["type"] == "array"
    
    def test_required_parameters_discoverable(self) -> None:
        """Test that required parameters are discoverable."""
        @mcp_tool()
        def tool(required_param: str, optional_param: str = "default") -> None:
            """Tool with required and optional parameters."""
            pass
        
        tools = get_registered_tools()
        schema = tools["tool"].parameters
        
        assert "required_param" in schema["required"]
        assert "optional_param" not in schema["required"]


class TestVersionInformation:
    """Test version information discovery."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_tool_version_discoverable(self) -> None:
        """Test that tool version is discoverable."""
        @mcp_tool(version="1.0.0")
        def tool1() -> None:
            """Tool 1."""
            pass
        
        @mcp_tool(version="2.1.0")
        def tool2() -> None:
            """Tool 2."""
            pass
        
        tools = get_registered_tools()
        assert tools["tool1"].version == "1.0.0"
        assert tools["tool2"].version == "2.1.0"
    
    def test_default_version(self) -> None:
        """Test that tools have default version."""
        @mcp_tool()
        def tool() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["tool"].version == "1.0.0"
    
    def test_version_in_metadata(self) -> None:
        """Test that version is included in metadata."""
        @mcp_tool(version="3.2.1")
        def tool() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        metadata = tools["tool"]
        assert metadata.version == "3.2.1"


class TestDescriptionDiscovery:
    """Test description discovery for tools."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_tool_description_from_docstring(self) -> None:
        """Test that tool description comes from docstring."""
        @mcp_tool()
        def tool() -> None:
            """This is a tool description."""
            pass
        
        tools = get_registered_tools()
        assert "This is a tool description" in tools["tool"].description
    
    def test_descriptions_are_strings(self) -> None:
        """Test that descriptions are strings."""
        @mcp_tool()
        def tool1() -> None:
            """Description 1."""
            pass
        
        @mcp_tool()
        def tool2() -> None:
            """Description 2."""
            pass
        
        tools = get_registered_tools()
        for name, tool in tools.items():
            assert isinstance(tool.description, str)
            assert len(tool.description) > 0


class TestEnhancedDiscoveryEndpoint:
    """Test enhanced discovery endpoint capabilities."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_discovery_data_structure(self) -> None:
        """Test that discovery returns structured data."""
        @mcp_tool(category="test", version="1.0.0")
        def tool(param: str) -> None:
            """Test tool description."""
            pass
        
        tools = get_registered_tools()
        tool_data = tools["tool"]
        
        # Check structure
        assert hasattr(tool_data, "name")
        assert hasattr(tool_data, "description")
        assert hasattr(tool_data, "category")
        assert hasattr(tool_data, "version")
        assert hasattr(tool_data, "parameters")
    
    def test_discovery_json_serializable(self) -> None:
        """Test that discovery data is JSON serializable."""
        @mcp_tool(category="test")
        def tool(param: str) -> None:
            """Tool description."""
            pass
        
        tools = get_registered_tools()
        metadata = tools["tool"]
        
        # Create JSON-serializable representation
        discovery_data = {
            "name": metadata.name,
            "description": metadata.description,
            "category": metadata.category,
            "version": metadata.version,
            "parameters": metadata.parameters
        }
        
        json_str = json.dumps(discovery_data)
        assert json_str is not None
        
        # Deserialize to verify
        recovered = json.loads(json_str)
        assert recovered["name"] == "tool"


class TestMultiAttributeDiscovery:
    """Test discovery of multiple tool attributes."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_full_tool_discovery(self) -> None:
        """Test complete tool discovery with all attributes."""
        @mcp_tool(category="orchestrator", version="2.0.0")
        def scaffold_orchestrator(template: str, name: str) -> None:
            """Generate a new orchestrator from template."""
            pass
        
        tools = get_registered_tools()
        tool = tools["scaffold_orchestrator"]
        
        # All attributes discoverable
        assert tool.name == "scaffold_orchestrator"
        assert "orchestrator" in tool.description.lower()
        assert tool.category == "orchestrator"
        assert tool.version == "2.0.0"
        assert "template" in tool.parameters["properties"]
        assert "name" in tool.parameters["properties"]
        assert "template" in tool.parameters["required"]
        assert "name" in tool.parameters["required"]


class TestDiscoveryOrganization:
    """Test discovery organization and filtering."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_filter_by_category(self) -> None:
        """Test filtering tools by category."""
        @mcp_tool(category="orchestrator")
        def tool1() -> None:
            """Tool 1."""
            pass
        
        @mcp_tool(category="validator")
        def tool2() -> None:
            """Tool 2."""
            pass
        
        @mcp_tool(category="orchestrator")
        def tool3() -> None:
            """Tool 3."""
            pass
        
        tools = get_registered_tools()
        
        # Manual filtering
        orchestrator_tools = {
            name: tool for name, tool in tools.items()
            if tool.category == "orchestrator"
        }
        
        assert len(orchestrator_tools) == 2
    
    def test_filter_by_required_params(self) -> None:
        """Test filtering tools by required parameters."""
        @mcp_tool()
        def tool1(required: str) -> None:
            """Tool 1."""
            pass
        
        @mcp_tool()
        def tool2(optional: str = "default") -> None:
            """Tool 2."""
            pass
        
        tools = get_registered_tools()
        
        # Tools with required parameters
        tools_with_required = {
            name: tool for name, tool in tools.items()
            if len(tool.parameters.get("required", [])) > 0
        }
        
        assert len(tools_with_required) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
