"""Response Formatter - Formats responses for display.

Formats and structures responses for different output targets.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from enum import Enum


class FormatterType(Enum):
    """Response formatter types."""

    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    HTML = "html"


@dataclass
class FormattedResponse:
    """Formatted response output.

    Attributes:
        formatter_type: Format type.
        content: Formatted content.
        metadata: Metadata about formatting.
        validation_errors: Any validation errors.
    """

    formatter_type: FormatterType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)


class LensResponseFormatter:
    """Formats responses using LENS framework."""

    def __init__(self, default_format: FormatterType = FormatterType.JSON) -> None:
        """Initialize response formatter.

        Args:
            default_format: Default formatter type.
        """
        self.default_format = default_format
        self.formatted_responses: List[FormattedResponse] = []

    def format(
        self,
        content: str,
        format_type: Optional[FormatterType] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FormattedResponse:
        """Format content.

        Args:
            content: Content to format.
            format_type: Override format type.
            metadata: Optional metadata.

        Returns:
            FormattedResponse.
        """
        fmt = format_type or self.default_format
        formatted = FormattedResponse(
            formatter_type=fmt, content=content, metadata=metadata or {}
        )
        self.formatted_responses.append(formatted)
        return formatted

    def format_as_json(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> FormattedResponse:
        """Format as JSON.

        Args:
            content: Content to format.
            metadata: Optional metadata.

        Returns:
            FormattedResponse.
        """
        return self.format(content, FormatterType.JSON, metadata)

    def format_as_yaml(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> FormattedResponse:
        """Format as YAML.

        Args:
            content: Content to format.
            metadata: Optional metadata.

        Returns:
            FormattedResponse.
        """
        return self.format(content, FormatterType.YAML, metadata)

    def format_as_markdown(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> FormattedResponse:
        """Format as Markdown.

        Args:
            content: Content to format.
            metadata: Optional metadata.

        Returns:
            FormattedResponse.
        """
        return self.format(content, FormatterType.MARKDOWN, metadata)

    def get_formatted_count(self) -> int:
        """Get count of formatted responses.

        Returns:
            Number of formatted responses.
        """
        return len(self.formatted_responses)


# Alias for backward compatibility
ResponseFormatter = LensResponseFormatter
LENSResponseFormatter = LensResponseFormatter

__all__ = [
    "LensResponseFormatter",
    "ResponseFormatter",
    "LENSResponseFormatter",
    "FormattedResponse",
    "FormatterType",
]
