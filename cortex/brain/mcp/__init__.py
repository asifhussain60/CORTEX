"""
CORTEX MCP Module

Model Context Protocol integration:
- decorator.py: @mcp_tool decorator
- registry.py: OrchestratorRegistry for tool registration
- server.py: MCP server implementation
"""

from cortex.brain.mcp.decorator import mcp_tool

# Import OrchestratorRegistry from correct location
try:
    from cortex.orchestrators.registry import OrchestratorRegistry
except ImportError:
    # Fallback for backward compatibility
    OrchestratorRegistry = None  # type: ignore

__all__ = ["mcp_tool", "OrchestratorRegistry"]
