"""Turn Response Generator - Generates formatted responses for turns.

Orchestrates generation of response content for conversation turns.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseFormat(Enum):
    """Response format types."""

    STRUCTURED = "structured"
    FREE_FORM = "free_form"
    HYBRID = "hybrid"
    MINIMAL = "minimal"


@dataclass
class ResponseContent:
    """Response content container.

    Attributes:
        text: Main response text.
        format: Response format.
        metadata: Optional metadata.
        citations: List of citations.
        confidence: Confidence score (0-1).
    """

    text: str
    format: ResponseFormat = ResponseFormat.STRUCTURED
    metadata: Dict[str, Any] = field(default_factory=dict)
    citations: List[str] = field(default_factory=list)
    confidence: float = 1.0


class TurnResponseGenerator:
    """Generates responses for conversation turns."""

    def __init__(self, format_type: ResponseFormat = ResponseFormat.STRUCTURED) -> None:
        """Initialize response generator.

        Args:
            format_type: Default response format.
        """
        self.format_type = format_type
        self.generated_responses: List[ResponseContent] = []

    def generate(
        self,
        content: str,
        format_type: Optional[ResponseFormat] = None,
        metadata: Optional[Dict[str, Any]] = None,
        citations: Optional[List[str]] = None,
        confidence: float = 1.0,
    ) -> ResponseContent:
        """Generate a response.

        Args:
            content: Main response content.
            format_type: Override format type.
            metadata: Optional metadata.
            citations: Optional citations.
            confidence: Confidence score.

        Returns:
            ResponseContent.
        """
        fmt = format_type or self.format_type
        response = ResponseContent(
            text=content,
            format=fmt,
            metadata=metadata or {},
            citations=citations or [],
            confidence=confidence,
        )
        self.generated_responses.append(response)
        return response

    def get_last_response(self) -> Optional[ResponseContent]:
        """Get last generated response.

        Returns:
            Last ResponseContent or None.
        """
        return self.generated_responses[-1] if self.generated_responses else None

    def get_response_count(self) -> int:
        """Get count of generated responses.

        Returns:
            Number of responses.
        """
        return len(self.generated_responses)


# Alias for backward compatibility
ResponseGenerator = TurnResponseGenerator

__all__ = ["TurnResponseGenerator", "ResponseGenerator", "ResponseContent", "ResponseFormat"]
