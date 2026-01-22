"""MCP Protocol

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime


class ErrorCode(Enum):
    """MCP error codes."""
    SUCCESS = "success"
    INVALID_REQUEST = "invalid_request"
    INVALID_PARAMS = "invalid_params"
    METHOD_NOT_FOUND = "method_not_found"
    INTERNAL_ERROR = "internal_error"
    EXECUTION_ERROR = "execution_error"
    TIMEOUT = "timeout"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    PARSE_ERROR = "parse_error"
    TOOL_NOT_FOUND = "tool_not_found"
    UNSUPPORTED = "unsupported"


class MCPError(Exception):
    """MCP protocol error."""
    
    def __init__(
        self,
        code: Optional[ErrorCode] = None,
        message: str = "",
        data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize MCP error.
        
        Args:
            code: Error code from ErrorCode enum
            message: Error message
            data: Additional error data
        """
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


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
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ToolDefinition:
    """Tool definition."""
    id: str  # Unique identifier
    name: str
    description: str
    parameters: list = field(default_factory=list)
    tags: list = field(default_factory=list)  # Tag list for categorization
    deprecated: bool = False  # Whether tool is deprecated
    version: str = "1.0"  # Tool version
    timeout_ms: Optional[int] = None  # Tool-specific timeout in milliseconds
    returns: Optional[Dict[str, Any]] = None  # Return schema for the tool
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate parameters against definition.
        
        Args:
            params: Parameters to validate.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        for param_def in self.parameters:
            if isinstance(param_def, ToolParameter):
                # Check required parameters
                if param_def.required and param_def.name not in params:
                    return False, f"Missing required parameter: {param_def.name}"
                
                # Check unknown parameters
                if param_def.name in params:
                    value = params[param_def.name]
                    
                    # Check type (basic type validation)
                    if param_def.type == "number" and not isinstance(value, (int, float)):
                        return False, f"Invalid type for {param_def.name}: expected number"
                    if param_def.type == "string" and not isinstance(value, str):
                        return False, f"Invalid type for {param_def.name}: expected string"
                    
                    # Check min/max
                    if param_def.min_value is not None and isinstance(value, (int, float)):
                        if value < param_def.min_value:
                            return False, f"Value for {param_def.name} below minimum: {param_def.min_value}"
                    if param_def.max_value is not None and isinstance(value, (int, float)):
                        if value > param_def.max_value:
                            return False, f"Value for {param_def.name} above maximum: {param_def.max_value}"
        
        # Check for unknown parameters
        known_params = {p.name for p in self.parameters if isinstance(p, ToolParameter)}
        for param_name in params:
            if param_name not in known_params:
                return False, f"Unknown parameter: {param_name}"
        
        return True, None


@dataclass
class ToolParameter:
    """Tool parameter."""
    name: str
    type: str
    description: str = ""
    required: bool = False
    default: Optional[Any] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum: Optional[List[str]] = None


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
    
    def get_error_code(self) -> "ErrorCode":
        """Get error code for failed execution.
        
        Returns:
            ErrorCode: Default EXECUTION_ERROR.
        """
        return ErrorCode.EXECUTION_ERROR


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


class ToolValidator:
    """Validates tool parameters."""
    
    @staticmethod
    def validate_parameter(param: "ToolParameter", value: Any) -> bool:
        """Validate a parameter value against its definition.
        
        Args:
            param: ToolParameter definition
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required
        if param.required and value is None:
            return False
        
        # Allow None for optional parameters
        if value is None and not param.required:
            return True
        
        # Type validation
        if param.type == "string":
            if not isinstance(value, str):
                return False
        elif param.type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False
        elif param.type == "boolean":
            if not isinstance(value, bool):
                return False
        elif param.type == "array":
            if not isinstance(value, list):
                return False
        elif param.type == "object":
            if not isinstance(value, dict):
                return False
        
        # Range validation for numbers
        if param.type == "number" and isinstance(value, (int, float)):
            if param.min_value is not None and value < param.min_value:
                return False
            if param.max_value is not None and value > param.max_value:
                return False
        
        # Enum validation
        if param.enum and value not in param.enum:
            return False
        
        return True
    
    @staticmethod
    def validate_all_params(tool_def: "ToolDefinition", params: Dict[str, Any]) -> tuple:
        """Validate all parameters for a tool definition.
        
        Args:
            tool_def: Tool definition
            params: Dictionary of parameters to validate
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        # Check required parameters
        for param in tool_def.parameters:
            if param.required:
                if param.name not in params:
                    return False, f"Missing required parameter: {param.name}"
                
                if not ToolValidator.validate_parameter(param, params[param.name]):
                    return False, f"Invalid value for parameter: {param.name}"
        
        # Check provided parameters
        param_names = {p.name for p in tool_def.parameters}
        for param_name in params:
            if param_name not in param_names:
                return False, f"Unknown parameter: {param_name}"
            
            # Find the parameter definition
            param_def = None
            for p in tool_def.parameters:
                if p.name == param_name:
                    param_def = p
                    break
            
            if param_def:
                if not ToolValidator.validate_parameter(param_def, params[param_name]):
                    # Check if it's a range error
                    if param_def.type == "number" and isinstance(params[param_name], (int, float)):
                        if param_def.max_value is not None and params[param_name] > param_def.max_value:
                            return False, f"Parameter {param_name} exceeds maximum value of {param_def.max_value}"
                        if param_def.min_value is not None and params[param_name] < param_def.min_value:
                            return False, f"Parameter {param_name} is below minimum value of {param_def.min_value}"
                    return False, f"Invalid value for parameter: {param_name}"
        
        return True, ""


__all__ = ["ErrorCode", "MCPError", "MCPRequest", "MCPResponse", "ToolDefinition", "ToolParameter", "MCPTool", "ToolValidator", "MessageType", "MCPProtocolHandler"]
