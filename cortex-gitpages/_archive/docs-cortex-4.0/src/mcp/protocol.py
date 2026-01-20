"""
MCP (Model Context Protocol) Protocol Implementation.

Full compliance with MCP v2024-11-05 specification including:
- JSON-RPC 2.0 message format
- Tool definition and execution
- Resource and Prompt handling
- Error handling and recovery
- Message type support (tools, resources, prompts, notifications)
"""
from typing import Protocol, Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class ErrorCode(Enum):
    """MCP Error codes per JSON-RPC 2.0 and MCP spec."""
    # JSON-RPC 2.0 standard codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000  # -32000 to -32099 reserved for server errors
    
    # MCP-specific success codes
    SUCCESS = 0
    
    # MCP-specific error codes
    TOOL_NOT_FOUND = -32001
    EXECUTION_ERROR = -32002
    TIMEOUT = -32003
    UNSUPPORTED = -32004
    AUTHORIZATION_ERROR = -32005
    NOT_IMPLEMENTED = -32006

@dataclass
class ToolParameter:
    """
    Tool parameter definition per MCP spec.
    
    Attributes:
        name: Parameter name (snake_case)
        type: Parameter type (string, number, boolean, object, array)
        description: Human-readable description
        required: Whether parameter is required
        default: Default value if not provided
        enum: List of allowed values
        min_value: Minimum value for numeric types
        max_value: Maximum value for numeric types
    """
    name: str
    type: str  # "string", "number", "boolean", "object", "array"
    description: str
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def validate(self) -> tuple[bool, str]:
        """Validate parameter definition. Returns (is_valid, error_message)."""
        if not self.name:
            return False, "Parameter name cannot be empty"
        
        if not self.type or self.type not in ["string", "number", "boolean", "object", "array"]:
            return False, f"Invalid type: {self.type}"
        
        if not self.description:
            return False, "Parameter must have description"
        
        return True, ""

@dataclass
class ToolDefinition:
    """
    MCP-compliant tool definition per specification.
    
    Attributes:
        id: Unique tool identifier
        name: Tool name (snake_case)
        description: Comprehensive description
        parameters: List of parameter definitions
        returns: Return value schema
        version: Tool version (semver)
        tags: Categorization tags
        deprecated: Deprecation status
        timeout_ms: Execution timeout in milliseconds
    """
    id: str
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    returns: Optional[Dict[str, Any]] = None
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    deprecated: bool = False
    timeout_ms: int = 30000

    def validate(self) -> tuple[bool, str]:
        """Validate tool definition. Returns (is_valid, error_message)."""
        if not self.id:
            return False, "Tool ID cannot be empty"
        
        if not self.name:
            return False, "Tool name cannot be empty"
        
        if not self.description:
            return False, "Tool must have description"
        
        if self.timeout_ms <= 0:
            return False, f"Invalid timeout: {self.timeout_ms}ms"
        
        # Validate all parameters
        for param in self.parameters:
            is_valid, msg = param.validate()
            if not is_valid:
                return False, f"Invalid parameter '{param.name}': {msg}"
        
        return True, ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                    "enum": p.enum,
                    "min_value": p.min_value,
                    "max_value": p.max_value,
                }
                for p in self.parameters
            ],
            "returns": self.returns,
            "version": self.version,
            "tags": self.tags,
            "deprecated": self.deprecated,
            "timeout_ms": self.timeout_ms,
        }

class MCPTool(Protocol):
    """Protocol for MCP-compliant tools."""
    
    def get_definition(self) -> ToolDefinition:
        """Get the tool's MCP definition."""
        ...
    
    def execute(self, **params) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        ...
    
    def call(self, **params) -> Dict[str, Any]:
        """Execute the tool with given parameters (alias for execute)."""
        ...
    
    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """Validate parameters for this tool."""
        ...
    
    def get_error_code(self) -> 'ErrorCode':
        """Get error code for this tool."""
        ...


@dataclass
class MCPError:
    """MCP error response per JSON-RPC 2.0."""
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {
            "code": self.code,
            "message": self.message,
        }
        if self.data:
            result["data"] = self.data
        return result


