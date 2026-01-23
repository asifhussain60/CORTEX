"""
Conversation Orchestrator - Multi-turn conversation management.

Handles multi-turn conversation state, context persistence, and cancellation.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any


class ConversationOrchestrator:
    """
    Manages multi-turn conversations with state persistence and cancellation.
    """

    def __init__(self, timeout_seconds: float = 300.0) -> None:
        """Initialize the conversation orchestrator."""
        self.session_id = str(uuid.uuid4())
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_context: Dict[str, Any] = {}
        self.is_cancelled = False
        self.timeout_seconds = timeout_seconds
        self.created_at = datetime.now()

    def process_turn(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single conversation turn.
        
        Args:
            request: Turn request with user_input, context, turn_number.
            
        Returns:
            Response with output, context, and metadata.
        """
        if self.is_cancelled:
            return {"error": "Conversation is cancelled"}

        turn_number = request.get("turn_number", len(self.conversation_history) + 1)
        user_input = request.get("user_input", "")
        context = request.get("context", {})

        # Merge contexts
        self.current_context.update(context)

        # Store in history
        turn_record = {
            "turn_number": turn_number,
            "user_input": user_input,
            "context": dict(self.current_context),
            "timestamp": datetime.now().isoformat(),
        }
        self.conversation_history.append(turn_record)

        # Generate response
        response = {
            "turn_number": turn_number,
            "output": f"Response to: {user_input}",
            "context": dict(self.current_context),
            "success": True,
            "timeout_exceeded": False,
        }

        return response

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history."""
        return list(self.conversation_history)

    def cancel_conversation(self) -> bool:
        """Cancel the current conversation."""
        self.is_cancelled = True
        return True
