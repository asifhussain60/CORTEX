"""Unified intent classification, validation, and routing gateway.

Phase-m2-b introduces this component as a canonical request pipeline entrypoint.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class IntentGatewayResult:
    """Structured outcome returned by IntentGateway.

    Args:
        intent: Resolved canonical intent value.
        confidence: Confidence score for the transformed request.
        route: Canonical route key used by the execution layer.
        transformed_summary: Distilled request summary.
        context: Structured context payload.
        requires_clarification: Flag for low-confidence requests.
    """

    intent: str
    confidence: float
    route: str
    transformed_summary: str
    context: dict[str, Any]
    requires_clarification: bool


class IntentGateway:
    """Single-pass classify + validate + route gateway."""

    DEFAULT_ROUTE: str = "QUERY"

    def __init__(
        self,
        route_map: Optional[dict[str, str]] = None,
    ) -> None:
        """Initialise IntentGateway.

        Args:
            route_map: Optional route map override.
        """
        self._route_map = route_map or {
            "IMPLEMENT": "IMPLEMENT",
            "FIX": "FIX",
            "REFACTOR": "REFACTOR",
            "ANALYZE": "ANALYZE",
            "PLAN": "PLAN",
            "DESIGN": "DESIGN",
            "AUDIT": "AUDIT",
            "DIGEST": "DIGEST",
            "QUERY": "QUERY",
        }

    def process(self, request_text: str) -> IntentGatewayResult:
        """Classify, validate, and route a user request.

        Args:
            request_text: Raw user request text.

        Returns:
            IntentGatewayResult with intent and routing metadata.

        Raises:
            ValueError: If request_text is empty.
        """
        normalized_text = request_text.strip()
        if not normalized_text:
            raise ValueError("request_text cannot be empty")

        classified_intent = self._classify_intent(normalized_text)
        routed_intent = self._route_map.get(classified_intent, self.DEFAULT_ROUTE)
        context = self._build_context(normalized_text, classified_intent)

        return IntentGatewayResult(
            intent=classified_intent,
            confidence=context.get("confidence", 0.7),
            route=routed_intent,
            transformed_summary=context.get("distilled_summary", normalized_text),
            context=context,
            requires_clarification=context.get("clarification_needed", False),
        )

    def health_check(self) -> dict[str, Any]:
        """Return health status for wiring-contract checks."""
        return {"status": "healthy", "component": "IntentGateway"}

    def _classify_intent(self, request_text: str) -> str:
        """Classify request intent using deterministic keyword heuristics."""
        lower = request_text.lower()
        intent_rules = (
            ("FIX", ("fix", "bug", "error", "issue", "broken")),
            ("IMPLEMENT", ("implement", "create", "add", "build", "feature")),
            ("REFACTOR", ("refactor", "improve", "cleanup", "clean")),
            ("AUDIT", ("audit", "compliance", "governance", "healthcheck")),
            ("ANALYZE", ("analyze", "review", "investigate", "inspect")),
            ("PLAN", ("plan", "roadmap", "phase")),
            ("DESIGN", ("design", "architecture", "architect")),
            ("DIGEST", ("digest", "distill", "summarize")),
        )
        for intent, keywords in intent_rules:
            if any(keyword in lower for keyword in keywords):
                return intent
        return "QUERY"

    def _build_context(self, request_text: str, intent: str) -> dict[str, Any]:
        """Build structured context payload for downstream consumers."""
        tokens = [token for token in request_text.split() if token.strip()]
        confidence = 0.9 if intent != "QUERY" else 0.72
        urgency = "high" if any(word in request_text.lower() for word in ("urgent", "immediately", "critical")) else "medium"
        return {
            "intent_type": intent,
            "scope": "module",
            "impact": "medium",
            "urgency": urgency,
            "canonical_keywords": tokens[:8],
            "clarification_needed": len(tokens) < 3,
            "distilled_summary": request_text,
            "confidence": confidence,
        }
