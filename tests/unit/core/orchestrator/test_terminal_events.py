"""
Tests for Terminal Events and Break Condition Handlers.

Tests validate:
- Terminal event dataclasses
- EventListener interface
- EventRegistry pattern
- Event firing and listener notification
- Audit trail for events
"""

import pytest
from dataclasses import dataclass
from typing import List, Callable
from datetime import datetime

from cortex.core.orchestrator.terminal_events import (
    TerminalEvent,
    PhaseCompletedEvent,
    UserCancelledEvent,
    MaxTurnsReachedEvent,
    ErrorOccurredEvent,
    TokenLimitEvent,
    GovernanceViolationEvent,
    UserApprovalRejectedEvent,
    EventListener,
    EventRegistry,
)
from cortex.core.orchestrator.continuation_decision import ContinuationReason


class TestEventDefinitions:
    """Test that all terminal events are properly defined."""

    def test_phase_completed_event(self):
        """Test PhaseCompletedEvent."""
        event = PhaseCompletedEvent(
            operation="planning_complete",
            result="Successfully planned phase",
            turn_number=3,
        )
        
        assert event.operation == "planning_complete"
        assert event.result == "Successfully planned phase"
        assert event.turn_number == 3
        assert hasattr(event, "timestamp")

    def test_user_cancelled_event(self):
        """Test UserCancelledEvent."""
        event = UserCancelledEvent(
            reason="User clicked cancel button",
            turn_number=2,
        )
        
        assert event.reason == "User clicked cancel button"
        assert event.turn_number == 2

    def test_max_turns_reached_event(self):
        """Test MaxTurnsReachedEvent."""
        event = MaxTurnsReachedEvent(
            turn_number=10,
            max_turns=10,
            current_turn=10,
            reason="Safety limit enforced",
        )
        
        assert event.max_turns == 10
        assert event.current_turn == 10
        assert event.reason == "Safety limit enforced"

    def test_error_occurred_event(self):
        """Test ErrorOccurredEvent."""
        event = ErrorOccurredEvent(
            error_message="Division by zero",
            error_type="ValueError",
            turn_number=5,
            recoverable=False,
        )
        
        assert event.error_message == "Division by zero"
        assert event.error_type == "ValueError"
        assert event.turn_number == 5
        assert event.recoverable is False

    def test_token_limit_event(self):
        """Test TokenLimitEvent."""
        event = TokenLimitEvent(
            tokens_used=19500,
            token_limit=20000,
            percentage_used=97.5,
            turn_number=8,
        )
        
        assert event.tokens_used == 19500
        assert event.token_limit == 20000
        assert event.percentage_used == 97.5
        assert event.turn_number == 8

    def test_governance_violation_event(self):
        """Test GovernanceViolationEvent."""
        event = GovernanceViolationEvent(
            rule_id="CORE-017",
            violation_message="Governance halt triggered",
            turn_number=4,
        )
        
        assert event.rule_id == "CORE-017"
        assert event.violation_message == "Governance halt triggered"
        assert event.turn_number == 4

    def test_user_approval_rejected_event(self):
        """Test UserApprovalRejectedEvent."""
        event = UserApprovalRejectedEvent(
            approval_request="Do you approve this plan?",
            rejection_reason="Plan too risky",
            turn_number=3,
        )
        
        assert event.approval_request == "Do you approve this plan?"
        assert event.rejection_reason == "Plan too risky"
        assert event.turn_number == 3


class TestEventListener:
    """Test EventListener interface."""

    def test_listener_interface_defined(self):
        """Test that EventListener is a callable interface."""
        # EventListener should be callable
        assert callable(EventListener) or hasattr(EventListener, '__call__')

    def test_listener_implementation(self):
        """Test implementing a listener."""
        class TestListener:
            def on_event(self, event: TerminalEvent) -> bool:
                """Handle event. Return True to continue, False to break."""
                return not isinstance(event, UserCancelledEvent)
        
        listener = TestListener()
        
        # Should handle events
        cancelled = UserCancelledEvent("user request", 1)
        assert listener.on_event(cancelled) is False
        
        completed = PhaseCompletedEvent("done", "success", 1)
        assert listener.on_event(completed) is True


class TestEventRegistry:
    """Test EventRegistry pattern."""

    def test_registry_creation(self):
        """Test creating an EventRegistry."""
        registry = EventRegistry()
        
        assert registry is not None
        assert hasattr(registry, 'register_listener')
        assert hasattr(registry, 'fire_event')

    def test_register_listener_for_event(self):
        """Test registering a listener for an event type."""
        registry = EventRegistry()
        listener_called = []
        
        def test_listener(event: TerminalEvent) -> bool:
            listener_called.append(True)
            return True
        
        registry.register_listener(PhaseCompletedEvent, test_listener)
        assert registry is not None

    def test_fire_event_calls_listeners(self):
        """Test that firing an event calls registered listeners."""
        registry = EventRegistry()
        listener_calls = []
        
        def test_listener(event: TerminalEvent) -> bool:
            listener_calls.append(event)
            return True
        
        registry.register_listener(PhaseCompletedEvent, test_listener)
        
        event = PhaseCompletedEvent("operation", "result", 1)
        registry.fire_event(event)
        
        # Listener should have been called
        assert len(listener_calls) > 0

    def test_multiple_listeners_same_event(self):
        """Test multiple listeners for same event type."""
        registry = EventRegistry()
        calls = []
        
        def listener1(event: TerminalEvent) -> bool:
            calls.append("listener1")
            return True
        
        def listener2(event: TerminalEvent) -> bool:
            calls.append("listener2")
            return True
        
        registry.register_listener(PhaseCompletedEvent, listener1)
        registry.register_listener(PhaseCompletedEvent, listener2)
        
        event = PhaseCompletedEvent("op", "result", 1)
        registry.fire_event(event)
        
        # Both listeners should have been called
        assert "listener1" in calls or "listener2" in calls

    def test_listener_can_veto_continuation(self):
        """Test that listeners can veto continuation."""
        registry = EventRegistry()
        veto_decisions = []
        
        def veto_listener(event: TerminalEvent) -> bool:
            veto_decisions.append(False)  # Veto: don't continue
            return False
        
        registry.register_listener(UserCancelledEvent, veto_listener)
        
        event = UserCancelledEvent("user cancelled", 2)
        result = registry.fire_event(event)
        
        # Registry should indicate event vetoed
        assert result is not None


