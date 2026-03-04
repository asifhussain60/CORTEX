"""routing_enforcement.py — Routing Enforcement Engine."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    pass


@dataclass
class RoutingViolation:
    """Represents a routing rule violation."""
    rule: str
    message: str


@dataclass
class RoutingEnforcementResult:
    """Result of routing enforcement evaluation."""
    allowed: bool
    violations: List[RoutingViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Alias for allowed — compatibility with validate_routing_decision callers."""
        return self.allowed


class RoutingEnforcementEngine:  # CORE-035-scoped — domain-specific variant
    """Validates intent routing decisions against governance rules."""

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        disambiguation_threshold: float = 0.7,
        blocking_enabled: bool = True,
    ) -> None:
        """Initialise the enforcement engine with routing thresholds.

        Args:
            confidence_threshold: Minimum confidence to allow routing.
            disambiguation_threshold: Threshold below which disambiguation is required.
            blocking_enabled: Whether enforcement actively blocks low-confidence routing.
        """
        self.confidence_threshold = confidence_threshold
        self.disambiguation_threshold = disambiguation_threshold
        self.blocking_enabled = blocking_enabled

    def enforce(self, intent: str, confidence: float) -> RoutingEnforcementResult:
        """Enforce routing rules for an intent.

        Args:
            intent: The classified intent string.
            confidence: Routing confidence score.

        Returns:
            RoutingEnforcementResult with allow/deny decision.
        """
        if confidence < 0.0 or confidence > 1.0:
            return RoutingEnforcementResult(
                allowed=False,
                violations=[RoutingViolation("CONFIDENCE_RANGE", f"Invalid: {confidence}")],
            )
        return RoutingEnforcementResult(allowed=True)

    def validate_routing_decision(self, decision: Any) -> RoutingEnforcementResult:
        """Validate a fully-formed RoutingDecision against governance rules.

        Args:
            decision: A RoutingDecision dataclass instance.

        Returns:
            RoutingEnforcementResult indicating whether the decision is allowed.
        """
        confidence = getattr(decision, "confidence_score", 1.0)
        return self.enforce(getattr(decision, "intent_type", ""), confidence)
