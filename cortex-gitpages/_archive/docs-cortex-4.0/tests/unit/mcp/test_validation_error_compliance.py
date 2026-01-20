"""Tests for Input Validation, Error Handling, and Compliance."""
import pytest
from src.mcp.protocol import ToolDefinition, ToolParameter, ErrorCode, MCPError, MCPResponse
from src.mcp.input_validator import ToolInputValidator, ValidationError
from src.mcp.error_handler import MCPErrorHandler, ErrorThrottler, ErrorRecoveryStrategy
from src.mcp.compliance import MCPComplianceTester, ComplianceLevel

# ===== INPUT VALIDATION TESTS =====

@pytest.fixture
def sample_definition():
    """Create sample tool definition."""
    return ToolDefinition(
        id="test_tool",
        name="test_op",
        description="Test operation",
        parameters=[
            ToolParameter(name="query", type="string", description="Query", required=True),
            ToolParameter(name="limit", type="number", description="Limit", required=False, min_value=1, max_value=100, default=10),
            ToolParameter(name="mode", type="string", description="Mode", enum=["fast", "slow", "medium"]),
        ]
    )

def test_validate_input_success(sample_definition):
    """Test successful input validation."""
    params = {"query": "test", "limit": 50}
    is_valid, errors = ToolInputValidator.validate_input(sample_definition, params)
    assert is_valid is True
    assert len(errors) == 0

def test_validate_input_missing_required(sample_definition):
    """Test validation with missing required parameter."""
    params = {}
    is_valid, errors = ToolInputValidator.validate_input(sample_definition, params)
    assert is_valid is False
    assert len(errors) > 0
    assert any(e.parameter == "query" for e in errors)

def test_validate_input_type_error(sample_definition):
    """Test validation with type error."""
    params = {"query": 123}  # Should be string
    is_valid, errors = ToolInputValidator.validate_input(sample_definition, params)
    assert is_valid is False
    assert any(e.error_code == "type_error" for e in errors)

def test_validate_input_range_error(sample_definition):
    """Test validation with range error."""
    params = {"query": "test", "limit": 200}  # Max is 100
    is_valid, errors = ToolInputValidator.validate_input(sample_definition, params)
    assert is_valid is False
    assert any(e.error_code == "range_error" for e in errors)

def test_validate_input_enum_error(sample_definition):
    """Test validation with enum error."""
    params = {"query": "test", "mode": "invalid"}
    is_valid, errors = ToolInputValidator.validate_input(sample_definition, params)
    assert is_valid is False
    assert any(e.error_code == "enum_error" for e in errors)

def test_validate_input_unknown_parameter(sample_definition):
    """Test validation with unknown parameter."""
    params = {"query": "test", "unknown": "value"}
    is_valid, errors = ToolInputValidator.validate_input(sample_definition, params)
    assert is_valid is False
    assert any(e.error_code == "unknown_parameter" for e in errors)

def test_get_validation_error_message(sample_definition):
    """Test getting formatted error message."""
    params = {"limit": 200}  # Missing required and out of range
    is_valid, errors = ToolInputValidator.validate_input(sample_definition, params)
    message = ToolInputValidator.get_validation_error_message(errors)
    assert "Validation errors:" in message
    assert len(message) > 0

def test_get_validation_report(sample_definition):
    """Test getting validation report."""
    params = {"query": "test", "limit": 500}
    report = ToolInputValidator.get_validation_report(sample_definition, params)
    assert "is_valid" in report
    assert "total_errors" in report
    assert "errors" in report

# ===== ERROR HANDLING TESTS =====

def test_handle_value_error():
    """Test handling ValueError."""
    exc = ValueError("Invalid value")
    error = MCPErrorHandler.handle_exception(exc)
    assert error.code == ErrorCode.INVALID_PARAMS

def test_handle_timeout_error():
    """Test handling TimeoutError."""
    exc = TimeoutError("Execution timeout")
    error = MCPErrorHandler.handle_exception(exc)
    assert error.code == ErrorCode.TIMEOUT

def test_handle_exception_with_context():
    """Test handling exception with context."""
    exc = RuntimeError("Test error")
    context = {"tool_id": "test_tool"}
    error = MCPErrorHandler.handle_exception(exc, context)
    assert error.data is not None
    assert "context" in error.data

def test_get_recovery_strategy():
    """Test getting recovery strategy."""
    strategy = MCPErrorHandler.get_recovery_strategy(ErrorCode.TIMEOUT)
    assert strategy is not None
    assert strategy.retry is True
    assert strategy.exponential_backoff is True

def test_validate_error_response():
    """Test validating error response."""
    valid_error = MCPError(code=ErrorCode.INVALID_PARAMS, message="Test error")
    assert MCPErrorHandler.validate_error_response(valid_error) is True
    
    invalid_error = MCPError(code=None, message="Test")
    assert MCPErrorHandler.validate_error_response(invalid_error) is False

