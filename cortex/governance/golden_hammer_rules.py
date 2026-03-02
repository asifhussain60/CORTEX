"""
Golden Hammer Anti-Pattern Prevention Rules

Validates routing decisions to prevent misuse of workflow templates.
Enforces thresholds and requires rationale for overrides.

Authority: WORKFLOW-COMPLEXITY-GATE-001 / GOLDEN-HAMMER-001/002/003
Date: 2026-02-17
"""

from typing import Optional
from dataclasses import dataclass

from cortex.orchestrators.core.intent_router.workflow_gate import RoutingDecision, RoutingStrategy


@dataclass
class GoldenHammerViolation(Exception):
    """Raised when golden hammer anti-pattern detected."""
    rule: str
    message: str
    decision: RoutingDecision


class GoldenHammerRules:
    """
    Validates routing decisions against golden hammer anti-patterns.

    Rules:
    - GOLDEN-HAMMER-001: TRIVIAL operations MUST NOT use templates
    - GOLDEN-HAMMER-002: HIGH complexity operations MUST use templates
    - GOLDEN-HAMMER-003: MODERATE operations MAY override with rationale
    """

    TRIVIAL_THRESHOLD = 0.15
    COMPLEX_THRESHOLD = 0.75

    def validate_routing_decision(
        self,
        decision: RoutingDecision,
        override_rationale: Optional[str] = None
    ) -> None:
        """
        Enforce golden hammer prevention rules.

        Args:
            decision: Routing decision to validate
            override_rationale: Optional rationale for moderate override

        Raises:
            GoldenHammerViolation: If rule violated
        """
        # Rule 1: TRIVIAL operations MUST NOT use templates
        if (decision.complexity < self.TRIVIAL_THRESHOLD and
            decision.route == RoutingStrategy.WORKFLOW_TEMPLATE):
            raise GoldenHammerViolation(
                rule="GOLDEN-HAMMER-001",
                message=(
                    f"Trivial operation (score={decision.complexity:.2f}) "
                    "routed to workflow template (overhead violation)"
                ),
                decision=decision
            )

        # Rule 2: HIGH complexity operations MUST use templates
        if (decision.complexity >= self.COMPLEX_THRESHOLD and
            decision.route == RoutingStrategy.DIRECT_ORCHESTRATOR):
            raise GoldenHammerViolation(
                rule="GOLDEN-HAMMER-002",
                message=(
                    f"High complexity operation (score={decision.complexity:.2f}) "
                    "bypassed workflow template (safety violation)"
                ),
                decision=decision
            )

        # Rule 3: MODERATE operations MAY override with rationale
        if (self.TRIVIAL_THRESHOLD <= decision.complexity < self.COMPLEX_THRESHOLD):
            if decision.route != self._default_route_for_moderate(decision.complexity):
                if not override_rationale:
                    raise GoldenHammerViolation(
                        rule="GOLDEN-HAMMER-003",
                        message=(
                            f"Moderate complexity operation (score={decision.complexity:.2f}) "
                            "routing override requires rationale"
                        ),
                        decision=decision
                    )

    def _default_route_for_moderate(self, complexity: float) -> RoutingStrategy:
        """Determine default route for moderate complexity (0.15-0.75)."""
        # Default routing thresholds:
        # 0.15-0.35: Direct orchestrator
        # 0.35-0.75: Workflow template
        if complexity < 0.35:
            return RoutingStrategy.DIRECT_ORCHESTRATOR
        else:
            return RoutingStrategy.WORKFLOW_TEMPLATE
