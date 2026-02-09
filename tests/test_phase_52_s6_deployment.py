"""
Tests for Phase 52 S6: Deployment & Monitoring Orchestrator
"""

import pytest
from datetime import datetime, timedelta
from cortex.orchestrators.pr_review.deployment_orchestrator import (
    DeploymentType, HealthCheckType, MetricType, AlertSeverity,
    HealthCheckConfig, MetricDefinition, AlertRule, DeploymentConfig,
    DeploymentOrchestrator, HealthChecker, MetricsCollector, Alerting
)


class TestHealthCheckConfig:
    """Tests for health check configuration."""
    
    def test_valid_http_config(self):
        """Test valid HTTP config."""
        config = HealthCheckConfig(
            check_type=HealthCheckType.HTTP,
            interval_seconds=10,
            timeout_seconds=5,
            endpoint="http://localhost:8000/health"
        )
        valid, msg = config.validate()
        assert valid
        assert msg == "Valid"
    
    def test_invalid_interval(self):
        """Test invalid interval."""
        config = HealthCheckConfig(
            check_type=HealthCheckType.HTTP,
            interval_seconds=-1,
            timeout_seconds=5,
            endpoint="http://localhost:8000/health"
        )
        valid, msg = config.validate()
        assert not valid
        assert "positive" in msg
    
    def test_http_missing_endpoint(self):
        """Test HTTP check missing endpoint."""
        config = HealthCheckConfig(
            check_type=HealthCheckType.HTTP,
            interval_seconds=10,
            timeout_seconds=5
        )
        valid, msg = config.validate()
        assert not valid
        assert "endpoint" in msg
    
    def test_script_missing_path(self):
        """Test script check missing path."""
        config = HealthCheckConfig(
            check_type=HealthCheckType.SCRIPT,
            interval_seconds=10,
            timeout_seconds=5
        )
        valid, msg = config.validate()
        assert not valid
        assert "script_path" in msg


class TestMetricDefinition:
    """Tests for metric definitions."""
    
    def test_create_metric(self):
        """Test creating metric definition."""
        metric = MetricDefinition(
            name="request_latency",
            metric_type=MetricType.HISTOGRAM,
            unit="milliseconds",
            description="Request latency histogram"
        )
        assert metric.name == "request_latency"
        assert metric.metric_type == MetricType.HISTOGRAM
    
    def test_metric_to_dict(self):
        """Test metric dictionary conversion."""
        metric = MetricDefinition(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            unit="percentage",
            description="CPU usage gauge",
            tags={"service": "api"}
        )
        data = metric.to_dict()
        assert data["name"] == "cpu_usage"
        assert data["type"] == "gauge"
        assert data["tags"]["service"] == "api"


class TestAlertRule:
    """Tests for alert rules."""
    
    def test_valid_alert_rule(self):
        """Test valid alert rule."""
        rule = AlertRule(
            name="high_latency",
            metric_name="request_latency",
            condition="value > 1000",
            severity=AlertSeverity.WARNING,
            duration_seconds=300,
            description="Alert when latency > 1s"
        )
        valid, msg = rule.validate()
        assert valid
        assert msg == "Valid"
    
    def test_invalid_duration(self):
        """Test invalid duration."""
        rule = AlertRule(
            name="high_latency",
            metric_name="request_latency",
            condition="value > 1000",
            severity=AlertSeverity.WARNING,
            duration_seconds=0,
            description="Alert"
        )
        valid, msg = rule.validate()
        assert not valid
        assert "Duration" in msg


