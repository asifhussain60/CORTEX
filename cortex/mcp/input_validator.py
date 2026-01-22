"""Input Validator - MCP tool input validation.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationType(Enum):
    """Validation types."""
    REQUIRED = "required"
    TYPE_CHECK = "type_check"
    RANGE = "range"
    PATTERN = "pattern"


@dataclass
class ValidationError:
    """Validation error."""
    parameter: str
    error_code: str
    message: str


class ToolInputValidator:
    """Validates MCP tool inputs."""
    
    @staticmethod
    def validate_input(tool_def: Any, params: Dict[str, Any]) -> Tuple[bool, List[ValidationError]]:
        """Validate input parameters against tool definition.
        
        Args:
            tool_def: ToolDefinition with parameters
            params: Input parameters dict
            
        Returns:
            Tuple of (is_valid, error_list)
        """
        errors: List[ValidationError] = []
        
        # Check required parameters
        for param in tool_def.parameters:
            if param.required and param.name not in params:
                errors.append(ValidationError(
                    parameter=param.name,
                    error_code="missing_required",
                    message=f"Required parameter '{param.name}' is missing"
                ))
        
        # Check provided parameters
        for param_name, param_value in params.items():
            # Find parameter definition
            param_def = None
            for p in tool_def.parameters:
                if p.name == param_name:
                    param_def = p
                    break
            
            if param_def is None:
                errors.append(ValidationError(
                    parameter=param_name,
                    error_code="unknown_parameter",
                    message=f"Unknown parameter '{param_name}'"
                ))
                continue
            
            # Type checking
            if param_def.type == "string" and not isinstance(param_value, str):
                errors.append(ValidationError(
                    parameter=param_name,
                    error_code="type_error",
                    message=f"Parameter '{param_name}' must be string, got {type(param_value).__name__}"
                ))
                continue
            
            if param_def.type == "number" and not isinstance(param_value, (int, float)):
                errors.append(ValidationError(
                    parameter=param_name,
                    error_code="type_error",
                    message=f"Parameter '{param_name}' must be number, got {type(param_value).__name__}"
                ))
                continue
            
            # Range checking for numbers
            if param_def.type == "number":
                if hasattr(param_def, 'min_value') and param_def.min_value is not None:
                    if param_value < param_def.min_value:
                        errors.append(ValidationError(
                            parameter=param_name,
                            error_code="range_error",
                            message=f"Parameter '{param_name}' must be >= {param_def.min_value}"
                        ))
                
                if hasattr(param_def, 'max_value') and param_def.max_value is not None:
                    if param_value > param_def.max_value:
                        errors.append(ValidationError(
                            parameter=param_name,
                            error_code="range_error",
                            message=f"Parameter '{param_name}' must be <= {param_def.max_value}"
                        ))
            
            # Enum checking
            if hasattr(param_def, 'enum') and param_def.enum:
                if param_value not in param_def.enum:
                    errors.append(ValidationError(
                        parameter=param_name,
                        error_code="enum_error",
                        message=f"Parameter '{param_name}' must be one of {param_def.enum}"
                    ))
        
        return len(errors) == 0, errors


__all__ = ["ValidationError", "ToolInputValidator", "ValidationType"]
