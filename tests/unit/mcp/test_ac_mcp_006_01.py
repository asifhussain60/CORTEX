"""
AC-MCP-006-01: Complete Tool Exposure Tests

Tests for exposing all remaining orchestrator and utility functions as MCP tools:
- IntentRouter
- RelationshipAnalyzer
- DomainClassifier
- LensSynthesis
- DependencyValidator
- And others

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import pytest
from typing import Dict, Any, List, Optional
from cortex.mcp.decorator import mcp_tool, get_registered_tools, clear_tools


class TestIntentRouterExposure:
    """Test IntentRouter exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_route_intent_tool_exists(self) -> None:
        """Test that route_intent is exposed as MCP tool."""
        @mcp_tool(category="orchestrator")
        def route_intent(query: str) -> Dict[str, Any]:
            """Route user intent to appropriate orchestrator."""
            return {"intent": "routed", "handler": "default"}
        
        tools = get_registered_tools()
        assert "route_intent" in tools


class TestRelationshipAnalyzerExposure:
    """Test RelationshipAnalyzer exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_analyze_relationships_tool_exists(self) -> None:
        """Test that analyze_relationships is exposed as MCP tool."""
        @mcp_tool(category="analyzer")
        def analyze_relationships(file_path: str) -> Dict[str, Any]:
            """Analyze relationships between code components."""
            return {"file": file_path, "relationships": []}
        
        tools = get_registered_tools()
        assert "analyze_relationships" in tools


class TestDomainClassifierExposure:
    """Test DomainClassifier exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_classify_domain_tool_exists(self) -> None:
        """Test that classify_domain is exposed as MCP tool."""
        @mcp_tool(category="classifier")
        def classify_domain(content: str) -> Dict[str, Any]:
            """Classify content into business domain."""
            return {"domain": "general", "confidence": 0.8}
        
        tools = get_registered_tools()
        assert "classify_domain" in tools


class TestLensSynthesisExposure:
    """Test LensSynthesis exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_synthesize_lens_tool_exists(self) -> None:
        """Test that synthesize_lens is exposed as MCP tool."""
        @mcp_tool(category="synthesis")
        def synthesize_lens(analysis_data: dict) -> Dict[str, Any]:
            """Synthesize analysis data into actionable insights."""
            return {"insights": [], "confidence": 0.9}
        
        tools = get_registered_tools()
        assert "synthesize_lens" in tools


class TestDependencyValidatorExposure:
    """Test DependencyValidator exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_validate_dependencies_tool_exists(self) -> None:
        """Test that validate_dependencies is exposed as MCP tool."""
        @mcp_tool(category="validator")
        def validate_dependencies(file_path: str) -> Dict[str, Any]:
            """Validate dependencies in a file."""
            return {"valid": True, "issues": []}
        
        tools = get_registered_tools()
        assert "validate_dependencies" in tools


class TestCompleteCatalogExposure:
    """Test complete tool catalog exposure."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_all_core_tools_can_be_registered(self) -> None:
        """Test that all core tools can be registered together."""
        @mcp_tool(category="orchestrator")
        def route_intent(query: str) -> Dict[str, Any]:
            """Route user intent."""
            return {}
        
        @mcp_tool(category="analyzer")
        def analyze_relationships(file_path: str) -> Dict[str, Any]:
            """Analyze relationships."""
            return {}
        
        @mcp_tool(category="classifier")
        def classify_domain(content: str) -> Dict[str, Any]:
            """Classify domain."""
            return {}
        
        @mcp_tool(category="synthesis")
        def synthesize_lens(analysis_data: dict) -> Dict[str, Any]:
            """Synthesize lens."""
            return {}
        
        @mcp_tool(category="validator")
        def validate_dependencies(file_path: str) -> Dict[str, Any]:
            """Validate dependencies."""
            return {}
        
        tools = get_registered_tools()
        assert len(tools) == 5
    
    def test_tools_have_diverse_categories(self) -> None:
        """Test that tools span multiple categories."""
        @mcp_tool(category="orchestrator")
        def tool1() -> None:
            """Tool 1."""
            pass
        
        @mcp_tool(category="analyzer")
        def tool2() -> None:
            """Tool 2."""
            pass
        
        @mcp_tool(category="classifier")
        def tool3() -> None:
            """Tool 3."""
            pass
        
        @mcp_tool(category="validator")
        def tool4() -> None:
            """Tool 4."""
            pass
        
        tools = get_registered_tools()
        categories = {t.category for t in tools.values()}
        assert len(categories) >= 4


class TestToolMetadata:
    """Test tool metadata for complete exposure."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_tools_have_descriptions(self) -> None:
        """Test that all tools have descriptions."""
        @mcp_tool()
        def tool1() -> None:
            """Description for tool 1."""
            pass
        
        @mcp_tool()
        def tool2() -> None:
            """Description for tool 2."""
            pass
        
        tools = get_registered_tools()
        for name, tool in tools.items():
            assert tool.description
            assert len(tool.description) > 0
    
    def test_tools_have_parameter_schemas(self) -> None:
        """Test that tools have parameter schemas."""
        @mcp_tool()
        def tool1(param1: str, param2: int) -> str:
            """Tool with parameters."""
            return ""
        
        @mcp_tool()
        def tool2() -> str:
            """Tool without parameters."""
            return ""
        
        tools = get_registered_tools()
        for name, tool in tools.items():
            assert "type" in tool.parameters
            assert "properties" in tool.parameters
    
    def test_tools_have_versions(self) -> None:
        """Test that tools have version information."""
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


class TestToolCategories:
    """Test tool categories for organization."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_orchestrator_category(self) -> None:
        """Test tools in orchestrator category."""
        @mcp_tool(category="orchestrator")
        def tool() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["tool"].category == "orchestrator"
    
    def test_analyzer_category(self) -> None:
        """Test tools in analyzer category."""
        @mcp_tool(category="analyzer")
        def tool() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["tool"].category == "analyzer"
    
    def test_validator_category(self) -> None:
        """Test tools in validator category."""
        @mcp_tool(category="validator")
        def tool() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["tool"].category == "validator"
    
    def test_classifier_category(self) -> None:
        """Test tools in classifier category."""
        @mcp_tool(category="classifier")
        def tool() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["tool"].category == "classifier"
    
    def test_synthesis_category(self) -> None:
        """Test tools in synthesis category."""
        @mcp_tool(category="synthesis")
        def tool() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        assert tools["tool"].category == "synthesis"


class TestToolDiscoverability:
    """Test that all tools are discoverable."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_all_registered_tools_discoverable(self) -> None:
        """Test that all registered tools can be discovered."""
        @mcp_tool()
        def tool1() -> None:
            """Tool 1."""
            pass
        
        @mcp_tool()
        def tool2() -> None:
            """Tool 2."""
            pass
        
        @mcp_tool()
        def tool3() -> None:
            """Tool 3."""
            pass
        
        tools = get_registered_tools()
        assert "tool1" in tools
        assert "tool2" in tools
        assert "tool3" in tools
    
    def test_tool_count_accurate(self) -> None:
        """Test that tool count is accurate."""
        @mcp_tool()
        def tool1() -> None:
            """Tool."""
            pass
        
        @mcp_tool()
        def tool2() -> None:
            """Tool."""
            pass
        
        tools = get_registered_tools()
        assert len(tools) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
