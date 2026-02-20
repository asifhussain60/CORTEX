"""
Tests for agent-orchestrator interaction patterns (phase-81 S2).

Authority: cortex-registry/_cortex-master/index.yaml WAVE-L
Created: 2026-02-12
AC-ID: AC-WAVE-L-002
"""

import pytest
from typing import List
from unittest.mock import Mock

from cortex.orchestrators.intelligence.interaction_patterns import (
    AgentRequest,
    AgentResponse,
    AgentResponseFormat,
    AgentToOrchestratorBridge,
    OrchestratorAgentInvoker,
    format_agent_response_for_user,
)


class TestAgentRequest:
    """Tests for AgentRequest dataclass."""
    
    def test_request_creation_with_defaults(self):
        """Test creating request with default values."""
        request = AgentRequest(
            agent_name="cortex-executor",
            operation="validate",
            context={"code": "print('hello')"},
        )
        
        assert request.agent_name == "cortex-executor"
        assert request.operation == "validate"
        assert request.format == AgentResponseFormat.STRUCTURED
        assert request.metadata == {}
    
    def test_request_creation_with_custom_format(self):
        """Test creating request with custom format."""
        request = AgentRequest(
            agent_name="cortex-auditor",
            operation="analyze",
            context={"target": "file.py"},
            format=AgentResponseFormat.TABLE,
            metadata={"priority": "high"},
        )
        
        assert request.format == AgentResponseFormat.TABLE
        assert request.metadata["priority"] == "high"


class TestAgentResponse:
    """Tests for AgentResponse dataclass."""
    
    def test_response_creation_success(self):
        """Test creating successful response."""
        response = AgentResponse(
            agent_name="cortex-executor",
            operation="validate",
            success=True,
            data={"status": "valid", "issues": []},
        )
        
        assert response.success is True
        assert response.errors == []
        assert response.warnings == []
        assert response.metadata == {}
    
    def test_response_creation_with_errors(self):
        """Test creating response with errors."""
        response = AgentResponse(
            agent_name="cortex-executor",
            operation="validate",
            success=False,
            data=None,
            errors=["Syntax error on line 10", "Missing type hint"],
            warnings=["Deprecated function used"],
        )
        
        assert response.success is False
        assert len(response.errors) == 2
        assert len(response.warnings) == 1


class TestAgentToOrchestratorBridge:
    """Tests for AgentToOrchestratorBridge."""
    
    def test_invoke_agent_not_found(self):
        """Test invoking agent that doesn't exist."""
        bridge = AgentToOrchestratorBridge()
        
        response = bridge.invoke_agent(
            agent_name="non-existent-agent",
            operation="validate",
            context={},
        )
        
        assert response.success is False
        assert len(response.errors) == 1
        assert "not found" in response.errors[0]
    
    def test_invoke_agent_with_preloaded(self):
        """Test invoking preloaded agent."""
        bridge = AgentToOrchestratorBridge()
        
        # Create mock agent
        mock_agent = Mock()
        mock_agent.execute.return_value = AgentResponse(
            agent_name="mock-agent",
            operation="validate",
            success=True,
            data={"result": "success"},
        )
        
        # Preload agent
        bridge.preload_agent("mock-agent", mock_agent)
        
        # Invoke agent
        response = bridge.invoke_agent(
            agent_name="mock-agent",
            operation="validate",
            context={"test": "data"},
        )
        
        assert response.success is True
        assert response.data["result"] == "success"
        mock_agent.execute.assert_called_once()
    
    def test_invoke_agent_exception_handling(self):
        """Test agent invocation with exception."""
        bridge = AgentToOrchestratorBridge()
        
        # Create mock agent that raises exception
        mock_agent = Mock()
        mock_agent.execute.side_effect = RuntimeError("Agent crashed")
        
        bridge.preload_agent("faulty-agent", mock_agent)
        
        response = bridge.invoke_agent(
            agent_name="faulty-agent",
            operation="validate",
            context={},
        )
        
        assert response.success is False
        assert len(response.errors) == 1
        assert "Agent execution failed" in response.errors[0]
    
    def test_clear_cache(self):
        """Test clearing agent cache."""
        bridge = AgentToOrchestratorBridge()
        
        mock_agent = Mock()
        bridge.preload_agent("test-agent", mock_agent)
        
        assert "test-agent" in bridge._agent_cache
        
        bridge.clear_cache()
        
        assert len(bridge._agent_cache) == 0


