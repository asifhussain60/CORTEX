"""
CORTEX 3.0 Metrics Collector
============================

Comprehensive metrics collection system for monitoring system performance,
application metrics, and custom business metrics with persistence and analysis.
"""

import time
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import statistics
from collections import deque, defaultdict
import sqlite3
import os


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"           # Monotonically increasing
    GAUGE = "gauge"              # Current value
    HISTOGRAM = "histogram"       # Distribution of values
    TIMER = "timer"              # Time-based measurements
    RATE = "rate"                # Rate over time


class AggregationType(Enum):
    """Aggregation methods for metrics."""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"


@dataclass
class MetricPoint:
    """Individual metric data point."""
    name: str
    value: Union[int, float]
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'timestamp': self.timestamp,
            'tags': self.tags,
            'metadata': self.metadata
        }


@dataclass
class Metric:
    """Metric configuration and storage."""
    name: str
    metric_type: MetricType
    description: str = ""
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    # Value storage
    current_value: Union[int, float] = 0
    values: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Statistics tracking
    total_count: int = 0
    last_updated: Optional[float] = None
    
    # Rate calculation (for RATE type)
    last_value_for_rate: Optional[float] = None
    last_rate_timestamp: Optional[float] = None
    
    def add_value(self, value: Union[int, float], timestamp: Optional[float] = None) -> None:
        """Add a value to the metric."""
        if timestamp is None:
            timestamp = time.time()
        
        point = MetricPoint(
            name=self.name,
            value=value,
            timestamp=timestamp,
            tags=self.tags.copy()
        )
        
        self.values.append(point)
        self.total_count += 1
        self.last_updated = timestamp
        
        # Update current value based on metric type
        if self.metric_type == MetricType.COUNTER:
            # For counters, we typically want the latest value
            self.current_value = value
        elif self.metric_type == MetricType.GAUGE:
            # For gauges, store the current value
            self.current_value = value
        elif self.metric_type == MetricType.RATE:
            # Calculate rate if we have previous value
            if self.last_value_for_rate is not None and self.last_rate_timestamp is not None:
                time_diff = timestamp - self.last_rate_timestamp
                if time_diff > 0:
                    self.current_value = (value - self.last_value_for_rate) / time_diff
            self.last_value_for_rate = value
            self.last_rate_timestamp = timestamp
        else:
            # For histograms and timers, current_value is the latest
            self.current_value = value
    
    def get_statistics(self, window_seconds: Optional[int] = None) -> Dict[str, float]:
        """Get statistics for the metric."""
        if not self.values:
            return {}
        
        # Filter by time window if specified
        cutoff_time = time.time() - window_seconds if window_seconds else 0
        relevant_values = [
            point.value for point in self.values
            if point.timestamp > cutoff_time
        ]
        
        if not relevant_values:
            return {}
        
        stats = {
            'count': len(relevant_values),
            'min': min(relevant_values),
            'max': max(relevant_values),
            'sum': sum(relevant_values),
            'average': statistics.mean(relevant_values)
        }
        
        # Add percentiles if we have enough data
        if len(relevant_values) >= 2:
            sorted_values = sorted(relevant_values)
            stats['median'] = statistics.median(sorted_values)
            
        if len(relevant_values) >= 20:  # Need reasonable sample size for percentiles
            stats['p95'] = self._percentile(relevant_values, 95)
            stats['p99'] = self._percentile(relevant_values, 99)
        
        return stats
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        
        # Linear interpolation
        lower_index = int(index)
        upper_index = lower_index + 1
        
        if upper_index >= len(sorted_values):
            return sorted_values[-1]
        
        weight = index - lower_index
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight


@dataclass
class MetricAlert:
    """Metric-based alert configuration."""
    name: str
    metric_name: str
    condition: str  # "greater_than", "less_than", "equals"
    threshold: float
    window_seconds: int = 300  # 5 minutes
    evaluation_interval: int = 60  # 1 minute
    enabled: bool = True
    
    # Alert state
    is_firing: bool = False
    last_triggered: Optional[float] = None
    trigger_count: int = 0


