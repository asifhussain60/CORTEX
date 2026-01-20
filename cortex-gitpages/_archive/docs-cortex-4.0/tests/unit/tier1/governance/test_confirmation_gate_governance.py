"""Tests for Governance Rules and Audit Logging (AC-CONF-004-01)."""
import pytest
from datetime import datetime
from cortex_brain.tier1.governance.confirmation_gate_rules import (
    AuditTrailEntry,
    GovernanceRules,
    GovernanceEnforcer,
    AuditLogger,
)

class TestConfGate001TrivialAutoApprove:
    """CONF-GATE-001: Trivial operations must auto-approve."""
    
    def test_trivial_score_must_be_approved(self):
        """Trivial operation (score <= 0.15) must be approved."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Should pass: trivial score with approval
        assert enforcer.validate_trivial_auto_approval(0.10, approved=True) is True
    
    def test_trivial_score_rejection_violates_rule(self):
        """Trivial operation rejection violates CONF-GATE-001."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Should raise: trivial score rejected
        with pytest.raises(ValueError, match="CONF-GATE-001 violation"):
            enforcer.validate_trivial_auto_approval(0.10, approved=False)
    
    def test_non_trivial_score_no_constraint(self):
        """Non-trivial scores not constrained by CONF-GATE-001."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Should pass: non-trivial score with rejection is ok
        assert enforcer.validate_trivial_auto_approval(0.50, approved=False) is True
    
    def test_threshold_boundary_0_15(self):
        """Threshold boundary at 0.15 is trivial."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # 0.15 is still trivial
        assert enforcer.validate_trivial_auto_approval(0.15, approved=True) is True
        
        # 0.151 is not trivial
        assert enforcer.validate_trivial_auto_approval(0.151, approved=False) is True
    
    def test_violation_counter_incremented(self):
        """Violation counter incremented on rule violation."""
        enforcer = GovernanceEnforcer(enforcement_mode='PERMISSIVE')
        
        assert enforcer.violation_count == 0
        
        # Trigger violation in permissive mode (returns False instead of raising)
        enforcer.validate_trivial_auto_approval(0.10, approved=False)
        
        assert enforcer.violation_count == 1


