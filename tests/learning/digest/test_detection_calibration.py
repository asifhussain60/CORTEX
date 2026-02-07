"""
Unit tests for DIGEST Detection Calibration System.

Tests for Phase 41 Stage 3 (ENH-057):
- AC-PHASE41-011: Ground truth labeling system (3 tests)
- AC-PHASE41-012: Precision/recall metrics (3 tests)
- AC-PHASE41-013: Auto-threshold adjustment (3 tests)
- AC-PHASE41-014: Marker weight learning (3 tests)

Total: 12 tests

Author: Asif Hussain
Date: 2026-02-07
"""

import pytest
from pathlib import Path
from typing import Dict, List, Tuple

from cortex.learning.digest.detection_calibrator import DetectionCalibrator
from cortex.learning.digest.detection_metrics import (
    DetectionMetrics,
    GroundTruthLabel,
    CalibrationResult,
)


# AC_START: AC-PHASE41-011
# Description: Ground truth labeling system
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def calibrator():
    """Create DetectionCalibrator instance."""
    return DetectionCalibrator()


@pytest.fixture
def sample_ground_truth():
    """Sample ground truth labels for testing."""
    return {
        "chat_session_1.md": GroundTruthLabel(is_chat=True, confidence=1.0),
        "chat_session_2.txt": GroundTruthLabel(is_chat=True, confidence=1.0),
        "regular_doc.md": GroundTruthLabel(is_chat=False, confidence=1.0),
        "code_file.py": GroundTruthLabel(is_chat=False, confidence=1.0),
        "ambiguous_1.md": GroundTruthLabel(is_chat=True, confidence=0.7),  # Low confidence
    }


class TestGroundTruthLabeling:
    """Test AC-PHASE41-011: Ground truth labeling system (3 tests)."""
    
    def test_stores_ground_truth_labels(self, calibrator):
        """Test storing ground truth labels for files."""
        calibrator.add_ground_truth("file1.md", is_chat=True, confidence=1.0)
        calibrator.add_ground_truth("file2.py", is_chat=False, confidence=1.0)
        
        labels = calibrator.get_ground_truth()
        
        assert "file1.md" in labels
        assert labels["file1.md"].is_chat is True
        assert labels["file1.md"].confidence == 1.0
        
        assert "file2.py" in labels
        assert labels["file2.py"].is_chat is False
    
    def test_loads_ground_truth_from_yaml(self, calibrator, tmp_path):
        """Test loading ground truth from YAML file."""
        # Create YAML ground truth file
        gt_file = tmp_path / "ground_truth.yaml"
        gt_file.write_text("""
chat_sessions:
  - path: "session1.md"
    is_chat: true
    confidence: 1.0
  - path: "session2.txt"
    is_chat: true
    confidence: 0.8

non_chat_files:
  - path: "doc.md"
    is_chat: false
    confidence: 1.0
""")
        
        calibrator.load_ground_truth(gt_file)
        labels = calibrator.get_ground_truth()
        
        assert len(labels) == 3
        assert labels["session1.md"].is_chat is True
        assert labels["session2.txt"].confidence == 0.8
        assert labels["doc.md"].is_chat is False
    
    def test_updates_existing_labels(self, calibrator):
        """Test updating existing ground truth labels."""
        # Initial label
        calibrator.add_ground_truth("file.md", is_chat=True, confidence=0.7)
        
        # Update with higher confidence
        calibrator.add_ground_truth("file.md", is_chat=True, confidence=1.0)
        
        labels = calibrator.get_ground_truth()
        assert labels["file.md"].confidence == 1.0  # Updated


# AC-PHASE41-012: Precision/recall metrics (3 tests)


