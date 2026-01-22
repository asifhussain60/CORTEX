"""Tier2 Governance: Core 030 Baselines

Performance SLA baselines and monitoring for CORE-030 compliance.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime


class ComponentName(str, Enum):
    """Component names for SLA tracking."""
    
    ORCHESTRATOR = "orchestrator"
    INTENT_ROUTER = "intent_router"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    DATABASE = "database"
    MCP_SERVER = "mcp_server"
    API = "api"
    AUDIT_LOGGING = "audit_logging"
    OUTPUT_VALIDATION = "output_validation"


class MetricType(str, Enum):
    """Metric types for performance tracking."""
    
    LATENCY = "latency"
    LATENCY_MS = "latency_ms"
    RESPONSE_TIME_MS = "response_time_ms"
    THROUGHPUT = "throughput"
    THROUGHPUT_RPS = "throughput_rps"
    ERROR_RATE = "error_rate"
    ERROR_RATE_PCT = "error_rate_pct"
    AVAILABILITY_PCT = "availability_pct"
    MEMORY = "memory"
    CPU = "cpu"


@dataclass
class PerformanceSLA:
    """Performance SLA definition.
    
    Defines performance baselines for CORE-030 compliance.
    
    Args:
        component: Component name
        metric: Metric type
        target: Target value (ideal)
        p99: 99th percentile acceptable value
        maximum: Maximum acceptable value
        unit: Unit of measurement (optional, defaults to "ms")
        description: Human-readable description (optional, defaults to empty)
    
    Raises:
        ValueError: If constraints are invalid (target > p99 > maximum)
    """
    
    component: str
    metric: str
    target: float
    p99: float
    maximum: float
    unit: str = "ms"
    description: str = ""
    
    def __post_init__(self) -> None:
        """Validate SLA constraints."""
        if self.target > self.p99:
            raise ValueError(f"Target ({self.target}) cannot be greater than p99 ({self.p99})")
        if self.p99 > self.maximum:
            raise ValueError(f"P99 ({self.p99}) cannot be greater than maximum ({self.maximum})")
        if self.target <= 0 or self.p99 <= 0 or self.maximum <= 0:
            raise ValueError("All values must be positive")
    
    def check_compliance(self, value: float) -> tuple:
        """Check compliance of a value against this SLA.
        
        Args:
            value: Value to check
        
        Returns:
            Tuple of (compliant, severity) where:
            - compliant: True if within maximum, False otherwise
            - severity: "ok" if within target, "warning" if within p99, 
                       "critical" if within maximum, "violation" if exceeds maximum
        """
        if value > self.maximum:
            return (False, "violation")
        elif value > self.p99:
            return (True, "critical")
        elif value > self.target:
            return (True, "warning")
        else:
            return (True, "ok")


@dataclass
class ComplianceViolation:
    """Record of SLA compliance violation.
    
    Args:
        component: Component that violated SLA
        metric: Metric that was violated
        measured_value: Actual measured value
        sla_target: SLA target value
        sla_maximum: SLA maximum value
        timestamp: When violation occurred (optional, defaults to now)
        severity: Violation severity (auto-calculated if not provided)
    """
    
    component: str
    metric: str
    measured_value: float
    sla_target: float
    sla_maximum: float
    timestamp: datetime = None
    severity: str = None
    
    def __post_init__(self) -> None:
        """Validate violation data and auto-calculate severity."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        
        if self.severity is None:
            # Auto-calculate severity based on measured value
            midpoint = self.sla_target + (self.sla_maximum - self.sla_target) / 2
            if self.measured_value >= self.sla_maximum:
                self.severity = "CRITICAL"
            elif self.measured_value >= midpoint:
                self.severity = "WARNING"
            else:
                self.severity = "INFO"
        
        if self.severity not in ["INFO", "WARNING", "CRITICAL"]:
            raise ValueError(f"Invalid severity: {self.severity}")


