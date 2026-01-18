"""
Governance Rule Evaluation Engine

AC-FR-002-01: Rules evaluated in tier priority order
AC-FR-002-02: Violations returned with rule ID and message
AC-FR-002-03: Evaluation performance <5ms per rule
"""

import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from cortex.brain.core.governance_registry import GovernanceRegistry, GovernanceRule
from cortex.brain.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class RuleViolation:
    """Represents a rule violation"""
    rule_id: str
    rule_name: str
    rule_tier: int
    severity: str
    message: str
    context: Dict[str, Any]
    
    def __repr__(self) -> str:
        return f"RuleViolation(rule_id={self.rule_id}, severity={self.severity})"


@dataclass
class EvaluationResult:
    """Result of rule evaluation"""
    passed: bool
    violations: List[RuleViolation]
    evaluation_time_ms: float
    rules_evaluated: int
    
    def __repr__(self) -> str:
        return f"EvaluationResult(passed={self.passed}, violations={len(self.violations)}, time={self.evaluation_time_ms}ms)"


class RuleEvaluator:
    """
    Evaluates governance rules against operations.
    
    AC-FR-002-01: Rules evaluated in tier priority order (0 > 1 > 2)
    AC-FR-002-03: Evaluation performance optimized <5ms per rule
    """
    
    def __init__(self):
        """Initialize rule evaluator"""
        self.logger = EnhancedAuditLogger.instance()
        self.registry = GovernanceRegistry.instance()
    
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
    
    def _evaluate_single_rule(self, rule: GovernanceRule, context: Dict[str, Any]) -> Optional[RuleViolation]:
        """
        Evaluate a single rule against context.
        
        Returns violation if rule fails, None if passes
        """
        try:
            # Rule matching logic based on rule_id and context
            # This is a simplified version - real implementation would have complex matching
            
            # Example: Check if operation type matches rule
            if "operation_type" in context:
                op_type = context["operation_type"]
                
                # SKULL-001: No modifications to Tier 0 rules
                if rule.rule_id == "SKULL-001" and op_type == "MODIFY_TIER0":
                    return RuleViolation(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        rule_tier=rule.tier,
                        severity=rule.severity,
                        message=f"Operation '{op_type}' violates {rule.rule_id}: {rule.description}",
                        context=context
                    )
            
            # Check if rule should apply based on context
            # Return None if rule passes
            return None
        
        except Exception as e:
            # On evaluation error, return violation with error details
            return RuleViolation(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                rule_tier=rule.tier,
                severity="warning",
                message=f"Error evaluating rule: {str(e)}",
                context=context
            )
    
    def evaluate_tier_priority(self, context: Dict[str, Any]) -> Result[EvaluationResult]:
        """
        AC-FR-002-01: Evaluate rules respecting tier priority (0 > 1 > 2)
        
        If Tier 0 rule fails, stop evaluation (Tier 0 is blocking)
        """
        try:
            start_time = time.time()
            
            violations: List[RuleViolation] = []
            rules_evaluated = 0
            
            # Evaluate Tier 0 first - if any violation, they're blocking
            for tier in [0, 1, 2]:
                tier_rules = self._get_rules_by_tier(tier)
                tier_violations = []
                
                for rule in tier_rules:
                    violation = self._evaluate_single_rule(rule, context)
                    if violation:
                        tier_violations.append(violation)
                    rules_evaluated += 1
                
                violations.extend(tier_violations)
                
                # If Tier 0 violations found, stop (blocking)
                if tier == 0 and tier_violations:
                    break
            
            evaluation_time_ms = (time.time() - start_time) * 1000
            passed = len(violations) == 0
            
            return Ok(EvaluationResult(
                passed=passed,
                violations=violations,
                evaluation_time_ms=evaluation_time_ms,
                rules_evaluated=rules_evaluated
            ))
        
        except Exception as e:
            return Err(f"Tier priority evaluation failed: {str(e)}")


class ViolationReporter:
    """
    AC-FR-002-02: Reports governance rule violations with details
    
    Formats and reports violations with:
    - Rule ID and name
    - Severity level
    - Human-readable message
    - Context that triggered violation
    """
    
    def __init__(self):
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
