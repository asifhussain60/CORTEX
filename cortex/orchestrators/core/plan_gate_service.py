"""
PlanGateService — Mandatory plan creation before execution.

Creates InteractionPlan artifacts between Stage 1 (Comprehension)
and Stage 4 (Execution) in MasterOrchestrator.process_user_request().

Authority: Phase 102 — Plan-Before-Execute Gate
CORE Rules:
  - CORE-008: TDD mandatory (tests exist in test_plan_gate.py)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-028: snake_case file naming
  - CORE-035: Single canonical implementation
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from cortex.models.interaction_plan import (
    InteractionPlan,
    InteractionPlanStep,
)

logger = logging.getLogger(__name__)


# ============================================================================
# STEP TEMPLATES BY INTENT
# ============================================================================

_IMPLEMENT_STEPS = [
    InteractionPlanStep(order=1, description="Write failing tests (TDD RED phase)", estimated_duration="15m", risk_level="low"),
    InteractionPlanStep(order=2, description="Implement minimum code to pass tests (GREEN phase)", estimated_duration="20m", risk_level="medium"),
    InteractionPlanStep(order=3, description="Refactor with tests passing (REFACTOR phase)", estimated_duration="10m", risk_level="low"),
    InteractionPlanStep(order=4, description="Run governance validation (CORE rules check)", estimated_duration="2m", risk_level="low"),
    InteractionPlanStep(order=5, description="Commit with audit trail markers", estimated_duration="3m", risk_level="low"),
]

_FIX_STEPS = [
    InteractionPlanStep(order=1, description="Reproduce the issue and write regression test", estimated_duration="10m", risk_level="low"),
    InteractionPlanStep(order=2, description="Identify root cause via LENS analysis", estimated_duration="10m", risk_level="low"),
    InteractionPlanStep(order=3, description="Apply minimal fix to pass regression test", estimated_duration="15m", risk_level="medium"),
    InteractionPlanStep(order=4, description="Verify no regressions (full test suite)", estimated_duration="5m", risk_level="low"),
    InteractionPlanStep(order=5, description="Commit with audit trail markers", estimated_duration="3m", risk_level="low"),
]

_REFACTOR_STEPS = [
    InteractionPlanStep(order=1, description="Verify all existing tests pass before changes", estimated_duration="5m", risk_level="low"),
    InteractionPlanStep(order=2, description="Identify refactoring targets via LENS analysis", estimated_duration="10m", risk_level="low"),
    InteractionPlanStep(order=3, description="Apply incremental refactoring (<500 LOC per step)", estimated_duration="20m", risk_level="medium"),
    InteractionPlanStep(order=4, description="Verify tests still pass after refactoring", estimated_duration="5m", risk_level="low"),
    InteractionPlanStep(order=5, description="Run governance validation and commit", estimated_duration="3m", risk_level="low"),
]

_DEFAULT_STEPS = [
    InteractionPlanStep(order=1, description="Analyze request via LENS", estimated_duration="5m", risk_level="low"),
    InteractionPlanStep(order=2, description="Write tests for expected behavior", estimated_duration="15m", risk_level="low"),
    InteractionPlanStep(order=3, description="Execute implementation", estimated_duration="20m", risk_level="medium"),
    InteractionPlanStep(order=4, description="Validate and commit", estimated_duration="5m", risk_level="low"),
]

_STEP_TEMPLATES: Dict[str, list] = {
    "IMPLEMENT": _IMPLEMENT_STEPS,
    "FIX": _FIX_STEPS,
    "REFACTOR": _REFACTOR_STEPS,
}

_DEFAULT_RISK_SCORE = 0.3
_DURATION_MAP: Dict[str, str] = {
    "IMPLEMENT": "50m",
    "FIX": "43m",
    "REFACTOR": "43m",
}
_DEFAULT_DURATION = "45m"


class PlanGateService:
    """Service that creates mandatory InteractionPlan artifacts.

    Creates plans between InteractionOrchestrator comprehension
    (Stage 1) and domain execution (Stage 4) in the
    MasterOrchestrator pipeline.

    Plans are returned to the user for approval before any
    code-modifying operation proceeds.

    Attributes:
        _plan_counter: Internal counter for unique plan IDs.
    """

    def __init__(self) -> None:
        """Initialize PlanGateService."""
        self._plan_counter = 0

    def create_plan(
        self,
        user_request: str,
        intent_type: str,
        lens_context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> InteractionPlan:
        """Create an InteractionPlan from comprehension output.

        Generates a step-by-step plan based on intent type and
        LENS context. Each plan includes TDD steps per CORE-008.

        Args:
            user_request: Original user request text.
            intent_type: Classified intent (IMPLEMENT/FIX/REFACTOR).
            lens_context: LENS analysis context from Stage 1.
            metadata: Optional additional metadata.

        Returns:
            InteractionPlan artifact for user approval.
        """
        self._plan_counter += 1
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        intent_upper = intent_type.upper()

        # Get steps template for intent
        steps = self._get_steps_for_intent(intent_upper)

        # Calculate risk score from LENS context
        risk_score = self._calculate_risk_score(lens_context)

        # Calculate estimated duration
        estimated_duration = _DURATION_MAP.get(intent_upper, _DEFAULT_DURATION)

        plan = InteractionPlan(
            plan_id=plan_id,
            user_request=user_request,
            intent_type=intent_upper,
            steps=steps,
            estimated_duration=estimated_duration,
            risk_score=risk_score,
            lens_context=lens_context,
            approved=False,
        )

        logger.info(
            "PlanGate: Created plan %s for %s intent (%d steps, risk=%.2f)",
            plan_id,
            intent_upper,
            plan.step_count(),
            risk_score,
        )

        return plan

    def _get_steps_for_intent(self, intent_type: str) -> list:
        """Get step templates for a given intent type.

        Args:
            intent_type: The intent type (IMPLEMENT/FIX/REFACTOR).

        Returns:
            List of InteractionPlanStep for the intent.
        """
        template = _STEP_TEMPLATES.get(intent_type, _DEFAULT_STEPS)
        # Return copies to avoid shared state
        return [
            InteractionPlanStep(
                order=step.order,
                description=step.description,
                estimated_duration=step.estimated_duration,
                risk_level=step.risk_level,
            )
            for step in template
        ]

    def _calculate_risk_score(self, lens_context: Dict[str, Any]) -> float:
        """Calculate risk score from LENS context.

        Uses risk_score from LENS if available, otherwise defaults
        to 0.3 (low-medium baseline).

        Args:
            lens_context: LENS analysis context.

        Returns:
            Risk score between 0.0 and 1.0.
        """
        if "risk_score" in lens_context:
            score = float(lens_context["risk_score"])
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        return _DEFAULT_RISK_SCORE
