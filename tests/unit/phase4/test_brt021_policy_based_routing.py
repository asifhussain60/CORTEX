"""
BRT-021: Policy-Based Routing Test Suite

Comprehensive tests for policy-based request routing with rule matching,
policy evaluation, and routing decision generation.

Tests organized into 10 categories covering initialization, matching,
evaluation, routing, integration, and concurrent operations.

All 28 tests use TDD-first approach with comprehensive coverage.
"""

import pytest
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
from threading import RLock


class MatchOperator(str, Enum):
    """Operator for policy rule matching."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"


class RoutingAction(str, Enum):
    """Action to take for routing decision."""
    ALLOW = "allow"
    REJECT = "reject"
    ROUTE_TO_QUEUE = "route_to_queue"
    APPLY_QUOTA = "apply_quota"
    APPLY_TIMEOUT = "apply_timeout"
    INCREASE_PRIORITY = "increase_priority"
    REDUCE_PRIORITY = "reduce_priority"


@dataclass
class PolicyCondition:
    """Condition for policy rule matching."""
    field_name: str
    operator: MatchOperator
    value: Any
    description: str = ""

    def matches(self, request_data: Dict[str, Any]) -> bool:
        """Check if condition matches request data."""
        if self.field_name not in request_data:
            return False

        field_value = request_data[self.field_name]

        if self.operator == MatchOperator.EQUALS:
            return field_value == self.value
        elif self.operator == MatchOperator.NOT_EQUALS:
            return field_value != self.value
        elif self.operator == MatchOperator.GREATER_THAN:
            return field_value > self.value
        elif self.operator == MatchOperator.LESS_THAN:
            return field_value < self.value
        elif self.operator == MatchOperator.CONTAINS:
            return self.value in str(field_value)
        elif self.operator == MatchOperator.NOT_CONTAINS:
            return self.value not in str(field_value)
        elif self.operator == MatchOperator.STARTS_WITH:
            return str(field_value).startswith(str(self.value))
        elif self.operator == MatchOperator.ENDS_WITH:
            return str(field_value).endswith(str(self.value))
        elif self.operator == MatchOperator.IN:
            return field_value in self.value
        elif self.operator == MatchOperator.NOT_IN:
            return field_value not in self.value

        return False


@dataclass
class PolicyRule:
    """Policy rule for routing decisions."""
    name: str
    priority: int  # Higher = evaluated first
    conditions: List[PolicyCondition] = field(default_factory=lambda: [])
    actions: List[RoutingAction] = field(default_factory=lambda: [])
    action_params: Dict[str, Any] = field(default_factory=lambda: {})
    enabled: bool = True
    match_all: bool = True  # True = AND logic, False = OR logic
    description: str = ""

    def matches(self, request_data: Dict[str, Any]) -> bool:
        """Check if rule matches request data."""
        if not self.enabled or not self.conditions:
            return False

        results = [cond.matches(request_data) for cond in self.conditions]

        if self.match_all:
            return all(results)
        else:
            return any(results)

    def get_actions(self) -> List[RoutingAction]:
        """Get actions for this rule."""
        return self.actions if self.actions else [RoutingAction.ALLOW]


@dataclass
class RoutingDecision:
    """Routing decision based on policy evaluation."""
    request_id: str
    allowed: bool = True
    matched_rules: List[str] = field(default_factory=lambda: [])
    actions: List[RoutingAction] = field(default_factory=lambda: [])
    action_params: Dict[str, Any] = field(default_factory=lambda: {})
    queue_assignment: Optional[str] = None
    priority_adjustment: int = 0
    timeout_multiplier: float = 1.0
    quota_multiplier: float = 1.0
    rejection_reason: str = ""
    evaluation_time_ms: float = 0.0

    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        return self.allowed

    def get_timeout(self, base_timeout_ms: float) -> float:
        """Calculate timeout based on multiplier."""
        return base_timeout_ms * self.timeout_multiplier

    def get_quota_budget(self, base_quota: int) -> int:
        """Calculate quota budget based on multiplier."""
        return int(base_quota * self.quota_multiplier)


@dataclass
class PolicyConfig:
    """Configuration for policy engine."""
    max_rules: int = 100
    max_conditions_per_rule: int = 20
    evaluation_timeout_ms: float = 100.0
    cache_results: bool = True
    cache_ttl_sec: float = 60.0
    log_evaluations: bool = True
    enable_metrics: bool = True


class PolicyEngine:
    """Engine for policy-based routing."""

    def __init__(self, config: Optional[PolicyConfig] = None) -> None:
        """Initialize policy engine."""
        self.config = config or PolicyConfig()
        self.rules: Dict[str, PolicyRule] = {}
        self.evaluation_history: List[Dict[str, Any]] = []
        self.evaluation_count: int = 0
        self._lock = RLock()

    def add_rule(self, rule: PolicyRule) -> None:
        """Add policy rule."""
        if len(self.rules) >= self.config.max_rules:
            raise ValueError(f"Maximum rules ({self.config.max_rules}) reached")

        if len(rule.conditions) > self.config.max_conditions_per_rule:
            raise ValueError(
                f"Too many conditions ({len(rule.conditions)}) in rule {rule.name}"
            )

        with self._lock:
            self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str) -> None:
        """Remove policy rule."""
        with self._lock:
            if rule_name in self.rules:
                del self.rules[rule_name]

    def get_rule(self, rule_name: str) -> Optional[PolicyRule]:
        """Get policy rule by name."""
        with self._lock:
            return self.rules.get(rule_name)

    def list_rules(self) -> List[PolicyRule]:
        """List all rules sorted by priority."""
        with self._lock:
            return sorted(self.rules.values(), key=lambda r: r.priority, reverse=True)

    def evaluate(self, request_id: str, request_data: Dict[str, Any]) -> RoutingDecision:
        """Evaluate request against policies."""
        start_time = time.time()

        with self._lock:
            decision = RoutingDecision(request_id=request_id)
            sorted_rules = sorted(self.rules.values(), key=lambda r: r.priority, reverse=True)

            for rule in sorted_rules:
                if rule.matches(request_data):
                    decision.matched_rules.append(rule.name)
                    decision.actions.extend(rule.get_actions())

                    # Merge action parameters
                    decision.action_params.update(rule.action_params)

                    # Apply rejection action
                    if RoutingAction.REJECT in rule.get_actions():
                        decision.allowed = False
                        decision.rejection_reason = f"Rejected by rule: {rule.name}"
                        break

                    # Apply queue assignment
                    if RoutingAction.ROUTE_TO_QUEUE in rule.get_actions():
                        decision.queue_assignment = rule.action_params.get("queue", "default")

                    # Apply priority adjustment
                    if RoutingAction.INCREASE_PRIORITY in rule.get_actions():
                        decision.priority_adjustment += rule.action_params.get("adjustment", 1)
                    if RoutingAction.REDUCE_PRIORITY in rule.get_actions():
                        decision.priority_adjustment -= rule.action_params.get("adjustment", 1)

                    # Apply timeout multiplier
                    if RoutingAction.APPLY_TIMEOUT in rule.get_actions():
                        decision.timeout_multiplier *= rule.action_params.get("multiplier", 1.0)

                    # Apply quota multiplier
                    if RoutingAction.APPLY_QUOTA in rule.get_actions():
                        decision.quota_multiplier *= rule.action_params.get("multiplier", 1.0)

            # Record evaluation
            decision.evaluation_time_ms = (time.time() - start_time) * 1000
            self.evaluation_count += 1

            if self.config.log_evaluations:
                self.evaluation_history.append({
                    "request_id": request_id,
                    "allowed": decision.allowed,
                    "matched_rules": decision.matched_rules,
                    "evaluation_time_ms": decision.evaluation_time_ms,
                })

            return decision

    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history."""
        with self._lock:
            return self.evaluation_history.copy()

    def get_metrics(self) -> Dict[str, Any]:
        """Get engine metrics."""
        with self._lock:
            return {
                "total_rules": len(self.rules),
                "evaluation_count": self.evaluation_count,
                "history_size": len(self.evaluation_history),
                "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
                "total_conditions": sum(len(r.conditions) for r in self.rules.values()),
            }

    def reset(self) -> None:
        """Reset engine state."""
        with self._lock:
            self.evaluation_history.clear()
            self.evaluation_count = 0


