"""
Health Monitoring System for CORTEX Runtime

Implements comprehensive health checks and monitoring for system components.

AC-OB-002-01: Alerting & Health Monitoring
- Real-time health status monitoring
- Multi-level health checks (system, component, operation)
- Integrated with alerting framework
- Configurable check intervals and thresholds
"""

import logging
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import json

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = field(default_factory=dict)
    check_duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component": self.component,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "check_duration_ms": self.check_duration_ms
        }


class HealthCheck:
    """Base class for health checks."""
    
    def __init__(
        self,
        name: str,
        component: str,
        timeout_seconds: float = 5.0
    ):
        self.name = name
        self.component = component
        self.timeout_seconds = timeout_seconds
    
    def check(self) -> HealthCheckResult:
        """Execute health check. Must be overridden."""
        raise NotImplementedError("Subclasses must implement check()")


class DatabaseHealthCheck(HealthCheck):
    """Health check for database connectivity."""
    
    def __init__(self, db_connection=None):
        super().__init__("database_check", "database")
        self.db_connection = db_connection
    
    def check(self) -> HealthCheckResult:
        """Check database connectivity and performance."""
        start_time = time.time()
        try:
            if self.db_connection is None:
                return HealthCheckResult(
                    component=self.component,
                    status=HealthStatus.UNHEALTHY,
                    message="No database connection available"
                )
            
            # Try simple query
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            
            duration_ms = (time.time() - start_time) * 1000
            
            status = HealthStatus.HEALTHY
            if duration_ms > 100:
                status = HealthStatus.DEGRADED
            
            return HealthCheckResult(
                component=self.component,
                status=status,
                message="Database connection OK",
                metrics={"response_time_ms": duration_ms},
                check_duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=self.component,
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                check_duration_ms=duration_ms
            )


class MemoryHealthCheck(HealthCheck):
    """Health check for memory usage."""
    
    def __init__(self, threshold_percent: float = 80.0):
        super().__init__("memory_check", "memory")
        self.threshold_percent = threshold_percent
    
    def check(self) -> HealthCheckResult:
        """Check memory usage."""
        start_time = time.time()
        try:
            import psutil
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent
            
            duration_ms = (time.time() - start_time) * 1000
            
            if memory_percent > self.threshold_percent:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {memory_percent:.1f}%"
            elif memory_percent > self.threshold_percent * 0.75:
                status = HealthStatus.DEGRADED
                message = f"Memory usage elevated: {memory_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory_percent:.1f}%"
            
            return HealthCheckResult(
                component=self.component,
                status=status,
                message=message,
                metrics={
                    "memory_percent": memory_percent,
                    "memory_available_mb": memory_info.available / (1024 * 1024)
                },
                check_duration_ms=duration_ms
            )
        except ImportError:
            return HealthCheckResult(
                component=self.component,
                status=HealthStatus.UNKNOWN,
                message="psutil not available for memory checks"
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=self.component,
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                check_duration_ms=duration_ms
            )


class CPUHealthCheck(HealthCheck):
    """Health check for CPU usage."""
    
    def __init__(self, threshold_percent: float = 85.0):
        super().__init__("cpu_check", "cpu")
        self.threshold_percent = threshold_percent
    
    def check(self) -> HealthCheckResult:
        """Check CPU usage."""
        start_time = time.time()
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            duration_ms = (time.time() - start_time) * 1000
            
            if cpu_percent > self.threshold_percent:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage critical: {cpu_percent:.1f}%"
            elif cpu_percent > self.threshold_percent * 0.75:
                status = HealthStatus.DEGRADED
                message = f"CPU usage elevated: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            return HealthCheckResult(
                component=self.component,
                status=status,
                message=message,
                metrics={"cpu_percent": cpu_percent},
                check_duration_ms=duration_ms
            )
        except ImportError:
            return HealthCheckResult(
                component=self.component,
                status=HealthStatus.UNKNOWN,
                message="psutil not available for CPU checks"
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                component=self.component,
                status=HealthStatus.UNHEALTHY,
                message=f"CPU check failed: {str(e)}",
                check_duration_ms=duration_ms
            )


class HealthMonitor:
    """Central health monitoring service."""
    
    def __init__(self, check_interval_seconds: float = 30.0):
        self.check_interval_seconds = check_interval_seconds
        self.checks: Dict[str, HealthCheck] = {}
        self.results: Dict[str, HealthCheckResult] = {}
        self.handlers: List[Callable[[HealthCheckResult], None]] = []
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
    
    def register_check(self, check: HealthCheck) -> None:
        """Register a health check."""
        self.checks[check.name] = check
        logger.info(f"Registered health check: {check.name}")
    
    def register_handler(
        self,
        handler: Callable[[HealthCheckResult], None]
    ) -> None:
        """Register a result handler."""
        self.handlers.append(handler)
    
    def run_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {}
        for name, check in self.checks.items():
            try:
                result = check.check()
                results[name] = result
                self.results[name] = result
                
                # Call handlers
                for handler in self.handlers:
                    try:
                        handler(result)
                    except Exception as e:
                        logger.error(f"Error in health check handler: {str(e)}")
                
                logger.debug(f"Health check '{name}': {result.status.value}")
            except Exception as e:
                logger.error(f"Error running health check '{name}': {str(e)}")
                result = HealthCheckResult(
                    component=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Check failed: {str(e)}"
                )
                results[name] = result
        
        return results
    
    def start_background_monitoring(self) -> None:
        """Start background health monitoring."""
        if self.running:
            logger.warning("Health monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Health monitoring started")
    
    def stop_background_monitoring(self) -> None:
        """Stop background health monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self.running:
            try:
                self.run_checks()
                time.sleep(self.check_interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")
    
    def get_status(self, component: str) -> Optional[HealthCheckResult]:
        """Get health status for a component."""
        return self.results.get(component)
    
    def get_all_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get all health statuses."""
        return {
            name: result.to_dict()
            for name, result in self.results.items()
        }
    
    def is_healthy(self) -> bool:
        """Check if system is overall healthy."""
        if not self.results:
            return True
        
        return all(
            result.status == HealthStatus.HEALTHY
            for result in self.results.values()
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get health summary."""
        if not self.results:
            return {"status": "unknown", "components": {}}
        
        healthy_count = sum(
            1 for r in self.results.values()
            if r.status == HealthStatus.HEALTHY
        )
        degraded_count = sum(
            1 for r in self.results.values()
            if r.status == HealthStatus.DEGRADED
        )
        unhealthy_count = sum(
            1 for r in self.results.values()
            if r.status == HealthStatus.UNHEALTHY
        )
        
        overall_status = HealthStatus.HEALTHY.value
        if unhealthy_count > 0:
            overall_status = HealthStatus.UNHEALTHY.value
        elif degraded_count > 0:
            overall_status = HealthStatus.DEGRADED.value
        
        return {
            "status": overall_status,
            "healthy": healthy_count,
            "degraded": degraded_count,
            "unhealthy": unhealthy_count,
            "total": len(self.results),
            "components": self.get_all_statuses()
        }


# Global health monitor instance
_health_monitor = None


def get_health_monitor() -> HealthMonitor:
    """Get or create global health monitor."""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor
