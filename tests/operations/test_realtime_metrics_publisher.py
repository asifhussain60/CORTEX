"""
Tests for Real-Time Metrics Publisher

Tests:
    - Publisher initialization
    - Metrics snapshot extraction
    - WebSocket broadcasting
    - Operation progress tracking
    - Alert publishing
    - Health update publishing
    - Graceful degradation (no WebSocket server)
    - Metrics aggregation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.operations.realtime_metrics_publisher import (
    RealtimeMetricsPublisher,
    OperationProgress,
    MetricsUpdate,
    PublishChannel
)
from src.operations.modules.data_integration.real_time_metrics_dashboard import (
    RealTimeMetricsDashboard,
    UnifiedMetricsSnapshot,
    DashboardAlert,
    MetricSeverity
)


@pytest.fixture
def mock_dashboard():
    """Create mock dashboard."""
    dashboard = MagicMock(spec=RealTimeMetricsDashboard)
    dashboard.get_current_dashboard_state.return_value = {
        'collectors_active': 5,
        'collectors_total': 10,
        'collection_success_rate': 0.95,
        'avg_collection_time_ms': 15.5,
        'brain_health_score': 0.87,
        'tier1_performance_ms': 12.3,
        'tier2_performance_ms': 45.6,
        'tier3_performance_ms': 78.9,
        'cache_hit_rate': 0.82,
        'cache_memory_mb': 128.5,
        'memory_usage_mb': 512.0,
        'memory_pressure': 'normal',
        'templates_used_24h': 150,
        'avg_template_response_time_ms': 50.0,
        'template_success_rate': 0.98,
        'tokens_used_24h': 50000,
        'token_optimization_rate': 0.65,
        'estimated_cost_24h': 2.50,
        'workspace_health_score': 0.90,
        'files_monitored': 250,
        'build_status': 'passing',
        'test_coverage': 0.85,
        'active_alerts': []
    }
    return dashboard


@pytest.fixture
def mock_websocket_server():
    """Create mock WebSocket server."""
    server = AsyncMock()
    server.broadcast = AsyncMock()
    return server


@pytest.mark.asyncio
async def test_publisher_initialization(mock_dashboard):
    """Test publisher initializes correctly."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=None,
        publish_interval=5.0
    )
    
    assert publisher.dashboard == mock_dashboard
    assert publisher.websocket_server is None
    assert publisher.publish_interval == 5.0
    assert not publisher._running
    assert publisher._publish_task is None


@pytest.mark.asyncio
async def test_get_current_snapshot(mock_dashboard):
    """Test metrics snapshot extraction."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        publish_interval=5.0
    )
    
    snapshot = publisher._get_current_snapshot()
    
    assert isinstance(snapshot, UnifiedMetricsSnapshot)
    assert snapshot.collectors_active == 5
    assert snapshot.collectors_total == 10
    assert snapshot.brain_health_score == 0.87
    assert snapshot.cache_hit_rate == 0.82
    assert snapshot.memory_pressure == 'normal'


@pytest.mark.asyncio
async def test_snapshot_unchanged_detection(mock_dashboard):
    """Test unchanged snapshot detection."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        enable_aggregation=True
    )
    
    # First snapshot
    snapshot1 = publisher._get_current_snapshot()
    publisher._last_snapshot = snapshot1
    
    # Second snapshot (unchanged)
    snapshot2 = publisher._get_current_snapshot()
    
    assert publisher._snapshot_unchanged(snapshot2)


@pytest.mark.asyncio
async def test_publish_metrics_update(mock_dashboard, mock_websocket_server):
    """Test metrics update broadcasting."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=mock_websocket_server,
        publish_interval=5.0
    )
    
    snapshot = publisher._get_current_snapshot()
    await publisher._publish_metrics_update(snapshot)
    
    # Verify broadcast was called
    mock_websocket_server.broadcast.assert_called_once()
    
    # Verify message structure
    call_args = mock_websocket_server.broadcast.call_args
    message = call_args[0][0]
    
    assert message['type'] == 'metrics_update'
    assert message['channel'] == 'metrics'
    assert 'timestamp' in message
    assert 'data' in message
    assert 'collectors' in message['data']
    assert 'brain' in message['data']
    assert 'cache' in message['data']


@pytest.mark.asyncio
async def test_publish_operation_progress(mock_dashboard, mock_websocket_server):
    """Test operation progress publishing."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=mock_websocket_server
    )
    
    await publisher.publish_operation_progress(
        operation='sync',
        progress=50.0,
        status='Processing files...',
        total=100,
        current=50,
        metadata={'files_processed': 50}
    )
    
    # Verify broadcast was called
    mock_websocket_server.broadcast.assert_called_once()
    
    # Verify message structure
    call_args = mock_websocket_server.broadcast.call_args
    message = call_args[0][0]
    
    assert message['type'] == 'operation_progress'
    assert message['channel'] == 'operations'
    assert message['data']['operation'] == 'sync'
    assert message['data']['progress'] == 50.0
    assert message['data']['status'] == 'Processing files...'
    
    # Verify operation is tracked
    operations = publisher.get_active_operations()
    assert 'sync' in operations
    assert operations['sync'].progress == 50.0


