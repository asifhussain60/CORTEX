"""
CORTEX 3.0 Performance Monitor
==============================

Real-time performance monitoring and metrics collection for production
documentation generation workflows.
"""

import time
import threading
import psutil
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
import logging
import json
from pathlib import Path
import asyncio


logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: float = field(default_factory=time.time)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    open_files: int = 0
    thread_count: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_used_mb': self.memory_used_mb,
            'memory_available_mb': self.memory_available_mb,
            'disk_io_read_mb': self.disk_io_read_mb,
            'disk_io_write_mb': self.disk_io_write_mb,
            'network_bytes_sent': self.network_bytes_sent,
            'network_bytes_recv': self.network_bytes_recv,
            'open_files': self.open_files,
            'thread_count': self.thread_count
        }


@dataclass
class ApplicationMetrics:
    """Application-specific performance metrics."""
    timestamp: float = field(default_factory=time.time)
    active_requests: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    min_response_time_ms: float = 0.0
    requests_per_second: float = 0.0
    cache_hit_rate: float = 0.0
    cache_size_mb: float = 0.0
    generation_time_ms: float = 0.0
    queue_size: int = 0
    worker_utilization: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'active_requests': self.active_requests,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'avg_response_time_ms': self.avg_response_time_ms,
            'max_response_time_ms': self.max_response_time_ms,
            'min_response_time_ms': self.min_response_time_ms,
            'requests_per_second': self.requests_per_second,
            'cache_hit_rate': self.cache_hit_rate,
            'cache_size_mb': self.cache_size_mb,
            'generation_time_ms': self.generation_time_ms,
            'queue_size': self.queue_size,
            'worker_utilization': self.worker_utilization
        }


@dataclass
class HealthStatus:
    """System health status."""
    status: str = "healthy"  # healthy, warning, critical
    message: str = ""
    checks: Dict[str, bool] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    last_check: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'status': self.status,
            'message': self.message,
            'checks': self.checks,
            'metrics': self.metrics,
            'last_check': self.last_check
        }


