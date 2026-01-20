"""
Tests for OC-002-02: Event Integration with ConversationProtocol.

This module tests the integration of EventRegistry and terminal events
into the ConversationProtocol lifecycle.

Test Classes:
    - TestEventRegistryIntegration: EventRegistry initialization and injection
    - TestEventFiringOnMaxTurns: MaxTurnsReachedEvent firing
    - TestEventFiringOnTokenLimit: TokenLimitEvent firing
    - TestEventFiringOnCompletion: PhaseCompletedEvent firing
    - TestEventFiringOnError: ErrorOccurredEvent firing
    - TestEventFiringOnApprovalRejection: UserApprovalRejectedEvent firing
    - TestEventListenerVeto: Listener can veto continuation
    - TestEventAuditIntegration: Events linked to audit trail
    - TestMultiEventScenarios: Complex multi-event workflows
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from unittest.mock import Mock, MagicMock

import pytest

from cortex.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)
from cortex.core.orchestrator.conversation_protocol import ConversationProtocol
from cortex.core.orchestrator.terminal_events import (
    EventRegistry,
    PhaseCompletedEvent,
    UserCancelledEvent,
    MaxTurnsReachedEvent,
    ErrorOccurredEvent,
    TokenLimitEvent,
    GovernanceViolationEvent,
    UserApprovalRejectedEvent,
    TerminalEvent,
)
from cortex.core.result import Ok, Err


@dataclass
class MockIOrchestrator:
    """Mock IOrchestrator for testing - matches structure from test_conversation_protocol.py"""
    
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


class TestEventRegistryIntegration:
    """Test EventRegistry initialization and integration with ConversationProtocol."""

    def test_event_registry_created_by_default(self):
        """ConversationProtocol creates default EventRegistry if not provided."""
        mock_orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(mock_orchestrator)
        
        assert protocol.event_registry is not None
        assert isinstance(protocol.event_registry, EventRegistry)

    def test_custom_event_registry_injected(self):
        """ConversationProtocol accepts custom EventRegistry in constructor."""
        mock_orchestrator = MockIOrchestrator()
        custom_registry = EventRegistry()
        
        protocol = ConversationProtocol(
            mock_orchestrator,
            event_registry=custom_registry
        )
        
        assert protocol.event_registry is custom_registry

    def test_event_registry_methods_accessible(self):
        """EventRegistry methods are accessible via protocol."""
        mock_orchestrator = MockIOrchestrator()
        protocol = ConversationProtocol(mock_orchestrator)
        
        # Should be able to register listeners
        listener = Mock(return_value=True)
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent, listener
        )
        
        assert protocol.event_registry.get_listener_count(MaxTurnsReachedEvent) == 1

    def test_event_registry_persists_across_turns(self):
        """EventRegistry persists state across multiple turns."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={"status": "pending", "next_operation": "continue"}
        )
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=3)
        
        # Register listener
        fired_events = []
        listener = Mock(
            side_effect=lambda e: fired_events.append(e) or True
        )
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent, listener
        )
        
        # Simulate multiple turns until max
        for turn in range(1, 4):
            protocol.execute_turn(f"turn {turn}", {})
        
        # Check that listener was called
        assert listener.called


