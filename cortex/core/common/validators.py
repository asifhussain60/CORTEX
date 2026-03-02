"""
cortex/common/validators.py

Unified validation patterns and decorators.

AC-REM-002-05: Consolidates validation logic across codebase.
"""

import functools
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Pattern, Type, TypeVar, Union

T = TypeVar('T')


class ValidationError(Exception):
    """Exception raised when validation fails.

    Provides clear error messages for validation failures.
    """

    def __init__(
        self,
        field: str,
        message: str,
        value: Any = None,
    ) -> None:
        """Initialize validation error.

        Args:
            field: Name of the field that failed validation
            message: Error message
            value: The invalid value (optional)
        """
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation failed for '{field}': {message}")


@dataclass
class ValidationResult:
    """
    Canonical ValidationResult - Single Source of Truth (SSOT).

    AC-ID: AC-CORE-035-VALIDATION-001
    Purpose: Eliminate 7 duplicate ValidationResult definitions across codebase.

    This is the ONLY place ValidationResult should be defined.
    All other files MUST import from this module.

    Attributes:
        is_valid: Whether validation passed (default: True)
        errors: Dict of field_name -> error_message
        warnings: Dict of field_name -> warning_message
        metadata: Additional validation metadata (file_path, context, etc.)

    Compatibility Properties:
        passed: Alias for is_valid (environment_integrity_agent compatibility)
        failures: Alias for errors (environment_integrity_agent compatibility)

    Governance: CORE-035 (Single Canonical Implementation)
    """
    is_valid: bool = True
    errors: Dict[str, str] = field(default_factory=dict)
    warnings: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        """Alias for is_valid (environment_integrity_agent compatibility)."""
        return self.is_valid and not self.errors

    @property
    def failures(self) -> Dict[str, str]:
        """Alias for errors (environment_integrity_agent compatibility)."""
        return self.errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dict with is_valid, errors, warnings, and metadata
        """
        return {
            "is_valid": self.is_valid,
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


def required(
    param_name: str,
    message: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to validate required parameter.

    Args:
        param_name: Name of required parameter
        message: Custom error message

    Returns:
        Decorated function

    Example:
        @required("name")
        def greet(name: str) -> str:
            return f"Hello, {name}"
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Wrap *func* with required-parameter validation."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Validate that the required parameter is present."""
            value = kwargs.get(param_name)
            if value is None:
                error_msg = message or f"'{param_name}' is required"
                raise ValidationError(param_name, error_msg, value)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def type_check(
    param_name: str,
    expected_type: Type,
    message: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to validate parameter type.

    Args:
        param_name: Name of parameter to check
        expected_type: Expected type for parameter
        message: Custom error message

    Returns:
        Decorated function

    Example:
        @type_check("count", int)
        def process(count: int) -> int:
            return count * 2
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Wrap *func* with type-check validation."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Validate the parameter type before calling *func*."""
            value = kwargs.get(param_name)
            if value is not None and not isinstance(value, expected_type):
                error_msg = message or (
                    f"'{param_name}' must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                raise ValidationError(param_name, error_msg, value)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def range_check(
    param_name: str,
    min_val: Optional[Union[int, float]] = None,
    max_val: Optional[Union[int, float]] = None,
    message: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to validate parameter is within range.

    Args:
        param_name: Name of parameter to check
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        message: Custom error message

    Returns:
        Decorated function

    Example:
        @range_check("age", min_val=0, max_val=150)
        def set_age(age: int) -> None:
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Wrap *func* with range-check validation."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Validate the parameter is within the allowed range."""
            value = kwargs.get(param_name)
            if value is not None:
                if min_val is not None and value < min_val:
                    error_msg = message or (
                        f"'{param_name}' must be >= {min_val}, got {value}"
                    )
                    raise ValidationError(param_name, error_msg, value)
                if max_val is not None and value > max_val:
                    error_msg = message or (
                        f"'{param_name}' must be <= {max_val}, got {value}"
                    )
                    raise ValidationError(param_name, error_msg, value)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def regex_match(
    param_name: str,
    pattern: Union[str, Pattern],
    message: Optional[str] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    r"""Decorator to validate parameter matches regex pattern.

    Args:
        param_name: Name of parameter to check
        pattern: Regex pattern to match
        message: Custom error message

    Returns:
        Decorated function

    Example:
        @regex_match("email", r"^[\w.-]+@[\w.-]+\.\w+$")
        def send_email(email: str) -> None:
            pass
    """
    if isinstance(pattern, str):
        compiled = re.compile(pattern)
    else:
        compiled = pattern

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        """Wrap *func* with regex-match validation."""
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            """Validate the parameter matches the required pattern."""
            value = kwargs.get(param_name)
            if value is not None and isinstance(value, str):
                if not compiled.match(value):
                    error_msg = message or (
                        f"'{param_name}' does not match required pattern"
                    )
                    raise ValidationError(param_name, error_msg, value)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_schema(
    data: Dict[str, Any],
    schema: Dict[str, Type],
) -> ValidationResult:
    """Validate data against a schema.

    Args:
        data: Data dictionary to validate
        schema: Schema defining required fields and types

    Returns:
        ValidationResult with is_valid and errors

    Example:
        schema = {"name": str, "age": int}
        result = validate_schema({"name": "John"}, schema)
        if not result.is_valid:
            print(result.errors)
    """
    errors: Dict[str, str] = {}

    for field_name, expected_type in schema.items():
        if field_name not in data:
            errors[field_name] = f"Missing required field: {field_name}"
        elif data[field_name] is not None and not isinstance(
            data[field_name], expected_type
        ):
            errors[field_name] = (
                f"Expected {expected_type.__name__}, "
                f"got {type(data[field_name]).__name__}"
            )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
    )
