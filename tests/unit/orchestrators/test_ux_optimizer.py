"""
Comprehensive test suite for User Experience Optimization Module

Tests AC-RESP-004-01: User Experience Optimization

Test Coverage:
  - ResponseQualityMetrics validation and conversion
  - UserFeedback creation, validation, and sentiment classification
  - ABTestVariant properties and conversion
  - QualityScoringStrategy implementations
  - FeedbackRegistry operations
  - ResponseUXOptimizer quality metrics calculation
  - A/B test winner determination
  - Optimization recommendations
  - Edge cases and error handling

Total Tests: 20+
"""

import pytest
from datetime import datetime, timedelta
from cortex.orchestrators.response.ux_optimizer import (
    ResponseQualityMetrics,
    UserFeedback,
    ABTestVariant,
    QualityMetricType,
    FeedbackSentiment,
    DefaultQualityScoringStrategy,
    FeedbackRegistry,
    ResponseUXOptimizer,
    get_ux_optimizer,
    reset_ux_optimizer,
)


class TestResponseQualityMetrics:
    """Test ResponseQualityMetrics class."""

    def test_metrics_creation(self):
        """Test creating quality metrics."""
        metrics = ResponseQualityMetrics(
            response_id="resp_123",
            timestamp=datetime.now(),
            clarity_score=85.0,
            completeness_score=75.0,
            relevance_score=90.0,
            tone_appropriateness=80.0,
            actionability=70.0,
            accuracy=88.0,
            efficiency=65.0,
            overall_score=80.0,
        )
        
        assert metrics.response_id == "resp_123"
        assert metrics.clarity_score == 85.0
        assert metrics.overall_score == 80.0

    def test_metrics_validation_invalid_score(self):
        """Test metrics validation rejects invalid scores."""
        with pytest.raises(ValueError, match="clarity_score must be between 0 and 100"):
            ResponseQualityMetrics(
                response_id="resp_123",
                timestamp=datetime.now(),
                clarity_score=105.0,  # Invalid
            )

    def test_metrics_validation_invalid_rating(self):
        """Test metrics validation rejects invalid ratings."""
        with pytest.raises(ValueError, match="user_rating_avg must be between 0 and 5"):
            ResponseQualityMetrics(
                response_id="resp_123",
                timestamp=datetime.now(),
                user_rating_avg=6.0,  # Invalid
            )

    def test_metrics_to_dict(self):
        """Test converting metrics to dictionary."""
        now = datetime.now()
        metrics = ResponseQualityMetrics(
            response_id="resp_123",
            timestamp=now,
            clarity_score=80.0,
            overall_score=85.0,
            feedback_count=5,
            user_rating_avg=4.2,
        )
        
        data = metrics.to_dict()
        
        assert data['response_id'] == "resp_123"
        assert data['clarity_score'] == 80.0
        assert data['overall_score'] == 85.0
        assert data['feedback_count'] == 5
        assert data['user_rating_avg'] == 4.2


class TestUserFeedback:
    """Test UserFeedback class."""

    def test_feedback_creation(self):
        """Test creating user feedback."""
        feedback = UserFeedback(
            feedback_id="fb_123",
            response_id="resp_123",
            rating=4,
            timestamp=datetime.now(),
            comment="Great response!",
            recommendation=True,
        )
        
        assert feedback.feedback_id == "fb_123"
        assert feedback.rating == 4
        assert feedback.comment == "Great response!"

    def test_feedback_auto_sentiment_classification(self):
        """Test automatic sentiment classification."""
        # Very negative
        fb1 = UserFeedback(
            feedback_id="fb1", response_id="r1", rating=1, timestamp=datetime.now()
        )
        assert fb1.sentiment == FeedbackSentiment.VERY_NEGATIVE

        # Negative
        fb2 = UserFeedback(
            feedback_id="fb2", response_id="r2", rating=2, timestamp=datetime.now()
        )
        assert fb2.sentiment == FeedbackSentiment.NEGATIVE

        # Neutral
        fb3 = UserFeedback(
            feedback_id="fb3", response_id="r3", rating=3, timestamp=datetime.now()
        )
        assert fb3.sentiment == FeedbackSentiment.NEUTRAL

        # Positive
        fb4 = UserFeedback(
            feedback_id="fb4", response_id="r4", rating=4, timestamp=datetime.now()
        )
        assert fb4.sentiment == FeedbackSentiment.POSITIVE

        # Very positive
        fb5 = UserFeedback(
            feedback_id="fb5", response_id="r5", rating=5, timestamp=datetime.now()
        )
        assert fb5.sentiment == FeedbackSentiment.VERY_POSITIVE

    def test_feedback_validation_invalid_rating(self):
        """Test feedback validation rejects invalid ratings."""
        with pytest.raises(ValueError, match="rating must be between 1 and 5"):
            UserFeedback(
                feedback_id="fb_123",
                response_id="resp_123",
                rating=6,  # Invalid
                timestamp=datetime.now(),
            )

    def test_feedback_to_dict(self):
        """Test converting feedback to dictionary."""
        now = datetime.now()
        feedback = UserFeedback(
            feedback_id="fb_123",
            response_id="resp_123",
            rating=4,
            timestamp=now,
            user_id="user_456",
            comment="Good",
        )
        
        data = feedback.to_dict()
        
        assert data['feedback_id'] == "fb_123"
        assert data['rating'] == 4
        assert data['user_id'] == "user_456"
        assert data['comment'] == "Good"


