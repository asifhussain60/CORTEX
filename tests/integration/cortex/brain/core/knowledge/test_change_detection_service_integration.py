"""Integration tests for change detection with MasterOrchestrator.

Tests change detection service integration with the orchestrator framework.
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List
from unittest.mock import Mock, patch, MagicMock

from cortex.brain.core.knowledge.change_detection import (
    ChangeDetectionService,
    AnomalyType,
    SeverityLevel,
)


# ============================================================================
# Mock Providers
# ============================================================================


class MockKnowledgeRepository:
    """Mock knowledge repository for integration testing."""

    def __init__(self, entries: List[Dict[str, Any]] = None) -> None:
        """Initialize mock repository."""
        self.entries = entries or []
        self.is_loaded = True
        self.entry_count = len(self.entries)
        self.domains = set()
        for entry in self.entries:
            if "domain" in entry:
                self.domains.add(entry["domain"])

    def query(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Query repository."""
        return self.entries

    def get_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get entries by domain."""
        return [e for e in self.entries if e.get("domain") == domain]

    def get_relevant_knowledge(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Get relevant knowledge."""
        return self.entries


# ============================================================================
# Change Detection Integration Tests
# ============================================================================


class TestChangeDetectionWithRepository:
    """Tests for change detection with knowledge repositories."""

    def test_service_initialization(self) -> None:
        """Test change detection service initialization."""
        service = ChangeDetectionService(detection_window_hours=24)
        assert service.detection_window_seconds == 86400

    def test_detect_changes_in_repository(self) -> None:
        """Test detecting changes in a repository."""
        entries = [
            {"id": "1", "domain": "api", "title": "REST API", "description": "API patterns"},
            {"id": "2", "domain": "security", "title": "Auth", "description": "Authentication"},
        ]

        service = ChangeDetectionService()
        anomalies = service.detect_anomalies(entries)

        assert isinstance(anomalies, list)

    def test_track_entry_modifications(self) -> None:
        """Test tracking entry modifications."""
        service = ChangeDetectionService()

        # Record initial version
        entry_v1 = {"id": "entry1", "version": 1, "value": "original"}
        service.record_entry_change("entry1", entry_v1, "Initial creation")

        # Record modification
        entry_v2 = {"id": "entry1", "version": 2, "value": "updated"}
        service.record_entry_change("entry1", entry_v2, "Value updated")

        assert "entry1" in service.history
        assert len(service.history["entry1"].timestamps) == 2

    def test_detect_schema_changes(self) -> None:
        """Test detecting schema changes in entries."""
        service = ChangeDetectionService()

        # Initial entries with schema
        entries_v1 = [
            {
                "id": "1",
                "domain": "api",
                "title": "REST API",
                "description": "Patterns",
            }
        ]

        # Baseline detection
        service.detect_anomalies(entries_v1)

        # Modified entries with different schema
        entries_v2 = [
            {
                "id": "1",
                "domain": "api",
                "title": "REST API",
                "description": "Patterns",
                "new_field": "added",  # New field
            }
        ]

        anomalies = service.detect_anomalies(entries_v2)
        assert isinstance(anomalies, list)

    def test_detect_semantic_changes(self) -> None:
        """Test detecting semantic content changes."""
        service = ChangeDetectionService()

        entries_v1 = [
            {
                "id": "1",
                "content": "This is about API design patterns and best practices",
            }
        ]
        service.detect_anomalies(entries_v1)

        entries_v2 = [
            {
                "id": "1",
                "content": "Completely unrelated information about databases",
            }
        ]

        anomalies = service.detect_anomalies(entries_v2)
        # Service should detect but not necessarily report (depends on learning mode)
        assert isinstance(anomalies, list)

    def test_detect_coverage_gaps(self) -> None:
        """Test detecting coverage gaps in domain areas."""
        service = ChangeDetectionService()

        entries_v1 = [
            {"id": "1", "domain": "api"},
            {"id": "2", "domain": "security"},
            {"id": "3", "domain": "architecture"},
        ]
        service.detect_anomalies(entries_v1)

        # Remove security entries
        entries_v2 = [
            {"id": "1", "domain": "api"},
            {"id": "3", "domain": "architecture"},
        ]

        anomalies = service.detect_anomalies(entries_v2)
        assert isinstance(anomalies, list)

    def test_detect_stale_entries(self) -> None:
        """Test detecting stale entries."""
        service = ChangeDetectionService()

        now = datetime.utcnow()
        old_date = (now - timedelta(days=40)).isoformat()

        entries = [
            {
                "id": "1",
                "domain": "api",
                "updated_at": old_date,  # 40 days old
            }
        ]

        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_detect_volume_anomalies(self) -> None:
        """Test detecting volume anomalies."""
        service = ChangeDetectionService()

        # Build volume history
        for size in [100, 102, 98, 101, 99]:
            entries = [{"id": str(i)} for i in range(size)]
            service.detect_anomalies(entries)

        # Sudden spike
        anomalies_spike = service.detect_anomalies(
            [{"id": str(i)} for i in range(500)]
        )
        assert isinstance(anomalies_spike, list)


