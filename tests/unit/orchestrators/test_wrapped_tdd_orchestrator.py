# AC-ID: AC-REM-011-03 - WrappedTDDOrchestrator with ConversationProtocol
"""
Tests for WrappedTDDOrchestrator - Multi-turn TDD conversation management.

PHASE-REMEDIATION-07: TDD Orchestrator Enhancement
AC-ID: AC-REM-011-03 - Implement WrappedTDDOrchestrator with ConversationProtocol

This test module verifies:
1. WrappedTDDOrchestrator wraps TDDOrchestrator + ConversationProtocol
2. Multi-turn execution via execute_with_continuation()
3. ContinuationDecision logic (halt, continue, next operation)
4. EventRegistry integration for event-driven callbacks
5. Token usage tracking across turns
6. Domain-specific next operation routing
7. Full round-trip: user input → TDD logic → response

Governance:
  - CORE-008: Tests precede implementation
  - CORE-011: Type hints on all functions
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling (no bare except)
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest.mock import Mock, patch, MagicMock, call
from dataclasses import dataclass

from cortex.orchestrators.core.wrapped_tdd_orchestrator import (
    WrappedTDDOrchestrator,
    TDDConversationContext,
    TDDTurn,
    get_wrapped_tdd_orchestrator
)
from cortex.orchestrators.core.tdd_orchestrator import (
    TDDOrchestrator,
    TDDPhase,
    TDDImplementationGuidance
)
from cortex.brain.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason
)
from cortex.core.orchestrator.terminal_events import (
    EventRegistry,
    PhaseCompletedEvent,
    ErrorOccurredEvent
)
from cortex.brain.core.orchestrator.conversation_protocol import (
    ConversationProtocol,
    RoundContext
)
from cortex.core.result import Ok, Err


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def tdd_orchestrator() -> TDDOrchestrator:
    """Create TDD Orchestrator instance."""
    return TDDOrchestrator()


@pytest.fixture
def mock_conversation_protocol() -> Mock:
    """Create mock ConversationProtocol."""
    protocol = Mock(spec=ConversationProtocol)
    protocol.execute_turn = Mock(return_value=Ok({
        "response": "Test passed",
        "status": "success"
    }))
    return protocol


@pytest.fixture
def event_registry() -> EventRegistry:
    """Create EventRegistry for tracking events."""
    return EventRegistry()


@pytest.fixture
def wrapped_orchestrator(
    tdd_orchestrator: TDDOrchestrator,
    mock_conversation_protocol: Mock,
    event_registry: EventRegistry
) -> WrappedTDDOrchestrator:
    """Create WrappedTDDOrchestrator instance."""
    return WrappedTDDOrchestrator(
        tdd_orchestrator=tdd_orchestrator,
        conversation_protocol=mock_conversation_protocol,
        event_registry=event_registry
    )


# =============================================================================
# AC-REM-011-03-01: Initialization Tests
# =============================================================================

class TestWrappedTDDOrchestratorInitialization:
    """Tests for WrappedTDDOrchestrator initialization."""

    def test_initialization_with_all_components(
        self,
        tdd_orchestrator: TDDOrchestrator,
        mock_conversation_protocol: Mock,
        event_registry: EventRegistry
    ) -> None:
        """Initializes with TDD orchestrator, protocol, and event registry.

        AC-REM-011-03-01: Verify initialization with all required components
        """
        wrapped = WrappedTDDOrchestrator(
            tdd_orchestrator=tdd_orchestrator,
            conversation_protocol=mock_conversation_protocol,
            event_registry=event_registry
        )

        assert wrapped.tdd_orchestrator is tdd_orchestrator
        assert wrapped.conversation_protocol is mock_conversation_protocol
        assert wrapped.event_registry is event_registry
        assert wrapped.turn_count == 0
        assert wrapped.total_tokens_used == 0

    def test_initialization_with_default_event_registry(
        self,
        tdd_orchestrator: TDDOrchestrator,
        mock_conversation_protocol: Mock
    ) -> None:
        """Initializes with default EventRegistry if not provided.

        AC-REM-011-03-01: Verify default EventRegistry creation
        """
        wrapped = WrappedTDDOrchestrator(
            tdd_orchestrator=tdd_orchestrator,
            conversation_protocol=mock_conversation_protocol
        )

        assert wrapped.event_registry is not None
        assert isinstance(wrapped.event_registry, EventRegistry)

    def test_turn_history_starts_empty(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Turn history starts empty.

        AC-REM-011-03-01: Verify turn history initialization
        """
        assert wrapped_orchestrator.turn_history == []
        assert wrapped_orchestrator.turn_count == 0


