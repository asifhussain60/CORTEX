"""Tier2 Governance: Core 030 Baselines

Performance SLA baselines and monitoring for CORE-030 compliance.

STUB IMPLEMENTATION - To be completed in Phase E.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class ComponentName(str, Enum):
    """Component names for SLA tracking."""
    INTENT_ROUTER = "intent_router"
    ORCHESTRATOR = "orchestrator"
    GOVERNANCE = "governance"
    MCP_SERVER = "mcp_server"
    KNOWLEDGE_GRAPH = "knowledge_graph"


class MetricType(str, Enum):
    """Metric types for performance tracking."""
    LATENCY = "latency"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"


@dataclass
class PerformanceSLA:
    """Performance SLA definition."""
    component: ComponentName
    metric: MetricType
    target_value: float
    threshold_warning: float
    threshold_critical: float
    unit: str = "ms"


@dataclass
class ComplianceViolation:
    """SLA compliance violation record."""
    component: ComponentName
    metric: MetricType
    measured_value: float
    target_value: float
    severity: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PerformanceMonitor:
    """Monitor performance against SLAs."""
    
    def __init__(self):
        """Initialize monitor."""
        self.measurements: List[Dict] = []
        self.violations: List[ComplianceViolation] = []
    
    def record_measurement(
        self, 
        component: ComponentName, 
        metric: MetricType, 
        value: float
    ) -> None:
        """Record a performance measurement."""
        self.measurements.append({
            "component": component,
            "metric": metric,
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_violations(self) -> List[ComplianceViolation]:
        """Get all violations."""
        return self.violations
    
    def check_compliance(
        self, 
        component: ComponentName, 
        metric: MetricType, 
        value: float, 
        sla: PerformanceSLA
    ) -> Optional[ComplianceViolation]:
        """Check if measurement violates SLA."""
        if value > sla.threshold_critical:
            violation = ComplianceViolation(
                component=component,
                metric=metric,
                measured_value=value,
                target_value=sla.target_value,
                severity="CRITICAL"
            )
            self.violations.append(violation)
            return violation
        elif value > sla.threshold_warning:
            violation = ComplianceViolation(
                component=component,
                metric=metric,
                measured_value=value,
                target_value=sla.target_value,
                severity="WARNING"
            )
            self.violations.append(violation)
            return violation
        return None


# Global SLA baselines
CORE_030_BASELINES = {
    ComponentName.INTENT_ROUTER: PerformanceSLA(
        component=ComponentName.INTENT_ROUTER,
        metric=MetricType.LATENCY,
        target_value=50.0,
        threshold_warning=75.0,
        threshold_critical=100.0,
        unit="ms"
    ),
    ComponentName.ORCHESTRATOR: PerformanceSLA(
        component=ComponentName.ORCHESTRATOR,
        metric=MetricType.LATENCY,
        target_value=100.0,
        threshold_warning=150.0,
        threshold_critical=200.0,
        unit="ms"
    ),
}

# Global monitor instance
_monitor_instance = None


def get_monitor() -> PerformanceMonitor:
    """Get global monitor instance."""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PerformanceMonitor()
    return _monitor_instance


def check_sla(component: ComponentName, metric: MetricType, value: float) -> Optional[ComplianceViolation]:
    """Check SLA compliance for a measurement."""
    if component in CORE_030_BASELINES:
        sla = CORE_030_BASELINES[component]
        return get_monitor().check_compliance(component, metric, value, sla)
    return None


def record_measurement(component: ComponentName, metric: MetricType, value: float) -> None:
    """Record a performance measurement."""
    get_monitor().record_measurement(component, metric, value)


__all__ = [
    "PerformanceSLA",
    "PerformanceMonitor",
    "ComplianceViolation",
    "CORE_030_BASELINES",
    "ComponentName",
    "MetricType",
    "check_sla",
    "record_measurement",
    "get_monitor",
]
