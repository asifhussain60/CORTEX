"""
CORTEX Confidence Scoring Module

Calculates and formats confidence scores for pattern usage display.
Converts internal confidence (0.0-1.0) to user-friendly percentages.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from datetime import datetime
import math


class ConfidenceLevel(Enum):
    """Confidence level categories for user display"""
    VERY_HIGH = "Very High"  # 90-100%
    HIGH = "High"            # 75-89%
    MEDIUM = "Medium"        # 50-74%
    LOW = "Low"              # 30-49%
    VERY_LOW = "Very Low"    # <30%


@dataclass
class ConfidenceScore:
    """Confidence score with metadata for display"""
    percentage: int  # 0-100
    level: ConfidenceLevel
    pattern_count: int  # Number of patterns used
    usage_history: int  # Total usage count
    last_used: Optional[datetime]
    factors: Dict[str, float]  # Contributing factors
    
    def format_display(self) -> str:
        """Format confidence for user display"""
        emoji = self._get_emoji()
        return f"{emoji} Confidence: {self.percentage}% ({self.level.value})"
    
    def format_detailed(self) -> str:
        """Format detailed confidence explanation"""
        display = self.format_display()
        details = f"Based on {self.pattern_count} similar pattern{'s' if self.pattern_count != 1 else ''}"
        if self.usage_history > 0:
            details += f" ({self.usage_history} successful use{'s' if self.usage_history != 1 else ''})"
        return f"{display} - {details}"
    
    def _get_emoji(self) -> str:
        """Get emoji for confidence level"""
        emoji_map = {
            ConfidenceLevel.VERY_HIGH: "🟢",
            ConfidenceLevel.HIGH: "🟢", 
            ConfidenceLevel.MEDIUM: "🟡",
            ConfidenceLevel.LOW: "🟠",
            ConfidenceLevel.VERY_LOW: "🔴"
        }
        return emoji_map.get(self.level, "⚪")


class ConfidenceScorer:
    """
    Calculate confidence scores from pattern data
    
    Factors considered:
    - Pattern match quality (40%)
    - Usage history (30%)
    - Success rate (20%)
    - Recency (10%)
    """
    
    # Weights for confidence calculation
    WEIGHT_MATCH_QUALITY = 0.40
    WEIGHT_USAGE_HISTORY = 0.30
    WEIGHT_SUCCESS_RATE = 0.20
    WEIGHT_RECENCY = 0.10
    
    def calculate_confidence(
        self,
        base_confidence: float,
        usage_count: int = 0,
        success_rate: float = 0.0,
        last_used: Optional[datetime] = None,
        pattern_count: int = 1
    ) -> ConfidenceScore:
        """
        Calculate comprehensive confidence score
        
        Args:
            base_confidence: Pattern match quality (0.0-1.0)
            usage_count: Number of times pattern used successfully
            success_rate: Success rate of pattern (0.0-1.0)
            last_used: When pattern was last used
            pattern_count: Number of patterns contributing
            
        Returns:
            ConfidenceScore with percentage and metadata
        """
        factors = {}
        
        # Factor 1: Match Quality (40%)
        match_score = base_confidence
        factors['match_quality'] = match_score
        
        # Factor 2: Usage History (30%)
        # More usage = higher confidence (logarithmic scale)
        usage_score = min(1.0, math.log10(usage_count + 1) / 2.0) if usage_count > 0 else 0.0
        factors['usage_history'] = usage_score
        
        # Factor 3: Success Rate (20%)
        factors['success_rate'] = success_rate
        
        # Factor 4: Recency (10%)
        recency_score = self._calculate_recency_score(last_used)
        factors['recency'] = recency_score
        
        # Weighted sum
        weighted_confidence = (
            match_score * self.WEIGHT_MATCH_QUALITY +
            usage_score * self.WEIGHT_USAGE_HISTORY +
            success_rate * self.WEIGHT_SUCCESS_RATE +
            recency_score * self.WEIGHT_RECENCY
        )
        
        # Convert to percentage (0-100)
        percentage = int(weighted_confidence * 100)
        
        # Determine confidence level
        level = self._determine_level(percentage)
        
        return ConfidenceScore(
            percentage=percentage,
            level=level,
            pattern_count=pattern_count,
            usage_history=usage_count,
            last_used=last_used,
            factors=factors
        )
    
    def _calculate_recency_score(self, last_used: Optional[datetime]) -> float:
        """Calculate recency score (1.0 = recent, 0.0 = old)"""
        if not last_used:
            return 0.5  # Neutral score if no data
        
        age_days = (datetime.now() - last_used).days
        
        if age_days <= 7:
            return 1.0  # Very recent
        elif age_days <= 30:
            return 0.8  # Recent
        elif age_days <= 90:
            return 0.6  # Moderately old
        elif age_days <= 180:
            return 0.4  # Old
        else:
            return 0.2  # Very old
    
    def _determine_level(self, percentage: int) -> ConfidenceLevel:
        """Determine confidence level from percentage"""
        if percentage >= 90:
            return ConfidenceLevel.VERY_HIGH
        elif percentage >= 75:
            return ConfidenceLevel.HIGH
        elif percentage >= 50:
            return ConfidenceLevel.MEDIUM
        elif percentage >= 30:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