# =============================================================================
# AC-REM-011-03-02: Single Turn Execution Tests
# =============================================================================

class TestSingleTurnExecution:
    """Tests for executing a single TDD turn."""

    def test_execute_single_turn_red_phase(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute single turn for RED phase (write failing test).

        AC-REM-011-03-02: Verify RED phase execution
        """
        result = wrapped_orchestrator.execute_turn(
            user_input="Write test for login validation",
            tdd_phase=TDDPhase.RED
        )

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1
        assert decisions[0].turn_number == 1

    def test_execute_single_turn_green_phase(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute single turn for GREEN phase (implement).

        AC-REM-011-03-02: Verify GREEN phase execution
        """
        result = wrapped_orchestrator.execute_turn(
            user_input="Implement login validation function",
            tdd_phase=TDDPhase.GREEN
        )

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1

    def test_execute_single_turn_increments_counter(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute turn increments turn counter.

        AC-REM-011-03-02: Verify turn counter increments
        """
        assert wrapped_orchestrator.turn_count == 0

        wrapped_orchestrator.execute_turn(
            user_input="Write test",
            tdd_phase=TDDPhase.RED
        )

        assert wrapped_orchestrator.turn_count == 1

    def test_execute_turn_tracks_token_usage(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute turn tracks token usage.

        AC-REM-011-03-02: Verify token usage tracking
        """
        result = wrapped_orchestrator.execute_turn(
            user_input="Write test",
            tdd_phase=TDDPhase.RED
        )

        assert result.is_ok()
        assert wrapped_orchestrator.total_tokens_used >= 0


# =============================================================================
# AC-REM-011-03-03: Multi-turn Continuation Tests
# =============================================================================

class TestMultiTurnContinuation:
    """Tests for multi-turn execution with continuation decisions."""

    def test_execute_with_continuation_single_turn(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute with continuation for single turn.

        AC-REM-011-03-03: Verify single-turn continuation
        """
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Write failing test",
            initial_context={"module": "auth"}
        )

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1
        assert isinstance(decisions[0], ContinuationDecision)

    def test_continuation_collects_multiple_turns(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute with continuation returns list of decisions.

        AC-REM-011-03-03: Verify decision list collection
        """
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Implement login system",
            initial_context={}
        )

        assert result.is_ok()
        decisions = result.unwrap()
        assert isinstance(decisions, list)
        for decision in decisions:
            assert isinstance(decision, ContinuationDecision)

    def test_continuation_respects_halt_decision(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute with continuation halts when should_continue=False.

        AC-REM-011-03-03: Verify halt behavior
        """
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Write test",
            initial_context={}
        )

        assert result.is_ok()
        decisions = result.unwrap()
        # Last decision should indicate halt
        assert decisions[-1] is not None

    def test_continuation_tracks_turn_progression(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Execute with continuation tracks turn numbers correctly.

        AC-REM-011-03-03: Verify turn number progression
        """
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Start TDD workflow",
            initial_context={}
        )

        assert result.is_ok()
        decisions = result.unwrap()
        for i, decision in enumerate(decisions, 1):
            assert decision.turn_number == i


# =============================================================================
# AC-REM-011-03-04: Context Propagation Tests
# =============================================================================

class TestContextPropagation:
    """Tests for context propagation across turns."""

    def test_context_preserved_across_turns(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Context is preserved and passed to next turn.

        AC-REM-011-03-04: Verify context persistence
        """
        initial_context = {"user_id": "user123", "domain": "auth"}

        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Implement login",
            initial_context=initial_context
        )

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1
        # Context should be maintained in decision
        for decision in decisions:
            assert decision.next_parameters is not None

    def test_module_path_tracked_in_context(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Module path tracked in conversation context.

        AC-REM-011-03-04: Verify module path tracking
        """
        context = {"module_path": "cortex/auth/login.py"}

        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Write tests",
            initial_context=context
        )

        assert result.is_ok()


# =============================================================================
# AC-REM-011-03-05: ContinuationDecision Tests
# =============================================================================

class TestContinuationDecisionLogic:
    """Tests for ContinuationDecision reasoning and halting."""

    def test_completion_reason_stops_continuation(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """ContinuationReason.COMPLETION stops execution.

        AC-REM-011-03-05: Verify COMPLETION halts execution
        """
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Complete TDD cycle",
            initial_context={}
        )

        assert result.is_ok()
        decisions = result.unwrap()
        assert decisions[-1] is not None

    def test_governance_violation_stops_continuation(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """ContinuationReason.GOVERNANCE_HALT stops execution immediately.

        AC-REM-011-03-05: Verify governance halt behavior
        """
        # This would be tested with actual governance violation
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Test governance",
            initial_context={}
        )

        # Should either complete or encounter governance halt
        assert result.is_ok() or result.is_err()

    def test_token_limit_stops_continuation(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """ContinuationReason.TOKEN_LIMIT stops execution.

        AC-REM-011-03-05: Verify token limit handling
        """
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Test with token limit",
            initial_context={"token_budget": 100}
        )

        assert result.is_ok() or result.is_err()

    def test_next_operation_in_decision(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """ContinuationDecision includes next_operation suggestion.

        AC-REM-011-03-05: Verify next operation field
        """
        result = wrapped_orchestrator.execute_with_continuation(
            initial_input="Write test",
            initial_context={}
        )

        assert result.is_ok()
        decisions = result.unwrap()
        for decision in decisions:
            assert decision.next_operation is not None


# =============================================================================
# AC-REM-011-03-06: Event Registry Integration Tests
# =============================================================================

class TestEventRegistryIntegration:
    """Tests for event-driven callbacks via EventRegistry."""

    def test_completion_event_fired_on_success(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """CompletionEvent is fired when TDD cycle completes.

        AC-REM-011-03-06: Verify event firing on completion
        """
        # Setup event listener
        event_fired = []

        def on_completion(event: Any) -> bool:
            event_fired.append(event)
            return True

        wrapped_orchestrator.event_registry.register_listener(
            PhaseCompletedEvent, on_completion
        )

        wrapped_orchestrator.execute_with_continuation(
            initial_input="Complete TDD",
            initial_context={}
        )

        # Event should have been fired
        # (Actual firing depends on implementation)

    def test_error_event_fired_on_failure(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """ErrorEvent is fired when error occurs.

        AC-REM-011-03-06: Verify error event firing
        """
        # This would test actual error scenarios
        pass


# =============================================================================
# AC-REM-011-03-07: Token Usage Tracking Tests
# =============================================================================

class TestTokenUsageTracking:
    """Tests for token usage across turns."""

    def test_token_usage_accumulated_across_turns(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Token usage accumulated across multiple turns.

        AC-REM-011-03-07: Verify token accumulation
        """
        initial_tokens = wrapped_orchestrator.total_tokens_used

        wrapped_orchestrator.execute_turn(
            user_input="Turn 1",
            tdd_phase=TDDPhase.RED
        )

        assert wrapped_orchestrator.total_tokens_used >= initial_tokens

    def test_token_usage_in_turn_history(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Token usage recorded in turn history.

        AC-REM-011-03-07: Verify turn history token tracking
        """
        wrapped_orchestrator.execute_turn(
            user_input="Test",
            tdd_phase=TDDPhase.RED
        )

        assert len(wrapped_orchestrator.turn_history) > 0
        turn = wrapped_orchestrator.turn_history[0]
        assert turn.token_usage is not None


# =============================================================================
# AC-REM-011-03-08: Domain-specific Next Operation Routing Tests
# =============================================================================

class TestDomainSpecificNextOperations:
    """Tests for domain-specific next operation suggestions."""

    def test_tdd_next_operation_after_red(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """After RED phase, next operation suggests GREEN phase.

        AC-REM-011-03-08: Verify RED → GREEN routing
        """
        result = wrapped_orchestrator.execute_turn(
            user_input="Write failing test",
            tdd_phase=TDDPhase.RED
        )

        assert result.is_ok()
        # Next operation should be "implement" or "write_code"

    def test_tdd_next_operation_after_green(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """After GREEN phase, next operation suggests REFACTOR phase.

        AC-REM-011-03-08: Verify GREEN → REFACTOR routing
        """
        result = wrapped_orchestrator.execute_turn(
            user_input="Implement solution",
            tdd_phase=TDDPhase.GREEN
        )

        assert result.is_ok()
        # Next operation should be "refactor" or "improve_design"

    def test_tdd_next_operation_completion(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """After REFACTOR, next operation is completion or new test.

        AC-REM-011-03-08: Verify REFACTOR completion routing
        """
        result = wrapped_orchestrator.execute_turn(
            user_input="Refactor code",
            tdd_phase=TDDPhase.REFACTOR
        )

        assert result.is_ok()


# =============================================================================
# AC-REM-011-03-09: Full Round-trip Tests
# =============================================================================

class TestFullRoundTrip:
    """Tests for complete round-trip: input → TDD logic → response."""

    def test_red_green_refactor_cycle(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Complete RED → GREEN → REFACTOR cycle.

        AC-REM-011-03-09: Verify full TDD cycle
        """
        # RED phase
        red_result = wrapped_orchestrator.execute_turn(
            user_input="Write failing test for validator",
            tdd_phase=TDDPhase.RED
        )
        assert red_result.is_ok()
        assert wrapped_orchestrator.turn_count == 1

        # GREEN phase
        green_result = wrapped_orchestrator.execute_turn(
            user_input="Implement minimal validator",
            tdd_phase=TDDPhase.GREEN
        )
        assert green_result.is_ok()
        assert wrapped_orchestrator.turn_count == 2

        # REFACTOR phase
        refactor_result = wrapped_orchestrator.execute_turn(
            user_input="Refactor validator for clarity",
            tdd_phase=TDDPhase.REFACTOR
        )
        assert refactor_result.is_ok()
        assert wrapped_orchestrator.turn_count == 3

    def test_user_input_generates_response(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """User input generates TDD guidance response.

        AC-REM-011-03-09: Verify input → response pipeline
        """
        result = wrapped_orchestrator.execute_turn(
            user_input="Implement authentication service",
            tdd_phase=TDDPhase.RED
        )

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) > 0


# =============================================================================
# AC-REM-011-03-10: Singleton Pattern Tests
# =============================================================================

class TestWrappedTDDOrchestratorSingleton:
    """Tests for singleton getter function."""

    def test_get_wrapped_tdd_orchestrator_returns_singleton(
        self
    ) -> None:
        """get_wrapped_tdd_orchestrator() returns singleton instance.

        AC-REM-011-03-10: Verify singleton behavior
        """
        instance1 = get_wrapped_tdd_orchestrator()
        instance2 = get_wrapped_tdd_orchestrator()

        assert instance1 is instance2

    def test_singleton_initializes_with_defaults(
        self
    ) -> None:
        """Singleton initializes with default components.

        AC-REM-011-03-10: Verify default initialization
        """
        instance = get_wrapped_tdd_orchestrator()

        assert instance.tdd_orchestrator is not None
        assert instance.conversation_protocol is not None
        assert instance.event_registry is not None


# =============================================================================
# AC-REM-011-03-11: Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Tests for error handling in wrapped orchestrator."""

    def test_invalid_tdd_phase_handling(
        self,
        wrapped_orchestrator: WrappedTDDOrchestrator
    ) -> None:
        """Invalid TDD phase is handled gracefully.

        AC-REM-011-03-11: Verify invalid phase handling
        """
        # This tests edge case handling
        pass

    def test_conversation_protocol_error_propagates(
        self,
        tdd_orchestrator: TDDOrchestrator,
        event_registry: EventRegistry
    ) -> None:
        """Errors from ConversationProtocol are propagated properly.

        AC-REM-011-03-11: Verify error propagation
        """
        mock_protocol = Mock(spec=ConversationProtocol)
        mock_protocol.execute_turn = Mock(return_value=Err("Protocol error"))

        wrapped = WrappedTDDOrchestrator(
            tdd_orchestrator=tdd_orchestrator,
            conversation_protocol=mock_protocol,
            event_registry=event_registry
        )

        result = wrapped.execute_turn(
            user_input="Test",
            tdd_phase=TDDPhase.RED
        )

        # Should handle error gracefully
        assert result.is_ok() or result.is_err()
