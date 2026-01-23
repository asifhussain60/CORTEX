"""Confidence-Based Intent Router.

AC-ID: REMEDIATION-INTENT-003
Routes intents based on confidence thresholds with multi-tier decision making.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class RoutingDecisionType(Enum):
    """Types of routing decisions."""

    DIRECT_ROUTE = "DIRECT_ROUTE"
    CAUTION_ROUTE = "CAUTION_ROUTE"
    CLARIFICATION_NEEDED = "CLARIFICATION_NEEDED"


@dataclass
class RoutingDecision:
    """A routing decision for an intent."""

    decision_type: RoutingDecisionType
    confidence: float
    target_stage: Optional[str] = None
    caution_flag: bool = False
    reason: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of decision.
        """
        return {
            "decision_type": self.decision_type.value,
            "confidence": self.confidence,
            "target_stage": self.target_stage,
            "caution_flag": self.caution_flag,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


class ConfidenceRouter:
    """Route intents based on confidence scores."""

    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    MEDIUM_CONFIDENCE_THRESHOLD = 0.70

    def __init__(self) -> None:
        """Initialize the confidence router."""
        pass

    def route(
        self,
        intent_type: str,
        confidence: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> RoutingDecision:
        """Route intent based on confidence score.

        Args:
            intent_type: Type of intent (IMPLEMENT, FIX, REFACTOR, QUERY, ANALYZE).
            confidence: Confidence score (0.0-1.0).
            context: Optional context information.

        Returns:
            RoutingDecision with routing direction.
        """
        context = context or {}

        # Special handling for QUERY and ANALYZE - always direct response
        if intent_type in ["QUERY", "ANALYZE"]:
            return RoutingDecision(
                decision_type=RoutingDecisionType.DIRECT_ROUTE,
                confidence=confidence,
                target_stage="DIRECT_RESPONSE",
                reason=f"{intent_type} intents always route to direct response",
            )

        # High confidence: direct route to next stage
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            return RoutingDecision(
                decision_type=RoutingDecisionType.DIRECT_ROUTE,
                confidence=confidence,
                target_stage="KNOWLEDGE",
                caution_flag=False,
                reason=f"High confidence ({confidence:.2f}) - direct route to knowledge integration",
            )

        # Medium confidence: caution route with escalation
        if confidence >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return RoutingDecision(
                decision_type=RoutingDecisionType.CAUTION_ROUTE,
                confidence=confidence,
                target_stage="KNOWLEDGE",
                caution_flag=True,
                reason=f"Medium confidence ({confidence:.2f}) - caution route with escalation to governance tier",
            )

        # Low confidence: clarification needed, return to interaction
        return RoutingDecision(
            decision_type=RoutingDecisionType.CLARIFICATION_NEEDED,
            confidence=confidence,
            target_stage="INTERACTION",
            caution_flag=False,
            reason=f"Low confidence ({confidence:.2f}) - return to user for clarification",
        )

    def adjust_confidence(
        self,
        base_confidence: float,
        context: Dict[str, Any],
    ) -> float:
        """Adjust confidence score based on context.

        Args:
            base_confidence: Base confidence score.
            context: Context information for adjustment.

        Returns:
            Adjusted confidence score.
        """
        adjusted = base_confidence

        # Boost confidence if previous turns were successful
        if context.get("previous_decisions"):
            success_rate = sum(
                1
                for d in context["previous_decisions"]
                if d.get("success", False)
            ) / len(context["previous_decisions"])
            adjusted += success_rate * 0.05  # Up to +0.05 boost

        # Reduce confidence if conversation turn is high (fatigue)
        if context.get("conversation_turn", 1) > 5:
            adjusted -= (context["conversation_turn"] - 5) * 0.02

        # Cap at 0.0 - 1.0
        return max(0.0, min(1.0, adjusted))

    def get_escalation_path(
        self, decision: RoutingDecision
    ) -> Dict[str, Any]:
        """Get escalation path for a decision.

        Args:
            decision: The routing decision.

        Returns:
            Escalation path information.
        """
        if decision.decision_type == RoutingDecisionType.DIRECT_ROUTE:
            return {
                "escalation_needed": False,
                "path": ["KNOWLEDGE", "EXECUTION"],
            }

        if decision.decision_type == RoutingDecisionType.CAUTION_ROUTE:
            return {
                "escalation_needed": True,
                "path": ["KNOWLEDGE", "GOVERNANCE_REVIEW", "EXECUTION"],
                "governance_tier": "TIER_1_2",
            }

        # Clarification needed
        return {
            "escalation_needed": True,
            "path": ["INTERACTION", "COMPREHENSION"],
            "reason": decision.reason,
        }
