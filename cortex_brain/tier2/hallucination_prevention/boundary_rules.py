"""Boundary Rules - Behavioral boundaries for hallucination prevention.

Defines and enforces behavioral boundaries to prevent hallucinations.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class BoundaryRule:
    """A behavioral boundary rule.

    Attributes:
        rule_id: Unique rule identifier.
        name: Rule name.
        description: Rule description.
        validator: Function that validates against rule.
        severity: Rule severity (0-100).
    """

    rule_id: str
    name: str
    description: str
    validator: Callable[[Any], bool]
    severity: int = 50


class BehavioralBoundaryRules:
    """Manages behavioral boundary rules."""

    def __init__(self) -> None:
        """Initialize boundary rules."""
        self.rules: Dict[str, BoundaryRule] = {}
        self.violations: list = []

    def register_rule(self, rule: BoundaryRule) -> None:
        """Register a boundary rule.

        Args:
            rule: BoundaryRule to register.
        """
        self.rules[rule.rule_id] = rule

    def unregister_rule(self, rule_id: str) -> None:
        """Unregister a rule.

        Args:
            rule_id: ID of rule to unregister.
        """
        if rule_id in self.rules:
            del self.rules[rule_id]

    def validate(self, rule_id: str, value: Any) -> bool:
        """Validate value against a rule.

        Args:
            rule_id: Rule ID to validate against.
            value: Value to validate.

        Returns:
            True if valid, False if violation.
        """
        if rule_id not in self.rules:
            return True  # Unknown rule, allow

        rule = self.rules[rule_id]
        try:
            is_valid = rule.validator(value)
            if not is_valid:
                self.violations.append(
                    {
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "value": str(value)[:100],  # Truncate for logging
                    }
                )
            return is_valid
        except Exception:
            return False

    def validate_all(self, value: Any) -> bool:
        """Validate value against all rules.

        Args:
            value: Value to validate.

        Returns:
            True if all rules pass, False if any violation.
        """
        for rule_id in self.rules:
            if not self.validate(rule_id, value):
                return False
        return True

    def get_rule(self, rule_id: str) -> Optional[BoundaryRule]:
        """Get a rule by ID.

        Args:
            rule_id: Rule ID.

        Returns:
            BoundaryRule or None if not found.
        """
        return self.rules.get(rule_id)

    def get_all_rules(self) -> List[BoundaryRule]:
        """Get all registered rules.

        Returns:
            List of all rules.
        """
        return list(self.rules.values())

    def get_violations(self) -> list:
        """Get recorded violations.

        Returns:
            List of violations.
        """
        return self.violations.copy()

    def clear_violations(self) -> None:
        """Clear violation history."""
        self.violations.clear()


# Global instance
_global_boundary_rules: Optional[BehavioralBoundaryRules] = None


def get_behavioral_boundary_rules() -> BehavioralBoundaryRules:
    """Get global boundary rules instance.

    Returns:
        BehavioralBoundaryRules singleton.
    """
    global _global_boundary_rules
    if _global_boundary_rules is None:
        _global_boundary_rules = BehavioralBoundaryRules()
    return _global_boundary_rules


__all__ = [
    "BehavioralBoundaryRules",
    "BoundaryRule",
    "get_behavioral_boundary_rules",
]