class TestABTestVariant:
    """Test ABTestVariant class."""

    def test_variant_creation(self):
        """Test creating A/B test variant."""
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_v1",
            description="Control group",
            created_at=datetime.now(),
        )
        
        assert variant.variant_id == "var_a"
        assert variant.variant_name == "Variant A"

    def test_variant_conversion_rate(self):
        """Test conversion rate calculation."""
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_v1",
            description="Test",
            created_at=datetime.now(),
            exposure_count=100,
            conversion_count=25,
        )
        
        assert variant.conversion_rate == 0.25

    def test_variant_conversion_rate_zero_exposure(self):
        """Test conversion rate with zero exposure."""
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_v1",
            description="Test",
            created_at=datetime.now(),
            exposure_count=0,
            conversion_count=0,
        )
        
        assert variant.conversion_rate == 0.0

    def test_variant_average_feedback(self):
        """Test average feedback calculation."""
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_v1",
            description="Test",
            created_at=datetime.now(),
            feedback_scores=[4, 5, 3, 5, 4],
        )
        
        assert variant.average_feedback == pytest.approx(4.2)

    def test_variant_average_feedback_empty(self):
        """Test average feedback with no scores."""
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_v1",
            description="Test",
            created_at=datetime.now(),
            feedback_scores=[],
        )
        
        assert variant.average_feedback == 0.0

    def test_variant_to_dict(self):
        """Test converting variant to dictionary."""
        now = datetime.now()
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_v1",
            description="Control",
            created_at=now,
            exposure_count=100,
            conversion_count=20,
            feedback_scores=[4, 5, 3, 4],
        )
        
        data = variant.to_dict()
        
        assert data['variant_id'] == "var_a"
        assert data['exposure_count'] == 100
        assert data['conversion_count'] == 20
        assert data['conversion_rate'] == 0.2
        assert data['average_feedback'] == pytest.approx(4.0)


class TestDefaultQualityScoringStrategy:
    """Test DefaultQualityScoringStrategy."""

    def test_clarity_calculation(self):
        """Test clarity score calculation."""
        strategy = DefaultQualityScoringStrategy()
        
        # Short sentences = high clarity
        response = "Step one. Step two. Step three."
        clarity = strategy._calculate_clarity(response)
        assert clarity == 100.0

    def test_clarity_empty_text(self):
        """Test clarity with empty text."""
        strategy = DefaultQualityScoringStrategy()
        clarity = strategy._calculate_clarity("")
        assert clarity == 0.0

    def test_completeness_calculation(self):
        """Test completeness score calculation."""
        strategy = DefaultQualityScoringStrategy()
        
        # Very short = low completeness
        short_response = "No."
        completeness = strategy._calculate_completeness(short_response)
        assert completeness == 40.0

    def test_relevance_calculation(self):
        """Test relevance score calculation."""
        strategy = DefaultQualityScoringStrategy()
        
        response = "The algorithm optimization improves performance significantly."
        context = {'query': 'algorithm optimization'}
        
        relevance = strategy._calculate_relevance(response, context)
        assert relevance > 70.0

    def test_actionability_calculation(self):
        """Test actionability score calculation."""
        strategy = DefaultQualityScoringStrategy()
        
        response = "Follow these steps: implement the algorithm, run the code, and execute tests."
        actionability = strategy._calculate_actionability(response)
        assert actionability > 60.0

    def test_score_method(self):
        """Test full scoring strategy."""
        strategy = DefaultQualityScoringStrategy()
        
        response = "Here is a comprehensive solution. Follow these steps to implement."
        context = {'query': 'solution', 'requested_tone': 'TECHNICAL'}
        
        scores = strategy.score(response, context)
        
        assert QualityMetricType.CLARITY in scores
        assert QualityMetricType.COMPLETENESS in scores
        assert QualityMetricType.RELEVANCE in scores
        assert QualityMetricType.TONE_APPROPRIATENESS in scores
        assert QualityMetricType.ACTIONABILITY in scores
        assert QualityMetricType.ACCURACY in scores
        assert QualityMetricType.EFFICIENCY in scores
        
        for metric_type, score in scores.items():
            assert 0.0 <= score <= 100.0