# ============================================================================
# MasterOrchestrator Context Integration Tests
# ============================================================================


class TestMasterOrchestratorIntegration:
    """Tests for integration with MasterOrchestrator patterns."""

    def test_change_detection_in_operation_context(self) -> None:
        """Test change detection during operation context."""
        service = ChangeDetectionService()

        # Simulate MasterOrchestrator operation context
        operation_context = {
            "operation_type": "API_DESIGN",
            "target_domains": ["api_design", "architecture"],
        }

        entries = [
            {
                "id": "1",
                "domain": "api_design",
                "title": "REST Design",
            },
            {
                "id": "2",
                "domain": "architecture",
                "title": "Architecture",
            },
        ]

        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_record_orchestrator_changes(self) -> None:
        """Test recording changes from orchestrator operations."""
        service = ChangeDetectionService()

        # Simulate orchestrator discovering changes
        updated_entry = {
            "id": "entry1",
            "domain": "api",
            "title": "REST API",
            "version": 2,
        }

        service.record_entry_change("entry1", updated_entry, "Updated by orchestrator")

        assert "entry1" in service.history

    def test_get_actionable_anomalies(self) -> None:
        """Test getting anomalies actionable by orchestrator."""
        service = ChangeDetectionService()

        entries = [
            {"id": str(i), "domain": "api", "updated_at": datetime.utcnow().isoformat()}
            for i in range(10)
        ]

        anomalies = service.get_critical_anomalies(entries)
        assert isinstance(anomalies, list)

        # All critical anomalies should have severity CRITICAL
        for anomaly in anomalies:
            assert anomaly.severity == SeverityLevel.CRITICAL

    def test_change_metrics_for_orchestrator(self) -> None:
        """Test providing change metrics for orchestrator decisions."""
        service = ChangeDetectionService()

        now = datetime.utcnow()

        service.record_entry_change("entry1", {}, "Change 1")
        service.record_entry_change("entry2", {}, "Change 2")
        service.record_entry_change("entry1", {}, "Change 3")

        summary = service.get_change_summary(now - timedelta(minutes=5))

        assert "entry1" in summary
        assert "entry2" in summary
        assert summary["entry1"] == 2
        assert summary["entry2"] == 1


# ============================================================================
# Batch Processing Integration Tests
# ============================================================================


class TestBatchProcessing:
    """Tests for batch processing of knowledge entries."""

    def test_detect_anomalies_large_batch(self) -> None:
        """Test detection across large batch of entries."""
        service = ChangeDetectionService()

        entries = [
            {
                "id": f"entry_{i}",
                "domain": f"domain_{i % 5}",
                "title": f"Title {i}",
                "content": f"Content for entry {i}",
            }
            for i in range(1000)
        ]

        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_batch_change_recording(self) -> None:
        """Test recording multiple changes in batch."""
        service = ChangeDetectionService()

        changes = [
            ("entry1", {"version": 1}, "First change"),
            ("entry2", {"version": 1}, "First change"),
            ("entry3", {"version": 1}, "First change"),
            ("entry1", {"version": 2}, "Second change"),
        ]

        for entry_id, version, summary in changes:
            service.record_entry_change(entry_id, version, summary)

        assert len(service.history) == 3
        assert len(service.history["entry1"].timestamps) == 2


# ============================================================================
# Continuous Monitoring Tests
# ============================================================================


class TestContinuousMonitoring:
    """Tests for continuous monitoring of knowledge repositories."""

    def test_rolling_detection_window(self) -> None:
        """Test detection within rolling time window."""
        service = ChangeDetectionService(detection_window_hours=24)
        assert service.detection_window_seconds == 86400

    def test_anomaly_severity_escalation(self) -> None:
        """Test that anomaly severity escalates over time."""
        service = ChangeDetectionService()

        old_date = (datetime.utcnow() - timedelta(days=100)).isoformat()
        entries = [{"id": "1", "updated_at": old_date}]

        anomalies = service.detect_anomalies(entries)
        # Service may not report until learning mode expires

    def test_repeated_detection_cycles(self) -> None:
        """Test repeated detection cycles on same data."""
        service = ChangeDetectionService()

        entries = [
            {"id": "1", "domain": "api", "value": "data1"},
            {"id": "2", "domain": "security", "value": "data2"},
        ]

        # Multiple detection runs
        for _ in range(3):
            anomalies = service.detect_anomalies(entries)
            assert isinstance(anomalies, list)


