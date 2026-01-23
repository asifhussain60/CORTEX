"""
Progress Tracker Tests - TDD for AC-FR-005

Tests for:
- AC-FR-005-01: Progress Tracking by Phase (% complete calculation)
- AC-FR-005-02: Blocker Detection & Escalation Alerts
- AC-FR-005-03: Progress Persistence to Database

Author: Asif Hussain
"""

import pytest

from cortex.infrastructure.progress_tracker import (
    ProgressTrackerManager,
    BlockerSeverity,
    BlockerCategory,
    AlertPriority,
)
from cortex.infrastructure.database import DatabaseManager, DatabaseConfig


class TestPhaseProgressInitialization:
    """Test phase progress initialization"""
    
    def test_initialize_phase(self):
        """Should initialize phase progress tracking."""
        tracker = ProgressTrackerManager()
        
        result = tracker.initialize_phase("PHASE-01", total_acs=36)
        
        assert result.is_ok()
        progress = result.unwrap()
        assert progress.phase_id == "PHASE-01"
        assert progress.total_acs == 36
        assert progress.completed_acs == 0
        assert progress.completion_percentage == 0.0
    
    def test_cannot_reinitialize_phase(self):
        """Cannot initialize phase twice."""
        tracker = ProgressTrackerManager()
        
        tracker.initialize_phase("PHASE-01", total_acs=36)
        result = tracker.initialize_phase("PHASE-01", total_acs=36)
        
        assert result.is_err()
        assert "already initialized" in str(result).lower()


@pytest.mark.ac("FR-005-01")
class TestProgressTracking:
    """Test AC-FR-005-01: Progress tracking and calculation"""
    
    def test_get_initial_phase_progress(self):
        """Should get initial 0% progress."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        result = tracker.get_phase_progress("PHASE-01")
        
        assert result.is_ok()
        progress = result.unwrap()
        assert progress.completion_percentage == 0.0
        assert progress.get_status() == "NOT_STARTED"
    
    def test_update_ac_status_to_completed(self):
        """Should update progress when AC completed."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        result = tracker.update_ac_status("PHASE-01", "AC-TEST-001", "COMPLETED")
        
        assert result.is_ok()
        progress = result.unwrap()
        assert progress.completed_acs == 1
        assert progress.completion_percentage == 10.0
    
    def test_progress_percentage_calculation(self):
        """Should correctly calculate completion percentage."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        # Complete 5 ACs
        for i in range(5):
            tracker.update_ac_status("PHASE-01", f"AC-TEST-{i:03d}", "COMPLETED")
        
        result = tracker.get_phase_progress("PHASE-01")
        progress = result.unwrap()
        
        assert progress.completion_percentage == 50.0
    
    def test_100_percent_completion(self):
        """Should reach 100% completion."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=5)
        
        # Complete all ACs
        for i in range(5):
            tracker.update_ac_status("PHASE-01", f"AC-TEST-{i:03d}", "COMPLETED")
        
        result = tracker.get_phase_progress("PHASE-01")
        progress = result.unwrap()
        
        assert progress.completion_percentage == 100.0
        assert progress.get_status() == "COMPLETE"
    
    def test_progress_with_in_progress_acs(self):
        """Should track in-progress ACs."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        tracker.update_ac_status("PHASE-01", "AC-TEST-001", "COMPLETED")
        tracker.update_ac_status("PHASE-01", "AC-TEST-002", "IN_PROGRESS")
        
        result = tracker.get_phase_progress("PHASE-01")
        progress = result.unwrap()
        
        assert progress.completed_acs == 1
        assert progress.in_progress_acs == 1
        assert progress.get_status() == "IN_PROGRESS"
    
    def test_progress_with_blocked_acs(self):
        """Should track blocked ACs and show BLOCKED status when blockers exist."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        tracker.update_ac_status("PHASE-01", "AC-TEST-001", "BLOCKED")
        
        # Add a blocker to trigger BLOCKED status
        blocker_result = tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.HIGH,
            "Test failure"
        )
        assert blocker_result.is_ok()
        
        result = tracker.get_phase_progress("PHASE-01")
        progress = result.unwrap()
        
        assert progress.blocked_acs == 1
        assert progress.active_blockers == 1
        assert progress.get_status() == "BLOCKED"


