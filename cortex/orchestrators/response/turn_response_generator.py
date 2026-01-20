"""Turn Response Generator

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ResponseMetadata:
    """Response metadata."""
    response_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TurnResponse:
    """Turn response."""
    turn_id: str
    content: str
    metadata: ResponseMetadata = None

__all__ = ["ResponseMetadata", "TurnResponse"]