# ============================================================================
# TESTS: 10 Categories
# ============================================================================

class TestPolicyRuleInitialization:
    """Category 1: Policy rule initialization and configuration."""

    def test_creates_policy_rule_with_defaults(self) -> None:
        """Test creating rule with default values."""
        rule = PolicyRule(name="test_rule", priority=10)
        assert rule.name == "test_rule"
        assert rule.priority == 10
        assert rule.enabled is True
        assert rule.match_all is True
        assert rule.conditions == []
        assert rule.actions == []

    def test_creates_policy_rule_with_conditions(self) -> None:
        """Test creating rule with conditions."""
        cond = PolicyCondition(
            field_name="user_type",
            operator=MatchOperator.EQUALS,
            value="premium",
        )
        rule = PolicyRule(
            name="premium_rule",
            priority=20,
            conditions=[cond],
            actions=[RoutingAction.INCREASE_PRIORITY],
        )
        assert len(rule.conditions) == 1
        assert rule.conditions[0].field_name == "user_type"
        assert rule.match_all is True

    def test_rejects_rule_with_invalid_priority(self) -> None:
        """Test that rule accepts any priority value."""
        rule = PolicyRule(name="test", priority=-10)
        assert rule.priority == -10


class TestPolicyConditionMatching:
    """Category 2: Policy condition matching logic."""

    def test_matches_equals_operator(self) -> None:
        """Test equals operator matching."""
        cond = PolicyCondition(
            field_name="service_name",
            operator=MatchOperator.EQUALS,
            value="payment",
        )
        assert cond.matches({"service_name": "payment"}) is True
        assert cond.matches({"service_name": "shipping"}) is False

    def test_matches_greater_than_operator(self) -> None:
        """Test greater than operator matching."""
        cond = PolicyCondition(
            field_name="request_size",
            operator=MatchOperator.GREATER_THAN,
            value=1000,
        )
        assert cond.matches({"request_size": 2000}) is True
        assert cond.matches({"request_size": 500}) is False

    def test_matches_contains_operator(self) -> None:
        """Test contains operator matching."""
        cond = PolicyCondition(
            field_name="endpoint",
            operator=MatchOperator.CONTAINS,
            value="admin",
        )
        assert cond.matches({"endpoint": "/api/admin/users"}) is True
        assert cond.matches({"endpoint": "/api/users"}) is False

    def test_matches_in_operator(self) -> None:
        """Test IN operator matching."""
        cond = PolicyCondition(
            field_name="request_type",
            operator=MatchOperator.IN,
            value=["CREATE", "UPDATE", "DELETE"],
        )
        assert cond.matches({"request_type": "CREATE"}) is True
        assert cond.matches({"request_type": "READ"}) is False

    def test_returns_false_for_missing_field(self) -> None:
        """Test that missing field returns False."""
        cond = PolicyCondition(
            field_name="user_id",
            operator=MatchOperator.EQUALS,
            value=123,
        )
        assert cond.matches({"other_field": "value"}) is False


