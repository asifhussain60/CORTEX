"""
Phase 52 S2.1: Automated Code Review Rules Engine

Configurable PR review rule system supporting:
- Custom rule definitions (conditions, actions, precedence)
- Rule evaluation against PR metadata and diffs
- Action execution (APPROVE, BLOCK, COMMENT, REQUEST_CHANGES)
- Rule inheritance and composition
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set
from abc import ABC, abstractmethod
import re
import logging

logger = logging.getLogger(__name__)


class RuleAction(Enum):
    """Actions that rules can trigger"""
    APPROVE = "approve"
    BLOCK = "block"
    COMMENT = "comment"
    REQUEST_CHANGES = "request_changes"
    WARN = "warn"
    SKIP = "skip"


class ConditionOperator(Enum):
    """Operators for rule conditions"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    MATCHES_REGEX = "matches_regex"
    NOT_MATCHES_REGEX = "not_matches_regex"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"


class RulePriority(Enum):
    """Rule execution priority levels"""
    CRITICAL = 100
    HIGH = 75
    MEDIUM = 50
    LOW = 25
    MINIMAL = 10


@dataclass
class Condition:
    """Single condition in a rule"""
    field: str  # Field to check (e.g., 'file_extensions', 'author', 'changed_lines')
    operator: ConditionOperator
    value: Any
    description: Optional[str] = None

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate condition against context"""
        field_value = context.get(self.field)
        
        if self.operator == ConditionOperator.EQUALS:
            return field_value == self.value
        elif self.operator == ConditionOperator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == ConditionOperator.CONTAINS:
            return isinstance(field_value, (list, str)) and self.value in field_value
        elif self.operator == ConditionOperator.NOT_CONTAINS:
            return not (isinstance(field_value, (list, str)) and self.value in field_value)
        elif self.operator == ConditionOperator.MATCHES_REGEX:
            return isinstance(field_value, str) and re.search(self.value, field_value) is not None
        elif self.operator == ConditionOperator.NOT_MATCHES_REGEX:
            return not (isinstance(field_value, str) and re.search(self.value, field_value) is not None)
        elif self.operator == ConditionOperator.GREATER_THAN:
            return isinstance(field_value, (int, float)) and field_value > self.value
        elif self.operator == ConditionOperator.LESS_THAN:
            return isinstance(field_value, (int, float)) and field_value < self.value
        elif self.operator == ConditionOperator.IN_LIST:
            return field_value in self.value
        elif self.operator == ConditionOperator.NOT_IN_LIST:
            return field_value not in self.value
        else:
            return False


@dataclass
class RuleActionDefinition:
    """Action triggered by rule"""
    action: RuleAction
    message: Optional[str] = None
    severity: Optional[str] = None
    auto_dismiss: bool = False


@dataclass
class Rule:
    """Configurable review rule"""
    rule_id: str
    name: str
    description: str
    enabled: bool = True
    priority: RulePriority = RulePriority.MEDIUM
    conditions: List[Condition] = field(default_factory=list)
    actions: List[RuleActionDefinition] = field(default_factory=list)
    condition_logic: str = "AND"  # AND or OR
    tags: List[str] = field(default_factory=list)
    max_violations: int = 1
    applies_to: List[str] = field(default_factory=list)  # File patterns
    excludes: List[str] = field(default_factory=list)   # Exclude patterns

    def matches_scope(self, file_path: str) -> bool:
        """Check if rule applies to file"""
        if not self.applies_to:
            return True
        
        matches_include = any(self._pattern_matches(file_path, p) for p in self.applies_to)
        
        if self.excludes:
            matches_exclude = any(self._pattern_matches(file_path, p) for p in self.excludes)
            return matches_include and not matches_exclude
        
        return matches_include

    @staticmethod
    def _pattern_matches(path: str, pattern: str) -> bool:
        """Check if path matches glob-like pattern.
        
        Supports standard glob patterns including:
        - * matches any characters except /
        - ** matches any characters including /
        - ? matches single character
        """
        import fnmatch
        from pathlib import PurePath
        
        # Handle ** glob pattern (recursive match)
        if '**' in pattern:
            # Convert ** to fnmatch-compatible pattern
            # src/**/*.ts -> matches src/app.ts, src/foo/bar.ts
            pattern_parts = pattern.split('**')
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                prefix = prefix.rstrip('/')
                suffix = suffix.lstrip('/')
                
                # If path starts with prefix and ends matching suffix
                if prefix and not path.startswith(prefix.rstrip('*')):
                    return False
                
                if suffix:
                    return fnmatch.fnmatch(PurePath(path).name, suffix) or \
                           fnmatch.fnmatch(path, pattern.replace('**/', '*').replace('**', '*'))
                return True
        
        return fnmatch.fnmatch(path, pattern)

    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate all conditions"""
        if not self.enabled or not self.conditions:
            return False
        
        results = [cond.evaluate(context) for cond in self.conditions]
        
        if self.condition_logic == "AND":
            return all(results)
        elif self.condition_logic == "OR":
            return any(results)
        else:
            return False


@dataclass
class RuleEvaluationResult:
    """Result of evaluating rules"""
    rule_id: str
    name: str
    matched: bool
    priority: int
    actions: List[RuleActionDefinition]
    message: Optional[str] = None


