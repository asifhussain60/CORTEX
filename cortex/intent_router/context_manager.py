"""Context Manager

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ConversationContext:
    """Conversation context."""
    context_id: str
    data: Dict[str, Any] = field(default_factory=dict)

__all__ = ["ConversationContext"]
