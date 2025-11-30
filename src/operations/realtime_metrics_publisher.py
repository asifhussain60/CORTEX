"""
Real-Time Metrics Publisher

Extends RealTimeMetricsDashboard with WebSocket broadcasting capabilities.
Publishes metrics updates to connected WebSocket clients in real-time.

Architecture:
    RealTimeMetricsDashboard -> MetricsPublisher -> WebSocket Server -> Clients
         |                           |                    |              |
    Metrics Collection        Event-driven            Broadcasting   Dashboard UI
         |                      Observer                  |              |
    Every N seconds            Pattern              Rate limiting    Auto-update

Features:
    - WebSocket broadcasting integration
    - Event-driven observer pattern
    - Metrics aggregation and filtering
    - Operation progress tracking
    - Configurable publish intervals
    - Graceful degradation (works without WebSocket server)

Usage:
    # Initialize with WebSocket server
    publisher = RealtimeMetricsPublisher(
        dashboard=dashboard,
        websocket_server=server
    )
    
    # Start publishing
    await publisher.start()
    
    # Publish operation progress
    await publisher.publish_operation_progress(
        operation='sync',
        progress=50,
        status='Processing files...'
    )
    
    # Stop publishing
    await publisher.stop()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

# Import RealTimeMetricsDashboard
try:
    from src.operations.modules.data_integration.real_time_metrics_dashboard import (
        RealTimeMetricsDashboard,
        UnifiedMetricsSnapshot,
        DashboardAlert,
        MetricSeverity
    )
except ImportError:
    # Fallback import
    from modules.data_integration.real_time_metrics_dashboard import (
        RealTimeMetricsDashboard,
        UnifiedMetricsSnapshot,
        DashboardAlert,
        MetricSeverity
    )

# Import WebSocket server
try:
    from src.operations.realtime_dashboard_server import RealtimeDashboardServer
except ImportError:
    RealtimeDashboardServer = None


logger = logging.getLogger(__name__)


class PublishChannel(Enum):
    """WebSocket publish channels."""
    METRICS = "metrics"
    OPERATIONS = "operations"
    ALERTS = "alerts"
    HEALTH = "health"
    ALL = "all"


@dataclass
class OperationProgress:
    """Operation progress data."""
    operation: str
    progress: float
    total: Optional[int]
    current: Optional[int]
    status: str
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class MetricsUpdate:
    """Metrics update message."""
    type: str
    channel: str
    timestamp: str
    data: Dict[str, Any]


class RealtimeMetricsPublisher:
    """
    Real-time metrics publisher with WebSocket broadcasting.
    
    Extends RealTimeMetricsDashboard to publish metrics updates
    to connected WebSocket clients.
    
    Features:
        - Event-driven metrics publishing
        - WebSocket broadcasting integration
        - Operation progress tracking
        - Channel-based subscriptions
        - Metrics aggregation
        - Graceful degradation
    
    Attributes:
        dashboard (RealTimeMetricsDashboard): Metrics dashboard
        websocket_server (RealtimeDashboardServer): WebSocket server
        publish_interval (float): Publish interval (seconds)
        _running (bool): Publisher running state
        _publish_task (asyncio.Task): Publishing task
    """
    
    def __init__(
        self,
        dashboard: RealTimeMetricsDashboard,
        websocket_server: Optional['RealtimeDashboardServer'] = None,
        publish_interval: float = 5.0,
        enable_aggregation: bool = True
    ):
        """
        Initialize metrics publisher.
        
        Args:
            dashboard: RealTimeMetricsDashboard instance
            websocket_server: WebSocket server for broadcasting
            publish_interval: Interval for publishing metrics (seconds)
            enable_aggregation: Enable metrics aggregation
        """
        self.dashboard = dashboard
        self.websocket_server = websocket_server
        self.publish_interval = publish_interval
        self.enable_aggregation = enable_aggregation
        
        self._running = False
        self._publish_task: Optional[asyncio.Task] = None
        self._last_snapshot: Optional[UnifiedMetricsSnapshot] = None
        self._operations: Dict[str, OperationProgress] = {}
        
        logger.info(f"Initialized RealtimeMetricsPublisher (interval={publish_interval}s)")
    
    async def start(self):
        """Start metrics publishing."""
        if self._running:
            logger.warning("Metrics publisher already running")
            return
        
        self._running = True
        self._publish_task = asyncio.create_task(self._publish_loop())
        
        logger.info("Metrics publisher started")
    
    async def stop(self):
        """Stop metrics publishing."""
        self._running = False
        
        if self._publish_task:
            self._publish_task.cancel()
            try:
                await self._publish_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Metrics publisher stopped")
    
    async def _publish_loop(self):
        """Main publishing loop."""
        while self._running:
            try:
                # Get current metrics snapshot
                snapshot = self._get_current_snapshot()
                
                # Check if metrics changed (aggregation)
                if self.enable_aggregation and self._snapshot_unchanged(snapshot):
                    await asyncio.sleep(self.publish_interval)
                    continue
                
                # Publish metrics update
                await self._publish_metrics_update(snapshot)
                
                # Update last snapshot
                self._last_snapshot = snapshot
                
                await asyncio.sleep(self.publish_interval)
            
            except Exception as e:
                logger.error(f"Error in publish loop: {e}")
                await asyncio.sleep(self.publish_interval)
    
    def _get_current_snapshot(self) -> UnifiedMetricsSnapshot:
        """Get current metrics snapshot from dashboard."""
        try:
            dashboard_state = self.dashboard.get_current_dashboard_state()
            
            # Extract metrics from dashboard state
            return UnifiedMetricsSnapshot(
                timestamp=datetime.now(),
                collectors_active=dashboard_state.get('collectors_active', 0),
                collectors_total=dashboard_state.get('collectors_total', 0),
                collection_success_rate=dashboard_state.get('collection_success_rate', 0.0),
                avg_collection_time_ms=dashboard_state.get('avg_collection_time_ms', 0.0),
                brain_health_score=dashboard_state.get('brain_health_score', 0.0),
                tier1_performance_ms=dashboard_state.get('tier1_performance_ms', 0.0),
                tier2_performance_ms=dashboard_state.get('tier2_performance_ms', 0.0),
                tier3_performance_ms=dashboard_state.get('tier3_performance_ms', 0.0),
                cache_hit_rate=dashboard_state.get('cache_hit_rate', 0.0),
                cache_memory_mb=dashboard_state.get('cache_memory_mb', 0.0),
                memory_usage_mb=dashboard_state.get('memory_usage_mb', 0.0),
                memory_pressure=dashboard_state.get('memory_pressure', 'normal'),
                templates_used_24h=dashboard_state.get('templates_used_24h', 0),
                avg_template_response_time_ms=dashboard_state.get('avg_template_response_time_ms', 0.0),
                template_success_rate=dashboard_state.get('template_success_rate', 0.0),
                tokens_used_24h=dashboard_state.get('tokens_used_24h', 0),
                token_optimization_rate=dashboard_state.get('token_optimization_rate', 0.0),
                estimated_cost_24h=dashboard_state.get('estimated_cost_24h', 0.0),
                workspace_health_score=dashboard_state.get('workspace_health_score', 0.0),
                files_monitored=dashboard_state.get('files_monitored', 0),
                build_status=dashboard_state.get('build_status', 'unknown'),
                test_coverage=dashboard_state.get('test_coverage', 0.0),
                active_alerts=dashboard_state.get('active_alerts', [])
            )
        
        except Exception as e:
            logger.error(f"Error getting metrics snapshot: {e}")
            # Return empty snapshot
            return UnifiedMetricsSnapshot(
                timestamp=datetime.now(),
                collectors_active=0,
                collectors_total=0,
                collection_success_rate=0.0,
                avg_collection_time_ms=0.0,
                brain_health_score=0.0,
                tier1_performance_ms=0.0,
                tier2_performance_ms=0.0,
                tier3_performance_ms=0.0,
                cache_hit_rate=0.0,
                cache_memory_mb=0.0,
                memory_usage_mb=0.0,
                memory_pressure='unknown',
                templates_used_24h=0,
                avg_template_response_time_ms=0.0,
                template_success_rate=0.0,
                tokens_used_24h=0,
                token_optimization_rate=0.0,
                estimated_cost_24h=0.0,
                workspace_health_score=0.0,
                files_monitored=0,
                build_status='unknown',
                test_coverage=0.0,
                active_alerts=[]
            )
    
    def _snapshot_unchanged(self, snapshot: UnifiedMetricsSnapshot) -> bool:
        """Check if snapshot is unchanged from last snapshot."""
        if not self._last_snapshot:
            return False
        
        # Compare key metrics
        return (
            snapshot.brain_health_score == self._last_snapshot.brain_health_score and
            snapshot.cache_hit_rate == self._last_snapshot.cache_hit_rate and
            snapshot.memory_pressure == self._last_snapshot.memory_pressure and
            len(snapshot.active_alerts) == len(self._last_snapshot.active_alerts)
        )
    
    async def _publish_metrics_update(self, snapshot: UnifiedMetricsSnapshot):
        """Publish metrics update to WebSocket clients."""
        if not self.websocket_server:
            # Graceful degradation: No WebSocket server available
            logger.debug("No WebSocket server available, skipping publish")
            return
        
        # Create metrics update message
        message = MetricsUpdate(
            type='metrics_update',
            channel=PublishChannel.METRICS.value,
            timestamp=snapshot.timestamp.isoformat(),
            data={
                'collectors': {
                    'active': snapshot.collectors_active,
                    'total': snapshot.collectors_total,
                    'success_rate': snapshot.collection_success_rate,
                    'avg_time_ms': snapshot.avg_collection_time_ms
                },
                'brain': {
                    'health_score': snapshot.brain_health_score,
                    'tier1_ms': snapshot.tier1_performance_ms,
                    'tier2_ms': snapshot.tier2_performance_ms,
                    'tier3_ms': snapshot.tier3_performance_ms
                },
                'cache': {
                    'hit_rate': snapshot.cache_hit_rate,
                    'memory_mb': snapshot.cache_memory_mb
                },
                'memory': {
                    'usage_mb': snapshot.memory_usage_mb,
                    'pressure': snapshot.memory_pressure
                },
                'templates': {
                    'used_24h': snapshot.templates_used_24h,
                    'avg_response_time_ms': snapshot.avg_template_response_time_ms,
                    'success_rate': snapshot.template_success_rate
                },
                'tokens': {
                    'used_24h': snapshot.tokens_used_24h,
                    'optimization_rate': snapshot.token_optimization_rate,
                    'cost_24h': snapshot.estimated_cost_24h
                },
                'workspace': {
                    'health_score': snapshot.workspace_health_score,
                    'files_monitored': snapshot.files_monitored,
                    'build_status': snapshot.build_status,
                    'test_coverage': snapshot.test_coverage
                },
                'alerts': [
                    {
                        'severity': alert.severity.value,
                        'component': alert.component,
                        'metric': alert.metric,
                        'value': alert.value,
                        'message': alert.message
                    }
                    for alert in snapshot.active_alerts
                ]
            }
        )
        
        # Broadcast to all admin clients
        await self.websocket_server.broadcast(
            asdict(message),
            admin_only=True
        )
    
    async def publish_operation_progress(
        self,
        operation: str,
        progress: float,
        status: str,
        total: Optional[int] = None,
        current: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Publish operation progress update.
        
        Args:
            operation: Operation name (sync, optimize, deploy, etc.)
            progress: Progress percentage (0-100)
            status: Status message
            total: Total items (optional)
            current: Current item (optional)
            metadata: Additional metadata (optional)
        """
        # Create progress update
        progress_update = OperationProgress(
            operation=operation,
            progress=progress,
            total=total,
            current=current,
            status=status,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store in operations dict
        self._operations[operation] = progress_update
        
        # Publish to WebSocket clients
        if self.websocket_server:
            message = MetricsUpdate(
                type='operation_progress',
                channel=PublishChannel.OPERATIONS.value,
                timestamp=progress_update.timestamp.isoformat(),
                data={
                    'operation': operation,
                    'progress': progress,
                    'total': total,
                    'current': current,
                    'status': status,
                    'metadata': metadata or {}
                }
            )
            
            await self.websocket_server.broadcast(
                asdict(message),
                admin_only=True
            )
    
    async def publish_alert(
        self,
        severity: MetricSeverity,
        component: str,
        metric: str,
        value: Any,
        threshold: Any,
        message: str,
        action_required: bool = False
    ):
        """
        Publish alert to WebSocket clients.
        
        Args:
            severity: Alert severity
            component: Component name
            metric: Metric name
            value: Current value
            threshold: Threshold value
            message: Alert message
            action_required: Whether action is required
        """
        if not self.websocket_server:
            return
        
        alert_message = MetricsUpdate(
            type='alert',
            channel=PublishChannel.ALERTS.value,
            timestamp=datetime.now().isoformat(),
            data={
                'severity': severity.value,
                'component': component,
                'metric': metric,
                'value': value,
                'threshold': threshold,
                'message': message,
                'action_required': action_required
            }
        )
        
        await self.websocket_server.broadcast(
            asdict(alert_message),
            admin_only=True
        )
    
    async def publish_health_update(
        self,
        health_score: float,
        components: Dict[str, Any]
    ):
        """
        Publish health update to WebSocket clients.
        
        Args:
            health_score: Overall health score (0-100)
            components: Component health details
        """
        if not self.websocket_server:
            return
        
        health_message = MetricsUpdate(
            type='health_update',
            channel=PublishChannel.HEALTH.value,
            timestamp=datetime.now().isoformat(),
            data={
                'health_score': health_score,
                'components': components
            }
        )
        
        await self.websocket_server.broadcast(
            asdict(health_message),
            admin_only=True
        )
    
    def get_active_operations(self) -> Dict[str, OperationProgress]:
        """Get all active operations."""
        return self._operations.copy()
    
    def clear_completed_operation(self, operation: str):
        """Clear completed operation from tracking."""
        if operation in self._operations:
            del self._operations[operation]


# Example usage
async def main():
    """Example publisher usage."""
    # Create dashboard (assuming already initialized)
    from src.operations.modules.data_integration.real_time_metrics_dashboard import create_real_time_dashboard
    dashboard = create_real_time_dashboard()
    
    # Create WebSocket server
    from src.operations.realtime_dashboard_server import RealtimeDashboardServer
    server = RealtimeDashboardServer(host='0.0.0.0', port=8765)
    await server.start()
    
    # Create publisher
    publisher = RealtimeMetricsPublisher(
        dashboard=dashboard,
        websocket_server=server,
        publish_interval=5.0
    )
    
    try:
        await publisher.start()
        
        # Simulate operation progress
        for i in range(0, 101, 10):
            await publisher.publish_operation_progress(
                operation='sync',
                progress=i,
                status=f'Processing files... {i}%',
                current=i,
                total=100
            )
            await asyncio.sleep(1)
        
        # Keep publisher running
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    
    finally:
        await publisher.stop()
        await server.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
