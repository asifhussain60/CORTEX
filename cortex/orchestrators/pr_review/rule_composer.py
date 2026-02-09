"""
Phase 52 S2.2: Rule Evaluation & Composition System

Advanced rule composition with:
- Rule groups and inheritance
- Conflict resolution
- Custom evaluators
- Performance optimization
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Set, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)

from rule_engine import Rule, RuleEngine, RulesetEvaluationResult, RuleAction, Condition, RulePriority


class ConflictResolutionStrategy(Enum):
    """How to resolve conflicting rule recommendations"""
    FIRST_MATCH = "first_match"      # Use highest priority
    MOST_RESTRICTIVE = "most_restrictive"  # Block wins over all
    VOTE = "vote"                     # Majority wins
    CUSTOM = "custom"                 # Use custom resolver


@dataclass
class RuleGroup:
    """Group related rules together"""
    group_id: str
    name: str
    description: str
    rules: List[str] = field(default_factory=list)  # Rule IDs
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class RuleConflict:
    """Conflict between rule evaluations"""
    rule_ids: List[str]
    conflicting_actions: List[RuleAction]
    context: Dict[str, Any]
    resolution: Optional[RuleAction] = None


class RuleComposer:
    """Advanced rule composition and evaluation"""

    def __init__(self, engine: RuleEngine):
        self.engine = engine
        self.groups: Dict[str, RuleGroup] = {}
        self.conflict_history: List[RuleConflict] = []
        self.conflict_resolver: Optional[Callable] = None
        self.evaluation_hooks: List[Callable] = []

    def add_group(self, group: RuleGroup) -> None:
        """Add a rule group"""
        self.groups[group.group_id] = group
        logger.info(f"Added group: {group.group_id}")

    def enable_group(self, group_id: str) -> bool:
        """Enable all rules in group"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        group.enabled = True
        
        for rule_id in group.rules:
            self.engine.enable_rule(rule_id)
        
        return True

    def disable_group(self, group_id: str) -> bool:
        """Disable all rules in group"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        group.enabled = False
        
        for rule_id in group.rules:
            self.engine.disable_rule(rule_id)
        
        return True

    def set_conflict_resolver(self, resolver: Callable[[List[RuleConflict]], RuleAction]) -> None:
        """Set custom conflict resolution function"""
        self.conflict_resolver = resolver

    def add_evaluation_hook(self, hook: Callable[[RulesetEvaluationResult, Dict[str, Any]], None]) -> None:
        """Add post-evaluation hook"""
        self.evaluation_hooks.append(hook)

    def evaluate_with_composition(self, pr_context: Dict[str, Any], 
                                  file_path: Optional[str] = None,
                                  strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MOST_RESTRICTIVE) -> RulesetEvaluationResult:
        """Evaluate with conflict resolution"""
        result = self.engine.evaluate_pr(pr_context, file_path)
        
        # Check for conflicts
        conflicts = self._detect_conflicts(result)
        
        if conflicts:
            logger.warning(f"Detected {len(conflicts)} rule conflicts")
            resolved_action = self._resolve_conflicts(conflicts, strategy)
            result.recommended_action = resolved_action
        
        # Run evaluation hooks
        for hook in self.evaluation_hooks:
            try:
                hook(result, pr_context)
            except Exception as e:
                logger.error(f"Hook execution failed: {e}")
        
        return result

    def _detect_conflicts(self, result: RulesetEvaluationResult) -> List[RuleConflict]:
        """Detect conflicting rule recommendations"""
        conflicts = []
        
        if not result.matching_rules:
            return conflicts
        
        # Group by action type
        action_groups: Dict[RuleAction, List[str]] = {}
        for rule_eval in result.matching_rules:
            for action in rule_eval.actions:
                if action.action not in action_groups:
                    action_groups[action.action] = []
                action_groups[action.action].append(rule_eval.rule_id)
        
        # Check for conflicts (e.g., APPROVE and BLOCK)
        if RuleAction.APPROVE in action_groups and RuleAction.BLOCK in action_groups:
            conflict = RuleConflict(
                rule_ids=action_groups[RuleAction.APPROVE] + action_groups[RuleAction.BLOCK],
                conflicting_actions=[RuleAction.APPROVE, RuleAction.BLOCK],
                context={}
            )
            conflicts.append(conflict)
        
        return conflicts

    def _resolve_conflicts(self, conflicts: List[RuleConflict], 
                          strategy: ConflictResolutionStrategy) -> RuleAction:
        """Resolve conflicts using strategy"""
        if strategy == ConflictResolutionStrategy.MOST_RESTRICTIVE:
            # BLOCK > REQUEST_CHANGES > COMMENT > APPROVE
            priorities = {
                RuleAction.BLOCK: 4,
                RuleAction.REQUEST_CHANGES: 3,
                RuleAction.COMMENT: 2,
                RuleAction.APPROVE: 1,
                RuleAction.WARN: 2,
                RuleAction.SKIP: 0
            }
            
            all_actions = []
            for conflict in conflicts:
                all_actions.extend(conflict.conflicting_actions)
            
            return max(all_actions, key=lambda a: priorities.get(a, 0))
        
        elif strategy == ConflictResolutionStrategy.CUSTOM and self.conflict_resolver:
            return self.conflict_resolver(conflicts)
        
        else:  # Default to first match
            return conflicts[0].conflicting_actions[0] if conflicts else RuleAction.SKIP

    def get_group_stats(self) -> Dict[str, Any]:
        """Get group statistics"""
        return {
            "total_groups": len(self.groups),
            "enabled_groups": len([g for g in self.groups.values() if g.enabled]),
            "total_grouped_rules": sum(len(g.rules) for g in self.groups.values()),
            "conflicts_detected": len(self.conflict_history)
        }


class RuleValidator:
    """Validate rule definitions and configurations"""

    @staticmethod
    def validate_rule(rule: Rule) -> tuple[bool, List[str]]:
        """Validate rule definition"""
        errors = []
        
        if not rule.rule_id or not rule.rule_id.strip():
            errors.append("rule_id is required")
        
        if not rule.name or not rule.name.strip():
            errors.append("name is required")
        
        if not rule.conditions and not rule.actions:
            errors.append("Rule must have at least one condition or action")
        
        if rule.condition_logic not in ["AND", "OR"]:
            errors.append(f"Invalid condition_logic: {rule.condition_logic}")
        
        if rule.max_violations < 1:
            errors.append("max_violations must be >= 1")
        
        # Validate conditions
        for i, cond in enumerate(rule.conditions):
            if not cond.field or not cond.field.strip():
                errors.append(f"Condition {i}: field is required")
        
        # Validate actions
        if not rule.actions:
            errors.append("Rule must have at least one action")
        
        return len(errors) == 0, errors

    @staticmethod
    def validate_ruleset(engine: RuleEngine) -> tuple[bool, List[str]]:
        """Validate entire ruleset"""
        errors = []
        
        if not engine.rules:
            errors.append("Ruleset is empty")
            return False, errors
        
        rule_ids = set()
        for rule_id, rule in engine.rules.items():
            # Check for duplicates
            if rule_id in rule_ids:
                errors.append(f"Duplicate rule ID: {rule_id}")
            rule_ids.add(rule_id)
            
            # Validate individual rule
            valid, rule_errors = RuleValidator.validate_rule(rule)
            if not valid:
                errors.extend([f"Rule {rule_id}: {e}" for e in rule_errors])
        
        return len(errors) == 0, errors


@dataclass
class RuleExecutionPlan:
    """Execution plan for rule evaluation"""
    rules_to_evaluate: List[Rule]
    estimated_time_ms: float
    priority_order: List[str]
    parallelizable_groups: List[List[str]]


class RuleOptimizer:
    """Optimize rule execution for performance"""

    @staticmethod
    def analyze_dependencies(engine: RuleEngine) -> Dict[str, Set[str]]:
        """Analyze rule dependencies"""
        dependencies = {}
        
        for rule_id, rule in engine.rules.items():
            deps = set()
            
            for condition in rule.conditions:
                # Extract field dependencies
                deps.add(condition.field)
            
            dependencies[rule_id] = deps
        
        return dependencies

    @staticmethod
    def create_execution_plan(engine: RuleEngine) -> RuleExecutionPlan:
        """Create optimized execution plan"""
        # Sort by priority
        sorted_rules = sorted(
            engine.rules.values(),
            key=lambda r: r.priority.value,
            reverse=True
        )
        
        # Group parallelizable rules (independent conditions)
        parallelizable = RuleOptimizer._find_parallelizable_groups(sorted_rules)
        
        # Estimate execution time (rough)
        estimated_time = len(sorted_rules) * 0.5  # 0.5ms per rule
        
        return RuleExecutionPlan(
            rules_to_evaluate=sorted_rules,
            estimated_time_ms=estimated_time,
            priority_order=[r.rule_id for r in sorted_rules],
            parallelizable_groups=parallelizable
        )

    @staticmethod
    def _find_parallelizable_groups(rules: List[Rule]) -> List[List[str]]:
        """Find rules that can be evaluated in parallel"""
        groups = []
        current_group = []
        
        for rule in rules:
            # Simplified: group rules with same priority
            if current_group and rule.priority != rules[len(groups) - 1 if groups else 0].priority:
                groups.append([r.rule_id for r in current_group])
                current_group = []
            
            current_group.append(rule)
        
        if current_group:
            groups.append([r.rule_id for r in current_group])
        
        return groups
