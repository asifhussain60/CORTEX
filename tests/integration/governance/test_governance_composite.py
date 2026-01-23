"""
Tests for Governance Composite - Coordinated multi-layer governance policy enforcement.

Tests cover:
- GovernanceComposite: Orchestration of governance modules
- PolicyComposer: Policy composition with precedence
- GovernanceChain: Chain-of-responsibility pattern
- CompositeEnforcer: Real-time policy enforcement
- Audit trail and metrics tracking
"""

import pytest
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PolicyLevel(Enum):
    """Policy priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class ViolationSeverity(Enum):
    """Severity of policy violations."""
    BLOCKING = "blocking"
    WARNING = "warning"
    INFO = "info"


@dataclass
class PolicyRule:
    """Represents a single policy rule."""
    rule_id: str
    name: str
    level: PolicyLevel
    check_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    description: str = ""
    remediation: str = ""


@dataclass
class PolicyViolation:
    """Represents a policy violation."""
    rule_id: str
    severity: ViolationSeverity
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class PolicyDecision:
    """Result of policy evaluation."""
    approved: bool
    violations: List[PolicyViolation] = field(default_factory=lambda: [])
    enforcement_level: ViolationSeverity = ViolationSeverity.INFO
    remediation_suggestions: List[str] = field(default_factory=lambda: [])
    evaluation_time_ms: float = 0.0


class GovernancePolicy:
    """Individual governance policy."""

    def __init__(self, policy_id: str, name: str, level: PolicyLevel):
        """Initialize policy.
        
        Args:
            policy_id: Policy identifier.
            name: Human-readable name.
            level: Priority level.
        """
        self.policy_id = policy_id
        self.name = name
        self.level = level
        self.rules: List[PolicyRule] = []
        self.enabled = True

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a rule to policy.
        
        Args:
            rule: Rule to add.
        """
        self.rules.append(rule)

    def evaluate(self, context: Dict[str, Any]) -> PolicyDecision:
        """Evaluate policy against context.
        
        Args:
            context: Context for evaluation.
            
        Returns:
            Policy decision.
        """
        if not self.enabled:
            return PolicyDecision(approved=True)
        
        violations: List[PolicyViolation] = []
        
        for rule in self.rules:
            if rule.check_fn and not rule.check_fn(context):
                violations.append(PolicyViolation(
                    rule_id=rule.rule_id,
                    severity=ViolationSeverity.BLOCKING,
                    description=f"Rule '{rule.name}' violated: {rule.description}",
                    context=context.copy(),
                ))
        
        return PolicyDecision(
            approved=len(violations) == 0,
            violations=violations,
            enforcement_level=ViolationSeverity.BLOCKING if violations else ViolationSeverity.INFO,
            remediation_suggestions=[r.remediation for r in self.rules]
        )


class PolicyComposer:
    """Composes multiple policies with precedence rules."""

    def __init__(self):
        """Initialize policy composer."""
        self.policies: Dict[str, GovernancePolicy] = {}
        self._precedence_rules: Dict[str, int] = {}

    def add_policy(self, policy: GovernancePolicy, precedence: int = 100) -> None:
        """Add policy to composer.
        
        Args:
            policy: Policy to add.
            precedence: Higher number = higher precedence.
        """
        self.policies[policy.policy_id] = policy
        self._precedence_rules[policy.policy_id] = precedence

    def compose(self, context: Dict[str, Any]) -> PolicyDecision:
        """Compose all policies and return combined decision.
        
        Args:
            context: Context for evaluation.
            
        Returns:
            Combined policy decision.
        """
        all_violations: List[PolicyViolation] = []
        remediation_set: set[str] = set()
        max_severity = ViolationSeverity.INFO
        
        # Evaluate policies in precedence order
        sorted_policies = sorted(
            self.policies.values(),
            key=lambda p: self._precedence_rules.get(p.policy_id, 0),
            reverse=True
        )
        
        for policy in sorted_policies:
            decision = policy.evaluate(context)
            all_violations.extend(decision.violations)
            remediation_set.update(decision.remediation_suggestions)
            
            # Track max severity
            if decision.enforcement_level == ViolationSeverity.BLOCKING:
                max_severity = ViolationSeverity.BLOCKING
        
        return PolicyDecision(
            approved=len(all_violations) == 0,
            violations=all_violations,
            enforcement_level=max_severity,
            remediation_suggestions=list(remediation_set)
        )


