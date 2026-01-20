"""
Tests for Tier Access Control Validation (AC-AR-012-03)

Tests tier access validation, enforcement, and audit logging.
"""

import pytest
from datetime import datetime
from typing import Any

from cortex.core.orchestrator_base import OrchestratorBase, OrchestrationContext
from cortex.core.tier_validator import (
    TierAccessValidator,
    TierAccessEnforcer,
    TierViolation,
    TierViolationType,
)


# =============================================================================
# Test Orchestrators
# =============================================================================

class Tier0Orchestrator(OrchestratorBase):
    """Orchestrator with tier 0 access only"""
    def get_tier_access(self):
        return {0}
    
    def execute(self) -> Any:
        return {"tier": "0"}


class Tier01Orchestrator(OrchestratorBase):
    """Orchestrator with tier 0,1 access"""
    def get_tier_access(self):
        return {0, 1}
    
    def execute(self) -> Any:
        return {"tiers": [0, 1]}


class AllTierOrchestrator(OrchestratorBase):
    """Orchestrator with all tiers access"""
    def get_tier_access(self):
        return {0, 1, 2, 3}
    
    def execute(self) -> Any:
        return {"tiers": [0, 1, 2, 3]}


class RuleRequiringOrchestrator(OrchestratorBase):
    """Orchestrator requiring specific rules"""
    def get_required_rules(self):
        return ["RULE-A", "RULE-B"]
    
    def execute(self) -> Any:
        return {"rules": self.get_required_rules()}


# =============================================================================
# Tests: TierAccessValidator
# =============================================================================

class TestTierAccessValidator:
    """Test TierAccessValidator class"""
    
    def test_validator_creation(self):
        """Test creating validator instances"""
        validator_enforce = TierAccessValidator(enforce_mode=True)
        assert validator_enforce.enforce_mode is True
        
        validator_warn = TierAccessValidator(enforce_mode=False)
        assert validator_warn.enforce_mode is False
    
    def test_validate_tier_declaration_valid(self):
        """Test validating valid tier declarations"""
        validator = TierAccessValidator(enforce_mode=True)
        
        # Valid: all single tiers
        assert validator.validate_tier_declaration("orch-1", "Orch1", {0}) is True
        assert validator.validate_tier_declaration("orch-2", "Orch2", {1}) is True
        assert validator.validate_tier_declaration("orch-3", "Orch3", {2}) is True
        assert validator.validate_tier_declaration("orch-4", "Orch4", {3}) is True
        
        # Valid: multiple tiers
        assert validator.validate_tier_declaration("orch-5", "Orch5", {0, 1}) is True
        assert validator.validate_tier_declaration("orch-6", "Orch6", {0, 1, 2, 3}) is True
    
    def test_validate_tier_declaration_invalid_tiers(self):
        """Test validating invalid tier declarations"""
        validator = TierAccessValidator(enforce_mode=False)
        
        # Invalid: negative tier
        assert validator.validate_tier_declaration("orch-1", "Orch1", {-1}) is False
        
        # Invalid: tier > 3
        assert validator.validate_tier_declaration("orch-2", "Orch2", {4}) is False
        
        # Invalid: mixed valid and invalid
        assert validator.validate_tier_declaration("orch-3", "Orch3", {0, 5}) is False
    
    def test_validate_tier_declaration_enforce_mode_raises(self):
        """Test that enforce_mode raises on invalid tiers"""
        validator = TierAccessValidator(enforce_mode=True)
        
        with pytest.raises(ValueError, match="Invalid tier access"):
            validator.validate_tier_declaration("orch-1", "Orch1", {-1})
    
    def test_validate_access_attempt_allowed(self):
        """Test validating allowed access attempts"""
        validator = TierAccessValidator(enforce_mode=True)
        
        context = OrchestrationContext("test-1", "Test")
        orch = Tier01Orchestrator(context)
        
        # Access to declared tiers should be allowed
        assert validator.validate_access_attempt(orch, 0) is True
        assert validator.validate_access_attempt(orch, 1) is True
    
    def test_validate_access_attempt_denied(self):
        """Test validating denied access attempts"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        orch = Tier01Orchestrator(context)
        
        # Access to undeclared tiers should be denied
        assert validator.validate_access_attempt(orch, 2) is False
        assert validator.validate_access_attempt(orch, 3) is False
    
    def test_validate_access_attempt_enforce_mode_raises(self):
        """Test that enforce_mode raises on access denial"""
        validator = TierAccessValidator(enforce_mode=True)
        
        context = OrchestrationContext("test-1", "Test")
        orch = Tier01Orchestrator(context)
        
        with pytest.raises(PermissionError, match="Undeclared tier access"):
            validator.validate_access_attempt(orch, 2)
    
    def test_validate_access_with_governance_rules(self):
        """Test validating access with governance rules"""
        validator = TierAccessValidator(enforce_mode=True)
        
        context = OrchestrationContext("test-1", "Test")
        orch = RuleRequiringOrchestrator(context)
        
        # Access with matching rules should be allowed
        assert validator.validate_access_attempt(
            orch, 0,
            governance_rules=["RULE-A", "RULE-B"]
        ) is True
    
    def test_validate_access_missing_governance_rules(self):
        """Test denying access when governance rules missing"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        orch = RuleRequiringOrchestrator(context)
        
        # Access without required rules should be denied
        assert validator.validate_access_attempt(
            orch, 0,
            governance_rules=["RULE-A", "RULE-B", "RULE-C"]  # RULE-C not in orchestrator
        ) is False
    
    def test_validate_context_integrity_valid(self):
        """Test validating context integrity"""
        validator = TierAccessValidator(enforce_mode=True)
        
        # Create context with correct tier access
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 1}
        
        orch = Tier01Orchestrator(context)
        assert validator.validate_context_integrity(orch) is True
    
    def test_validate_context_integrity_mismatch(self):
        """Test detecting context tier access mismatch"""
        validator = TierAccessValidator(enforce_mode=False)
        
        # Create context with incorrect tier access
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 2}  # Wrong: should be {0, 1}
        
        orch = Tier01Orchestrator(context)
        assert validator.validate_context_integrity(orch) is False
    
    def test_validate_context_injection(self):
        """Test validating context injection"""
        validator = TierAccessValidator(enforce_mode=True)
        
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 1}
        context.required_rules = ["RULE-A", "RULE-B"]
        
        # Valid injection
        assert validator.validate_context_injection(
            context,
            tier_dependencies={0, 1},
            required_rules=["RULE-A", "RULE-B"]
        ) is True
    
    def test_validate_context_injection_tier_mismatch(self):
        """Test detecting tier injection mismatch"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 2}
        context.required_rules = ["RULE-A"]
        
        # Invalid injection: tiers don't match
        assert validator.validate_context_injection(
            context,
            tier_dependencies={0, 1},
            required_rules=["RULE-A"]
        ) is False
    
    def test_validate_context_injection_rule_mismatch(self):
        """Test detecting rule injection mismatch"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 1}
        context.required_rules = ["RULE-A", "RULE-C"]
        
        # Invalid injection: rules don't match
        assert validator.validate_context_injection(
            context,
            tier_dependencies={0, 1},
            required_rules=["RULE-A", "RULE-B"]
        ) is False


