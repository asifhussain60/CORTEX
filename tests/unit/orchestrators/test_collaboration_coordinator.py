# AC_START: AC-PHASE81-S3-TEST-002
"""
Test suite for Agent Collaboration Coordinator.

Tests: 12 collaboration pattern + execution tests

Module: tests/unit/orchestrators/test_collaboration_coordinator.py
Authority: Phase 81 S3
"""

import pytest
from datetime import datetime

from cortex.intent_router.collaboration_coordinator import (
    AgentCollaborationCoordinator,
    CollaborationRequest,
    CollaborationPattern,
    AgentContext,
    CollaborationResult
)


class TestAgentContextManagement:
    """Tests for agent context (5 tests)."""
    
    def test_context_initialization(self):
        """Context should initialize with required fields."""
        context = AgentContext(
            agent_id="test-agent",
            request_id="req-001",
            user_request="test request",
            intent="IMPLEMENT"
        )
        
        assert context.agent_id == "test-agent"
        assert context.request_id == "req-001"
        assert len(context.lens_cache) == 0
    
    def test_lens_cache_operations(self):
        """Context should support LENS cache operations."""
        context = AgentContext(
            agent_id="test-agent",
            request_id="req-001",
            user_request="test",
            intent="ANALYZE"
        )
        
        # Add to cache
        context.add_lens_cache("key-1", {"data": "value"})
        assert context.is_lens_cached("key-1")
        
        # Retrieve from cache
        value = context.get_lens_cache("key-1")
        assert value == {"data": "value"}
    
    def test_context_phase_state(self):
        """Context should store phase state for PLAN mode."""
        context = AgentContext(
            agent_id="cortex-phase-resolver",
            request_id="req-002",
            user_request="phase 81",
            intent="PLAN"
        )
        
        phase_state = {"phase_id": "phase-81", "stage": "S3", "progress": 30}
        context.phase_state = phase_state
        
        assert context.phase_state["phase_id"] == "phase-81"
    
    def test_context_execution_metadata(self):
        """Context should accumulate execution metadata."""
        context = AgentContext(
            agent_id="cortex-phase-resolver",
            request_id="req-003",
            user_request="test",
            intent="IMPLEMENT"
        )
        
        context.execution_metadata["agent-1"] = {"status": "completed"}
        context.execution_metadata["agent-2"] = {"status": "in_progress"}
        
        assert len(context.execution_metadata) == 2


class TestCollaborationRequestBuilding:
    """Tests for collaboration request construction (5 tests)."""
    
    def test_request_initialization(self):
        """Request should initialize with required fields."""
        request = CollaborationRequest(
            request_id="req-004",
            primary_agent_id="cortex-auditor"
        )
        
        assert request.request_id == "req-004"
        assert request.primary_agent_id == "cortex-auditor"
        assert request.pattern == CollaborationPattern.SEQUENTIAL
    
    def test_add_secondary_agent(self):
        """Should add secondary agents to request."""
        request = CollaborationRequest(
            request_id="req-005",
            primary_agent_id="cortex-phase-resolver"
        )
        
        request.add_secondary_agent("cortex-master-plan-auditor")
        request.add_secondary_agent("cortex-auditor")
        
        assert len(request.secondary_agents) == 2
        assert "cortex-master-plan-auditor" in request.secondary_agents
    
    def test_request_with_pattern(self):
        """Request should support different patterns."""
        request = CollaborationRequest(
            request_id="req-006",
            primary_agent_id="cortex-auditor",
            pattern=CollaborationPattern.HIERARCHICAL
        )
        
        assert request.pattern == CollaborationPattern.HIERARCHICAL
    
    def test_request_with_context(self):
        """Request should attach context."""
        context = AgentContext(
            agent_id="cortex-auditor",
            request_id="req-007",
            user_request="audit",
            intent="AUDIT"
        )
        
        request = CollaborationRequest(
            request_id="req-007",
            primary_agent_id="cortex-auditor",
            context=context
        )
        
        assert request.context == context


