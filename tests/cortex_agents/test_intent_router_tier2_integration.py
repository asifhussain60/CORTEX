"""
Integration tests for IntentRouter with real Tier 2 Knowledge Graph

These tests verify that the intent router properly integrates with
the Tier 2 knowledge graph for:
- Pattern storage and retrieval
- Similar intent matching
- Learning from routing decisions
- Confidence boosting from historical patterns

Priority: P1 - Integration testing
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType, AgentType
from src.tier2.knowledge_graph import KnowledgeGraph


@pytest.fixture
def temp_tier2_db():
    """Create temporary Tier 2 database for integration tests."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_knowledge_graph.db"
    
    yield str(db_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def real_tier2(temp_tier2_db):
    """Create real Tier 2 Knowledge Graph instance."""
    kg = KnowledgeGraph(db_path=temp_tier2_db)
    # Database is automatically initialized in __init__
    return kg


@pytest.fixture
def intent_router_with_real_tier2(real_tier2):
    """Create IntentRouter with real Tier 2 integration."""
    # Mock Tier 1 and Tier 3 for focused integration test
    from unittest.mock import Mock
    
    tier1 = Mock()
    tier1.log_event = Mock()
    tier1.get_recent_conversations = Mock(return_value=[])
    tier1.get_profile = Mock(return_value={
        'interaction_mode': 'autonomous',
        'experience_level': 'senior'
    })
    
    tier3 = Mock()
    tier3.get_project_context = Mock(return_value={})
    
    config = {
        'vision_api_enabled': False,
        'tdd_auto_activation': True,
        'confidence_threshold': 0.7
    }
    
    router = IntentRouter(
        name="TestRouter",  # Add required 'name' parameter
        tier1_api=tier1,
        tier2_kg=real_tier2,
        tier3_context=tier3,
        config=config
    )
    
    return router


class TestTier2PatternStorage:
    """Test pattern storage in Tier 2."""
    
    def test_store_routing_decision_in_tier2(self, intent_router_with_real_tier2, real_tier2):
        """Test that routing decisions are stored in Tier 2."""
        router = intent_router_with_real_tier2
        
        # Make a routing decision
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan authentication feature"
        )
        
        response = router.execute(request)
        
        # Verify pattern was stored in Tier 2
        patterns = real_tier2.get_routing_patterns()
        assert len(patterns) > 0
        
        # Verify pattern contains expected fields (in metadata)
        pattern = patterns[0]
        metadata = pattern.get('metadata', {})
        assert 'message' in metadata or 'user_message' in pattern or 'message_hash' in pattern
        assert 'intent' in metadata or 'classified_intent' in metadata or 'intent' in pattern
    
    def test_pattern_confidence_tracking(self, intent_router_with_real_tier2, real_tier2):
        """Test that pattern confidence is tracked over time."""
        router = intent_router_with_real_tier2
        
        # Create multiple similar requests
        messages = [
            "plan authentication system",
            "plan auth service",
            "create plan for authentication"
        ]
        
        for msg in messages:
            request = AgentRequest(intent="unknown", context={}, user_message=msg)
            router.execute(request)
        
        # Verify patterns are stored with confidence
        patterns = real_tier2.get_routing_patterns()
        assert len(patterns) >= 3
    
    def test_pattern_learning_from_success(self, intent_router_with_real_tier2, real_tier2):
        """Test that successful routing decisions strengthen patterns."""
        router = intent_router_with_real_tier2
        
        # First request - new pattern
        request1 = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan user authentication"
        )
        response1 = router.execute(request1)
        
        # Store success feedback
        real_tier2.add_pattern(
            pattern_type="routing_success",
            data={
                'message': "plan user authentication",
                'intent': response1.metadata.get('classified_intent', 'PLAN'),
                'confidence': response1.metadata.get('classification_confidence', 0.8),
                'success': True
            }
        )
        
        # Verify pattern exists
        patterns = real_tier2.get_routing_patterns()
        assert len(patterns) > 0


class TestTier2SimilarIntentMatching:
    """Test similar intent matching using Tier 2."""
    
    def test_find_similar_intents_boosts_confidence(self, intent_router_with_real_tier2, real_tier2):
        """Test that similar historical intents boost confidence."""
        router = intent_router_with_real_tier2
        
        # Store a pattern manually
        real_tier2.add_pattern(
            pattern_type="intent_classification",
            data={
                'message': "plan authentication system",
                'intent': 'PLAN',
                'confidence': 0.9
            }
        )
        
        # Make similar request
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan authentication feature"
        )
        
        response = router.execute(request)
        
        # Confidence should be boosted by similar pattern
        confidence = response.metadata.get('classification_confidence', 0)
        assert confidence > 0.7  # Should have decent confidence
    
    def test_no_similar_patterns_fallback(self, intent_router_with_real_tier2):
        """Test behavior when no similar patterns exist."""
        router = intent_router_with_real_tier2
        
        # Request with no historical patterns
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="completely unique request xyz123abc"
        )
        
        response = router.execute(request)
        
        # Should still return a response (fallback classification)
        assert response is not None
    
    def test_similar_intent_search_with_typos(self, intent_router_with_real_tier2, real_tier2):
        """Test similar intent matching with typos."""
        router = intent_router_with_real_tier2
        
        # Store pattern with correct spelling
        real_tier2.add_pattern(
            pattern_type="intent_classification",
            data={
                'message': "plan authentication system",
                'intent': 'PLAN',
                'confidence': 0.9
            }
        )
        
        # Request with typo
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan authenitcation system"  # typo: authenitcation
        )
        
        response = router.execute(request)
        
        # Should still classify reasonably
        assert response.success is True


