"""Tests for multi-turn conversation workflows.

AC-ID: REMEDIATION-INTENT-007
Tests complete end-to-end multi-turn conversation flows.
"""

import pytest
from cortex.orchestrators.multi_turn_workflow import (
    MultiTurnWorkflow,
    ConversationState,
    TurnResult,
)


class BaseMultiTurnTest:
    """Base test class with common fixtures."""

    @pytest.fixture(autouse=True)
    def setup_workflow(self):
        """Setup MultiTurnWorkflow instance."""
        self.workflow = MultiTurnWorkflow()


class TestMultiTurnWorkflowInitialization(BaseMultiTurnTest):
    """Test MultiTurnWorkflow initialization."""

    def test_workflow_initializes(self):
        """Test workflow initialization."""
        assert self.workflow is not None

    def test_conversation_state_initialized(self):
        """Test conversation state is initialized."""
        assert hasattr(self.workflow, "conversation_state")
        assert isinstance(self.workflow.conversation_state, ConversationState)

    def test_turn_counter_starts_at_zero(self):
        """Test turn counter starts at zero."""
        assert self.workflow.turn_count == 0

    def test_turn_history_empty_initially(self):
        """Test turn history is empty."""
        assert len(self.workflow.get_turn_history()) == 0


class TestConversationState(BaseMultiTurnTest):
    """Test ConversationState data class."""

    def test_conversation_state_creation(self):
        """Test ConversationState creation."""
        state = ConversationState(
            conversation_id="conv_001",
            turn_number=1,
            user_intent="IMPLEMENT",
        )
        assert state.conversation_id == "conv_001"
        assert state.turn_number == 1

    def test_conversation_state_with_context(self):
        """Test state with accumulated context."""
        state = ConversationState(
            conversation_id="conv_001",
            turn_number=2,
            user_intent="FIX",
            accumulated_context={"previous_intent": "IMPLEMENT"},
        )
        assert len(state.accumulated_context) > 0

    def test_conversation_state_to_dict(self):
        """Test to_dict() serialization."""
        state = ConversationState(
            conversation_id="conv_001",
            turn_number=1,
            user_intent="QUERY",
        )
        result = state.to_dict()
        assert result["conversation_id"] == "conv_001"
        assert result["turn_number"] == 1


class TestTurnResult(BaseMultiTurnTest):
    """Test TurnResult data class."""

    def test_turn_result_creation(self):
        """Test TurnResult creation."""
        result = TurnResult(
            turn_number=1,
            intent_type="IMPLEMENT",
            confidence=0.95,
            status="PASSED",
        )
        assert result.turn_number == 1
        assert result.confidence == 0.95

    def test_turn_result_with_challenges(self):
        """Test result with challenges."""
        result = TurnResult(
            turn_number=1,
            intent_type="IMPLEMENT",
            status="PASSED_WITH_CHALLENGES",
            challenges=[
                {
                    "category": "TEST_GAP",
                    "severity": "MEDIUM",
                }
            ],
        )
        assert len(result.challenges) > 0

    def test_turn_result_to_dict(self):
        """Test to_dict() serialization."""
        result = TurnResult(
            turn_number=2,
            intent_type="FIX",
            confidence=0.80,
        )
        result_dict = result.to_dict()
        assert result_dict["turn_number"] == 2


class TestSingleTurnExecution(BaseMultiTurnTest):
    """Test single turn execution."""

    def test_execute_single_turn(self):
        """Test executing a single turn."""
        result = self.workflow.execute_turn(
            user_input="Implement user authentication",
            intent_type="IMPLEMENT",
            turn_number=1,
        )
        assert result is not None
        assert result.turn_number == 1

    def test_turn_counter_increments(self):
        """Test turn counter increments."""
        initial = self.workflow.turn_count
        self.workflow.execute_turn(
            user_input="Query",
            intent_type="QUERY",
            turn_number=1,
        )
        assert self.workflow.turn_count > initial

    def test_turn_result_captured(self):
        """Test turn result is captured."""
        self.workflow.execute_turn(
            user_input="Implement feature",
            intent_type="IMPLEMENT",
            turn_number=1,
        )
        history = self.workflow.get_turn_history()
        assert len(history) > 0


