"""User Experience Optimization Module (AC-RESP-004-01).

Author: CORTEX Framework
Date: 2025
Version: 1.0.0
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from scipy import stats


class FeedbackSentiment(str, Enum):
    """User feedback sentiment classification.
    
    Attributes:
        VERY_NEGATIVE: Rating 1
        NEGATIVE: Rating 2
        NEUTRAL: Rating 3
        POSITIVE: Rating 4
        VERY_POSITIVE: Rating 5
    """
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


# CONSOLIDATED: Import from cortex.orchestrators.response.unified_response_composer
# class QualityMetricType(str, Enum):
    """Quality metric types.
    
    Attributes:
        CLARITY: Response clarity and readability
        COMPLETENESS: Response completeness
        RELEVANCE: Response relevance to query
        TONE_APPROPRIATENESS: Tone appropriateness
        ACTIONABILITY: Actionability of response
        ACCURACY: Response accuracy
        EFFICIENCY: Response efficiency
    """
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    TONE_APPROPRIATENESS = "tone_appropriateness"
    ACTIONABILITY = "actionability"
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"


@dataclass
class ResponseQualityMetrics:
    """Response quality metrics.
    
    Attributes:
        response_id: Response identifier
        timestamp: Metric calculation timestamp
        clarity_score: Clarity score (0-100)
        completeness_score: Completeness score (0-100)
        relevance_score: Relevance score (0-100)
        tone_appropriateness: Tone appropriateness score (0-100)
        actionability: Actionability score (0-100)
        accuracy: Accuracy score (0-100)
        efficiency: Efficiency score (0-100)
        overall_score: Overall quality score (0-100)
        feedback_count: Number of feedback entries
        user_rating_avg: Average user rating (0-5)
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
    
    def __post_init__(self) -> None:
        """Validate metrics after initialization."""
        # Validate scores (0-100)
        score_fields = [
            'clarity_score', 'completeness_score', 'relevance_score',
            'tone_appropriateness', 'actionability', 'accuracy',
            'efficiency', 'overall_score'
        ]
        
        for field_name in score_fields:
            value = getattr(self, field_name)
            if not (0.0 <= value <= 100.0):
                raise ValueError(f"{field_name} must be between 0 and 100")
        
        # Validate rating (0-5)
        if not (0.0 <= self.user_rating_avg <= 5.0):
            raise ValueError("user_rating_avg must be between 0 and 5")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary.
        
        Returns:
            Dictionary representation of metrics
        """
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
            'user_rating_avg': self.user_rating_avg
        }


@dataclass
class UserFeedback:
    """User feedback data.
    
    Attributes:
        feedback_id: Feedback identifier
        response_id: Associated response identifier
        rating: User rating (1-5)
        timestamp: Feedback timestamp
        user_id: Optional user identifier
        comment: Optional feedback comment
        recommendation: Whether user recommends
        metrics_tags: Optional tags for specific metrics
        sentiment: Auto-classified sentiment
    """
    feedback_id: str
    response_id: str
    rating: int
    timestamp: datetime
    user_id: Optional[str] = None
    comment: str = ""
    recommendation: Optional[bool] = None
    metrics_tags: Optional[Dict[str, bool]] = None
    sentiment: FeedbackSentiment = field(init=False)
    
    def __post_init__(self) -> None:
        """Validate and classify feedback after initialization."""
        # Validate rating
        if not (1 <= self.rating <= 5):
            raise ValueError("rating must be between 1 and 5")
        
        # Auto-classify sentiment based on rating
        if self.rating == 1:
            self.sentiment = FeedbackSentiment.VERY_NEGATIVE
        elif self.rating == 2:
            self.sentiment = FeedbackSentiment.NEGATIVE
        elif self.rating == 3:
            self.sentiment = FeedbackSentiment.NEUTRAL
        elif self.rating == 4:
            self.sentiment = FeedbackSentiment.POSITIVE
        else:  # rating == 5
            self.sentiment = FeedbackSentiment.VERY_POSITIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback to dictionary.
        
        Returns:
            Dictionary representation of feedback
        """
        return {
            'feedback_id': self.feedback_id,
            'response_id': self.response_id,
            'rating': self.rating,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'comment': self.comment,
            'recommendation': self.recommendation,
            'sentiment': self.sentiment.value
        }


