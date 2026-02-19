"""
Tests for Toolkit MCP Tools.

Tests MCP integration for all 5 toolkit tools.
"""

import pytest
from cortex.mcp.tools.toolkit import (
    ToolkitDiagnoseTool,
    ToolkitVerifyTool,
    ToolkitCleanupTool,
    ToolkitValidateTool,
    ToolkitAnalyzeTool
)


class TestToolkitDiagnoseTool:
    """Test ToolkitDiagnoseTool MCP integration."""
    
    def test_tool_initialization(self):
        """Test tool can be initialized."""
        tool = ToolkitDiagnoseTool()
        assert tool.name == "toolkit_diagnose"
        assert "diagnos" in tool.description.lower()
    
    def test_supported_operations(self):
        """Test tool exposes correct operations."""
        tool = ToolkitDiagnoseTool()
        assert "full" in tool.supported_operations
        assert "mcp" in tool.supported_operations
        assert "venv" in tool.supported_operations


class TestToolkitVerifyTool:
    """Test ToolkitVerifyTool MCP integration."""
    
    def test_tool_initialization(self):
        """Test tool can be initialized."""
        tool = ToolkitVerifyTool()
        assert tool.name == "toolkit_verify"
        assert "verify" in tool.description.lower()
    
    def test_supported_operations(self):
        """Test tool exposes correct operations."""
        tool = ToolkitVerifyTool()
        assert "auto" in tool.supported_operations
        assert "windows" in tool.supported_operations
        assert "macos" in tool.supported_operations
        assert "linux" in tool.supported_operations


class TestToolkitCleanupTool:
    """Test ToolkitCleanupTool MCP integration."""
    
    def test_tool_initialization(self):
        """Test tool can be initialized."""
        tool = ToolkitCleanupTool()
        assert tool.name == "toolkit_cleanup"
        assert "cleanup" in tool.description.lower()
    
    def test_supported_operations(self):
        """Test tool exposes correct operations."""
        tool = ToolkitCleanupTool()
        assert "all" in tool.supported_operations
        assert "markdown" in tool.supported_operations
        assert "pycache" in tool.supported_operations
        assert "debug" in tool.supported_operations
    
    def test_dry_run_parameter(self):
        """Test dry_run parameter is available."""
        tool = ToolkitCleanupTool()
        params = {p.name: p for p in tool.parameters}
        assert "dry_run" in params
        assert params["dry_run"].type == "boolean"


class TestToolkitValidateTool:
    """Test ToolkitValidateTool MCP integration."""
    
    def test_tool_initialization(self):
        """Test tool can be initialized."""
        tool = ToolkitValidateTool()
        assert tool.name == "toolkit_validate"
        assert "validat" in tool.description.lower()
    
    def test_supported_operations(self):
        """Test tool exposes correct operations."""
        tool = ToolkitValidateTool()
        assert "all" in tool.supported_operations
        assert "governance" in tool.supported_operations
        assert "production" in tool.supported_operations
        assert "security" in tool.supported_operations


class TestToolkitAnalyzeTool:
    """Test ToolkitAnalyzeTool MCP integration."""
    
    def test_tool_initialization(self):
        """Test tool can be initialized."""
        tool = ToolkitAnalyzeTool()
        assert tool.name == "toolkit_analyze"
        assert "analyz" in tool.description.lower()
    
    def test_supported_operations(self):
        """Test tool exposes correct operations."""
        tool = ToolkitAnalyzeTool()
        assert "traces" in tool.supported_operations
        assert "performance" in tool.supported_operations
        assert "usage" in tool.supported_operations
        assert "health" in tool.supported_operations


class TestToolkitIntegration:
    """Test toolkit tools work together."""
    
    def test_all_tools_unique_names(self):
        """Test all toolkit tools have unique names."""
        tools = [
            ToolkitDiagnoseTool(),
            ToolkitVerifyTool(),
            ToolkitCleanupTool(),
            ToolkitValidateTool(),
            ToolkitAnalyzeTool()
        ]
        names = [t.name for t in tools]
        assert len(names) == len(set(names)), "Tool names must be unique"
    
    def test_all_tools_have_descriptions(self):
        """Test all tools have non-empty descriptions."""
        tools = [
            ToolkitDiagnoseTool(),
            ToolkitVerifyTool(),
            ToolkitCleanupTool(),
            ToolkitValidateTool(),
            ToolkitAnalyzeTool()
        ]
        for tool in tools:
            assert len(tool.description) > 10, f"{tool.name} needs longer description"
    
    def test_all_tools_have_operations(self):
        """Test all tools define supported operations."""
        tools = [
            ToolkitDiagnoseTool(),
            ToolkitVerifyTool(),
            ToolkitCleanupTool(),
            ToolkitValidateTool(),
            ToolkitAnalyzeTool()
        ]
        for tool in tools:
            assert len(tool.supported_operations) > 0, f"{tool.name} needs operations"