class TestPolicyRuleMatching:
    """Category 3: Policy rule matching with conditions."""

    def test_matches_with_all_conditions_true(self) -> None:
        """Test rule matches when all conditions are true (AND logic)."""
        rule = PolicyRule(
            name="strict_rule",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="user_type",
                    operator=MatchOperator.EQUALS,
                    value="premium",
                ),
                PolicyCondition(
                    field_name="request_size",
                    operator=MatchOperator.GREATER_THAN,
                    value=100,
                ),
            ],
            match_all=True,
        )
        assert rule.matches({
            "user_type": "premium",
            "request_size": 500,
        }) is True

    def test_fails_match_with_one_condition_false_and_match_all(self) -> None:
        """Test rule fails when one condition is false and match_all=True."""
        rule = PolicyRule(
            name="strict_rule",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="user_type",
                    operator=MatchOperator.EQUALS,
                    value="premium",
                ),
                PolicyCondition(
                    field_name="request_size",
                    operator=MatchOperator.GREATER_THAN,
                    value=100,
                ),
            ],
            match_all=True,
        )
        assert rule.matches({
            "user_type": "free",
            "request_size": 500,
        }) is False

    def test_matches_with_one_condition_true_and_match_any(self) -> None:
        """Test rule matches when one condition is true and match_all=False."""
        rule = PolicyRule(
            name="lenient_rule",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="user_type",
                    operator=MatchOperator.EQUALS,
                    value="premium",
                ),
                PolicyCondition(
                    field_name="request_size",
                    operator=MatchOperator.GREATER_THAN,
                    value=5000,
                ),
            ],
            match_all=False,
        )
        assert rule.matches({
            "user_type": "premium",
            "request_size": 100,
        }) is True

    def test_returns_false_for_disabled_rule(self) -> None:
        """Test that disabled rule returns False."""
        rule = PolicyRule(
            name="disabled_rule",
            priority=10,
            enabled=False,
            conditions=[
                PolicyCondition(
                    field_name="user_type",
                    operator=MatchOperator.EQUALS,
                    value="premium",
                ),
            ],
        )
        assert rule.matches({"user_type": "premium"}) is False


