"""
Toolkit Verify MCP Tool.

Exposes SetupVerifier for cross-platform environment verification.

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
from cortex.toolkit.setup import SetupVerifier


class ToolkitVerifyTool(ConsolidatedTool):
    """
    MCP tool for cross-platform environment verification.
    
    Exposes SetupVerifier functionality via MCP protocol.
    """
    
    @property
    def name(self) -> str:
        return "toolkit_verify"
    
    @property
    def description(self) -> str:
        return "Verify CORTEX environment setup (auto-detects platform: windows, macos, linux)"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.UTILITIES
    
    @property
    def parameters(self) -> list:
        return [
            ToolParameter(
                name="platform",
                type="string",
                required=False,
                description="Platform to verify (auto, windows, macos, linux)",
                default="auto",
                enum=["auto", "windows", "macos", "linux"]
            )
        ]
    
    @property
    def supported_operations(self) -> list:
        return ["auto", "windows", "macos", "linux"]
    
    def execute(self, platform: str = "auto", **kwargs) -> ToolResult:
        """
        Execute environment verification.
        
        Args:
            platform: Platform to verify (auto-detects if 'auto')
        
        Returns:
            ToolResult with verification results
        """
        try:
            verifier = SetupVerifier()
            
            # Auto-detect platform if needed
            if platform == "auto":
                import sys
                if sys.platform == "win32":
                    platform = "windows"
                elif sys.platform == "darwin":
                    platform = "macos"
                else:
                    platform = "linux"
            
            result = verifier.verify_environment(platform=platform)
            
            return ToolResult(
                success=result.get("status") == "verified",
                data=result,
                metadata={"platform": platform, "auto_detected": platform == "auto"}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                data={},
                error=f"Verification failed: {str(e)}",
                metadata={"platform": platform}
            )