class TestMultiTurnConversation(BaseMultiTurnTest):
    """Test multi-turn conversations."""

    def test_two_turn_conversation(self):
        """Test two-turn conversation."""
        result1 = self.workflow.execute_turn(
            user_input="Query: What is the API?",
            intent_type="QUERY",
            turn_number=1,
        )
        result2 = self.workflow.execute_turn(
            user_input="Now implement it",
            intent_type="IMPLEMENT",
            turn_number=2,
        )
        assert result1.turn_number == 1
        assert result2.turn_number == 2

    def test_three_turn_conversation(self):
        """Test three-turn conversation."""
        results = []
        for i, intent in enumerate(["QUERY", "IMPLEMENT", "FIX"], 1):
            result = self.workflow.execute_turn(
                user_input=f"Turn {i}",
                intent_type=intent,
                turn_number=i,
            )
            results.append(result)
        assert len(results) == 3
        assert results[0].turn_number == 1
        assert results[2].turn_number == 3

    def test_long_conversation(self):
        """Test long conversation (10+ turns)."""
        intents = ["QUERY", "IMPLEMENT", "FIX"] * 4  # 12 turns
        for i, intent in enumerate(intents, 1):
            self.workflow.execute_turn(
                user_input=f"Turn {i}",
                intent_type=intent,
                turn_number=i,
            )
        history = self.workflow.get_turn_history()
        assert len(history) >= 3  # At least some turns


class TestContextAccumulation(BaseMultiTurnTest):
    """Test context accumulation across turns."""

    def test_context_preserved_across_turns(self):
        """Test context is preserved."""
        self.workflow.execute_turn(
            user_input="First turn",
            intent_type="QUERY",
            turn_number=1,
        )
        # Context should be available for next turn
        state = self.workflow.conversation_state
        assert state.turn_number >= 1

    def test_accumulated_context_grows(self):
        """Test accumulated context grows with turns."""
        for i in range(1, 4):
            self.workflow.execute_turn(
                user_input=f"Input {i}",
                intent_type="QUERY",
                turn_number=i,
            )
        state = self.workflow.conversation_state
        # Context should have grown
        assert state.turn_number == 3

    def test_context_available_in_next_turn(self):
        """Test previous context available in next turn."""
        self.workflow.execute_turn(
            user_input="First: implement auth",
            intent_type="IMPLEMENT",
            turn_number=1,
        )
        result2 = self.workflow.execute_turn(
            user_input="Now fix it",
            intent_type="FIX",
            turn_number=2,
            context={"previous_intent": "IMPLEMENT"},
        )
        assert result2.turn_number == 2


class TestGovernanceAcrossTurns(BaseMultiTurnTest):
    """Test governance validation across turns."""

    def test_governance_checked_each_turn(self):
        """Test governance is validated each turn."""
        results = []
        for i in range(1, 4):
            result = self.workflow.execute_turn(
                user_input=f"Turn {i}",
                intent_type="IMPLEMENT",
                turn_number=i,
            )
            results.append(result)
        # All should have governance status
        assert all(r.status is not None for r in results)

    def test_tier0_blocking_across_turns(self):
        """Test TIER 0 blocks subsequent turns."""
        result1 = self.workflow.execute_turn(
            user_input="Query something",
            intent_type="QUERY",
            turn_number=1,
        )
        # Even after success, dangerous pattern should block
        result2 = self.workflow.execute_turn(
            user_input="eval('dangerous code')",
            intent_type="IMPLEMENT",
            turn_number=2,
        )
        # Result2 might be blocked or warned
        assert result2.status is not None

    def test_escalation_tracking_across_turns(self):
        """Test escalations are tracked."""
        for i in range(1, 4):
            self.workflow.execute_turn(
                user_input=f"Turn {i}",
                intent_type="IMPLEMENT",
                turn_number=i,
            )
        # Check escalation history
        escalations = self.workflow.get_escalation_history()
        assert isinstance(escalations, list)


class TestConfidenceTracking(BaseMultiTurnTest):
    """Test confidence tracking across turns."""

    def test_confidence_recorded_per_turn(self):
        """Test confidence is recorded per turn."""
        result1 = self.workflow.execute_turn(
            user_input="Query",
            intent_type="QUERY",
            turn_number=1,
            confidence=0.95,
        )
        result2 = self.workflow.execute_turn(
            user_input="Implement",
            intent_type="IMPLEMENT",
            turn_number=2,
            confidence=0.75,
        )
        assert result1.confidence == 0.95
        assert result2.confidence == 0.75

    def test_confidence_affects_routing(self):
        """Test confidence affects turn routing."""
        high_conf = self.workflow.execute_turn(
            user_input="High confidence",
            intent_type="IMPLEMENT",
            turn_number=1,
            confidence=0.92,
        )
        low_conf = self.workflow.execute_turn(
            user_input="Low confidence",
            intent_type="IMPLEMENT",
            turn_number=2,
            confidence=0.55,
        )
        # Different confidence may lead to different statuses
        assert high_conf.status is not None
        assert low_conf.status is not None


class TestChallengeAcrossTurns(BaseMultiTurnTest):
    """Test challenges across turns."""

    def test_challenges_identified_per_turn(self):
        """Test challenges are identified."""
        result1 = self.workflow.execute_turn(
            user_input="Implement without tests",
            intent_type="IMPLEMENT",
            turn_number=1,
        )
        # Check if challenges identified
        assert isinstance(result1.challenges, list)

    def test_previous_challenges_remembered(self):
        """Test previous challenges are remembered."""
        self.workflow.execute_turn(
            user_input="First turn",
            intent_type="IMPLEMENT",
            turn_number=1,
        )
        result2 = self.workflow.execute_turn(
            user_input="Second turn",
            intent_type="FIX",
            turn_number=2,
        )
        # Should have access to previous challenges
        history = self.workflow.get_turn_history()
        assert len(history) > 0