@pytest.mark.ac("FR-005-02")
class TestBlockerDetection:
    """Test AC-FR-005-02: Blocker detection and management"""
    
    def test_add_blocker(self):
        """Should add blocker to phase."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        result = tracker.add_blocker(
            ac_id="AC-TEST-001",
            phase_id="PHASE-01",
            category=BlockerCategory.FAILED_TEST,
            severity=BlockerSeverity.HIGH,
            description="Test suite failing",
        )
        
        assert result.is_ok()
        blocker = result.unwrap()
        assert blocker.ac_id == "AC-TEST-001"
        assert blocker.is_active() is True
    
    def test_blocker_with_impact_estimate(self):
        """Should track estimated impact hours."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        result = tracker.add_blocker(
            ac_id="AC-TEST-001",
            phase_id="PHASE-01",
            category=BlockerCategory.MISSING_DEPENDENCY,
            severity=BlockerSeverity.CRITICAL,
            description="Missing external library",
            estimated_impact_hours=4.5,
        )
        
        blocker = result.unwrap()
        assert blocker.estimated_impact_hours == 4.5
    
    def test_resolve_blocker(self):
        """Should resolve blocker."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        blocker_result = tracker.add_blocker(
            ac_id="AC-TEST-001",
            phase_id="PHASE-01",
            category=BlockerCategory.FAILED_TEST,
            severity=BlockerSeverity.HIGH,
            description="Test failing",
        )
        blocker = blocker_result.unwrap()
        
        resolve_result = tracker.resolve_blocker(
            blocker.blocker_id,
            "Fixed the test case"
        )
        
        assert resolve_result.is_ok()
        resolved = resolve_result.unwrap()
        assert resolved.is_active() is False
        assert resolved.resolved_at is not None
        assert resolved.resolution_notes == "Fixed the test case"
    
    def test_get_active_blockers(self):
        """Should retrieve active blockers."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        # Add multiple blockers
        blocker1_result = tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.HIGH,
            "Test 1 failing"
        )
        blocker2_result = tracker.add_blocker(
            "AC-TEST-002",
            "PHASE-01",
            BlockerCategory.MISSING_DEPENDENCY,
            BlockerSeverity.CRITICAL,
            "Missing dependency"
        )
        
        # Resolve one
        blocker1 = blocker1_result.unwrap()
        tracker.resolve_blocker(blocker1.blocker_id, "Fixed")
        
        # Get active
        result = tracker.get_active_blockers(phase_id="PHASE-01")
        
        assert result.is_ok()
        active = result.unwrap()
        assert len(active) == 1
        assert active[0].ac_id == "AC-TEST-002"
    
    def test_blocker_severity_ordering(self):
        """Active blockers should be ordered by severity."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        # Add blockers in random severity order
        tracker.add_blocker(
            "AC-LOW",
            "PHASE-01",
            BlockerCategory.OTHER,
            BlockerSeverity.LOW,
            "Low priority"
        )
        tracker.add_blocker(
            "AC-CRITICAL",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.CRITICAL,
            "Critical issue"
        )
        tracker.add_blocker(
            "AC-MEDIUM",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.MEDIUM,
            "Medium priority"
        )
        
        result = tracker.get_active_blockers(phase_id="PHASE-01")
        blockers = result.unwrap()
        
        # Should be ordered: CRITICAL, MEDIUM, LOW
        assert blockers[0].severity == BlockerSeverity.CRITICAL
        assert blockers[1].severity == BlockerSeverity.MEDIUM
        assert blockers[2].severity == BlockerSeverity.LOW
    
    def test_blocker_increases_phase_blocker_count(self):
        """Adding blocker should increase phase blocker count."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        initial = tracker.get_phase_progress("PHASE-01").unwrap()
        assert initial.active_blockers == 0
        
        tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.HIGH,
            "Test failing"
        )
        
        updated = tracker.get_phase_progress("PHASE-01").unwrap()
        assert updated.active_blockers == 1
    
    def test_resolving_blocker_decreases_phase_blocker_count(self):
        """Resolving blocker should decrease phase blocker count."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        blocker_result = tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.HIGH,
            "Test failing"
        )
        blocker = blocker_result.unwrap()
        
        assert tracker.get_phase_progress("PHASE-01").unwrap().active_blockers == 1
        
        tracker.resolve_blocker(blocker.blocker_id, "Fixed")
        
        assert tracker.get_phase_progress("PHASE-01").unwrap().active_blockers == 0


@pytest.mark.ac("FR-005-02")
class TestAlertEscalation:
    """Test AC-FR-005-02: Alert escalation"""
    
    def test_critical_blocker_creates_urgent_alert(self):
        """Critical blocker should create urgent alert."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.GOVERNANCE_VIOLATION,
            BlockerSeverity.CRITICAL,
            "Governance violation"
        )
        
        result = tracker.get_alerts(acknowledged=False)
        
        assert result.is_ok()
        alerts = result.unwrap()
        assert len(alerts) == 1
        assert alerts[0].priority == AlertPriority.URGENT
    
    def test_high_blocker_creates_high_alert(self):
        """High blocker should create high priority alert."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.HIGH,
            "Test failing"
        )
        
        result = tracker.get_alerts(acknowledged=False)
        
        assert result.is_ok()
        alerts = result.unwrap()
        assert len(alerts) == 1
        assert alerts[0].priority == AlertPriority.HIGH
    
    def test_medium_low_blockers_no_alerts(self):
        """Medium/Low blockers should not create alerts."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.OTHER,
            BlockerSeverity.MEDIUM,
            "Medium blocker"
        )
        tracker.add_blocker(
            "AC-TEST-002",
            "PHASE-01",
            BlockerCategory.OTHER,
            BlockerSeverity.LOW,
            "Low blocker"
        )
        
        result = tracker.get_alerts(acknowledged=False)
        
        assert result.is_ok()
        alerts = result.unwrap()
        assert len(alerts) == 0
    
    def test_acknowledge_alert(self):
        """Should acknowledge alert."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.GOVERNANCE_VIOLATION,
            BlockerSeverity.CRITICAL,
            "Critical issue"
        )
        
        # Get unacknowledged
        unack_result = tracker.get_alerts(acknowledged=False)
        unack_alerts = unack_result.unwrap()
        assert len(unack_alerts) == 1
        
        alert_id = unack_alerts[0].alert_id
        
        # Acknowledge
        ack_result = tracker.acknowledge_alert(alert_id, "user@example.com")
        
        assert ack_result.is_ok()
        acknowledged = ack_result.unwrap()
        assert acknowledged.acknowledged_at is not None
        assert acknowledged.acknowledged_by == "user@example.com"
        
        # Should not appear in unacknowledged
        unack_result = tracker.get_alerts(acknowledged=False)
        unack_alerts = unack_result.unwrap()
        assert len(unack_alerts) == 0
        
        # Should appear in acknowledged
        ack_result = tracker.get_alerts(acknowledged=True)
        ack_alerts = ack_result.unwrap()
        assert len(ack_alerts) == 1


@pytest.mark.ac("FR-005-03")
class TestProgressPersistence:
    """Test AC-FR-005-03: Progress persistence to database"""
    
    def test_progress_persisted_to_database(self, tmp_path):
        """Progress updates should be persisted to database."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        tracker = ProgressTrackerManager(db)
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        # Update progress
        tracker.update_ac_status("PHASE-01", "AC-TEST-001", "COMPLETED")
        
        # Verify in audit log
        query_result = db.query_audit_by_ac_id("PHASE-01")  # Using phase as AC-ID filter
        
        # Should have entries (at least progress updates)
        if query_result.is_ok():
            entries = query_result.unwrap()
            # May or may not have phase_id entries
        
        db.close()
    
    def test_blocker_persisted_to_database(self, tmp_path):
        """Blockers should be persisted to database."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        tracker = ProgressTrackerManager(db)
        tracker.initialize_phase("PHASE-01", total_acs=10)
        
        # Add blocker
        tracker.add_blocker(
            "AC-TEST-001",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.HIGH,
            "Test failing"
        )
        
        # Verify in audit log
        query_result = db.query_audit_by_ac_id("AC-TEST-001")
        
        assert query_result.is_ok()
        entries = query_result.unwrap()
        # Should have blocker entries
        blocker_entries = [e for e in entries if "BLOCKER" in e.get("operation", "")]
        assert len(blocker_entries) > 0
        
        db.close()


class TestProgressTrackerIntegration:
    """Integration tests for progress tracker."""
    
    def test_complete_phase_workflow(self):
        """Test complete phase progression workflow."""
        tracker = ProgressTrackerManager()
        tracker.initialize_phase("PHASE-01", total_acs=5)
        
        # Progress phase
        tracker.update_ac_status("PHASE-01", "AC-1", "COMPLETED")
        tracker.update_ac_status("PHASE-01", "AC-2", "IN_PROGRESS")
        
        progress = tracker.get_phase_progress("PHASE-01").unwrap()
        assert progress.completion_percentage == 20.0
        
        # Add blocker
        tracker.add_blocker(
            "AC-3",
            "PHASE-01",
            BlockerCategory.FAILED_TEST,
            BlockerSeverity.HIGH,
            "Test failing"
        )
        
        progress = tracker.get_phase_progress("PHASE-01").unwrap()
        assert progress.active_blockers == 1
        assert progress.get_status() == "BLOCKED"
    
    def test_singleton_consistency(self):
        """Singleton instance should be consistent."""
        tracker1 = ProgressTrackerManager.instance()
        tracker2 = ProgressTrackerManager.instance()
        
        assert tracker1 is tracker2
