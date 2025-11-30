"""ConversationQuality value object - Represents conversation quality with thresholds"""
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Any
from src.domain.common.value_object import ValueObject
from src.application.common.guards import Guard


class QualityThreshold(Enum):
    """Quality thresholds for conversation assessment"""
    EXCELLENT = 0.90
    GOOD = 0.70
    FAIR = 0.50
    POOR = 0.30


@dataclass(frozen=True)
class ConversationQuality(ValueObject):
    """Represents conversation quality with threshold-based categorization
    
    Combines multiple factors:
    - Quality score (0.0-1.0)
    - Turn count (conversation depth)
    - Entity count (richness of content)
    
    Thresholds:
    - Excellent: >= 0.90 (exceptional strategic value)
    - Good: >= 0.70 (worth capturing for learning)
    - Fair: >= 0.50 (basic utility)
    - Poor: < 0.50 (low value)
    
    Example:
        quality = ConversationQuality(
            score=0.85,
            turn_count=12,
            entity_count=25
        )
        print(quality.is_good)  # True
        print(quality.should_capture)  # True
    """
    score: float
    turn_count: int
    entity_count: int
    
    def __post_init__(self):
        """Validate quality components"""
        Guard.against_out_of_range(
            self.score, 0.0, 1.0, 
            "ConversationQuality.score"
        )
        Guard.against_negative_or_zero(self.turn_count, "turn_count")
        Guard.against_negative(self.entity_count, "entity_count")
    
    @property
    def is_excellent(self) -> bool:
        """Check if quality is excellent (>= 0.85)"""
        return self.score >= 0.85
    
    @property
    def is_good(self) -> bool:
        """Check if quality is good (>= 0.70)"""
        return self.score >= QualityThreshold.GOOD.value
    
    @property
    def is_fair(self) -> bool:
        """Check if quality is fair (>= 0.50)"""
        return self.score >= QualityThreshold.FAIR.value
    
    @property
    def is_poor(self) -> bool:
        """Check if quality is poor (< 0.50)"""
        return self.score < QualityThreshold.FAIR.value
    
    @property
    def quality_level(self) -> str:
        """Get quality level as string"""
        if self.is_excellent:
            return "Excellent"
        elif self.is_good:
            return "Good"
        elif self.is_fair:
            return "Fair"
        else:
            return "Poor"
    
    @property
    def quality_emoji(self) -> str:
        """Get emoji representation of quality"""
        if self.is_excellent:
            return "⭐"
        elif self.is_good:
            return "✅"
        elif self.is_fair:
            return "⚠️"
        else:
            return "❌"
    
    @property
    def should_capture(self) -> bool:
        """Determine if conversation should be captured for learning
        
        Captures conversations that are:
        - Good or better quality (>= 0.70)
        - OR have substantial content (>= 10 turns and >= 15 entities)
        """
        return (
            self.score >= QualityThreshold.GOOD.value or
            (self.turn_count >= 10 and self.entity_count >= 15)
        )
    
    @property
    def richness_factor(self) -> float:
        """Calculate content richness (entities per turn)"""
        if self.turn_count == 0:
            return 0.0
        return self.entity_count / self.turn_count
    
    @property
    def is_rich_conversation(self) -> bool:
        """Check if conversation has rich content (>= 1.5 entities per turn)"""
        return self.richness_factor >= 1.5
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        """Return components used for equality comparison"""
        return (self.score, self.turn_count, self.entity_count)
    
    def __str__(self) -> str:
        """String representation with quality level"""
        return (
            f"{self.quality_level} Quality "
            f"(Score: {self.score:.2f}, "
            f"Turns: {self.turn_count}, "
            f"Entities: {self.entity_count})"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"ConversationQuality(score={self.score}, "
            f"turn_count={self.turn_count}, "
            f"entity_count={self.entity_count})"
        )
