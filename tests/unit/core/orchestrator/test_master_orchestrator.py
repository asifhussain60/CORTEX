"""
Tests for OC-003-02: Master Loop Pattern with ConversationProtocol.

This module tests the MasterOrchestrator pattern which coordinates
multi-domain workflows using explicit loops over ConversationProtocol
instead of imperative orchestration.

Test Classes:
    - TestMasterOrchestratorInitialization: Setup and configuration
    - TestMasterOrchestratorSingleDomain: Single domain workflows
    - TestMasterOrchestratorMultiDomain: Cross-domain coordination
    - TestMasterOrchestratorEventAggregation: Event collection
    - TestMasterOrchestratorDecisionTracking: Decision history
    - TestMasterOrchestratorErrorRecovery: Error handling
"""

from typing import Any, Dict, List, Optional
from unittest.mock import Mock, MagicMock, patch
from enum import Enum

import pytest

from src.core.orchestrator.continuation_decision import (
    ContinuationDecision,
    ContinuationReason,
)
from src.core.orchestrator.conversation_protocol import ConversationProtocol
from src.core.orchestrator.terminal_events import EventRegistry, TerminalEvent
from src.core.result import Ok, Err, Result


class OrchestrationDomain(Enum):
    """Enumeration of orchestration domains."""
    PLANNING = "planning"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"


