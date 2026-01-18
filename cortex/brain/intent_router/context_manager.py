"""AC-PHX-007-05: Intent Context Preservation"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ConversationContext:
    """Preserves conversation context across turns."""
    previous_intents: list = field(default_factory=list)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    turn_count: int = 0

class ContextManager:
    """Manages intent context across conversation turns."""
    def __init__(self) -> None:
        self.context_cache: Dict[str, ConversationContext] = {}
    
    def get_context(self, session_id: str) -> ConversationContext:
        """Get or create context for session."""
        if session_id not in self.context_cache:
            self.context_cache[session_id] = ConversationContext()
        return self.context_cache[session_id]
    
    def update_context(self, session_id: str, intent: str) -> None:
        """Update context with new intent."""
        context = self.get_context(session_id)
        context.previous_intents.append(intent)
        context.turn_count += 1
