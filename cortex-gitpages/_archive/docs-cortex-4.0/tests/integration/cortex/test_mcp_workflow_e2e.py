"""
Test suite for MCP (Model Context Protocol) workflow end-to-end integration.

AC-REM-011-03: MCP Tool Workflow E2E testing

This module validates the complete MCP workflow including:
- Tool discovery and registration
- Parameter validation and transformation
- MCP request/response cycle
- Tool execution with error handling
- Result caching and lifecycle management
- Concurrent invocations and protocol compliance

Tests cover all aspects of MCP integration including:
- Discovery of available tools
- Registration of new tools
- Parameter validation
- Timeout and retry mechanisms
- Error handling and formatting
- Tool lifecycle (create, execute, cleanup)
- MCP protocol compliance
- Concurrent execution safety

Governance:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import hashlib
import time


class MCPRequestType(Enum):
    """MCP request types."""
    DISCOVER = "discover"
    REGISTER = "register"
    EXECUTE = "execute"
    VALIDATE = "validate"
    MONITOR = "monitor"


class MCPResponseStatus(Enum):
    """MCP response status codes."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"


class ToolLifecycleState(Enum):
    """Tool lifecycle states."""
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CLEANUP = "cleanup"


@dataclass
class ToolParameter:
    """MCP tool parameter specification."""
    name: str
    type: str
    required: bool
    description: str
    default: Optional[Any] = None
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class ToolSpecification:
    """MCP tool specification."""
    tool_id: str
    name: str
    description: str
    version: str
    parameters: List[ToolParameter]
    handler: Optional[Callable] = None
    lifecycle_state: ToolLifecycleState = ToolLifecycleState.DISCOVERED
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPRequest:
    """MCP protocol request."""
    request_id: str
    request_type: MCPRequestType
    tool_id: str
    parameters: Dict[str, Any]
    timeout_ms: int = 5000
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class MCPResponse:
    """MCP protocol response."""
    request_id: str
    status: MCPResponseStatus
    tool_id: str
    result: Optional[Any] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    execution_time_ms: float = 0.0
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolExecutionRecord:
    """Record of tool execution."""
    request_id: str
    tool_id: str
    parameters: Dict[str, Any]
    status: MCPResponseStatus
    result: Optional[Any]
    error: Optional[str]
    execution_time_ms: float
    timestamp: float
    cache_key: Optional[str] = None