@dataclass
class ABTestVariant:
    """A/B test variant data.
    
    Attributes:
        variant_id: Variant identifier
        variant_name: Variant display name
        response_template: Template used for variant
        description: Variant description
        created_at: Creation timestamp
        exposure_count: Number of exposures
        conversion_count: Number of conversions
        feedback_scores: List of feedback scores
    """
    variant_id: str
    variant_name: str
    response_template: str
    description: str
    created_at: datetime
    exposure_count: int = 0
    conversion_count: int = 0
    feedback_scores: List[int] = field(default_factory=list)
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate.
        
        Returns:
            Conversion rate (0.0-1.0)
        """
        if self.exposure_count == 0:
            return 0.0
        return self.conversion_count / self.exposure_count
    
    @property
    def average_feedback(self) -> float:
        """Calculate average feedback score.
        
        Returns:
            Average feedback score
        """
        if not self.feedback_scores:
            return 0.0
        return sum(self.feedback_scores) / len(self.feedback_scores)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert variant to dictionary.
        
        Returns:
            Dictionary representation of variant
        """
        return {
            'variant_id': self.variant_id,
            'variant_name': self.variant_name,
            'response_template': self.response_template,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'exposure_count': self.exposure_count,
            'conversion_count': self.conversion_count,
            'conversion_rate': self.conversion_rate,
            'feedback_scores': self.feedback_scores,
            'average_feedback': self.average_feedback
        }


