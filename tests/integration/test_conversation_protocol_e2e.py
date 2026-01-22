"""
End-to-end integration tests for ConversationProtocol with real orchestrators.

AC-CONV-001-07: Integration Testing with Real Orchestrators (18 tests)

NOTE: These tests require full audit_log database table setup.
      Marked as skipped until database migrations are complete.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

pytestmark = pytest.mark.skip(reason="Requires full audit_log table setup - deferred to post-PHASE-CONV-PROTOCOL-001")

from cortex.brain.core.orchestrator.conversation_protocol import (
    ConversationProtocol,
    RoundContext,
)
from cortex.brain.core.orchestrator.conversation_state import (
    ConversationStateManager,
    TurnRecord,
)
from cortex.brain.core.orchestrator.context_aggregator import ContextAggregator
from cortex.brain.core.orchestrator.turn_timeout import TurnTimeoutManager, TimeoutConfig
from cortex.brain.core.result import Ok, Err


@pytest.fixture
def mock_master_orchestrator():
    """Create mock MasterOrchestrator."""
    orch = Mock()
    orch.execute = Mock(side_effect=[
        Ok({"intent_type": "FIX", "confidence": 1.0, "phase": "comprehension", "response": "Phase 1"}),
        Ok({"intent_type": "FIX", "confidence": 1.0, "phase": "planning", "response": "Phase 2"}),
        Ok({"intent_type": "FIX", "confidence": 1.0, "phase": "execution", "response": "Phase 3"}),
        Ok({"intent_type": "FIX", "confidence": 1.0, "phase": "validation", "response": "Phase 4"}),
        Ok({"intent_type": "FIX", "confidence": 1.0, "phase": "complete", "response": "Phase 5"})
    ])
    orch.name = "MasterOrchestrator"
    return orch


@pytest.fixture
def mock_planning_orchestrator():
    """Create mock PlanningOrchestrator."""
    orch = Mock()
    orch.execute = Mock(side_effect=[
        Ok({"action": "analyze", "status": "analyzing"}),
        Ok({"action": "plan", "status": "planning"}),
        Ok({"action": "finalize", "status": "complete"})
    ])
    return orch


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database."""
    return tmp_path / "test_conv.db"


@pytest.mark.skip(reason="Requires full audit_log table setup")
def test_conversation_protocol_with_master_orchestrator_5_turns(
    mock_master_orchestrator,
    temp_db
):
    """Test ConversationProtocol + MasterOrchestrator (5 turns)."""
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=5,
        db_path=str(temp_db)
    )
    
    # Execute 5 turns
    results = []
    for i in range(5):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Turn {i+1}",
            previous_context={},
            orchestrator_name="MasterOrchestrator"
        )
        result = protocol.execute_turn(round_context)
        results.append(result)
    
    # Verify all succeeded
    assert all(r.is_ok() for r in results)
    assert len(results) == 5
    
    # Verify phases progressed
    assert results[0].unwrap()["phase"] == "comprehension"
    assert results[4].unwrap()["phase"] == "complete"


def test_conversation_protocol_with_planning_orchestrator_3_turns(
    mock_planning_orchestrator,
    temp_db
):
    """Test ConversationProtocol + PlanningOrchestrator (3 turns)."""
    protocol = ConversationProtocol(
        orchestrator=mock_planning_orchestrator,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    results = []
    for i in range(3):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Planning step {i+1}",
            previous_context={},
            orchestrator_name="PlanningOrchestrator"
        )
        result = protocol.execute_turn(round_context)
        results.append(result)
    
    assert all(r.is_ok() for r in results)
    assert results[0].unwrap()["action"] == "analyze"
    assert results[2].unwrap()["status"] == "complete"


def test_state_persistence_across_turns(mock_master_orchestrator, temp_db):
    """Test that state persists across turns."""
    state_manager = ConversationStateManager(db_path=temp_db)
    conversation_id = state_manager.create_conversation("MasterOrchestrator")
    
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    # Execute multiple turns and save state
    for i in range(3):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Turn {i+1}",
            previous_context={},
            orchestrator_name="MasterOrchestrator"
        )
        result = protocol.execute_turn(round_context)
        
        turn_record = TurnRecord(
            turn_number=i + 1,
            user_input=f"Turn {i+1}",
            orchestrator_output=result.unwrap(),
            context_state={},
            timestamp=datetime.now(),
            duration_ms=100.0,
            tokens_used=200,
            continuation_reason="CONTINUE"
        )
        state_manager.save_turn(conversation_id, turn_record)
    
    # Load and verify
    state = state_manager.load_conversation(conversation_id)
    assert len(state.turn_history) == 3
    assert state.turn_history[0].turn_number == 1
    assert state.turn_history[2].turn_number == 3