@dataclass
class MCPRequest:
    """
    JSON-RPC 2.0 request per MCP specification.
    
    Attributes:
        jsonrpc: JSON-RPC version ("2.0")
        method: Method name (e.g., "tools/list", "tools/call")
        params: Method parameters (optional)
        id: Request ID for correlation (optional for notifications)
    """
    jsonrpc: str = "2.0"
    method: str = ""
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    id: Optional[Union[int, str]] = None

    def validate(self) -> tuple[bool, str]:
        """Validate JSON-RPC 2.0 compliance."""
        if self.jsonrpc != "2.0":
            return False, f"Invalid jsonrpc version: {self.jsonrpc}"
        
        if not self.method:
            return False, "Method cannot be empty"
        
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
        }
        if self.params is not None:
            result["params"] = self.params
        if self.id is not None:
            result["id"] = self.id
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class MCPResponse:
    """
    JSON-RPC 2.0 response per MCP specification.
    
    Attributes:
        jsonrpc: JSON-RPC version ("2.0")
        result: Success result (mutually exclusive with error)
        error: Error object (mutually exclusive with result)
        id: Request ID for correlation
    """
    jsonrpc: str = "2.0"
    result: Optional[Dict[str, Any]] = None
    error: Optional[MCPError] = None
    id: Optional[Union[int, str]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_error(self) -> bool:
        """Check if response contains an error."""
        return self.error is not None

    def validate(self) -> tuple[bool, str]:
        """Validate JSON-RPC 2.0 compliance."""
        if self.jsonrpc != "2.0":
            return False, f"Invalid jsonrpc version: {self.jsonrpc}"
        
        if self.result is not None and self.error is not None:
            return False, "Response cannot have both result and error"
        
        if self.result is None and self.error is None:
            return False, "Response must have either result or error"
        
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        result = {"jsonrpc": self.jsonrpc}
        
        if self.result is not None:
            result["result"] = self.result
        
        if self.error is not None:
            result["error"] = self.error.to_dict()
        
        if self.id is not None:
            result["id"] = self.id
        
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

class ToolValidator:
    """Validates tool inputs against definitions per MCP spec."""
    
    @staticmethod
    def validate_parameter(param: ToolParameter, value: Any) -> tuple[bool, str]:
        """
        Validate single parameter.
        Returns: (is_valid, error_message)
        """
        if value is None:
            if param.required:
                return False, f"Required parameter missing: {param.name}"
            return True, ""
        
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
            return False, f"Parameter '{param.name}' has wrong type. Expected {param.type}, got {type(value).__name__}"
        
        # Enum check
        if param.enum and value not in param.enum:
            return False, f"Parameter '{param.name}' value not in enum: {param.enum}"
        
        # Range check for numbers
        if param.type == "number":
            if param.min_value is not None and value < param.min_value:
                return False, f"Parameter '{param.name}' is below minimum: {param.min_value}"
            if param.max_value is not None and value > param.max_value:
                return False, f"Parameter '{param.name}' is above maximum: {param.max_value}"
        
        return True, ""
    
    @staticmethod
    def validate_all_params(definition: ToolDefinition, params: Optional[Dict[str, Any]]) -> tuple[bool, str]:
        """
        Validate all parameters against tool definition.
        Returns: (is_valid, error_message)
        """
        if params is None:
            params = {}
        
        # Check required parameters
        for param in definition.parameters:
            if param.required and param.name not in params:
                return False, f"Missing required parameter: {param.name}"
            
            if param.name in params:
                is_valid, msg = ToolValidator.validate_parameter(param, params[param.name])
                if not is_valid:
                    return False, msg
        
        # Check for unknown parameters
        known_names = {p.name for p in definition.parameters}
        for key in params:
            if key not in known_names:
                return False, f"Unknown parameter: {key}"
        
        return True, ""


class MessageType(Enum):
    """MCP message types per specification."""
    # Tool-related
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    # Resource-related
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    RESOURCES_SUBSCRIBE = "resources/subscribe"
    RESOURCES_UNSUBSCRIBE = "resources/unsubscribe"
    
    # Prompt-related
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    
    # Notifications
    NOTIFICATION_RESOURCE_UPDATED = "notifications/resources/updated"
    NOTIFICATION_TOOL_CALLED = "notifications/tools/called"


class MCPProtocolHandler:
    """Handles MCP protocol requests and responses."""
    
    @staticmethod
    def create_error_response(
        code: int,
        message: str,
        request_id: Optional[Union[int, str]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> MCPResponse:
        """Create an error response per JSON-RPC 2.0 spec."""
        error = MCPError(code=code, message=message, data=data)
        return MCPResponse(jsonrpc="2.0", error=error, id=request_id)
    
    @staticmethod
    def create_success_response(
        result: Dict[str, Any],
        request_id: Optional[Union[int, str]] = None
    ) -> MCPResponse:
        """Create a success response per JSON-RPC 2.0 spec."""
        return MCPResponse(jsonrpc="2.0", result=result, id=request_id)
    
    @staticmethod
    def parse_request(data: Union[str, Dict[str, Any]]) -> tuple[bool, Union[MCPRequest, str]]:
        """
        Parse incoming JSON-RPC 2.0 request.
        Returns: (is_valid, MCPRequest or error_message)
        """
        try:
            if isinstance(data, str):
                request_dict = json.loads(data)
            else:
                request_dict = data
            
            request = MCPRequest(
                jsonrpc=request_dict.get("jsonrpc", "2.0"),
                method=request_dict.get("method", ""),
                params=request_dict.get("params"),
                id=request_dict.get("id")
            )
            
            is_valid, msg = request.validate()
            if not is_valid:
                return False, msg
            
            return True, request
        except (json.JSONDecodeError, TypeError) as e:
            return False, f"Invalid JSON: {str(e)}"
    
    @staticmethod
    def error_code_to_message(code: int) -> str:
        """Map error code to human-readable message."""
        code_messages = {
            -32700: "Parse error",
            -32600: "Invalid Request",
            -32601: "Method not found",
            -32602: "Invalid params",
            -32603: "Internal error",
            -32001: "Tool not found",
            -32002: "Execution error",
            -32003: "Timeout",
            -32004: "Unsupported",
            -32005: "Authorization error",
            -32006: "Not implemented",
        }
        return code_messages.get(code, "Unknown error")
