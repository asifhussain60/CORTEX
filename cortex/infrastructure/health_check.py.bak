"""
cortex/infrastructure/health_check.py

Health check framework for production readiness.
Provides health checks for database, audit logger, and connection pool.
"""

import sqlite3
import logging
import time
from typing import Dict, Tuple, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HealthStatus:
    """Health status result."""
    component: str
    healthy: bool
    message: str
    latency_ms: float
    timestamp: float


class DatabaseHealthCheck:
    """Health check for database connectivity and performance."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
    
    def check(self) -> HealthStatus:
        """Check database health."""
        start = time.time()
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            
            latency = (time.time() - start) * 1000
            
            if latency > 5000:
                self.logger.warning(f"Database health check slow: {latency:.1f}ms")
            
            return HealthStatus(
                component="database",
                healthy=True,
                message=f"Database OK (latency: {latency:.1f}ms)",
                latency_ms=latency,
                timestamp=time.time()
            )
        
        except sqlite3.Error as e:
            self.logger.error(f"Database health check failed: {e}")
            return HealthStatus(
                component="database",
                healthy=False,
                message=f"Database error: {e}",
                latency_ms=(time.time() - start) * 1000,
                timestamp=time.time()
            )
        except Exception as e:
            self.logger.error(f"Unexpected error in database health check: {e}")
            return HealthStatus(
                component="database",
                healthy=False,
                message=f"Unexpected error: {e}",
                latency_ms=(time.time() - start) * 1000,
                timestamp=time.time()
            )


class AuditLoggerHealthCheck:
    """Health check for audit logger write/read cycle."""
    
    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path
        self.logger = logging.getLogger(__name__)
    
    def check(self) -> HealthStatus:
        """Check audit logger health."""
        start = time.time()
        try:
            # Test write
            test_message = f"health_check_{int(time.time())}"
            with open(self.audit_log_path, 'a') as f:
                f.write(test_message + "\n")
            
            # Test read
            with open(self.audit_log_path, 'r') as f:
                content = f.read()
                if test_message in content:
                    latency = (time.time() - start) * 1000
                    return HealthStatus(
                        component="audit_logger",
                        healthy=True,
                        message=f"Audit logger OK (latency: {latency:.1f}ms)",
                        latency_ms=latency,
                        timestamp=time.time()
                    )
                else:
                    raise RuntimeError("Health check write not found in log")
        
        except IOError as e:
            self.logger.error(f"Audit logger health check failed: {e}")
            return HealthStatus(
                component="audit_logger",
                healthy=False,
                message=f"IO error: {e}",
                latency_ms=(time.time() - start) * 1000,
                timestamp=time.time()
            )
        except Exception as e:
            self.logger.error(f"Unexpected error in audit logger health check: {e}")
            return HealthStatus(
                component="audit_logger",
                healthy=False,
                message=f"Unexpected error: {e}",
                latency_ms=(time.time() - start) * 1000,
                timestamp=time.time()
            )


class ConnectionPoolHealthCheck:
    """Health check for connection pool availability and utilization."""
    
    def __init__(self, connection_pool):
        self.pool = connection_pool
        self.logger = logging.getLogger(__name__)
    
    def check(self) -> HealthStatus:
        """Check connection pool health."""
        start = time.time()
        try:
            if hasattr(self.pool, '_available'):
                available = self.pool._available.qsize() if hasattr(self.pool._available, 'qsize') else 0
            else:
                available = 0
            
            if hasattr(self.pool, '_all_connections'):
                total = len(self.pool._all_connections)
            else:
                total = 0
            
            latency = (time.time() - start) * 1000
            
            healthy = available > 0 or total > 0
            
            return HealthStatus(
                component="connection_pool",
                healthy=healthy,
                message=f"Pool OK (available: {available}/{total}, latency: {latency:.1f}ms)",
                latency_ms=latency,
                timestamp=time.time()
            )
        
        except Exception as e:
            self.logger.error(f"Connection pool health check failed: {e}")
            return HealthStatus(
                component="connection_pool",
                healthy=False,
                message=f"Error: {e}",
                latency_ms=(time.time() - start) * 1000,
                timestamp=time.time()
            )


class HealthCheckManager:
    """Manages all health checks."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.checks: Dict[str, any] = {}
    
    def register_check(self, name: str, checker) -> None:
        """Register a health check."""
        self.checks[name] = checker
    
    def check_all(self) -> Tuple[bool, List[HealthStatus]]:
        """Run all health checks."""
        results = []
        overall_healthy = True
        
        for name, checker in self.checks.items():
            try:
                result = checker.check()
                results.append(result)
                if not result.healthy:
                    overall_healthy = False
                    self.logger.warning(f"Health check failed: {name}")
            except Exception as e:
                self.logger.error(f"Error running health check {name}: {e}")
                overall_healthy = False
        
        return overall_healthy, results