class TestDeploymentConfig:
    """Tests for deployment configuration."""
    
    def test_blue_green_config(self):
        """Test blue-green deployment config."""
        config = DeploymentConfig(
            deployment_type=DeploymentType.BLUE_GREEN,
            replicas=3
        )
        valid, msg = config.validate()
        assert valid
    
    def test_canary_config(self):
        """Test canary deployment config."""
        config = DeploymentConfig(
            deployment_type=DeploymentType.CANARY,
            replicas=3,
            canary_percentage=10
        )
        valid, msg = config.validate()
        assert valid
    
    def test_canary_missing_percentage(self):
        """Test canary config missing percentage."""
        config = DeploymentConfig(
            deployment_type=DeploymentType.CANARY,
            replicas=3
        )
        valid, msg = config.validate()
        assert not valid
        assert "canary_percentage" in msg
    
    def test_invalid_replicas(self):
        """Test invalid replicas."""
        config = DeploymentConfig(
            deployment_type=DeploymentType.ROLLING,
            replicas=0
        )
        valid, msg = config.validate()
        assert not valid


class TestHealthChecker:
    """Tests for health checker."""
    
    def test_add_check(self):
        """Test adding health check."""
        checker = HealthChecker()
        config = HealthCheckConfig(
            check_type=HealthCheckType.HTTP,
            interval_seconds=10,
            timeout_seconds=5,
            endpoint="http://localhost:8000/health"
        )
        valid, msg = checker.add_check("api_health", config)
        assert valid
        assert "api_health" in checker.checks
    
    def test_add_invalid_check(self):
        """Test adding invalid health check."""
        checker = HealthChecker()
        config = HealthCheckConfig(
            check_type=HealthCheckType.HTTP,
            interval_seconds=-1,
            timeout_seconds=5
        )
        valid, msg = checker.add_check("bad_check", config)
        assert not valid
    
    def test_run_check(self):
        """Test running health check."""
        checker = HealthChecker()
        config = HealthCheckConfig(
            check_type=HealthCheckType.HTTP,
            interval_seconds=10,
            timeout_seconds=5,
            endpoint="http://localhost:8000/health"
        )
        checker.add_check("api_health", config)
        valid, msg = checker.run_check("api_health")
        assert valid
    
    def test_run_nonexistent_check(self):
        """Test running nonexistent check."""
        checker = HealthChecker()
        valid, msg = checker.run_check("nonexistent")
        assert not valid
    
    def test_get_status(self):
        """Test getting health status."""
        checker = HealthChecker()
        config = HealthCheckConfig(
            check_type=HealthCheckType.HTTP,
            interval_seconds=10,
            timeout_seconds=5,
            endpoint="http://localhost:8000/health"
        )
        checker.add_check("api_health", config)
        checker.run_check("api_health")
        status = checker.get_status()
        assert status.overall_healthy
        assert "api_health" in status.component_statuses


class TestMetricsCollector:
    """Tests for metrics collector."""
    
    def test_define_metric(self):
        """Test defining metric."""
        collector = MetricsCollector()
        metric = MetricDefinition(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            unit="percentage",
            description="CPU usage"
        )
        valid, msg = collector.define_metric(metric)
        assert valid
        assert "cpu_usage" in collector.metrics
    
    def test_duplicate_metric(self):
        """Test defining duplicate metric."""
        collector = MetricsCollector()
        metric = MetricDefinition(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            unit="percentage",
            description="CPU usage"
        )
        collector.define_metric(metric)
        valid, msg = collector.define_metric(metric)
        assert not valid
        assert "already defined" in msg
    
    def test_record_metric(self):
        """Test recording metric value."""
        collector = MetricsCollector()
        metric = MetricDefinition(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            unit="percentage",
            description="CPU usage"
        )
        collector.define_metric(metric)
        valid, msg = collector.record_metric("cpu_usage", 45.5)
        assert valid
    
    def test_get_metric_stats(self):
        """Test getting metric statistics."""
        collector = MetricsCollector()
        metric = MetricDefinition(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            unit="percentage",
            description="CPU usage"
        )
        collector.define_metric(metric)
        collector.record_metric("cpu_usage", 40.0)
        collector.record_metric("cpu_usage", 50.0)
        collector.record_metric("cpu_usage", 60.0)
        
        stats = collector.get_metric_stats("cpu_usage")
        assert stats["count"] == 3
        assert stats["min"] == 40.0
        assert stats["max"] == 60.0
        assert stats["avg"] == 50.0


