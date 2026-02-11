"""Confidence Scorer - Computes confidence scores for intent classification.

Provides confidence scoring based on multiple signals including keyword matches,
signal strength, and historical data.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Score:
    """Confidence score result."""
    value: float
    keywords: int
    signals: int
    breakdown: Dict[str, float] = field(default_factory=dict)


class ConfidenceScorer:
    """Compute confidence scores for intent classification.

    Combines multiple signals (keywords, patterns, signals) to produce
    a normalized confidence score in the range [0.0, 1.0].

    Attributes:
        metrics: Scoring metrics tracking
        weights: Weights for different scoring components
    """

    def __init__(self):
        """Initialize confidence scorer."""
        self.metrics: Dict[str, Any] = {
            "total_scores": 0,
            "avg_score": 0.0,
            "score_sum": 0.0
        }
        self.weights = {
            "keywords": 0.6,
            "signals": 0.4
        }

    def score(self, keywords: int, signals: int) -> float:
        """Compute confidence score.

        Args:
            keywords: Number of keyword matches
            signals: Number of detected signals

        Returns:
            Confidence score in range [0.0, 1.0]
        """
        # Normalize inputs
        keyword_score = min(keywords / 5.0, 1.0)  # Max 5 keywords = 1.0
        signal_score = min(signals / 3.0, 1.0)    # Max 3 signals = 1.0

        # Weighted combination
        confidence = (
            self.weights["keywords"] * keyword_score +
            self.weights["signals"] * signal_score
        )

        # Update metrics
        self.metrics["total_scores"] += 1
        self.metrics["score_sum"] += confidence
        self.metrics["avg_score"] = self.metrics["score_sum"] / self.metrics["total_scores"]

        return confidence

    def get_metrics(self) -> Dict[str, Any]:
        """Get scoring metrics.

        Returns:
            Dictionary with scoring statistics
        """
        return self.metrics.copy()


__all__ = ['ConfidenceScorer', 'Score']