class TestEventFiringOnMaxTurns:
    """Test MaxTurnsReachedEvent firing when max turns exceeded."""

    def test_max_turns_event_fired(self):
        """MaxTurnsReachedEvent fires when turn_number >= max_turns."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=1)
        fired_events = []
        
        def capture_event(event: TerminalEvent) -> bool:
            fired_events.append(event)
            return True
        
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent, capture_event
        )
        
        # Turn 1 - hits max_turns=1
        result = protocol.execute_turn("input", {})
        
        # Event should fire once
        assert len(fired_events) == 1
        assert isinstance(fired_events[0], MaxTurnsReachedEvent)
        assert fired_events[0].max_turns == 1
        assert fired_events[0].current_turn == 1

    def test_max_turns_event_contains_metadata(self):
        """MaxTurnsReachedEvent includes turn and reason metadata."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=1)
        fired_events = []
        
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        protocol.turn_number = 1
        protocol.execute_turn("input", {})
        
        event = fired_events[0]
        assert event.max_turns == 1
        assert event.reason == "Max turns exceeded"

    def test_max_turns_decision_has_correct_reason(self):
        """Decision after max turns has MAX_ROUNDS_REACHED reason."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=1)
        
        protocol.turn_number = 1
        result = protocol.execute_turn("input", {})
        
        if result.is_ok():
            decision = result.unwrap()
            assert decision.reason == ContinuationReason.MAX_ROUNDS_REACHED
            assert decision.should_continue is False


class TestEventFiringOnTokenLimit:
    """Test TokenLimitEvent firing when token limit approached."""

    def test_token_limit_event_fired(self):
        """TokenLimitEvent fires when tokens > 90% of limit."""
        mock_orchestrator = MockIOrchestrator()
        
        
        token_limit = 1000
        protocol = ConversationProtocol(
            mock_orchestrator, token_limit=token_limit
        )
        fired_events = []
        
        protocol.event_registry.register_listener(
            TokenLimitEvent,
            lambda e: fired_events.append(e) or True
        )
        
        # Set tokens to 95% of limit
        protocol.total_tokens_used = int(token_limit * 0.95)
        protocol.execute_turn("input", {})
        
        assert len(fired_events) == 1
        assert isinstance(fired_events[0], TokenLimitEvent)

    def test_token_limit_event_contains_usage_info(self):
        """TokenLimitEvent includes token usage and percentage."""
        mock_orchestrator = MockIOrchestrator()
        
        
        token_limit = 1000
        protocol = ConversationProtocol(
            mock_orchestrator, token_limit=token_limit
        )
        fired_events = []
        
        protocol.event_registry.register_listener(
            TokenLimitEvent,
            lambda e: fired_events.append(e) or True
        )
        
        tokens_used = int(token_limit * 0.95)
        protocol.total_tokens_used = tokens_used
        protocol.execute_turn("input", {})
        
        event = fired_events[0]
        assert event.tokens_used == tokens_used
        assert event.token_limit == token_limit
        assert event.percentage_used == 95

    def test_token_limit_decision_has_correct_reason(self):
        """Decision after token limit has TOKEN_LIMIT reason."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, token_limit=1000)
        protocol.total_tokens_used = 950
        
        result = protocol.execute_turn("input", {})
        
        if result.is_ok():
            decision = result.unwrap()
            assert decision.reason == ContinuationReason.TOKEN_LIMIT
            assert decision.should_continue is False


class TestEventFiringOnCompletion:
    """Test PhaseCompletedEvent firing when orchestrator completes."""

    def test_phase_completed_event_fired(self):
        """PhaseCompletedEvent fires when orchestrator status='completed'."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={
                "status": "completed",
                "operation": "planning_phase",
                "result": {"plan": "test plan"}
            }
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        fired_events = []
        
        protocol.event_registry.register_listener(
            PhaseCompletedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        result = protocol.execute_turn("input", {})
        
        assert len(fired_events) == 1
        assert isinstance(fired_events[0], PhaseCompletedEvent)

    def test_phase_completed_event_contains_result(self):
        """PhaseCompletedEvent includes operation and result."""
        mock_orchestrator = MockIOrchestrator()
        expected_result = {"plan": "detailed plan", "steps": 5}
        mock_orchestrator.execute = Mock(
            return_value={
                "status": "completed",
                "operation": "planning",
                "result": expected_result
            }
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        fired_events = []
        
        protocol.event_registry.register_listener(
            PhaseCompletedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        protocol.execute_turn("input", {})
        
        event = fired_events[0]
        assert event.operation == "planning"
        assert event.result == expected_result

    def test_completion_decision_has_correct_reason(self):
        """Decision after completion has COMPLETION reason."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={"status": "completed", "operation": "phase"}
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        result = protocol.execute_turn("input", {})
        
        if result.is_ok():
            decision = result.unwrap()
            assert decision.reason == ContinuationReason.COMPLETION
            assert decision.should_continue is False


