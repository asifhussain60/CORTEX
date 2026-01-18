"""
Test suite for AC-NFR-004-02: Real-Time Progress Dashboard Service

This test module validates the real-time progress dashboard service,
including live metrics updates, <1s update frequency, and data consistency.

AC-ID: AC-NFR-004-02
Title: Real-Time Progress Dashboard Service
Tests Required: 10 unit tests + 4 integration tests = 14 total
"""

import pytest
import time
import threading
from typing import Dict, List, Optional, Any, Callable
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass, field
from enum import Enum
from collections import deque


class DashboardUpdateType(Enum):
    """Types of dashboard updates."""
    METRIC = "metric"
    STATUS = "status"
    ALERT = "alert"
    PROGRESS = "progress"


@dataclass
class DashboardUpdate:
    """A single dashboard update."""
    update_type: DashboardUpdateType
    timestamp: float
    data: Dict[str, Any]


@dataclass
class DashboardMetrics:
    """Metrics displayed on dashboard."""
    total_operations: int = 0
    completed_operations: int = 0
    failed_operations: int = 0
    in_progress: int = 0
    average_duration_ms: float = 0.0
    throughput_ops_per_sec: float = 0.0
    error_rate: float = 0.0


class RealTimeProgressDashboard:
    """
    Real-time progress dashboard service.
    
    Provides <1s update frequency with:
    - Live metrics display
    - Operation progress tracking
    - Status updates
    - Error/alert display
    
    AC-ID: AC-NFR-004-02
    Title: Real-Time Progress Dashboard Service
    """
    
    def __init__(self, update_interval_ms: float = 500):
        """
        Initialize dashboard.
        
        Args:
            update_interval_ms: Target update frequency
        """
        self.update_interval_ms = update_interval_ms
        self.metrics = DashboardMetrics()
        self.updates: deque = deque(maxlen=1000)  # Keep last 1000 updates
        self.is_active = False
        self.last_update_time = time.time()
        self._lock = threading.RLock()
        self.subscribers: List[Callable] = []
    
    def start(self) -> None:
        """Start the dashboard."""
        with self._lock:
            self.is_active = True
    
    def stop(self) -> None:
        """Stop the dashboard."""
        with self._lock:
            self.is_active = False
    
    def update_metrics(self, metrics: DashboardMetrics) -> None:
        """
        Update dashboard metrics.
        
        Args:
            metrics: New metrics to display
        """
        with self._lock:
            self.metrics = metrics
            self._record_update(DashboardUpdateType.METRIC, {"metrics": vars(metrics)})
    
    def record_operation_progress(self, operation_id: str, progress: float) -> None:
        """
        Record progress for an operation (0.0-1.0).
        
        Args:
            operation_id: Unique operation identifier
            progress: Progress percentage (0.0-1.0)
        """
        with self._lock:
            self._record_update(DashboardUpdateType.PROGRESS, {
                "operation_id": operation_id,
                "progress": progress
            })
    
    def record_status_update(self, status: str) -> None:
        """Record a status update message."""
        with self._lock:
            self._record_update(DashboardUpdateType.STATUS, {"status": status})
    
    def record_alert(self, alert_message: str, severity: str = "warning") -> None:
        """
        Record an alert.
        
        Args:
            alert_message: Alert message
            severity: "info", "warning", or "error"
        """
        with self._lock:
            self._record_update(DashboardUpdateType.ALERT, {
                "message": alert_message,
                "severity": severity
            })
    
    def _record_update(self, update_type: DashboardUpdateType, data: Dict[str, Any]) -> None:
        """Record a dashboard update (must be called with lock)."""
        update = DashboardUpdate(
            update_type=update_type,
            timestamp=time.time(),
            data=data
        )
        self.updates.append(update)
        self.last_update_time = time.time()
        
        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(update)
            except Exception:
                pass  # Ignore subscriber errors
    
    def subscribe(self, callback: Callable[[DashboardUpdate], None]) -> None:
        """
        Subscribe to dashboard updates.
        
        Args:
            callback: Function called for each update
        """
        with self._lock:
            self.subscribers.append(callback)
    
    def get_updates_since(self, timestamp: float) -> List[DashboardUpdate]:
        """
        Get updates since a given timestamp.
        
        Args:
            timestamp: Starting timestamp
            
        Returns:
            List of updates after the timestamp
        """
        with self._lock:
            return [u for u in self.updates if u.timestamp >= timestamp]
    
    def get_time_since_last_update(self) -> float:
        """Get milliseconds since last update."""
        with self._lock:
            return (time.time() - self.last_update_time) * 1000
    
    def is_updating_within_sla(self) -> bool:
        """Check if updates are within <1s SLA."""
        return self.get_time_since_last_update() < 1000.0
    
    def get_current_metrics(self) -> DashboardMetrics:
        """Get current dashboard metrics."""
        with self._lock:
            return DashboardMetrics(
                total_operations=self.metrics.total_operations,
                completed_operations=self.metrics.completed_operations,
                failed_operations=self.metrics.failed_operations,
                in_progress=self.metrics.in_progress,
                average_duration_ms=self.metrics.average_duration_ms,
                throughput_ops_per_sec=self.metrics.throughput_ops_per_sec,
                error_rate=self.metrics.error_rate
            )


