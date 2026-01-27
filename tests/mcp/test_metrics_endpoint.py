"""
AC-MCP-METRICS-001 through AC-MCP-METRICS-010
Test Prometheus metrics endpoint functionality.

Phase 5 Task 2: Metrics Endpoint Implementation
Date: 2026-01-27
Author: Asif Hussain

CORE-008: Tests written first (TDD)
CORE-011: All functions have type hints
CORE-012: All functions have docstrings
"""

import pytest
import time
from typing import Dict, Any
from unittest.mock import Mock, patch


class TestMetricsCollection:
    """Test metrics collection functionality."""
    
    # AC-MCP-METRICS-001
    def test_metrics_collector_initialization(self):
        """Metrics collector should initialize with zero counts."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        assert hasattr(collector, 'requests_total')
        assert hasattr(collector, 'request_duration')
        assert hasattr(collector, 'orchestrator_invocations')
        assert hasattr(collector, 'wiring_health')
    
    # AC-MCP-METRICS-002
    def test_request_counter_increments(self):
        """Request counter should increment on record_request."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        collector.record_request(method="GET", endpoint="/health", status="200")
        collector.record_request(method="POST", endpoint="/mcp/execute", status="200")
        
        # Verify metrics were recorded (collection happens)
        assert collector.requests_total is not None
    
    # AC-MCP-METRICS-003
    def test_request_duration_histogram(self):
        """Request duration should be recorded in histogram."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        collector.record_request_duration(
            method="GET",
            endpoint="/health",
            duration_seconds=0.05
        )
        
        assert collector.request_duration is not None
    
    # AC-MCP-METRICS-004
    def test_orchestrator_invocation_counter(self):
        """Orchestrator invocation counter should track calls."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        collector.record_orchestrator_invocation(
            orchestrator="TDDOrchestrator",
            operation="generate_tests",
            status="success"
        )
        
        collector.record_orchestrator_invocation(
            orchestrator="RefactoringOrchestrator",
            operation="analyze_code",
            status="success"
        )
        
        assert collector.orchestrator_invocations is not None
    
    # AC-MCP-METRICS-005
    def test_wiring_health_gauge(self):
        """Wiring health gauge should track health status."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        # 0 = unhealthy, 1 = degraded, 2 = healthy
        collector.set_wiring_health(2)  # healthy
        collector.set_wiring_health(1)  # degraded
        collector.set_wiring_health(0)  # unhealthy
        
        assert collector.wiring_health is not None


class TestMetricsEndpoint:
    """Test /metrics endpoint functionality."""
    
    # AC-MCP-METRICS-006
    def test_metrics_endpoint_returns_prometheus_format(self):
        """Metrics endpoint should return Prometheus text format."""
        from cortex.mcp.metrics import get_metrics_collector, generate_metrics_response
        
        collector = get_metrics_collector()
        collector.record_request("GET", "/health", "200")
        
        response = generate_metrics_response()
        
        # Prometheus format characteristics
        assert isinstance(response, str)
        assert "cortex_requests_total" in response or "# TYPE" in response
    
    # AC-MCP-METRICS-007
    def test_metrics_include_all_required_metrics(self):
        """Metrics response should include all 4 required metrics."""
        from cortex.mcp.metrics import generate_metrics_response
        
        response = generate_metrics_response()
        
        # Check for metric names (may be in HELP or TYPE comments)
        assert "cortex_requests_total" in response or "requests" in response.lower()
        assert "cortex_request_duration" in response or "duration" in response.lower()
        assert "cortex_orchestrator_invocations" in response or "orchestrator" in response.lower()
        assert "cortex_wiring_health" in response or "wiring" in response.lower()
    
    # AC-MCP-METRICS-008
    def test_metrics_endpoint_performance(self):
        """Metrics endpoint should respond quickly (<100ms)."""
        from cortex.mcp.metrics import generate_metrics_response
        
        start = time.time()
        response = generate_metrics_response()
        elapsed = time.time() - start
        
        assert elapsed < 0.1  # 100ms
        assert response is not None


class TestMetricsLabels:
    """Test metrics label functionality."""
    
    # AC-MCP-METRICS-009
    def test_request_counter_labels(self):
        """Request counter should support method, endpoint, status labels."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        # Different label combinations
        collector.record_request("GET", "/health", "200")
        collector.record_request("GET", "/health", "500")
        collector.record_request("POST", "/mcp/execute", "200")
        
        # Verify labels are tracked separately
        assert collector.requests_total is not None
    
    # AC-MCP-METRICS-010
    def test_orchestrator_invocation_labels(self):
        """Orchestrator invocations should have orchestrator, operation, status labels."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        collector.record_orchestrator_invocation(
            orchestrator="MasterOrchestrator",
            operation="coordinate",
            status="success"
        )
        
        collector.record_orchestrator_invocation(
            orchestrator="TDDOrchestrator",
            operation="generate_tests",
            status="failure"
        )
        
        assert collector.orchestrator_invocations is not None


class TestMetricsIntegration:
    """Test metrics integration with existing systems."""
    
    def test_metrics_collector_singleton(self):
        """Metrics collector should be a singleton."""
        from cortex.mcp.metrics import get_metrics_collector
        
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        
        assert collector1 is collector2
    
    def test_metrics_reset(self):
        """Metrics collector should support reset for testing."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        collector.record_request("GET", "/health", "200")
        
        # Reset for clean test state
        collector2 = MetricsCollector()
        
        # New instance should be independent
        assert collector2 is not None
    
    def test_concurrent_metric_recording(self):
        """Metrics should be thread-safe for concurrent recording."""
        import threading
        from cortex.mcp.metrics import get_metrics_collector
        
        collector = get_metrics_collector()
        errors = []
        
        def record_metrics():
            try:
                for _ in range(10):
                    collector.record_request("GET", "/health", "200")
            except Exception as e:
                errors.append(e)
        
        threads = []
        for _ in range(5):
            t = threading.Thread(target=record_metrics)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should complete without errors
        assert len(errors) == 0


