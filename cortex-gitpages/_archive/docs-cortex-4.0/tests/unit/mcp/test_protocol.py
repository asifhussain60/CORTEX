"""Tests for MCP Protocol Implementation (AC-MCP-COMPLIANCE-001)."""
import pytest
from datetime import datetime
from src.mcp.protocol import (
    ToolParameter, ToolDefinition, MCPError, MCPResponse, 
    ErrorCode, ToolValidator
)

@pytest.fixture
def sample_parameter():
    """Create sample parameter."""
    return ToolParameter(
        name="query",
        type="string",
        description="Search query",
        required=True
    )

@pytest.fixture
def sample_definition():
    """Create sample tool definition."""
    return ToolDefinition(
        id="tool_001",
        name="search_knowledge",
        description="Search knowledge base",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True
            ),
            ToolParameter(
                name="limit",
                type="number",
                description="Result limit",
                required=False,
                default=10,
                min_value=1,
                max_value=100
            )
        ],
        version="1.0",
        tags=["search", "knowledge"]
    )

# Unit Tests - Protocol Features
def test_tool_parameter_creation(sample_parameter):
    """Test tool parameter creation."""
    assert sample_parameter.name == "query"
    assert sample_parameter.type == "string"
    assert sample_parameter.required is True

def test_tool_parameter_with_constraints():
    """Test tool parameter with constraints."""
    param = ToolParameter(
        name="count",
        type="number",
        description="Count",
        min_value=1,
        max_value=100,
        enum=[5, 10, 25, 50, 100]
    )
    assert param.min_value == 1
    assert param.max_value == 100
    assert len(param.enum) == 5

def test_tool_definition_creation(sample_definition):
    """Test tool definition creation."""
    assert sample_definition.id == "tool_001"
    assert len(sample_definition.parameters) == 2
    assert sample_definition.version == "1.0"

def test_tool_definition_with_tags():
    """Test tool definition with tags."""
    definition = ToolDefinition(
        id="tool_002",
        name="analyze",
        description="Analyze data",
        tags=["analysis", "data", "ml"]
    )
    assert "analysis" in definition.tags
    assert len(definition.tags) == 3

def test_mcp_error_creation():
    """Test MCP error creation."""
    error = MCPError(
        code=ErrorCode.INVALID_PARAMS,
        message="Missing required parameter",
        data={"param": "query"}
    )
    assert error.code == ErrorCode.INVALID_PARAMS
    assert "Missing" in error.message

def test_mcp_error_codes():
    """Test MCP error code enumeration."""
    assert ErrorCode.SUCCESS.value == "success"
    assert ErrorCode.INVALID_REQUEST.value == "invalid_request"
    assert ErrorCode.TIMEOUT.value == "timeout"
    assert ErrorCode.TOOL_NOT_FOUND.value == "tool_not_found"

def test_mcp_response_with_result():
    """Test MCP response with result."""
    response = MCPResponse(
        id="exec_001",
        result={"data": "test", "count": 42}
    )
    assert response.id == "exec_001"
    assert response.result["data"] == "test"
    assert response.error is None

def test_mcp_response_with_error():
    """Test MCP response with error."""
    error = MCPError(code=ErrorCode.EXECUTION_ERROR, message="Failed")
    response = MCPResponse(id="exec_002", error=error)
    assert response.error is not None
    assert response.error.code == ErrorCode.EXECUTION_ERROR
    assert response.result is None

def test_mcp_response_timestamp():
    """Test MCP response includes timestamp."""
    before = datetime.now()
    response = MCPResponse(id="exec_003")
    after = datetime.now()
    assert before <= response.timestamp <= after

# Validation Tests
def test_parameter_validation_string():
    """Test string parameter validation."""
    param = ToolParameter(name="text", type="string", description="Text", required=True)
    assert ToolValidator.validate_parameter(param, "hello") is True
    assert ToolValidator.validate_parameter(param, 123) is False
    assert ToolValidator.validate_parameter(param, None) is False

def test_parameter_validation_number():
    """Test number parameter validation."""
    param = ToolParameter(name="count", type="number", description="Count", required=True)
    assert ToolValidator.validate_parameter(param, 42) is True
    assert ToolValidator.validate_parameter(param, 3.14) is True
    assert ToolValidator.validate_parameter(param, "42") is False

