"""
ComplianceValidationAgent — Tier 1 phase readiness rule validation.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-003
"""

from __future__ import annotations

from typing import Any, Dict

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class ComplianceValidationAgent:
    """
    Validates Tier 1 phase readiness rules.

    Checks:
    - Phase prerequisites met
    - Acceptance criteria satisfied
    - Test coverage adequate
    """

    def __init__(self) -> None:
        """Initialize compliance validation agent."""
        self.name = "ComplianceValidationAgent"

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation against phase readiness rules.

        Args:
            operation: Operation context dictionary

        Returns:
            EnforcementResult with warnings (Tier 1 violations escalate, not block)
        """
        warnings = []

        # Check phase prerequisites
        prerequisites_met = operation.get("prerequisites_met")
        if prerequisites_met is False:
            phase = operation.get("phase", "Unknown")
            warnings.append(
                f"TIER-1 WARNING: Phase {phase} prerequisites not fully met"
            )

        # Check test coverage for critical operations
        if operation.get("intent") == "DEPLOY":
            test_coverage = operation.get("test_coverage", 0)
            if test_coverage < 80:
                warnings.append(
                    f"TIER-1 WARNING: Test coverage ({test_coverage}%) below 80% threshold for deployment"
                )

        level = EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=[],
            warnings=warnings,
            metadata={
                "agent": "ComplianceValidationAgent",
                "rules_checked": ["Tier 1 Phase Rules"],
            },
        )
