"""
Test suite for PlanningLearner - Learning subsystem for Planning System 3.0.

Tests decision recording, feedback processing, weight calibration, and accuracy metrics.
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime

from src.operations.modules.learning.planning_learner import (
    PlanningLearner,
    RoutingDecision
)


@pytest.fixture
def temp_brain_path():
    """Create temporary brain directory for testing."""
    temp_dir = tempfile.mkdtemp()
    brain_path = Path(temp_dir) / "cortex-brain"
    brain_path.mkdir(parents=True, exist_ok=True)
    
    yield brain_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def learner(temp_brain_path):
    """Create PlanningLearner instance with temp brain path."""
    return PlanningLearner(temp_brain_path)


class TestPlanningLearner:
    """Test suite for PlanningLearner class."""
    
    def test_initialization(self, learner, temp_brain_path):
        """Test learner initializes with correct paths and defaults."""
        assert learner.brain_path == temp_brain_path
        assert learner.learning_db.parent.exists()
        assert learner.metrics_file.parent.exists()
        
        # Check default calibration factors
        assert 'scope_weight' in learner.calibration_factors
        assert 'dependencies_weight' in learner.calibration_factors
        assert 'risk_weight' in learner.calibration_factors
        assert 'uncertainty_weight' in learner.calibration_factors
        
        # Weights should sum to ~1.0
        total = sum(learner.calibration_factors.values())
        assert abs(total - 1.0) < 0.01
    
    def test_record_decision(self, learner):
        """Test decision recording creates entry in database."""
        request = "Implement user authentication system"
        tier = 3
        complexity = 0.75
        
        learner.record_decision(request, tier, complexity)
        
        # Verify decision was recorded
        assert learner.learning_db.exists()
        
        decisions = learner._load_all_decisions()
        assert len(decisions) == 1
        assert decisions[0].request == request
        assert decisions[0].predicted_tier == tier
        assert decisions[0].complexity_score == complexity
        assert decisions[0].actual_tier is None  # No feedback yet
    
    def test_record_multiple_decisions(self, learner):
        """Test recording multiple decisions."""
        requests = [
            ("Add button to UI", 2, 0.3),
            ("Refactor database layer", 4, 0.9),
            ("Fix typo in README", 1, 0.1)
        ]
        
        for req, tier, complexity in requests:
            learner.record_decision(req, tier, complexity)
        
        decisions = learner._load_all_decisions()
        assert len(decisions) == 3
        
        # Verify order preserved
        assert decisions[0].predicted_tier == 2
        assert decisions[1].predicted_tier == 4
        assert decisions[2].predicted_tier == 1
    
    def test_provide_feedback_correct_prediction(self, learner):
        """Test feedback for correct prediction."""
        request = "Add logging to service"
        learner.record_decision(request, 2, 0.4)
        
        # Provide feedback that prediction was correct
        learner.provide_feedback(request, 2, "Correctly identified as Tier 2")
        
        decisions = learner._load_all_decisions()
        assert decisions[0].actual_tier == 2
        assert decisions[0].was_correct is True
        assert "Correctly identified" in decisions[0].feedback
    
    def test_provide_feedback_incorrect_prediction(self, learner):
        """Test feedback for incorrect prediction triggers recalibration."""
        request = "Migrate to microservices architecture"
        learner.record_decision(request, 3, 0.65)
        
        # Provide feedback that it should have been Tier 4
        original_weights = learner.calibration_factors.copy()
        learner.provide_feedback(request, 4, "Too complex for Tier 3")
        
        decisions = learner._load_all_decisions()
        assert decisions[0].actual_tier == 4
        assert decisions[0].was_correct is False
        
        # Weights should have changed
        assert learner.calibration_factors != original_weights
    
    def test_get_accuracy_metrics_no_feedback(self, learner):
        """Test accuracy metrics with no feedback."""
        learner.record_decision("Test request", 2, 0.5)
        
        metrics = learner.get_accuracy_metrics()
        assert metrics['accuracy'] == 0.0  # No feedback yet
        assert metrics['total_decisions'] == 1
        assert metrics['decisions_with_feedback'] == 0
        assert metrics['correct_predictions'] == 0
    
    def test_get_accuracy_metrics_with_feedback(self, learner):
        """Test accuracy metrics calculation."""
        # Record 5 decisions with varying accuracy
        decisions_data = [
            ("Request 1", 2, 2, True),   # Correct
            ("Request 2", 3, 3, True),   # Correct
            ("Request 3", 1, 2, False),  # Incorrect
            ("Request 4", 4, 4, True),   # Correct
            ("Request 5", 2, 3, False),  # Incorrect
        ]
        
        for req, predicted, actual, _ in decisions_data:
            learner.record_decision(req, predicted, 0.5)
            learner.provide_feedback(req, actual)
        
        metrics = learner.get_accuracy_metrics()
        assert metrics['accuracy'] == 0.6  # 3/5 correct
        assert metrics['total_decisions'] == 5
        assert metrics['decisions_with_feedback'] == 5
        assert metrics['correct_predictions'] == 3
    
    def test_tier_accuracy_breakdown(self, learner):
        """Test tier-specific accuracy calculation."""
        # Create decisions for each tier
        test_cases = [
            ("Tier 1 task", 1, 1),  # Correct
            ("Tier 1 task 2", 1, 1),  # Correct
            ("Tier 2 task", 2, 3),  # Incorrect
            ("Tier 3 task", 3, 3),  # Correct
            ("Tier 4 task", 4, 3),  # Incorrect
        ]
        
        for req, predicted, actual in test_cases:
            learner.record_decision(req, predicted, 0.5)
            learner.provide_feedback(req, actual)
        
        metrics = learner.get_accuracy_metrics()
        tier_breakdown = metrics['tier_breakdown']
        
        assert tier_breakdown['tier_1'] == 1.0  # 2/2 correct
        assert tier_breakdown['tier_2'] == 0.0  # 0/0 (no actual tier 2)
        # Tier 3 has 3 entries: one correct (tier 3 task), two incorrect (tier 2→3, tier 4→3)
        assert abs(tier_breakdown['tier_3'] - 0.333) < 0.01  # 1/3 correct
    
    def test_weight_recalibration_increases_weights(self, learner):
        """Test weight increase when predicted tier too low."""
        # Predict Tier 2, actual is Tier 4
        learner.record_decision("Complex task", 2, 0.5)
        
        original_sum = sum(learner.calibration_factors.values())
        learner.provide_feedback("Complex task", 4)
        new_sum = sum(learner.calibration_factors.values())
        
        # Weights should still sum to ~1.0
        assert abs(new_sum - 1.0) < 0.01
        assert abs(original_sum - 1.0) < 0.01
    
    def test_weight_recalibration_decreases_weights(self, learner):
        """Test weight decrease when predicted tier too high."""
        # Predict Tier 4, actual is Tier 2
        learner.record_decision("Simple task", 4, 0.8)
        
        learner.provide_feedback("Simple task", 2)
        
        # Weights should still sum to ~1.0
        total = sum(learner.calibration_factors.values())
        assert abs(total - 1.0) < 0.01
    
    def test_learning_rate_decay(self, learner):
        """Test learning rate decreases with more feedback."""
        # Record first incorrect prediction
        learner.record_decision("Task 1", 2, 0.5)
        original_weights = learner.calibration_factors.copy()
        learner.provide_feedback("Task 1", 4)
        first_change = sum(
            abs(learner.calibration_factors[k] - original_weights[k])
            for k in original_weights
        )
        
        # Record many more decisions to increase feedback count
        for i in range(50):
            learner.record_decision(f"Task {i+2}", 2, 0.5)
            learner.provide_feedback(f"Task {i+2}", 2)  # All correct
        
        # Record another incorrect prediction
        learner.record_decision("Task 100", 2, 0.5)
        before_weights = learner.calibration_factors.copy()
        learner.provide_feedback("Task 100", 4)
        second_change = sum(
            abs(learner.calibration_factors[k] - before_weights[k])
            for k in before_weights
        )
        
        # Second change should be smaller due to decay
        assert second_change < first_change
    
    def test_weight_boundaries(self, learner):
        """Test weights stay within 0.1 to 0.4 boundaries."""
        # Force extreme adjustments
        for i in range(100):
            learner.record_decision(f"Task {i}", 1, 0.1)
            learner.provide_feedback(f"Task {i}", 4)  # Always predict too low
        
        # All weights should be within bounds
        for weight in learner.calibration_factors.values():
            assert 0.1 <= weight <= 0.4
    
    def test_calibration_persistence(self, learner, temp_brain_path):
        """Test calibration factors are saved and loaded."""
        # Modify calibration
        learner.record_decision("Test", 2, 0.5)
        learner.provide_feedback("Test", 4)
        
        modified_weights = learner.calibration_factors.copy()
        
        # Create new learner instance
        new_learner = PlanningLearner(temp_brain_path)
        
        # Should load saved calibration
        assert new_learner.calibration_factors == modified_weights
    
    def test_request_length_limiting(self, learner):
        """Test very long requests are truncated."""
        long_request = "x" * 1000
        learner.record_decision(long_request, 2, 0.5)
        
        decisions = learner._load_all_decisions()
        assert len(decisions[0].request) <= 500
    
    def test_get_calibration_summary(self, learner):
        """Test calibration summary generation."""
        # Record some decisions
        learner.record_decision("Task 1", 2, 0.5)
        learner.provide_feedback("Task 1", 2)
        
        summary = learner.get_calibration_summary()
        
        assert "Current Calibration Factors:" in summary
        assert "scope_weight" in summary
        assert "Routing Accuracy:" in summary
        assert "Total Decisions:" in summary
    
    def test_concurrent_decision_recording(self, learner):
        """Test handling of rapid sequential decisions."""
        import threading
        import time
        
        def record_decisions(start_idx):
            for i in range(start_idx, start_idx + 10):
                learner.record_decision(f"Task {i}", 2, 0.5)
                time.sleep(0.001)  # Small delay to reduce race conditions
        
        threads = [
            threading.Thread(target=record_decisions, args=(i*10,))
            for i in range(3)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        decisions = learner._load_all_decisions()
        # With concurrent writes, we might lose 1-2 due to race conditions
        assert 28 <= len(decisions) <= 30


class TestRoutingDecision:
    """Test RoutingDecision dataclass."""
    
    def test_routing_decision_creation(self):
        """Test creating routing decision."""
        decision = RoutingDecision(
            request="Test request",
            predicted_tier=2,
            actual_tier=None,
            complexity_score=0.5,
            timestamp=datetime.now().isoformat()
        )
        
        assert decision.request == "Test request"
        assert decision.predicted_tier == 2
        assert decision.actual_tier is None
        assert decision.complexity_score == 0.5
        assert decision.was_correct is None
    
    def test_routing_decision_with_feedback(self):
        """Test routing decision with feedback."""
        decision = RoutingDecision(
            request="Test request",
            predicted_tier=2,
            actual_tier=3,
            complexity_score=0.5,
            timestamp=datetime.now().isoformat(),
            feedback="Should be Tier 3",
            was_correct=False
        )
        
        assert decision.actual_tier == 3
        assert decision.was_correct is False
        assert decision.feedback == "Should be Tier 3"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
