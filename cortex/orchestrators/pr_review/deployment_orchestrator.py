"""
Phase 52 S6: Deployment & Monitoring Orchestrator
Handles deployment strategies, monitoring setup, health checks, and metrics collection.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DeploymentType(Enum):
    """Deployment strategy types."""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    IMMUTABLE = "immutable"


class HealthCheckType(Enum):
    """Types of health checks."""
    HTTP = "http"
    TCP = "tcp"
    SCRIPT = "script"
    CONTAINER = "container"


class MetricType(Enum):
    """Metric types for monitoring."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""
    check_type: HealthCheckType
    interval_seconds: int
    timeout_seconds: int
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    endpoint: Optional[str] = None
    script_path: Optional[str] = None

    def validate(self) -> Tuple[bool, str]:
        """Validate health check configuration."""
        if self.interval_seconds <= 0:
            return (False, "Interval must be positive")
        if self.timeout_seconds <= 0:
            return (False, "Timeout must be positive")
        if self.timeout_seconds >= self.interval_seconds:
            return (False, "Timeout cannot exceed interval")
        if self.check_type == HealthCheckType.HTTP and not self.endpoint:
            return (False, "HTTP checks require endpoint")
        if self.check_type == HealthCheckType.SCRIPT and not self.script_path:
            return (False, "Script checks require script_path")
        return (True, "Valid")


@dataclass
class MetricDefinition:
    """Definition of a metric to collect."""
    name: str
    metric_type: MetricType
    unit: str
    description: str
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "unit": self.unit,
            "description": self.description,
            "tags": self.tags
        }


@dataclass
class AlertRule:
    """Alert rule for monitoring."""
    name: str
    metric_name: str
    condition: str  # e.g., "value > 100"
    severity: AlertSeverity
    duration_seconds: int
    description: str

    def validate(self) -> Tuple[bool, str]:
        """Validate alert rule."""
        if not self.metric_name:
            return (False, "Metric name required")
        if not self.condition:
            return (False, "Condition required")
        if self.duration_seconds <= 0:
            return (False, "Duration must be positive")
        return (True, "Valid")


@dataclass
class DeploymentConfig:
    """Deployment configuration."""
    deployment_type: DeploymentType
    replicas: int = 3
    max_surge: float = 0.25
    max_unavailable: float = 0.25
    termination_grace_period_seconds: int = 30
    revision_history_limit: int = 10
    canary_percentage: Optional[int] = None  # For canary deployments

    def validate(self) -> Tuple[bool, str]:
        """Validate deployment config."""
        if self.replicas <= 0:
            return (False, "Replicas must be positive")
        if not (0 <= self.max_surge <= 1):
            return (False, "max_surge must be between 0 and 1")
        if not (0 <= self.max_unavailable <= 1):
            return (False, "max_unavailable must be between 0 and 1")
        if self.deployment_type == DeploymentType.CANARY and not self.canary_percentage:
            return (False, "Canary deployments require canary_percentage")
        if self.deployment_type == DeploymentType.CANARY and not (0 < self.canary_percentage < 100):
            return (False, "Canary percentage must be between 0 and 100")
        return (True, "Valid")


@dataclass
class DeploymentPlan:
    """Plan for deployment execution."""
    deployment_id: str
    deployment_type: DeploymentType
    stages: List[str]
    estimated_duration_minutes: int
    rollback_strategy: str
    validation_steps: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "deployment_id": self.deployment_id,
            "type": self.deployment_type.value,
            "stages": self.stages,
            "estimated_duration": f"{self.estimated_duration_minutes}m",
            "rollback_strategy": self.rollback_strategy,
            "validation_steps": self.validation_steps
        }


@dataclass
class DeploymentMetrics:
    """Metrics for deployment monitoring."""
    deployment_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    successful_replicas: int = 0
    failed_replicas: int = 0
    health_check_failures: int = 0
    error_messages: List[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.successful_replicas + self.failed_replicas
        return (self.successful_replicas / total * 100) if total > 0 else 0.0

    @property
    def duration_seconds(self) -> int:
        """Calculate duration."""
        end = self.end_time or datetime.now()
        return int((end - self.start_time).total_seconds())


@dataclass
class HealthStatus:
    """Current health status."""
    timestamp: datetime
    overall_healthy: bool
    component_statuses: Dict[str, bool]
    metrics: Dict[str, float]
    last_check_time: datetime
    consecutive_failures: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "overall_healthy": self.overall_healthy,
            "components": self.component_statuses,
            "metrics": self.metrics,
            "last_check_time": self.last_check_time.isoformat(),
            "consecutive_failures": self.consecutive_failures
        }


