"""
Unit tests for GovernancePregate interface (AC-FIX-002-01).

This test suite validates the GovernancePregate interface implementation,
which provides pre-execution governance validation gates.

FINDING-002 addresses: Governance validation must happen BEFORE orchestrator execution
(not after), to prevent unauthorized operations from executing.

Tests:
- PreGate interface definition
- Resource quota validation
- Authorization validation
- Tier access validation
- Gate decision logic
"""

import pytest
from typing import List, Dict, Any
from dataclasses import dataclass

from src.core.governance_pregate import (
    GovernancePregate, 
    PreGateDecision, 
    DefaultGovernancePregate,
    get_governance_pregate,
    set_governance_pregate
)
from src.core.governance_registry import GovernanceRegistry


class TestGovernancePregateInterface:
    """Test GovernancePregate interface definition."""
    
    def test_pregate_interface_exists(self):
        """Verify GovernancePregate interface is defined."""
        assert GovernancePregate is not None
        assert hasattr(GovernancePregate, 'check_resource_quota')
        assert hasattr(GovernancePregate, 'check_authorization')
        assert hasattr(GovernancePregate, 'check_tier_access')
    
    def test_pregate_interface_has_required_methods(self):
        """Verify GovernancePregate has all required abstract methods."""
        # Methods should be:
        # - check_resource_quota(operation_id, estimated_cost)
        # - check_authorization(operation_id, actor_id, target_resource)
        # - check_tier_access(tier_id, operation_context)
        assert hasattr(GovernancePregate, 'check_resource_quota')
        assert hasattr(GovernancePregate, 'check_authorization')
        assert hasattr(GovernancePregate, 'check_tier_access')
        assert hasattr(GovernancePregate, 'evaluate_all_gates')
    
    def test_pregate_decision_dataclass(self):
        """Verify PreGateDecision dataclass exists."""
        # Should contain:
        # - allowed: bool
        # - reason: str
        # - violation_type: Optional[str]
        # - audit_context: Dict[str, Any]
        decision = PreGateDecision(
            allowed=True,
            reason="Test decision"
        )
        assert hasattr(decision, 'allowed')
        assert hasattr(decision, 'reason')
        assert hasattr(decision, 'violation_type')
        assert hasattr(decision, 'audit_context')
        assert decision.allowed == True
        assert decision.reason == "Test decision"
        assert decision.violation_type is None
        assert "timestamp" in decision.audit_context


class TestResourceQuotaGate:
    """Test resource quota pre-gate validation."""
    
    def test_resource_quota_gate_blocks_exceeded_quota(self):
        """Verify gate blocks operations exceeding resource quota."""
        # Scenario: Operation requires 5000 tokens, quota is 1000
        # Expected: Gate returns allowed=False
        pregate = DefaultGovernancePregate(max_token_quota=1000)
        
        decision = pregate.check_resource_quota(
            operation_id="op_001",
            estimated_token_cost=5000,
            context={"actor_id": "user_001"}
        )
        
        assert decision.allowed == False
        assert "Quota exceeded" in decision.reason
        assert decision.violation_type == "RESOURCE_QUOTA"
    
    def test_resource_quota_gate_allows_within_quota(self):
        """Verify gate allows operations within quota."""
        # Scenario: Operation requires 500 tokens, quota is 1000
        # Expected: Gate returns allowed=True
        pregate = DefaultGovernancePregate(max_token_quota=1000)
        
        decision = pregate.check_resource_quota(
            operation_id="op_001",
            estimated_token_cost=500,
            context={"actor_id": "user_001"}
        )
        
        assert decision.allowed == True
        assert "passed" in decision.reason.lower()
        assert decision.violation_type is None
    
    def test_resource_quota_includes_explanation(self):
        """Verify gate decision includes reason when blocked."""
        # Expected: reason = "Quota exceeded: 5000 tokens requested, 1000 available"
        pregate = DefaultGovernancePregate(max_token_quota=1000)
        
        decision = pregate.check_resource_quota(
            operation_id="op_001",
            estimated_token_cost=5000,
            context={"actor_id": "user_001"}
        )
        
        assert "5000" in decision.reason
        assert "available" in decision.reason.lower()
        assert decision.audit_context["tokens_requested"] == 5000
    
    def test_resource_quota_tracks_usage(self):
        """Verify quota tracking across multiple operations."""
        # Op 1: Use 600 tokens (400 remaining)
        # Op 2: Use 300 tokens (100 remaining)
        # Op 3: Require 200 tokens → BLOCKED
        pregate = DefaultGovernancePregate(max_token_quota=1000)
        
        # Op 1
        decision1 = pregate.check_resource_quota(
            operation_id="op_001",
            estimated_token_cost=600,
            context={"actor_id": "user_001"}
        )
        assert decision1.allowed == True
        
        # Op 2
        decision2 = pregate.check_resource_quota(
            operation_id="op_002",
            estimated_token_cost=300,
            context={"actor_id": "user_001"}
        )
        assert decision2.allowed == True
        
        # Op 3 - should fail
        decision3 = pregate.check_resource_quota(
            operation_id="op_003",
            estimated_token_cost=200,
            context={"actor_id": "user_001"}
        )
        assert decision3.allowed == False
        assert "Quota exceeded" in decision3.reason


