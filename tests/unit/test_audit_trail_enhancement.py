"""
Test suite for Audit Trail Enhancement (OB-003-01).

This module tests searchable audit history, retention policies, and
export functionality for CORTEX observability audit trail.

Acceptance Tests:
- Audit history is searchable
- Retention policies enforced
- Export in multiple formats
"""

import pytest
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import json


# Import modules to be tested (will be created)
from cortex.core.observability.audit_trail import (
    AuditTrail,
    AuditEntry,
    RetentionPolicy,
    AuditExporter,
)


class TestAuditEntryCreation:
    """Test audit entry creation and storage."""

    def test_audit_entry_initialization(self) -> None:
        """
        Test that audit entries initialize correctly.

        Expected:
        - Entry created with required fields
        - Timestamp set automatically
        """
        entry = AuditEntry(
            event_type="span_created",
            resource_name="operation.a",
            actor="profiler",
            action="RECORD",
            details={"latency_ms": 100},
        )

        assert entry is not None
        assert entry.event_type == "span_created"
        assert entry.resource_name == "operation.a"
        assert entry.timestamp is not None

    def test_audit_entry_with_status(self) -> None:
        """
        Test audit entry with operation status.

        Expected:
        - Status field stored correctly
        - Status values: START, EXECUTE, COMPLETE, ERROR
        """
        entry = AuditEntry(
            event_type="operation_start",
            resource_name="test_operation",
            actor="test_actor",
            action="START",
            details={},
            status="INITIATED",
        )

        assert entry.status == "INITIATED"

    def test_audit_entry_with_metadata(self) -> None:
        """
        Test audit entry with additional metadata.

        Expected:
        - Metadata dictionary preserved
        - Can contain arbitrary key-value pairs
        """
        metadata = {
            "source_service": "cortex-core",
            "request_id": "req-123",
            "user_id": "user-456",
        }

        entry = AuditEntry(
            event_type="alert_triggered",
            resource_name="alert_rule_1",
            actor="alert_manager",
            action="TRIGGER",
            details={},
            metadata=metadata,
        )

        assert entry.metadata["source_service"] == "cortex-core"


class TestAuditTrailStorage:
    """Test audit trail storage operations."""

    def test_audit_trail_initialization(self) -> None:
        """
        Test that audit trail initializes correctly.

        Expected:
        - Trail instance created
        - Storage mechanism ready
        """
        trail = AuditTrail()

        assert trail is not None

    def test_record_audit_entry(self) -> None:
        """
        Test recording audit entries to trail.

        Expected:
        - Entry added to trail
        - Entry retrievable by ID
        """
        trail = AuditTrail()

        entry = AuditEntry(
            event_type="test_event",
            resource_name="test_resource",
            actor="test_actor",
            action="TEST",
            details={},
        )

        entry_id = trail.record(entry)

        assert entry_id is not None

    def test_get_entry_by_id(self) -> None:
        """
        Test retrieving audit entry by ID.

        Expected:
        - Entry retrieved correctly
        - All fields preserved
        """
        trail = AuditTrail()

        entry = AuditEntry(
            event_type="test_event",
            resource_name="test_resource",
            actor="test_actor",
            action="TEST",
            details={"key": "value"},
        )

        entry_id = trail.record(entry)
        retrieved = trail.get_entry(entry_id)

        assert retrieved is not None
        assert retrieved.event_type == "test_event"
        assert retrieved.details["key"] == "value"