class TestConfGate002ApprovalMatrixEnforcement:
    """CONF-GATE-002: Approval matrix enforcement."""
    
    def test_trivial_simple_auto_approvable(self):
        """TRIVIAL/SIMPLE (score <= 0.35) can be auto-approved."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # No confirmation required for TRIVIAL/SIMPLE
        assert enforcer.validate_approval_matrix(0.10, 'TRIVIAL', requires_confirmation=False) is True
        assert enforcer.validate_approval_matrix(0.35, 'SIMPLE', requires_confirmation=False) is True
    
    def test_moderate_requires_confirmation(self):
        """MODERATE (0.35 < score <= 0.60) must require confirmation."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Should pass: MODERATE with confirmation
        assert enforcer.validate_approval_matrix(0.45, 'MODERATE', requires_confirmation=True) is True
        
        # Should fail: MODERATE without confirmation
        with pytest.raises(ValueError, match="CONF-GATE-002 violation"):
            enforcer.validate_approval_matrix(0.45, 'MODERATE', requires_confirmation=False)
    
    def test_complex_requires_confirmation_and_escalation(self):
        """COMPLEX/CRITICAL (score > 0.60) must require confirmation."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Should pass: COMPLEX with confirmation
        assert enforcer.validate_approval_matrix(0.75, 'COMPLEX', requires_confirmation=True) is True
        
        # Should fail: COMPLEX without confirmation
        with pytest.raises(ValueError, match="CONF-GATE-002 violation"):
            enforcer.validate_approval_matrix(0.75, 'COMPLEX', requires_confirmation=False)
    
    def test_critical_requires_confirmation(self):
        """CRITICAL operations require confirmation."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        assert enforcer.validate_approval_matrix(0.95, 'CRITICAL', requires_confirmation=True) is True
        
        with pytest.raises(ValueError, match="CONF-GATE-002 violation"):
            enforcer.validate_approval_matrix(0.95, 'CRITICAL', requires_confirmation=False)
    
    def test_matrix_boundaries(self):
        """Test approval matrix boundary conditions."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Boundary: 0.35 is still SIMPLE (no confirmation needed)
        assert enforcer.validate_approval_matrix(0.35, 'SIMPLE', requires_confirmation=False) is True
        
        # Boundary: 0.36 is MODERATE (confirmation needed)
        with pytest.raises(ValueError):
            enforcer.validate_approval_matrix(0.36, 'MODERATE', requires_confirmation=False)


class TestConfGate003AlternativeRecommendations:
    """CONF-GATE-003: Alternative recommendations for COMPLEX/CRITICAL."""
    
    def test_complex_operation_requires_alternatives(self):
        """COMPLEX operations must provide alternatives."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Should fail: COMPLEX without alternatives
        with pytest.raises(ValueError, match="CONF-GATE-003 violation"):
            enforcer.validate_alternative_recommendations('COMPLEX', [])
    
    def test_critical_operation_requires_alternatives(self):
        """CRITICAL operations must provide alternatives."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # Should fail: CRITICAL without alternatives
        with pytest.raises(ValueError, match="CONF-GATE-003 violation"):
            enforcer.validate_alternative_recommendations('CRITICAL', [])
    
    def test_complex_with_alternatives(self):
        """COMPLEX operation with alternatives passes."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        alternatives = [
            {'name': 'Alt1', 'complexity': 0.5},
            {'name': 'Alt2', 'complexity': 0.4},
            {'name': 'Alt3', 'complexity': 0.3},
        ]
        
        assert enforcer.validate_alternative_recommendations('COMPLEX', alternatives) is True
    
    def test_simple_moderate_no_alternatives_required(self):
        """SIMPLE/MODERATE operations don't require alternatives."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        assert enforcer.validate_alternative_recommendations('SIMPLE', []) is True
        assert enforcer.validate_alternative_recommendations('MODERATE', []) is True
    
    def test_minimum_three_alternatives_preferred(self):
        """At least 3 alternatives recommended (but not enforced)."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        # 1 or 2 alternatives don't fail but are suboptimal
        alternatives_1 = [{'name': 'Alt1', 'complexity': 0.5}]
        alternatives_2 = [
            {'name': 'Alt1', 'complexity': 0.5},
            {'name': 'Alt2', 'complexity': 0.4},
        ]
        
        # Should pass (not enforced strictly, just recommended)
        assert enforcer.validate_alternative_recommendations('COMPLEX', alternatives_1) is True
        assert enforcer.validate_alternative_recommendations('COMPLEX', alternatives_2) is True


class TestConfGate004UserGoalEnhancement:
    """CONF-GATE-004: User goal enhancement with best recommendation."""
    
    def test_user_goal_enhancement_enabled_by_default(self):
        """User goal enhancement is enabled by default."""
        enforcer = GovernanceEnforcer()
        
        assert enforcer.ENABLE_GOAL_ENHANCEMENT is True
    
    def test_goal_enhancement_for_complex_operations(self):
        """Goal enhancement applies to COMPLEX operations."""
        enforcer = GovernanceEnforcer()
        
        # No recommendation (warning but not enforced)
        result = enforcer.validate_user_goal_enhancement('COMPLEX', best_recommendation=None)
        assert result is True
    
    def test_goal_enhancement_with_recommendation(self):
        """Goal enhancement with recommendation for COMPLEX."""
        enforcer = GovernanceEnforcer()
        
        result = enforcer.validate_user_goal_enhancement(
            'COMPLEX',
            best_recommendation='Refactor incrementally'
        )
        assert result is True
    
    def test_goal_enhancement_disabled(self):
        """Goal enhancement can be disabled."""
        enforcer = GovernanceEnforcer()
        enforcer.ENABLE_GOAL_ENHANCEMENT = False
        
        # Should pass regardless
        result = enforcer.validate_user_goal_enhancement('COMPLEX', best_recommendation=None)
        assert result is True


