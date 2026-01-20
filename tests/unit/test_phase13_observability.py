"""
Comprehensive Test Suite for Phase 13 - Observability & Telemetry Maturity

Tests for the remaining 3 acceptance criteria:
- OB-002-01: Alerting & Health Monitoring
- OB-002-02: Performance Profiling & Optimization
- OB-003-01: Audit Trail Enhancement
"""

import pytest
import time
import json
import csv
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from cortex.observability.health_monitor import (
    HealthMonitor,
    HealthCheck,
    HealthCheckResult,
    HealthStatus,
    DatabaseHealthCheck,
    MemoryHealthCheck,
)

from cortex.observability.performance_profiler import (
    PerformanceProfiler,
    PerformanceMetric,
    PerformanceLevel,
    Bottleneck,
)

from cortex.observability.audit_trail import (
    AuditTrail,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    RetentionPolicy,
)


# ============================================================================
# OB-002-01: Alerting & Health Monitoring Tests
# ============================================================================

class TestHealthMonitorBasics:
    """Test basic health monitoring functionality."""
    
    def test_health_check_creation(self):
        """Test creating a health check."""
        check = HealthCheck(
            name="test_check",
            component="test_component",
            timeout_seconds=5.0
        )
        
        assert check.name == "test_check"
        assert check.component == "test_component"
        assert check.timeout_seconds == 5.0
    
    def test_health_check_result(self):
        """Test health check result."""
        result = HealthCheckResult(
            component="test",
            status=HealthStatus.HEALTHY,
            message="All good"
        )
        
        assert result.component == "test"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "All good"
        
        result_dict = result.to_dict()
        assert result_dict["status"] == "healthy"
        assert result_dict["component"] == "test"


class TestHealthMonitor:
    """Test HealthMonitor service."""
    
    def test_health_monitor_creation(self):
        """Test creating health monitor."""
        monitor = HealthMonitor(check_interval_seconds=10.0)
        
        assert monitor.check_interval_seconds == 10.0
        assert monitor.running is False
        assert len(monitor.checks) == 0
    
    def test_register_health_check(self):
        """Test registering health checks."""
        monitor = HealthMonitor()
        check = HealthCheck("test", "component")
        
        monitor.register_check(check)
        
        assert "test" in monitor.checks
        assert monitor.checks["test"] == check
    
    def test_health_monitor_overall_health(self):
        """Test checking overall system health."""
        monitor = HealthMonitor()
        
        # Create mock checks
        class MockHealthyCheck(HealthCheck):
            def check(self):
                return HealthCheckResult(
                    component=self.component,
                    status=HealthStatus.HEALTHY,
                    message="OK"
                )
        
        class MockUnhealthyCheck(HealthCheck):
            def check(self):
                return HealthCheckResult(
                    component=self.component,
                    status=HealthStatus.UNHEALTHY,
                    message="Not OK"
                )
        
        # Test all healthy
        monitor.register_check(MockHealthyCheck("check1", "comp1"))
        results = monitor.run_checks()
        
        assert monitor.is_healthy() is True
        assert results["check1"].status == HealthStatus.HEALTHY
        
        # Add unhealthy check
        monitor.register_check(MockUnhealthyCheck("check2", "comp2"))
        results = monitor.run_checks()
        
        assert monitor.is_healthy() is False
        assert results["check2"].status == HealthStatus.UNHEALTHY
    
    def test_health_monitor_handlers(self):
        """Test health monitor event handlers."""
        monitor = HealthMonitor()
        
        handler_calls = []
        
        def test_handler(result):
            handler_calls.append(result)
        
        monitor.register_handler(test_handler)
        
        class MockCheck(HealthCheck):
            def check(self):
                return HealthCheckResult(
                    component=self.component,
                    status=HealthStatus.HEALTHY,
                    message="OK"
                )
        
        monitor.register_check(MockCheck("test", "component"))
        monitor.run_checks()
        
        assert len(handler_calls) == 1
        assert handler_calls[0].status == HealthStatus.HEALTHY
    
    def test_health_monitor_summary(self):
        """Test getting health monitor summary."""
        monitor = HealthMonitor()
        
        class MockCheck(HealthCheck):
            def check(self):
                status = HealthStatus.HEALTHY if self.name == "check1" else HealthStatus.DEGRADED
                return HealthCheckResult(
                    component=self.component,
                    status=status,
                    message="Test"
                )
        
        monitor.register_check(MockCheck("check1", "comp1"))
        monitor.register_check(MockCheck("check2", "comp2"))
        
        monitor.run_checks()
        summary = monitor.get_summary()
        
        assert summary["healthy"] == 1
        assert summary["degraded"] == 1
        assert summary["status"] in ["healthy", "degraded"]


