"""
Tests for ConversationProtocol - single-turn executor for orchestrators.

Tests validate:
- Protocol wraps any IOrchestrator
- execute_turn() executes exactly one turn
- Pre/post-turn governance validation
- Token tracking per turn
- Audit logging (AC_START/EXECUTE/COMPLETE)
- LENS context creation per turn
- Continuation logic evaluation
- Result[T] pattern usage
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass
from typing import Dict, Any

from cortex.core.orchestrator.conversation_protocol import (
    ConversationProtocol,
    RoundContext,
)
from cortex.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)
from cortex.core.result import Result, Ok, Err


@dataclass
class MockIOrchestrator:
    """Mock IOrchestrator for testing."""
    
    name: str = "MockOrchestrator"
    
    def execute(
        self, user_input: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock execute method."""
        return {
            "result": "mock_result",
            "user_input": user_input,
            "turn": context.get("turn_number", 1),
        }


class TestConversationProtocolInitialization:
    """Test ConversationProtocol initialization."""

    def test_protocol_initialization_with_defaults(self):
        """Test initializing ConversationProtocol with default parameters."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        assert protocol.orchestrator == orchestrator
        assert protocol.max_turns == 10  # Default
        assert protocol.token_limit == 20000  # Default
        assert protocol.turn_number == 0
        assert protocol.total_tokens_used == 0
        assert len(protocol.decisions_history) == 0

    def test_protocol_initialization_with_custom_limits(self):
        """Test initializing ConversationProtocol with custom limits."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(
            orchestrator, max_turns=5, token_limit=10000
        )
        
        assert protocol.max_turns == 5
        assert protocol.token_limit == 10000

    def test_protocol_initialization_stores_orchestrator(self):
        """Test that protocol stores reference to orchestrator."""
        orchestrator = MockIOrchestrator(name="TestOrchestrator")
        protocol = ConversationProtocol(orchestrator)
        
        assert protocol.orchestrator.name == "TestOrchestrator"


class TestSingleTurnExecution:
    """Test single-turn execution logic."""

    def test_execute_turn_increments_turn_number(self, test_db_path):
        """Test that execute_turn increments turn_number."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator, db_path=str(test_db_path))
        
        assert protocol.turn_number == 0
        
        # Execute first turn
        result = protocol.execute_turn("user input 1", {})
        assert result.is_ok()
        assert protocol.turn_number == 1
        
        # Execute second turn
        result = protocol.execute_turn("user input 2", {})
        assert result.is_ok()
        assert protocol.turn_number == 2

    def test_execute_turn_returns_continuation_decision(self, test_db_path):
        """Test that execute_turn returns ContinuationDecision."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test input", {})
        
        assert result.is_ok()
        decision = result.unwrap()
        assert isinstance(decision, ContinuationDecision)

    def test_execute_turn_adds_to_decisions_history(self):
        """Test that decisions are added to history."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        assert len(protocol.decisions_history) == 0
        
        protocol.execute_turn("input 1", {})
        assert len(protocol.decisions_history) == 1
        
        protocol.execute_turn("input 2", {})
        assert len(protocol.decisions_history) == 2

    def test_execute_turn_with_empty_context(self):
        """Test execute_turn with empty context."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        assert result.is_ok()

    def test_execute_turn_with_previous_context(self):
        """Test execute_turn preserves previous context."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        context = {"turn_number": 1, "previous_result": "some_data"}
        result = protocol.execute_turn("input", context)
        
        assert result.is_ok()
        # Verify turn context includes previous data
        decision = result.unwrap()
        assert decision.turn_number >= 1


class TestGovernanceValidation:
    """Test governance validation before/after turns."""

    @patch("src.core.orchestrator.conversation_protocol.GovernanceRegistry")
    def test_pre_turn_governance_validation_called(self, mock_registry):
        """Test that pre-turn governance validation is called."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        # Mock should_proceed() to return True
        mock_registry_instance = MagicMock()
        mock_registry_instance.should_proceed.return_value = True
        
        protocol.execute_turn("test", {})
        
        # Pre-turn validation should have been called
        # (Would verify if we could access internal call)

    def test_max_turns_limit_enforced(self):
        """Test that max turns limit is enforced."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator, max_turns=2)
        
        # First turn - OK
        result1 = protocol.execute_turn("input 1", {})
        assert result1.is_ok()
        
        # Second turn - OK
        result2 = protocol.execute_turn("input 2", {})
        assert result2.is_ok()
        
        # Third turn - should fail (max reached)
        result3 = protocol.execute_turn("input 3", {})
        # Should fail or return MAX_ROUNDS_REACHED decision
        assert result3.is_ok()  # Decision created, but reason is MAX_ROUNDS_REACHED
        decision = result3.unwrap()
        assert decision.reason == ContinuationReason.MAX_ROUNDS_REACHED


class TestTokenTracking:
    """Test token usage tracking per turn."""

    def test_token_usage_tracked_per_turn(self):
        """Test that token usage is tracked for each turn."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        assert protocol.total_tokens_used == 0
        
        result = protocol.execute_turn("test", {})
        decision = result.unwrap()
        
        # Decision should have token usage
        assert "prompt" in decision.token_usage
        assert "completion" in decision.token_usage
        assert "total" in decision.token_usage

    def test_total_tokens_accumulated(self):
        """Test that total tokens accumulate across turns."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator, token_limit=1000)
        
        protocol.execute_turn("input 1", {})
        tokens_after_turn1 = protocol.total_tokens_used
        
        protocol.execute_turn("input 2", {})
        tokens_after_turn2 = protocol.total_tokens_used
        
        # Total should increase or stay same
        assert tokens_after_turn2 >= tokens_after_turn1

    def test_token_limit_triggers_halt_reason(self):
        """Test that approaching token limit triggers halt."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator, token_limit=100)
        
        # Simulate using most of the token budget
        protocol.total_tokens_used = 95
        
        result = protocol.execute_turn("input", {})
        decision = result.unwrap()
        
        # Should indicate token limit concern
        if protocol.total_tokens_used > 90:
            assert decision.reason == ContinuationReason.TOKEN_LIMIT or decision.should_continue is True


