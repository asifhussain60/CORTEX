"""
dor_approval_gate.py — Definition of Ready Approval Gate

Restored for import compatibility after Wave 7 purge.
Preserves public interface: IntentReflection, ApprovalDecision, DoRApprovalGate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cortex.orchestrators.core.approval_gate import ApprovalDecision


@dataclass
class IntentReflection:
    """Captures the reflected intent prior to approval gating."""

    intent: str
    confidence: float
    context: dict[str, Any] = field(default_factory=dict)


class DoRApprovalGate:
    """Definition of Ready approval gate — validates requests before execution."""

    def evaluate(self, reflection: IntentReflection) -> ApprovalDecision:
        """Evaluate an intent reflection against DoR criteria.

        Args:
            reflection: The intent reflection to evaluate.

        Returns:
            ApprovalDecision indicating whether execution may proceed.
        """
        context = reflection.context or {}
        gate_open = bool(context.get("gate_open", False))
        missing_dimensions = context.get("missing_dimensions", []) or []
        dor_pct = context.get("dor_pct")

        # Primary path: explicit readiness context from guided interaction.
        if gate_open:
            return ApprovalDecision(approved=True, reason="DoR criteria met")

        if missing_dimensions:
            return ApprovalDecision(
                approved=False,
                reason=(
                    f"{len(missing_dimensions)} readiness dimension"
                    f"{'s' if len(missing_dimensions) != 1 else ''} incomplete"
                ),
            )

        if isinstance(dor_pct, int) and dor_pct < 100:
            return ApprovalDecision(
                approved=False,
                reason=f"DoR below threshold: {dor_pct}% < 100%",
            )

        # Compatibility fallback for callers that only provide intent confidence.
        if reflection.confidence < 0.6:
            return ApprovalDecision(
                approved=False,
                reason="Confidence below 0.6 threshold",
            )
        return ApprovalDecision(approved=True, reason="DoR criteria met")
