"""
ValidationRule base class for defining validation rules.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Callable

T = TypeVar('T')
TProperty = TypeVar('TProperty')


class ValidationRule(ABC, Generic[T, TProperty]):
    """Base class for validation rules."""
    
    def __init__(
        self,
        property_name: str,
        property_selector: Callable[[T], TProperty],
        error_message: Optional[str] = None,
        condition: Optional[Callable[[T], bool]] = None
    ):
        """
        Initialize validation rule.
        
        Args:
            property_name: Name of the property being validated
            property_selector: Function to extract property value from instance
            error_message: Custom error message (optional)
            condition: Condition that must be true for rule to apply (optional)
        """
        self.property_name = property_name
        self.property_selector = property_selector
        self._error_message = error_message
        self.condition = condition
    
    @abstractmethod
    def is_valid(self, value: TProperty, instance: T) -> bool:
        """
        Check if the property value is valid.
        
        Args:
            value: The property value to validate
            instance: The full instance being validated
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_default_message(self) -> str:
        """Get the default error message for this rule."""
        pass
    
    def get_error_message(self, value: TProperty) -> str:
        """
        Get the error message to display.
        
        Args:
            value: The property value that failed validation
            
        Returns:
            Error message string
        """
        if self._error_message:
            return self._error_message
        return self.get_default_message()
    
    def should_validate(self, instance: T) -> bool:
        """
        Check if this rule should be applied based on condition.
        
        Args:
            instance: The instance being validated
            
        Returns:
            True if rule should be validated, False to skip
        """
        if self.condition is None:
            return True
        return self.condition(instance)
    
    def validate(self, instance: T) -> tuple[bool, Optional[str]]:
        """
        Validate the rule against an instance.
        
        Args:
            instance: The instance to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if rule should be applied
        if not self.should_validate(instance):
            return (True, None)
        
        # Extract property value
        value = self.property_selector(instance)
        
        # Validate
        if self.is_valid(value, instance):
            return (True, None)
        
        return (False, self.get_error_message(value))
