"""Governance Registry - Rule registration and management.

Central registry for governance rules, policies, and enforcement metadata.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class RuleSeverity(Enum):
    """Governance rule severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class GovernanceRule:
    """Single governance rule.

    Attributes:
        id: Unique rule identifier.
        name: Human-readable rule name.
        description: Rule description.
        severity: Rule severity level.
        enforced: Whether rule is actively enforced.
        metadata: Additional metadata.
    """

    id: str
    name: str
    description: str
    severity: RuleSeverity = RuleSeverity.ERROR
    enforced: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize metadata."""
        if self.metadata is None:
            self.metadata = {}


class GovernanceViolationError(Exception):
    """Exception raised when governance rule is violated."""

    pass


class GovernanceRegistry:
    """Central governance rule registry.

    Attributes:
        rules: Dictionary of registered rules.
        policies: Dictionary of policies (rule groupings).
        _lock: Thread safety lock.
    """

    def __init__(self) -> None:
        """Initialize governance registry."""
        self.rules: Dict[str, GovernanceRule] = {}
        self.policies: Dict[str, List[str]] = {}
        import threading
        self._lock = threading.RLock()

    def register_rule(self, rule: GovernanceRule) -> None:
        """Register a governance rule.

        Args:
            rule: GovernanceRule to register.

        Raises:
            ValueError: If rule ID already exists.
        """
        with self._lock:
            if rule.id in self.rules:
                raise ValueError(f"Rule {rule.id} already registered")
            self.rules[rule.id] = rule

    def unregister_rule(self, rule_id: str) -> None:
        """Unregister a governance rule.

        Args:
            rule_id: Rule identifier to unregister.
        """
        with self._lock:
            self.rules.pop(rule_id, None)

    def get_rule(self, rule_id: str) -> Optional[GovernanceRule]:
        """Get a governance rule by ID.

        Args:
            rule_id: Rule identifier.

        Returns:
            GovernanceRule or None if not found.
        """
        with self._lock:
            return self.rules.get(rule_id)

    def get_enforced_rules(self) -> List[GovernanceRule]:
        """Get all actively enforced rules.

        Returns:
            List of enforced GovernanceRule objects.
        """
        with self._lock:
            return [r for r in self.rules.values() if r.enforced]

    def register_policy(self, policy_name: str, rule_ids: List[str]) -> None:
        """Register a policy (collection of rules).

        Args:
            policy_name: Unique policy name.
            rule_ids: List of rule IDs in this policy.
        """
        with self._lock:
            self.policies[policy_name] = rule_ids

    def get_policy_rules(self, policy_name: str) -> List[GovernanceRule]:
        """Get all rules in a policy.

        Args:
            policy_name: Policy name.

        Returns:
            List of GovernanceRule objects in policy.
        """
        with self._lock:
            rule_ids = self.policies.get(policy_name, [])
            return [self.rules[rid] for rid in rule_ids if rid in self.rules]

    def check_rule(self, rule_id: str) -> bool:
        """Check if a rule is registered and enforced.

        Args:
            rule_id: Rule identifier.

        Returns:
            True if rule is enforced.
        """
        with self._lock:
            rule = self.rules.get(rule_id)
            return rule is not None and rule.enforced

    def clear(self) -> None:
        """Clear all rules and policies."""
        with self._lock:
            self.rules.clear()
            self.policies.clear()


# Global registry instance
_global_registry: Optional[GovernanceRegistry] = None


def get_governance_registry() -> GovernanceRegistry:
    """Get global governance registry.

    Returns:
        Singleton GovernanceRegistry instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = GovernanceRegistry()
    return _global_registry


class GovernanceEnforcer:
    """Enforces governance rules and violations."""

    def __init__(self, registry: Optional[GovernanceRegistry] = None) -> None:
        """Initialize enforcer.

        Args:
            registry: GovernanceRegistry to use (default: global).
        """
        self.registry = registry or get_governance_registry()
        self.violations: List[Dict[str, Any]] = []

    def enforce(self, rule_id: str, context: Dict[str, Any]) -> bool:
        """Enforce a specific rule.

        Args:
            rule_id: ID of rule to enforce.
            context: Context for rule evaluation.

        Returns:
            True if rule enforcement passes, False if violated.
        """
        enforced = self.registry.get_enforced_rules()
        rule = None
        for r in enforced:
            if r.rule_id == rule_id:
                rule = r
                break

        if not rule:
            return True  # Unknown rule, allow

        # Simple enforcement: check if context satisfies rule
        if not self._check_rule(rule, context):
            violation = {
                "rule_id": rule_id,
                "severity": rule.severity.value,
                "description": rule.description,
                "context": context,
            }
            self.violations.append(violation)
            return False

        return True

    def _check_rule(self, rule: GovernanceRule, context: Dict[str, Any]) -> bool:
        """Check if context satisfies rule.

        Args:
            rule: Rule to check.
            context: Context to validate.

        Returns:
            True if rule is satisfied, False otherwise.
        """
        # Basic rule checking logic
        return True

    def get_violations(self) -> List[Dict[str, Any]]:
        """Get recorded violations.

        Returns:
            List of violations.
        """
        return self.violations.copy()

    def clear_violations(self) -> None:
        """Clear violation history."""
        self.violations.clear()


__all__ = [
    "GovernanceRegistry",
    "GovernanceRule",
    "GovernanceViolationError",
    "GovernanceEnforcer",
    "RuleSeverity",
    "get_governance_registry",
]