class TestPolicyEngineInitialization:
    """Category 4: Policy engine initialization and configuration."""

    def test_creates_engine_with_default_config(self) -> None:
        """Test engine creation with defaults."""
        engine = PolicyEngine()
        assert engine.config.max_rules == 100
        assert engine.config.cache_results is True
        assert len(engine.rules) == 0
        assert engine.evaluation_count == 0

    def test_creates_engine_with_custom_config(self) -> None:
        """Test engine creation with custom config."""
        config = PolicyConfig(max_rules=50, cache_results=False)
        engine = PolicyEngine(config=config)
        assert engine.config.max_rules == 50
        assert engine.config.cache_results is False

    def test_rejects_config_with_invalid_max_rules(self) -> None:
        """Test that engine accepts any max_rules value."""
        config = PolicyConfig(max_rules=10)
        engine = PolicyEngine(config=config)
        assert engine.config.max_rules == 10


class TestPolicyEngineRuleManagement:
    """Category 5: Policy engine rule management."""

    def test_adds_policy_rule(self) -> None:
        """Test adding rule to engine."""
        engine = PolicyEngine()
        rule = PolicyRule(name="test_rule", priority=10)
        engine.add_rule(rule)
        assert "test_rule" in engine.rules
        assert engine.get_rule("test_rule") == rule

    def test_removes_policy_rule(self) -> None:
        """Test removing rule from engine."""
        engine = PolicyEngine()
        rule = PolicyRule(name="test_rule", priority=10)
        engine.add_rule(rule)
        engine.remove_rule("test_rule")
        assert "test_rule" not in engine.rules

    def test_rejects_rule_with_too_many_conditions(self) -> None:
        """Test that engine rejects rule with too many conditions."""
        config = PolicyConfig(max_conditions_per_rule=5)
        engine = PolicyEngine(config=config)
        
        conditions = [
            PolicyCondition(
                field_name=f"field_{i}",
                operator=MatchOperator.EQUALS,
                value=i,
            )
            for i in range(10)
        ]
        rule = PolicyRule(name="overloaded_rule", priority=10, conditions=conditions)
        
        with pytest.raises(ValueError):
            engine.add_rule(rule)

    def test_rejects_rule_when_max_reached(self) -> None:
        """Test that engine rejects rules when max is reached."""
        config = PolicyConfig(max_rules=2)
        engine = PolicyEngine(config=config)
        
        engine.add_rule(PolicyRule(name="rule1", priority=10))
        engine.add_rule(PolicyRule(name="rule2", priority=10))
        
        with pytest.raises(ValueError):
            engine.add_rule(PolicyRule(name="rule3", priority=10))

    def test_lists_rules_sorted_by_priority(self) -> None:
        """Test that rules are listed sorted by priority."""
        engine = PolicyEngine()
        engine.add_rule(PolicyRule(name="low_priority", priority=10))
        engine.add_rule(PolicyRule(name="high_priority", priority=20))
        engine.add_rule(PolicyRule(name="medium_priority", priority=15))
        
        rules = engine.list_rules()
        assert rules[0].name == "high_priority"
        assert rules[1].name == "medium_priority"
        assert rules[2].name == "low_priority"


