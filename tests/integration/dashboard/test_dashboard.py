"""Tests for Dashboard - System Observability and Operations UI."""

import pytest
import json
from typing import Dict, Any, List
from datetime import datetime, timezone
from cortex.api.dashboard_api import DashboardAPI
from cortex.models.dashboard_models import (
    SystemHealth,
    MetricsData,
    ActivityLogEntry,
    DashboardConfig
)


class TestDashboardLoad:
    """Tests for dashboard loading performance."""

    def test_dashboard_api_initialization(self) -> None:
        """Test dashboard API can be initialized."""
        api = DashboardAPI()
        assert api is not None

    def test_dashboard_returns_health_overview(self) -> None:
        """Test dashboard returns system health overview."""
        api = DashboardAPI()
        health = api.get_health_overview()
        
        assert isinstance(health, SystemHealth)
        assert hasattr(health, "status")
        assert hasattr(health, "error_rate")
        assert hasattr(health, "active_operations")

    def test_dashboard_returns_metrics(self) -> None:
        """Test dashboard returns performance metrics."""
        api = DashboardAPI()
        metrics = api.get_metrics()
        
        assert isinstance(metrics, MetricsData)
        assert hasattr(metrics, "p50_latency")
        assert hasattr(metrics, "p95_latency")
        assert hasattr(metrics, "p99_latency")
        assert hasattr(metrics, "throughput")
        assert hasattr(metrics, "error_rate")

    def test_dashboard_returns_activity_log(self) -> None:
        """Test dashboard returns activity log."""
        api = DashboardAPI()
        log = api.get_activity_log()
        
        assert isinstance(log, list)
        assert all(isinstance(entry, ActivityLogEntry) for entry in log)
        assert len(log) <= 50

    def test_dashboard_load_time(self) -> None:
        """Test dashboard initial load completes quickly."""
        api = DashboardAPI()
        
        start = datetime.now(timezone.utc)
        health = api.get_health_overview()
        metrics = api.get_metrics()
        log = api.get_activity_log()
        end = datetime.now(timezone.utc)
        
        elapsed_seconds = (end - start).total_seconds()
        assert elapsed_seconds < 2.0  # Must load in <2 seconds


class TestHealthOverview:
    """Tests for system health overview."""

    def test_health_overview_shows_status(self) -> None:
        """Test health overview displays system status."""
        api = DashboardAPI()
        health = api.get_health_overview()
        
        assert health.status in ["healthy", "degraded", "unhealthy"]

    def test_health_overview_shows_error_rate(self) -> None:
        """Test health overview shows error rate."""
        api = DashboardAPI()
        health = api.get_health_overview()
        
        assert 0 <= health.error_rate <= 1.0
        assert isinstance(health.error_rate, float)

    def test_health_overview_shows_active_operations(self) -> None:
        """Test health overview shows active operations count."""
        api = DashboardAPI()
        health = api.get_health_overview()
        
        assert health.active_operations >= 0
        assert isinstance(health.active_operations, int)

    def test_health_overview_contains_all_fields(self) -> None:
        """Test health overview contains all required fields."""
        api = DashboardAPI()
        health = api.get_health_overview()
        
        assert hasattr(health, "status")
        assert hasattr(health, "error_rate")
        assert hasattr(health, "active_operations")
        assert hasattr(health, "timestamp")


class TestMetricsDisplay:
    """Tests for metrics display."""

    def test_metrics_include_latency_percentiles(self) -> None:
        """Test metrics include p50, p95, p99 latencies."""
        api = DashboardAPI()
        metrics = api.get_metrics()
        
        assert metrics.p50_latency >= 0
        assert metrics.p95_latency >= metrics.p50_latency
        assert metrics.p99_latency >= metrics.p95_latency

    def test_metrics_include_throughput(self) -> None:
        """Test metrics include throughput."""
        api = DashboardAPI()
        metrics = api.get_metrics()
        
        assert metrics.throughput >= 0
        assert isinstance(metrics.throughput, (int, float))

    def test_metrics_include_error_rate(self) -> None:
        """Test metrics include error rate."""
        api = DashboardAPI()
        metrics = api.get_metrics()
        
        assert 0 <= metrics.error_rate <= 1.0

    def test_metrics_update_refresh(self) -> None:
        """Test metrics can be refreshed."""
        api = DashboardAPI()
        
        metrics1 = api.get_metrics()
        metrics2 = api.get_metrics()
        
        # Both calls should succeed and return valid metrics
        assert metrics1.throughput >= 0
        assert metrics2.throughput >= 0


