"""
DoR Validator - Definition of Ready checks

AC-PHASE-24: Master Orchestrator Decomposition
- Validates intent classification
- Checks challenge completion
- Verifies confidence thresholds
- Gates before execution
"""

from __future__ import annotations

from typing import Dict, Any, List, Callable, Tuple
from dataclasses import dataclass


@dataclass
class DoRCheckResult:
    """Result from a Definition of Ready check."""
    check_name: str
    passed: bool
    details: Dict[str, Any]
    severity: str  # "BLOCKING", "WARNING", "INFO"


class DoRValidator:
    """
    Validates Definition of Ready before execution.

    Responsibilities:
    - Verify intent classification
    - Check challenge completion
    - Validate confidence scores
    - Gate operations

    Example:
        validator = DoRValidator()
        result = validator.validate_dor(intent="IMPLEMENT", context={})
    """

    def __init__(self) -> None:
        """Initialize validator."""
        self.checks: Dict[str, Callable] = {}

    def register_check(self, name: str, check_fn: Callable) -> None:
        """Register a DoR check."""
        self.checks[name] = check_fn

    def validate_dor(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> List[DoRCheckResult]:
        """
        Run all registered DoR checks.

        Args:
            intent: Intent type (IMPLEMENT, FIX, etc.)
            context: Operation context

        Returns:
            List of check results
        """
        results: List[DoRCheckResult] = []

        for check_name, check_fn in self.checks.items():
            try:
                passed, details, severity = check_fn(intent, context)
                results.append(DoRCheckResult(
                    check_name=check_name,
                    passed=passed,
                    details=details,
                    severity=severity
                ))
            except Exception as e:
                results.append(DoRCheckResult(
                    check_name=check_name,
                    passed=False,
                    details={"error": str(e)},
                    severity="WARNING"
                ))

        return results

    def is_ready(self, results: List[DoRCheckResult]) -> bool:
        """Check if all blocking checks passed."""
        blocking = [r for r in results if r.severity == "BLOCKING"]
        return all(r.passed for r in blocking)