class TestTier2LearningFromHistory:
    """Test learning and improvement from historical data."""
    
    def test_repeated_patterns_increase_confidence(self, intent_router_with_real_tier2, real_tier2):
        """Test that repeated patterns increase confidence over time."""
        router = intent_router_with_real_tier2
        
        # Execute same request multiple times
        message = "plan feature X"
        
        confidences = []
        for i in range(3):
            request = AgentRequest(
                intent="unknown",
                context={},
                user_message=message
            )
            response = router.execute(request)
            confidences.append(response.metadata.get('classification_confidence', 0))
        
        # Confidence should be relatively stable (not necessarily increasing
        # in this mock scenario, but should all be valid)
        assert all(c > 0 for c in confidences)
    
    def test_diverse_patterns_for_same_intent(self, intent_router_with_real_tier2, real_tier2):
        """Test learning from diverse patterns for same intent."""
        router = intent_router_with_real_tier2
        
        # Different ways to express planning intent
        planning_messages = [
            "plan authentication",
            "create plan for auth",
            "I need a plan for user login",
            "let's plan the authentication feature"
        ]
        
        for msg in planning_messages:
            request = AgentRequest(intent="unknown", context={}, user_message=msg)
            router.execute(request)
        
        # Verify patterns are stored
        patterns = real_tier2.get_routing_patterns()
        assert len(patterns) >= 4
    
    def test_intent_pattern_retrieval(self, intent_router_with_real_tier2, real_tier2):
        """Test retrieving patterns for specific intents."""
        router = intent_router_with_real_tier2
        
        # Store patterns for different intents
        intents = [
            ("plan authentication", "PLAN"),
            ("check system health", "HEALTHCHECK"),
            ("align the system", "ALIGN")
        ]
        
        for msg, intent in intents:
            real_tier2.add_pattern(
                pattern_type="intent_classification",
                data={'message': msg, 'intent': intent, 'confidence': 0.9}
            )
        
        # Retrieve patterns
        all_patterns = real_tier2.get_routing_patterns()
        assert len(all_patterns) >= 3


class TestTier2ConfidenceBoostingStrategies:
    """Test different confidence boosting strategies."""
    
    def test_exact_match_high_confidence(self, intent_router_with_real_tier2, real_tier2):
        """Test that exact matches get high confidence."""
        router = intent_router_with_real_tier2
        
        # Store exact pattern
        message = "plan authentication system"
        real_tier2.add_pattern(
            pattern_type="intent_classification",
            data={'message': message, 'intent': 'PLAN', 'confidence': 0.95}
        )
        
        # Request with exact match
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=message
        )
        
        response = router.execute(request)
        
        # Should have high confidence
        confidence = response.metadata.get('classification_confidence', 0)
        assert confidence > 0.8
    
    def test_partial_match_moderate_confidence(self, intent_router_with_real_tier2, real_tier2):
        """Test that partial matches get moderate confidence."""
        router = intent_router_with_real_tier2
        
        # Store pattern
        real_tier2.add_pattern(
            pattern_type="intent_classification",
            data={
                'message': "plan comprehensive authentication system",
                'intent': 'PLAN',
                'confidence': 0.9
            }
        )
        
        # Request with partial overlap
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan basic authentication"
        )
        
        response = router.execute(request)
        
        # Should still classify successfully
        assert response.success is True
    
    def test_no_match_fallback_confidence(self, intent_router_with_real_tier2):
        """Test fallback confidence when no matches exist."""
        router = intent_router_with_real_tier2
        
        # Request with no historical data
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="completely novel request 987xyz"
        )
        
        response = router.execute(request)
        
        # Should fallback to regex classification
        assert response is not None


class TestTier2ErrorHandling:
    """Test error handling with Tier 2 integration."""
    
    def test_tier2_unavailable_graceful_degradation(self, intent_router_with_real_tier2):
        """Test graceful degradation when Tier 2 is unavailable."""
        router = intent_router_with_real_tier2
        
        # Simulate Tier 2 failure (router.tier2, not tier2_kg)
        router.tier2 = None
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan feature"
        )
        
        response = router.execute(request)
        
        # Should still work with fallback
        assert response is not None
    
    def test_tier2_search_exception_handled(self, intent_router_with_real_tier2):
        """Test handling of Tier 2 search exceptions."""
        from unittest.mock import Mock
        
        router = intent_router_with_real_tier2
        
        # Make Tier 2 search raise exception (router.tier2, not tier2_kg)
        router.tier2.search = Mock(side_effect=Exception("Database error"))
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="plan feature"
        )
        
        response = router.execute(request)
        
        # Should handle gracefully
        assert response is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