class TestAlerting:
    """Tests for alerting system."""
    
    def test_add_rule(self):
        """Test adding alert rule."""
        collector = MetricsCollector()
        alerting = Alerting(collector)
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition="value > 80",
            severity=AlertSeverity.CRITICAL,
            duration_seconds=300,
            description="High CPU usage"
        )
        valid, msg = alerting.add_rule(rule)
        assert valid
        assert "high_cpu" in alerting.rules
    
    def test_duplicate_rule(self):
        """Test adding duplicate rule."""
        collector = MetricsCollector()
        alerting = Alerting(collector)
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition="value > 80",
            severity=AlertSeverity.CRITICAL,
            duration_seconds=300,
            description="High CPU usage"
        )
        alerting.add_rule(rule)
        valid, msg = alerting.add_rule(rule)
        assert not valid
    
    def test_evaluate_rules(self):
        """Test evaluating alert rules."""
        collector = MetricsCollector()
        alerting = Alerting(collector)
        
        metric = MetricDefinition(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            unit="percentage",
            description="CPU usage"
        )
        collector.define_metric(metric)
        collector.record_metric("cpu_usage", 85.0)
        
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition="value > 80",
            severity=AlertSeverity.CRITICAL,
            duration_seconds=300,
            description="High CPU usage"
        )
        alerting.add_rule(rule)
        
        alerts = alerting.evaluate_rules()
        assert len(alerts) > 0
        assert alerts[0][0] == "high_cpu"


class TestDeploymentOrchestrator:
    """Tests for deployment orchestrator."""
    
    def test_plan_deployment_blue_green(self):
        """Test planning blue-green deployment."""
        orchestrator = DeploymentOrchestrator()
        config = DeploymentConfig(
            deployment_type=DeploymentType.BLUE_GREEN,
            replicas=3
        )
        valid, plan = orchestrator.plan_deployment(DeploymentType.BLUE_GREEN, config)
        assert valid
        assert plan.deployment_type == DeploymentType.BLUE_GREEN
        assert len(plan.stages) > 0
        assert "green" in plan.stages[0].lower()
    
    def test_plan_deployment_canary(self):
        """Test planning canary deployment."""
        orchestrator = DeploymentOrchestrator()
        config = DeploymentConfig(
            deployment_type=DeploymentType.CANARY,
            replicas=3,
            canary_percentage=10
        )
        valid, plan = orchestrator.plan_deployment(DeploymentType.CANARY, config)
        assert valid
        assert plan.deployment_type == DeploymentType.CANARY
        assert "canary" in plan.stages[0].lower()
    
    def test_plan_deployment_rolling(self):
        """Test planning rolling deployment."""
        orchestrator = DeploymentOrchestrator()
        config = DeploymentConfig(
            deployment_type=DeploymentType.ROLLING,
            replicas=3
        )
        valid, plan = orchestrator.plan_deployment(DeploymentType.ROLLING, config)
        assert valid
        assert plan.deployment_type == DeploymentType.ROLLING
        assert "update" in plan.stages[0].lower() or "rolling" in " ".join(plan.stages).lower()
    
    def test_execute_deployment(self):
        """Test executing deployment."""
        orchestrator = DeploymentOrchestrator()
        config = DeploymentConfig(
            deployment_type=DeploymentType.BLUE_GREEN,
            replicas=3
        )
        valid, plan = orchestrator.plan_deployment(DeploymentType.BLUE_GREEN, config)
        
        valid, metrics = orchestrator.execute_deployment(plan.deployment_id)
        assert valid
        assert metrics.deployment_id == plan.deployment_id
        assert metrics.successful_replicas > 0
    
    def test_get_deployment_status(self):
        """Test getting deployment status."""
        orchestrator = DeploymentOrchestrator()
        config = DeploymentConfig(
            deployment_type=DeploymentType.BLUE_GREEN,
            replicas=3
        )
        valid, plan = orchestrator.plan_deployment(DeploymentType.BLUE_GREEN, config)
        orchestrator.execute_deployment(plan.deployment_id)
        
        status = orchestrator.get_deployment_status(plan.deployment_id)
        assert status is not None
        assert status["deployment_id"] == plan.deployment_id
        assert "success_rate" in status
    
    def test_get_system_health(self):
        """Test getting system health."""
        orchestrator = DeploymentOrchestrator()
        health = orchestrator.get_system_health()
        assert health is not None
        assert "overall_healthy" in health
        assert "components" in health
    
    def test_deployment_not_found(self):
        """Test deployment not found."""
        orchestrator = DeploymentOrchestrator()
        valid, metrics = orchestrator.execute_deployment("nonexistent")
        assert not valid
    
    def test_deployment_plan_validation(self):
        """Test deployment plan validation."""
        orchestrator = DeploymentOrchestrator()
        config = DeploymentConfig(
            deployment_type=DeploymentType.ROLLING,
            replicas=0  # Invalid
        )
        valid, plan = orchestrator.plan_deployment(DeploymentType.ROLLING, config)
        assert not valid


