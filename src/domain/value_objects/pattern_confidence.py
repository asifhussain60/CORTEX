"""PatternConfidence value object - Represents learning confidence metrics"""
from dataclasses import dataclass
from typing import Tuple, Any
from src.domain.common.value_object import ValueObject
from src.application.common.guards import Guard


@dataclass(frozen=True)
class PatternConfidence(ValueObject):
    """Represents confidence in a learned pattern
    
    Combines multiple factors to assess pattern reliability:
    - Confidence score (0.0-1.0)
    - Observation count (how many times seen)
    - Success rate (how often pattern worked)
    
    Confidence Levels:
    - Proven: >= 0.90 and >= 10 observations (very reliable)
    - Reliable: >= 0.75 and >= 5 observations (trustworthy)
    - Emerging: >= 0.60 and >= 3 observations (promising)
    - Experimental: < 0.60 or < 3 observations (unproven)
    
    Example:
        confidence = PatternConfidence(
            score=0.85,
            observation_count=12,
            success_rate=0.92
        )
        print(confidence.is_reliable)  # True
        print(confidence.confidence_level)  # "Reliable"
    """
    score: float
    observation_count: int
    success_rate: float
    
    def __post_init__(self):
        """Validate confidence components"""
        Guard.against_out_of_range(
            self.score, 0.0, 1.0, 
            "PatternConfidence.score"
        )
        Guard.against_negative(self.observation_count, "observation_count")
        Guard.against_out_of_range(
            self.success_rate, 0.0, 1.0,
            "success_rate"
        )
    
    @property
    def is_proven(self) -> bool:
        """Check if pattern is proven (>= 0.90 confidence, >= 20 observations)"""
        return self.score >= 0.90 and self.observation_count >= 20
    
    @property
    def is_reliable(self) -> bool:
        """Check if pattern is reliable (>= 0.75 confidence, >= 10 observations)"""
        return self.score >= 0.75 and self.observation_count >= 10 and not self.is_proven
    
    @property
    def is_emerging(self) -> bool:
        """Check if pattern is emerging (>= 0.60 confidence, >= 5 observations)"""
        return self.score >= 0.60 and self.observation_count >= 5 and not self.is_reliable and not self.is_proven
    
    @property
    def is_experimental(self) -> bool:
        """Check if pattern is experimental (< 0.60 or < 5 observations)"""
        return self.score < 0.60 or self.observation_count < 5
    
    @property
    def confidence_level(self) -> str:
        """Get confidence level as string"""
        if self.is_proven:
            return "Proven"
        elif self.is_reliable:
            return "Reliable"
        elif self.is_emerging:
            return "Emerging"
        else:
            return "Experimental"
    
    @property
    def confidence_emoji(self) -> str:
        """Get emoji representation of confidence"""
        if self.is_proven:
            return "💎"
        elif self.is_reliable:
            return "✅"
        elif self.is_emerging:
            return "🌱"
        else:
            return "🧪"
    
    @property
    def should_recommend(self) -> bool:
        """Determine if pattern should be recommended to users
        
        Recommends patterns that are:
        - Reliable or better (>= 0.75 confidence, >= 10 observations)
        """
        return self.is_reliable or self.is_proven
    
    @property
    def needs_more_data(self) -> bool:
        """Check if pattern needs more observations for reliable assessment"""
        return self.observation_count < 5
    
    @property
    def quality_score(self) -> float:
        """Calculate overall quality score (simple average)"""
        return (self.score + self.success_rate) / 2.0
    
    def with_new_observation(self, was_successful: bool) -> 'PatternConfidence':
        """Create new confidence with additional observation
        
        Args:
            was_successful: Whether the new observation was successful
            
        Returns:
            New PatternConfidence with updated metrics
        """
        new_count = self.observation_count + 1
        
        # Update success rate with new observation
        total_successes = int(self.success_rate * self.observation_count)
        if was_successful:
            total_successes += 1
        new_success_rate = total_successes / new_count
        
        # Adjust confidence score based on trend
        # Success increases confidence slightly, failure decreases it
        score_adjustment = 0.02 if was_successful else -0.03
        new_score = max(0.0, min(1.0, self.score + score_adjustment))
        
        return PatternConfidence(
            score=new_score,
            observation_count=new_count,
            success_rate=new_success_rate
        )
    
    def get_equality_components(self) -> Tuple[Any, ...]:
        """Return components used for equality comparison"""
        return (self.score, self.observation_count, self.success_rate)
    
    def __str__(self) -> str:
        """String representation with confidence level"""
        return (
            f"{self.confidence_level} "
            f"(Score: {self.score:.2f}, "
            f"Observations: {self.observation_count}, "
            f"Success: {self.success_rate:.1%})"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation"""
        return (
            f"PatternConfidence(score={self.score}, "
            f"observation_count={self.observation_count}, "
            f"success_rate={self.success_rate})"
        )
