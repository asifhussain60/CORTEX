"""RelevanceScore value object - Represents relevance between 0.0 and 1.0"""
from dataclasses import dataclass
from typing import Tuple, Any
from src.domain.common.value_object import ValueObject
from src.application.common.guards import Guard


@dataclass(frozen=True)
class RelevanceScore(ValueObject):
    """Represents relevance score between 0.0 and 1.0
    
    Used for measuring conversation relevance, pattern matching confidence,
    and context similarity throughout CORTEX.
    
    Quality Thresholds:
    - High: >= 0.80 (🟢)
    - Medium: 0.50-0.79 (🟡)
    - Low: < 0.50 (🔴)
    
    Example:
        score = RelevanceScore(0.85)
        print(score.is_high)  # True
        print(score.quality_label)  # "High"
        print(score.quality_emoji)  # "🟢"
    """
    value: float
    
    def __post_init__(self):
        """Validate score is in valid range [0.0, 1.0]"""
        Guard.against_out_of_range(
            self.value, 0.0, 1.0, 
            "RelevanceScore.value", 
            "RelevanceScore must be between 0.0 and 1.0"
        )
    
    @property
    def is_high(self) -> bool:
        """Check if relevance is high (>= 0.80)"""
        return self.value >= 0.80
    
    @property
    def is_medium(self) -> bool:
        """Check if relevance is medium (0.50-0.79)"""
        return 0.50 <= self.value < 0.80
    
    @property
    def is_low(self) -> bool:
        """Check if relevance is low (< 0.50)"""
        return self.value < 0.50
    
    @property
    def quality_label(self) -> str:
        """Get human-readable quality label"""
        if self.is_high:
            return "High"
        elif self.is_medium:
            return "Medium"
        else:
            return "Low"
    
    @property
    def quality_emoji(self) -> str:
        """Get emoji indicator for quality"""
        if self.is_high:
            return "🟢"
        elif self.is_medium:
            return "🟡"
        else:
            return "🔴"
    
    @property
    def percentage(self) -> float:
        """Get percentage representation"""
        return self.value * 100.0
    
    def exceeds_threshold(self, threshold: float) -> bool:
        """Check if score exceeds given threshold"""
        Guard.against_out_of_range(threshold, 0.0, 1.0, "threshold")
        return self.value >= threshold
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        """Return components used for equality comparison"""
        return (self.value,)
    
    def __str__(self) -> str:
        """String representation with quality indicator"""
        return f"{self.percentage} ({self.quality_label} {self.quality_emoji})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return f"RelevanceScore(value={self.value})"
