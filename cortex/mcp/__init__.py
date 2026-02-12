"""
CORTEX MCP Module: Model Context Protocol Implementation.

Consolidated MCP Server (WAVE-100):
    - 24 production tools (75% reduction from 98)
    - Business capability alignment
    - Cross-platform support (macOS, Windows, Linux)
    - Comprehensive test coverage

Usage:
    from cortex.mcp import MCPServer
    from cortex.mcp.base import Tool, ToolCategory
    from cortex.mcp.registry import get_registry

Authority: WAVE-100 MCP Consolidation
"""

from cortex.mcp.server import MCPServer, MCPRequest, MCPResponse
from cortex.mcp.base import Tool, ToolResult, ToolCategory
from cortex.mcp.registry import ToolRegistry, get_registry

MCPServerV2 = MCPServer

__all__ = [
    "MCPServer",
    "MCPServerV2",
    "MCPRequest",
    "MCPResponse",
    "Tool",
    "ToolResult",
    "ToolCategory",
    "ToolRegistry",
    "get_registry",
]
