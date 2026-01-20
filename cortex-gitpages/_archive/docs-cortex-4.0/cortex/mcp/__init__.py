"""
CORTEX MCP Module: Model Context Protocol Implementation.

This module provides JSON-RPC 2.0 compliant Model Context Protocol for
tool management, discovery, and execution within the CORTEX system.

Exports:
    MCPServer: Main MCP protocol server
    Tool: Abstract base class for MCP tools
    ToolDefinition: Tool definition data model
    ToolParameter: Tool parameter definition
    MCPRequest: JSON-RPC request model
    MCPResponse: JSON-RPC response model
    MCPError: JSON-RPC error model
"""

from cortex.mcp.server import (
    MCPServer,
    Tool,
    SampleTool,
    ToolDefinition,
    ToolParameter,
    MCPRequest,
    MCPResponse,
    MCPError,
)
from cortex.mcp.decorators import mcp_tool, MCP_TOOLS_REGISTRY
from cortex.mcp.endpoints import (
    list_tools_endpoint,
    get_tool_metadata,
    filter_tools_by_domain,
    get_tool_count,
    is_tool_registered,
    call_tool,
)

__all__ = [
    "MCPServer",
    "Tool",
    "SampleTool",
    "ToolDefinition",
    "ToolParameter",
    "MCPRequest",
    "MCPResponse",
    "MCPError",
    "mcp_tool",
    "MCP_TOOLS_REGISTRY",
    "list_tools_endpoint",
    "get_tool_metadata",
    "filter_tools_by_domain",
    "get_tool_count",
    "is_tool_registered",
    "call_tool",
]