class TestDatabaseHealthCheck:
    """Test database health checks."""
    
    def test_database_health_check_no_connection(self):
        """Test database health check with no connection."""
        check = DatabaseHealthCheck(db_connection=None)
        result = check.check()
        
        assert result.status == HealthStatus.UNHEALTHY
        assert "No database connection" in result.message
    
    def test_database_health_check_success(self):
        """Test successful database health check."""
        # Create in-memory database
        conn = sqlite3.connect(":memory:")
        check = DatabaseHealthCheck(db_connection=conn)
        result = check.check()
        
        assert result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        assert "OK" in result.message
        assert result.check_duration_ms >= 0


class TestMemoryHealthCheck:
    """Test memory health checks."""
    
    def test_memory_health_check(self):
        """Test memory health check."""
        check = MemoryHealthCheck(threshold_percent=99.0)
        result = check.check()
        
        # Should be either healthy or degraded under normal conditions
        assert result.status in [
            HealthStatus.HEALTHY,
            HealthStatus.DEGRADED,
            HealthStatus.UNKNOWN
        ]
        assert "memory" in result.message.lower() or "not available" in result.message.lower()


# ============================================================================
# OB-002-02: Performance Profiling & Optimization Tests
# ============================================================================

class TestPerformanceMetric:
    """Test performance metric tracking."""
    
    def test_performance_metric_creation(self):
        """Test creating performance metric."""
        metric = PerformanceMetric(
            name="test_op",
            duration_ms=50.5
        )
        
        assert metric.name == "test_op"
        assert metric.duration_ms == 50.5
    
    def test_performance_level_classification(self):
        """Test performance level classification."""
        # Excellent
        metric = PerformanceMetric("op", 25.0)
        assert metric.get_level() == PerformanceLevel.EXCELLENT
        
        # Good
        metric = PerformanceMetric("op", 75.0)
        assert metric.get_level() == PerformanceLevel.GOOD
        
        # Fair
        metric = PerformanceMetric("op", 200.0)
        assert metric.get_level() == PerformanceLevel.FAIR
        
        # Poor
        metric = PerformanceMetric("op", 1000.0)
        assert metric.get_level() == PerformanceLevel.POOR
        
        # Critical
        metric = PerformanceMetric("op", 3000.0)
        assert metric.get_level() == PerformanceLevel.CRITICAL


