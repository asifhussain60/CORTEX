"""Confidence Scoring - Confidence metrics for hallucination detection.

Provides confidence scoring for operations to detect unreliable outputs.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ConfidenceScore:
    """Confidence score for an operation.

    Attributes:
        operation_id: Operation identifier.
        overall_score: Overall confidence (0-1).
        input_confidence: Input quality confidence.
        processing_confidence: Processing confidence.
        output_confidence: Output quality confidence.
        factors: Confidence factors.
    """

    operation_id: str
    overall_score: float
    input_confidence: float = 0.5
    processing_confidence: float = 0.5
    output_confidence: float = 0.5
    factors: Dict[str, float] = None

    def __post_init__(self) -> None:
        """Initialize defaults."""
        if self.factors is None:
            self.factors = {}

    def is_confident(self, threshold: float = 0.8) -> bool:
        """Check if score meets confidence threshold.

        Args:
            threshold: Confidence threshold (0-1).

        Returns:
            True if confident, False otherwise.
        """
        return self.overall_score >= threshold


class ConfidenceScorer:
    """Scores confidence of operations."""

    def __init__(self) -> None:
        """Initialize scorer."""
        self.scores: Dict[str, ConfidenceScore] = {}
        self.weights = {
            "input": 0.3,
            "processing": 0.4,
            "output": 0.3,
        }

    def score(
        self,
        operation_id: str,
        input_confidence: float = 0.5,
        processing_confidence: float = 0.5,
        output_confidence: float = 0.5,
        factors: Optional[Dict[str, float]] = None,
    ) -> ConfidenceScore:
        """Score an operation's confidence.

        Args:
            operation_id: Operation ID.
            input_confidence: Input confidence (0-1).
            processing_confidence: Processing confidence (0-1).
            output_confidence: Output confidence (0-1).
            factors: Additional confidence factors.

        Returns:
            ConfidenceScore.
        """
        # Clamp values to 0-1
        input_conf = max(0, min(1, input_confidence))
        proc_conf = max(0, min(1, processing_confidence))
        out_conf = max(0, min(1, output_confidence))

        # Calculate weighted score
        overall = (
            input_conf * self.weights["input"]
            + proc_conf * self.weights["processing"]
            + out_conf * self.weights["output"]
        )

        score = ConfidenceScore(
            operation_id=operation_id,
            overall_score=overall,
            input_confidence=input_conf,
            processing_confidence=proc_conf,
            output_confidence=out_conf,
            factors=factors or {},
        )

        self.scores[operation_id] = score
        return score

    def get_score(self, operation_id: str) -> Optional[ConfidenceScore]:
        """Get confidence score for operation.

        Args:
            operation_id: Operation ID.

        Returns:
            ConfidenceScore or None if not found.
        """
        return self.scores.get(operation_id)

    def get_low_confidence_operations(self, threshold: float = 0.7) -> list:
        """Get operations below confidence threshold.

        Args:
            threshold: Confidence threshold.

        Returns:
            List of low-confidence operation IDs.
        """
        return [
            op_id for op_id, score in self.scores.items()
            if score.overall_score < threshold
        ]

    def average_confidence(self) -> float:
        """Get average confidence across all operations.

        Returns:
            Average confidence score (0-1).
        """
        if not self.scores:
            return 0.0
        total = sum(s.overall_score for s in self.scores.values())
        return total / len(self.scores)

    def clear_scores(self) -> None:
        """Clear all scores."""
        self.scores.clear()


__all__ = ["ConfidenceScorer", "ConfidenceScore"]