def test_error_throttler_record():
    """Test error throttler recording errors."""
    throttler = ErrorThrottler(threshold=3)
    assert throttler.record_error("tool_1") is False
    assert throttler.record_error("tool_1") is False
    assert throttler.record_error("tool_1") is False
    assert throttler.record_error("tool_1") is True  # Threshold exceeded

def test_error_throttler_get_error_rate():
    """Test getting error rate."""
    throttler = ErrorThrottler()
    for _ in range(5):
        throttler.record_error("tool_1")
    rate = throttler.get_error_rate("tool_1")
    assert rate >= 0

def test_error_throttler_is_throttled():
    """Test throttle status."""
    throttler = ErrorThrottler(threshold=2)
    throttler.record_error("tool_1")
    throttler.record_error("tool_1")
    throttler.record_error("tool_1")  # Need 3 to exceed threshold of 2
    assert throttler.is_throttled("tool_1") is True

def test_error_throttler_reset():
    """Test resetting throttler."""
    throttler = ErrorThrottler(threshold=2)
    throttler.record_error("tool_1")
    throttler.record_error("tool_1")
    throttler.reset("tool_1")
    assert throttler.is_throttled("tool_1") is False

# ===== COMPLIANCE TESTING TESTS =====

def test_tool_definition_compliance_valid(sample_definition):
    """Test valid tool definition compliance."""
    passed, results = MCPComplianceTester.test_tool_definition_compliance(sample_definition)
    assert passed is True
    assert all(r.passed for r in results)

def test_tool_definition_compliance_missing_id():
    """Test tool definition without ID."""
    definition = ToolDefinition(id="", name="test", description="test")
    passed, results = MCPComplianceTester.test_tool_definition_compliance(definition)
    assert passed is False

def test_parameter_compliance_valid(sample_definition):
    """Test valid parameter compliance."""
    passed, results = MCPComplianceTester.test_parameter_compliance(sample_definition)
    assert passed is True

def test_error_response_compliance_valid():
    """Test valid error response compliance."""
    error = MCPError(code=ErrorCode.INVALID_PARAMS, message="Invalid parameters")
    passed, results = MCPComplianceTester.test_error_response_compliance(error)
    assert passed is True
    assert all(r.passed for r in results)

def test_error_response_compliance_missing_code():
    """Test error response without code."""
    error = MCPError(code=None, message="Test")
    passed, results = MCPComplianceTester.test_error_response_compliance(error)
    assert passed is False

def test_response_compliance_valid():
    """Test valid response compliance."""
    response = MCPResponse(id="exec_001", result={"status": "ok"})
    passed, results = MCPComplianceTester.test_response_compliance(response)
    assert passed is True

def test_response_compliance_both_result_and_error():
    """Test response with both result and error."""
    error = MCPError(code=ErrorCode.INTERNAL_ERROR, message="Error")
    response = MCPResponse(id="exec_001", result={"data": "ok"}, error=error)
    passed, results = MCPComplianceTester.test_response_compliance(response)
    assert passed is False

def test_get_compliance_level_full():
    """Test compliance level FULL."""
    from src.mcp.compliance import ComplianceResult
    results = [
        ComplianceResult("check1", True, "Pass", {}),
        ComplianceResult("check2", True, "Pass", {}),
    ]
    level = MCPComplianceTester.get_compliance_level(results)
    assert level == ComplianceLevel.FULL

def test_get_compliance_level_partial():
    """Test compliance level PARTIAL."""
    from src.mcp.compliance import ComplianceResult
    results = [
        ComplianceResult("check1", True, "Pass", {}),
        ComplianceResult("check2", True, "Pass", {}),
        ComplianceResult("check3", True, "Pass", {}),
        ComplianceResult("check4", True, "Pass", {}),
        ComplianceResult("check5", False, "Fail", {}),
    ]
    level = MCPComplianceTester.get_compliance_level(results)
    assert level == ComplianceLevel.PARTIAL

def test_generate_compliance_report(sample_definition):
    """Test generating compliance report."""
    report = MCPComplianceTester.generate_compliance_report(sample_definition)
    assert "tool_id" in report
    assert "overall_level" in report
    assert "total_checks" in report
    assert "pass_rate" in report
    assert report["tool_id"] == "test_tool"

def test_compliance_report_with_errors(sample_definition):
    """Test compliance report with errors."""
    error = MCPError(code=ErrorCode.INVALID_PARAMS, message="Invalid params")
    report = MCPComplianceTester.generate_compliance_report(sample_definition, errors=[error])
    assert report["error_compliance"]["total_errors_tested"] == 1

def test_compliance_report_with_responses(sample_definition):
    """Test compliance report with responses."""
    response = MCPResponse(id="exec_001", result={"status": "ok"})
    report = MCPComplianceTester.generate_compliance_report(sample_definition, responses=[response])
    assert report["response_compliance"]["total_responses_tested"] == 1
