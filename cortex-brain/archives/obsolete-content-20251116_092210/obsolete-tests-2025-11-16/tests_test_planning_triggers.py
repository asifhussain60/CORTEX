"""
Test Planning Trigger Detection

Tests that all documented planning trigger phrases correctly activate
the planning system via the IntentRouter.

Author: Asif Hussain
Date: 2025-11-13
"""

import pytest
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.agent_types import IntentType, AgentType
from src.cortex_agents.base_agent import AgentRequest


class TestPlanningTriggers:
    """Test planning trigger phrase detection"""
    
    @pytest.fixture
    def intent_router(self):
        """Create IntentRouter instance for testing"""
        return IntentRouter(name="TestRouter")
    
    # Test cases organized by trigger category
    
    DIRECT_PLANNING_TRIGGERS = [
        "plan a feature",
        "plan this feature",
        "plan this",
        "let's plan",
        "lets plan",
        "let's plan together",
        "lets plan together",
        "help me plan",
        "help me plan this",
        "help me plan a feature",
        "need help planning",
        "need your help planning",
        "can you help me plan",
        "can you help plan",
        "I want to plan",
        "i want to plan",
        "I need to plan",
        "i need to plan",
        "planning",
        "start planning",
        "begin planning",
        "let's create a plan",
        "lets create a plan",
        "create a plan",
        "make a plan",
        "build a plan",
        "we need to plan"
    ]
    
    FEATURE_SPECIFIC_TRIGGERS = [
        "plan authentication",
        "plan user dashboard",
        "plan API endpoint",
        "plan the API",
        "plan database schema",
        "plan frontend",
        "plan backend",
        "plan integration",
        "plan deployment",
        "plan testing",
        "plan migration",
        "plan refactor",
        "plan new feature"
    ]
    
    QUESTION_FORM_TRIGGERS = [
        "how do I plan",
        "how do i plan",
        "how should I plan",
        "how should i plan",
        "how to plan this",
        "what's the best way to plan",
        "whats the best way to plan",
        "help planning this",
        "help planning this out",
        "help me plan this out"
    ]
    
    COLLABORATIVE_TRIGGERS = [
        "let's plan a feature together",
        "lets plan a feature together",
        "plan together",
        "work with me to plan",
        "collaborate on planning",
        "help me break this down",
        "break this down for me",
        "break this down",
        "help me structure this"
    ]
    
    IMPLICIT_PLANNING_TRIGGERS = [
        "I need a roadmap",
        "i need a roadmap",
        "create a roadmap",
        "build a roadmap",
        "roadmap",
        "help me organize this work",
        "how should I approach this",
        "how should i approach this",
        "what's the best approach",
        "whats the best approach",
        "how do I tackle this",
        "how do i tackle this"
    ]
    
    @pytest.mark.parametrize("trigger_phrase", DIRECT_PLANNING_TRIGGERS)
    def test_direct_planning_triggers(self, intent_router, trigger_phrase):
        """Test direct planning request triggers"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=trigger_phrase
        )
        
        classified_intent = intent_router._classify_intent(request)
        
        assert classified_intent == IntentType.PLAN, \
            f"Failed to detect PLAN intent for: '{trigger_phrase}' (got {classified_intent.value})"
    
    @pytest.mark.parametrize("trigger_phrase", FEATURE_SPECIFIC_TRIGGERS)
    def test_feature_specific_triggers(self, intent_router, trigger_phrase):
        """Test feature-specific planning triggers"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=trigger_phrase
        )
        
        classified_intent = intent_router._classify_intent(request)
        
        assert classified_intent == IntentType.PLAN, \
            f"Failed to detect PLAN intent for: '{trigger_phrase}' (got {classified_intent.value})"
    
    @pytest.mark.parametrize("trigger_phrase", QUESTION_FORM_TRIGGERS)
    def test_question_form_triggers(self, intent_router, trigger_phrase):
        """Test question-form planning triggers"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=trigger_phrase
        )
        
        classified_intent = intent_router._classify_intent(request)
        
        assert classified_intent == IntentType.PLAN, \
            f"Failed to detect PLAN intent for: '{trigger_phrase}' (got {classified_intent.value})"
    
    @pytest.mark.parametrize("trigger_phrase", COLLABORATIVE_TRIGGERS)
    def test_collaborative_triggers(self, intent_router, trigger_phrase):
        """Test collaborative planning triggers"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=trigger_phrase
        )
        
        classified_intent = intent_router._classify_intent(request)
        
        assert classified_intent == IntentType.PLAN, \
            f"Failed to detect PLAN intent for: '{trigger_phrase}' (got {classified_intent.value})"
    
    @pytest.mark.parametrize("trigger_phrase", IMPLICIT_PLANNING_TRIGGERS)
    def test_implicit_planning_triggers(self, intent_router, trigger_phrase):
        """Test implicit planning triggers"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=trigger_phrase
        )
        
        classified_intent = intent_router._classify_intent(request)
        
        assert classified_intent == IntentType.PLAN, \
            f"Failed to detect PLAN intent for: '{trigger_phrase}' (got {classified_intent.value})"
    
    def test_planning_routes_to_work_planner(self, intent_router):
        """Test that PLAN intent routes to WorkPlanner agent"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan a new authentication system"
        )
        
        response = intent_router.execute(request)
        
        assert response.success, "Routing should succeed"
        assert response.result["primary_agent"] == AgentType.PLANNER, \
            f"PLAN intent should route to PLANNER agent (got {response.result['primary_agent']})"
        assert response.result["intent"] == IntentType.PLAN
    
    def test_all_triggers_count(self):
        """Verify we have comprehensive trigger coverage"""
        total_triggers = (
            len(self.DIRECT_PLANNING_TRIGGERS) +
            len(self.FEATURE_SPECIFIC_TRIGGERS) +
            len(self.QUESTION_FORM_TRIGGERS) +
            len(self.COLLABORATIVE_TRIGGERS) +
            len(self.IMPLICIT_PLANNING_TRIGGERS)
        )
        
        # We documented 70+ triggers, verify we're testing that many
        assert total_triggers >= 70, \
            f"Expected at least 70 trigger phrases, found {total_triggers}"
    
    def test_case_insensitive_triggers(self, intent_router):
        """Test that triggers work regardless of case"""
        test_cases = [
            "PLAN A FEATURE",
            "Plan A Feature",
            "plan a feature",
            "PlAn A fEaTuRe"
        ]
        
        for trigger in test_cases:
            request = AgentRequest(
                intent="unknown",
                context={},
                user_message=trigger
            )
            
            classified_intent = intent_router._classify_intent(request)
            
            assert classified_intent == IntentType.PLAN, \
                f"Case variation '{trigger}' should detect PLAN intent"
    
    def test_trigger_in_longer_sentence(self, intent_router):
        """Test that triggers work when embedded in longer sentences"""
        test_cases = [
            "Hey, can you help me plan a new authentication system?",
            "I'd like to plan this feature before implementing it",
            "We need to create a roadmap for the Q4 release",
            "Could you help me break this down into smaller tasks?"
        ]
        
        for sentence in test_cases:
            request = AgentRequest(
                intent="unknown",
                context={},
                user_message=sentence
            )
            
            classified_intent = intent_router._classify_intent(request)
            
            assert classified_intent == IntentType.PLAN, \
                f"Planning trigger in sentence '{sentence}' should detect PLAN intent"
    
    def test_non_planning_triggers_not_detected(self, intent_router):
        """Test that non-planning phrases don't trigger PLAN intent"""
        non_planning_phrases = [
            "create a new file",
            "run the tests",
            "fix this bug",
            "debug the authentication issue",
            "commit these changes"
        ]
        
        for phrase in non_planning_phrases:
            request = AgentRequest(
                intent="unknown",
                context={},
                user_message=phrase
            )
            
            classified_intent = intent_router._classify_intent(request)
            
            assert classified_intent != IntentType.PLAN, \
                f"Non-planning phrase '{phrase}' should not detect PLAN intent (got {classified_intent.value})"
    
    def test_confidence_scoring(self, intent_router):
        """Test confidence scoring for planning requests"""
        # High confidence: explicit planning request
        high_confidence_request = AgentRequest(
            intent="unknown",
            context={"project": "auth-system"},
            user_message="plan JWT authentication with OAuth2 integration"
        )
        
        response = intent_router.execute(high_confidence_request)
        assert response.result["confidence"] >= 0.7, \
            "Explicit planning request should have high confidence"
        
        # Lower confidence: vague request
        low_confidence_request = AgentRequest(
            intent="unknown",
            context={},
            user_message="planning"
        )
        
        response = intent_router.execute(low_confidence_request)
        assert response.result["confidence"] >= 0.3, \
            "Vague planning request should still have some confidence"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
