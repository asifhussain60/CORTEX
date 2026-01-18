"""Tool Input Validation - Comprehensive validation framework."""
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

from src.mcp.protocol import ToolParameter, ToolDefinition

@dataclass
class ValidationError:
    """Validation error detail."""
    parameter: str
    error_code: str  # "type_error", "range_error", "enum_error", "required_error", "format_error"
    message: str
    received_value: Any
    expected_type: Optional[str] = None

class ToolInputValidator:
    """Comprehensive tool input validation."""
    
    @staticmethod
    def validate_input(definition: ToolDefinition, params: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """Validate all inputs. Returns (is_valid, errors)."""
        errors = []
        
        # Check required parameters
        for param in definition.parameters:
            if param.required and param.name not in params:
                errors.append(ValidationError(
                    parameter=param.name,
                    error_code="required_error",
                    message=f"Required parameter '{param.name}' is missing",
                    received_value=None
                ))
        
        # Check each parameter provided
        for key, value in params.items():
            # Check parameter exists
            param_def = None
            for p in definition.parameters:
                if p.name == key:
                    param_def = p
                    break
            
            if not param_def:
                errors.append(ValidationError(
                    parameter=key,
                    error_code="unknown_parameter",
                    message=f"Unknown parameter '{key}'",
                    received_value=value
                ))
                continue
            
            # Validate the parameter
            param_errors = ToolInputValidator._validate_parameter_value(param_def, value)
            errors.extend(param_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_parameter_value(param: ToolParameter, value: Any) -> List[ValidationError]:
        """Validate a single parameter value."""
        errors = []
        
        if value is None:
            if param.required:
                errors.append(ValidationError(
                    parameter=param.name,
                    error_code="required_error",
                    message=f"Parameter '{param.name}' cannot be null",
                    received_value=None
                ))
            return errors
        
        # Type validation
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }
        
        expected_type = type_map.get(param.type)
        if expected_type and not isinstance(value, expected_type):
            errors.append(ValidationError(
                parameter=param.name,
                error_code="type_error",
                message=f"Parameter '{param.name}' must be {param.type}, got {type(value).__name__}",
                received_value=value,
                expected_type=param.type
            ))
            return errors
        
        # Enum validation
        if param.enum and value not in param.enum:
            errors.append(ValidationError(
                parameter=param.name,
                error_code="enum_error",
                message=f"Parameter '{param.name}' must be one of {param.enum}",
                received_value=value
            ))
            return errors
        
        # Range validation
        if isinstance(value, (int, float)):
            if param.min_value is not None and value < param.min_value:
                errors.append(ValidationError(
                    parameter=param.name,
                    error_code="range_error",
                    message=f"Parameter '{param.name}' must be >= {param.min_value}",
                    received_value=value
                ))
            
            if param.max_value is not None and value > param.max_value:
                errors.append(ValidationError(
                    parameter=param.name,
                    error_code="range_error",
                    message=f"Parameter '{param.name}' must be <= {param.max_value}",
                    received_value=value
                ))
        
        return errors
    
    @staticmethod
    def get_validation_error_message(errors: List[ValidationError]) -> str:
        """Get formatted validation error message."""
        if not errors:
            return ""
        
        lines = ["Validation errors:"]
        for error in errors:
            lines.append(f"  - {error.parameter}: {error.message}")
        
        return "\n".join(lines)
    
    @staticmethod
    def get_validation_report(definition: ToolDefinition, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed validation report."""
        is_valid, errors = ToolInputValidator.validate_input(definition, params)
        
        return {
            "is_valid": is_valid,
            "total_errors": len(errors),
            "errors": [
                {
                    "parameter": e.parameter,
                    "error_code": e.error_code,
                    "message": e.message,
                    "received_value": str(e.received_value),
                    "expected_type": e.expected_type
                }
                for e in errors
            ]
        }
