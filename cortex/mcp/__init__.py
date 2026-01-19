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

__all__ = [
    "MCPServer",
    "Tool",
    "SampleTool",
    "ToolDefinition",
    "ToolParameter",
    "MCPRequest",
    "MCPResponse",
    "MCPError",
]
