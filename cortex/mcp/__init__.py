"""
CORTEX MCP Module: Model Context Protocol Implementation.

MCP Server — 30 production tools registered in mcp_registry.py.
    - Business capability alignment
    - Cross-platform support (macOS, Windows, Linux)
    - Comprehensive test coverage

Authoritative tool count: len(PRODUCTION_TOOLS) from cortex.mcp.mcp_registry

Usage:
    from cortex.mcp import MCPServer
    from cortex.mcp.mcp_tool_base import Tool, ToolCategory
    from cortex.mcp.mcp_registry import get_registry

Authority: WAVE-100 MCP Consolidation
"""

from cortex.mcp.server import MCPServer, MCPRequest, MCPResponse
from cortex.mcp.mcp_tool_base import Tool, ToolResult, ToolCategory
from cortex.mcp.mcp_registry import ToolRegistry, get_registry

__all__ = [
    "MCPServer",
    "MCPRequest",
    "MCPResponse",
    "Tool",
    "ToolResult",
    "ToolCategory",
    "ToolRegistry",
    "get_registry",
]
