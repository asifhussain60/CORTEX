"""Consistency Validator for Domain Brain.

Provides validation for domain consistency and integrity.

Author: CORTEX Framework
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of a validation operation.
    
    Attributes:
        is_valid: Whether validation passed.
        errors: List of error messages.
        warnings: List of warning messages.
        timestamp: Validation timestamp.
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat()
        }


class ConsistencyValidator:
    """Validates domain consistency and integrity.
    
    Ensures domains meet structural and semantic requirements.
    """
    
    def __init__(self) -> None:
        """Initialize validator."""
        self._rules: List[Dict[str, Any]] = []
        self._validation_history: List[ValidationResult] = []
    
    def validate_domain(self, domain: Any) -> ValidationResult:
        """Validate a domain for consistency.
        
        Args:
            domain: Domain object to validate.
        
        Returns:
            ValidationResult with errors and warnings.
        """
        errors = []
        warnings = []
        
        # Check required fields
        if not getattr(domain, "domain_id", None):
            errors.append("domain_id is required")
        
        if not getattr(domain, "name", None):
            errors.append("name is required")
        
        # Check entities
        entities = getattr(domain, "entities", {})
        if not entities:
            warnings.append("Domain has no entities")
        
        # Check for orphaned references
        for entity_id, entity in entities.items():
            if not getattr(entity, "name", None):
                errors.append(f"Entity {entity_id} missing name")
        
        result = ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
        self._validation_history.append(result)
        return result
    
    def validate_entity(self, entity: Any) -> ValidationResult:
        """Validate a single entity.
        
        Args:
            entity: Entity to validate.
        
        Returns:
            ValidationResult with errors and warnings.
        """
        errors = []
        warnings = []
        
        if not getattr(entity, "entity_id", None):
            errors.append("entity_id is required")
        
        if not getattr(entity, "name", None):
            errors.append("name is required")
        
        if not getattr(entity, "entity_type", None):
            errors.append("entity_type is required")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a validation rule.
        
        Args:
            rule: Rule configuration dictionary.
        """
        self._rules.append(rule)
    
    def get_validation_history(self) -> List[ValidationResult]:
        """Get validation history.
        
        Returns:
            List of past validation results.
        """
        return self._validation_history.copy()
    
    def clear_history(self) -> None:
        """Clear validation history."""
        self._validation_history.clear()


__all__ = [
    "ConsistencyValidator",
    "ValidationResult"
]
