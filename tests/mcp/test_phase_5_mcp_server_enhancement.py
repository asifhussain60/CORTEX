"""
Phase 5: MCP Server Enhancement Tests.

Tests for health endpoints, metrics, and server features.

CORE-008: Tests written first (TDD approach).
CORE-011: All functions have type hints.
CORE-012: Google-style docstrings.
"""

import pytest
import time
from typing import Dict, Any
from cortex.mcp.health_checker import HealthChecker, get_health_checker
from cortex.mcp.metrics_collector import MetricsCollector, get_metrics_collector
from cortex.mcp.startup_banner import get_banner, get_banner_dict, print_banner
from cortex.mcp.wiring_watcher import WiringFileWatcher, get_wiring_watcher


class TestHealthChecker:
    """Test health checking functionality."""
    
    def test_health_checker_initialization(self) -> None:
        """Test HealthChecker initialization."""
        checker = HealthChecker()
        assert checker.start_time > 0
        assert checker.request_count == 0
        assert checker.error_count == 0
    
    def test_get_uptime_seconds(self) -> None:
        """Test uptime calculation."""
        checker = HealthChecker()
        time.sleep(0.1)
        uptime = checker.get_uptime_seconds()
        assert uptime >= 0.1
    
    def test_increment_requests(self) -> None:
        """Test request counter."""
        checker = HealthChecker()
        checker.increment_requests()
        checker.increment_requests()
        assert checker.request_count == 2
    
    def test_increment_errors(self) -> None:
        """Test error counter."""
        checker = HealthChecker()
        checker.increment_errors()
        checker.increment_errors()
        assert checker.error_count == 2
    
    def test_basic_health_check(self) -> None:
        """Test basic health check endpoint."""
        checker = HealthChecker()
        checker.increment_requests()
        
        health = checker.check_basic_health()
        
        assert health.status in ["healthy", "degraded", "unhealthy"]
        assert health.uptime_seconds >= 0
        assert "service" in health.checks
        assert health.checks["requests_total"] == 1
    
    def test_wiring_health_check(self) -> None:
        """Test wiring system health check."""
        checker = HealthChecker()
        
        health = checker.check_wiring_health()
        
        assert health.status == "healthy"
        assert "wiring_file" in health.checks
        assert health.checks["orchestrators_wired"] == 23
    
    def test_orchestrator_health_check(self) -> None:
        """Test orchestrator availability check."""
        checker = HealthChecker()
        
        health = checker.check_orchestrator_health()
        
        assert health.status == "healthy"
        assert health.checks["core_orchestrators"] == 6
        assert health.checks["domain_orchestrators"] == 6
        assert health.checks["support_orchestrators"] == 11
        assert health.checks["total_orchestrators"] == 23
    
    def test_health_status_timestamp(self) -> None:
        """Test health status includes timestamp."""
        checker = HealthChecker()
        health = checker.check_basic_health()
        
        # Should be ISO format with T separator
        assert "T" in health.timestamp
        assert health.timestamp  # Non-empty string


class TestMetricsCollector:
    """Test metrics collection functionality."""
    
    def test_metrics_collector_initialization(self) -> None:
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        assert collector.requests_total == 0
        assert collector.errors_total == 0
    
    def test_record_request(self) -> None:
        """Test recording requests."""
        collector = MetricsCollector()
        collector.record_request("tools/call", 0.1, True)
        
        assert collector.requests_total == 1
        assert collector.errors_total == 0
    
    def test_record_request_with_error(self) -> None:
        """Test recording failed requests."""
        collector = MetricsCollector()
        collector.record_request("tools/call", 0.1, False)
        
        assert collector.requests_total == 1
        assert collector.errors_total == 1
    
    def test_record_orchestrator_invocation(self) -> None:
        """Test recording orchestrator invocations."""
        collector = MetricsCollector()
        collector.record_orchestrator_invocation("MasterOrchestrator")
        collector.record_orchestrator_invocation("TDDOrchestrator")
        collector.record_orchestrator_invocation("MasterOrchestrator")
        
        assert collector.orchestrator_invocations["MasterOrchestrator"] == 2
        assert collector.orchestrator_invocations["TDDOrchestrator"] == 1
    
    def test_get_prometheus_metrics(self) -> None:
        """Test Prometheus format metrics output."""
        collector = MetricsCollector()
        collector.record_request("tools/call", 0.05, True)
        collector.record_orchestrator_invocation("MasterOrchestrator")
        
        metrics = collector.get_prometheus_metrics()
        
        assert "cortex_requests_total" in metrics
        assert "cortex_errors_total" in metrics
        assert "cortex_orchestrator_invocations" in metrics
        assert "cortex_wiring_health" in metrics
        assert "1" in metrics  # At least one metric has value
    
    def test_prometheus_format_validity(self) -> None:
        """Test Prometheus output format is valid."""
        collector = MetricsCollector()
        collector.record_request("tools/call", 0.1, True)
        
        metrics = collector.get_prometheus_metrics()
        lines = metrics.strip().split("\n")
        
        # Should have help, type, and value lines
        assert len(lines) > 0
        
        # Check for standard Prometheus format
        has_help = any("# HELP" in line for line in lines)
        has_type = any("# TYPE" in line for line in lines)
        has_value = any(line and not line.startswith("#") for line in lines)
        
        assert has_help
        assert has_type
        assert has_value


