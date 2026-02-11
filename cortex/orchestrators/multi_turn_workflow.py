"""Multi-Turn Conversation Workflow System.

AC-ID: REMEDIATION-INTENT-007
Coordinates complete end-to-end multi-turn conversation flows.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ConversationState:
    """State for a conversation."""

    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turn_number: int = 1
    user_intent: str = ""
    accumulated_context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "conversation_id": self.conversation_id,
            "turn_number": self.turn_number,
            "user_intent": self.user_intent,
            "accumulated_context": self.accumulated_context,
            "timestamp": self.timestamp,
        }


@dataclass
class TurnResult:
    """Result of a single turn execution."""

    turn_number: int
    intent_type: str
    confidence: float = 0.0
    status: str = "PENDING"
    challenges: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    execution_result: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "turn_number": self.turn_number,
            "intent_type": self.intent_type,
            "confidence": self.confidence,
            "status": self.status,
            "challenges": self.challenges,
            "recommendations": self.recommendations,
            "execution_result": self.execution_result,
            "timestamp": self.timestamp,
        }


class MultiTurnWorkflow:
    """Coordinates multi-turn conversation workflows."""

    def __init__(self) -> None:
        """Initialize multi-turn workflow."""
        self.conversation_state = ConversationState()
        self.turn_count = 0
        self.turn_history: List[Dict[str, Any]] = []
        self.escalation_history: List[Dict[str, Any]] = []

    def execute_turn(
        self,
        user_input: str,
        intent_type: str,
        turn_number: int,
        confidence: float = 0.8,
        context: Optional[Dict[str, Any]] = None,
    ) -> TurnResult:
        """Execute a single conversation turn.

        Args:
            user_input: User input for this turn.
            intent_type: Type of intent (QUERY, IMPLEMENT, FIX, REFACTOR, ANALYZE).
            turn_number: Turn number in conversation.
            confidence: Confidence score for intent.
            context: Optional context from previous turns.

        Returns:
            TurnResult with execution details.
        """
        context = context or {}
        self.turn_count += 1

        # Update conversation state
        self.conversation_state.turn_number = turn_number
        self.conversation_state.user_intent = intent_type

        # Merge previous context
        if context:
            self.conversation_state.accumulated_context.update(context)

        # Create turn result
        status = "PASSED"
        challenges = self._identify_challenges(user_input, intent_type)
        if challenges:
            status = "PASSED_WITH_CHALLENGES"

        result = TurnResult(
            turn_number=turn_number,
            intent_type=intent_type,
            confidence=confidence,
            status=status,
            challenges=challenges,
            execution_result=f"Turn {turn_number} executed successfully",
        )

        # Record in history
        self.turn_history.append(result.to_dict())

        # Check governance
        self._check_governance(result)

        return result

    def _identify_challenges(
        self,
        user_input: str,
        intent_type: str,
    ) -> List[Dict[str, Any]]:
        """Identify challenges for this turn.

        Args:
            user_input: User input.
            intent_type: Intent type.

        Returns:
            List of identified challenges.
        """
        challenges = []

        # Check for common patterns
        if "eval" in user_input.lower() or "exec" in user_input.lower():
            challenges.append({
                "category": "GOVERNANCE_RISK",
                "severity": "CRITICAL",
                "description": "Dangerous function usage detected",
            })

        if intent_type == "IMPLEMENT" and len(user_input) < 10:
            challenges.append({
                "category": "TEST_GAP",
                "severity": "MEDIUM",
                "description": "Brief implementation might lack test coverage",
            })

        return challenges

    def _check_governance(self, result: TurnResult) -> None:
        """Check governance rules for turn.

        Args:
            result: Turn result to check.
        """
        if result.challenges:
            # Check severity levels
            severities = {c.get("severity") for c in result.challenges}
            if "CRITICAL" in severities:
                self.escalation_history.append({
                    "turn_number": result.turn_number,
                    "escalation_level": "CRITICAL",
                    "timestamp": datetime.now().isoformat(),
                })

    def get_turn_history(self) -> List[Dict[str, Any]]:
        """Get turn execution history.

        Returns:
            List of turn results.
        """
        return self.turn_history

    def get_escalation_history(self) -> List[Dict[str, Any]]:
        """Get escalation history.

        Returns:
            List of escalations.
        """
        return self.escalation_history

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary.

        Returns:
            Summary dictionary.
        """
        total_challenges = sum(
            len(turn.get("challenges", [])) for turn in self.turn_history
        )

        return {
            "conversation_id": self.conversation_state.conversation_id,
            "turn_count": len(self.turn_history),
            "total_challenges": total_challenges,
            "escalations": len(self.escalation_history),
            "timestamp": datetime.now().isoformat(),
        }

    def reset_conversation(self) -> None:
        """Reset conversation state.

        Used to start a new conversation.
        """
        self.conversation_state = ConversationState()
        self.turn_count = 0
        self.turn_history = []
        self.escalation_history = []

    def get_context_for_turn(self, turn_number: int) -> Dict[str, Any]:
        """Get accumulated context for a turn.

        Args:
            turn_number: Turn number.

        Returns:
            Accumulated context up to this turn.
        """
        context = {
            "previous_turns": self.turn_history[:turn_number - 1],
            "conversation_id": self.conversation_state.conversation_id,
        }
        return context

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations across all turns.

        Returns:
            List of all recommendations.
        """
        recommendations = []
        for turn in self.turn_history:
            if turn.get("recommendations"):
                recommendations.extend(turn["recommendations"])
        return recommendations

    def get_conversation_state(self) -> ConversationState:
        """Get current conversation state.

        Returns:
            Current conversation state.
        """
        return self.conversation_state
