"""
CORTEX 3.0 Phase 2 - Real-Time Metrics Dashboard
===============================================

Real-time metrics dashboard integrating Phase 1 data collectors with Phase 2 brain optimization.
Provides unified monitoring, health scoring, and performance analytics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Data Collection Integration (Task 3)
Integration: Phase 1 Data Collectors + Phase 2 Brain Optimization
"""

import time
import threading
import json
import sqlite3
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import logging
from enum import Enum

# Import Phase 1 data collectors
try:
    from src.collectors.manager import CollectorManager, get_collector_manager
    from src.collectors.base_collector import CollectorMetric, CollectorHealth, CollectorStatus
    from src.collectors.brain_performance_collector import BrainPerformanceCollector
    from src.collectors.response_template_collector import ResponseTemplateMetricsCollector
    from src.collectors.token_usage_collector import TokenUsageCollector
    from src.collectors.workspace_health_collector import WorkspaceHealthCollector
except ImportError:
    # Fallback for testing
    CollectorManager = None
    CollectorMetric = None
    CollectorHealth = None
    CollectorStatus = None

# Import Phase 2 brain optimization
try:
    from src.operations.modules.brain.brain_performance_integration import (
        IntegratedBrainPerformanceSystem, 
        BrainPerformanceSnapshot,
        create_optimized_brain_system
    )
    from src.operations.modules.brain.optimization_engine import BrainOptimizationEngine
    from src.operations.modules.brain.query_cache import SmartQueryCache, CacheMetrics
    from src.operations.modules.brain.memory_manager import BrainMemoryManager, MemoryMetrics
except ImportError:
    # Fallback for testing
    IntegratedBrainPerformanceSystem = None
    BrainPerformanceSnapshot = None


class DashboardStatus(Enum):
    """Dashboard status levels"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    STOPPED = "stopped"


class MetricSeverity(Enum):
    """Metric severity levels"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DashboardAlert:
    """Dashboard alert data structure"""
    timestamp: datetime
    severity: MetricSeverity
    component: str
    metric: str
    value: Union[float, int, str]
    threshold: Union[float, int, str]
    message: str
    action_required: bool = False


@dataclass
class UnifiedMetricsSnapshot:
    """Unified snapshot of all CORTEX metrics"""
    timestamp: datetime
    
    # Phase 1 Data Collector Metrics
    collectors_active: int
    collectors_total: int
    collection_success_rate: float
    avg_collection_time_ms: float
    
    # Brain Performance Metrics  
    brain_health_score: float
    tier1_performance_ms: float
    tier2_performance_ms: float
    tier3_performance_ms: float
    
    # Optimization Metrics
    cache_hit_rate: float
    cache_memory_mb: float
    memory_usage_mb: float
    memory_pressure: str
    
    # Template Usage Metrics
    templates_used_24h: int
    avg_template_response_time_ms: float
    template_success_rate: float
    
    # Token Usage Metrics
    tokens_used_24h: int
    token_optimization_rate: float
    estimated_cost_24h: float
    
    # Workspace Health Metrics
    workspace_health_score: float
    files_monitored: int
    build_status: str
    test_coverage: float
    
    # System Alerts
    active_alerts: List[DashboardAlert]