class DefaultQualityScoringStrategy:
    """Default quality scoring strategy.
    
    Implements scoring algorithms for various quality metrics.
    """
    
    def score(
        self,
        response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[QualityMetricType, float]:
        """Score response quality across multiple metrics.
        
        Args:
            response: Response text to score
            context: Optional context information
            
        Returns:
            Dictionary of quality scores by metric type
        """
        context = context or {}
        
        return {
            QualityMetricType.CLARITY: self._calculate_clarity(response),
            QualityMetricType.COMPLETENESS: self._calculate_completeness(response),
            QualityMetricType.RELEVANCE: self._calculate_relevance(response, context),
            QualityMetricType.TONE_APPROPRIATENESS: self._calculate_tone_appropriateness(response, context),
            QualityMetricType.ACTIONABILITY: self._calculate_actionability(response),
            QualityMetricType.ACCURACY: self._calculate_accuracy(response, context),
            QualityMetricType.EFFICIENCY: self._calculate_efficiency(response)
        }
    
    def _calculate_clarity(self, text: str) -> float:
        """Calculate clarity score based on sentence structure.
        
        Args:
            text: Text to analyze
            
        Returns:
            Clarity score (0-100)
        """
        if not text:
            return 0.0
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 50.0
        
        # Calculate average sentence length
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Shorter sentences = higher clarity
        # Optimal: 10-20 words per sentence
        if avg_length <= 10:
            return 100.0
        elif avg_length <= 20:
            return 90.0
        elif avg_length <= 30:
            return 70.0
        else:
            return 50.0
    
    def _calculate_completeness(self, text: str) -> float:
        """Calculate completeness score based on length.
        
        Args:
            text: Text to analyze
            
        Returns:
            Completeness score (0-100)
        """
        if not text:
            return 0.0
        
        word_count = len(text.split())
        
        # Score based on word count
        if word_count < 10:
            return 40.0
        elif word_count < 50:
            return 70.0
        elif word_count < 200:
            return 85.0
        else:
            return 95.0
    
    def _calculate_relevance(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score based on context.
        
        Args:
            text: Text to analyze
            context: Context information
            
        Returns:
            Relevance score (0-100)
        """
        if not text:
            return 0.0
        
        # Base score
        score = 75.0
        
        # Check for query terms in response
        query = context.get('query', '')
        if query:
            query_terms = query.lower().split()
            text_lower = text.lower()
            matches = sum(1 for term in query_terms if term in text_lower)
            if matches > 0:
                score += min(25.0, matches * 5.0)
        
        return min(100.0, score)
    
    def _calculate_tone_appropriateness(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate tone appropriateness score.
        
        Args:
            text: Text to analyze
            context: Context information
            
        Returns:
            Tone appropriateness score (0-100)
        """
        # Default: assume appropriate tone
        return 80.0
    
    def _calculate_actionability(self, text: str) -> float:
        """Calculate actionability score based on action words.
        
        Args:
            text: Text to analyze
            
        Returns:
            Actionability score (0-100)
        """
        if not text:
            return 0.0
        
        # Look for action words
        action_words = [
            'implement', 'run', 'execute', 'follow', 'create',
            'build', 'test', 'configure', 'install', 'setup',
            'click', 'select', 'choose', 'enter', 'type'
        ]
        
        text_lower = text.lower()
        action_count = sum(1 for word in action_words if word in text_lower)
        
        # More action words = more actionable
        base_score = 50.0
        bonus = min(40.0, action_count * 10.0)
        
        return base_score + bonus
    
    def _calculate_accuracy(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate accuracy score.
        
        Args:
            text: Text to analyze
            context: Context information
            
        Returns:
            Accuracy score (0-100)
        """
        # Default: assume accurate
        return 85.0
    
    def _calculate_efficiency(self, text: str) -> float:
        """Calculate efficiency score based on conciseness.
        
        Args:
            text: Text to analyze
            
        Returns:
            Efficiency score (0-100)
        """
        if not text:
            return 0.0
        
        word_count = len(text.split())
        
        # Optimal: 50-150 words
        if 50 <= word_count <= 150:
            return 90.0
        elif word_count < 50:
            return 70.0  # Too brief
        elif word_count < 300:
            return 75.0  # Slightly long
        else:
            return 60.0  # Too verbose


class FeedbackRegistry:
    """Registry for user feedback and quality metrics.
    
    Attributes:
        _feedback: Dictionary of response_id to feedback list
        _metrics: Dictionary of response_id to metrics
    """
    
    def __init__(self) -> None:
        """Initialize the feedback registry."""
        self._feedback: Dict[str, List[UserFeedback]] = {}
        self._metrics: Dict[str, ResponseQualityMetrics] = {}
    
    def add_feedback(self, feedback: UserFeedback) -> None:
        """Add user feedback.
        
        Args:
            feedback: Feedback to add
        """
        if feedback.response_id not in self._feedback:
            self._feedback[feedback.response_id] = []
        self._feedback[feedback.response_id].append(feedback)
    
    def get_feedback(self, response_id: str) -> List[UserFeedback]:
        """Get feedback for a response.
        
        Args:
            response_id: Response identifier
            
        Returns:
            List of feedback entries
        """
        return self._feedback.get(response_id, [])
    
    def store_metrics(self, metrics: ResponseQualityMetrics) -> None:
        """Store quality metrics.
        
        Args:
            metrics: Metrics to store
        """
        self._metrics[metrics.response_id] = metrics
    
    def get_metrics(self, response_id: str) -> Optional[ResponseQualityMetrics]:
        """Get quality metrics for a response.
        
        Args:
            response_id: Response identifier
            
        Returns:
            Metrics if found, None otherwise
        """
        return self._metrics.get(response_id)
    
    def clear(self) -> None:
        """Clear all feedback and metrics."""
        self._feedback.clear()
        self._metrics.clear()


class ResponseUXOptimizer:
    """Response UX optimizer with feedback and A/B testing.
    
    Attributes:
        _scoring_strategy: Quality scoring strategy
        _feedback_registry: Feedback and metrics registry
        _ab_variants: Dictionary of A/B test variants
    """
    
    def __init__(
        self,
        scoring_strategy: Optional[DefaultQualityScoringStrategy] = None
    ) -> None:
        """Initialize the UX optimizer.
        
        Args:
            scoring_strategy: Optional custom scoring strategy
        """
        self._scoring_strategy = scoring_strategy or DefaultQualityScoringStrategy()
        self._feedback_registry = FeedbackRegistry()
        self._ab_variants: Dict[str, ABTestVariant] = {}
    
    def calculate_quality_metrics(
        self,
        response: str,
        response_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ResponseQualityMetrics:
        """Calculate quality metrics for a response.
        
        Args:
            response: Response text
            response_id: Response identifier
            context: Optional context information
            
        Returns:
            Quality metrics
        """
        # Calculate scores
        scores = self._scoring_strategy.score(response, context)
        
        # Calculate overall score
        overall = sum(scores.values()) / len(scores)
        
        # Get feedback stats
        feedback_list = self._feedback_registry.get_feedback(response_id)
        feedback_count = len(feedback_list)
        user_rating_avg = 0.0
        
        if feedback_list:
            user_rating_avg = sum(fb.rating for fb in feedback_list) / feedback_count
        
        # Create metrics
        metrics = ResponseQualityMetrics(
            response_id=response_id,
            timestamp=datetime.now(),
            clarity_score=scores[QualityMetricType.CLARITY],
            completeness_score=scores[QualityMetricType.COMPLETENESS],
            relevance_score=scores[QualityMetricType.RELEVANCE],
            tone_appropriateness=scores[QualityMetricType.TONE_APPROPRIATENESS],
            actionability=scores[QualityMetricType.ACTIONABILITY],
            accuracy=scores[QualityMetricType.ACCURACY],
            efficiency=scores[QualityMetricType.EFFICIENCY],
            overall_score=overall,
            feedback_count=feedback_count,
            user_rating_avg=user_rating_avg
        )
        
        # Store metrics
        self._feedback_registry.store_metrics(metrics)
        
        return metrics
    
    def record_feedback(
        self,
        response_id: str,
        feedback: UserFeedback
    ) -> None:
        """Record user feedback.
        
        Args:
            response_id: Response identifier
            feedback: User feedback
        """
        self._feedback_registry.add_feedback(feedback)
    
    def register_ab_variant(self, variant: ABTestVariant) -> None:
        """Register an A/B test variant.
        
        Args:
            variant: Variant to register
        """
        self._ab_variants[variant.variant_id] = variant
    
    def record_variant_exposure(self, variant_id: str) -> None:
        """Record variant exposure.
        
        Args:
            variant_id: Variant identifier
        """
        if variant_id in self._ab_variants:
            self._ab_variants[variant_id].exposure_count += 1
    
    def record_variant_conversion(
        self,
        variant_id: str,
        rating: int
    ) -> None:
        """Record variant conversion.
        
        Args:
            variant_id: Variant identifier
            rating: User rating (1-5)
        """
        if variant_id in self._ab_variants:
            variant = self._ab_variants[variant_id]
            variant.feedback_scores.append(rating)
            # Count conversion if rating >= 4
            if rating >= 4:
                variant.conversion_count += 1
    
    def determine_test_winner(
        self,
        variant_a_id: str,
        variant_b_id: str,
        confidence_level: float = 0.95
    ) -> Tuple[str, float, str]:
        """Determine A/B test winner using statistical test.
        
        Args:
            variant_a_id: Variant A identifier
            variant_b_id: Variant B identifier
            confidence_level: Confidence level for test (default 0.95)
            
        Returns:
            Tuple of (winner_id, p_value, conclusion)
            
        Raises:
            ValueError: If variants not registered
        """
        if variant_a_id not in self._ab_variants or variant_b_id not in self._ab_variants:
            raise ValueError("Both variants must be registered")
        
        variant_a = self._ab_variants[variant_a_id]
        variant_b = self._ab_variants[variant_b_id]
        
        # Check for sufficient data
        if not variant_a.feedback_scores or not variant_b.feedback_scores:
            return ("NO_WINNER", 1.0, "Insufficient data for statistical test")
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(
            variant_a.feedback_scores,
            variant_b.feedback_scores
        )
        
        # Determine winner
        alpha = 1 - confidence_level
        
        if p_value < alpha:
            # Statistically significant difference
            if variant_a.average_feedback > variant_b.average_feedback:
                return (variant_a_id, p_value, "VARIANT_A_WINS")
            else:
                return (variant_b_id, p_value, "VARIANT_B_WINS")
        else:
            # No significant difference
            return ("NO_WINNER", p_value, "No statistically significant winner")
    
    def get_optimization_recommendations(
        self,
        response_id: str
    ) -> List[str]:
        """Get optimization recommendations for a response.
        
        Args:
            response_id: Response identifier
            
        Returns:
            List of recommendation strings
        """
        metrics = self._feedback_registry.get_metrics(response_id)
        
        if not metrics:
            return []
        
        recommendations = []
        
        # Check each metric against thresholds
        if metrics.clarity_score < 70:
            recommendations.append(
                "Improve clarity by using shorter sentences and simpler language"
            )
        
        if metrics.completeness_score < 70:
            recommendations.append(
                "Improve completeness by providing more detailed information"
            )
        
        if metrics.relevance_score < 70:
            recommendations.append(
                "Improve relevance by focusing more on the user's query"
            )
        
        if metrics.tone_appropriateness < 70:
            recommendations.append(
                "Adjust tone to better match the context"
            )
        
        if metrics.actionability < 70:
            recommendations.append(
                "Improve actionability by including clear next steps"
            )
        
        if metrics.accuracy < 70:
            recommendations.append(
                "Verify accuracy of information provided"
            )
        
        if metrics.efficiency < 70:
            recommendations.append(
                "Improve efficiency by being more concise"
            )
        
        return recommendations


# Singleton instance
_ux_optimizer: Optional[ResponseUXOptimizer] = None


def get_ux_optimizer() -> ResponseUXOptimizer:
    """Get the singleton UX optimizer instance.
    
    Returns:
        UX optimizer instance
    """
    global _ux_optimizer
    if _ux_optimizer is None:
        _ux_optimizer = ResponseUXOptimizer()
    return _ux_optimizer


def reset_ux_optimizer() -> None:
    """Reset the UX optimizer singleton."""
    global _ux_optimizer
    _ux_optimizer = None


__all__ = [
    "FeedbackSentiment",
    "QualityMetricType",
    "ResponseQualityMetrics",
    "UserFeedback",
    "ABTestVariant",
    "DefaultQualityScoringStrategy",
    "FeedbackRegistry",
    "ResponseUXOptimizer",
    "get_ux_optimizer",
    "reset_ux_optimizer"
]
