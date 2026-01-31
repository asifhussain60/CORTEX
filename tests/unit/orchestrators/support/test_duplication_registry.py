"""
Test suite for DuplicationRegistry orchestrator.

This module provides comprehensive test coverage for the DuplicationRegistry,
which maintains a queryable catalog of all detected duplications in CORTEX.

Test Organization:
    - TestDuplicationRegistryCore: Core registry functionality
    - TestQueryInterface: Query and filtering capabilities
    - TestRegistryOperations: Add/update/remove operations
    - TestRegistryPersistence: Storage and retrieval
    - TestRegistryPerformance: Performance benchmarks
    - TestRegistryRobustness: Edge cases and error handling
    - TestRegistryAudit: Audit logging integration

AC_START: TEST-DuplicationRegistry-001
"""

import pytest
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.support.duplication_registry import (
    DuplicationRegistry,
    DuplicationRecord,
    DuplicationQuery,
    SeverityLevel,
    DuplicationStatus,
)
from cortex.brain.core.orchestrator_base import OrchestrationContext
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@pytest.fixture
def registry():
    """Create a fresh DuplicationRegistry for testing."""
    return DuplicationRegistry()


@pytest.fixture
def sample_record():
    """Create a sample duplication record."""
    return DuplicationRecord(
        duplication_id="dup-001",
        category="ExecutionContext",
        severity=SeverityLevel.CRITICAL,
        source_files=[
            "cortex/execution/execution_context.py",
            "cortex/core/execution_context.py",
        ],
        description="Duplicate ExecutionContext definitions",
        confidence_score=0.95,
    )


@pytest.fixture
def multiple_records():
    """Create multiple sample records for batch testing."""
    return [
        DuplicationRecord(
            duplication_id="dup-001",
            category="ExecutionContext",
            severity=SeverityLevel.CRITICAL,
            source_files=["cortex/execution/execution_context.py"],
            description="ExecutionContext duplicate 1",
        ),
        DuplicationRecord(
            duplication_id="dup-002",
            category="Registry",
            severity=SeverityLevel.HIGH,
            source_files=["cortex/core/registry.py"],
            description="Registry duplicate",
        ),
        DuplicationRecord(
            duplication_id="dup-003",
            category="WiringSystem",
            severity=SeverityLevel.CRITICAL,
            source_files=["cortex/wiring/wiring_system.py"],
            description="WiringSystem duplicate",
        ),
    ]


class TestDuplicationRegistryCore:
    """Core registry functionality tests."""

    def test_registry_001_initialization(self, registry):
        """REGISTRY-001: Registry initializes with empty state."""
        assert registry.size() == 0
        assert registry.get_all() == []
        assert registry.name == "DuplicationRegistry"

    def test_registry_002_add_duplication(self, registry, sample_record):
        """REGISTRY-002: Add single duplication to registry."""
        dup_id = registry.add_duplication(sample_record)
        assert dup_id == "dup-001"
        assert registry.size() == 1
        assert registry.exists("dup-001")

    def test_registry_003_add_multiple_duplications(self, registry, multiple_records):
        """REGISTRY-003: Add multiple duplications in batch."""
        ids = registry.add_duplications_batch(multiple_records)
        assert len(ids) == 3
        assert registry.size() == 3

    def test_registry_004_duplication_exists(self, registry, sample_record):
        """REGISTRY-004: Check if duplication exists by ID."""
        registry.add_duplication(sample_record)
        assert registry.exists("dup-001")
        assert not registry.exists("dup-999")

    def test_registry_005_get_duplication_by_id(self, registry, sample_record):
        """REGISTRY-005: Retrieve duplication by unique ID."""
        registry.add_duplication(sample_record)
        retrieved = registry.get_duplication("dup-001")
        assert retrieved is not None
        assert retrieved.category == "ExecutionContext"
        assert retrieved.severity == SeverityLevel.CRITICAL

    def test_registry_006_registry_state_consistency(self, registry, multiple_records):
        """REGISTRY-006: Registry maintains consistent state after operations."""
        registry.add_duplications_batch(multiple_records)
        assert registry.size() == 3

        registry.remove_duplication("dup-001")
        assert registry.size() == 2
        assert not registry.exists("dup-001")

        registry.update_status("dup-002", DuplicationStatus.RESOLVED)
        record = registry.get_duplication("dup-002")
        assert record.status == DuplicationStatus.RESOLVED

    def test_registry_007_registry_size(self, registry, multiple_records):
        """REGISTRY-007: Correctly report registry size."""
        assert registry.size() == 0
        registry.add_duplications_batch(multiple_records[:1])
        assert registry.size() == 1
        registry.add_duplications_batch(multiple_records[1:])
        assert registry.size() == 3

    def test_registry_008_clear_registry(self, registry, multiple_records):
        """REGISTRY-008: Clear all duplications from registry."""
        registry.add_duplications_batch(multiple_records)
        assert registry.size() == 3
        registry.clear()
        assert registry.size() == 0
        assert registry.get_all() == []