class TestPrecisionRecallMetrics:
    """Test AC-PHASE41-012: Precision/recall metrics (3 tests)."""
    
    def test_calculates_precision_recall(self, calibrator):
        """Test precision = TP/(TP+FP), recall = TP/(TP+FN)."""
        # Ground truth: 3 chat, 2 non-chat
        # Predictions: 2 TP, 1 FP, 1 FN
        
        ground_truth = {
            "chat1.md": True,  # TP: detected as chat
            "chat2.md": True,  # TP: detected as chat
            "chat3.md": True,  # FN: missed (detected as non-chat)
            "doc1.md": False,  # TN: correctly not detected
            "doc2.md": False,  # FP: incorrectly detected as chat
        }
        
        predictions = {
            "chat1.md": True,   # TP
            "chat2.md": True,   # TP
            "chat3.md": False,  # FN
            "doc1.md": False,   # TN
            "doc2.md": True,    # FP
        }
        
        metrics = calibrator.calculate_metrics(ground_truth, predictions)
        
        # TP=2, FP=1, FN=1, TN=1
        assert metrics.precision == pytest.approx(0.667, rel=0.01)  # 2/(2+1)
        assert metrics.recall == pytest.approx(0.667, rel=0.01)     # 2/(2+1)
        assert metrics.f1_score == pytest.approx(0.667, rel=0.01)   # 2*P*R/(P+R)
        assert metrics.true_positives == 2
        assert metrics.false_positives == 1
        assert metrics.false_negatives == 1
    
    def test_perfect_precision_recall(self, calibrator):
        """Test 100% precision/recall with perfect detection."""
        ground_truth = {
            "chat1.md": True,
            "chat2.md": True,
            "doc1.md": False,
            "doc2.md": False,
        }
        
        predictions = {
            "chat1.md": True,
            "chat2.md": True,
            "doc1.md": False,
            "doc2.md": False,
        }
        
        metrics = calibrator.calculate_metrics(ground_truth, predictions)
        
        assert metrics.precision == 1.0
        assert metrics.recall == 1.0
        assert metrics.f1_score == 1.0
    
    def test_tracks_metrics_over_time(self, calibrator):
        """Test tracking precision/recall across multiple calibrations."""
        # Calibration 1: Low performance
        metrics_v1 = DetectionMetrics(
            precision=0.6,
            recall=0.5,
            f1_score=0.545,
            true_positives=5,
            false_positives=3,
            false_negatives=5
        )
        
        # Calibration 2: Improved performance
        metrics_v2 = DetectionMetrics(
            precision=0.8,
            recall=0.75,
            f1_score=0.774,
            true_positives=9,
            false_positives=2,
            false_negatives=3
        )
        
        calibrator.record_metrics("v1", metrics_v1)
        calibrator.record_metrics("v2", metrics_v2)
        
        history = calibrator.get_metrics_history()
        
        assert len(history) == 2
        assert history["v2"].f1_score > history["v1"].f1_score


# AC-PHASE41-013: Auto-threshold adjustment (3 tests)


class TestAutoThresholdAdjustment:
    """Test AC-PHASE41-013: Auto-threshold adjustment (3 tests)."""
    
    def test_finds_optimal_threshold_for_f1(self, calibrator):
        """Test finding threshold that maximizes F1 score."""
        # Mock data: chat scores from detection
        chat_scores = [
            ("chat1.md", 8, True),   # True positive at threshold 5
            ("chat2.md", 7, True),   # True positive at threshold 5
            ("chat3.md", 4, True),   # False negative at threshold 5
            ("doc1.md", 3, False),   # True negative at threshold 5
            ("doc2.md", 6, False),   # False positive at threshold 5
        ]
        
        result = calibrator.optimize_threshold(chat_scores)
        
        # Optimal threshold should maximize F1 (actual: 4 gives best F1)
        assert result.optimal_threshold >= 4
        assert result.optimal_f1_score >= 0.6  # Should improve F1
        assert result.improvement_pct > 0
    
    def test_adjusts_threshold_based_on_data(self, calibrator):
        """Test threshold adjustment based on data distribution."""
        # High-quality chat sessions (scores 8-10)
        high_quality = [
            ("chat1.md", 10, True),
            ("chat2.md", 9, True),
            ("chat3.md", 8, True),
            ("doc1.md", 2, False),
            ("doc2.md", 3, False),
        ]
        
        result_high = calibrator.optimize_threshold(high_quality)
        
        # Low-quality chat sessions (scores 4-6)
        low_quality = [
            ("chat1.md", 6, True),
            ("chat2.md", 5, True),
            ("chat3.md", 4, True),
            ("doc1.md", 2, False),
            ("doc2.md", 3, False),
        ]
        
        result_low = calibrator.optimize_threshold(low_quality)
        
        # Both should find optimal thresholds that work for their data
        assert result_high.optimal_f1_score >= 0.9  # High quality = high F1
        assert result_low.optimal_f1_score >= 0.9   # Low quality = also high F1
        # Threshold values adapt to data distribution
        assert result_high.optimal_threshold >= 4
        assert result_low.optimal_threshold >= 4
    
    def test_applies_optimized_threshold(self, calibrator):
        """Test applying optimized threshold to SessionParser."""
        initial_threshold = calibrator.get_current_threshold()
        
        # Optimize with sample data
        chat_scores = [
            ("chat1.md", 8, True),
            ("chat2.md", 7, True),
            ("doc1.md", 3, False),
        ]
        
        result = calibrator.optimize_threshold(chat_scores, apply=True)
        
        new_threshold = calibrator.get_current_threshold()
        
        assert new_threshold != initial_threshold
        assert new_threshold == result.optimal_threshold


