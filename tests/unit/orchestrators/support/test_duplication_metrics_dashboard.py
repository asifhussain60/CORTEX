"""
Test suite for DuplicationMetricsDashboard.

AC_START: TEST-DuplicationMetricsDashboard-001
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from cortex.orchestrators.support.duplication_metrics_dashboard import (
    DuplicationMetricsDashboard,
    MetricSnapshot,
)
from cortex.orchestrators.support.duplication_registry import (
    DuplicationRegistry,
    DuplicationRecord,
    SeverityLevel,
    DuplicationStatus,
)


@pytest.fixture
def registry_with_data():
    """Create registry with sample data."""
    reg = DuplicationRegistry()
    records = [
        DuplicationRecord(
            duplication_id="dup-001",
            category="ExecutionContext",
            severity=SeverityLevel.CRITICAL,
            source_files=["file1.py"],
            description="Test",
        ),
        DuplicationRecord(
            duplication_id="dup-002",
            category="Registry",
            severity=SeverityLevel.HIGH,
            source_files=["file2.py"],
            description="Test",
        ),
        DuplicationRecord(
            duplication_id="dup-003",
            category="ExecutionContext",
            severity=SeverityLevel.CRITICAL,
            source_files=["file3.py"],
            description="Test",
        ),
    ]
    reg.add_duplications_batch(records)
    return reg


@pytest.fixture
def dashboard():
    """Create a metrics dashboard."""
    return DuplicationMetricsDashboard()


class TestDashboardCore:
    """Core dashboard functionality tests."""

    def test_dash_001_initialization(self, dashboard):
        """DASH-001: Dashboard initializes."""
        assert dashboard.name == "DuplicationMetricsDashboard"
        assert len(dashboard._snapshots) == 0

    def test_dash_002_set_registry(self, dashboard, registry_with_data):
        """DASH-002: Can set registry."""
        dashboard.set_registry(registry_with_data)
        assert dashboard._registry is not None

    def test_dash_003_capture_snapshot(self, dashboard, registry_with_data):
        """DASH-003: Capture metrics snapshot."""
        dashboard.set_registry(registry_with_data)
        snapshot = dashboard.capture_snapshot()
        assert snapshot.total_duplications == 3
        assert snapshot.critical_count == 2
        assert snapshot.high_count == 1

    def test_dash_004_get_current_metrics(self, dashboard, registry_with_data):
        """DASH-004: Get current metrics."""
        dashboard.set_registry(registry_with_data)
        metrics = dashboard.get_current_metrics()
        assert metrics['total_duplications'] == 3
        assert 'by_severity' in metrics
        assert 'by_category' in metrics

    def test_dash_005_category_breakdown(self, dashboard, registry_with_data):
        """DASH-005: Get category breakdown."""
        dashboard.set_registry(registry_with_data)
        breakdown = dashboard.get_category_breakdown()
        assert 'ExecutionContext' in breakdown
        assert breakdown['ExecutionContext']['CRITICAL'] == 2

    def test_dash_006_resolution_rate(self, dashboard, registry_with_data):
        """DASH-006: Calculate resolution rate."""
        dashboard.set_registry(registry_with_data)
        rate = dashboard.get_resolution_rate()
        assert rate['total_duplications'] == 3
        assert rate['resolution_rate_percent'] == 0.0  # None resolved yet

    def test_dash_007_top_problem_categories(self, dashboard, registry_with_data):
        """DASH-007: Get top problem categories."""
        dashboard.set_registry(registry_with_data)
        top = dashboard.get_top_problem_categories(limit=3)
        assert len(top) <= 3
        assert top[0]['category'] == 'ExecutionContext'

    def test_dash_008_trend_data(self, dashboard, registry_with_data):
        """DASH-008: Get trend data."""
        dashboard.set_registry(registry_with_data)
        dashboard.capture_snapshot()
        trend = dashboard.get_trend(days=7)
        assert 'data' in trend
        assert len(trend['data']) >= 1

    def test_dash_009_export_metrics(self, dashboard, registry_with_data):
        """DASH-009: Export metrics to JSON."""
        dashboard.set_registry(registry_with_data)
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "metrics.json"
            dashboard.export_metrics(json_file)
            assert json_file.exists()

    def test_dash_010_multiple_snapshots(self, dashboard, registry_with_data):
        """DASH-010: Store multiple snapshots."""
        dashboard.set_registry(registry_with_data)
        dashboard.capture_snapshot()
        dashboard.capture_snapshot()
        assert len(dashboard._snapshots) == 2


# AC_COMPLETE: TEST-DuplicationMetricsDashboard-001