class TestFeedbackRegistry:
    """Test FeedbackRegistry class."""

    def test_registry_creation(self):
        """Test creating feedback registry."""
        registry = FeedbackRegistry()
        assert registry is not None

    def test_add_and_get_feedback(self):
        """Test adding and retrieving feedback."""
        registry = FeedbackRegistry()
        
        feedback = UserFeedback(
            feedback_id="fb_1",
            response_id="resp_1",
            rating=4,
            timestamp=datetime.now(),
        )
        
        registry.add_feedback(feedback)
        
        retrieved = registry.get_feedback("resp_1")
        assert len(retrieved) == 1
        assert retrieved[0].feedback_id == "fb_1"

    def test_get_feedback_empty(self):
        """Test getting feedback for non-existent response."""
        registry = FeedbackRegistry()
        feedback = registry.get_feedback("non_existent")
        assert feedback == []

    def test_store_and_get_metrics(self):
        """Test storing and retrieving metrics."""
        registry = FeedbackRegistry()
        
        metrics = ResponseQualityMetrics(
            response_id="resp_1",
            timestamp=datetime.now(),
            overall_score=85.0,
        )
        
        registry.store_metrics(metrics)
        
        retrieved = registry.get_metrics("resp_1")
        assert retrieved is not None
        assert retrieved.overall_score == 85.0

    def test_registry_clear(self):
        """Test clearing registry."""
        registry = FeedbackRegistry()
        
        feedback = UserFeedback(
            feedback_id="fb_1",
            response_id="resp_1",
            rating=4,
            timestamp=datetime.now(),
        )
        registry.add_feedback(feedback)
        
        metrics = ResponseQualityMetrics(
            response_id="resp_1",
            timestamp=datetime.now(),
        )
        registry.store_metrics(metrics)
        
        registry.clear()
        
        assert registry.get_feedback("resp_1") == []
        assert registry.get_metrics("resp_1") is None


