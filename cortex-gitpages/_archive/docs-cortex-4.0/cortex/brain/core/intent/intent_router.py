"""
Intent Router - Routes canonicalized intents to appropriate orchestrators.

AC-PROD-001-02: Intent Router Decision Tree

Routes intents based on:
1. Intent type (IMPLEMENT, FIX, QUERY, etc.)
2. Confidence level (high/medium/low)
3. Special handling for non-delegatable intents (queries)
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

from cortex.brain.core.intent.intent_canonicalizer import (
    CanonicalizedIntent,
    IntentType,
)


class OrchestrationTarget(Enum):
    """Possible orchestration targets."""

    TDD = "TDD"  # For IMPLEMENT, FIX, REFACTOR, DEBUG, TEST
    DIRECT_RESPONSE = "DIRECT_RESPONSE"  # For QUERY, ANALYZE, STATUS (no delegation)
    PLANNING = "PLANNING"  # For PLANNING, ADO_WORK
    INTERACTION = "INTERACTION"  # For low-confidence or UNKNOWN intents


@dataclass
class RoutingDecision:
    """Result of routing an intent to a target orchestrator."""

    target_orchestrator: OrchestrationTarget
    """The orchestrator this intent routes to."""

    canonical_intent: CanonicalizedIntent
    """The original canonicalized intent."""

    routing_reason: str
    """Human-readable explanation of routing decision."""

    requires_delegation: bool
    """Whether this requires delegating to another orchestrator."""

    caution_flag: bool = False
    """Whether this routing should be treated with caution (low confidence, etc.)."""

    def __post_init__(self) -> None:
        """Validate routing decision after initialization."""
        if self.target_orchestrator is None:
            raise ValueError("target_orchestrator cannot be None")
        if not self.routing_reason:
            raise ValueError("routing_reason cannot be empty")


class IntentRouter:
    """
    Routes canonicalized intents to appropriate orchestrators.

    Decision Tree:
    ┌─ Intent Type?
    │  ├─ IMPLEMENT/FIX/REFACTOR/DEBUG/TEST
    │  │  └─ Confidence >= 0.85?
    │  │     ├─ YES → TDD (no caution)
    │  │     ├─ 0.70-0.84 → TDD (with caution)
    │  │     └─ < 0.70 → INTERACTION (clarification needed)
    │  ├─ QUERY/ANALYZE/STATUS
    │  │  └─ DIRECT_RESPONSE (no delegation, even if low confidence)
    │  ├─ PLANNING/ADO_WORK
    │  │  └─ Confidence >= 0.85?
    │  │     ├─ YES → PLANNING (no caution)
    │  │     ├─ 0.70-0.84 → PLANNING (with caution)
    │  │     └─ < 0.70 → INTERACTION (clarification needed)
    │  └─ UNKNOWN/None
    │     └─ INTERACTION (always needs clarification)
    """

    # Routing map for intent types
    ROUTING_MAP: Dict[IntentType, OrchestrationTarget] = {
        # Code work → TDD
        IntentType.IMPLEMENT: OrchestrationTarget.TDD,
        IntentType.FIX: OrchestrationTarget.TDD,
        IntentType.REFACTOR: OrchestrationTarget.TDD,
        IntentType.VALIDATE: OrchestrationTarget.TDD,  # Validation is like testing
        IntentType.MIGRATE: OrchestrationTarget.TDD,  # Migration is like refactoring
        # Queries → Direct response (no delegation)
        IntentType.QUERY: OrchestrationTarget.DIRECT_RESPONSE,
        IntentType.ANALYZE: OrchestrationTarget.DIRECT_RESPONSE,
        # Unknown → Back to Interaction for clarification
        IntentType.UNKNOWN: OrchestrationTarget.INTERACTION,
    }

    # Which targets require delegation
    REQUIRES_DELEGATION: Dict[OrchestrationTarget, bool] = {
        OrchestrationTarget.TDD: True,
        OrchestrationTarget.DIRECT_RESPONSE: False,
        OrchestrationTarget.PLANNING: True,
        OrchestrationTarget.INTERACTION: False,
    }

    # Confidence thresholds
    CONFIDENCE_HIGH = 0.85
    CONFIDENCE_MEDIUM_LOW = 0.70

    def route(self, canonical_intent: CanonicalizedIntent) -> RoutingDecision:
        """
        Route a canonicalized intent to the appropriate orchestrator.

        Args:
            canonical_intent: The canonicalized intent to route

        Returns:
            RoutingDecision indicating target orchestrator and routing rationale

        Raises:
            ValueError: If intent data is invalid
        """
        # Get base target from intent type
        target = self._get_target_for_intent_type(canonical_intent.intent_type)

        # Apply confidence-based routing rules
        (target, reason, caution) = self._apply_confidence_rules(
            target, canonical_intent
        )

        # Build routing decision
        requires_delegation = self.REQUIRES_DELEGATION[target]

        decision = RoutingDecision(
            target_orchestrator=target,
            canonical_intent=canonical_intent,
            routing_reason=reason,
            requires_delegation=requires_delegation,
            caution_flag=caution,
        )

        return decision

    def _get_target_for_intent_type(
        self, intent_type: Optional[IntentType]
    ) -> OrchestrationTarget:
        """
        Get the default target orchestrator for an intent type.

        Args:
            intent_type: The intent type to route

        Returns:
            The target orchestrator for this intent type
        """
        if intent_type is None:
            return OrchestrationTarget.INTERACTION

        return self.ROUTING_MAP.get(intent_type, OrchestrationTarget.INTERACTION)

    def _apply_confidence_rules(
        self,
        base_target: OrchestrationTarget,
        canonical_intent: CanonicalizedIntent,
    ) -> tuple[OrchestrationTarget, str, bool]:
        """
        Apply confidence-based routing rules.

        High confidence (>= 0.85):
            Route to base target, no caution

        Medium confidence (0.70-0.84):
            Route to base target, but with caution flag

        Low confidence (< 0.70):
            Query intents → still route to DIRECT_RESPONSE (queries are safe)
            Other intents → return to INTERACTION for clarification

        Args:
            base_target: The base target from intent type
            canonical_intent: The canonicalized intent

        Returns:
            Tuple of (final_target, reason, caution_flag)
        """
        confidence = canonical_intent.confidence
        intent_type = canonical_intent.intent_type

        # Queries are safe even with low confidence
        if base_target == OrchestrationTarget.DIRECT_RESPONSE:
            reason = f"Routing QUERY-type intent {intent_type.name} to DirectResponse for immediate handling."
            return (base_target, reason, False)

        # High confidence: route with certainty
        if confidence >= self.CONFIDENCE_HIGH:
            reason = (
                f"High confidence ({confidence:.0%}) {intent_type.name} intent routes to {base_target.value}. "
                f"Ready for delegation."
            )
            return (base_target, reason, False)

        # Medium confidence: route with caution
        if confidence >= self.CONFIDENCE_MEDIUM_LOW:
            reason = (
                f"Medium confidence ({confidence:.0%}) {intent_type.name} intent routes to {base_target.value} "
                f"with caution flag. Consider clarification if issues arise."
            )
            return (base_target, reason, True)

        # Low confidence: return for clarification (except queries)
        reason = (
            f"Low confidence ({confidence:.0%}) {intent_type.name} intent requires clarification. "
            f"Routing back to InteractionOrchestrator for user interaction."
        )
        return (OrchestrationTarget.INTERACTION, reason, True)

    @property
    def routing_map(self) -> Dict[IntentType, OrchestrationTarget]:
        """Get the routing map (read-only)."""
        return self.ROUTING_MAP.copy()

    @property
    def confidence_thresholds(self) -> Dict[str, float]:
        """Get confidence thresholds (read-only)."""
        return {
            "high": self.CONFIDENCE_HIGH,
            "medium_low": self.CONFIDENCE_MEDIUM_LOW,
        }