class TestConfGate005AuditTrailEnrichment:
    """CONF-GATE-005: Audit trail enrichment with complexity factors."""
    
    def test_audit_trail_entry_creation(self):
        """Audit trail entries created for all decisions."""
        enforcer = GovernanceEnforcer()
        
        entry = enforcer.record_decision_in_audit_trail(
            operation_id='op_001',
            complexity_score=0.50,
            complexity_level='MODERATE',
            complexity_factors={'lens_confidence': 0.8, 'files_affected': 0.3},
            approved=False,
            lens_confidence=0.8,
            user_intent='Refactor module',
            affected_files_count=5,
        )
        
        assert entry is not None
        assert entry.operation_id == 'op_001'
        assert entry.complexity_score == 0.50
        assert entry.complexity_level == 'MODERATE'
        assert entry.approval_decision == 'needs_confirmation'
    
    def test_audit_trail_entry_has_hash(self):
        """Audit trail entries have integrity hash."""
        enforcer = GovernanceEnforcer()
        
        entry = enforcer.record_decision_in_audit_trail(
            operation_id='op_001',
            complexity_score=0.50,
            complexity_level='MODERATE',
            complexity_factors={},
            approved=False,
            lens_confidence=0.8,
        )
        
        assert entry.entry_hash
        assert len(entry.entry_hash) == 64  # SHA256 hex length
    
    def test_audit_trail_entry_timestamp(self):
        """Audit trail entries have timestamps."""
        enforcer = GovernanceEnforcer()
        
        before = datetime.now()
        entry = enforcer.record_decision_in_audit_trail(
            operation_id='op_001',
            complexity_score=0.50,
            complexity_level='MODERATE',
            complexity_factors={},
            approved=False,
            lens_confidence=0.8,
        )
        after = datetime.now()
        
        assert before <= entry.timestamp <= after
    
    def test_audit_trail_complexity_factors_enriched(self):
        """Audit trail enriched with complexity factors."""
        enforcer = GovernanceEnforcer()
        
        complexity_factors = {
            'lens_confidence': 0.85,
            'files_affected': 0.30,
            'dependency_depth': 0.45,
            'operation_scope': 0.20,
        }
        
        entry = enforcer.record_decision_in_audit_trail(
            operation_id='op_001',
            complexity_score=0.50,
            complexity_level='MODERATE',
            complexity_factors=complexity_factors,
            approved=False,
            lens_confidence=0.85,
        )
        
        assert entry.complexity_factors == complexity_factors
    
    def test_audit_trail_persists_all_decisions(self):
        """All decisions recorded in audit trail."""
        enforcer = GovernanceEnforcer()
        
        for i in range(3):
            enforcer.record_decision_in_audit_trail(
                operation_id=f'op_{i:03d}',
                complexity_score=0.10 + (i * 0.30),
                complexity_level=['TRIVIAL', 'MODERATE', 'CRITICAL'][i],
                complexity_factors={},
                approved=(i == 0),
                lens_confidence=0.8,
            )
        
        trail = enforcer.get_audit_trail()
        assert len(trail) == 3
        assert trail[0].operation_id == 'op_000'
        assert trail[2].operation_id == 'op_002'
    
    def test_audit_trail_integrity_verification(self):
        """Audit trail integrity can be verified."""
        enforcer = GovernanceEnforcer()
        
        entry = enforcer.record_decision_in_audit_trail(
            operation_id='op_001',
            complexity_score=0.50,
            complexity_level='MODERATE',
            complexity_factors={},
            approved=False,
            lens_confidence=0.8,
        )
        
        integrity = enforcer.verify_audit_trail_integrity()
        assert integrity['integrity_valid'] is True
        assert integrity['total_entries'] == 1
        assert len(integrity['issues']) == 0
    
    def test_audit_trail_entry_unique_ids(self):
        """Audit trail entry IDs are unique."""
        enforcer = GovernanceEnforcer()
        
        entries = []
        for i in range(5):
            entry = enforcer.record_decision_in_audit_trail(
                operation_id=f'op_{i:03d}',
                complexity_score=0.30,
                complexity_level='MODERATE',
                complexity_factors={},
                approved=False,
                lens_confidence=0.8,
            )
            entries.append(entry.entry_id)
        
        assert len(set(entries)) == 5  # All unique


