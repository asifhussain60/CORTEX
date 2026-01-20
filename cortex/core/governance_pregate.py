"""Governance Pre-Gate - Pre-execution governance validation.

Validates operations against governance rules before execution.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class PreGateDecision(Enum):
    """Pre-gate validation decisions."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    LOG_ONLY = "log_only"


@dataclass
class PreGateResult:
    """Result of pre-gate validation.

    Attributes:
        decision: PreGateDecision.
        reason: Explanation for decision.
        violations: List of rule violations.
    """

    decision: PreGateDecision
    reason: str
    violations: list[str] = None

    def __post_init__(self) -> None:
        """Initialize violations list."""
        if self.violations is None:
            self.violations = []

    def is_allowed(self) -> bool:
        """Check if operation is allowed.

        Returns:
            True if decision is ALLOW.
        """
        return self.decision == PreGateDecision.ALLOW


class GovernancePreGate:
    """Pre-execution governance validation."""

    def __init__(self) -> None:
        """Initialize pre-gate validator."""
        self.rules: Dict[str, Any] = {}

    def register_rule(self, rule_id: str, rule: Dict[str, Any]) -> None:
        """Register a governance rule.

        Args:
            rule_id: Unique rule identifier.
            rule: Rule definition.
        """
        self.rules[rule_id] = rule

    def validate(
        self, operation: str, context: Dict[str, Any]
    ) -> PreGateResult:
        """Validate operation against governance rules.

        Args:
            operation: Operation to validate.
            context: Operation context.

        Returns:
            PreGateResult with validation decision.
        """
        violations = []

        # Check basic rules
        if not operation:
            violations.append("Operation name cannot be empty")

        if not isinstance(context, dict):
            violations.append("Context must be a dictionary")

        # Apply registered rules
        for rule_id, rule in self.rules.items():
            if not self._check_rule(rule, operation, context):
                violations.append(f"Rule {rule_id} violated")

        if violations:
            return PreGateResult(
                decision=PreGateDecision.DENY,
                reason=f"{len(violations)} rules violated",
                violations=violations,
            )

        return PreGateResult(
            decision=PreGateDecision.ALLOW,
            reason="All governance rules satisfied",
        )

    def _check_rule(
        self, rule: Dict[str, Any], operation: str, context: Dict[str, Any]
    ) -> bool:
        """Check if a specific rule is satisfied.

        Args:
            rule: Rule definition.
            operation: Operation name.
            context: Operation context.

        Returns:
            True if rule is satisfied.
        """
        # Basic implementation - can be extended
        required_fields = rule.get("required_fields", [])
        for field in required_fields:
            if field not in context:
                return False
        return True


def get_governance_pregate() -> GovernancePreGate:
    """Get or create governance pre-gate instance.

    Returns:
        GovernancePreGate singleton instance.
    """
    # Singleton pattern
    if not hasattr(get_governance_pregate, "_instance"):
        get_governance_pregate._instance = GovernancePreGate()
    return get_governance_pregate._instance


__all__ = ["GovernancePreGate", "PreGateResult", "PreGateDecision", "get_governance_pregate"]
