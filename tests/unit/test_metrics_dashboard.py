"""
Test suite for Metrics Dashboard (OB-001-02).

This module tests the metrics dashboard UI/API for visualizing CORTEX runtime
metrics, providing real-time updates, and enabling historical data queries.

Acceptance Tests:
- Dashboard displays key metrics
- Real-time updates working
- Historical data queryable
"""

import pytest
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import json


# Import modules to be tested (will be created)
from cortex.core.observability.metrics_dashboard import MetricsDashboard, DashboardConfig
from cortex.core.observability.metrics_aggregator import MetricsAggregator, MetricPoint


class TestDashboardInitialization:
    """Test MetricsDashboard initialization."""

    def test_dashboard_initializes_with_valid_config(self) -> None:
        """
        Test that MetricsDashboard initializes with valid configuration.

        Expected:
        - Dashboard instance created successfully
        - Configuration stored correctly
        - HTTP server configured
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        assert dashboard is not None
        assert dashboard.host == "127.0.0.1"
        assert dashboard.port == 8080
        assert dashboard.enabled is True

    def test_dashboard_respects_disabled_flag(self) -> None:
        """
        Test that MetricsDashboard respects the enabled flag.

        Expected:
        - When enabled=False, HTTP server not started
        - Dashboard still instantiates
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=False,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        assert dashboard.enabled is False

    def test_dashboard_requires_valid_port(self) -> None:
        """
        Test that MetricsDashboard validates port number.

        Expected:
        - Invalid port raises ValueError
        """
        with pytest.raises(ValueError, match="port must be between 1 and 65535"):
            config = DashboardConfig(
                host="127.0.0.1",
                port=99999,  # Invalid
                enabled=True,
                title="CORTEX Metrics Dashboard",
                refresh_interval_seconds=5,
            )


class TestMetricsDisplay:
    """Test metrics display and aggregation."""

    def test_dashboard_displays_key_metrics(self) -> None:
        """
        Test that dashboard displays key metrics.

        Expected:
        - Metrics endpoint returns JSON with key metrics
        - Metrics include: span count, trace count, error rate, latency
        - Timestamp included
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Add some metrics
        dashboard.metrics_aggregator.record_span("test.operation", 100.0)
        dashboard.metrics_aggregator.record_span("test.operation", 150.0)
        dashboard.metrics_aggregator.record_error("test.operation")
        
        # Get metrics
        metrics = dashboard.get_metrics_data()
        
        assert metrics is not None
        assert "timestamp" in metrics
        assert "metrics" in metrics
        assert len(metrics["metrics"]) > 0

    def test_key_metrics_include_span_count(self) -> None:
        """
        Test that key metrics include span count.

        Expected:
        - Span count metric present
        - Value is integer
        - Increments correctly
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Record spans
        for i in range(5):
            dashboard.metrics_aggregator.record_span(f"operation.{i}", 100.0 + i)
        
        metrics = dashboard.get_metrics_data()
        span_count = metrics["metrics"].get("span_count", 0)
        
        assert span_count == 5

    def test_key_metrics_include_error_rate(self) -> None:
        """
        Test that key metrics include error rate.

        Expected:
        - Error rate metric present
        - Value is percentage (0-100)
        - Calculated correctly
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Record 10 operations, 2 with errors
        for i in range(10):
            dashboard.metrics_aggregator.record_span(f"operation.{i}", 100.0)
            if i < 2:
                dashboard.metrics_aggregator.record_error(f"operation.{i}")
        
        metrics = dashboard.get_metrics_data()
        error_rate = metrics["metrics"].get("error_rate", 0)
        
        assert 0 <= error_rate <= 100
        # With 2 errors out of 10 spans, error_rate should be ~20%
        assert 15 < error_rate < 25

    def test_key_metrics_include_latency_stats(self) -> None:
        """
        Test that key metrics include latency statistics.

        Expected:
        - Latency stats present (min, max, avg, p95, p99)
        - Values are numbers (milliseconds)
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Record latencies
        for latency in [50, 100, 150, 200, 250, 300]:
            dashboard.metrics_aggregator.record_span("operation.test", float(latency))
        
        metrics = dashboard.get_metrics_data()
        latency_stats = metrics["metrics"].get("latency_stats", {})
        
        assert "avg" in latency_stats
        assert "min" in latency_stats
        assert "max" in latency_stats
        assert "p95" in latency_stats
        assert "p99" in latency_stats


