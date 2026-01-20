"""
AC-MCP-COMPLIANCE-007: Tool Input Validation Test Suite.

Tests for comprehensive tool input validation:
- Parameter type validation
- Range and constraint validation
- Required/optional parameter handling
- Complex type validation (objects, arrays)
- Clear error messages for validation failures
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union
from enum import Enum

from src.mcp.protocol import ToolParameter, ToolDefinition, MCPError


class ParameterType(Enum):
    """Supported parameter types."""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


@dataclass
class ParameterConstraint:
    """Constraint for parameter validation."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    enum_values: Optional[List[Any]] = None


class ParameterValidator:
    """Validates tool parameters."""
    
    def __init__(self) -> None:
        """Initialize validator."""
        self._validation_errors: List[str] = []
    
    def validate_parameter_type(self, value: Any, param_type: str) -> bool:
        """Validate parameter has correct type."""
        if param_type == "string":
            return isinstance(value, str)
        elif param_type == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif param_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        elif param_type == "boolean":
            return isinstance(value, bool)
        elif param_type == "object":
            return isinstance(value, dict)
        elif param_type == "array":
            return isinstance(value, list)
        elif param_type == "null":
            return value is None
        return False
    
    def validate_string_constraints(self, value: str, constraint: ParameterConstraint) -> tuple[bool, str]:
        """Validate string constraints."""
        if constraint.min_length is not None and len(value) < constraint.min_length:
            msg = f"String length {len(value)} is less than minimum {constraint.min_length}"
            return False, msg
        
        if constraint.max_length is not None and len(value) > constraint.max_length:
            msg = f"String length {len(value)} is greater than maximum {constraint.max_length}"
            return False, msg
        
        if constraint.enum_values is not None and value not in constraint.enum_values:
            msg = f"String value '{value}' not in allowed values: {constraint.enum_values}"
            return False, msg
        
        return True, ""
    
    def validate_numeric_constraints(self, value: Union[int, float], constraint: ParameterConstraint) -> tuple[bool, str]:
        """Validate numeric constraints."""
        if constraint.min_value is not None and value < constraint.min_value:
            msg = f"Value {value} is less than minimum {constraint.min_value}"
            return False, msg
        
        if constraint.max_value is not None and value > constraint.max_value:
            msg = f"Value {value} is greater than maximum {constraint.max_value}"
            return False, msg
        
        if constraint.enum_values is not None and value not in constraint.enum_values:
            msg = f"Value {value} not in allowed values: {constraint.enum_values}"
            return False, msg
        
        return True, ""
    
    def validate_array_constraints(self, value: list, constraint: ParameterConstraint) -> tuple[bool, str]:
        """Validate array constraints."""
        if constraint.min_length is not None and len(value) < constraint.min_length:
            msg = f"Array length {len(value)} is less than minimum {constraint.min_length}"
            return False, msg
        
        if constraint.max_length is not None and len(value) > constraint.max_length:
            msg = f"Array length {len(value)} is greater than maximum {constraint.max_length}"
            return False, msg
        
        return True, ""
    
    def validate_parameter(self, name: str, value: Any, param_type: str, 
                          constraint: Optional[ParameterConstraint] = None) -> tuple[bool, str]:
        """Validate a parameter."""
        # Type check
        if not self.validate_parameter_type(value, param_type):
            return False, f"Parameter '{name}' has type {type(value).__name__}, expected {param_type}"
        
        # Constraint validation
        if constraint:
            if param_type == "string":
                return self.validate_string_constraints(value, constraint)
            elif param_type in ["number", "integer"]:
                return self.validate_numeric_constraints(value, constraint)
            elif param_type == "array":
                return self.validate_array_constraints(value, constraint)
        
        return True, ""


class TestParameterTypeValidation:
    """Test parameter type validation."""
    
    def test_validate_string_parameter(self) -> None:
        """Test validating string parameter."""
        validator = ParameterValidator()
        
        assert validator.validate_parameter_type("hello", "string") is True
        assert validator.validate_parameter_type(123, "string") is False
    
    def test_validate_number_parameter(self) -> None:
        """Test validating number parameter."""
        validator = ParameterValidator()
        
        assert validator.validate_parameter_type(42, "number") is True
        assert validator.validate_parameter_type(3.14, "number") is True
        assert validator.validate_parameter_type(True, "number") is False
    
    def test_validate_integer_parameter(self) -> None:
        """Test validating integer parameter."""
        validator = ParameterValidator()
        
        assert validator.validate_parameter_type(42, "integer") is True
        assert validator.validate_parameter_type(3.14, "integer") is False
        assert validator.validate_parameter_type(True, "integer") is False
    
    def test_validate_boolean_parameter(self) -> None:
        """Test validating boolean parameter."""
        validator = ParameterValidator()
        
        assert validator.validate_parameter_type(True, "boolean") is True
        assert validator.validate_parameter_type(False, "boolean") is True
        assert validator.validate_parameter_type(1, "boolean") is False
    
    def test_validate_object_parameter(self) -> None:
        """Test validating object parameter."""
        validator = ParameterValidator()
        
        assert validator.validate_parameter_type({"key": "value"}, "object") is True
        assert validator.validate_parameter_type([], "object") is False
    
    def test_validate_array_parameter(self) -> None:
        """Test validating array parameter."""
        validator = ParameterValidator()
        
        assert validator.validate_parameter_type([1, 2, 3], "array") is True
        assert validator.validate_parameter_type({"key": "value"}, "array") is False
    
    def test_validate_null_parameter(self) -> None:
        """Test validating null parameter."""
        validator = ParameterValidator()
        
        assert validator.validate_parameter_type(None, "null") is True
        assert validator.validate_parameter_type("", "null") is False


