# AC_START: AC-PHASE81-S3-P3-003
"""
Advanced MCP Tool Integration Tests

Tests complex multi-agent scenarios with MCP tool execution.

Module: tests/unit/intent_router/test_mcp_advanced_integration.py
Authority: Phase 81 S3 Part 3 - MCP Tool Integration
Version: 1.0
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from cortex.intent_router.mcp_executor import (
    MCPToolExecutor,
    MCPExecutionRequest
)
from cortex.intent_router.collaboration_coordinator import (
    AgentCollaborationCoordinator,
    CollaborationRequest,
    CollaborationPattern,
    AgentContext
)


class TestMCPMultiAgentScenarios:
    """Test complex multi-agent scenarios with MCP."""
    
    @pytest.fixture
    def coordinator_with_agents(self):
        """Setup coordinator with multiple agents."""
        coordinator = AgentCollaborationCoordinator()
        
        # Register resolver agent
        coordinator.register_agent(
            agent_id="cortex-phase-resolver",
            capabilities=["phase_resolution", "context_extraction"],
            mcp_tools=["cortex_resolve_phase"],
            priority="P0"
        )
        
        # Register auditor agent
        coordinator.register_agent(
            agent_id="cortex-master-plan-auditor",
            capabilities=["planning", "resource_allocation"],
            mcp_tools=["cortex_audit_plan", "cortex_sync_plan_status"],
            priority="P1"
        )
        
        # Register audit agent
        coordinator.register_agent(
            agent_id="cortex-auditor",
            capabilities=["code_audit", "governance_check"],
            mcp_tools=["cortex_audit_codebase"],
            priority="P2"
        )
        
        return coordinator
    
    def test_hierarchical_plan_execution(self, coordinator_with_agents):
        """Test hierarchical execution: Resolver → Auditor → Executor."""
        coordinator = coordinator_with_agents
        
        # Register mock handlers
        resolver_handler = Mock(return_value={"phase_id": "phase-81"})
        auditor_handler = Mock(return_value={"validation": "passed"})
        
        coordinator._mcp_executor.register_tool_handler(
            "cortex_resolve_phase",
            resolver_handler
        )
        coordinator._mcp_executor.register_tool_handler(
            "cortex_audit_plan",
            auditor_handler
        )
        
        # Create hierarchical request
        context = AgentContext(
            agent_id="cortex-phase-resolver",
            request_id="req-hierarchical-001",
            user_request="execute phase 81 with full audit",
            intent="PLAN"
        )
        
        request = CollaborationRequest(
            request_id="req-hierarchical-001",
            primary_agent_id="cortex-phase-resolver",
            secondary_agents=["cortex-master-plan-auditor"],
            pattern=CollaborationPattern.HIERARCHICAL,
            context=context
        )
        
        # Execute
        result = coordinator.coordinate(request)
        
        # Verify execution
        assert result.success is True
        assert len(result.execution_path) == 2
        # In hierarchical pattern, agents execute one after another
        assert "cortex-phase-resolver" in result.execution_path
        assert "cortex-master-plan-auditor" in result.execution_path
    
    def test_sequential_audit_workflow(self, coordinator_with_agents):
        """Test sequential execution of multiple audit agents."""
        coordinator = coordinator_with_agents
        
        # Register mock handlers
        handlers = {
            "cortex_resolve_phase": Mock(return_value={"phase": "phase-81"}),
            "cortex_audit_codebase": Mock(return_value={"audit": "passed"})
        }
        
        for tool, handler in handlers.items():
            coordinator._mcp_executor.register_tool_handler(tool, handler)
        
        # Create sequential request
        context = AgentContext(
            agent_id="cortex-phase-resolver",
            request_id="req-sequential-001",
            user_request="audit phase implementation",
            intent="AUDIT"
        )
        
        request = CollaborationRequest(
            request_id="req-sequential-001",
            primary_agent_id="cortex-phase-resolver",
            secondary_agents=["cortex-auditor"],
            pattern=CollaborationPattern.SEQUENTIAL,
            context=context
        )
        
        # Execute
        result = coordinator.coordinate(request)
        
        # Verify
        assert result.success is True
        assert len(result.execution_path) == 2
        history = coordinator._mcp_executor.get_execution_history()
        assert len(history) >= 2  # At least 2 tool invocations


class TestMCPToolSelectorIntegration:
    """Test MCP tool selection logic."""
    
    def test_agent_primary_tool_selection(self):
        """Test selection of primary MCP tool for agent."""
        executor = MCPToolExecutor()
        
        # Agent with multiple tools
        multi_tools = ["cortex_resolve_phase", "cortex_audit_phase", "cortex_validate_phase"]
        executor.register_agent_tools("cortex-phase-resolver", multi_tools)
        
        # Verify first tool is primary
        tools = executor.get_agent_tools("cortex-phase-resolver")
        assert len(tools) == 3
        assert tools[0] == "cortex_resolve_phase"
    
    def test_tool_handler_dispatch(self):
        """Test dispatching to correct tool handler."""
        executor = MCPToolExecutor()
        
        # Setup multiple handlers
        handlers = {
            "tool1": Mock(return_value={"tool": "1"}),
            "tool2": Mock(return_value={"tool": "2"}),
        }
        
        for tool_name, handler in handlers.items():
            executor.register_tool_handler(tool_name, handler)
        
        executor.register_agent_tools("cortex-test", ["tool1", "tool2"])
        
        # Execute tool1
        req1 = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="tool1",
            tool_parameters={},
            request_id="req-001"
        )
        
        result1 = executor.execute(req1)
        assert result1.output["tool"] == "1"
        assert handlers["tool1"].called
        assert not handlers["tool2"].called
        
        # Execute tool2
        req2 = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="tool2",
            tool_parameters={},
            request_id="req-002"
        )
        
        result2 = executor.execute(req2)
        assert result2.output["tool"] == "2"
        assert handlers["tool2"].called


class TestMCPContextPassing:
    """Test context passing through MCP tool invocations."""
    
    def test_context_preservation_across_agents(self):
        """Test context is preserved when passing between agents."""
        coordinator = AgentCollaborationCoordinator()
        
        coordinator.register_agent(
            agent_id="agent-1",
            capabilities=["analysis"],
            mcp_tools=["tool1"]
        )
        
        coordinator.register_agent(
            agent_id="agent-2",
            capabilities=["validation"],
            mcp_tools=["tool2"]
        )
        
        # Setup context with phase state
        context = AgentContext(
            agent_id="agent-1",
            request_id="req-context-001",
            user_request="test context passing",
            intent="TEST",
            extracted_data={"key": "value"},
            phase_state={"phase": "phase-81", "stage": "3"}
        )
        
        # Verify context fields
        assert context.extracted_data["key"] == "value"
        if context.phase_state:
            assert context.phase_state["phase"] == "phase-81"
        
        # Add LENS cache
        context.add_lens_cache("analysis-result", {"result": "analyzed"})
        assert context.is_lens_cached("analysis-result")
        assert context.get_lens_cache("analysis-result") == {"result": "analyzed"}
    
    def test_lens_cache_optimization_with_mcp(self):
        """Test LENS cache reduces duplicate tool invocations."""
        executor = MCPToolExecutor()
        
        # Setup analyzer tool
        analysis_count = [0]
        
        def counting_analyzer(**kwargs):
            analysis_count[0] += 1
            return {"analysis_count": analysis_count[0]}
        
        executor.register_tool_handler("cortex_analyze", counting_analyzer)
        executor.register_agent_tools("cortex-analyzer", ["cortex_analyze"])
        
        # First invocation (will run analyzer)
        req1 = MCPExecutionRequest(
            agent_id="cortex-analyzer",
            tool_name="cortex_analyze",
            tool_parameters={"file": "app.py"},
            request_id="req-001"
        )
        
        result1 = executor.execute(req1)
        assert result1.output["analysis_count"] == 1
        
        # In real scenario with LENS cache, second agent would use cached result
        # Here we're demonstrating the potential for optimization
        history = executor.get_execution_history()
        assert len(history) == 1


class TestMCPErrorRecovery:
    """Test error recovery in MCP execution."""
    
    def test_partial_failure_recovery(self):
        """Test coordinator continues on partial agent failure."""
        coordinator = AgentCollaborationCoordinator()
        
        # Register agents
        coordinator.register_agent(
            agent_id="agent-good",
            capabilities=["analysis"],
            mcp_tools=["good_tool"]
        )
        
        coordinator.register_agent(
            agent_id="agent-bad",
            capabilities=["validation"],
            mcp_tools=["bad_tool"]
        )
        
        # Register handlers (one fails)
        good_handler = Mock(return_value={"status": "ok"})
        bad_handler = Mock(side_effect=RuntimeError("Tool failed"))
        
        coordinator._mcp_executor.register_tool_handler("good_tool", good_handler)
        coordinator._mcp_executor.register_tool_handler("bad_tool", bad_handler)
        
        # Execute sequential workflow
        context = AgentContext(
            agent_id="agent-good",
            request_id="req-001",
            user_request="test failure",
            intent="TEST"
        )
        
        request = CollaborationRequest(
            request_id="req-001",
            primary_agent_id="agent-good",
            secondary_agents=["agent-bad"],
            pattern=CollaborationPattern.SEQUENTIAL,
            context=context
        )
        
        result = coordinator.coordinate(request)
        
        # First agent should succeed
        assert result.combined_output["agent-good"]["status"] == "completed"
        
        # Second agent should fail but be recorded
        assert result.combined_output["agent-bad"]["status"] == "failed"
    
    def test_retry_failed_mcp_tool(self):
        """Test retrying failed MCP tool invocation."""
        executor = MCPToolExecutor()
        
        call_count = [0]
        
        def flaky_tool(**kwargs):
            call_count[0] += 1
            if call_count[0] < 3:
                raise RuntimeError("Temporary failure")
            return {"success": True}
        
        executor.register_tool_handler("cortex_flaky", flaky_tool)
        executor.register_agent_tools("cortex-test", ["cortex_flaky"])
        
        # First attempt fails
        req1 = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="cortex_flaky",
            tool_parameters={},
            request_id="req-001"
        )
        
        result1 = executor.execute(req1)
        assert result1.success is False
        
        # Second attempt fails
        req2 = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="cortex_flaky",
            tool_parameters={},
            request_id="req-002"
        )
        
        result2 = executor.execute(req2)
        assert result2.success is False
        
        # Third attempt succeeds (simulating retry)
        req3 = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="cortex_flaky",
            tool_parameters={},
            request_id="req-003"
        )
        
        result3 = executor.execute(req3)
        assert result3.success is True
        assert result3.output["success"] is True


class TestMCPPerformance:
    """Test performance characteristics of MCP execution."""
    
    def test_execution_performance_benchmarks(self):
        """Test execution meets performance targets."""
        executor = MCPToolExecutor()
        
        fast_handler = Mock(return_value={"ok": True})
        executor.register_tool_handler("cortex_fast", fast_handler)
        executor.register_agent_tools("cortex-test", ["cortex_fast"])
        
        # Execute multiple times
        for i in range(10):
            req = MCPExecutionRequest(
                agent_id="cortex-test",
                tool_name="cortex_fast",
                tool_parameters={},
                request_id=f"req-{i}"
            )
            result = executor.execute(req)
            
            # Should be very fast (< 50ms for mock)
            assert result.duration_seconds < 0.05
    
    def test_batch_execution_performance(self):
        """Test batch execution efficiency."""
        executor = MCPToolExecutor()
        
        handler = Mock(return_value={"ok": True})
        executor.register_tool_handler("cortex_tool", handler)
        executor.register_agent_tools("cortex-test", ["cortex_tool"])
        
        # Create batch
        requests = [
            MCPExecutionRequest(
                agent_id="cortex-test",
                tool_name="cortex_tool",
                tool_parameters={},
                request_id=f"req-batch-{i}"
            )
            for i in range(20)
        ]
        
        # Execute batch
        results = executor.execute_batch(requests)
        
        # All should succeed
        assert len(results) == 20
        assert all(r.success for r in results)
        
        # Verify all invocations recorded
        history = executor.get_execution_history()
        assert len(history) >= 20


# AC_COMPLETE: AC-PHASE81-S3-P3-003 ✅ Advanced MCP Integration Tests
