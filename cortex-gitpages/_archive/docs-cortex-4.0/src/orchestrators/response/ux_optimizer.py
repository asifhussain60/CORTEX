"""
User Experience Optimization Module for Response Composition System

AC-RESP-004-01: Implement response quality metrics, user feedback integration,
A/B testing support, and response optimization recommendations.

This module provides:
  - ResponseQualityMetrics: Quantifiable measures of response quality
  - UserFeedback: Structured user feedback capture and storage
  - ABTestVariant: Variant configuration for A/B testing
  - ResponseUXOptimizer: Main optimizer engine for response quality analysis

Architecture:
  - Strategy pattern for different quality scoring algorithms
  - Registry pattern for feedback storage and retrieval
  - Statistical analysis for A/B test winner determination
  - Caching for performance optimization

Example:
    >>> optimizer = get_ux_optimizer()
    >>> metrics = optimizer.calculate_quality_metrics(response)
    >>> feedback = UserFeedback(rating=4, comment="Clear and helpful")
    >>> optimizer.record_feedback("response_123", feedback)
    >>> test_result = optimizer.determine_test_winner(variant_a_id, variant_b_id)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import statistics
import math
from abc import ABC, abstractmethod


class QualityMetricType(Enum):
    """Types of quality metrics."""
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    TONE_APPROPRIATENESS = "tone_appropriateness"
    ACTIONABILITY = "actionability"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    OVERALL = "overall"


class FeedbackSentiment(Enum):
    """User feedback sentiment classification."""
    VERY_NEGATIVE = 1
    NEGATIVE = 2
    NEUTRAL = 3
    POSITIVE = 4
    VERY_POSITIVE = 5


class TestStatistic(Enum):
    """Statistical test types for A/B testing."""
    CHI_SQUARE = "chi_square"
    T_TEST = "t_test"
    MANN_WHITNEY_U = "mann_whitney_u"
    BINOMIAL = "binomial"


@dataclass
class ResponseQualityMetrics:
    """
    Quantifiable measures of response quality.
    
    Attributes:
        response_id: Unique identifier for the response
        timestamp: When metrics were calculated
        clarity_score: Clarity of communication (0-100)
        completeness_score: Completeness of information (0-100)
        relevance_score: Relevance to query (0-100)
        tone_appropriateness: Appropriateness of tone (0-100)
        actionability: Usefulness of action items (0-100)
        accuracy: Factual accuracy (0-100)
        efficiency: Conciseness and efficiency (0-100)
        overall_score: Weighted average of all metrics (0-100)
        feedback_count: Number of user feedback entries
        user_rating_avg: Average user rating (1-5 scale)
        confidence_level: Confidence in metrics (0-100)
    """
    response_id: str
    timestamp: datetime
    clarity_score: float = 0.0
    completeness_score: float = 0.0
    relevance_score: float = 0.0
    tone_appropriateness: float = 0.0
    actionability: float = 0.0
    accuracy: float = 0.0
    efficiency: float = 0.0
    overall_score: float = 0.0
    feedback_count: int = 0
    user_rating_avg: float = 0.0
    confidence_level: float = 0.0

    def __post_init__(self):
        """Validate metric scores are in valid range."""
        for score_name in ['clarity_score', 'completeness_score', 'relevance_score',
                          'tone_appropriateness', 'actionability', 'accuracy',
                          'efficiency', 'overall_score', 'confidence_level']:
            score = getattr(self, score_name)
            if not 0.0 <= score <= 100.0:
                raise ValueError(f"{score_name} must be between 0 and 100, got {score}")
        
        if not 0.0 <= self.user_rating_avg <= 5.0:
            raise ValueError(f"user_rating_avg must be between 0 and 5, got {self.user_rating_avg}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'response_id': self.response_id,
            'timestamp': self.timestamp.isoformat(),
            'clarity_score': self.clarity_score,
            'completeness_score': self.completeness_score,
            'relevance_score': self.relevance_score,
            'tone_appropriateness': self.tone_appropriateness,
            'actionability': self.actionability,
            'accuracy': self.accuracy,
            'efficiency': self.efficiency,
            'overall_score': self.overall_score,
            'feedback_count': self.feedback_count,
            'user_rating_avg': self.user_rating_avg,
            'confidence_level': self.confidence_level,
        }


@dataclass
class UserFeedback:
    """
    Structured user feedback capture and storage.
    
    Attributes:
        feedback_id: Unique feedback identifier
        response_id: ID of response being rated
        user_id: ID of user providing feedback (optional, anonymous if not provided)
        rating: Numeric rating (1-5 scale)
        sentiment: Classified sentiment
        comment: Optional text feedback
        timestamp: When feedback was provided
        metrics_tags: Optional tags for specific metric evaluation
        recommendation: Whether user would recommend this response
    """
    feedback_id: str
    response_id: str
    rating: int
    timestamp: datetime
    user_id: Optional[str] = None
    comment: Optional[str] = None
    sentiment: Optional[FeedbackSentiment] = None
    metrics_tags: Dict[str, bool] = field(default_factory=dict)
    recommendation: bool = True

    def __post_init__(self):
        """Validate feedback."""
        if not 1 <= self.rating <= 5:
            raise ValueError(f"rating must be between 1 and 5, got {self.rating}")
        
        # Auto-classify sentiment if not provided
        if self.sentiment is None:
            if self.rating <= 2:
                self.sentiment = FeedbackSentiment(self.rating)
            elif self.rating == 3:
                self.sentiment = FeedbackSentiment.NEUTRAL
            else:
                self.sentiment = FeedbackSentiment(self.rating)

    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback to dictionary."""
        return {
            'feedback_id': self.feedback_id,
            'response_id': self.response_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'sentiment': self.sentiment.name if self.sentiment else None,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat(),
            'metrics_tags': self.metrics_tags,
            'recommendation': self.recommendation,
        }


