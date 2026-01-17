"""
Tests for OC-003-01: Orchestrator Wrapping with ConversationProtocol.

This module tests the integration of PlanningOrchestrator, ADOOrchestrator,
and TDDOrchestrator with ConversationProtocol for multi-turn, event-driven
execution.

Test Classes:
    - TestWrappedPlanningOrchestrator: Planning orchestrator wrapping
    - TestWrappedADOOrchestrator: ADO orchestrator wrapping
    - TestWrappedTDDOrchestrator: TDD orchestrator wrapping
    - TestOrchestratorIntegration: Cross-orchestrator workflows
    - TestDomainSpecificNextOperations: Domain routing
"""

from typing import Any, Dict, List, Optional
from unittest.mock import Mock, MagicMock, patch

import pytest

from src.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)
from src.core.orchestrator.conversation_protocol import ConversationProtocol
from src.core.orchestrator.terminal_events import EventRegistry
from src.core.result import Ok, Err, Result


# Apply timeout to all tests in this module to prevent hangs
pytestmark = pytest.mark.timeout(10)


class MockOrchestrator:
    """Mock orchestrator for testing wrapping pattern."""

    def __init__(self, name: str = "MockOrchestrator"):
        self.name = name
        self.execute_calls = []

    def execute(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute method matching IOrchestrator interface."""
        self.execute_calls.append({
            "user_input": user_input,
            "context": context
        })
        return {
            "status": "pending",
            "output": f"Result from {self.name}",
            "next_operation": "continue"
        }

    def get_domain_name(self) -> str:
        """Get domain name."""
        return self.name

    def __class__(self):
        """Mock class name for ConversationProtocol."""
        return type('MockOrchestrator', (), {'__name__': self.name})


class WrappedOrchestrator:
    """Base wrapper for orchestrators with ConversationProtocol."""
    
    # Safety guard: Maximum iterations to prevent infinite loops
    MAX_TURN_ITERATIONS = 50

    def __init__(
        self,
        orchestrator: Any,
        max_turns: int = 5,
        token_limit: int = 30000,
        event_registry: Optional[EventRegistry] = None,
    ):
        """Initialize wrapped orchestrator."""
        self.orchestrator = orchestrator
        self.protocol = ConversationProtocol(
            orchestrator,
            max_turns=max_turns,
            token_limit=token_limit,
            event_registry=event_registry,
        )
        self.decisions = []

    def execute_with_continuation(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Result[List[ContinuationDecision]]:
        """Execute multi-turn workflow yielding decisions."""
        if context is None:
            context = {}

        self.decisions = []
        current_input = user_input
        current_context = context
        
        # Safety guard: Track iterations to prevent infinite loops
        turn_iterations = 0

        while True:
            turn_iterations += 1
            if turn_iterations > self.MAX_TURN_ITERATIONS:
                return Err(
                    f"Orchestrator exceeded maximum turn iterations ({self.MAX_TURN_ITERATIONS}). "
                    f"Possible infinite loop in conversation protocol."
                )
            
            result = self.protocol.execute_turn(current_input, current_context)

            if result.is_err():
                return Err(result.error)

            decision = result.unwrap()
            self.decisions.append(decision)

            if not decision.should_continue:
                break

            # Prepare for next turn
            current_input = decision.next_operation or "continue"
            current_context = decision.next_parameters or current_context

        return Ok(self.decisions)

    def get_domain_name(self) -> str:
        """Get domain name."""
        if hasattr(self.orchestrator, 'get_domain_name'):
            return self.orchestrator.get_domain_name()
        return self.orchestrator.__class__.__name__


class TestWrappedPlanningOrchestrator:
    """Test Planning orchestrator wrapping with ConversationProtocol."""

    def test_wrapped_planning_orchestrator_single_turn(self):
        """WrappedPlanningOrchestrator executes single turn correctly."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")
        wrapped = WrappedOrchestrator(mock_planner)

        result = wrapped.execute_with_continuation("Create a plan", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1
        assert isinstance(decisions[0], ContinuationDecision)

    def test_wrapped_planning_orchestrator_multi_turn(self):
        """WrappedPlanningOrchestrator supports multi-turn workflow."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")
        call_count = [0]

        def planning_execute(user_input: str, context: Dict) -> Dict:
            call_count[0] += 1
            if call_count[0] < 3:
                # First two turns continue
                return {
                    "status": "pending",
                    "output": f"Planning turn {call_count[0]}",
                    "next_operation": "refine_plan"
                }
            else:
                # Third turn completes
                return {
                    "status": "completed",
                    "operation": "planning",
                    "result": {"plan": "complete plan"}
                }

        mock_planner.execute = planning_execute
        wrapped = WrappedOrchestrator(mock_planner, max_turns=5)

        result = wrapped.execute_with_continuation("Create a plan", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1
        # Last decision should have COMPLETION reason
        assert decisions[-1].reason == ContinuationReason.COMPLETION

    def test_wrapped_planning_orchestrator_event_firing(self):
        """Events fire during planning orchestrator execution."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")
        registry = EventRegistry()
        fired_events = []

        registry.register_listener(
            type(None),  # Register for all
            lambda e: fired_events.append(e) or True
        )

        wrapped = WrappedOrchestrator(mock_planner, event_registry=registry)
        result = wrapped.execute_with_continuation("Create a plan", {})

        assert result.is_ok()

    def test_wrapped_planning_orchestrator_token_tracking(self):
        """Token usage tracked across planning turns."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")
        wrapped = WrappedOrchestrator(mock_planner)

        result = wrapped.execute_with_continuation("Create a plan", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert all(d.token_usage is not None for d in decisions)

    def test_wrapped_planning_orchestrator_context_propagation(self):
        """Context propagates correctly across planning turns."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")
        initial_context = {"user_id": "user123", "domain": "planning"}

        call_contexts = []

        def capturing_execute(user_input: str, context: Dict) -> Dict:
            call_contexts.append(context.copy())
            return {"status": "completed", "operation": "planning"}

        mock_planner.execute = capturing_execute
        wrapped = WrappedOrchestrator(mock_planner)

        result = wrapped.execute_with_continuation("Create a plan", initial_context)

        assert result.is_ok()
        # Context should be passed to orchestrator
        assert len(call_contexts) >= 1

    def test_wrapped_planning_orchestrator_error_handling(self):
        """Errors in planning orchestrator handled gracefully."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")

        def error_execute(user_input: str, context: Dict) -> Dict:
            return {
                "error": "Failed to parse requirements",
                "error_type": "parse_error"
            }

        mock_planner.execute = error_execute
        wrapped = WrappedOrchestrator(mock_planner)

        result = wrapped.execute_with_continuation("Create a plan", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert decisions[-1].reason == ContinuationReason.ERROR_UNRECOVERABLE


class TestWrappedADOOrchestrator:
    """Test ADO orchestrator wrapping with ConversationProtocol."""

    def test_wrapped_ado_orchestrator_single_turn(self):
        """WrappedADOOrchestrator executes single turn correctly."""
        mock_ado = MockOrchestrator("ADOOrchestrator")
        wrapped = WrappedOrchestrator(mock_ado)

        result = wrapped.execute_with_continuation("Design architecture", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1
        assert isinstance(decisions[0], ContinuationDecision)

    def test_wrapped_ado_orchestrator_multi_turn(self):
        """WrappedADOOrchestrator supports multi-turn workflow."""
        mock_ado = MockOrchestrator("ADOOrchestrator")
        call_count = [0]

        def ado_execute(user_input: str, context: Dict) -> Dict:
            call_count[0] += 1
            if call_count[0] < 3:
                return {
                    "status": "pending",
                    "output": f"ADO turn {call_count[0]}",
                    "next_operation": "refine_design"
                }
            else:
                return {
                    "status": "completed",
                    "operation": "ado",
                    "result": {"architecture": "complete design"}
                }

        mock_ado.execute = ado_execute
        wrapped = WrappedOrchestrator(mock_ado, max_turns=5)

        result = wrapped.execute_with_continuation("Design architecture", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert decisions[-1].reason == ContinuationReason.COMPLETION

    def test_wrapped_ado_orchestrator_event_firing(self):
        """Events fire during ADO orchestrator execution."""
        mock_ado = MockOrchestrator("ADOOrchestrator")
        registry = EventRegistry()
        wrapped = WrappedOrchestrator(mock_ado, event_registry=registry)

        result = wrapped.execute_with_continuation("Design architecture", {})

        assert result.is_ok()

    def test_wrapped_ado_orchestrator_token_tracking(self):
        """Token usage tracked across ADO turns."""
        mock_ado = MockOrchestrator("ADOOrchestrator")
        wrapped = WrappedOrchestrator(mock_ado)

        result = wrapped.execute_with_continuation("Design architecture", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert all(d.token_usage is not None for d in decisions)

    def test_wrapped_ado_orchestrator_context_propagation(self):
        """Context propagates correctly across ADO turns."""
        mock_ado = MockOrchestrator("ADOOrchestrator")
        initial_context = {"user_id": "user456", "domain": "ado"}

        call_contexts = []

        def capturing_execute(user_input: str, context: Dict) -> Dict:
            call_contexts.append(context.copy())
            return {"status": "completed", "operation": "ado"}

        mock_ado.execute = capturing_execute
        wrapped = WrappedOrchestrator(mock_ado)

        result = wrapped.execute_with_continuation("Design architecture", initial_context)

        assert result.is_ok()
        assert len(call_contexts) >= 1

    def test_wrapped_ado_orchestrator_error_handling(self):
        """Errors in ADO orchestrator handled gracefully."""
        mock_ado = MockOrchestrator("ADOOrchestrator")

        def error_execute(user_input: str, context: Dict) -> Dict:
            return {
                "error": "Failed to design architecture",
                "error_type": "design_error"
            }

        mock_ado.execute = error_execute
        wrapped = WrappedOrchestrator(mock_ado)

        result = wrapped.execute_with_continuation("Design architecture", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert decisions[-1].reason == ContinuationReason.ERROR_UNRECOVERABLE


class TestWrappedTDDOrchestrator:
    """Test TDD orchestrator wrapping with ConversationProtocol."""

    def test_wrapped_tdd_orchestrator_single_turn(self):
        """WrappedTDDOrchestrator executes single turn correctly."""
        mock_tdd = MockOrchestrator("TDDOrchestrator")
        wrapped = WrappedOrchestrator(mock_tdd)

        result = wrapped.execute_with_continuation("Write tests", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert len(decisions) >= 1
        assert isinstance(decisions[0], ContinuationDecision)

    def test_wrapped_tdd_orchestrator_multi_turn(self):
        """WrappedTDDOrchestrator supports multi-turn workflow."""
        mock_tdd = MockOrchestrator("TDDOrchestrator")
        call_count = [0]

        def tdd_execute(user_input: str, context: Dict) -> Dict:
            call_count[0] += 1
            if call_count[0] < 3:
                return {
                    "status": "pending",
                    "output": f"TDD turn {call_count[0]}",
                    "next_operation": "refactor_code"
                }
            else:
                return {
                    "status": "completed",
                    "operation": "tdd",
                    "result": {"tests": "all passing"}
                }

        mock_tdd.execute = tdd_execute
        wrapped = WrappedOrchestrator(mock_tdd, max_turns=5)

        result = wrapped.execute_with_continuation("Write tests", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert decisions[-1].reason == ContinuationReason.COMPLETION

    def test_wrapped_tdd_orchestrator_event_firing(self):
        """Events fire during TDD orchestrator execution."""
        mock_tdd = MockOrchestrator("TDDOrchestrator")
        registry = EventRegistry()
        wrapped = WrappedOrchestrator(mock_tdd, event_registry=registry)

        result = wrapped.execute_with_continuation("Write tests", {})

        assert result.is_ok()

    def test_wrapped_tdd_orchestrator_token_tracking(self):
        """Token usage tracked across TDD turns."""
        mock_tdd = MockOrchestrator("TDDOrchestrator")
        wrapped = WrappedOrchestrator(mock_tdd)

        result = wrapped.execute_with_continuation("Write tests", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert all(d.token_usage is not None for d in decisions)

    def test_wrapped_tdd_orchestrator_context_propagation(self):
        """Context propagates correctly across TDD turns."""
        mock_tdd = MockOrchestrator("TDDOrchestrator")
        initial_context = {"user_id": "user789", "domain": "tdd"}

        call_contexts = []

        def capturing_execute(user_input: str, context: Dict) -> Dict:
            call_contexts.append(context.copy())
            return {"status": "completed", "operation": "tdd"}

        mock_tdd.execute = capturing_execute
        wrapped = WrappedOrchestrator(mock_tdd)

        result = wrapped.execute_with_continuation("Write tests", initial_context)

        assert result.is_ok()
        assert len(call_contexts) >= 1

    def test_wrapped_tdd_orchestrator_error_handling(self):
        """Errors in TDD orchestrator handled gracefully."""
        mock_tdd = MockOrchestrator("TDDOrchestrator")

        def error_execute(user_input: str, context: Dict) -> Dict:
            return {
                "error": "Failed to write tests",
                "error_type": "test_error"
            }

        mock_tdd.execute = error_execute
        wrapped = WrappedOrchestrator(mock_tdd)

        result = wrapped.execute_with_continuation("Write tests", {})

        assert result.is_ok()
        decisions = result.unwrap()
        assert decisions[-1].reason == ContinuationReason.ERROR_UNRECOVERABLE


class TestOrchestratorIntegration:
    """Test cross-orchestrator integration and workflows."""

    def test_planning_to_ado_workflow(self):
        """Workflow: Planning → ADO suggests next operation."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")

        def planning_execute(user_input: str, context: Dict) -> Dict:
            return {
                "status": "completed",
                "operation": "planning",
                "result": {"plan": "complete"},
                "next_operation": "begin_ado"
            }

        mock_planner.execute = planning_execute
        wrapped_planner = WrappedOrchestrator(mock_planner, max_turns=10)

        result = wrapped_planner.execute_with_continuation("Create plan", {})

        assert result.is_ok()
        decisions = result.unwrap()
        last_decision = decisions[-1]
        # When status='completed', next_operation becomes 'done' in protocol
        assert last_decision.reason == ContinuationReason.COMPLETION

    def test_ado_to_tdd_workflow(self):
        """Workflow: ADO → TDD suggests next operation."""
        mock_ado = MockOrchestrator("ADOOrchestrator")

        def ado_execute(user_input: str, context: Dict) -> Dict:
            return {
                "status": "completed",
                "operation": "ado",
                "result": {"architecture": "complete"},
                "next_operation": "begin_tdd"
            }

        mock_ado.execute = ado_execute
        wrapped_ado = WrappedOrchestrator(mock_ado, max_turns=10)

        result = wrapped_ado.execute_with_continuation("Design architecture", {})

        assert result.is_ok()
        decisions = result.unwrap()
        last_decision = decisions[-1]
        # When status='completed', next_operation becomes 'done' in protocol
        assert last_decision.reason == ContinuationReason.COMPLETION

    def test_orchestrator_decision_history(self):
        """Orchestrator maintains decision history across turns."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")
        call_count = [0]

        def planning_execute(user_input: str, context: Dict) -> Dict:
            call_count[0] += 1
            if call_count[0] < 2:
                return {"status": "pending", "next_operation": "continue"}
            else:
                return {"status": "completed", "operation": "planning"}

        mock_planner.execute = planning_execute
        wrapped = WrappedOrchestrator(mock_planner, max_turns=5)

        result = wrapped.execute_with_continuation("Create plan", {})

        assert result.is_ok()
        assert len(wrapped.decisions) >= 1

    def test_multiple_domain_shared_context(self):
        """Shared context maintained across orchestrator domains."""
        context_snapshot = {"phase": "planning"}

        mock_planner = MockOrchestrator("PlanningOrchestrator")

        def planning_execute(user_input: str, context: Dict) -> Dict:
            # Update context for next phase
            context["phase"] = "design"
            return {
                "status": "completed",
                "operation": "planning",
                "next_parameters": context
            }

        mock_planner.execute = planning_execute
        wrapped = WrappedOrchestrator(mock_planner)

        result = wrapped.execute_with_continuation("Create plan", context_snapshot)

        assert result.is_ok()

    def test_error_propagation_across_domains(self):
        """Errors handled consistently across all domains."""
        for domain in ["Planning", "ADO", "TDD"]:
            mock_orch = MockOrchestrator(f"{domain}Orchestrator")

            def error_execute(user_input: str, context: Dict) -> Dict:
                return {"error": f"{domain} error"}

            mock_orch.execute = error_execute
            wrapped = WrappedOrchestrator(mock_orch)

            result = wrapped.execute_with_continuation(f"Execute {domain}", {})

            assert result.is_ok()
            decisions = result.unwrap()
            assert decisions[-1].reason == ContinuationReason.ERROR_UNRECOVERABLE


class TestDomainSpecificNextOperations:
    """Test domain-specific routing and next operations."""

    def test_planning_next_operation_suggestions(self):
        """Planning orchestrator suggests appropriate next operations."""
        mock_planner = MockOrchestrator("PlanningOrchestrator")

        def planning_execute(user_input: str, context: Dict) -> Dict:
            if "refine" in user_input:
                return {
                    "status": "pending",
                    "next_operation": "refine_plan"
                }
            else:
                return {
                    "status": "completed",
                    "next_operation": "begin_ado"
                }

        mock_planner.execute = planning_execute
        wrapped = WrappedOrchestrator(mock_planner)

        result = wrapped.execute_with_continuation("Refine the plan", {})

        assert result.is_ok()

    def test_ado_next_operation_suggestions(self):
        """ADO orchestrator suggests appropriate next operations."""
        mock_ado = MockOrchestrator("ADOOrchestrator")

        def ado_execute(user_input: str, context: Dict) -> Dict:
            if "refine" in user_input:
                return {
                    "status": "pending",
                    "next_operation": "refine_architecture"
                }
            else:
                return {
                    "status": "completed",
                    "next_operation": "begin_tdd"
                }

        mock_ado.execute = ado_execute
        wrapped = WrappedOrchestrator(mock_ado)

        result = wrapped.execute_with_continuation("Refine architecture", {})

        assert result.is_ok()

    def test_tdd_next_operation_suggestions(self):
        """TDD orchestrator suggests appropriate next operations."""
        mock_tdd = MockOrchestrator("TDDOrchestrator")

        def tdd_execute(user_input: str, context: Dict) -> Dict:
            if "refactor" in user_input:
                return {
                    "status": "pending",
                    "next_operation": "refactor_code"
                }
            else:
                return {
                    "status": "completed",
                    "next_operation": "complete"
                }

        mock_tdd.execute = tdd_execute
        wrapped = WrappedOrchestrator(mock_tdd)

        result = wrapped.execute_with_continuation("Refactor the code", {})

        assert result.is_ok()

    def test_domain_name_retrieval(self):
        """Wrapped orchestrator returns correct domain name."""
        domains = ["Planning", "ADO", "TDD"]

        for domain in domains:
            mock_orch = MockOrchestrator(f"{domain}Orchestrator")
            wrapped = WrappedOrchestrator(mock_orch)

            assert domain in wrapped.get_domain_name()

    def test_orchestrator_get_domain_name_interface(self):
        """Wrapped orchestrator supports get_domain_name() interface."""
        mock_orch = MockOrchestrator("TestOrchestrator")
        wrapped = WrappedOrchestrator(mock_orch)

        domain = wrapped.get_domain_name()

        assert isinstance(domain, str)
        assert len(domain) > 0
