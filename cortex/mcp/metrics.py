"""
CORTEX MCP Server Prometheus Metrics.

Provides comprehensive metrics collection for monitoring:
- Request counts and durations
- Orchestrator invocations
- Wiring system health
- Performance tracking

Phase 5 Task 2: Prometheus Metrics Endpoint
Date: 2026-01-27

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
CORE-008: Implementation follows TDD specification from test suite.
CORE-030: No database_registry imports - Docker-first architecture.
"""

from typing import Optional, Dict, Any
import time
from threading import Lock

try:
    from prometheus_client import (
        Counter, Histogram, Gauge, 
        generate_latest, CONTENT_TYPE_LATEST,
        CollectorRegistry
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Graceful degradation if prometheus_client not installed
    PROMETHEUS_AVAILABLE = False


class MetricsCollector:
    """
    Collects and exposes Prometheus metrics for CORTEX MCP Server.
    
    Tracks:
    - Request counts (by method, endpoint, status)
    - Request durations (histogram with buckets)
    - Orchestrator invocations (by orchestrator, operation, status)
    - Wiring health status (gauge: 0=unhealthy, 1=degraded, 2=healthy)
    
    Thread-safe for concurrent metric recording.
    Uses dedicated registry to avoid duplicate metric registration errors.
    
    Example:
        >>> collector = MetricsCollector()
        >>> collector.record_request("GET", "/health", "200")
        >>> collector.record_request_duration("GET", "/health", 0.05)
        >>> collector.set_wiring_health(2)  # healthy
    """
    
    def __init__(self, registry: Optional[Any] = None) -> None:
        """
        Initialize metrics collector with Prometheus metrics.
        
        Args:
            registry: Optional CollectorRegistry. If None, creates new registry.
                     This allows tests to use isolated registries.
        """
        self._lock = Lock()
        
        if PROMETHEUS_AVAILABLE:
            # Create dedicated registry to avoid conflicts
            self.registry = registry if registry is not None else CollectorRegistry()
            
            # Request counter: cortex_requests_total{method, endpoint, status}
            self.requests_total = Counter(
                'cortex_requests_total',
                'Total number of requests to CORTEX MCP Server',
                ['method', 'endpoint', 'status'],
                registry=self.registry
            )
            
            # Request duration histogram: cortex_request_duration_seconds{method, endpoint}
            # Buckets: 100ms, 500ms, 1s, 5s, 10s
            self.request_duration = Histogram(
                'cortex_request_duration_seconds',
                'Request duration in seconds',
                ['method', 'endpoint'],
                buckets=[0.1, 0.5, 1.0, 5.0, 10.0],
                registry=self.registry
            )
            
            # Orchestrator invocation counter: cortex_orchestrator_invocations{orchestrator, operation, status}
            self.orchestrator_invocations = Counter(
                'cortex_orchestrator_invocations',
                'Total number of orchestrator invocations',
                ['orchestrator', 'operation', 'status'],
                registry=self.registry
            )
            
            # Wiring health gauge: cortex_wiring_health
            # Values: 0 (unhealthy), 1 (degraded), 2 (healthy)
            self.wiring_health = Gauge(
                'cortex_wiring_health',
                'Wiring system health status (0=unhealthy, 1=degraded, 2=healthy)',
                registry=self.registry
            )
        else:
            # Mock metrics for graceful degradation
            self.registry = None
            self.requests_total = None
            self.request_duration = None
            self.orchestrator_invocations = None
            self.wiring_health = None
    
    def record_request(self, method: str, endpoint: str, status: str) -> None:
        """
        Record a request to the MCP server.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: Request endpoint (/health, /mcp/execute, etc.)
            status: HTTP status code (200, 404, 500, etc.)
        
        Example:
            >>> collector.record_request("GET", "/health", "200")
            >>> collector.record_request("POST", "/mcp/execute", "500")
        """
        if PROMETHEUS_AVAILABLE and self.requests_total is not None:
            with self._lock:
                self.requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()
    
    def record_request_duration(
        self,
        method: str,
        endpoint: str,
        duration_seconds: float
    ) -> None:
        """
        Record request duration in histogram.
        
        Args:
            method: HTTP method
            endpoint: Request endpoint
            duration_seconds: Duration in seconds
        
        Example:
            >>> collector.record_request_duration("GET", "/health", 0.05)  # 50ms
        """
        if PROMETHEUS_AVAILABLE and self.request_duration is not None:
            with self._lock:
                self.request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration_seconds)
    
    def record_orchestrator_invocation(
        self,
        orchestrator: str,
        operation: str,
        status: str
    ) -> None:
        """
        Record an orchestrator invocation.
        
        Args:
            orchestrator: Orchestrator name (TDDOrchestrator, RefactoringOrchestrator, etc.)
            operation: Operation name (generate_tests, analyze_code, etc.)
            status: Operation status (success, failure, timeout, etc.)
        
        Example:
            >>> collector.record_orchestrator_invocation(
            ...     "TDDOrchestrator",
            ...     "generate_tests",
            ...     "success"
            ... )
        """
        if PROMETHEUS_AVAILABLE and self.orchestrator_invocations is not None:
            with self._lock:
                self.orchestrator_invocations.labels(
                    orchestrator=orchestrator,
                    operation=operation,
                    status=status
                ).inc()
    
    def set_wiring_health(self, health_value: int) -> None:
        """
        Set wiring health status.
        
        Args:
            health_value: Health status
                - 0: unhealthy (wiring failures)
                - 1: degraded (some orchestrators unavailable)
                - 2: healthy (all orchestrators wired)
        
        Example:
            >>> collector.set_wiring_health(2)  # healthy
            >>> collector.set_wiring_health(1)  # degraded
            >>> collector.set_wiring_health(0)  # unhealthy
        """
        if PROMETHEUS_AVAILABLE and self.wiring_health is not None:
            with self._lock:
                self.wiring_health.set(health_value)


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None
_collector_lock = Lock()


