"""
Tests for Progress Monitoring Integration - Feature 5
Tests progress tracking, velocity calculation, and dashboard integration

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil
from src.orchestrators.progress_monitor import (
    ProgressMonitor,
    PhaseProgress,
    VelocityMetrics,
    ProgressStatus
)


class TestPhaseTracking:
    """Test phase start/complete/fail tracking"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_starts_new_phase_tracking(self, temp_storage):
        """Should track when a phase starts"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        result = monitor.start_phase(
            feature_name="Feature 5",
            phase_name="Phase 5.1 (RED)",
            estimated_hours=0.5
        )
        
        assert result.status == ProgressStatus.IN_PROGRESS
        assert result.feature_name == "Feature 5"
        assert result.phase_name == "Phase 5.1 (RED)"
        assert result.start_time is not None
        assert result.estimated_hours == 0.5
        assert result.actual_hours is None
    
    def test_completes_phase_tracking(self, temp_storage):
        """Should track when a phase completes"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        monitor.start_phase("Feature 5", "Phase 5.1", 0.5)
        
        result = monitor.complete_phase("Feature 5", "Phase 5.1")
        
        assert result.status == ProgressStatus.COMPLETED
        assert result.end_time is not None
        assert result.actual_hours is not None
        assert result.actual_hours > 0
    
    def test_marks_phase_as_failed(self, temp_storage):
        """Should track phase failures with reason"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        monitor.start_phase("Feature 5", "Phase 5.1", 0.5)
        
        result = monitor.fail_phase(
            "Feature 5",
            "Phase 5.1",
            reason="Tests not failing as expected"
        )
        
        assert result.status == ProgressStatus.FAILED
        assert result.failure_reason == "Tests not failing as expected"
        assert result.end_time is not None
    
    def test_retrieves_phase_status(self, temp_storage):
        """Should retrieve current phase status"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        monitor.start_phase("Feature 5", "Phase 5.1", 0.5)
        
        status = monitor.get_phase_status("Feature 5", "Phase 5.1")
        
        assert status.status == ProgressStatus.IN_PROGRESS
        assert status.feature_name == "Feature 5"
    
    def test_lists_all_phases_for_feature(self, temp_storage):
        """Should list all phases for a feature"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        monitor.start_phase("Feature 5", "Phase 5.1", 0.5)
        monitor.complete_phase("Feature 5", "Phase 5.1")
        monitor.start_phase("Feature 5", "Phase 5.2", 0.75)
        
        phases = monitor.get_feature_phases("Feature 5")
        
        assert len(phases) == 2
        assert phases[0].phase_name == "Phase 5.1"
        assert phases[0].status == ProgressStatus.COMPLETED
        assert phases[1].phase_name == "Phase 5.2"
        assert phases[1].status == ProgressStatus.IN_PROGRESS


class TestVelocityCalculation:
    """Test velocity and performance metrics"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_calculates_phases_per_hour(self, temp_storage):
        """Should calculate phase completion velocity"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # Manually create phases with specific durations
        base_time = datetime(2025, 12, 12, 10, 0, 0)
        
        # Phase 1: 40 minutes
        phase1 = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        phase1.start_time = base_time
        phase1.end_time = base_time + timedelta(minutes=40)
        phase1.actual_hours = 40 / 60
        phase1.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.1"] = phase1
        
        # Phase 2: 40 minutes
        phase2 = monitor.start_phase("Feature 1", "Phase 1.2", 0.5)
        phase2.start_time = base_time + timedelta(minutes=40)
        phase2.end_time = base_time + timedelta(minutes=80)
        phase2.actual_hours = 40 / 60
        phase2.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.2"] = phase2
        
        # Phase 3: 40 minutes (total 2 hours for 3 phases = 1.5 phases/hour)
        phase3 = monitor.start_phase("Feature 1", "Phase 1.3", 0.5)
        phase3.start_time = base_time + timedelta(minutes=80)
        phase3.end_time = base_time + timedelta(minutes=120)
        phase3.actual_hours = 40 / 60
        phase3.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.3"] = phase3
        
        velocity = monitor.calculate_velocity()
        
        assert velocity.phases_per_hour == pytest.approx(1.5, rel=0.1)
        assert velocity.total_phases_completed == 3
        assert velocity.total_hours_spent == pytest.approx(2.0, rel=0.1)
    
    def test_compares_estimated_vs_actual_time(self, temp_storage):
        """Should compare estimated vs actual completion time"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # Phase estimated 0.5 hours, actually takes 1 hour
        phase = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        phase.actual_hours = 1.0
        phase.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.1"] = phase
        
        velocity = monitor.calculate_velocity()
        
        # Accuracy = (estimated / actual) * 100 = (0.5 / 1.0) * 100 = 50%
        assert velocity.accuracy_percentage == pytest.approx(50.0, rel=0.1)
        assert velocity.total_estimated_hours == 0.5
        assert velocity.total_actual_hours == pytest.approx(1.0, rel=0.1)
    
    def test_calculates_completion_percentage(self, temp_storage):
        """Should calculate overall completion percentage"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # 3 phases: 2 complete, 1 in progress = 66.67%
        phase1 = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        phase1.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.1"] = phase1
        
        phase2 = monitor.start_phase("Feature 1", "Phase 1.2", 0.5)
        phase2.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.2"] = phase2
        
        monitor.start_phase("Feature 1", "Phase 1.3", 0.5)
        # Phase 1.3 remains IN_PROGRESS
        
        completion = monitor.calculate_completion_percentage()
        
        assert completion == pytest.approx(66.67, rel=0.1)
    
    def test_retrieves_historical_velocity_data(self, temp_storage):
        """Should retrieve historical velocity from storage"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # Create completed phases within last 7 days
        base_time = datetime.now() - timedelta(days=3)
        
        phase1 = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        phase1.end_time = base_time
        phase1.actual_hours = 0.5
        phase1.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.1"] = phase1
        
        phase2 = monitor.start_phase("Feature 2", "Phase 2.1", 0.75)
        phase2.end_time = base_time + timedelta(days=1)
        phase2.actual_hours = 0.75
        phase2.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 2::Phase 2.1"] = phase2
        
        history = monitor.get_historical_velocity(days=7)
        
        assert len(history) == 2
        assert history[0]['hours'] == 0.5
        assert history[1]['hours'] == 0.75


