"""Turn Response Generator

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from enum import Enum


class ResponseMode(Enum):
    """Response generation mode."""
    BRIEF = "brief"
    DETAILED = "detailed"
    TECHNICAL = "technical"


class ResponseTone(Enum):
    """Response tone."""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"


class ResponseFormat(Enum):
    """Response format."""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


@dataclass
class ResponseMetadata:
    """Response metadata."""
    response_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseContent:
    """Response content."""
    text: str
    format: str = "plain"
    metadata: dict = field(default_factory=dict)


@dataclass
class ResponseSegment:
    """Response segment."""
    segment_id: str
    content: str
    segment_type: str = "text"


@dataclass
class TurnResponse:
    """Turn response."""
    turn_id: str
    content: str
    metadata: ResponseMetadata = None


@dataclass
class ResponseGenerator:
    """Response generator."""
    mode: ResponseMode = ResponseMode.BRIEF
    
    def generate(self, input: str) -> str:
        """Generate response."""
        return f"Generated: {input}"



class TurnResponseGenerator:
    """Generate turn responses."""
    
    def generate(self, turn_id: str, content: str) -> TurnResponse:
        """Generate response."""
        metadata = ResponseMetadata(response_id=f"{turn_id}_resp")
        return TurnResponse(turn_id=turn_id, content=content, metadata=metadata)

__all__ = ["ResponseMetadata", "TurnResponse", "TurnResponseGenerator"]
