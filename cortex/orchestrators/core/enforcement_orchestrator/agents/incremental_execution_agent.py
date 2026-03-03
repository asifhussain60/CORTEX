"""
IncrementalExecutionAgent — CORE-001 and CORE-004 enforcement.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rules: CORE-001 (incremental execution), CORE-004 (continuation limits).

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-005
"""

from __future__ import annotations

from typing import Any, Dict

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class IncrementalExecutionAgent:
    """
    Enforces CORE-001 (incremental execution) and CORE-004 (continuation limits).

    CORE-001: Operations adding/modifying >500 LOC require decomposition.
    CORE-004: Continuation requests >1000 tokens receive warnings.

    Ensures large operations are broken into manageable chunks.
    """

    def validate(self, context: Dict[str, Any]) -> EnforcementResult:
        """
        Validate incremental execution requirements.

        Args:
            context: Operation context including:
                - intent: Operation type (IMPLEMENT, CONTINUE, etc.)
                - estimated_loc: Estimated lines of code (optional)
                - continuation_tokens: Token count for continuations (optional)

        Returns:
            EnforcementResult with BLOCKED (>500 LOC), WARNING (>1000 tokens), or PASS
        """
        violations = []
        warnings = []

        # CORE-001: Check LOC limit for IMPLEMENT intents
        intent = context.get("intent", "").upper()
        estimated_loc = context.get("estimated_loc", 0)

        if intent == "IMPLEMENT" and estimated_loc > 500:
            violations.append(
                f"CORE-001 VIOLATION: Operation estimates {estimated_loc} LOC (limit: 500). "
                "Please decompose into smaller increments using IncrementalTaskDecomposer."
            )

        # CORE-004: Check token limit for CONTINUE intents
        if intent == "CONTINUE":
            continuation_tokens = context.get("continuation_tokens", 0)
            if continuation_tokens > 1000:
                warnings.append(
                    f"CORE-004 WARNING: Continuation request has {continuation_tokens} tokens "
                    "(recommended limit: 1000). Consider breaking into smaller tasks."
                )

        if violations:
            level = EnforcementLevel.BLOCKED
        elif warnings:
            level = EnforcementLevel.WARNING
        else:
            level = EnforcementLevel.PASS

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "IncrementalExecutionAgent",
                "rules_checked": ["CORE-001", "CORE-004"],
                "estimated_loc": estimated_loc,
                "continuation_tokens": context.get("continuation_tokens", 0),
            },
        )
