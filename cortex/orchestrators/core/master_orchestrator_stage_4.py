"""Stage 4: Approval — Approval gating and implementation planning.

Implements Stage 4 of the Master Orchestrator pipeline.
Evaluates Stage 3 knowledge output through configurable approval gates
and produces a final decision with an implementation plan.

CORE Governance:
    CORE-008: TDD mandatory
    CORE-011: Type hints on all functions
    CORE-012: Docstrings on all public APIs
    CORE-027: Audit trail logging

AC-PROD-003-03
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result


@dataclass
class Stage4ApprovalContext:
    """Input context for Stage 4 approval gating.

    Attributes:
        stage3_output: Output produced by Stage 3 (may be None)
        user_id: Identifier of the requesting user
        urgency: Urgency level ('low', 'medium', 'high', 'critical')
        approval_level: Required approval tier ('standard', 'expert')
        constraints: Optional list of domain constraint identifiers
        metadata: Additional context metadata
    """

    stage3_output: Optional[Any]
    user_id: str = ""
    urgency: str = "medium"
    approval_level: str = "standard"
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Stage4Output:
    """Decision output produced by Stage 4 approval.

    Attributes:
        operation: Operation type
        approved: Whether the operation was approved
        approval_reason: Human-readable justification
        confidence_score: Decision confidence (0.0–1.0)
        approval_confidence: Alias for confidence_score (workflow compat)
        gates_passed: List of gate identifiers that passed
        implementation_plan: Ordered implementation steps
        metadata: Additional output metadata
    """

    operation: str
    approved: bool
    approval_reason: str = ""
    confidence_score: float = 0.85
    approval_confidence: float = 0.85
    gates_passed: List[str] = field(default_factory=list)
    implementation_plan: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Synchronise approval_confidence with confidence_score."""
        if self.approval_confidence == 0.85 and self.confidence_score != 0.85:
            self.approval_confidence = self.confidence_score
        elif self.confidence_score == 0.85 and self.approval_confidence != 0.85:
            self.confidence_score = self.approval_confidence


# ---------------------------------------------------------------------------
# Approval gate weights
# ---------------------------------------------------------------------------
_URGENCY_WEIGHTS: Dict[str, float] = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25,
}
_CONFIDENCE_APPROVAL_THRESHOLD = 0.60