class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for production documentation
    generation with real-time metrics, alerting, and health checks.
    """
    
    def __init__(
        self,
        collection_interval: float = 5.0,
        retention_minutes: int = 60,
        alert_thresholds: Optional[Dict[str, float]] = None,
        metrics_file: Optional[str] = None
    ):
        self.collection_interval = collection_interval
        self.retention_minutes = retention_minutes
        self.metrics_file = Path(metrics_file) if metrics_file else None
        
        # Default alert thresholds
        self.alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'avg_response_time_ms': 5000.0,
            'error_rate': 0.1,  # 10%
            'queue_size': 100
        }
        
        # Metrics storage
        max_samples = int((retention_minutes * 60) / collection_interval)
        self.system_metrics: deque[SystemMetrics] = deque(maxlen=max_samples)
        self.app_metrics: deque[ApplicationMetrics] = deque(maxlen=max_samples)
        self.response_times: deque[float] = deque(maxlen=1000)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # Process information
        self._process = psutil.Process()
        self._last_disk_io = None
        self._last_network_io = None
        
        # Request tracking
        self._active_requests = 0
        self._total_requests = 0
        self._successful_requests = 0
        self._failed_requests = 0
        self._start_time = time.time()
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        # Save metrics if file specified
        if self.metrics_file:
            self.export_metrics(str(self.metrics_file))
        
        logger.info("Performance monitoring stopped")
    
    def record_request_start(self) -> str:
        """Record the start of a request and return request ID."""
        with self._lock:
            self._active_requests += 1
            self._total_requests += 1
            request_id = f"req-{self._total_requests}-{int(time.time() * 1000)}"
        
        return request_id
    
    def record_request_end(
        self,
        request_id: str,
        success: bool = True,
        response_time_ms: Optional[float] = None
    ) -> None:
        """Record the completion of a request."""
        with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
            
            if success:
                self._successful_requests += 1
            else:
                self._failed_requests += 1
            
            if response_time_ms is not None:
                self.response_times.append(response_time_ms)
    
    def get_current_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_used_mb = (memory.total - memory.available) / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_io_read_mb = 0.0
            disk_io_write_mb = 0.0
            
            if disk_io and self._last_disk_io:
                read_diff = disk_io.read_bytes - self._last_disk_io.read_bytes
                write_diff = disk_io.write_bytes - self._last_disk_io.write_bytes
                disk_io_read_mb = read_diff / (1024 * 1024)
                disk_io_write_mb = write_diff / (1024 * 1024)
            
            if disk_io:
                self._last_disk_io = disk_io
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_bytes_sent = 0
            network_bytes_recv = 0
            
            if network_io and self._last_network_io:
                network_bytes_sent = network_io.bytes_sent - self._last_network_io.bytes_sent
                network_bytes_recv = network_io.bytes_recv - self._last_network_io.bytes_recv
            
            if network_io:
                self._last_network_io = network_io
            
            # Process-specific metrics
            open_files = len(self._process.open_files())
            thread_count = self._process.num_threads()
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_io_read_mb=disk_io_read_mb,
                disk_io_write_mb=disk_io_write_mb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                open_files=open_files,
                thread_count=thread_count
            )
        
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
            return SystemMetrics()
    
    def get_current_app_metrics(self) -> ApplicationMetrics:
        """Get current application metrics."""
        with self._lock:
            # Calculate response time statistics
            avg_response_time = 0.0
            max_response_time = 0.0
            min_response_time = 0.0
            
            if self.response_times:
                avg_response_time = sum(self.response_times) / len(self.response_times)
                max_response_time = max(self.response_times)
                min_response_time = min(self.response_times)
            
            # Calculate requests per second
            uptime = time.time() - self._start_time
            requests_per_second = self._total_requests / uptime if uptime > 0 else 0.0
            
            return ApplicationMetrics(
                active_requests=self._active_requests,
                total_requests=self._total_requests,
                successful_requests=self._successful_requests,
                failed_requests=self._failed_requests,
                avg_response_time_ms=avg_response_time,
                max_response_time_ms=max_response_time,
                min_response_time_ms=min_response_time,
                requests_per_second=requests_per_second
            )
    
    def update_app_metrics(self, **kwargs) -> None:
        """Update application-specific metrics."""
        if not self.app_metrics:
            return
        
        latest_metrics = self.app_metrics[-1]
        
        # Update specific fields
        for key, value in kwargs.items():
            if hasattr(latest_metrics, key):
                setattr(latest_metrics, key, value)
    
    def get_health_status(self) -> HealthStatus:
        """Get current system health status."""
        status = HealthStatus()
        
        # Get latest metrics
        current_system = self.get_current_system_metrics()
        current_app = self.get_current_app_metrics()
        
        # Health checks
        checks = {
            'cpu_normal': current_system.cpu_percent < self.alert_thresholds['cpu_percent'],
            'memory_normal': current_system.memory_percent < self.alert_thresholds['memory_percent'],
            'response_time_normal': current_app.avg_response_time_ms < self.alert_thresholds['avg_response_time_ms'],
            'error_rate_normal': True,  # Will calculate below
            'queue_normal': current_app.queue_size < self.alert_thresholds['queue_size']
        }
        
        # Calculate error rate
        if current_app.total_requests > 0:
            error_rate = current_app.failed_requests / current_app.total_requests
            checks['error_rate_normal'] = error_rate < self.alert_thresholds['error_rate']
        
        status.checks = checks
        
        # Determine overall status
        if all(checks.values()):
            status.status = "healthy"
            status.message = "All systems operating normally"
        elif any(not check for check in checks.values()):
            status.status = "warning"
            failed_checks = [name for name, passed in checks.items() if not passed]
            status.message = f"Warning conditions: {', '.join(failed_checks)}"
        else:
            status.status = "critical"
            status.message = "Critical system conditions detected"
        
        # Add key metrics
        status.metrics = {
            'cpu_percent': current_system.cpu_percent,
            'memory_percent': current_system.memory_percent,
            'avg_response_time_ms': current_app.avg_response_time_ms,
            'requests_per_second': current_app.requests_per_second,
            'error_rate': current_app.failed_requests / max(current_app.total_requests, 1)
        }
        
        return status
    
    def get_metrics_summary(self, minutes: int = 10) -> Dict[str, Any]:
        """Get summarized metrics for the last N minutes."""
        cutoff_time = time.time() - (minutes * 60)
        
        # Filter recent metrics
        recent_system = [m for m in self.system_metrics if m.timestamp > cutoff_time]
        recent_app = [m for m in self.app_metrics if m.timestamp > cutoff_time]
        
        summary = {
            'timeframe_minutes': minutes,
            'sample_count': len(recent_system),
            'system': {},
            'application': {}
        }
        
        if recent_system:
            summary['system'] = {
                'avg_cpu_percent': sum(m.cpu_percent for m in recent_system) / len(recent_system),
                'max_cpu_percent': max(m.cpu_percent for m in recent_system),
                'avg_memory_percent': sum(m.memory_percent for m in recent_system) / len(recent_system),
                'max_memory_percent': max(m.memory_percent for m in recent_system),
                'total_disk_read_mb': sum(m.disk_io_read_mb for m in recent_system),
                'total_disk_write_mb': sum(m.disk_io_write_mb for m in recent_system)
            }
        
        if recent_app:
            summary['application'] = {
                'total_requests': recent_app[-1].total_requests - recent_app[0].total_requests,
                'avg_response_time_ms': sum(m.avg_response_time_ms for m in recent_app) / len(recent_app),
                'max_response_time_ms': max(m.max_response_time_ms for m in recent_app),
                'avg_requests_per_second': sum(m.requests_per_second for m in recent_app) / len(recent_app)
            }
        
        return summary
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add alert callback function."""
        self._alert_callbacks.append(callback)
    
    def remove_alert_callback(self, callback: Callable) -> None:
        """Remove alert callback function."""
        if callback in self._alert_callbacks:
            self._alert_callbacks.remove(callback)
    
    def export_metrics(self, filepath: str, format: str = "json") -> bool:
        """Export collected metrics to file."""
        try:
            data = {
                'export_time': time.time(),
                'collection_interval': self.collection_interval,
                'system_metrics': [m.to_dict() for m in self.system_metrics],
                'application_metrics': [m.to_dict() for m in self.app_metrics],
                'alert_thresholds': self.alert_thresholds
            }
            
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Metrics exported to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return False
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        logger.info("Performance monitoring loop started")
        
        while self._monitoring:
            try:
                # Collect metrics
                system_metrics = self.get_current_system_metrics()
                app_metrics = self.get_current_app_metrics()
                
                with self._lock:
                    self.system_metrics.append(system_metrics)
                    self.app_metrics.append(app_metrics)
                
                # Check for alerts
                self._check_alerts(system_metrics, app_metrics)
                
                time.sleep(self.collection_interval)
            
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.collection_interval)
        
        logger.info("Performance monitoring loop stopped")
    
    def _check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics) -> None:
        """Check metrics against alert thresholds."""
        alerts = []
        
        # System alerts
        if system_metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {system_metrics.cpu_percent:.1f}%")
        
        if system_metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {system_metrics.memory_percent:.1f}%")
        
        # Application alerts
        if app_metrics.avg_response_time_ms > self.alert_thresholds['avg_response_time_ms']:
            alerts.append(f"High response time: {app_metrics.avg_response_time_ms:.1f}ms")
        
        if app_metrics.queue_size > self.alert_thresholds['queue_size']:
            alerts.append(f"Large queue size: {app_metrics.queue_size}")
        
        # Error rate alert
        if app_metrics.total_requests > 0:
            error_rate = app_metrics.failed_requests / app_metrics.total_requests
            if error_rate > self.alert_thresholds['error_rate']:
                alerts.append(f"High error rate: {error_rate:.2%}")
        
        # Trigger alert callbacks
        if alerts:
            alert_data = {
                'timestamp': time.time(),
                'alerts': alerts,
                'system_metrics': system_metrics.to_dict(),
                'app_metrics': app_metrics.to_dict()
            }
            
            for callback in self._alert_callbacks:
                try:
                    callback("performance_alert", alert_data)
                except Exception as e:
                    logger.warning(f"Alert callback error: {e}")


# Global monitor instance
default_monitor = PerformanceMonitor()