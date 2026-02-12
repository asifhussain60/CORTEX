"""
Detection Calibration System for DIGEST Mode.

Phase 41 Stage 3 (ENH-057):
Implements self-calibrating chat session detection with:
1. Ground truth labeling system
2. Precision/recall metrics calculation
3. Auto-threshold adjustment via F1 optimization
4. Marker weight learning via gradient descent

Author: Asif Hussain
Date: 2026-02-07
"""

import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cortex.learning.digest.detection_metrics import (
    CalibrationResult,
    CalibrationState,
    DetectionMetrics,
    GroundTruthLabel,
    MarkerWeights,
)


class DetectionCalibrator:
    """
    Self-calibrating chat session detector.

    Learns optimal threshold and marker weights from ground truth data.
    Tracks precision/recall metrics over time.

    Usage:
        calibrator = DetectionCalibrator()
        calibrator.add_ground_truth("chat.md", is_chat=True)
        result = calibrator.optimize_threshold(chat_scores)
        calibrator.learn_marker_weights(training_data, epochs=100)
    """

    def __init__(self):
        """Initialize DetectionCalibrator with default state."""
        self.state = CalibrationState()

    # AC-PHASE41-011: Ground truth labeling

    def add_ground_truth(
        self,
        file_path: str,
        is_chat: bool,
        confidence: float = 1.0,
        labeler: str = "human"
    ) -> None:
        """
        Add ground truth label for a file.

        Args:
            file_path: Path to file
            is_chat: True if file is chat session
            confidence: Confidence in label (0-1)
            labeler: Who labeled this (human/auto)
        """
        self.state.ground_truth[file_path] = GroundTruthLabel(
            is_chat=is_chat,
            confidence=confidence,
            labeler=labeler,
            timestamp=datetime.now()
        )

    def get_ground_truth(self) -> Dict[str, GroundTruthLabel]:
        """Get all ground truth labels."""
        return self.state.ground_truth

    def load_ground_truth(self, yaml_path: Path) -> None:
        """
        Load ground truth from YAML file.

        Args:
            yaml_path: Path to YAML file with ground truth

        YAML format:
            chat_sessions:
              - path: "session1.md"
                is_chat: true
                confidence: 1.0
            non_chat_files:
              - path: "doc.md"
                is_chat: false
                confidence: 1.0
        """
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        for session in data.get("chat_sessions", []):
            self.add_ground_truth(
                session["path"],
                is_chat=session["is_chat"],
                confidence=session.get("confidence", 1.0),
                labeler="yaml"
            )

        for file_data in data.get("non_chat_files", []):
            self.add_ground_truth(
                file_data["path"],
                is_chat=file_data["is_chat"],
                confidence=file_data.get("confidence", 1.0),
                labeler="yaml"
            )

    # AC-PHASE41-012: Precision/recall metrics

    def calculate_metrics(
        self,
        ground_truth: Dict[str, bool],
        predictions: Dict[str, bool]
    ) -> DetectionMetrics:
        """
        Calculate precision/recall/F1 metrics.

        Args:
            ground_truth: {file_path: is_chat}
            predictions: {file_path: predicted_is_chat}

        Returns:
            DetectionMetrics with precision/recall/F1
        """
        tp = 0  # True positives
        fp = 0  # False positives
        fn = 0  # False negatives
        tn = 0  # True negatives

        for file_path in ground_truth:
            gt = ground_truth[file_path]
            pred = predictions.get(file_path, False)

            if gt and pred:
                tp += 1
            elif not gt and pred:
                fp += 1
            elif gt and not pred:
                fn += 1
            elif not gt and not pred:
                tn += 1

        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        return DetectionMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            true_negatives=tn,
            threshold=self.state.current_threshold,
            timestamp=datetime.now()
        )

    def record_metrics(self, version: str, metrics: DetectionMetrics) -> None:
        """Record metrics for a version."""
        self.state.metrics_history[version] = metrics

    def get_metrics_history(self) -> Dict[str, DetectionMetrics]:
        """Get historical metrics."""
        return self.state.metrics_history

    # AC-PHASE41-013: Auto-threshold adjustment

    def optimize_threshold(
        self,
        chat_scores: List[Tuple[str, int, bool]],
        apply: bool = False
    ) -> CalibrationResult:
        """
        Find optimal threshold that maximizes F1 score.

        Args:
            chat_scores: List of (file_path, score, ground_truth_is_chat)
            apply: Whether to apply optimal threshold

        Returns:
            CalibrationResult with optimal threshold and metrics
        """
        # Baseline F1 with current threshold
        baseline_predictions = {
            path: score >= self.state.current_threshold
            for path, score, _ in chat_scores
        }
        baseline_gt = {path: is_chat for path, _, is_chat in chat_scores}
        baseline_metrics = self.calculate_metrics(baseline_gt, baseline_predictions)

        # Search for optimal threshold
        best_f1 = 0.0
        best_threshold = self.state.current_threshold
        best_precision = 0.0
        best_recall = 0.0

        # Try thresholds from 0 to max_score
        max_score = max(score for _, score, _ in chat_scores)

        for threshold in range(0, max_score + 1):
            predictions = {
                path: score >= threshold
                for path, score, _ in chat_scores
            }

            metrics = self.calculate_metrics(baseline_gt, predictions)

            if metrics.f1_score > best_f1:
                best_f1 = metrics.f1_score
                best_threshold = threshold
                best_precision = metrics.precision
                best_recall = metrics.recall

        # Calculate improvement
        improvement_pct = (
            ((best_f1 - baseline_metrics.f1_score) / baseline_metrics.f1_score * 100)
            if baseline_metrics.f1_score > 0
            else 0.0
        )

        result = CalibrationResult(
            optimal_threshold=best_threshold,
            optimal_f1_score=best_f1,
            optimal_precision=best_precision,
            optimal_recall=best_recall,
            improvement_pct=improvement_pct,
            baseline_f1=baseline_metrics.f1_score,
            search_range=(0, max_score),
            iterations=max_score + 1
        )

        # Apply if requested
        if apply:
            self.state.current_threshold = best_threshold

        return result

    def get_current_threshold(self) -> float:
        """Get current detection threshold."""
        return self.state.current_threshold

    def set_current_threshold(self, threshold: float) -> None:
        """Set current detection threshold."""
        self.state.current_threshold = threshold

    # AC-PHASE41-014: Marker weight learning

    def get_marker_weights(self) -> Dict[str, float]:
        """Get current marker weights as dict."""
        return {
            "User": self.state.marker_weights.User,
            "Copilot": self.state.marker_weights.Copilot,
            "Tool": self.state.marker_weights.Tool,
            "Drift": self.state.marker_weights.Drift,
            "Pattern": self.state.marker_weights.Pattern,
            "Efficiency": self.state.marker_weights.Efficiency,
        }

    def reset_marker_weights(self) -> None:
        """Reset marker weights to default (all 1.0)."""
        self.state.marker_weights = MarkerWeights()

    def learn_marker_weights(
        self,
        training_data: List[List[Any]],
        epochs: int = 100,
        learning_rate: float = 0.01
    ) -> Dict[str, Any]:
        """
        Learn marker weights via gradient descent.

        Args:
            training_data: List of [marker_dict, is_chat_bool]
            epochs: Number of training epochs
            learning_rate: Learning rate for gradient descent

        Returns:
            Dict with training history (final_loss, converged, etc.)
        """
        # Initialize weights
        weights = self.get_marker_weights()
        marker_names = list(weights.keys())

        # Training loop
        prev_loss = float('inf')
        converged = False

        for epoch in range(epochs):
            total_loss = 0.0

            for markers, is_chat in training_data:
                # Calculate weighted score
                score = sum(markers.get(name, 0) * weights[name] for name in marker_names)

                # Sigmoid for probability
                prob = 1 / (1 + math.exp(-score / 10))  # Scale down to avoid overflow

                # Binary cross-entropy loss
                epsilon = 1e-7  # Avoid log(0)
                y = 1 if is_chat else 0
                loss = -(y * math.log(prob + epsilon) + (1 - y) * math.log(1 - prob + epsilon))
                total_loss += loss

                # Gradient descent update
                error = prob - y
                for name in marker_names:
                    gradient = error * markers.get(name, 0)
                    weights[name] -= learning_rate * gradient

                    # Clip weights to [0, 2]
                    weights[name] = max(0.0, min(2.0, weights[name]))

            # Check convergence (loss change < 0.001)
            avg_loss = total_loss / len(training_data)
            if abs(prev_loss - avg_loss) < 0.001:
                converged = True
                break

            prev_loss = avg_loss

        # Update state
        self.state.marker_weights.User = weights["User"]
        self.state.marker_weights.Copilot = weights["Copilot"]
        self.state.marker_weights.Tool = weights["Tool"]
        self.state.marker_weights.Drift = weights["Drift"]
        self.state.marker_weights.Pattern = weights["Pattern"]
        self.state.marker_weights.Efficiency = weights["Efficiency"]
        self.state.marker_weights.epochs_trained = epoch + 1
        self.state.marker_weights.final_loss = prev_loss
        self.state.marker_weights.converged = converged
        self.state.marker_weights.learning_rate = learning_rate

        return {
            "final_loss": prev_loss,
            "converged": converged,
            "epochs": epoch + 1,
            "weights": weights
        }

    def predict_chat(self, markers: Dict[str, int]) -> bool:
        """
        Predict if markers indicate chat session.

        Args:
            markers: Dict of marker counts

        Returns:
            True if predicted as chat
        """
        weights = self.get_marker_weights()
        score = sum(markers.get(name, 0) * weights[name] for name in weights)
        return score >= self.state.current_threshold

    # State persistence

    def save_state(self, yaml_path: Path) -> None:
        """
        Save calibration state to YAML.

        Args:
            yaml_path: Path to save state
        """
        self.state.last_updated = datetime.now()

        with open(yaml_path, 'w') as f:
            yaml.dump(self.state.model_dump(mode='json'), f, default_flow_style=False)

    def load_state(self, yaml_path: Path) -> None:
        """
        Load calibration state from YAML.

        Args:
            yaml_path: Path to load state from
        """
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        self.state = CalibrationState(**data)