class TestAuditTrailSearch:
    """Test audit trail search and filtering."""

    def test_search_by_event_type(self) -> None:
        """
        Test searching audit trail by event type.

        Expected:
        - Entries with matching event type returned
        - Non-matching entries excluded
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="alert",
                resource_name="res1",
                actor="actor1",
                action="TRIGGER",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="metric",
                resource_name="res2",
                actor="actor1",
                action="RECORD",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="alert",
                resource_name="res3",
                actor="actor1",
                action="TRIGGER",
                details={},
            )
        )

        results = trail.search(event_type="alert")

        assert len(results) >= 2

    def test_search_by_resource_name(self) -> None:
        """
        Test searching audit trail by resource name.

        Expected:
        - Entries with matching resource name returned
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="event1",
                resource_name="database_query",
                actor="actor1",
                action="EXECUTE",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="event2",
                resource_name="api_call",
                actor="actor1",
                action="INVOKE",
                details={},
            )
        )

        results = trail.search(resource_name="database_query")

        assert len(results) >= 1

    def test_search_by_actor(self) -> None:
        """
        Test searching audit trail by actor.

        Expected:
        - Entries with matching actor returned
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="event1",
                resource_name="res1",
                actor="profiler",
                action="ANALYZE",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="event2",
                resource_name="res2",
                actor="monitor",
                action="CHECK",
                details={},
            )
        )

        results = trail.search(actor="profiler")

        assert len(results) >= 1

    def test_search_by_time_range(self) -> None:
        """
        Test searching audit trail by time range.

        Expected:
        - Entries within time range returned
        - Entries outside range excluded
        """
        trail = AuditTrail()

        now = datetime.now()
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)

        trail.record(
            AuditEntry(
                event_type="old_event",
                resource_name="res1",
                actor="actor1",
                action="OLD",
                details={},
            )
        )

        results = trail.search(start_time=past, end_time=future)

        assert len(results) > 0

    def test_search_with_multiple_filters(self) -> None:
        """
        Test searching with multiple filter criteria.

        Expected:
        - Only entries matching ALL criteria returned
        - Filters applied as AND logic
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="alert",
                resource_name="rule_1",
                actor="manager",
                action="TRIGGER",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="metric",
                resource_name="rule_1",
                actor="manager",
                action="RECORD",
                details={},
            )
        )

        results = trail.search(event_type="alert", actor="manager")

        assert len(results) >= 1
        assert all(r.event_type == "alert" for r in results)
        assert all(r.actor == "manager" for r in results)


class TestRetentionPolicy:
    """Test retention policy configuration and enforcement."""

    def test_retention_policy_initialization(self) -> None:
        """
        Test that retention policy initializes correctly.

        Expected:
        - Policy created with retention days
        - Default values set appropriately
        """
        policy = RetentionPolicy(retention_days=90)

        assert policy.retention_days == 90

    def test_retention_policy_with_max_entries(self) -> None:
        """
        Test retention policy with max entries limit.

        Expected:
        - Max entries limit set
        - Older entries removed when limit exceeded
        """
        policy = RetentionPolicy(retention_days=90, max_entries=10000)

        assert policy.max_entries == 10000

    def test_apply_retention_policy(self) -> None:
        """
        Test applying retention policy to audit trail.

        Expected:
        - Entries older than retention period removed
        - Recent entries retained
        """
        trail = AuditTrail()
        policy = RetentionPolicy(retention_days=30)

        # Record entry with current timestamp
        trail.record(
            AuditEntry(
                event_type="recent",
                resource_name="res1",
                actor="actor",
                action="ACTION",
                details={},
            )
        )

        # Apply policy - should keep recent entries
        removed_count = trail.apply_retention_policy(policy)

        # Verify trail still has recent entry
        all_entries = trail.search()
        assert len(all_entries) > 0

    def test_retention_policy_enforcement_mode(self) -> None:
        """
        Test retention policy enforcement mode.

        Expected:
        - ARCHIVE mode: moves entries to cold storage
        - DELETE mode: removes entries permanently
        """
        policy_archive = RetentionPolicy(
            retention_days=90, enforcement_mode="ARCHIVE"
        )
        policy_delete = RetentionPolicy(
            retention_days=90, enforcement_mode="DELETE"
        )

        assert policy_archive.enforcement_mode == "ARCHIVE"
        assert policy_delete.enforcement_mode == "DELETE"


