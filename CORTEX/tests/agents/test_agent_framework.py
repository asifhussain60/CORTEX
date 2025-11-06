"""
Tests for Agent Framework Base Classes

Tests BaseAgent, AgentRequest, AgentResponse, and core infrastructure.
"""

import pytest
from datetime import datetime
from CORTEX.src.cortex_agents.base_agent import (
    BaseAgent,
    AgentRequest,
    AgentResponse,
)
from CORTEX.src.cortex_agents.agent_types import IntentType, Priority
from CORTEX.src.cortex_agents.exceptions import AgentExecutionError


class TestAgentRequest:
    """Test AgentRequest dataclass"""
    
    def test_create_basic_request(self):
        """Test creating a basic agent request"""
        request = AgentRequest(
            intent="test",
            context={"key": "value"},
            user_message="Test message"
        )
        
        assert request.intent == "test"
        assert request.context == {"key": "value"}
        assert request.user_message == "Test message"
        assert request.conversation_id is None
        assert request.priority == 3  # NORMAL
        assert isinstance(request.timestamp, datetime)
    
    def test_create_request_with_conversation(self):
        """Test creating request with conversation ID"""
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan feature",
            conversation_id="conv-123"
        )
        
        assert request.conversation_id == "conv-123"
    
    def test_create_request_with_priority(self):
        """Test creating request with custom priority"""
        request = AgentRequest(
            intent="fix",
            context={},
            user_message="Fix bug",
            priority=Priority.CRITICAL.value
        )
        
        assert request.priority == 1  # CRITICAL


class TestAgentResponse:
    """Test AgentResponse dataclass"""
    
    def test_create_success_response(self):
        """Test creating successful response"""
        response = AgentResponse(
            success=True,
            result={"status": "done"},
            message="Operation completed",
            agent_name="TestAgent"
        )
        
        assert response.success is True
        assert response.result == {"status": "done"}
        assert response.message == "Operation completed"
        assert response.agent_name == "TestAgent"
        assert isinstance(response.timestamp, datetime)
    
    def test_create_failure_response(self):
        """Test creating failure response"""
        response = AgentResponse(
            success=False,
            result=None,
            message="Operation failed"
        )
        
        assert response.success is False
        assert response.result is None
    
    def test_response_with_duration(self):
        """Test response with execution duration"""
        response = AgentResponse(
            success=True,
            result={},
            message="Done",
            duration_ms=123.45
        )
        
        assert response.duration_ms == 123.45
    
    def test_response_with_next_actions(self):
        """Test response with suggested next actions"""
        response = AgentResponse(
            success=True,
            result={},
            message="Step 1 complete",
            next_actions=["Run tests", "Commit changes"]
        )
        
        assert len(response.next_actions) == 2
        assert "Run tests" in response.next_actions


class TestBaseAgent:
    """Test BaseAgent abstract class"""
    
    def test_agent_initialization(self, mock_tier_apis):
        """Test agent initialization with tier APIs"""
        from CORTEX.tests.conftest import MockAgent
        
        agent = MockAgent(
            name="TestAgent",
            tier1_api=mock_tier_apis["tier1_api"],
            tier2_kg=mock_tier_apis["tier2_kg"],
            tier3_context=mock_tier_apis["tier3_context"]
        )
        
        assert agent.name == "TestAgent"
        assert agent.tier1 is not None
        assert agent.tier2 is not None
        assert agent.tier3 is not None
        assert agent.logger is not None
    
    def test_agent_can_handle(self, mock_agent, sample_agent_request):
        """Test agent can_handle method"""
        assert mock_agent.can_handle(sample_agent_request) is True
        
        # Test with different intent
        wrong_request = AgentRequest(
            intent="wrong_intent",
            context={},
            user_message="Test"
        )
        assert mock_agent.can_handle(wrong_request) is False
    
    def test_agent_execute(self, mock_agent, sample_agent_request):
        """Test agent execute method"""
        response = mock_agent.execute(sample_agent_request)
        
        assert isinstance(response, AgentResponse)
        assert response.success is True
        assert response.agent_name == "MockAgent"
        assert "Handled request" in response.message
    
    def test_agent_logging(self, mock_agent, sample_agent_request, caplog):
        """Test agent logging infrastructure"""
        import logging
        caplog.set_level(logging.INFO)
        
        mock_agent.log_request(sample_agent_request)
        
        assert "MockAgent" in caplog.text
        assert "test_intent" in caplog.text
    
    def test_agent_repr(self, mock_agent):
        """Test agent string representation"""
        repr_str = repr(mock_agent)
        assert "MockAgent" in repr_str
        assert "name='MockAgent'" in repr_str
    
    def test_measure_execution(self, mock_agent):
        """Test execution time measurement"""
        def sample_func(x, y):
            return x + y
        
        result, duration = mock_agent._measure_execution(sample_func, 2, 3)
        
        assert result == 5
        assert duration >= 0
        assert isinstance(duration, float)


class TestAgentIntegration:
    """Integration tests for agent framework"""
    
    def test_full_agent_workflow(self, mock_agent, mock_tier_apis):
        """Test complete agent workflow from request to response"""
        # Create request
        request = AgentRequest(
            intent="test_intent",
            context={"operation": "test"},
            user_message="Perform test operation",
            conversation_id="conv-001"
        )
        
        # Check if agent can handle
        assert mock_agent.can_handle(request) is True
        
        # Execute
        response = mock_agent.execute(request)
        
        # Validate response
        assert response.success is True
        assert response.result is not None
        assert response.message is not None
        assert response.agent_name == "MockAgent"
    
    def test_agent_with_tier1_interaction(self, mock_agent, mock_tier_apis):
        """Test agent interacting with Tier 1"""
        tier1 = mock_tier_apis["tier1_api"]
        
        # Start a conversation through agent's Tier 1 API
        conv_id = mock_agent.tier1.start_conversation("Test conversation")
        assert conv_id is not None
        
        # Add messages
        mock_agent.tier1.process_message(conv_id, "user", "Test message")
        
        # Retrieve conversation
        conv = mock_agent.tier1.get_conversation(conv_id)
        assert conv is not None
        assert len(conv["messages"]) == 1
    
    def test_agent_with_tier2_interaction(self, mock_agent, mock_tier_apis):
        """Test agent interacting with Tier 2"""
        tier2 = mock_tier_apis["tier2_kg"]
        
        # Add a pattern through agent's Tier 2 API
        mock_agent.tier2.add_pattern(
            "workflow",
            "Test pattern",
            "Pattern content"
        )
        
        # Search for pattern
        results = mock_agent.tier2.search("test")
        assert len(results) > 0
        assert results[0]["title"] == "Test pattern"
    
    def test_agent_with_tier3_interaction(self, mock_agent, mock_tier_apis):
        """Test agent interacting with Tier 3"""
        tier3 = mock_tier_apis["tier3_context"]
        
        # Get context summary through agent's Tier 3 API
        summary = mock_agent.tier3.get_context_summary()
        
        assert "total_commits" in summary
        assert "average_velocity" in summary
        assert summary["total_commits"] == 100