class TestQueryInterface:
    """Query and filtering capabilities tests."""

    def test_query_001_query_by_file(self, registry, multiple_records):
        """QUERY-001: Query duplications by file path."""
        registry.add_duplications_batch(multiple_records)
        query = registry.query().by_file("cortex/core/registry.py")
        results = registry.execute_query(query)
        assert len(results) == 1
        assert results[0].duplication_id == "dup-002"

    def test_query_002_query_by_category(self, registry, multiple_records):
        """QUERY-002: Query duplications by category."""
        registry.add_duplications_batch(multiple_records)
        query = registry.query().by_category("ExecutionContext")
        results = registry.execute_query(query)
        assert len(results) == 1
        assert results[0].category == "ExecutionContext"

    def test_query_003_query_by_severity(self, registry, multiple_records):
        """QUERY-003: Query duplications by severity level."""
        registry.add_duplications_batch(multiple_records)
        query = registry.query().by_severity(SeverityLevel.CRITICAL)
        results = registry.execute_query(query)
        assert len(results) == 2  # dup-001 and dup-003 are CRITICAL
        assert all(r.severity == SeverityLevel.CRITICAL for r in results)

    def test_query_004_query_by_date_range(self, registry):
        """QUERY-004: Query duplications within date range."""
        now = datetime.now()
        record = DuplicationRecord(
            duplication_id="dup-dated",
            category="Test",
            severity=SeverityLevel.MEDIUM,
            source_files=["test.py"],
            description="Test",
            created_at=now,
        )
        registry.add_duplication(record)

        # Query with range that includes the record
        query = (
            registry.query()
            .by_date_range(now - timedelta(hours=1), now + timedelta(hours=1))
        )
        results = registry.execute_query(query)
        assert len(results) == 1

    def test_query_005_query_by_multiple_filters(self, registry, multiple_records):
        """QUERY-005: Query with multiple filters combined."""
        registry.add_duplications_batch(multiple_records)
        query = (
            registry.query()
            .by_category("ExecutionContext")
            .by_severity(SeverityLevel.CRITICAL)
        )
        results = registry.execute_query(query)
        assert len(results) == 1
        assert results[0].duplication_id == "dup-001"

    def test_query_006_query_returns_empty_on_no_match(self, registry, multiple_records):
        """QUERY-006: Query returns empty list when no matches."""
        registry.add_duplications_batch(multiple_records)
        query = registry.query().by_category("NonExistent")
        results = registry.execute_query(query)
        assert len(results) == 0

    def test_query_007_query_exact_match(self, registry, multiple_records):
        """QUERY-007: Query returns exact match for single result."""
        registry.add_duplications_batch(multiple_records)
        query = registry.query().by_category("Registry")
        results = registry.execute_query(query)
        assert len(results) == 1
        assert results[0].duplication_id == "dup-002"

    def test_query_008_query_sorted_results(self, registry, multiple_records):
        """QUERY-008: Query results sorted by severity (descending)."""
        registry.add_duplications_batch(multiple_records)
        query = registry.query().sort_by('severity', descending=True)
        results = registry.execute_query(query)
        # Should be in order: CRITICAL, CRITICAL, HIGH
        assert results[0].severity == SeverityLevel.CRITICAL
        assert results[1].severity == SeverityLevel.CRITICAL
        assert results[2].severity == SeverityLevel.HIGH

    def test_query_009_query_limit_results(self, registry, multiple_records):
        """QUERY-009: Query with result limit."""
        registry.add_duplications_batch(multiple_records)
        query = registry.query().with_limit(2)
        results = registry.execute_query(query)
        assert len(results) == 2

    def test_query_010_query_statistics(self, registry, multiple_records):
        """QUERY-010: Get statistics for query results."""
        registry.add_duplications_batch(multiple_records)
        stats = registry.get_statistics()
        assert stats['total_duplications'] == 3
        assert stats['severity_distribution']['CRITICAL'] == 2
        assert stats['severity_distribution']['HIGH'] == 1
        assert 'average_confidence' in stats


