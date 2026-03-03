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
        if reflection.confidence < 0.6:
            return ApprovalDecision(
                approved=False,
                reason="Confidence below 0.6 threshold",
                violations=["LOW_CONFIDENCE"],
            )
        return ApprovalDecision(approved=True, reason="DoR criteria met")
