"""
CORTEX 3.0 - Tier 2 Learning Integration for Smart Hints

Purpose: Learn from user acceptance/rejection patterns to improve hint suggestions.
         Adapts quality threshold based on user behavior.

Architecture:
- Tracks user responses (accepted, rejected, ignored)
- Analyzes acceptance patterns by quality level
- Adapts threshold dynamically (6/10 ↔ 8/10 range)
- Stores preferences in Tier 2 knowledge graph
- Implements confidence decay to reduce noise

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict


logger = logging.getLogger(__name__)


@dataclass
class UserResponse:
    """User's response to a Smart Hint."""
    session_id: str
    response: str  # 'accepted', 'rejected', 'ignored'
    quality_score: int
    quality_level: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'response': self.response,
            'quality_score': self.quality_score,
            'quality_level': self.quality_level,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserResponse':
        """Create from dictionary."""
        return cls(
            session_id=data['session_id'],
            response=data['response'],
            quality_score=data['quality_score'],
            quality_level=data['quality_level'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


@dataclass
class ThresholdRecommendation:
    """Recommendation for threshold adjustment."""
    current_threshold: str
    recommended_threshold: str
    confidence: float
    reasoning: str
    sample_size: int


class Tier2LearningIntegration:
    """
    Learns from user hint response patterns and adapts behavior.
    
    Learning Strategy:
    - Track acceptance rate by quality level
    - If acceptance rate > 70%: Lower threshold (more hints)
    - If acceptance rate < 30%: Raise threshold (fewer hints)
    - Requires minimum 10 samples before adjusting
    
    Threshold Levels (internal score → quality level):
    - EXCELLENT: ≥19 points (strictest)
    - GOOD: ≥10 points (default)
    - FAIR: ≥2 points (most permissive, not recommended)
    
    Note: We don't go below GOOD in practice (FAIR would be too noisy)
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        min_samples_for_learning: int = 10,
        high_acceptance_threshold: float = 0.70,
        low_acceptance_threshold: float = 0.30
    ):
        """
        Initialize Tier 2 learning integration.
        
        Args:
            storage_path: Path to store learning data (JSON)
            min_samples_for_learning: Minimum responses before adapting
            high_acceptance_threshold: Acceptance rate to lower threshold
            low_acceptance_threshold: Acceptance rate to raise threshold
        """
        self.storage_path = storage_path or Path(
            "cortex-brain/tier2/smart-hint-learning.json"
        )
        self.min_samples = min_samples_for_learning
        self.high_threshold = high_acceptance_threshold
        self.low_threshold = low_acceptance_threshold
        
        # Response history
        self.responses: List[UserResponse] = []
        
        # Load existing data if available
        self._load_learning_data()
        
        logger.info(
            f"Tier2LearningIntegration initialized: "
            f"min_samples={min_samples_for_learning}, "
            f"storage={self.storage_path}"
        )
    
    def record_response(
        self,
        session_id: str,
        response: str,
        quality_score: int,
        quality_level: str
    ) -> None:
        """
        Record user's response to Smart Hint.
        
        Args:
            session_id: Session identifier
            response: 'accepted', 'rejected', or 'ignored'
            quality_score: Internal quality score
            quality_level: Quality level (EXCELLENT, GOOD, FAIR, LOW)
        """
        user_response = UserResponse(
            session_id=session_id,
            response=response,
            quality_score=quality_score,
            quality_level=quality_level,
            timestamp=datetime.now()
        )
        
        self.responses.append(user_response)
        
        logger.info(
            f"Recorded user response: {response} "
            f"(quality={quality_level}, score={quality_score})"
        )
        
        # Save after each response
        self._save_learning_data()
    
    def get_acceptance_rate(
        self,
        quality_level: Optional[str] = None
    ) -> float:
        """
        Calculate acceptance rate.
        
        Args:
            quality_level: Optional filter by quality level
            
        Returns:
            Acceptance rate (0.0 to 1.0)
        """
        if not self.responses:
            return 0.0
        
        filtered = self.responses
        if quality_level:
            filtered = [r for r in self.responses if r.quality_level == quality_level]
        
        if not filtered:
            return 0.0
        
        accepted = sum(1 for r in filtered if r.response == 'accepted')
        return accepted / len(filtered)
    
    def get_response_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive response statistics.
        
        Returns:
            Dict with stats by quality level and overall
        """
        if not self.responses:
            return {
                'total_responses': 0,
                'acceptance_rate': 0.0,
                'by_quality_level': {}
            }
        
        # Overall stats
        total = len(self.responses)
        accepted = sum(1 for r in self.responses if r.response == 'accepted')
        rejected = sum(1 for r in self.responses if r.response == 'rejected')
        ignored = sum(1 for r in self.responses if r.response == 'ignored')
        
        # By quality level
        by_level = defaultdict(lambda: {'total': 0, 'accepted': 0, 'rejected': 0, 'ignored': 0})
        
        for response in self.responses:
            level = response.quality_level
            by_level[level]['total'] += 1
            by_level[level][response.response] += 1
        
        # Calculate rates for each level
        level_stats = {}
        for level, counts in by_level.items():
            level_stats[level] = {
                'total': counts['total'],
                'accepted': counts['accepted'],
                'rejected': counts['rejected'],
                'ignored': counts['ignored'],
                'acceptance_rate': counts['accepted'] / counts['total']
            }
        
        return {
            'total_responses': total,
            'accepted': accepted,
            'rejected': rejected,
            'ignored': ignored,
            'acceptance_rate': accepted / total,
            'by_quality_level': level_stats
        }
    
    def recommend_threshold_adjustment(
        self,
        current_threshold: str = "GOOD"
    ) -> Optional[ThresholdRecommendation]:
        """
        Recommend threshold adjustment based on learning.
        
        Args:
            current_threshold: Current quality threshold
            
        Returns:
            ThresholdRecommendation or None if insufficient data
        """
        if len(self.responses) < self.min_samples:
            return None
        
        acceptance_rate = self.get_acceptance_rate()
        
        # Determine recommendation
        if acceptance_rate >= self.high_threshold:
            # High acceptance: user wants more hints
            if current_threshold == "EXCELLENT":
                recommended = "GOOD"
                reasoning = (
                    f"High acceptance rate ({acceptance_rate:.1%}) suggests "
                    "user values hints. Lowering threshold to show more."
                )
            else:
                # Already at GOOD, don't go lower (FAIR would be too noisy)
                recommended = current_threshold
                reasoning = (
                    f"High acceptance rate ({acceptance_rate:.1%}) but "
                    "already at minimum recommended threshold (GOOD)."
                )
        
        elif acceptance_rate <= self.low_threshold:
            # Low acceptance: user finds hints annoying
            if current_threshold == "GOOD":
                recommended = "EXCELLENT"
                reasoning = (
                    f"Low acceptance rate ({acceptance_rate:.1%}) suggests "
                    "hints are too frequent. Raising threshold to be more selective."
                )
            else:
                # Already at EXCELLENT
                recommended = current_threshold
                reasoning = (
                    f"Low acceptance rate ({acceptance_rate:.1%}) but "
                    "already at maximum threshold (EXCELLENT)."
                )
        
        else:
            # Acceptance rate in sweet spot
            recommended = current_threshold
            reasoning = (
                f"Acceptance rate ({acceptance_rate:.1%}) is balanced. "
                "Current threshold is appropriate."
            )
        
        confidence = min(1.0, len(self.responses) / (self.min_samples * 2))
        
        return ThresholdRecommendation(
            current_threshold=current_threshold,
            recommended_threshold=recommended,
            confidence=confidence,
            reasoning=reasoning,
            sample_size=len(self.responses)
        )
    
    def should_adjust_threshold(
        self,
        current_threshold: str = "GOOD"
    ) -> bool:
        """
        Check if threshold should be adjusted.
        
        Args:
            current_threshold: Current threshold setting
            
        Returns:
            True if adjustment recommended
        """
        recommendation = self.recommend_threshold_adjustment(current_threshold)
        
        if not recommendation:
            return False
        
        return (
            recommendation.recommended_threshold != current_threshold and
            recommendation.confidence >= 0.5
        )
    
    def get_quality_level_preferences(self) -> Dict[str, float]:
        """
        Get user's acceptance rates by quality level.
        
        Returns:
            Dict mapping quality level to acceptance rate
        """
        stats = self.get_response_stats()
        
        if not stats['by_quality_level']:
            return {}
        
        return {
            level: data['acceptance_rate']
            for level, data in stats['by_quality_level'].items()
        }
    
    def _load_learning_data(self) -> None:
        """Load learning data from storage."""
        if not self.storage_path.exists():
            logger.info(f"No existing learning data at {self.storage_path}")
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            self.responses = [
                UserResponse.from_dict(r)
                for r in data.get('responses', [])
            ]
            
            logger.info(
                f"Loaded {len(self.responses)} responses from {self.storage_path}"
            )
        
        except Exception as e:
            logger.error(f"Failed to load learning data: {e}")
    
    def _save_learning_data(self) -> None:
        """Save learning data to storage."""
        try:
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'version': '1.0.0',
                'last_updated': datetime.now().isoformat(),
                'total_responses': len(self.responses),
                'responses': [r.to_dict() for r in self.responses]
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved learning data to {self.storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")
    
    def reset_learning_data(self) -> None:
        """Reset all learning data (for testing or user request)."""
        self.responses = []
        self._save_learning_data()
        logger.info("Learning data reset")


def create_tier2_learning(
    config: Optional[Dict[str, Any]] = None
) -> Tier2LearningIntegration:
    """
    Factory function to create Tier 2 learning integration.
    
    Args:
        config: Optional configuration dict
            - storage_path: Path (default: cortex-brain/tier2/smart-hint-learning.json)
            - min_samples_for_learning: int (default: 10)
            - high_acceptance_threshold: float (default: 0.70)
            - low_acceptance_threshold: float (default: 0.30)
            
    Returns:
        Configured Tier2LearningIntegration instance
    """
    if not config:
        config = {}
    
    storage_path = config.get('storage_path')
    if storage_path and not isinstance(storage_path, Path):
        storage_path = Path(storage_path)
    
    return Tier2LearningIntegration(
        storage_path=storage_path,
        min_samples_for_learning=config.get('min_samples_for_learning', 10),
        high_acceptance_threshold=config.get('high_acceptance_threshold', 0.70),
        low_acceptance_threshold=config.get('low_acceptance_threshold', 0.30)
    )