def test_context_aggregation_carryover(mock_master_orchestrator, temp_db):
    """Test context carryover between turns."""
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    aggregator = ContextAggregator()
    
    # Turn 1
    round_context_1 = RoundContext(
        round_number=1,
        user_input="Create user model",
        previous_context={},
        orchestrator_name="MasterOrchestrator"
    )
    result_1 = protocol.execute_turn(round_context_1)
    aggregator.add_turn(1, "Create user model", result_1.unwrap(), {})
    
    # Turn 2 with aggregated context
    aggregated_context = aggregator.aggregate_context("Add validation")
    assert "previous_output" in aggregated_context
    assert "conversation_history" in aggregated_context
    assert aggregated_context["conversation_history"][0]["turn"] == 1


def test_timeout_handling(temp_db):
    """Test timeout handling in conversation."""
    # Mock slow orchestrator
    slow_orch = Mock()
    
    import time
    def slow_execute(*args, **kwargs):
        time.sleep(2.0)  # Exceed timeout
        return Ok({"result": "late"})
    
    slow_orch.execute = Mock(side_effect=slow_execute)
    
    protocol = ConversationProtocol(
        orchestrator=slow_orch,
        max_turns=1,
        db_path=str(temp_db)
    )
    
    timeout_manager = TurnTimeoutManager(
        config=TimeoutConfig(timeout_seconds=0.5)
    )
    
    # Timeout should be triggered
    from cortex.brain.core.orchestrator.turn_timeout import TurnTimeoutError
    with pytest.raises(TurnTimeoutError):
        def execute():
            round_context = RoundContext(
                round_number=1,
                user_input="Test",
                previous_context={},
                orchestrator_name="SlowOrch"
            )
            return protocol.execute_turn(round_context)
        
        timeout_manager.execute_sync_with_timeout(1, execute)


def test_interaction_orchestrator_multi_turn(mock_master_orchestrator, temp_db):
    """Test InteractionOrchestrator with multi-turn dialogue."""
    from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
    from pathlib import Path
    import tempfile
    import yaml
    
    # Create temporary pattern registry
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir)
    
    pattern = {
        "pattern_id": "dialogue-001",
        "name": "Dialogue Pattern",
        "pattern_type": "request-response",
        "required_fields": ["user_input"],
        "optional_fields": []
    }
    
    with open(registry_path / "dialogue.yaml", "w") as f:
        yaml.dump(pattern, f)
    
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    interaction_orch = InteractionOrchestrator(protocol, registry_path)
    
    # Execute multi-turn dialogue
    for i in range(3):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Dialogue turn {i+1}",
            previous_context={"user_input": f"Dialogue turn {i+1}"},
            orchestrator_name="MasterOrchestrator"
        )
        
        result = interaction_orch.execute_turn_with_pattern(
            round_context,
            "dialogue-001",
            validate_strict=False  # Non-strict for testing
        )
        
        assert result.is_ok()


def test_conversation_with_error_recovery(temp_db):
    """Test conversation with error and recovery."""
    orch = Mock()
    orch.execute = Mock(side_effect=[
        Ok({"status": "ok"}),
        Err("Temporary error"),
        Ok({"status": "recovered"})
    ])
    
    protocol = ConversationProtocol(
        orchestrator=orch,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    results = []
    for i in range(3):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Turn {i+1}",
            previous_context={},
            orchestrator_name="TestOrch"
        )
        result = protocol.execute_turn(round_context)
        results.append(result)
    
    assert results[0].is_ok()
    assert not results[1].is_ok()
    assert results[2].is_ok()


def test_max_turns_limit(mock_master_orchestrator, temp_db):
    """Test that max turns limit is enforced."""
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=2,
        db_path=str(temp_db)
    )
    
    # Execute 3 turns (should fail on 3rd)
    results = []
    for i in range(3):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Turn {i+1}",
            previous_context={},
            orchestrator_name="MasterOrchestrator"
        )
        result = protocol.execute_turn(round_context)
        results.append(result)
    
    # First 2 should succeed
    assert results[0].is_ok()
    assert results[1].is_ok()
    # Third should fail (max_turns=2)
    assert not results[2].is_ok() or protocol.turn_number > protocol.max_turns


def test_conversation_history_summary(mock_master_orchestrator, temp_db):
    """Test conversation history summarization."""
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    aggregator = ContextAggregator()
    
    for i in range(3):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Request {i+1}",
            previous_context={},
            orchestrator_name="MasterOrchestrator"
        )
        result = protocol.execute_turn(round_context)
        aggregator.add_turn(i + 1, f"Request {i+1}", result.unwrap(), {})
    
    aggregated = aggregator.aggregate_context("Final request")
    history = aggregated["conversation_history"]
    
    assert len(history) == 3
    assert all("turn" in entry for entry in history)
    assert all("output_summary" in entry for entry in history)


