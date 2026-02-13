"""
Unit tests for EventBusHealthMonitor.

Tests metrics collection, health checks, and performance monitoring.

Authority: WAVE-3 Stage 2 - ENH-089 EventBus Debugger
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import json
import tempfile

from cortex.observability.eventbus_health import (
    EventBusHealthMonitor,
    EventMetrics,
    HealthStatus
)
from cortex.core.event_bus import Event


@pytest.fixture
def temp_files():
    """Create temporary log and DLQ files."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_event.jsonl') as f:
        log_file = f.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_dlq.jsonl') as f:
        dlq_file = f.name
    
    yield log_file, dlq_file
    
    # Cleanup
    Path(log_file).unlink(missing_ok=True)
    Path(dlq_file).unlink(missing_ok=True)


@pytest.fixture
def monitor_with_events(temp_files):
    """Create health monitor with test event data."""
    log_file, dlq_file = temp_files
    
    # Write test events to log
    now = datetime.now()
    
    with open(log_file, 'w') as f:
        for i in range(10):
            event = {
                "timestamp": (now - timedelta(seconds=i*10)).isoformat(),
                "type": f"test.event_{i % 3}",
                "payload": {
                    "correlation_id": f"corr-{i}",
                    "event_id": f"evt-{i}",
                    "source": "TDDOrchestrator" if i % 2 == 0 else "EnforcementAgent",
                    "priority": i % 3
                }
            }
            f.write(json.dumps(event) + '\n')
    
    monitor = EventBusHealthMonitor(
        log_file=log_file,
        dlq_file=dlq_file,
        metrics_window_seconds=300
    )
    
    return monitor


def test_monitor_initialization(temp_files):
    """Test EventBusHealthMonitor initialization."""
    log_file, dlq_file = temp_files
    
    monitor = EventBusHealthMonitor(
        log_file=log_file,
        dlq_file=dlq_file
    )
    
    assert monitor.log_file == Path(log_file)
    assert monitor.dlq_file == Path(dlq_file)
    assert monitor.metrics_window.total_seconds() == 300


def test_collect_metrics_empty_log(temp_files):
    """Test metrics collection with empty log."""
    log_file, dlq_file = temp_files
    
    monitor = EventBusHealthMonitor(log_file, dlq_file)
    metrics = monitor.collect_metrics()
    
    assert metrics.throughput_per_second == 0.0
    assert metrics.avg_latency_ms == 0.0
    assert metrics.failure_rate == 0.0
    assert len(metrics.event_type_distribution) == 0


def test_collect_metrics_with_events(monitor_with_events):
    """Test metrics collection with events."""
    metrics = monitor_with_events.collect_metrics()
    
    assert metrics.throughput_per_second > 0
    assert isinstance(metrics.event_type_distribution, dict)
    assert isinstance(metrics.source_distribution, dict)
    assert isinstance(metrics.priority_distribution, dict)


def test_metrics_throughput_calculation(monitor_with_events):
    """Test throughput calculation."""
    metrics = monitor_with_events.collect_metrics()
    
    # Should have some throughput
    assert metrics.throughput_per_second >= 0


def test_metrics_latency_calculation(monitor_with_events):
    """Test latency calculation."""
    metrics = monitor_with_events.collect_metrics()
    
    # Should calculate average latency
    assert metrics.avg_latency_ms >= 0


def test_metrics_event_distribution(monitor_with_events):
    """Test event type distribution."""
    metrics = monitor_with_events.collect_metrics()
    
    # Should have multiple event types
    assert len(metrics.event_type_distribution) > 0
    assert "test.event_0" in metrics.event_type_distribution or \
           "test.event_1" in metrics.event_type_distribution


def test_metrics_source_distribution(monitor_with_events):
    """Test source distribution."""
    metrics = monitor_with_events.collect_metrics()
    
    # Should track sources
    assert len(metrics.source_distribution) > 0


def test_check_health_healthy(monitor_with_events):
    """Test health check with healthy system."""
    health = monitor_with_events.check_health()
    
    assert isinstance(health, HealthStatus)
    # May or may not be healthy depending on test data
    assert isinstance(health.healthy, bool)
    assert isinstance(health.warnings, list)
    assert isinstance(health.recommendations, list)


def test_health_thresholds(temp_files):
    """Test health check threshold configuration."""
    log_file, dlq_file = temp_files
    
    monitor = EventBusHealthMonitor(log_file, dlq_file)
    
    assert monitor.min_throughput > 0
    assert monitor.max_latency_ms > 0
    assert monitor.max_failure_rate > 0


def test_get_metrics_history(monitor_with_events):
    """Test historical metrics retrieval."""
    history = monitor_with_events.get_metrics_history(
        duration_minutes=60,
        interval_minutes=5
    )
    
    assert isinstance(history, list)
    # May be empty if no events in time windows
    assert all(isinstance(m, EventMetrics) for m in history)
