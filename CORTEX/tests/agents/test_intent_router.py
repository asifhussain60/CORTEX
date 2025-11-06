"""
Tests for IntentRouter Agent

Tests routing logic, intent classification, pattern matching, and multi-agent routing.
"""

import pytest
from CORTEX.src.cortex_agents.intent_router import IntentRouter
from CORTEX.src.cortex_agents.base_agent import AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import AgentType, IntentType


class TestIntentRouterBasics:
    """Test basic IntentRouter functionality"""
    
    def test_router_initialization(self, mock_tier_apis):
        """Test IntentRouter initialization"""
        router = IntentRouter(
            name="Router",
            tier1_api=mock_tier_apis["tier1_api"],
            tier2_kg=mock_tier_apis["tier2_kg"],
            tier3_context=mock_tier_apis["tier3_context"]
        )
        
        assert router.name == "Router"
        assert router.tier1 is not None
        assert router.tier2 is not None
        assert router.tier3 is not None
    
    def test_router_can_handle_all_requests(self, mock_tier_apis):
        """Test that router can handle any request"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        # Test various intents
        for intent in ["plan", "code", "test", "unknown", "anything"]:
            request = AgentRequest(
                intent=intent,
                context={},
                user_message="Test message"
            )
            assert router.can_handle(request) is True


class TestIntentClassification:
    """Test intent classification from user messages"""
    
    def test_classify_planning_intent(self, mock_tier_apis):
        """Test classification of planning requests"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Plan a new authentication feature"
        )
        
        intent = router._classify_intent(request)
        assert intent == IntentType.PLAN
    
    def test_classify_code_intent(self, mock_tier_apis):
        """Test classification of code implementation requests"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Create a new user model"
        )
        
        intent = router._classify_intent(request)
        assert intent == IntentType.CODE
    
    def test_classify_test_intent(self, mock_tier_apis):
        """Test classification of testing requests"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Run tests for the authentication module"
        )
        
        intent = router._classify_intent(request)
        assert intent == IntentType.RUN_TESTS
    
    def test_classify_fix_intent(self, mock_tier_apis):
        """Test classification of fix/debug requests"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Fix the login bug"
        )
        
        intent = router._classify_intent(request)
        assert intent == IntentType.FIX
    
    def test_classify_unknown_intent(self, mock_tier_apis):
        """Test classification when intent is unclear"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Lorem ipsum dolor sit amet"
        )
        
        intent = router._classify_intent(request)
        assert intent == IntentType.UNKNOWN
    
    def test_preserve_valid_intent(self, mock_tier_apis):
        """Test that valid pre-classified intents are preserved"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check system status"
        )
        
        intent = router._classify_intent(request)
        assert intent == IntentType.HEALTH_CHECK


class TestRoutingDecisions:
    """Test routing decision logic"""
    
    def test_route_plan_to_planner(self, mock_tier_apis):
        """Test routing of plan intent to WorkPlanner"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Plan the authentication feature"
        )
        
        response = router.execute(request)
        
        assert response.success is True
        assert response.result["primary_agent"] == AgentType.PLANNER
        assert response.result["intent"] == IntentType.PLAN
    
    def test_route_code_to_executor(self, mock_tier_apis):
        """Test routing of code intent to CodeExecutor"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Create a new user authentication module"
        )
        
        response = router.execute(request)
        
        assert response.success is True
        assert response.result["primary_agent"] == AgentType.EXECUTOR
    
    def test_route_with_multiple_agents(self, mock_tier_apis):
        """Test routing that requires multiple agents"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Create a new module with tests"
        )
        
        response = router.execute(request)
        
        assert response.success is True
        # Should route to EXECUTOR primarily
        assert response.result["primary_agent"] == AgentType.EXECUTOR
        # Should also involve TESTER
        assert AgentType.TESTER in response.result.get("secondary_agents", [])
    
    def test_confidence_scoring(self, mock_tier_apis):
        """Test confidence scoring in routing decisions"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        # Clear request should have high confidence
        clear_request = AgentRequest(
            intent="plan",
            context={"feature": "auth"},
            user_message="Plan the authentication feature"
        )
        
        response = router.execute(clear_request)
        assert response.result["confidence"] > 0.7
        
        # Unclear request should have lower confidence
        unclear_request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Do something"
        )
        
        response = router.execute(unclear_request)
        assert response.result["confidence"] < 0.7


class TestTierIntegration:
    """Test integration with Tier 1, 2, 3"""
    
    def test_query_tier2_for_patterns(self, mock_tier_apis):
        """Test querying Tier 2 for similar patterns"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        # Add a pattern to Tier 2
        router.tier2.add_pattern(
            "routing",
            "Plan authentication",
            "Plan feature: authentication"
        )
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="Plan authentication feature"
        )
        
        patterns = router._find_similar_intents(request)
        assert len(patterns) > 0
        assert "authentication" in patterns[0]["title"].lower()
    
    def test_log_to_tier1_conversation(self, mock_tier_apis):
        """Test logging routing decision to Tier 1"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        # Start a conversation
        conv_id = router.tier1.start_conversation("Test routing")
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan feature",
            conversation_id=conv_id
        )
        
        response = router.execute(request)
        
        # Check conversation was logged to
        conv = router.tier1.get_conversation(conv_id)
        assert len(conv["messages"]) > 0
    
    def test_store_routing_pattern_in_tier2(self, mock_tier_apis):
        """Test storing routing patterns in Tier 2"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        initial_count = len(router.tier2.patterns)
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan new feature"
        )
        
        router.execute(request)
        
        # New pattern should be stored
        assert len(router.tier2.patterns) > initial_count


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_router_without_tier_apis(self):
        """Test router works without tier APIs"""
        router = IntentRouter("Router")
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan feature"
        )
        
        response = router.execute(request)
        assert response.success is True
    
    def test_empty_user_message(self, mock_tier_apis):
        """Test handling of empty user message"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=""
        )
        
        response = router.execute(request)
        assert response.success is True
        assert response.result["intent"] == IntentType.UNKNOWN
    
    def test_very_long_user_message(self, mock_tier_apis):
        """Test handling of very long user messages"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        long_message = "Plan feature " * 100
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=long_message
        )
        
        response = router.execute(request)
        assert response.success is True
    
    def test_tier2_search_failure(self, mock_tier_apis):
        """Test graceful handling of Tier 2 search failure"""
        router = IntentRouter("Router", **mock_tier_apis)
        
        # Break Tier 2 search
        def broken_search(*args, **kwargs):
            raise Exception("Search failed")
        
        router.tier2.search = broken_search
        
        request = AgentRequest(
            intent="plan",
            context={},
            user_message="Plan feature"
        )
        
        # Should still succeed despite Tier 2 failure
        response = router.execute(request)
        assert response.success is True
