"""
Tests for MetricsCollector - Low-level metrics capture with sampling.

TDD Phase: RED
Author: Asif Hussain
Created: 2026-02-04
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Import will fail until we implement (RED phase)
try:
    from cortex.observability.metrics_collector import (
        MetricsCollector,
        get_metrics_collector,
    )
    from cortex.observability.metrics_schema import TDDMetric, DebugMetric
    IMPORTS_AVAILABLE = True
except ImportError:
    IMPORTS_AVAILABLE = False


@pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Metrics collector not yet implemented")
class TestMetricsCollector:
    """Tests for MetricsCollector functionality."""
    
    def test_collector_singleton(self):
        """Test collector is singleton."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        assert collector1 is collector2
        
    def test_record_tdd_metric(self):
        """Test recording a TDD metric."""
        collector = MetricsCollector()
        metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440000",
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1500,
            success=True,
        )
        
        collector.record(metric)
        
        metrics = collector.get_metrics("tdd", limit=10)
        assert len(metrics) == 1
        assert metrics[0].phase == "RED"
        
    def test_record_multiple_metric_types(self):
        """Test recording different metric types."""
        collector = MetricsCollector()
        
        tdd_metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440001",
            phase="GREEN",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=2000,
            success=True,
        )
        
        debug_metric = DebugMetric(
            session_id="660e8400-e29b-41d4-a716-446655440000",
            orchestrator="DebuggingOrchestrator",
            target_file="cortex/orchestrators/core/intent_router.py",
            duration_ms=30000,
            resolved=True,
            steps_taken=5,
        )
        
        collector.record(tdd_metric)
        collector.record(debug_metric)
        
        tdd_metrics = collector.get_metrics("tdd")
        debug_metrics = collector.get_metrics("debug")
        
        assert len(tdd_metrics) == 1
        assert len(debug_metrics) == 1
        
    def test_sampling_rate(self):
        """Test sampling rate controls metric recording."""
        collector = MetricsCollector(sampling_rate=0.5)
        
        # Record 100 metrics with 50% sampling
        with patch('random.random') as mock_random:
            recorded_count = 0
            for i in range(100):
                # Alternate between recording and not recording
                mock_random.return_value = 0.3 if i % 2 == 0 else 0.7
                metric = TDDMetric(
                    cycle_id=f"550e8400-e29b-41d4-a716-44665544{i:04d}",
                    phase="RED",
                    orchestrator="TDDOrchestrator",
                    test_file="tests/unit/test_example.py",
                    duration_ms=1000,
                    success=True,
                )
                if collector.record(metric):
                    recorded_count += 1
                    
        # With mocked 50% sampling, should record ~50
        assert recorded_count == 50
        
    def test_metrics_retention(self):
        """Test metrics are retained for configured period."""
        collector = MetricsCollector(retention_hours=24)
        
        # Create old metric (simulated)
        old_metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440002",
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1000,
            success=True,
        )
        
        collector.record(old_metric)
        
        # Simulate time passing beyond retention
        with patch.object(collector, '_get_retention_cutoff') as mock_cutoff:
            mock_cutoff.return_value = datetime.now() + timedelta(hours=25)
            collector.cleanup_old_metrics()
            
        metrics = collector.get_metrics("tdd")
        assert len(metrics) == 0
        
    def test_get_metrics_with_time_range(self):
        """Test getting metrics within time range."""
        collector = MetricsCollector()
        
        now = datetime.now()
        
        # Record metrics at different times
        for i in range(5):
            metric = TDDMetric(
                cycle_id=f"550e8400-e29b-41d4-a716-44665544{i:04d}",
                phase="GREEN",
                orchestrator="TDDOrchestrator",
                test_file="tests/unit/test_example.py",
                duration_ms=1000 + (i * 500),
                success=True,
            )
            collector.record(metric)
            
        # Get metrics from last hour
        metrics = collector.get_metrics(
            "tdd",
            since=now - timedelta(hours=1),
            until=now + timedelta(hours=1),
        )
        
        assert len(metrics) == 5
        
    def test_aggregate_metrics(self):
        """Test aggregating metrics."""
        collector = MetricsCollector()
        
        # Record multiple TDD metrics
        durations = [1000, 2000, 3000, 4000, 5000]
        for i, duration in enumerate(durations):
            metric = TDDMetric(
                cycle_id=f"550e8400-e29b-41d4-a716-44665544{i:04d}",
                phase="GREEN",
                orchestrator="TDDOrchestrator",
                test_file="tests/unit/test_example.py",
                duration_ms=duration,
                success=i < 4,  # 4 success, 1 failure
            )
            collector.record(metric)
            
        aggregation = collector.aggregate("tdd")
        
        assert aggregation.count == 5
        assert aggregation.avg_duration_ms == 3000
        assert aggregation.success_rate == 0.8
        
    def test_flush_to_storage(self):
        """Test flushing metrics to persistent storage."""
        collector = MetricsCollector()
        
        metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440010",
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1500,
            success=True,
        )
        
        collector.record(metric)
        
        # Mock storage backend
        mock_storage = MagicMock()
        collector.set_storage_backend(mock_storage)
        
        collector.flush()
        
        mock_storage.write.assert_called_once()
        
    def test_metrics_by_orchestrator(self):
        """Test filtering metrics by orchestrator."""
        collector = MetricsCollector()
        
        # Record metrics from different orchestrators
        orchestrators = ["TDDOrchestrator", "DebuggingOrchestrator", "TDDOrchestrator"]
        for i, orch in enumerate(orchestrators):
            metric = TDDMetric(
                cycle_id=f"550e8400-e29b-41d4-a716-44665544{i:04d}",
                phase="GREEN",
                orchestrator=orch,
                test_file="tests/unit/test_example.py",
                duration_ms=1000,
                success=True,
            )
            collector.record(metric)
            
        tdd_metrics = collector.get_metrics("tdd", orchestrator="TDDOrchestrator")
        
        assert len(tdd_metrics) == 2
        
    def test_clear_metrics(self):
        """Test clearing all metrics."""
        collector = MetricsCollector()
        
        metric = TDDMetric(
            cycle_id="550e8400-e29b-41d4-a716-446655440020",
            phase="RED",
            orchestrator="TDDOrchestrator",
            test_file="tests/unit/test_example.py",
            duration_ms=1000,
            success=True,
        )
        
        collector.record(metric)
        assert len(collector.get_metrics("tdd")) == 1
        
        collector.clear()
        assert len(collector.get_metrics("tdd")) == 0