@dataclass
class RulesetEvaluationResult:
    """Overall ruleset evaluation result"""
    matching_rules: List[RuleEvaluationResult] = field(default_factory=list)
    recommended_action: RuleAction = RuleAction.SKIP
    confidence: float = 0.5
    blocking_violations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def should_block(self) -> bool:
        """Check if any rule recommends blocking"""
        return any(r.actions and any(a.action == RuleAction.BLOCK for a in r.actions) 
                   for r in self.matching_rules)

    @property
    def should_approve(self) -> bool:
        """Check if all conditions favor approval"""
        return not self.should_block and all(
            not any(a.action == RuleAction.REQUEST_CHANGES for a in r.actions)
            for r in self.matching_rules
        )


class RuleEngine:
    """Central rule evaluation engine"""

    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules: Dict[str, Rule] = {}
        self.evaluation_cache: Dict[str, RulesetEvaluationResult] = {}
        
        if rules:
            for rule in rules:
                self.add_rule(rule)

    def add_rule(self, rule: Rule) -> None:
        """Register a rule"""
        if not rule.rule_id:
            raise ValueError("Rule must have rule_id")
        self.rules[rule.rule_id] = rule
        logger.info(f"Added rule: {rule.rule_id} ({rule.name})")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed rule: {rule_id}")
            return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            return True
        return False

    def evaluate_pr(self, pr_context: Dict[str, Any], file_path: Optional[str] = None) -> RulesetEvaluationResult:
        """Evaluate PR against all rules"""
        result = RulesetEvaluationResult()
        
        # Sort rules by priority (highest first)
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda r: r.priority.value,
            reverse=True
        )
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Check scope if file_path provided
            if file_path and rule.applies_to:
                if not rule.matches_scope(file_path):
                    continue
            
            # Evaluate rule
            if rule.evaluate(pr_context):
                eval_result = RuleEvaluationResult(
                    rule_id=rule.rule_id,
                    name=rule.name,
                    matched=True,
                    priority=rule.priority.value,
                    actions=rule.actions,
                    message=rule.description
                )
                result.matching_rules.append(eval_result)
                
                # Update warnings
                if rule.priority == RulePriority.HIGH:
                    result.warnings.append(f"{rule.name}: {rule.description}")
                
                # Check for blocks
                if any(a.action == RuleAction.BLOCK for a in rule.actions):
                    result.blocking_violations.append(rule.rule_id)
        
        # Calculate confidence based on matching rules
        if result.matching_rules:
            blocking_count = len(result.blocking_violations)
            total_count = len(result.matching_rules)
            result.confidence = 1.0 - (blocking_count / total_count)
            
            if result.should_block:
                result.recommended_action = RuleAction.BLOCK
            elif result.should_approve:
                result.recommended_action = RuleAction.APPROVE
            else:
                result.recommended_action = RuleAction.COMMENT
        
        return result

    def get_rule_stats(self) -> Dict[str, Any]:
        """Get ruleset statistics"""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules.values() if r.enabled]),
            "by_priority": {
                "critical": len([r for r in self.rules.values() if r.priority == RulePriority.CRITICAL]),
                "high": len([r for r in self.rules.values() if r.priority == RulePriority.HIGH]),
                "medium": len([r for r in self.rules.values() if r.priority == RulePriority.MEDIUM]),
                "low": len([r for r in self.rules.values() if r.priority == RulePriority.LOW]),
            }
        }


# Standard rule templates
class StandardRules:
    """Pre-built rule templates"""

    @staticmethod
    def require_tests_for_code_changes() -> Rule:
        """Require test additions for code changes"""
        return Rule(
            rule_id="STD-001",
            name="Require Tests for Code Changes",
            description="PR must include tests for new code",
            priority=RulePriority.HIGH,
            conditions=[
                Condition(
                    field="has_code_changes",
                    operator=ConditionOperator.EQUALS,
                    value=True
                ),
                Condition(
                    field="has_test_changes",
                    operator=ConditionOperator.EQUALS,
                    value=False
                )
            ],
            actions=[RuleActionDefinition(action=RuleAction.REQUEST_CHANGES, message="Add tests for code changes")],
            applies_to=["*.py", "src/**/*.ts"]
        )

    @staticmethod
    def block_secrets_in_pr() -> Rule:
        """Block PRs containing secrets"""
        return Rule(
            rule_id="STD-002",
            name="Block Secrets in PR",
            description="PR contains potential secrets",
            priority=RulePriority.CRITICAL,
            conditions=[
                Condition(
                    field="has_secrets",
                    operator=ConditionOperator.EQUALS,
                    value=True
                )
            ],
            actions=[RuleActionDefinition(action=RuleAction.BLOCK, message="Secrets detected in diff")],
        )

    @staticmethod
    def approve_docs_only() -> Rule:
        """Auto-approve documentation-only changes"""
        return Rule(
            rule_id="STD-003",
            name="Auto-Approve Docs Only",
            description="Documentation-only changes",
            priority=RulePriority.LOW,
            conditions=[
                Condition(
                    field="only_docs_changed",
                    operator=ConditionOperator.EQUALS,
                    value=True
                ),
                Condition(
                    field="file_count",
                    operator=ConditionOperator.LESS_THAN,
                    value=5
                )
            ],
            actions=[RuleActionDefinition(action=RuleAction.APPROVE, message="Docs-only change")],
            applies_to=["docs/**", "*.md"]
        )

    @staticmethod
    def large_pr_warning() -> Rule:
        """Warn on large PRs"""
        return Rule(
            rule_id="STD-004",
            name="Large PR Warning",
            description="PR is larger than recommended",
            priority=RulePriority.MEDIUM,
            conditions=[
                Condition(
                    field="changed_lines",
                    operator=ConditionOperator.GREATER_THAN,
                    value=500
                )
            ],
            actions=[RuleActionDefinition(action=RuleAction.COMMENT, message="Consider breaking into smaller PRs")],
        )
