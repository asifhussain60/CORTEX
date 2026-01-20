"""
Prometheus metrics implementation (AC-OPS-004-02).

Implements comprehensive Prometheus metrics following RED (Rate, Errors, Duration)
and USE (Utilization, Saturation, Errors) methods with proper label cardinality control.

Classes:
    MetricsConfig: Configuration for metrics collection.
    MetricsCollector: Main metrics collection coordinator.
    RequestMetrics: HTTP request metrics (RED method).
    DatabaseMetrics: Database metrics (USE method).
    BusinessMetrics: Business-level metrics.
    CustomMetrics: Custom metrics for orchestrators and circuit breakers.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set, Any
import time
import threading
from collections import defaultdict
from datetime import datetime

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    REGISTRY,
    generate_latest,
)


@dataclass
class MetricsConfig:
    """Configuration for metrics collection.
    
    Args:
        environment: Deployment environment (test, staging, prod).
        cardinality_limit: Maximum unique label values per metric (prevent explosion).
        histogram_buckets: Latency buckets for histograms (seconds).
        registry: Prometheus registry to use (uses default if None).
        enable_performance_metrics: Enable profiling metrics.
    """

    environment: str = "production"
    cardinality_limit: int = 100
    histogram_buckets: List[float] = field(
        default_factory=lambda: [0.001, 0.01, 0.1, 1, 10]
    )
    registry: Optional[CollectorRegistry] = None
    enable_performance_metrics: bool = True


class RequestMetrics:
    """HTTP request metrics following RED (Rate, Errors, Duration) method.
    
    Metrics:
        http_requests_total: Counter of requests by status, method, endpoint.
        http_request_duration_seconds: Histogram of request latency.
        http_requests_in_flight: Gauge of currently processing requests.
    """

    def __init__(
        self,
        registry: Optional[CollectorRegistry] = None,
        config: Optional[MetricsConfig] = None,
    ) -> None:
        """Initialize request metrics.
        
        Args:
            registry: Prometheus registry to use.
            config: Metrics configuration.
        """
        self.registry = registry or REGISTRY
        self.config = config or MetricsConfig(environment="production")
        self._label_cache: Dict[str, Set[str]] = defaultdict(set)
        self._lock = threading.Lock()
        self._in_flight_requests: Dict[str, float] = {}

        # Initialize metrics
        self.requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        self.request_duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["endpoint"],
            buckets=self.config.histogram_buckets,
            registry=self.registry,
        )

        self.requests_in_flight = Gauge(
            "http_requests_in_flight",
            "HTTP requests currently being processed",
            ["endpoint"],
            registry=self.registry,
        )

    def record_request(
        self,
        endpoint: str,
        method: str,
        status: int,
    ) -> None:
        """Record a completed HTTP request.
        
        Args:
            endpoint: Request endpoint path.
            method: HTTP method (GET, POST, etc).
            status: HTTP response status code.
        """
        endpoint = self._enforce_cardinality("endpoint", endpoint)
        self.requests_total.labels(
            method=method,
            endpoint=endpoint,
            status=status,
        ).inc()

    def record_request_duration(
        self,
        endpoint: str,
        duration_seconds: float,
    ) -> None:
        """Record request duration histogram.
        
        Args:
            endpoint: Request endpoint path.
            duration_seconds: Request duration in seconds.
        """
        endpoint = self._enforce_cardinality("endpoint", endpoint)
        self.request_duration.labels(endpoint=endpoint).observe(duration_seconds)

    def start_request(self, endpoint: str) -> str:
        """Start tracking an in-flight request.
        
        Args:
            endpoint: Request endpoint path.
            
        Returns:
            Request ID for later reference.
        """
        request_id = f"{endpoint}_{time.time()}"
        endpoint = self._enforce_cardinality("endpoint", endpoint)
        with self._lock:
            self._in_flight_requests[request_id] = time.time()
            self.requests_in_flight.labels(endpoint=endpoint).inc()
        return request_id

    def end_request(self, request_id: str, endpoint: str) -> None:
        """End tracking an in-flight request.
        
        Args:
            request_id: Request ID from start_request.
            endpoint: Request endpoint path.
        """
        endpoint = self._enforce_cardinality("endpoint", endpoint)
        with self._lock:
            if request_id in self._in_flight_requests:
                del self._in_flight_requests[request_id]
                self.requests_in_flight.labels(endpoint=endpoint).dec()

    def _enforce_cardinality(self, label_name: str, value: str) -> str:
        """Enforce cardinality limit on label values.
        
        Args:
            label_name: Label name.
            value: Label value.
            
        Returns:
            Either the original value or 'other' if cardinality limit exceeded.
        """
        with self._lock:
            self._label_cache[label_name].add(value)
            if len(self._label_cache[label_name]) > self.config.cardinality_limit:
                return "other"
        return value


class DatabaseMetrics:
    """Database metrics following USE (Utilization, Saturation, Errors) method.
    
    Metrics:
        db_connections_active: Gauge of active connections.
        db_connections_idle: Gauge of idle connections.
        db_query_duration_seconds: Histogram of query duration.
        db_queries_total: Counter of queries by type and status.
    """

    def __init__(
        self,
        registry: Optional[CollectorRegistry] = None,
        config: Optional[MetricsConfig] = None,
    ) -> None:
        """Initialize database metrics.
        
        Args:
            registry: Prometheus registry to use.
            config: Metrics configuration.
        """
        self.registry = registry or REGISTRY
        self.config = config or MetricsConfig(environment="production")
        self._lock = threading.Lock()

        # Initialize metrics
        self.connections_active = Gauge(
            "db_connections_active",
            "Active database connections",
            registry=self.registry,
        )

        self.connections_idle = Gauge(
            "db_connections_idle",
            "Idle database connections",
            registry=self.registry,
        )

        self.query_duration = Histogram(
            "db_query_duration_seconds",
            "Database query duration in seconds",
            ["query_type"],
            buckets=self.config.histogram_buckets,
            registry=self.registry,
        )

        self.queries_total = Counter(
            "db_queries_total",
            "Total database queries",
            ["query_type", "status"],
            registry=self.registry,
        )

    def set_active_connections(self, count: int) -> None:
        """Set the number of active database connections.
        
        Args:
            count: Number of active connections.
        """
        self.connections_active.set(count)

    def set_idle_connections(self, count: int) -> None:
        """Set the number of idle database connections.
        
        Args:
            count: Number of idle connections.
        """
        self.connections_idle.set(count)

    def record_query_duration(
        self,
        query_type: str,
        duration_seconds: float,
    ) -> None:
        """Record database query duration.
        
        Args:
            query_type: Type of query (SELECT, INSERT, UPDATE, DELETE).
            duration_seconds: Query duration in seconds.
        """
        self.query_duration.labels(query_type=query_type).observe(duration_seconds)

    def record_query(
        self,
        query_type: str,
        status: str,
    ) -> None:
        """Record a database query execution.
        
        Args:
            query_type: Type of query.
            status: Query status (success, error, timeout).
        """
        self.queries_total.labels(query_type=query_type, status=status).inc()


class BusinessMetrics:
    """Business-level metrics for phases and governance.
    
    Metrics:
        phases_total: Counter of phase completions.
        ac_completed_total: Counter of acceptance criteria completions.
        governance_checks_total: Counter of governance checks by rule and decision.
    """

    def __init__(
        self,
        registry: Optional[CollectorRegistry] = None,
        config: Optional[MetricsConfig] = None,
    ) -> None:
        """Initialize business metrics.
        
        Args:
            registry: Prometheus registry to use.
            config: Metrics configuration.
        """
        self.registry = registry or REGISTRY
        self.config = config or MetricsConfig(environment="production")

        self.phases_total = Counter(
            "phases_total",
            "Total phase completions",
            ["status"],
            registry=self.registry,
        )

        self.ac_completed_total = Counter(
            "ac_completed_total",
            "Total acceptance criteria completed",
            ["phase"],
            registry=self.registry,
        )

        self.governance_checks_total = Counter(
            "governance_checks_total",
            "Total governance checks",
            ["rule", "decision"],
            registry=self.registry,
        )

    def record_phase_completion(self, status: str) -> None:
        """Record a phase completion.
        
        Args:
            status: Phase status (success, failed, skipped).
        """
        self.phases_total.labels(status=status).inc()

    def record_ac_completion(self, phase: str, count: int = 1) -> None:
        """Record acceptance criteria completions.
        
        Args:
            phase: Phase ID.
            count: Number of ACs completed.
        """
        for _ in range(count):
            self.ac_completed_total.labels(phase=phase).inc()

    def record_governance_check(self, rule: str, decision: str) -> None:
        """Record a governance check result.
        
        Args:
            rule: Governance rule ID.
            decision: Rule decision (allow, deny, warn).
        """
        self.governance_checks_total.labels(rule=rule, decision=decision).inc()


class CustomMetrics:
    """Custom metrics for orchestrators and circuit breakers.
    
    Metrics:
        orchestrator_executions_total: Counter of orchestrator executions.
        circuit_breaker_state: Gauge of circuit breaker state.
    """

    def __init__(
        self,
        registry: Optional[CollectorRegistry] = None,
        config: Optional[MetricsConfig] = None,
    ) -> None:
        """Initialize custom metrics.
        
        Args:
            registry: Prometheus registry to use.
            config: Metrics configuration.
        """
        self.registry = registry or REGISTRY
        self.config = config or MetricsConfig(environment="production")

        self.orchestrator_executions_total = Counter(
            "orchestrator_executions_total",
            "Total orchestrator executions",
            ["orchestrator", "status"],
            registry=self.registry,
        )

        self.circuit_breaker_state = Gauge(
            "circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half_open)",
            ["circuit"],
            registry=self.registry,
        )

    def record_orchestrator_execution(
        self,
        orchestrator: str,
        status: str,
    ) -> None:
        """Record an orchestrator execution.
        
        Args:
            orchestrator: Orchestrator name.
            status: Execution status (success, error, timeout).
        """
        self.orchestrator_executions_total.labels(
            orchestrator=orchestrator,
            status=status,
        ).inc()

    def set_circuit_breaker_state(self, circuit: str, state: int) -> None:
        """Set circuit breaker state.
        
        Args:
            circuit: Circuit name.
            state: State code (0=closed, 1=open, 2=half_open).
        """
        self.circuit_breaker_state.labels(circuit=circuit).set(state)


class MetricsCollector:
    """Main coordinator for all metrics collection.
    
    Manages HTTP request metrics, database metrics, business metrics,
    and custom metrics with a unified interface.
    """

    def __init__(self, config: MetricsConfig) -> None:
        """Initialize metrics collector.
        
        Args:
            config: Metrics configuration.
        """
        self.config = config
        self.registry = config.registry or REGISTRY

        # Initialize all metric groups
        self.request_metrics = RequestMetrics(
            registry=self.registry,
            config=config,
        )
        self.database_metrics = DatabaseMetrics(
            registry=self.registry,
            config=config,
        )
        self.business_metrics = BusinessMetrics(
            registry=self.registry,
            config=config,
        )
        self.custom_metrics = CustomMetrics(
            registry=self.registry,
            config=config,
        )

    def generate_metrics_text(self) -> str:
        """Generate Prometheus metrics text format.
        
        Returns:
            Metrics in Prometheus text format.
        """
        return generate_latest(self.registry).decode("utf-8")

    def get_metrics_dict(self) -> Dict[str, Any]:
        """Get metrics as a dictionary.
        
        Returns:
            Dictionary representation of metrics.
        """
        metrics_text = self.generate_metrics_text()
        return {"metrics": metrics_text, "timestamp": datetime.utcnow().isoformat()}