class RealTimeMetricsDashboard:
    """
    Real-time metrics dashboard for CORTEX 3.0.
    
    Integrates Phase 1 data collectors with Phase 2 brain optimization
    to provide unified monitoring, alerting, and performance analytics.
    
    Features:
    - Unified metrics collection from all components
    - Real-time health monitoring with alerting
    - Performance trend analysis
    - Optimization recommendations
    - Historical data storage
    """
    
    def __init__(self, 
                 brain_path: str = None,
                 workspace_path: str = None,
                 dashboard_config: Dict[str, Any] = None):
        """
        Initialize real-time metrics dashboard.
        
        Args:
            brain_path: Path to CORTEX brain directory
            workspace_path: Path to workspace
            dashboard_config: Dashboard configuration
        """
        self.brain_path = brain_path or "cortex-brain"
        self.workspace_path = workspace_path or "."
        self.config = dashboard_config or self._default_config()
        
        # Initialize logger early
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Phase 1 collector manager
        self.collector_manager = None
        self._initialize_collectors()
        
        # Initialize Phase 2 brain optimization system
        self.brain_system = None
        self._initialize_brain_system()
        
        # Dashboard state
        self.status = DashboardStatus.INITIALIZING
        self.dashboard_start_time = datetime.now()
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Metrics storage
        self.metrics_snapshots: List[UnifiedMetricsSnapshot] = []
        self.active_alerts: List[DashboardAlert] = []
        self.performance_trends = {
            'brain_health': [],
            'collection_success': [],
            'cache_performance': [],
            'memory_usage': [],
            'template_usage': []
        }
        
        # Historical data storage
        self.db_path = Path(self.brain_path) / "metrics" / "dashboard_metrics.db"
        self._initialize_database()
        
        # Alerting thresholds
        self.alert_thresholds = self.config.get('alert_thresholds', {
            'brain_health_critical': 60,
            'brain_health_warning': 80,
            'collection_success_critical': 0.7,
            'collection_success_warning': 0.9,
            'tier1_slow_critical': 100,
            'tier1_slow_warning': 60,
            'tier2_slow_critical': 300,
            'tier2_slow_warning': 200,
            'tier3_slow_critical': 400,
            'tier3_slow_warning': 250,
            'cache_hit_low_critical': 0.5,
            'cache_hit_low_warning': 0.7,
            'memory_usage_high_critical': 180,  # MB
            'memory_usage_high_warning': 150,   # MB
            'template_response_slow_warning': 100,  # ms
            'workspace_health_low_warning': 70
        })
        
        # Logger already initialized earlier
        self.logger.info("Real-time metrics dashboard initialized")
        
        # Auto-start monitoring if configured
        if self.config.get('auto_start', True):
            self.start_monitoring()
    
    def _default_config(self) -> Dict[str, Any]:
        """Get default dashboard configuration."""
        return {
            'auto_start': True,
            'monitoring_interval_seconds': 30,
            'snapshot_retention_hours': 72,
            'alert_retention_hours': 24,
            'enable_database_storage': True,
            'enable_web_interface': False,  # Future enhancement
            'alert_thresholds': {},
            'performance_targets': {
                'tier1_target_ms': 50,
                'tier2_target_ms': 150,
                'tier3_target_ms': 200,
                'collection_target_success_rate': 0.95,
                'cache_target_hit_rate': 0.8,
                'brain_target_health': 90
            }
        }
    
    def _initialize_collectors(self):
        """Initialize Phase 1 data collectors."""
        try:
            if CollectorManager:
                self.collector_manager = get_collector_manager(
                    brain_path=self.brain_path,
                    workspace_path=self.workspace_path
                )
                
                # Initialize and start collectors
                if self.collector_manager.initialize():
                    self.collector_manager.start_all_collectors()
                    self.logger.info("Phase 1 data collectors initialized successfully")
                else:
                    self.logger.warning("Failed to initialize Phase 1 data collectors")
            else:
                self.logger.warning("Phase 1 data collectors not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize collectors: {e}")
    
    def _initialize_brain_system(self):
        """Initialize Phase 2 brain optimization system."""
        try:
            if IntegratedBrainPerformanceSystem:
                self.brain_system = create_optimized_brain_system(
                    brain_path=self.brain_path,
                    config=self.config.get('brain_config', {})
                )
                self.logger.info("Phase 2 brain optimization system initialized successfully")
            else:
                self.logger.warning("Phase 2 brain optimization system not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize brain system: {e}")
    
    def _initialize_database(self):
        """Initialize historical metrics database."""
        if not self.config.get('enable_database_storage', True):
            return
        
        try:
            # Create metrics directory
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create database tables
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                
                # Metrics snapshots table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    data TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Alerts table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    severity TEXT NOT NULL,
                    component TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    value TEXT NOT NULL,
                    threshold TEXT NOT NULL,
                    message TEXT NOT NULL,
                    action_required BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # Performance trends table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                conn.commit()
                
            self.logger.info(f"Dashboard database initialized: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard database: {e}")
    
    def start_monitoring(self):
        """Start real-time monitoring."""
        if self.monitoring_active:
            return
        
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self.monitoring_active = True
        self.status = DashboardStatus.ACTIVE
        
        self.logger.info("Real-time metrics monitoring started")
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.monitoring_active = False
        self.status = DashboardStatus.STOPPED
        
        # Stop component systems
        if self.brain_system and hasattr(self.brain_system, 'stop_monitoring'):
            self.brain_system.stop_monitoring()
        
        if self.collector_manager:
            self.collector_manager.stop_all_collectors()
        
        self.logger.info("Real-time metrics monitoring stopped")
    
    def get_current_dashboard_state(self) -> Dict[str, Any]:
        """Get current dashboard state and latest metrics."""
        try:
            # Get latest unified snapshot
            latest_snapshot = self.get_unified_metrics_snapshot()
            
            # Calculate uptime
            uptime_seconds = (datetime.now() - self.dashboard_start_time).total_seconds()
            
            # Get system status
            dashboard_state = {
                'dashboard_status': self.status.value,
                'uptime_seconds': uptime_seconds,
                'monitoring_active': self.monitoring_active,
                'last_update': datetime.now().isoformat(),
                
                # Latest metrics
                'latest_metrics': asdict(latest_snapshot) if latest_snapshot else {},
                
                # Component status
                'components': {
                    'collectors': {
                        'available': self.collector_manager is not None,
                        'active': latest_snapshot.collectors_active if latest_snapshot else 0,
                        'total': latest_snapshot.collectors_total if latest_snapshot else 0
                    },
                    'brain_system': {
                        'available': self.brain_system is not None,
                        'optimization_active': (
                            self.brain_system.monitoring_active 
                            if self.brain_system else False
                        )
                    }
                },
                
                # Current alerts
                'alerts': {
                    'total': len(self.active_alerts),
                    'critical': len([a for a in self.active_alerts if a.severity == MetricSeverity.CRITICAL]),
                    'warning': len([a for a in self.active_alerts if a.severity == MetricSeverity.WARNING]),
                    'recent_alerts': [asdict(alert) for alert in self.active_alerts[-5:]]
                },
                
                # Performance summary
                'performance_summary': self._get_performance_summary()
            }
            
            return dashboard_state
            
        except Exception as e:
            self.logger.error(f"Failed to get dashboard state: {e}")
            return {
                'dashboard_status': DashboardStatus.ERROR.value,
                'error': str(e),
                'last_update': datetime.now().isoformat()
            }
    
    def get_unified_metrics_snapshot(self) -> Optional[UnifiedMetricsSnapshot]:
        """Collect unified metrics snapshot from all systems."""
        try:
            timestamp = datetime.now()
            
            # Initialize metric values
            collectors_active = 0
            collectors_total = 0
            collection_success_rate = 0.0
            avg_collection_time_ms = 0.0
            
            brain_health_score = 0.0
            tier1_performance_ms = 0.0
            tier2_performance_ms = 0.0
            tier3_performance_ms = 0.0
            
            cache_hit_rate = 0.0
            cache_memory_mb = 0.0
            memory_usage_mb = 0.0
            memory_pressure = "unknown"
            
            templates_used_24h = 0
            avg_template_response_time_ms = 0.0
            template_success_rate = 0.0
            
            tokens_used_24h = 0
            token_optimization_rate = 0.0
            estimated_cost_24h = 0.0
            
            workspace_health_score = 0.0
            files_monitored = 0
            build_status = "unknown"
            test_coverage = 0.0
            
            # Collect Phase 1 data collector metrics
            if self.collector_manager:
                try:
                    collector_health = self.collector_manager.get_collector_health()
                    collectors_total = len(self.collector_manager.collectors)
                    collectors_active = sum(
                        1 for health in collector_health.values() 
                        if health.status == CollectorStatus.ACTIVE
                    )
                    
                    # Calculate success rate
                    if collector_health:
                        successful_collections = sum(
                            1 for health in collector_health.values() 
                            if health.last_collection_success
                        )
                        collection_success_rate = successful_collections / len(collector_health)
                    
                    # Get collection time metrics
                    all_metrics = self.collector_manager.collect_all_metrics()
                    if all_metrics:
                        collection_times = []
                        for collector_metrics in all_metrics.values():
                            collection_times.extend([
                                getattr(metric, 'collection_time_ms', 0) 
                                for metric in collector_metrics
                            ])
                        if collection_times:
                            avg_collection_time_ms = sum(collection_times) / len(collection_times)
                    
                    # Template metrics
                    if 'response_templates' in self.collector_manager.collectors:
                        template_collector = self.collector_manager.collectors['response_templates']
                        if hasattr(template_collector, 'get_template_summary'):
                            template_summary = template_collector.get_template_summary()
                            templates_used_24h = template_summary.get('usage_count_24h', 0)
                            avg_template_response_time_ms = template_summary.get('avg_response_time_ms', 0.0)
                            template_success_rate = template_summary.get('success_rate', 0.0)
                    
                    # Token metrics
                    if 'token_usage' in self.collector_manager.collectors:
                        token_collector = self.collector_manager.collectors['token_usage']
                        if hasattr(token_collector, 'get_usage_summary'):
                            token_summary = token_collector.get_usage_summary()
                            tokens_used_24h = token_summary.get('total_tokens_24h', 0)
                            token_optimization_rate = token_summary.get('optimization_rate', 0.0)
                            estimated_cost_24h = token_summary.get('estimated_cost_24h', 0.0)
                    
                    # Workspace metrics
                    if 'workspace_health' in self.collector_manager.collectors:
                        workspace_collector = self.collector_manager.collectors['workspace_health']
                        if hasattr(workspace_collector, 'get_workspace_summary'):
                            workspace_summary = workspace_collector.get_workspace_summary()
                            workspace_health_score = workspace_summary.get('health_score', 0.0)
                            files_monitored = workspace_summary.get('files_monitored', 0)
                            build_status = workspace_summary.get('build_status', 'unknown')
                            test_coverage = workspace_summary.get('test_coverage', 0.0)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to collect Phase 1 metrics: {e}")
            
            # Collect Phase 2 brain optimization metrics
            if self.brain_system:
                try:
                    brain_snapshot = self.brain_system.get_unified_performance_snapshot()
                    
                    brain_health_score = brain_snapshot.health_score
                    tier1_performance_ms = brain_snapshot.tier1_avg_ms
                    tier2_performance_ms = brain_snapshot.tier2_avg_ms
                    tier3_performance_ms = brain_snapshot.tier3_avg_ms
                    
                    cache_hit_rate = brain_snapshot.cache_hit_rate
                    cache_memory_mb = brain_snapshot.cache_memory_mb
                    memory_usage_mb = brain_snapshot.total_memory_mb
                    memory_pressure = brain_snapshot.memory_pressure
                    
                except Exception as e:
                    self.logger.warning(f"Failed to collect Phase 2 metrics: {e}")
            
            # Check for alerts
            active_alerts = self._check_and_update_alerts({
                'brain_health_score': brain_health_score,
                'collection_success_rate': collection_success_rate,
                'tier1_performance_ms': tier1_performance_ms,
                'tier2_performance_ms': tier2_performance_ms,
                'tier3_performance_ms': tier3_performance_ms,
                'cache_hit_rate': cache_hit_rate,
                'memory_usage_mb': memory_usage_mb,
                'avg_template_response_time_ms': avg_template_response_time_ms,
                'workspace_health_score': workspace_health_score
            })
            
            # Create unified snapshot
            snapshot = UnifiedMetricsSnapshot(
                timestamp=timestamp,
                collectors_active=collectors_active,
                collectors_total=collectors_total,
                collection_success_rate=collection_success_rate,
                avg_collection_time_ms=avg_collection_time_ms,
                brain_health_score=brain_health_score,
                tier1_performance_ms=tier1_performance_ms,
                tier2_performance_ms=tier2_performance_ms,
                tier3_performance_ms=tier3_performance_ms,
                cache_hit_rate=cache_hit_rate,
                cache_memory_mb=cache_memory_mb,
                memory_usage_mb=memory_usage_mb,
                memory_pressure=memory_pressure,
                templates_used_24h=templates_used_24h,
                avg_template_response_time_ms=avg_template_response_time_ms,
                template_success_rate=template_success_rate,
                tokens_used_24h=tokens_used_24h,
                token_optimization_rate=token_optimization_rate,
                estimated_cost_24h=estimated_cost_24h,
                workspace_health_score=workspace_health_score,
                files_monitored=files_monitored,
                build_status=build_status,
                test_coverage=test_coverage,
                active_alerts=active_alerts
            )
            
            # Store snapshot
            self.metrics_snapshots.append(snapshot)
            
            # Cleanup old snapshots
            cutoff_time = datetime.now() - timedelta(
                hours=self.config.get('snapshot_retention_hours', 72)
            )
            self.metrics_snapshots = [
                s for s in self.metrics_snapshots if s.timestamp >= cutoff_time
            ]
            
            # Update performance trends
            self._update_performance_trends(snapshot)
            
            # Store to database
            self._store_snapshot_to_database(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to create unified metrics snapshot: {e}")
            return None
    
    def _check_and_update_alerts(self, metrics: Dict[str, Any]) -> List[DashboardAlert]:
        """Check metrics against thresholds and update alerts."""
        new_alerts = []
        current_time = datetime.now()
        
        # Brain health alerts
        brain_health = metrics.get('brain_health_score', 0)
        if brain_health < self.alert_thresholds['brain_health_critical']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.CRITICAL,
                component="brain_system",
                metric="health_score",
                value=brain_health,
                threshold=self.alert_thresholds['brain_health_critical'],
                message=f"Brain health critically low: {brain_health:.1f}%",
                action_required=True
            ))
        elif brain_health < self.alert_thresholds['brain_health_warning']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.WARNING,
                component="brain_system",
                metric="health_score",
                value=brain_health,
                threshold=self.alert_thresholds['brain_health_warning'],
                message=f"Brain health below optimal: {brain_health:.1f}%"
            ))
        
        # Collection success rate alerts
        success_rate = metrics.get('collection_success_rate', 0)
        if success_rate < self.alert_thresholds['collection_success_critical']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.CRITICAL,
                component="data_collectors",
                metric="success_rate",
                value=success_rate,
                threshold=self.alert_thresholds['collection_success_critical'],
                message=f"Data collection failing: {success_rate:.1%} success rate",
                action_required=True
            ))
        elif success_rate < self.alert_thresholds['collection_success_warning']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.WARNING,
                component="data_collectors",
                metric="success_rate",
                value=success_rate,
                threshold=self.alert_thresholds['collection_success_warning'],
                message=f"Data collection degraded: {success_rate:.1%} success rate"
            ))
        
        # Tier performance alerts
        tier1_ms = metrics.get('tier1_performance_ms', 0)
        if tier1_ms > self.alert_thresholds['tier1_slow_critical']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.CRITICAL,
                component="brain_system",
                metric="tier1_performance",
                value=tier1_ms,
                threshold=self.alert_thresholds['tier1_slow_critical'],
                message=f"Tier 1 critically slow: {tier1_ms:.1f}ms",
                action_required=True
            ))
        elif tier1_ms > self.alert_thresholds['tier1_slow_warning']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.WARNING,
                component="brain_system",
                metric="tier1_performance",
                value=tier1_ms,
                threshold=self.alert_thresholds['tier1_slow_warning'],
                message=f"Tier 1 performance degraded: {tier1_ms:.1f}ms"
            ))
        
        # Cache hit rate alerts
        cache_hit = metrics.get('cache_hit_rate', 0)
        if cache_hit < self.alert_thresholds['cache_hit_low_critical']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.CRITICAL,
                component="brain_system",
                metric="cache_hit_rate",
                value=cache_hit,
                threshold=self.alert_thresholds['cache_hit_low_critical'],
                message=f"Cache performance critically low: {cache_hit:.1%}",
                action_required=True
            ))
        elif cache_hit < self.alert_thresholds['cache_hit_low_warning']:
            new_alerts.append(DashboardAlert(
                timestamp=current_time,
                severity=MetricSeverity.WARNING,
                component="brain_system",
                metric="cache_hit_rate",
                value=cache_hit,
                threshold=self.alert_thresholds['cache_hit_low_warning'],
                message=f"Cache performance degraded: {cache_hit:.1%}"
            ))
        
        # Add new alerts to active list
        self.active_alerts.extend(new_alerts)
        
        # Clean up old alerts
        alert_cutoff_time = current_time - timedelta(
            hours=self.config.get('alert_retention_hours', 24)
        )
        self.active_alerts = [
            alert for alert in self.active_alerts 
            if alert.timestamp >= alert_cutoff_time
        ]
        
        # Store alerts to database
        for alert in new_alerts:
            self._store_alert_to_database(alert)
        
        return self.active_alerts.copy()
    
    def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from recent metrics."""
        if not self.metrics_snapshots:
            return {'error': 'No metrics available'}
        
        recent_snapshots = self.metrics_snapshots[-10:]  # Last 10 snapshots
        latest_snapshot = self.metrics_snapshots[-1]
        
        targets = self.config.get('performance_targets', {})
        
        summary = {
            'current_performance': {
                'brain_health': {
                    'current': latest_snapshot.brain_health_score,
                    'target': targets.get('brain_target_health', 90),
                    'status': 'good' if latest_snapshot.brain_health_score >= targets.get('brain_target_health', 90) else 'needs_attention'
                },
                'tier1_performance': {
                    'current_ms': latest_snapshot.tier1_performance_ms,
                    'target_ms': targets.get('tier1_target_ms', 50),
                    'status': 'good' if latest_snapshot.tier1_performance_ms <= targets.get('tier1_target_ms', 50) else 'slow'
                },
                'data_collection': {
                    'success_rate': latest_snapshot.collection_success_rate,
                    'target_rate': targets.get('collection_target_success_rate', 0.95),
                    'status': 'good' if latest_snapshot.collection_success_rate >= targets.get('collection_target_success_rate', 0.95) else 'degraded'
                },
                'cache_performance': {
                    'hit_rate': latest_snapshot.cache_hit_rate,
                    'target_rate': targets.get('cache_target_hit_rate', 0.8),
                    'status': 'good' if latest_snapshot.cache_hit_rate >= targets.get('cache_target_hit_rate', 0.8) else 'low'
                }
            },
            'trends': {
                'brain_health_trend': self._calculate_trend([s.brain_health_score for s in recent_snapshots]),
                'tier1_trend': self._calculate_trend([s.tier1_performance_ms for s in recent_snapshots]),
                'collection_trend': self._calculate_trend([s.collection_success_rate for s in recent_snapshots]),
                'cache_trend': self._calculate_trend([s.cache_hit_rate for s in recent_snapshots])
            }
        }
        
        return summary
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from list of values."""
        if len(values) < 2:
            return 'stable'
        
        recent_avg = sum(values[-3:]) / min(3, len(values))
        older_avg = sum(values[:-3]) / max(1, len(values) - 3)
        
        if len(values) < 3:
            recent_avg = values[-1]
            older_avg = values[0]
        
        change_percent = (recent_avg - older_avg) / older_avg if older_avg != 0 else 0
        
        if change_percent > 0.05:
            return 'improving'
        elif change_percent < -0.05:
            return 'declining'
        else:
            return 'stable'
    
    def _update_performance_trends(self, snapshot: UnifiedMetricsSnapshot):
        """Update performance trend tracking."""
        self.performance_trends['brain_health'].append(snapshot.brain_health_score)
        self.performance_trends['collection_success'].append(snapshot.collection_success_rate)
        self.performance_trends['cache_performance'].append(snapshot.cache_hit_rate)
        self.performance_trends['memory_usage'].append(snapshot.memory_usage_mb)
        self.performance_trends['template_usage'].append(snapshot.templates_used_24h)
        
        # Store trends to database
        self._store_trend_to_database(snapshot.timestamp, 'brain_health', snapshot.brain_health_score)
        self._store_trend_to_database(snapshot.timestamp, 'collection_success', snapshot.collection_success_rate)
        self._store_trend_to_database(snapshot.timestamp, 'cache_performance', snapshot.cache_hit_rate)
        
        # Keep only recent trends (last 100 data points)
        for trend_key in self.performance_trends:
            if len(self.performance_trends[trend_key]) > 100:
                self.performance_trends[trend_key] = self.performance_trends[trend_key][-100:]
    
    def _store_snapshot_to_database(self, snapshot: UnifiedMetricsSnapshot):
        """Store snapshot to database."""
        if not self.config.get('enable_database_storage', True):
            return
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO metrics_snapshots (timestamp, data) VALUES (?, ?)",
                    (snapshot.timestamp, json.dumps(asdict(snapshot), default=str))
                )
                conn.commit()
        except Exception as e:
            self.logger.warning(f"Failed to store snapshot to database: {e}")
    
    def _store_alert_to_database(self, alert: DashboardAlert):
        """Store alert to database."""
        if not self.config.get('enable_database_storage', True):
            return
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO alerts 
                       (timestamp, severity, component, metric, value, threshold, message, action_required) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (alert.timestamp, alert.severity.value, alert.component, alert.metric,
                     str(alert.value), str(alert.threshold), alert.message, alert.action_required)
                )
                conn.commit()
        except Exception as e:
            self.logger.warning(f"Failed to store alert to database: {e}")
    
    def _store_trend_to_database(self, timestamp: datetime, metric_name: str, value: float):
        """Store performance trend to database."""
        if not self.config.get('enable_database_storage', True):
            return
        
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO performance_trends (timestamp, metric_name, value) VALUES (?, ?, ?)",
                    (timestamp, metric_name, value)
                )
                conn.commit()
        except Exception as e:
            self.logger.warning(f"Failed to store trend to database: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        self.logger.info("Real-time monitoring loop started")
        
        while not self.stop_monitoring:
            try:
                # Collect unified metrics
                snapshot = self.get_unified_metrics_snapshot()
                
                if snapshot:
                    # Log periodic status
                    if len(self.metrics_snapshots) % 10 == 0:  # Every 10th snapshot
                        self.logger.info(
                            f"Dashboard metrics: "
                            f"Brain Health={snapshot.brain_health_score:.1f}%, "
                            f"Collectors={snapshot.collectors_active}/{snapshot.collectors_total}, "
                            f"Collection Rate={snapshot.collection_success_rate:.1%}, "
                            f"Alerts={len(snapshot.active_alerts)}"
                        )
                
                # Sleep for monitoring interval
                time.sleep(self.config.get('monitoring_interval_seconds', 30))
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(10)  # Wait before retrying
        
        self.logger.info("Real-time monitoring loop stopped")


# Convenience functions for easy dashboard setup
def create_real_time_dashboard(brain_path: str = None, 
                             workspace_path: str = None,
                             config: Dict[str, Any] = None) -> RealTimeMetricsDashboard:
    """
    Create and start real-time metrics dashboard.
    
    Args:
        brain_path: Path to CORTEX brain directory
        workspace_path: Path to workspace
        config: Dashboard configuration
        
    Returns:
        Initialized and running RealTimeMetricsDashboard
    """
    dashboard = RealTimeMetricsDashboard(
        brain_path=brain_path,
        workspace_path=workspace_path,
        dashboard_config=config
    )
    
    return dashboard


def get_dashboard_summary(dashboard: RealTimeMetricsDashboard) -> Dict[str, Any]:
    """
    Get comprehensive dashboard summary.
    
    Args:
        dashboard: Dashboard instance
        
    Returns:
        Dashboard summary with all key metrics
    """
    return dashboard.get_current_dashboard_state()


if __name__ == "__main__":
    # Test the real-time metrics dashboard
    print("🎯 CORTEX 3.0 Phase 2 - Real-Time Metrics Dashboard Test")
    print("=" * 70)
    
    # Create dashboard with test configuration
    test_config = {
        'monitoring_interval_seconds': 10,  # Faster for testing
        'auto_start': True,
        'enable_database_storage': True
    }
    
    dashboard = create_real_time_dashboard(
        brain_path="cortex-brain",
        workspace_path=".",
        config=test_config
    )
    
    print(f"✅ Dashboard created and monitoring started")
    print(f"   Status: {dashboard.status.value}")
    print(f"   Monitoring active: {dashboard.monitoring_active}")
    print()
    
    # Wait for initial data collection
    time.sleep(5)
    
    # Get dashboard state
    dashboard_state = get_dashboard_summary(dashboard)
    
    print("📊 Current Dashboard State:")
    print(f"   Uptime: {dashboard_state['uptime_seconds']:.1f} seconds")
    
    if 'latest_metrics' in dashboard_state and dashboard_state['latest_metrics']:
        metrics = dashboard_state['latest_metrics']
        print(f"   Brain Health: {metrics.get('brain_health_score', 0):.1f}%")
        print(f"   Collectors Active: {metrics.get('collectors_active', 0)}/{metrics.get('collectors_total', 0)}")
        print(f"   Collection Success: {metrics.get('collection_success_rate', 0):.1%}")
        print(f"   Tier 1 Performance: {metrics.get('tier1_performance_ms', 0):.1f}ms")
        print(f"   Cache Hit Rate: {metrics.get('cache_hit_rate', 0):.1%}")
        print(f"   Active Alerts: {len(metrics.get('active_alerts', []))}")
    
    # Show component status
    if 'components' in dashboard_state:
        components = dashboard_state['components']
        print("\n🔧 Component Status:")
        print(f"   Data Collectors: {'✅' if components['collectors']['available'] else '❌'}")
        print(f"   Brain System: {'✅' if components['brain_system']['available'] else '❌'}")
    
    # Show performance summary
    if 'performance_summary' in dashboard_state and 'current_performance' in dashboard_state['performance_summary']:
        perf = dashboard_state['performance_summary']['current_performance']
        print("\n📈 Performance Status:")
        for component, data in perf.items():
            if isinstance(data, dict) and 'status' in data:
                status_icon = "✅" if data['status'] in ['good'] else "⚠️"
                print(f"   {component}: {status_icon} {data['status']}")
    
    print("\n🎯 Real-time metrics dashboard integration complete!")
    print("   Dashboard will continue monitoring in background...")
    print("   Use dashboard.get_current_dashboard_state() for latest metrics")