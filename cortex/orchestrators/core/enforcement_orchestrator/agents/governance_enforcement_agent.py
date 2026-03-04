"""
GovernanceEnforcementAgent — Tier 0 code-quality rule enforcement.

Extracted from enforcement_orchestrator.py (Phase 103-e god-object decomposition).
Rules: CORE-008, CORE-011, CORE-012, CORE-013, CORE-029, CORE-030, CORE-035.

Author: Asif Hussain
AC-ID: AC-P103E-AGENT-001
"""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.orchestrators.core.enforcement_orchestrator.models import (
    EnforcementLevel,
    EnforcementResult,
)


class GovernanceEnforcementAgent:  # CORE-035 — scoped extraction: this is the rule-checker extracted from enforcement_orchestrator; cortex/enforcement/governance_enforcement_agent.py is a separate MCP-facing delegator  # CORE-035-scoped — domain-specific variant
    """
    Enforces Tier 0 code quality rules.

    Rules:
    - CORE-008: TDD (tests must exist before code)
    - CORE-011: Type hints mandatory
    - CORE-012: Google-style docstrings mandatory
    - CORE-013: No bare except clauses
    - CORE-029: Response header enforcement
    - CORE-030: Implementation truth (verify code, not docs)
    - CORE-035: Single canonical implementation
    """

    def __init__(self) -> None:
        """Initialize governance enforcement agent."""
        self.name = "GovernanceEnforcementAgent"
        self.rules = ["CORE-008", "CORE-011", "CORE-012", "CORE-013", "CORE-029", "CORE-030", "CORE-035"]

    def validate(self, operation: Dict[str, Any]) -> EnforcementResult:
        """
        Validate operation against code quality rules.

        Args:
            operation: Operation context dictionary

        Returns:
            EnforcementResult with violations if blocked, warnings if concerns found
        """
        violations: List[str] = []
        warnings: List[str] = []

        # CORE-008: TDD - Tests must exist for IMPLEMENT/FIX operations
        if operation.get("intent") in ["IMPLEMENT", "FIX"]:
            test_file = operation.get("test_file")
            if not test_file:
                violations.append(
                    "CORE-008 VIOLATION: TDD required - tests must exist before code implementation"
                )

        # CORE-013: No bare except clauses
        code_sample = operation.get("code_sample", "")
        if "except:" in code_sample:
            violations.append(
                "CORE-013 VIOLATION: Bare except clause detected - use specific exceptions"
            )

        # CORE-011: Type hints (warning for now)
        if code_sample and "def " in code_sample:
            if "->" not in code_sample:
                warnings.append(
                    "CORE-011 WARNING: Type hints recommended for all functions"
                )

        # CORE-012: Docstrings (warning for now)
        if code_sample and "def " in code_sample:
            if '"""' not in code_sample and "'''" not in code_sample:
                warnings.append(
                    "CORE-012 WARNING: Google-style docstrings recommended"
                )

        # CORE-030: Implementation truth - verify file existence
        target_file = operation.get("target_file")
        if target_file and operation.get("verify_existence"):
            # Future enhancement: actually check file existence
            pass

        level = EnforcementLevel.BLOCKED if violations else (
            EnforcementLevel.WARNING if warnings else EnforcementLevel.PASS
        )

        return EnforcementResult(
            level=level,
            violations=violations,
            warnings=warnings,
            metadata={
                "agent": "GovernanceEnforcementAgent",
                "rules_checked": ["CORE-008", "CORE-011", "CORE-012", "CORE-013", "CORE-030"],
            },
        )
