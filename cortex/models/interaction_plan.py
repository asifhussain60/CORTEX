"""
InteractionPlan model for mandatory plan-before-execute gate.

Lightweight plan artifact created between Stage 1 (Comprehension) and
Stage 4 (Execution) in MasterOrchestrator.process_user_request().

Authority: Phase 102 — Plan-Before-Execute Gate
CORE Rules:
  - CORE-008: TDD mandatory (test written first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-028: snake_case file naming
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class PlanGateIntent(Enum):
    """Intent types that require mandatory plan creation."""

    IMPLEMENT = auto()
    FIX = auto()
    REFACTOR = auto()


# Intents that bypass the plan gate (read-only operations)
PLAN_GATE_BYPASS_INTENTS = frozenset({"QUERY", "ANALYZE", "DIGEST", "RECALL", "ONBOARD", "DESIGN"})


@dataclass
class InteractionPlanStep:
    """Single step in an interaction plan."""

    order: int
    description: str
    estimated_duration: str = "5m"
    risk_level: str = "low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of the step.
        """
        return {
            "order": self.order,
            "description": self.description,
            "estimated_duration": self.estimated_duration,
            "risk_level": self.risk_level,
        }


@dataclass
class InteractionPlan:
    """Lightweight plan artifact for pre-execution review.

    Created by MasterOrchestrator between Stage 1 comprehension
    and Stage 4 execution. Presented to user for approval before
    any code-modifying operation proceeds.

    Attributes:
        plan_id: Unique plan identifier.
        user_request: Original user request text.
        intent_type: Classified intent (IMPLEMENT/FIX/REFACTOR).
        steps: Ordered list of execution steps.
        estimated_duration: Total estimated duration.
        risk_score: Risk assessment score (0.0-1.0).
        lens_context: LENS analysis context from Stage 1.
        created_at: Plan creation timestamp.
        approved: Whether user has approved the plan.
    """

    plan_id: str
    user_request: str
    intent_type: str
    steps: List[InteractionPlanStep] = field(default_factory=list)
    estimated_duration: str = "unknown"
    risk_score: float = 0.0
    lens_context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary for serialization.

        Returns:
            Dictionary representation of the plan.
        """
        return {
            "plan_id": self.plan_id,
            "user_request": self.user_request,
            "intent_type": self.intent_type,
            "steps": [step.to_dict() for step in self.steps],
            "estimated_duration": self.estimated_duration,
            "risk_score": self.risk_score,
            "lens_context": self.lens_context,
            "created_at": self.created_at,
            "approved": self.approved,
        }

    def approve(self) -> None:
        """Mark plan as approved by user."""
        self.approved = True

    def step_count(self) -> int:
        """Return number of steps in plan.

        Returns:
            Number of steps.
        """
        return len(self.steps)

    def is_high_risk(self) -> bool:
        """Check if plan is high risk (score > 0.7).

        Returns:
            True if risk score exceeds 0.7 threshold.
        """
        return self.risk_score > 0.7


def requires_plan_gate(intent_type: str) -> bool:
    """Determine if an intent type requires the plan gate.

    Code-modifying intents (IMPLEMENT, FIX, REFACTOR) require
    a plan to be created and approved before execution.
    Read-only intents bypass the gate.

    Args:
        intent_type: The classified intent type string.

    Returns:
        True if plan gate is required.
    """
    return intent_type.upper() not in PLAN_GATE_BYPASS_INTENTS
