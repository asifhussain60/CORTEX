"""MCP Protocol - Re-exports from server module and defines protocol types."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum

from cortex.mcp.server import ToolDefinition, ToolParameter, MCPError  # noqa


class ErrorCode(Enum):
    """MCP error codes."""

    INVALID_REQUEST = "invalid_request"
    METHOD_NOT_FOUND = "method_not_found"
    INVALID_PARAMS = "invalid_params"
    INTERNAL_ERROR = "internal_error"
    SERVER_ERROR = "server_error"
    TOOL_NOT_FOUND = "tool_not_found"


@dataclass
class MCPTool:
    """MCP Tool definition.

    Attributes:
        tool_id: Unique tool identifier.
        name: Tool name.
        description: Tool description.
        parameters: Tool parameters.
        metadata: Additional metadata.
    """

    tool_id: str
    name: str
    description: str
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


__all__ = ["ToolDefinition", "ToolParameter", "MCPError", "MCPTool", "ErrorCode"]