class TestResponseUXOptimizer:
    """Test ResponseUXOptimizer class."""

    def test_optimizer_creation(self):
        """Test creating optimizer."""
        optimizer = ResponseUXOptimizer()
        assert optimizer is not None

    def test_optimizer_custom_strategy(self):
        """Test optimizer with custom strategy."""
        strategy = DefaultQualityScoringStrategy()
        optimizer = ResponseUXOptimizer(scoring_strategy=strategy)
        assert optimizer is not None

    def test_calculate_quality_metrics(self):
        """Test quality metrics calculation."""
        optimizer = ResponseUXOptimizer()
        
        response = "This is a comprehensive solution with clear steps to follow."
        metrics = optimizer.calculate_quality_metrics(response, "resp_1")
        
        assert metrics.response_id == "resp_1"
        assert metrics.clarity_score > 0
        assert metrics.completeness_score > 0
        assert metrics.overall_score > 0
        assert 0 <= metrics.overall_score <= 100

    def test_calculate_metrics_with_context(self):
        """Test metrics calculation with context."""
        optimizer = ResponseUXOptimizer()
        
        response = "The algorithm implementation is efficient."
        context = {
            'query': 'algorithm implementation',
            'requested_tone': 'TECHNICAL',
        }
        
        metrics = optimizer.calculate_quality_metrics(response, "resp_2", context)
        
        assert metrics.relevance_score > 60

    def test_record_feedback(self):
        """Test recording user feedback."""
        optimizer = ResponseUXOptimizer()
        
        feedback = UserFeedback(
            feedback_id="fb_1",
            response_id="resp_1",
            rating=4,
            timestamp=datetime.now(),
            comment="Good",
        )
        
        optimizer.record_feedback("resp_1", feedback)
        
        metrics = optimizer.calculate_quality_metrics("test", "resp_1")
        assert metrics.feedback_count == 1
        assert metrics.user_rating_avg == 4.0

    def test_record_multiple_feedback(self):
        """Test recording multiple feedback entries."""
        optimizer = ResponseUXOptimizer()
        
        feedbacks = [
            UserFeedback(f"fb_{i}", "resp_1", rating=i+1, timestamp=datetime.now())
            for i in range(5)
        ]
        
        for fb in feedbacks:
            optimizer.record_feedback("resp_1", fb)
        
        metrics = optimizer.calculate_quality_metrics("test", "resp_1")
        assert metrics.feedback_count == 5
        assert metrics.user_rating_avg == pytest.approx(3.0)  # average of 1,2,3,4,5

    def test_register_ab_variant(self):
        """Test registering A/B test variant."""
        optimizer = ResponseUXOptimizer()
        
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Control",
            response_template="template_1",
            description="Control group",
            created_at=datetime.now(),
        )
        
        optimizer.register_ab_variant(variant)
        assert "var_a" in optimizer._ab_variants

    def test_record_variant_exposure(self):
        """Test recording variant exposure."""
        optimizer = ResponseUXOptimizer()
        
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Control",
            response_template="template_1",
            description="Control",
            created_at=datetime.now(),
        )
        
        optimizer.register_ab_variant(variant)
        
        optimizer.record_variant_exposure("var_a")
        optimizer.record_variant_exposure("var_a")
        
        assert optimizer._ab_variants["var_a"].exposure_count == 2

    def test_record_variant_conversion(self):
        """Test recording variant conversion."""
        optimizer = ResponseUXOptimizer()
        
        variant = ABTestVariant(
            variant_id="var_a",
            variant_name="Control",
            response_template="template_1",
            description="Control",
            created_at=datetime.now(),
        )
        
        optimizer.register_ab_variant(variant)
        
        optimizer.record_variant_conversion("var_a", 5)  # High rating
        optimizer.record_variant_conversion("var_a", 3)  # Low rating
        
        assert optimizer._ab_variants["var_a"].conversion_count == 1  # Only 5 counts
        assert len(optimizer._ab_variants["var_a"].feedback_scores) == 2

    def test_determine_test_winner_variant_a_wins(self):
        """Test determining A/B test winner when A wins."""
        optimizer = ResponseUXOptimizer()
        
        var_a = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_a",
            description="A",
            created_at=datetime.now(),
            feedback_scores=[5, 5, 5, 4, 4],  # High scores
        )
        
        var_b = ABTestVariant(
            variant_id="var_b",
            variant_name="Variant B",
            response_template="template_b",
            description="B",
            created_at=datetime.now(),
            feedback_scores=[2, 2, 3, 2, 3],  # Low scores
        )
        
        optimizer.register_ab_variant(var_a)
        optimizer.register_ab_variant(var_b)
        
        winner_id, p_value, conclusion = optimizer.determine_test_winner("var_a", "var_b", 0.95)
        
        assert winner_id == "var_a"
        assert p_value < 0.05
        assert conclusion == "VARIANT_A_WINS"

    def test_determine_test_winner_no_winner(self):
        """Test determining A/B test winner with no significant difference."""
        optimizer = ResponseUXOptimizer()
        
        var_a = ABTestVariant(
            variant_id="var_a",
            variant_name="Variant A",
            response_template="template_a",
            description="A",
            created_at=datetime.now(),
            feedback_scores=[3, 3, 3, 3],
        )
        
        var_b = ABTestVariant(
            variant_id="var_b",
            variant_name="Variant B",
            response_template="template_b",
            description="B",
            created_at=datetime.now(),
            feedback_scores=[3, 3, 3, 3],
        )
        
        optimizer.register_ab_variant(var_a)
        optimizer.register_ab_variant(var_b)
        
        winner_id, p_value, conclusion = optimizer.determine_test_winner("var_a", "var_b", 0.95)
        
        assert winner_id == "NO_WINNER"
        assert conclusion == "No statistically significant winner"

    def test_determine_test_winner_insufficient_data(self):
        """Test determining winner with insufficient data."""
        optimizer = ResponseUXOptimizer()
        
        var_a = ABTestVariant(
            variant_id="var_a",
            variant_name="A",
            response_template="t_a",
            description="A",
            created_at=datetime.now(),
            feedback_scores=[],  # No feedback
        )
        
        var_b = ABTestVariant(
            variant_id="var_b",
            variant_name="B",
            response_template="t_b",
            description="B",
            created_at=datetime.now(),
            feedback_scores=[5, 4],
        )
        
        optimizer.register_ab_variant(var_a)
        optimizer.register_ab_variant(var_b)
        
        winner_id, p_value, conclusion = optimizer.determine_test_winner("var_a", "var_b")
        
        assert winner_id == "NO_WINNER"
        assert "Insufficient" in conclusion

    def test_determine_test_winner_missing_variant(self):
        """Test determining winner with missing variant."""
        optimizer = ResponseUXOptimizer()
        
        with pytest.raises(ValueError, match="Both variants must be registered"):
            optimizer.determine_test_winner("var_a", "var_b")

    def test_get_optimization_recommendations(self):
        """Test getting optimization recommendations."""
        optimizer = ResponseUXOptimizer()
        
        # Low quality metrics
        metrics = ResponseQualityMetrics(
            response_id="resp_1",
            timestamp=datetime.now(),
            clarity_score=50.0,
            completeness_score=40.0,
            relevance_score=60.0,
            overall_score=45.0,
        )
        
        optimizer._feedback_registry.store_metrics(metrics)
        
        recommendations = optimizer.get_optimization_recommendations("resp_1")
        
        assert len(recommendations) > 0
        assert any("clarity" in rec.lower() for rec in recommendations)
        assert any("completeness" in rec.lower() for rec in recommendations)

    def test_get_optimization_recommendations_high_quality(self):
        """Test getting recommendations for high quality response."""
        optimizer = ResponseUXOptimizer()
        
        metrics = ResponseQualityMetrics(
            response_id="resp_1",
            timestamp=datetime.now(),
            clarity_score=95.0,
            completeness_score=90.0,
            relevance_score=95.0,
            tone_appropriateness=90.0,
            actionability=85.0,
            accuracy=92.0,
            efficiency=88.0,
            overall_score=90.0,
        )
        
        optimizer._feedback_registry.store_metrics(metrics)
        
        recommendations = optimizer.get_optimization_recommendations("resp_1")
        
        # No recommendations for high quality
        assert len(recommendations) == 0

    def test_get_optimization_recommendations_no_metrics(self):
        """Test getting recommendations with no stored metrics."""
        optimizer = ResponseUXOptimizer()
        
        recommendations = optimizer.get_optimization_recommendations("non_existent")
        
        assert recommendations == []


