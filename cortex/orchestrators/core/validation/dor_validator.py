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
        """Initialize validator and register default checks."""
        self.checks: Dict[str, Callable] = {}
        self._register_default_checks()
    
    def _register_default_checks(self) -> None:
        """Register default DoR checks (Phase 43: AC-PHASE43-006)."""
        # Check 1: Intent classification
        self.register_check(
            "intent_classification",
            self._check_intent_classification
        )
        
        # Check 2: Context completeness
        self.register_check(
            "context_completeness",
            self._check_context_completeness
        )
        
        # Check 3: Confidence threshold
        self.register_check(
            "confidence_threshold",
            self._check_confidence_threshold
        )
        
        # Check 4: Blocking issue check
        self.register_check(
            "blocking_issue_check",
            self._check_blocking_issues
        )
        
        # Check 5: Test readiness
        self.register_check(
            "test_readiness",
            self._check_test_readiness
        )
    
    def _check_intent_classification(self, intent: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Check if intent is valid and properly classified."""
        valid_intents = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "PLAN", "AUDIT", "DESIGN"]
        
        passed = intent in valid_intents
        details = {
            "intent": intent,
            "valid_intents": valid_intents,
        }
        
        return passed, details, "BLOCKING"
    
    def _check_context_completeness(self, intent: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Check if context has required fields."""
        required_fields = ["intent"]
        
        # Add intent-specific requirements
        if intent == "IMPLEMENT":
            required_fields.extend(["feature_description"])
        elif intent == "FIX":
            required_fields.extend(["bug_description"])
        elif intent == "REFACTOR":
            required_fields.extend(["target"])
        
        missing_fields = [f for f in required_fields if f not in context]
        
        passed = len(missing_fields) == 0
        details = {
            "required_fields": required_fields,
            "missing_fields": missing_fields,
            "provided_fields": list(context.keys()),
        }
        
        return passed, details, "WARNING"
    
    def _check_confidence_threshold(self, intent: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Check if confidence score meets threshold."""
        confidence = context.get("confidence", 0.0)
        threshold = 0.7  # 70% minimum confidence
        
        passed = confidence >= threshold
        details = {
            "confidence": confidence,
            "threshold": threshold,
            "meets_threshold": passed,
        }
        
        return passed, details, "WARNING"
    
    def _check_blocking_issues(self, intent: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Check for blocking issues in context."""
        blocking_issues = context.get("blocking_issues", [])
        
        passed = len(blocking_issues) == 0
        details = {
            "blocking_issue_count": len(blocking_issues),
            "issues": blocking_issues,
        }
        
        return passed, details, "BLOCKING"
    
    def _check_test_readiness(self, intent: str, context: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """Check if TDD path is ready (tests exist)."""
        # For TDD-first enforcement
        test_readiness = context.get("test_readiness", {})
        tests_exist = test_readiness.get("tests_exist", False)
        
        # For IMPLEMENT intent, tests should exist or be planned
        if intent == "IMPLEMENT":
            passed = test_readiness.get("tests_exist") or test_readiness.get("tests_planned", False)
        else:
            passed = True  # Other intents don't strictly require tests
        
        details = {
            "intent": intent,
            "tests_exist": tests_exist,
            "tests_planned": test_readiness.get("tests_planned", False),
            "requires_tests": intent == "IMPLEMENT",
        }
        
        return passed, details, "WARNING" if intent == "IMPLEMENT" else "INFO"

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