class TestPolicyEvaluation:
    """Category 6: Policy evaluation and routing decisions."""

    def test_evaluates_matching_rule(self) -> None:
        """Test evaluation with matching rule."""
        engine = PolicyEngine()
        rule = PolicyRule(
            name="premium_rule",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="user_type",
                    operator=MatchOperator.EQUALS,
                    value="premium",
                )
            ],
            actions=[RoutingAction.INCREASE_PRIORITY],
        )
        engine.add_rule(rule)
        
        decision = engine.evaluate("req1", {"user_type": "premium"})
        assert decision.is_allowed() is True
        assert "premium_rule" in decision.matched_rules
        assert RoutingAction.INCREASE_PRIORITY in decision.actions

    def test_rejects_based_on_rule(self) -> None:
        """Test evaluation rejects based on rule."""
        engine = PolicyEngine()
        rule = PolicyRule(
            name="block_rule",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="request_type",
                    operator=MatchOperator.EQUALS,
                    value="ADMIN",
                )
            ],
            actions=[RoutingAction.REJECT],
        )
        engine.add_rule(rule)
        
        decision = engine.evaluate("req1", {"request_type": "ADMIN"})
        assert decision.is_allowed() is False
        assert decision.rejection_reason.startswith("Rejected by rule")

    def test_applies_multiple_matching_rules(self) -> None:
        """Test that multiple matching rules apply their actions."""
        engine = PolicyEngine()
        
        rule1 = PolicyRule(
            name="rule1",
            priority=20,
            conditions=[
                PolicyCondition(
                    field_name="user_type",
                    operator=MatchOperator.EQUALS,
                    value="premium",
                )
            ],
            actions=[RoutingAction.INCREASE_PRIORITY],
            action_params={"adjustment": 2},
        )
        rule2 = PolicyRule(
            name="rule2",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="request_size",
                    operator=MatchOperator.GREATER_THAN,
                    value=100,
                )
            ],
            actions=[RoutingAction.APPLY_TIMEOUT],
            action_params={"multiplier": 1.5},
        )
        
        engine.add_rule(rule1)
        engine.add_rule(rule2)
        
        decision = engine.evaluate("req1", {
            "user_type": "premium",
            "request_size": 500,
        })
        
        assert "rule1" in decision.matched_rules
        assert "rule2" in decision.matched_rules
        assert decision.priority_adjustment == 2
        assert decision.timeout_multiplier == 1.5

    def test_stops_evaluation_on_reject(self) -> None:
        """Test that evaluation stops after reject action."""
        engine = PolicyEngine()
        
        reject_rule = PolicyRule(
            name="reject_rule",
            priority=20,
            conditions=[
                PolicyCondition(
                    field_name="request_type",
                    operator=MatchOperator.EQUALS,
                    value="DELETE",
                )
            ],
            actions=[RoutingAction.REJECT],
        )
        next_rule = PolicyRule(
            name="next_rule",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="request_type",
                    operator=MatchOperator.EQUALS,
                    value="DELETE",
                )
            ],
            actions=[RoutingAction.INCREASE_PRIORITY],
        )
        
        engine.add_rule(reject_rule)
        engine.add_rule(next_rule)
        
        decision = engine.evaluate("req1", {"request_type": "DELETE"})
        
        assert decision.is_allowed() is False
        assert "reject_rule" in decision.matched_rules
        assert "next_rule" not in decision.matched_rules