class TestDeploymentMetrics:
    """Tests for deployment metrics."""
    
    def test_metrics_creation(self):
        """Test creating deployment metrics."""
        from cortex.orchestrators.pr_review.deployment_orchestrator import DeploymentMetrics
        metrics = DeploymentMetrics(
            deployment_id="deploy-001",
            start_time=datetime.now()
        )
        assert metrics.deployment_id == "deploy-001"
        assert metrics.success_rate == 0.0
    
    def test_metrics_success_rate(self):
        """Test calculating success rate."""
        from cortex.orchestrators.pr_review.deployment_orchestrator import DeploymentMetrics
        now = datetime.now()
        metrics = DeploymentMetrics(
            deployment_id="deploy-001",
            start_time=now,
            successful_replicas=3,
            failed_replicas=1
        )
        assert metrics.success_rate == 75.0
    
    def test_metrics_duration(self):
        """Test calculating duration."""
        from cortex.orchestrators.pr_review.deployment_orchestrator import DeploymentMetrics
        now = datetime.now()
        metrics = DeploymentMetrics(
            deployment_id="deploy-001",
            start_time=now,
            end_time=now + timedelta(seconds=120)
        )
        assert metrics.duration_seconds == 120


class TestDeploymentPlan:
    """Tests for deployment plan."""
    
    def test_plan_to_dict(self):
        """Test converting plan to dictionary."""
        from cortex.orchestrators.pr_review.deployment_orchestrator import DeploymentPlan
        plan = DeploymentPlan(
            deployment_id="deploy-001",
            deployment_type=DeploymentType.BLUE_GREEN,
            stages=["Provision", "Deploy", "Test"],
            estimated_duration_minutes=15,
            rollback_strategy="automatic",
            validation_steps=["Health check", "Verify"]
        )
        data = plan.to_dict()
        assert data["deployment_id"] == "deploy-001"
        assert data["type"] == "blue_green"
        assert len(data["stages"]) == 3


class TestHealthStatus:
    """Tests for health status."""
    
    def test_health_status_to_dict(self):
        """Test converting health status to dict."""
        from cortex.orchestrators.pr_review.deployment_orchestrator import HealthStatus
        now = datetime.now()
        status = HealthStatus(
            timestamp=now,
            overall_healthy=True,
            component_statuses={"api": True, "db": True},
            metrics={"uptime": 99.9},
            last_check_time=now
        )
        data = status.to_dict()
        assert data["overall_healthy"] is True
        assert data["components"]["api"] is True
        assert len(data["metrics"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
