"""Tests for base_collector.py

Test Coverage:
- Collector initialization and configuration
- Start/stop lifecycle management
- Metric collection and storage
- Health monitoring
- Error handling
- Abstract method enforcement
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.collectors.base_collector import (
    BaseCollector,
    CollectorStatus,
    CollectorPriority,
    CollectorMetric,
    CollectorHealth,
    ICollector
)


class ConcreteCollector(BaseCollector):
    """Concrete implementation for testing abstract BaseCollector"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collect_count = 0
    
    def _collect_metrics(self):
        """Test implementation of abstract method"""
        self.collect_count += 1
        return [
            CollectorMetric(
                name="test_metric",
                value=100,
                timestamp=datetime.now(timezone.utc)
            )
        ]


class TestCollectorEnums:
    """Tests for collector enums"""
    
    def test_collector_status_values(self):
        """Test CollectorStatus enum has expected values"""
        assert CollectorStatus.INITIALIZING.value == "initializing"
        assert CollectorStatus.ACTIVE.value == "active"
        assert CollectorStatus.PAUSED.value == "paused"
        assert CollectorStatus.ERROR.value == "error"
        assert CollectorStatus.STOPPED.value == "stopped"
    
    def test_collector_priority_values(self):
        """Test CollectorPriority enum has expected values"""
        assert CollectorPriority.CRITICAL.value == "critical"
        assert CollectorPriority.HIGH.value == "high"
        assert CollectorPriority.MEDIUM.value == "medium"
        assert CollectorPriority.LOW.value == "low"


class TestCollectorMetric:
    """Tests for CollectorMetric dataclass"""
    
    def test_metric_creation(self):
        """Test creating a CollectorMetric instance"""
        timestamp = datetime.now(timezone.utc)
        metric = CollectorMetric(
            name="test_metric",
            value=42,
            timestamp=timestamp
        )
        
        assert metric.name == "test_metric"
        assert metric.value == 42
        assert metric.timestamp == timestamp
        assert metric.tags == {}
        assert metric.metadata == {}
    
    def test_metric_with_tags_and_metadata(self):
        """Test metric with tags and metadata"""
        metric = CollectorMetric(
            name="test",
            value=100,
            timestamp=datetime.now(timezone.utc),
            tags={"env": "test"},
            metadata={"source": "unit_test"}
        )
        
        assert metric.tags == {"env": "test"}
        assert metric.metadata == {"source": "unit_test"}
    
    def test_metric_to_dict(self):
        """Test converting metric to dictionary"""
        timestamp = datetime.now(timezone.utc)
        metric = CollectorMetric(
            name="test",
            value=50,
            timestamp=timestamp,
            tags={"tag1": "value1"}
        )
        
        result = metric.to_dict()
        assert isinstance(result, dict)
        assert result['name'] == "test"
        assert result['value'] == 50
        assert 'timestamp' in result
        assert isinstance(result['timestamp'], str)  # ISO format


class TestCollectorHealth:
    """Tests for CollectorHealth dataclass"""
    
    def test_health_creation(self):
        """Test creating CollectorHealth instance"""
        health = CollectorHealth(
            status=CollectorStatus.ACTIVE,
            metrics_collected=100
        )
        
        assert health.status == CollectorStatus.ACTIVE
        assert health.metrics_collected == 100
        assert health.error_count == 0


class TestBaseCollectorInitialization:
    """Tests for BaseCollector initialization"""
    
    def test_init_with_required_params(self):
        """Test initialization with required parameters"""
        collector = ConcreteCollector(
            collector_id="test_collector",
            name="Test Collector"
        )
        
        assert collector.collector_id == "test_collector"
        assert collector.name == "Test Collector"
        assert collector.priority == CollectorPriority.MEDIUM
        assert collector.status == CollectorStatus.INITIALIZING
    
    def test_init_with_all_params(self):
        """Test initialization with all parameters"""
        collector = ConcreteCollector(
            collector_id="test_collector",
            name="Test Collector",
            priority=CollectorPriority.HIGH,
            collection_interval_seconds=30.0,
            brain_path="/tmp/brain"
        )
        
        assert collector.priority == CollectorPriority.HIGH
        assert collector.collection_interval == 30.0
        assert collector.brain_path == Path("/tmp/brain")
    
    def test_init_sets_default_values(self):
        """Test that initialization sets sensible defaults"""
        collector = ConcreteCollector("id", "name")
        
        assert collector.enabled is True
        assert collector.auto_start is True
        assert collector.error_count == 0
        assert collector.last_error is None
        assert collector.metrics_collected == 0


class TestCollectorLifecycle:
    """Tests for collector start/stop lifecycle"""
    
    def test_start_collector_success(self):
        """Test starting collector successfully"""
        collector = ConcreteCollector("test", "Test")
        result = collector.start()
        
        assert result is True
        assert collector.status == CollectorStatus.ACTIVE
    
    def test_start_collector_already_active(self):
        """Test starting already active collector"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        result = collector.start()  # Start again
        
        assert result is True
        assert collector.status == CollectorStatus.ACTIVE
    
    def test_start_disabled_collector(self):
        """Test that disabled collector does not start"""
        collector = ConcreteCollector("test", "Test")
        collector.enabled = False
        result = collector.start()
        
        assert result is False
        assert collector.status != CollectorStatus.ACTIVE
    
    def test_stop_collector_success(self):
        """Test stopping collector successfully"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        result = collector.stop()
        
        assert result is True
        assert collector.status == CollectorStatus.STOPPED
    
    def test_stop_collector_already_stopped(self):
        """Test stopping already stopped collector"""
        collector = ConcreteCollector("test", "Test")
        collector.status = CollectorStatus.STOPPED
        result = collector.stop()
        
        assert result is True
        assert collector.status == CollectorStatus.STOPPED


