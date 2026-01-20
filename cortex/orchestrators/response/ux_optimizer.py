"""UX Optimizer - Optimizes response UX.

Optimizes response formatting for better UX.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from enum import Enum


class UXOptimizationStrategy(Enum):
    """UX optimization strategies."""

    CLARITY = "clarity"
    BREVITY = "brevity"
    COMPREHENSIVENESS = "comprehensiveness"
    INTERACTIVE = "interactive"


@dataclass
class UXMetrics:
    """UX metrics for responses.

    Attributes:
        readability_score: Readability score (0-100).
        clarity_score: Clarity score (0-100).
        engagement_score: Engagement score (0-100).
        overall_score: Overall UX score (0-100).
    """

    readability_score: float = 0.0
    clarity_score: float = 0.0
    engagement_score: float = 0.0
    overall_score: float = 0.0


class UXOptimizer:
    """Optimizes response UX."""

    def __init__(self, strategy: UXOptimizationStrategy = UXOptimizationStrategy.CLARITY) -> None:
        """Initialize UX optimizer.

        Args:
            strategy: Optimization strategy.
        """
        self.strategy = strategy
        self.metrics_history: List[UXMetrics] = []

    def optimize(self, response: str) -> Dict[str, Any]:
        """Optimize a response.

        Args:
            response: Response to optimize.

        Returns:
            Optimized response with metrics.
        """
        # Calculate metrics
        metrics = UXMetrics(
            readability_score=self._calculate_readability(response),
            clarity_score=self._calculate_clarity(response),
            engagement_score=self._calculate_engagement(response),
        )
        metrics.overall_score = (
            metrics.readability_score * 0.3
            + metrics.clarity_score * 0.4
            + metrics.engagement_score * 0.3
        )

        self.metrics_history.append(metrics)

        # Apply optimization based on strategy
        optimized = self._apply_strategy(response)

        return {
            "original": response,
            "optimized": optimized,
            "metrics": metrics,
            "strategy": self.strategy.value,
        }

    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score.

        Args:
            text: Text to evaluate.

        Returns:
            Readability score (0-100).
        """
        # Simple heuristic: shorter paragraphs = more readable
        paragraphs = text.split("\n\n")
        avg_length = len(text) / len(paragraphs) if paragraphs else len(text)
        # Ideal paragraph length ~100-150 chars
        return min(100, 100 * (150 / max(1, avg_length)))

    def _calculate_clarity(self, text: str) -> float:
        """Calculate clarity score.

        Args:
            text: Text to evaluate.

        Returns:
            Clarity score (0-100).
        """
        # Simple heuristic: active voice, short sentences
        sentences = text.split(". ")
        avg_sentence_length = len(text) / len(sentences) if sentences else len(text)
        # Ideal sentence length ~15-20 words
        words_per_sentence = avg_sentence_length / 5  # Rough estimate
        return min(100, 100 * (20 / max(1, words_per_sentence)))

    def _calculate_engagement(self, text: str) -> float:
        """Calculate engagement score.

        Args:
            text: Text to evaluate.

        Returns:
            Engagement score (0-100).
        """
        # Simple heuristic: questions, examples, formatting
        engagement = 50  # Base score
        if "?" in text:
            engagement += 15
        if any(marker in text for marker in ["•", "-", "*", "1.", "2."]):
            engagement += 20
        if any(word in text.lower() for word in ["example", "for instance", "such as"]):
            engagement += 15
        return min(100, engagement)

    def _apply_strategy(self, response: str) -> str:
        """Apply optimization strategy.

        Args:
            response: Response to optimize.

        Returns:
            Optimized response.
        """
        if self.strategy == UXOptimizationStrategy.CLARITY:
            return response  # Already clear
        elif self.strategy == UXOptimizationStrategy.BREVITY:
            # Remove verbose phrases
            phrases = {
                "please note that ": "",
                "it is important to mention that ": "",
                "in order to ": "to ",
            }
            result = response
            for phrase, replacement in phrases.items():
                result = result.replace(phrase, replacement)
            return result
        else:
            return response

    def get_average_metrics(self) -> Optional[UXMetrics]:
        """Get average metrics across all optimizations.

        Returns:
            Average UXMetrics or None.
        """
        if not self.metrics_history:
            return None

        avg = UXMetrics(
            readability_score=sum(m.readability_score for m in self.metrics_history)
            / len(self.metrics_history),
            clarity_score=sum(m.clarity_score for m in self.metrics_history)
            / len(self.metrics_history),
            engagement_score=sum(m.engagement_score for m in self.metrics_history)
            / len(self.metrics_history),
        )
        avg.overall_score = (
            avg.readability_score * 0.3 + avg.clarity_score * 0.4 + avg.engagement_score * 0.3
        )
        return avg


__all__ = [
    "UXOptimizer",
    "UXMetrics",
    "UXOptimizationStrategy",
]
