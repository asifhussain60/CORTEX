"""
Context aggregation for multi-turn conversations.

Aggregates previous outputs and context across turns, enabling
"remember what I said 3 turns ago" queries.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TurnContext:
    """Context from a single turn."""
    
    turn_number: int
    user_input: str
    orchestrator_output: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: datetime


class ContextAggregator:
    """
    Aggregates context across conversation turns.
    
    Merges previous outputs into next turn's context, preserving
    conversation history and enabling cross-turn references.
    """
    
    def __init__(self, max_history_turns: int = 3):
        """
        Initialize context aggregator.
        
        Args:
            max_history_turns: Maximum number of turns to keep in history
                             (default: 3 for token optimization, was 10)
        """
        self.max_history_turns = max_history_turns
        self.turn_history: List[TurnContext] = []
    
    def add_turn(
        self,
        turn_number: int,
        user_input: str,
        orchestrator_output: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """
        Add a turn to the history.
        
        Args:
            turn_number: Turn number
            user_input: User's input for this turn
            orchestrator_output: Orchestrator's output
            context: Context state for this turn
        """
        turn_context = TurnContext(
            turn_number=turn_number,
            user_input=user_input,
            orchestrator_output=orchestrator_output,
            context=context,
            timestamp=datetime.now()
        )
        
        self.turn_history.append(turn_context)
        
        # Trim history if needed
        if len(self.turn_history) > self.max_history_turns:
            self.turn_history = self.turn_history[-self.max_history_turns:]
    
    def aggregate_context(
        self,
        current_user_input: str,
        base_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate context from history into current turn's context.
        
        Args:
            current_user_input: Current user input
            base_context: Base context to merge with history
            
        Returns:
            Aggregated context with history
        """
        aggregated = base_context.copy() if base_context else {}
        
        # Add conversation history summary
        aggregated["conversation_history"] = [
            {
                "turn": tc.turn_number,
                "user_input": tc.user_input[:100] + "..." if len(tc.user_input) > 100 else tc.user_input,
                "output_summary": self._summarize_output(tc.orchestrator_output),
                "timestamp": tc.timestamp.isoformat()
            }
            for tc in self.turn_history
        ]
        
        # Add previous outputs (for carryover)
        if self.turn_history:
            last_turn = self.turn_history[-1]
            aggregated["previous_output"] = last_turn.orchestrator_output
            aggregated["previous_context"] = last_turn.context
        
        # Add current input
        aggregated["current_user_input"] = current_user_input
        aggregated["total_turns_in_conversation"] = len(self.turn_history)
        
        # Merge any user corrections from previous turns
        corrections = self._extract_corrections()
        if corrections:
            aggregated["user_corrections"] = corrections
        
        return aggregated
    
    def _summarize_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of orchestrator output.
        
        Args:
            output: Full orchestrator output
            
        Returns:
            Summarized output
        """
        # Keep only key fields for history
        summary = {}
        
        # Common fields to preserve
        preserve_fields = [
            "intent_type",
            "confidence",
            "action_taken",
            "result_summary",
            "status",
            "error"
        ]
        
        for field in preserve_fields:
            if field in output:
                summary[field] = output[field]
        
        return summary
    
    def _extract_corrections(self) -> List[Dict[str, Any]]:
        """
        Extract user corrections from conversation history.
        
        Looks for patterns like "no, I meant...", "actually...", etc.
        
        Returns:
            List of corrections with context
        """
        corrections = []
        
        correction_keywords = ["no", "actually", "i meant", "correction", "wrong"]
        
        for tc in self.turn_history:
            user_input_lower = tc.user_input.lower()
            
            if any(keyword in user_input_lower for keyword in correction_keywords):
                corrections.append({
                    "turn": tc.turn_number,
                    "correction": tc.user_input,
                    "previous_turn": tc.turn_number - 1 if tc.turn_number > 1 else None
                })
        
        return corrections
    
    def get_turn_by_number(self, turn_number: int) -> Optional[TurnContext]:
        """
        Get context for a specific turn.
        
        Args:
            turn_number: Turn number to retrieve
            
        Returns:
            TurnContext if found, None otherwise
        """
        for tc in self.turn_history:
            if tc.turn_number == turn_number:
                return tc
        return None
    
    def get_recent_turns(self, n: int = 3) -> List[TurnContext]:
        """
        Get the N most recent turns.
        
        Args:
            n: Number of recent turns to return
            
        Returns:
            List of recent turn contexts
        """
        return self.turn_history[-n:] if self.turn_history else []
    
    def clear_history(self) -> None:
        """Clear all turn history."""
        self.turn_history.clear()
    
    def get_history_length(self) -> int:
        """Get the number of turns in history."""
        return len(self.turn_history)
