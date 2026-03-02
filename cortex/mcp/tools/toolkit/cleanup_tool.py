"""
Toolkit Cleanup MCP Tool.

Exposes VacuumAutomation for automated cleanup strategies.

Author: CORTEX Framework
Phase: 90 (Toolkit Centralization)
"""

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.tools.toolkit.cleanup import VacuumAutomation


class ToolkitCleanupTool(ConsolidatedTool):
    """
    MCP tool for automated cleanup operations.
    
    Exposes VacuumAutomation functionality via MCP protocol.
    """
    
    @property
    def name(self) -> str:
        """The unique tool name identifier."""
        return "toolkit_cleanup"
    
    @property
    def description(self) -> str:
        """Human-readable description of the tool."""
        return "Run automated cleanup (markdown, pycache, debug, sessions, builds, all)"
    
    @property
    def category(self) -> ToolCategory:
        """The tool category for registry classification."""
        return ToolCategory.UTILITIES
    
    @property
    def parameters(self) -> list:
        """List of parameters accepted by the tool."""
        return [
            ToolParameter(
                name="strategy",
                type="string",
                required=False,
                description="Cleanup strategy to apply",
                default="all",
                enum=["markdown", "pycache", "debug", "sessions", "builds", "all"]
            ),
            ToolParameter(
                name="dry_run",
                type="boolean",
                required=False,
                description="Preview changes without executing",
                default=False
            )
        ]
    
    @property
    def supported_operations(self) -> list:
        """List of operation types this tool supports."""
        return ["markdown", "pycache", "debug", "sessions", "builds", "all"]
    
    def execute(self, strategy: str = "all", dry_run: bool = False, **kwargs) -> ToolResult:
        """
        Execute cleanup operations.
        
        Args:
            strategy: Cleanup strategy (markdown, pycache, debug, sessions, builds, all)
            dry_run: Preview changes without executing
        
        Returns:
            ToolResult with cleanup results
        """
        try:
            vacuum = VacuumAutomation()
            
            if strategy == "all":
                result = vacuum.execute_all_strategies(dry_run=dry_run)
            elif strategy == "markdown":
                result = vacuum.cleanup_markdown_sprawl(dry_run=dry_run)
            elif strategy == "pycache":
                result = vacuum.cleanup_pycache(dry_run=dry_run)
            elif strategy == "debug":
                result = vacuum.cleanup_debug_markers(dry_run=dry_run)
            elif strategy == "sessions":
                result = vacuum.cleanup_session_artifacts(dry_run=dry_run)
            elif strategy == "builds":
                result = vacuum.cleanup_build_artifacts(dry_run=dry_run)
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unknown strategy: {strategy}",
                    metadata={"available_strategies": self.supported_operations}
                )
            
            return ToolResult(
                success=True,
                data=result,
                metadata={"strategy": strategy, "dry_run": dry_run}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Cleanup failed: {str(e)}",
                metadata={"strategy": strategy, "dry_run": dry_run}
            )
