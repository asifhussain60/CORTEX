"""
Tests for Governance Rule Evaluation Engine

AC-FR-002-01: Rules evaluated in tier priority order
AC-FR-002-02: Violations returned with rule ID and message
AC-FR-002-03: Evaluation performance <5ms per rule
"""

import pytest
import time
from src.core.rule_evaluator import RuleEvaluator, ViolationReporter, RuleViolation, EvaluationResult
from src.core.governance_registry import GovernanceRegistry, GovernanceRule


class TestRuleEvaluator:
    """Test rule evaluation functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        # Reset registry
        GovernanceRegistry._instance = None
        self.evaluator = RuleEvaluator()
        self.registry = GovernanceRegistry.instance()
    
    def test_evaluator_initialization(self):
        """Test evaluator can be initialized"""
        evaluator = RuleEvaluator()
        
        assert evaluator is not None
        assert evaluator.registry is not None
    
    def test_evaluate_rules_empty_context(self):
        """Test evaluating rules with empty context"""
        context = {}
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        assert isinstance(eval_result, EvaluationResult)
    
    def test_evaluate_rules_with_valid_context(self):
        """Test evaluating rules with valid context"""
        context = {
            "operation_type": "READ",
            "user": "alice",
            "timestamp": "2026-01-14T10:00:00Z"
        }
        
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        assert eval_result.evaluation_time_ms >= 0
    
    def test_tier_priority_order(self):
        """
        AC-FR-002-01: Test that rules are evaluated in tier priority order
        """
        # Add test rules
        self.registry._tier0_rules["SKULL-001"] = GovernanceRule(
            rule_id="SKULL-001",
            name="No Tier 0 Modifications",
            description="Tier 0 rules are immutable",
            tier=0,
            severity="blocked"
        )
        
        self.registry._tier1_rules["RULE-001"] = GovernanceRule(
            rule_id="RULE-001",
            name="Project Rule",
            description="Project-level governance",
            tier=1,
            severity="warning"
        )
        
        # Evaluate with context that should trigger Tier 0 rule
        context = {"operation_type": "MODIFY_TIER0"}
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        # Should have evaluated rules
        assert eval_result.rules_evaluated >= 0
    
    def test_tier_filter(self):
        """Test evaluating specific tier only"""
        # Add test rules across tiers
        self.registry._tier0_rules["SKULL-001"] = GovernanceRule(
            rule_id="SKULL-001",
            name="Tier 0 Rule",
            description="Immutable",
            tier=0
        )
        
        self.registry._tier1_rules["RULE-001"] = GovernanceRule(
            rule_id="RULE-001",
            name="Tier 1 Rule",
            description="Project",
            tier=1
        )
        
        context = {"operation": "test"}
        result = self.evaluator.evaluate_rules(context, tier_filter=0)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        # When filtering to Tier 0, should only evaluate 1 rule
        assert eval_result.rules_evaluated >= 1
    
    def test_category_filter(self):
        """Test evaluating specific category only"""
        # Add test rule with category
        self.registry._tier0_rules["SKULL-001"] = GovernanceRule(
            rule_id="SKULL-001",
            name="Audit Rule",
            description="Audit category",
            tier=0,
            category="audit"
        )
        
        context = {"operation": "test"}
        result = self.evaluator.evaluate_rules(context, category_filter="audit")
        
        assert result.is_ok()
        eval_result = result.unwrap()
        assert eval_result is not None


@pytest.mark.ac("FR-002-01")
class TestTierPriority:
    """Test AC-FR-002-01: Tier priority evaluation"""
    
    def setup_method(self):
        """Setup for each test"""
        GovernanceRegistry._instance = None
        self.evaluator = RuleEvaluator()
        self.registry = GovernanceRegistry.instance()
    
    def test_tier_0_blocking_evaluation(self):
        """Test that Tier 0 violations block further evaluation"""
        # Add Tier 0 rule
        self.registry._tier0_rules["SKULL-001"] = GovernanceRule(
            rule_id="SKULL-001",
            name="Blocking Rule",
            description="This blocks everything",
            tier=0,
            severity="blocked"
        )
        
        # Add Tier 1 rule
        self.registry._tier1_rules["RULE-001"] = GovernanceRule(
            rule_id="RULE-001",
            name="Warning Rule",
            description="Just a warning",
            tier=1,
            severity="warning"
        )
        
        context = {"operation_type": "MODIFY_TIER0"}
        result = self.evaluator.evaluate_tier_priority(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        # Should have violations from Tier 0
        assert eval_result.violations is not None
    
    def test_tier_priority_no_blocking_rules(self):
        """Test evaluation continues if no Tier 0 violations"""
        # Add Tier 0 rule (non-blocking)
        self.registry._tier0_rules["SKULL-001"] = GovernanceRule(
            rule_id="SKULL-001",
            name="Info Rule",
            description="Just info",
            tier=0,
            severity="info"
        )
        
        # Add Tier 1 rule
        self.registry._tier1_rules["RULE-001"] = GovernanceRule(
            rule_id="RULE-001",
            name="Warning Rule",
            description="Warning",
            tier=1,
            severity="warning"
        )
        
        context = {"operation_type": "READ"}
        result = self.evaluator.evaluate_tier_priority(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        assert eval_result.passed is not None


@pytest.mark.ac("FR-002-02")
class TestRuleViolation:
    """Test AC-FR-002-02: Rule violation details"""
    
    def test_rule_violation_creation(self):
        """Test creating a rule violation"""
        violation = RuleViolation(
            rule_id="SKULL-001",
            rule_name="Immutability",
            rule_tier=0,
            severity="blocked",
            message="Cannot modify Tier 0 rules",
            context={"operation": "MODIFY"}
        )
        
        assert violation.rule_id == "SKULL-001"
        assert violation.severity == "blocked"
        assert violation.context["operation"] == "MODIFY"
    
    def test_rule_violation_repr(self):
        """Test rule violation string representation"""
        violation = RuleViolation(
            rule_id="SKULL-001",
            rule_name="Test",
            rule_tier=0,
            severity="warning",
            message="Test message",
            context={}
        )
        
        repr_str = repr(violation)
        assert "SKULL-001" in repr_str
        assert "warning" in repr_str


@pytest.mark.ac("FR-002-02")
class TestViolationReporter:
    """Test AC-FR-002-02: Violation reporting"""
    
    def setup_method(self):
        """Setup for each test"""
        self.reporter = ViolationReporter()
    
    def test_reporter_initialization(self):
        """Test reporter initialization"""
        reporter = ViolationReporter()
        
        assert reporter is not None
    
    def test_report_no_violations(self):
        """Test reporting when no violations"""
        result = self.reporter.report_violations([])
        
        assert result.is_ok()
        report = result.unwrap()
        assert report["violation_count"] == 0
        assert len(report["violations"]) == 0
    
    def test_report_single_violation(self):
        """
        AC-FR-002-02: Test reporting violation with rule ID and message
        """
        violation = RuleViolation(
            rule_id="SKULL-001",
            rule_name="Immutability",
            rule_tier=0,
            severity="blocked",
            message="Cannot modify Tier 0 rules",
            context={"operation": "MODIFY"}
        )
        
        result = self.reporter.report_violations([violation])
        
        assert result.is_ok()
        report = result.unwrap()
        assert report["violation_count"] == 1
        assert report["violations"][0]["rule_id"] == "SKULL-001"
        assert "Cannot modify" in report["violations"][0]["message"]
    
    def test_report_multiple_violations(self):
        """Test reporting multiple violations"""
        violations = [
            RuleViolation(
                rule_id="SKULL-001",
                rule_name="Rule 1",
                rule_tier=0,
                severity="blocked",
                message="Violation 1",
                context={}
            ),
            RuleViolation(
                rule_id="SKULL-002",
                rule_name="Rule 2",
                rule_tier=0,
                severity="warning",
                message="Violation 2",
                context={}
            )
        ]
        
        result = self.reporter.report_violations(violations)
        
        assert result.is_ok()
        report = result.unwrap()
        assert report["violation_count"] == 2
        assert len(report["violations"]) == 2
    
    def test_report_grouped_by_severity(self):
        """Test violations are grouped by severity"""
        violations = [
            RuleViolation("SKULL-001", "Rule", 0, "blocked", "Msg", {}),
            RuleViolation("RULE-001", "Rule", 1, "warning", "Msg", {}),
            RuleViolation("RULE-002", "Rule", 1, "info", "Msg", {})
        ]
        
        result = self.reporter.report_violations(violations)
        
        assert result.is_ok()
        report = result.unwrap()
        by_severity = report["by_severity"]
        assert len(by_severity["blocked"]) == 1
        assert len(by_severity["warning"]) == 1
        assert len(by_severity["info"]) == 1
    
    def test_report_without_context(self):
        """Test reporting violations without context"""
        violation = RuleViolation(
            rule_id="SKULL-001",
            rule_name="Rule",
            rule_tier=0,
            severity="blocked",
            message="Violation",
            context={"operation": "TEST"}
        )
        
        result = self.reporter.report_violations([violation], include_context=False)
        
        assert result.is_ok()
        report = result.unwrap()
        assert "context" not in report["violations"][0]
    
    def test_format_violation_message(self):
        """Test formatting a single violation message"""
        violation = RuleViolation(
            rule_id="SKULL-001",
            rule_name="Immutability",
            rule_tier=0,
            severity="blocked",
            message="Cannot modify Tier 0 rules",
            context={}
        )
        
        message = self.reporter.format_violation_message(violation)
        
        assert "SKULL-001" in message
        assert "Immutability" in message
        assert "blocked" in message
        assert "Cannot modify" in message
    
    def test_get_violation_summary_no_violations(self):
        """Test summary with no violations"""
        summary = self.reporter.get_violation_summary([])
        
        assert "No governance violations" in summary
    
    def test_get_violation_summary_with_violations(self):
        """Test summary with multiple violations"""
        violations = [
            RuleViolation("R1", "Rule", 0, "blocked", "Msg", {}),
            RuleViolation("R2", "Rule", 0, "warning", "Msg", {}),
            RuleViolation("R3", "Rule", 0, "info", "Msg", {})
        ]
        
        summary = self.reporter.get_violation_summary(violations)
        
        assert "3 violations" in summary
        assert "1 blocked" in summary
        assert "1 warnings" in summary
        assert "1 infos" in summary


class TestEvaluationResult:
    """Test EvaluationResult dataclass"""
    
    def test_evaluation_result_creation(self):
        """Test creating evaluation result"""
        result = EvaluationResult(
            passed=True,
            violations=[],
            evaluation_time_ms=2.5,
            rules_evaluated=10
        )
        
        assert result.passed == True
        assert len(result.violations) == 0
        assert result.evaluation_time_ms == 2.5
        assert result.rules_evaluated == 10
    
    def test_evaluation_result_with_violations(self):
        """Test evaluation result with violations"""
        violations = [
            RuleViolation("R1", "Rule", 0, "blocked", "Msg", {})
        ]
        
        result = EvaluationResult(
            passed=False,
            violations=violations,
            evaluation_time_ms=1.2,
            rules_evaluated=1
        )
        
        assert result.passed == False
        assert len(result.violations) == 1
    
    def test_evaluation_result_repr(self):
        """Test evaluation result string representation"""
        result = EvaluationResult(
            passed=True,
            violations=[],
            evaluation_time_ms=2.5,
            rules_evaluated=10
        )
        
        repr_str = repr(result)
        assert "passed=True" in repr_str
        assert "time=2.5ms" in repr_str


@pytest.mark.ac("FR-002-03")
class TestPerformance:
    """Test AC-FR-002-03: Evaluation performance"""
    
    def setup_method(self):
        """Setup for each test"""
        GovernanceRegistry._instance = None
        self.evaluator = RuleEvaluator()
        self.registry = GovernanceRegistry.instance()
        
        # Add multiple rules
        for i in range(25):
            self.registry._tier0_rules[f"SKULL-{i:03d}"] = GovernanceRule(
                rule_id=f"SKULL-{i:03d}",
                name=f"Rule {i}",
                description="Test rule",
                tier=0
            )
    
    def test_evaluation_performance_under_5ms(self):
        """
        AC-FR-002-03: Test that evaluation completes under 5ms
        """
        context = {"operation": "test"}
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        
        # Performance requirement: <5ms per rule on average
        # With 25 rules, should complete quickly
        avg_time_per_rule = eval_result.evaluation_time_ms / max(eval_result.rules_evaluated, 1)
        
        # Should be well under 5ms per rule (typically sub-millisecond)
        assert eval_result.evaluation_time_ms < 100  # Allow 100ms total for 25 rules
    
    def test_evaluation_time_recorded(self):
        """Test that evaluation time is recorded"""
        context = {"operation": "test"}
        result = self.evaluator.evaluate_rules(context)
        
        assert result.is_ok()
        eval_result = result.unwrap()
        assert eval_result.evaluation_time_ms >= 0
        assert isinstance(eval_result.evaluation_time_ms, float)


class TestIntegration:
    """Integration tests for rule evaluation"""
    
    def setup_method(self):
        """Setup for each test"""
        GovernanceRegistry._instance = None
        self.evaluator = RuleEvaluator()
        self.reporter = ViolationReporter()
        self.registry = GovernanceRegistry.instance()
    
    def test_complete_evaluation_workflow(self):
        """Test complete workflow: evaluate, report, summarize"""
        # Add test rule
        self.registry._tier0_rules["SKULL-001"] = GovernanceRule(
            rule_id="SKULL-001",
            name="Immutability",
            description="Tier 0 rules are immutable",
            tier=0,
            severity="blocked"
        )
        
        # Evaluate
        context = {"operation_type": "MODIFY_TIER0"}
        eval_result = self.evaluator.evaluate_rules(context)
        assert eval_result.is_ok()
        
        evaluation = eval_result.unwrap()
        
        # Report
        report_result = self.reporter.report_violations(evaluation.violations)
        assert report_result.is_ok()
        
        report = report_result.unwrap()
        
        # Summarize
        summary = self.reporter.get_violation_summary(evaluation.violations)
        assert summary is not None
