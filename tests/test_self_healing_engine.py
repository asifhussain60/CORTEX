"""
Test suite for self-healing engine.

Tests cover:
- Pattern detection (recurring errors, performance degradation)
- Anomaly detection (statistical outliers, threshold violations)
- Error clustering (similar errors grouped for analysis)
- Automated recovery (retry logic, fallback strategies)
- State recovery (checkpoint restoration)
- Self-healing metrics (success rate, recovery time)
"""

import asyncio
import json
import pytest
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.logging.self_healing_engine import (
    SelfHealingEngine,
    PatternDetector,
    AnomalyDetector,
    ErrorCluster,
    RecoveryStrategy
)
from src.logging.audit_logger import AuditLogger, LogLevel


class TestPatternDetector:
    """Test pattern detection in audit logs."""
    
    @pytest.fixture
    def pattern_detector(self):
        """Create pattern detector instance."""
        return PatternDetector(
            window_size=100,  # Analyze last 100 events
            min_occurrences=3,  # Pattern needs 3+ occurrences
            confidence_threshold=0.7  # 70% confidence required
        )
    
    def test_detect_recurring_error_pattern(self, pattern_detector):
        """Test detection of recurring error patterns."""
        events = [
            {"event": "database_connection_failed", "orchestrator": "planning", "timestamp": "2026-01-05T10:00:00"},
            {"event": "api_call_timeout", "orchestrator": "ado", "timestamp": "2026-01-05T10:01:00"},
            {"event": "database_connection_failed", "orchestrator": "planning", "timestamp": "2026-01-05T10:02:00"},
            {"event": "database_connection_failed", "orchestrator": "maintenance", "timestamp": "2026-01-05T10:03:00"},
            {"event": "api_call_timeout", "orchestrator": "ado", "timestamp": "2026-01-05T10:04:00"},
        ]
        
        patterns = pattern_detector.detect_patterns(events)
        
        # Should detect "database_connection_failed" as recurring pattern (3 occurrences)
        assert len(patterns) >= 1
        db_pattern = next((p for p in patterns if "database_connection_failed" in p.signature), None)
        assert db_pattern is not None
        assert db_pattern.occurrences >= 3
        assert db_pattern.confidence >= 0.7
    
    def test_detect_performance_degradation_pattern(self, pattern_detector):
        """Test detection of performance degradation patterns."""
        events = [
            {"event": "operation_completed", "data": {"duration_ms": 100}, "timestamp": "2026-01-05T10:00:00"},
            {"event": "operation_completed", "data": {"duration_ms": 150}, "timestamp": "2026-01-05T10:01:00"},
            {"event": "operation_completed", "data": {"duration_ms": 200}, "timestamp": "2026-01-05T10:02:00"},
            {"event": "operation_completed", "data": {"duration_ms": 500}, "timestamp": "2026-01-05T10:03:00"},
            {"event": "operation_completed", "data": {"duration_ms": 800}, "timestamp": "2026-01-05T10:04:00"},
        ]
        
        degradation = pattern_detector.detect_performance_degradation(events)
        
        # Should detect increasing duration trend
        assert degradation is not None
        assert degradation.degradation_rate > 0  # Positive rate = degrading
        assert degradation.severity in ["medium", "high"]
    
    def test_no_pattern_below_threshold(self, pattern_detector):
        """Test that patterns below threshold are not detected."""
        events = [
            {"event": f"unique_event_{i}", "timestamp": f"2026-01-05T10:00:{i:02d}"}
            for i in range(10)
        ]
        
        patterns = pattern_detector.detect_patterns(events)
        
        # All events unique, no patterns should be detected
        assert len(patterns) == 0