class TestAuthorizationGate:
    """Test authorization pre-gate validation."""
    
    def test_authorization_gate_blocks_unauthorized_actor(self):
        """Verify gate blocks operations from unauthorized actors."""
        # Scenario: Actor "user_002" trying to access "admin_resources"
        # Expected: Gate returns allowed=False, reason="Unauthorized actor"
        pregate = DefaultGovernancePregate()
        
        # Set rules: user_001 can access admin_resources, user_002 cannot
        pregate.set_authorization_rule("user_001", ["admin_resources", "standard_resources"])
        pregate.set_authorization_rule("user_002", ["standard_resources"])
        
        # user_002 tries to access admin_resources
        decision = pregate.check_authorization(
            operation_id="op_admin",
            actor_id="user_002",
            target_resource="admin_resources"
        )
        
        assert decision.allowed == False
        assert "not authorized" in decision.reason.lower()
        assert decision.violation_type == "AUTHORIZATION"
    
    def test_authorization_gate_allows_authorized_actor(self):
        """Verify gate allows operations from authorized actors."""
        # Scenario: Actor "admin_001" accessing "admin_resources"
        # Expected: Gate returns allowed=True
        pregate = DefaultGovernancePregate()
        
        pregate.set_authorization_rule("admin_001", ["admin_resources"])
        
        decision = pregate.check_authorization(
            operation_id="op_admin",
            actor_id="admin_001",
            target_resource="admin_resources"
        )
        
        assert decision.allowed == True
        assert "authorized" in decision.reason.lower()
    
    def test_authorization_gate_checks_resource_level_permissions(self):
        """Verify gate validates resource-specific permissions."""
        # Actor may have tier access but not specific resource access
        pregate = DefaultGovernancePregate()
        
        pregate.set_authorization_rule("user_001", ["resource_a", "resource_b"])
        
        # Can access resource_a
        decision1 = pregate.check_authorization(
            operation_id="op_001",
            actor_id="user_001",
            target_resource="resource_a"
        )
        assert decision1.allowed == True
        
        # Cannot access resource_c
        decision2 = pregate.check_authorization(
            operation_id="op_002",
            actor_id="user_001",
            target_resource="resource_c"
        )
        assert decision2.allowed == False