class HealthChecker:
    """Manages health checks."""

    def __init__(self):
        """Initialize health checker."""
        self.checks: Dict[str, HealthCheckConfig] = {}
        self.last_results: Dict[str, Tuple[datetime, bool]] = {}

    def add_check(self, name: str, config: HealthCheckConfig) -> Tuple[bool, str]:
        """Add a health check."""
        valid, msg = config.validate()
        if not valid:
            return (False, msg)
        self.checks[name] = config
        logger.info(f"Added health check: {name}")
        return (True, f"Added health check {name}")

    def run_check(self, name: str) -> Tuple[bool, str]:
        """Run a specific health check."""
        if name not in self.checks:
            return (False, f"Check not found: {name}")

        config = self.checks[name]

        # Simulate health check based on type
        if config.check_type == HealthCheckType.HTTP:
            result = self._check_http(config)
        elif config.check_type == HealthCheckType.TCP:
            result = self._check_tcp(config)
        elif config.check_type == HealthCheckType.SCRIPT:
            result = self._check_script(config)
        else:
            result = (True, "Container check passed")

        self.last_results[name] = (datetime.now(), result[0])
        return result

    def _check_http(self, config: HealthCheckConfig) -> Tuple[bool, str]:
        """Check HTTP endpoint."""
        # In production, would use requests library
        return (True, f"HTTP check passed for {config.endpoint}")

    def _check_tcp(self, config: HealthCheckConfig) -> Tuple[bool, str]:
        """Check TCP port."""
        # In production, would use socket
        return (True, "TCP check passed")

    def _check_script(self, config: HealthCheckConfig) -> Tuple[bool, str]:
        """Check using script."""
        # In production, would execute script
        return (True, f"Script check passed: {config.script_path}")

    def get_status(self) -> HealthStatus:
        """Get overall health status."""
        component_statuses = {}
        for name, (timestamp, healthy) in self.last_results.items():
            component_statuses[name] = healthy

        overall_healthy = all(component_statuses.values()) if component_statuses else True

        return HealthStatus(
            timestamp=datetime.now(),
            overall_healthy=overall_healthy,
            component_statuses=component_statuses,
            metrics={"component_count": len(component_statuses)},
            last_check_time=datetime.now()
        )


