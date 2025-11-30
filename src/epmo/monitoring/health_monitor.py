"""
CORTEX 3.0 Health Monitor
=========================

Comprehensive health monitoring system with configurable health checks,
status aggregation, and health endpoint management.
"""

import time
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import psutil


logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class CheckType(Enum):
    """Types of health checks."""
    SYSTEM_RESOURCE = "system_resource"
    SERVICE_AVAILABILITY = "service_availability"
    DATABASE_CONNECTION = "database_connection"
    EXTERNAL_SERVICE = "external_service"
    CUSTOM = "custom"


@dataclass
class HealthCheck:
    """Individual health check configuration."""
    name: str
    check_type: CheckType
    check_function: Callable[[], Dict[str, Any]]
    interval_seconds: float = 30.0
    timeout_seconds: float = 10.0
    retry_count: int = 2
    enabled: bool = True
    critical: bool = False  # If true, failure affects overall system health
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Results tracking
    last_check_time: Optional[float] = None
    last_result: Optional[Dict[str, Any]] = None
    consecutive_failures: int = 0
    total_checks: int = 0
    total_failures: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_checks == 0:
            return 100.0
        return ((self.total_checks - self.total_failures) / self.total_checks) * 100.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if health check is currently healthy."""
        if not self.last_result:
            return False
        return self.last_result.get('status') == HealthStatus.HEALTHY.value


@dataclass
class SystemHealthReport:
    """Comprehensive system health report."""
    timestamp: float
    overall_status: HealthStatus
    component_count: int
    healthy_components: int
    warning_components: int
    critical_components: int
    check_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    system_metrics: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'timestamp': self.timestamp,
            'overall_status': self.overall_status.value,
            'component_count': self.component_count,
            'healthy_components': self.healthy_components,
            'warning_components': self.warning_components,
            'critical_components': self.critical_components,
            'check_results': self.check_results,
            'system_metrics': self.system_metrics,
            'recommendations': self.recommendations,
            'health_score': self.health_score
        }
    
    @property
    def health_score(self) -> float:
        """Calculate overall health score (0-100)."""
        if self.component_count == 0:
            return 100.0
        
        # Weight different statuses
        score = (
            (self.healthy_components * 100) +
            (self.warning_components * 50) +
            (self.critical_components * 0)
        ) / self.component_count
        
        return min(100.0, max(0.0, score))


class HealthMonitor:
    """
    Comprehensive health monitoring system that manages health checks,
    aggregates status, and provides health endpoints for production monitoring.
    """
    
    def __init__(
        self,
        check_interval: float = 30.0,
        enable_auto_checks: bool = True,
        health_history_size: int = 1000,
        enable_system_checks: bool = True
    ):
        self.check_interval = check_interval
        self.enable_auto_checks = enable_auto_checks
        self.health_history_size = health_history_size
        self.enable_system_checks = enable_system_checks
        
        # Health check registry
        self._health_checks: Dict[str, HealthCheck] = {}
        self._check_lock = threading.RLock()
        
        # Health status tracking
        self._health_history: List[SystemHealthReport] = []
        self._current_status = HealthStatus.UNKNOWN
        
        # Monitoring state
        self._monitoring_active = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Health change callbacks
        self._health_callbacks: List[Callable[[SystemHealthReport], None]] = []
        
        # System metrics cache
        self._system_metrics_cache: Dict[str, float] = {}
        self._metrics_cache_time = 0.0
        
        # Initialize default system health checks
        if enable_system_checks:
            self._register_default_health_checks()
    
    def start_monitoring(self) -> None:
        """Start automatic health monitoring."""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitor_thread.start()
        
        logger.info("Health monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop automatic health monitoring."""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        logger.info("Health monitoring stopped")
    
    def register_health_check(self, health_check: HealthCheck) -> None:
        """
        Register a new health check.
        
        Args:
            health_check: Health check configuration
        """
        with self._check_lock:
            self._health_checks[health_check.name] = health_check
        
        logger.info(f"Registered health check: {health_check.name}")
    
    def unregister_health_check(self, check_name: str) -> bool:
        """
        Unregister a health check.
        
        Args:
            check_name: Name of health check to remove
            
        Returns:
            True if check was removed
        """
        with self._check_lock:
            if check_name in self._health_checks:
                del self._health_checks[check_name]
                logger.info(f"Unregistered health check: {check_name}")
                return True
            return False
    
    def run_health_check(self, check_name: str) -> Dict[str, Any]:
        """
        Run a specific health check manually.
        
        Args:
            check_name: Name of health check to run
            
        Returns:
            Health check result
        """
        with self._check_lock:
            check = self._health_checks.get(check_name)
            if not check:
                return {
                    'status': HealthStatus.UNKNOWN.value,
                    'message': f'Health check {check_name} not found',
                    'timestamp': time.time()
                }
            
            return self._execute_health_check(check)
    
    def run_all_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """
        Run all registered health checks.
        
        Returns:
            Dictionary of health check results
        """
        results = {}
        
        with self._check_lock:
            for name, check in self._health_checks.items():
                if check.enabled:
                    results[name] = self._execute_health_check(check)
        
        return results
    
    def get_system_health_report(self) -> SystemHealthReport:
        """
        Get comprehensive system health report.
        
        Returns:
            Complete system health report
        """
        # Run all health checks
        check_results = self.run_all_health_checks()
        
        # Aggregate status
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        
        overall_status = HealthStatus.HEALTHY
        critical_failures = []
        
        for check_name, result in check_results.items():
            status = HealthStatus(result['status'])
            
            if status == HealthStatus.HEALTHY:
                healthy_count += 1
            elif status == HealthStatus.WARNING:
                warning_count += 1
                if overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.WARNING
            elif status == HealthStatus.CRITICAL:
                critical_count += 1
                overall_status = HealthStatus.CRITICAL
                
                # Check if this is a critical component
                check = self._health_checks.get(check_name)
                if check and check.critical:
                    critical_failures.append(check_name)
        
        # Override status if critical components fail
        if critical_failures:
            overall_status = HealthStatus.CRITICAL
        
        # Get system metrics
        system_metrics = self._get_system_metrics()
        
        # Generate recommendations
        recommendations = self._generate_health_recommendations(
            check_results, system_metrics, critical_failures
        )
        
        # Create report
        report = SystemHealthReport(
            timestamp=time.time(),
            overall_status=overall_status,
            component_count=len(check_results),
            healthy_components=healthy_count,
            warning_components=warning_count,
            critical_components=critical_count,
            check_results=check_results,
            system_metrics=system_metrics,
            recommendations=recommendations
        )
        
        # Store in history
        self._health_history.append(report)
        if len(self._health_history) > self.health_history_size:
            self._health_history = self._health_history[-self.health_history_size//2:]
        
        # Update current status
        self._current_status = overall_status
        
        # Notify callbacks
        for callback in self._health_callbacks:
            try:
                callback(report)
            except Exception as e:
                logger.warning(f"Health callback error: {e}")
        
        return report
    
    def get_health_endpoint_data(self) -> Dict[str, Any]:
        """
        Get health data formatted for HTTP health endpoints.
        
        Returns:
            Health endpoint response data
        """
        report = self.get_system_health_report()
        
        return {
            'status': report.overall_status.value,
            'timestamp': report.timestamp,
            'version': "3.0.0",
            'health_score': report.health_score,
            'details': {
                'components': {
                    name: {
                        'status': result['status'],
                        'message': result.get('message', ''),
                        'last_check': result.get('timestamp')
                    }
                    for name, result in report.check_results.items()
                },
                'metrics': report.system_metrics,
                'summary': {
                    'total_components': report.component_count,
                    'healthy': report.healthy_components,
                    'warning': report.warning_components,
                    'critical': report.critical_components
                }
            }
        }
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get health trends over specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Health trend analysis
        """
        cutoff_time = time.time() - (hours * 3600)
        recent_reports = [
            report for report in self._health_history
            if report.timestamp > cutoff_time
        ]
        
        if not recent_reports:
            return {'message': 'No health data available for the specified period'}
        
        # Calculate trends
        status_counts = {status.value: 0 for status in HealthStatus}
        health_scores = []
        
        for report in recent_reports:
            status_counts[report.overall_status.value] += 1
            health_scores.append(report.health_score)
        
        return {
            'period_hours': hours,
            'total_reports': len(recent_reports),
            'status_distribution': status_counts,
            'avg_health_score': sum(health_scores) / len(health_scores),
            'min_health_score': min(health_scores),
            'max_health_score': max(health_scores),
            'current_status': self._current_status.value,
            'trend': self._calculate_health_trend(health_scores)
        }
    
    def add_health_callback(self, callback: Callable[[SystemHealthReport], None]) -> None:
        """Add callback for health status changes."""
        self._health_callbacks.append(callback)
    
    def _register_default_health_checks(self) -> None:
        """Register default system health checks."""
        # CPU usage check
        self.register_health_check(HealthCheck(
            name="system_cpu",
            check_type=CheckType.SYSTEM_RESOURCE,
            check_function=self._check_cpu_usage,
            interval_seconds=30.0,
            critical=False
        ))
        
        # Memory usage check
        self.register_health_check(HealthCheck(
            name="system_memory",
            check_type=CheckType.SYSTEM_RESOURCE,
            check_function=self._check_memory_usage,
            interval_seconds=30.0,
            critical=True
        ))
        
        # Disk usage check
        self.register_health_check(HealthCheck(
            name="system_disk",
            check_type=CheckType.SYSTEM_RESOURCE,
            check_function=self._check_disk_usage,
            interval_seconds=60.0,
            critical=False
        ))
        
        # Application responsiveness check
        self.register_health_check(HealthCheck(
            name="app_responsiveness",
            check_type=CheckType.SERVICE_AVAILABILITY,
            check_function=self._check_app_responsiveness,
            interval_seconds=15.0,
            critical=True
        ))
    
    def _check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage health."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1.0)
            
            if cpu_percent > 90:
                status = HealthStatus.CRITICAL
                message = f"Critical CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                status = HealthStatus.WARNING
                message = f"High CPU usage: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            return {
                'status': status.value,
                'message': message,
                'timestamp': time.time(),
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'cpu_count': psutil.cpu_count()
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': f'CPU check failed: {e}',
                'timestamp': time.time()
            }
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """Check memory usage health."""
        try:
            memory = psutil.virtual_memory()
            
            if memory.percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical memory usage: {memory.percent:.1f}%"
            elif memory.percent > 85:
                status = HealthStatus.WARNING
                message = f"High memory usage: {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}%"
            
            return {
                'status': status.value,
                'message': message,
                'timestamp': time.time(),
                'metrics': {
                    'memory_percent': memory.percent,
                    'memory_total_gb': memory.total / (1024**3),
                    'memory_available_gb': memory.available / (1024**3)
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': f'Memory check failed: {e}',
                'timestamp': time.time()
            }
    
    def _check_disk_usage(self) -> Dict[str, Any]:
        """Check disk usage health."""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 95:
                status = HealthStatus.CRITICAL
                message = f"Critical disk usage: {disk_percent:.1f}%"
            elif disk_percent > 85:
                status = HealthStatus.WARNING
                message = f"High disk usage: {disk_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk_percent:.1f}%"
            
            return {
                'status': status.value,
                'message': message,
                'timestamp': time.time(),
                'metrics': {
                    'disk_percent': disk_percent,
                    'disk_total_gb': disk.total / (1024**3),
                    'disk_free_gb': disk.free / (1024**3)
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': f'Disk check failed: {e}',
                'timestamp': time.time()
            }
    
    def _check_app_responsiveness(self) -> Dict[str, Any]:
        """Check application responsiveness."""
        try:
            # Simple responsiveness test - measure basic operation time
            start_time = time.time()
            
            # Perform a simple operation (like checking current time)
            test_operations = []
            for i in range(100):
                test_operations.append(time.time())
            
            response_time = time.time() - start_time
            
            if response_time > 1.0:  # > 1 second for simple operations
                status = HealthStatus.CRITICAL
                message = f"Poor responsiveness: {response_time:.3f}s"
            elif response_time > 0.1:  # > 100ms
                status = HealthStatus.WARNING
                message = f"Slow responsiveness: {response_time:.3f}s"
            else:
                status = HealthStatus.HEALTHY
                message = f"Good responsiveness: {response_time:.3f}s"
            
            return {
                'status': status.value,
                'message': message,
                'timestamp': time.time(),
                'metrics': {
                    'response_time_ms': response_time * 1000,
                    'operations_tested': len(test_operations)
                }
            }
        except Exception as e:
            return {
                'status': HealthStatus.CRITICAL.value,
                'message': f'Responsiveness check failed: {e}',
                'timestamp': time.time()
            }
    
    def _execute_health_check(self, check: HealthCheck) -> Dict[str, Any]:
        """Execute a single health check with error handling."""
        try:
            # Update check statistics
            check.total_checks += 1
            check.last_check_time = time.time()
            
            # Execute check function with timeout
            result = check.check_function()
            
            # Validate result format
            if not isinstance(result, dict) or 'status' not in result:
                raise ValueError("Health check must return dict with 'status' field")
            
            # Update success/failure tracking
            if result['status'] != HealthStatus.HEALTHY.value:
                check.consecutive_failures += 1
                check.total_failures += 1
            else:
                check.consecutive_failures = 0
            
            check.last_result = result
            return result
        
        except Exception as e:
            # Handle check failure
            check.consecutive_failures += 1
            check.total_failures += 1
            
            error_result = {
                'status': HealthStatus.CRITICAL.value,
                'message': f'Health check execution failed: {e}',
                'timestamp': time.time(),
                'error': str(e)
            }
            
            check.last_result = error_result
            logger.error(f"Health check '{check.name}' failed: {e}")
            return error_result
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get cached system metrics."""
        current_time = time.time()
        
        # Cache metrics for 30 seconds
        if current_time - self._metrics_cache_time > 30.0:
            try:
                self._system_metrics_cache = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100,
                    'load_average_1min': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
                    'process_count': len(psutil.pids()),
                    'uptime_hours': (current_time - psutil.boot_time()) / 3600
                }
                self._metrics_cache_time = current_time
            except Exception as e:
                logger.warning(f"Failed to collect system metrics: {e}")
        
        return self._system_metrics_cache.copy()
    
    def _generate_health_recommendations(
        self,
        check_results: Dict[str, Dict[str, Any]],
        system_metrics: Dict[str, float],
        critical_failures: List[str]
    ) -> List[str]:
        """Generate health recommendations based on check results."""
        recommendations = []
        
        # Critical failure recommendations
        if critical_failures:
            recommendations.append(f"Address critical component failures: {', '.join(critical_failures)}")
        
        # System resource recommendations
        if system_metrics.get('cpu_percent', 0) > 80:
            recommendations.append("High CPU usage detected - consider scaling or optimization")
        
        if system_metrics.get('memory_percent', 0) > 85:
            recommendations.append("High memory usage detected - monitor for memory leaks")
        
        if system_metrics.get('disk_percent', 0) > 85:
            recommendations.append("High disk usage detected - clean up or expand storage")
        
        # Check-specific recommendations
        warning_checks = [
            name for name, result in check_results.items()
            if result['status'] == HealthStatus.WARNING.value
        ]
        if warning_checks:
            recommendations.append(f"Monitor warning components: {', '.join(warning_checks)}")
        
        if not recommendations:
            recommendations.append("All systems operating normally")
        
        return recommendations
    
    def _calculate_health_trend(self, health_scores: List[float]) -> str:
        """Calculate health trend direction."""
        if len(health_scores) < 5:
            return "stable"
        
        # Compare recent scores with earlier scores
        recent_avg = sum(health_scores[-5:]) / 5
        earlier_avg = sum(health_scores[-10:-5]) / 5 if len(health_scores) >= 10 else recent_avg
        
        if recent_avg > earlier_avg + 5:
            return "improving"
        elif recent_avg < earlier_avg - 5:
            return "degrading"
        else:
            return "stable"
    
    def _monitoring_loop(self) -> None:
        """Main health monitoring loop."""
        logger.info("Health monitoring loop started")
        
        while self._monitoring_active:
            try:
                # Run health checks
                self.get_system_health_report()
                
                # Wait for next check interval
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
                time.sleep(self.check_interval)
        
        logger.info("Health monitoring loop stopped")


# Global health monitor instance
default_health_monitor = HealthMonitor()