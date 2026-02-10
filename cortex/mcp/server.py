"""
MCP Server: Model Context Protocol Tool Execution Framework.

Implements JSON-RPC 2.0 compliant MCP protocol for tool discovery,
invocation, execution, and response formatting. Provides comprehensive
tool management with parameter validation, error handling, and caching.

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
CORE-008: Implementation follows TDD specification from test suite.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, asdict, field
from abc import ABC, abstractmethod
from datetime import datetime

try:
    from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
except (ImportError, ModuleNotFoundError):
    EnhancedAuditLogger = None


# ============================================================================
# MCP DATA MODELS
# ============================================================================

@dataclass
class ToolParameter:
    """
    MCP Tool Parameter Definition (compliant with MCP v2024-11-05).
    
    Attributes:
        name: Parameter name
        type: Parameter type (string, number, boolean, array, object)
        required: Whether parameter is required
        description: Parameter description
        default: Default value if parameter is optional
        enum: List of allowed values (for validation)
        min_value: Minimum value for numeric types
        max_value: Maximum value for numeric types
    """
    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None


@dataclass
class ToolDefinition:
    """
    MCP Tool Definition.
    
    Attributes:
        name: Tool name (unique identifier)
        description: Tool description
        parameters: List of ToolParameter definitions
        metadata: Additional tool metadata
    """
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPRequest:
    """
    JSON-RPC 2.0 MCP Request.
    
    Attributes:
        jsonrpc: JSON-RPC version (always "2.0")
        method: Method name (e.g., "tools/call")
        params: Method parameters
        id: Request ID (for correlation)
    """
    jsonrpc: str = "2.0"
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None


@dataclass
class MCPResponse:
    """
    JSON-RPC 2.0 MCP Response.
    
    Attributes:
        jsonrpc: JSON-RPC version (always "2.0")
        result: Response result (if successful)
        error: Error object (if failed)
        id: Request ID (matches request)
    """
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

    def to_json(self) -> str:
        """Serialize response to JSON string."""
        return json.dumps(asdict(self), default=str)


@dataclass
class MCPError:
    """
    JSON-RPC 2.0 Error Object.
    
    Attributes:
        code: Error code (-32700 to -32600, or -32000 to -32099)
        message: Error message
        data: Additional error data
    """
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result: Dict[str, Any] = {
            "code": self.code,
            "message": self.message,
        }
        if self.data is not None:
            result["data"] = self.data
        return result


# ============================================================================
# TOOL IMPLEMENTATION
# ============================================================================

class Tool(ABC):
    """Abstract base class for MCP tools."""

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Get tool definition (name, description, parameters)."""
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """
        Execute tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        pass


class SampleTool(Tool):
    """Sample tool for testing."""

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="sample_tool",
            description="Sample tool for MCP testing",
            parameters=[
                ToolParameter(
                    name="input",
                    type="string",
                    required=True,
                    description="Input parameter"
                ),
                ToolParameter(
                    name="mode",
                    type="string",
                    required=False,
                    description="Execution mode"
                ),
            ],
            metadata={"version": "1.0"}
        )

    def execute(self, input: str = "", mode: str = "normal", **kwargs: Any) -> Dict[str, Any]:
        """Execute sample tool."""
        return {
            "status": "success",
            "input": input,
            "mode": mode,
            "output": f"Processed: {input}",
            "timestamp": datetime.now().isoformat(),
        }


# ============================================================================
# MCP SERVER IMPLEMENTATION
# ============================================================================

class MCPServer:
    """
    MCP Protocol Server for Tool Execution.
    
    Implements JSON-RPC 2.0 compliant Model Context Protocol for
    tool discovery, invocation, execution, and response formatting.
    """

    # JSON-RPC error codes
    PARSE_ERROR: int = -32700
    INVALID_REQUEST: int = -32600
    METHOD_NOT_FOUND: int = -32601
    INVALID_PARAMS: int = -32602
    INTERNAL_ERROR: int = -32603
    SERVER_ERROR_START: int = -32099

    def __init__(self) -> None:
        """Initialize MCP Server."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._tools: Dict[str, Tool] = {}
        self._request_cache: Dict[str, Any] = {}
        self._execution_history: List[Dict[str, Any]] = []
        self._response_cache: Dict[str, MCPResponse] = {}
        
        # Register built-in tools
        self._register_tool(SampleTool())
        
        # AC-MCP-REGISTRY-001: Restore decorator-registered tools from global registry
        # Ensure tools decorated with @mcp_tool() are available on boot
        try:
            from cortex.mcp.decorators import get_registered_tools as get_decorator_tools
            decorator_tools = get_decorator_tools()
            self.logger.info(f"Found {len(decorator_tools)} tools from @mcp_tool decorator registry")
            # Note: Decorator registry stores metadata only, not Tool objects
            # These are exposed via list_tools() but not directly registered here
        except (ImportError, Exception) as e:
            self.logger.debug(f"No decorator-registered tools available: {e}")
        
        # Register CORTEX orchestrator tools
        try:
            from cortex.mcp.cortex_tools import get_cortex_tools
            for tool in get_cortex_tools():
                self._register_tool(tool)
            self.logger.info("CORTEX orchestrator tools registered")
        except (ImportError, Exception) as e:
            self.logger.warning(f"Could not register CORTEX tools: {e}")
        
        # Auto-discover and register MCP tools by category
        try:
            from cortex.mcp.tool_discovery import auto_discover_and_register_tools
            auto_discover_and_register_tools()
            self.logger.info("MCP tools auto-discovered and registered")
        except (ImportError, Exception) as e:
            self.logger.warning(f"Could not auto-discover MCP tools: {e}")
        
        if EnhancedAuditLogger is not None:
            self._audit_logger: Optional[Any] = EnhancedAuditLogger.instance()
        else:
            self._audit_logger = None

    def _register_tool(self, tool: Tool) -> None:
        """
        Register a tool.
        
        Args:
            tool: Tool implementation
        """
        definition: ToolDefinition = tool.definition
        self._tools[definition.name] = tool
        self.logger.info(f"Registered tool: {definition.name}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from local registry and all orchestrators.
        
        AC-MCP-EXPOSURE-001b: Dynamic tool discovery from all 23 orchestrators
        
        Tool sources:
        1. Locally registered tools (self._tools)
        2. Global ToolRegistry
        3. All 23 registered orchestrators via MasterOrchestrator
        
        Returns:
            List of tool definitions as dictionaries, consolidated from all sources
        """
        from cortex.mcp.tool_registry import get_mcp_tool_registry
        
        # Get tools from local registry and global ToolRegistry
        tools_list = []
        seen_tools = set()
        
        # 1. Add locally registered tools (like SampleTool)
        for tool in self._tools.values():
            tool_dict = {
                "name": tool.definition.name,
                "description": tool.definition.description,
                "source": "local",
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "required": p.required,
                        "description": p.description,
                    }
                    for p in tool.definition.parameters
                ],
            }
            tools_list.append(tool_dict)
            seen_tools.add(tool.definition.name)
        
        # 2. Add tools from global ToolRegistry
        try:
            registry = get_mcp_tool_registry()
            for metadata in registry.list_all():
                # Skip if already added
                if metadata.id not in seen_tools:
                    # Handle parameters - they're stored as Dict[str, Dict[str, Any]]
                    params_list = []
                    if isinstance(metadata.parameters, dict):
                        for param_name, param_spec in metadata.parameters.items():
                            if isinstance(param_spec, dict):
                                params_list.append({
                                    "name": param_name,
                                    "type": param_spec.get("type", "string"),
                                    "required": param_spec.get("required", False),
                                    "description": param_spec.get("description", ""),
                                })
                    
                    tool_dict = {
                        "name": metadata.id,
                        "description": metadata.description,
                        "source": "registry",
                        "parameters": params_list,
                    }
                    tools_list.append(tool_dict)
                    seen_tools.add(metadata.id)
        except Exception as e:
            self.logger.warning(f"Could not load tools from ToolRegistry: {e}")
        
        # 2.5. Add decorator-registered tools (@mcp_tool)
        try:
            from cortex.mcp.decorators import get_registered_tools as get_decorator_tools
            decorator_tools = get_decorator_tools()
            
            for tool_name, tool_meta in decorator_tools.items():
                if tool_name not in seen_tools:
                    # Convert parameter dict to list format
                    params_list = []
                    if isinstance(tool_meta.get("parameters"), dict):
                        for param_name, param_type in tool_meta["parameters"].items():
                            params_list.append({
                                "name": param_name,
                                "type": param_type if isinstance(param_type, str) else "string",
                                "required": False,  # Can't determine from decorator metadata
                                "description": "",
                            })
                    
                    tool_dict = {
                        "name": tool_name,
                        "description": tool_meta.get("description", ""),
                        "source": "decorator",
                        "category": tool_meta.get("category", "utility"),
                        "parameters": params_list,
                    }
                    tools_list.append(tool_dict)
                    seen_tools.add(tool_name)
            
            if len(decorator_tools) > 0:
                self.logger.info(f"Added {len(decorator_tools)} decorator-registered tools")
        except Exception as e:
            self.logger.warning(f"Could not load decorator-registered tools: {e}")
        
        # 3. Add tools from all 23 registered orchestrators
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            from cortex.orchestrators.core.orchestrator_wiring import get_wiring_registry
            
            registry = get_wiring_registry()
            orchestrator_count = 0
            
            # Query each registered orchestrator for its tools
            if hasattr(registry, 'wired_orchestrators'):
                for domain, metadata in registry.wired_orchestrators.items():
                    orchestrator = metadata.orchestrator
                    orchestrator_count += 1
                    
                    # Call get_mcp_tools() on each orchestrator
                    if hasattr(orchestrator, 'get_mcp_tools'):
                        try:
                            tools_result = orchestrator.get_mcp_tools()
                            
                            if tools_result and isinstance(tools_result, dict):
                                orchestrator_tools = tools_result.get("tools", {})
                                
                                # Extract tool names from result
                                if isinstance(orchestrator_tools, dict):
                                    for category, tool_names in orchestrator_tools.items():
                                        if isinstance(tool_names, list):
                                            for tool_name in tool_names:
                                                # Add if not already seen
                                                if tool_name not in seen_tools:
                                                    tool_dict = {
                                                        "name": tool_name,
                                                        "category": category,
                                                        "source": f"orchestrator:{domain}",
                                                    }
                                                    tools_list.append(tool_dict)
                                                    seen_tools.add(tool_name)
                        except Exception as e:
                            self.logger.warning(
                                f"Could not get tools from orchestrator '{domain}': {e}"
                            )
            
            self.logger.info(
                f"Tool discovery: queried {orchestrator_count} orchestrators, "
                f"found {len(seen_tools)} unique tools"
            )
            
        except Exception as e:
            self.logger.warning(f"Could not query orchestrators for tools: {e}")
        
        return tools_list

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get all tools (alias for list_tools).
        
        Returns:
            List of tool definitions as dictionaries
        """
        return self.list_tools()

    def _validate_parameters(
        self,
        tool_name: str,
        params: Dict[str, Any]
    ) -> Tuple[bool, Optional[MCPError]]:
        """
        Validate parameters for a tool.
        
        Args:
            tool_name: Name of the tool
            params: Parameters to validate
            
        Returns:
            Tuple of (valid, error) where error is None if valid
        """
        if tool_name not in self._tools:
            return False, MCPError(
                code=self.METHOD_NOT_FOUND,
                message=f"Tool not found: {tool_name}"
            )
        
        tool: Tool = self._tools[tool_name]
        definition: ToolDefinition = tool.definition
        
        # Check required parameters
        for param in definition.parameters:
            if param.required and param.name not in params:
                return False, MCPError(
                    code=self.INVALID_PARAMS,
                    message=f"Required parameter missing: {param.name}",
                    data={"parameter": param.name}
                )
        
        # Check parameter types (basic validation)
        for param in definition.parameters:
            if param.name in params:
                value: Any = params[param.name]
                if param.type == "string" and not isinstance(value, str):
                    return False, MCPError(
                        code=self.INVALID_PARAMS,
                        message=f"Parameter {param.name} must be string",
                        data={"parameter": param.name, "expected": "string"}
                    )
                elif param.type == "number" and not isinstance(value, (int, float)):
                    return False, MCPError(
                        code=self.INVALID_PARAMS,
                        message=f"Parameter {param.name} must be number",
                        data={"parameter": param.name, "expected": "number"}
                    )
        
        return True, None

    def call_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> MCPResponse:
        """
        Call a tool and return MCP response.
        
        Args:
            tool_name: Name of the tool to call
            params: Tool parameters
            request_id: Request ID for correlation
            
        Returns:
            MCPResponse with result or error
        """
        start_time: float = time.time()
        
        # Validate parameters
        valid, error = self._validate_parameters(tool_name, params)
        if not valid:
            return MCPResponse(
                error=error.to_dict() if error else None,
                id=request_id
            )
        
        # Check cache
        cache_key: str = f"{tool_name}:{json.dumps(params, sort_keys=True, default=str)}"
        if cache_key in self._response_cache:
            return self._response_cache[cache_key]
        
        try:
            # Get tool and execute
            tool: Tool = self._tools[tool_name]
            result: Any = tool.execute(**params)
            
            # Record execution
            execution_time_ms: float = (time.time() - start_time) * 1000
            self._execution_history.append({
                "tool": tool_name,
                "params": params,
                "result": result,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.now().isoformat(),
            })
            
            # Create response
            response: MCPResponse = MCPResponse(
                result={
                    "tool": tool_name,
                    "output": result,
                    "execution_time_ms": execution_time_ms,
                },
                id=request_id
            )
            
            # Cache response
            self._response_cache[cache_key] = response
            
            # Phase 71 S3: Learning Gateway Interception (defense-in-depth)
            try:
                from cortex.mcp.learning_gateway_interceptor import get_mcp_learning_interceptor
                interceptor = get_mcp_learning_interceptor()
                interceptor.after_execution(
                    tool_name=tool_name,
                    parameters=params,
                    result=result,
                    execution_time_ms=execution_time_ms,
                    request_id=request_id,
                )
            except Exception as e:
                # Non-blocking - don't let learning failures affect tool execution
                self.logger.warning(f"MCP learning interception failed: {e}")
            
            # Audit execution
            if self._audit_logger is not None:
                try:
                    self._audit_logger.log_operation_start(
                        operation="MCP_TOOL_CALL",
                        details={
                            "tool": tool_name,
                            "execution_time_ms": execution_time_ms,
                        }
                    )
                except Exception:
                    pass  # Graceful degradation
            
            return response
            
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}", exc_info=True)
            
            execution_time_ms = (time.time() - start_time) * 1000
            return MCPResponse(
                error=MCPError(
                    code=self.INTERNAL_ERROR,
                    message=str(e),
                    data={"tool": tool_name, "execution_time_ms": execution_time_ms}
                ).to_dict(),
                id=request_id
            )

    def process_request(self, request: MCPRequest) -> MCPResponse:
        """
        Process MCP request and return response.
        
        Args:
            request: MCPRequest object
            
        Returns:
            MCPResponse object
        """
        if request.method == "tools/list":
            return MCPResponse(
                result={"tools": self.list_tools()},
                id=request.id
            )
        
        elif request.method == "tools/call":
            tool_name: str = request.params.get("tool", "")
            params: Dict[str, Any] = request.params.get("params", {})
            return self.call_tool(tool_name, params, request.id)
        
        else:
            return MCPResponse(
                error=MCPError(
                    code=self.METHOD_NOT_FOUND,
                    message=f"Method not found: {request.method}"
                ).to_dict(),
                id=request.id
            )

    def process_json_rpc(self, json_str: str) -> str:
        """
        Process JSON-RPC 2.0 request string and return response string.
        
        Args:
            json_str: JSON request string
            
        Returns:
            JSON response string
        """
        try:
            request_data: Dict[str, Any] = json.loads(json_str)
            
            # Validate JSON-RPC format
            if "jsonrpc" not in request_data or request_data["jsonrpc"] != "2.0":
                error_response: MCPResponse = MCPResponse(
                    error=MCPError(
                        code=self.INVALID_REQUEST,
                        message="Invalid JSON-RPC version"
                    ).to_dict(),
                    id=request_data.get("id")
                )
                return error_response.to_json()
            
            request: MCPRequest = MCPRequest(
                jsonrpc=request_data.get("jsonrpc", "2.0"),
                method=request_data.get("method", ""),
                params=request_data.get("params", {}),
                id=request_data.get("id")
            )
            
            response: MCPResponse = self.process_request(request)
            return response.to_json()
            
        except json.JSONDecodeError as e:
            error_response: MCPResponse = MCPResponse(
                error=MCPError(
                    code=self.PARSE_ERROR,
                    message=f"JSON parse error: {e}"
                ).to_dict()
            )
            return error_response.to_json()
        except Exception as e:
            error_response: MCPResponse = MCPResponse(
                error=MCPError(
                    code=self.INTERNAL_ERROR,
                    message=str(e)
                ).to_dict()
            )
            return error_response.to_json()

    @property
    def execution_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary with execution stats
        """
        return {
            "total_executions": len(self._execution_history),
            "tools_registered": len(self._tools),
            "cache_size": len(self._response_cache),
            "execution_history": self._execution_history[-10:] if self._execution_history else [],
        }


if __name__ == "__main__":
    # Example usage
    server: MCPServer = MCPServer()
    
    # List tools
    print("Available tools:")
    print(json.dumps(server.list_tools(), indent=2))
    
    # Call a tool
    response: MCPResponse = server.call_tool(
        "sample_tool",
        {"input": "test", "mode": "demo"},
        request_id="123"
    )
    
    print("\nTool execution response:")
    print(response.to_json())