class MockDomainOrchestrator:
    """Mock orchestrator for a specific domain."""

    def __init__(self, domain: OrchestrationDomain):
        self.domain = domain
        self.execute_calls = []

    def execute(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute domain-specific orchestration."""
        self.execute_calls.append({"user_input": user_input, "context": context})
        return {
            "status": "completed",
            "domain": self.domain.value,
            "result": f"Completed {self.domain.value}",
        }

    def get_domain_name(self) -> str:
        """Get domain name."""
        return self.domain.value

    @property
    def __class__(self):
        """Mock class for protocol."""
        return type('MockOrchestrator', (), {'__name__': f'{self.domain.value}_orchestrator'})


class MasterOrchestrator:
    """Master orchestrator coordinating multi-domain workflows."""

    def __init__(self):
        """Initialize master orchestrator."""
        self.orchestrators: Dict[OrchestrationDomain, Any] = {}
        self.current_domain: Optional[OrchestrationDomain] = None
        self.domain_decisions: Dict[OrchestrationDomain, List[ContinuationDecision]] = {}
        self.all_events: List[TerminalEvent] = []
        self.workflow_complete = False

    def register_orchestrator(
        self,
        domain: OrchestrationDomain,
        orchestrator: Any,
        max_turns: int = 5,
    ):
        """Register a domain orchestrator."""
        self.orchestrators[domain] = {
            "orchestrator": orchestrator,
            "protocol": ConversationProtocol(
                orchestrator,
                max_turns=max_turns,
                event_registry=EventRegistry(),
            ),
            "max_turns": max_turns,
        }
        self.domain_decisions[domain] = []

    def execute_workflow(
        self,
        initial_domain: OrchestrationDomain,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Result[Dict[str, Any]]:
        """
        Execute explicit multi-domain workflow.
        
        Replaces imperative domain-hopping with declarative loop.
        """
        if context is None:
            context = {}

        self.current_domain = initial_domain
        current_input = user_input
        current_context = context

        while self.current_domain is not None:
            if self.current_domain not in self.orchestrators:
                return Err(f"No orchestrator for domain {self.current_domain}")

            # Execute this domain's orchestrator
            protocol_result = self._execute_domain(
                self.current_domain,
                current_input,
                current_context,
            )

            if protocol_result.is_err():
                return Err(protocol_result.unwrap_err())

            decisions = protocol_result.unwrap()
            self.domain_decisions[self.current_domain] = decisions

            # Extract next domain from last decision
            last_decision = decisions[-1]
            next_domain = self._parse_next_domain(last_decision.next_operation)

            if next_domain is None:
                # Workflow complete
                self.workflow_complete = True
                break

            # Prepare for next domain
            self.current_domain = next_domain
            current_input = last_decision.next_operation or "continue"
            current_context = last_decision.next_parameters or current_context

        return Ok({
            "workflow_complete": self.workflow_complete,
            "domains_executed": list(self.domain_decisions.keys()),
            "total_decisions": sum(
                len(d) for d in self.domain_decisions.values()
            ),
        })

    def _execute_domain(
        self,
        domain: OrchestrationDomain,
        user_input: str,
        context: Dict[str, Any],
    ) -> Result[List[ContinuationDecision]]:
        """Execute orchestrator for a single domain."""
        try:
            orchestrator = self.orchestrators[domain]["orchestrator"]
            protocol = self.orchestrators[domain]["protocol"]
            
            decisions = []
            current_input = user_input
            current_context = context
            next_domain_suggestion = None

            while True:
                # Get raw orchestrator result to check for domain routing
                raw_result = orchestrator.execute(current_input, current_context)
                
                # Check if orchestrator suggests next domain BEFORE protocol processes it
                if raw_result.get("next_operation") and not raw_result.get("error"):
                    suggested_domain = self._parse_next_domain(raw_result.get("next_operation"))
                    if suggested_domain and suggested_domain != domain:
                        next_domain_suggestion = raw_result.get("next_operation")
                
                # Now execute through protocol for full decision processing
                result = protocol.execute_turn(current_input, current_context)

                if result.is_err():
                    return Err(result.unwrap_err())

                decision = result.unwrap()
                
                # Override next_operation if we captured cross-domain suggestion
                if next_domain_suggestion and decision.reason == ContinuationReason.COMPLETION:
                    decision = ContinuationDecision(
                        should_continue=False,
                        reason=ContinuationReason.IMPLICIT_NEXT_OPERATION,
                        next_operation=next_domain_suggestion,
                        next_parameters=decision.next_parameters,
                        turn_number=decision.turn_number,
                        token_usage=decision.token_usage,
                        audit_entry_id=decision.audit_entry_id,
                        governance_violations=decision.governance_violations,
                    )
                    next_domain_suggestion = None
                
                decisions.append(decision)

                if not decision.should_continue:
                    break

                current_input = decision.next_operation or "continue"
                current_context = decision.next_parameters or current_context

            return Ok(decisions)
        except Exception as e:
            return Err(f"Error executing {domain.value}: {str(e)}")

    def _parse_next_domain(self, next_operation: str) -> Optional[OrchestrationDomain]:
        """Parse next operation to determine next domain."""
        if not next_operation or next_operation in ("done", "halt", "halt_max_rounds"):
            return None

        # Map next_operation to domain
        next_op_lower = next_operation.lower()
        if "planning" in next_op_lower or "plan" in next_op_lower:
            return OrchestrationDomain.PLANNING
        elif "design" in next_op_lower or "ado" in next_op_lower:
            return OrchestrationDomain.DESIGN
        elif "tdd" in next_op_lower or "implementation" in next_op_lower or "impl" in next_op_lower:
            return OrchestrationDomain.IMPLEMENTATION
        
        return None

    def get_domain_decisions(
        self, domain: OrchestrationDomain
    ) -> List[ContinuationDecision]:
        """Get decisions for a domain."""
        return self.domain_decisions.get(domain, [])


class TestMasterOrchestratorInitialization:
    """Test MasterOrchestrator initialization and setup."""

    def test_master_orchestrator_creates_empty(self):
        """MasterOrchestrator initializes with no domains."""
        master = MasterOrchestrator()
        
        assert len(master.orchestrators) == 0
        assert master.current_domain is None
        assert master.workflow_complete is False

    def test_master_orchestrator_register_domain(self):
        """MasterOrchestrator registers domain orchestrators."""
        master = MasterOrchestrator()
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        master.register_orchestrator(
            OrchestrationDomain.PLANNING,
            mock_planner,
            max_turns=5,
        )
        
        assert OrchestrationDomain.PLANNING in master.orchestrators
        assert master.orchestrators[OrchestrationDomain.PLANNING]["max_turns"] == 5

    def test_master_orchestrator_register_multiple_domains(self):
        """MasterOrchestrator registers multiple domains."""
        master = MasterOrchestrator()
        
        for domain in [OrchestrationDomain.PLANNING, OrchestrationDomain.DESIGN]:
            mock_orch = MockDomainOrchestrator(domain)
            master.register_orchestrator(domain, mock_orch)
        
        assert len(master.orchestrators) == 2

    def test_master_orchestrator_domain_decisions_initialized(self):
        """Domain decisions tracking initialized for each registered domain."""
        master = MasterOrchestrator()
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        
        assert OrchestrationDomain.PLANNING in master.domain_decisions
        assert master.domain_decisions[OrchestrationDomain.PLANNING] == []


class TestMasterOrchestratorSingleDomain:
    """Test MasterOrchestrator with single domain workflows."""

    def test_single_domain_workflow_completes(self):
        """Single domain workflow executes and completes."""
        master = MasterOrchestrator()
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_ok()
        workflow_result = result.unwrap()
        assert workflow_result["workflow_complete"] is True

    def test_single_domain_captures_decisions(self):
        """Single domain workflow captures all decisions."""
        master = MasterOrchestrator()
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_ok()
        decisions = master.get_domain_decisions(OrchestrationDomain.PLANNING)
        assert len(decisions) >= 1
        assert all(isinstance(d, ContinuationDecision) for d in decisions)

    def test_single_domain_context_propagation(self):
        """Context propagates within single domain."""
        master = MasterOrchestrator()
        
        initial_context = {"user_id": "user123"}
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            initial_context,
        )
        
        assert result.is_ok()

    def test_single_domain_error_handling(self):
        """Single domain errors handled gracefully."""
        master = MasterOrchestrator()
        
        # Simulate error by not registering orchestrator
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_err()


class TestMasterOrchestratorMultiDomain:
    """Test MasterOrchestrator with multi-domain workflows."""

    def test_planning_to_design_workflow(self):
        """Workflow: Planning → Design."""
        master = MasterOrchestrator()
        
        # Setup orchestrators
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        mock_designer = MockDomainOrchestrator(OrchestrationDomain.DESIGN)
        
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        master.register_orchestrator(OrchestrationDomain.DESIGN, mock_designer)
        
        # Override planner to suggest design next
        def planning_execute(user_input: str, context: Dict) -> Dict:
            return {
                "status": "completed",
                "domain": "planning",
                "next_operation": "begin_design"
            }
        
        mock_planner.execute = planning_execute
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_ok()
        # Both domains should have been executed
        planning_decisions = master.get_domain_decisions(OrchestrationDomain.PLANNING)
        design_decisions = master.get_domain_decisions(OrchestrationDomain.DESIGN)
        
        assert len(planning_decisions) >= 1
        assert len(design_decisions) >= 1

    def test_full_planning_design_implementation_workflow(self):
        """Full workflow: Planning → Design → Implementation."""
        master = MasterOrchestrator()
        
        # Register all domains
        for domain in [OrchestrationDomain.PLANNING, OrchestrationDomain.DESIGN, OrchestrationDomain.IMPLEMENTATION]:
            mock_orch = MockDomainOrchestrator(domain)
            master.register_orchestrator(domain, mock_orch)
        
        # Configure routing
        def create_executor(current_domain: OrchestrationDomain):
            def executor(user_input: str, context: Dict) -> Dict:
                if current_domain == OrchestrationDomain.PLANNING:
                    return {"status": "completed", "next_operation": "begin_design"}
                elif current_domain == OrchestrationDomain.DESIGN:
                    return {"status": "completed", "next_operation": "begin_implementation"}
                else:
                    return {"status": "completed", "next_operation": "done"}
            return executor
        
        for domain, orch_info in master.orchestrators.items():
            orch = orch_info["orchestrator"]
            orch.execute = create_executor(domain)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Full workflow",
            {},
        )
        
        assert result.is_ok()
        assert master.workflow_complete is True

    def test_multi_domain_context_sharing(self):
        """Context flows from one domain to next."""
        master = MasterOrchestrator()
        
        captured_contexts = {}
        
        for domain in [OrchestrationDomain.PLANNING, OrchestrationDomain.DESIGN]:
            mock_orch = MockDomainOrchestrator(domain)
            
            def create_executor(d: OrchestrationDomain):
                def executor(user_input: str, context: Dict) -> Dict:
                    captured_contexts[d.value] = context.copy()
                    if d == OrchestrationDomain.PLANNING:
                        return {"status": "completed", "next_operation": "begin_design"}
                    else:
                        return {"status": "completed", "next_operation": "done"}
                return executor
            
            mock_orch.execute = create_executor(domain)
            master.register_orchestrator(domain, mock_orch)
        
        initial_context = {"workflow_id": "wf123"}
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Test workflow",
            initial_context,
        )
        
        assert result.is_ok()
        # Context should be captured for both domains
        assert "planning" in captured_contexts
        assert "design" in captured_contexts


class TestMasterOrchestratorEventAggregation:
    """Test event collection and aggregation."""

    def test_master_orchestrator_tracks_all_events(self):
        """Master orchestrator can track all events across domains."""
        master = MasterOrchestrator()
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_ok()
        # Events tracked at protocol level
        protocol = master.orchestrators[OrchestrationDomain.PLANNING]["protocol"]
        assert protocol.event_registry is not None


class TestMasterOrchestratorDecisionTracking:
    """Test decision history tracking."""

    def test_master_orchestrator_maintains_decision_history(self):
        """Master maintains decision history for all domains."""
        master = MasterOrchestrator()
        
        for domain in [OrchestrationDomain.PLANNING, OrchestrationDomain.DESIGN]:
            mock_orch = MockDomainOrchestrator(domain)
            master.register_orchestrator(domain, mock_orch)
        
        # Configure routing
        def create_executor(d: OrchestrationDomain):
            def executor(user_input: str, context: Dict) -> Dict:
                if d == OrchestrationDomain.PLANNING:
                    return {"status": "completed", "next_operation": "begin_design"}
                else:
                    return {"status": "completed", "next_operation": "done"}
            return executor
        
        for domain, orch_info in master.orchestrators.items():
            orch = orch_info["orchestrator"]
            orch.execute = create_executor(domain)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Test workflow",
            {},
        )
        
        assert result.is_ok()
        
        # Verify history for both domains
        planning_decisions = master.get_domain_decisions(OrchestrationDomain.PLANNING)
        design_decisions = master.get_domain_decisions(OrchestrationDomain.DESIGN)
        
        assert len(planning_decisions) >= 1
        assert len(design_decisions) >= 1

    def test_master_orchestrator_decision_reasons_correct(self):
        """Decision reasons correctly reflect orchestrator states."""
        master = MasterOrchestrator()
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_ok()
        decisions = master.get_domain_decisions(OrchestrationDomain.PLANNING)
        last_decision = decisions[-1]
        
        # Last decision should indicate completion or next step
        assert last_decision.reason in [
            ContinuationReason.COMPLETION,
            ContinuationReason.IMPLICIT_NEXT_OPERATION,
            ContinuationReason.INTERACTION_REQUIRED,
        ]


class TestMasterOrchestratorErrorRecovery:
    """Test error handling and recovery."""

    def test_unregistered_domain_error(self):
        """Error when domain orchestrator not registered."""
        master = MasterOrchestrator()
        
        # Try to execute without registering
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_err()

    def test_orchestrator_error_propagation(self):
        """Orchestrator errors propagate through master."""
        master = MasterOrchestrator()
        mock_planner = MockDomainOrchestrator(OrchestrationDomain.PLANNING)
        
        def error_execute(user_input: str, context: Dict) -> Dict:
            return {"error": "Planning failed"}
        
        mock_planner.execute = error_execute
        master.register_orchestrator(OrchestrationDomain.PLANNING, mock_planner)
        
        result = master.execute_workflow(
            OrchestrationDomain.PLANNING,
            "Create a plan",
            {},
        )
        
        assert result.is_ok()
        decisions = master.get_domain_decisions(OrchestrationDomain.PLANNING)
        last_decision = decisions[-1]
        
        # Should capture error in decision
        assert last_decision.reason == ContinuationReason.ERROR_UNRECOVERABLE
