"""
CORE-030: Performance Baselines and SLAs

This module defines performance expectations and Service Level Agreements (SLAs) 
for all critical CORTEX components. It provides:

1. SLA Definitions: Target, P99, and maximum thresholds for each component
2. SLA Validation: Check if measured values comply with defined SLAs
3. Performance Metrics: Standardized metric definitions across the system
4. Compliance Tracking: Audit trail of SLA compliance/violations

CORE-030 COMPLIANCE:
- All async operations must have documented SLAs
- Performance violations trigger warnings/alerts
- Compliance metrics exposed for monitoring
- Baselines reviewed quarterly with stakeholders

GOVERNANCE:
- AC-CORE-030-01: SLA definitions established
- AC-CORE-030-02: Monitoring infrastructure ready
- AC-CORE-030-03: Alerting configured
- AC-CORE-030-04: Compliance tracking operational

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Type of performance metric."""
    RESPONSE_TIME_MS = "response_time_ms"
    THROUGHPUT_RPS = "throughput_rps"
    ERROR_RATE_PCT = "error_rate_pct"
    LATENCY_MS = "latency_ms"
    AVAILABILITY_PCT = "availability_pct"
    QUEUE_DEPTH = "queue_depth"


class ComponentName(Enum):
    """Registered components with SLA requirements."""
    INTENT_ROUTER = "intent_router"
    AUDIT_LOGGING = "audit_logging"
    OUTPUT_VALIDATION = "output_validation"
    THREAD_POOL = "thread_pool"
    LLM_INTERFACE = "llm_interface"
    DATABASE = "database"
    CACHE_LAYER = "cache_layer"


@dataclass
class PerformanceSLA:
    """Service Level Agreement for a component metric.
    
    Attributes:
        component: Component name
        metric: Metric type
        target: Target value (50th percentile acceptable range)
        p99: 99th percentile target (most requests should be better than this)
        maximum: Absolute maximum value (hard limit)
        unit: Unit of measurement
        description: Human-readable description
    """
    component: str
    metric: str
    target: float
    p99: float
    maximum: float
    unit: str = ""
    description: str = ""
    
    def __post_init__(self):
        """Validate SLA constraints."""
        if not (self.target <= self.p99 <= self.maximum):
            raise ValueError(
                f"Invalid SLA: target ({self.target}) must be <= p99 ({self.p99}) "
                f"must be <= maximum ({self.maximum})"
            )
    
    def check_compliance(self, value: float) -> Tuple[bool, str]:
        """Check if value complies with SLA.
        
        Returns:
            Tuple of (compliant: bool, severity: str)
            - Severity: "ok", "warning", "critical"
        """
        if value <= self.target:
            return (True, "ok")
        elif value <= self.p99:
            return (True, "warning")
        elif value <= self.maximum:
            return (True, "critical")
        else:
            return (False, "violation")


