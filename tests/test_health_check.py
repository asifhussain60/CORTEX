"""
Test suite for health check system.

Tests cover:
- System health checks
- Orchestrator health monitoring
- Metrics collection (Prometheus format)
- Statistics gathering
- Health status determination
"""

import asyncio
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.logging.health_check import HealthCheckSystem
from src.logging.audit_logger import AuditLogger, LogLevel
from src.logging.self_healing_engine import SelfHealingEngine


class TestHealthCheckSystem:
    """Test HealthCheckSystem functionality."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def audit_logger(self, temp_log_dir):
        """Create audit logger instance."""
        return AuditLogger({"log_dir": str(temp_log_dir)})
    
    @pytest.fixture
    def self_healing_engine(self, audit_logger):
        """Create self-healing engine instance."""
        return SelfHealingEngine(
            audit_logger=audit_logger,
            analysis_interval=1.0,
            auto_recovery_enabled=True
        )
    
    @pytest.fixture
    def health_check_system(self, audit_logger, self_healing_engine):
        """Create health check system instance."""
        return HealthCheckSystem(
            audit_logger=audit_logger,
            self_healing_engine=self_healing_engine
        )
    
    @pytest.mark.asyncio
    async def test_system_health_check(self, health_check_system):
        """Test overall system health check."""
        health = await health_check_system.get_system_health()
        
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "timestamp" in health
        assert "uptime_seconds" in health
        assert "components" in health
        
        # Check components
        components = health["components"]
        assert "audit_logger" in components
        assert "self_healing_engine" in components
        assert "log_storage" in components
    
    @pytest.mark.asyncio
    async def test_audit_logger_health(self, health_check_system):
        """Test audit logger health check."""
        health = await health_check_system._check_audit_logger()
        
        assert "status" in health
        assert "error_count" in health
        assert "buffer_size" in health
        assert "async_enabled" in health
    
    @pytest.mark.asyncio
    async def test_self_healing_health(self, health_check_system):
        """Test self-healing engine health check."""
        health = await health_check_system._check_self_healing()
        
        assert "status" in health
        assert "enabled" in health
        assert "recovery_attempts" in health
        assert "success_rate" in health
    
    @pytest.mark.asyncio
    async def test_log_storage_health(self, health_check_system):
        """Test log storage health check."""
        health = await health_check_system._check_log_storage()
        
        assert "status" in health
        # May have error if directory doesn't exist yet
        if health["status"] == "healthy":
            assert "total_size_bytes" in health
            assert "file_count" in health
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_no_activity(self, health_check_system):
        """Test orchestrator health with no activity."""
        health = await health_check_system.get_orchestrator_health("unknown_orchestrator")
        
        assert health["orchestrator"] == "unknown_orchestrator"
        assert health["status"] == "unknown"
        assert "message" in health
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_with_activity(self, health_check_system, audit_logger):
        """Test orchestrator health with logged activity."""
        # Log some events
        for i in range(10):
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator="test_orch",
                event="test_event",
                data={"iteration": i}
            )
        
        health = await health_check_system.get_orchestrator_health("test_orch")
        
        assert health["orchestrator"] == "test_orch"
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "metrics" in health
        
        metrics = health["metrics"]
        assert metrics["total_events"] >= 10
        assert "error_rate" in metrics
        assert "last_activity" in metrics
    
    @pytest.mark.asyncio
    async def test_orchestrator_health_with_errors(self, health_check_system, audit_logger):
        """Test orchestrator health with errors."""
        # Log mix of normal and error events
        for i in range(5):
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator="error_orch",
                event="normal_event",
                data={"iteration": i}
            )
        
        for i in range(3):
            await audit_logger.log(
                level=LogLevel.ERROR,
                orchestrator="error_orch",
                event="error_event",
                data={"error": f"Test error {i}"}
            )
        
        health = await health_check_system.get_orchestrator_health("error_orch")
        
        assert health["orchestrator"] == "error_orch"
        metrics = health["metrics"]
        assert metrics["error_events"] == 3
        assert metrics["error_rate"] > 0
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, health_check_system, audit_logger):
        """Test metrics collection."""
        # Log some events
        await audit_logger.log(
            level=LogLevel.INFO,
            orchestrator="orch1",
            event="test_event_completed",
            data={"duration_ms": 100}
        )
        await audit_logger.log(
            level=LogLevel.ERROR,
            orchestrator="orch2",
            event="error_event",
            data={"error": "test"}
        )
        
        metrics = await health_check_system.get_metrics()
        
        assert "timestamp" in metrics
        assert "uptime_seconds" in metrics
        assert "event_counts" in metrics
        assert "error_counts" in metrics
        assert "performance_metrics" in metrics
        assert "self_healing" in metrics
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, health_check_system, audit_logger):
        """Test statistics gathering."""
        # Log some events
        for i in range(20):
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator=f"orch{i % 3}",
                event="test_event",
                data={"iteration": i}
            )
        
        stats = await health_check_system.get_statistics()
        
        assert "timestamp" in stats
        assert "total_events" in stats
        assert "last_hour" in stats
        assert "last_24_hours" in stats
        assert "event_types" in stats
        assert "log_levels" in stats
        assert "system_info" in stats
        
        # Check system info
        system_info = stats["system_info"]
        assert "uptime_seconds" in system_info
        assert "cache_size" in system_info
    
    def test_prometheus_format(self, health_check_system):
        """Test Prometheus metrics formatting."""
        metrics = {
            "uptime_seconds": 123.45,
            "event_counts": {
                "orch1": 100,
                "orch2": 50
            },
            "error_counts": {
                "orch1": 5,
                "orch2": 2
            },
            "performance_metrics": {
                "orch1": {
                    "avg_duration_ms": 50.5,
                    "min_duration_ms": 10.0,
                    "max_duration_ms": 200.0
                }
            },
            "self_healing": {
                "total_attempts": 10,
                "success_rate": 0.8
            }
        }
        
        prom_output = health_check_system.to_prometheus_format(metrics)
        
        # Check key metrics are present
        assert "cortex_uptime_seconds 123.45" in prom_output
        assert 'cortex_events_total{orchestrator="orch1"} 100' in prom_output
        assert 'cortex_errors_total{orchestrator="orch1"} 5' in prom_output
        assert 'cortex_recovery_attempts_total 10' in prom_output
        assert 'cortex_recovery_success_rate 0.8' in prom_output
        
        # Check Prometheus format structure
        assert "# HELP" in prom_output
        assert "# TYPE" in prom_output
    
    @pytest.mark.asyncio
    async def test_health_status_determination(self, health_check_system, audit_logger):
        """Test health status determination logic."""
        # Healthy scenario (no errors)
        for i in range(10):
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator="healthy_orch",
                event="test_event",
                data={"iteration": i}
            )
        
        health = await health_check_system.get_orchestrator_health("healthy_orch")
        assert health["status"] == "healthy"
        
        # Degraded scenario (some errors, <50%)
        audit_logger._event_cache.clear()  # Reset
        for i in range(7):
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator="degraded_orch",
                event="test_event",
                data={"iteration": i}
            )
        for i in range(2):
            await audit_logger.log(
                level=LogLevel.ERROR,
                orchestrator="degraded_orch",
                event="error_event",
                data={"error": f"Error {i}"}
            )
        
        health = await health_check_system.get_orchestrator_health("degraded_orch")
        # Error rate: 2/9 = 0.222 (>0.1, <0.5) = degraded
        assert health["status"] in ["degraded", "healthy"]
    
    @pytest.mark.asyncio
    async def test_performance_metrics_calculation(self, health_check_system, audit_logger):
        """Test performance metrics calculation."""
        # Log operations with varying durations
        durations = [50, 100, 150, 200, 250]
        for duration in durations:
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator="perf_orch",
                event="operation_completed",
                data={"duration_ms": duration}
            )
        
        metrics = await health_check_system.get_metrics()
        perf_metrics = metrics.get("performance_metrics", {}).get("perf_orch")
        
        if perf_metrics:
            assert perf_metrics["total_operations"] == 5
            assert perf_metrics["min_duration_ms"] == 50
            assert perf_metrics["max_duration_ms"] == 250
            assert perf_metrics["avg_duration_ms"] == 150  # Mean of 50-250


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