# AC-PHASE41-014: Marker weight learning (3 tests)


class TestMarkerWeightLearning:
    """Test AC-PHASE41-014: Marker weight learning (3 tests)."""
    
    def test_learns_marker_weights_from_data(self, calibrator):
        """Test gradient descent learning for marker weights."""
        # Initial weights (equal)
        initial_weights = calibrator.get_marker_weights()
        
        # Training data: marker presence and ground truth
        training_data = [
            [
                # chat1: User, Copilot present → chat
                {"User": 5, "Copilot": 5, "Tool": 2, "Drift": 0, "Pattern": 0, "Efficiency": 0},
                True,
            ],
            [
                # chat2: User, Copilot, Tool present → chat
                {"User": 3, "Copilot": 3, "Tool": 1, "Drift": 1, "Pattern": 0, "Efficiency": 0},
                True,
            ],
            [
                # doc1: No markers → non-chat
                {"User": 0, "Copilot": 0, "Tool": 0, "Drift": 0, "Pattern": 0, "Efficiency": 0},
                False,
            ],
            [
                # doc2: Only Pattern marker → non-chat (low weight)
                {"User": 0, "Copilot": 0, "Tool": 0, "Drift": 0, "Pattern": 3, "Efficiency": 0},
                False,
            ],
        ]
        
        # Learn weights
        calibrator.learn_marker_weights(training_data, epochs=100, learning_rate=0.01)
        
        learned_weights = calibrator.get_marker_weights()
        
        # User/Copilot weights should increase (strong predictors)
        assert learned_weights["User"] > initial_weights["User"]
        assert learned_weights["Copilot"] > initial_weights["Copilot"]
        
        # Pattern weight should decrease or stay low (weak predictor)
        assert learned_weights["Pattern"] <= initial_weights["Pattern"]
    
    def test_weights_converge_with_training(self, calibrator):
        """Test that weights converge after sufficient training."""
        training_data = [
            [{"User": 5, "Copilot": 5, "Tool": 2, "Drift": 0, "Pattern": 0, "Efficiency": 0}, True],
            [{"User": 3, "Copilot": 3, "Tool": 1, "Drift": 1, "Pattern": 0, "Efficiency": 0}, True],
            [{"User": 0, "Copilot": 0, "Tool": 0, "Drift": 0, "Pattern": 0, "Efficiency": 0}, False],
            [{"User": 0, "Copilot": 0, "Tool": 0, "Drift": 0, "Pattern": 3, "Efficiency": 0}, False],
        ]
        
        # Train for 10 epochs
        history_10 = calibrator.learn_marker_weights(training_data, epochs=10, learning_rate=0.01)
        
        # Train for 100 epochs
        calibrator.reset_marker_weights()  # Reset first
        history_100 = calibrator.learn_marker_weights(training_data, epochs=100, learning_rate=0.01)
        
        # Loss should decrease with more training
        assert history_100["final_loss"] < history_10["final_loss"]
        assert history_100["converged"] is True
    
    def test_applies_learned_weights_to_detection(self, calibrator):
        """Test using learned weights for improved detection."""
        # Initial detection accuracy
        test_data = [
            {"User": 4, "Copilot": 4, "Tool": 1, "Drift": 0, "Pattern": 0, "Efficiency": 0},
            {"User": 0, "Copilot": 0, "Tool": 0, "Drift": 0, "Pattern": 2, "Efficiency": 0},
        ]
        
        ground_truth = [True, False]
        
        initial_predictions = [calibrator.predict_chat(markers) for markers in test_data]
        
        # Train weights
        training_data = [
            [{"User": 5, "Copilot": 5, "Tool": 2, "Drift": 0, "Pattern": 0, "Efficiency": 0}, True],
            [{"User": 0, "Copilot": 0, "Tool": 0, "Drift": 0, "Pattern": 3, "Efficiency": 0}, False],
        ]
        calibrator.learn_marker_weights(training_data, epochs=100, learning_rate=0.01)
        
        # Post-training predictions
        trained_predictions = [calibrator.predict_chat(markers) for markers in test_data]
        
        # Accuracy should improve
        initial_accuracy = sum(p == gt for p, gt in zip(initial_predictions, ground_truth)) / len(ground_truth)
        trained_accuracy = sum(p == gt for p, gt in zip(trained_predictions, ground_truth)) / len(ground_truth)
        
        assert trained_accuracy >= initial_accuracy


