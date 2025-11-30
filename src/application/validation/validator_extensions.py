"""
RuleBuilder for fluent validation API with chainable methods.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from typing import TypeVar, Callable, Any, Optional, Pattern
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .validator import Validator

T = TypeVar('T')
TProperty = TypeVar('TProperty')


class RuleBuilder:
    """
    Fluent builder for creating validation rules.
    
    Supports chainable methods for common validators:
    - not_empty(): Value must not be None, empty string, or empty collection
    - min_length(min): String/collection must have at least min items
    - max_length(max): String/collection must have at most max items
    - matches(pattern): String must match regex pattern
    - must(predicate): Custom predicate must return True
    - with_message(msg): Custom error message
    - when(condition): Conditional validation
    """
    
    _property_counter = 0  # Class-level counter for unique property IDs
    
    def __init__(self, validator: "Validator[T]", property_selector: Callable[[T], Any]):
        """
        Initialize rule builder.
        
        Args:
            validator: Parent validator instance
            property_selector: Function to extract property value
        """
        self._validator = validator
        self._property_selector = property_selector
        self._property_name = self._extract_property_name(property_selector)
        self._pending_message: Optional[str] = None
        self._pending_condition: Optional[Callable[[T], bool]] = None
    
    def _extract_property_name(self, selector: Callable[[T], Any]) -> str:
        """
        Extract property name from lambda selector.
        
        Args:
            selector: Lambda function like lambda x: x.name
            
        Returns:
            Property name as string
        """
        # Try to extract from lambda code
        import inspect
        import re
        try:
            # Get the source code
            source = inspect.getsource(selector)
            # Remove any leading/trailing whitespace
            source = source.strip()
            
            # Try to match lambda pattern: lambda x: x.property_name
            match = re.search(r'lambda\s+\w+\s*:\s*\w+\.(\w+)', source)
            if match:
                return match.group(1)
            
            # Try alternative pattern with parentheses: self.rule_for(lambda x: x.prop)
            match = re.search(r'\blambda\s+\w+\s*:\s*\w+\.(\w+)\s*[\)\,]', source)
            if match:
                return match.group(1)
                
        except (OSError, TypeError, IOError):
            # getsource() fails for lambdas defined in certain contexts
            pass
        
        # If we can't extract the name, try calling the selector with a mock object
        try:
            class MockObject:
                def __getattribute__(self, name):
                    if not name.startswith('_'):
                        return name
                    return object.__getattribute__(self, name)
            
            mock = MockObject()
            result = selector(mock)  # type: ignore
            if isinstance(result, str) and not result.startswith('_'):
                return result
        except Exception:
            pass
        
        # Last resort fallback
        RuleBuilder._property_counter += 1
        return f"property_{RuleBuilder._property_counter}"
    
    def not_empty(self) -> "RuleBuilder":
        """Value must not be None, empty string, or empty collection."""
        from .common_validators import NotEmptyValidator
        rule = NotEmptyValidator(
            self._property_name,
            self._property_selector,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def min_length(self, min_length: int) -> "RuleBuilder":
        """String or collection must have at least min_length items."""
        from .common_validators import MinLengthValidator
        rule = MinLengthValidator(
            self._property_name,
            self._property_selector,
            min_length,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def max_length(self, max_length: int) -> "RuleBuilder":
        """String or collection must have at most max_length items."""
        from .common_validators import MaxLengthValidator
        rule = MaxLengthValidator(
            self._property_name,
            self._property_selector,
            max_length,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def matches(self, pattern: str) -> "RuleBuilder":
        """String must match the regex pattern."""
        from .common_validators import RegexValidator
        rule = RegexValidator(
            self._property_name,
            self._property_selector,
            pattern,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def email(self) -> "RuleBuilder":
        """Value must be a valid email address."""
        from .common_validators import EmailValidator
        rule = EmailValidator(
            self._property_name,
            self._property_selector,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def url(self) -> "RuleBuilder":
        """Value must be a valid URL."""
        from .common_validators import UrlValidator
        rule = UrlValidator(
            self._property_name,
            self._property_selector,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def range(self, min_value: float, max_value: float) -> "RuleBuilder":
        """Numeric value must be within the specified range (inclusive)."""
        from .common_validators import RangeValidator
        rule = RangeValidator(
            self._property_name,
            self._property_selector,
            min_value,
            max_value,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def must(self, predicate: Callable[[Any], bool]) -> "RuleBuilder":
        """Value must satisfy the custom predicate function."""
        from .common_validators import PredicateValidator
        rule = PredicateValidator(
            self._property_name,
            self._property_selector,
            predicate,
            self._pending_message,
            self._pending_condition
        )
        self._validator.add_rule(rule)
        # Reset pending message and condition after adding rule
        self._pending_message = None
        self._pending_condition = None
        return self
    
    def with_message(self, message: str) -> "RuleBuilder":
        """
        Set a custom error message for the previous or next rule.
        
        Args:
            message: Custom error message to display
            
        Returns:
            Self for chaining
        """
        # If called after a rule, update the last added rule
        if len(self._validator._rules) > 0:
            last_rule = self._validator._rules[-1]
            if last_rule.property_name == self._property_name:
                last_rule._error_message = message
        else:
            # Otherwise, set pending message for next rule
            self._pending_message = message
        return self
    
    def when(self, condition: Callable[[T], bool]) -> "RuleBuilder":
        """
        Apply validation rule only when condition is True.
        
        Args:
            condition: Function that returns True if rule should be applied
            
        Returns:
            Self for chaining
        """
        # If called after a rule, update the last added rule
        if len(self._validator._rules) > 0:
            last_rule = self._validator._rules[-1]
            if last_rule.property_name == self._property_name:
                last_rule.condition = condition
        else:
            # Otherwise, set pending condition for next rule
            self._pending_condition = condition
        return self
