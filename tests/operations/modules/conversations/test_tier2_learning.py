"""
Tests for Tier 2 Learning Integration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from src.operations.modules.conversations.tier2_learning import (
    Tier2LearningIntegration,
    UserResponse,
    ThresholdRecommendation,
    create_tier2_learning
)


class TestTier2Learning:
    """Test suite for Tier 2 Learning Integration."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()
    
    def test_initialization(self, temp_storage):
        """Test learning integration initializes correctly."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        assert learner.min_samples == 10
        assert learner.high_threshold == 0.70
        assert learner.low_threshold == 0.30
        assert len(learner.responses) == 0
    
    def test_custom_config(self, temp_storage):
        """Test with custom configuration."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=5,
            high_acceptance_threshold=0.80,
            low_acceptance_threshold=0.20
        )
        
        assert learner.min_samples == 5
        assert learner.high_threshold == 0.80
        assert learner.low_threshold == 0.20
    
    def test_record_response(self, temp_storage):
        """Test recording user response."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        learner.record_response(
            session_id="test-1",
            response="accepted",
            quality_score=14,
            quality_level="GOOD"
        )
        
        assert len(learner.responses) == 1
        assert learner.responses[0].response == "accepted"
        assert learner.responses[0].quality_level == "GOOD"
    
    def test_record_multiple_responses(self, temp_storage):
        """Test recording multiple responses."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        responses = [
            ("test-1", "accepted", 20, "EXCELLENT"),
            ("test-2", "rejected", 14, "GOOD"),
            ("test-3", "accepted", 15, "GOOD"),
            ("test-4", "ignored", 22, "EXCELLENT")
        ]
        
        for session_id, response, score, level in responses:
            learner.record_response(session_id, response, score, level)
        
        assert len(learner.responses) == 4
    
    def test_acceptance_rate_overall(self, temp_storage):
        """Test calculating overall acceptance rate."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        # 3 accepted out of 5 = 60%
        learner.record_response("s1", "accepted", 14, "GOOD")
        learner.record_response("s2", "accepted", 15, "GOOD")
        learner.record_response("s3", "rejected", 16, "GOOD")
        learner.record_response("s4", "accepted", 17, "GOOD")
        learner.record_response("s5", "ignored", 18, "GOOD")
        
        rate = learner.get_acceptance_rate()
        assert rate == 0.6  # 3/5
    
    def test_acceptance_rate_by_level(self, temp_storage):
        """Test calculating acceptance rate by quality level."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        # GOOD: 2 accepted out of 3
        learner.record_response("s1", "accepted", 14, "GOOD")
        learner.record_response("s2", "accepted", 15, "GOOD")
        learner.record_response("s3", "rejected", 16, "GOOD")
        
        # EXCELLENT: 1 accepted out of 2
        learner.record_response("s4", "accepted", 20, "EXCELLENT")
        learner.record_response("s5", "rejected", 22, "EXCELLENT")
        
        good_rate = learner.get_acceptance_rate("GOOD")
        excellent_rate = learner.get_acceptance_rate("EXCELLENT")
        
        assert good_rate == pytest.approx(0.667, rel=0.01)
        assert excellent_rate == 0.5
    
    def test_response_stats(self, temp_storage):
        """Test comprehensive response statistics."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        learner.record_response("s1", "accepted", 14, "GOOD")
        learner.record_response("s2", "accepted", 15, "GOOD")
        learner.record_response("s3", "rejected", 16, "GOOD")
        learner.record_response("s4", "ignored", 20, "EXCELLENT")
        learner.record_response("s5", "accepted", 22, "EXCELLENT")
        
        stats = learner.get_response_stats()
        
        assert stats['total_responses'] == 5
        assert stats['accepted'] == 3
        assert stats['rejected'] == 1
        assert stats['ignored'] == 1
        assert stats['acceptance_rate'] == 0.6
        
        # By level
        assert stats['by_quality_level']['GOOD']['total'] == 3
        assert stats['by_quality_level']['GOOD']['accepted'] == 2
        assert stats['by_quality_level']['EXCELLENT']['total'] == 2
        assert stats['by_quality_level']['EXCELLENT']['accepted'] == 1
    
    def test_no_recommendation_insufficient_data(self, temp_storage):
        """Test no recommendation with insufficient data."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=10
        )
        
        # Only 5 responses, need 10
        for i in range(5):
            learner.record_response(f"s{i}", "accepted", 14, "GOOD")
        
        recommendation = learner.recommend_threshold_adjustment("GOOD")
        
        assert recommendation is None
    
    def test_recommendation_high_acceptance_lower_threshold(self, temp_storage):
        """Test recommendation to lower threshold with high acceptance."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=10,
            high_acceptance_threshold=0.70
        )
        
        # 9 accepted out of 10 = 90% (high acceptance)
        for i in range(9):
            learner.record_response(f"s{i}", "accepted", 20, "EXCELLENT")
        learner.record_response("s10", "rejected", 22, "EXCELLENT")
        
        recommendation = learner.recommend_threshold_adjustment("EXCELLENT")
        
        assert recommendation is not None
        assert recommendation.recommended_threshold == "GOOD"
        assert "High acceptance rate" in recommendation.reasoning
    
    def test_recommendation_low_acceptance_raise_threshold(self, temp_storage):
        """Test recommendation to raise threshold with low acceptance."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=10,
            low_acceptance_threshold=0.30
        )
        
        # 2 accepted out of 10 = 20% (low acceptance)
        for i in range(2):
            learner.record_response(f"s{i}", "accepted", 14, "GOOD")
        for i in range(8):
            learner.record_response(f"s{i+2}", "rejected", 15, "GOOD")
        
        recommendation = learner.recommend_threshold_adjustment("GOOD")
        
        assert recommendation is not None
        assert recommendation.recommended_threshold == "EXCELLENT"
        assert "Low acceptance rate" in recommendation.reasoning
    
    def test_recommendation_balanced_no_change(self, temp_storage):
        """Test no change recommendation with balanced acceptance."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=10
        )
        
        # 5 accepted out of 10 = 50% (balanced)
        for i in range(5):
            learner.record_response(f"s{i}", "accepted", 14, "GOOD")
        for i in range(5):
            learner.record_response(f"s{i+5}", "rejected", 15, "GOOD")
        
        recommendation = learner.recommend_threshold_adjustment("GOOD")
        
        assert recommendation is not None
        assert recommendation.recommended_threshold == "GOOD"
        assert "balanced" in recommendation.reasoning.lower()
    
    def test_should_adjust_threshold_true(self, temp_storage):
        """Test should_adjust_threshold returns True when needed."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=10
        )
        
        # High acceptance (90%) at EXCELLENT → should lower to GOOD
        for i in range(9):
            learner.record_response(f"s{i}", "accepted", 20, "EXCELLENT")
        learner.record_response("s10", "rejected", 22, "EXCELLENT")
        
        assert learner.should_adjust_threshold("EXCELLENT") is True
    
    def test_should_adjust_threshold_false_balanced(self, temp_storage):
        """Test should_adjust_threshold returns False when balanced."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=10
        )
        
        # Balanced acceptance (50%)
        for i in range(5):
            learner.record_response(f"s{i}", "accepted", 14, "GOOD")
        for i in range(5):
            learner.record_response(f"s{i+5}", "rejected", 15, "GOOD")
        
        assert learner.should_adjust_threshold("GOOD") is False
    
    def test_quality_level_preferences(self, temp_storage):
        """Test getting user preferences by quality level."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        # GOOD: 2/3 = 66.7%
        learner.record_response("s1", "accepted", 14, "GOOD")
        learner.record_response("s2", "accepted", 15, "GOOD")
        learner.record_response("s3", "rejected", 16, "GOOD")
        
        # EXCELLENT: 1/2 = 50%
        learner.record_response("s4", "accepted", 20, "EXCELLENT")
        learner.record_response("s5", "rejected", 22, "EXCELLENT")
        
        prefs = learner.get_quality_level_preferences()
        
        assert prefs['GOOD'] == pytest.approx(0.667, rel=0.01)
        assert prefs['EXCELLENT'] == 0.5
    
    def test_persistence_save_and_load(self, temp_storage):
        """Test data persists across instances."""
        # Create first instance and record data
        learner1 = Tier2LearningIntegration(storage_path=temp_storage)
        learner1.record_response("s1", "accepted", 14, "GOOD")
        learner1.record_response("s2", "rejected", 15, "GOOD")
        
        # Create new instance with same storage
        learner2 = Tier2LearningIntegration(storage_path=temp_storage)
        
        # Should have loaded previous data
        assert len(learner2.responses) == 2
        assert learner2.responses[0].response == "accepted"
        assert learner2.responses[1].response == "rejected"
    
    def test_reset_learning_data(self, temp_storage):
        """Test resetting learning data."""
        learner = Tier2LearningIntegration(storage_path=temp_storage)
        
        learner.record_response("s1", "accepted", 14, "GOOD")
        learner.record_response("s2", "rejected", 15, "GOOD")
        
        assert len(learner.responses) == 2
        
        learner.reset_learning_data()
        
        assert len(learner.responses) == 0
        
        # Verify persistence
        learner2 = Tier2LearningIntegration(storage_path=temp_storage)
        assert len(learner2.responses) == 0
    
    def test_confidence_increases_with_samples(self, temp_storage):
        """Test confidence increases with more samples."""
        learner = Tier2LearningIntegration(
            storage_path=temp_storage,
            min_samples_for_learning=10
        )
        
        # Add 10 samples (minimum)
        for i in range(10):
            learner.record_response(f"s{i}", "accepted", 14, "GOOD")
        
        rec1 = learner.recommend_threshold_adjustment("GOOD")
        confidence1 = rec1.confidence
        
        # Add 10 more samples (double minimum)
        for i in range(10):
            learner.record_response(f"s{i+10}", "accepted", 14, "GOOD")
        
        rec2 = learner.recommend_threshold_adjustment("GOOD")
        confidence2 = rec2.confidence
        
        # Confidence should be higher with more samples
        assert confidence2 > confidence1
        assert confidence2 == 1.0  # Caps at 1.0
    
    def test_factory_function_default(self, temp_storage):
        """Test factory function with defaults."""
        config = {'storage_path': str(temp_storage)}
        learner = create_tier2_learning(config)
        
        assert learner.min_samples == 10
        assert learner.high_threshold == 0.70
        assert learner.low_threshold == 0.30
    
    def test_factory_function_custom(self, temp_storage):
        """Test factory function with custom config."""
        config = {
            'storage_path': str(temp_storage),
            'min_samples_for_learning': 5,
            'high_acceptance_threshold': 0.80,
            'low_acceptance_threshold': 0.20
        }
        
        learner = create_tier2_learning(config)
        
        assert learner.min_samples == 5
        assert learner.high_threshold == 0.80
        assert learner.low_threshold == 0.20
    
    def test_user_response_serialization(self):
        """Test UserResponse to/from dict."""
        response = UserResponse(
            session_id="test-123",
            response="accepted",
            quality_score=14,
            quality_level="GOOD",
            timestamp=datetime(2025, 11, 16, 12, 0, 0)
        )
        
        # To dict
        data = response.to_dict()
        assert data['session_id'] == "test-123"
        assert data['response'] == "accepted"
        assert data['quality_score'] == 14
        
        # From dict
        restored = UserResponse.from_dict(data)
        assert restored.session_id == response.session_id
        assert restored.response == response.response
        assert restored.quality_score == response.quality_score