class TestPerformanceProfiler:
    """Test performance profiling."""
    
    def test_profiler_creation(self):
        """Test creating profiler."""
        profiler = PerformanceProfiler(retention_hours=24.0)
        
        assert profiler.retention_hours == 24.0
        assert len(profiler.metrics) == 0
    
    def test_record_metric(self):
        """Test recording metrics."""
        profiler = PerformanceProfiler()
        
        profiler.record_metric("query_db", 45.5)
        profiler.record_metric("query_db", 52.3)
        
        assert "query_db" in profiler.metrics
        assert len(profiler.metrics["query_db"]) == 2
    
    def test_get_statistics(self):
        """Test getting performance statistics."""
        profiler = PerformanceProfiler()
        
        # Record multiple measurements
        measurements = [50.0, 60.0, 55.0, 65.0, 52.0]
        for m in measurements:
            profiler.record_metric("test_op", m)
        
        stats = profiler.get_stats("test_op")
        
        assert stats is not None
        assert stats.count == 5
        assert stats.min_ms == 50.0
        assert stats.max_ms == 65.0
        assert stats.mean_ms == pytest.approx(56.4, abs=0.1)
        assert stats.median_ms == 55.0
    
    def test_baseline_tracking(self):
        """Test baseline tracking."""
        profiler = PerformanceProfiler()
        
        profiler.set_baseline("operation", 100.0)
        baseline = profiler.get_baseline("operation")
        
        assert baseline == 100.0
    
    def test_bottleneck_identification(self):
        """Test identifying bottlenecks."""
        profiler = PerformanceProfiler()
        
        # Record slow operation (> 200ms threshold)
        for _ in range(5):
            profiler.record_metric("slow_query", 250.0)
        
        # Record fast operation
        for _ in range(5):
            profiler.record_metric("fast_op", 50.0)
        
        bottlenecks = profiler.identify_bottlenecks()
        
        assert len(bottlenecks) > 0
        assert any(b.operation == "slow_query" for b in bottlenecks)
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations."""
        profiler = PerformanceProfiler()
        
        # Record slow database queries
        for _ in range(10):
            profiler.record_metric("database_query", 300.0)
        
        recommendations = profiler.generate_recommendations()
        
        assert len(recommendations) > 0
        # Should have database-related recommendations
        assert any(
            "database" in r.recommendation.lower() or "index" in r.recommendation.lower()
            for r in recommendations
        )
    
    def test_performance_comparison(self):
        """Test performance comparison to baseline."""
        profiler = PerformanceProfiler()
        
        profiler.set_baseline("operation", 100.0)
        
        # Record improved performance
        for _ in range(5):
            profiler.record_metric("operation", 80.0)
        
        comparison = profiler.get_performance_comparison("operation")
        
        assert comparison is not None
        assert comparison["improvement_percent"] > 0
        assert comparison["status"] == "improved"
    
    def test_profiler_summary(self):
        """Test getting profiler summary."""
        profiler = PerformanceProfiler()
        
        profiler.record_metric("op1", 50.0)
        profiler.record_metric("op2", 300.0)
        
        summary = profiler.get_summary()
        
        assert summary["metrics_tracked"] > 0
        assert summary["total_measurements"] > 0
        assert "bottlenecks" in summary
        assert "recommendations" in summary


# ============================================================================
# OB-003-01: Audit Trail Enhancement Tests
# ============================================================================

class TestAuditEvent:
    """Test audit event creation."""
    
    def test_audit_event_creation(self):
        """Test creating audit event."""
        event = AuditEvent(
            event_id="evt-001",
            event_type=AuditEventType.CREATE,
            component="database",
            action="insert_record",
            user="admin"
        )
        
        assert event.event_id == "evt-001"
        assert event.event_type == AuditEventType.CREATE
        assert event.component == "database"
        assert event.action == "insert_record"
        assert event.user == "admin"
    
    def test_audit_event_to_dict(self):
        """Test converting audit event to dictionary."""
        event = AuditEvent(
            event_id="evt-001",
            event_type=AuditEventType.UPDATE,
            component="config",
            action="update_setting",
            user="admin",
            severity=AuditSeverity.HIGH,
            details={"key": "value"}
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_id"] == "evt-001"
        assert event_dict["event_type"] == "update"
        assert event_dict["severity"] == "high"
        assert event_dict["details"]["key"] == "value"


class TestRetentionPolicy:
    """Test retention policy."""
    
    def test_retention_policy_defaults(self):
        """Test retention policy defaults."""
        policy = RetentionPolicy()
        
        assert policy.retention_days == 90
        assert policy.archive_after_days == 30
        assert policy.compress_after_days == 60
    
    def test_retention_cutoff(self):
        """Test getting retention cutoff."""
        policy = RetentionPolicy(retention_days=30)
        cutoff = policy.get_retention_cutoff()
        
        # Should be approximately 30 days ago
        now = datetime.utcnow()
        delta = now - cutoff
        assert 29 < delta.days < 31
    
    def test_should_archive(self):
        """Test archival decision."""
        policy = RetentionPolicy(archive_after_days=7)
        
        # Recent date - should not archive
        recent = datetime.utcnow() - timedelta(days=3)
        assert policy.should_archive(recent) is False
        
        # Old date - should archive
        old = datetime.utcnow() - timedelta(days=10)
        assert policy.should_archive(old) is True


class TestAuditTrail:
    """Test audit trail functionality."""
    
    def test_audit_trail_creation(self):
        """Test creating audit trail."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            trail = AuditTrail(db_path=db_path)
            assert trail.db_path == db_path
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_record_event(self):
        """Test recording audit event."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            trail = AuditTrail(db_path=db_path)
            
            event = trail.record_event(
                event_type=AuditEventType.CREATE,
                component="test",
                action="create_resource",
                user="test_user",
                severity=AuditSeverity.MEDIUM
            )
            
            assert event is not None
            assert event.event_type == AuditEventType.CREATE
            assert event.user == "test_user"
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_search_audit_trail(self):
        """Test searching audit trail."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            trail = AuditTrail(db_path=db_path)
            
            # Record multiple events
            trail.record_event(
                AuditEventType.CREATE, "database", "insert", "user1"
            )
            trail.record_event(
                AuditEventType.UPDATE, "database", "update", "user2"
            )
            trail.record_event(
                AuditEventType.DELETE, "config", "delete", "user1"
            )
            
            # Search by component
            results = trail.search(component="database")
            assert len(results) == 2
            
            # Search by user
            results = trail.search(user="user1")
            assert len(results) == 2
            
            # Search by event type
            results = trail.search(event_type=AuditEventType.CREATE)
            assert len(results) == 1
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_audit_trail_export_json(self):
        """Test exporting audit trail to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            trail = AuditTrail(db_path=str(db_path))
            
            # Record events
            trail.record_event(
                AuditEventType.CREATE, "test", "action", "user"
            )
            trail.record_event(
                AuditEventType.UPDATE, "test", "action", "user"
            )
            
            # Export
            export_path = Path(tmpdir) / "export.json"
            trail.export_json(str(export_path))
            
            assert export_path.exists()
            
            # Verify content
            with open(export_path) as f:
                data = json.load(f)
            
            assert len(data) == 2
            assert data[0]["event_type"] in ["create", "update"]
    
    def test_audit_trail_export_csv(self):
        """Test exporting audit trail to CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            trail = AuditTrail(db_path=str(db_path))
            
            # Record events
            trail.record_event(
                AuditEventType.CREATE, "test", "action", "user",
                details={"key": "value"}
            )
            trail.record_event(
                AuditEventType.UPDATE, "test", "action", "user",
                details={"key": "new_value"}
            )
            
            # Export
            export_path = Path(tmpdir) / "export.csv"
            trail.export_csv(str(export_path))
            
            assert export_path.exists()
            
            # Verify content
            with open(export_path) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            assert len(rows) == 2
            assert "key" in rows[0]
    
    def test_audit_trail_cleanup(self):
        """Test cleanup of expired entries."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            # Create trail with 1-day retention
            policy = RetentionPolicy(retention_days=1)
            trail = AuditTrail(db_path=db_path, retention_policy=policy)
            
            # Record events
            trail.record_event(
                AuditEventType.CREATE, "test", "action", "user"
            )
            
            # Cleanup should not delete recent events
            deleted = trail.cleanup()
            assert deleted == 0
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_audit_trail_statistics(self):
        """Test audit trail statistics."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            trail = AuditTrail(db_path=db_path)
            
            # Record events with various attributes
            trail.record_event(
                AuditEventType.CREATE, "comp1", "action", "user1",
                severity=AuditSeverity.HIGH
            )
            trail.record_event(
                AuditEventType.UPDATE, "comp2", "action", "user2",
                severity=AuditSeverity.MEDIUM
            )
            trail.record_event(
                AuditEventType.DELETE, "comp1", "action", "user1",
                severity=AuditSeverity.LOW
            )
            
            stats = trail.get_statistics()
            
            assert stats["total_events"] == 3
            assert "high" in stats["severity_distribution"]
            assert "comp1" in stats["top_components"]
            assert "user1" in stats["top_users"]
        finally:
            Path(db_path).unlink(missing_ok=True)
    
    def test_audit_handler(self):
        """Test audit event handler."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            trail = AuditTrail(db_path=db_path)
            
            handler_calls = []
            
            def test_handler(event):
                handler_calls.append(event)
            
            trail.register_handler(test_handler)
            
            # Record event
            trail.record_event(
                AuditEventType.CREATE, "test", "action", "user"
            )
            
            # Handler should have been called
            assert len(handler_calls) == 1
            assert handler_calls[0].event_type == AuditEventType.CREATE
        finally:
            Path(db_path).unlink(missing_ok=True)


# ============================================================================
# Integration Tests
# ============================================================================

class TestPhase13Integration:
    """Integration tests for Phase 13 observability features."""
    
    @pytest.mark.ac("OB-002-01")
    def test_health_monitoring_integration(self):
        """Test health monitoring integration with alerts."""
        monitor = HealthMonitor(check_interval_seconds=1)
        
        alert_triggered = []
        
        def alert_handler(result):
            if result.status == HealthStatus.UNHEALTHY:
                alert_triggered.append(result)
        
        monitor.register_handler(alert_handler)
        
        class MockUnhealthyCheck(HealthCheck):
            def check(self):
                return HealthCheckResult(
                    component=self.component,
                    status=HealthStatus.UNHEALTHY,
                    message="Critical issue"
                )
        
        monitor.register_check(MockUnhealthyCheck("critical", "system"))
        monitor.run_checks()
        
        assert len(alert_triggered) == 1
        assert alert_triggered[0].status == HealthStatus.UNHEALTHY
    
    @pytest.mark.ac("OB-002-02")
    def test_performance_profiling_integration(self):
        """Test performance profiling with recommendations."""
        profiler = PerformanceProfiler()
        
        # Simulate multiple slow database queries
        for i in range(20):
            duration = 250.0 + (i * 10)
            profiler.record_metric("db_query_users", duration)
        
        # Get bottlenecks and recommendations
        bottlenecks = profiler.identify_bottlenecks(threshold_ms=200)
        recommendations = profiler.generate_recommendations(bottlenecks)
        
        assert len(bottlenecks) > 0
        assert len(recommendations) > 0
        assert bottlenecks[0].operation == "db_query_users"
        assert any(
            "index" in r.recommendation.lower() or "database" in r.recommendation.lower()
            for r in recommendations
        )
    
    @pytest.mark.ac("OB-003-01")
    def test_audit_trail_integration(self):
        """Test audit trail with search and export."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            trail = AuditTrail(db_path=str(db_path))
            
            # Record various events
            for i in range(10):
                trail.record_event(
                    AuditEventType.CREATE,
                    "governance",
                    f"create_ac_{i}",
                    "admin",
                    severity=AuditSeverity.MEDIUM
                )
            
            # Search
            results = trail.search(component="governance")
            assert len(results) >= 10
            
            # Export
            export_json = Path(tmpdir) / "audit.json"
            trail.export_json(str(export_json), component="governance")
            assert export_json.exists()
            
            # Export CSV
            export_csv = Path(tmpdir) / "audit.csv"
            trail.export_csv(str(export_csv), component="governance")
            assert export_csv.exists()
            
            # Get statistics
            stats = trail.get_statistics()
            assert stats["total_events"] >= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
