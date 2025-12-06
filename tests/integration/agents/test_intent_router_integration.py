"""
Integration tests for Intent Router Agent.

Tests intent classification, agent routing, and cross-agent coordination.
"""

import pytest


def test_intent_router_initialization(temp_project, temp_brain):
    """Test intent router agent initialization."""
    from src.cortex_agents.intent_router import IntentRouter
    from src.cortex_agents.base_agent import AgentRequest
    
    router = IntentRouter()
    
    assert router is not None
    assert hasattr(router, "can_handle")
    assert hasattr(router, "execute")


def test_intent_classification(temp_project, temp_brain):
    """Test intent classification for various message types."""
    from src.cortex_agents.intent_router import IntentRouter
    from src.cortex_agents.base_agent import AgentRequest
    
    router = IntentRouter()
    
    # Test planning intent
    planning_request = AgentRequest(
        intent="unknown",
        message="create a plan for user authentication",
        context={}
    )
    
    classified_intent = router.classify_intent(planning_request)
    
    assert classified_intent is not None
    assert isinstance(classified_intent, str)


def test_agent_routing(temp_project, temp_brain):
    """Test routing to appropriate specialist agents."""
    from src.cortex_agents.intent_router import IntentRouter
    from src.cortex_agents.base_agent import AgentRequest
    
    router = IntentRouter()
    
    request = AgentRequest(
        intent="planning",
        message="plan feature",
        context={}
    )
    
    # Router should identify correct agent
    target_agent = router.route_to_agent(request)
    
    assert target_agent is not None


def test_multi_agent_coordination(temp_project, temp_brain):
    """Test coordination between multiple agents."""
    from src.cortex_agents.intent_router import IntentRouter
    from src.cortex_agents.base_agent import AgentRequest
    
    router = IntentRouter()
    
    # Complex request that may involve multiple agents
    request = AgentRequest(
        intent="complex",
        message="create plan and start tdd implementation",
        context={}
    )
    
    # Router should handle multi-agent scenarios
    result = router.execute(request)
    
    assert result is not None
