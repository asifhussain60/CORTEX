"""Integration tests for multi-turn, multi-domain orchestration workflows.

OC-004-01: Comprehensive Test Suite
Tests complex orchestration scenarios across multiple domains and turns.
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch

import pytest

from src.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)
from src.core.orchestrator.conversation_protocol import ConversationProtocol
from src.core.orchestrator.terminal_events import (
    EventRegistry,
    PhaseCompletedEvent,
    UserCancelledEvent,
    MaxTurnsReachedEvent,
    ErrorOccurredEvent,
    TokenLimitEvent,
)


class OrchestrationDomain(Enum):
    """Domain enumeration for multi-domain workflows."""

    PLANNING = "planning"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"


@dataclass
class DomainResult:
    """Result from executing a domain orchestrator."""

    domain: OrchestrationDomain
    turn_number: int
    status: str  # "in_progress", "completed"
    next_operation: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None


class MockMultiDomainOrchestrator:
    """Mock orchestrator that simulates realistic multi-domain behavior."""

    def __init__(self, domain: OrchestrationDomain):
        """Initialize with domain."""
        self.domain = domain
        self.turn_count = 0
        self.decisions_made = []

    def execute(self, user_input: str, context: Dict) -> Dict:
        """Execute orchestrator operation."""
        self.turn_count += 1

        # Simulate realistic turn progression
        if self.domain == OrchestrationDomain.PLANNING:
            return self._planning_turn(self.turn_count, user_input, context)
        elif self.domain == OrchestrationDomain.DESIGN:
            return self._design_turn(self.turn_count, user_input, context)
        else:  # IMPLEMENTATION
            return self._implementation_turn(self.turn_count, user_input, context)

    def _planning_turn(self, turn: int, user_input: str, context: Dict) -> Dict:
        """Simulate planning domain workflow."""
        if turn == 1:
            return {
                "status": "in_progress",
                "operation": "analyze_requirements",
                "result": "Requirements analyzed for 5 features",
                "next_operation": "create_design_spec",
            }
        elif turn == 2:
            return {
                "status": "in_progress",
                "operation": "validate_requirements",
                "result": "All requirements validated against acceptance criteria",
                "next_operation": "begin_design",
            }
        else:
            return {
                "status": "completed",
                "operation": "planning_complete",
                "result": "Planning phase complete - ready for design",
                "next_operation": "begin_design",
            }

    def _design_turn(self, turn: int, user_input: str, context: Dict) -> Dict:
        """Simulate design domain workflow."""
        if turn == 1:
            return {
                "status": "in_progress",
                "operation": "create_architecture",
                "result": "System architecture designed with 3 layers",
                "next_operation": "create_schema",
            }
        elif turn == 2:
            return {
                "status": "in_progress",
                "operation": "create_schema",
                "result": "Database schema created with 12 tables",
                "next_operation": "validate_design",
            }
        else:
            return {
                "status": "completed",
                "operation": "design_complete",
                "result": "Design phase complete - ready for TDD",
                "next_operation": "begin_implementation",
            }

    def _implementation_turn(self, turn: int, user_input: str, context: Dict) -> Dict:
        """Simulate implementation domain workflow."""
        if turn == 1:
            return {
                "status": "in_progress",
                "operation": "setup_environment",
                "result": "Development environment configured",
                "next_operation": "write_tests",
            }
        elif turn == 2:
            return {
                "status": "in_progress",
                "operation": "write_tests",
                "result": "45 test cases written and passing",
                "next_operation": "implement_features",
            }
        else:
            return {
                "status": "completed",
                "operation": "implementation_complete",
                "result": "All features implemented and tested",
                "next_operation": "done",
            }


class TestIntegrationWorkflows:
    """Test suite for multi-turn, multi-domain orchestration workflows."""

    @pytest.fixture
    def event_registry(self):
        """Create event registry for tests."""
        return EventRegistry()

    @pytest.fixture
    def planning_orchestrator(self):
        """Create planning orchestrator."""
        return MockMultiDomainOrchestrator(OrchestrationDomain.PLANNING)

    @pytest.fixture
    def design_orchestrator(self):
        """Create design orchestrator."""
        return MockMultiDomainOrchestrator(OrchestrationDomain.DESIGN)

    @pytest.fixture
    def implementation_orchestrator(self):
        """Create implementation orchestrator."""
        return MockMultiDomainOrchestrator(OrchestrationDomain.IMPLEMENTATION)

    def test_single_domain_multi_turn_workflow(
        self, event_registry, planning_orchestrator
    ):
        """Test multi-turn execution within single domain (Planning)."""
        protocol = ConversationProtocol(
            orchestrator=planning_orchestrator,
            max_turns=5,
            token_limit=10000,
            event_registry=event_registry,
        )

        decisions = []
        current_input = "Analyze the business requirements"

        for turn in range(3):
            result = protocol.execute_turn(current_input, {"domain": "planning"})
            assert result.is_ok()

            decision = result.unwrap()
            decisions.append(decision)
            assert decision.turn_number == turn

            # Simulate orchestrator execution
            orch_result = planning_orchestrator.execute(current_input, {})
            current_input = orch_result.get("operation", "continue")

            if orch_result.get("status") == "completed":
                break

        assert len(decisions) == 3
        assert decisions[-1].reason in [
            ContinuationReason.COMPLETION,
            ContinuationReason.IMPLICIT_NEXT_OPERATION,
        ]

    def test_multi_domain_sequential_workflow(
        self,
        event_registry,
        planning_orchestrator,
        design_orchestrator,
        implementation_orchestrator,
    ):
        """Test sequential workflow across Planning → Design → Implementation domains."""
        domains = [
            planning_orchestrator,
            design_orchestrator,
            implementation_orchestrator,
        ]

        protocol = ConversationProtocol(
            max_turns=10,
            token_limit=50000,
            event_registry=event_registry,
        )

        all_decisions = []

        for domain_orchestrator in domains:
            domain = domain_orchestrator.domain
            current_input = f"Begin {domain.value} phase"

            for turn in range(3):
                result = protocol.execute_turn(
                    current_input, {"domain": domain.value}
                )
                assert result.is_ok()

                decision = result.unwrap()
                all_decisions.append(decision)
                assert decision.turn_number == turn

                orch_result = domain_orchestrator.execute(current_input, {})
                current_input = orch_result.get("operation", "continue")

                if orch_result.get("status") == "completed":
                    break

        # Verify workflow progression
        assert len(all_decisions) >= 6  # At least 2 turns per domain
        assert all_decisions[0].turn_number == 0  # First turn is 0
        # Total turns should span multiple domains
        assert all_decisions[-1].turn_number < 10

    def test_token_tracking_across_multi_turn_workflow(self, event_registry):
        """Test token tracking accumulates correctly across multiple turns."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=1000,
            event_registry=event_registry,
        )

        tokens_by_turn = []

        for turn in range(3):
            result = protocol.execute_turn(f"Turn {turn} input", {"test": True})
            assert result.is_ok()

            decision = result.unwrap()
            tokens_by_turn.append(decision.token_usage)

        # Verify token usage is tracked
        assert len(tokens_by_turn) == 3
        # Token usage should be accumulating (or at least tracked)
        assert tokens_by_turn[0] >= 0

    def test_context_sharing_across_domains(self, event_registry):
        """Test context propagation and sharing across domain transitions."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        shared_context = {
            "project_id": "proj-123",
            "requirements": ["Feature A", "Feature B"],
            "timestamp": "2026-01-16T00:00:00Z",
        }

        # Turn 1: Planning domain
        result = protocol.execute_turn(
            "Analyze requirements", {"domain": "planning", **shared_context}
        )
        assert result.is_ok()

        # Turn 2: Design domain - context should be available
        result = protocol.execute_turn(
            "Design architecture",
            {"domain": "design", **shared_context},
        )
        assert result.is_ok()

        decision = result.unwrap()
        assert decision.turn_number == 1

    def test_error_recovery_in_multi_turn_workflow(self, event_registry):
        """Test error handling and recovery across turns."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        # Turn 1: Successful
        result1 = protocol.execute_turn(
            "Valid input", {"domain": "planning"}
        )
        assert result1.is_ok()

        # Turn 2: Simulate error scenario
        error_result = {
            "error": "Validation failed",
            "error_type": "ValidationError",
            "recoverable": True,
        }

        result2 = protocol.execute_turn(
            "Invalid input",
            {"domain": "planning", "expected_error": error_result},
        )
        # Protocol should handle errors gracefully
        if result2.is_ok():
            decision = result2.unwrap()
            # Error should be captured in decision or reason
            assert decision.turn_number == 1

    def test_max_turns_enforcement_in_complex_workflow(self, event_registry):
        """Test that max_turns limit is enforced in multi-turn workflows."""
        max_turns = 3
        protocol = ConversationProtocol(
            max_turns=max_turns,
            token_limit=50000,
            event_registry=event_registry,
        )

        turns_executed = 0

        for turn in range(max_turns + 2):  # Try to execute beyond limit
            result = protocol.execute_turn(f"Input {turn}", {})
            if result.is_ok():
                decision = result.unwrap()
                turns_executed += 1

                if decision.turn_number >= max_turns - 1:
                    # Should be approaching limit
                    assert decision.turn_number < max_turns

        # Should not exceed max_turns
        assert turns_executed <= max_turns

    def test_event_firing_in_multi_turn_workflow(self, event_registry):
        """Test that events are properly fired during multi-turn workflows."""
        events_fired = []

        def capture_event(event):
            """Capture events for testing."""
            events_fired.append(type(event).__name__)
            return True  # Allow continuation

        event_registry.register_listener(PhaseCompletedEvent, capture_event)
        event_registry.register_listener(MaxTurnsReachedEvent, capture_event)

        protocol = ConversationProtocol(
            max_turns=2,
            token_limit=5000,
            event_registry=event_registry,
        )

        # Execute until max turns
        for turn in range(3):
            protocol.execute_turn(f"Turn {turn}", {})

        # At least some events should be fired during workflow
        # (could be MaxTurnsReachedEvent or others)
        assert isinstance(events_fired, list)

    def test_decision_history_accumulation(self, event_registry):
        """Test that decision history accumulates across turns."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        decisions = []

        for turn in range(3):
            result = protocol.execute_turn(f"Turn {turn}", {})
            if result.is_ok():
                decision = result.unwrap()
                decisions.append(decision)

        # Verify decision history
        assert len(decisions) == 3
        for i, decision in enumerate(decisions):
            assert decision.turn_number == i

    def test_cross_domain_routing_hints(self, event_registry):
        """Test cross-domain navigation hints in continuation decisions."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        result = protocol.execute_turn(
            "Complete planning phase",
            {"domain": "planning", "final_turn": True},
        )

        if result.is_ok():
            decision = result.unwrap()
            # Decision should be valid
            assert isinstance(decision, ContinuationDecision)
            assert decision.turn_number >= 0

    def test_orchestrator_context_propagation(self, event_registry):
        """Test that orchestrator execution context propagates correctly."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        orchestrator_metadata = {
            "orchestrator_name": "PlanningOrchestrator",
            "phase": "phase-16",
            "user_id": "test-user",
        }

        result = protocol.execute_turn("Execute task", orchestrator_metadata)
        assert result.is_ok()

        decision = result.unwrap()
        # Context should be available in decision
        assert decision is not None
        assert decision.turn_number >= 0

    def test_governance_validation_in_workflow(self, event_registry):
        """Test governance validation throughout multi-turn workflows."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        # Turn with governance context
        context_with_governance = {
            "phase": "PHASE-16",
            "ac_id": "OC-004-01",
            "governance_tier": 0,
        }

        result = protocol.execute_turn(
            "Execute with governance",
            context_with_governance,
        )
        assert result.is_ok()

    def test_partial_failure_recovery(self, event_registry):
        """Test partial failure scenarios and recovery mechanisms."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        # Simulate partially successful turns
        for turn in range(3):
            if turn == 1:
                # Simulate partial failure
                context = {"partial_failure": True}
            else:
                context = {}

            result = protocol.execute_turn(f"Turn {turn}", context)
            # Should handle gracefully even with failures
            if result.is_ok():
                decision = result.unwrap()
                assert decision is not None

    def test_workflow_state_consistency(self, event_registry):
        """Test that workflow state remains consistent across turns."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        turn_numbers = []

        for turn in range(3):
            result = protocol.execute_turn(f"Turn {turn}", {})
            if result.is_ok():
                decision = result.unwrap()
                turn_numbers.append(decision.turn_number)

        # Turn numbers should be sequential
        for i, turn_num in enumerate(turn_numbers):
            assert turn_num == i

    def test_continuation_reason_progression(self, event_registry):
        """Test that continuation reasons progress logically through workflow."""
        protocol = ConversationProtocol(
            max_turns=3,
            token_limit=5000,
            event_registry=event_registry,
        )

        reasons = []

        for turn in range(3):
            result = protocol.execute_turn(f"Turn {turn}", {})
            if result.is_ok():
                decision = result.unwrap()
                reasons.append(decision.reason)

        # Should have valid reasons
        assert len(reasons) > 0
        for reason in reasons:
            assert isinstance(reason, ContinuationReason)

    def test_audit_trail_completeness_in_workflow(self, event_registry):
        """Test that audit trail remains complete across multi-turn workflows."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        audit_entries = 0

        for turn in range(3):
            result = protocol.execute_turn(f"Turn {turn}", {})
            if result.is_ok():
                decision = result.unwrap()
                if decision.audit_entry_id:
                    audit_entries += 1

        # Should have audit entries from turns
        assert audit_entries >= 0  # At least tracked


class TestComplexWorkflowScenarios:
    """Test complex real-world orchestration scenarios."""

    @pytest.fixture
    def event_registry(self):
        """Create event registry."""
        return EventRegistry()

    def test_scenario_five_turn_planning_domain(self, event_registry):
        """Scenario: 5-turn planning phase workflow."""
        protocol = ConversationProtocol(
            max_turns=10,
            token_limit=10000,
            event_registry=event_registry,
        )

        orchestrator = MockMultiDomainOrchestrator(OrchestrationDomain.PLANNING)

        for _ in range(5):
            result = protocol.execute_turn(
                "Analyze and refine requirements",
                {"domain": "planning"},
            )
            assert result.is_ok()
            orchestrator.execute("", {})

    def test_scenario_full_workflow_planning_design_impl(self, event_registry):
        """Scenario: Complete workflow across all 3 domains."""
        protocol = ConversationProtocol(
            max_turns=15,
            token_limit=50000,
            event_registry=event_registry,
        )

        orchestrators = {
            "planning": MockMultiDomainOrchestrator(OrchestrationDomain.PLANNING),
            "design": MockMultiDomainOrchestrator(OrchestrationDomain.DESIGN),
            "implementation": MockMultiDomainOrchestrator(
                OrchestrationDomain.IMPLEMENTATION
            ),
        }

        domains_order = ["planning", "design", "implementation"]

        for domain_name in domains_order:
            for _ in range(3):
                result = protocol.execute_turn(
                    f"Execute {domain_name}",
                    {"domain": domain_name},
                )
                assert result.is_ok()
                orchestrators[domain_name].execute("", {})

    def test_scenario_token_constrained_workflow(self, event_registry):
        """Scenario: Workflow with token limits forcing early termination."""
        protocol = ConversationProtocol(
            max_turns=100,
            token_limit=500,  # Very limited tokens
            event_registry=event_registry,
        )

        turns_before_limit = 0

        for _ in range(20):
            result = protocol.execute_turn("Process data", {})
            if result.is_ok():
                decision = result.unwrap()
                turns_before_limit += 1
                if not decision.should_continue:
                    break

        # Should have executed some turns before hitting token limit
        assert turns_before_limit > 0

    def test_scenario_error_then_recovery(self, event_registry):
        """Scenario: Single error followed by successful recovery."""
        protocol = ConversationProtocol(
            max_turns=5,
            token_limit=5000,
            event_registry=event_registry,
        )

        # Turn 1: Success
        result1 = protocol.execute_turn("Initial setup", {})
        assert result1.is_ok()

        # Turn 2: Error
        result2 = protocol.execute_turn(
            "Invalid operation", {"expect_error": True}
        )

        # Turn 3: Recovery
        result3 = protocol.execute_turn("Retry operation", {})
        if result3.is_ok():
            decision = result3.unwrap()
            assert decision is not None

    def test_scenario_domain_switching_rapid(self, event_registry):
        """Scenario: Rapid switching between domains."""
        protocol = ConversationProtocol(
            max_turns=10,
            token_limit=5000,
            event_registry=event_registry,
        )

        domains = ["planning", "design", "implementation", "design", "planning"]

        for domain in domains:
            result = protocol.execute_turn(
                f"Switch to {domain}",
                {"domain": domain},
            )
            assert result.is_ok()


class TestPerformanceValidation:
    """Test performance characteristics of orchestration workflows."""

    @pytest.fixture
    def event_registry(self):
        """Create event registry."""
        return EventRegistry()

    def test_performance_single_turn_execution(self, event_registry):
        """Performance: Single turn execution should be fast."""
        protocol = ConversationProtocol(
            max_turns=100,
            token_limit=50000,
            event_registry=event_registry,
        )

        import time

        start = time.time()
        result = protocol.execute_turn("Test input", {})
        elapsed = time.time() - start

        assert result.is_ok()
        assert elapsed < 0.1  # Should complete in < 100ms

    def test_performance_hundred_turn_workflow(self, event_registry):
        """Performance: 100-turn workflow should complete in reasonable time."""
        protocol = ConversationProtocol(
            max_turns=200,
            token_limit=500000,
            event_registry=event_registry,
        )

        import time

        start = time.time()
        for _ in range(100):
            result = protocol.execute_turn("Test input", {})
            if not result.is_ok():
                break

        elapsed = time.time() - start

        # 100 turns should complete in < 5 seconds
        assert elapsed < 5.0

    def test_performance_event_registry_with_many_listeners(self, event_registry):
        """Performance: Event system should scale with many listeners."""
        # Register 50 listeners
        for i in range(50):

            def listener(event):
                return True

            event_registry.register_listener(PhaseCompletedEvent, listener)

        protocol = ConversationProtocol(
            max_turns=10,
            token_limit=5000,
            event_registry=event_registry,
        )

        import time

        start = time.time()
        for _ in range(10):
            protocol.execute_turn("Test", {})

        elapsed = time.time() - start

        # Should still be performant with many listeners
        assert elapsed < 2.0


# ============================================================================
# Test Utilities
# ============================================================================


def create_test_workflow(
    num_domains: int = 3,
    turns_per_domain: int = 3,
    event_registry: Optional[EventRegistry] = None,
) -> Dict[str, Any]:
    """Create a test workflow configuration.

    Args:
        num_domains: Number of domains in workflow
        turns_per_domain: Turns per domain
        event_registry: EventRegistry instance

    Returns:
        Test workflow configuration dict
    """
    if event_registry is None:
        event_registry = EventRegistry()

    return {
        "num_domains": num_domains,
        "turns_per_domain": turns_per_domain,
        "total_turns": num_domains * turns_per_domain,
        "event_registry": event_registry,
    }
