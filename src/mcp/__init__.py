"""
CORTEX 4.0 MCP Gateway - Minimal Stub

This is a minimal stub implementation for Phase 1.
Full MCP Gateway will be implemented in Phase 4.

Purpose: Allow orchestrators to reference MCP Gateway without blocking Phase 3 migration.

Design: Delegates to legacy tool wrappers until full implementation complete.
"""

from typing import Any, Dict
import logging


class MCPGatewayStub:
    """
    Minimal MCP Gateway stub for Phase 1-3.
    
    This stub allows orchestrators to be written with MCP Gateway references
    without requiring the full implementation. It delegates to legacy wrappers.
    
    Full implementation in Phase 4 will replace this stub.
    """
    
    def __init__(self):
        """Initialize MCP Gateway stub."""
        self.logger = logging.getLogger(__name__)
        self.logger.warning(
            "Using MCP Gateway stub. Full implementation available in Phase 4."
        )
        self._enabled = False
    
    def invoke_tool(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool through MCP Gateway (stub).
        
        Args:
            tool: Tool name (e.g., "git", "docker", "pytest")
            params: Tool parameters
        
        Returns:
            Tool execution result
        
        Note:
            This is a stub. It logs the call but returns empty result.
            Full implementation will route to MCP servers.
        """
        self.logger.debug(f"MCP Gateway stub: invoke_tool(tool={tool}, params={params})")
        
        # Stub response
        return {
            "success": False,
            "message": "MCP Gateway stub - full implementation in Phase 4",
            "tool": tool,
            "params": params
        }
    
    def is_enabled(self) -> bool:
        """Check if MCP Gateway is enabled."""
        return self._enabled
    
    def get_available_tools(self) -> list:
        """Get list of available tools (stub)."""
        return []


# Singleton instance
_gateway_stub: MCPGatewayStub = None


def get_mcp_gateway() -> MCPGatewayStub:
    """Get MCP Gateway singleton instance."""
    global _gateway_stub
    if _gateway_stub is None:
        _gateway_stub = MCPGatewayStub()
    return _gateway_stub
