# AC_START: AC-PHASE81-S3-P3-002
"""
Tests for MCP Tool Execution in Agent Collaboration

Tests MCP executor, tool invocation, error handling, and integration.

Module: tests/unit/intent_router/test_mcp_tool_integration.py
Authority: Phase 81 S3 Part 3 - MCP Tool Integration
Version: 1.0
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any

from cortex.orchestrators.core.intent_router.mcp_executor import (
    MCPToolExecutor,
    MCPExecutionRequest,
    MCPExecutionResult
)
from cortex.orchestrators.core.intent_router.collaboration_coordinator import (
    AgentCollaborationCoordinator,
    CollaborationRequest,
    CollaborationPattern,
    AgentContext
)


class TestMCPExecutionRequest:
    """Test MCPExecutionRequest dataclass."""
    
    def test_request_creation(self):
        """Test basic request creation."""
        req = MCPExecutionRequest(
            agent_id="cortex-auditor",
            tool_name="cortex_audit_codebase",
            tool_parameters={"scope": "all"},
            request_id="req-001"
        )
        
        assert req.agent_id == "cortex-auditor"
        assert req.tool_name == "cortex_audit_codebase"
        assert req.tool_parameters["scope"] == "all"
        assert req.request_id == "req-001"
        assert req.timeout_seconds == 30
    
    def test_request_with_custom_timeout(self):
        """Test request with custom timeout."""
        req = MCPExecutionRequest(
            agent_id="cortex-phase-resolver",
            tool_name="cortex_resolve_phase",
            tool_parameters={},
            request_id="req-002",
            timeout_seconds=60
        )
        
        assert req.timeout_seconds == 60


class TestMCPExecutionResult:
    """Test MCPExecutionResult dataclass."""
    
    def test_successful_result(self):
        """Test successful execution result."""
        result = MCPExecutionResult(
            success=True,
            agent_id="cortex-auditor",
            tool_name="cortex_audit_codebase",
            output={"status": "health_check_passed"}
        )
        
        assert result.success is True
        assert result.agent_id == "cortex-auditor"
        assert result.output["status"] == "health_check_passed"
        assert result.error_message is None
        assert result.execution_timestamp  # Should be auto-set
    
    def test_error_result(self):
        """Test error execution result."""
        result = MCPExecutionResult(
            success=False,
            agent_id="cortex-auditor",
            tool_name="cortex_audit_codebase",
            output={},
            error_message="Tool timeout"
        )
        
        assert result.success is False
        assert result.error_message == "Tool timeout"
        assert result.output == {}


class TestMCPToolExecutor:
    """Test MCPToolExecutor core functionality."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        return MCPToolExecutor()
    
    def test_executor_initialization(self, executor):
        """Test executor initializes correctly."""
        assert executor._tool_handlers == {}
        assert executor._agent_tools == {}
        assert executor._execution_history == []
    
    def test_register_tool_handler(self, executor):
        """Test registering tool handler."""
        mock_handler = Mock()
        executor.register_tool_handler("cortex_audit_codebase", mock_handler)
        
        assert "cortex_audit_codebase" in executor._tool_handlers
        assert executor._tool_handlers["cortex_audit_codebase"] == mock_handler
    
    def test_register_agent_tools(self, executor):
        """Test registering agent's available tools."""
        tools = ["cortex_audit_codebase", "cortex_validate_governance"]
        executor.register_agent_tools("cortex-auditor", tools)
        
        assert "cortex-auditor" in executor._agent_tools
        assert executor._agent_tools["cortex-auditor"] == tools
    
    def test_get_agent_tools(self, executor):
        """Test retrieving agent's tools."""
        tools = ["tool1", "tool2"]
        executor.register_agent_tools("cortex-auditor", tools)
        
        retrieved = executor.get_agent_tools("cortex-auditor")
        assert retrieved == tools
    
    def test_get_nonexistent_agent_tools(self, executor):
        """Test retrieving tools for unregistered agent."""
        retrieved = executor.get_agent_tools("cortex-nonexistent")
        assert retrieved == []
    
    def test_execute_success(self, executor):
        """Test successful tool execution."""
        # Setup
        mock_handler = Mock(return_value={"result": "success"})
        executor.register_tool_handler("cortex_audit_codebase", mock_handler)
        executor.register_agent_tools("cortex-auditor", ["cortex_audit_codebase"])
        
        # Execute
        request = MCPExecutionRequest(
            agent_id="cortex-auditor",
            tool_name="cortex_audit_codebase",
            tool_parameters={"scope": "all"},
            request_id="req-001"
        )
        
        result = executor.execute(request)
        
        # Verify
        assert result.success is True
        assert result.agent_id == "cortex-auditor"
        assert result.tool_name == "cortex_audit_codebase"
        assert result.output["result"] == "success"
        assert mock_handler.called
        assert len(executor._execution_history) == 1
    
    def test_execute_unregistered_agent(self, executor):
        """Test execution fails for unregistered agent."""
        request = MCPExecutionRequest(
            agent_id="cortex-nonexistent",
            tool_name="cortex_audit_codebase",
            tool_parameters={},
            request_id="req-001"
        )
        
        result = executor.execute(request)
        
        assert result.success is False
        assert "not registered" in result.error_message
    
    def test_execute_unavailable_tool(self, executor):
        """Test execution fails when agent doesn't have tool."""
        executor.register_agent_tools("cortex-auditor", ["cortex_audit_codebase"])
        
        request = MCPExecutionRequest(
            agent_id="cortex-auditor",
            tool_name="cortex_unavailable_tool",
            tool_parameters={},
            request_id="req-001"
        )
        
        result = executor.execute(request)
        
        assert result.success is False
        assert "not available" in result.error_message
    
    def test_execute_no_handler_mock_fallback(self, executor):
        """Test execution uses mock when no handler registered."""
        executor.register_agent_tools("cortex-auditor", ["cortex_audit_codebase"])
        
        request = MCPExecutionRequest(
            agent_id="cortex-auditor",
            tool_name="cortex_audit_codebase",
            tool_parameters={"scope": "all"},
            request_id="req-001"
        )
        
        result = executor.execute(request)
        
        # Should succeed with mock
        assert result.success is True
        assert result.output["mock"] is True
    
    def test_execute_handler_exception(self, executor):
        """Test execution handles handler exceptions."""
        mock_handler = Mock(side_effect=RuntimeError("Handler failed"))
        executor.register_tool_handler("cortex_audit_codebase", mock_handler)
        executor.register_agent_tools("cortex-auditor", ["cortex_audit_codebase"])
        
        request = MCPExecutionRequest(
            agent_id="cortex-auditor",
            tool_name="cortex_audit_codebase",
            tool_parameters={},
            request_id="req-001"
        )
        
        result = executor.execute(request)
        
        assert result.success is False
        assert "Handler failed" in result.error_message
    
    def test_execute_batch(self, executor):
        """Test batch execution of multiple tools."""
        mock_handler = Mock(return_value={"status": "ok"})
        executor.register_tool_handler("cortex_audit_codebase", mock_handler)
        executor.register_agent_tools("cortex-auditor", ["cortex_audit_codebase"])
        
        requests = [
            MCPExecutionRequest(
                agent_id="cortex-auditor",
                tool_name="cortex_audit_codebase",
                tool_parameters={},
                request_id=f"req-{i}"
            )
            for i in range(3)
        ]
        
        results = executor.execute_batch(requests)
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert len(executor._execution_history) == 3
    
    def test_get_execution_history_all(self, executor):
        """Test retrieving all execution history."""
        executor.register_agent_tools("cortex-auditor", ["tool1"])
        mock_handler = Mock(return_value={"ok": True})
        executor.register_tool_handler("tool1", mock_handler)
        
        for i in range(3):
            req = MCPExecutionRequest(
                agent_id="cortex-auditor",
                tool_name="tool1",
                tool_parameters={},
                request_id=f"req-{i}"
            )
            executor.execute(req)
        
        history = executor.get_execution_history()
        assert len(history) == 3
    
    def test_get_execution_history_filtered(self, executor):
        """Test retrieving execution history filtered by agent."""
        executor.register_agent_tools("cortex-auditor", ["tool1"])
        executor.register_agent_tools("cortex-resolver", ["tool1"])
        mock_handler = Mock(return_value={"ok": True})
        executor.register_tool_handler("tool1", mock_handler)
        
        # Execute for both agents
        for agent in ["cortex-auditor", "cortex-resolver"]:
            req = MCPExecutionRequest(
                agent_id=agent,
                tool_name="tool1",
                tool_parameters={},
                request_id=f"req-{agent}"
            )
            executor.execute(req)
        
        auditor_history = executor.get_execution_history("cortex-auditor")
        assert len(auditor_history) == 1
        assert auditor_history[0].agent_id == "cortex-auditor"


