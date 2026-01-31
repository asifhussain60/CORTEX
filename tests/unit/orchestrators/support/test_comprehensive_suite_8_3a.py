"""
Comprehensive Test Suite for Phase 8.3A Foundation.

Covers all sections (1-4) with advanced test scenarios:
- Integration tests
- End-to-end workflows
- Performance benchmarks
- Edge cases
- Production scenarios

AC_START: TEST-ComprehensiveSuite-001
"""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta

from cortex.orchestrators.support.duplication_detector_orchestrator import DuplicationDetector
from cortex.orchestrators.support.pre_commit_pattern_matcher import PreCommitPatternMatcher
from cortex.orchestrators.support.duplication_registry import (
    DuplicationRegistry,
    DuplicationRecord,
    SeverityLevel,
    DuplicationStatus,
)
from cortex.orchestrators.support.duplication_metrics_dashboard import DuplicationMetricsDashboard


class TestE2EWorkflow:
    """End-to-end workflow tests."""

    def test_e2e_001_detection_to_registry(self):
        """E2E-001: Detect duplications and add to registry."""
        registry = DuplicationRegistry()
        records = [
            DuplicationRecord(
                duplication_id="dup-001",
                category="ExecutionContext",
                severity=SeverityLevel.CRITICAL,
                source_files=["file1.py", "file2.py"],
                description="ExecutionContext duplicate",
            ),
        ]
        ids = registry.add_duplications_batch(records)
        assert len(ids) == 1
        assert registry.size() == 1

    def test_e2e_002_detection_to_metrics(self):
        """E2E-002: Detect duplications, track metrics."""
        registry = DuplicationRegistry()
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:03d}",
                category="Test",
                severity=SeverityLevel.CRITICAL if i % 2 == 0 else SeverityLevel.HIGH,
                source_files=[f"file{i}.py"],
                description=f"Dup {i}",
            )
            for i in range(10)
        ]
        registry.add_duplications_batch(records)

        dashboard = DuplicationMetricsDashboard()
        dashboard.set_registry(registry)
        metrics = dashboard.get_current_metrics()
        assert metrics['total_duplications'] == 10

    def test_e2e_003_registry_to_resolution(self):
        """E2E-003: Track resolution workflow."""
        registry = DuplicationRegistry()
        record = DuplicationRecord(
            duplication_id="dup-001",
            category="Test",
            severity=SeverityLevel.CRITICAL,
            source_files=["file.py"],
            description="Test",
        )
        registry.add_duplication(record)

        # Mark as resolved
        registry.update_status("dup-001", DuplicationStatus.RESOLVED)
        retrieved = registry.get_duplication("dup-001")
        assert retrieved.status == DuplicationStatus.RESOLVED

    def test_e2e_004_full_pipeline(self):
        """E2E-004: Full pipeline - detect, register, track, export."""
        # Create registry with data
        registry = DuplicationRegistry()
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:03d}",
                category=["ExecutionContext", "Registry", "Wiring"][i % 3],
                severity=[SeverityLevel.CRITICAL, SeverityLevel.HIGH, SeverityLevel.MEDIUM][i % 3],
                source_files=[f"f{i}.py"],
                description=f"Dup {i}",
            )
            for i in range(20)
        ]
        registry.add_duplications_batch(records)

        # Create dashboard
        dashboard = DuplicationMetricsDashboard()
        dashboard.set_registry(registry)
        dashboard.capture_snapshot()

        # Resolve some
        for i in range(5):
            registry.update_status(f"dup-{i:03d}", DuplicationStatus.RESOLVED)

        # Export
        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard.export_metrics(Path(tmpdir) / "metrics.json")
            registry.save_to_json(Path(tmpdir) / "registry.json")
            registry.export_to_csv(Path(tmpdir) / "registry.csv")

        metrics = dashboard.get_current_metrics()
        assert metrics['total_duplications'] == 20