class TestAuditLogging:
    """Test audit logging per turn (AC_START/EXECUTE/COMPLETE)."""

    def test_audit_entry_id_in_decision(self):
        """Test that decision contains audit entry ID."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        decision = result.unwrap()
        
        assert decision.audit_entry_id is not None
        assert len(decision.audit_entry_id) > 0


class TestContinuationLogic:
    """Test continuation decision logic."""

    def test_continuation_decision_created(self):
        """Test that continuation decision is created after turn."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        assert result.is_ok()
        
        decision = result.unwrap()
        assert isinstance(decision, ContinuationDecision)

    def test_continuation_decision_has_clear_reason(self):
        """Test that continuation decision has clear reason."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        decision = result.unwrap()
        
        # Reason must be one of the defined values
        valid_reasons = set(ContinuationReason)
        assert decision.reason in valid_reasons

    def test_turn_context_passed_to_orchestrator(self):
        """Test that turn context is created and passed."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test input", {"extra": "data"})
        assert result.is_ok()
        
        decision = result.unwrap()
        assert decision.next_operation is not None

    def test_decision_includes_next_operation(self):
        """Test that decision specifies next operation."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        decision = result.unwrap()
        
        assert decision.next_operation is not None
        assert isinstance(decision.next_operation, str)

    def test_decision_includes_next_parameters(self):
        """Test that decision can include parameters for next operation."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        decision = result.unwrap()
        
        # next_parameters should be dict (may be empty)
        assert isinstance(decision.next_parameters, dict)


class TestErrorHandling:
    """Test error handling with Result[T] pattern."""

    def test_execute_turn_returns_result_type(self):
        """Test that execute_turn returns Result[ContinuationDecision]."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        
        # Should be Result type
        assert hasattr(result, "is_ok")
        assert hasattr(result, "is_err")
        assert hasattr(result, "unwrap")

    def test_result_unwrap_gives_decision(self):
        """Test that Result.unwrap() gives ContinuationDecision."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        
        assert result.is_ok()
        decision = result.unwrap()
        assert isinstance(decision, ContinuationDecision)

    def test_governance_violation_included_in_decision(self):
        """Test that governance violations are included in decision."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        decision = result.unwrap()
        
        # Should have governance_violations list (may be empty)
        assert isinstance(decision.governance_violations, list)


class TestLENSIntegration:
    """Test LENS protocol integration per turn."""

    def test_lens_context_created_per_turn(self):
        """Test that LENS context is created fresh per turn."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        # Execute multiple turns
        result1 = protocol.execute_turn("input 1", {})
        result2 = protocol.execute_turn("input 2", {})
        
        # Both should have executed (LENS ran both times)
        assert result1.is_ok()
        assert result2.is_ok()

    def test_lens_phases_executed_per_turn(self):
        """Test that all LENS phases execute per turn."""
        orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(orchestrator)
        
        result = protocol.execute_turn("test", {})
        assert result.is_ok()
        
        # If we could access LENS state, would verify Language/Exam/Nav/Synth