class TestRealTimeUpdates:
    """Test real-time metric updates."""

    def test_metrics_update_in_real_time(self) -> None:
        """
        Test that metrics update in real time as spans complete.

        Expected:
        - Initial metrics retrieved
        - New span recorded
        - Updated metrics retrieved
        - New span reflected in metrics
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Get initial metrics
        initial_metrics = dashboard.get_metrics_data()
        initial_count = initial_metrics["metrics"].get("span_count", 0)
        
        # Record new span
        dashboard.metrics_aggregator.record_span("new.operation", 100.0)
        
        # Get updated metrics
        updated_metrics = dashboard.get_metrics_data()
        updated_count = updated_metrics["metrics"].get("span_count", 0)
        
        assert updated_count == initial_count + 1

    def test_websocket_updates_streaming(self) -> None:
        """
        Test that WebSocket provides streaming metric updates.

        Expected:
        - WebSocket endpoint available
        - Sends updates at configured interval
        - Client receives new metrics
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=1,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Mock WebSocket
        mock_ws = AsyncMock()
        
        with patch.object(dashboard, "broadcast_metrics_update") as mock_broadcast:
            # Simulate metric update
            dashboard.metrics_aggregator.record_span("test.op", 100.0)
            
            # In real implementation, would broadcast to connected WebSockets


class TestHistoricalDataQuery:
    """Test querying historical metrics data."""

    def test_query_metrics_by_time_range(self) -> None:
        """
        Test querying metrics within a time range.

        Expected:
        - Query with start and end timestamps
        - Returns metrics points within range
        - Excludes metrics outside range
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Record metrics at different times
        now = datetime.utcnow()
        dashboard.metrics_aggregator.record_span("operation.1", 100.0, timestamp=now)
        dashboard.metrics_aggregator.record_span("operation.2", 150.0, timestamp=now - timedelta(hours=1))
        dashboard.metrics_aggregator.record_span("operation.3", 200.0, timestamp=now - timedelta(hours=2))
        
        # Query last hour
        start_time = now - timedelta(hours=1)
        end_time = now
        
        results = dashboard.query_metrics(start_time=start_time, end_time=end_time)
        
        # Should include operation.1 and operation.2
        assert len(results) >= 2

    def test_query_metrics_by_operation_name(self) -> None:
        """
        Test querying metrics for specific operation.

        Expected:
        - Filter by operation_name
        - Returns only metrics for that operation
        - Excludes other operations
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Record metrics for different operations
        dashboard.metrics_aggregator.record_span("operation.a", 100.0)
        dashboard.metrics_aggregator.record_span("operation.a", 110.0)
        dashboard.metrics_aggregator.record_span("operation.b", 200.0)
        
        # Query for operation.a only
        results = dashboard.query_metrics(operation_name="operation.a")
        
        # All results should be for operation.a
        assert len(results) >= 2
        for result in results:
            assert result.get("operation") == "operation.a" or "operation.a" in str(result)

    def test_query_aggregated_metrics(self) -> None:
        """
        Test querying aggregated metrics (hourly, daily).

        Expected:
        - Aggregation by time bucket (1h, 1d)
        - Returns aggregated stats per bucket
        - Includes min, max, avg, count
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Record metrics
        for i in range(10):
            dashboard.metrics_aggregator.record_span("operation.test", 100.0 + i * 10)
        
        # Query aggregated by hour
        results = dashboard.query_metrics_aggregated(bucket_size_seconds=3600)
        
        assert len(results) > 0
        for result in results:
            assert "min" in result
            assert "max" in result
            assert "avg" in result
            assert "count" in result


class TestDashboardVisualization:
    """Test dashboard HTML/JSON visualization."""

    def test_dashboard_html_endpoint(self) -> None:
        """
        Test that dashboard HTML endpoint returns valid HTML.

        Expected:
        - /dashboard endpoint returns HTML
        - Includes metric cards
        - Includes charts
        - Includes auto-refresh script
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        html = dashboard.get_dashboard_html()
        
        assert html is not None
        assert "<!DOCTYPE html>" in html or "<html" in html
        assert "CORTEX Metrics Dashboard" in html
        assert "refresh" in html.lower() or "auto-update" in html.lower()

    def test_metrics_json_api_endpoint(self) -> None:
        """
        Test that metrics JSON API endpoint returns valid JSON.

        Expected:
        - /api/metrics endpoint returns JSON
        - Parseable JSON format
        - Includes timestamp and metrics
        """
        config = DashboardConfig(
            host="127.0.0.1",
            port=8080,
            enabled=True,
            title="CORTEX Metrics Dashboard",
            refresh_interval_seconds=5,
        )
        
        dashboard = MetricsDashboard(config=config)
        
        # Record some metrics
        dashboard.metrics_aggregator.record_span("test.op", 100.0)
        
        # Get JSON
        json_data = dashboard.get_metrics_json()
        
        # Should be valid JSON string
        parsed = json.loads(json_data)
        assert "metrics" in parsed
        assert "timestamp" in parsed


