"""MCP Compliance Testing - Validates MCP protocol compliance.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class ComplianceLevel(Enum):
    """MCP compliance levels."""
    STRICT = "strict"
    STANDARD = "standard"
    LENIENT = "lenient"


@dataclass
class ComplianceResult:
    """Result of a compliance test."""
    
    test_name: str
    passed: bool
    level: ComplianceLevel
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class MCPComplianceTester:
    """Tests MCP protocol compliance."""
    
    def __init__(self, compliance_level: ComplianceLevel = ComplianceLevel.STANDARD):
        """Initialize compliance tester.
        
        Args:
            compliance_level: Level of compliance to enforce
        """
        self.compliance_level = compliance_level
        self.test_results: List[ComplianceResult] = []
    
    def test_tool_definition(self, tool_def: Any) -> ComplianceResult:
        """Test if a tool definition is compliant.
        
        Args:
            tool_def: Tool definition to test
            
        Returns:
            ComplianceResult indicating pass/fail
        """
        result = ComplianceResult(
            test_name="tool_definition",
            passed=True,
            level=self.compliance_level,
            message="Tool definition is compliant"
        )
        
        # Check required fields
        if not hasattr(tool_def, 'name'):
            result.passed = False
            result.message = "Missing required field: name"
        elif not hasattr(tool_def, 'description'):
            result.passed = False
            result.message = "Missing required field: description"
        
        self.test_results.append(result)
        return result
    
    def test_parameter_validation(self, params: List[Any]) -> ComplianceResult:
        """Test if parameters follow MCP validation rules.
        
        Args:
            params: List of parameters to test
            
        Returns:
            ComplianceResult indicating pass/fail
        """
        result = ComplianceResult(
            test_name="parameter_validation",
            passed=True,
            level=self.compliance_level,
            message="Parameters are compliant"
        )
        
        for param in params:
            if not hasattr(param, 'name'):
                result.passed = False
                result.message = f"Parameter missing name field"
                break
            if not hasattr(param, 'type'):
                result.passed = False
                result.message = f"Parameter {param.name} missing type field"
                break
        
        self.test_results.append(result)
        return result
    
    def test_error_handling(self, error_handler: Any) -> ComplianceResult:
        """Test if error handling is compliant.
        
        Args:
            error_handler: Error handler to test
            
        Returns:
            ComplianceResult indicating pass/fail
        """
        result = ComplianceResult(
            test_name="error_handling",
            passed=True,
            level=self.compliance_level,
            message="Error handling is compliant"
        )
        
        # Check that handler has required methods
        required_methods = ['handle_error', 'get_error_summary']
        for method in required_methods:
            if not hasattr(error_handler, method):
                result.passed = False
                result.message = f"Error handler missing required method: {method}"
                break
        
        self.test_results.append(result)
        return result
    
    def run_all_tests(self, tool_def: Any, params: List[Any], error_handler: Any) -> bool:
        """Run all compliance tests.
        
        Args:
            tool_def: Tool definition
            params: Parameters
            error_handler: Error handler
            
        Returns:
            True if all tests pass
        """
        results = [
            self.test_tool_definition(tool_def),
            self.test_parameter_validation(params),
            self.test_error_handling(error_handler)
        ]
        
        return all(r.passed for r in results)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of compliance test results.
        
        Returns:
            Dictionary with test statistics
        """
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "compliance_level": self.compliance_level.value
        }
    
    @staticmethod
    def test_tool_definition_compliance(tool_def: Any) -> tuple:
        """Test tool definition compliance.
        
        Args:
            tool_def: Tool definition to test
            
        Returns:
            Tuple of (passed: bool, results: List[ComplianceResult])
        """
        results = []
        
        # Check ID
        result = ComplianceResult(
            test_name="tool_definition_id",
            passed=True,
            level=ComplianceLevel.STANDARD,
            message="Tool ID is present"
        )
        if not hasattr(tool_def, 'id') or not tool_def.id:
            result.passed = False
            result.message = "Tool definition missing required ID"
        results.append(result)
        
        # Check name
        result = ComplianceResult(
            test_name="tool_definition_name",
            passed=True,
            level=ComplianceLevel.STANDARD,
            message="Tool name is present"
        )
        if not hasattr(tool_def, 'name') or not tool_def.name:
            result.passed = False
            result.message = "Tool definition missing required name"
        results.append(result)
        
        # Check description
        result = ComplianceResult(
            test_name="tool_definition_description",
            passed=True,
            level=ComplianceLevel.STANDARD,
            message="Tool description is present"
        )
        if not hasattr(tool_def, 'description') or not tool_def.description:
            result.passed = False
            result.message = "Tool definition missing required description"
        results.append(result)
        
        passed = all(r.passed for r in results)
        return passed, results
    
    @staticmethod
    def test_parameter_compliance(tool_def: Any) -> tuple:
        """Test parameter compliance.
        
        Args:
            tool_def: Tool definition to test
            
        Returns:
            Tuple of (passed: bool, results: List[ComplianceResult])
        """
        results = []
        
        result = ComplianceResult(
            test_name="parameter_compliance",
            passed=True,
            level=ComplianceLevel.STANDARD,
            message="Parameters are compliant"
        )
        
        if hasattr(tool_def, 'parameters'):
            for param in tool_def.parameters:
                if not hasattr(param, 'name'):
                    result.passed = False
                    result.message = "Parameter missing name"
                    break
        
        results.append(result)
        passed = all(r.passed for r in results)
        return passed, results
    
    @staticmethod
    def test_error_response_compliance(error: Any) -> tuple:
        """Test error response compliance.
        
        Args:
            error: Error response to test
            
        Returns:
            Tuple of (passed: bool, results: List[ComplianceResult])
        """
        results = []
        
        # Check code
        result = ComplianceResult(
            test_name="error_response_code",
            passed=True,
            level=ComplianceLevel.STANDARD,
            message="Error code is present"
        )
        if not hasattr(error, 'code') or error.code is None:
            result.passed = False
            result.message = "Error response missing required code"
        results.append(result)
        
        # Check message
        result = ComplianceResult(
            test_name="error_response_message",
            passed=True,
            level=ComplianceLevel.STANDARD,
            message="Error message is present"
        )
        if not hasattr(error, 'message') or not error.message:
            result.passed = False
            result.message = "Error response missing required message"
        results.append(result)
        
        passed = all(r.passed for r in results)
        return passed, results


__all__ = ["MCPComplianceTester", "ComplianceLevel", "ComplianceResult"]
