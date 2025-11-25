"""
Validator base class with fluent API for validation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from typing import Generic, TypeVar, List, Callable, Any
from .validation_result import ValidationResult
from .validation_rule import ValidationRule

T = TypeVar('T')


class Validator(Generic[T]):
    """
    Base validator class with fluent API for defining validation rules.
    
    Example:
        class UserValidator(Validator[User]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.name) \\
                    .not_empty() \\
                    .min_length(3) \\
                    .max_length(100)
                
                self.rule_for(lambda x: x.email) \\
                    .not_empty() \\
                    .email()
    """
    
    def __init__(self):
        """Initialize validator with empty rule list."""
        self._rules: List[ValidationRule] = []
    
    def rule_for(self, property_selector: Callable[[T], Any]) -> "RuleBuilder":
        """
        Start defining a validation rule for a property.
        
        Args:
            property_selector: Lambda function to select property (e.g., lambda x: x.name)
            
        Returns:
            RuleBuilder for chaining validation methods
        """
        from .validator_extensions import RuleBuilder
        return RuleBuilder(self, property_selector)
    
    def add_rule(self, rule: ValidationRule) -> None:
        """
        Add a validation rule to this validator.
        
        Args:
            rule: ValidationRule instance to add
        """
        self._rules.append(rule)
    
    def validate(self, instance: T) -> ValidationResult:
        """
        Validate an instance against all defined rules.
        
        Args:
            instance: The instance to validate
            
        Returns:
            ValidationResult containing any validation errors
        """
        result = ValidationResult()
        
        for rule in self._rules:
            is_valid, error_message = rule.validate(instance)
            if not is_valid:
                result.add_error(
                    property_name=rule.property_name,
                    error_message=error_message,
                    attempted_value=rule.property_selector(instance)
                )
        
        return result
    
    async def validate_async(self, instance: T) -> ValidationResult:
        """
        Validate an instance asynchronously (for I/O-bound validation).
        
        Args:
            instance: The instance to validate
            
        Returns:
            ValidationResult containing any validation errors
        """
        # For now, delegate to synchronous validation
        # Async rules can be added later by checking isinstance(rule, AsyncValidationRule)
        return self.validate(instance)
