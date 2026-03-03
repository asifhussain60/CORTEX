"""
Governance Rule Evaluation Engine

AC-FR-002-01: Rules evaluated in tier priority order
AC-FR-002-02: Violations returned with rule ID and message
AC-FR-002-03: Evaluation performance <5ms per rule
AC-GOV-CTX-001-04: Context-aware rule evaluation with validators
AC-P1-FIX-002: Real context extraction + graceful fallback
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from __future__ import annotations

from typing import TYPE_CHECKING

from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.core.interfaces import GovernanceRule

if TYPE_CHECKING:
    pass  # CORE-035  # interface pattern — registry lives in L3

logger = logging.getLogger(__name__)


@dataclass
class RuleViolation:
    """Represents a rule violation."""

    rule_id: str
    rule_name: str
    rule_tier: int
    severity: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"RuleViolation(rule_id={self.rule_id}, severity={self.severity})"


@dataclass
class EvaluationResult:
    """Result of rule evaluation."""

    passed: bool
    violations: List[RuleViolation]
    evaluation_time_ms: float
    rules_evaluated: int

    def __repr__(self) -> str:
        return (
            f"EvaluationResult(passed={self.passed}, "
            f"violations={len(self.violations)}, "
            f"time={self.evaluation_time_ms:.2f}ms)"
        )


class RuleEvaluator:
    """
    Evaluates governance rules against operations.

    AC-FR-002-01: Rules evaluated in tier priority order (0 > 1 > 2)
    AC-FR-002-03: Evaluation performance optimized <5ms per rule
    AC-GOV-CTX-001-04: Context-aware evaluation with validators
    AC-P1-FIX-002: Inline context extraction — no external dependency crash
    """

    # Built-in validators keyed by CORE rule ID
    _VALIDATORS: Dict[str, Callable[..., Optional["RuleViolation"]]] = {}

    def __init__(self) -> None:
        """Initialize rule evaluator with registry and audit logger."""
        from cortex.orchestrators.core.governance_registry import GovernanceRegistry  # LAZY: GovernanceRegistry lives in L3; lazy import breaks L1→L3 module-level cycle
        self.logger = EnhancedAuditLogger.instance()
        self.registry = GovernanceRegistry.instance()

        # Ensure registry is initialised with rules
        init_result = self.registry.initialize()
        if init_result.is_err():
            error_msg = (
                str(init_result.err())
                if hasattr(init_result, "err")
                else "Unknown error"
            )
            logger.warning("Registry init failed: %s", error_msg)
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-GOV-CTX-001-04",
                    operation="INIT_REGISTRY",
                    success=False,
                    details={"error": error_msg},
                )

    def evaluate_rules(
        self,
        context: Dict[str, Any],
        tier_filter: Optional[int] = None,
        category_filter: Optional[str] = None
    ) -> Result[EvaluationResult]:
        """
        Evaluate all applicable rules against context.

        AC-FR-002-01: Evaluates rules in tier priority order (Tier 0 first)
        AC-FR-002-03: Performance optimized

        Args:
            context: Operation context with relevant data
            tier_filter: Optional tier to filter (0, 1, or 2)
            category_filter: Optional category to filter

        Returns:
            EvaluationResult with violations list or Err
        """
        try:
            start_time = time.time()

            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-FR-002-01",
                    operation="EVALUATE_RULES",
                    details={
                        "context_keys": list(context.keys()),
                        "tier_filter": tier_filter,
                        "category_filter": category_filter
                    }
                )

            violations: List[RuleViolation] = []
            rules_evaluated = 0

            # Evaluate Tier 0 rules first (highest priority)
            for tier in [0, 1, 2]:
                if tier_filter is not None and tier != tier_filter:
                    continue

                rules = self._get_rules_by_tier(tier)

                for rule in rules:
                    if category_filter and rule.category != category_filter:
                        continue

                    # Evaluate rule
                    violation = self._evaluate_single_rule(rule, context)
                    if violation:
                        violations.append(violation)

                    rules_evaluated += 1

            evaluation_time_ms = (time.time() - start_time) * 1000
            passed = len(violations) == 0

            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-FR-002-01",
                    operation="EVALUATE_RULES",
                    success=True,
                    details={
                        "violations_count": len(violations),
                        "rules_evaluated": rules_evaluated,
                        "evaluation_time_ms": evaluation_time_ms
                    }
                )

            result = EvaluationResult(
                passed=passed,
                violations=violations,
                evaluation_time_ms=evaluation_time_ms,
                rules_evaluated=rules_evaluated
            )

            return Ok(result)

        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-FR-002-01",
                    operation="EVALUATE_RULES",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(f"Rule evaluation failed: {str(e)}")

    def _get_rules_by_tier(self, tier: int) -> List[GovernanceRule]:
        """Get all rules for a specific tier"""
        all_rules = self.registry.get_all_rules()

        if tier == 0:
            return all_rules.get("tier0", [])
        elif tier == 1:
            return all_rules.get("tier1", [])
        elif tier == 2:
            return all_rules.get("tier2", [])

        return []

    def _evaluate_single_rule(
        self, rule: GovernanceRule, context: Dict[str, Any]
    ) -> Optional[RuleViolation]:
        """
        Evaluate a single rule against context using inline extraction.

        AC-GOV-CTX-001-04: Context extraction → Applicability → Validation.
        Uses built-in validators per CORE rule ID. Falls back to generic
        metadata-based checking when no specific validator exists.

        Args:
            rule: Governance rule to evaluate.
            context: Operation context dict.

        Returns:
            A :class:`RuleViolation` if the rule fails, else ``None``.
        """
        try:
            file_path = context.get("file_path", context.get("target", ""))

            # ---- Applicability check (inline) ----
            # Skip rules that don't apply to the given file type
            if file_path and not self._rule_applies_to_file(rule, file_path):
                return None

            # ---- Built-in validator lookup ----
            validator_func = self._VALIDATORS.get(rule.rule_id)
            if validator_func is not None:
                return validator_func(rule, context)

            # ---- Generic evaluation fallback ----
            return self._generic_rule_check(rule, context)

        except Exception as exc:
            # On evaluation error, return a warning-level violation
            return RuleViolation(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                rule_tier=rule.tier,
                severity="warning",
                message=f"Error evaluating rule: {exc}",
                context=context,
            )

    # ------------------------------------------------------------------
    # Inline applicability
    # ------------------------------------------------------------------

    @staticmethod
    def _rule_applies_to_file(rule: GovernanceRule, file_path: str) -> bool:
        """
        Determine whether a rule is applicable to a given file.

        Args:
            rule: The governance rule.
            file_path: Target file path.

        Returns:
            True if the rule should be evaluated for this file.
        """
        # Test files are exempt from docstring/type-hint rules at tier 2
        if rule.tier >= 2 and "/tests/" in file_path:
            return False

        # Config / YAML files are exempt from code-quality rules
        if file_path.endswith((".yaml", ".yml", ".toml", ".cfg", ".ini")):
            return False

        return True

    # ------------------------------------------------------------------
    # Generic fallback check
    # ------------------------------------------------------------------

    @staticmethod
    def _generic_rule_check(
        rule: GovernanceRule, context: Dict[str, Any]
    ) -> Optional[RuleViolation]:
        """
        Generic metadata-based rule check.

        Checks for explicit violation flags in context
        (e.g. ``violates_core_001: True``), and handles the legacy
        SKULL-001 tier-0 protection check.

        Args:
            rule: Governance rule.
            context: Operation context dict.

        Returns:
            RuleViolation or None.
        """
        # Legacy SKULL-001 check for tier-0 protection
        if (
            rule.rule_id == "SKULL-001"
            and context.get("operation_type") == "MODIFY_TIER0"
        ):
            return RuleViolation(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                rule_tier=rule.tier,
                severity=rule.severity,
                message=(
                    f"Operation '{context.get('operation_type')}' "
                    f"violates {rule.rule_id}: {rule.description}"
                ),
                context=context,
            )

        # Check for explicit violation flag
        violation_key = f"violates_{rule.rule_id.lower().replace('-', '_')}"
        if context.get(violation_key, False):
            return RuleViolation(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                rule_tier=rule.tier,
                severity=rule.severity,
                message=f"Violation of {rule.rule_id}: {rule.description}",
                context=context,
            )

        return None

    # ------------------------------------------------------------------
    # Tier-priority evaluation
    # ------------------------------------------------------------------

    def evaluate_tier_priority(self, context: Dict[str, Any]) -> Result:
        """
        Evaluate rules respecting tier priority (tier 0 > 1 > 2).

        AC-FR-002-01: If a tier 0 rule fails, evaluation stops
        immediately because tier 0 rules are blocking.

        Args:
            context: Operation context dict.

        Returns:
            Ok(EvaluationResult) or Err on failure.
        """
        try:
            start_time = time.time()
            violations: List[RuleViolation] = []
            rules_evaluated = 0

            for tier in [0, 1, 2]:
                tier_rules = self._get_rules_by_tier(tier)
                tier_violations: List[RuleViolation] = []

                for rule in tier_rules:
                    violation = self._evaluate_single_rule(rule, context)
                    if violation:
                        tier_violations.append(violation)
                    rules_evaluated += 1

                violations.extend(tier_violations)

                # If tier 0 violations found, stop (blocking)
                if tier == 0 and tier_violations:
                    break

            evaluation_time_ms = (time.time() - start_time) * 1000
            passed = len(violations) == 0

            return Ok(
                EvaluationResult(
                    passed=passed,
                    violations=violations,
                    evaluation_time_ms=evaluation_time_ms,
                    rules_evaluated=rules_evaluated,
                )
            )

        except Exception as exc:
            return Err(f"Tier priority evaluation failed: {exc}")


# ======================================================================
# Built-in CORE rule validators (registered on class)
# ======================================================================

def _validate_core_001(rule: GovernanceRule, ctx: Dict[str, Any]) -> Optional[RuleViolation]:
    """CORE-001 — Incremental execution (<500 LOC per commit)."""
    lines_changed = ctx.get("lines_changed", 0)
    if lines_changed > 500:
        return RuleViolation(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            rule_tier=rule.tier,
            severity=rule.severity,
            message=f"Change is {lines_changed} lines (limit 500).",
            context=ctx,
        )
    return None


def _validate_core_008(rule: GovernanceRule, ctx: Dict[str, Any]) -> Optional[RuleViolation]:
    """CORE-008 — TDD mandatory (tests before code)."""
    if not ctx.get("test_file_exists", True):
        return RuleViolation(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            rule_tier=rule.tier,
            severity=rule.severity,
            message="No test file found for this module — TDD required.",
            context=ctx,
        )
    return None


def _validate_core_011(rule: GovernanceRule, ctx: Dict[str, Any]) -> Optional[RuleViolation]:
    """CORE-011 — Type hints mandatory."""
    total = ctx.get("functions_analyzed", 0)
    with_hints = ctx.get("functions_with_hints", 0)
    if total > 0 and with_hints < total:
        return RuleViolation(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            rule_tier=rule.tier,
            severity=rule.severity,
            message=f"Type hint coverage: {with_hints}/{total} functions.",
            context=ctx,
        )
    return None


def _validate_core_012(rule: GovernanceRule, ctx: Dict[str, Any]) -> Optional[RuleViolation]:
    """CORE-012 — Google-style docstrings."""
    total = ctx.get("public_apis", 0)
    documented = ctx.get("documented_apis", 0)
    if total > 0 and documented < total:
        return RuleViolation(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            rule_tier=rule.tier,
            severity=rule.severity,
            message=f"Docstring coverage: {documented}/{total} public APIs.",
            context=ctx,
        )
    return None


def _validate_core_013(rule: GovernanceRule, ctx: Dict[str, Any]) -> Optional[RuleViolation]:
    """CORE-013 — No bare except."""
    bare = ctx.get("bare_except_count", 0)
    if bare > 0:
        return RuleViolation(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            rule_tier=rule.tier,
            severity=rule.severity,
            message=f"Found {bare} bare except clause(s).",
            context=ctx,
        )
    return None


# Register built-in validators
RuleEvaluator._VALIDATORS = {
    "CORE-001": _validate_core_001,
    "CORE-008": _validate_core_008,
    "CORE-011": _validate_core_011,
    "CORE-012": _validate_core_012,
    "CORE-013": _validate_core_013,
}


class ViolationReporter:
    """
    AC-FR-002-02: Reports governance rule violations with details

    Formats and reports violations with:
    - Rule ID and name
    - Severity level
    - Human-readable message
    - Context that triggered violation
    """

    def __init__(self) -> None:
        """Initialize violation reporter"""
        self.logger = EnhancedAuditLogger.instance()

    def report_violations(
        self,
        violations: List[RuleViolation],
        include_context: bool = True
    ) -> Result[Dict[str, Any]]:
        """
        Format and report violations.

        AC-FR-002-02: Returns violations with rule ID and message

        Args:
            violations: List of RuleViolation objects
            include_context: Whether to include context in report

        Returns:
            Formatted violation report or Err
        """
        try:
            if self.logger:
                self.logger.log_operation_start(
                    ac_id="AC-FR-002-02",
                    operation="REPORT_VIOLATIONS",
                    details={"violation_count": len(violations)}
                )

            report = {
                "violation_count": len(violations),
                "violations": []
            }

            # Group by severity
            by_severity = {"blocked": [], "warning": [], "info": []}

            for violation in violations:
                violation_detail = {
                    "rule_id": violation.rule_id,
                    "rule_name": violation.rule_name,
                    "rule_tier": violation.rule_tier,
                    "severity": violation.severity,
                    "message": violation.message
                }

                if include_context:
                    violation_detail["context"] = violation.context

                report["violations"].append(violation_detail)

                if violation.severity in by_severity:
                    by_severity[violation.severity].append(violation_detail)

            report["by_severity"] = by_severity

            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-FR-002-02",
                    operation="REPORT_VIOLATIONS",
                    success=True,
                    details={"violations_reported": len(violations)}
                )

            return Ok(report)

        except Exception as e:
            if self.logger:
                self.logger.log_operation_complete(
                    ac_id="AC-FR-002-02",
                    operation="REPORT_VIOLATIONS",
                    success=False,
                    details={"error": str(e)}
                )
            return Err(f"Violation reporting failed: {str(e)}")

    def format_violation_message(self, violation: RuleViolation) -> str:
        """
        Format a single violation as human-readable message.

        AC-FR-002-02: Violations with rule ID and message

        Args:
            violation: RuleViolation to format

        Returns:
            Formatted message string
        """
        severity_icon = {
            "blocked": "🚫",
            "warning": "⚠️",
            "info": "ℹ️"
        }.get(violation.severity, "")

        return (
            f"{severity_icon} [{violation.rule_id}] {violation.rule_name}\n"
            f"   Tier: {violation.rule_tier} | Severity: {violation.severity}\n"
            f"   {violation.message}"
        )

    def get_violation_summary(self, violations: List[RuleViolation]) -> str:
        """Get a summary of all violations"""
        if not violations:
            return "✓ No governance violations"

        blocked = sum(1 for v in violations if v.severity == "blocked")
        warnings = sum(1 for v in violations if v.severity == "warning")
        infos = sum(1 for v in violations if v.severity == "info")

        summary = f"📊 {len(violations)} violations: "
        parts = []
        if blocked > 0:
            parts.append(f"🚫 {blocked} blocked")
        if warnings > 0:
            parts.append(f"⚠️ {warnings} warnings")
        if infos > 0:
            parts.append(f"ℹ️ {infos} infos")

        return summary + ", ".join(parts)