class MetricsCollector:
    """Collects and stores metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, MetricDefinition] = {}
        self.data: Dict[str, List[Tuple[datetime, float]]] = {}
        self.retention_hours = 24

    def define_metric(self, definition: MetricDefinition) -> Tuple[bool, str]:
        """Define a new metric."""
        if definition.name in self.metrics:
            return (False, f"Metric already defined: {definition.name}")
        self.metrics[definition.name] = definition
        self.data[definition.name] = []
        logger.info(f"Defined metric: {definition.name}")
        return (True, f"Defined metric {definition.name}")

    def record_metric(self, metric_name: str, value: float) -> Tuple[bool, str]:
        """Record a metric value."""
        if metric_name not in self.metrics:
            return (False, f"Metric not defined: {metric_name}")

        self.data[metric_name].append((datetime.now(), value))
        # Clean old data
        cutoff = datetime.now() - timedelta(hours=self.retention_hours)
        self.data[metric_name] = [
            (ts, v) for ts, v in self.data[metric_name] if ts > cutoff
        ]
        return (True, f"Recorded metric {metric_name}")

    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if metric_name not in self.data:
            return {}

        values = [v for _, v in self.data[metric_name]]
        if not values:
            return {}

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else 0
        }

    def get_all_metrics(self) -> Dict[str, dict]:
        """Get all metric definitions."""
        return {name: defn.to_dict() for name, defn in self.metrics.items()}


class Alerting:
    """Manages alert rules and evaluations."""

    def __init__(self, metrics_collector: MetricsCollector):
        """Initialize alerting system."""
        self.metrics_collector = metrics_collector
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, datetime] = {}

    def add_rule(self, rule: AlertRule) -> Tuple[bool, str]:
        """Add an alert rule."""
        valid, msg = rule.validate()
        if not valid:
            return (False, msg)
        if rule.name in self.rules:
            return (False, f"Rule already exists: {rule.name}")
        self.rules[rule.name] = rule
        logger.info(f"Added alert rule: {rule.name}")
        return (True, f"Added alert rule {rule.name}")

    def evaluate_rules(self) -> List[Tuple[str, AlertSeverity, str]]:
        """Evaluate all alert rules."""
        alerts = []
        for rule_name, rule in self.rules.items():
            stats = self.metrics_collector.get_metric_stats(rule.metric_name)
            if stats and self._evaluate_condition(rule.condition, stats["latest"]):
                alerts.append((rule_name, rule.severity, rule.description))
                self.active_alerts[rule_name] = datetime.now()
        return alerts

    def _evaluate_condition(self, condition: str, value: float) -> bool:
        """Evaluate a condition string."""
        # Simple condition evaluation (e.g., "value > 100")
        try:
            return eval(condition.replace("value", str(value)))
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False


class DeploymentOrchestrator:
    """Main deployment orchestrator."""

    def __init__(self):
        """Initialize deployment orchestrator."""
        self.deployments: Dict[str, DeploymentPlan] = {}
        self.deployment_metrics: Dict[str, DeploymentMetrics] = {}
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        self.alerting = Alerting(self.metrics_collector)

    def plan_deployment(
        self,
        deployment_type: DeploymentType,
        config: DeploymentConfig
    ) -> Tuple[bool, DeploymentPlan]:
        """Plan a deployment."""
        valid, msg = config.validate()
        if not valid:
            return (False, None)

        deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Generate stages based on deployment type
        stages = self._generate_stages(deployment_type, config)

        # Estimate duration
        estimated_duration = len(stages) * 5

        plan = DeploymentPlan(
            deployment_id=deployment_id,
            deployment_type=deployment_type,
            stages=stages,
            estimated_duration_minutes=estimated_duration,
            rollback_strategy="automated_rollback_on_failure",
            validation_steps=[
                "Verify replicas are ready",
                "Run health checks",
                "Check metrics thresholds",
                "Validate service connectivity"
            ]
        )

        self.deployments[deployment_id] = plan
        logger.info(f"Created deployment plan: {deployment_id}")
        return (True, plan)

    def _generate_stages(
        self,
        deployment_type: DeploymentType,
        config: DeploymentConfig
    ) -> List[str]:
        """Generate deployment stages."""
        if deployment_type == DeploymentType.BLUE_GREEN:
            return [
                "Provision green environment",
                "Deploy to green",
                "Run smoke tests",
                "Switch traffic to green",
                "Decommission blue"
            ]
        elif deployment_type == DeploymentType.CANARY:
            return [
                "Deploy canary (10%)",
                "Monitor canary metrics",
                "Gradually increase traffic",
                "Full deployment (100%)",
                "Cleanup canary"
            ]
        elif deployment_type == DeploymentType.ROLLING:
            return [
                "Update replica set",
                "Rolling update (batch 1)",
                "Health checks",
                "Rolling update (batch 2)",
                "Verify all replicas"
            ]
        else:
            return [
                "Pull new image",
                "Create new container",
                "Health verification",
                "Cleanup old container"
            ]

    def execute_deployment(self, deployment_id: str) -> Tuple[bool, DeploymentMetrics]:
        """Execute a deployment."""
        if deployment_id not in self.deployments:
            return (False, None)

        plan = self.deployments[deployment_id]
        metrics = DeploymentMetrics(
            deployment_id=deployment_id,
            start_time=datetime.now()
        )

        # Simulate deployment execution
        metrics.successful_replicas = plan.deployment_type.value.count('a') % 3 + 1
        metrics.failed_replicas = 0
        metrics.end_time = datetime.now()

        self.deployment_metrics[deployment_id] = metrics
        logger.info(f"Executed deployment: {deployment_id}")
        return (True, metrics)

    def get_deployment_status(self, deployment_id: str) -> Optional[Dict]:
        """Get deployment status."""
        if deployment_id not in self.deployment_metrics:
            return None

        metrics = self.deployment_metrics[deployment_id]
        return {
            "deployment_id": deployment_id,
            "success_rate": f"{metrics.success_rate:.1f}%",
            "duration_seconds": metrics.duration_seconds,
            "successful_replicas": metrics.successful_replicas,
            "failed_replicas": metrics.failed_replicas,
            "health_check_failures": metrics.health_check_failures
        }

    def get_system_health(self) -> Dict:
        """Get overall system health."""
        health_status = self.health_checker.get_status()
        return {
            "timestamp": health_status.timestamp.isoformat(),
            "overall_healthy": health_status.overall_healthy,
            "components": health_status.component_statuses,
            "active_deployments": len(self.deployment_metrics),
            "active_alerts": len(self.alerting.active_alerts)
        }
