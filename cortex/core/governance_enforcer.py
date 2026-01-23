"""Governance Enforcer - Enforces governance rules.

Validates operations against governance rules.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Callable
from enum import Enum


class RuleSeverity(Enum):
    """Rule severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class GovernanceRule:
    """Governance rule definition.

    Attributes:
        rule_id: Unique rule identifier.
        name: Rule name.
        description: Rule description.
        validator: Validation function.
        severity: Rule severity.
    """

    rule_id: str
    name: str
    validator: Callable
    severity: RuleSeverity = RuleSeverity.WARNING
    description: str = ""


class GovernanceEnforcer:
    """Enforces governance rules."""

    def __init__(self) -> None:
        """Initialize governance enforcer."""
        self.rules: Dict[str, GovernanceRule] = {}
        self.violations: List[Dict[str, Any]] = []

    def register_rule(self, rule: GovernanceRule) -> None:
        """Register a governance rule.

        Args:
            rule: GovernanceRule to register.
        """
        self.rules[rule.rule_id] = rule

    def enforce(self, context: Dict[str, Any]) -> bool:
        """Enforce all rules against context.

        Args:
            context: Context to validate.

        Returns:
            True if all rules passed.
        """
        self.violations = []
        all_passed = True

        for rule in self.rules.values():
            if not self._check_rule(rule, context):
                all_passed = False

        return all_passed

    def _check_rule(self, rule: GovernanceRule, context: Dict[str, Any]) -> bool:
        """Check a single rule.

        Args:
            rule: Rule to check.
            context: Context to validate.

        Returns:
            True if rule passed.
        """
        try:
            result = rule.validator(context)
            if not result:
                self.violations.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "severity": rule.severity.value,
                    "description": rule.description,
                })
            return result
        except Exception:
            return False

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get rule violations.

        Returns:
            List of violations.
        """
        return self.violations.copy()


__all__ = ["GovernanceEnforcer", "GovernanceRule", "RuleSeverity", "EnforcementResult"]

# Stub for test compatibility
class EnforcementResult:
    """Result of governance enforcement."""
    def __init__(self, compliant: bool = True, violations: Optional[List[str]] = None):
        self.compliant = compliant
        self.violations = violations or []