class TestSingleton:
    """Test singleton pattern for UX optimizer."""

    def test_get_ux_optimizer_singleton(self):
        """Test get_ux_optimizer returns singleton."""
        reset_ux_optimizer()
        
        opt1 = get_ux_optimizer()
        opt2 = get_ux_optimizer()
        
        assert opt1 is opt2

    def test_reset_ux_optimizer(self):
        """Test resetting optimizer singleton."""
        reset_ux_optimizer()
        
        opt1 = get_ux_optimizer()
        reset_ux_optimizer()
        opt2 = get_ux_optimizer()
        
        assert opt1 is not opt2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_quality_metrics_boundary_values(self):
        """Test quality metrics with boundary values."""
        metrics = ResponseQualityMetrics(
            response_id="resp_1",
            timestamp=datetime.now(),
            clarity_score=0.0,
            completeness_score=100.0,
            overall_score=50.0,
        )
        
        assert metrics.clarity_score == 0.0
        assert metrics.completeness_score == 100.0

    def test_user_feedback_with_metrics_tags(self):
        """Test feedback with metrics tags."""
        feedback = UserFeedback(
            feedback_id="fb_1",
            response_id="resp_1",
            rating=4,
            timestamp=datetime.now(),
            metrics_tags={
                'clarity': True,
                'completeness': False,
                'relevance': True,
            },
        )
        
        assert feedback.metrics_tags['clarity'] is True
        assert feedback.metrics_tags['completeness'] is False

    def test_optimizer_multiple_responses(self):
        """Test optimizer handling multiple responses."""
        optimizer = ResponseUXOptimizer()
        
        for i in range(5):
            response = f"Response {i}"
            optimizer.calculate_quality_metrics(response, f"resp_{i}")
        
        for i in range(5):
            metrics = optimizer._feedback_registry.get_metrics(f"resp_{i}")
            assert metrics is not None