class PerformanceMonitor:
    """Performance monitoring and SLA compliance tracking.
    
    Tracks performance measurements and detects SLA violations.
    
    Args:
        slas: Dictionary of SLAs keyed by component, then metric
    """
    
    def __init__(self, slas: Optional[Dict[str, Dict[str, PerformanceSLA]]] = None) -> None:
        """Initialize monitor with SLAs."""
        self._slas = slas or {}
        self._violations: List[ComplianceViolation] = []
        self._measurements: Dict[tuple, List[tuple]] = {}
    
    def add_sla(self, sla: PerformanceSLA) -> None:
        """Add SLA to monitor.
        
        Args:
            sla: SLA to add
        """
        if sla.component not in self._slas:
            self._slas[sla.component] = {}
        self._slas[sla.component][sla.metric] = sla
    
    def get_sla(self, component: str, metric: str) -> PerformanceSLA:
        """Get SLA for component and metric.
        
        Args:
            component: Component name
            metric: Metric type
        
        Returns:
            PerformanceSLA for the component/metric
        
        Raises:
            ValueError: If component or metric not found
        """
        if component not in self._slas:
            raise ValueError(f"Unknown component: {component}")
        if metric not in self._slas[component]:
            raise ValueError(f"Unknown metric: {metric}")
        return self._slas[component][metric]
    
    def record_measurement(
        self,
        component: str,
        metric: str,
        value: float,
        timestamp: Optional[datetime] = None
    ) -> Optional[ComplianceViolation]:
        """Record performance measurement and check compliance.
        
        Args:
            component: Component name
            metric: Metric type
            value: Measured value
            timestamp: Measurement timestamp (defaults to now)
        
        Returns:
            ComplianceViolation if SLA exceeded, None otherwise
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Store measurement
        key = (component, metric)
        if key not in self._measurements:
            self._measurements[key] = []
        self._measurements[key].append((timestamp, value))
        
        # Check compliance
        sla = self._slas.get(component, {}).get(metric)
        if sla is None:
            return None
        
        # Check if value exceeds target (any level)
        if value <= sla.target:
            return None
        
        # Create violation record
        violation = ComplianceViolation(
            component=component,
            metric=metric,
            measured_value=value,
            sla_target=sla.target,
            sla_maximum=sla.maximum,
            timestamp=timestamp
        )
        
        self._violations.append(violation)
        return violation
    
    def get_violations(
        self,
        component: Optional[str] = None,
        metric: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[ComplianceViolation]:
        """Get recorded violations with optional filtering.
        
        Args:
            component: Filter by component
            metric: Filter by metric
            severity: Filter by severity
        
        Returns:
            List of matching violations
        """
        violations = self._violations
        
        if component:
            violations = [v for v in violations if v.component == component]
        if metric:
            violations = [v for v in violations if v.metric == metric]
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        return violations
    
    def get_measurements(
        self,
        component: str,
        metric: str
    ) -> List[tuple]:
        """Get all measurements for a component/metric.
        
        Args:
            component: Component name
            metric: Metric type
        
        Returns:
            List of (timestamp, value) tuples
        """
        key = (component, metric)
        return self._measurements.get(key, []).copy()
    
    def clear_violations(self) -> None:
        """Clear all recorded violations."""
        self._violations.clear()
    
    def get_statistics(
        self,
        component: str,
        metric: str
    ) -> Dict[str, float]:
        """Get statistics for measurements.
        
        Args:
            component: Component name
            metric: Metric type
        
        Returns:
            Dictionary with count, min, max, mean, p50, p95, p99
        """
        measurements = self.get_measurements(component, metric)
        if not measurements:
            return {
                "count": 0,
                "min": 0,
                "max": 0,
                "mean": 0,
                "p50": 0,
                "p95": 0,
                "p99": 0
            }
        
        values = [v for _, v in measurements]
        values_sorted = sorted(values)
        count = len(values)
        
        def percentile(data: List[float], p: float) -> float:
            """Calculate percentile."""
            if not data:
                return 0
            k = (len(data) - 1) * p / 100
            f = int(k)
            c = f + 1 if f < len(data) - 1 else f
            if f == c:
                return data[f]
            return data[f] * (c - k) + data[c] * (k - f)
        
        return {
            "count": count,
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / count,
            "p50": percentile(values_sorted, 50),
            "p95": percentile(values_sorted, 95),
            "p99": percentile(values_sorted, 99)
        }
    
    def check_compliance(
        self,
        component: str,
        metric: str,
        value: float
    ) -> bool:
        """Check if value is within SLA and record violation if not.
        
        Args:
            component: Component name
            metric: Metric type
            value: Value to check
        
        Returns:
            True if within SLA (p99), False otherwise
        """
        sla = self._slas.get(component, {}).get(metric)
        if sla is None:
            return True
        
        # Record violation if exceeds target
        if value > sla.target:
            violation = ComplianceViolation(
                component=component,
                metric=metric,
                measured_value=value,
                sla_target=sla.target,
                sla_maximum=sla.maximum,
                timestamp=datetime.now()
            )
            self._violations.append(violation)
        
        # Compliance is based on p99
        return value <= sla.p99


# CORE-030 baseline SLAs
CORE_030_BASELINES: Dict[str, Dict[str, PerformanceSLA]] = {
    "orchestrator": {
        "latency": PerformanceSLA(
            component="orchestrator",
            metric="latency",
            target=100,
            p99=500,
            maximum=1000,
            unit="ms",
            description="Orchestrator response time"
        ),
    },
    "intent_router": {
        "latency": PerformanceSLA(
            component="intent_router",
            metric="latency",
            target=50,
            p99=200,
            maximum=500,
            unit="ms",
            description="Intent routing time"
        ),
        "response_time_ms": PerformanceSLA(
            component="intent_router",
            metric="response_time_ms",
            target=50,
            p99=200,
            maximum=500,
            unit="ms",
            description="Intent router response time"
        ),
        "throughput_rps": PerformanceSLA(
            component="intent_router",
            metric="throughput_rps",
            target=10,
            p99=50,
            maximum=100,
            unit="rps",
            description="Intent router throughput (minimum acceptable throughput)"
        ),
        "error_rate_pct": PerformanceSLA(
            component="intent_router",
            metric="error_rate_pct",
            target=0.1,
            p99=1.0,
            maximum=5.0,
            unit="%",
            description="Intent router error rate"
        ),
    },
    "knowledge_graph": {
        "latency": PerformanceSLA(
            component="knowledge_graph",
            metric="latency",
            target=200,
            p99=1000,
            maximum=2000,
            unit="ms",
            description="Knowledge graph query time"
        ),
    },
    "database": {
        "latency": PerformanceSLA(
            component="database",
            metric="latency",
            target=10,
            p99=50,
            maximum=100,
            unit="ms",
            description="Database query time"
        ),
    },
    "mcp_server": {
        "latency": PerformanceSLA(
            component="mcp_server",
            metric="latency",
            target=100,
            p99=500,
            maximum=1000,
            unit="ms",
            description="MCP tool invocation time"
        ),
    },
    "audit_logging": {
        "latency_ms": PerformanceSLA(
            component="audit_logging",
            metric="latency_ms",
            target=10,
            p99=50,
            maximum=100,
            unit="ms",
            description="Audit log write latency"
        ),
        "availability_pct": PerformanceSLA(
            component="audit_logging",
            metric="availability_pct",
            target=99.0,
            p99=99.5,
            maximum=99.9,
            unit="%",
            description="Audit logging availability"
        ),
    },
    "output_validation": {
        "latency_ms": PerformanceSLA(
            component="output_validation",
            metric="latency_ms",
            target=50,
            p99=200,
            maximum=500,
            unit="ms",
            description="Output validation latency"
        ),
        "error_rate_pct": PerformanceSLA(
            component="output_validation",
            metric="error_rate_pct",
            target=0.1,
            p99=1.0,
            maximum=5.0,
            unit="%",
            description="Output validation error rate"
        ),
    },
}


# Global monitor instance
_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance.
    
    Returns:
        Global PerformanceMonitor instance
    """
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor(CORE_030_BASELINES)
    return _monitor


def check_sla(component: str, metric: str, value: float) -> bool:
    """Check if value is within SLA (convenience function).
    
    Args:
        component: Component name
        metric: Metric type
        value: Value to check
    
    Returns:
        True if within SLA, False otherwise
    """
    return get_monitor().check_compliance(component, metric, value)


def record_measurement(
    component: str,
    metric: str,
    value: float,
    timestamp: Optional[datetime] = None
) -> Optional[ComplianceViolation]:
    """Record measurement and check compliance (convenience function).
    
    Args:
        component: Component name
        metric: Metric type
        value: Measured value
        timestamp: Measurement timestamp (defaults to now)
    
    Returns:
        ComplianceViolation if SLA exceeded, None otherwise
    """
    return get_monitor().record_measurement(component, metric, value, timestamp)
