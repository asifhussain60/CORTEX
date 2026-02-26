"""
CORTEX MCP Module: Model Context Protocol Implementation.

MCP Server — current state (target: 39 registered tools):
    - 28 production tools registered in mcp_registry.py (as of 2026-02-26)
    - Business capability alignment
    - Cross-platform support (macOS, Windows, Linux)
    - Comprehensive test coverage

Authoritative tool count: len(MCP_TOOL_REGISTRY) from cortex.mcp.mcp_registry
Target count (39) is the architecture goal; gap of 11 tools is tracked in
cortex-registry/planning/ as planned phases.

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