class TestAnomalyDetector:
    """Test anomaly detection in audit logs."""
    
    @pytest.fixture
    def anomaly_detector(self):
        """Create anomaly detector instance."""
        return AnomalyDetector(
            std_threshold=3.0,  # 3 standard deviations
            iqr_threshold=1.5,  # 1.5x interquartile range
            baseline_window=50  # Use last 50 events for baseline
        )
    
    def test_detect_statistical_outliers(self, anomaly_detector):
        """Test detection of statistical outliers."""
        # Normal distribution: mean=100, std=10
        normal_values = [100 + (i % 20 - 10) for i in range(50)]
        # Outliers: 3+ standard deviations from mean
        outlier_values = [200, 250, 300]
        
        events = [
            {"event": "metric", "data": {"value": v}, "timestamp": f"2026-01-05T10:00:{i:02d}"}
            for i, v in enumerate(normal_values + outlier_values)
        ]
        
        anomalies = anomaly_detector.detect_anomalies(events, metric_key="data.value")
        
        # Should detect 3 outliers
        assert len(anomalies) >= 3
        for anomaly in anomalies:
            assert anomaly.value >= 200  # All outliers > 200
            assert anomaly.z_score > 3.0  # More than 3 std deviations
    
    def test_detect_threshold_violations(self, anomaly_detector):
        """Test detection of threshold violations."""
        events = [
            {"event": "cpu_usage", "data": {"percent": 95}, "timestamp": "2026-01-05T10:00:00"},
            {"event": "memory_usage", "data": {"percent": 98}, "timestamp": "2026-01-05T10:01:00"},
            {"event": "disk_usage", "data": {"percent": 99}, "timestamp": "2026-01-05T10:02:00"},
        ]
        
        thresholds = {
            "cpu_usage": {"metric": "data.percent", "max": 90},
            "memory_usage": {"metric": "data.percent", "max": 95},
            "disk_usage": {"metric": "data.percent", "max": 95}
        }
        
        violations = anomaly_detector.detect_threshold_violations(events, thresholds)
        
        # All events exceed thresholds
        assert len(violations) == 3
        assert all(v.severity in ["warning", "critical"] for v in violations)
    
    def test_detect_rate_anomalies(self, anomaly_detector):
        """Test detection of sudden rate changes."""
        # Normal rate: 10 events per minute
        normal_events = [
            {"event": "api_call", "timestamp": f"2026-01-05T10:{i:02d}:00"}
            for i in range(10)
        ]
        # Sudden spike: 100 events in one minute
        spike_events = [
            {"event": "api_call", "timestamp": f"2026-01-05T10:11:{i:02d}"}
            for i in range(100)
        ]
        
        anomalies = anomaly_detector.detect_rate_anomalies(normal_events + spike_events, window_seconds=60)
        
        # Should detect spike
        assert len(anomalies) >= 1
        spike_anomaly = anomalies[0]
        assert spike_anomaly.rate_change > 5.0  # More than 5x increase


class TestErrorCluster:
    """Test error clustering functionality."""
    
    @pytest.fixture
    def error_cluster(self):
        """Create error cluster instance."""
        return ErrorCluster(
            similarity_threshold=0.8,  # 80% similarity to group
            min_cluster_size=2  # At least 2 errors to form cluster
        )
    
    def test_cluster_similar_errors(self, error_cluster):
        """Test clustering of similar error messages."""
        errors = [
            {"error": "Connection timeout after 30 seconds", "orchestrator": "planning"},
            {"error": "Connection timeout after 60 seconds", "orchestrator": "ado"},
            {"error": "Connection timeout after 45 seconds", "orchestrator": "tdd"},
            {"error": "File not found: /path/to/file.txt", "orchestrator": "vacuum"},
            {"error": "File not found: /path/to/data.json", "orchestrator": "cleanup"},
        ]
        
        clusters = error_cluster.cluster_errors(errors)
        
        # Should create 2 clusters: timeouts and file-not-found
        assert len(clusters) == 2
        
        timeout_cluster = next((c for c in clusters if "timeout" in c.representative_error.lower()), None)
        assert timeout_cluster is not None
        assert len(timeout_cluster.errors) == 3
        
        file_cluster = next((c for c in clusters if "file not found" in c.representative_error.lower()), None)
        assert file_cluster is not None
        assert len(file_cluster.errors) == 2
    
    def test_identify_cluster_root_cause(self, error_cluster):
        """Test root cause identification for error clusters."""
        errors = [
            {
                "error": "Database connection failed",
                "orchestrator": "planning",
                "data": {"host": "db.example.com", "port": 5432}
            },
            {
                "error": "Database connection failed",
                "orchestrator": "ado",
                "data": {"host": "db.example.com", "port": 5432}
            },
            {
                "error": "Database connection failed",
                "orchestrator": "maintenance",
                "data": {"host": "db.example.com", "port": 5432}
            },
        ]
        
        clusters = error_cluster.cluster_errors(errors)
        root_cause = error_cluster.identify_root_cause(clusters[0])
        
        # Should identify common attributes
        assert root_cause.common_attributes["host"] == "db.example.com"
        assert root_cause.common_attributes["port"] == 5432
        assert root_cause.affected_orchestrators == ["planning", "ado", "maintenance"]
        assert "database" in root_cause.suggested_fix.lower()