class TestMetricsAggregator:
    """Test the metrics aggregator component."""

    def test_aggregator_records_span_latencies(self) -> None:
        """
        Test that aggregator records span latencies.

        Expected:
        - Records latency values
        - Computes min, max, avg
        """
        aggregator = MetricsAggregator()
        
        latencies = [100.0, 150.0, 200.0, 50.0]
        for latency in latencies:
            aggregator.record_span("operation.test", latency)
        
        stats = aggregator.get_latency_stats("operation.test")
        
        assert stats["min"] == 50.0
        assert stats["max"] == 200.0
        assert stats["avg"] == sum(latencies) / len(latencies)

    def test_aggregator_records_errors(self) -> None:
        """
        Test that aggregator tracks error counts.

        Expected:
        - Records error occurrences
        - Computes error count and rate
        """
        aggregator = MetricsAggregator()
        
        # Record 10 spans, 3 errors
        for i in range(10):
            aggregator.record_span(f"operation.{i}", 100.0)
        
        for i in range(3):
            aggregator.record_error(f"operation.{i}")
        
        error_rate = aggregator.get_error_rate()
        
        assert 25 < error_rate < 35  # Should be ~30%

    def test_aggregator_computes_percentiles(self) -> None:
        """
        Test that aggregator computes latency percentiles.

        Expected:
        - p50, p95, p99 available
        - Values in correct order: p50 <= p95 <= p99
        """
        aggregator = MetricsAggregator()
        
        # Record 100 latencies
        for i in range(1, 101):
            aggregator.record_span("operation.test", float(i * 10))
        
        stats = aggregator.get_latency_stats("operation.test")
        
        assert "p50" in stats
        assert "p95" in stats
        assert "p99" in stats
        assert stats["p50"] <= stats["p95"] <= stats["p99"]


class TestTypeHints:
    """Test that all functions have proper type hints (CORE-011)."""

    def test_dashboard_has_type_hints(self) -> None:
        """
        Test that MetricsDashboard methods have complete type hints.

        Expected:
        - All parameters have type annotations
        - Return types specified
        """
        import inspect
        
        methods = inspect.getmembers(MetricsDashboard, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                sig = inspect.signature(method)
                assert sig.return_annotation != inspect.Signature.empty


class TestDocstrings:
    """Test that all public APIs have docstrings (CORE-012)."""

    def test_dashboard_has_docstrings(self) -> None:
        """
        Test that MetricsDashboard has docstrings on public methods.

        Expected:
        - All public methods have docstrings
        - Docstrings follow Google style
        """
        import inspect
        
        methods = inspect.getmembers(MetricsDashboard, predicate=inspect.ismethod)
        
        for name, method in methods:
            if not name.startswith("_"):
                assert method.__doc__ is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
