"""
Pydantic data models for DIGEST Detection Calibration System.

Phase 41 Stage 3 (ENH-057):
- GroundTruthLabel: Ground truth labels for files
- DetectionMetrics: Precision/recall/F1 metrics
- CalibrationResult: Threshold optimization results
- MarkerWeights: Learned weights for chat markers

Author: Asif Hussain
Date: 2026-02-07
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class GroundTruthLabel(BaseModel):
    """
    Ground truth label for a file.

    Marks file as chat/non-chat with confidence score.
    """

    is_chat: bool = Field(
        ...,
        description="True if file is a chat session"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in label (0-1)"
    )

    labeler: Optional[str] = Field(
        default=None,
        description="Who labeled this file (human/auto)"
    )

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When label was created"
    )


class DetectionMetrics(BaseModel):
    """
    Precision/recall/F1 metrics for chat detection.

    Tracks detection performance against ground truth.
    """

    precision: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Precision: TP/(TP+FP)"
    )

    recall: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Recall: TP/(TP+FN)"
    )

    f1_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="F1 score: 2*P*R/(P+R)"
    )

    true_positives: int = Field(
        ...,
        ge=0,
        description="Correctly detected chats"
    )

    false_positives: int = Field(
        ...,
        ge=0,
        description="Non-chats incorrectly detected as chats"
    )

    false_negatives: int = Field(
        ...,
        ge=0,
        description="Chats incorrectly detected as non-chats"
    )

    true_negatives: int = Field(
        default=0,
        ge=0,
        description="Correctly detected non-chats"
    )

    threshold: Optional[float] = Field(
        default=None,
        description="Detection threshold used"
    )

    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When metrics were calculated"
    )


class CalibrationResult(BaseModel):
    """
    Result of threshold optimization.

    Contains optimal threshold and performance metrics.
    """

    optimal_threshold: float = Field(
        ...,
        ge=0,
        description="Optimal detection threshold"
    )

    optimal_f1_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="F1 score at optimal threshold"
    )

    optimal_precision: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Precision at optimal threshold"
    )

    optimal_recall: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Recall at optimal threshold"
    )

    improvement_pct: float = Field(
        ...,
        description="Percentage improvement over baseline"
    )

    baseline_f1: Optional[float] = Field(
        default=None,
        description="Baseline F1 score before optimization"
    )

    search_range: tuple = Field(
        default=(0, 10),
        description="Threshold search range"
    )

    iterations: int = Field(
        default=0,
        ge=0,
        description="Number of optimization iterations"
    )


class MarkerWeights(BaseModel):
    """
    Learned weights for chat markers.

    Weights determine importance of each marker for detection.
    """

    User: float = Field(default=1.0, description="Weight for 'User:' marker")
    Copilot: float = Field(default=1.0, description="Weight for 'GitHub Copilot:' marker")
    Tool: float = Field(default=1.0, description="Weight for '[Tool call:' marker")
    Drift: float = Field(default=1.0, description="Weight for '# Drift' marker")
    Pattern: float = Field(default=1.0, description="Weight for '# Pattern' marker")
    Efficiency: float = Field(default=1.0, description="Weight for '# Efficiency' marker")

    epochs_trained: int = Field(
        default=0,
        ge=0,
        description="Number of training epochs"
    )

    final_loss: Optional[float] = Field(
        default=None,
        description="Final training loss"
    )

    converged: bool = Field(
        default=False,
        description="Whether training converged"
    )

    learning_rate: float = Field(
        default=0.01,
        gt=0,
        description="Learning rate used for training"
    )


class CalibrationState(BaseModel):
    """
    Full calibration state for persistence.

    Includes ground truth, metrics history, and learned parameters.
    """

    ground_truth: Dict[str, GroundTruthLabel] = Field(
        default_factory=dict,
        description="Ground truth labels"
    )

    metrics_history: Dict[str, DetectionMetrics] = Field(
        default_factory=dict,
        description="Historical metrics by version"
    )

    current_threshold: float = Field(
        default=5.0,
        ge=0,
        description="Current detection threshold"
    )

    marker_weights: MarkerWeights = Field(
        default_factory=MarkerWeights,
        description="Learned marker weights"
    )

    version: str = Field(
        default="1.0",
        description="Calibration state version"
    )

    last_updated: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