class TestStartupBanner:
    """Test startup banner functionality."""
    
    def test_get_banner_default(self) -> None:
        """Test banner generation with defaults."""
        banner = get_banner()
        
        assert "CORTEX MCP Server" in banner
        assert "Version:" in banner
        assert "Wiring Hash:" in banner
        assert "Orchestrators:" in banner
        assert "Port:" in banner
        assert "Environment:" in banner
    
    def test_get_banner_custom_values(self) -> None:
        """Test banner with custom values."""
        banner = get_banner(
            version="2.2",
            wiring_hash="abcd1234",
            orchestrator_count=23,
            port=9000,
            environment="production"
        )
        
        assert "2.2" in banner
        assert "abcd1234" in banner
        assert "23/23" in banner
        assert "9000" in banner
        assert "production" in banner
    
    def test_get_banner_dict(self) -> None:
        """Test banner as dictionary."""
        banner_dict = get_banner_dict(
            version="2.1",
            wiring_hash="test1234",
            orchestrator_count=23,
            port=8443,
            environment="development"
        )
        
        assert banner_dict["version"] == "2.1"
        assert banner_dict["wiring_hash"] == "test1234"
        assert banner_dict["orchestrator_count"] == 23
        assert banner_dict["port"] == 8443
        assert banner_dict["environment"] == "development"
        assert banner_dict["orchestrators_total"] == 23
        assert banner_dict["protocol"] == "MCP"
        assert banner_dict["json_rpc_version"] == "2.0"
    
    def test_print_banner_no_error(self) -> None:
        """Test banner printing doesn't error."""
        try:
            print_banner()
            assert True
        except Exception as e:
            pytest.fail(f"print_banner raised {e}")


class TestWiringFileWatcher:
    """Test wiring file watcher functionality."""
    
    def test_wiring_watcher_initialization(self) -> None:
        """Test WiringFileWatcher initialization."""
        watcher = WiringFileWatcher()
        
        assert watcher.wiring_path.name == "wiring.yaml"
        assert watcher.check_interval == 1.0
        assert not watcher.is_watching()
    
    def test_wiring_watcher_start_stop(self) -> None:
        """Test starting and stopping watcher."""
        watcher = WiringFileWatcher()
        
        watcher.start()
        assert watcher.is_watching()
        
        watcher.stop()
        assert not watcher.is_watching()
    
    def test_wiring_watcher_custom_interval(self) -> None:
        """Test watcher with custom check interval."""
        watcher = WiringFileWatcher(check_interval=0.5)
        
        assert watcher.check_interval == 0.5
    
    def test_wiring_watcher_callback_optional(self) -> None:
        """Test watcher works without callback."""
        watcher = WiringFileWatcher()
        
        watcher.start()
        time.sleep(0.1)
        watcher.stop()
        
        # Should not error even without callback
        assert True
    
    def test_global_wiring_watcher(self) -> None:
        """Test global wiring watcher singleton."""
        watcher1 = get_wiring_watcher()
        watcher2 = get_wiring_watcher()
        
        assert watcher1 is watcher2


class TestGlobalInstances:
    """Test global singleton instances."""
    
    def test_get_health_checker(self) -> None:
        """Test health checker singleton."""
        checker1 = get_health_checker()
        checker2 = get_health_checker()
        
        assert checker1 is checker2
    
    def test_get_metrics_collector(self) -> None:
        """Test metrics collector singleton."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        
        assert collector1 is collector2
    
    def test_singleton_state_persistence(self) -> None:
        """Test that singletons maintain state."""
        checker = get_health_checker()
        checker.increment_requests()
        
        # Get same instance again
        checker2 = get_health_checker()
        assert checker2.request_count == 1


class TestPhase5Integration:
    """Integration tests for Phase 5 components."""
    
    def test_health_and_metrics_together(self) -> None:
        """Test health and metrics work together."""
        checker = HealthChecker()  # Create fresh instance for this test
        collector = get_metrics_collector()
        
        checker.increment_requests()
        collector.record_request("tools/call", 0.1, True)
        
        health = checker.check_basic_health()
        metrics = collector.get_prometheus_metrics()
        
        assert health.checks["requests_total"] == 1
        assert "cortex_requests_total" in metrics
    
    def test_banner_with_watcher_callback(self) -> None:
        """Test banner generation can be used with watcher."""
        banner_dict = get_banner_dict()
        watcher = WiringFileWatcher()
        
        # Should not error
        assert banner_dict["version"]
        assert not watcher.is_watching()
    
    def test_concurrent_health_checks(self) -> None:
        """Test concurrent health checks don't error."""
        import threading
        
        checker = get_health_checker()
        results = []
        
        def check_health() -> None:
            health = checker.check_basic_health()
            results.append(health)
        
        threads = [threading.Thread(target=check_health) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert len(results) == 5
        for health in results:
            assert health.status in ["healthy", "degraded", "unhealthy"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