class TestGovernanceEnforcer:
    """Test overall governance enforcer functionality."""
    
    def test_enforcer_initialization(self):
        """Enforcer initializes correctly."""
        enforcer = GovernanceEnforcer(enforcement_mode='STRICT')
        
        assert enforcer.enforcement_mode == 'STRICT'
        assert len(enforcer.audit_trail) == 0
        assert enforcer.violation_count == 0
    
    def test_validate_all_rules(self):
        """Validate all rules for a decision."""
        enforcer = GovernanceEnforcer(enforcement_mode='PERMISSIVE')
        
        results = enforcer.validate_all_rules(
            complexity_score=0.50,
            complexity_level='MODERATE',
            approved=False,
            requires_confirmation=True,
            alternatives=[],
        )
        
        assert 'CONF-GATE-001' in results
        assert 'CONF-GATE-002' in results
        assert 'CONF-GATE-003' in results
        assert 'CONF-GATE-004' in results
        assert 'CONF-GATE-005' in results
    
    def test_compliance_tracking(self):
        """Compliance tracking across decisions."""
        enforcer = GovernanceEnforcer(enforcement_mode='PERMISSIVE')
        
        assert enforcer.is_compliant() is True
        
        # Trigger violation
        enforcer.validate_trivial_auto_approval(0.10, approved=False)
        
        assert enforcer.is_compliant() is False
    
    def test_rule_enforcement_statistics(self):
        """Get rule enforcement statistics."""
        enforcer = GovernanceEnforcer()
        
        for i in range(3):
            enforcer.record_decision_in_audit_trail(
                operation_id=f'op_{i:03d}',
                complexity_score=0.10,
                complexity_level='TRIVIAL',
                complexity_factors={},
                approved=True,
                lens_confidence=0.8,
            )
        
        stats = enforcer.get_rule_enforcement_statistics()
        assert stats['total_decisions'] == 3
        assert stats['enforcement_mode'] == 'STRICT'
        assert 'CONF-GATE-001' in stats['rules_applied']


class TestAuditLogger:
    """Test audit logger integration."""
    
    def test_audit_logger_initialization(self):
        """Audit logger initializes with enforcer."""
        enforcer = GovernanceEnforcer()
        logger = AuditLogger(enforcer)
        
        assert logger.enforcer is enforcer
        assert len(logger.external_audit_trail) == 0
    
    def test_log_to_external_audit(self):
        """Log decision to external audit system."""
        enforcer = GovernanceEnforcer()
        logger = AuditLogger(enforcer)
        
        entry = enforcer.record_decision_in_audit_trail(
            operation_id='op_001',
            complexity_score=0.50,
            complexity_level='MODERATE',
            complexity_factors={'lens': 0.8},
            approved=False,
            lens_confidence=0.8,
        )
        
        logger.log_to_external_audit(entry)
        
        assert len(logger.external_audit_trail) == 1
        assert logger.external_audit_trail[0]['operation_id'] == 'op_001'
    
    def test_governance_audit_report(self):
        """Generate governance audit report."""
        enforcer = GovernanceEnforcer()
        logger = AuditLogger(enforcer)
        
        enforcer.record_decision_in_audit_trail(
            operation_id='op_001',
            complexity_score=0.50,
            complexity_level='MODERATE',
            complexity_factors={},
            approved=False,
            lens_confidence=0.8,
        )
        
        report = logger.get_governance_audit_report()
        
        assert 'governance_rules_statistics' in report
        assert 'audit_trail_integrity' in report
        assert 'total_logged_entries' in report
        assert 'is_compliant' in report
        assert report['is_compliant'] is True


class TestGovernanceRulesEnum:
    """Test GovernanceRules enum."""
    
    def test_all_five_rules_defined(self):
        """All 5 governance rules are defined."""
        rules = [
            GovernanceRules.TRIVIAL_AUTO_APPROVE,
            GovernanceRules.APPROVAL_MATRIX_ENFORCEMENT,
            GovernanceRules.ALTERNATIVE_RECOMMENDATIONS,
            GovernanceRules.USER_GOAL_ENHANCEMENT,
            GovernanceRules.AUDIT_TRAIL_ENRICHMENT,
        ]
        
        assert len(rules) == 5
    
    def test_rule_value_format(self):
        """Rule values follow CONF-GATE-XXX format."""
        assert GovernanceRules.TRIVIAL_AUTO_APPROVE.value == 'CONF-GATE-001'
        assert GovernanceRules.APPROVAL_MATRIX_ENFORCEMENT.value == 'CONF-GATE-002'
        assert GovernanceRules.ALTERNATIVE_RECOMMENDATIONS.value == 'CONF-GATE-003'
        assert GovernanceRules.USER_GOAL_ENHANCEMENT.value == 'CONF-GATE-004'
        assert GovernanceRules.AUDIT_TRAIL_ENRICHMENT.value == 'CONF-GATE-005'
