"""Tests for Approval Gate Logic."""
import pytest
from src.core.orchestrator.complexity_assessment import (
    ComplexitySignals,
    ComplexityAssessment,
    ComplexityLevel,
    ComplexityAssessmentEngine,
)
from src.core.orchestrator.approval_gate import (
    ApprovalGateLogic,
    ApprovalDecision,
    ConfirmationRequest,
    AlternativeRecommendation,
)

@pytest.fixture
def gate():
    """Create approval gate logic."""
    return ApprovalGateLogic()

@pytest.fixture
def engine():
    """Create complexity assessment engine."""
    return ComplexityAssessmentEngine()

@pytest.fixture
def trivial_assessment():
    """Create trivial complexity assessment."""
    signals = ComplexitySignals(
        lens_confidence=0.95, files_affected_count=1, call_graph_depth=1,
        circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
        operation_scope='local', ast_complexity=2, criticality_level='low'
    )
    engine = ComplexityAssessmentEngine()
    return engine.assess_complexity(signals)

@pytest.fixture
def simple_assessment():
    """Create simple complexity assessment."""
    signals = ComplexitySignals(
        lens_confidence=0.88, files_affected_count=2, call_graph_depth=2,
        circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.1,
        operation_scope='local', ast_complexity=5, criticality_level='low'
    )
    engine = ComplexityAssessmentEngine()
    return engine.assess_complexity(signals)

@pytest.fixture
def moderate_assessment():
    """Create moderate complexity assessment."""
    signals = ComplexitySignals(
        lens_confidence=0.70, files_affected_count=5, call_graph_depth=4,
        circular_dependencies=0, dependency_depth=2, tight_coupling_score=0.3,
        operation_scope='cross_layer', ast_complexity=15, criticality_level='medium'
    )
    engine = ComplexityAssessmentEngine()
    return engine.assess_complexity(signals)

@pytest.fixture
def complex_assessment():
    """Create complex complexity assessment."""
    signals = ComplexitySignals(
        lens_confidence=0.50, files_affected_count=25, call_graph_depth=8,
        circular_dependencies=1, dependency_depth=4, tight_coupling_score=0.7,
        operation_scope='global', ast_complexity=40, criticality_level='high'
    )
    engine = ComplexityAssessmentEngine()
    return engine.assess_complexity(signals)

@pytest.fixture
def critical_assessment():
    """Create critical complexity assessment."""
    signals = ComplexitySignals(
        lens_confidence=0.30, files_affected_count=50, call_graph_depth=10,
        circular_dependencies=3, dependency_depth=5, tight_coupling_score=0.9,
        operation_scope='global', ast_complexity=50, criticality_level='critical'
    )
    engine = ComplexityAssessmentEngine()
    return engine.assess_complexity(signals)

# ===== THRESHOLD TESTS =====

def test_trivial_threshold_auto_approve(gate, trivial_assessment):
    """Test trivial operations are auto-approved."""
    decision = gate.evaluate_approval(trivial_assessment, "op_001")
    assert decision.approved is True
    assert decision.requires_confirmation is False
    assert decision.escalated is False

def test_simple_threshold_auto_approve(gate, simple_assessment):
    """Test simple operations are auto-approved."""
    decision = gate.evaluate_approval(simple_assessment, "op_002")
    # Simple may show summary but still approved
    assert decision.approved is True
    assert decision.escalated is False

def test_moderate_threshold_confirmation_request(gate, moderate_assessment):
    """Test moderate operations request confirmation."""
    decision = gate.evaluate_approval(moderate_assessment, "op_003")
    assert decision.approved is False
    assert decision.requires_confirmation is True
    assert decision.escalated is False

def test_complex_threshold_escalation(gate, complex_assessment):
    """Test complex operations are escalated."""
    decision = gate.evaluate_approval(complex_assessment, "op_004")
    assert decision.approved is False
    assert decision.requires_confirmation is True
    assert decision.escalated is True

def test_critical_threshold_executive_summary(gate, critical_assessment):
    """Test critical operations get executive summary."""
    decision = gate.evaluate_approval(critical_assessment, "op_005")
    assert decision.approved is False
    assert decision.requires_confirmation is True
    assert decision.escalated is True

def test_threshold_boundary_crossing(gate):
    """Test boundary crossing detection."""
    # Crossing from simple (0.35) to moderate (0.36)
    result = gate.check_threshold_crossing(0.35, 0.36)
    assert result['crossed_boundary'] is True
    assert result['from_level'] == 'SIMPLE'
    assert result['to_level'] == 'MODERATE'

def test_approval_decision_consistency(gate, moderate_assessment):
    """Test approval decisions are consistent."""
    decision = gate.evaluate_approval(moderate_assessment, "op_006")
    is_consistent = gate.ensure_consistency(decision)
    assert is_consistent is True