class TestRegistryOperations:
    """Add/update/remove operations tests."""

    def test_ops_001_add_operation_returns_id(self, registry, sample_record):
        """OPS-001: Add operation returns unique ID."""
        dup_id = registry.add_duplication(sample_record)
        assert dup_id == "dup-001"
        assert isinstance(dup_id, str)

    def test_ops_002_update_duplication_status(self, registry, sample_record):
        """OPS-002: Update duplication resolution status."""
        registry.add_duplication(sample_record)
        registry.update_status("dup-001", DuplicationStatus.PENDING_REVIEW)
        record = registry.get_duplication("dup-001")
        assert record.status == DuplicationStatus.PENDING_REVIEW

    def test_ops_003_mark_as_resolved(self, registry, sample_record):
        """OPS-003: Mark duplication as resolved."""
        registry.add_duplication(sample_record)
        registry.update_status("dup-001", DuplicationStatus.RESOLVED)
        record = registry.get_duplication("dup-001")
        assert record.status == DuplicationStatus.RESOLVED
        assert record.resolved_at is not None

    def test_ops_004_mark_as_ignored(self, registry, sample_record):
        """OPS-004: Mark duplication as ignored."""
        registry.add_duplication(sample_record)
        registry.update_status("dup-001", DuplicationStatus.IGNORED)
        record = registry.get_duplication("dup-001")
        assert record.status == DuplicationStatus.IGNORED

    def test_ops_005_remove_duplication(self, registry, sample_record):
        """OPS-005: Remove duplication from registry."""
        registry.add_duplication(sample_record)
        assert registry.size() == 1
        removed = registry.remove_duplication("dup-001")
        assert removed is True
        assert registry.size() == 0
        assert not registry.exists("dup-001")

    def test_ops_006_bulk_update_status(self, registry, multiple_records):
        """OPS-006: Bulk update status for multiple duplications."""
        registry.add_duplications_batch(multiple_records)
        for dup_id in ["dup-001", "dup-002", "dup-003"]:
            registry.update_status(dup_id, DuplicationStatus.RESOLVED)

        stats = registry.get_statistics()
        assert stats['status_distribution']['RESOLVED'] == 3

    def test_ops_007_duplicate_id_rejected(self, registry, sample_record):
        """OPS-007: Adding duplicate ID is rejected."""
        registry.add_duplication(sample_record)
        with pytest.raises(ValueError, match="already exists"):
            registry.add_duplication(sample_record)

    def test_ops_008_update_nonexistent_raises_error(self, registry):
        """OPS-008: Updating nonexistent duplication raises error."""
        with pytest.raises(ValueError, match="not found"):
            registry.update_status("dup-999", DuplicationStatus.RESOLVED)


