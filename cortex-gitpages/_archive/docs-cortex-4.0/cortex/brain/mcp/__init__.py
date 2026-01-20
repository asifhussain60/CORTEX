"""
CORTEX MCP Module

Model Context Protocol integration:
- decorator.py: @mcp_tool decorator
- registry.py: OrchestratorRegistry for tool registration
- server.py: MCP server implementation
"""

from cortex.brain.mcp.decorator import mcp_tool
from cortex.brain.mcp.registry import OrchestratorRegistry

__all__ = ["mcp_tool", "OrchestratorRegistry"]