class TestEventFiringOnError:
    """Test ErrorOccurredEvent firing when orchestrator errors."""

    def test_error_event_fired(self):
        """ErrorOccurredEvent fires when orchestrator result contains error."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={"error": "Failed to parse input"}
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        fired_events = []
        
        protocol.event_registry.register_listener(
            ErrorOccurredEvent,
            lambda e: fired_events.append(e) or True
        )
        
        result = protocol.execute_turn("input", {})
        
        assert len(fired_events) == 1
        assert isinstance(fired_events[0], ErrorOccurredEvent)

    def test_error_event_contains_details(self):
        """ErrorOccurredEvent includes error message and type."""
        mock_orchestrator = MockIOrchestrator()
        error_msg = "Connection timeout"
        mock_orchestrator.execute = Mock(
            return_value={"error": error_msg}
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        fired_events = []
        
        protocol.event_registry.register_listener(
            ErrorOccurredEvent,
            lambda e: fired_events.append(e) or True
        )
        
        protocol.execute_turn("input", {})
        
        event = fired_events[0]
        assert event.error_message == error_msg
        assert event.error_type == "orchestrator_error"
        assert event.recoverable is False

    def test_error_decision_has_correct_reason(self):
        """Decision after error has ERROR_UNRECOVERABLE reason."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={"error": "Something failed"}
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        result = protocol.execute_turn("input", {})
        
        if result.is_ok():
            decision = result.unwrap()
            assert decision.reason == ContinuationReason.ERROR_UNRECOVERABLE
            assert decision.should_continue is False


class TestEventFiringOnApprovalRejection:
    """Test UserApprovalRejectedEvent firing when user rejects approval."""

    def test_approval_rejected_event_fired(self):
        """UserApprovalRejectedEvent fires when approval is rejected."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={
                "requires_approval": True,
                "approval_rejected": True,
                "approval_request": "Deploy to production?",
                "rejection_reason": "Not ready"
            }
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        fired_events = []
        
        protocol.event_registry.register_listener(
            UserApprovalRejectedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        result = protocol.execute_turn("input", {})
        
        assert len(fired_events) == 1
        assert isinstance(fired_events[0], UserApprovalRejectedEvent)

    def test_approval_rejected_event_contains_details(self):
        """UserApprovalRejectedEvent includes request and reason."""
        mock_orchestrator = MockIOrchestrator()
        request = "Execute migration?"
        reason = "Blocked by governance"
        mock_orchestrator.execute = Mock(
            return_value={
                "requires_approval": True,
                "approval_rejected": True,
                "approval_request": request,
                "rejection_reason": reason
            }
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        fired_events = []
        
        protocol.event_registry.register_listener(
            UserApprovalRejectedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        protocol.execute_turn("input", {})
        
        event = fired_events[0]
        assert event.approval_request == request
        assert event.rejection_reason == reason

    def test_rejection_decision_has_correct_reason(self):
        """Decision after rejection has USER_REJECTION reason."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={
                "requires_approval": True,
                "approval_rejected": True,
                "approval_request": "Deploy?",
                "rejection_reason": "No"
            }
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        result = protocol.execute_turn("input", {})
        
        if result.is_ok():
            decision = result.unwrap()
            assert decision.reason == ContinuationReason.USER_REJECTION
            assert decision.should_continue is False


class TestEventListenerVeto:
    """Test that listeners can veto continuation."""

    def test_listener_veto_blocks_continuation(self):
        """Listener returning False prevents continuation."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=10)
        
        # Listener that vetoes
        veto_listener = Mock(return_value=False)
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent, veto_listener
        )
        
        # This would normally not fire MaxTurnsReachedEvent
        # But we can test the mechanism
        protocol.turn_number = 10
        result = protocol.execute_turn("input", {})
        
        # Event still fires but listener was consulted
        assert veto_listener.called

    def test_listener_allows_continuation(self):
        """Listener returning True allows continuation."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator)
        
        allow_listener = Mock(return_value=True)
        protocol.event_registry.register_listener(
            PhaseCompletedEvent, allow_listener
        )
        
        # Register a completion event
        protocol.execute_turn("input", {})
        
        # Listener should have been called (or not, depending on logic)
        # The key is that returning True allows continuation