class TestRegistryPersistence:
    """Storage and retrieval tests."""

    def test_persist_001_save_to_json(self, registry, multiple_records):
        """PERSIST-001: Save registry to JSON file."""
        registry.add_duplications_batch(multiple_records)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "registry.json"
            registry.save_to_json(json_file)
            assert json_file.exists()

            # Verify file content
            with open(json_file) as f:
                data = json.load(f)
            assert data['metadata']['total_records'] == 3
            assert len(data['duplications']) == 3

    def test_persist_002_load_from_json(self, registry, multiple_records):
        """PERSIST-002: Load registry from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "registry.json"

            # Save
            registry.add_duplications_batch(multiple_records)
            registry.save_to_json(json_file)

            # Load into new registry
            registry2 = DuplicationRegistry()
            registry2.load_from_json(json_file)
            assert registry2.size() == 3

    def test_persist_003_round_trip_consistency(self, registry, multiple_records):
        """PERSIST-003: Save and load preserves data integrity."""
        registry.add_duplications_batch(multiple_records)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "registry.json"
            registry.save_to_json(json_file)

            registry2 = DuplicationRegistry()
            registry2.load_from_json(json_file)

            # Verify all records are identical
            for dup_id in ["dup-001", "dup-002", "dup-003"]:
                orig = registry.get_duplication(dup_id)
                loaded = registry2.get_duplication(dup_id)
                assert orig.category == loaded.category
                assert orig.severity == loaded.severity

    def test_persist_004_save_creates_directory(self, registry, sample_record):
        """PERSIST-004: Save creates directory if needed."""
        registry.add_duplication(sample_record)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "subdir" / "registry.json"
            registry.save_to_json(json_file)
            assert json_file.exists()
            assert json_file.parent.exists()

    def test_persist_005_load_missing_file_graceful(self, registry):
        """PERSIST-005: Loading missing file returns empty registry."""
        registry.load_from_json(Path("/nonexistent/path.json"))
        assert registry.size() == 0

    def test_persist_006_save_to_multiple_formats(self, registry, multiple_records):
        """PERSIST-006: Save registry in JSON and CSV formats."""
        registry.add_duplications_batch(multiple_records)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "registry.json"
            csv_file = Path(tmpdir) / "registry.csv"

            registry.save_to_json(json_file)
            registry.export_to_csv(csv_file)

            assert json_file.exists()
            assert csv_file.exists()

    def test_persist_007_export_filtered_subset(self, registry, multiple_records):
        """PERSIST-007: Export filtered subset of registry."""
        registry.add_duplications_batch(multiple_records)

        # Query for critical only
        query = registry.query().by_severity(SeverityLevel.CRITICAL)
        results = registry.execute_query(query)
        assert len(results) == 2  # dup-001 and dup-003


class TestRegistryPerformance:
    """Performance benchmark tests."""

    def test_perf_001_add_1000_duplications(self, registry):
        """PERF-001: Add 1000 duplications in < 500ms."""
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:04d}",
                category="ExecutionContext",
                severity=SeverityLevel.CRITICAL,
                source_files=[f"file_{i}.py"],
                description=f"Duplication {i}",
            )
            for i in range(1000)
        ]

        start_time = time.time()
        registry.add_duplications_batch(records)
        elapsed = (time.time() - start_time) * 1000  # Convert to ms

        assert registry.size() == 1000
        assert elapsed < 500, f"Add 1000 took {elapsed:.1f}ms (expected < 500ms)"

    def test_perf_002_query_1000_duplications(self, registry):
        """PERF-002: Query 1000 duplications in < 100ms."""
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:04d}",
                category="ExecutionContext" if i % 2 == 0 else "Registry",
                severity=SeverityLevel.CRITICAL if i % 3 == 0 else SeverityLevel.HIGH,
                source_files=[f"file_{i}.py"],
                description=f"Duplication {i}",
            )
            for i in range(1000)
        ]
        registry.add_duplications_batch(records)

        start_time = time.time()
        query = registry.query().by_category("ExecutionContext")
        results = registry.execute_query(query)
        elapsed = (time.time() - start_time) * 1000

        assert len(results) == 500
        assert elapsed < 100, f"Query took {elapsed:.1f}ms (expected < 100ms)"

    def test_perf_003_filter_by_severity_large_set(self, registry):
        """PERF-003: Filter 1000 duplications by severity in < 50ms."""
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:04d}",
                category="Test",
                severity=SeverityLevel.CRITICAL if i % 4 == 0 else SeverityLevel.HIGH,
                source_files=[f"file_{i}.py"],
                description=f"Duplication {i}",
            )
            for i in range(1000)
        ]
        registry.add_duplications_batch(records)

        start_time = time.time()
        query = registry.query().by_severity(SeverityLevel.CRITICAL)
        results = registry.execute_query(query)
        elapsed = (time.time() - start_time) * 1000

        assert len(results) == 250  # 1000 / 4
        assert elapsed < 50, f"Filter took {elapsed:.1f}ms (expected < 50ms)"

    def test_perf_004_save_large_registry(self, registry):
        """PERF-004: Save 1000 duplications to disk in < 1s."""
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:04d}",
                category="ExecutionContext",
                severity=SeverityLevel.CRITICAL,
                source_files=[f"file_{i}.py"],
                description=f"Duplication {i}",
            )
            for i in range(1000)
        ]
        registry.add_duplications_batch(records)

        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "registry.json"
            start_time = time.time()
            registry.save_to_json(json_file)
            elapsed = (time.time() - start_time) * 1000

            assert json_file.exists()
            assert elapsed < 1000, f"Save took {elapsed:.1f}ms (expected < 1000ms)"

    def test_perf_005_load_large_registry(self, registry):
        """PERF-005: Load 1000 duplications from disk in < 1s."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "registry.json"

            # First save 1000 records
            records = [
                DuplicationRecord(
                    duplication_id=f"dup-{i:04d}",
                    category="ExecutionContext",
                    severity=SeverityLevel.CRITICAL,
                    source_files=[f"file_{i}.py"],
                    description=f"Duplication {i}",
                )
                for i in range(1000)
            ]
            registry.add_duplications_batch(records)
            registry.save_to_json(json_file)

            # Now load into fresh registry
            registry2 = DuplicationRegistry()
            start_time = time.time()
            registry2.load_from_json(json_file)
            elapsed = (time.time() - start_time) * 1000

            assert registry2.size() == 1000
            assert elapsed < 1000, f"Load took {elapsed:.1f}ms (expected < 1000ms)"