def test_parameter_validation_boolean():
    """Test boolean parameter validation."""
    param = ToolParameter(name="enabled", type="boolean", description="Enabled")
    assert ToolValidator.validate_parameter(param, True) is True
    assert ToolValidator.validate_parameter(param, False) is True
    assert ToolValidator.validate_parameter(param, "true") is False

def test_parameter_validation_with_range():
    """Test parameter validation with min/max range."""
    param = ToolParameter(
        name="limit",
        type="number",
        description="Limit",
        min_value=1,
        max_value=100
    )
    assert ToolValidator.validate_parameter(param, 50) is True
    assert ToolValidator.validate_parameter(param, 1) is True
    assert ToolValidator.validate_parameter(param, 100) is True
    assert ToolValidator.validate_parameter(param, 0) is False
    assert ToolValidator.validate_parameter(param, 101) is False

def test_parameter_validation_with_enum():
    """Test parameter validation with enum values."""
    param = ToolParameter(
        name="level",
        type="string",
        description="Level",
        enum=["low", "medium", "high"]
    )
    assert ToolValidator.validate_parameter(param, "low") is True
    assert ToolValidator.validate_parameter(param, "medium") is True
    assert ToolValidator.validate_parameter(param, "invalid") is False

def test_parameter_validation_optional():
    """Test optional parameter validation."""
    param = ToolParameter(
        name="description",
        type="string",
        description="Description",
        required=False
    )
    assert ToolValidator.validate_parameter(param, "text") is True
    assert ToolValidator.validate_parameter(param, None) is True

def test_all_params_validation_success(sample_definition):
    """Test validation of all parameters - success case."""
    params = {"query": "test", "limit": 50}
    is_valid, msg = ToolValidator.validate_all_params(sample_definition, params)
    assert is_valid is True
    assert msg == ""

def test_all_params_validation_missing_required(sample_definition):
    """Test validation - missing required parameter."""
    params = {"limit": 50}
    is_valid, msg = ToolValidator.validate_all_params(sample_definition, params)
    assert is_valid is False
    assert "query" in msg

def test_all_params_validation_invalid_type(sample_definition):
    """Test validation - invalid parameter type."""
    params = {"query": 123}  # Should be string
    is_valid, msg = ToolValidator.validate_all_params(sample_definition, params)
    assert is_valid is False
    assert "query" in msg

def test_all_params_validation_unknown_parameter(sample_definition):
    """Test validation - unknown parameter."""
    params = {"query": "test", "unknown": "value"}
    is_valid, msg = ToolValidator.validate_all_params(sample_definition, params)
    assert is_valid is False
    assert "Unknown" in msg

def test_all_params_validation_out_of_range(sample_definition):
    """Test validation - parameter out of range."""
    params = {"query": "test", "limit": 200}  # Max is 100
    is_valid, msg = ToolValidator.validate_all_params(sample_definition, params)
    assert is_valid is False
    assert "limit" in msg

# Integration Tests
def test_complex_tool_definition():
    """Test complex tool definition."""
    definition = ToolDefinition(
        id="complex_tool",
        name="analyze_document",
        description="Analyze document",
        parameters=[
            ToolParameter(
                name="document",
                type="object",
                description="Document",
                required=True
            ),
            ToolParameter(
                name="options",
                type="object",
                description="Analysis options",
                required=False
            ),
            ToolParameter(
                name="formats",
                type="array",
                description="Output formats",
                required=False
            )
        ],
        timeout_ms=60000,
        tags=["analysis", "document", "ml"]
    )
    assert definition.timeout_ms == 60000
    assert len(definition.parameters) == 3

def test_mcp_error_recovery():
    """Test MCP error includes recovery info."""
    error = MCPError(
        code=ErrorCode.TIMEOUT,
        message="Execution timeout",
        data={
            "retry": True,
            "retry_after_ms": 5000,
            "max_retries": 3
        }
    )
    assert error.data["retry"] is True
    assert error.data["retry_after_ms"] == 5000

def test_parameter_type_coercion():
    """Test parameter type checking."""
    types_to_check = [
        ("string", "hello", True),
        ("number", 42, True),
        ("boolean", True, True),
        ("object", {}, True),
        ("array", [], True),
        ("string", 42, False),
        ("number", "42", False),
    ]
    
    for ptype, value, expected in types_to_check:
        param = ToolParameter(
            name="test",
            type=ptype,
            description="Test"
        )
        result = ToolValidator.validate_parameter(param, value)
        assert result == expected