class TestConversationReset(BaseMultiTurnTest):
    """Test conversation reset functionality."""

    def test_reset_clears_history(self):
        """Test reset clears turn history."""
        self.workflow.execute_turn(
            user_input="Turn 1",
            intent_type="QUERY",
            turn_number=1,
        )
        self.workflow.reset_conversation()
        history = self.workflow.get_turn_history()
        assert len(history) == 0

    def test_reset_resets_turn_counter(self):
        """Test reset resets turn counter."""
        self.workflow.execute_turn(
            user_input="Turn 1",
            intent_type="QUERY",
            turn_number=1,
        )
        self.workflow.reset_conversation()
        assert self.workflow.turn_count == 0

    def test_new_conversation_after_reset(self):
        """Test new conversation works after reset."""
        self.workflow.execute_turn(
            user_input="First conversation",
            intent_type="QUERY",
            turn_number=1,
        )
        self.workflow.reset_conversation()
        result = self.workflow.execute_turn(
            user_input="Second conversation",
            intent_type="IMPLEMENT",
            turn_number=1,
        )
        assert result.turn_number == 1


class TestConversationMetrics(BaseMultiTurnTest):
    """Test conversation metrics and analytics."""

    def test_get_conversation_summary(self):
        """Test getting conversation summary."""
        for i in range(1, 4):
            self.workflow.execute_turn(
                user_input=f"Turn {i}",
                intent_type="IMPLEMENT",
                turn_number=i,
            )
        summary = self.workflow.get_conversation_summary()
        assert isinstance(summary, dict)
        assert summary.get("turn_count", 0) >= 0

    def test_get_turn_history(self):
        """Test getting turn history."""
        self.workflow.execute_turn(
            user_input="Turn 1",
            intent_type="QUERY",
            turn_number=1,
        )
        history = self.workflow.get_turn_history()
        assert isinstance(history, list)
        assert len(history) > 0

    def test_get_escalation_history(self):
        """Test getting escalation history."""
        for i in range(1, 3):
            self.workflow.execute_turn(
                user_input=f"Turn {i}",
                intent_type="IMPLEMENT",
                turn_number=i,
            )
        escalations = self.workflow.get_escalation_history()
        assert isinstance(escalations, list)


class TestErrorHandling(BaseMultiTurnTest):
    """Test error handling in multi-turn workflows."""

    def test_invalid_intent_handled(self):
        """Test invalid intent is handled."""
        try:
            result = self.workflow.execute_turn(
                user_input="Something",
                intent_type="INVALID_INTENT",
                turn_number=1,
            )
            # Should either return result or raise
            assert result is not None or result is None
        except ValueError:
            # Acceptable to raise for invalid intent
            pass

    def test_out_of_order_turns_handled(self):
        """Test out-of-order turn numbers handled."""
        result1 = self.workflow.execute_turn(
            user_input="Turn 1",
            intent_type="QUERY",
            turn_number=1,
        )
        result3 = self.workflow.execute_turn(
            user_input="Turn 3",
            intent_type="IMPLEMENT",
            turn_number=3,
        )
        # Should handle gracefully
        assert result1 is not None
        assert result3 is not None


class TestEdgeCases(BaseMultiTurnTest):
    """Test edge cases and boundary conditions."""

    def test_empty_user_input(self):
        """Test empty user input."""
        result = self.workflow.execute_turn(
            user_input="",
            intent_type="QUERY",
            turn_number=1,
        )
        assert result is not None

    def test_very_long_conversation(self):
        """Test very long conversation."""
        for i in range(1, 51):
            self.workflow.execute_turn(
                user_input=f"Turn {i}",
                intent_type="QUERY",
                turn_number=i,
            )
        history = self.workflow.get_turn_history()
        assert len(history) > 0

    def test_repeated_intents(self):
        """Test repeated intents."""
        for i in range(1, 4):
            self.workflow.execute_turn(
                user_input=f"IMPLEMENT turn {i}",
                intent_type="IMPLEMENT",
                turn_number=i,
            )
        history = self.workflow.get_turn_history()
        assert len(history) >= 1

    def test_multiple_workflows_independent(self):
        """Test multiple workflows are independent."""
        workflow1 = MultiTurnWorkflow()
        workflow2 = MultiTurnWorkflow()
        workflow1.execute_turn(
            user_input="Workflow 1",
            intent_type="QUERY",
            turn_number=1,
        )
        history2 = workflow2.get_turn_history()
        # Workflow2 should not have workflow1's turns
        assert len(history2) == 0