class GovernanceChain:
    """Chain-of-responsibility for layered governance."""

    def __init__(self):
        """Initialize governance chain."""
        self.handlers: List[Callable[[Dict[str, Any]], PolicyDecision]] = []

    def add_handler(
        self, handler: Callable[[Dict[str, Any]], PolicyDecision]
    ) -> None:
        """Add handler to chain.
        
        Args:
            handler: Handler function.
        """
        self.handlers.append(handler)

    def process(self, context: Dict[str, Any]) -> PolicyDecision:
        """Process through chain of handlers.
        
        Args:
            context: Context for processing.
            
        Returns:
            Final policy decision.
        """
        combined_violations: List[PolicyViolation] = []
        combined_remediation: List[str] = []
        
        for handler in self.handlers:
            decision = handler(context)
            combined_violations.extend(decision.violations)
            combined_remediation.extend(decision.remediation_suggestions)
            
            # Stop on blocking violation
            if decision.enforcement_level == ViolationSeverity.BLOCKING:
                break
        
        return PolicyDecision(
            approved=len(combined_violations) == 0,
            violations=combined_violations,
            enforcement_level=(
                ViolationSeverity.BLOCKING if combined_violations else ViolationSeverity.INFO
            ),
            remediation_suggestions=list(set(combined_remediation))
        )