class TestAgentCollaborationWithMCP:
    """Test agent collaboration with MCP tool integration."""
    
    @pytest.fixture
    def coordinator(self):
        """Create coordinator instance."""
        return AgentCollaborationCoordinator()
    
    def test_coordinator_has_mcp_executor(self, coordinator):
        """Test coordinator initializes with MCP executor."""
        assert hasattr(coordinator, "_mcp_executor")
        assert isinstance(coordinator._mcp_executor, MCPToolExecutor)
    
    def test_register_agent_registers_mcp_tools(self, coordinator):
        """Test agent registration also registers MCP tools."""
        coordinator.register_agent(
            agent_id="cortex-auditor",
            capabilities=["audit"],
            mcp_tools=["cortex_audit_codebase"]
        )
        
        # Verify tools registered with executor
        tools = coordinator._mcp_executor.get_agent_tools("cortex-auditor")
        assert "cortex_audit_codebase" in tools
    
    def test_execute_agent_invokes_mcp_tool(self, coordinator):
        """Test _execute_agent invokes MCP tools."""
        # Setup
        coordinator.register_agent(
            agent_id="cortex-auditor",
            capabilities=["audit"],
            mcp_tools=["cortex_audit_codebase"]
        )
        
        mock_handler = Mock(return_value={"audit_result": "passed"})
        coordinator._mcp_executor.register_tool_handler(
            "cortex_audit_codebase",
            mock_handler
        )
        
        # Create request
        context = AgentContext(
            agent_id="cortex-auditor",
            request_id="req-001",
            user_request="audit code",
            intent="AUDIT"
        )
        
        request = CollaborationRequest(
            request_id="req-001",
            primary_agent_id="cortex-auditor",
            context=context
        )
        
        # Execute
        output = coordinator._execute_agent("cortex-auditor", request)
        
        # Verify
        assert output["agent_id"] == "cortex-auditor"
        assert output["status"] == "completed"
        assert "cortex_audit_codebase" in output["mcp_tools_invoked"]
        assert output["mcp_execution_result"]["success"] is True
    
    def test_coordinate_hierarchical_uses_mcp_tools(self, coordinator):
        """Test hierarchical coordination executes agents via MCP."""
        # Setup agents
        coordinator.register_agent(
            agent_id="cortex-phase-resolver",
            capabilities=["phase_resolution"],
            mcp_tools=["cortex_resolve_phase"]
        )
        
        coordinator.register_agent(
            agent_id="cortex-master-plan-auditor",
            capabilities=["planning"],
            mcp_tools=["cortex_audit_plan"]
        )
        
        # Register mock handlers
        handler1 = Mock(return_value={"phase": "phase-81"})
        handler2 = Mock(return_value={"plan": "valid"})
        
        coordinator._mcp_executor.register_tool_handler("cortex_resolve_phase", handler1)
        coordinator._mcp_executor.register_tool_handler("cortex_audit_plan", handler2)
        
        # Create request
        context = AgentContext(
            agent_id="cortex-phase-resolver",
            request_id="req-001",
            user_request="execute phase 81",
            intent="PLAN"
        )
        
        request = CollaborationRequest(
            request_id="req-001",
            primary_agent_id="cortex-phase-resolver",
            secondary_agents=["cortex-master-plan-auditor"],
            pattern=CollaborationPattern.HIERARCHICAL,
            context=context
        )
        
        # Execute
        result = coordinator.coordinate(request)
        
        # Verify
        assert result.success is True
        assert len(result.execution_path) == 2
        assert "cortex-phase-resolver" in result.execution_path
        assert "cortex-master-plan-auditor" in result.execution_path


