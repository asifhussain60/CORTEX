"""
SecurityCheckpointAgent — Tier 0 safety rule enforcement.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rules: CORE-026, CORE-025, CORE-027.

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-002
"""

from __future__ import annotations

from typing import Any, Dict

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class SecurityCheckpointAgent:
    """
    Enforces Tier 0 safety rules.

    Rules:
    - CORE-026: Git checkpoint before major changes
    - CORE-025: Security review for sensitive operations
    - CORE-027: Audit trail logging (AC_START → AC_EXECUTE → AC_COMPLETE)
    """

    def __init__(self) -> None:
        """Initialize security checkpoint agent."""
        self.name = "SecurityCheckpointAgent"
        self.rules = ["CORE-026", "CORE-025", "CORE-027"]

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation against safety rules.

        Args:
            operation: Operation context dictionary

        Returns:
            EnforcementResult with violations if blocked, warnings if concerns found
        """
        violations = []
        warnings = []

        # CORE-026: Git checkpoint for major changes (SYSTEM scope)
        scope = operation.get("scope", "FILE")
        git_checkpoint = operation.get("git_checkpoint_created", False)

        if scope == "SYSTEM" and not git_checkpoint:
            violations.append(
                "CORE-026 VIOLATION: Git checkpoint required before system-wide changes"
            )

        # CORE-027: Audit trail - ensure AC_ID present
        ac_id = operation.get("ac_id")
        if not ac_id and operation.get("intent") != "ANALYZE":
            warnings.append(
                "CORE-027 WARNING: Audit trail (AC_ID) recommended for all operations"
            )

        level = EnforcementLevel.BLOCKED if violations else (
            EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS
        )

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "SecurityCheckpointAgent",
                "rules_checked": ["CORE-025", "CORE-026", "CORE-027"],
            },
        )
