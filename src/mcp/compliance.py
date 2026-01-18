"""MCP Compliance Testing - Comprehensive compliance validation."""
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.mcp.protocol import ToolDefinition, ErrorCode, MCPResponse, MCPError

class ComplianceLevel(Enum):
    """Compliance level."""
    FULL = "full"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"

@dataclass
class ComplianceResult:
    """Compliance check result."""
    check_name: str
    passed: bool
    message: str
    details: Dict[str, Any]

class MCPComplianceTester:
    """Tests MCP compliance."""
    
    @staticmethod
    def test_tool_definition_compliance(definition: ToolDefinition) -> Tuple[bool, List[ComplianceResult]]:
        """Test tool definition for MCP compliance."""
        results = []
        
        # Required fields
        checks = [
            ("id_present", lambda: bool(definition.id), "Tool must have an ID"),
            ("name_present", lambda: bool(definition.name), "Tool must have a name"),
            ("description_present", lambda: bool(definition.description), "Tool must have a description"),
            ("id_format", lambda: _is_valid_id(definition.id), "Tool ID must be alphanumeric with underscores"),
            ("version_present", lambda: bool(definition.version), "Tool must specify a version"),
            ("timeout_valid", lambda: definition.timeout_ms > 0, "Timeout must be > 0"),
        ]
        
        for check_name, check_fn, message in checks:
            try:
                passed = check_fn()
                results.append(ComplianceResult(
                    check_name=check_name,
                    passed=passed,
                    message=message,
                    details={}
                ))
            except Exception as e:
                results.append(ComplianceResult(
                    check_name=check_name,
                    passed=False,
                    message=f"{message} - {str(e)}",
                    details={"error": str(e)}
                ))
        
        all_passed = all(r.passed for r in results)
        return all_passed, results
    
    @staticmethod
    def test_parameter_compliance(definition: ToolDefinition) -> Tuple[bool, List[ComplianceResult]]:
        """Test parameter definitions for compliance."""
        results = []
        
        for i, param in enumerate(definition.parameters):
            # Each parameter must have required fields
            checks = [
                (f"param_{i}_name", bool(param.name), f"Parameter {i} must have a name"),
                (f"param_{i}_type", bool(param.type), f"Parameter {i} must have a type"),
                (f"param_{i}_type_valid", param.type in ["string", "number", "boolean", "object", "array"], f"Parameter {i} has invalid type"),
                (f"param_{i}_description", bool(param.description), f"Parameter {i} must have a description"),
            ]
            
            for check_name, passed, message in checks:
                results.append(ComplianceResult(
                    check_name=check_name,
                    passed=passed,
                    message=message,
                    details={"parameter": param.name}
                ))
        
        all_passed = all(r.passed for r in results)
        return all_passed, results
    
    @staticmethod
    def test_error_response_compliance(error: MCPError) -> Tuple[bool, List[ComplianceResult]]:
        """Test error response for MCP compliance."""
        results = []
        
        checks = [
            ("error_code_present", error.code is not None, "Error must have a code"),
            ("error_code_valid", isinstance(error.code, ErrorCode), "Error code must be valid ErrorCode"),
            ("error_message_present", bool(error.message), "Error must have a message"),
            ("error_message_not_empty", len(str(error.message)) > 0, "Error message must not be empty"),
        ]
        
        for check_name, passed, message in checks:
            results.append(ComplianceResult(
                check_name=check_name,
                passed=passed,
                message=message,
                details={}
            ))
        
        all_passed = all(r.passed for r in results)
        return all_passed, results
    
    @staticmethod
    def test_response_compliance(response: MCPResponse) -> Tuple[bool, List[ComplianceResult]]:
        """Test response for MCP compliance."""
        results = []
        
        checks = [
            ("response_id_present", bool(response.id), "Response must have an ID"),
            ("response_has_result_or_error", response.result is not None or response.error is not None,
             "Response must have either result or error"),
            ("response_not_both", not (response.result is not None and response.error is not None),
             "Response must not have both result and error"),
            ("response_timestamp_present", response.timestamp is not None, "Response must have a timestamp"),
        ]
        
        for check_name, passed, message in checks:
            results.append(ComplianceResult(
                check_name=check_name,
                passed=passed,
                message=message,
                details={}
            ))
        
        all_passed = all(r.passed for r in results)
        return all_passed, results
    
    @staticmethod
    def get_compliance_level(results: List[ComplianceResult]) -> ComplianceLevel:
        """Determine overall compliance level."""
        if not results:
            return ComplianceLevel.NON_COMPLIANT
        
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        
        if passed == total:
            return ComplianceLevel.FULL
        elif passed / total >= 0.8:
            return ComplianceLevel.PARTIAL
        else:
            return ComplianceLevel.NON_COMPLIANT
    
    @staticmethod
    def generate_compliance_report(
        definition: ToolDefinition,
        errors: List[MCPError] = None,
        responses: List[MCPResponse] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        if errors is None:
            errors = []
        if responses is None:
            responses = []
        
        # Test tool definition
        def_passed, def_results = MCPComplianceTester.test_tool_definition_compliance(definition)
        param_passed, param_results = MCPComplianceTester.test_parameter_compliance(definition)
        
        # Test errors if provided
        error_results = []
        for error in errors:
            passed, results = MCPComplianceTester.test_error_response_compliance(error)
            error_results.extend(results)
        
        # Test responses if provided
        response_results = []
        for response in responses:
            passed, results = MCPComplianceTester.test_response_compliance(response)
            response_results.extend(results)
        
        all_results = def_results + param_results + error_results + response_results
        
        return {
            "tool_id": definition.id,
            "timestamp": str(__import__("datetime").datetime.now()),
            "overall_level": MCPComplianceTester.get_compliance_level(all_results).value,
            "total_checks": len(all_results),
            "passed_checks": sum(1 for r in all_results if r.passed),
            "failed_checks": sum(1 for r in all_results if not r.passed),
            "pass_rate": sum(1 for r in all_results if r.passed) / len(all_results) if all_results else 0,
            "definition_compliance": {
                "passed": def_passed,
                "results": def_results
            },
            "parameter_compliance": {
                "passed": param_passed,
                "results": param_results
            },
            "error_compliance": {
                "total_errors_tested": len(errors),
                "results": error_results
            },
            "response_compliance": {
                "total_responses_tested": len(responses),
                "results": response_results
            }
        }

def _is_valid_id(tool_id: str) -> bool:
    """Check if tool ID is valid."""
    if not tool_id:
        return False
    # Allow alphanumeric and underscores
    return all(c.isalnum() or c == '_' for c in tool_id)
