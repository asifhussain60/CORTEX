"""
CORTEX MCP Module: Model Context Protocol Implementation.

Consolidated MCP Server (WAVE-100):
    - 24 production tools (75% reduction from 98)
    - Business capability alignment
    - Cross-platform support (macOS, Windows, Linux)
    - Comprehensive test coverage

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
