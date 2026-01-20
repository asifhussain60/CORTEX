"""Input Validator - MCP tool input validation.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ValidationType(Enum):
    """Validation types."""
    REQUIRED = "required"
    TYPE_CHECK = "type_check"
    RANGE = "range"
    PATTERN = "pattern"


@dataclass
class ValidationRule:
    """Validation rule."""
    field_name: str
    validation_type: ValidationType
    expected_type: Optional[type] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    pattern: Optional[str] = None


class ValidationError(Exception):
    """Validation error."""
    
    def __init__(self, message: str, field: Optional[str] = None, errors: Optional[List[str]] = None):
        """Initialize validation error."""
        super().__init__(message)
        self.field = field
        self.errors = errors or []


class ToolInputValidator:
    """Validates MCP tool inputs."""
    
    def __init__(self):
        """Initialize validator."""
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add validation rule."""
        self.rules.append(rule)
    
    def validate(self, inputs: Dict[str, Any]) -> None:
        """Validate inputs against rules.
        
        Args:
            inputs: Input dictionary to validate.
            
        Raises:
            ValidationError: If validation fails.
        """
        errors = []
        
        for rule in self.rules:
            if rule.validation_type == ValidationType.REQUIRED:
                if rule.field_name not in inputs:
                    errors.append(f"Required field '{rule.field_name}' is missing")
            
            elif rule.validation_type == ValidationType.TYPE_CHECK:
                if rule.field_name in inputs and rule.expected_type:
                    if not isinstance(inputs[rule.field_name], rule.expected_type):
                        errors.append(
                            f"Field '{rule.field_name}' must be of type {rule.expected_type.__name__}"
                        )
        
        if errors:
            raise ValidationError("Validation failed", errors=errors)


__all__ = ["ValidationRule", "ValidationType", "ValidationError", "ToolInputValidator"]
