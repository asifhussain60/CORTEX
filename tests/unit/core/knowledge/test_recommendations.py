"""Tests for recommendations engine."""
import pytest
from cortex.core.knowledge.recommendations import RecommendationEngine, Recommendation

@pytest.fixture
def recommendation_engine():
    backends = {"backend_a": {}, "backend_b": {}}
    return RecommendationEngine(backends)

def test_get_recommendations_basic(recommendation_engine):
    """Test basic recommendation generation."""
    context = {"topic": "machine learning", "difficulty": "advanced"}
    recs = recommendation_engine.get_recommendations(context)
    assert isinstance(recs, list)

def test_get_recommendations_with_context(recommendation_engine):
    """Test recommendations with specific context."""
    context = {"skill": "python", "interest": "data science"}
    recs = recommendation_engine.get_recommendations(context)
    if recs:
        assert all(isinstance(r, Recommendation) for r in recs)

def test_get_recommendations_confidence_scores(recommendation_engine):
    """Test recommendation confidence scoring."""
    context = {"query": "algorithms"}
    recs = recommendation_engine.get_recommendations(context)
    if recs:
        assert all(0 <= r.confidence <= 1 for r in recs)

def test_recommendations_sorted_by_confidence(recommendation_engine):
    """Test recommendations sorted by confidence."""
    context = {"topic": "ml"}
    recs = recommendation_engine.get_recommendations(context)
    if len(recs) > 1:
        for i in range(len(recs) - 1):
            assert recs[i].confidence >= recs[i+1].confidence

def test_learn_from_interaction(recommendation_engine):
    """Test learning from user interaction."""
    recommendation_engine.learn_from_interaction("user1", "doc1", "view", 0.8)
    assert "user1" in recommendation_engine.behavior_history
    assert len(recommendation_engine.behavior_history["user1"]) == 1

def test_multiple_interactions(recommendation_engine):
    """Test recording multiple interactions."""
    recommendation_engine.learn_from_interaction("user1", "doc1", "view", 0.8)
    recommendation_engine.learn_from_interaction("user1", "doc2", "click", 0.9)
    recommendation_engine.learn_from_interaction("user2", "doc1", "share", 0.7)
    assert len(recommendation_engine.behavior_history["user1"]) == 2
    assert len(recommendation_engine.behavior_history["user2"]) == 1

def test_get_behavioral_recommendations(recommendation_engine):
    """Test behavioral recommendations."""
    recommendation_engine.learn_from_interaction("user1", "doc1", "view", 0.8)
    recommendation_engine.learn_from_interaction("user1", "doc2", "view", 0.8)
    recs = recommendation_engine.get_behavioral_recommendations("user1")
    assert isinstance(recs, list)

def test_behavioral_recommendations_based_on_history(recommendation_engine):
    """Test that behavioral recs reflect access history."""
    recommendation_engine.learn_from_interaction("user1", "doc1", "view", 0.8)
    recommendation_engine.learn_from_interaction("user1", "doc1", "view", 0.8)
    recommendation_engine.learn_from_interaction("user1", "doc2", "view", 0.8)
    recs = recommendation_engine.get_behavioral_recommendations("user1")
    if recs:
        assert recs[0].knowledge_id == "doc1"

def test_behavioral_recommendations_limit(recommendation_engine):
    """Test behavioral recommendations limit."""
    for i in range(20):
        recommendation_engine.learn_from_interaction("user1", f"doc{i}", "view", 0.8)
    recs = recommendation_engine.get_behavioral_recommendations("user1", limit=5)
    assert len(recs) <= 5

def test_behavioral_recommendations_no_history(recommendation_engine):
    """Test behavioral recommendations with no history."""
    recs = recommendation_engine.get_behavioral_recommendations("nonexistent_user")
    assert len(recs) == 0

def test_recommendation_reason(recommendation_engine):
    """Test recommendation includes reason."""
    context = {"topic": "test"}
    recs = recommendation_engine.get_recommendations(context)
    if recs:
        assert all(r.reason for r in recs)

def test_recommendation_attributes(recommendation_engine):
    """Test recommendation has all attributes."""
    context = {"query": "test"}
    recs = recommendation_engine.get_recommendations(context)
    if recs:
        r = recs[0]
        assert hasattr(r, "knowledge_id")
        assert hasattr(r, "confidence")
        assert hasattr(r, "reason")
        assert hasattr(r, "backend")

def test_context_score_computation(recommendation_engine):
    """Test context scoring."""
    context1 = {"key": "short"}
    context2 = {"key": "this is a much longer value with more content"}
    context3 = {"key": 42}
    
    recs1 = recommendation_engine.get_recommendations(context1)
    recs2 = recommendation_engine.get_recommendations(context2)
    recs3 = recommendation_engine.get_recommendations(context3)
    
    assert isinstance(recs1, list)
    assert isinstance(recs2, list)
    assert isinstance(recs3, list)

def test_multiple_users_isolation(recommendation_engine):
    """Test recommendation history isolation between users."""
    recommendation_engine.learn_from_interaction("user1", "doc1", "view", 0.8)
    recommendation_engine.learn_from_interaction("user2", "doc2", "view", 0.8)
    
    recs1 = recommendation_engine.get_behavioral_recommendations("user1")
    recs2 = recommendation_engine.get_behavioral_recommendations("user2")
    
    if recs1:
        assert recs1[0].knowledge_id == "doc1"
    if recs2:
        assert recs2[0].knowledge_id == "doc2"