class TestMetricCollection:
    """Tests for metric collection functionality"""
    
    def test_collect_metrics_when_active(self):
        """Test collecting metrics when collector is active"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        
        metrics = collector.collect()
        
        assert len(metrics) == 1
        assert metrics[0].name == "test_metric"
        assert collector.metrics_collected == 1
        assert collector.collect_count == 1
    
    def test_collect_metrics_when_not_active(self):
        """Test that collecting when not active returns empty list"""
        collector = ConcreteCollector("test", "Test")
        # Don't start collector
        
        metrics = collector.collect()
        
        assert metrics == []
        assert collector.metrics_collected == 0
    
    def test_collect_updates_last_collection_time(self):
        """Test that collect updates last_collection timestamp"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        
        assert collector.last_collection is None
        collector.collect()
        assert collector.last_collection is not None
        assert isinstance(collector.last_collection, datetime)
    
    def test_collect_stores_recent_metrics(self):
        """Test that collected metrics are stored in recent cache"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        
        collector.collect()
        recent = collector.get_recent_metrics()
        
        assert len(recent) == 1
        assert recent[0].name == "test_metric"
    
    def test_get_recent_metrics_with_count(self):
        """Test getting specific number of recent metrics"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        
        # Collect multiple times
        for _ in range(5):
            collector.collect()
        
        recent = collector.get_recent_metrics(count=3)
        assert len(recent) == 3


class TestHealthMonitoring:
    """Tests for collector health monitoring"""
    
    def test_get_health_returns_collector_health(self):
        """Test that get_health returns CollectorHealth instance"""
        collector = ConcreteCollector("test", "Test")
        health = collector.get_health()
        
        assert isinstance(health, CollectorHealth)
        assert health.status == CollectorStatus.INITIALIZING
    
    def test_health_reflects_active_status(self):
        """Test health reflects active collector status"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        health = collector.get_health()
        
        assert health.status == CollectorStatus.ACTIVE
    
    def test_health_tracks_metrics_collected(self):
        """Test health tracks number of metrics collected"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        collector.collect()
        collector.collect()
        
        health = collector.get_health()
        assert health.metrics_collected == 2
    
    def test_health_tracks_error_count(self):
        """Test health tracks error count"""
        collector = ConcreteCollector("test", "Test")
        collector._handle_error("Test error")
        
        health = collector.get_health()
        assert health.error_count == 1
        assert health.last_error == "Test error"


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_handle_error_increments_count(self):
        """Test that _handle_error increments error count"""
        collector = ConcreteCollector("test", "Test")
        collector._handle_error("Error 1")
        collector._handle_error("Error 2")
        
        assert collector.error_count == 2
    
    def test_handle_error_sets_status(self):
        """Test that _handle_error sets status to ERROR"""
        collector = ConcreteCollector("test", "Test")
        collector.start()
        collector._handle_error("Test error")
        
        assert collector.status == CollectorStatus.ERROR
    
    def test_handle_error_stores_last_error(self):
        """Test that _handle_error stores last error message"""
        collector = ConcreteCollector("test", "Test")
        collector._handle_error("First error")
        collector._handle_error("Second error")
        
        assert collector.last_error == "Second error"


class TestRecentMetricsCache:
    """Tests for recent metrics caching"""
    
    def test_recent_metrics_cache_respects_max_size(self):
        """Test that recent metrics cache doesn't exceed max size"""
        collector = ConcreteCollector("test", "Test")
        collector._max_recent_metrics = 10
        collector.start()
        
        # Collect more than max
        for _ in range(15):
            collector.collect()
        
        assert len(collector._recent_metrics) <= 10
    
    def test_store_recent_metrics_trims_excess(self):
        """Test that storing metrics trims oldest when exceeding max"""
        collector = ConcreteCollector("test", "Test")
        collector._max_recent_metrics = 5
        
        # Add metrics directly
        for i in range(10):
            metric = CollectorMetric(
                name=f"metric_{i}",
                value=i,
                timestamp=datetime.now(timezone.utc)
            )
            collector._store_recent_metrics([metric])
        
        # Should only keep last 5
        assert len(collector._recent_metrics) == 5


class TestAbstractMethodEnforcement:
    """Tests for abstract method enforcement"""
    
    def test_cannot_instantiate_base_collector_directly(self):
        """Test that BaseCollector cannot be instantiated without implementing abstract methods"""
        with pytest.raises(TypeError):
            BaseCollector("test", "Test")  # Should raise TypeError


class TestPersistence:
    """Tests for metric persistence"""
    
    def test_persist_metrics_creates_directory(self, tmp_path):
        """Test that persist_metrics creates metrics directory"""
        collector = ConcreteCollector("test", "Test", brain_path=str(tmp_path))
        collector.start()
        
        metrics = [CollectorMetric("test", 100, datetime.now(timezone.utc))]
        collector._persist_metrics(metrics)
        
        metrics_dir = tmp_path / "metrics-history"
        assert metrics_dir.exists()
    
    def test_persist_metrics_without_brain_path(self):
        """Test that persist without brain_path doesn't raise error"""
        collector = ConcreteCollector("test", "Test", brain_path=None)
        metrics = [CollectorMetric("test", 100, datetime.now(timezone.utc))]
        
        # Should not raise error
        collector._persist_metrics(metrics)