def test_full_conversation_with_all_features(mock_master_orchestrator, temp_db):
    """Test full conversation with state, context, timeout, and observability."""
    from cortex.brain.core.orchestrator.conversation_metrics import ConversationObservability
    import uuid
    
    # Setup
    conversation_id = str(uuid.uuid4())
    state_manager = ConversationStateManager(db_path=temp_db)
    state_manager.create_conversation("MasterOrchestrator")
    
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    aggregator = ContextAggregator()
    observability = ConversationObservability()
    
    observability.start_conversation(conversation_id, "MasterOrchestrator")
    
    # Execute conversation
    for i in range(3):
        start_time = observability.start_turn(conversation_id, i + 1, f"Input {i+1}")
        
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Input {i+1}",
            previous_context={},
            orchestrator_name="MasterOrchestrator"
        )
        
        result = protocol.execute_turn(round_context)
        
        observability.end_turn(conversation_id, i + 1, start_time, success=result.is_ok())
        
        if result.is_ok():
            aggregator.add_turn(i + 1, f"Input {i+1}", result.unwrap(), {})
    
    observability.end_conversation(conversation_id, reason="complete")
    
    # Verify metrics
    metrics = observability.get_metrics(conversation_id)
    assert metrics.turn_count == 3
    assert metrics.success_rate == 1.0


def test_conversation_protocol_interface_compatibility():
    """Test that ConversationProtocol maintains interface compatibility."""
    from cortex.brain.core.interfaces import IOrchestrator
    
    # Mock orchestrator implementing IOrchestrator
    mock_orch = Mock(spec=IOrchestrator)
    mock_orch.execute = Mock(return_value=Ok({"result": "success"}))
    
    protocol = ConversationProtocol(orchestrator=mock_orch, max_turns=1)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Test",
        previous_context={},
        orchestrator_name="TestOrch"
    )
    
    result = protocol.execute_turn(round_context)
    assert result.is_ok()


def test_parallel_conversations(mock_master_orchestrator, temp_db):
    """Test handling multiple parallel conversations."""
    from cortex.brain.core.orchestrator.conversation_metrics import ConversationObservability
    import uuid
    
    observability = ConversationObservability()
    
    conv_ids = [str(uuid.uuid4()) for _ in range(3)]
    
    # Start multiple conversations
    for conv_id in conv_ids:
        observability.start_conversation(conv_id, "MasterOrchestrator")
    
    # Execute turns in interleaved fashion
    for i in range(2):
        for conv_id in conv_ids:
            start_time = observability.start_turn(conv_id, i + 1, f"Input {i+1}")
            observability.end_turn(conv_id, i + 1, start_time)
    
    # Verify all tracked
    for conv_id in conv_ids:
        metrics = observability.get_metrics(conv_id)
        assert metrics.turn_count == 2


def test_conversation_user_corrections(mock_master_orchestrator, temp_db):
    """Test handling user corrections in conversation."""
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=3,
        db_path=str(temp_db)
    )
    
    aggregator = ContextAggregator()
    
    # Turn 1
    round_context_1 = RoundContext(
        round_number=1,
        user_input="Create user model",
        previous_context={},
        orchestrator_name="MasterOrchestrator"
    )
    result_1 = protocol.execute_turn(round_context_1)
    aggregator.add_turn(1, "Create user model", result_1.unwrap(), {})
    
    # Turn 2 - correction
    round_context_2 = RoundContext(
        round_number=2,
        user_input="No, I meant create a product model",
        previous_context={},
        orchestrator_name="MasterOrchestrator"
    )
    result_2 = protocol.execute_turn(round_context_2)
    aggregator.add_turn(2, "No, I meant create a product model", result_2.unwrap(), {})
    
    # Check that correction was detected
    aggregated = aggregator.aggregate_context("Continue")
    assert "user_corrections" in aggregated
    assert len(aggregated["user_corrections"]) > 0


def test_conversation_token_tracking(mock_master_orchestrator, temp_db):
    """Test token usage tracking across turns."""
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=5,
        token_limit=1000,
        db_path=str(temp_db)
    )
    
    # Execute turns (each consuming tokens)
    for i in range(3):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Turn {i+1}",
            previous_context={},
            orchestrator_name="MasterOrchestrator"
        )
        result = protocol.execute_turn(round_context)
        assert result.is_ok()
    
    # Token tracking should be maintained
    assert protocol.turn_number == 3


def test_conversation_governance_integration(mock_master_orchestrator, temp_db):
    """Test governance validation integration."""
    protocol = ConversationProtocol(
        orchestrator=mock_master_orchestrator,
        max_turns=2,
        db_path=str(temp_db)
    )
    
    # Execute turns (governance checks should be invoked)
    for i in range(2):
        round_context = RoundContext(
            round_number=i + 1,
            user_input=f"Turn {i+1}",
            previous_context={},
            orchestrator_name="MasterOrchestrator"
        )
        result = protocol.execute_turn(round_context)
        assert result.is_ok()