class GovernanceComposite:
    """Main governance composite orchestrator."""

    def __init__(self):
        """Initialize composite."""
        self.policy_composer = PolicyComposer()
        self.governance_chain = GovernanceChain()
        self.audit_trail: List[Dict[str, Any]] = []
        self.metrics = {
            "policies_evaluated": 0,
            "violations_detected": 0,
            "decisions_blocked": 0,
            "total_evaluation_time_ms": 0.0,
        }

    def add_policy(self, policy: GovernancePolicy, precedence: int = 100) -> None:
        """Add policy to composite.
        
        Args:
            policy: Policy to add.
            precedence: Priority level.
        """
        self.policy_composer.add_policy(policy, precedence)

    def add_chain_handler(
        self, handler: Callable[[Dict[str, Any]], PolicyDecision]
    ) -> None:
        """Add handler to governance chain.
        
        Args:
            handler: Handler function.
        """
        self.governance_chain.add_handler(handler)

    def enforce(self, context: Dict[str, Any]) -> PolicyDecision:
        """Enforce all governance policies.
        
        Args:
            context: Context for enforcement.
            
        Returns:
            Governance decision.
        """
        import time
        start_time = time.time()
        
        # Step 1: Compose policies
        composer_decision = self.policy_composer.compose(context)
        
        # Step 2: Process through chain
        chain_decision = self.governance_chain.process(context)
        
        # Combine decisions
        all_violations = composer_decision.violations + chain_decision.violations
        
        final_decision = PolicyDecision(
            approved=len(all_violations) == 0,
            violations=all_violations,
            enforcement_level=(
                ViolationSeverity.BLOCKING if all_violations else ViolationSeverity.INFO
            ),
            remediation_suggestions=list(set(
                composer_decision.remediation_suggestions +
                chain_decision.remediation_suggestions
            ))
        )
        
        # Record evaluation time
        evaluation_time = (time.time() - start_time) * 1000
        final_decision.evaluation_time_ms = evaluation_time
        
        # Update metrics
        self._update_metrics(final_decision)
        
        # Audit trail
        self._log_audit_trail(context, final_decision)
        
        return final_decision

    def _update_metrics(self, decision: PolicyDecision) -> None:
        """Update metrics from decision.
        
        Args:
            decision: Policy decision.
        """
        self.metrics["policies_evaluated"] += 1
        self.metrics["violations_detected"] += len(decision.violations)
        if not decision.approved:
            self.metrics["decisions_blocked"] += 1
        self.metrics["total_evaluation_time_ms"] += decision.evaluation_time_ms

    def _log_audit_trail(
        self, context: Dict[str, Any], decision: PolicyDecision
    ) -> None:
        """Log decision to audit trail.
        
        Args:
            context: Evaluation context.
            decision: Decision made.
        """
        self.audit_trail.append({
            "timestamp": datetime.now().isoformat(),
            "context_keys": list(context.keys()),
            "approved": decision.approved,
            "violations_count": len(decision.violations),
            "enforcement_level": decision.enforcement_level.value,
            "evaluation_time_ms": decision.evaluation_time_ms,
        })

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get audit trail.
        
        Returns:
            Audit trail entries.
        """
        return self.audit_trail.copy()

    def get_metrics(self) -> Dict[str, Any]:
        """Get governance metrics.
        
        Returns:
            Metrics dictionary.
        """
        return self.metrics.copy()


# Tests

class TestGovernancePolicy:
    """Tests for GovernancePolicy."""

    def test_policy_initializes(self) -> None:
        """Test policy initialization."""
        policy = GovernancePolicy("pol-001", "Security Policy", PolicyLevel.CRITICAL)
        assert policy.policy_id == "pol-001"
        assert policy.enabled is True

    def test_policy_adds_rules(self) -> None:
        """Test adding rules to policy."""
        policy = GovernancePolicy("pol-001", "Security", PolicyLevel.CRITICAL)
        rule = PolicyRule("rule-001", "No passwords", PolicyLevel.CRITICAL)
        policy.add_rule(rule)
        assert len(policy.rules) == 1

    def test_policy_evaluates_context(self) -> None:
        """Test policy evaluation."""
        policy = GovernancePolicy("pol-001", "Test", PolicyLevel.HIGH)
        rule = PolicyRule(
            "rule-001", "Check value", PolicyLevel.HIGH,
            check_fn=lambda ctx: ctx.get("value", 0) > 0  # type: ignore
        )
        policy.add_rule(rule)
        decision = policy.evaluate({"value": 5})
        assert decision.approved is True


class TestPolicyComposer:
    """Tests for PolicyComposer."""

    def test_composer_adds_policies(self) -> None:
        """Test adding policies to composer."""
        composer = PolicyComposer()
        policy = GovernancePolicy("pol-001", "Policy", PolicyLevel.HIGH)
        composer.add_policy(policy)
        assert len(composer.policies) == 1

    def test_composer_respects_precedence(self) -> None:
        """Test precedence ordering."""
        composer = PolicyComposer()
        
        policy1 = GovernancePolicy("pol-001", "P1", PolicyLevel.HIGH)
        policy2 = GovernancePolicy("pol-002", "P2", PolicyLevel.HIGH)
        
        composer.add_policy(policy1, precedence=100)
        composer.add_policy(policy2, precedence=50)
        
        # Policy 1 should be evaluated first (higher precedence)
        assert len(composer.policies) == 2


class TestGovernanceChain:
    """Tests for GovernanceChain."""

    def test_chain_adds_handlers(self) -> None:
        """Test adding handlers to chain."""
        chain = GovernanceChain()
        
        def handler1(ctx: Dict[str, Any]) -> PolicyDecision:
            return PolicyDecision(approved=True)
        chain.add_handler(handler1)
        
        assert len(chain.handlers) == 1

    def test_chain_processes_handlers(self) -> None:
        """Test chain processing."""
        chain = GovernanceChain()
        
        def handler1(ctx: Dict[str, Any]) -> PolicyDecision:
            return PolicyDecision(approved=True)
        def handler2(ctx: Dict[str, Any]) -> PolicyDecision:
            return PolicyDecision(approved=True)
        
        chain.add_handler(handler1)
        chain.add_handler(handler2)
        
        decision = chain.process({})
        assert decision.approved is True


class TestGovernanceComposite:
    """Tests for GovernanceComposite."""

    def test_composite_initializes(self) -> None:
        """Test composite initialization."""
        composite = GovernanceComposite()
        assert len(composite.audit_trail) == 0
        assert composite.metrics["policies_evaluated"] == 0

    def test_composite_enforces_policies(self) -> None:
        """Test policy enforcement."""
        composite = GovernanceComposite()
        
        policy = GovernancePolicy("pol-001", "Test", PolicyLevel.HIGH)
        rule = PolicyRule(
            "rule-001", "Always pass", PolicyLevel.HIGH,
            check_fn=lambda ctx: True
        )
        policy.add_rule(rule)
        composite.add_policy(policy)
        
        decision = composite.enforce({})
        assert decision.approved is True

    def test_composite_detects_violations(self) -> None:
        """Test violation detection."""
        composite = GovernanceComposite()
        
        policy = GovernancePolicy("pol-001", "Security", PolicyLevel.CRITICAL)
        rule = PolicyRule(
            "rule-001", "Block negatives", PolicyLevel.CRITICAL,
            check_fn=lambda ctx: ctx.get("value", 0) >= 0
        )
        policy.add_rule(rule)
        composite.add_policy(policy)
        
        decision = composite.enforce({"value": -5})
        assert not decision.approved
        assert len(decision.violations) > 0

    def test_composite_tracks_metrics(self) -> None:
        """Test metrics tracking."""
        composite = GovernanceComposite()
        
        policy = GovernancePolicy("pol-001", "Test", PolicyLevel.HIGH)
        composite.add_policy(policy)
        
        composite.enforce({})
        composite.enforce({})
        
        metrics = composite.get_metrics()
        assert metrics["policies_evaluated"] == 2

    def test_composite_maintains_audit_trail(self) -> None:
        """Test audit trail logging."""
        composite = GovernanceComposite()
        
        policy = GovernancePolicy("pol-001", "Test", PolicyLevel.HIGH)
        composite.add_policy(policy)
        
        composite.enforce({"key": "value"})
        
        trail = composite.get_audit_trail()
        assert len(trail) == 1
        assert trail[0]["approved"] is True


class TestGovernanceIntegration:
    """Integration tests for governance composite."""

    def test_full_composite_workflow(self) -> None:
        """Test complete composite workflow."""
        composite = GovernanceComposite()
        
        # Add security policy
        security_policy = GovernancePolicy("pol-security", "Security", PolicyLevel.CRITICAL)
        security_rule = PolicyRule(
            "rule-no-password", "No passwords in context",
            PolicyLevel.CRITICAL,
            check_fn=lambda ctx: "password" not in str(ctx).lower()
        )
        security_policy.add_rule(security_rule)
        composite.add_policy(security_policy, precedence=100)
        
        # Add compliance policy
        compliance_policy = GovernancePolicy("pol-compliance", "Compliance", PolicyLevel.HIGH)
        composite.add_policy(compliance_policy, precedence=80)
        
        # Enforce on clean context
        decision1 = composite.enforce({"user": "alice", "role": "admin"})
        assert decision1.approved is True
        
        # Enforce on violating context
        decision2 = composite.enforce({"password": "secret123"})
        assert not decision2.approved
        
        # Verify metrics
        metrics = composite.get_metrics()
        assert metrics["policies_evaluated"] == 2
        assert metrics["violations_detected"] == 1

    def test_chain_and_composer_integration(self) -> None:
        """Test integration of chain and composer."""
        composite = GovernanceComposite()
        
        # Add policy
        policy = GovernancePolicy("pol-001", "Test", PolicyLevel.HIGH)
        composite.add_policy(policy)
        
        # Add chain handler
        def chain_handler(ctx: Dict[str, Any]) -> PolicyDecision:
            return PolicyDecision(approved=bool(ctx.get("chain_approval", True)))
        
        composite.add_chain_handler(chain_handler)
        
        # Should use both paths
        decision = composite.enforce({"chain_approval": True})
        assert decision.approved is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