class TestDashboardIntegration:
    """Test real-time dashboard display"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_generates_progress_summary(self, temp_storage):
        """Should generate summary for dashboard display"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        phase1 = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        phase1.status = ProgressStatus.COMPLETED
        phase1.actual_hours = 0.5
        monitor.phases[f"Feature 1::Phase 1.1"] = phase1
        
        monitor.start_phase("Feature 1", "Phase 1.2", 0.5)
        
        summary = monitor.generate_dashboard_summary()
        
        assert summary['total_phases'] == 2
        assert summary['completed_phases'] == 1
        assert summary['in_progress_phases'] == 1
        assert summary['completion_percentage'] == 50.0
        assert 'velocity' in summary
    
    def test_generates_phase_timeline(self, temp_storage):
        """Should generate timeline for visualization"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        base_time = datetime(2025, 12, 12, 10, 0, 0)
        
        phase = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        phase.start_time = base_time
        phase.end_time = base_time + timedelta(minutes=30)
        phase.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.1"] = phase
        
        timeline = monitor.generate_timeline()
        
        assert len(timeline) == 1
        assert timeline[0]['feature'] == "Feature 1"
        assert timeline[0]['phase'] == "Phase 1.1"
        assert timeline[0]['duration_minutes'] == 30
    
    def test_detects_bottlenecks(self, temp_storage):
        """Should detect phases taking longer than estimated"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # Phase estimated 0.5 hours, took 2 hours
        phase = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        phase.actual_hours = 2.0
        phase.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.1"] = phase
        
        bottlenecks = monitor.detect_bottlenecks()
        
        assert len(bottlenecks) == 1
        assert bottlenecks[0]['phase'] == "Phase 1.1"
        assert bottlenecks[0]['overrun_percentage'] == 300.0


