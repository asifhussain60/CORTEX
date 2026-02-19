"""Governance rules and enforcement."""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from cortex.models.canonical_enums import AuditEventType


class GovernanceRuleType(Enum):
    """Types of governance rules."""
    POLICY = "policy"
    COMPLIANCE = "compliance"
    AUDIT = "audit"
    SECURITY = "security"




class GovernanceRule:
    """Defines a governance rule."""

    def __init__(
        self,
        rule_id: str,
        rule_type: GovernanceRuleType,
        evaluator: Callable[[Dict[str, Any]], bool]
    ):
        self.rule_id = rule_id
        self.rule_type = rule_type
        self.evaluator = evaluator

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate rule against context."""
        try:
            return self.evaluator(context)
        except Exception:
            return False


class GovernanceEngine:
    """Enforce governance rules."""

    def __init__(self):
        self.rules: Dict[str, GovernanceRule] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def register_rule(self, rule: GovernanceRule) -> None:
        """Register governance rule."""
        self.rules[rule.rule_id] = rule

    def evaluate_context(self, context: Dict[str, Any]) -> bool:
        """Evaluate all rules against context."""
        all_compliant = True

        for rule in self.rules.values():
            is_compliant = rule.evaluate(context)
            if not is_compliant:
                all_compliant = False

            self.audit_log.append({
                "rule_id": rule.rule_id,
                "compliant": is_compliant,
                "event_type": AuditEventType.COMPLIANCE_CHECK.value
            })

        return all_compliant

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log."""
        return self.audit_log
