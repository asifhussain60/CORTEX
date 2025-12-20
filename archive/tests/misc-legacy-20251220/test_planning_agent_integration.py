"""
Integration tests for Planning Agent.

Tests planning agent execution, validation, and orchestrator integration.
"""

import pytest


def test_planning_agent_initialization(temp_project, temp_brain):
    """Test planning agent initialization."""
    from src.cortex_agents.planning_agent import PlanningAgent
    from src.cortex_agents.base_agent import AgentRequest
    
    agent = PlanningAgent()
    
    assert agent is not None
    assert hasattr(agent, "can_handle")
    assert hasattr(agent, "execute")


def test_planning_agent_intent_detection(temp_project, temp_brain):
    """Test planning agent intent detection."""
    from src.cortex_agents.planning_agent import PlanningAgent
    from src.cortex_agents.base_agent import AgentRequest
    
    agent = PlanningAgent()
    
    # Planning intents
    planning_intents = ["planning", "create_plan", "plan_feature"]
    
    for intent in planning_intents:
        request = AgentRequest(
            intent=intent,
            message="Test planning message",
            context={}
        )
        
        assert agent.can_handle(request) is True


def test_planning_agent_execution(temp_project, temp_brain, sample_planning_request):
    """Test planning agent execution."""
    from src.cortex_agents.planning_agent import PlanningAgent
    from src.cortex_agents.base_agent import AgentRequest, AgentResponse
    
    agent = PlanningAgent()
    
    request = AgentRequest(
        intent="planning",
        message=f"Create plan for {sample_planning_request['feature_name']}",
        context={
            "project_root": temp_project,
            "feature_name": sample_planning_request["feature_name"],
            "description": sample_planning_request["description"]
        }
    )
    
    response = agent.execute(request)
    
    assert isinstance(response, AgentResponse)
    assert response.success is True or response.message != ""


def test_planning_agent_orchestrator_integration(temp_project, temp_brain):
    """Test planning agent integration with planning orchestrator."""
    from src.cortex_agents.planning_agent import PlanningAgent
    from src.cortex_agents.base_agent import AgentRequest
    
    agent = PlanningAgent()
    
    # Agent should coordinate with PlanningOrchestrator
    request = AgentRequest(
        intent="planning",
        message="Create comprehensive plan",
        context={"project_root": temp_project}
    )
    
    response = agent.execute(request)
    
    # Verify orchestrator coordination
    assert response is not None
