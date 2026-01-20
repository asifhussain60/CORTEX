"""Integration tests for Stage 2.5 Confirmation Gate."""
import pytest
from src.core.orchestrator.complexity_assessment import ComplexitySignals
from src.orchestrators.core.stage_2_5_gate import (
    Stage25Gate,
    ConfirmationContext,
    ContinuationDecision,
    ConversationProtocolIntegration,
)

# ===== STAGE 2.5 GATE TESTS =====

@pytest.fixture
def gate():
    """Create Stage 2.5 gate."""
    return Stage25Gate()

@pytest.fixture
def integration():
    """Create ConversationProtocol integration."""
    return ConversationProtocolIntegration()

@pytest.fixture
def trivial_signals():
    """Create trivial complexity signals."""
    return ComplexitySignals(
        lens_confidence=0.95, files_affected_count=1, call_graph_depth=1,
        circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
        operation_scope='local', ast_complexity=2, criticality_level='low'
    )

@pytest.fixture
def moderate_signals():
    """Create moderate complexity signals."""
    return ComplexitySignals(
        lens_confidence=0.70, files_affected_count=5, call_graph_depth=4,
        circular_dependencies=0, dependency_depth=2, tight_coupling_score=0.3,
        operation_scope='cross_layer', ast_complexity=15, criticality_level='medium'
    )

@pytest.fixture
def critical_signals():
    """Create critical complexity signals."""
    return ComplexitySignals(
        lens_confidence=0.30, files_affected_count=50, call_graph_depth=10,
        circular_dependencies=3, dependency_depth=5, tight_coupling_score=0.9,
        operation_scope='global', ast_complexity=50, criticality_level='critical'
    )

# ===== STAGE 2.5 GATE EVALUATION TESTS =====

def test_stage_2_5_insertion_after_routing(gate, trivial_signals):
    """Test Stage 2.5 is positioned after routing (Stage 2)."""
    decision = gate.evaluate(
        operation_id="op_001",
        lens_confidence=0.95,
        signals=trivial_signals,
    )
    # Trivial should auto-approve, no confirmation needed
    assert decision.continue_execution is True
    assert decision.is_confirmation_gate is False

def test_continuation_decision_confirmation_reason(gate, moderate_signals):
    """Test continuation decision includes confirmation reason."""
    decision = gate.evaluate(
        operation_id="op_002",
        lens_confidence=0.70,
        signals=moderate_signals,
    )
    # Moderate should need confirmation
    assert decision.continue_execution is False
    assert decision.confirmation_reason is not None
    assert "Moderate" in decision.confirmation_reason or "confirmation" in decision.confirmation_reason.lower()

def test_confirmation_context_dataclass_structure(gate, moderate_signals):
    """Test confirmation context has required structure."""
    decision = gate.evaluate(
        operation_id="op_003",
        lens_confidence=0.70,
        signals=moderate_signals,
        user_intent="fix_bug",
        affected_files=["file1.py", "file2.py"],
    )
    
    context = decision.confirmation_context
    assert context is not None
    assert context.operation_id == "op_003"
    assert context.lens_confidence == 0.70
    assert context.user_intent == "fix_bug"
    assert len(context.affected_files) == 2
    assert context.reasons  # Should have reasons
    assert context.confidence > 0.0

def test_turn_execution_with_confirmation_gate(gate, trivial_signals):
    """Test turn execution flow through confirmation gate."""
    decision = gate.evaluate(
        operation_id="op_004",
        lens_confidence=0.95,
        signals=trivial_signals,
    )
    
    # Auto-approved operation should continue
    assert isinstance(decision, ContinuationDecision)
    assert decision.continue_execution is True
    assert "Auto-approved" in decision.reason

def test_per_turn_gate_isolation(gate):
    """Test each turn is evaluated independently."""
    signals1 = ComplexitySignals(
        lens_confidence=0.95, files_affected_count=1, call_graph_depth=1,
        circular_dependencies=0, dependency_depth=1, tight_coupling_score=0.0,
        operation_scope='local', ast_complexity=2, criticality_level='low'
    )
    signals2 = ComplexitySignals(
        lens_confidence=0.50, files_affected_count=20, call_graph_depth=8,
        circular_dependencies=2, dependency_depth=4, tight_coupling_score=0.7,
        operation_scope='global', ast_complexity=40, criticality_level='high'
    )
    
    d1 = gate.evaluate("op_001", 0.95, signals1)
    d2 = gate.evaluate("op_002", 0.50, signals2)
    
    # Each decision should be independent
    assert d1.continue_execution is True
    assert d2.continue_execution is False
    assert d1.confirmation_context is None
    assert d2.confirmation_context is not None

def test_gate_does_not_block_low_complexity_ops(gate, trivial_signals):
    """Test gate doesn't block trivial/simple operations."""
    decision = gate.evaluate(
        operation_id="op_005",
        lens_confidence=0.95,
        signals=trivial_signals,
    )
    
    # Low complexity should proceed
    assert decision.continue_execution is True
    assert not decision.is_confirmation_gate

# ===== CONFIRMATION CONTEXT TESTS =====

def test_confirmation_context_with_alternatives(gate, critical_signals):
    """Test confirmation context includes alternatives."""
    alternatives = [
        {'name': 'Alt1', 'description': 'Phased approach', 'complexity_score': 0.45},
        {'name': 'Alt2', 'description': 'Incremental', 'complexity_score': 0.50},
    ]
    
    decision = gate.evaluate(
        operation_id="op_006",
        lens_confidence=0.30,
        signals=critical_signals,
        alternatives=alternatives,
    )
    
    context = decision.confirmation_context
    assert context is not None
    assert len(context.alternatives) > 0

