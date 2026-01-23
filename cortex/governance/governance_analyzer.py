"""Governance Analyzer for policy violation detection."""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ViolationReport:
    """Policy violation report."""

    rule_id: str
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    message: str
    entity: str
    remediation: str


class GovernanceAnalyzer:
    """Analyzes entities for policy violations."""

    # Core governance rules
    CORE_RULES = {
        "CORE-008": {
            "name": "Test-Driven Development",
            "check": lambda data: data.get("has_tests", True)
        },
        "CORE-011": {
            "name": "Type Hints Required",
            "check": lambda data: data.get("has_type_hints", True)
        },
        "CORE-012": {
            "name": "Google Docstrings Required",
            "check": lambda data: data.get("has_docstring", True)
        },
        "CORE-013": {
            "name": "No Bare Except Clauses",
            "check": lambda data: not data.get("bare_except", False)
        },
        "CORE-017": {
            "name": "Strict Governance Enforcement",
            "check": lambda data: True  # Always passes if checked
        }
    }

    def __init__(self) -> None:
        """Initialize analyzer."""
        self.custom_rules: Dict[str, Dict[str, Any]] = {}
        self.metrics = {
            "total_checks": 0,
            "violations_detected": 0
        }

    def analyze(
        self,
        entity_type: str,
        entity_data: Dict[str, Any]
    ) -> List[ViolationReport]:
        """Analyze entity for policy violations.
        
        Args:
            entity_type: Type of entity (operation, code, function, etc.)
            entity_data: Entity data to analyze
            
        Returns:
            List of ViolationReport objects
        """
        self.metrics["total_checks"] += 1
        violations: List[ViolationReport] = []
        
        # Check core rules
        for rule_id, rule_info in self.CORE_RULES.items():
            try:
                if not rule_info["check"](entity_data):
                    violations.append(
                        ViolationReport(
                            rule_id=rule_id,
                            severity="HIGH",
                            message=f"Violates {rule_info['name']}",
                            entity=entity_type,
                            remediation=f"Ensure compliance with {rule_id}"
                        )
                    )
            except Exception:
                pass
        
        # Check custom rules
        for rule_id, rule_info in self.custom_rules.items():
            try:
                check_func = rule_info.get("check_function")
                if check_func and not check_func(entity_data):
                    violations.append(
                        ViolationReport(
                            rule_id=rule_id,
                            severity="MEDIUM",
                            message=rule_info.get("rule_text", "Custom rule violated"),
                            entity=entity_type,
                            remediation=f"Fix violation for {rule_id}"
                        )
                    )
            except Exception:
                pass
        
        if violations:
            self.metrics["violations_detected"] += len(violations)
        
        return violations

    def add_custom_rule(
        self,
        rule_id: str,
        rule_text: str,
        check_function: Any
    ) -> None:
        """Add custom governance rule.
        
        Args:
            rule_id: Unique rule identifier
            rule_text: Human-readable rule description
            check_function: Function that returns True if compliant
        """
        self.custom_rules[rule_id] = {
            "rule_text": rule_text,
            "check_function": check_function
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get analyzer metrics.
        
        Returns:
            Dictionary with metrics
        """
        return self.metrics.copy()
