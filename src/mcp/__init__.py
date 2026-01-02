"""
MCP (Model Context Protocol) package.

Provides universal orchestrator invocation infrastructure via MCP v1.0 protocol.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from .server import MCPServer, MCPRequest, MCPResponse, mcp_tool, MCPVersion, RequestStatus

__version__ = "1.0.0"
__all__ = [
    "MCPServer",
    "MCPRequest",
    "MCPResponse",
    "mcp_tool",
    "MCPVersion",
    "RequestStatus",
]