def test_fallback_logic_missing_signals(gate):
    """Test fallback when signals are missing."""
    # Create assessment with low confidence
    signals = ComplexitySignals(
        lens_confidence=0.50, files_affected_count=5, call_graph_depth=3,
        circular_dependencies=0, dependency_depth=2, tight_coupling_score=0.2,
        operation_scope='cross_layer', ast_complexity=10, criticality_level='medium'
    )
    engine = ComplexityAssessmentEngine()
    assessment = engine.assess_complexity(signals)
    
    # Manually lower confidence
    assessment.confidence = 0.6
    
    decision = gate.handle_missing_signals(assessment)
    # Should require confirmation as fallback
    assert decision.requires_confirmation is True

# ===== CONFIRMATION REQUEST TESTS =====

def test_confirmation_request_not_needed(gate, trivial_assessment):
    """Test no confirmation request for trivial."""
    decision = gate.evaluate_approval(trivial_assessment, "op_007")
    request = gate.get_confirmation_request(decision, "Single file edit")
    assert request is None

def test_confirmation_request_for_moderate(gate, moderate_assessment):
    """Test confirmation request for moderate."""
    decision = gate.evaluate_approval(moderate_assessment, "op_008")
    request = gate.get_confirmation_request(decision, "Cross-layer change")
    assert request is not None
    assert request.operation_id == "op_008"
    assert request.complexity_level == moderate_assessment.complexity_level

def test_confirmation_request_for_critical(gate, critical_assessment):
    """Test confirmation request for critical."""
    decision = gate.evaluate_approval(critical_assessment, "op_009")
    request = gate.get_confirmation_request(decision, "System-wide refactor")
    assert request is not None
    assert request.suggested_action == "Review escalation details and select approach"

# ===== ALTERNATIVE RECOMMENDATIONS TESTS =====

def test_alternatives_for_complex(gate, complex_assessment):
    """Test alternatives are provided for complex operations."""
    alternatives = [
        {'name': 'Alt1', 'description': 'Phased approach', 'complexity_score': 0.45},
        {'name': 'Alt2', 'description': 'Incremental', 'complexity_score': 0.50},
    ]
    decision = gate.evaluate_approval(complex_assessment, "op_010", alternatives=alternatives)
    assert len(decision.alternatives) > 0
    assert decision.alternatives[0].complexity_score < 0.65

def test_top_k_alternatives_for_critical(gate, critical_assessment):
    """Test top-3 alternatives for critical operations."""
    alternatives = [
        {'name': f'Alt{i}', 'description': f'Approach {i}', 'complexity_score': 0.4 + i*0.1}
        for i in range(5)
    ]
    decision = gate.evaluate_approval(critical_assessment, "op_011", alternatives=alternatives)
    # Should limit to 3 alternatives
    assert len(decision.alternatives) <= 3

# ===== DECISION HISTORY TESTS =====

def test_decision_history_recording(gate, trivial_assessment, moderate_assessment):
    """Test decisions are recorded in history."""
    gate.evaluate_approval(trivial_assessment, "op_012")
    gate.evaluate_approval(moderate_assessment, "op_013")
    
    history = gate.get_decision_history()
    assert len(history) >= 2

def test_decision_history_limit(gate, trivial_assessment):
    """Test history limit works."""
    # Add multiple decisions
    for i in range(15):
        gate.evaluate_approval(trivial_assessment, f"op_{i:03d}")
    
    history = gate.get_decision_history(limit=5)
    assert len(history) == 5

# ===== STATISTICS TESTS =====

def test_approval_statistics(gate, trivial_assessment, moderate_assessment):
    """Test approval statistics."""
    gate.evaluate_approval(trivial_assessment, "op_014")
    gate.evaluate_approval(moderate_assessment, "op_015")
    
    stats = gate.get_approval_statistics()
    assert stats['total_decisions'] >= 2
    assert 'approval_rate' in stats
    assert 'by_complexity_level' in stats

def test_statistics_empty_history(gate):
    """Test statistics with empty history."""
    stats = gate.get_approval_statistics()
    assert stats['total_decisions'] == 0
    assert stats['approval_rate'] == 0.0

# ===== CONSISTENCY VALIDATION TESTS =====

def test_consistency_trivial(gate):
    """Test consistency for trivial."""
    assessment = ComplexityAssessment(
        complexity_score=0.10,
        complexity_level='TRIVIAL',
        signals=None,
        confidence=0.95,
        factors={},
    )
    decision = gate.evaluate_approval(assessment, "op_016")
    assert gate.ensure_consistency(decision) is True

def test_consistency_moderate(gate):
    """Test consistency for moderate."""
    assessment = ComplexityAssessment(
        complexity_score=0.50,
        complexity_level='MODERATE',
        signals=None,
        confidence=0.90,
        factors={},
    )
    decision = gate.evaluate_approval(assessment, "op_017")
    assert gate.ensure_consistency(decision) is True

def test_consistency_complex(gate):
    """Test consistency for complex."""
    assessment = ComplexityAssessment(
        complexity_score=0.75,
        complexity_level='COMPLEX',
        signals=None,
        confidence=0.85,
        factors={},
    )
    decision = gate.evaluate_approval(assessment, "op_018")
    assert gate.ensure_consistency(decision) is True
