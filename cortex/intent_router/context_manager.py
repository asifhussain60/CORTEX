"""Context Manager - Preserves conversation context across interactions.

Manages conversation state, intent history, and session context for
multi-turn conversations.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class ConversationContext:
    """Conversation context for a session.
    
    Attributes:
        session_id: Unique session identifier
        previous_intents: List of previous intents in order
        turn_count: Number of turns in conversation
        metadata: Additional context metadata
    """
    session_id: str
    previous_intents: List[str] = field(default_factory=list)
    turn_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """Manage conversation context across sessions.
    
    Provides context persistence, intent history tracking, and
    session state management for multi-turn conversations.
    
    Attributes:
        contexts: Dictionary mapping session IDs to contexts
    """
    
    def __init__(self):
        """Initialize context manager."""
        self.contexts: Dict[str, ConversationContext] = {}
    
    def get_context(self, session_id: str) -> ConversationContext:
        """Get or create context for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationContext for the session
        """
        if session_id not in self.contexts:
            self.contexts[session_id] = ConversationContext(session_id=session_id)
        return self.contexts[session_id]
    
    def update_context(self, session_id: str, intent: str) -> None:
        """Update context with new intent.
        
        Args:
            session_id: Session identifier
            intent: New intent to add to history
        """
        context = self.get_context(session_id)
        context.previous_intents.append(intent)
        context.turn_count += 1
    
    def clear_context(self, session_id: str) -> None:
        """Clear context for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.contexts:
            del self.contexts[session_id]


__all__ = ["ConversationContext", "ContextManager"]