"""
ROI Composite Scorer

Extracted from PhaseManager (cortex/registry/phase_manager.py).
Calculates ROI scores for phases using weighted formula.

Formula:
    ROI = (arch_impact * 0.35) + (efficiency * 0.25) +
          (accuracy * 0.20) + ((1 - effort) * 0.15) +
          (blocking * 0.05)

Authority: Wave 8 Stage 3, phase-25 spec
"""

from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum


class PriorityTier(Enum):
    """Priority tiers based on ROI score"""
    HIGH = "HIGH"      # ROI >= 0.75
    MEDIUM = "MEDIUM"  # ROI >= 0.60
    LOW = "LOW"        # ROI >= 0.40
    DEFER = "DEFER"    # ROI < 0.40


@dataclass
class ROIWeights:
    """Weights for ROI calculation dimensions"""
    architectural_impact: float = 0.35
    efficiency_gain: float = 0.25
    accuracy_improvement: float = 0.20
    effort_cost: float = 0.15
    blocking_severity: float = 0.05

    def __post_init__(self):
        """Validate weights sum to 1.0"""
        total = (
            self.architectural_impact +
            self.efficiency_gain +
            self.accuracy_improvement +
            self.effort_cost +
            self.blocking_severity
        )
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"ROI weights must sum to 1.0, got {total}")


@dataclass
class PhaseMetrics:
    """Phase metrics for ROI calculation (all 0.0-1.0)"""
    architectural_impact: float
    efficiency_gain: float
    accuracy_improvement: float
    effort_cost: float
    blocking_severity: float

    def __post_init__(self):
        """Validate all metrics are in [0.0, 1.0] range"""
        for field_name in ["architectural_impact", "efficiency_gain",
                           "accuracy_improvement", "effort_cost", "blocking_severity"]:
            value = getattr(self, field_name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(
                    f"{field_name} must be in [0.0, 1.0], got {value}"
                )

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            "architectural_impact": self.architectural_impact,
            "efficiency_gain": self.efficiency_gain,
            "accuracy_improvement": self.accuracy_improvement,
            "effort_cost": self.effort_cost,
            "blocking_severity": self.blocking_severity,
        }


class ROICompositeScorer:
    """
    Calculate ROI scores for phases using weighted formula.

    Thread-safe, stateless scorer that can be reused across operations.

    Example:
        >>> scorer = ROICompositeScorer()
        >>> metrics = PhaseMetrics(
        ...     architectural_impact=0.9,
        ...     efficiency_gain=0.95,
        ...     accuracy_improvement=0.4,
        ...     effort_cost=0.3,
        ...     blocking_severity=1.0
        ... )
        >>> score = scorer.calculate(metrics)
        >>> print(f"ROI: {score:.4f}")  # 0.7875
        >>> tier = scorer.get_priority_tier(metrics)
        >>> print(tier)  # PriorityTier.HIGH
    """

    # Default thresholds (from phase-25 spec)
    HIGH_ROI_THRESHOLD = 0.75
    MEDIUM_ROI_THRESHOLD = 0.60
    LOW_ROI_THRESHOLD = 0.40

    def __init__(self, weights: Optional[ROIWeights] = None) -> None:
        """
        Initialize scorer with optional custom weights.

        Args:
            weights: Custom ROI weights (defaults to phase-25 spec)
        """
        self.weights = weights or ROIWeights()

    def calculate(self, metrics: PhaseMetrics) -> float:
        """
        Calculate ROI score from phase metrics.

        Args:
            metrics: Phase metrics (all 0.0-1.0)

        Returns:
            ROI score (0.0-1.0), rounded to 4 decimal places
        """
        roi_score = (
            (metrics.architectural_impact * self.weights.architectural_impact) +
            (metrics.efficiency_gain * self.weights.efficiency_gain) +
            (metrics.accuracy_improvement * self.weights.accuracy_improvement) +
            ((1.0 - metrics.effort_cost) * self.weights.effort_cost) +  # Inverted
            (metrics.blocking_severity * self.weights.blocking_severity)
        )

        return round(roi_score, 4)

    def get_priority_tier(self, metrics: PhaseMetrics) -> PriorityTier:
        """
        Determine priority tier from phase metrics.

        Args:
            metrics: Phase metrics

        Returns:
            Priority tier enum
        """
        roi_score = self.calculate(metrics)

        if roi_score >= self.HIGH_ROI_THRESHOLD:
            return PriorityTier.HIGH
        elif roi_score >= self.MEDIUM_ROI_THRESHOLD:
            return PriorityTier.MEDIUM
        elif roi_score >= self.LOW_ROI_THRESHOLD:
            return PriorityTier.LOW
        else:
            return PriorityTier.DEFER

    def calculate_from_dict(self, metrics_dict: Dict[str, float]) -> float:
        """
        Calculate ROI from dictionary (convenience method).

        Args:
            metrics_dict: Dictionary with metric keys

        Returns:
            ROI score (0.0-1.0)
        """
        metrics = PhaseMetrics(**metrics_dict)
        return self.calculate(metrics)
