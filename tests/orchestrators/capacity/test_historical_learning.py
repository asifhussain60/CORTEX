"""
Test Historical Learning System (CAP-011-013).

Tests estimate tracking, actual recording, and accuracy calculation (MAPE).

AC Coverage:
- CAP-011: Estimate tracking with audit trail
- CAP-012: Actual hours recording
- CAP-013: MAPE calculation and model weight adjustment
"""

import pytest
from cortex.capacity.historical_learning import (
    LearningOrchestrator,
    EstimateRecord,
    ActualRecord,
)


class TestEstimateTracking:
    """Test estimate recording (CAP-011)."""
    
    def test_record_estimate_stores_all_models(self):
        """Record should capture PERT, SP, CPM, and consensus estimates."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_estimate(
            task_id="T1",
            pert_estimate=58.0,
            story_point_estimate=60.0,
            cpm_estimate=52.0,
            consensus_estimate=57.6
        )
        
        record = orchestrator.get_estimate("T1")
        assert record is not None
        assert record.task_id == "T1"
        assert record.pert_estimate == 58.0
        assert record.story_point_estimate == 60.0
        assert record.cpm_estimate == 52.0
        assert record.consensus_estimate == 57.6
    
    def test_multiple_estimates_stored_separately(self):
        """Each task should have its own estimate record."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_estimate("T1", 50.0, 55.0, 48.0, 51.5)
        orchestrator.record_estimate("T2", 100.0, 110.0, 95.0, 103.0)
        
        assert orchestrator.get_estimate("T1").consensus_estimate == 51.5
        assert orchestrator.get_estimate("T2").consensus_estimate == 103.0
    
    def test_estimate_includes_timestamp(self):
        """Estimate records should include creation timestamp."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_estimate("T1", 50.0, 55.0, 48.0, 51.5)
        
        record = orchestrator.get_estimate("T1")
        assert record.timestamp is not None


class TestActualRecording:
    """Test actual hours capture (CAP-012)."""
    
    def test_record_actual_hours(self):
        """Record should capture actual hours spent."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_actual(
            task_id="T1",
            actual_hours=62.0
        )
        
        actual = orchestrator.get_actual("T1")
        assert actual is not None
        assert actual.task_id == "T1"
        assert actual.actual_hours == 62.0
    
    def test_record_actual_with_team_info(self):
        """Actual record can include team composition."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_actual(
            task_id="T1",
            actual_hours=62.0,
            team_info={"senior": 1, "mid": 2, "junior": 1}
        )
        
        actual = orchestrator.get_actual("T1")
        assert actual.team_info == {"senior": 1, "mid": 2, "junior": 1}
    
    def test_actual_includes_timestamp(self):
        """Actual records should include completion timestamp."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_actual("T1", 62.0)
        
        actual = orchestrator.get_actual("T1")
        assert actual.timestamp is not None


class TestAccuracyCalculation:
    """Test MAPE calculation (CAP-013)."""
    
    def test_calculate_mape_for_single_task(self):
        """MAPE = |actual - estimate| / actual * 100."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_estimate("T1", 58.0, 60.0, 52.0, 57.6)
        orchestrator.record_actual("T1", 62.0)
        
        mape = orchestrator.calculate_mape()
        
        # MAPE = |62 - 57.6| / 62 * 100 = 7.1%
        assert 7.0 <= mape <= 7.2
    
    def test_calculate_mape_for_multiple_tasks(self):
        """MAPE should average across multiple completed tasks."""
        orchestrator = LearningOrchestrator()
        
        # T1: estimate 60, actual 62 → |62-60|/62 = 3.2%
        orchestrator.record_estimate("T1", 58.0, 60.0, 52.0, 60.0)
        orchestrator.record_actual("T1", 62.0)
        
        # T2: estimate 100, actual 90 → |90-100|/90 = 11.1%
        orchestrator.record_estimate("T2", 98.0, 105.0, 95.0, 100.0)
        orchestrator.record_actual("T2", 90.0)
        
        mape = orchestrator.calculate_mape()
        
        # Average: (3.2 + 11.1) / 2 = 7.15%
        assert 7.0 <= mape <= 7.5
    
    def test_mape_only_includes_completed_tasks(self):
        """MAPE calculation should skip tasks without actual hours."""
        orchestrator = LearningOrchestrator()
        
        # T1: completed
        orchestrator.record_estimate("T1", 58.0, 60.0, 52.0, 60.0)
        orchestrator.record_actual("T1", 62.0)
        
        # T2: estimated but not completed
        orchestrator.record_estimate("T2", 100.0, 110.0, 95.0, 103.0)
        
        mape = orchestrator.calculate_mape()
        
        # Only T1 included: |62-60|/62 = 3.2%
        assert 3.0 <= mape <= 3.5
    
    def test_perfect_estimate_has_zero_mape(self):
        """Perfect estimates should result in 0% MAPE."""
        orchestrator = LearningOrchestrator()
        
        orchestrator.record_estimate("T1", 60.0, 60.0, 60.0, 60.0)
        orchestrator.record_actual("T1", 60.0)
        
        mape = orchestrator.calculate_mape()
        assert mape == 0.0
    
    def test_mape_below_target_threshold(self):
        """Production MAPE target: <15% for reliable planning."""
        orchestrator = LearningOrchestrator()
        
        # Simulate realistic estimates within 15% error
        orchestrator.record_estimate("T1", 50.0, 55.0, 48.0, 52.0)
        orchestrator.record_actual("T1", 56.0)
        
        mape = orchestrator.calculate_mape()
        
        # |56-52|/56 = 7.1% < 15% ✅
        assert mape < 15.0
