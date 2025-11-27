"""
CORTEX 3.0 Monitoring Dashboard
==============================

Interactive monitoring dashboard with real-time metrics visualization,
status displays, and alert management for production monitoring.
"""

import time
import threading
import json
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import math


logger = logging.getLogger(__name__)


class DashboardTheme(Enum):
    """Dashboard visual themes."""
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"


class PanelType(Enum):
    """Types of dashboard panels."""
    METRIC_GRAPH = "metric_graph"
    STATUS_INDICATOR = "status_indicator"
    ALERT_LIST = "alert_list"
    HEALTH_SUMMARY = "health_summary"
    LOG_VIEWER = "log_viewer"
    CUSTOM = "custom"


class MetricVisualization(Enum):
    """Metric visualization types."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    GAUGE = "gauge"
    COUNTER = "counter"
    TABLE = "table"


@dataclass
class DashboardPanel:
    """Dashboard panel configuration."""
    id: str
    title: str
    panel_type: PanelType
    position: Dict[str, int]  # {"x": 0, "y": 0, "width": 6, "height": 4}
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    
    # Data source configuration
    data_source: str = "metrics"  # "metrics", "health", "alerts", "logs"
    query: Dict[str, Any] = field(default_factory=dict)
    
    # Display configuration
    refresh_interval_seconds: int = 30
    last_refresh: Optional[float] = None
    
    def needs_refresh(self) -> bool:
        """Check if panel needs data refresh."""
        if self.last_refresh is None:
            return True
        return time.time() - self.last_refresh > self.refresh_interval_seconds


@dataclass
class DashboardLayout:
    """Dashboard layout configuration."""
    id: str
    name: str
    description: str
    panels: List[DashboardPanel] = field(default_factory=list)
    theme: DashboardTheme = DashboardTheme.DARK
    auto_refresh: bool = True
    
    # Grid configuration
    grid_columns: int = 12
    grid_rows: int = 20
    
    # Access control
    created_by: str = "system"
    is_public: bool = True
    allowed_users: List[str] = field(default_factory=list)
    
    def add_panel(self, panel: DashboardPanel) -> None:
        """Add panel to layout."""
        self.panels.append(panel)
    
    def remove_panel(self, panel_id: str) -> bool:
        """Remove panel from layout."""
        for i, panel in enumerate(self.panels):
            if panel.id == panel_id:
                del self.panels[i]
                return True
        return False
    
    def get_panel(self, panel_id: str) -> Optional[DashboardPanel]:
        """Get panel by ID."""
        for panel in self.panels:
            if panel.id == panel_id:
                return panel
        return None


class MonitoringDashboard:
    """
    Interactive monitoring dashboard that provides real-time visualization
    of metrics, health status, alerts, and system information with customizable
    layouts and panels for production monitoring.
    """
    
    def __init__(
        self,
        metrics_collector=None,
        health_monitor=None,
        alert_system=None,
        status_checker=None
    ):
        # Monitoring components (will be injected or use defaults)
        self.metrics_collector = metrics_collector
        self.health_monitor = health_monitor
        self.alert_system = alert_system
        self.status_checker = status_checker
        
        # Dashboard management
        self._layouts: Dict[str, DashboardLayout] = {}
        self._layouts_lock = threading.RLock()
        
        # Dashboard state
        self._current_layout: Optional[str] = None
        self._panel_data_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        
        # Real-time updates
        self._update_active = False
        self._update_thread: Optional[threading.Thread] = None
        
        # Event callbacks
        self._update_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # Initialize default layouts
        self._create_default_layouts()
    
    def start_dashboard(self) -> None:
        """Start dashboard updates."""
        if self._update_active:
            return
        
        self._update_active = True
        self._update_thread = threading.Thread(
            target=self._update_loop,
            daemon=True
        )
        self._update_thread.start()
        
        logger.info("Dashboard updates started")
    
    def stop_dashboard(self) -> None:
        """Stop dashboard updates."""
        self._update_active = False
        if self._update_thread:
            self._update_thread.join(timeout=5.0)
        
        logger.info("Dashboard updates stopped")
    
    def create_layout(
        self,
        layout_id: str,
        name: str,
        description: str = "",
        theme: DashboardTheme = DashboardTheme.DARK
    ) -> DashboardLayout:
        """
        Create a new dashboard layout.
        
        Args:
            layout_id: Unique layout identifier
            name: Layout name
            description: Layout description
            theme: Dashboard theme
            
        Returns:
            Created layout
        """
        layout = DashboardLayout(
            id=layout_id,
            name=name,
            description=description,
            theme=theme
        )
        
        with self._layouts_lock:
            self._layouts[layout_id] = layout
        
        logger.info(f"Created dashboard layout: {layout_id}")
        return layout
    
    def get_layout(self, layout_id: str) -> Optional[DashboardLayout]:
        """Get dashboard layout by ID."""
        with self._layouts_lock:
            return self._layouts.get(layout_id)
    
    def list_layouts(self) -> List[DashboardLayout]:
        """List all dashboard layouts."""
        with self._layouts_lock:
            return list(self._layouts.values())
    
    def set_current_layout(self, layout_id: str) -> bool:
        """Set current active layout."""
        with self._layouts_lock:
            if layout_id in self._layouts:
                self._current_layout = layout_id
                logger.info(f"Switched to layout: {layout_id}")
                return True
            return False
    
    def add_metric_panel(
        self,
        layout_id: str,
        panel_id: str,
        title: str,
        metric_name: str,
        position: Dict[str, int],
        visualization: MetricVisualization = MetricVisualization.LINE_CHART,
        time_range_hours: int = 1
    ) -> bool:
        """
        Add a metric visualization panel to a layout.
        
        Args:
            layout_id: Target layout ID
            panel_id: Unique panel ID
            title: Panel title
            metric_name: Name of metric to display
            position: Panel position and size
            visualization: How to visualize the metric
            time_range_hours: Time range for historical data
            
        Returns:
            True if panel was added
        """
        layout = self.get_layout(layout_id)
        if not layout:
            return False
        
        panel = DashboardPanel(
            id=panel_id,
            title=title,
            panel_type=PanelType.METRIC_GRAPH,
            position=position,
            data_source="metrics",
            config={
                'visualization': visualization.value,
                'time_range_hours': time_range_hours,
                'show_legend': True,
                'show_grid': True
            },
            query={'metric_name': metric_name}
        )
        
        layout.add_panel(panel)
        logger.info(f"Added metric panel {panel_id} to layout {layout_id}")
        return True
    
    def add_status_panel(
        self,
        layout_id: str,
        panel_id: str,
        title: str,
        position: Dict[str, int],
        show_details: bool = True
    ) -> bool:
        """
        Add a status indicator panel to a layout.
        
        Args:
            layout_id: Target layout ID
            panel_id: Unique panel ID
            title: Panel title
            position: Panel position and size
            show_details: Whether to show detailed status info
            
        Returns:
            True if panel was added
        """
        layout = self.get_layout(layout_id)
        if not layout:
            return False
        
        panel = DashboardPanel(
            id=panel_id,
            title=title,
            panel_type=PanelType.STATUS_INDICATOR,
            position=position,
            data_source="health",
            config={
                'show_details': show_details,
                'show_trends': True,
                'compact_view': False
            }
        )
        
        layout.add_panel(panel)
        logger.info(f"Added status panel {panel_id} to layout {layout_id}")
        return True
    
    def add_alert_panel(
        self,
        layout_id: str,
        panel_id: str,
        title: str,
        position: Dict[str, int],
        max_alerts: int = 10,
        severity_filter: Optional[List[str]] = None
    ) -> bool:
        """
        Add an alert list panel to a layout.
        
        Args:
            layout_id: Target layout ID
            panel_id: Unique panel ID
            title: Panel title
            position: Panel position and size
            max_alerts: Maximum number of alerts to display
            severity_filter: Filter alerts by severity
            
        Returns:
            True if panel was added
        """
        layout = self.get_layout(layout_id)
        if not layout:
            return False
        
        panel = DashboardPanel(
            id=panel_id,
            title=title,
            panel_type=PanelType.ALERT_LIST,
            position=position,
            data_source="alerts",
            config={
                'max_alerts': max_alerts,
                'severity_filter': severity_filter or [],
                'show_resolved': False,
                'auto_refresh': True
            }
        )
        
        layout.add_panel(panel)
        logger.info(f"Added alert panel {panel_id} to layout {layout_id}")
        return True
    
    def add_health_summary_panel(
        self,
        layout_id: str,
        panel_id: str,
        title: str,
        position: Dict[str, int]
    ) -> bool:
        """
        Add a health summary panel to a layout.
        
        Args:
            layout_id: Target layout ID
            panel_id: Unique panel ID
            title: Panel title
            position: Panel position and size
            
        Returns:
            True if panel was added
        """
        layout = self.get_layout(layout_id)
        if not layout:
            return False
        
        panel = DashboardPanel(
            id=panel_id,
            title=title,
            panel_type=PanelType.HEALTH_SUMMARY,
            position=position,
            data_source="health",
            config={
                'show_score': True,
                'show_trends': True,
                'show_recommendations': True,
                'compact_view': False
            }
        )
        
        layout.add_panel(panel)
        logger.info(f"Added health summary panel {panel_id} to layout {layout_id}")
        return True
    
    def get_panel_data(self, layout_id: str, panel_id: str) -> Dict[str, Any]:
        """
        Get data for a specific panel.
        
        Args:
            layout_id: Layout ID
            panel_id: Panel ID
            
        Returns:
            Panel data dictionary
        """
        layout = self.get_layout(layout_id)
        if not layout:
            return {'error': 'Layout not found'}
        
        panel = layout.get_panel(panel_id)
        if not panel:
            return {'error': 'Panel not found'}
        
        # Check cache first
        cache_key = f"{layout_id}:{panel_id}"
        if cache_key in self._panel_data_cache:
            cache_time = self._cache_timestamps.get(cache_key, 0)
            if time.time() - cache_time < panel.refresh_interval_seconds:
                return self._panel_data_cache[cache_key]
        
        # Generate fresh data
        data = self._generate_panel_data(panel)
        
        # Cache data
        self._panel_data_cache[cache_key] = data
        self._cache_timestamps[cache_key] = time.time()
        panel.last_refresh = time.time()
        
        return data
    
    def get_layout_data(self, layout_id: str) -> Dict[str, Any]:
        """
        Get data for all panels in a layout.
        
        Args:
            layout_id: Layout ID
            
        Returns:
            Complete layout data
        """
        layout = self.get_layout(layout_id)
        if not layout:
            return {'error': 'Layout not found'}
        
        layout_data = {
            'layout': {
                'id': layout.id,
                'name': layout.name,
                'description': layout.description,
                'theme': layout.theme.value,
                'auto_refresh': layout.auto_refresh,
                'grid_columns': layout.grid_columns,
                'grid_rows': layout.grid_rows
            },
            'panels': {},
            'timestamp': time.time()
        }
        
        # Get data for each panel
        for panel in layout.panels:
            if panel.enabled:
                layout_data['panels'][panel.id] = {
                    'config': {
                        'title': panel.title,
                        'type': panel.panel_type.value,
                        'position': panel.position,
                        'refresh_interval': panel.refresh_interval_seconds
                    },
                    'data': self.get_panel_data(layout_id, panel.id)
                }
        
        return layout_data
    
    def export_layout(self, layout_id: str) -> str:
        """
        Export layout configuration as JSON.
        
        Args:
            layout_id: Layout ID to export
            
        Returns:
            JSON string of layout configuration
        """
        layout = self.get_layout(layout_id)
        if not layout:
            return json.dumps({'error': 'Layout not found'})
        
        export_data = {
            'id': layout.id,
            'name': layout.name,
            'description': layout.description,
            'theme': layout.theme.value,
            'grid_columns': layout.grid_columns,
            'grid_rows': layout.grid_rows,
            'auto_refresh': layout.auto_refresh,
            'panels': [
                {
                    'id': panel.id,
                    'title': panel.title,
                    'panel_type': panel.panel_type.value,
                    'position': panel.position,
                    'data_source': panel.data_source,
                    'query': panel.query,
                    'config': panel.config,
                    'refresh_interval_seconds': panel.refresh_interval_seconds,
                    'enabled': panel.enabled
                }
                for panel in layout.panels
            ]
        }
        
        return json.dumps(export_data, indent=2)
    
    def import_layout(self, layout_json: str) -> bool:
        """
        Import layout configuration from JSON.
        
        Args:
            layout_json: JSON string of layout configuration
            
        Returns:
            True if import was successful
        """
        try:
            layout_data = json.loads(layout_json)
            
            # Create layout
            layout = DashboardLayout(
                id=layout_data['id'],
                name=layout_data['name'],
                description=layout_data.get('description', ''),
                theme=DashboardTheme(layout_data.get('theme', DashboardTheme.DARK.value)),
                auto_refresh=layout_data.get('auto_refresh', True),
                grid_columns=layout_data.get('grid_columns', 12),
                grid_rows=layout_data.get('grid_rows', 20)
            )
            
            # Add panels
            for panel_data in layout_data.get('panels', []):
                panel = DashboardPanel(
                    id=panel_data['id'],
                    title=panel_data['title'],
                    panel_type=PanelType(panel_data['panel_type']),
                    position=panel_data['position'],
                    data_source=panel_data.get('data_source', 'metrics'),
                    query=panel_data.get('query', {}),
                    config=panel_data.get('config', {}),
                    refresh_interval_seconds=panel_data.get('refresh_interval_seconds', 30),
                    enabled=panel_data.get('enabled', True)
                )
                layout.add_panel(panel)
            
            # Store layout
            with self._layouts_lock:
                self._layouts[layout.id] = layout
            
            logger.info(f"Imported dashboard layout: {layout.id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to import layout: {e}")
            return False
    
    def add_update_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add callback for dashboard updates."""
        self._update_callbacks.append(callback)
    
    def _generate_panel_data(self, panel: DashboardPanel) -> Dict[str, Any]:
        """Generate data for a specific panel based on its configuration."""
        try:
            if panel.panel_type == PanelType.METRIC_GRAPH:
                return self._generate_metric_data(panel)
            elif panel.panel_type == PanelType.STATUS_INDICATOR:
                return self._generate_status_data(panel)
            elif panel.panel_type == PanelType.ALERT_LIST:
                return self._generate_alert_data(panel)
            elif panel.panel_type == PanelType.HEALTH_SUMMARY:
                return self._generate_health_summary_data(panel)
            else:
                return {'error': f'Unsupported panel type: {panel.panel_type}'}
        
        except Exception as e:
            logger.error(f"Error generating panel data for {panel.id}: {e}")
            return {'error': str(e)}
    
    def _generate_metric_data(self, panel: DashboardPanel) -> Dict[str, Any]:
        """Generate metric visualization data."""
        if not self.metrics_collector:
            return {'error': 'Metrics collector not available'}
        
        metric_name = panel.query.get('metric_name')
        if not metric_name:
            return {'error': 'No metric name specified'}
        
        # Get metric statistics
        time_range_hours = panel.config.get('time_range_hours', 1)
        window_seconds = time_range_hours * 3600
        
        try:
            stats = self.metrics_collector.get_metric_statistics(metric_name, window_seconds)
            current_value = self.metrics_collector.get_metric_value(metric_name)
            
            visualization = panel.config.get('visualization', MetricVisualization.LINE_CHART.value)
            
            data = {
                'metric_name': metric_name,
                'current_value': current_value,
                'statistics': stats,
                'visualization': visualization,
                'timestamp': time.time()
            }
            
            # Add visualization-specific data
            if visualization == MetricVisualization.GAUGE.value:
                data['gauge'] = {
                    'value': current_value or 0,
                    'min': stats.get('min', 0),
                    'max': stats.get('max', 100),
                    'target': panel.config.get('target_value'),
                    'unit': panel.config.get('unit', '')
                }
            elif visualization == MetricVisualization.COUNTER.value:
                data['counter'] = {
                    'value': current_value or 0,
                    'change': stats.get('average', 0) - current_value if current_value else 0,
                    'unit': panel.config.get('unit', ''),
                    'precision': panel.config.get('precision', 2)
                }
            
            return data
        
        except Exception as e:
            return {'error': f'Failed to get metric data: {e}'}
    
    def _generate_status_data(self, panel: DashboardPanel) -> Dict[str, Any]:
        """Generate status indicator data."""
        if not self.status_checker:
            return {'error': 'Status checker not available'}
        
        try:
            summary = self.status_checker.get_status_summary()
            trends = self.status_checker.get_status_trends(hours=6)
            
            return {
                'overall_status': summary.overall_status.value,
                'health_percentage': summary.health_percentage,
                'component_summary': {
                    'total': summary.total_checks,
                    'operational': summary.operational_checks,
                    'degraded': summary.degraded_checks,
                    'failed': summary.failed_checks,
                    'maintenance': summary.maintenance_checks
                },
                'check_results': {
                    name: result.to_dict() 
                    for name, result in summary.check_results.items()
                },
                'trends': trends,
                'show_details': panel.config.get('show_details', True),
                'timestamp': time.time()
            }
        
        except Exception as e:
            return {'error': f'Failed to get status data: {e}'}
    
    def _generate_alert_data(self, panel: DashboardPanel) -> Dict[str, Any]:
        """Generate alert list data."""
        if not self.alert_system:
            return {'error': 'Alert system not available'}
        
        try:
            active_alerts = self.alert_system.get_active_alerts()
            max_alerts = panel.config.get('max_alerts', 10)
            severity_filter = panel.config.get('severity_filter', [])
            
            # Filter alerts by severity if specified
            if severity_filter:
                filtered_alerts = [
                    alert for alert in active_alerts
                    if alert.severity.value in severity_filter
                ]
            else:
                filtered_alerts = active_alerts
            
            # Sort by severity and timestamp
            severity_priority = {'emergency': 4, 'critical': 3, 'warning': 2, 'info': 1}
            filtered_alerts.sort(
                key=lambda a: (severity_priority.get(a.severity.value, 0), a.created_at),
                reverse=True
            )
            
            # Limit to max_alerts
            displayed_alerts = filtered_alerts[:max_alerts]
            
            # Get alert statistics
            stats = self.alert_system.get_alert_statistics()
            
            return {
                'alerts': [alert.to_dict() for alert in displayed_alerts],
                'total_active': len(active_alerts),
                'total_filtered': len(filtered_alerts),
                'statistics': stats,
                'filters': {
                    'severity': severity_filter,
                    'max_displayed': max_alerts
                },
                'timestamp': time.time()
            }
        
        except Exception as e:
            return {'error': f'Failed to get alert data: {e}'}
    
    def _generate_health_summary_data(self, panel: DashboardPanel) -> Dict[str, Any]:
        """Generate health summary data."""
        if not self.health_monitor:
            return {'error': 'Health monitor not available'}
        
        try:
            report = self.health_monitor.get_system_health_report()
            trends = self.health_monitor.get_health_trends(hours=24)
            
            return {
                'overall_status': report.overall_status.value,
                'health_score': report.health_score,
                'component_summary': {
                    'total': report.component_count,
                    'healthy': report.healthy_components,
                    'warning': report.warning_components,
                    'critical': report.critical_components
                },
                'system_metrics': report.system_metrics,
                'recommendations': report.recommendations,
                'trends': trends,
                'show_score': panel.config.get('show_score', True),
                'show_trends': panel.config.get('show_trends', True),
                'show_recommendations': panel.config.get('show_recommendations', True),
                'timestamp': time.time()
            }
        
        except Exception as e:
            return {'error': f'Failed to get health summary data: {e}'}
    
    def _create_default_layouts(self) -> None:
        """Create default dashboard layouts."""
        # System Overview Layout
        overview_layout = self.create_layout(
            "system_overview",
            "System Overview",
            "Comprehensive system monitoring overview"
        )
        
        # Add panels to overview layout
        self.add_health_summary_panel(
            "system_overview", "health_summary", "System Health",
            {"x": 0, "y": 0, "width": 6, "height": 4}
        )
        
        self.add_status_panel(
            "system_overview", "system_status", "Service Status",
            {"x": 6, "y": 0, "width": 6, "height": 4}
        )
        
        self.add_alert_panel(
            "system_overview", "active_alerts", "Active Alerts",
            {"x": 0, "y": 4, "width": 12, "height": 6}
        )
        
        # Performance Layout
        perf_layout = self.create_layout(
            "performance",
            "Performance Metrics",
            "System performance and resource monitoring"
        )
        
        # Add performance panels (will work when metrics are available)
        self.add_metric_panel(
            "performance", "cpu_usage", "CPU Usage",
            "system.cpu_percent", {"x": 0, "y": 0, "width": 6, "height": 4},
            MetricVisualization.GAUGE
        )
        
        self.add_metric_panel(
            "performance", "memory_usage", "Memory Usage",
            "system.memory_percent", {"x": 6, "y": 0, "width": 6, "height": 4},
            MetricVisualization.GAUGE
        )
        
        # Set default current layout
        self.set_current_layout("system_overview")
        
        logger.info("Created default dashboard layouts")
    
    def _update_loop(self) -> None:
        """Main dashboard update loop."""
        logger.info("Dashboard update loop started")
        
        while self._update_active:
            try:
                # Update data for current layout
                if self._current_layout:
                    layout_data = self.get_layout_data(self._current_layout)
                    
                    # Notify callbacks
                    for callback in self._update_callbacks:
                        try:
                            callback(self._current_layout, layout_data)
                        except Exception as e:
                            logger.warning(f"Dashboard callback error: {e}")
                
                # Wait for next update
                time.sleep(30)  # Update every 30 seconds
            
            except Exception as e:
                logger.error(f"Dashboard update loop error: {e}")
                time.sleep(30)
        
        logger.info("Dashboard update loop stopped")


# Global monitoring dashboard instance
default_monitoring_dashboard = MonitoringDashboard()