@pytest.mark.asyncio
async def test_publish_alert(mock_dashboard, mock_websocket_server):
    """Test alert publishing."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=mock_websocket_server
    )
    
    await publisher.publish_alert(
        severity=MetricSeverity.WARNING,
        component='cache',
        metric='hit_rate',
        value=0.50,
        threshold=0.70,
        message='Cache hit rate below threshold',
        action_required=True
    )
    
    # Verify broadcast was called
    mock_websocket_server.broadcast.assert_called_once()
    
    # Verify message structure
    call_args = mock_websocket_server.broadcast.call_args
    message = call_args[0][0]
    
    assert message['type'] == 'alert'
    assert message['channel'] == 'alerts'
    assert message['data']['severity'] == 'warning'
    assert message['data']['component'] == 'cache'
    assert message['data']['action_required'] is True


@pytest.mark.asyncio
async def test_publish_health_update(mock_dashboard, mock_websocket_server):
    """Test health update publishing."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=mock_websocket_server
    )
    
    await publisher.publish_health_update(
        health_score=0.87,
        components={
            'tier1': {'status': 'healthy', 'score': 0.90},
            'tier2': {'status': 'healthy', 'score': 0.85},
            'tier3': {'status': 'healthy', 'score': 0.86}
        }
    )
    
    # Verify broadcast was called
    mock_websocket_server.broadcast.assert_called_once()
    
    # Verify message structure
    call_args = mock_websocket_server.broadcast.call_args
    message = call_args[0][0]
    
    assert message['type'] == 'health_update'
    assert message['channel'] == 'health'
    assert message['data']['health_score'] == 0.87
    assert 'components' in message['data']


@pytest.mark.asyncio
async def test_graceful_degradation_no_websocket(mock_dashboard):
    """Test publisher works without WebSocket server."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=None
    )
    
    # Should not raise errors
    snapshot = publisher._get_current_snapshot()
    await publisher._publish_metrics_update(snapshot)
    
    await publisher.publish_operation_progress(
        operation='test',
        progress=50.0,
        status='Testing'
    )
    
    await publisher.publish_alert(
        severity=MetricSeverity.WARNING,
        component='test',
        metric='test_metric',
        value=1.0,
        threshold=2.0,
        message='Test alert'
    )


@pytest.mark.asyncio
async def test_start_stop_publisher(mock_dashboard, mock_websocket_server):
    """Test starting and stopping publisher."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=mock_websocket_server,
        publish_interval=0.1  # Fast interval for testing
    )
    
    # Start publisher
    await publisher.start()
    assert publisher._running is True
    assert publisher._publish_task is not None
    
    # Wait for at least one publish cycle
    await asyncio.sleep(0.2)
    
    # Stop publisher
    await publisher.stop()
    assert publisher._running is False


@pytest.mark.asyncio
async def test_clear_completed_operation(mock_dashboard):
    """Test clearing completed operations."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard
    )
    
    # Add operation
    await publisher.publish_operation_progress(
        operation='test',
        progress=100.0,
        status='Complete'
    )
    
    assert 'test' in publisher.get_active_operations()
    
    # Clear operation
    publisher.clear_completed_operation('test')
    
    assert 'test' not in publisher.get_active_operations()


@pytest.mark.asyncio
async def test_get_active_operations(mock_dashboard):
    """Test getting active operations."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard
    )
    
    # Add multiple operations
    await publisher.publish_operation_progress(
        operation='sync',
        progress=50.0,
        status='Syncing'
    )
    
    await publisher.publish_operation_progress(
        operation='optimize',
        progress=30.0,
        status='Optimizing'
    )
    
    operations = publisher.get_active_operations()
    
    assert len(operations) == 2
    assert 'sync' in operations
    assert 'optimize' in operations
    assert operations['sync'].progress == 50.0
    assert operations['optimize'].progress == 30.0


@pytest.mark.asyncio
async def test_metrics_aggregation_enabled(mock_dashboard, mock_websocket_server):
    """Test metrics aggregation prevents duplicate broadcasts."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=mock_websocket_server,
        enable_aggregation=True,
        publish_interval=0.1
    )
    
    # Start publisher
    await publisher.start()
    
    # Wait for initial publish
    await asyncio.sleep(0.15)
    
    initial_call_count = mock_websocket_server.broadcast.call_count
    
    # Wait for another publish cycle (metrics unchanged)
    await asyncio.sleep(0.15)
    
    # Should not have additional broadcast (aggregation prevents it)
    assert mock_websocket_server.broadcast.call_count == initial_call_count
    
    await publisher.stop()


@pytest.mark.asyncio
async def test_error_handling_in_publish_loop(mock_dashboard, mock_websocket_server):
    """Test error handling in publish loop."""
    publisher = RealtimeMetricsPublisher(
        dashboard=mock_dashboard,
        websocket_server=mock_websocket_server,
        publish_interval=0.1
    )
    
    # Make get_current_dashboard_state raise exception
    mock_dashboard.get_current_dashboard_state.side_effect = Exception("Test error")
    
    # Start publisher (should not crash)
    await publisher.start()
    await asyncio.sleep(0.2)
    
    # Publisher should still be running
    assert publisher._running is True
    
    await publisher.stop()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