def test_confirmation_context_reasons_populated(gate, moderate_signals):
    """Test confirmation context has reasons populated."""
    decision = gate.evaluate(
        operation_id="op_007",
        lens_confidence=0.70,
        signals=moderate_signals,
    )
    
    context = decision.confirmation_context
    assert context is not None
    assert len(context.reasons) > 0

# ===== RECORD CONFIRMATION TESTS =====

def test_record_confirmation_decision(gate, moderate_signals):
    """Test recording confirmation decision."""
    gate.evaluate(
        operation_id="op_008",
        lens_confidence=0.70,
        signals=moderate_signals,
    )
    
    gate.record_confirmation("op_008", confirmed=True)
    assert gate.should_bypass_confirmation("op_008") is True

def test_bypass_already_confirmed(gate, moderate_signals):
    """Test operations can bypass confirmation if already confirmed."""
    gate.evaluate("op_009", 0.70, moderate_signals)
    gate.record_confirmation("op_009", confirmed=True)
    
    # Should bypass confirmation on retry
    assert gate.should_bypass_confirmation("op_009") is True

# ===== PROTOCOL INTEGRATION TESTS =====

def test_protocol_integration_initialization(integration):
    """Test ConversationProtocol integration initializes."""
    assert integration.stage_2_5 is not None
    assert isinstance(integration.stage_2_5, Stage25Gate)

def test_execute_turn_with_confirmation_gate(integration):
    """Test turn execution through integration."""
    routing_decision = {
        'alternatives': [
            {'name': 'Alt1', 'complexity_score': 0.4}
        ]
    }
    stage_2_context = {
        'lens_confidence': 0.95,
        'intent': 'simple_edit',
        'affected_files': ['file1.py'],
        'files_affected_count': 1,
        'call_graph_depth': 1,
        'circular_dependencies': 0,
        'dependency_depth': 1,
        'tight_coupling_score': 0.0,
        'operation_scope': 'local',
        'ast_complexity': 2,
        'criticality_level': 'low',
    }
    
    decision = integration.execute_turn_with_confirmation_gate(
        operation_id="op_010",
        routing_decision=routing_decision,
        stage_2_context=stage_2_context,
    )
    
    assert isinstance(decision, ContinuationDecision)
    assert decision.continue_execution is True  # Auto-approved trivial

def test_handle_confirmation_response_approved(integration):
    """Test handling approved confirmation response."""
    decision = integration.handle_confirmation_response(
        operation_id="op_011",
        confirmed=True,
    )
    
    assert decision.continue_execution is True
    assert "confirmed" in decision.reason.lower()

def test_handle_confirmation_response_rejected(integration):
    """Test handling rejected confirmation response."""
    decision = integration.handle_confirmation_response(
        operation_id="op_012",
        confirmed=False,
    )
    
    assert decision.continue_execution is False
    assert "rejected" in decision.reason.lower()

def test_signals_built_from_stage_2_context(integration):
    """Test signals are properly built from Stage 2 context."""
    stage_2_context = {
        'lens_confidence': 0.75,
        'files_affected_count': 5,
        'call_graph_depth': 3,
        'circular_dependencies': 1,
        'dependency_depth': 2,
        'tight_coupling_score': 0.4,
        'operation_scope': 'cross_layer',
        'ast_complexity': 12,
        'criticality_level': 'medium',
    }
    
    signals = ConversationProtocolIntegration._build_signals_from_stage_2(stage_2_context)
    
    assert signals.lens_confidence == 0.75
    assert signals.files_affected_count == 5
    assert signals.operation_scope == 'cross_layer'
    assert signals.criticality_level == 'medium'

def test_integration_statistics(integration):
    """Test integration statistics."""
    stage_2_context = {
        'lens_confidence': 0.95,
        'files_affected_count': 1,
        'call_graph_depth': 1,
        'circular_dependencies': 0,
        'dependency_depth': 1,
        'tight_coupling_score': 0.0,
        'operation_scope': 'local',
        'ast_complexity': 2,
        'criticality_level': 'low',
    }
    
    # Execute multiple times
    for i in range(3):
        integration.execute_turn_with_confirmation_gate(
            operation_id=f"op_{i:03d}",
            routing_decision={},
            stage_2_context=stage_2_context,
        )
    
    stats = integration.get_integration_statistics()
    assert stats['total_evaluations'] >= 3
    assert 'confirmation_rate' in stats

# ===== EDGE CASE TESTS =====

def test_complex_operation_escalation(gate, critical_signals):
    """Test complex operation gets escalated."""
    decision = gate.evaluate(
        operation_id="op_013",
        lens_confidence=0.30,
        signals=critical_signals,
        alternatives=[
            {'name': 'Alt1', 'complexity_score': 0.5}
        ]
    )
    
    assert decision.continue_execution is False
    assert decision.is_confirmation_gate is True
    assert decision.confirmation_context.alternatives is not None

def test_execution_count_incremented(gate, trivial_signals):
    """Test execution counter increments."""
    initial_count = gate.execution_count
    
    gate.evaluate("op_014", 0.95, trivial_signals)
    gate.evaluate("op_015", 0.95, trivial_signals)
    
    assert gate.execution_count == initial_count + 2

def test_confirmation_context_timestamp(gate, moderate_signals):
    """Test confirmation context has timestamp."""
    decision = gate.evaluate(
        operation_id="op_016",
        lens_confidence=0.70,
        signals=moderate_signals,
    )
    
    assert decision.confirmation_context.timestamp is not None