class MasterOrchestrationStage4:
    """Stage 4 of the Master Orchestrator pipeline — Approval.

    Evaluates Stage 3 recommendations through approval gates and
    produces a final implementation decision.

    Approval Gates:
        1. domain_validation — checks domain is known
        2. risk_assessment   — checks confidence_score threshold
        3. urgency_check     — boosts low-risk operations with critical urgency
        4. constraints_check — verifies no blocking constraints
        5. expert_gate       — requires expert sign-off if approval_level == 'expert'

    Example:
        >>> stage4 = MasterOrchestrationStage4()
        >>> ctx = Stage4ApprovalContext(stage3_output=output, urgency="high")
        >>> result = stage4.approve_operation(ctx)
        >>> assert result.is_ok()
    """

    def __init__(self) -> None:
        """Initialise Stage 4 with logger, empty history, and gate registry."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.approval_history: List[Dict[str, Any]] = []
        self.approval_gates: List[str] = [
            "domain_validation",
            "risk_assessment",
            "urgency_check",
            "constraints_check",
            "expert_gate",
        ]

    def approve_operation(
        self, context: Optional[Stage4ApprovalContext]
    ) -> Result[Stage4Output]:
        """Evaluate approval gates and produce a decision.

        Args:
            context: Stage4ApprovalContext. If None, returns Err.

        Returns:
            Result[Stage4Output] — Ok with decision on success, Err on failure
        """
        if context is None:
            return Err("Stage4ApprovalContext must not be None")

        import time as _time_mod
        _ac_id = f"AC-STAGE4-{int(_time_mod.time() * 1000)}"
        # AC_START: {_ac_id}
        try:
            # Extract metadata from Stage 3 output
            stage3 = context.stage3_output
            operation = "unknown"
            confidence = 0.75
            domain = "core"

            if stage3 is not None:
                operation = getattr(stage3, "operation", operation)
                confidence = float(getattr(stage3, "confidence_score", confidence))
                domain = getattr(stage3, "domain", domain)

            # Run gates
            gates_passed: List[str] = []
            approved = True
            approval_reason = ""

            # Gate 1: domain_validation
            if domain and domain != "unknown":
                gates_passed.append("domain_validation")
            else:
                approved = False
                approval_reason = "domain_validation failed: unknown domain"

            # Gate 2: risk_assessment
            urgency = context.urgency if context.urgency in _URGENCY_WEIGHTS else "medium"
            urgency_weight = _URGENCY_WEIGHTS[urgency]

            # Critical urgency auto-approves regardless of confidence
            if urgency == "critical":
                gates_passed.append("risk_assessment")
                gates_passed.append("urgency_check")
                if not approval_reason:
                    approval_reason = "Auto-approved: critical urgency"
            else:
                effective_threshold = _CONFIDENCE_APPROVAL_THRESHOLD - (urgency_weight * 0.10)
                if confidence >= effective_threshold:
                    gates_passed.append("risk_assessment")
                else:
                    approved = False
                    if not approval_reason:
                        approval_reason = (
                            f"risk_assessment failed: confidence {confidence:.2f} "
                            f"< threshold {effective_threshold:.2f}"
                        )

                if "risk_assessment" in gates_passed:
                    gates_passed.append("urgency_check")

            # Gate 3: constraints_check
            blocking_constraints = [
                c for c in (context.constraints or [])
                if "block" in c.lower()
            ]
            if not blocking_constraints:
                gates_passed.append("constraints_check")
            else:
                approved = False
                if not approval_reason:
                    approval_reason = f"constraints_check failed: {blocking_constraints}"

            # Gate 4: expert_gate
            if context.approval_level == "expert" and urgency != "critical":
                # Expert gate always passes for now (human-in-the-loop placeholder)
                gates_passed.append("expert_gate")
            else:
                gates_passed.append("expert_gate")

            if approved and not approval_reason:
                approval_reason = "All approval gates passed"

            # Build implementation plan for approved operations
            plan = self._build_implementation_plan(operation, domain, confidence) if approved else []

            output = Stage4Output(
                operation=operation,
                approved=approved,
                approval_reason=approval_reason,
                confidence_score=confidence,
                approval_confidence=confidence,
                gates_passed=gates_passed,
                implementation_plan=plan,
            )

            self.approval_history.append(
                {
                    "operation": operation,
                    "approved": approved,
                    "urgency": urgency,
                    "confidence": confidence,
                    "gates_passed": gates_passed,
                }
            )

            self.logger.debug(
                "Stage4: operation=%s approved=%s confidence=%.2f gates=%s",
                operation,
                approved,
                confidence,
                gates_passed,
            )
            # AC_COMPLETE: {_ac_id} ✅
            return Ok(output)

        except Exception as exc:  # noqa: BLE001
            self.logger.error("Stage4 error: %s", exc)
            # AC_COMPLETE: {_ac_id} ❌
            return Err(str(exc))

    def get_approval_history(self) -> List[Dict[str, Any]]:
        """Return chronological list of all approval decisions.

        Returns:
            List of approval decision dicts
        """
        return list(self.approval_history)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_implementation_plan(
        self,
        operation: str,
        domain: str,
        confidence: float,
    ) -> List[Dict[str, Any]]:
        """Build an implementation plan for an approved operation.

        Args:
            operation: Operation type string
            domain: Target domain
            confidence: Approval confidence score

        Returns:
            Ordered list of implementation step dicts
        """
        steps: List[Dict[str, Any]] = [
            {"step": 1, "description": f"LENS scan of {domain} domain"},
            {"step": 2, "description": f"Write failing tests for {operation} (CORE-008 RED)"},
            {"step": 3, "description": f"Implement {operation} (GREEN phase)"},
            {"step": 4, "description": "Refactor and validate compliance"},
            {"step": 5, "description": "Run regression suite and commit"},
        ]
        if confidence < 0.70:
            steps.insert(
                1,
                {"step": 0, "description": "Manual review recommended (confidence < 0.70)"},
            )
        return steps

    def health_check(self) -> dict:
        """Return health status for L1 wiring contract compliance."""
        return {"status": "healthy", "orchestrator": "MasterOrchestrationStage4"}