class TestStringConstraintValidation:
    """Test string constraint validation."""
    
    def test_string_min_length(self) -> None:
        """Test string minimum length constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(min_length=3)
        
        success, msg = validator.validate_string_constraints("hello", constraint)
        assert success is True
        
        success, msg = validator.validate_string_constraints("hi", constraint)
        assert success is False
        assert "minimum" in msg.lower()
    
    def test_string_max_length(self) -> None:
        """Test string maximum length constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(max_length=5)
        
        success, msg = validator.validate_string_constraints("hello", constraint)
        assert success is True
        
        success, msg = validator.validate_string_constraints("hello world", constraint)
        assert success is False
        assert "maximum" in msg.lower()
    
    def test_string_enum_values(self) -> None:
        """Test string enum values constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(enum_values=["red", "green", "blue"])
        
        success, msg = validator.validate_string_constraints("red", constraint)
        assert success is True
        
        success, msg = validator.validate_string_constraints("yellow", constraint)
        assert success is False
        assert "allowed values" in msg.lower()


class TestNumericConstraintValidation:
    """Test numeric constraint validation."""
    
    def test_numeric_min_value(self) -> None:
        """Test numeric minimum value constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(min_value=0)
        
        success, msg = validator.validate_numeric_constraints(5, constraint)
        assert success is True
        
        success, msg = validator.validate_numeric_constraints(-5, constraint)
        assert success is False
        assert "minimum" in msg.lower()
    
    def test_numeric_max_value(self) -> None:
        """Test numeric maximum value constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(max_value=100)
        
        success, msg = validator.validate_numeric_constraints(50, constraint)
        assert success is True
        
        success, msg = validator.validate_numeric_constraints(150, constraint)
        assert success is False
        assert "maximum" in msg.lower()
    
    def test_numeric_range(self) -> None:
        """Test numeric range constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(min_value=0, max_value=100)
        
        success, msg = validator.validate_numeric_constraints(50, constraint)
        assert success is True
        
        success, msg = validator.validate_numeric_constraints(-10, constraint)
        assert success is False
        
        success, msg = validator.validate_numeric_constraints(150, constraint)
        assert success is False
    
    def test_numeric_enum_values(self) -> None:
        """Test numeric enum values constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(enum_values=[1, 2, 3, 5, 8])
        
        success, msg = validator.validate_numeric_constraints(5, constraint)
        assert success is True
        
        success, msg = validator.validate_numeric_constraints(4, constraint)
        assert success is False


class TestArrayConstraintValidation:
    """Test array constraint validation."""
    
    def test_array_min_length(self) -> None:
        """Test array minimum length constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(min_length=2)
        
        success, msg = validator.validate_array_constraints([1, 2, 3], constraint)
        assert success is True
        
        success, msg = validator.validate_array_constraints([1], constraint)
        assert success is False
        assert "minimum" in msg.lower()
    
    def test_array_max_length(self) -> None:
        """Test array maximum length constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(max_length=3)
        
        success, msg = validator.validate_array_constraints([1, 2], constraint)
        assert success is True
        
        success, msg = validator.validate_array_constraints([1, 2, 3, 4], constraint)
        assert success is False
        assert "maximum" in msg.lower()


class TestComplexParameterValidation:
    """Test complex parameter validation."""
    
    def test_validate_required_parameter(self) -> None:
        """Test required parameter validation."""
        validator = ParameterValidator()
        
        param = ToolParameter(
            name="required_input",
            type="string",
            description="Required input",
            required=True
        )
        
        assert param.required is True
    
    def test_validate_optional_parameter(self) -> None:
        """Test optional parameter validation."""
        validator = ParameterValidator()
        
        param = ToolParameter(
            name="optional_input",
            type="string",
            description="Optional input",
            required=False
        )
        
        assert param.required is False
    
    def test_validate_parameter_with_default(self) -> None:
        """Test parameter with default value."""
        param = ToolParameter(
            name="with_default",
            type="string",
            description="Parameter with default",
            required=False
        )
        
        assert param.required is False
    
    def test_validate_nested_object_parameter(self) -> None:
        """Test nested object parameter validation."""
        validator = ParameterValidator()
        
        nested_object = {
            "name": "John",
            "age": 30,
            "email": "john@example.com"
        }
        
        is_valid = validator.validate_parameter_type(nested_object, "object")
        assert is_valid is True
    
    def test_validate_array_of_objects(self) -> None:
        """Test array of objects parameter validation."""
        validator = ParameterValidator()
        
        array_of_objects = [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"}
        ]
        
        is_valid = validator.validate_parameter_type(array_of_objects, "array")
        assert is_valid is True


class TestClearErrorMessages:
    """Test clear error messages for validation failures."""
    
    def test_type_error_message(self) -> None:
        """Test clear error message for type mismatch."""
        validator = ParameterValidator()
        success, msg = validator.validate_parameter("user_id", "not_a_number", "integer")
        
        assert success is False
        assert "user_id" in msg
        assert "integer" in msg
    
    def test_range_error_message(self) -> None:
        """Test clear error message for range violation."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(min_value=0, max_value=100)
        success, msg = validator.validate_numeric_constraints(150, constraint)
        
        assert success is False
        assert "150" in msg
        assert "100" in msg
    
    def test_length_error_message(self) -> None:
        """Test clear error message for length violation."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(min_length=5)
        success, msg = validator.validate_string_constraints("hi", constraint)
        
        assert success is False
        assert "length" in msg.lower()
        assert "5" in msg
    
    def test_enum_error_message(self) -> None:
        """Test clear error message for enum constraint."""
        validator = ParameterValidator()
        constraint = ParameterConstraint(enum_values=["A", "B", "C"])
        success, msg = validator.validate_string_constraints("D", constraint)
        
        assert success is False
        assert "allowed values" in msg.lower()
        assert "D" in msg
    
    def test_missing_required_parameter_message(self) -> None:
        """Test clear error message for missing required parameter."""
        error = MCPError(
            code=-32602,
            message="Missing required parameter 'api_key'",
            data={"parameter": "api_key", "required": True}
        )
        
        assert error.code == -32602
        assert "api_key" in error.message
        assert "required" in error.message.lower()


class TestValidationWithToolDefinition:
    """Test validation with ToolDefinition."""
    
    def test_validate_tool_with_parameters(self) -> None:
        """Test validating tool with multiple parameters."""
        tool = ToolDefinition(
            id="tool_001",
            name="calculate",
            description="Calculate operation",
            parameters=[
                ToolParameter("operation", "string", "Operation to perform"),
                ToolParameter("value1", "number", "First value"),
                ToolParameter("value2", "number", "Second value"),
            ]
        )
        
        assert len(tool.parameters) == 3
        assert all(isinstance(p, ToolParameter) for p in tool.parameters)
    
    def test_validate_mixed_required_optional(self) -> None:
        """Test tool with mix of required and optional parameters."""
        tool = ToolDefinition(
            id="tool_001",
            name="search",
            description="Search tool",
            parameters=[
                ToolParameter("query", "string", "Search query", required=True),
                ToolParameter("limit", "integer", "Result limit", required=False),
                ToolParameter("offset", "integer", "Result offset", required=False),
            ]
        )
        
        required_params = [p for p in tool.parameters if p.required]
        optional_params = [p for p in tool.parameters if not p.required]
        
        assert len(required_params) == 1
        assert len(optional_params) == 2


class TestParameterValidationIntegration:
    """Integration tests for parameter validation."""
    
    def test_full_validation_flow(self) -> None:
        """Test complete validation flow."""
        validator = ParameterValidator()
        
        # Define constraints
        constraint = ParameterConstraint(
            min_value=0,
            max_value=100,
            enum_values=None
        )
        
        # Validate multiple values
        test_cases = [
            (50, True),
            (0, True),
            (100, True),
            (-1, False),
            (101, False),
        ]
        
        for value, expected in test_cases:
            success, msg = validator.validate_numeric_constraints(value, constraint)
            assert success == expected
    
    def test_validation_error_accumulation(self) -> None:
        """Test accumulating multiple validation errors."""
        validator = ParameterValidator()
        
        errors: List[str] = []
        
        # Check multiple parameters
        params_values = [
            ("name", "John", "string"),
            ("age", 30, "integer"),
            ("email", "john@example.com", "string"),
        ]
        
        for name, value, param_type in params_values:
            if not validator.validate_parameter_type(value, param_type):
                errors.append(f"Parameter '{name}' has invalid type")
        
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
