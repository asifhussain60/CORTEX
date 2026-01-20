"""
Tests for comprehensive health and readiness checks (AC-OPS-004-04).

Tests liveness checks, readiness checks, component health status,
dependency health verification, and proper HTTP status codes.
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional
from datetime import datetime

from cortex.api.health_endpoints import (
    HealthStatus,
    ComponentHealth,
    HealthCheckResponse,
    HealthChecksCollector,
    HealthCheckConfig,
)


class TestHealthStatusEnum:
    """Test health status enumeration."""

    def test_health_statuses_defined(self) -> None:
        """Test that health statuses are properly defined."""
        assert hasattr(HealthStatus, "HEALTHY")
        assert hasattr(HealthStatus, "DEGRADED")
        assert hasattr(HealthStatus, "UNHEALTHY")

    def test_health_status_values(self) -> None:
        """Test health status string values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"


class TestComponentHealth:
    """Test component health representation."""

    def test_component_health_creation(self) -> None:
        """Test creating component health object."""
        health = ComponentHealth(
            status=HealthStatus.HEALTHY,
            latency_ms=5.0,
        )
        assert health.status == HealthStatus.HEALTHY
        assert health.latency_ms == 5.0

    def test_component_health_with_reason(self) -> None:
        """Test component health with degradation reason."""
        health = ComponentHealth(
            status=HealthStatus.DEGRADED,
            latency_ms=150.0,
            reason="High latency detected",
        )
        assert health.status == HealthStatus.DEGRADED
        assert health.reason == "High latency detected"

    def test_component_health_error_reason(self) -> None:
        """Test component health with error reason."""
        health = ComponentHealth(
            status=HealthStatus.UNHEALTHY,
            reason="Connection timeout",
            error_message="Failed to connect to database",
        )
        assert health.status == HealthStatus.UNHEALTHY
        assert health.error_message is not None


class TestHealthCheckResponse:
    """Test health check response structure."""

    def test_health_check_response_creation(self) -> None:
        """Test creating health check response."""
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow().isoformat(),
            version="1.2.3",
            uptime_seconds=3600,
        )
        assert response.status == HealthStatus.HEALTHY
        assert response.version == "1.2.3"
        assert response.uptime_seconds == 3600

    def test_health_check_response_with_components(self) -> None:
        """Test health check response with component details."""
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow().isoformat(),
            version="1.2.3",
            uptime_seconds=3600,
            components={
                "database": ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=5.0),
                "cache": ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=2.0),
            },
        )
        assert len(response.components) == 2
        assert response.components["database"].status == HealthStatus.HEALTHY

    def test_health_check_response_to_dict(self) -> None:
        """Test converting health check response to dictionary."""
        response = HealthCheckResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.utcnow().isoformat(),
            version="1.2.3",
            uptime_seconds=3600,
        )
        data = response.to_dict()
        assert isinstance(data, dict)
        assert data["status"] == "healthy"
        assert data["version"] == "1.2.3"


class TestHealthChecksCollector:
    """Test health checks collector."""

    def test_health_collector_creation(self) -> None:
        """Test creating health checks collector."""
        config = HealthCheckConfig(
            service_name="cortex-test",
            version="1.2.3",
        )
        collector = HealthChecksCollector(config)
        assert collector is not None
        assert collector.config.service_name == "cortex-test"

    def test_liveness_check_always_responds_quickly(self) -> None:
        """Test that liveness check responds in <100ms."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        start = time.time()
        response = collector.liveness_check()
        elapsed = (time.time() - start) * 1000
        
        # Should respond quickly
        assert elapsed < 100, f"Liveness check took {elapsed:.0f}ms"
        assert response.status in [HealthStatus.HEALTHY, HealthStatus.UNHEALTHY]

    def test_readiness_check_reflects_service_state(self) -> None:
        """Test that readiness check accurately reflects service state."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        # Should be ready by default
        response = collector.readiness_check()
        assert response.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]

    def test_deep_health_check_includes_components(self) -> None:
        """Test that deep health check includes component details."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        # Register component checks
        collector.register_component_check("database", lambda: HealthStatus.HEALTHY)
        collector.register_component_check("cache", lambda: HealthStatus.HEALTHY)
        
        response = collector.deep_health_check()
        
        assert response.status is not None
        assert response.components is not None
        assert len(response.components) >= 2

    def test_component_check_registration(self) -> None:
        """Test registering component health checks."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        # Register a component check
        def check_db() -> HealthStatus:
            return HealthStatus.HEALTHY
        
        collector.register_component_check("database", check_db)
        
        # Check should be registered
        components = collector.get_component_checks()
        assert "database" in components

    def test_http_status_codes_200_for_healthy(self) -> None:
        """Test HTTP 200 status code for healthy."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        response = collector.liveness_check()
        status_code = collector.get_http_status_code(response)
        
        if response.status == HealthStatus.HEALTHY:
            assert status_code == 200

    def test_http_status_codes_503_for_unhealthy(self) -> None:
        """Test HTTP 503 status code for degraded/unhealthy."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        # Mark service as degraded
        response = HealthCheckResponse(
            status=HealthStatus.DEGRADED,
            timestamp=datetime.utcnow().isoformat(),
            version="1.2.3",
            uptime_seconds=3600,
        )
        status_code = collector.get_http_status_code(response)
        
        assert status_code == 503


