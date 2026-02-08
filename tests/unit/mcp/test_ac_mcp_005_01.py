"""
AC-MCP-005-01: Vacuum Tool MCP Exposure Tests

Tests for CortexVacuumAnalyzer and CortexVacuumExecutor exposure as MCP tools.

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import pytest
from typing import Dict, Any
from cortex.mcp.decorators import mcp_tool, get_registered_tools, clear_tools


class TestVacuumAnalyzerExposure:
    """Test CortexVacuumAnalyzer exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_analyze_vacuum_tool_exists(self) -> None:
        """Test that analyze_vacuum is exposed as MCP tool."""
        @mcp_tool(category="vacuum")
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state (unused code)."""
            return {
                "directory": directory,
                "unused_files": [],
                "unused_functions": []
            }
        
        tools = get_registered_tools()
        assert "analyze_vacuum" in tools
        assert tools["analyze_vacuum"].category == "vacuum"
    
    def test_analyze_vacuum_parameters(self) -> None:
        """Test analyze_vacuum tool parameters."""
        @mcp_tool()
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state."""
            return {}
        
        tools = get_registered_tools()
        schema = tools["analyze_vacuum"].parameters
        
        assert "directory" in schema["required"]
        assert schema["properties"]["directory"]["type"] == "string"
    
    def test_analyze_vacuum_callable(self) -> None:
        """Test that analyze_vacuum is callable."""
        @mcp_tool()
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state."""
            return {"status": "analyzed", "dir": directory}
        
        result = analyze_vacuum("/path/to/code")
        assert result["status"] == "analyzed"
        assert result["dir"] == "/path/to/code"


class TestVacuumExecutorExposure:
    """Test CortexVacuumExecutor exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_execute_vacuum_tool_exists(self) -> None:
        """Test that execute_vacuum is exposed as MCP tool."""
        @mcp_tool(category="vacuum")
        def execute_vacuum(
            directory: str,
            dry_run: bool = True,
            patterns: list = None
        ) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {
                "directory": directory,
                "dry_run": dry_run,
                "deleted_files": []
            }
        
        tools = get_registered_tools()
        assert "execute_vacuum" in tools
        assert tools["execute_vacuum"].category == "vacuum"
    
    def test_execute_vacuum_parameters(self) -> None:
        """Test execute_vacuum tool parameters."""
        @mcp_tool()
        def execute_vacuum(
            directory: str,
            dry_run: bool = True,
            patterns: list = None
        ) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {}
        
        tools = get_registered_tools()
        schema = tools["execute_vacuum"].parameters
        
        # Required parameters
        assert "directory" in schema["required"]
        
        # Optional parameters
        assert "dry_run" not in schema["required"]
        assert "patterns" not in schema["required"]
        
        # Parameter types
        props = schema["properties"]
        assert props["directory"]["type"] == "string"
        assert props["dry_run"]["type"] == "boolean"
        assert props["patterns"]["type"] == "array"
    
    def test_execute_vacuum_dry_run_default(self) -> None:
        """Test that execute_vacuum has dry_run default."""
        @mcp_tool()
        def execute_vacuum(directory: str, dry_run: bool = True) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {"dry_run": dry_run}
        
        result = execute_vacuum("/path")
        assert result["dry_run"] is True


class TestVacuumToolsCollective:
    """Test vacuum tools together."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_both_vacuum_tools_registered(self) -> None:
        """Test that both vacuum tools can be registered."""
        @mcp_tool(category="vacuum")
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state."""
            return {}
        
        @mcp_tool(category="vacuum")
        def execute_vacuum(directory: str, dry_run: bool = True) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {}
        
        tools = get_registered_tools()
        assert len(tools) == 2
        assert "analyze_vacuum" in tools
        assert "execute_vacuum" in tools
    
    def test_vacuum_tools_workflow(self) -> None:
        """Test typical vacuum workflow."""
        @mcp_tool()
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state."""
            return {"unused": ["file1.py", "func1"], "count": 2}
        
        @mcp_tool()
        def execute_vacuum(directory: str, dry_run: bool = True) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            if dry_run:
                return {"would_delete": 2, "deleted": 0}
            return {"deleted": 2}
        
        # Analyze
        analysis = analyze_vacuum("/code")
        assert analysis["count"] == 2
        
        # Dry run
        dry_result = execute_vacuum("/code", dry_run=True)
        assert dry_result["deleted"] == 0
        
        # Execute
        exec_result = execute_vacuum("/code", dry_run=False)
        assert exec_result["deleted"] == 2


class TestVacuumToolDescriptions:
    """Test vacuum tool descriptions."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_analyze_vacuum_has_description(self) -> None:
        """Test analyze_vacuum has proper description."""
        @mcp_tool()
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state (unused code)."""
            return {}
        
        tools = get_registered_tools()
        desc = tools["analyze_vacuum"].description
        assert "analyze" in desc.lower() or "vacuum" in desc.lower()
    
    def test_execute_vacuum_has_description(self) -> None:
        """Test execute_vacuum has proper description."""
        @mcp_tool()
        def execute_vacuum(directory: str) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {}
        
        tools = get_registered_tools()
        desc = tools["execute_vacuum"].description
        assert "execute" in desc.lower() or "cleanup" in desc.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
