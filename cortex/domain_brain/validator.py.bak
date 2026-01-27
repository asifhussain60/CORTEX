"""Consistency Validator for Domain Brain.

Provides validation for domain consistency and integrity.

Author: CORTEX Framework
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from cortex.common.validators import ValidationResult


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
        result = ValidationResult(is_valid=True)
        
        # Validate domain structure
        if not self._validate_structure(domain, result):
            return result
        
        # Validate domain semantics
        if not self._validate_semantics(domain, result):
            return result
            
        # Validate domain relationships
        if not self._validate_relationships(domain, result):
            return result
        
        self._validation_history.append(result)
        return result
    
    def _validate_structure(self, domain: Any, result: ValidationResult) -> bool:
        """Validate domain structure.
        
        Args:
            domain: Domain to validate.
            result: ValidationResult to populate.
            
        Returns:
            True if structure is valid.
        """
        # Check required attributes
        required_attrs = ['name', 'type', 'config']
        for attr in required_attrs:
            if not hasattr(domain, attr):
                result.errors[f'missing_{attr}'] = f"Domain missing required attribute: {attr}"
                result.is_valid = False
        
        return result.is_valid
    
    def _validate_semantics(self, domain: Any, result: ValidationResult) -> bool:
        """Validate domain semantics.
        
        Args:
            domain: Domain to validate.
            result: ValidationResult to populate.
            
        Returns:
            True if semantics are valid.
        """
        # Implement semantic validation rules
        if hasattr(domain, 'name') and not domain.name.strip():
            result.errors['empty_name'] = "Domain name cannot be empty"
            result.is_valid = False
            
        return result.is_valid
    
    def _validate_relationships(self, domain: Any, result: ValidationResult) -> bool:
        """Validate domain relationships.
        
        Args:
            domain: Domain to validate.
            result: ValidationResult to populate.
            
        Returns:
            True if relationships are valid.
        """
        # Implement relationship validation
        # This could check dependencies, constraints, etc.
        return True
    
    def get_validation_history(self) -> List[ValidationResult]:
        """Get validation history.
        
        Returns:
            List of previous validation results.
        """
        return self._validation_history.copy()
    
    def clear_history(self) -> None:
        """Clear validation history."""
        self._validation_history.clear()
    
    def add_rule(self, rule: Dict[str, Any]) -> None:
        """Add a validation rule.
        
        Args:
            rule: Rule configuration dictionary.
        """
        self._rules.append(rule)
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get current validation rules.
        
        Returns:
            List of validation rules.
        """
        return self._rules.copy()


def create_validator() -> ConsistencyValidator:
    """Create a new consistency validator.
    
    Returns:
        Configured ConsistencyValidator instance.
    """
    validator = ConsistencyValidator()
    
    # Add default rules
    default_rules = [
        {
            'name': 'structure_validation',
            'description': 'Validate domain structure',
            'enabled': True,
        },
        {
            'name': 'semantic_validation', 
            'description': 'Validate domain semantics',
            'enabled': True,
        },
        {
            'name': 'relationship_validation',
            'description': 'Validate domain relationships',
            'enabled': True,
        }
    ]
    
    for rule in default_rules:
        validator.add_rule(rule)
    
    return validator