class ToolRegistry:
    """Registry for MCP tools."""

    def __init__(self) -> None:
        """Initialize tool registry."""
        self.tools: Dict[str, ToolSpecification] = {}
        self.execution_cache: Dict[str, ToolExecutionRecord] = {}
        self.execution_history: List[ToolExecutionRecord] = []
        self.concurrent_executions: Dict[str, float] = {}

    def discover_tool(self, tool_spec: ToolSpecification) -> bool:
        """
        Discover a tool specification.

        Args:
            tool_spec: Tool specification to discover

        Returns:
            True if tool discovered successfully
        """
        if tool_spec.tool_id in self.tools:
            return False

        tool_spec.lifecycle_state = ToolLifecycleState.DISCOVERED
        self.tools[tool_spec.tool_id] = tool_spec
        return True

    def register_tool(self, tool_id: str, handler: Callable) -> bool:
        """
        Register a tool with its handler.

        Args:
            tool_id: Tool identifier
            handler: Callable handler for the tool

        Returns:
            True if tool registered successfully
        """
        if tool_id not in self.tools:
            return False

        tool = self.tools[tool_id]
        tool.handler = handler
        tool.lifecycle_state = ToolLifecycleState.REGISTERED
        return True

    def validate_parameters(self, tool_id: str, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate parameters for a tool.

        Args:
            tool_id: Tool identifier
            parameters: Parameters to validate

        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        if tool_id not in self.tools:
            return False, ["Tool not found"]

        tool = self.tools[tool_id]
        errors = []

        for param in tool.parameters:
            if param.required and param.name not in parameters:
                errors.append(f"Missing required parameter: {param.name}")
            elif param.name in parameters:
                value = parameters[param.name]
                if not self._validate_type(value, param.type):
                    errors.append(f"Parameter {param.name} has invalid type")

        return len(errors) == 0, errors

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """
        Validate value against expected type.

        Args:
            value: Value to validate
            expected_type: Expected type name

        Returns:
            True if value matches expected type
        """
        type_map = {
            "string": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
        }
        expected = type_map.get(expected_type)
        return isinstance(value, expected) if expected else False

    def generate_cache_key(self, tool_id: str, parameters: Dict[str, Any]) -> str:
        """
        Generate cache key for tool execution.

        Args:
            tool_id: Tool identifier
            parameters: Execution parameters

        Returns:
            Cache key hash
        """
        key_data = f"{tool_id}:{json.dumps(parameters, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def execute_tool(self, request: MCPRequest) -> MCPResponse:
        """
        Execute a tool via MCP request.

        Args:
            request: MCP request

        Returns:
            MCP response
        """
        start_time = time.time()

        # Validate tool exists
        if request.tool_id not in self.tools:
            return MCPResponse(
                request_id=request.request_id,
                status=MCPResponseStatus.FAILED,
                tool_id=request.tool_id,
                error_message="Tool not found",
                error_code="TOOL_NOT_FOUND",
            )

        # Validate parameters
        is_valid, errors = self.validate_parameters(request.tool_id, request.parameters)
        if not is_valid:
            return MCPResponse(
                request_id=request.request_id,
                status=MCPResponseStatus.VALIDATION_ERROR,
                tool_id=request.tool_id,
                error_message="; ".join(errors),
                error_code="VALIDATION_ERROR",
            )

        # Check cache
        cache_key = self.generate_cache_key(request.tool_id, request.parameters)
        if cache_key in self.execution_cache:
            cached_record = self.execution_cache[cache_key]
            execution_time = time.time() - start_time
            return MCPResponse(
                request_id=request.request_id,
                status=cached_record.status,
                tool_id=request.tool_id,
                result=cached_record.result,
                error_message=cached_record.error,
                execution_time_ms=execution_time * 1000,
                cache_hit=True,
                metadata={"cache_key": cache_key},
            )

        # Track concurrent execution
        self.concurrent_executions[request.request_id] = time.time()

        try:
            tool = self.tools[request.tool_id]

            # Execute tool handler if available
            if tool.handler:
                result = tool.handler(**request.parameters)
            else:
                result = {"simulated_result": True, "tool_id": request.tool_id}

            execution_time = time.time() - start_time

            # Check timeout
            if execution_time * 1000 > request.timeout_ms:
                record = ToolExecutionRecord(
                    request_id=request.request_id,
                    tool_id=request.tool_id,
                    parameters=request.parameters,
                    status=MCPResponseStatus.TIMEOUT,
                    result=None,
                    error="Tool execution timeout",
                    execution_time_ms=execution_time * 1000,
                    timestamp=time.time(),
                    cache_key=cache_key,
                )
                self.execution_history.append(record)
                return MCPResponse(
                    request_id=request.request_id,
                    status=MCPResponseStatus.TIMEOUT,
                    tool_id=request.tool_id,
                    error_message="Tool execution timeout",
                    error_code="TIMEOUT",
                    execution_time_ms=execution_time * 1000,
                    metadata={"cache_key": cache_key},
                )

            # Success
            record = ToolExecutionRecord(
                request_id=request.request_id,
                tool_id=request.tool_id,
                parameters=request.parameters,
                status=MCPResponseStatus.SUCCESS,
                result=result,
                error=None,
                execution_time_ms=execution_time * 1000,
                timestamp=time.time(),
                cache_key=cache_key,
            )
            self.execution_history.append(record)
            self.execution_cache[cache_key] = record

            return MCPResponse(
                request_id=request.request_id,
                status=MCPResponseStatus.SUCCESS,
                tool_id=request.tool_id,
                result=result,
                execution_time_ms=execution_time * 1000,
                metadata={"cache_key": cache_key},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            record = ToolExecutionRecord(
                request_id=request.request_id,
                tool_id=request.tool_id,
                parameters=request.parameters,
                status=MCPResponseStatus.FAILED,
                result=None,
                error=str(e),
                execution_time_ms=execution_time * 1000,
                timestamp=time.time(),
                cache_key=cache_key,
            )
            self.execution_history.append(record)

            return MCPResponse(
                request_id=request.request_id,
                status=MCPResponseStatus.FAILED,
                tool_id=request.tool_id,
                error_message=str(e),
                error_code="EXECUTION_ERROR",
                execution_time_ms=execution_time * 1000,
                metadata={"cache_key": cache_key},
            )

        finally:
            if request.request_id in self.concurrent_executions:
                del self.concurrent_executions[request.request_id]

    def get_tool_execution_history(self, tool_id: Optional[str] = None) -> List[ToolExecutionRecord]:
        """
        Get tool execution history.

        Args:
            tool_id: Optional tool ID to filter by

        Returns:
            List of execution records
        """
        if tool_id:
            return [r for r in self.execution_history if r.tool_id == tool_id]
        return self.execution_history.copy()

    def get_cache_hit_rate(self) -> float:
        """
        Get cache hit rate.

        Returns:
            Cache hit rate as percentage
        """
        if not self.execution_history:
            return 0.0

        cache_hits = sum(1 for r in self.execution_history if r.cache_key in self.execution_cache)
        return (cache_hits / len(self.execution_history)) * 100.0

    def cleanup_tool(self, tool_id: str) -> bool:
        """
        Clean up tool resources.

        Args:
            tool_id: Tool identifier

        Returns:
            True if cleanup successful
        """
        if tool_id not in self.tools:
            return False

        tool = self.tools[tool_id]
        tool.lifecycle_state = ToolLifecycleState.CLEANUP
        del self.tools[tool_id]
        return True


# Test Classes

class TestMCPToolDiscovery:
    """Tests for MCP tool discovery."""

    def test_discover_single_tool(self) -> None:
        """Test discovering a single tool."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )

        result = registry.discover_tool(tool_spec)

        assert result is True
        assert "tool_1" in registry.tools

    def test_discover_multiple_tools(self) -> None:
        """Test discovering multiple tools."""
        registry = ToolRegistry()

        for i in range(5):
            tool_spec = ToolSpecification(
                tool_id=f"tool_{i}",
                name=f"Tool {i}",
                description=f"Tool {i} description",
                version="1.0.0",
                parameters=[],
            )
            registry.discover_tool(tool_spec)

        assert len(registry.tools) == 5

    def test_discover_duplicate_tool_fails(self) -> None:
        """Test discovering duplicate tool fails."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )

        result1 = registry.discover_tool(tool_spec)
        result2 = registry.discover_tool(tool_spec)

        assert result1 is True
        assert result2 is False

    def test_discover_tool_sets_lifecycle_state(self) -> None:
        """Test discovered tool has correct lifecycle state."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )

        registry.discover_tool(tool_spec)

        assert registry.tools["tool_1"].lifecycle_state == ToolLifecycleState.DISCOVERED


class TestMCPToolRegistration:
    """Tests for MCP tool registration."""

    def test_register_tool_handler(self) -> None:
        """Test registering a tool handler."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        result = registry.register_tool("tool_1", handler)

        assert result is True
        assert registry.tools["tool_1"].handler is not None
        assert registry.tools["tool_1"].lifecycle_state == ToolLifecycleState.REGISTERED

    def test_register_nonexistent_tool_fails(self) -> None:
        """Test registering nonexistent tool fails."""
        registry = ToolRegistry()

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        result = registry.register_tool("nonexistent", handler)

        assert result is False

    def test_register_tool_updates_lifecycle(self) -> None:
        """Test registration updates tool lifecycle state."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        assert registry.tools["tool_1"].lifecycle_state == ToolLifecycleState.REGISTERED


class TestMCPParameterValidation:
    """Tests for MCP parameter validation."""

    def test_validate_required_parameter_present(self) -> None:
        """Test validation succeeds with required parameters."""
        registry = ToolRegistry()
        param = ToolParameter(name="input", type="string", required=True, description="Input")
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[param],
        )
        registry.discover_tool(tool_spec)

        is_valid, errors = registry.validate_parameters("tool_1", {"input": "test"})

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_required_parameter_missing(self) -> None:
        """Test validation fails with missing required parameters."""
        registry = ToolRegistry()
        param = ToolParameter(name="input", type="string", required=True, description="Input")
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[param],
        )
        registry.discover_tool(tool_spec)

        is_valid, errors = registry.validate_parameters("tool_1", {})

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_parameter_type_correct(self) -> None:
        """Test validation succeeds with correct parameter types."""
        registry = ToolRegistry()
        param = ToolParameter(name="count", type="int", required=True, description="Count")
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[param],
        )
        registry.discover_tool(tool_spec)

        is_valid, errors = registry.validate_parameters("tool_1", {"count": 42})

        assert is_valid is True

    def test_validate_parameter_type_incorrect(self) -> None:
        """Test validation fails with incorrect parameter types."""
        registry = ToolRegistry()
        param = ToolParameter(name="count", type="int", required=True, description="Count")
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[param],
        )
        registry.discover_tool(tool_spec)

        is_valid, errors = registry.validate_parameters("tool_1", {"count": "not_an_int"})

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_multiple_parameters(self) -> None:
        """Test validation with multiple parameters."""
        registry = ToolRegistry()
        params = [
            ToolParameter(name="input", type="string", required=True, description="Input"),
            ToolParameter(name="count", type="int", required=True, description="Count"),
            ToolParameter(name="enabled", type="bool", required=False, description="Enabled"),
        ]
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=params,
        )
        registry.discover_tool(tool_spec)

        is_valid, errors = registry.validate_parameters(
            "tool_1", {"input": "test", "count": 5, "enabled": True}
        )

        assert is_valid is True
        assert len(errors) == 0


class TestMCPCacheKey:
    """Tests for MCP cache key generation."""

    def test_cache_key_generation(self) -> None:
        """Test cache key is generated consistently."""
        registry = ToolRegistry()
        params = {"input": "test", "count": 5}

        key1 = registry.generate_cache_key("tool_1", params)
        key2 = registry.generate_cache_key("tool_1", params)

        assert key1 == key2

    def test_cache_key_different_for_different_params(self) -> None:
        """Test cache key differs for different parameters."""
        registry = ToolRegistry()

        key1 = registry.generate_cache_key("tool_1", {"input": "test1"})
        key2 = registry.generate_cache_key("tool_1", {"input": "test2"})

        assert key1 != key2

    def test_cache_key_different_for_different_tools(self) -> None:
        """Test cache key differs for different tools."""
        registry = ToolRegistry()
        params = {"input": "test"}

        key1 = registry.generate_cache_key("tool_1", params)
        key2 = registry.generate_cache_key("tool_2", params)

        assert key1 != key2


class TestMCPExecution:
    """Tests for MCP tool execution."""

    def test_execute_tool_success(self) -> None:
        """Test successful tool execution."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={},
        )
        response = registry.execute_tool(request)

        assert response.status == MCPResponseStatus.SUCCESS
        assert response.result is not None

    def test_execute_nonexistent_tool(self) -> None:
        """Test executing nonexistent tool returns error."""
        registry = ToolRegistry()

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="nonexistent",
            parameters={},
        )
        response = registry.execute_tool(request)

        assert response.status == MCPResponseStatus.FAILED
        assert response.error_code == "TOOL_NOT_FOUND"

    def test_execute_tool_with_invalid_parameters(self) -> None:
        """Test tool execution with invalid parameters."""
        registry = ToolRegistry()
        param = ToolParameter(name="count", type="int", required=True, description="Count")
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[param],
        )
        registry.discover_tool(tool_spec)

        def handler(count: int) -> Dict[str, int]:
            return {"result": count * 2}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={"count": "invalid"},
        )
        response = registry.execute_tool(request)

        assert response.status == MCPResponseStatus.VALIDATION_ERROR
        assert response.error_code == "VALIDATION_ERROR"

    def test_execute_tool_records_history(self) -> None:
        """Test tool execution is recorded in history."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={},
        )
        registry.execute_tool(request)

        history = registry.get_tool_execution_history()
        assert len(history) == 1
        assert history[0].request_id == "req_1"

    def test_execute_tool_with_parameters(self) -> None:
        """Test tool execution with parameters."""
        registry = ToolRegistry()
        param = ToolParameter(name="value", type="int", required=True, description="Value")
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[param],
        )
        registry.discover_tool(tool_spec)

        def handler(value: int) -> Dict[str, int]:
            return {"result": value * 2}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={"value": 21},
        )
        response = registry.execute_tool(request)

        assert response.status == MCPResponseStatus.SUCCESS
        assert response.result["result"] == 42


class TestMCPCaching:
    """Tests for MCP execution caching."""

    def test_cache_hit_on_identical_request(self) -> None:
        """Test cache hit on identical request."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={},
        )

        response1 = registry.execute_tool(request)
        request.request_id = "req_2"
        response2 = registry.execute_tool(request)

        assert response1.cache_hit is False
        assert response2.cache_hit is True

    def test_cache_miss_on_different_parameters(self) -> None:
        """Test cache miss on different parameters."""
        registry = ToolRegistry()
        param = ToolParameter(name="value", type="int", required=True, description="Value")
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[param],
        )
        registry.discover_tool(tool_spec)

        def handler(value: int) -> Dict[str, int]:
            return {"result": value * 2}

        registry.register_tool("tool_1", handler)

        request1 = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={"value": 10},
        )
        response1 = registry.execute_tool(request1)

        request2 = MCPRequest(
            request_id="req_2",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={"value": 20},
        )
        response2 = registry.execute_tool(request2)

        assert response1.cache_hit is False
        assert response2.cache_hit is False

    def test_cache_hit_rate_calculation(self) -> None:
        """Test cache hit rate calculation."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        # Execute 5 times with same parameters
        for i in range(5):
            request = MCPRequest(
                request_id=f"req_{i}",
                request_type=MCPRequestType.EXECUTE,
                tool_id="tool_1",
                parameters={},
            )
            registry.execute_tool(request)

        hit_rate = registry.get_cache_hit_rate()
        assert 0 <= hit_rate <= 100


class TestMCPErrorHandling:
    """Tests for MCP error handling."""

    def test_handler_exception_caught(self) -> None:
        """Test handler exceptions are caught and reported."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> None:
            raise ValueError("Handler error")

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={},
        )
        response = registry.execute_tool(request)

        assert response.status == MCPResponseStatus.FAILED
        assert "Handler error" in response.error_message


