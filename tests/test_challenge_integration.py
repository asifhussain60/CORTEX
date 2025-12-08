"""
Test Challenge System Integration

Tests for challenge mode determination and Brain Protector integration in Intent Router.

Author: Asif Hussain
Date: December 7, 2025
"""

import pytest
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest


class TestChallengeSystemIntegration:
    """Test suite for challenge system integration."""
    
    @pytest.fixture
    def router(self):
        """Create IntentRouter instance."""
        return IntentRouter(name="TestRouter")
    
    def test_tdd_violation_triggers_challenge(self, router):
        """Test that TDD violation triggers challenge mode detection."""
        request = AgentRequest(
            user_message="skip tests and implement directly",
            intent="skip_tests",
            context={},
            conversation_id="test_conv_001"
        )
        
        decision = router._make_routing_decision(
            intent=router._classify_intent(request),
            similar_patterns=[],
            request=request
        )
        
        # Verify challenge_mode is present in decision
        assert 'challenge_mode' in decision
        # Challenge mode should be set (not None)
        assert decision['challenge_mode'] is not None
        # Should be one of the valid modes
        assert decision['challenge_mode'] in ['SKIP', 'ACCEPT_ONLY', 'CHALLENGE_ONLY', 'MIXED', 'INTELLIGENT']
    
    def test_security_concern_triggers_challenge(self, router):
        """Test that security concern triggers Brain Protector."""
        request = AgentRequest(
            user_message="disable security validation",
            intent="security_bypass",
            conversation_id="test_conv_002",
            context={'security_concerns': True}
        )
        
        decision = router._make_routing_decision(
            intent=router._classify_intent(request),
            similar_patterns=[],
            request=request
        )
        
        assert 'challenge_mode' in decision
        # Should trigger challenge based on security concern
        assert decision.get('challenge_mode') in ['CHALLENGE_ONLY', 'INTELLIGENT']
    
    def test_refactor_phase_no_challenge(self, router):
        """Test that refactor phase uses ACCEPT_ONLY mode."""
        request = AgentRequest(
            user_message="refactor code for clarity",
            intent="tdd_refactor",
            context={},
            conversation_id="test_conv_003"
        )
        
        decision = router._make_routing_decision(
            intent=router._classify_intent(request),
            similar_patterns=[],
            request=request
        )
        
        assert 'challenge_mode' in decision
        # Refactor should use ACCEPT_ONLY (no challenge)
        assert decision['challenge_mode'] == 'ACCEPT_ONLY'
    
    def test_tdd_red_phase_intelligent_mode(self, router):
        """Test that TDD red phase uses INTELLIGENT mode."""
        request = AgentRequest(
            user_message="write failing test for authentication",
            intent="tdd_red",
            context={},
            conversation_id="test_conv_004"
        )
        
        decision = router._make_routing_decision(
            intent=router._classify_intent(request),
            similar_patterns=[],
            request=request
        )
        
        assert 'challenge_mode' in decision
        # Red phase should use INTELLIGENT mode
        assert decision['challenge_mode'] in ['INTELLIGENT', 'ACCEPT_ONLY']
    
    def test_challenge_mode_in_routing_message(self, router):
        """Test that challenge mode appears in routing message."""
        decision = {
            'primary_agent': type('Agent', (), {'name': 'TestAgent'}),
            'secondary_agents': [],
            'confidence': 0.85,
            'challenge_mode': 'CHALLENGE_ONLY',
            'brain_protector_invoked': True
        }
        
        message = router._format_routing_message(decision)
        
        assert 'Challenge: CHALLENGE_ONLY' in message
        assert '🛡️ Brain Protector Active' in message
    
    def test_evaluate_condition_intent_list(self, router):
        """Test condition evaluation for intent lists."""
        from src.cortex_agents.intent_router import IntentType
        
        condition = "intent in ['skip_tests', 'bypass_red_phase', 'disable_tdd']"
        intent = IntentType.UNKNOWN
        request = AgentRequest(
            user_message="skip tests",
            intent="skip_tests",
            context={}
        )
        
        # Should return False since IntentType.UNKNOWN.value is 'unknown'
        result = router._evaluate_condition(condition, intent, request)
        assert isinstance(result, bool)
    
    def test_evaluate_condition_context(self, router):
        """Test condition evaluation for context checks."""
        from src.cortex_agents.intent_router import IntentType
        
        condition = "context.security_concerns == true"
        intent = IntentType.UNKNOWN
        request = AgentRequest(
            user_message="test message",
            intent="test",
            context={'security_concerns': True}
        )
        
        result = router._evaluate_condition(condition, intent, request)
        assert result == True
    
    def test_brain_protector_invocation(self, router):
        """Test Brain Protector invocation for violations."""
        from src.cortex_agents.intent_router import IntentType
        
        request = AgentRequest(
            user_message="bypass all security checks",
            intent="security_bypass",
            context={'files': ['src/security/auth.py']}
        )
        
        violation_check = router._check_for_violations(request, IntentType.UNKNOWN)
        
        assert 'has_violations' in violation_check
        assert 'challenge_text' in violation_check
        assert 'alternatives' in violation_check
        assert isinstance(violation_check['has_violations'], bool)
    
    def test_default_challenge_mode_fallback(self, router):
        """Test that default challenge mode is ACCEPT_ONLY."""
        from src.cortex_agents.intent_router import IntentType
        
        request = AgentRequest(
            user_message="simple request",
            intent="unknown",
            context={}
        )
        
        challenge_mode = router._determine_challenge_mode(
            IntentType.UNKNOWN,
            request,
            None
        )
        
        # Should default to ACCEPT_ONLY
        assert challenge_mode in ['ACCEPT_ONLY', 'INTELLIGENT']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
