"""Result type for error handling.

Provides a Rust-style Result[T] type for explicit error handling without
exceptions. Supports both Ok(value) and Err(error) cases.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Generic, TypeVar, Union, Callable, Optional, Any

T = TypeVar("T")
E = TypeVar("E")
U = TypeVar("U")


class _ResultMeta(type):
    """Metaclass to make Result subscriptable."""

    def __getitem__(cls, item: Any) -> type:
        """Allow Result[T] syntax.

        Args:
            item: Type parameter.

        Returns:
            The Result class itself (type checking only).
        """
        return cls


class Ok(Generic[T], metaclass=_ResultMeta):
    """Success result containing a value."""

    def __init__(self, value: T) -> None:
        """Initialize Ok result.

        Args:
            value: The success value.
        """
        self.value = value
        self.metadata: dict[str, Any] = {}

    def is_ok(self) -> bool:
        """Check if result is Ok.

        Returns:
            True (always for Ok).
        """
        return True

    def is_err(self) -> bool:
        """Check if result is Err.

        Returns:
            False (always for Ok).
        """
        return False

    def unwrap(self) -> T:
        """Get Ok value.

        Returns:
            The contained value.
        """
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get Ok value or default.

        Args:
            default: Default value (unused for Ok).

        Returns:
            The contained value.
        """
        return self.value

    def map(self, fn: Callable[[T], U]) -> "Ok[U]":
        """Transform Ok value.

        Args:
            fn: Function to transform the value.

        Returns:
            Ok with transformed value.
        """
        return Ok(fn(self.value))

    def map_err(self, fn: Callable[[E], Any]) -> "Ok[T]":
        """Transform Err value (no-op for Ok).

        Args:
            fn: Function to transform error (unused).

        Returns:
            Self unchanged.
        """
        return self

    def __repr__(self) -> str:
        """String representation."""
        return f"Ok({self.value!r})"

    def __class_getitem__(cls, item: Any) -> type:
        """Allow subscripting for type hints.

        Args:
            item: Type parameter(s).

        Returns:
            The class itself.
        """
        return cls


class Err(Generic[E], metaclass=_ResultMeta):
    """Error result containing an error value."""

    def __init__(self, error: E) -> None:
        """Initialize Err result.

        Args:
            error: The error value.
        """
        self.error = error
        self.metadata: dict[str, Any] = {}

    def is_ok(self) -> bool:
        """Check if result is Ok.

        Returns:
            False (always for Err).
        """
        return False

    def is_err(self) -> bool:
        """Check if result is Err.

        Returns:
            True (always for Err).
        """
        return True

    def unwrap(self) -> T:
        """Get Ok value or raise exception.

        Raises:
            RuntimeError: Always (Err contains no Ok value).

        Returns:
            Never returns.
        """
        raise RuntimeError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Get Ok value or default.

        Args:
            default: Default value to return.

        Returns:
            The default value.
        """
        return default

    def map(self, fn: Callable[[T], U]) -> "Err[E]":
        """Transform Ok value (no-op for Err).

        Args:
            fn: Function to transform value (unused).

        Returns:
            Self unchanged.
        """
        return self

    def map_err(self, fn: Callable[[E], Any]) -> "Err[Any]":
        """Transform Err value.

        Args:
            fn: Function to transform the error.

        Returns:
            Err with transformed error.
        """
        return Err(fn(self.error))

    def __repr__(self) -> str:
        """String representation."""
        return f"Err({self.error!r})"

    def __class_getitem__(cls, item: Any) -> type:
        """Allow subscripting for type hints.

        Args:
            item: Type parameter(s).

        Returns:
            The class itself.
        """
        return cls



# Create a ResultType that supports subscripting
class _ResultType(metaclass=_ResultMeta):
    """Type that allows Result[T] syntax for type hints."""
    
    def __getitem__(self, item: Any) -> type:
        """Allow Result[T] subscripting.
        
        Args:
            item: Type parameter.
        
        Returns:
            Self for chaining (type hints only).
        """
        return self
    
    def __instancecheck__(self, instance: Any) -> bool:
        """Check if instance is Ok or Err."""
        return isinstance(instance, (Ok, Err))
    
    def __subclasscheck__(self, subclass: Any) -> bool:
        """Check if subclass is Ok or Err."""
        return subclass in (Ok, Err)


# Export Result as a subscriptable type
Result = _ResultType()

# For isinstance checks, make a union available
ResultUnion = Union[Ok[T], Err[E]]

__all__ = ["Result", "ResultUnion", "Ok", "Err"]
