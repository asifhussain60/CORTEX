"""
Governance Validator - EnforcementOrchestrator integration

AC-PHASE-24: Master Orchestrator Decomposition
- Validates CORE rules
- Enforces governance gates
- Integrates with EnforcementOrchestrator
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class GovernanceValidationResult:
    """Result from governance validation."""
    rule_id: str
    passed: bool
    violation_details: Optional[Dict[str, Any]] = None
    remediation: Optional[str] = None


class GovernanceValidator:
    """
    Validates operations against governance rules.

    Responsibilities:
    - Check CORE rules compliance
    - Enforce pre-execution gates
    - Coordinate with EnforcementOrchestrator

    Example:
        validator = GovernanceValidator()
        results = validator.validate_governance(operation_type="IMPLEMENT")
    """

    def __init__(self, enforcement_orchestrator: Optional[Any] = None) -> None:
        """
        Initialize governance validator.

        Args:
            enforcement_orchestrator: Reference to EnforcementOrchestrator
        """
        self.enforcement_orchestrator = enforcement_orchestrator
        self.rules: Dict[str, Callable] = {}

    def register_rule(self, rule_id: str, rule_fn: Callable) -> None:
        """Register a governance rule."""
        self.rules[rule_id] = rule_fn

    def validate_governance(
        self,
        operation_type: str,
        context: Dict[str, Any]
    ) -> List[GovernanceValidationResult]:
        """
        Run all registered governance rules.

        Args:
            operation_type: Type of operation (IMPLEMENT, FIX, etc.)
            context: Operation context

        Returns:
            List of validation results
        """
        results: List[GovernanceValidationResult] = []

        for rule_id, rule_fn in self.rules.items():
            try:
                passed, violation_details = rule_fn(operation_type, context)
                results.append(GovernanceValidationResult(
                    rule_id=rule_id,
                    passed=passed,
                    violation_details=violation_details
                ))
            except Exception as e:
                results.append(GovernanceValidationResult(
                    rule_id=rule_id,
                    passed=False,
                    violation_details={"error": str(e)}
                ))

        return results