class TestTierAccessGate:
    """Test tier access pre-gate validation."""
    
    def test_tier_access_gate_enforces_tier0_immutability(self):
        """Verify gate prevents any modifications to TIER-0 rules."""
        # Scenario: Operation attempts to modify TIER-0 rule
        # Expected: Gate returns allowed=False
        pregate = DefaultGovernancePregate()
        
        decision = pregate.check_tier_access(
            tier_id="TIER-0",
            operation_id="op_modify_tier0",
            declared_access=["TIER-1"],
            context={"is_modification": True}
        )
        
        assert decision.allowed == False
        assert "immutable" in decision.reason.lower()
        assert decision.violation_type == "TIER_ACCESS"
    
    def test_tier_access_gate_allows_tier1_modifications(self):
        """Verify gate allows modifications to TIER-1 rules."""
        pregate = DefaultGovernancePregate()
        
        decision = pregate.check_tier_access(
            tier_id="TIER-1",
            operation_id="op_modify_tier1",
            declared_access=["TIER-1"],
            context={"is_modification": True}
        )
        
        assert decision.allowed == True
    
    def test_tier_access_gate_validates_declared_access(self):
        """Verify gate checks if operation declared tier access."""
        # ConversationProtocol declares "tier_access=['TIER-1', 'TIER-2']"
        # Gate should verify operation doesn't try TIER-0 access
        pregate = DefaultGovernancePregate()
        
        decision = pregate.check_tier_access(
            tier_id="TIER-1",
            operation_id="op_001",
            declared_access=["TIER-1", "TIER-2"]
        )
        
        assert decision.allowed == True
    
    def test_tier_access_gate_blocks_undeclared_access(self):
        """Verify gate blocks access to tiers not explicitly declared."""
        pregate = DefaultGovernancePregate()
        
        decision = pregate.check_tier_access(
            tier_id="TIER-0",
            operation_id="op_001",
            declared_access=["TIER-1", "TIER-2"]
        )
        
        assert decision.allowed == False
        assert "did not declare" in decision.reason.lower()


class TestPreGateDecision:
    """Test pre-gate decision structure and content."""
    
    def test_pregate_decision_on_allow(self):
        """Verify PreGateDecision content when gate allows operation."""
        # decision.allowed = True
        # decision.reason = "All checks passed"
        # decision.audit_context['gate_checks_performed'] = [...]
        decision = PreGateDecision(
            allowed=True,
            reason="All checks passed"
        )
        
        assert decision.allowed == True
        assert decision.reason == "All checks passed"
        assert decision.violation_type is None
        assert "timestamp" in decision.audit_context
    
    def test_pregate_decision_on_block(self):
        """Verify PreGateDecision content when gate blocks operation."""
        # decision.allowed = False
        # decision.reason = "Resource quota exceeded"
        # decision.violation_type = "RESOURCE_QUOTA"
        # decision.audit_context['violation_details'] = {...}
        decision = PreGateDecision(
            allowed=False,
            reason="Resource quota exceeded",
            violation_type="RESOURCE_QUOTA",
            audit_context={"violation_details": "More details here"}
        )
        
        assert decision.allowed == False
        assert decision.reason == "Resource quota exceeded"
        assert decision.violation_type == "RESOURCE_QUOTA"
        assert "timestamp" in decision.audit_context
    
    def test_pregate_decision_audit_context_completeness(self):
        """Verify audit_context has all required information."""
        # Required fields:
        # - timestamp
        # - actor_id (optional but important)
        # - operation_id (optional but important)
        decision = PreGateDecision(
            allowed=False,
            reason="Test violation",
            violation_type="TEST",
            audit_context={
                "actor_id": "test_actor",
                "operation_id": "test_op",
                "checks_performed": ["check_1", "check_2"]
            }
        )
        
        assert "timestamp" in decision.audit_context
        assert decision.audit_context["actor_id"] == "test_actor"
        assert decision.audit_context["operation_id"] == "test_op"
        assert "checks_performed" in decision.audit_context


