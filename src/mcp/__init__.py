"""
CORTEX MCP Module

Model Context Protocol integration:
- decorator.py: @mcp_tool decorator
- registry.py: OrchestratorRegistry for tool registration
- server.py: MCP server implementation
"""

from src.mcp.decorator import mcp_tool
from src.mcp.registry import OrchestratorRegistry

__all__ = ["mcp_tool", "OrchestratorRegistry"]