class TestRecoveryStrategy:
    """Test automated recovery strategies."""
    
    @pytest.mark.asyncio
    async def test_retry_strategy(self):
        """Test retry recovery strategy."""
        # Mock failing operation
        attempt_count = 0
        
        async def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        strategy = RecoveryStrategy(
            strategy_type="retry",
            max_attempts=5,
            backoff_seconds=0.1  # Fast for testing
        )
        
        result = await strategy.execute(failing_operation)
        
        # Should succeed after 3 attempts
        assert result == "success"
        assert attempt_count == 3
    
    @pytest.mark.asyncio
    async def test_fallback_strategy(self):
        """Test fallback recovery strategy."""
        primary_failed = False
        
        async def primary_operation():
            nonlocal primary_failed
            primary_failed = True
            raise Exception("Primary failed")
        
        async def fallback_operation():
            return "fallback_success"
        
        strategy = RecoveryStrategy(
            strategy_type="fallback",
            fallback_func=fallback_operation
        )
        
        result = await strategy.execute(primary_operation)
        
        # Should use fallback
        assert primary_failed
        assert result == "fallback_success"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_strategy(self):
        """Test circuit breaker recovery strategy."""
        call_count = 0
        
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            raise Exception("Always fails")
        
        strategy = RecoveryStrategy(
            strategy_type="circuit_breaker",
            failure_threshold=3,  # Open after 3 failures
            timeout_seconds=1.0
        )
        
        # First 3 calls should attempt operation
        for _ in range(3):
            with pytest.raises(Exception):
                await strategy.execute(flaky_operation)
        
        # Circuit should be OPEN now, no more calls
        initial_count = call_count
        with pytest.raises(Exception, match="Circuit breaker OPEN"):
            await strategy.execute(flaky_operation)
        
        assert call_count == initial_count  # No additional calls made


class TestSelfHealingEngine:
    """Test integrated self-healing engine."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    async def self_healing_engine(self, temp_log_dir):
        """Create self-healing engine instance."""
        audit_logger = AuditLogger({"log_dir": str(temp_log_dir)})
        
        engine = SelfHealingEngine(
            audit_logger=audit_logger,
            analysis_interval=1.0,  # Analyze every second
            auto_recovery_enabled=True
        )
        
        yield engine
        
        await engine.stop()
    
    @pytest.mark.asyncio
    async def test_detect_and_recover_from_error_pattern(self, self_healing_engine):
        """Test end-to-end detection and recovery."""
        # Simulate recurring error
        for i in range(5):
            await self_healing_engine.audit_logger.log(
                level=LogLevel.ERROR,
                orchestrator="planning",
                event="database_connection_failed",
                data={"attempt": i, "error": "Connection timeout"}
            )
        
        # Wait for analysis
        await asyncio.sleep(1.5)
        
        # Check if pattern was detected
        patterns = self_healing_engine.get_detected_patterns()
        assert len(patterns) >= 1
        
        db_pattern = next((p for p in patterns if "database_connection" in p.signature), None)
        assert db_pattern is not None
        
        # Check if recovery was attempted
        recoveries = self_healing_engine.get_recovery_attempts()
        assert len(recoveries) >= 1
    
    @pytest.mark.asyncio
    async def test_self_healing_metrics(self, self_healing_engine):
        """Test self-healing metrics collection."""
        # Simulate successful recovery
        await self_healing_engine.record_recovery_attempt(
            pattern_id="test_pattern_1",
            strategy="retry",
            success=True,
            recovery_time_ms=150
        )
        
        # Simulate failed recovery
        await self_healing_engine.record_recovery_attempt(
            pattern_id="test_pattern_2",
            strategy="fallback",
            success=False,
            recovery_time_ms=500
        )
        
        metrics = await self_healing_engine.get_metrics()
        
        # Should have success rate, average recovery time
        assert "success_rate" in metrics
        assert metrics["success_rate"] == 0.5  # 1 of 2 successful
        assert "avg_recovery_time_ms" in metrics
        assert metrics["total_attempts"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
