"""Change detection service integration with MasterOrchestrator.

This module provides seamless integration of the change detection service
with the MasterOrchestrator framework, enabling automatic anomaly detection
and reporting during operation coordination.

CORE Governance:
- CORE-004: Tier structure (Tier1 service, uses Tier0 protocols)
- CORE-011: Type hints (100% coverage with mypy --strict)
- CORE-012: Documentation (100% docstrings)
- CORE-013: Specific exceptions
- CORE-028: Portable paths

Integration Points:
- ChangeDetectionService: Core anomaly detection
- MasterOrchestrator: Operation coordination
- AuditTrail: Logging of detected changes
- Governance: Registry of anomaly rules
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from cortex.brain.core.knowledge.change_detection import (
    AnomalyDetection,
    AnomalyType,
    ChangeDetectionService,
    ChangeHistory,
    SeverityLevel,
)
from cortex.models.canonical_enums import ActionType

logger = logging.getLogger(__name__)




@dataclass
class AnomalyResponse:
    """Response action for a detected anomaly.

    Attributes:
        anomaly: The original anomaly detection.
        action: Action type to take.
        timestamp: When action was taken.
        status: Status of action execution.
        details: Additional details about action.
    """

    anomaly: AnomalyDetection
    action: ActionType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChangeDetectionReport:
    """Comprehensive report of change detection results.

    Attributes:
        timestamp: When detection was run.
        operation_id: Associated operation identifier.
        entries_scanned: Number of entries scanned.
        anomalies_detected: List of detected anomalies.
        critical_count: Number of critical anomalies.
        warning_count: Number of warning anomalies.
        changes_recorded: Number of changes recorded.
        summary: Text summary of findings.
    """

    timestamp: datetime = field(default_factory=datetime.utcnow)
    operation_id: Optional[str] = None
    entries_scanned: int = 0
    anomalies_detected: List[AnomalyDetection] = field(default_factory=list)
    critical_count: int = 0
    warning_count: int = 0
    changes_recorded: int = 0
    summary: str = ""

    def add_anomaly(self, anomaly: AnomalyDetection) -> None:
        """Add an anomaly to the report.

        Args:
            anomaly: Anomaly to add.
        """
        self.anomalies_detected.append(anomaly)
        if anomaly.severity == SeverityLevel.CRITICAL:
            self.critical_count += 1
        elif anomaly.severity == SeverityLevel.WARNING:
            self.warning_count += 1

    def has_critical_issues(self) -> bool:
        """Check if report contains critical issues.

        Returns:
            True if critical anomalies exist.
        """
        return self.critical_count > 0

    def get_summary_text(self) -> str:
        """Generate summary text for report.

        Returns:
            Human-readable summary.
        """
        if not self.anomalies_detected:
            return f"No anomalies detected. Scanned {self.entries_scanned} entries."

        return (
            f"Detection Report: {self.entries_scanned} entries scanned, "
            f"{len(self.anomalies_detected)} anomalies detected "
            f"({self.critical_count} critical, {self.warning_count} warnings)"
        )


class AnomalyHandler(ABC):
    """Base class for handling detected anomalies."""

    @abstractmethod
    def handle(self, anomaly: AnomalyDetection) -> AnomalyResponse:
        """Handle a detected anomaly.

        Args:
            anomaly: The anomaly to handle.

        Returns:
            Response indicating action taken.
        """


class CriticalAnomalyHandler(AnomalyHandler):
    """Handler for critical-severity anomalies."""

    def handle(self, anomaly: AnomalyDetection) -> AnomalyResponse:
        """Handle critical anomaly with escalation.

        Args:
            anomaly: The critical anomaly.

        Returns:
            Response with escalation action.
        """
        if anomaly.severity != SeverityLevel.CRITICAL:
            raise ValueError("Handler only processes CRITICAL anomalies")

        return AnomalyResponse(
            anomaly=anomaly,
            action=ActionType.ESCALATE,
            status="escalated",
            details={
                "escalation_reason": "Critical anomaly detected",
                "anomaly_type": anomaly.anomaly_type.value,
                "affected_entries": len(anomaly.affected_entries),
            },
        )


class WarningAnomalyHandler(AnomalyHandler):
    """Handler for warning-severity anomalies."""

    def handle(self, anomaly: AnomalyDetection) -> AnomalyResponse:
        """Handle warning anomaly with notification.

        Args:
            anomaly: The warning anomaly.

        Returns:
            Response with notification action.
        """
        if anomaly.severity != SeverityLevel.WARNING:
            raise ValueError("Handler only processes WARNING anomalies")

        return AnomalyResponse(
            anomaly=anomaly,
            action=ActionType.NOTIFY,
            status="notified",
            details={
                "notification_sent_to": "governance_registry",
                "anomaly_type": anomaly.anomaly_type.value,
            },
        )


class InfoAnomalyHandler(AnomalyHandler):
    """Handler for info-level anomalies."""

    def handle(self, anomaly: AnomalyDetection) -> AnomalyResponse:
        """Handle info anomaly with logging.

        Args:
            anomaly: The info anomaly.

        Returns:
            Response with log action.
        """
        if anomaly.severity != SeverityLevel.INFO:
            raise ValueError("Handler only processes INFO anomalies")

        return AnomalyResponse(
            anomaly=anomaly,
            action=ActionType.LOG,
            status="logged",
            details={"audit_trail_entry_id": f"change_det_{datetime.utcnow().timestamp()}"},
        )


class ChangeDetectionIntegration:
    """Integration layer between change detection and MasterOrchestrator.

    Orchestrates anomaly detection, response handling, and reporting.
    """

    def __init__(self, detection_window_hours: int = 24) -> None:
        """Initialize integration layer.

        Args:
            detection_window_hours: Detection window in hours.
        """
        self.detection_service = ChangeDetectionService(
            detection_window_hours=detection_window_hours
        )
        self.handlers: Dict[SeverityLevel, AnomalyHandler] = {
            SeverityLevel.CRITICAL: CriticalAnomalyHandler(),
            SeverityLevel.WARNING: WarningAnomalyHandler(),
            SeverityLevel.INFO: InfoAnomalyHandler(),
        }
        self.responses: List[AnomalyResponse] = []
        self.last_report: Optional[ChangeDetectionReport] = None

    def scan_for_changes(
        self,
        entries: List[Dict[str, Any]],
        operation_id: Optional[str] = None,
    ) -> ChangeDetectionReport:
        """Scan entries for changes and generate report.

        Args:
            entries: Entries to scan.
            operation_id: Associated operation identifier.

        Returns:
            Comprehensive change detection report.
        """
        report = ChangeDetectionReport(
            operation_id=operation_id,
            entries_scanned=len(entries),
        )

        # Detect anomalies
        anomalies = self.detection_service.detect_anomalies(entries)

        for anomaly in anomalies:
            report.add_anomaly(anomaly)

            # Handle each anomaly
            handler = self.handlers.get(anomaly.severity)
            if handler:
                response = handler.handle(anomaly)
                self.responses.append(response)

        report.summary = report.get_summary_text()
        self.last_report = report

        logger.info(f"Change detection scan complete: {report.summary}")

        return report

    def record_change(
        self,
        entry_id: str,
        version: Dict[str, Any],
        change_summary: str,
    ) -> None:
        """Record an entry change.

        Args:
            entry_id: Unique entry identifier.
            version: Current version of entry.
            change_summary: Description of change.
        """
        self.detection_service.record_entry_change(entry_id, version, change_summary)

    def get_critical_anomalies(
        self, entries: List[Dict[str, Any]]
    ) -> List[AnomalyDetection]:
        """Get only critical anomalies.

        Args:
            entries: Entries to scan.

        Returns:
            List of critical anomalies.
        """
        return self.detection_service.get_critical_anomalies(entries)

    def should_pause_operations(
        self, entries: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """Determine if operations should be paused due to anomalies.

        Args:
            entries: Entries to scan.

        Returns:
            Tuple of (should_pause, reason).
        """
        critical = self.get_critical_anomalies(entries)

        if not critical:
            return False, None

        # Critical anomalies found - pause operations
        reason = f"{len(critical)} critical anomalies detected requiring review"
        logger.warning(f"Pausing operations: {reason}")

        return True, reason

    def get_recent_changes(
        self, lookback_hours: int = 24
    ) -> Dict[str, List[Tuple[datetime, str]]]:
        """Get recent changes within lookback window.

        Args:
            lookback_hours: Hours to look back in history.

        Returns:
            Dictionary of entry_id -> list of (timestamp, change_summary) tuples.
        """
        since = datetime.utcnow() - timedelta(hours=lookback_hours)
        recent_changes: Dict[str, List[Tuple[datetime, str]]] = {}

        for entry_id, history in self.detection_service.history.items():
            changes = history.get_changes_since(since)
            if changes:
                recent_changes[entry_id] = changes

        return recent_changes

    def get_entry_change_history(self, entry_id: str) -> Optional[ChangeHistory]:
        """Get complete change history for an entry.

        Args:
            entry_id: Unique entry identifier.

        Returns:
            ChangeHistory object or None if entry not in history.
        """
        return self.detection_service.history.get(entry_id)

    def get_last_report(self) -> Optional[ChangeDetectionReport]:
        """Get the most recent detection report.

        Returns:
            Last ChangeDetectionReport or None.
        """
        return self.last_report

    def get_response_history(
        self, action_type: Optional[ActionType] = None
    ) -> List[AnomalyResponse]:
        """Get history of anomaly responses.

        Args:
            action_type: Filter by action type (optional).

        Returns:
            List of responses, optionally filtered.
        """
        if action_type is None:
            return self.responses

        return [r for r in self.responses if r.action == action_type]

    def clear_response_history(self) -> int:
        """Clear response history and return count cleared.

        Returns:
            Number of responses cleared.
        """
        count = len(self.responses)
        self.responses.clear()
        return count


class MasterOrchestratorChangeDetection:
    """Integration pattern for MasterOrchestrator usage.

    Provides recommended integration methods for orchestrator operations.
    """

    @staticmethod
    def create_integration(detection_window_hours: int = 24) -> ChangeDetectionIntegration:
        """Factory method to create integration instance.

        Args:
            detection_window_hours: Detection window in hours.

        Returns:
            Configured ChangeDetectionIntegration instance.
        """
        return ChangeDetectionIntegration(detection_window_hours=detection_window_hours)

    @staticmethod
    def scan_operation_entries(
        integration: ChangeDetectionIntegration,
        entries: List[Dict[str, Any]],
        operation_type: str,
    ) -> ChangeDetectionReport:
        """Scan entries for a specific operation type.

        Args:
            integration: The integration instance.
            entries: Entries to scan.
            operation_type: Type of operation being performed.

        Returns:
            Change detection report.
        """
        report = integration.scan_for_changes(entries, operation_id=operation_type)
        return report

    @staticmethod
    def should_proceed_with_operation(
        integration: ChangeDetectionIntegration,
        entries: List[Dict[str, Any]],
        fail_on_critical: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """Determine if operation should proceed based on anomalies.

        Args:
            integration: The integration instance.
            entries: Entries to check.
            fail_on_critical: If True, fail on critical anomalies.

        Returns:
            Tuple of (should_proceed, reason_if_not).
        """
        if not fail_on_critical:
            return True, None

        should_pause, reason = integration.should_pause_operations(entries)
        if should_pause:
            return False, reason

        return True, None
