"""MCP (Model Context Protocol) Protocol Implementation."""
from typing import Protocol, Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ErrorCode(Enum):
    """MCP Error codes."""
    SUCCESS = "success"
    INVALID_REQUEST = "invalid_request"
    METHOD_NOT_FOUND = "method_not_found"
    INVALID_PARAMS = "invalid_params"
    INTERNAL_ERROR = "internal_error"
    PARSE_ERROR = "parse_error"
    TOOL_NOT_FOUND = "tool_not_found"
    EXECUTION_ERROR = "execution_error"
    TIMEOUT = "timeout"
    UNSUPPORTED = "unsupported"

@dataclass
class ToolParameter:
    """Tool parameter definition."""
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

@dataclass
class ToolDefinition:
    """MCP-compliant tool definition."""
    id: str
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: Optional[Dict[str, Any]] = None
    version: str = "1.0"
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    timeout_ms: int = 30000

@dataclass
class MCPError:
    """MCP error response."""
    code: ErrorCode
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MCPResponse:
    """MCP response structure."""
    id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[MCPError] = None
    timestamp: datetime = field(default_factory=datetime.now)

class MCPTool(Protocol):
    """Protocol for MCP-compliant tools."""
    
    def get_definition(self) -> ToolDefinition:
        """Get tool definition."""
        ...
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with parameters."""
        ...
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate execution parameters."""
        ...
    
    def get_error_code(self, error: Exception) -> ErrorCode:
        """Map exception to MCP error code."""
        ...

class ToolValidator:
    """Validates tool inputs against definitions."""
    
    @staticmethod
    def validate_parameter(param: ToolParameter, value: Any) -> bool:
        """Validate single parameter."""
        if value is None:
            return not param.required
        
        # Type checking
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }
        
        expected_type = type_map.get(param.type)
        if expected_type and not isinstance(value, expected_type):
            return False
        
        # Enum check
        if param.enum and value not in param.enum:
            return False
        
        # Range check
        if param.min_value is not None and value < param.min_value:
            return False
        if param.max_value is not None and value > param.max_value:
            return False
        
        return True
    
    @staticmethod
    def validate_all_params(definition: ToolDefinition, params: Dict[str, Any]) -> tuple:
        """Validate all parameters. Returns (is_valid, error_message)."""
        # Check required parameters
        for param in definition.parameters:
            if param.required and param.name not in params:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in params:
                if not ToolValidator.validate_parameter(param, params[param.name]):
                    return False, f"Invalid value for parameter {param.name}"
        
        # Check for unknown parameters
        known_names = {p.name for p in definition.parameters}
        for key in params:
            if key not in known_names:
                return False, f"Unknown parameter: {key}"
        
        return True, ""