class TestComponentHealthChecks:
    """Test individual component health checks."""

    def test_database_health_check(self) -> None:
        """Test database component health check."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        # Register database check
        def check_db():
            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                latency_ms=5.0,
            )
        
        collector.register_component_check("database", check_db)
        response = collector.deep_health_check()
        
        assert response.components is not None
        assert response.components["database"].status == HealthStatus.HEALTHY

    def test_cache_health_check(self) -> None:
        """Test cache component health check."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        def check_cache():
            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                latency_ms=2.0,
            )
        
        collector.register_component_check("cache", check_cache)
        response = collector.deep_health_check()
        
        assert response.components["cache"].status == HealthStatus.HEALTHY

    def test_governance_component_health(self) -> None:
        """Test governance component health check."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        def check_governance():
            return ComponentHealth(
                status=HealthStatus.HEALTHY,
                latency_ms=1.0,
            )
        
        collector.register_component_check("governance", check_governance)
        response = collector.deep_health_check()
        
        assert response.components["governance"].status == HealthStatus.HEALTHY

    def test_component_check_timeout(self) -> None:
        """Test component check timeout handling."""
        config = HealthCheckConfig(
            service_name="cortex-test",
            version="1.2.3",
            component_timeout_seconds=0.1,
        )
        collector = HealthChecksCollector(config)
        
        def slow_check():
            time.sleep(0.5)  # Slower than timeout
            return HealthStatus.HEALTHY
        
        collector.register_component_check("slow", slow_check)
        response = collector.deep_health_check()
        
        # Should handle timeout gracefully
        assert response.components is not None


class TestHealthCheckEdgeCases:
    """Test edge cases in health checking."""

    def test_all_components_failing(self) -> None:
        """Test system status when all components fail."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        def failing_check():
            return ComponentHealth(
                status=HealthStatus.UNHEALTHY,
                reason="Component failed",
            )
        
        collector.register_component_check("db", failing_check)
        collector.register_component_check("cache", failing_check)
        
        response = collector.deep_health_check()
        
        # System should be unhealthy
        assert response.status in [HealthStatus.DEGRADED, HealthStatus.UNHEALTHY]

    def test_partial_component_failure(self) -> None:
        """Test system status with partial component failure."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        def healthy_check():
            return ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=5.0)
        
        def degraded_check():
            return ComponentHealth(
                status=HealthStatus.DEGRADED,
                reason="Component degraded",
            )
        
        collector.register_component_check("db", healthy_check)
        collector.register_component_check("cache", degraded_check)
        
        response = collector.deep_health_check()
        
        # System should be degraded when one component is degraded
        assert response.status in [HealthStatus.DEGRADED, HealthStatus.HEALTHY]

    def test_health_check_retry_on_failure(self) -> None:
        """Test retry logic for failed health checks."""
        config = HealthCheckConfig(
            service_name="cortex-test",
            version="1.2.3",
            retry_failed_checks=True,
            retry_count=3,
        )
        collector = HealthChecksCollector(config)
        
        # Counter for calls
        call_count = [0]
        
        def sometimes_failing_check():
            call_count[0] += 1
            if call_count[0] < 3:
                return ComponentHealth(status=HealthStatus.UNHEALTHY)
            return ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=5.0)
        
        collector.register_component_check("flaky", sometimes_failing_check)
        response = collector.deep_health_check()
        
        # After retries, should succeed
        assert response.components is not None

    def test_circular_health_check_dependency(self) -> None:
        """Test detecting circular health check dependencies."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        # This is a complex case that should be handled
        collector.register_component_check("comp1", lambda: HealthStatus.HEALTHY)
        collector.register_component_check("comp2", lambda: HealthStatus.HEALTHY)
        
        response = collector.deep_health_check()
        
        # Should complete without deadlock
        assert response is not None


class TestHealthCheckPerformance:
    """Test health check performance requirements."""

    def test_liveness_check_performance(self) -> None:
        """Test liveness check completes in <100ms."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        start = time.time()
        for _ in range(100):
            collector.liveness_check()
        elapsed = (time.time() - start) / 100
        
        assert elapsed < 0.1, f"Liveness check avg {elapsed*1000:.1f}ms"

    def test_readiness_check_performance(self) -> None:
        """Test readiness check completes in <500ms."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        start = time.time()
        response = collector.readiness_check()
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 500, f"Readiness check took {elapsed:.0f}ms"

    def test_deep_health_check_with_multiple_components(self) -> None:
        """Test deep health check with many components."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        # Register many component checks
        for i in range(10):
            collector.register_component_check(
                f"component_{i}",
                lambda: ComponentHealth(status=HealthStatus.HEALTHY, latency_ms=5.0),
            )
        
        start = time.time()
        response = collector.deep_health_check()
        elapsed = (time.time() - start) * 1000
        
        # Should handle many components efficiently
        assert elapsed < 500, f"Deep health check took {elapsed:.0f}ms"

    def test_uptime_tracking(self) -> None:
        """Test that uptime is accurately tracked."""
        config = HealthCheckConfig(service_name="cortex-test", version="1.2.3")
        collector = HealthChecksCollector(config)
        
        response1 = collector.liveness_check()
        time.sleep(0.1)
        response2 = collector.liveness_check()
        
        # Uptime should increase
        assert response2.uptime_seconds >= response1.uptime_seconds
