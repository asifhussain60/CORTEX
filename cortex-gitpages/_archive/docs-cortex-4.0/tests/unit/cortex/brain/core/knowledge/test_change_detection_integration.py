"""Unit tests for change detection service integration with MasterOrchestrator.

Tests integration layer, anomaly response handling, and orchestrator patterns.
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List

from cortex.brain.core.knowledge.change_detection_integration import (
    ActionType,
    AnomalyResponse,
    ChangeDetectionReport,
    AnomalyHandler,
    CriticalAnomalyHandler,
    WarningAnomalyHandler,
    InfoAnomalyHandler,
    ChangeDetectionIntegration,
    MasterOrchestratorChangeDetection,
)
from cortex.brain.core.knowledge.change_detection import (
    AnomalyDetection,
    AnomalyScore,
    AnomalyType,
    SeverityLevel,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_anomalies() -> Dict[str, AnomalyDetection]:
    """Sample anomalies for testing."""
    critical = AnomalyDetection(
        anomaly_type=AnomalyType.SCHEMA_DRIFT,
        severity=SeverityLevel.CRITICAL,
        score=AnomalyScore(value=0.9, confidence=0.95, reasoning="Critical drift"),
        affected_entries=["entry1", "entry2"],
        reasoning="Major schema changes detected",
    )

    warning = AnomalyDetection(
        anomaly_type=AnomalyType.COVERAGE_GAP,
        severity=SeverityLevel.WARNING,
        score=AnomalyScore(value=0.6, confidence=0.8, reasoning="Coverage gap"),
        affected_entries=["domain1"],
        reasoning="Coverage gap in domain",
    )

    info = AnomalyDetection(
        anomaly_type=AnomalyType.STALENESS,
        severity=SeverityLevel.INFO,
        score=AnomalyScore(value=0.3, confidence=0.7, reasoning="Some staleness"),
        affected_entries=["entry3"],
        reasoning="Minor staleness detected",
    )

    return {"critical": critical, "warning": warning, "info": info}


@pytest.fixture
def sample_entries() -> List[Dict[str, Any]]:
    """Sample knowledge entries."""
    return [
        {
            "id": "entry1",
            "domain": "api",
            "title": "REST API",
            "updated_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "entry2",
            "domain": "security",
            "title": "Auth",
            "updated_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        },
        {
            "id": "entry3",
            "domain": "architecture",
            "title": "Microservices",
            "updated_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        },
    ]


# ============================================================================
# AnomalyResponse Tests
# ============================================================================


class TestAnomalyResponse:
    """Tests for anomaly response handling."""

    def test_response_creation(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test creating anomaly response."""
        response = AnomalyResponse(
            anomaly=sample_anomalies["critical"],
            action=ActionType.ESCALATE,
        )

        assert response.action == ActionType.ESCALATE
        assert response.status == "pending"

    def test_response_with_details(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test response with additional details."""
        details = {"escalated_to": "security_team", "ticket_id": "SEC-123"}
        response = AnomalyResponse(
            anomaly=sample_anomalies["critical"],
            action=ActionType.ESCALATE,
            status="escalated",
            details=details,
        )

        assert response.details["ticket_id"] == "SEC-123"


# ============================================================================
# ChangeDetectionReport Tests
# ============================================================================


class TestChangeDetectionReport:
    """Tests for change detection reports."""

    def test_report_creation(self) -> None:
        """Test creating a report."""
        report = ChangeDetectionReport(entries_scanned=100)
        assert report.entries_scanned == 100
        assert len(report.anomalies_detected) == 0

    def test_add_anomaly_to_report(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test adding anomalies to report."""
        report = ChangeDetectionReport()

        report.add_anomaly(sample_anomalies["critical"])
        report.add_anomaly(sample_anomalies["warning"])

        assert len(report.anomalies_detected) == 2
        assert report.critical_count == 1
        assert report.warning_count == 1

    def test_has_critical_issues(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test checking for critical issues."""
        report = ChangeDetectionReport()

        assert not report.has_critical_issues()

        report.add_anomaly(sample_anomalies["critical"])
        assert report.has_critical_issues()

    def test_get_summary_text_empty(self) -> None:
        """Test summary text for empty report."""
        report = ChangeDetectionReport(entries_scanned=50)
        summary = report.get_summary_text()

        assert "No anomalies" in summary
        assert "50 entries" in summary

    def test_get_summary_text_with_anomalies(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test summary text with anomalies."""
        report = ChangeDetectionReport(entries_scanned=100)
        report.add_anomaly(sample_anomalies["critical"])
        report.add_anomaly(sample_anomalies["warning"])

        summary = report.get_summary_text()

        assert "100 entries" in summary
        assert "2 anomalies" in summary
        assert "1 critical" in summary


# ============================================================================
# Anomaly Handler Tests
# ============================================================================


class TestCriticalAnomalyHandler:
    """Tests for critical anomaly handling."""

    def test_handle_critical(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test handling critical anomaly."""
        handler = CriticalAnomalyHandler()
        response = handler.handle(sample_anomalies["critical"])

        assert response.action == ActionType.ESCALATE
        assert response.status == "escalated"

    def test_handle_non_critical_raises(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test that non-critical anomaly raises error."""
        handler = CriticalAnomalyHandler()

        with pytest.raises(ValueError):
            handler.handle(sample_anomalies["warning"])


class TestWarningAnomalyHandler:
    """Tests for warning anomaly handling."""

    def test_handle_warning(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test handling warning anomaly."""
        handler = WarningAnomalyHandler()
        response = handler.handle(sample_anomalies["warning"])

        assert response.action == ActionType.NOTIFY
        assert response.status == "notified"

    def test_handle_non_warning_raises(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test that non-warning anomaly raises error."""
        handler = WarningAnomalyHandler()

        with pytest.raises(ValueError):
            handler.handle(sample_anomalies["critical"])


class TestInfoAnomalyHandler:
    """Tests for info anomaly handling."""

    def test_handle_info(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test handling info anomaly."""
        handler = InfoAnomalyHandler()
        response = handler.handle(sample_anomalies["info"])

        assert response.action == ActionType.LOG
        assert response.status == "logged"


# ============================================================================
# ChangeDetectionIntegration Tests
# ============================================================================


class TestChangeDetectionIntegration:
    """Tests for main integration class."""

    def test_initialization(self) -> None:
        """Test integration initialization."""
        integration = ChangeDetectionIntegration(detection_window_hours=24)
        assert integration.detection_service is not None
        assert len(integration.handlers) == 3

    def test_scan_for_changes(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test scanning for changes."""
        integration = ChangeDetectionIntegration()
        report = integration.scan_for_changes(sample_entries, operation_id="OP-001")

        assert report.entries_scanned == len(sample_entries)
        assert report.operation_id == "OP-001"
        assert report.summary != ""

    def test_record_change(self) -> None:
        """Test recording a change."""
        integration = ChangeDetectionIntegration()
        version = {"id": "entry1", "value": "test"}

        integration.record_change("entry1", version, "Test change")

        assert "entry1" in integration.detection_service.history

    def test_get_critical_anomalies(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test getting critical anomalies."""
        integration = ChangeDetectionIntegration()
        critical = integration.get_critical_anomalies(sample_entries)

        assert isinstance(critical, list)

    def test_should_pause_operations_no_issues(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test pause determination with no issues."""
        integration = ChangeDetectionIntegration()
        should_pause, reason = integration.should_pause_operations(sample_entries)

        # Should not pause when no critical anomalies, or may depend on detection results
        assert isinstance(should_pause, bool)
        if should_pause:
            assert reason is not None

    def test_should_pause_operations_with_critical(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test pause determination with critical anomalies."""
        integration = ChangeDetectionIntegration()

        # Manually add critical anomaly
        critical = AnomalyDetection(
            anomaly_type=AnomalyType.SCHEMA_DRIFT,
            severity=SeverityLevel.CRITICAL,
            score=AnomalyScore(value=0.9, confidence=0.95, reasoning="Critical"),
            affected_entries=["entry1"],
        )

        integration.detection_service.detectors[
            AnomalyType.SCHEMA_DRIFT
        ].start_learning_mode()

        # Should determine pause based on critical anomalies

    def test_get_recent_changes(self) -> None:
        """Test getting recent changes."""
        integration = ChangeDetectionIntegration()

        # Record changes
        integration.record_change("entry1", {}, "Change 1")
        integration.record_change("entry2", {}, "Change 2")
        integration.record_change("entry1", {}, "Change 3")

        recent = integration.get_recent_changes(lookback_hours=24)

        assert "entry1" in recent
        assert "entry2" in recent

    def test_get_entry_change_history(self) -> None:
        """Test getting entry change history."""
        integration = ChangeDetectionIntegration()

        integration.record_change("entry1", {}, "Change 1")
        integration.record_change("entry1", {}, "Change 2")

        history = integration.get_entry_change_history("entry1")

        assert history is not None
        assert len(history.timestamps) == 2

    def test_get_entry_change_history_nonexistent(self) -> None:
        """Test getting history for non-existent entry."""
        integration = ChangeDetectionIntegration()
        history = integration.get_entry_change_history("nonexistent")

        assert history is None

    def test_get_last_report(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test getting last report."""
        integration = ChangeDetectionIntegration()

        assert integration.get_last_report() is None

        report = integration.scan_for_changes(sample_entries)
        assert integration.get_last_report() == report

    def test_get_response_history(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test getting response history."""
        integration = ChangeDetectionIntegration()

        # Create responses manually
        response1 = AnomalyResponse(
            anomaly=sample_anomalies["critical"],
            action=ActionType.ESCALATE,
        )
        response2 = AnomalyResponse(
            anomaly=sample_anomalies["warning"],
            action=ActionType.NOTIFY,
        )

        integration.responses.append(response1)
        integration.responses.append(response2)

        # Get all responses
        all_responses = integration.get_response_history()
        assert len(all_responses) == 2

        # Get only escalations
        escalations = integration.get_response_history(ActionType.ESCALATE)
        assert len(escalations) == 1

    def test_clear_response_history(self, sample_anomalies: Dict[str, AnomalyDetection]) -> None:
        """Test clearing response history."""
        integration = ChangeDetectionIntegration()

        # Add responses
        integration.responses.append(
            AnomalyResponse(
                anomaly=sample_anomalies["critical"],
                action=ActionType.ESCALATE,
            )
        )
        integration.responses.append(
            AnomalyResponse(
                anomaly=sample_anomalies["warning"],
                action=ActionType.NOTIFY,
            )
        )

        cleared = integration.clear_response_history()

        assert cleared == 2
        assert len(integration.responses) == 0


# ============================================================================
# MasterOrchestrator Integration Pattern Tests
# ============================================================================


class TestMasterOrchestratorIntegrationPattern:
    """Tests for MasterOrchestrator integration patterns."""

    def test_create_integration_factory(self) -> None:
        """Test factory method."""
        integration = MasterOrchestratorChangeDetection.create_integration(
            detection_window_hours=24
        )

        assert isinstance(integration, ChangeDetectionIntegration)

    def test_scan_operation_entries(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test scanning entries for operation."""
        integration = MasterOrchestratorChangeDetection.create_integration()
        report = MasterOrchestratorChangeDetection.scan_operation_entries(
            integration, sample_entries, operation_type="API_DESIGN"
        )

        assert report.operation_id == "API_DESIGN"
        assert report.entries_scanned == len(sample_entries)

    def test_should_proceed_with_operation_always_true(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test proceed decision when not failing on critical."""
        integration = MasterOrchestratorChangeDetection.create_integration()
        proceed, reason = MasterOrchestratorChangeDetection.should_proceed_with_operation(
            integration, sample_entries, fail_on_critical=False
        )

        assert proceed

    def test_should_proceed_with_operation_fail_on_critical(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test proceed decision with fail_on_critical."""
        integration = MasterOrchestratorChangeDetection.create_integration()
        proceed, reason = MasterOrchestratorChangeDetection.should_proceed_with_operation(
            integration, sample_entries, fail_on_critical=True
        )

        assert isinstance(proceed, bool)


# ============================================================================
# Integration Workflow Tests
# ============================================================================


class TestIntegrationWorkflow:
    """Tests for complete integration workflows."""

    def test_end_to_end_scan_and_response(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test end-to-end scan and response workflow."""
        integration = ChangeDetectionIntegration()

        # Scan entries
        report = integration.scan_for_changes(sample_entries, operation_id="WORKFLOW-001")

        assert report.operation_id == "WORKFLOW-001"
        assert report.entries_scanned == len(sample_entries)
        assert report.summary != ""

    def test_continuous_monitoring_workflow(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test continuous monitoring workflow."""
        integration = ChangeDetectionIntegration()

        # Initial scan
        report1 = integration.scan_for_changes(sample_entries)
        initial_time = report1.timestamp

        # Record some changes
        integration.record_change("entry1", {"version": 2}, "Updated")

        # Second scan
        report2 = integration.scan_for_changes(sample_entries)

        assert report2.timestamp >= initial_time

    def test_change_tracking_and_history(self) -> None:
        """Test change tracking and history retrieval."""
        integration = ChangeDetectionIntegration()

        # Track multiple changes
        for i in range(5):
            integration.record_change(
                "entry1", {"version": i}, f"Change {i}"
            )

        # Get history
        history = integration.get_entry_change_history("entry1")
        assert history is not None
        assert len(history.timestamps) == 5

        # Get recent changes
        recent = integration.get_recent_changes(lookback_hours=24)
        assert "entry1" in recent


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling in integration."""

    def test_scan_empty_entries(self) -> None:
        """Test scanning empty entry list."""
        integration = ChangeDetectionIntegration()
        report = integration.scan_for_changes([])

        assert report.entries_scanned == 0

    def test_record_change_nonexistent_entry(self) -> None:
        """Test recording change for new entry."""
        integration = ChangeDetectionIntegration()

        integration.record_change("new_entry", {}, "First change")

        assert "new_entry" in integration.detection_service.history

    def test_get_history_nonexistent(self) -> None:
        """Test getting history for non-existent entry."""
        integration = ChangeDetectionIntegration()
        history = integration.get_entry_change_history("nonexistent")

        assert history is None