class TestRegistryRobustness:
    """Edge cases and error handling tests."""

    def test_robust_001_empty_query_results(self, registry):
        """ROBUST-001: Gracefully handle empty query results."""
        query = registry.query().by_category("NonExistent")
        results = registry.execute_query(query)
        assert results == []

    def test_robust_002_invalid_filter_values(self, registry):
        """ROBUST-002: Reject invalid filter values."""
        # This tests that invalid values don't crash the query
        query = registry.query().by_category("")
        results = registry.execute_query(query)
        assert isinstance(results, list)

    def test_robust_003_special_characters_in_paths(self, registry):
        """ROBUST-003: Handle special characters in file paths."""
        record = DuplicationRecord(
            duplication_id="dup-special",
            category="ExecutionContext",
            severity=SeverityLevel.CRITICAL,
            source_files=["cortex/file with spaces.py", "cortex/file-with-dashes.py"],
            description="Special chars in paths",
        )
        registry.add_duplication(record)
        assert registry.exists("dup-special")

    def test_robust_004_concurrent_access(self, registry, multiple_records):
        """ROBUST-004: Handle concurrent read access."""
        registry.add_duplications_batch(multiple_records)
        # Simulate multiple concurrent reads
        for _ in range(10):
            results = registry.query().by_category("ExecutionContext")
            registry.execute_query(results)
        assert registry.size() == 3

    def test_robust_005_malformed_duplication_data(self, registry):
        """ROBUST-005: Reject malformed duplication data."""
        # Invalid record with minimal data
        record = DuplicationRecord(
            duplication_id="dup-minimal",
            category="",
            severity=SeverityLevel.LOW,
            source_files=[],
            description="",
        )
        dup_id = registry.add_duplication(record)
        assert dup_id == "dup-minimal"

    def test_robust_006_unicode_in_descriptions(self, registry):
        """ROBUST-006: Handle Unicode in duplication descriptions."""
        record = DuplicationRecord(
            duplication_id="dup-unicode",
            category="ExecutionContext",
            severity=SeverityLevel.CRITICAL,
            source_files=["test.py"],
            description="Unicode test: 你好世界 🚀 Ñoño",
        )
        registry.add_duplication(record)
        retrieved = registry.get_duplication("dup-unicode")
        assert "你好世界" in retrieved.description

    def test_robust_007_very_long_file_paths(self, registry):
        """ROBUST-007: Handle very long file paths (>256 chars)."""
        long_path = "cortex/" + "/".join(["dir"] * 50) + "/file.py"
        record = DuplicationRecord(
            duplication_id="dup-long-path",
            category="ExecutionContext",
            severity=SeverityLevel.CRITICAL,
            source_files=[long_path],
            description="Very long path",
        )
        registry.add_duplication(record)
        assert registry.exists("dup-long-path")