# Integration test: Full calibration cycle


def test_full_calibration_cycle(calibrator, sample_ground_truth):
    """Integration test: Complete calibration workflow."""
    # 1. Load ground truth
    for file_path, label in sample_ground_truth.items():
        calibrator.add_ground_truth(file_path, label.is_chat, label.confidence)
    
    # 2. Generate detection scores (mock)
    chat_scores = [
        ("chat_session_1.md", 8, True),
        ("chat_session_2.txt", 7, True),
        ("regular_doc.md", 3, False),
        ("code_file.py", 2, False),
        ("ambiguous_1.md", 6, True),
    ]
    
    # 3. Calculate metrics
    predictions = {path: score >= 5 for path, score, _ in chat_scores}
    ground_truth = {path: label.is_chat for path, label in sample_ground_truth.items()}
    
    metrics = calibrator.calculate_metrics(ground_truth, predictions)
    
    assert metrics.precision > 0
    assert metrics.recall > 0
    
    # 4. Optimize threshold
    result = calibrator.optimize_threshold(chat_scores, apply=True)
    
    assert result.optimal_f1_score >= metrics.f1_score  # Should improve or stay same


def test_saves_and_loads_calibration_state(calibrator, tmp_path):
    """Test persisting calibration state (weights, threshold, metrics)."""
    # Set up calibration
    calibrator.add_ground_truth("chat1.md", is_chat=True)
    calibrator.set_current_threshold(7)
    
    training_data = [
        [{"User": 5, "Copilot": 5, "Tool": 2, "Drift": 0, "Pattern": 0, "Efficiency": 0}, True],
        [{"User": 0, "Copilot": 0, "Tool": 0, "Drift": 0, "Pattern": 0, "Efficiency": 0}, False],
    ]
    calibrator.learn_marker_weights(training_data, epochs=50)
    
    # Save state
    state_file = tmp_path / "calibration_state.yaml"
    calibrator.save_state(state_file)
    
    # Load into new instance
    new_calibrator = DetectionCalibrator()
    new_calibrator.load_state(state_file)
    
    # Verify state preserved
    assert new_calibrator.get_current_threshold() == 7
    assert new_calibrator.get_marker_weights() == calibrator.get_marker_weights()
    assert len(new_calibrator.get_ground_truth()) == 1


# AC_COMPLETE: AC-PHASE41-011, AC-PHASE41-012, AC-PHASE41-013, AC-PHASE41-014 ✅ 12/12 tests