# Define all SLAs for components
CORE_030_BASELINES: Dict[str, Dict[str, PerformanceSLA]] = {
    
    ComponentName.INTENT_ROUTER.value: {
        MetricType.RESPONSE_TIME_MS.value: PerformanceSLA(
            component=ComponentName.INTENT_ROUTER.value,
            metric=MetricType.RESPONSE_TIME_MS.value,
            target=500,          # 50th percentile: < 500ms
            p99=1500,            # 99th percentile: < 1500ms
            maximum=2000,        # Hard max: < 2000ms (3σ)
            unit="ms",
            description="Time for intent router to classify request"
        ),
        MetricType.THROUGHPUT_RPS.value: PerformanceSLA(
            component=ComponentName.INTENT_ROUTER.value,
            metric=MetricType.THROUGHPUT_RPS.value,
            target=100,          # Sustain 100 req/sec
            p99=150,             # 99th percentile: 150 req/sec
            maximum=200,         # Burst maximum: 200 req/sec
            unit="req/sec",
            description="Request throughput capacity"
        ),
        MetricType.ERROR_RATE_PCT.value: PerformanceSLA(
            component=ComponentName.INTENT_ROUTER.value,
            metric=MetricType.ERROR_RATE_PCT.value,
            target=0.1,          # Target: 0.1% error rate
            p99=0.5,             # 99th percentile: 0.5%
            maximum=1.0,         # Hard max: 1% (99% availability)
            unit="%",
            description="Classification error rate"
        ),
    },
    
    ComponentName.AUDIT_LOGGING.value: {
        MetricType.LATENCY_MS.value: PerformanceSLA(
            component=ComponentName.AUDIT_LOGGING.value,
            metric=MetricType.LATENCY_MS.value,
            target=50,           # Log entry written within 50ms
            p99=200,             # 99th percentile: 200ms
            maximum=500,         # Absolute max: 500ms
            unit="ms",
            description="Audit log entry write latency"
        ),
        MetricType.AVAILABILITY_PCT.value: PerformanceSLA(
            component=ComponentName.AUDIT_LOGGING.value,
            metric=MetricType.AVAILABILITY_PCT.value,
            target=98.0,         # 98% minimum availability target
            p99=99.0,            # 99th percentile: 99%
            maximum=99.5,        # Maximum achievable: 99.5%
            unit="%",
            description="Audit logging system availability"
        ),
    },
    
    ComponentName.OUTPUT_VALIDATION.value: {
        MetricType.LATENCY_MS.value: PerformanceSLA(
            component=ComponentName.OUTPUT_VALIDATION.value,
            metric=MetricType.LATENCY_MS.value,
            target=100,          # Validate within 100ms
            p99=300,             # 99th percentile: 300ms
            maximum=500,         # Hard max: 500ms
            unit="ms",
            description="LLM output validation latency"
        ),
        MetricType.ERROR_RATE_PCT.value: PerformanceSLA(
            component=ComponentName.OUTPUT_VALIDATION.value,
            metric=MetricType.ERROR_RATE_PCT.value,
            target=0.05,         # 0.05% false negative rate
            p99=0.1,             # 99th percentile: 0.1%
            maximum=0.5,         # Hard max: 0.5%
            unit="%",
            description="Output validation false negative rate"
        ),
    },
    
    ComponentName.THREAD_POOL.value: {
        MetricType.QUEUE_DEPTH.value: PerformanceSLA(
            component=ComponentName.THREAD_POOL.value,
            metric=MetricType.QUEUE_DEPTH.value,
            target=5,            # Ideal queue depth: 5 tasks
            p99=20,              # 99th percentile: 20 tasks
            maximum=100,         # Hard max: 100 tasks (reject beyond)
            unit="tasks",
            description="Thread pool queue depth"
        ),
    },
    
    ComponentName.LLM_INTERFACE.value: {
        MetricType.RESPONSE_TIME_MS.value: PerformanceSLA(
            component=ComponentName.LLM_INTERFACE.value,
            metric=MetricType.RESPONSE_TIME_MS.value,
            target=5000,         # LLM response target: 5s
            p99=15000,           # 99th percentile: 15s
            maximum=30000,       # Hard max: 30s timeout
            unit="ms",
            description="LLM API response latency"
        ),
        MetricType.AVAILABILITY_PCT.value: PerformanceSLA(
            component=ComponentName.LLM_INTERFACE.value,
            metric=MetricType.AVAILABILITY_PCT.value,
            target=95.0,         # 95% minimum availability (account for provider downtime)
            p99=97.0,            # 99th percentile: 97%
            maximum=98.0,        # Maximum achievable: 98%
            unit="%",
            description="LLM provider availability"
        ),
    },
    
    ComponentName.DATABASE.value: {
        MetricType.RESPONSE_TIME_MS.value: PerformanceSLA(
            component=ComponentName.DATABASE.value,
            metric=MetricType.RESPONSE_TIME_MS.value,
            target=50,           # DB query target: 50ms
            p99=200,             # 99th percentile: 200ms
            maximum=1000,        # Hard max: 1s
            unit="ms",
            description="Database query response time"
        ),
        MetricType.AVAILABILITY_PCT.value: PerformanceSLA(
            component=ComponentName.DATABASE.value,
            metric=MetricType.AVAILABILITY_PCT.value,
            target=98.0,         # 98% minimum availability target
            p99=99.0,            # 99th percentile: 99%
            maximum=99.5,        # Maximum achievable: 99.5%
            unit="%",
            description="Database system availability"
        ),
    },
}