@dataclass
class ABTestVariant:
    """
    Variant configuration for A/B testing.
    
    Attributes:
        variant_id: Unique variant identifier
        variant_name: Human-readable name
        response_template: Template/pattern used for this variant
        description: Description of variant changes
        created_at: When variant was created
        exposure_count: Number of times variant was shown
        conversion_count: Number of positive outcomes
        feedback_scores: List of user ratings for this variant
        metadata: Additional variant metadata
    """
    variant_id: str
    variant_name: str
    response_template: str
    description: str
    created_at: datetime
    exposure_count: int = 0
    conversion_count: int = 0
    feedback_scores: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate."""
        if self.exposure_count == 0:
            return 0.0
        return self.conversion_count / self.exposure_count

    @property
    def average_feedback(self) -> float:
        """Calculate average feedback score."""
        if not self.feedback_scores:
            return 0.0
        return sum(self.feedback_scores) / len(self.feedback_scores)

    def to_dict(self) -> Dict[str, Any]:
        """Convert variant to dictionary."""
        return {
            'variant_id': self.variant_id,
            'variant_name': self.variant_name,
            'response_template': self.response_template,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'exposure_count': self.exposure_count,
            'conversion_count': self.conversion_count,
            'conversion_rate': self.conversion_rate,
            'average_feedback': self.average_feedback,
            'feedback_count': len(self.feedback_scores),
            'metadata': self.metadata,
        }


class QualityScoringStrategy(ABC):
    """Abstract base for quality scoring strategies."""

    @abstractmethod
    def score(self, response_text: str, context: Dict[str, Any]) -> Dict[QualityMetricType, float]:
        """
        Calculate quality scores for a response.
        
        Args:
            response_text: The response to score
            context: Additional context for scoring
            
        Returns:
            Dictionary mapping metric types to scores (0-100)
        """
        pass


class DefaultQualityScoringStrategy(QualityScoringStrategy):
    """Default quality scoring implementation."""

    def score(self, response_text: str, context: Dict[str, Any]) -> Dict[QualityMetricType, float]:
        """Calculate quality scores using heuristics."""
        scores = {}
        
        # Clarity: based on sentence complexity and length
        clarity = self._calculate_clarity(response_text)
        scores[QualityMetricType.CLARITY] = clarity
        
        # Completeness: based on response length and structure
        completeness = self._calculate_completeness(response_text)
        scores[QualityMetricType.COMPLETENESS] = completeness
        
        # Relevance: based on context matching (heuristic)
        relevance = self._calculate_relevance(response_text, context)
        scores[QualityMetricType.RELEVANCE] = relevance
        
        # Tone appropriateness: based on context
        tone = self._calculate_tone(response_text, context)
        scores[QualityMetricType.TONE_APPROPRIATENESS] = tone
        
        # Actionability: based on presence of action items
        actionability = self._calculate_actionability(response_text)
        scores[QualityMetricType.ACTIONABILITY] = actionability
        
        # Accuracy: default to neutral (requires external validation)
        scores[QualityMetricType.ACCURACY] = 50.0
        
        # Efficiency: based on word count vs content value
        efficiency = self._calculate_efficiency(response_text)
        scores[QualityMetricType.EFFICIENCY] = efficiency
        
        return scores

    @staticmethod
    def _calculate_clarity(text: str) -> float:
        """Calculate clarity score."""
        if not text:
            return 0.0
        
        # Heuristic: shorter sentences are generally clearer
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        if not sentences:
            return 50.0
        
        avg_words_per_sentence = sum(len(s.split()) for s in sentences) / len(sentences)
        # Optimal is 10-15 words per sentence
        if avg_words_per_sentence < 10:
            clarity = 100.0
        elif avg_words_per_sentence < 20:
            clarity = 90.0 - (avg_words_per_sentence - 10) * 2
        else:
            clarity = max(50.0, 90.0 - (avg_words_per_sentence - 10))
        
        return min(100.0, max(0.0, clarity))

    @staticmethod
    def _calculate_completeness(text: str) -> float:
        """Calculate completeness score."""
        if not text:
            return 0.0
        
        word_count = len(text.split())
        # Length heuristic: 100-500 words is ideal
        if word_count < 50:
            return 40.0
        elif word_count < 100:
            return 60.0
        elif word_count < 500:
            return 90.0
        elif word_count < 2000:
            return 95.0
        else:
            return 85.0

    @staticmethod
    def _calculate_relevance(text: str, context: Dict[str, Any]) -> float:
        """Calculate relevance score based on context matching."""
        if not text or not context:
            return 50.0
        
        # Simple heuristic: check if response mentions query terms
        query = context.get('query', '').lower()
        text_lower = text.lower()
        
        if not query:
            return 70.0
        
        query_terms = query.split()
        matched_terms = sum(1 for term in query_terms if term in text_lower)
        
        if not query_terms:
            return 50.0
        
        match_ratio = matched_terms / len(query_terms)
        return min(100.0, 50.0 + match_ratio * 50.0)

    @staticmethod
    def _calculate_tone(text: str, context: Dict[str, Any]) -> float:
        """Calculate tone appropriateness."""
        requested_tone = context.get('requested_tone', 'FORMAL')
        
        # Simple heuristic based on formality indicators
        casual_words = ['hey', 'gonna', 'kinda', 'awesome', 'cool']
        technical_words = ['algorithm', 'implementation', 'architecture', 'optimization']
        
        text_lower = text.lower()
        casual_count = sum(1 for word in casual_words if word in text_lower)
        technical_count = sum(1 for word in technical_words if word in text_lower)
        
        # Score based on how well tone matches request
        if requested_tone == 'CASUAL':
            return 50.0 + casual_count * 5.0
        elif requested_tone == 'TECHNICAL':
            return 50.0 + technical_count * 5.0
        else:
            # FORMAL - prefer no casual language
            return max(50.0, 100.0 - casual_count * 10.0)

    @staticmethod
    def _calculate_actionability(text: str) -> float:
        """Calculate actionability score."""
        text_lower = text.lower()
        action_indicators = ['do', 'try', 'implement', 'follow', 'steps', 'instructions',
                            'example', 'code', 'run', 'execute']
        
        indicator_count = sum(1 for indicator in action_indicators if indicator in text_lower)
        
        # Score based on presence of action items
        return min(100.0, 50.0 + indicator_count * 5.0)

    @staticmethod
    def _calculate_efficiency(text: str) -> float:
        """Calculate efficiency score."""
        if not text:
            return 0.0
        
        word_count = len(text.split())
        unique_words = len(set(text.lower().split()))
        
        # Efficiency: ratio of unique words to total words
        # Higher is better (less repetition)
        if word_count == 0:
            return 50.0
        
        uniqueness_ratio = unique_words / word_count
        return min(100.0, uniqueness_ratio * 100.0)


class FeedbackRegistry:
    """Registry for storing and retrieving feedback."""

    def __init__(self):
        """Initialize feedback registry."""
        self._feedback: Dict[str, List[UserFeedback]] = {}
        self._response_metrics: Dict[str, ResponseQualityMetrics] = {}

    def add_feedback(self, feedback: UserFeedback) -> None:
        """
        Add feedback for a response.
        
        Args:
            feedback: UserFeedback instance
        """
        if feedback.response_id not in self._feedback:
            self._feedback[feedback.response_id] = []
        self._feedback[feedback.response_id].append(feedback)

    def get_feedback(self, response_id: str) -> List[UserFeedback]:
        """
        Get all feedback for a response.
        
        Args:
            response_id: Response identifier
            
        Returns:
            List of UserFeedback instances
        """
        return self._feedback.get(response_id, [])

    def store_metrics(self, metrics: ResponseQualityMetrics) -> None:
        """Store quality metrics."""
        self._response_metrics[metrics.response_id] = metrics

    def get_metrics(self, response_id: str) -> Optional[ResponseQualityMetrics]:
        """Get stored quality metrics."""
        return self._response_metrics.get(response_id)

    def clear(self) -> None:
        """Clear all stored feedback and metrics."""
        self._feedback.clear()
        self._response_metrics.clear()


class ResponseUXOptimizer:
    """
    Main optimizer engine for response quality analysis and optimization.
    
    Provides:
      - Quality metric calculation
      - User feedback tracking
      - A/B test analysis
      - Optimization recommendations
    """

    def __init__(self, scoring_strategy: Optional[QualityScoringStrategy] = None):
        """
        Initialize the UX optimizer.
        
        Args:
            scoring_strategy: Optional custom scoring strategy
        """
        self._scoring_strategy = scoring_strategy or DefaultQualityScoringStrategy()
        self._feedback_registry = FeedbackRegistry()
        self._ab_variants: Dict[str, ABTestVariant] = {}

    def calculate_quality_metrics(self, response_text: str, response_id: str = "default",
                                 context: Optional[Dict[str, Any]] = None) -> ResponseQualityMetrics:
        """
        Calculate quality metrics for a response.
        
        Args:
            response_text: The response to analyze
            response_id: Unique identifier for response
            context: Additional context for scoring
            
        Returns:
            ResponseQualityMetrics instance
        """
        if context is None:
            context = {}
        
        # Get individual scores
        scores = self._scoring_strategy.score(response_text, context)
        
        # Calculate overall score as weighted average
        weights = {
            QualityMetricType.CLARITY: 0.2,
            QualityMetricType.COMPLETENESS: 0.15,
            QualityMetricType.RELEVANCE: 0.25,
            QualityMetricType.TONE_APPROPRIATENESS: 0.15,
            QualityMetricType.ACTIONABILITY: 0.1,
            QualityMetricType.ACCURACY: 0.1,
            QualityMetricType.EFFICIENCY: 0.05,
        }
        
        overall_score = sum(scores.get(metric_type, 50.0) * weight
                           for metric_type, weight in weights.items())
        
        # Get feedback data if available
        feedback_list = self._feedback_registry.get_feedback(response_id)
        ratings = [fb.rating for fb in feedback_list if 1 <= fb.rating <= 5]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        metrics = ResponseQualityMetrics(
            response_id=response_id,
            timestamp=datetime.now(),
            clarity_score=scores.get(QualityMetricType.CLARITY, 0.0),
            completeness_score=scores.get(QualityMetricType.COMPLETENESS, 0.0),
            relevance_score=scores.get(QualityMetricType.RELEVANCE, 0.0),
            tone_appropriateness=scores.get(QualityMetricType.TONE_APPROPRIATENESS, 0.0),
            actionability=scores.get(QualityMetricType.ACTIONABILITY, 0.0),
            accuracy=scores.get(QualityMetricType.ACCURACY, 0.0),
            efficiency=scores.get(QualityMetricType.EFFICIENCY, 0.0),
            overall_score=overall_score,
            feedback_count=len(ratings),
            user_rating_avg=avg_rating,
            confidence_level=min(100.0, 80.0 + len(ratings) * 5.0),
        )
        
        self._feedback_registry.store_metrics(metrics)
        return metrics

    def record_feedback(self, response_id: str, feedback: UserFeedback) -> None:
        """
        Record user feedback for a response.
        
        Args:
            response_id: Response identifier
            feedback: UserFeedback instance
        """
        feedback.response_id = response_id
        self._feedback_registry.add_feedback(feedback)

    def register_ab_variant(self, variant: ABTestVariant) -> None:
        """
        Register an A/B test variant.
        
        Args:
            variant: ABTestVariant instance
        """
        self._ab_variants[variant.variant_id] = variant

    def record_variant_exposure(self, variant_id: str) -> None:
        """
        Record that a variant was shown to a user.
        
        Args:
            variant_id: Variant identifier
        """
        if variant_id in self._ab_variants:
            self._ab_variants[variant_id].exposure_count += 1

    def record_variant_conversion(self, variant_id: str, rating: int) -> None:
        """
        Record a conversion for a variant with user feedback.
        
        Args:
            variant_id: Variant identifier
            rating: User rating (1-5)
        """
        if variant_id in self._ab_variants:
            variant = self._ab_variants[variant_id]
            if rating >= 4:  # Consider 4+ as conversion
                variant.conversion_count += 1
            variant.feedback_scores.append(rating)

    def determine_test_winner(self, variant_a_id: str, variant_b_id: str,
                             confidence_level: float = 0.95) -> Tuple[str, float, str]:
        """
        Determine statistical winner in A/B test.
        
        Args:
            variant_a_id: First variant identifier
            variant_b_id: Second variant identifier
            confidence_level: Required confidence for decision (0-1)
            
        Returns:
            Tuple of (winner_id, p_value, conclusion)
            Conclusion is one of: "VARIANT_A_WINS", "VARIANT_B_WINS", "NO_WINNER"
        """
        variant_a = self._ab_variants.get(variant_a_id)
        variant_b = self._ab_variants.get(variant_b_id)
        
        if not variant_a or not variant_b:
            raise ValueError("Both variants must be registered")
        
        if not variant_a.feedback_scores or not variant_b.feedback_scores:
            return ("NO_WINNER", 0.0, "Insufficient feedback data")
        
        # Perform two-sample t-test on feedback scores
        p_value = self._calculate_t_test_p_value(variant_a.feedback_scores, 
                                                 variant_b.feedback_scores)
        
        # Determine winner
        alpha = 1.0 - confidence_level
        
        avg_a = variant_a.average_feedback
        avg_b = variant_b.average_feedback
        
        if p_value < alpha:
            # Statistically significant difference
            if avg_a > avg_b:
                return (variant_a_id, p_value, "VARIANT_A_WINS")
            else:
                return (variant_b_id, p_value, "VARIANT_B_WINS")
        else:
            # No significant difference
            return ("NO_WINNER", p_value, "No statistically significant winner")

    @staticmethod
    def _calculate_t_test_p_value(group_a: List[float], group_b: List[float]) -> float:
        """
        Calculate p-value for two-sample t-test.
        
        Args:
            group_a: First group of scores
            group_b: Second group of scores
            
        Returns:
            P-value (0-1)
        """
        if len(group_a) < 2 or len(group_b) < 2:
            return 1.0  # Not enough data
        
        mean_a = statistics.mean(group_a)
        mean_b = statistics.mean(group_b)
        
        # Welch's t-test (doesn't assume equal variances)
        try:
            var_a = statistics.variance(group_a)
            var_b = statistics.variance(group_b)
        except statistics.StatisticsError:
            return 1.0
        
        if var_a == 0 and var_b == 0:
            return 1.0
        
        # Calculate t-statistic
        n_a = len(group_a)
        n_b = len(group_b)
        
        se_sq = (var_a / n_a) + (var_b / n_b)
        if se_sq == 0:
            return 1.0
        
        t_stat = (mean_a - mean_b) / math.sqrt(se_sq)
        
        # Approximated p-value (simple approximation)
        # In production, use scipy.stats.ttest_ind
        p_value = 2.0 * (1.0 - ResponseUXOptimizer._normal_cdf(abs(t_stat)))
        
        return min(1.0, max(0.0, p_value))

    @staticmethod
    def _normal_cdf(x: float) -> float:
        """Approximate normal CDF using error function."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    def get_optimization_recommendations(self, response_id: str) -> List[str]:
        """
        Get recommendations for improving a response.
        
        Args:
            response_id: Response identifier
            
        Returns:
            List of optimization recommendations
        """
        metrics = self._feedback_registry.get_metrics(response_id)
        if not metrics:
            return []
        
        recommendations = []
        
        if metrics.clarity_score < 70:
            recommendations.append("Improve clarity: Consider using shorter sentences and simpler language")
        
        if metrics.completeness_score < 70:
            recommendations.append("Improve completeness: Add more details or structured information")
        
        if metrics.relevance_score < 70:
            recommendations.append("Improve relevance: Better align response with user query")
        
        if metrics.tone_appropriateness < 70:
            recommendations.append("Adjust tone: Ensure tone matches the context and user expectations")
        
        if metrics.actionability < 70:
            recommendations.append("Add actionability: Include concrete steps or examples")
        
        if metrics.efficiency < 70:
            recommendations.append("Improve efficiency: Reduce redundancy and improve conciseness")
        
        if metrics.overall_score < 60:
            recommendations.append("Overall quality is low: Consider major revisions")
        
        return recommendations


# Singleton instance and accessor
_optimizer_instance: Optional[ResponseUXOptimizer] = None


def get_ux_optimizer(scoring_strategy: Optional[QualityScoringStrategy] = None) -> ResponseUXOptimizer:
    """
    Get or create the global UX optimizer instance.
    
    Args:
        scoring_strategy: Optional custom scoring strategy
        
    Returns:
        ResponseUXOptimizer instance
    """
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = ResponseUXOptimizer(scoring_strategy)
    return _optimizer_instance


def reset_ux_optimizer() -> None:
    """Reset the global UX optimizer instance."""
    global _optimizer_instance
    _optimizer_instance = None