# =============================================================================
# Tests: Violation Tracking
# =============================================================================

class TestViolationTracking:
    """Test violation tracking and reporting"""
    
    def test_violations_recorded(self):
        """Test that violations are recorded"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        orch = Tier01Orchestrator(context)
        
        # Attempt undeclared access
        validator.validate_access_attempt(orch, 2)
        
        assert validator.get_violation_count() == 1
        violations = validator.get_violations()
        assert len(violations) == 1
        assert violations[0].violation_type == TierViolationType.UNDECLARED_ACCESS
    
    def test_get_violations_by_orchestrator(self):
        """Test filtering violations by orchestrator"""
        validator = TierAccessValidator(enforce_mode=False)
        
        # Create violations from different orchestrators
        context1 = OrchestrationContext("test-1", "Test1")
        orch1 = Tier01Orchestrator(context1)
        
        context2 = OrchestrationContext("test-2", "Test2")
        orch2 = Tier0Orchestrator(context2)
        
        validator.validate_access_attempt(orch1, 2)
        validator.validate_access_attempt(orch2, 1)
        
        # Filter by first orchestrator
        violations = validator.get_violations(orchestrator_id="test-1")
        assert len(violations) == 1
        assert violations[0].orchestrator_id == "test-1"
    
    def test_get_violations_by_type(self):
        """Test filtering violations by type"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        orch = Tier01Orchestrator(context)
        
        # Create different types of violations
        validator.validate_access_attempt(orch, 2)  # UNDECLARED_ACCESS
        validator.validate_tier_declaration("test-2", "Test2", {-1})  # INSUFFICIENT_PERMISSION
        
        # Filter by undeclared access
        undeclared = validator.get_violations(
            violation_type=TierViolationType.UNDECLARED_ACCESS
        )
        assert len(undeclared) == 1
    
    def test_clear_violations(self):
        """Test clearing violations"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        orch = Tier01Orchestrator(context)
        
        validator.validate_access_attempt(orch, 2)
        assert validator.get_violation_count() == 1
        
        validator.clear_violations()
        assert validator.get_violation_count() == 0
    
    def test_violation_summary(self):
        """Test getting violation summary"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context1 = OrchestrationContext("test-1", "Test1")
        orch1 = Tier01Orchestrator(context1)
        
        context2 = OrchestrationContext("test-2", "Test2")
        orch2 = Tier01Orchestrator(context2)
        
        # Create multiple violations of same type
        validator.validate_access_attempt(orch1, 2)
        validator.validate_access_attempt(orch1, 3)
        validator.validate_access_attempt(orch2, 2)
        
        summary = validator.get_violation_summary()
        assert summary["undeclared_access"] == 3
    
    def test_audit_report(self):
        """Test creating audit report"""
        validator = TierAccessValidator(enforce_mode=False)
        
        context = OrchestrationContext("test-1", "Test")
        orch = Tier01Orchestrator(context)
        
        validator.validate_access_attempt(orch, 2)
        validator.validate_access_attempt(orch, 3)
        
        report = validator.create_audit_report()
        
        assert report["total_violations"] == 2
        assert report["enforce_mode"] is False
        assert len(report["violations"]) == 2
        assert "timestamp" in report
        assert "violation_summary" in report