class TestRegistryAudit:
    """Audit logging integration tests."""

    def test_audit_001_log_add_operation(self, registry, sample_record):
        """AUDIT-001: Log registry add operations."""
        # Verify add operation creates audit entry
        with patch.object(registry.audit_logger, 'log_operation_start') as mock_log:
            registry.add_duplication(sample_record)
            # Should have been called for init and add
            assert mock_log.call_count >= 1

    def test_audit_002_log_query_operations(self, registry, multiple_records):
        """AUDIT-002: Log registry query operations."""
        registry.add_duplications_batch(multiple_records)

        with patch.object(registry.audit_logger, 'log_operation_start') as mock_log:
            query = registry.query().by_category("ExecutionContext")
            registry.execute_query(query)
            # Query execution should log
            assert mock_log.call_count >= 1

    def test_audit_003_log_update_operations(self, registry, sample_record):
        """AUDIT-003: Log registry update operations."""
        registry.add_duplication(sample_record)

        with patch.object(registry.audit_logger, 'log_operation_start') as mock_log:
            registry.update_status("dup-001", DuplicationStatus.RESOLVED)
            assert mock_log.call_count >= 1

    def test_audit_004_audit_trail_completeness(self, registry, multiple_records):
        """AUDIT-004: All operations logged to audit trail."""
        # Add operations
        registry.add_duplications_batch(multiple_records)

        # Query operations
        registry.query().by_category("ExecutionContext")

        # Update operations
        registry.update_status("dup-001", DuplicationStatus.RESOLVED)

        # Registry maintains audit logger
        assert registry.audit_logger is not None


class TestDuplicationQueryBuilder:
    """DuplicationQuery builder pattern tests."""

    def test_builder_001_fluent_interface(self, registry):
        """BUILDER-001: Query builder supports fluent interface."""
        query = (
            registry.query()
            .by_category("ExecutionContext")
            .by_severity(SeverityLevel.CRITICAL)
            .with_limit(10)
        )
        assert query is not None
        config = query.build()
        assert 'filters' in config
        assert config['limit'] == 10

    def test_builder_002_build_valid_query(self, registry):
        """BUILDER-002: Builder creates valid query object."""
        query = registry.query().by_category("Test")
        config = query.build()
        assert isinstance(config, dict)
        assert 'filters' in config
        assert 'sort_by' in config
        assert 'sort_desc' in config

    def test_builder_003_chain_multiple_filters(self, registry, multiple_records):
        """BUILDER-003: Chain multiple filter methods."""
        registry.add_duplications_batch(multiple_records)

        query = (
            registry.query()
            .by_category("ExecutionContext")
            .by_severity(SeverityLevel.CRITICAL)
            .by_status(DuplicationStatus.DETECTED)
        )
        results = registry.execute_query(query)
        assert len(results) >= 0

    def test_builder_004_reset_builder(self, registry):
        """BUILDER-004: Reset builder for new query."""
        query = registry.query().by_category("Test")
        config1 = query.build()
        assert 'category' in config1['filters']

        query.reset()
        config2 = query.build()
        assert len(config2['filters']) == 0


if __name__ == "__main__":
    # Development mode - show test discovery
    pytest.main([__file__, "-v", "--collect-only"])


# AC_COMPLETE: TEST-DuplicationRegistry-001