@dataclass
class ComplianceViolation:
    """Record of SLA compliance violation."""
    component: str
    metric: str
    measured_value: float
    sla_target: float
    sla_maximum: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = ""
    details: str = ""
    
    def __post_init__(self):
        """Auto-determine severity."""
        if self.measured_value > self.sla_maximum:
            self.severity = "CRITICAL"
        elif self.measured_value > (self.sla_target + (self.sla_maximum - self.sla_target) / 2):
            self.severity = "WARNING"
        else:
            self.severity = "INFO"


class PerformanceMonitor:
    """Monitor and validate performance metrics against SLAs."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.violations: List[ComplianceViolation] = []
        self.measurements: Dict[Tuple[str, str], List[float]] = {}
    
    def get_sla(self, component: str, metric: str) -> PerformanceSLA:
        """Get SLA definition for component metric.
        
        Args:
            component: Component name
            metric: Metric name
            
        Returns:
            PerformanceSLA object
            
        Raises:
            ValueError: If component or metric not found
        """
        if component not in CORE_030_BASELINES:
            raise ValueError(f"Unknown component: {component}")
        
        baselines = CORE_030_BASELINES[component]
        if metric not in baselines:
            raise ValueError(f"Unknown metric for {component}: {metric}")
        
        return baselines[metric]
    
    def check_compliance(self, component: str, metric: str, value: float) -> bool:
        """Check if measured value complies with SLA.
        
        Args:
            component: Component name
            metric: Metric name
            value: Measured value
            
        Returns:
            True if compliant, False if violation
        """
        sla = self.get_sla(component, metric)
        compliant, severity = sla.check_compliance(value)
        
        if not compliant or severity == "warning":
            violation = ComplianceViolation(
                component=component,
                metric=metric,
                measured_value=value,
                sla_target=sla.target,
                sla_maximum=sla.maximum,
                severity=severity,
                details=f"{metric}={value} exceeds SLA"
            )
            self.violations.append(violation)
            
            if severity == "CRITICAL":
                logger.error(f"SLA VIOLATION: {component}/{metric}={value} (max={sla.maximum})")
            elif severity == "warning":
                logger.warning(f"SLA WARNING: {component}/{metric}={value} (target={sla.target})")
        
        return compliant
    
    def record_measurement(self, component: str, metric: str, value: float) -> None:
        """Record a performance measurement.
        
        Args:
            component: Component name
            metric: Metric name
            value: Measured value
        """
        key = (component, metric)
        if key not in self.measurements:
            self.measurements[key] = []
        self.measurements[key].append(value)
    
    def get_statistics(self, component: str, metric: str) -> Dict[str, float]:
        """Get statistical summary of measurements.
        
        Args:
            component: Component name
            metric: Metric name
            
        Returns:
            Dictionary with min, max, mean, p99, etc.
        """
        key = (component, metric)
        if key not in self.measurements or not self.measurements[key]:
            return {}
        
        values = sorted(self.measurements[key])
        n = len(values)
        
        return {
            "count": n,
            "min": values[0],
            "max": values[-1],
            "mean": sum(values) / n,
            "p50": values[n // 2],
            "p99": values[int(n * 0.99)] if n > 100 else values[-1],
            "p999": values[int(n * 0.999)] if n > 1000 else values[-1],
        }
    
    def get_violations(self, component: Optional[str] = None) -> List[ComplianceViolation]:
        """Get list of recorded violations.
        
        Args:
            component: Optional component filter
            
        Returns:
            List of ComplianceViolation objects
        """
        if component is None:
            return self.violations
        
        return [v for v in self.violations if v.component == component]
    
    def clear_violations(self) -> None:
        """Clear violation history."""
        self.violations.clear()


# Global monitor instance
_global_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance.
    
    Returns:
        PerformanceMonitor instance
    """
    return _global_monitor


def check_sla(component: str, metric: str, value: float) -> bool:
    """Convenience function to check SLA compliance.
    
    Args:
        component: Component name
        metric: Metric name
        value: Measured value
        
    Returns:
        True if compliant
    """
    return _global_monitor.check_compliance(component, metric, value)


def record_measurement(component: str, metric: str, value: float) -> None:
    """Convenience function to record a measurement.
    
    Args:
        component: Component name
        metric: Metric name
        value: Measured value
    """
    _global_monitor.record_measurement(component, metric, value)