class TestOrchestratorIntegration:
    """Test integration with other orchestrators"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_tracks_planning_orchestrator_phases(self, temp_storage):
        """Should track Planning Orchestrator phase transitions"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # Simulate Planning Orchestrator calling hooks
        monitor.on_orchestrator_phase_start(
            orchestrator="PlanningOrchestrator",
            phase="DoR Validation"
        )
        
        status = monitor.get_current_phase()
        
        assert status.feature_name == "PlanningOrchestrator"
        assert status.phase_name == "DoR Validation"
        assert status.status == ProgressStatus.IN_PROGRESS
    
    def test_tracks_tdd_orchestrator_phases(self, temp_storage):
        """Should track TDD Mastery Orchestrator phases"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        monitor.on_orchestrator_phase_start("TDDOrchestrator", "RED Phase")
        monitor.on_orchestrator_phase_complete("TDDOrchestrator", "RED Phase")
        monitor.on_orchestrator_phase_start("TDDOrchestrator", "GREEN Phase")
        
        phases = monitor.get_feature_phases("TDDOrchestrator")
        
        assert len(phases) == 2
        assert phases[0].phase_name == "RED Phase"
        assert phases[0].status == ProgressStatus.COMPLETED
        assert phases[1].phase_name == "GREEN Phase"
        assert phases[1].status == ProgressStatus.IN_PROGRESS
    
    def test_tracks_environment_gate_validations(self, temp_storage):
        """Should track TDD Environment Gate checks"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        monitor.on_gate_validation_start("TDDEnvironmentGate")
        monitor.on_gate_validation_complete("TDDEnvironmentGate", passed=True)
        
        validations = monitor.get_gate_validations()
        
        assert len(validations) == 1
        assert validations[0]['gate'] == "TDDEnvironmentGate"
        assert validations[0]['passed'] is True
    
    def test_auto_tracks_git_checkpoints(self, temp_storage):
        """Should auto-track git checkpoints from Feature 2"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # For now, just verify method exists and returns empty list
        monitor.sync_with_git_checkpoints()
        checkpoints = monitor.get_checkpoints()
        
        assert isinstance(checkpoints, list)


class TestMetricsPersistence:
    """Test persistence to storage"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_persists_phase_to_storage(self, temp_storage):
        """Should persist phase data to storage file"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        monitor.complete_phase("Feature 1", "Phase 1.1")
        
        # Verify storage file exists
        storage_file = temp_storage / "phases.json"
        assert storage_file.exists()
        
        # Verify data persisted
        import json
        with open(storage_file, 'r') as f:
            data = json.load(f)
        
        assert "Feature 1::Phase 1.1" in data
        assert data["Feature 1::Phase 1.1"]['status'] == 'completed'
    
    def test_loads_phases_from_storage(self, temp_storage):
        """Should load existing phases from storage"""
        # Create storage file with data
        storage_file = temp_storage / "phases.json"
        import json
        
        data = {
            "Feature 1::Phase 1.1": {
                'feature_name': 'Feature 1',
                'phase_name': 'Phase 1.1',
                'status': 'completed',
                'start_time': '2025-12-12T10:00:00',
                'end_time': '2025-12-12T10:30:00',
                'estimated_hours': 0.5,
                'actual_hours': 0.5,
                'failure_reason': None
            }
        }
        
        storage_file.parent.mkdir(parents=True, exist_ok=True)
        with open(storage_file, 'w') as f:
            json.dump(data, f)
        
        # Load monitor
        monitor = ProgressMonitor(storage_path=temp_storage)
        phases = monitor.get_feature_phases("Feature 1")
        
        assert len(phases) == 1
        assert phases[0].phase_name == "Phase 1.1"
        assert phases[0].status == ProgressStatus.COMPLETED
    
    def test_updates_existing_phase_in_storage(self, temp_storage):
        """Should update phase status in storage"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        monitor.complete_phase("Feature 1", "Phase 1.1")
        
        # Verify updated in storage
        storage_file = temp_storage / "phases.json"
        import json
        with open(storage_file, 'r') as f:
            data = json.load(f)
        
        assert data["Feature 1::Phase 1.1"]['status'] == 'completed'
        assert data["Feature 1::Phase 1.1"]['end_time'] is not None
    
    def test_cleans_old_metrics_from_storage(self, temp_storage):
        """Should clean metrics older than 30 days"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # Create old phase (31 days ago)
        old_phase = monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        old_phase.end_time = datetime.now() - timedelta(days=31)
        old_phase.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 1::Phase 1.1"] = old_phase
        
        # Create recent phase
        recent_phase = monitor.start_phase("Feature 2", "Phase 2.1", 0.5)
        recent_phase.end_time = datetime.now() - timedelta(days=1)
        recent_phase.status = ProgressStatus.COMPLETED
        monitor.phases[f"Feature 2::Phase 2.1"] = recent_phase
        
        # Save both
        monitor._save_phase(old_phase)
        monitor._save_phase(recent_phase)
        
        # Cleanup
        monitor.cleanup_old_metrics(days=30)
        
        # Verify old removed, recent kept
        assert "Feature 1::Phase 1.1" not in monitor.phases
        assert "Feature 2::Phase 2.1" in monitor.phases


class TestPerformanceRequirements:
    """Test performance benchmarks"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_phase_tracking_completes_under_100ms(self, temp_storage):
        """Should track phase start/complete in under 100ms"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        start = datetime.now()
        monitor.start_phase("Feature 1", "Phase 1.1", 0.5)
        monitor.complete_phase("Feature 1", "Phase 1.1")
        duration = (datetime.now() - start).total_seconds()
        
        assert duration < 0.1  # 100ms
    
    def test_dashboard_summary_generates_under_500ms(self, temp_storage):
        """Should generate dashboard summary in under 500ms"""
        monitor = ProgressMonitor(storage_path=temp_storage)
        
        # Create 20 phases
        for i in range(20):
            phase = monitor.start_phase(f"Feature {i}", f"Phase {i}", 0.5)
            if i % 2 == 0:
                phase.status = ProgressStatus.COMPLETED
                phase.actual_hours = 0.5
                monitor.phases[f"Feature {i}::Phase {i}"] = phase
        
        start = datetime.now()
        summary = monitor.generate_dashboard_summary()
        duration = (datetime.now() - start).total_seconds()
        
        assert duration < 0.5  # 500ms
        assert summary['total_phases'] == 20
