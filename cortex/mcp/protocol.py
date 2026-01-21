"""MCP Protocol

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class ErrorCode(Enum):
    """MCP error codes."""
    INVALID_REQUEST = "invalid_request"
    METHOD_NOT_FOUND = "method_not_found"
    INTERNAL_ERROR = "internal_error"


class MCPError(Exception):
    """MCP protocol error."""
    pass


@dataclass
class MCPRequest:
    """MCP request."""
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


@dataclass
class MCPResponse:
    """MCP response."""
    result: Any = None
    error: Optional[str] = None
    id: Optional[str] = None


@dataclass
class ToolDefinition:
    """Tool definition."""
    id: str  # Unique identifier
    name: str
    description: str
    parameters: list = field(default_factory=list)
    tags: list = field(default_factory=list)  # Tag list for categorization
    deprecated: bool = False  # Whether tool is deprecated


@dataclass
class ToolParameter:
    """Tool parameter."""
    name: str
    type: str
    required: bool = False


@dataclass
class MCPTool:
    """MCP tool."""
    name: str
    definition: ToolDefinition
    enabled: bool = True
    
    def get_definition(self) -> ToolDefinition:
        """Get tool definition.
        
        Returns:
            ToolDefinition: Tool definition.
        """
        return self.definition
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool.
        
        Args:
            **kwargs: Tool parameters.
            
        Returns:
            Execution result.
        """
        return {"status": "success"}


class ToolValidator:
    """Validate MCP tools."""
    
    def validate(self, tool: MCPTool) -> bool:
        """Validate tool."""
        return True


class MessageType(Enum):
    """MCP message types."""
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"


class MCPProtocolHandler:
    """Handle MCP protocol."""
    
    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle request."""
        return MCPResponse(result="OK")

__all__ = ["ErrorCode", "MCPError", "MCPRequest", "MCPResponse", "ToolDefinition", "ToolParameter", "MCPTool", "ToolValidator", "MessageType", "MCPProtocolHandler"]