class TestMCPToolErrorHandling:
    """Test error handling in MCP tool execution."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        return MCPToolExecutor()
    
    def test_handler_timeout_handling(self, executor):
        """Test handling of tool timeout."""
        import time
        
        def slow_handler(**kwargs):
            time.sleep(0.1)
            return {"result": "ok"}
        
        executor.register_tool_handler("cortex_slow_tool", slow_handler)
        executor.register_agent_tools("cortex-test", ["cortex_slow_tool"])
        
        request = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="cortex_slow_tool",
            tool_parameters={},
            request_id="req-001",
            timeout_seconds=30  # Sufficient timeout
        )
        
        result = executor.execute(request)
        
        # Should complete successfully within timeout
        assert result.success is True
        assert result.duration_seconds >= 0.1
    
    def test_invalid_parameters_error(self, executor):
        """Test handling of invalid tool parameters."""
        def strict_handler(tool_name, parameters, **kwargs):
            if not parameters.get("required_param"):
                raise ValueError("Missing required_param")
            return {"ok": True}
        
        executor.register_tool_handler("cortex_strict_tool", strict_handler)
        executor.register_agent_tools("cortex-test", ["cortex_strict_tool"])
        
        request = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="cortex_strict_tool",
            tool_parameters={"wrong_param": "value"},
            request_id="req-001"
        )
        
        result = executor.execute(request)
        
        assert result.success is False
        assert "Missing required_param" in result.error_message


class TestMCPToolIntegrationMetrics:
    """Test metrics and monitoring for MCP tool integration."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        return MCPToolExecutor()
    
    def test_execution_duration_tracking(self, executor):
        """Test tool execution duration is tracked."""
        import time
        
        def timed_handler(**kwargs):
            time.sleep(0.05)
            return {"ok": True}
        
        executor.register_tool_handler("cortex_timed_tool", timed_handler)
        executor.register_agent_tools("cortex-test", ["cortex_timed_tool"])
        
        request = MCPExecutionRequest(
            agent_id="cortex-test",
            tool_name="cortex_timed_tool",
            tool_parameters={},
            request_id="req-001"
        )
        
        result = executor.execute(request)
        
        assert result.success is True
        assert result.duration_seconds >= 0.05
        assert result.duration_seconds < 1.0  # Should be fast
    
    def test_execution_history_metrics(self, executor):
        """Test execution history tracks success/failure metrics."""
        executor.register_agent_tools("cortex-test", ["tool1", "tool2"])
        
        success_handler = Mock(return_value={"ok": True})
        error_handler = Mock(side_effect=RuntimeError("Failed"))
        
        executor.register_tool_handler("tool1", success_handler)
        executor.register_tool_handler("tool2", error_handler)
        
        # Execute successes
        for i in range(2):
            req = MCPExecutionRequest(
                agent_id="cortex-test",
                tool_name="tool1",
                tool_parameters={},
                request_id=f"req-success-{i}"
            )
            executor.execute(req)
        
        # Execute failures
        for i in range(1):
            req = MCPExecutionRequest(
                agent_id="cortex-test",
                tool_name="tool2",
                tool_parameters={},
                request_id=f"req-fail-{i}"
            )
            executor.execute(req)
        
        history = executor.get_execution_history()
        successful = [r for r in history if r.success]
        failed = [r for r in history if not r.success]
        
        assert len(successful) == 2
        assert len(failed) == 1


# AC_COMPLETE: AC-PHASE81-S3-P3-002 ✅ MCP Tool Integration Tests