class TestActivityLog:
    """Tests for activity log display."""

    def test_activity_log_returns_list(self) -> None:
        """Test activity log returns list of entries."""
        api = DashboardAPI()
        log = api.get_activity_log()
        
        assert isinstance(log, list)

    def test_activity_log_limited_to_50_entries(self) -> None:
        """Test activity log limits to 50 most recent entries."""
        api = DashboardAPI()
        log = api.get_activity_log()
        
        assert len(log) <= 50

    def test_activity_log_entries_have_required_fields(self) -> None:
        """Test activity log entries have required fields."""
        api = DashboardAPI()
        log = api.get_activity_log()
        
        for entry in log:
            assert hasattr(entry, "operation_type")
            assert hasattr(entry, "status")
            assert hasattr(entry, "duration_ms")
            assert hasattr(entry, "timestamp")

    def test_activity_log_entry_status_valid(self) -> None:
        """Test activity log entries have valid status."""
        api = DashboardAPI()
        log = api.get_activity_log()
        
        valid_statuses = ["success", "failure", "in_progress"]
        for entry in log:
            assert entry.status in valid_statuses

    def test_activity_log_entry_duration_positive(self) -> None:
        """Test activity log entry durations are positive."""
        api = DashboardAPI()
        log = api.get_activity_log()
        
        for entry in log:
            if entry.status != "in_progress":
                assert entry.duration_ms > 0


class TestDashboardCharts:
    """Tests for chart/graph types."""

    def test_dashboard_supports_line_chart(self) -> None:
        """Test dashboard supports line chart type."""
        api = DashboardAPI()
        charts = api.get_available_chart_types()
        
        assert "line" in charts

    def test_dashboard_supports_bar_chart(self) -> None:
        """Test dashboard supports bar chart type."""
        api = DashboardAPI()
        charts = api.get_available_chart_types()
        
        assert "bar" in charts

    def test_dashboard_supports_pie_chart(self) -> None:
        """Test dashboard supports pie chart type."""
        api = DashboardAPI()
        charts = api.get_available_chart_types()
        
        assert "pie" in charts

    def test_dashboard_has_minimum_chart_types(self) -> None:
        """Test dashboard supports at least 3 chart types."""
        api = DashboardAPI()
        charts = api.get_available_chart_types()
        
        assert len(charts) >= 3


class TestDashboardMetrics:
    """Tests for metrics data structure."""

    def test_metrics_latency_in_milliseconds(self) -> None:
        """Test latency metrics are in milliseconds."""
        api = DashboardAPI()
        metrics = api.get_metrics()
        
        # Typical latencies should be in millisecond range (not seconds, not nanoseconds)
        assert metrics.p50_latency < 60000  # Less than 60 seconds
        assert metrics.p50_latency >= 0

    def test_metrics_throughput_is_numeric(self) -> None:
        """Test throughput is numeric."""
        api = DashboardAPI()
        metrics = api.get_metrics()
        
        assert isinstance(metrics.throughput, (int, float))

    def test_metrics_have_timestamp(self) -> None:
        """Test metrics include timestamp."""
        api = DashboardAPI()
        metrics = api.get_metrics()
        
        assert hasattr(metrics, "timestamp")
        assert metrics.timestamp is not None


class TestDashboardConfig:
    """Tests for dashboard configuration."""

    def test_dashboard_config_can_be_created(self) -> None:
        """Test dashboard config can be created."""
        config = DashboardConfig(
            refresh_interval_seconds=5,
            max_log_entries=50
        )
        
        assert config.refresh_interval_seconds == 5
        assert config.max_log_entries == 50

    def test_dashboard_config_defaults(self) -> None:
        """Test dashboard config has sensible defaults."""
        api = DashboardAPI()
        config = api.get_config()
        
        assert config.refresh_interval_seconds >= 1
        assert config.max_log_entries <= 500


class TestDashboardIntegration:
    """Integration tests for dashboard."""

    def test_dashboard_full_data_load(self) -> None:
        """Test loading all dashboard data together."""
        api = DashboardAPI()
        
        health = api.get_health_overview()
        metrics = api.get_metrics()
        log = api.get_activity_log()
        
        assert health.status is not None
        assert metrics.throughput >= 0
        assert isinstance(log, list)

    def test_dashboard_consistent_data(self) -> None:
        """Test dashboard returns consistent data across calls."""
        api = DashboardAPI()
        
        health1 = api.get_health_overview()
        health2 = api.get_health_overview()
        
        # Status should be consistent (same or natural progression)
        assert health1.status is not None
        assert health2.status is not None

    def test_dashboard_responsive_design_support(self) -> None:
        """Test dashboard supports responsive design."""
        api = DashboardAPI()
        
        # Check that dashboard can be rendered in different viewport sizes
        for viewport in ["mobile", "tablet", "desktop"]:
            config = api.get_config_for_viewport(viewport)
            assert config is not None

    def test_dashboard_handles_no_data_gracefully(self) -> None:
        """Test dashboard handles scenarios with minimal data."""
        api = DashboardAPI()
        
        # Should not raise even if no activity
        log = api.get_activity_log()
        assert isinstance(log, list)
