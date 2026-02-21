"""
Toolkit Diagnose MCP Tool.

Exposes MCPHealthChecker for comprehensive MCP diagnostics.

Author: CORTEX Framework
Phase: 90 (Toolkit Centralization)
"""

from typing import Any, Dict
from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.tools.toolkit.diagnostics import MCPHealthChecker


class ToolkitDiagnoseTool(ConsolidatedTool):
    """
    MCP tool for comprehensive MCP diagnostics.
    
    Exposes MCPHealthChecker functionality via MCP protocol.
    """
    
    @property
    def name(self) -> str:
        """The unique tool name identifier."""
        return "toolkit_diagnose"
    
    @property
    def description(self) -> str:
        """Human-readable description of the tool."""
        return "Run comprehensive MCP diagnostics (full, mcp, venv, settings, tools)"
    
    @property
    def category(self) -> ToolCategory:
        """The tool category for registry classification."""
        return ToolCategory.UTILITIES
    
    @property
    def parameters(self) -> list:
        """List of parameters accepted by the tool."""
        return [
            ToolParameter(
                name="operation",
                type="string",
                required=False,
                description="Diagnostic operation to perform",
                default="full",
                enum=["full", "mcp", "venv", "settings", "tools"]
            )
        ]
    
    @property
    def supported_operations(self) -> list:
        """List of operation types this tool supports."""
        return ["full", "mcp", "venv", "settings", "tools"]
    
    def execute(self, operation: str = "full", **kwargs) -> ToolResult:
        """
        Execute MCP diagnostics.
        
        Args:
            operation: Diagnostic operation (full, mcp, venv, settings, tools)
        
        Returns:
            ToolResult with diagnostic findings
        """
        try:
            checker = MCPHealthChecker()
            
            if operation == "full":
                result = checker.check_all()
            elif operation == "mcp":
                result = checker.check_mcp_configuration()
            elif operation == "venv":
                result = checker.check_virtual_environment()
            elif operation == "settings":
                result = checker.check_vscode_settings()
            elif operation == "tools":
                result = checker.check_tool_availability()
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unknown operation: {operation}",
                    metadata={"available_operations": self.supported_operations}
                )
            
            return ToolResult(
                success=result.get("status") == "healthy",
                data=result,
                metadata={"operation": operation}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Diagnostic failed: {str(e)}",
                metadata={"operation": operation}
            )
