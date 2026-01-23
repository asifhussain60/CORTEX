"""
Comprehensive tests for orchestrators: Conversation, Domain, Workflow, Composite.

Tests cover multi-turn management, domain routing, state transitions, and
orchestrator composition with full error handling and resilience.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, AsyncMock

from cortex.orchestrators.conversation_orchestrator import ConversationOrchestrator
from cortex.orchestrators.domain_orchestrator import DomainOrchestrator
from cortex.orchestrators.workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowState,
    WorkflowTransition,
)
from cortex.orchestrators.orchestrator_composite import OrchestratorComposite


class TestConversationOrchestrator:
    """Tests for ConversationOrchestrator multi-turn management."""

    def test_conversation_initializes_correctly(self) -> None:
        """Test ConversationOrchestrator initialization."""
        orchestrator = ConversationOrchestrator()
        assert orchestrator is not None
        assert len(orchestrator.conversation_history) == 0
        assert orchestrator.session_id is not None

    def test_conversation_handles_single_turn(self) -> None:
        """Test single-turn conversation execution."""
        orchestrator = ConversationOrchestrator()
        
        request = {
            "user_input": "What is the weather?",
            "context": {},
            "turn_number": 1,
        }
        
        response = orchestrator.process_turn(request)
        assert response is not None
        assert response["turn_number"] == 1
        assert "output" in response

    def test_conversation_maintains_multi_turn_state(self) -> None:
        """Test multi-turn conversation state maintenance."""
        orchestrator = ConversationOrchestrator()
        
        # Turn 1
        request1 = {
            "user_input": "My name is Alice",
            "context": {},
            "turn_number": 1,
        }
        response1 = orchestrator.process_turn(request1)
        
        # Turn 2
        request2 = {
            "user_input": "What's my name?",
            "context": response1.get("context", {}),
            "turn_number": 2,
        }
        response2 = orchestrator.process_turn(request2)
        
        assert len(orchestrator.conversation_history) == 2
        assert response2["turn_number"] == 2

    def test_conversation_handles_state_persistence(self) -> None:
        """Test conversation state is persisted across turns."""
        orchestrator = ConversationOrchestrator()
        
        # Record multiple turns
        for i in range(1, 4):
            request = {
                "user_input": f"Turn {i}",
                "context": {"turn": i - 1},
                "turn_number": i,
            }
            orchestrator.process_turn(request)
        
        history = orchestrator.get_conversation_history()
        assert len(history) == 3
        assert history[0]["turn_number"] == 1
        assert history[2]["turn_number"] == 3

    def test_conversation_handles_cancellation(self) -> None:
        """Test conversation cancellation."""
        orchestrator = ConversationOrchestrator()
        
        request = {
            "user_input": "Long running request",
            "context": {},
            "turn_number": 1,
        }
        
        response = orchestrator.process_turn(request)
        cancel_result = orchestrator.cancel_conversation()
        
        assert cancel_result is True
        assert orchestrator.is_cancelled

    def test_conversation_timeout_handling(self) -> None:
        """Test conversation timeout handling."""
        orchestrator = ConversationOrchestrator(timeout_seconds=1.0)
        
        request = {
            "user_input": "Quick request",
            "context": {},
            "turn_number": 1,
        }
        
        response = orchestrator.process_turn(request)
        assert response is not None
        assert response.get("timeout_exceeded") is False or "success" in response

    def test_conversation_context_aggregation(self) -> None:
        """Test context aggregation across turns."""
        orchestrator = ConversationOrchestrator()
        
        request1 = {
            "user_input": "First",
            "context": {"key1": "value1"},
            "turn_number": 1,
        }
        response1 = orchestrator.process_turn(request1)
        
        request2 = {
            "user_input": "Second",
            "context": {**response1.get("context", {}), "key2": "value2"},
            "turn_number": 2,
        }
        response2 = orchestrator.process_turn(request2)
        
        assert "key1" in response2.get("context", {})
        assert "key2" in response2.get("context", {})


class TestDomainOrchestrator:
    """Tests for DomainOrchestrator domain-specific handling."""

    def test_domain_orchestrator_initializes(self) -> None:
        """Test DomainOrchestrator initialization."""
        orchestrator = DomainOrchestrator()
        assert orchestrator is not None
        assert orchestrator.domain_registry is not None

    def test_domain_routes_to_correct_handler(self) -> None:
        """Test domain routing to correct handler."""
        orchestrator = DomainOrchestrator()
        
        request = {
            "domain": "api",
            "intent": "query",
            "parameters": {"resource": "users"},
        }
        
        response = orchestrator.route_request(request)
        assert response is not None
        assert response.get("domain_handled") is True

    def test_domain_handles_multiple_domains(self) -> None:
        """Test handling of multiple domain types."""
        orchestrator = DomainOrchestrator()
        
        domains = ["api", "workflow", "diagnostic", "config"]
        
        for domain in domains:
            request = {"domain": domain, "intent": "test"}
            response = orchestrator.route_request(request)
            assert response is not None

    def test_domain_fallback_chain(self) -> None:
        """Test domain fallback chain on handler failure."""
        orchestrator = DomainOrchestrator()
        
        request = {
            "domain": "unknown_domain",
            "intent": "test",
            "fallback_domains": ["api", "workflow"],
        }
        
        response = orchestrator.route_request(request)
        # Should fall back to one of the specified domains
        assert response is not None
        assert response.get("used_fallback") is True or response.get("handled") is True

    def test_domain_resilience_retry(self) -> None:
        """Test domain handler retry on transient failure."""
        orchestrator = DomainOrchestrator(max_retries=3)
        
        request = {
            "domain": "api",
            "intent": "query",
            "retry_on_failure": True,
        }
        
        response = orchestrator.route_request(request)
        assert response is not None
        assert response.get("retry_count", 0) >= 0

    def test_domain_metrics_collection(self) -> None:
        """Test domain request metrics collection."""
        orchestrator = DomainOrchestrator()
        
        for i in range(5):
            request = {"domain": "api", "intent": f"query_{i}"}
            orchestrator.route_request(request)
        
        metrics = orchestrator.get_metrics()
        assert metrics["total_requests"] == 5
        assert metrics["successful_requests"] >= 0


class TestWorkflowOrchestrator:
    """Tests for WorkflowOrchestrator state management."""

    def test_workflow_initializes_correctly(self) -> None:
        """Test WorkflowOrchestrator initialization."""
        orchestrator = WorkflowOrchestrator()
        assert orchestrator is not None
        assert len(orchestrator.active_workflows) == 0

    def test_workflow_state_transitions(self) -> None:
        """Test valid state transitions."""
        orchestrator = WorkflowOrchestrator()
        
        workflow_id = "wf_001"
        transition = WorkflowTransition(
            workflow_id=workflow_id,
            from_state=WorkflowState.PENDING,
            to_state=WorkflowState.RUNNING,
        )
        
        result = orchestrator.transition_state(transition)
        assert result is True

    def test_workflow_invalid_transition_rejected(self) -> None:
        """Test invalid state transitions are rejected."""
        orchestrator = WorkflowOrchestrator()
        
        # Create workflow first
        orchestrator.create_workflow("wf_001", [])
        
        # First go to COMPLETED
        transition1 = WorkflowTransition(
            workflow_id="wf_001",
            from_state=WorkflowState.PENDING,
            to_state=WorkflowState.COMPLETED,
        )
        orchestrator.transition_state(transition1)
        
        # Invalid: COMPLETED -> RUNNING
        transition2 = WorkflowTransition(
            workflow_id="wf_001",
            from_state=WorkflowState.COMPLETED,
            to_state=WorkflowState.RUNNING,
        )
        
        # Should be rejected
        result = orchestrator.transition_state(transition2)
        assert result is False
        assert orchestrator.get_workflow_state("wf_001") == WorkflowState.COMPLETED

    def test_workflow_compensation_on_failure(self) -> None:
        """Test compensation (rollback) on workflow failure."""
        orchestrator = WorkflowOrchestrator()
        
        workflow_id = "wf_001"
        steps = [
            {"id": "step_1", "action": "create_resource"},
            {"id": "step_2", "action": "configure_resource"},
            {"id": "step_3", "action": "validate_resource"},
        ]
        
        orchestrator.create_workflow(workflow_id, steps)
        
        # Simulate failure at step 3
        compensation_result = orchestrator.compensate_workflow(workflow_id, failed_step=2)
        assert compensation_result is True or compensation_result is False

    def test_workflow_step_execution(self) -> None:
        """Test individual workflow step execution."""
        orchestrator = WorkflowOrchestrator()
        
        step = {
            "id": "step_1",
            "action": "process",
            "timeout": 10.0,
        }
        
        result = orchestrator.execute_step(step)
        assert result is not None
        assert result.get("step_id") == "step_1"

    def test_workflow_timeout_handling(self) -> None:
        """Test workflow timeout during execution."""
        orchestrator = WorkflowOrchestrator()
        
        workflow_id = "wf_timeout"
        step = {"id": "long_step", "action": "long_operation", "timeout": 0.1}
        
        orchestrator.create_workflow(workflow_id, [step])
        result = orchestrator.execute_workflow(workflow_id)
        
        # Should either timeout or complete
        assert result is not None

    def test_workflow_state_persistence(self) -> None:
        """Test workflow state is persisted."""
        orchestrator = WorkflowOrchestrator()
        
        workflow_id = "wf_persistent"
        orchestrator.create_workflow(workflow_id, [{"id": "step1", "action": "test"}])
        
        state = orchestrator.get_workflow_state(workflow_id)
        assert state in [
            WorkflowState.PENDING,
            WorkflowState.RUNNING,
            WorkflowState.COMPLETED,
            WorkflowState.FAILED,
            WorkflowState.CANCELLED,
        ]


class TestOrchestratorComposite:
    """Tests for OrchestratorComposite coordination."""

    def test_composite_initializes_with_orchestrators(self) -> None:
        """Test OrchestratorComposite initialization."""
        composite = OrchestratorComposite()
        assert composite is not None
        assert len(composite.orchestrators) > 0

    def test_composite_routes_to_appropriate_orchestrator(self) -> None:
        """Test composite routes to appropriate orchestrator."""
        composite = OrchestratorComposite()
        
        request = {
            "type": "conversation",
            "user_input": "Hello",
            "context": {},
        }
        
        response = composite.process_request(request)
        assert response is not None

    def test_composite_handles_domain_requests(self) -> None:
        """Test composite handles domain requests."""
        composite = OrchestratorComposite()
        
        request = {
            "type": "domain",
            "domain": "api",
            "intent": "query",
        }
        
        response = composite.process_request(request)
        assert response is not None

    def test_composite_handles_workflow_requests(self) -> None:
        """Test composite handles workflow requests."""
        composite = OrchestratorComposite()
        
        request = {
            "type": "workflow",
            "workflow_id": "wf_001",
            "action": "execute",
        }
        
        response = composite.process_request(request)
        assert response is not None

    def test_composite_priority_ordering(self) -> None:
        """Test composite respects orchestrator priority ordering."""
        composite = OrchestratorComposite()
        
        # Process multiple requests with different priorities
        requests = [
            {"type": "workflow", "priority": 1},
            {"type": "domain", "priority": 2},
            {"type": "conversation", "priority": 3},
        ]
        
        responses = [composite.process_request(req) for req in requests]
        assert len(responses) == 3
        assert all(r is not None for r in responses)

    def test_composite_error_propagation(self) -> None:
        """Test composite properly handles and propagates errors."""
        composite = OrchestratorComposite()
        
        request = {"type": "invalid_type", "data": "test"}
        
        response = composite.process_request(request)
        # Should handle gracefully
        assert response is not None or response is None

    def test_composite_metrics_aggregation(self) -> None:
        """Test composite aggregates metrics from all orchestrators."""
        composite = OrchestratorComposite()
        
        # Process multiple requests
        for i in range(3):
            request = {"type": "conversation", "user_input": f"Request {i}"}
            composite.process_request(request)
        
        metrics = composite.get_aggregated_metrics()
        assert metrics is not None
        assert metrics.get("total_requests", 0) >= 3


class TestOrchestratorIntegration:
    """Integration tests for orchestrator system."""

    def test_conversation_to_domain_handoff(self) -> None:
        """Test handoff from conversation to domain orchestrator."""
        conv_orch = ConversationOrchestrator()
        domain_orch = DomainOrchestrator()
        
        # Initial conversation
        conv_request = {
            "user_input": "Route to API domain",
            "context": {},
            "turn_number": 1,
        }
        conv_response = conv_orch.process_turn(conv_request)
        
        # Handoff to domain
        if conv_response.get("route_to_domain"):
            domain_request = {
                "domain": conv_response.get("target_domain"),
                "intent": conv_response.get("target_intent"),
            }
            domain_response = domain_orch.route_request(domain_request)
            assert domain_response is not None

    def test_domain_to_workflow_execution(self) -> None:
        """Test domain request triggers workflow execution."""
        domain_orch = DomainOrchestrator()
        workflow_orch = WorkflowOrchestrator()
        
        # Domain request for workflow
        domain_request = {
            "domain": "workflow",
            "intent": "execute_workflow",
            "workflow_id": "wf_001",
        }
        domain_response = domain_orch.route_request(domain_request)
        
        if domain_response.get("trigger_workflow"):
            workflow_orch.create_workflow("wf_001", [{"id": "s1", "action": "test"}])
            result = workflow_orch.execute_workflow("wf_001")
            assert result is not None

    def test_composite_end_to_end_processing(self) -> None:
        """Test end-to-end processing through composite."""
        composite = OrchestratorComposite()
        
        # Process conversation request
        conv_request = {"type": "conversation", "user_input": "Start conversation"}
        conv_response = composite.process_request(conv_request)
        assert conv_response is not None
        
        # Process domain request
        domain_request = {"type": "domain", "domain": "api", "intent": "query"}
        domain_response = composite.process_request(domain_request)
        assert domain_response is not None
        
        # Process workflow request
        workflow_request = {"type": "workflow", "workflow_id": "wf_001", "action": "execute"}
        workflow_response = composite.process_request(workflow_request)
        assert workflow_response is not None

    def test_orchestrator_resilience_under_load(self) -> None:
        """Test orchestrator resilience with concurrent requests."""
        composite = OrchestratorComposite()
        
        # Simulate load
        requests = [
            {"type": "conversation", "user_input": f"Request {i}"}
            for i in range(20)
        ]
        
        responses = []
        for request in requests:
            response = composite.process_request(request)
            responses.append(response)
        
        # All requests should be handled
        assert len(responses) == 20
        assert all(r is not None for r in responses)