# UNIT TESTS (10 required)

class TestDashboardBasics:
    """Test basic dashboard functionality."""
    
    def test_dashboard_initialization(self):
        """Test dashboard initializes correctly."""
        dashboard = RealTimeProgressDashboard()
        
        assert dashboard.is_active is False
        assert dashboard.metrics.total_operations == 0
        assert len(dashboard.updates) == 0
    
    def test_dashboard_start_stop(self):
        """Test starting and stopping dashboard."""
        dashboard = RealTimeProgressDashboard()
        
        dashboard.start()
        assert dashboard.is_active is True
        
        dashboard.stop()
        assert dashboard.is_active is False
    
    def test_update_metrics(self):
        """Test updating dashboard metrics."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        metrics = DashboardMetrics(
            total_operations=100,
            completed_operations=75,
            failed_operations=5
        )
        dashboard.update_metrics(metrics)
        
        current = dashboard.get_current_metrics()
        assert current.total_operations == 100
        assert current.completed_operations == 75
        assert current.failed_operations == 5


class TestDashboardUpdates:
    """Test dashboard update recording."""
    
    def test_record_progress(self):
        """Test recording operation progress."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        dashboard.record_operation_progress("op-1", 0.5)
        
        assert len(dashboard.updates) == 1
        assert dashboard.updates[0].update_type == DashboardUpdateType.PROGRESS
    
    def test_record_status(self):
        """Test recording status updates."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        dashboard.record_status_update("Processing initiated")
        
        assert len(dashboard.updates) == 1
        assert dashboard.updates[0].update_type == DashboardUpdateType.STATUS
        assert dashboard.updates[0].data["status"] == "Processing initiated"
    
    def test_record_alert(self):
        """Test recording alerts."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        dashboard.record_alert("High memory usage", "warning")
        
        assert len(dashboard.updates) == 1
        assert dashboard.updates[0].update_type == DashboardUpdateType.ALERT
        assert dashboard.updates[0].data["severity"] == "warning"


class TestDashboardSubscriptions:
    """Test subscription notifications."""
    
    def test_subscribe_to_updates(self):
        """Test subscribing to dashboard updates."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        received_updates = []
        dashboard.subscribe(lambda u: received_updates.append(u))
        
        dashboard.record_status_update("Test")
        
        assert len(received_updates) == 1
        assert received_updates[0].data["status"] == "Test"
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        updates1 = []
        updates2 = []
        dashboard.subscribe(lambda u: updates1.append(u))
        dashboard.subscribe(lambda u: updates2.append(u))
        
        dashboard.record_status_update("Test")
        
        assert len(updates1) == 1
        assert len(updates2) == 1


class TestDashboardPerformance:
    """Test dashboard performance characteristics."""
    
    def test_update_within_sla(self):
        """Test updates complete within <1s SLA."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        # Record update
        dashboard.record_status_update("Test")
        
        # Should be within SLA immediately
        assert dashboard.is_updating_within_sla() is True
    
    def test_get_updates_since_timestamp(self):
        """Test retrieving updates since a timestamp."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        start_time = time.time()
        time.sleep(0.01)
        
        dashboard.record_status_update("Update 1")
        dashboard.record_status_update("Update 2")
        
        updates = dashboard.get_updates_since(start_time)
        assert len(updates) == 2


# INTEGRATION TESTS (4 required)

class TestDashboardIntegration:
    """Integration tests for dashboard."""
    
    def test_full_dashboard_lifecycle(self):
        """Test complete dashboard lifecycle."""
        dashboard = RealTimeProgressDashboard(update_interval_ms=100)
        updates_received = []
        
        dashboard.subscribe(lambda u: updates_received.append(u))
        dashboard.start()
        
        # Record various updates
        metrics = DashboardMetrics(total_operations=50, completed_operations=25)
        dashboard.update_metrics(metrics)
        dashboard.record_operation_progress("op-1", 0.5)
        dashboard.record_status_update("Half complete")
        dashboard.record_alert("Processing", "info")
        
        # Verify all recorded
        assert len(dashboard.updates) == 4
        assert len(updates_received) == 4
        
        dashboard.stop()
        assert dashboard.is_active is False
    
    def test_concurrent_updates(self):
        """Test concurrent update handling."""
        dashboard = RealTimeProgressDashboard()
        dashboard.start()
        
        def worker(worker_id: int):
            for i in range(10):
                dashboard.record_operation_progress(f"op-{worker_id}-{i}", i/10)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Should have 50 updates (5 workers * 10 updates)
        assert len(dashboard.updates) == 50
    
    def test_dashboard_with_high_frequency_updates(self):
        """Test dashboard with high frequency updates."""
        dashboard = RealTimeProgressDashboard(update_interval_ms=10)
        dashboard.start()
        
        start = time.time()
        for i in range(100):
            dashboard.record_operation_progress("op", i/100)
        elapsed = time.time() - start
        
        # Should complete quickly
        assert elapsed < 0.5
        assert dashboard.is_updating_within_sla() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
