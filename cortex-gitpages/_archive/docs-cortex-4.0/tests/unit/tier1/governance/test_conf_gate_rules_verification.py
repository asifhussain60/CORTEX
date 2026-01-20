"""
Test suite for CONF-GATE governance rules verification.
AC-REM-010-02: Verify governance rules implementation.
"""
import pytest
from src.confirmation.governance import GovernanceEngine, GovernanceRule, GovernanceRuleType, AuditEventType
from src.orchestrators.core.stage_2_5_gate import Stage25Gate, ConfirmationContext
from src.core.orchestrator.complexity_assessment import ComplexitySignals
from datetime import datetime


@pytest.fixture
def gov_engine():
    """Create governance engine."""
    return GovernanceEngine()


@pytest.fixture
def stage_gate():
    """Create Stage 2.5 gate."""
    return Stage25Gate()


class TestConfGateGovernance:
    """Test CONF-GATE governance rules."""
    
    def test_conf_gate_001_trivial_auto_approval(self, gov_engine):
        """CONF-GATE-001: Trivial operations auto-approved without override."""
        # Trivial operation: complexity ≤ 0.15
        rule = GovernanceRule(
            rule_id="CONF-GATE-001",
            rule_type=GovernanceRuleType.APPROVAL_ROUTING,
            description="Trivial operations auto-approval enforcement",
            enforcement_level="strict",
            is_active=True,
            created_at=datetime.now(),
            created_by="cortex"
        )
        gov_engine.register_rule(rule)
        
        # Verify rule is active
        assert gov_engine.is_rule_active("CONF-GATE-001")
        assert gov_engine.get_rule("CONF-GATE-001").enforcement_level == "strict"
    
    def test_conf_gate_002_approval_matrix_enforcement(self, stage_gate):
        """CONF-GATE-002: Confidence-based approval matrix enforcement."""
        trivial_signals = ComplexitySignals(
            lens_confidence=0.95, files_affected_count=1, call_graph_depth=1,
            circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
            operation_scope='local', ast_complexity=2, criticality_level='low'
        )
        
        decision = stage_gate.evaluate(
            operation_id="op_test",
            lens_confidence=0.95,
            signals=trivial_signals,
        )
        
        # Trivial should auto-approve
        assert decision.continue_execution is True
        assert decision.is_confirmation_gate is False
    
    def test_conf_gate_003_alternative_recommendations(self, stage_gate):
        """CONF-GATE-003: Alternative recommendations for COMPLEX ops."""
        complex_signals = ComplexitySignals(
            lens_confidence=0.30, files_affected_count=50, call_graph_depth=10,
            circular_dependencies=3, dependency_depth=5, tight_coupling_score=0.9,
            operation_scope='global', ast_complexity=50, criticality_level='critical'
        )
        
        decision = stage_gate.evaluate(
            operation_id="op_complex",
            lens_confidence=0.30,
            signals=complex_signals,
            alternatives=[
                {"approach": "refactor_first", "confidence": 0.85},
                {"approach": "incremental", "confidence": 0.75},
                {"approach": "rollback", "confidence": 0.60},
            ]
        )
        
        # Complex should request confirmation
        assert decision.continue_execution is False
        assert decision.confirmation_context is not None
        # Alternatives should be available
        assert len(decision.confirmation_context.alternatives) >= 1
    
    def test_conf_gate_004_005_audit_trail_enrichment(self, gov_engine, stage_gate):
        """CONF-GATE-004/005: Audit trail enrichment with complexity factors."""
        moderate_signals = ComplexitySignals(
            lens_confidence=0.70, files_affected_count=5, call_graph_depth=4,
            circular_dependencies=0, dependency_depth=2, tight_coupling_score=0.3,
            operation_scope='cross_layer', ast_complexity=15, criticality_level='medium'
        )
        
        decision = stage_gate.evaluate(
            operation_id="op_audit_test",
            lens_confidence=0.70,
            signals=moderate_signals,
        )
        
        # Verify decision has complexity metadata
        assert decision.confirmation_context is not None
        assert decision.confirmation_context.complexity_score is not None
        assert decision.confirmation_context.complexity_level is not None
        assert decision.confirmation_context.confidence is not None
        assert decision.confirmation_context.lens_confidence == 0.70
        
        # Log audit entry
        audit_entry = gov_engine.log_gate_decision(
            conversation_id="conv_001",
            actor_id="orchestrator",
            operation_id="op_audit_test",
            approval_decision=decision.continue_execution,
            complexity_score=decision.confirmation_context.complexity_score,
            complexity_level=decision.confirmation_context.complexity_level,
            rules_enforced=["CONF-GATE-002", "CONF-GATE-005"]
        )
        
        # Verify audit entry contains complexity factors
        assert audit_entry is not None
        assert "complexity_score" in audit_entry.metadata
        assert "complexity_level" in audit_entry.metadata
        assert audit_entry.event_type == AuditEventType.GATE_DECISION


class TestGovernanceRuleIntegration:
    """Test governance rules integration with gate."""
    
    def test_all_conf_gate_rules_active(self, gov_engine):
        """Verify all 5 CONF-GATE rules are registered and active."""
        # Initialize rules
        for i in range(1, 6):
            rule = GovernanceRule(
                rule_id=f"CONF-GATE-{i:03d}",
                rule_type=GovernanceRuleType.APPROVAL_ROUTING,
                description=f"CONF-GATE rule {i}",
                enforcement_level="strict",
                is_active=True,
                created_at=datetime.now(),
                created_by="cortex"
            )
            gov_engine.register_rule(rule)
        
        # Verify all rules active
        for i in range(1, 6):
            assert gov_engine.is_rule_active(f"CONF-GATE-{i:03d}")
    
    def test_compliance_audit_trail(self, gov_engine):
        """Verify compliance audit trail tracking."""
        # Create test entry
        entry = gov_engine.log_gate_decision(
            conversation_id="conv_test",
            actor_id="test_actor",
            operation_id="op_test",
            approval_decision=True,
            complexity_score=0.45,
            complexity_level="moderate",
            rules_enforced=["CONF-GATE-001", "CONF-GATE-002"]
        )
        
        assert entry is not None
        assert entry.metadata["complexity_score"] == 0.45
        assert entry.metadata["complexity_level"] == "moderate"
        assert "CONF-GATE-001" in entry.affected_rules


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
