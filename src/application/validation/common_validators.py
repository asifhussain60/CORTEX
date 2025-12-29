"""
Common validation rules for the validation framework.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import re
from typing import TypeVar, Callable, Optional, Any
from .validation_rule import ValidationRule

T = TypeVar('T')
TProperty = TypeVar('TProperty')


class NotEmptyValidator(ValidationRule[T, Any]):
    """Validates that a value is not None, empty string, or empty collection."""
    
    def is_valid(self, value: Any, instance: T) -> bool:
        """Check if value is not empty."""
        if value is None:
            return False
        if isinstance(value, str) and len(value.strip()) == 0:
            return False
        if hasattr(value, '__len__') and len(value) == 0:
            return False
        return True
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' must not be empty."


class MinLengthValidator(ValidationRule[T, Any]):
    """Validates that a string or collection has at least min_length items."""
    
    def __init__(
        self,
        property_name: str,
        property_selector: Callable[[T], Any],
        min_length: int,
        error_message: Optional[str] = None,
        condition: Optional[Callable[[T], bool]] = None
    ):
        super().__init__(property_name, property_selector, error_message, condition)
        self.min_length = min_length
    
    def is_valid(self, value: Any, instance: T) -> bool:
        """Check if value has minimum length."""
        if value is None:
            return False
        if not hasattr(value, '__len__'):
            return False
        return len(value) >= self.min_length
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' must be at least {self.min_length} characters."


class MaxLengthValidator(ValidationRule[T, Any]):
    """Validates that a string or collection has at most max_length items."""
    
    def __init__(
        self,
        property_name: str,
        property_selector: Callable[[T], Any],
        max_length: int,
        error_message: Optional[str] = None,
        condition: Optional[Callable[[T], bool]] = None
    ):
        super().__init__(property_name, property_selector, error_message, condition)
        self.max_length = max_length
    
    def is_valid(self, value: Any, instance: T) -> bool:
        """Check if value has maximum length."""
        if value is None:
            return True  # Null values pass max length check
        if not hasattr(value, '__len__'):
            return False
        return len(value) <= self.max_length
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' must be at most {self.max_length} characters."


class RegexValidator(ValidationRule[T, str]):
    """Validates that a string matches a regex pattern."""
    
    def __init__(
        self,
        property_name: str,
        property_selector: Callable[[T], str],
        pattern: str,
        error_message: Optional[str] = None,
        condition: Optional[Callable[[T], bool]] = None
    ):
        super().__init__(property_name, property_selector, error_message, condition)
        self.pattern = pattern
        self.regex = re.compile(pattern)
    
    def is_valid(self, value: str, instance: T) -> bool:
        """Check if value matches pattern."""
        if value is None:
            return False
        if not isinstance(value, str):
            return False
        return bool(self.regex.match(value))
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' does not match the required pattern."


class EmailValidator(ValidationRule[T, str]):
    """Validates that a string is a valid email address."""
    
    # Simple email regex pattern
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def is_valid(self, value: str, instance: T) -> bool:
        """Check if value is a valid email."""
        if value is None or not isinstance(value, str):
            return False
        return bool(re.match(self.EMAIL_PATTERN, value))
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' must be a valid email address."


class UrlValidator(ValidationRule[T, str]):
    """Validates that a string is a valid URL."""
    
    # Simple URL regex pattern
    URL_PATTERN = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    
    def is_valid(self, value: str, instance: T) -> bool:
        """Check if value is a valid URL."""
        if value is None or not isinstance(value, str):
            return False
        return bool(re.match(self.URL_PATTERN, value))
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' must be a valid URL."


class RangeValidator(ValidationRule[T, float]):
    """Validates that a numeric value is within a specified range."""
    
    def __init__(
        self,
        property_name: str,
        property_selector: Callable[[T], float],
        min_value: float,
        max_value: float,
        error_message: Optional[str] = None,
        condition: Optional[Callable[[T], bool]] = None
    ):
        super().__init__(property_name, property_selector, error_message, condition)
        self.min_value = min_value
        self.max_value = max_value
    
    def is_valid(self, value: float, instance: T) -> bool:
        """Check if value is within range."""
        if value is None:
            return False
        try:
            numeric_value = float(value)
            return self.min_value <= numeric_value <= self.max_value
        except (ValueError, TypeError):
            return False
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' must be between {self.min_value} and {self.max_value}."


class PredicateValidator(ValidationRule[T, Any]):
    """Validates using a custom predicate function."""
    
    def __init__(
        self,
        property_name: str,
        property_selector: Callable[[T], Any],
        predicate: Callable[[Any], bool],
        error_message: Optional[str] = None,
        condition: Optional[Callable[[T], bool]] = None
    ):
        super().__init__(property_name, property_selector, error_message, condition)
        self.predicate = predicate
    
    def is_valid(self, value: Any, instance: T) -> bool:
        """Check if value satisfies predicate."""
        try:
            return self.predicate(value)
        except Exception:
            return False
    
    def get_default_message(self) -> str:
        """Get default error message."""
        return f"'{self.property_name}' does not meet the required criteria."