def get_metrics_collector() -> MetricsCollector:
    """
    Get or create global metrics collector instance.
    
    Thread-safe singleton pattern.
    
    Returns:
        Global MetricsCollector instance.
    
    Example:
        >>> collector = get_metrics_collector()
        >>> collector.record_request("GET", "/health", "200")
    """
    global _metrics_collector
    
    if _metrics_collector is None:
        with _collector_lock:
            if _metrics_collector is None:
                _metrics_collector = MetricsCollector()
    
    return _metrics_collector


def generate_metrics_response() -> str:
    """
    Generate Prometheus-formatted metrics response.
    
    Returns metrics in Prometheus text exposition format.
    Uses global collector's registry.
    
    Returns:
        Metrics string in Prometheus format.
    
    Example:
        >>> metrics = generate_metrics_response()
        >>> print(metrics)
        # HELP cortex_requests_total Total number of requests
        # TYPE cortex_requests_total counter
        cortex_requests_total{method="GET",endpoint="/health",status="200"} 10.0
        ...
    """
    if PROMETHEUS_AVAILABLE:
        try:
            collector = get_metrics_collector()
            if collector.registry is not None:
                return generate_latest(collector.registry).decode('utf-8')
            else:
                return "# Metrics collection error: no registry\n"
        except Exception as e:
            return f"# Metrics collection error: {e}\n"
    else:
        return "# Prometheus client not available\n"


def get_metrics_content_type() -> str:
    """
    Get Prometheus metrics content type.
    
    Returns:
        Content type string for HTTP response.
    
    Example:
        >>> content_type = get_metrics_content_type()
        >>> # Use in HTTP response header: Content-Type: {content_type}
    """
    if PROMETHEUS_AVAILABLE:
        return CONTENT_TYPE_LATEST
    else:
        return "text/plain; version=0.0.4"


def update_wiring_health_metric() -> None:
    """
    Update wiring health metric based on current system state.
    
    Checks health and updates gauge:
    - 2 (healthy): All orchestrators wired
    - 1 (degraded): Some orchestrators unavailable
    - 0 (unhealthy): Wiring system failures
    
    Phase 5: Uses Docker-first architecture (no database_registry).
    """
    collector = get_metrics_collector()
    
    try:
        # Check wiring health from health_checker
        from cortex.mcp.health_checker import get_health_checker
        
        health_checker = get_health_checker()
        wiring_health = health_checker.check_wiring_health()
        
        # Map health status to numeric value
        if wiring_health.status == "healthy":
            collector.set_wiring_health(2)
        elif wiring_health.status == "degraded":
            collector.set_wiring_health(1)
        else:
            collector.set_wiring_health(0)
    
    except Exception:
        # On error, set to degraded
        collector.set_wiring_health(1)


# Request timing decorator
def track_request_metrics(method: str, endpoint: str):
    """
    Decorator to track request metrics automatically.
    
    Records both request count and duration.
    
    Args:
        method: HTTP method
        endpoint: Request endpoint
    
    Example:
        >>> @track_request_metrics("GET", "/health")
        ... def health_endpoint():
        ...     return {"status": "healthy"}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            collector = get_metrics_collector()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status = "200"
                return result
            except Exception as e:
                status = "500"
                raise
            finally:
                duration = time.time() - start_time
                collector.record_request(method, endpoint, status)
                collector.record_request_duration(method, endpoint, duration)
        
        return wrapper
    return decorator