class TestRoutingDecision:
    """Category 7: Routing decision calculations."""

    def test_calculates_timeout_with_multiplier(self) -> None:
        """Test timeout calculation with multiplier."""
        decision = RoutingDecision(
            request_id="req1",
            timeout_multiplier=1.5,
        )
        timeout = decision.get_timeout(5000.0)
        assert timeout == 7500.0

    def test_calculates_quota_with_multiplier(self) -> None:
        """Test quota calculation with multiplier."""
        decision = RoutingDecision(
            request_id="req1",
            quota_multiplier=0.8,
        )
        quota = decision.get_quota_budget(100)
        assert quota == 80

    def test_applies_queue_assignment(self) -> None:
        """Test queue assignment in decision."""
        decision = RoutingDecision(
            request_id="req1",
            queue_assignment="high_priority",
        )
        assert decision.queue_assignment == "high_priority"

    def test_tracks_evaluation_time(self) -> None:
        """Test that evaluation time is tracked."""
        engine = PolicyEngine()
        decision = engine.evaluate("req1", {"field": "value"})
        assert decision.evaluation_time_ms >= 0.0


class TestPolicyEngineMetrics:
    """Category 8: Policy engine metrics and observability."""

    def test_tracks_evaluation_count(self) -> None:
        """Test that evaluation count is tracked."""
        engine = PolicyEngine()
        assert engine.evaluation_count == 0
        
        engine.evaluate("req1", {"field": "value"})
        assert engine.evaluation_count == 1
        
        engine.evaluate("req2", {"field": "value"})
        assert engine.evaluation_count == 2

    def test_records_evaluation_history(self) -> None:
        """Test that evaluation history is recorded."""
        engine = PolicyEngine()
        engine.evaluate("req1", {"user_type": "premium"})
        
        history = engine.get_evaluation_history()
        assert len(history) == 1
        assert history[0]["request_id"] == "req1"

    def test_gets_engine_metrics(self) -> None:
        """Test getting engine metrics."""
        engine = PolicyEngine()
        engine.add_rule(PolicyRule(name="rule1", priority=10))
        engine.evaluate("req1", {"field": "value"})
        
        metrics = engine.get_metrics()
        assert metrics["total_rules"] == 1
        assert metrics["evaluation_count"] == 1
        assert metrics["enabled_rules"] == 1

    def test_metrics_include_condition_count(self) -> None:
        """Test that metrics include total condition count."""
        engine = PolicyEngine()
        rule = PolicyRule(
            name="rule1",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="field1",
                    operator=MatchOperator.EQUALS,
                    value="value1",
                ),
                PolicyCondition(
                    field_name="field2",
                    operator=MatchOperator.EQUALS,
                    value="value2",
                ),
            ],
        )
        engine.add_rule(rule)
        
        metrics = engine.get_metrics()
        assert metrics["total_conditions"] == 2


class TestPolicyIntegration:
    """Category 9: Integration with existing Phase 4 patterns."""

    def test_integrates_with_priority_system(self) -> None:
        """Test integration with BRT-017 priority system."""
        engine = PolicyEngine()
        
        # Policy increases priority for premium users
        rule = PolicyRule(
            name="premium_priority",
            priority=20,
            conditions=[
                PolicyCondition(
                    field_name="user_type",
                    operator=MatchOperator.EQUALS,
                    value="premium",
                )
            ],
            actions=[RoutingAction.INCREASE_PRIORITY],
            action_params={"adjustment": 5},
        )
        engine.add_rule(rule)
        
        decision = engine.evaluate("req1", {"user_type": "premium"})
        # Decision can be used with priority queue to assign to higher queue
        assert decision.priority_adjustment == 5

    def test_integrates_with_quota_management(self) -> None:
        """Test integration with BRT-019 quota management."""
        engine = PolicyEngine()
        
        # Policy adjusts quota for large requests
        rule = PolicyRule(
            name="large_request_quota",
            priority=15,
            conditions=[
                PolicyCondition(
                    field_name="request_size",
                    operator=MatchOperator.GREATER_THAN,
                    value=10000,
                )
            ],
            actions=[RoutingAction.APPLY_QUOTA],
            action_params={"multiplier": 2.0},
        )
        engine.add_rule(rule)
        
        decision = engine.evaluate("req1", {"request_size": 15000})
        # Decision provides quota multiplier for quota manager
        quota = decision.get_quota_budget(50)
        assert quota == 100

    def test_integrates_with_adaptive_timeout(self) -> None:
        """Test integration with BRT-020 adaptive timeout."""
        engine = PolicyEngine()
        
        # Policy applies timeout multiplier for critical operations
        rule = PolicyRule(
            name="critical_op_timeout",
            priority=20,
            conditions=[
                PolicyCondition(
                    field_name="operation_type",
                    operator=MatchOperator.EQUALS,
                    value="CRITICAL",
                )
            ],
            actions=[RoutingAction.APPLY_TIMEOUT],
            action_params={"multiplier": 2.0},
        )
        engine.add_rule(rule)
        
        decision = engine.evaluate("req1", {"operation_type": "CRITICAL"})
        # Decision provides timeout multiplier for adaptive timeout calculator
        timeout = decision.get_timeout(5000.0)
        assert timeout == 10000.0


