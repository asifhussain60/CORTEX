"""
Test Intent Router Rule Context Attachment (CORTEX 3.0 Phase 1)

Tests that the IntentRouter correctly attaches governance rule contexts
based on classified intent, enabling intelligent rule enforcement.

Author: Asif Hussain
Date: 2025-11-18
"""

import pytest
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.agent_types import IntentType, IntentClassificationResult
from src.cortex_agents.base_agent import AgentRequest


class TestIntentClassificationWithRules:
    """Test intent classification returns rich context with rules"""
    
    @pytest.fixture
    def router(self):
        """Create IntentRouter instance for testing"""
        return IntentRouter(name="TestRouter", tier1_api=None, tier2_kg=None, tier3_context=None)
    
    def test_classify_code_intent_attaches_tdd_rules(self, router):
        """Verify CODE intent attaches TDD enforcement rules"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="create a new authentication module"
        )
        
        result = router._classify_intent_with_rules(request)
        
        assert isinstance(result, IntentClassificationResult)
        assert result.intent == IntentType.CODE
        assert result.confidence > 0.0
        
        # Verify rule context
        assert 'rules_to_consider' in result.rule_context
        assert 'TDD_ENFORCEMENT' in result.rule_context['rules_to_consider']
        assert 'DEFINITION_OF_DONE' in result.rule_context['rules_to_consider']
        assert result.rule_context['intelligent_test_determination'] is True
        assert result.rule_context['skip_summary_generation'] is True
    
    def test_classify_architecture_intent_attaches_crawler_rules(self, router):
        """Verify ARCHITECTURE intent enables crawlers"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="analyze the system architecture"
        )
        
        result = router._classify_intent_with_rules(request)
        
        assert result.intent == IntentType.ARCHITECTURE
        
        # Verify crawler activation
        assert 'enable_crawlers' in result.rule_context
        assert result.rule_context['enable_crawlers'] is True
        assert result.rule_context['skip_summary_generation'] is False  # Investigations need summaries
        assert result.rule_context['requires_documentation'] is True
    
    def test_classify_fix_intent_skips_tdd_intelligently(self, router):
        """Verify FIX intent uses intelligent test determination (not always TDD)"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="fix the typo in the comment"
        )
        
        result = router._classify_intent_with_rules(request)
        
        assert result.intent == IntentType.FIX
        
        # Verify DoD but not always TDD
        assert 'DEFINITION_OF_DONE' in result.rule_context['rules_to_consider']
        assert 'TDD_ENFORCEMENT' not in result.rule_context['rules_to_consider']
        assert result.rule_context['intelligent_test_determination'] is True
    
    def test_classify_plan_intent_creates_persistent_artifact(self, router):
        """Verify PLAN intent creates files (not ephemeral summaries)"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="let's plan the authentication feature"
        )
        
        result = router._classify_intent_with_rules(request)
        
        assert result.intent == IntentType.PLAN
        
        # Verify planning behavior
        assert 'INCREMENTAL_PLAN_GENERATION' in result.rule_context['rules_to_consider']
        assert result.rule_context['skip_summary_generation'] is False  # Plans ARE deliverables
        assert result.rule_context['create_persistent_artifact'] is True
    
    def test_classify_screenshot_intent_enables_vision_api(self, router):
        """Verify SCREENSHOT intent enables vision API"""
        request = AgentRequest(
            intent="unknown",
            context={'image_base64': 'fake_image_data'},
            user_message="what's in this screenshot?"
        )
        
        result = router._classify_intent_with_rules(request)
        
        assert result.intent == IntentType.SCREENSHOT
        assert result.confidence == 1.0  # High confidence when image present
        
        # Verify vision API activation
        assert 'enable_vision_api' in result.rule_context
        assert result.rule_context['enable_vision_api'] is True
    
    def test_classify_unknown_intent_returns_empty_rules(self, router):
        """Verify UNKNOWN intent has no rule context"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="asdfghjkl qwerty"  # Gibberish
        )
        
        result = router._classify_intent_with_rules(request)
        
        assert result.intent == IntentType.UNKNOWN
        assert result.confidence == 0.0
        assert result.rule_context == {}  # No rules for unknown


class TestRoutingDecisionWithRules:
    """Test routing decisions include rule context"""
    
    @pytest.fixture
    def router(self):
        """Create IntentRouter instance for testing"""
        return IntentRouter(name="TestRouter", tier1_api=None, tier2_kg=None, tier3_context=None)
    
    def test_routing_decision_includes_rule_context(self, router):
        """Verify routing decision includes rule context from classification"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="implement a new user service"
        )
        
        # Use router execute to get full routing decision
        response = router.execute(request)
        
        assert response.success is True
        assert 'rule_context' in response.result
        
        rule_context = response.result['rule_context']
        assert 'rules_to_consider' in rule_context
        assert 'intelligent_test_determination' in rule_context
    
    def test_routing_metadata_includes_classification_info(self, router):
        """Verify response metadata includes classification confidence and rules"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="create authentication tests"
        )
        
        response = router.execute(request)
        
        assert 'classification_confidence' in response.metadata
        assert 'rule_context' in response.metadata
        assert 'routing_confidence' in response.metadata


class TestRuleContextMapping:
    """Test rule context mapping completeness"""
    
    @pytest.fixture
    def router(self):
        """Create IntentRouter instance for testing"""
        return IntentRouter(name="TestRouter", tier1_api=None, tier2_kg=None, tier3_context=None)
    
    def test_all_code_intents_have_dod_rules(self, router):
        """Verify all code-related intents enforce Definition of Done"""
        code_intents = [
            IntentType.CODE,
            IntentType.IMPLEMENT,
            IntentType.EDIT_FILE,
            IntentType.REFACTOR
        ]
        
        for intent_type in code_intents:
            rule_context = router.INTENT_RULE_CONTEXT.get(intent_type, {})
            rules = rule_context.get('rules_to_consider', [])
            
            assert 'DEFINITION_OF_DONE' in rules, \
                f"{intent_type.value} must enforce Definition of Done"
            assert rule_context.get('requires_dod_validation') is True
    
    def test_investigation_intents_allow_summaries(self, router):
        """Verify investigation intents don't suppress summaries"""
        investigation_intents = [
            IntentType.ARCHITECTURE,
            IntentType.ANALYZE_STRUCTURE,
            IntentType.DEBUG
        ]
        
        for intent_type in investigation_intents:
            rule_context = router.INTENT_RULE_CONTEXT.get(intent_type, {})
            
            assert rule_context.get('skip_summary_generation') is False, \
                f"{intent_type.value} should allow summaries for investigations"
    
    def test_execution_intents_suppress_summaries(self, router):
        """Verify execution intents suppress automatic summaries"""
        execution_intents = [
            IntentType.CODE,
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.TEST
        ]
        
        for intent_type in execution_intents:
            rule_context = router.INTENT_RULE_CONTEXT.get(intent_type, {})
            
            assert rule_context.get('skip_summary_generation') is True, \
                f"{intent_type.value} should suppress automatic summaries"


class TestBackwardCompatibility:
    """Test backward compatibility with existing code"""
    
    @pytest.fixture
    def router(self):
        """Create IntentRouter instance for testing"""
        return IntentRouter(name="TestRouter", tier1_api=None, tier2_kg=None, tier3_context=None)
    
    def test_legacy_classify_intent_still_works(self, router):
        """Verify old _classify_intent() method still works"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="create a new module"
        )
        
        # Legacy method should still return IntentType
        intent = router._classify_intent(request)
        
        assert isinstance(intent, IntentType)
        assert intent == IntentType.CODE
    
    def test_routing_decision_without_classification_result(self, router):
        """Verify routing decision works without classification result (legacy)"""
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="implement feature"
        )
        
        decision = router._make_routing_decision(
            intent=IntentType.IMPLEMENT,
            similar_patterns=[],
            request=request,
            classification_result=None  # Legacy call without classification
        )
        
        assert 'primary_agent' in decision
        assert 'confidence' in decision
        # Rule context should be missing (legacy behavior)
        assert 'rule_context' not in decision


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