# =============================================================================
# Tests: TierAccessEnforcer
# =============================================================================

class TestTierAccessEnforcer:
    """Test TierAccessEnforcer class"""
    
    def test_enforcer_creation(self):
        """Test creating enforcer"""
        enforcer = TierAccessEnforcer()
        assert enforcer.validator is not None
    
    def test_enforcer_with_custom_validator(self):
        """Test creating enforcer with custom validator"""
        validator = TierAccessValidator(enforce_mode=False)
        enforcer = TierAccessEnforcer(validator=validator)
        
        assert enforcer.validator is validator
    
    def test_enforce_on_orchestrator_valid(self):
        """Test enforcing on valid orchestrator"""
        enforcer = TierAccessEnforcer()
        
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 1}  # Correct
        
        orch = Tier01Orchestrator(context)
        
        assert enforcer.enforce_on_orchestrator(orch) is True
    
    def test_enforce_on_orchestrator_context_mismatch(self):
        """Test enforcing on orchestrator with context mismatch"""
        validator = TierAccessValidator(enforce_mode=False)
        enforcer = TierAccessEnforcer(validator=validator)
        
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 2}  # Wrong
        
        orch = Tier01Orchestrator(context)
        
        assert enforcer.enforce_on_orchestrator(orch) is False
    
    def test_enforce_on_orchestrator_with_governance_rules(self):
        """Test enforcing with governance rules"""
        enforcer = TierAccessEnforcer()
        
        context = OrchestrationContext("test-1", "Test")
        context.required_rules = ["RULE-A", "RULE-B"]
        
        orch = RuleRequiringOrchestrator(context)
        
        # Enforce with matching rules
        assert enforcer.enforce_on_orchestrator(
            orch,
            governance_rules=["RULE-A", "RULE-B"]
        ) is True
    
    def test_enforcer_get_violations(self):
        """Test getting violations from enforcer"""
        validator = TierAccessValidator(enforce_mode=False)
        enforcer = TierAccessEnforcer(validator=validator)
        
        context = OrchestrationContext("test-1", "Test")
        context.tier_access = {0, 2}  # Wrong: should be {0, 1}
        
        orch = Tier01Orchestrator(context)
        
        enforcer.enforce_on_orchestrator(orch)
        
        violations = enforcer.get_violations()
        assert len(violations) > 0


# =============================================================================
# Tests: TierViolation
# =============================================================================

class TestTierViolation:
    """Test TierViolation class"""
    
    def test_violation_creation(self):
        """Test creating violation"""
        violation = TierViolation(
            violation_type=TierViolationType.UNDECLARED_ACCESS,
            orchestrator_id="test-1",
            orchestrator_name="TestOrch",
            accessed_tier=2,
            declared_tiers={0, 1},
            timestamp=datetime.now(),
        )
        
        assert violation.violation_type == TierViolationType.UNDECLARED_ACCESS
        assert violation.orchestrator_id == "test-1"
        assert violation.enforcement_action == "DENY"
    
    def test_violation_to_dict(self):
        """Test converting violation to dict"""
        now = datetime.now()
        violation = TierViolation(
            violation_type=TierViolationType.UNDECLARED_ACCESS,
            orchestrator_id="test-1",
            orchestrator_name="TestOrch",
            accessed_tier=2,
            declared_tiers={0, 1},
            timestamp=now,
            rule_violated="RULE-X",
        )
        
        d = violation.to_dict()
        
        assert d["violation_type"] == "undeclared_access"
        assert d["orchestrator_id"] == "test-1"
        assert d["accessed_tier"] == 2
        assert d["declared_tiers"] == [0, 1]
        assert d["rule_violated"] == "RULE-X"