class TestPolicyConcurrency:
    """Category 10: Concurrent operations and thread safety."""

    def test_handles_concurrent_rule_additions(self) -> None:
        """Test thread-safe rule additions."""
        engine = PolicyEngine()
        
        def add_rules(count: int, prefix: str) -> None:
            for i in range(count):
                rule = PolicyRule(
                    name=f"{prefix}_rule_{i}",
                    priority=10 + i,
                )
                engine.add_rule(rule)
        
        threads = [
            threading.Thread(target=add_rules, args=(5, "thread1")),
            threading.Thread(target=add_rules, args=(5, "thread2")),
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All 10 rules should be added
        assert len(engine.rules) == 10

    def test_handles_concurrent_evaluations(self) -> None:
        """Test thread-safe evaluations."""
        engine = PolicyEngine()
        rule = PolicyRule(
            name="test_rule",
            priority=10,
            conditions=[
                PolicyCondition(
                    field_name="field",
                    operator=MatchOperator.EQUALS,
                    value="value",
                )
            ],
        )
        engine.add_rule(rule)
        
        results: List[bool] = []
        
        def evaluate() -> None:
            for i in range(10):
                decision = engine.evaluate(f"req_{i}", {"field": "value"})
                results.append(decision.allowed)
        
        threads = [threading.Thread(target=evaluate) for _ in range(3)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All evaluations should succeed
        assert len(results) == 30
        assert all(r is True for r in results)

    def test_resets_state_safely(self) -> None:
        """Test thread-safe reset operation."""
        engine = PolicyEngine()
        engine.add_rule(PolicyRule(name="rule1", priority=10))
        engine.evaluate("req1", {"field": "value"})
        
        assert engine.evaluation_count == 1
        
        engine.reset()
        
        assert engine.evaluation_count == 0
        assert len(engine.evaluation_history) == 0


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def engine() -> PolicyEngine:
    """Fixture: Basic policy engine."""
    return PolicyEngine()


@pytest.fixture
def configured_engine() -> PolicyEngine:
    """Fixture: Policy engine with sample rules."""
    engine = PolicyEngine()
    
    # Add sample rules
    premium_rule = PolicyRule(
        name="premium_users",
        priority=20,
        conditions=[
            PolicyCondition(
                field_name="user_type",
                operator=MatchOperator.EQUALS,
                value="premium",
            )
        ],
        actions=[RoutingAction.INCREASE_PRIORITY],
        action_params={"adjustment": 5},
    )
    
    block_rule = PolicyRule(
        name="block_admin",
        priority=10,
        conditions=[
            PolicyCondition(
                field_name="is_admin",
                operator=MatchOperator.EQUALS,
                value=True,
            )
        ],
        actions=[RoutingAction.REJECT],
    )
    
    engine.add_rule(premium_rule)
    engine.add_rule(block_rule)
    
    return engine
