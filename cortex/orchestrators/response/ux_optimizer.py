"""UX Optimizer

Author: CORTEX Framework
"""

from dataclasses import dataclass
from enum import Enum


class FeedbackSentiment(Enum):
    """User feedback sentiment."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


@dataclass
class ResponseQualityMetrics:
    """Response quality metrics."""
    clarity_score: float = 0.0
    relevance_score: float = 0.0
    completeness_score: float = 0.0


@dataclass
class UserFeedback:
    """User feedback data."""
    feedback_id: str
    rating: int
    comment: str = ""
    sentiment: FeedbackSentiment = FeedbackSentiment.NEUTRAL


@dataclass
class ABTestVariant:
    """A/B test variant."""
    variant_id: str
    name: str
    config: dict = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


class QualityMetricType(Enum):
    """Quality metric types."""
    CLARITY = "clarity"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    HELPFULNESS = "helpfulness"


class UXOptimizer:
    """Optimize user experience."""
    
    def optimize(self, response: str) -> str:
        """Optimize response."""
        return response
    
    def get_metrics(self) -> ResponseQualityMetrics:
        """Get quality metrics."""
        return ResponseQualityMetrics()


class DefaultQualityScoringStrategy:
    """Default quality scoring strategy."""
    
    def score(self, response: str) -> float:
        """Score response quality."""
        return 0.75


class FeedbackRegistry:
    """Registry for user feedback."""
    
    def __init__(self):
        self.feedback = []
    
    def add(self, feedback: UserFeedback) -> None:
        """Add feedback."""
        self.feedback.append(feedback)
    
    def get_all(self) -> list:
        """Get all feedback."""
        return self.feedback


class ResponseUXOptimizer:
    """Response UX optimizer with feedback."""
    
    def __init__(self):
        self.optimizer = UXOptimizer()
        self.registry = FeedbackRegistry()
    
    def optimize(self, response: str) -> str:
        """Optimize response UX."""
        return self.optimizer.optimize(response)

__all__ = ["FeedbackSentiment", "ResponseQualityMetrics", "UserFeedback", "ABTestVariant", "QualityMetricType", "DefaultQualityScoringStrategy", "FeedbackRegistry", "ResponseUXOptimizer", "UXOptimizer"]
