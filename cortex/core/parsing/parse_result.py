"""Parse Result - Result type for parsing operations.

Defines structured result types for parsing operations with success/failure
states and error information.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Generic, TypeVar

T = TypeVar("T")


@dataclass
class ParseResult(Generic[T]):
    """Result of a parsing operation.

    Attributes:
        success: Whether parsing was successful.
        value: Parsed value if successful.
        errors: List of parsing errors if failed.
        warnings: List of warnings.
        metadata: Additional metadata.
    """

    success: bool
    value: Optional[T] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_success(self) -> bool:
        """Check if parsing was successful.

        Returns:
            True if successful, False otherwise.
        """
        return self.success and not self.errors

    def add_error(self, error: str) -> None:
        """Add an error message.

        Args:
            error: Error message to add.
        """
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message.

        Args:
            warning: Warning message to add.
        """
        self.warnings.append(warning)

    def get_value(self) -> Optional[T]:
        """Get the parsed value.

        Returns:
            Parsed value or None if parsing failed.
        """
        return self.value if self.success else None


def create_success(value: T, metadata: Dict[str, Any] = None) -> ParseResult[T]:
    """Create a successful parse result.

    Args:
        value: Parsed value.
        metadata: Optional metadata.

    Returns:
        ParseResult with success state.
    """
    return ParseResult(
        success=True,
        value=value,
        metadata=metadata or {},
    )


def create_failure(errors: List[str], metadata: Dict[str, Any] = None) -> ParseResult:
    """Create a failed parse result.

    Args:
        errors: List of error messages.
        metadata: Optional metadata.

    Returns:
        ParseResult with failure state.
    """
    return ParseResult(
        success=False,
        errors=errors,
        metadata=metadata or {},
    )


__all__ = [
    "ParseResult",
    "create_success",
    "create_failure",
]