class TestPreGateIntegrationWithGovernanceRegistry:
    """Test PreGate integration with existing GovernanceRegistry."""
    
    def test_pregate_uses_governance_registry_rules(self):
        """Verify pregate consults governance registry for rules."""
        # When initialized, pregate should load rules from registry
        pregate = get_governance_pregate()
        assert pregate is not None
        assert isinstance(pregate, GovernancePregate)
    
    def test_pregate_respects_tier_hierarchy(self):
        """Verify pregate enforces tier precedence (0 > 1 > 2)."""
        pregate = DefaultGovernancePregate()
        
        # TIER-0 always immutable (no check needed)
        # TIER-1 modifiable
        # TIER-2 modifiable
        
        decision_tier0 = pregate.check_tier_access(
            "TIER-0", "op1", ["TIER-1"],
            context={"is_modification": True}
        )
        assert decision_tier0.allowed == False  # TIER-0 immutable
        
        decision_tier1 = pregate.check_tier_access(
            "TIER-1", "op1", ["TIER-1"],
            context={"is_modification": True}
        )
        assert decision_tier1.allowed == True  # TIER-1 modifiable
    
    def test_pregate_can_be_injected_into_conversation_protocol(self):
        """Verify PreGate can be injected into ConversationProtocol."""
        pregate = DefaultGovernancePregate()
        set_governance_pregate(pregate)
        
        retrieved = get_governance_pregate()
        assert retrieved is pregate


class TestPreGateErrorHandling:
    """Test PreGate error handling and edge cases."""
    
    def test_pregate_handles_missing_actor_id(self):
        """Verify pregate handles missing actor_id gracefully."""
        pregate = DefaultGovernancePregate()
        
        # Without context
        decision = pregate.check_resource_quota(
            operation_id="op_1",
            estimated_token_cost=100,
            context=None
        )
        # Should still work, using "unknown" actor
        assert decision.allowed == True
    
    def test_pregate_handles_invalid_operation_id(self):
        """Verify pregate handles invalid operation_id."""
        pregate = DefaultGovernancePregate()
        
        decision = pregate.check_resource_quota(
            operation_id="",
            estimated_token_cost=100,
            context={"actor_id": "user_001"}
        )
        # Should still work with empty operation_id
        assert decision.allowed == True
    
    def test_evaluate_all_gates_short_circuits_on_first_block(self):
        """Verify all_gates evaluation stops at first blocking gate."""
        pregate = DefaultGovernancePregate(max_token_quota=100)
        
        # Resource quota will fail immediately
        decision = pregate.evaluate_all_gates(
            operation_id="op_1",
            actor_id="user_1",
            target_resource="resource_1",
            estimated_token_cost=1000  # Exceeds quota
        )
        
        assert decision.allowed == False
        assert "RESOURCE_QUOTA" in str(decision.audit_context.get("checks_performed", []))
        assert decision.violation_type == "RESOURCE_QUOTA"


class TestPreGatePerformance:
    """Test PreGate performance characteristics."""
    
    def test_pregate_check_completes_quickly(self):
        """Verify pregate check completes quickly."""
        # Gate should be performant - not block orchestrator execution
        import time
        
        pregate = DefaultGovernancePregate()
        
        start = time.time()
        decision = pregate.check_resource_quota(
            operation_id="op_1",
            estimated_token_cost=100,
            context={"actor_id": "user_1"}
        )
        elapsed = time.time() - start
        
        # Should complete in less than 10ms
        assert elapsed < 0.01
        assert decision.allowed == True
    
    def test_pregate_all_gates_complete_quickly(self):
        """Verify all gates check completes quickly."""
        import time
        
        pregate = DefaultGovernancePregate()
        
        start = time.time()
        decision = pregate.evaluate_all_gates(
            operation_id="op_1",
            actor_id="user_1",
            target_resource="resource_1",
            estimated_token_cost=100,
            tier_access=["TIER-1", "TIER-2"]
        )
        elapsed = time.time() - start
        
        # Should complete in less than 50ms even with all gates
        assert elapsed < 0.05
        assert decision.allowed == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
