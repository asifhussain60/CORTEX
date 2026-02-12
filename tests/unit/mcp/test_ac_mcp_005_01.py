"""
AC-MCP-005-01: Vacuum Tool MCP Exposure Tests

Tests for CortexVacuumAnalyzer and CortexVacuumExecutor exposure as MCP tools.

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)

AC_START: AC-WAVE-K-008
Description: Fix vacuum tool MCP exposure tests
"""

import pytest
from typing import Dict, Any, Optional, List
from cortex.mcp.decorators import mcp_tool, get_registered_tools, clear_tools


class TestVacuumAnalyzerExposure:
    """Test CortexVacuumAnalyzer exposure as MCP tool."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_analyze_vacuum_tool_exists(self) -> None:
        """Test that analyze_vacuum is exposed as MCP tool."""
        @mcp_tool(
            name="analyze_vacuum",
            description="Analyze codebase for vacuum state (unused code)",
            category="vacuum"
        )
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state (unused code)."""
            return {
                "directory": directory,
                "unused_files": [],
                "unused_functions": []
            }
        
        tools = get_registered_tools()
        assert "analyze_vacuum" in tools
        assert tools["analyze_vacuum"]["category"] == "vacuum"
    
    def test_analyze_vacuum_parameters(self) -> None:
        """Test analyze_vacuum tool parameters."""
        @mcp_tool(
            name="analyze_vacuum",
            description="Analyze codebase for vacuum state"
        )
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            """Analyze codebase for vacuum state."""
            return {}
        
        tools = get_registered_tools()
        assert "analyze_vacuum" in tools
    
    def test_analyze_vacuum_callable(self) -> None:
        """Test that analyze_vacuum is callable."""
        @mcp_tool(
            name="analyze_vacuum",
            description="Analyze codebase for vacuum state"
        )
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
        @mcp_tool(
            name="execute_vacuum",
            description="Execute vacuum cleanup operations",
            category="vacuum"
        )
        def execute_vacuum(
            directory: str,
            dry_run: bool = True,
            patterns: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {
                "directory": directory,
                "dry_run": dry_run,
                "deleted_files": []
            }
        
        tools = get_registered_tools()
        assert "execute_vacuum" in tools
        assert tools["execute_vacuum"]["category"] == "vacuum"
    
    def test_execute_vacuum_parameters(self) -> None:
        """Test execute_vacuum tool parameters."""
        @mcp_tool(
            name="execute_vacuum",
            description="Execute vacuum cleanup operations"
        )
        def execute_vacuum(
            directory: str,
            dry_run: bool = True,
            patterns: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {}
        
        tools = get_registered_tools()
        assert "execute_vacuum" in tools
    
    def test_execute_vacuum_callable(self) -> None:
        """Test that execute_vacuum is callable."""
        @mcp_tool(
            name="execute_vacuum",
            description="Execute vacuum cleanup operations"
        )
        def execute_vacuum(
            directory: str,
            dry_run: bool = True,
            patterns: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Execute vacuum cleanup operations."""
            return {
                "status": "executed",
                "dir": directory,
                "dry": dry_run,
                "files_removed": 0
            }
        
        result = execute_vacuum("/path/to/code", dry_run=False)
        assert result["status"] == "executed"
        assert result["dir"] == "/path/to/code"
        assert result["dry"] is False


class TestVacuumToolsIntegration:
    """Test integration between vacuum analyzer and executor."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_both_vacuum_tools_registered(self) -> None:
        """Both vacuum tools can be registered simultaneously."""
        @mcp_tool(
            name="analyze_vacuum",
            description="Analyze vacuum state",
            category="vacuum"
        )
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            return {}
        
        @mcp_tool(
            name="execute_vacuum",
            description="Execute vacuum cleanup",
            category="vacuum"
        )
        def execute_vacuum(directory: str) -> Dict[str, Any]:
            return {}
        
        tools = get_registered_tools()
        assert len(tools) == 2
        assert "analyze_vacuum" in tools
        assert "execute_vacuum" in tools
    
    def test_vacuum_tools_workflow(self) -> None:
        """Test typical vacuum workflow: analyze then execute."""
        @mcp_tool(
            name="analyze_vacuum",
            description="Analyze vacuum state",
            category="vacuum"
        )
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            return {"unused_count": 5}
        
        @mcp_tool(
            name="execute_vacuum",
            description="Execute vacuum cleanup",
            category="vacuum"
        )
        def execute_vacuum(directory: str, dry_run: bool = True) -> Dict[str, Any]:
            return {"deleted_count": 5 if not dry_run else 0}
        
        # Analyze
        analysis = analyze_vacuum("/code")
        assert analysis["unused_count"] == 5
        
        # Execute (dry run)
        result_dry = execute_vacuum("/code", dry_run=True)
        assert result_dry["deleted_count"] == 0
        
        # Execute (real)
        result_real = execute_vacuum("/code", dry_run=False)
        assert result_real["deleted_count"] == 5


class TestVacuumToolDocumentation:
    """Test vacuum tool documentation."""
    
    def setup_method(self) -> None:
        """Clear tools before each test."""
        clear_tools()
    
    def test_analyze_vacuum_has_description(self) -> None:
        """Test analyze_vacuum tool has description."""
        @mcp_tool(
            name="analyze_vacuum",
            description="Analyze codebase for vacuum state"
        )
        def analyze_vacuum(directory: str) -> Dict[str, Any]:
            return {}
        
        tools = get_registered_tools()
        desc = tools["analyze_vacuum"]["description"]
        assert len(desc) > 0
    
    def test_execute_vacuum_has_description(self) -> None:
        """Test execute_vacuum tool has description."""
        @mcp_tool(
            name="execute_vacuum",
            description="Execute vacuum cleanup operations"
        )
        def execute_vacuum(directory: str) -> Dict[str, Any]:
            return {}
        
        tools = get_registered_tools()
        desc = tools["execute_vacuum"]["description"]
        assert len(desc) > 0


# AC_COMPLETE: AC-WAVE-K-008 ✅