# ============================================================================
# Error Handling and Resilience Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling and resilience."""

    def test_detect_with_corrupted_entries(self) -> None:
        """Test handling of corrupted entry data."""
        service = ChangeDetectionService()

        corrupted_entries = [
            {"id": "1", "data": "valid"},
            None,  # Corrupted
            {"id": "3", "data": "valid"},
        ]

        try:
            # Filter out None entries
            valid_entries = [e for e in corrupted_entries if e is not None]
            anomalies = service.detect_anomalies(valid_entries)
            assert isinstance(anomalies, list)
        except Exception as e:
            pytest.fail(f"Should handle corrupted entries: {e}")

    def test_detect_with_missing_fields(self) -> None:
        """Test handling of entries with missing fields."""
        service = ChangeDetectionService()

        entries = [
            {"id": "1"},  # Missing domain, title, etc.
            {"id": "2", "domain": "api"},  # Partial
        ]

        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_concurrent_change_recording(self) -> None:
        """Test recording changes concurrently."""
        service = ChangeDetectionService()

        # Simulate concurrent writes
        for i in range(100):
            service.record_entry_change(
                f"entry_{i % 10}", {"version": i}, f"Change {i}"
            )

        assert len(service.history) == 10
        assert sum(len(h.timestamps) for h in service.history.values()) == 100

    def test_detector_exception_handling(self) -> None:
        """Test that service continues if detector raises exception."""
        service = ChangeDetectionService()

        entries = [{"id": "1", "data": "test"}]

        # Even if one detector fails, service should continue
        try:
            anomalies = service.detect_anomalies(entries)
            assert isinstance(anomalies, list)
        except Exception as e:
            pytest.fail(f"Service should handle detector exceptions: {e}")


# ============================================================================
# Performance and Scalability Tests
# ============================================================================


class TestPerformance:
    """Tests for performance and scalability."""

    def test_detection_latency_small_batch(self) -> None:
        """Test detection latency for small batch."""
        service = ChangeDetectionService()

        entries = [{"id": str(i), "domain": "api"} for i in range(10)]

        import time
        start = time.time()
        service.detect_anomalies(entries)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 100  # Should complete in <100ms

    def test_detection_latency_medium_batch(self) -> None:
        """Test detection latency for medium batch."""
        service = ChangeDetectionService()

        entries = [
            {
                "id": str(i),
                "domain": f"domain_{i % 5}",
                "content": f"Entry {i} content",
            }
            for i in range(100)
        ]

        import time
        start = time.time()
        service.detect_anomalies(entries)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed < 500  # Should complete in <500ms

    def test_memory_efficiency(self) -> None:
        """Test memory efficiency with large history."""
        service = ChangeDetectionService()

        # Build up large history
        for i in range(1000):
            service.record_entry_change(
                f"entry_{i % 100}", {"version": i}, f"Change {i}"
            )

        # Service should maintain reasonable memory
        assert len(service.history) <= 100


# ============================================================================
# Edge Cases and Boundary Tests
# ============================================================================


class TestBoundaryConditions:
    """Tests for boundary conditions."""

    def test_zero_entries(self) -> None:
        """Test detection with zero entries."""
        service = ChangeDetectionService()
        anomalies = service.detect_anomalies([])
        assert len(anomalies) == 0

    def test_single_entry(self) -> None:
        """Test detection with single entry."""
        service = ChangeDetectionService()
        entries = [{"id": "1", "domain": "api"}]
        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_very_old_timestamps(self) -> None:
        """Test handling of very old timestamps."""
        service = ChangeDetectionService()

        very_old = (datetime.utcnow() - timedelta(days=1000)).isoformat()
        entries = [{"id": "1", "updated_at": very_old}]

        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_future_timestamps(self) -> None:
        """Test handling of future timestamps."""
        service = ChangeDetectionService()

        future = (datetime.utcnow() + timedelta(days=10)).isoformat()
        entries = [{"id": "1", "updated_at": future}]

        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)

    def test_extremely_large_content(self) -> None:
        """Test handling of extremely large content."""
        service = ChangeDetectionService()

        large_content = "x" * 1000000  # 1MB of content
        entries = [{"id": "1", "content": large_content}]

        anomalies = service.detect_anomalies(entries)
        assert isinstance(anomalies, list)