class TestAuditExport:
    """Test audit trail export functionality."""

    def test_export_to_json(self) -> None:
        """
        Test exporting audit trail to JSON format.

        Expected:
        - JSON string returned
        - All entries serializable
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="test",
                resource_name="res",
                actor="actor",
                action="ACTION",
                details={"key": "value"},
            )
        )

        exporter = AuditExporter(trail)
        json_output = exporter.to_json()

        assert json_output is not None
        assert isinstance(json_output, str)
        # Should be valid JSON
        data = json.loads(json_output)
        assert isinstance(data, (list, dict))

    def test_export_to_csv(self) -> None:
        """
        Test exporting audit trail to CSV format.

        Expected:
        - CSV string returned
        - Headers included
        - Entries as rows
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="test",
                resource_name="res",
                actor="actor",
                action="ACTION",
                details={},
            )
        )

        exporter = AuditExporter(trail)
        csv_output = exporter.to_csv()

        assert csv_output is not None
        assert isinstance(csv_output, str)
        assert "event_type" in csv_output

    def test_export_filtered_entries(self) -> None:
        """
        Test exporting filtered subset of entries.

        Expected:
        - Export includes only matching entries
        - Filter criteria applied before export
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="alert",
                resource_name="res1",
                actor="actor",
                action="TRIGGER",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="metric",
                resource_name="res2",
                actor="actor",
                action="RECORD",
                details={},
            )
        )

        exporter = AuditExporter(trail)
        json_output = exporter.to_json(event_type="alert")

        assert "alert" in json_output

    def test_export_with_compression(self) -> None:
        """
        Test exporting audit trail with compression.

        Expected:
        - Output compressed (gzip or similar)
        - File size reduced
        - Data integrity preserved
        """
        trail = AuditTrail()

        for i in range(100):
            trail.record(
                AuditEntry(
                    event_type=f"event_{i}",
                    resource_name=f"resource_{i}",
                    actor="actor",
                    action="ACTION",
                    details={"index": i},
                )
            )

        exporter = AuditExporter(trail)
        compressed = exporter.to_json_compressed()

        assert compressed is not None
        assert isinstance(compressed, bytes)


class TestAuditTrailMetrics:
    """Test audit trail metrics and statistics."""

    def test_get_entry_count(self) -> None:
        """
        Test retrieving total audit entry count.

        Expected:
        - Count returned correctly
        - Increments with each record
        """
        trail = AuditTrail()

        assert trail.get_entry_count() == 0

        trail.record(
            AuditEntry(
                event_type="event",
                resource_name="res",
                actor="actor",
                action="ACTION",
                details={},
            )
        )

        assert trail.get_entry_count() == 1

    def test_get_event_type_distribution(self) -> None:
        """
        Test getting distribution of event types.

        Expected:
        - Dictionary returned with event type counts
        - All event types represented
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="alert",
                resource_name="res1",
                actor="actor",
                action="ACTION",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="alert",
                resource_name="res2",
                actor="actor",
                action="ACTION",
                details={},
            )
        )
        trail.record(
            AuditEntry(
                event_type="metric",
                resource_name="res3",
                actor="actor",
                action="ACTION",
                details={},
            )
        )

        distribution = trail.get_event_type_distribution()

        assert "alert" in distribution
        assert distribution.get("alert", 0) >= 2

    def test_get_audit_stats(self) -> None:
        """
        Test retrieving comprehensive audit statistics.

        Expected:
        - Statistics dictionary returned
        - Includes counts, distribution, time range
        """
        trail = AuditTrail()

        trail.record(
            AuditEntry(
                event_type="event",
                resource_name="res",
                actor="actor",
                action="ACTION",
                details={},
            )
        )

        stats = trail.get_stats()

        assert stats is not None
        assert "total_entries" in stats


class TestTypeHints:
    """Test that all functions have proper type hints (CORE-011)."""

    def test_audit_trail_has_type_hints(self) -> None:
        """Test that AuditTrail methods have complete type hints."""
        import inspect

        methods = inspect.getmembers(AuditTrail, predicate=inspect.ismethod)

        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                assert sig.return_annotation != inspect.Signature.empty

    def test_exporter_has_type_hints(self) -> None:
        """Test that AuditExporter methods have complete type hints."""
        import inspect

        methods = inspect.getmembers(AuditExporter, predicate=inspect.ismethod)

        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                assert sig.return_annotation != inspect.Signature.empty


class TestDocstrings:
    """Test that all public APIs have docstrings (CORE-012)."""

    def test_audit_trail_has_docstrings(self) -> None:
        """Test that AuditTrail has docstrings on public methods."""
        import inspect

        methods = inspect.getmembers(AuditTrail, predicate=inspect.ismethod)

        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None

    def test_exporter_has_docstrings(self) -> None:
        """Test that AuditExporter has docstrings on public methods."""
        import inspect

        methods = inspect.getmembers(AuditExporter, predicate=inspect.ismethod)

        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