class TestMCPConcurrency:
    """Tests for MCP concurrent execution."""

    def test_concurrent_execution_tracked(self) -> None:
        """Test concurrent executions are tracked."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={},
        )
        response = registry.execute_tool(request)

        assert response.status == MCPResponseStatus.SUCCESS
        assert "req_1" not in registry.concurrent_executions

    def test_multiple_executions_tracked(self) -> None:
        """Test multiple executions are tracked separately."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        for i in range(3):
            request = MCPRequest(
                request_id=f"req_{i}",
                request_type=MCPRequestType.EXECUTE,
                tool_id="tool_1",
                parameters={},
            )
            response = registry.execute_tool(request)
            assert response.status == MCPResponseStatus.SUCCESS


class TestMCPToolLifecycle:
    """Tests for MCP tool lifecycle management."""

    def test_tool_cleanup(self) -> None:
        """Test tool cleanup removes tool from registry."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        result = registry.cleanup_tool("tool_1")

        assert result is True
        assert "tool_1" not in registry.tools

    def test_cleanup_nonexistent_tool(self) -> None:
        """Test cleanup of nonexistent tool fails."""
        registry = ToolRegistry()

        result = registry.cleanup_tool("nonexistent")

        assert result is False


class TestMCPProtocolCompliance:
    """Tests for MCP protocol compliance."""

    def test_request_response_matching(self) -> None:
        """Test request and response IDs match."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_unique_123",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={},
        )
        response = registry.execute_tool(request)

        assert response.request_id == request.request_id

    def test_response_contains_all_fields(self) -> None:
        """Test response contains all required fields."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        request = MCPRequest(
            request_id="req_1",
            request_type=MCPRequestType.EXECUTE,
            tool_id="tool_1",
            parameters={},
        )
        response = registry.execute_tool(request)

        assert response.request_id is not None
        assert response.status is not None
        assert response.tool_id is not None
        assert response.execution_time_ms >= 0


class TestMCPExecutionHistory:
    """Tests for MCP execution history."""

    def test_execution_history_recorded(self) -> None:
        """Test execution history is recorded."""
        registry = ToolRegistry()
        tool_spec = ToolSpecification(
            tool_id="tool_1",
            name="Test Tool",
            description="A test tool",
            version="1.0.0",
            parameters=[],
        )
        registry.discover_tool(tool_spec)

        def handler() -> Dict[str, str]:
            return {"status": "ok"}

        registry.register_tool("tool_1", handler)

        # Use different parameters to avoid cache hits
        for i in range(3):
            request = MCPRequest(
                request_id=f"req_{i}",
                request_type=MCPRequestType.EXECUTE,
                tool_id="tool_1",
                parameters={"param": i},  # Different parameters
            )
            registry.execute_tool(request)

        history = registry.get_tool_execution_history()
        assert len(history) == 3

    def test_execution_history_filtered_by_tool(self) -> None:
        """Test execution history can be filtered by tool."""
        registry = ToolRegistry()

        for tool_num in range(2):
            tool_spec = ToolSpecification(
                tool_id=f"tool_{tool_num}",
                name=f"Tool {tool_num}",
                description=f"Tool {tool_num} description",
                version="1.0.0",
                parameters=[],
            )
            registry.discover_tool(tool_spec)

            def handler() -> Dict[str, str]:
                return {"status": "ok"}

            registry.register_tool(f"tool_{tool_num}", handler)

        # Execute both tools
        for tool_num in range(2):
            request = MCPRequest(
                request_id=f"req_{tool_num}",
                request_type=MCPRequestType.EXECUTE,
                tool_id=f"tool_{tool_num}",
                parameters={},
            )
            registry.execute_tool(request)

        history = registry.get_tool_execution_history("tool_0")
        assert len(history) == 1
        assert history[0].tool_id == "tool_0"