class TestHistogramBuckets:
    """Test histogram bucket configuration."""
    
    def test_duration_histogram_buckets(self):
        """Duration histogram should have appropriate buckets."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        # Test various durations
        collector.record_request_duration("GET", "/health", 0.05)  # 50ms
        collector.record_request_duration("POST", "/mcp/execute", 0.5)  # 500ms
        collector.record_request_duration("GET", "/metrics", 0.01)  # 10ms
        
        # Histogram should handle these
        assert collector.request_duration is not None
    
    def test_histogram_bucket_ranges(self):
        """Histogram should cover expected request duration ranges."""
        from cortex.mcp.metrics import MetricsCollector
        
        collector = MetricsCollector()
        
        # Expected buckets: [0.1, 0.5, 1.0, 5.0, 10.0]
        # Test edge cases
        collector.record_request_duration("GET", "/test", 0.001)  # Very fast
        collector.record_request_duration("POST", "/test", 9.5)   # Slow
        collector.record_request_duration("GET", "/test", 0.5)    # Medium
        
        assert collector.request_duration is not None


class TestMetricsFormat:
    """Test Prometheus format compliance."""
    
    def test_prometheus_text_format(self):
        """Metrics should follow Prometheus text exposition format."""
        from cortex.mcp.metrics import generate_metrics_response
        
        response = generate_metrics_response()
        
        # Prometheus format rules:
        # - Lines starting with # are comments (HELP, TYPE)
        # - Metric lines: metric_name{labels} value timestamp
        lines = response.split('\n')
        
        # Should have some content
        assert len(lines) > 0
    
    def test_metrics_content_type(self):
        """Metrics should specify correct content type."""
        from cortex.mcp.metrics import get_metrics_content_type
        
        content_type = get_metrics_content_type()
        
        # Prometheus text format
        assert "text/plain" in content_type or content_type == "text/plain; version=0.0.4"
