"""
SweepCompositionEnforcementAgent — CORE-064 structural sweep gate.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rule: CORE-064 (Sweep Completeness Contract).

Validates that any composed workflow template for FIX, REFACTOR, or AUDIT
operations contains the mandatory sweep catalogue envelope.

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-010
"""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class SweepCompositionEnforcementAgent:
    """
    Enforces CORE-064 (Sweep Completeness Contract) at composition time.

    Validates that any composed workflow template for FIX, REFACTOR, or AUDIT
    operations contains the mandatory sweep catalogue envelope:
      - step[0].id == 'sweep_catalogue_open'
      - step[-1].id == 'sweep_catalogue_assert_exhausted' with blocking=True

    This is a **structural** check — it prevents a composed template from
    reaching execution without the sweep contract wired in.

    Authority: CORE-064 Sweep Completeness Contract.
    """

    SWEEP_OPERATIONS: frozenset = frozenset({"FIX", "REFACTOR", "AUDIT"})

    def __init__(self) -> None:
        """Initialize SweepCompositionEnforcementAgent."""
        self.name = "SweepCompositionEnforcementAgent"
        self.rules = ["CORE-064"]

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate that a composed template carries the CORE-064 sweep envelope.

        Args:
            context: Operation context with optional keys:
                - composed_template (Dict): The template produced by TemplateComposer.
                - operation_type (str): e.g. "FIX", "REFACTOR", "AUDIT", "IMPLEMENT".

        Returns:
            EnforcementResult — BLOCKED for Tier-0 CORE-064 violations, PASS otherwise.
        """
        violations: List[str] = []
        operation_type = context.get("operation_type", "").upper()
        composed_template = context.get("composed_template")

        if not composed_template:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "SweepCompositionEnforcementAgent",
                    "skipped": "No composed_template in context",
                },
            )

        if operation_type not in self.SWEEP_OPERATIONS:
            return EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={
                    "agent": "SweepCompositionEnforcementAgent",
                    "skipped": f"operation_type={operation_type!r} does not require sweep envelope",
                },
            )

        steps: List[Dict[str, Any]] = composed_template.get("steps", [])

        if not steps or steps[0].get("id") != "sweep_catalogue_open":
            violations.append(
                f"CORE-064 VIOLATION: Composed {operation_type} template is missing "
                "'sweep_catalogue_open' as step[0]. Every FIX/REFACTOR/AUDIT composed "
                "workflow must open a SweepCatalogue before execution. "
                "This is a P0 Sweep Completeness Contract violation."
            )

        if not steps or steps[-1].get("id") != "sweep_catalogue_assert_exhausted":
            violations.append(
                f"CORE-064 VIOLATION: Composed {operation_type} template is missing "
                "'sweep_catalogue_assert_exhausted' as step[-1]. Every FIX/REFACTOR/AUDIT "
                "composed workflow must assert the catalogue is exhausted before "
                "AC_COMPLETE is emitted. Partial sweeps are a governance violation."
            )
        elif not steps[-1].get("blocking", False):
            violations.append(
                "CORE-064 VIOLATION: 'sweep_catalogue_assert_exhausted' step must have "
                "blocking=True. A non-blocking close step allows partial sweeps to slip through."
            )

        level = EnforcementLevel.BLOCKED if violations else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=[],
            metadata={
                "agent": "SweepCompositionEnforcementAgent",
                "rules_checked": ["CORE-064"],
                "operation_type": operation_type,
                "step_count": len(steps),
                "sweep_envelope_present": len(violations) == 0,
            },
        )