class MetricsCollector:
    """
    Comprehensive metrics collection system that manages metrics registration,
    collection, aggregation, and storage with alerts and persistence.
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        auto_persist: bool = True,
        persist_interval: int = 300,  # 5 minutes
        enable_alerts: bool = True,
        max_metric_age_hours: int = 24
    ):
        self.storage_path = storage_path or "cortex_metrics.db"
        self.auto_persist = auto_persist
        self.persist_interval = persist_interval
        self.enable_alerts = enable_alerts
        self.max_metric_age_hours = max_metric_age_hours
        
        # Metrics registry
        self._metrics: Dict[str, Metric] = {}
        self._metrics_lock = threading.RLock()
        
        # Alert system
        self._alerts: Dict[str, MetricAlert] = {}
        self._alert_callbacks: List[Callable[[MetricAlert, float], None]] = []
        
        # Collection state
        self._collection_active = False
        self._collection_thread: Optional[threading.Thread] = None
        
        # Persistence
        self._last_persist_time = time.time()
        
        # Aggregation cache
        self._aggregation_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_expiry: Dict[str, float] = {}
        
        # Initialize storage
        if self.auto_persist:
            self._init_storage()
    
    def start_collection(self) -> None:
        """Start automatic metrics collection and persistence."""
        if self._collection_active:
            return
        
        self._collection_active = True
        self._collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        self._collection_thread.start()
        
        logger.info("Metrics collection started")
    
    def stop_collection(self) -> None:
        """Stop metrics collection."""
        self._collection_active = False
        if self._collection_thread:
            self._collection_thread.join(timeout=5.0)
        
        # Final persistence
        if self.auto_persist:
            self._persist_metrics()
        
        logger.info("Metrics collection stopped")
    
    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        unit: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> Metric:
        """
        Register a new metric for collection.
        
        Args:
            name: Unique metric name
            metric_type: Type of metric
            description: Metric description
            unit: Measurement unit
            tags: Additional tags
            
        Returns:
            Registered metric instance
        """
        with self._metrics_lock:
            if name in self._metrics:
                return self._metrics[name]
            
            metric = Metric(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit,
                tags=tags or {}
            )
            
            self._metrics[name] = metric
            
        logger.info(f"Registered metric: {name} ({metric_type.value})")
        return metric
    
    def record_value(
        self,
        metric_name: str,
        value: Union[int, float],
        timestamp: Optional[float] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a value for a metric.
        
        Args:
            metric_name: Name of metric to record
            value: Value to record
            timestamp: Optional timestamp (defaults to current time)
            tags: Additional tags for this measurement
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self._metrics_lock:
            metric = self._metrics.get(metric_name)
            if not metric:
                logger.warning(f"Metric {metric_name} not registered")
                return
            
            # Add tags if provided
            point_tags = metric.tags.copy()
            if tags:
                point_tags.update(tags)
            
            # Create metric point
            point = MetricPoint(
                name=metric_name,
                value=value,
                timestamp=timestamp,
                tags=point_tags
            )
            
            # Add to metric
            metric.add_value(value, timestamp)
        
        # Clear relevant cache
        self._invalidate_cache(metric_name)
        
        # Check alerts
        if self.enable_alerts:
            self._check_alerts(metric_name, value, timestamp)
    
    def increment_counter(
        self,
        counter_name: str,
        amount: Union[int, float] = 1,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Increment a counter metric.
        
        Args:
            counter_name: Name of counter
            amount: Amount to increment
            tags: Additional tags
        """
        with self._metrics_lock:
            metric = self._metrics.get(counter_name)
            if metric and metric.metric_type == MetricType.COUNTER:
                new_value = metric.current_value + amount
                self.record_value(counter_name, new_value, tags=tags)
            else:
                # Auto-register counter if it doesn't exist
                self.register_metric(counter_name, MetricType.COUNTER)
                self.record_value(counter_name, amount, tags=tags)
    
    def set_gauge(
        self,
        gauge_name: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Set a gauge metric value.
        
        Args:
            gauge_name: Name of gauge
            value: Current value
            tags: Additional tags
        """
        # Auto-register gauge if it doesn't exist
        if gauge_name not in self._metrics:
            self.register_metric(gauge_name, MetricType.GAUGE)
        
        self.record_value(gauge_name, value, tags=tags)
    
    def record_timer(
        self,
        timer_name: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a timer measurement.
        
        Args:
            timer_name: Name of timer
            duration_ms: Duration in milliseconds
            tags: Additional tags
        """
        # Auto-register timer if it doesn't exist
        if timer_name not in self._metrics:
            self.register_metric(timer_name, MetricType.TIMER, unit="ms")
        
        self.record_value(timer_name, duration_ms, tags=tags)
    
    def time_operation(self, operation_name: str, tags: Optional[Dict[str, str]] = None):
        """
        Context manager for timing operations.
        
        Args:
            operation_name: Name of operation to time
            tags: Additional tags
        """
        return TimerContext(self, operation_name, tags)
    
    def get_metric_value(self, metric_name: str) -> Optional[Union[int, float]]:
        """Get current value of a metric."""
        with self._metrics_lock:
            metric = self._metrics.get(metric_name)
            return metric.current_value if metric else None
    
    def get_metric_statistics(
        self,
        metric_name: str,
        window_seconds: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Get statistics for a metric.
        
        Args:
            metric_name: Name of metric
            window_seconds: Time window for statistics
            
        Returns:
            Statistics dictionary
        """
        # Check cache
        cache_key = f"{metric_name}:{window_seconds}"
        if cache_key in self._aggregation_cache:
            if self._cache_expiry.get(cache_key, 0) > time.time():
                return self._aggregation_cache[cache_key]
        
        with self._metrics_lock:
            metric = self._metrics.get(metric_name)
            if not metric:
                return {}
            
            stats = metric.get_statistics(window_seconds)
        
        # Cache results for 30 seconds
        self._aggregation_cache[cache_key] = stats
        self._cache_expiry[cache_key] = time.time() + 30
        
        return stats
    
    def get_all_metrics_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary of all metrics."""
        summary = {}
        
        with self._metrics_lock:
            for name, metric in self._metrics.items():
                summary[name] = {
                    'type': metric.metric_type.value,
                    'description': metric.description,
                    'unit': metric.unit,
                    'current_value': metric.current_value,
                    'total_count': metric.total_count,
                    'last_updated': metric.last_updated,
                    'tags': metric.tags,
                    'recent_stats': metric.get_statistics(window_seconds=300)  # 5 minutes
                }
        
        return summary
    
    def register_alert(
        self,
        alert_name: str,
        metric_name: str,
        condition: str,
        threshold: float,
        window_seconds: int = 300,
        evaluation_interval: int = 60
    ) -> None:
        """
        Register a metric-based alert.
        
        Args:
            alert_name: Unique alert name
            metric_name: Metric to monitor
            condition: Alert condition ("greater_than", "less_than", "equals")
            threshold: Threshold value
            window_seconds: Evaluation window
            evaluation_interval: How often to evaluate
        """
        alert = MetricAlert(
            name=alert_name,
            metric_name=metric_name,
            condition=condition,
            threshold=threshold,
            window_seconds=window_seconds,
            evaluation_interval=evaluation_interval
        )
        
        self._alerts[alert_name] = alert
        logger.info(f"Registered alert: {alert_name} for metric {metric_name}")
    
    def add_alert_callback(self, callback: Callable[[MetricAlert, float], None]) -> None:
        """Add callback for alert notifications."""
        self._alert_callbacks.append(callback)
    
    def export_metrics(
        self,
        format_type: str = "json",
        time_range_hours: Optional[int] = None
    ) -> str:
        """
        Export metrics in specified format.
        
        Args:
            format_type: Export format ("json", "prometheus", "csv")
            time_range_hours: Optional time range filter
            
        Returns:
            Formatted metrics data
        """
        if format_type == "json":
            return self._export_json(time_range_hours)
        elif format_type == "prometheus":
            return self._export_prometheus()
        elif format_type == "csv":
            return self._export_csv(time_range_hours)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def _init_storage(self) -> None:
        """Initialize SQLite storage for metrics persistence."""
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    tags TEXT,
                    metadata TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            """)
            
            # Create index for efficient queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
                ON metrics(name, timestamp)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Initialized metrics storage: {self.storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize metrics storage: {e}")
    
    def _persist_metrics(self) -> None:
        """Persist metrics to storage."""
        if not self.auto_persist:
            return
        
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            with self._metrics_lock:
                for metric in self._metrics.values():
                    # Only persist recent values to avoid overwhelming storage
                    recent_points = [
                        point for point in metric.values
                        if point.timestamp > self._last_persist_time
                    ]
                    
                    for point in recent_points:
                        cursor.execute("""
                            INSERT INTO metrics (name, value, timestamp, tags, metadata)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            point.name,
                            point.value,
                            point.timestamp,
                            json.dumps(point.tags),
                            json.dumps(point.metadata)
                        ))
            
            # Clean up old metrics
            cutoff_time = time.time() - (self.max_metric_age_hours * 3600)
            cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_time,))
            
            conn.commit()
            conn.close()
            
            self._last_persist_time = time.time()
            
        except Exception as e:
            logger.error(f"Failed to persist metrics: {e}")
    
    def _check_alerts(self, metric_name: str, value: float, timestamp: float) -> None:
        """Check if any alerts should be triggered."""
        for alert in self._alerts.values():
            if alert.metric_name != metric_name or not alert.enabled:
                continue
            
            try:
                should_fire = False
                
                if alert.condition == "greater_than":
                    should_fire = value > alert.threshold
                elif alert.condition == "less_than":
                    should_fire = value < alert.threshold
                elif alert.condition == "equals":
                    should_fire = abs(value - alert.threshold) < 0.001
                
                if should_fire and not alert.is_firing:
                    alert.is_firing = True
                    alert.last_triggered = timestamp
                    alert.trigger_count += 1
                    
                    # Notify callbacks
                    for callback in self._alert_callbacks:
                        try:
                            callback(alert, value)
                        except Exception as e:
                            logger.warning(f"Alert callback error: {e}")
                    
                    logger.warning(f"Alert triggered: {alert.name} (value={value})")
                
                elif not should_fire and alert.is_firing:
                    alert.is_firing = False
                    logger.info(f"Alert resolved: {alert.name}")
            
            except Exception as e:
                logger.error(f"Alert check error for {alert.name}: {e}")
    
    def _invalidate_cache(self, metric_name: str) -> None:
        """Invalidate aggregation cache for a metric."""
        keys_to_remove = [
            key for key in self._aggregation_cache.keys()
            if key.startswith(f"{metric_name}:")
        ]
        
        for key in keys_to_remove:
            self._aggregation_cache.pop(key, None)
            self._cache_expiry.pop(key, None)
    
    def _export_json(self, time_range_hours: Optional[int]) -> str:
        """Export metrics as JSON."""
        cutoff_time = time.time() - (time_range_hours * 3600) if time_range_hours else 0
        
        export_data = {
            'timestamp': time.time(),
            'metrics': {}
        }
        
        with self._metrics_lock:
            for name, metric in self._metrics.items():
                points = [
                    point.to_dict() for point in metric.values
                    if point.timestamp > cutoff_time
                ]
                
                export_data['metrics'][name] = {
                    'type': metric.metric_type.value,
                    'description': metric.description,
                    'unit': metric.unit,
                    'tags': metric.tags,
                    'current_value': metric.current_value,
                    'points': points,
                    'statistics': metric.get_statistics()
                }
        
        return json.dumps(export_data, indent=2)
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        with self._metrics_lock:
            for name, metric in self._metrics.items():
                # Sanitize metric name for Prometheus
                prom_name = name.replace('.', '_').replace('-', '_')
                
                # Add HELP and TYPE
                if metric.description:
                    lines.append(f"# HELP {prom_name} {metric.description}")
                
                metric_type_map = {
                    MetricType.COUNTER: "counter",
                    MetricType.GAUGE: "gauge",
                    MetricType.HISTOGRAM: "histogram",
                    MetricType.TIMER: "histogram"
                }
                prom_type = metric_type_map.get(metric.metric_type, "gauge")
                lines.append(f"# TYPE {prom_name} {prom_type}")
                
                # Add current value with tags
                tag_str = ""
                if metric.tags:
                    tag_pairs = [f'{k}="{v}"' for k, v in metric.tags.items()]
                    tag_str = "{" + ",".join(tag_pairs) + "}"
                
                lines.append(f"{prom_name}{tag_str} {metric.current_value}")
        
        return "\n".join(lines)
    
    def _export_csv(self, time_range_hours: Optional[int]) -> str:
        """Export metrics as CSV."""
        cutoff_time = time.time() - (time_range_hours * 3600) if time_range_hours else 0
        
        lines = ["timestamp,metric_name,value,tags"]
        
        with self._metrics_lock:
            for metric in self._metrics.values():
                for point in metric.values:
                    if point.timestamp > cutoff_time:
                        tag_str = json.dumps(point.tags) if point.tags else "{}"
                        lines.append(f"{point.timestamp},{point.name},{point.value},{tag_str}")
        
        return "\n".join(lines)
    
    def _collection_loop(self) -> None:
        """Main metrics collection loop."""
        logger.info("Metrics collection loop started")
        
        while self._collection_active:
            try:
                # Persist metrics if needed
                if self.auto_persist:
                    current_time = time.time()
                    if current_time - self._last_persist_time > self.persist_interval:
                        self._persist_metrics()
                
                # Wait for next iteration
                time.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                time.sleep(60)
        
        logger.info("Metrics collection loop stopped")


class TimerContext:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, operation_name: str, tags: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.operation_name = operation_name
        self.tags = tags
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration_ms = (time.time() - self.start_time) * 1000
            self.collector.record_timer(self.operation_name, duration_ms, self.tags)


# Global metrics collector instance
default_metrics_collector = MetricsCollector()