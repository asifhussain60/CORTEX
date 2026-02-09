"""
Phase 52 S2.3: Comprehensive Rule Testing Suite

30+ tests covering:
- Rule creation and validation
- Condition evaluation (all operators)
- Rule evaluation with context
- Rule composition and grouping
- Conflict detection and resolution
- Performance and optimization
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add orchestrator module to path
sys.path.insert(0, str(Path(__file__).parent.parent / "cortex" / "orchestrators" / "pr_review"))

from rule_engine import (
    Rule, RuleEngine, Condition, ConditionOperator, RuleAction, RulePriority,
    RuleEvaluationResult, RulesetEvaluationResult, StandardRules, RuleActionDefinition
)
from rule_composer import (
    RuleComposer, RuleGroup, ConflictResolutionStrategy, RuleValidator,
    RuleOptimizer, RuleExecutionPlan
)


class TestConditionEvaluation:
    """Test condition evaluation with all operators"""

    def test_condition_equals_operator(self):
        """Test EQUALS operator"""
        cond = Condition("status", ConditionOperator.EQUALS, "approved")
        assert cond.evaluate({"status": "approved"})
        assert not cond.evaluate({"status": "pending"})

    def test_condition_not_equals_operator(self):
        """Test NOT_EQUALS operator"""
        cond = Condition("status", ConditionOperator.NOT_EQUALS, "blocked")
        assert cond.evaluate({"status": "approved"})
        assert not cond.evaluate({"status": "blocked"})

    def test_condition_contains_operator_list(self):
        """Test CONTAINS operator with lists"""
        cond = Condition("tags", ConditionOperator.CONTAINS, "security")
        assert cond.evaluate({"tags": ["security", "performance"]})
        assert not cond.evaluate({"tags": ["docs"]})

    def test_condition_contains_operator_string(self):
        """Test CONTAINS operator with strings"""
        cond = Condition("description", ConditionOperator.CONTAINS, "API")
        assert cond.evaluate({"description": "Fix API endpoint"})
        assert not cond.evaluate({"description": "Fix database"})

    def test_condition_not_contains_operator(self):
        """Test NOT_CONTAINS operator"""
        cond = Condition("file_path", ConditionOperator.NOT_CONTAINS, "test")
        assert cond.evaluate({"file_path": "src/main.py"})
        assert not cond.evaluate({"file_path": "tests/test_main.py"})

    def test_condition_matches_regex(self):
        """Test MATCHES_REGEX operator"""
        cond = Condition("branch_name", ConditionOperator.MATCHES_REGEX, r"^hotfix/")
        assert cond.evaluate({"branch_name": "hotfix/critical-bug"})
        assert not cond.evaluate({"branch_name": "feature/new-feature"})

    def test_condition_not_matches_regex(self):
        """Test NOT_MATCHES_REGEX operator"""
        cond = Condition("branch_name", ConditionOperator.NOT_MATCHES_REGEX, r"^wip/")
        assert cond.evaluate({"branch_name": "feature/new"})
        assert not cond.evaluate({"branch_name": "wip/in-progress"})

    def test_condition_greater_than(self):
        """Test GREATER_THAN operator"""
        cond = Condition("changed_lines", ConditionOperator.GREATER_THAN, 500)
        assert cond.evaluate({"changed_lines": 600})
        assert not cond.evaluate({"changed_lines": 300})

    def test_condition_less_than(self):
        """Test LESS_THAN operator"""
        cond = Condition("file_count", ConditionOperator.LESS_THAN, 5)
        assert cond.evaluate({"file_count": 3})
        assert not cond.evaluate({"file_count": 10})

    def test_condition_in_list(self):
        """Test IN_LIST operator"""
        cond = Condition("author", ConditionOperator.IN_LIST, ["alice", "bob", "charlie"])
        assert cond.evaluate({"author": "bob"})
        assert not cond.evaluate({"author": "dave"})

    def test_condition_not_in_list(self):
        """Test NOT_IN_LIST operator"""
        cond = Condition("author", ConditionOperator.NOT_IN_LIST, ["bot", "automated"])
        assert cond.evaluate({"author": "alice"})
        assert not cond.evaluate({"author": "bot"})


class TestRuleDefinition:
    """Test rule creation and validation"""

    def test_create_basic_rule(self):
        """Test creating basic rule"""
        rule = Rule(
            rule_id="TST-001",
            name="Test Rule",
            description="Test",
            conditions=[Condition("status", ConditionOperator.EQUALS, "draft")],
            actions=[RuleActionDefinition(RuleAction.BLOCK, message="Draft PRs blocked")]
        )
        assert rule.rule_id == "TST-001"
        assert rule.enabled

    def test_rule_with_multiple_conditions_and(self):
        """Test rule with AND logic"""
        rule = Rule(
            rule_id="TST-002",
            name="Multiple Conditions AND",
            description="Test AND",
            condition_logic="AND",
            conditions=[
                Condition("has_tests", ConditionOperator.EQUALS, False),
                Condition("has_code_changes", ConditionOperator.EQUALS, True)
            ],
            actions=[RuleAction(RuleAction.REQUEST_CHANGES)]
        )
        
        # Both true
        assert rule.evaluate({"has_tests": False, "has_code_changes": True})
        # One false
        assert not rule.evaluate({"has_tests": True, "has_code_changes": True})

    def test_rule_with_multiple_conditions_or(self):
        """Test rule with OR logic"""
        rule = Rule(
            rule_id="TST-003",
            name="Multiple Conditions OR",
            description="Test OR",
            condition_logic="OR",
            conditions=[
                Condition("is_draft", ConditionOperator.EQUALS, True),
                Condition("has_wip_label", ConditionOperator.EQUALS, True)
            ],
            actions=[RuleAction(RuleAction.COMMENT)]
        )
        
        # Both false
        assert not rule.evaluate({"is_draft": False, "has_wip_label": False})
        # One true
        assert rule.evaluate({"is_draft": True, "has_wip_label": False})

    def test_rule_scope_matching_includes(self):
        """Test rule scope matching with includes"""
        rule = Rule(
            rule_id="TST-004",
            name="Scope Test",
            description="Scope test rule",
            applies_to=["*.py", "src/**/*.ts"]
        )
        
        assert rule.matches_scope("main.py")
        assert rule.matches_scope("src/app.ts")
        assert not rule.matches_scope("docs/readme.md")

    def test_rule_scope_matching_excludes(self):
        """Test rule scope matching with excludes"""
        rule = Rule(
            rule_id="TST-005",
            name="Scope Exclude Test",
            description="Scope exclude test rule",
            applies_to=["src/**/*.py"],
            excludes=["**/test_*.py"]
        )
        
        assert rule.matches_scope("src/main.py")
        assert not rule.matches_scope("src/test_main.py")


class TestRuleEngine:
    """Test rule engine core functionality"""

    def test_engine_add_rule(self):
        """Test adding rules to engine"""
        engine = RuleEngine()
        rule = Rule(rule_id="E-001", name="Test", description="Test rule", conditions=[], actions=[RuleActionDefinition(RuleAction.SKIP)])
        
        engine.add_rule(rule)
        assert "E-001" in engine.rules
        assert engine.rules["E-001"] == rule

    def test_engine_add_rule_without_id_fails(self):
        """Test that rules without ID are rejected"""
        engine = RuleEngine()
        rule = Rule(rule_id="", name="Test", description="Test rule", conditions=[], actions=[RuleActionDefinition(RuleAction.SKIP)])
        
        with pytest.raises(ValueError):
            engine.add_rule(rule)

    def test_engine_enable_disable_rule(self):
        """Test enabling/disabling rules"""
        engine = RuleEngine()
        rule = Rule(rule_id="E-002", name="Test", description="Test rule", conditions=[], actions=[RuleActionDefinition(RuleAction.SKIP)])
        engine.add_rule(rule)
        
        assert engine.disable_rule("E-002")
        assert not engine.rules["E-002"].enabled
        
        assert engine.enable_rule("E-002")
        assert engine.rules["E-002"].enabled

    def test_engine_remove_rule(self):
        """Test removing rules"""
        engine = RuleEngine()
        rule = Rule(rule_id="E-003", name="Test", description="Test rule", conditions=[], actions=[RuleActionDefinition(RuleAction.SKIP)])
        engine.add_rule(rule)
        
        assert engine.remove_rule("E-003")
        assert "E-003" not in engine.rules

    def test_engine_evaluate_pr_single_match(self):
        """Test PR evaluation with single matching rule"""
        engine = RuleEngine()
        rule = Rule(
            rule_id="E-004",
            name="Large PR",
            description="Large PR rule",
            priority=RulePriority.MEDIUM,
            conditions=[Condition("changed_lines", ConditionOperator.GREATER_THAN, 100)],
            actions=[RuleActionDefinition(RuleAction.COMMENT, message="Large PR")]
        )
        engine.add_rule(rule)
        
        result = engine.evaluate_pr({"changed_lines": 500})
        assert len(result.matching_rules) == 1
        assert result.matching_rules[0].rule_id == "E-004"
        assert result.recommended_action == RuleAction.COMMENT

    def test_engine_evaluate_pr_multiple_matches(self):
        """Test PR evaluation with multiple matching rules"""
        engine = RuleEngine()
        
        rule1 = Rule(
            rule_id="E-005",
            name="Has Code",
            description="Has code rule",
            priority=RulePriority.HIGH,
            conditions=[Condition("has_code", ConditionOperator.EQUALS, True)],
            actions=[RuleActionDefinition(RuleAction.REQUEST_CHANGES)]
        )
        
        rule2 = Rule(
            rule_id="E-006",
            name="Large PR",
            description="Large PR rule",
            priority=RulePriority.MEDIUM,
            conditions=[Condition("changed_lines", ConditionOperator.GREATER_THAN, 100)],
            actions=[RuleActionDefinition(RuleAction.COMMENT)]
        )
        
        engine.add_rule(rule1)
        engine.add_rule(rule2)
        
        result = engine.evaluate_pr({"has_code": True, "changed_lines": 500})
        assert len(result.matching_rules) == 2

    def test_engine_evaluate_pr_no_matches(self):
        """Test PR evaluation with no matching rules"""
        engine = RuleEngine()
        rule = Rule(
            rule_id="E-007",
            name="Docs Only",
            description="Docs only rule",
            conditions=[Condition("only_docs", ConditionOperator.EQUALS, True)],
            actions=[RuleActionDefinition(RuleAction.APPROVE)]
        )
        engine.add_rule(rule)
        
        result = engine.evaluate_pr({"only_docs": False})
        assert len(result.matching_rules) == 0

    def test_engine_get_stats(self):
        """Test engine statistics"""
        engine = RuleEngine()
        
        for i in range(3):
            rule = Rule(
                rule_id=f"STAT-{i}",
                name=f"Rule {i}",
                description=f"Rule {i}",
                priority=[RulePriority.CRITICAL, RulePriority.HIGH, RulePriority.MEDIUM][i],
                conditions=[],
                actions=[RuleActionDefinition(RuleAction.SKIP)]
            )
            engine.add_rule(rule)
        
        stats = engine.get_rule_stats()
        assert stats["total_rules"] == 3
        assert stats["enabled_rules"] == 3
        assert stats["by_priority"]["critical"] == 1
        assert stats["by_priority"]["high"] == 1
        assert stats["by_priority"]["medium"] == 1


class TestRuleComposer:
    """Test rule composition and grouping"""

    def test_composer_add_group(self):
        """Test adding rule groups"""
        engine = RuleEngine()
        composer = RuleComposer(engine)
        
        group = RuleGroup(
            group_id="GRP-001",
            name="Security",
            description="Security rules",
            rules=["SEC-001", "SEC-002"]
        )
        
        composer.add_group(group)
        assert "GRP-001" in composer.groups

    def test_composer_enable_disable_group(self):
        """Test enabling/disabling groups"""
        engine = RuleEngine()
        composer = RuleComposer(engine)
        
        rule = Rule(rule_id="GRP-TEST-001", name="Test", description="Test rule", conditions=[], actions=[RuleActionDefinition(RuleAction.SKIP)])
        engine.add_rule(rule)
        
        group = RuleGroup(group_id="GRP-002", name="Test Group", description="Test group", rules=["GRP-TEST-001"])
        composer.add_group(group)
        
        assert composer.disable_group("GRP-002")
        assert not engine.rules["GRP-TEST-001"].enabled
        
        assert composer.enable_group("GRP-002")
        assert engine.rules["GRP-TEST-001"].enabled

    def test_composer_conflict_detection(self):
        """Test conflict detection between rules"""
        engine = RuleEngine()
        composer = RuleComposer(engine)
        
        rule_block = Rule(
            rule_id="CONF-001",
            name="Block",
            description="Block rule",
            conditions=[Condition("security_issue", ConditionOperator.EQUALS, True)],
            actions=[RuleActionDefinition(RuleAction.BLOCK)]
        )
        
        rule_approve = Rule(
            rule_id="CONF-002",
            name="Approve",
            description="Approve rule",
            conditions=[Condition("security_issue", ConditionOperator.EQUALS, True)],
            actions=[RuleActionDefinition(RuleAction.APPROVE)]
        )
        
        engine.add_rule(rule_block)
        engine.add_rule(rule_approve)
        
        result = engine.evaluate_pr({"security_issue": True})
        conflicts = composer._detect_conflicts(result)
        assert len(conflicts) > 0

    def test_composer_conflict_resolution_most_restrictive(self):
        """Test most restrictive conflict resolution"""
        engine = RuleEngine()
        composer = RuleComposer(engine)
        
        rule_block = Rule(
            rule_id="RES-001",
            name="Block",
            description="Block rule",
            conditions=[Condition("flag", ConditionOperator.EQUALS, True)],
            actions=[RuleActionDefinition(RuleAction.BLOCK)]
        )
        
        rule_approve = Rule(
            rule_id="RES-002",
            name="Approve",
            description="Approve rule",
            conditions=[Condition("flag", ConditionOperator.EQUALS, True)],
            actions=[RuleActionDefinition(RuleAction.APPROVE)]
        )
        
        engine.add_rule(rule_block)
        engine.add_rule(rule_approve)
        
        result = composer.evaluate_with_composition(
            {"flag": True},
            strategy=ConflictResolutionStrategy.MOST_RESTRICTIVE
        )
        
        assert result.recommended_action == RuleAction.BLOCK


class TestStandardRules:
    """Test pre-built standard rules"""

    def test_standard_rule_require_tests(self):
        """Test standard rule: require tests"""
        rule = StandardRules.require_tests_for_code_changes()
        assert rule.rule_id == "STD-001"
        assert rule.priority == RulePriority.HIGH

    def test_standard_rule_block_secrets(self):
        """Test standard rule: block secrets"""
        rule = StandardRules.block_secrets_in_pr()
        assert rule.rule_id == "STD-002"
        assert rule.priority == RulePriority.CRITICAL

    def test_standard_rule_approve_docs(self):
        """Test standard rule: approve docs"""
        rule = StandardRules.approve_docs_only()
        assert rule.rule_id == "STD-003"
        assert rule.priority == RulePriority.LOW

    def test_standard_rule_large_pr_warning(self):
        """Test standard rule: large PR warning"""
        rule = StandardRules.large_pr_warning()
        assert rule.rule_id == "STD-004"
        assert rule.priority == RulePriority.MEDIUM


class TestRuleValidator:
    """Test rule validation"""

    def test_validate_valid_rule(self):
        """Test validating a valid rule"""
        rule = Rule(
            rule_id="VAL-001",
            name="Test",
            description="Test rule",
            conditions=[Condition("flag", ConditionOperator.EQUALS, True)],
            actions=[RuleAction(RuleAction.APPROVE)]
        )
        
        valid, errors = RuleValidator.validate_rule(rule)
        assert valid
        assert len(errors) == 0

    def test_validate_rule_missing_id(self):
        """Test validation fails for missing ID"""
        rule = Rule(
            rule_id="",
            name="Test",
            conditions=[],
            actions=[RuleAction(RuleAction.SKIP)]
        )
        
        valid, errors = RuleValidator.validate_rule(rule)
        assert not valid
        assert any("rule_id" in e for e in errors)

    def test_validate_rule_no_conditions_or_actions(self):
        """Test validation fails for no conditions or actions"""
        rule = Rule(rule_id="VAL-002", name="Empty", conditions=[], actions=[])
        
        valid, errors = RuleValidator.validate_rule(rule)
        assert not valid

    def test_validate_ruleset(self):
        """Test validating entire ruleset"""
        engine = RuleEngine()
        engine.add_rule(Rule(
            rule_id="VSET-001",
            name="Test",
            conditions=[Condition("flag", ConditionOperator.EQUALS, True)],
            actions=[RuleAction(RuleAction.APPROVE)]
        ))
        
        valid, errors = RuleValidator.validate_ruleset(engine)
        assert valid


class TestRuleOptimizer:
    """Test rule optimization"""

    def test_optimizer_analyze_dependencies(self):
        """Test dependency analysis"""
        engine = RuleEngine()
        engine.add_rule(Rule(
            rule_id="OPT-001",
            name="Test",
            description="Test rule",
            conditions=[
                Condition("has_tests", ConditionOperator.EQUALS, True),
                Condition("changed_lines", ConditionOperator.GREATER_THAN, 100)
            ],
            actions=[RuleActionDefinition(RuleAction.COMMENT)]
        ))
        
        deps = RuleOptimizer.analyze_dependencies(engine)
        assert "OPT-001" in deps
        assert "has_tests" in deps["OPT-001"]
        assert "changed_lines" in deps["OPT-001"]

    def test_optimizer_create_execution_plan(self):
        """Test creating execution plan"""
        engine = RuleEngine()
        for i in range(3):
            engine.add_rule(Rule(
                rule_id=f"PLAN-{i}",
                name=f"Rule {i}",
                description=f"Rule {i}",
                priority=[RulePriority.CRITICAL, RulePriority.HIGH, RulePriority.MEDIUM][i],
                conditions=[],
                actions=[RuleActionDefinition(RuleAction.SKIP)]
            ))
        
        plan = RuleOptimizer.create_execution_plan(engine)
        assert isinstance(plan, RuleExecutionPlan)
        assert len(plan.rules_to_evaluate) == 3
        assert plan.estimated_time_ms > 0
        assert len(plan.priority_order) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
