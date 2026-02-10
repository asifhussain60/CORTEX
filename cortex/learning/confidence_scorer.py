"""
Confidence Scorer - Phase 71 S1

AC-PHASE71-006: Confidence scoring based on pattern frequency

Scores learning confidence using:
- Frequency: How many times pattern observed
- Recency: More recent observations weighted higher
- Source reliability: User corrections > inferred patterns
- Threshold promotion: 3+ occurrences → high confidence

Author: GitHub Copilot
Date: 2026-02-10
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from typing import List, Dict, Any
from enum import Enum, auto
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Confidence level categories."""
    
    LOW = auto()        # 0.0-0.4: Single observation, inferred
    MEDIUM = auto()     # 0.4-0.7: 2-3 observations, emerging pattern
    HIGH = auto()       # 0.7-0.9: 4+ observations, established pattern
    ABSOLUTE = auto()   # 0.9-1.0: User-confirmed, explicit feedback


class ConfidenceScorer:
    """
    Scores pattern confidence based on frequency, recency, and source.
    
    AC-PHASE71-006: Frequency-based confidence scoring with threshold promotion
    """
    
    # Scoring weights
    FREQUENCY_WEIGHT = 0.5
    RECENCY_WEIGHT = 0.3
    SOURCE_WEIGHT = 0.2
    
    # Promotion thresholds
    THRESHOLD_MEDIUM = 0.4
    THRESHOLD_HIGH = 0.7
    THRESHOLD_ABSOLUTE = 0.9
    
    def __init__(self):
        """Initialize confidence scorer."""
        # Track pattern frequencies across sessions
        self._pattern_frequencies: Dict[str, int] = {}
        self._pattern_last_seen: Dict[str, datetime] = {}
    
    def score_learnings(
        self,
        learnings: List[Any]  # List[LearningCapture]
    ) -> List[Any]:
        """
        Score confidence for list of learnings.
        
        Args:
            learnings: List of LearningCapture objects
        
        Returns:
            Same list with updated confidence scores
        """
        for learning in learnings:
            # Generate pattern key
            pattern_key = self._generate_pattern_key(learning)
            
            # Update frequency tracking
            self._pattern_frequencies[pattern_key] = (
                self._pattern_frequencies.get(pattern_key, 0) + 1
            )
            self._pattern_last_seen[pattern_key] = learning.timestamp
            
            # Calculate confidence score
            frequency_score = self._calculate_frequency_score(pattern_key)
            recency_score = self._calculate_recency_score(pattern_key)
            source_score = self._calculate_source_score(learning)
            
            # Weighted average
            confidence = (
                frequency_score * self.FREQUENCY_WEIGHT +
                recency_score * self.RECENCY_WEIGHT +
                source_score * self.SOURCE_WEIGHT
            )
            
            # Update learning confidence
            learning.confidence = min(confidence, 1.0)
            learning.frequency = self._pattern_frequencies[pattern_key]
            
            logger.debug(
                f"Scored pattern {pattern_key}: "
                f"confidence={learning.confidence:.2f}, "
                f"frequency={learning.frequency}"
            )
        
        return learnings
    
    def _generate_pattern_key(self, learning: Any) -> str:
        """Generate unique key for pattern deduplication."""
        # Use orchestrator + operation + pattern description
        return f"{learning.orchestrator}:{learning.operation}:{learning.pattern_description}"
    
    def _calculate_frequency_score(self, pattern_key: str) -> float:
        """
        Calculate score based on pattern frequency.
        
        Scoring:
        - 1 occurrence: 0.2
        - 2 occurrences: 0.4
        - 3 occurrences: 0.7 (PROMOTION THRESHOLD)
        - 4+ occurrences: 0.9
        """
        frequency = self._pattern_frequencies.get(pattern_key, 1)
        
        if frequency == 1:
            return 0.2
        elif frequency == 2:
            return 0.4
        elif frequency == 3:
            return 0.7  # Promotion threshold
        else:
            return min(0.9, 0.7 + (frequency - 3) * 0.05)
    
    def _calculate_recency_score(self, pattern_key: str) -> float:
        """
        Calculate score based on pattern recency.
        
        Scoring:
        - Within 1 hour: 1.0
        - Within 1 day: 0.8
        - Within 1 week: 0.5
        - Older: 0.3
        """
        last_seen = self._pattern_last_seen.get(pattern_key, datetime.now())
        age = datetime.now() - last_seen
        
        if age < timedelta(hours=1):
            return 1.0
        elif age < timedelta(days=1):
            return 0.8
        elif age < timedelta(weeks=1):
            return 0.5
        else:
            return 0.3
    
    def _calculate_source_score(self, learning: Any) -> float:
        """
        Calculate score based on learning source reliability.
        
        Scoring:
        - User correction: 1.0 (ABSOLUTE confidence)
        - User choice: 0.9 (HIGH confidence)
        - Inferred pattern: 0.5 (MEDIUM confidence)
        - Generic extraction: 0.3 (LOW confidence)
        """
        # Check if user-confirmed (from context) - HIGHEST PRIORITY
        if learning.context.get("user_confirmed"):
            return 1.0  # User confirmations override everything
        
        # Check if user choice (interaction patterns)
        if learning.pattern_type.name == "INTERACTION":
            if "choice" in learning.pattern_data or "correction" in learning.pattern_data:
                return 0.95  # User choices are very high confidence
        
        # Check if explicit business knowledge
        if learning.pattern_type.name == "BUSINESS":
            return 0.7
        
        # Default: inferred pattern
        return 0.5
    
    def get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """
        Convert confidence score to confidence level category.
        
        Args:
            confidence: Confidence score (0.0-1.0)
        
        Returns:
            ConfidenceLevel enum
        """
        if confidence >= self.THRESHOLD_ABSOLUTE:
            return ConfidenceLevel.ABSOLUTE
        elif confidence >= self.THRESHOLD_HIGH:
            return ConfidenceLevel.HIGH
        elif confidence >= self.THRESHOLD_MEDIUM:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """
        Get pattern frequency statistics.
        
        Returns:
            Dictionary with pattern tracking statistics
        """
        return {
            "total_patterns": len(self._pattern_frequencies),
            "high_confidence_patterns": sum(
                1 for freq in self._pattern_frequencies.values()
                if freq >= 3
            ),
            "pattern_frequencies": self._pattern_frequencies.copy(),
            "most_frequent": sorted(
                self._pattern_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