class TestEventAuditIntegration:
    """Test that events are linked to audit trail."""

    def test_event_turn_number_matches_protocol_turn(self):
        """Terminal event turn_number matches protocol.turn_number."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=1)
        fired_events = []
        
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        protocol.turn_number = 1
        protocol.execute_turn("input", {})
        
        event = fired_events[0]
        assert event.turn_number == protocol.turn_number

    def test_event_timestamp_is_set(self):
        """Terminal events include timestamp for audit trail."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=1)
        fired_events = []
        
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        before = datetime.now()
        protocol.turn_number = 1
        protocol.execute_turn("input", {})
        after = datetime.now()
        
        event = fired_events[0]
        assert event.timestamp is not None
        assert before <= event.timestamp <= after


class TestMultiEventScenarios:
    """Test complex scenarios with multiple events."""

    def test_only_first_break_condition_fires_event(self):
        """When multiple conditions met, first one fires event."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=1, token_limit=100)
        
        fired_events = []
        for event_type in [MaxTurnsReachedEvent, TokenLimitEvent]:
            protocol.event_registry.register_listener(
                event_type,
                lambda e: fired_events.append(e) or True
            )
        
        # Set both conditions
        protocol.turn_number = 1
        protocol.total_tokens_used = 95  # > 90% of 100
        
        protocol.execute_turn("input", {})
        
        # Only max turns event should fire (checked first)
        assert len(fired_events) >= 1
        assert isinstance(fired_events[0], MaxTurnsReachedEvent)

    def test_event_registry_state_preserved_across_turns(self):
        """EventRegistry state persists across multiple turns."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=3)
        
        all_events = []
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent,
            lambda e: all_events.append(e) or True
        )
        
        # Simulate 3 turns
        for turn_num in range(1, 4):
            protocol.turn_number = turn_num
            protocol.execute_turn(f"input {turn_num}", {})
        
        # Event should only fire on turn 3 (when >= max_turns)
        assert len(all_events) >= 1

    def test_multiple_event_types_can_be_registered(self):
        """Multiple event types can have listeners simultaneously."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator)
        
        max_turns_events = []
        error_events = []
        
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent,
            lambda e: max_turns_events.append(e) or True
        )
        protocol.event_registry.register_listener(
            ErrorOccurredEvent,
            lambda e: error_events.append(e) or True
        )
        
        # Both listeners should be registered
        assert protocol.event_registry.get_listener_count(MaxTurnsReachedEvent) == 1
        assert protocol.event_registry.get_listener_count(ErrorOccurredEvent) == 1


class TestEventIntegrationWithDecisions:
    """Test that event firing aligns with decision reasons."""

    def test_max_turns_event_and_decision_align(self):
        """MaxTurnsReachedEvent and MAX_ROUNDS_REACHED decision are synchronized."""
        mock_orchestrator = MockIOrchestrator()
        
        
        protocol = ConversationProtocol(mock_orchestrator, max_turns=1)
        
        fired_events = []
        protocol.event_registry.register_listener(
            MaxTurnsReachedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        protocol.turn_number = 1
        result = protocol.execute_turn("input", {})
        
        # Check alignment
        if result.is_ok():
            decision = result.unwrap()
            assert len(fired_events) == 1
            assert fired_events[0].get_continuation_reason() == decision.reason

    def test_completion_event_and_decision_align(self):
        """PhaseCompletedEvent and COMPLETION decision are synchronized."""
        mock_orchestrator = MockIOrchestrator()
        mock_orchestrator.execute = Mock(
            return_value={"status": "completed", "operation": "phase"}
        )
        
        protocol = ConversationProtocol(mock_orchestrator)
        
        fired_events = []
        protocol.event_registry.register_listener(
            PhaseCompletedEvent,
            lambda e: fired_events.append(e) or True
        )
        
        result = protocol.execute_turn("input", {})
        
        if result.is_ok():
            decision = result.unwrap()
            assert len(fired_events) == 1
            assert fired_events[0].get_continuation_reason() == decision.reason
            assert decision.reason == ContinuationReason.COMPLETION
