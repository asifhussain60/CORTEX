"""
ValidationResult and ValidationError classes for validation framework.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ValidationError:
    """Represents a validation error for a specific property."""
    
    property_name: str
    error_message: str
    attempted_value: Optional[object] = None
    error_code: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of validation error."""
        return f"{self.property_name}: {self.error_message}"


@dataclass
class ValidationResult:
    """Result of validation operation containing errors if validation failed."""
    
    errors: List[ValidationError] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0
    
    @property
    def is_invalid(self) -> bool:
        """Check if validation failed (has errors)."""
        return len(self.errors) > 0
    
    def add_error(
        self,
        property_name: str,
        error_message: str,
        attempted_value: Optional[object] = None,
        error_code: Optional[str] = None
    ) -> None:
        """Add a validation error to the result."""
        error = ValidationError(
            property_name=property_name,
            error_message=error_message,
            attempted_value=attempted_value,
            error_code=error_code
        )
        self.errors.append(error)
    
    def get_errors_for_property(self, property_name: str) -> List[ValidationError]:
        """Get all validation errors for a specific property."""
        return [e for e in self.errors if e.property_name == property_name]
    
    def __str__(self) -> str:
        """String representation of validation result."""
        if self.is_valid:
            return "Validation succeeded"
        
        error_messages = [str(e) for e in self.errors]
        return f"Validation failed:\n  " + "\n  ".join(error_messages)
    
    @staticmethod
    def success() -> "ValidationResult":
        """Create a successful validation result with no errors."""
        return ValidationResult()
    
    @staticmethod
    def failure(errors: List[ValidationError]) -> "ValidationResult":
        """Create a failed validation result with specified errors."""
        return ValidationResult(errors=errors)