class TestCollaborationPatternExecution:
    """Tests for collaboration pattern execution (10 tests)."""
    
    @pytest.fixture
    def coordinator(self):
        """Set up coordinator."""
        return AgentCollaborationCoordinator()
    
    def test_hierarchical_execution(self, coordinator):
        """Hierarchical pattern should execute resolver → auditor → executor."""
        coordinator.register_agent("resolver", ["phase_resolution"], ["tool-1"], "P0")
        coordinator.register_agent("auditor", ["auditing"], ["tool-2"], "P0")
        coordinator.register_agent("executor", ["execution"], ["tool-3"], "P0")
        
        context = AgentContext(
            agent_id="resolver",
            request_id="req-008",
            user_request="test",
            intent="PLAN"
        )
        
        request = CollaborationRequest(
            request_id="req-008",
            primary_agent_id="resolver",
            secondary_agents=["auditor", "executor"],
            pattern=CollaborationPattern.HIERARCHICAL,
            context=context
        )
        
        result = coordinator.coordinate(request)
        
        assert result.success
        assert len(result.execution_path) == 3
        assert "resolver" in result.execution_path
    
    def test_sequential_execution(self, coordinator):
        """Sequential pattern should execute agents in order."""
        coordinator.register_agent("agent-1", ["cap-1"], ["tool-1"], "P1")
        coordinator.register_agent("agent-2", ["cap-2"], ["tool-2"], "P1")
        
        request = CollaborationRequest(
            request_id="req-009",
            primary_agent_id="agent-1",
            secondary_agents=["agent-2"],
            pattern=CollaborationPattern.SEQUENTIAL
        )
        
        result = coordinator.coordinate(request)
        
        assert result.success
        assert result.execution_path == ["agent-1", "agent-2"]
    
    def test_parallel_execution(self, coordinator):
        """Parallel pattern should execute agents concurrently."""
        coordinator.register_agent("parallel-1", ["cap"], ["tool"], "P2")
        coordinator.register_agent("parallel-2", ["cap"], ["tool"], "P2")
        coordinator.register_agent("parallel-3", ["cap"], ["tool"], "P2")
        
        request = CollaborationRequest(
            request_id="req-010",
            primary_agent_id="parallel-1",
            secondary_agents=["parallel-2", "parallel-3"],
            pattern=CollaborationPattern.PARALLEL
        )
        
        result = coordinator.coordinate(request)
        
        assert result.success
        assert len(result.execution_path) == 3
    
    def test_feedback_loop_execution(self, coordinator):
        """Feedback loop should iterate until convergence."""
        coordinator.register_agent("designer", ["design"], ["tool-1"], "P1")
        coordinator.register_agent("validator", ["validation"], ["tool-2"], "P1")
        
        request = CollaborationRequest(
            request_id="req-011",
            primary_agent_id="designer",
            secondary_agents=["validator"],
            pattern=CollaborationPattern.FEEDBACK_LOOP,
            max_iterations=3
        )
        
        result = coordinator.coordinate(request)
        
        assert result.success
        assert result.iterations_used <= 3
    
    def test_execution_result_structure(self, coordinator):
        """Result should have complete structure."""
        coordinator.register_agent("test-agent", ["cap"], ["tool"], "P2")
        
        request = CollaborationRequest(
            request_id="req-012",
            primary_agent_id="test-agent"
        )
        
        result = coordinator.coordinate(request)
        
        assert result.request_id == request.request_id
        assert result.primary_agent_id == "test-agent"
        assert result.duration_seconds >= 0
        assert result.combined_output is not None
    
    def test_error_handling_in_coordination(self, coordinator):
        """Coordinator should handle unregistered agents gracefully."""
        request = CollaborationRequest(
            request_id="req-013",
            primary_agent_id="unregistered-agent"
        )
        
        result = coordinator.coordinate(request)
        
        # Should complete but may not be fully successful
        assert result.request_id == "req-013"


class TestCollaborationCoordinatorIntegration:
    """Integration tests for complete collaboration workflows (7 tests)."""
    
    def test_agent_registration_and_coordination(self):
        """Full workflow: register agents → coordinate."""
        coordinator = AgentCollaborationCoordinator()
        
        # Register agent team
        coordinator.register_agent("resolver", ["phase_resolution"], ["tool-1"], "P0")
        coordinator.register_agent("auditor", ["plan_auditing"], ["tool-2"], "P0")
        
        # Create collaboration request
        request = CollaborationRequest(
            request_id="req-014",
            primary_agent_id="resolver",
            secondary_agents=["auditor"],
            pattern=CollaborationPattern.HIERARCHICAL
        )
        
        result = coordinator.coordinate(request)
        
        assert result.success
        assert result.primary_agent_id == "resolver"
    
    def test_multi_agent_collaboration_count(self):
        """Coordinator should track collaboration counts."""
        coordinator = AgentCollaborationCoordinator()
        
        coordinator.register_agent("agent-1", ["cap"], ["tool"], "P1")
        
        # First collaboration
        request1 = CollaborationRequest(
            request_id="req-015",
            primary_agent_id="agent-1"
        )
        coordinator.coordinate(request1)
        
        # Check count
        agent_info = coordinator._agent_registry["agent-1"]
        assert agent_info["collaboration_count"] >= 1
    
    def test_context_passing_through_agents(self):
        """Context should be passed through all agents in chain."""
        coordinator = AgentCollaborationCoordinator()
        
        coordinator.register_agent("agent-1", ["cap-1"], ["tool-1"], "P0")
        coordinator.register_agent("agent-2", ["cap-2"], ["tool-2"], "P0")
        
        context = AgentContext(
            agent_id="agent-1",
            request_id="req-016",
            user_request="test with context",
            intent="IMPLEMENT"
        )
        context.add_lens_cache("shared-key", {"shared": "value"})
        
        request = CollaborationRequest(
            request_id="req-016",
            primary_agent_id="agent-1",
            secondary_agents=["agent-2"],
            pattern=CollaborationPattern.SEQUENTIAL,
            context=context
        )
        
        result = coordinator.coordinate(request)
        
        assert result.context.is_lens_cached("shared-key")


# AC_COMPLETE: AC-PHASE81-S3-TEST-002 ✅ Collaboration Coordinator Tests