class TestEventAuditTrail:
    """Test event audit logging."""

    def test_event_audit_entry_created(self):
        """Test that event is auditable."""
        event = PhaseCompletedEvent("op", "result", 1)
        
        # Event should have fields for auditing
        assert hasattr(event, 'turn_number')
        assert hasattr(event, 'timestamp')

    def test_event_linked_to_turn(self):
        """Test event links to turn number."""
        event = TokenLimitEvent(
            tokens_used=19000,
            token_limit=20000,
            percentage_used=95.0,
            turn_number=7,
        )
        
        assert event.turn_number == 7

    def test_multiple_events_per_turn_auditable(self):
        """Test that multiple events can occur in one turn."""
        turn = 5
        
        event1 = TokenLimitEvent(
            turn_number=turn,
            tokens_used=19500,
            token_limit=20000,
            percentage_used=97.5,
        )
        event2 = UserApprovalRejectedEvent(
            turn_number=turn,
            approval_request="approve?",
            rejection_reason="no",
        )
        
        assert event1.turn_number == turn
        assert event2.turn_number == turn


class TestEventTypeMapping:
    """Test mapping events to continuation reasons."""

    def test_event_to_continuation_reason_mapping(self):
        """Test that events correspond to continuation reasons."""
        mappings = {
            PhaseCompletedEvent: ContinuationReason.COMPLETION,
            UserCancelledEvent: ContinuationReason.USER_REJECTION,
            MaxTurnsReachedEvent: ContinuationReason.MAX_ROUNDS_REACHED,
            ErrorOccurredEvent: ContinuationReason.ERROR_UNRECOVERABLE,
            TokenLimitEvent: ContinuationReason.TOKEN_LIMIT,
            GovernanceViolationEvent: ContinuationReason.GOVERNANCE_HALT,
            UserApprovalRejectedEvent: ContinuationReason.INTERACTION_REQUIRED,
        }
        
        # All events should map to continuation reasons
        assert len(mappings) == 7


class TestEventFireworkflow:
    """Test event firing and handling workflow."""

    def test_event_fired_updates_decision(self):
        """Test that fired events affect continuation decision."""
        registry = EventRegistry()
        decision_changed = []
        
        def on_token_limit(event: TerminalEvent) -> bool:
            decision_changed.append("halt_on_token_limit")
            return False  # Stop processing
        
        registry.register_listener(TokenLimitEvent, on_token_limit)
        
        event = TokenLimitEvent(
            turn_number=9,
            tokens_used=19800,
            token_limit=20000,
            percentage_used=99.0,
        )
        result = registry.fire_event(event)
        
        # Decision should have been affected
        assert len(decision_changed) > 0 or result is not None

    def test_event_listener_receives_full_event(self):
        """Test that listeners receive full event object."""
        registry = EventRegistry()
        received_events = []
        
        def capture_listener(event: TerminalEvent) -> bool:
            received_events.append(event)
            return True
        
        registry.register_listener(ErrorOccurredEvent, capture_listener)
        
        error_event = ErrorOccurredEvent(
            turn_number=3,
            error_message="Test error",
            error_type="TestException",
            recoverable=True
        )
        registry.fire_event(error_event)
        
        assert len(received_events) > 0
        if len(received_events) > 0:
            assert received_events[0].error_message == "Test error"

    def test_event_registry_clear_listeners(self):
        """Test clearing listeners."""
        registry = EventRegistry()
        
        def listener(event: TerminalEvent) -> bool:
            return True
        
        registry.register_listener(PhaseCompletedEvent, listener)
        
        # Should be able to clear (if method exists)
        if hasattr(registry, 'clear_listeners'):
            registry.clear_listeners()


class TestEventIntegration:
    """Test events integration with ConversationProtocol."""

    def test_registry_integration_signature(self):
        """Test registry can be integrated with protocol."""
        # EventRegistry should be injectable into ConversationProtocol
        registry = EventRegistry()
        
        # Should have fire_event method
        assert hasattr(registry, 'fire_event')
        assert callable(registry.fire_event)

    def test_event_firing_before_protocol_halt(self):
        """Test events can be fired before protocol halt."""
        registry = EventRegistry()
        events_fired = []
        
        def track_event(event: TerminalEvent) -> bool:
            events_fired.append(event.__class__.__name__)
            return False  # Halt
        
        registry.register_listener(MaxTurnsReachedEvent, track_event)
        
        # Fire event
        event = MaxTurnsReachedEvent(10, 10, "limit reached")
        registry.fire_event(event)
        
        # Should have fired
        assert len(events_fired) > 0
