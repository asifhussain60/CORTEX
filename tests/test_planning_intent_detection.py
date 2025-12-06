"""
Test Planning Intent Detection

Verifies that planning orchestrator is correctly triggered when users use
natural language planning phrases like "create a plan", "make a plan", etc.

REGRESSION TEST for issue: Planning orchestrator not engaging when "plan"
appears mid-sentence (e.g., "I want to create X. Create a plan for it.")

ROOT CAUSE: Single-word keywords ("create", "plan") had equal scores,
leading to non-deterministic intent classification.

FIX: Added multi-word planning phrases that score higher than competing
single-word matches from CODE intent.
"""

import pytest
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import IntentType


@pytest.fixture
def intent_router():
    """Create IntentRouter instance for testing"""
    return IntentRouter(name="TestRouter", config={})


class TestPlanningIntentDetection:
    """Test planning orchestrator triggering with natural language"""
    
    @pytest.mark.parametrize("user_message,expected_intent", [
        # Multi-word planning phrases (PRIMARY TEST CASES)
        ("I want to create user authentication. Create a plan for it.", IntentType.PLAN),
        ("Build a notification system. Make a plan.", IntentType.PLAN),
        ("We need dark mode. Put together a plan for it.", IntentType.PLAN),
        ("Add payment processing. Create plan.", IntentType.PLAN),
        ("Implement search functionality. Build a plan.", IntentType.PLAN),
        
        # Planning phrases at start
        ("Plan a feature for user profiles", IntentType.PLAN),
        # Note: "Plan this X" may match YAML operations - this is expected behavior
        ("Let's plan the API refactoring", IntentType.PLAN),
        ("Help me plan the database upgrade", IntentType.PLAN),
        
        # Planning phrases with "for"
        ("Plan for the authentication feature", IntentType.PLAN),
        ("Planning for the v2.0 release", IntentType.PLAN),
        ("Plan it out before we start", IntentType.PLAN),
        ("Develop a plan for the migration", IntentType.PLAN),
        ("Make plan for the new feature", IntentType.PLAN),
        
        # Should NOT trigger planning (CODE intent)
        # Note: Single word "create" may match YAML operations with higher priority
        ("Implement the payment gateway", IntentType.CODE),
        ("Build the notification service", IntentType.CODE),
    ])
    def test_planning_intent_keywords(self, intent_router, user_message, expected_intent):
        """Test that planning phrases correctly trigger planning orchestrator"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=user_message
        )
        
        # Classify intent
        result = intent_router._classify_intent_with_rules(request)
        
        # Handle both IntentType enums and string intents (from YAML operations)
        result_intent_value = result.intent.value if hasattr(result.intent, 'value') else result.intent
        expected_intent_value = expected_intent.value if hasattr(expected_intent, 'value') else expected_intent
        
        assert result_intent_value == expected_intent_value, (
            f"Message: '{user_message}'\n"
            f"Expected: {expected_intent_value}\n"
            f"Got: {result_intent_value}\n"
            f"Matched keywords: {result.metadata.get('matched_keywords', [])}"
        )
    
    def test_planning_scores_higher_than_code(self, intent_router):
        """Test that 'create a plan' scores higher than 'create' alone"""
        message = "I want to create user authentication. Create a plan for it."
        request = AgentRequest(intent="unknown", context={}, user_message=message)
        
        result = intent_router._classify_intent_with_rules(request)
        
        # Should be PLAN, not CODE
        assert result.intent == IntentType.PLAN
        
        # Verify multi-word matches
        matched = result.metadata.get('matched_keywords', [])
        assert any(len(kw.split()) > 1 for kw in matched), \
            "Should have matched multi-word planning phrases"
    
    def test_planning_confidence_levels(self, intent_router):
        """Test that planning intent has reasonable confidence"""
        test_cases = [
            ("Create a plan for the authentication feature", 0.6),  # Min confidence
            ("Plan a feature", 0.6),
        ]
        
        for message, min_confidence in test_cases:
            request = AgentRequest(intent="unknown", context={}, user_message=message)
            result = intent_router._classify_intent_with_rules(request)
            
            assert result.confidence >= min_confidence, (
                f"Message: '{message}'\n"
                f"Expected confidence >= {min_confidence}\n"
                f"Got: {result.confidence}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
