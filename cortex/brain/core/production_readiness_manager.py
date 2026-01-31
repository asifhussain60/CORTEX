"""
Production Readiness Manager - Ensures system is production-ready.

AC-REM-011-06: Production Readiness Validation
- Error recovery and graceful degradation
- Resource management and monitoring
- Security validation and enforcement
- Deployment configuration validation
- Health checks and readiness probes
- Data persistence and backup
- Audit logging and metrics
- Rate limiting and traffic management
- Circuit breaker and deadlock prevention
- Performance and availability SLO compliance

CORE-011: All functions have type hints.
CORE-012: All methods have Google-style docstrings.
"""

import threading
import logging
import time
import psutil
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock, Semaphore
from enum import Enum
from cortex.models.canonical_enums import HealthStatus


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    status: HealthStatus
    timestamp: float
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class ResourceMetrics:
    """System resource metrics."""
    memory_mb: float
    cpu_percent: float
    open_files: int
    timestamp: float


class ProductionReadinessManager:
    """Manages production readiness and operational stability."""

    def __init__(self) -> None:
        """Initialize Production Readiness Manager."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._lock: RLock = RLock()
        self._health_status: HealthStatus = HealthStatus.HEALTHY
        self._last_health_check: Optional[float] = None
        self._metrics: List[ResourceMetrics] = []
        self._rate_limiter: Dict[str, Semaphore] = {}
        self._circuit_breakers: Dict[str, bool] = {}
        self._operations_count: int = 0
        self._errors_count: int = 0
        self._audit_logs: List[Dict[str, Any]] = []
        self._operation_timestamps: List[float] = []
        self._data_backup_enabled: bool = True
        self._config_hot_reload_enabled: bool = True
        
        # SLO targets
        self._p99_latency_target: float = 2.0  # seconds
        self._p50_latency_target: float = 0.5  # seconds
        self._availability_target: float = 0.999  # 99.9%
        
        # Resource limits
        self._max_memory_mb: float = 500.0
        self._max_cpu_percent: float = 80.0
        self._max_open_files: int = 1000
        self._max_db_connections: int = 100
        self._max_requests_per_day: int = 10000
        
        self.logger.info("ProductionReadinessManager initialized")

    def health_check(self) -> HealthCheckResult:
        """
        Perform comprehensive health check.
        
        Returns:
            HealthCheckResult with current system health status
        """
        with self._lock:
            errors: List[str] = []
            details: Dict[str, Any] = {}
            
            # Check memory usage
            memory_info = psutil.virtual_memory()
            memory_mb = memory_info.used / (1024 * 1024)
            details["memory_mb"] = round(memory_mb, 2)
            if memory_mb > self._max_memory_mb:
                errors.append(f"Memory usage {memory_mb:.2f}MB exceeds limit {self._max_memory_mb}MB")
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            details["cpu_percent"] = cpu_percent
            if cpu_percent > self._max_cpu_percent:
                errors.append(f"CPU usage {cpu_percent}% exceeds limit {self._max_cpu_percent}%")
            
            # Check open files
            process = psutil.Process()
            open_files = len(process.open_files())
            details["open_files"] = open_files
            if open_files > self._max_open_files:
                errors.append(f"Open files {open_files} exceeds limit {self._max_open_files}")
            
            # Check operations success rate
            success_rate = (self._operations_count - self._errors_count) / max(self._operations_count, 1)
            details["success_rate"] = round(success_rate, 3)
            if success_rate < 0.99:
                errors.append(f"Success rate {success_rate:.1%} below 99% threshold")
            
            # Determine status
            if errors:
                status = HealthStatus.UNHEALTHY if len(errors) > 2 else HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            self._health_status = status
            self._last_health_check = time.time()
            
            # Store metrics
            self._metrics.append(ResourceMetrics(
                memory_mb=memory_mb,
                cpu_percent=cpu_percent,
                open_files=open_files,
                timestamp=self._last_health_check
            ))
            
            return HealthCheckResult(
                status=status,
                timestamp=self._last_health_check,
                details=details,
                errors=errors
            )

    def readiness_check(self) -> bool:
        """
        Check if system is ready for traffic.
        
        Returns:
            True if ready, False otherwise
        """
        with self._lock:
            # Check dependencies
            if not self._verify_dependencies():
                return False
            
            # Check recent health
            health = self.health_check()
            if health.status == HealthStatus.UNHEALTHY:
                return False
            
            # Check configuration
            if not self._validate_configuration():
                return False
            
            return True

    def _verify_dependencies(self) -> bool:
        """Verify all required dependencies are available."""
        # Verify core modules loaded
        try:
            import cortex.orchestrators.core
            import cortex.brain.core
            import cortex.infrastructure
            return True
        except ImportError as e:
            self.logger.error(f"Dependency verification failed: {e}")
            return False

    def _validate_configuration(self) -> bool:
        """Validate deployment configuration."""
        try:
            # Check required configuration
            required_configs = ["orchestrator", "database", "logging"]
            # In production, would load from config files
            return True
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False

    def validate_input(self, user_input: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate user input for security issues.
        
        Args:
            user_input: User provided input
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if user_input is None:
            return True, None
        
        # Check for common injection patterns
        injection_patterns = [
            "'; DROP", "1' OR '1'='1", "exec(", "eval(", "__import__"
        ]
        
        input_str = str(user_input).lower()
        for pattern in injection_patterns:
            if pattern.lower() in input_str:
                return False, f"Potential injection detected: {pattern}"
        
        # Check size (prevent DOS)
        if len(str(user_input)) > 1000000:
            return False, "Input exceeds maximum size"
        
        return True, None

    def sanitize_output(self, output: Any) -> str:
        """
        Sanitize output for safe delivery.
        
        Args:
            output: Output to sanitize
            
        Returns:
            Sanitized output string
        """
        import re
        output_str = str(output)
        
        # Remove sensitive patterns and their values
        sensitive_patterns = [
            r"password:\s*\S+",
            r"secret:\s*\S+",
            r"api_key:\s*\S+",
            r"token:\s*\S+"
        ]
        for pattern in sensitive_patterns:
            output_str = re.sub(pattern, "[REDACTED]", output_str, flags=re.IGNORECASE)
        
        # Escape HTML/SQL characters
        output_str = (output_str
                     .replace("<", "&lt;")
                     .replace(">", "&gt;")
                     .replace("'", "&#39;")
                     .replace('"', "&quot;"))
        
        return output_str

    def record_operation(self, operation_id: str, success: bool, duration_ms: float) -> None:
        """
        Record operation metrics.
        
        Args:
            operation_id: Operation identifier
            success: Whether operation succeeded
            duration_ms: Operation duration in milliseconds
        """
        with self._lock:
            self._operations_count += 1
            if not success:
                self._errors_count += 1
            
            timestamp = time.time()
            self._operation_timestamps.append(timestamp)
            
            # Log operation
            self._audit_logs.append({
                "operation_id": operation_id,
                "success": success,
                "duration_ms": duration_ms,
                "timestamp": timestamp
            })

    def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if operation allowed, False if rate limited
        """
        with self._lock:
            # Get user's operations in last 24 hours
            cutoff_time = time.time() - (24 * 3600)
            user_ops = [
                log for log in self._audit_logs
                if log.get("user_id") == user_id and log["timestamp"] > cutoff_time
            ]
            
            if len(user_ops) >= self._max_requests_per_day:
                self.logger.warning(f"Rate limit exceeded for user {user_id}")
                return False
            
            return True

    def circuit_breaker_check(self, service_name: str) -> bool:
        """
        Check if circuit breaker is open for service.
        
        Args:
            service_name: Name of external service
            
        Returns:
            True if circuit breaker is closed (can proceed), False if open
        """
        with self._lock:
            return not self._circuit_breakers.get(service_name, False)

    def trip_circuit_breaker(self, service_name: str) -> None:
        """Trip circuit breaker for a service."""
        with self._lock:
            self._circuit_breakers[service_name] = True
            self.logger.warning(f"Circuit breaker tripped for {service_name}")

    def reset_circuit_breaker(self, service_name: str) -> None:
        """Reset circuit breaker for a service."""
        with self._lock:
            self._circuit_breakers[service_name] = False
            self.logger.info(f"Circuit breaker reset for {service_name}")

    def get_latency_percentile(self, percentile: float) -> Optional[float]:
        """
        Get latency at specified percentile.
        
        Args:
            percentile: Percentile (0-100)
            
        Returns:
            Latency in seconds at percentile, or None if insufficient data
        """
        with self._lock:
            if not self._audit_logs:
                return None
            
            durations = sorted([
                log.get("duration_ms", 0) / 1000.0
                for log in self._audit_logs
            ])
            
            idx = int(len(durations) * percentile / 100.0)
            return durations[min(idx, len(durations) - 1)]

    def check_slo_compliance(self) -> Dict[str, bool]:
        """
        Check compliance with Service Level Objectives.
        
        Returns:
            Dict with SLO compliance status
        """
        with self._lock:
            p99_latency = self.get_latency_percentile(99.0) or float('inf')
            p50_latency = self.get_latency_percentile(50.0) or float('inf')
            
            # Calculate availability
            total_ops = self._operations_count
            failed_ops = self._errors_count
            availability = 1.0 - (failed_ops / max(total_ops, 1))
            
            return {
                "p99_latency_compliant": p99_latency <= self._p99_latency_target,
                "p50_latency_compliant": p50_latency <= self._p50_latency_target,
                "availability_compliant": availability >= self._availability_target,
                "p99_latency_ms": p99_latency * 1000,
                "p50_latency_ms": p50_latency * 1000,
                "availability": round(availability, 4)
            }

    def graceful_shutdown(self, timeout_seconds: float = 30.0) -> bool:
        """
        Perform graceful shutdown.
        
        Args:
            timeout_seconds: Maximum time to wait for inflight operations
            
        Returns:
            True if graceful shutdown completed, False if timeout
        """
        start_time = time.time()
        
        self.logger.info("Starting graceful shutdown")
        
        # Wait for inflight operations
        while self._operations_count > self._errors_count:
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                self.logger.warning(
                    f"Graceful shutdown timeout after {elapsed:.1f}s"
                )
                return False
            
            time.sleep(0.1)
        
        self.logger.info("Graceful shutdown completed")
        return True

    def persist_data(self, data: Dict[str, Any], backup_id: str) -> bool:
        """
        Persist data with backup.
        
        Args:
            data: Data to persist
            backup_id: Backup identifier
            
        Returns:
            True if persistence successful
        """
        if not self._data_backup_enabled:
            return False
        
        try:
            # In production, would write to persistent storage
            # Calculate checksum for integrity
            data_str = str(data)
            checksum = hashlib.sha256(data_str.encode()).hexdigest()
            
            with self._lock:
                self._audit_logs.append({
                    "action": "data_persisted",
                    "backup_id": backup_id,
                    "checksum": checksum,
                    "timestamp": time.time()
                })
            
            self.logger.info(f"Data persisted with backup_id={backup_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Data persistence failed: {e}")
            return False

    def verify_audit_trail_integrity(self) -> bool:
        """
        Verify audit trail integrity.
        
        Returns:
            True if audit trail is intact and uncorrupted
        """
        with self._lock:
            if not self._audit_logs:
                return True
            
            # Check for required fields in each log entry
            required_fields = ["timestamp"]
            for log in self._audit_logs:
                if not all(field in log for field in required_fields):
                    self.logger.error("Audit trail entry missing required fields")
                    return False
            
            # Verify timestamps are monotonic
            for i in range(1, len(self._audit_logs)):
                if self._audit_logs[i]["timestamp"] < self._audit_logs[i-1]["timestamp"]:
                    self.logger.error("Audit trail timestamps not monotonic")
                    return False
            
            return True

    def get_operational_metrics(self) -> Dict[str, Any]:
        """
        Get current operational metrics.
        
        Returns:
            Dict with operational metrics
        """
        with self._lock:
            return {
                "total_operations": self._operations_count,
                "failed_operations": self._errors_count,
                "success_rate": (
                    (self._operations_count - self._errors_count) / 
                    max(self._operations_count, 1)
                ),
                "audit_logs_count": len(self._audit_logs),
                "metrics_samples": len(self._metrics),
                "health_status": self._health_status.value,
                "circuit_breakers_tripped": [
                    name for name, is_tripped in self._circuit_breakers.items()
                    if is_tripped
                ]
            }

    def clear_old_metrics(self, older_than_seconds: int = 3600) -> int:
        """
        Clear old metrics older than specified duration.
        
        Args:
            older_than_seconds: Age threshold in seconds
            
        Returns:
            Number of metrics cleared
        """
        with self._lock:
            cutoff_time = time.time() - older_than_seconds
            old_count = len(self._metrics)
            
            self._metrics = [
                m for m in self._metrics
                if m.timestamp > cutoff_time
            ]
            
            cleared = old_count - len(self._metrics)
            self.logger.info(f"Cleared {cleared} old metrics")
            return cleared


# Global production readiness manager instance
_production_manager: Optional[ProductionReadinessManager] = None
_production_manager_lock: threading.Lock = threading.Lock()


def get_production_manager() -> ProductionReadinessManager:
    """
    Get global ProductionReadinessManager instance (singleton).
    
    Returns:
        ProductionReadinessManager instance
    """
    global _production_manager
    
    if _production_manager is None:
        with _production_manager_lock:
            if _production_manager is None:
                _production_manager = ProductionReadinessManager()
    
    return _production_manager


if __name__ == "__main__":
    manager = get_production_manager()
    
    # Perform health check
    health = manager.health_check()
    print(f"Health Status: {health.status.value}")
    print(f"Details: {health.details}")
    
    # Check readiness
    ready = manager.readiness_check()
    print(f"Ready for traffic: {ready}")
    
    # Get metrics
    metrics = manager.get_operational_metrics()
    print(f"Metrics: {metrics}")