class TestOrchestratorAgentInvoker:
    """Tests for OrchestratorAgentInvoker mixin."""
    
    def test_validate_with_agent(self):
        """Test validation invocation pattern."""
        invoker = OrchestratorAgentInvoker()
        
        # Preload mock agent
        mock_agent = Mock()
        mock_agent.execute.return_value = AgentResponse(
            agent_name="validator",
            operation="validate",
            success=True,
            data={"valid": True},
        )
        invoker.agent_bridge.preload_agent("validator", mock_agent)
        
        # Invoke validation
        response = invoker.validate_with_agent(
            agent_name="validator",
            validation_target="test_code.py",
            strict=True,
        )
        
        assert response.success is True
        assert response.data["valid"] is True
        
        # Verify context was passed correctly
        call_args = mock_agent.execute.call_args[0][0]
        assert call_args.operation == "validate"
        assert call_args.context["target"] == "test_code.py"
        assert call_args.context["strict"] is True
    
    def test_analyze_with_agent(self):
        """Test analysis invocation pattern."""
        invoker = OrchestratorAgentInvoker()
        
        mock_agent = Mock()
        mock_agent.execute.return_value = AgentResponse(
            agent_name="analyzer",
            operation="analyze",
            success=True,
            data={"complexity": 5},
        )
        invoker.agent_bridge.preload_agent("analyzer", mock_agent)
        
        response = invoker.analyze_with_agent(
            agent_name="analyzer",
            analysis_target="module.py",
        )
        
        assert response.success is True
        assert response.data["complexity"] == 5
    
    def test_execute_with_agent(self):
        """Test execution invocation pattern."""
        invoker = OrchestratorAgentInvoker()
        
        mock_agent = Mock()
        mock_agent.execute.return_value = AgentResponse(
            agent_name="executor",
            operation="execute",
            success=True,
            data={"executed": True},
        )
        invoker.agent_bridge.preload_agent("executor", mock_agent)
        
        response = invoker.execute_with_agent(
            agent_name="executor",
            execution_context={"action": "run_tests"},
        )
        
        assert response.success is True
        assert response.data["executed"] is True


class TestFormatAgentResponse:
    """Tests for format_agent_response_for_user function."""
    
    def test_format_success_response(self):
        """Test formatting successful response."""
        response = AgentResponse(
            agent_name="cortex-executor",
            operation="validate",
            success=True,
            data={"status": "valid", "tests": "10 passed"},
        )
        
        formatted = format_agent_response_for_user(response)
        
        assert "✅" in formatted
        assert "cortex-executor" in formatted
        assert "validate" in formatted
        assert "status" in formatted
        assert "valid" in formatted
    
    def test_format_error_response(self):
        """Test formatting error response."""
        response = AgentResponse(
            agent_name="cortex-executor",
            operation="validate",
            success=False,
            data=None,
            errors=["Syntax error", "Missing imports"],
        )
        
        formatted = format_agent_response_for_user(response)
        
        assert "❌" in formatted
        assert "Errors:" in formatted
        assert "Syntax error" in formatted
        assert "Missing imports" in formatted
    
    def test_format_response_with_warnings(self):
        """Test formatting response with warnings."""
        response = AgentResponse(
            agent_name="cortex-auditor",
            operation="analyze",
            success=True,
            data={"score": 85},
            warnings=["Deprecated API used", "Low test coverage"],
        )
        
        formatted = format_agent_response_for_user(response)
        
        assert "Warnings:" in formatted
        assert "⚠️" in formatted
        assert "Deprecated API used" in formatted
    
    def test_format_response_with_list_data(self):
        """Test formatting response with list data."""
        response = AgentResponse(
            agent_name="cortex-analyzer",
            operation="list",
            success=True,
            data=["item1", "item2", "item3"],
        )
        
        formatted = format_agent_response_for_user(response)
        
        assert "- item1" in formatted
        assert "- item2" in formatted
        assert "- item3" in formatted