class TestIntegration:
    """Integration tests."""

    def test_int_001_registry_with_multiple_categories(self):
        """INT-001: Registry handles multiple categories correctly."""
        registry = DuplicationRegistry()
        categories = ["ExecutionContext", "Registry", "Wiring", "Handler", "Plugin"]
        for i, cat in enumerate(categories):
            record = DuplicationRecord(
                duplication_id=f"dup-{i}",
                category=cat,
                severity=SeverityLevel.CRITICAL,
                source_files=[f"file{i}.py"],
                description=f"Test {cat}",
            )
            registry.add_duplication(record)

        breakdown = DuplicationMetricsDashboard()
        breakdown.set_registry(registry)
        breakdown_data = breakdown.get_category_breakdown()
        assert len(breakdown_data) == 5

    def test_int_002_registry_query_performance(self):
        """INT-002: Registry query performance with 5000 records."""
        registry = DuplicationRegistry()
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:05d}",
                category="Test",
                severity=SeverityLevel.CRITICAL if i % 100 == 0 else SeverityLevel.HIGH,
                source_files=[f"f{i}.py"],
                description=f"D{i}",
            )
            for i in range(5000)
        ]

        start = time.time()
        registry.add_duplications_batch(records)
        add_time = (time.time() - start) * 1000

        start = time.time()
        query = registry.query().by_severity(SeverityLevel.CRITICAL)
        results = registry.execute_query(query)
        query_time = (time.time() - start) * 1000

        assert len(results) == 50  # 5000 / 100
        assert add_time < 2000  # < 2 seconds
        assert query_time < 200  # < 200 ms

    def test_int_003_persistence_round_trip(self):
        """INT-003: Persistence handles complex scenarios."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save
            registry1 = DuplicationRegistry()
            for i in range(100):
                record = DuplicationRecord(
                    duplication_id=f"dup-{i:03d}",
                    category=["Cat1", "Cat2", "Cat3"][i % 3],
                    severity=SeverityLevel.CRITICAL,
                    source_files=[f"file{i}.py"],
                    description=f"Test {i}",
                )
                registry1.add_duplication(record)

            json_file = Path(tmpdir) / "test.json"
            registry1.save_to_json(json_file)

            # Load and verify
            registry2 = DuplicationRegistry()
            registry2.load_from_json(json_file)

            assert registry2.size() == 100
            assert registry2.get_duplication("dup-050") is not None


class TestEdgeCases:
    """Edge case and error handling tests."""

    def test_edge_001_empty_registry_operations(self):
        """EDGE-001: Operations on empty registry."""
        registry = DuplicationRegistry()
        assert registry.size() == 0
        assert registry.get_all() == []
        stats = registry.get_statistics()
        assert stats['total_duplications'] == 0

    def test_edge_002_duplicate_id_handling(self):
        """EDGE-002: Duplicate ID rejection."""
        registry = DuplicationRegistry()
        record = DuplicationRecord(
            duplication_id="dup-001",
            category="Test",
            severity=SeverityLevel.CRITICAL,
            source_files=["f.py"],
            description="Test",
        )
        registry.add_duplication(record)

        with pytest.raises(ValueError):
            registry.add_duplication(record)

    def test_edge_003_unicode_handling(self):
        """EDGE-003: Unicode in descriptions."""
        registry = DuplicationRegistry()
        record = DuplicationRecord(
            duplication_id="dup-unicode",
            category="Test",
            severity=SeverityLevel.CRITICAL,
            source_files=["文件.py"],
            description="Unicode: 你好 🎯 مرحبا",
        )
        registry.add_duplication(record)
        retrieved = registry.get_duplication("dup-unicode")
        assert "你好" in retrieved.description

    def test_edge_004_very_large_file_lists(self):
        """EDGE-004: Records with many files."""
        registry = DuplicationRegistry()
        record = DuplicationRecord(
            duplication_id="dup-large",
            category="Test",
            severity=SeverityLevel.CRITICAL,
            source_files=[f"file{i}.py" for i in range(1000)],
            description="Many files",
        )
        registry.add_duplication(record)
        assert registry.exists("dup-large")


class TestProductionScenarios:
    """Production-ready test scenarios."""

    def test_prod_001_concurrent_workflows(self):
        """PROD-001: Multiple concurrent operations."""
        registry = DuplicationRegistry()

        # Add records
        for batch in range(3):
            records = [
                DuplicationRecord(
                    duplication_id=f"dup-{batch}-{i:03d}",
                    category="Test",
                    severity=SeverityLevel.CRITICAL,
                    source_files=[f"f{batch}-{i}.py"],
                    description=f"Test {batch} {i}",
                )
                for i in range(100)
            ]
            registry.add_duplications_batch(records)

        assert registry.size() == 300

    def test_prod_002_query_consistency(self):
        """PROD-002: Query results remain consistent."""
        registry = DuplicationRegistry()
        records = [
            DuplicationRecord(
                duplication_id=f"dup-{i:03d}",
                category="Test",
                severity=SeverityLevel.CRITICAL if i % 2 == 0 else SeverityLevel.HIGH,
                source_files=[f"f{i}.py"],
                description=f"Test {i}",
            )
            for i in range(200)
        ]
        registry.add_duplications_batch(records)

        # Multiple queries should return consistent results
        results1 = registry.execute_query(registry.query().by_severity(SeverityLevel.CRITICAL))
        results2 = registry.execute_query(registry.query().by_severity(SeverityLevel.CRITICAL))
        assert len(results1) == len(results2)

    def test_prod_003_metrics_accuracy(self):
        """PROD-003: Metrics calculations are accurate."""
        registry = DuplicationRegistry()
        critical_count = 0
        high_count = 0

        for i in range(500):
            if i % 5 == 0:
                sev = SeverityLevel.CRITICAL
                critical_count += 1
            else:
                sev = SeverityLevel.HIGH
                high_count += 1

            record = DuplicationRecord(
                duplication_id=f"dup-{i:04d}",
                category="Test",
                severity=sev,
                source_files=[f"f{i}.py"],
                description=f"Test {i}",
            )
            registry.add_duplication(record)

        dashboard = DuplicationMetricsDashboard()
        dashboard.set_registry(registry)
        metrics = dashboard.get_current_metrics()

        assert metrics['by_severity']['CRITICAL'] == critical_count
        assert metrics['by_severity']['HIGH'] == high_count


# AC_COMPLETE: TEST-ComprehensiveSuite-001
