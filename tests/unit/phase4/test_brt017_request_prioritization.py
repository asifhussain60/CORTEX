"""
Comprehensive test suite for BRT-017: Request Prioritization Pattern.

Tests queue-based request prioritization enabling systems to process high-priority
requests first during normal operation and adjust priority handling during
degradation, ensuring critical requests proceed even when resources are constrained.

The request prioritization pattern provides:
- Multi-level priority queue management (HIGH, NORMAL, LOW)
- Request queueing with priority ordering
- Automatic priority adjustment during degradation
- Metrics tracking for queue dynamics
- Integration with graceful degradation patterns

AC-INFRA-002-08: Request prioritization with degradation integration
"""

import threading
import time
from typing import List, Generator, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

import pytest


# ============================================================================
# REQUEST PRIORITIZATION IMPLEMENTATION FOR TESTING
# ============================================================================

class PriorityLevel(str, Enum):
    """Priority levels for requests."""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Request:
    """Represents a request with priority."""
    
    request_id: str
    data: Any
    priority: PriorityLevel = PriorityLevel.NORMAL
    timestamp: float = field(default_factory=time.time)
    retry_count: int = 0


@dataclass
class RequestStats:
    """Statistics for a single request."""
    
    request_id: str
    priority: PriorityLevel
    wait_time_ms: float
    processing_time_ms: float
    skipped: bool = False
    processed: bool = False


@dataclass
class PriorityQueueConfig:
    """Configuration for priority queue."""
    
    max_queue_size: int = 1000
    skip_low_priority_on_degradation: bool = True
    boost_priority_on_recovery: bool = True
    timeout_ms: float = 30000.0


@dataclass
class QueueMetrics:
    """Metrics for the priority queue."""
    
    total_requests: int = 0
    processed_requests: int = 0
    skipped_requests: int = 0
    high_priority_count: int = 0
    normal_priority_count: int = 0
    low_priority_count: int = 0
    queue_size: int = 0


class PriorityQueueManager:
    """Manages request prioritization with multi-level queues."""
    
    def __init__(self, config: Optional[PriorityQueueConfig] = None) -> None:
        """Initialize priority queue manager."""
        self.config = config or PriorityQueueConfig()
        self.high_priority_queue: deque[Request] = deque()
        self.normal_priority_queue: deque[Request] = deque()
        self.low_priority_queue: deque[Request] = deque()
        self.metrics = QueueMetrics()
        self.lock = threading.Lock()
        self._request_stats: Dict[str, RequestStats] = {}
        self._is_degraded = False
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if self.config.max_queue_size <= 0:
            raise ValueError("max_queue_size must be > 0")
        if self.config.timeout_ms <= 0:
            raise ValueError("timeout_ms must be > 0")
    
    def add_request(self, request: Request) -> bool:
        """Add request to appropriate priority queue."""
        with self.lock:
            # Check queue size limit
            total_size = (
                len(self.high_priority_queue)
                + len(self.normal_priority_queue)
                + len(self.low_priority_queue)
            )
            
            if total_size >= self.config.max_queue_size:
                return False
            
            # Add to appropriate queue based on priority
            if request.priority == PriorityLevel.HIGH:
                self.high_priority_queue.append(request)
                self.metrics.high_priority_count += 1
            elif request.priority == PriorityLevel.NORMAL:
                self.normal_priority_queue.append(request)
                self.metrics.normal_priority_count += 1
            else:  # LOW
                self.low_priority_queue.append(request)
                self.metrics.low_priority_count += 1
            
            self.metrics.total_requests += 1
            self._update_queue_size()
            
            # Initialize stats
            self._request_stats[request.request_id] = RequestStats(
                request_id=request.request_id,
                priority=request.priority,
                wait_time_ms=0.0,
                processing_time_ms=0.0,
            )
            
            return True
    
    def _update_queue_size(self) -> None:
        """Update current queue size metric."""
        self.metrics.queue_size = (
            len(self.high_priority_queue)
            + len(self.normal_priority_queue)
            + len(self.low_priority_queue)
        )
    
    def get_next_request(self) -> Optional[Request]:
        """Get next request respecting priority order and degradation state."""
        with self.lock:
            # If degraded, skip LOW priority requests
            if self._is_degraded and self.config.skip_low_priority_on_degradation:
                # Try HIGH first
                if self.high_priority_queue:
                    request = self.high_priority_queue.popleft()
                    self._update_queue_size()
                    return request
                
                # Then NORMAL
                if self.normal_priority_queue:
                    request = self.normal_priority_queue.popleft()
                    self._update_queue_size()
                    return request
                
                # LOW is skipped during degradation
                return None
            
            # Normal operation: process by priority
            if self.high_priority_queue:
                request = self.high_priority_queue.popleft()
                self._update_queue_size()
                return request
            
            if self.normal_priority_queue:
                request = self.normal_priority_queue.popleft()
                self._update_queue_size()
                return request
            
            if self.low_priority_queue:
                request = self.low_priority_queue.popleft()
                self._update_queue_size()
                return request
            
            return None
    
    def process_request(self, request: Request) -> Any:
        """Process a request (simulated)."""
        start_time = time.time()
        
        # Simulate processing based on priority
        if request.priority == PriorityLevel.HIGH:
            time.sleep(0.001)  # 1ms
        elif request.priority == PriorityLevel.NORMAL:
            time.sleep(0.002)  # 2ms
        else:
            time.sleep(0.005)  # 5ms
        
        processing_time = (time.time() - start_time) * 1000
        
        with self.lock:
            self.metrics.processed_requests += 1
            if request.request_id in self._request_stats:
                self._request_stats[request.request_id].processing_time_ms = processing_time
                self._request_stats[request.request_id].processed = True
        
        return f"processed_{request.request_id}"
    
    def skip_request(self, request: Request) -> None:
        """Mark request as skipped (e.g., during heavy degradation)."""
        with self.lock:
            self.metrics.skipped_requests += 1
            if request.request_id in self._request_stats:
                self._request_stats[request.request_id].skipped = True
    
    def set_degraded(self, is_degraded: bool) -> None:
        """Set degradation state."""
        with self.lock:
            self._is_degraded = is_degraded
    
    def is_degraded(self) -> bool:
        """Check if system is in degraded state."""
        with self.lock:
            return self._is_degraded
    
    def boost_priority(self, request_id: str, new_priority: PriorityLevel) -> bool:
        """Boost priority of a request in queue."""
        with self.lock:
            # Search for request in all queues
            queues = [
                self.high_priority_queue,
                self.normal_priority_queue,
                self.low_priority_queue,
            ]
            
            for queue in queues:
                for request in queue:
                    if request.request_id == request_id:
                        # Found it, remove and re-add with new priority
                        queue.remove(request)
                        old_priority = request.priority
                        request.priority = new_priority
                        
                        # Update metrics
                        if old_priority == PriorityLevel.HIGH:
                            self.metrics.high_priority_count -= 1
                        elif old_priority == PriorityLevel.NORMAL:
                            self.metrics.normal_priority_count -= 1
                        else:
                            self.metrics.low_priority_count -= 1
                        
                        if new_priority == PriorityLevel.HIGH:
                            self.high_priority_queue.append(request)
                            self.metrics.high_priority_count += 1
                        elif new_priority == PriorityLevel.NORMAL:
                            self.normal_priority_queue.append(request)
                            self.metrics.normal_priority_count += 1
                        else:
                            self.low_priority_queue.append(request)
                            self.metrics.low_priority_count += 1
                        
                        self._update_queue_size()
                        return True
            
            return False
    
    def get_queue_depth(self, priority: PriorityLevel) -> int:
        """Get depth of queue for specific priority."""
        with self.lock:
            if priority == PriorityLevel.HIGH:
                return len(self.high_priority_queue)
            elif priority == PriorityLevel.NORMAL:
                return len(self.normal_priority_queue)
            else:
                return len(self.low_priority_queue)
    
    def get_total_queue_depth(self) -> int:
        """Get total queue depth across all priorities."""
        with self.lock:
            return (
                len(self.high_priority_queue)
                + len(self.normal_priority_queue)
                + len(self.low_priority_queue)
            )
    
    def drain_queue(self) -> List[Any]:
        """Drain all requests from queue (for shutdown)."""
        with self.lock:
            requests: List[Any] = []
            
            # Drain in priority order
            requests.extend(list(self.high_priority_queue))
            self.high_priority_queue.clear()
            
            requests.extend(list(self.normal_priority_queue))
            self.normal_priority_queue.clear()
            
            requests.extend(list(self.low_priority_queue))
            self.low_priority_queue.clear()
            
            self.metrics.queue_size = 0
            
            return requests
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get queue metrics."""
        with self.lock:
            total_queue_depth = (
                len(self.high_priority_queue)
                + len(self.normal_priority_queue)
                + len(self.low_priority_queue)
            )
            
            return {
                "total_requests": self.metrics.total_requests,
                "processed_requests": self.metrics.processed_requests,
                "skipped_requests": self.metrics.skipped_requests,
                "high_priority_count": self.metrics.high_priority_count,
                "normal_priority_count": self.metrics.normal_priority_count,
                "low_priority_count": self.metrics.low_priority_count,
                "queue_size": self.metrics.queue_size,
                "pending_requests": total_queue_depth,
            }
    
    def get_request_stats(self, request_id: str) -> Optional[RequestStats]:
        """Get statistics for a specific request."""
        with self.lock:
            return self._request_stats.get(request_id)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def priority_queue() -> Generator[PriorityQueueManager, None, None]:
    """Create a PriorityQueueManager for testing."""
    manager = PriorityQueueManager()
    yield manager


@pytest.fixture
def configured_queue() -> Generator[PriorityQueueManager, None, None]:
    """Create queue with custom configuration."""
    config = PriorityQueueConfig(
        max_queue_size=100,
        skip_low_priority_on_degradation=True,
        boost_priority_on_recovery=True,
    )
    manager = PriorityQueueManager(config=config)
    yield manager


# ============================================================================
# CATEGORY 1: INITIALIZATION & CONFIGURATION (3/3)
# ============================================================================

class TestInitialization:
    """Test priority queue initialization."""
    
    def test_creates_queue_with_default_config(self, priority_queue: PriorityQueueManager) -> None:
        """Should create queue with default configuration."""
        assert priority_queue is not None
        assert priority_queue.config.max_queue_size == 1000
        assert priority_queue.config.skip_low_priority_on_degradation is True
    
    def test_creates_queue_with_custom_config(self) -> None:
        """Should create queue with custom configuration."""
        config = PriorityQueueConfig(
            max_queue_size=500,
            skip_low_priority_on_degradation=False,
        )
        manager = PriorityQueueManager(config=config)
        
        assert manager.config.max_queue_size == 500
        assert manager.config.skip_low_priority_on_degradation is False
    
    def test_rejects_invalid_max_queue_size(self) -> None:
        """Should reject invalid max queue size."""
        with pytest.raises(ValueError):
            config = PriorityQueueConfig(max_queue_size=-1)
            PriorityQueueManager(config=config)


# ============================================================================
# CATEGORY 2: PRIORITY LEVELS (3/3)
# ============================================================================

class TestPriorityLevels:
    """Test priority level handling."""
    
    def test_defines_high_priority(self) -> None:
        """Should define HIGH priority level."""
        assert PriorityLevel.HIGH.value == "high"
    
    def test_defines_normal_priority(self) -> None:
        """Should define NORMAL priority level."""
        assert PriorityLevel.NORMAL.value == "normal"
    
    def test_defines_low_priority(self) -> None:
        """Should define LOW priority level."""
        assert PriorityLevel.LOW.value == "low"


# ============================================================================
# CATEGORY 3: REQUEST QUEUEING (4/4)
# ============================================================================

class TestRequestQueueing:
    """Test request queueing operations."""
    
    def test_adds_high_priority_request(self, priority_queue: PriorityQueueManager) -> None:
        """Should add high priority request to queue."""
        request = Request("req1", "data", PriorityLevel.HIGH)
        result = priority_queue.add_request(request)
        
        assert result is True
        assert priority_queue.get_queue_depth(PriorityLevel.HIGH) == 1
    
    def test_adds_multiple_requests_with_different_priorities(
        self,
        priority_queue: PriorityQueueManager,
    ) -> None:
        """Should add requests with different priorities."""
        priority_queue.add_request(Request("req1", "data", PriorityLevel.HIGH))
        priority_queue.add_request(Request("req2", "data", PriorityLevel.NORMAL))
        priority_queue.add_request(Request("req3", "data", PriorityLevel.LOW))
        
        assert priority_queue.get_queue_depth(PriorityLevel.HIGH) == 1
        assert priority_queue.get_queue_depth(PriorityLevel.NORMAL) == 1
        assert priority_queue.get_queue_depth(PriorityLevel.LOW) == 1
    
    def test_respects_queue_size_limit(self, configured_queue: PriorityQueueManager) -> None:
        """Should enforce queue size limit."""
        configured_queue.config.max_queue_size = 2
        
        result1 = configured_queue.add_request(Request("req1", "data"))
        result2 = configured_queue.add_request(Request("req2", "data"))
        result3 = configured_queue.add_request(Request("req3", "data"))
        
        assert result1 is True
        assert result2 is True
        assert result3 is False
    
    def test_tracks_total_requests_added(self, priority_queue: PriorityQueueManager) -> None:
        """Should track total requests added."""
        priority_queue.add_request(Request("req1", "data"))
        priority_queue.add_request(Request("req2", "data"))
        
        metrics = priority_queue.get_metrics()
        assert metrics["total_requests"] == 2


# ============================================================================
# CATEGORY 4: DEQUEUE OPERATIONS (4/4)
# ============================================================================

class TestDequeueOperations:
    """Test request dequeueing with priority ordering."""
    
    def test_dequeues_high_priority_first(self, priority_queue: PriorityQueueManager) -> None:
        """Should dequeue high priority requests first."""
        priority_queue.add_request(Request("low1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("high1", "data", PriorityLevel.HIGH))
        priority_queue.add_request(Request("normal1", "data", PriorityLevel.NORMAL))
        
        # First dequeue should be HIGH
        request = priority_queue.get_next_request()
        assert request is not None
        assert request.request_id == "high1"
    
    def test_dequeues_normal_when_no_high(self, priority_queue: PriorityQueueManager) -> None:
        """Should dequeue NORMAL when no HIGH available."""
        priority_queue.add_request(Request("low1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("normal1", "data", PriorityLevel.NORMAL))
        
        request = priority_queue.get_next_request()
        assert request is not None
        assert request.priority == PriorityLevel.NORMAL
    
    def test_dequeues_low_when_no_higher(self, priority_queue: PriorityQueueManager) -> None:
        """Should dequeue LOW when no higher priority available."""
        priority_queue.add_request(Request("low1", "data", PriorityLevel.LOW))
        
        request = priority_queue.get_next_request()
        assert request is not None
        assert request.priority == PriorityLevel.LOW
    
    def test_returns_none_when_queue_empty(self, priority_queue: PriorityQueueManager) -> None:
        """Should return None when queue is empty."""
        request = priority_queue.get_next_request()
        assert request is None


# ============================================================================
# CATEGORY 5: PRIORITY ADJUSTMENT (4/4)
# ============================================================================

class TestPriorityAdjustment:
    """Test priority boosting and adjustment."""
    
    def test_boosts_request_priority(self, priority_queue: PriorityQueueManager) -> None:
        """Should boost request priority."""
        priority_queue.add_request(Request("req1", "data", PriorityLevel.LOW))
        
        result = priority_queue.boost_priority("req1", PriorityLevel.HIGH)
        assert result is True
        
        # Should now dequeue as HIGH
        request = priority_queue.get_next_request()
        assert request is not None
        assert request.priority == PriorityLevel.HIGH
    
    def test_returns_false_when_request_not_found(
        self,
        priority_queue: PriorityQueueManager,
    ) -> None:
        """Should return False when request not in queue."""
        result = priority_queue.boost_priority("nonexistent", PriorityLevel.HIGH)
        assert result is False
    
    def test_adjusts_metrics_on_priority_boost(self, priority_queue: PriorityQueueManager) -> None:
        """Should update metrics when boosting priority."""
        priority_queue.add_request(Request("req1", "data", PriorityLevel.LOW))
        
        metrics_before = priority_queue.get_metrics()
        assert metrics_before["low_priority_count"] == 1
        assert metrics_before["high_priority_count"] == 0
        
        priority_queue.boost_priority("req1", PriorityLevel.HIGH)
        
        metrics_after = priority_queue.get_metrics()
        assert metrics_after["low_priority_count"] == 0
        assert metrics_after["high_priority_count"] == 1
    
    def test_boosts_multiple_requests(self, priority_queue: PriorityQueueManager) -> None:
        """Should boost multiple requests."""
        priority_queue.add_request(Request("req1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("req2", "data", PriorityLevel.LOW))
        
        priority_queue.boost_priority("req1", PriorityLevel.HIGH)
        priority_queue.boost_priority("req2", PriorityLevel.NORMAL)
        
        metrics = priority_queue.get_metrics()
        assert metrics["low_priority_count"] == 0
        assert metrics["high_priority_count"] == 1
        assert metrics["normal_priority_count"] == 1


# ============================================================================
# CATEGORY 6: DEGRADATION INTEGRATION (4/4)
# ============================================================================

class TestDegradationIntegration:
    """Test integration with degradation state."""
    
    def test_skips_low_priority_when_degraded(self, priority_queue: PriorityQueueManager) -> None:
        """Should skip LOW priority requests during degradation."""
        priority_queue.config.skip_low_priority_on_degradation = True
        
        priority_queue.add_request(Request("low1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("high1", "data", PriorityLevel.HIGH))
        
        # Set degraded state
        priority_queue.set_degraded(True)
        
        # Should get HIGH, not LOW
        request = priority_queue.get_next_request()
        assert request is not None
        assert request.priority == PriorityLevel.HIGH
        
        # LOW should remain in queue
        assert priority_queue.get_queue_depth(PriorityLevel.LOW) == 1
    
    def test_processes_normal_when_degraded_and_no_high(
        self,
        priority_queue: PriorityQueueManager,
    ) -> None:
        """Should process NORMAL requests when degraded and no HIGH available."""
        priority_queue.config.skip_low_priority_on_degradation = True
        
        priority_queue.add_request(Request("low1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("normal1", "data", PriorityLevel.NORMAL))
        
        priority_queue.set_degraded(True)
        
        request = priority_queue.get_next_request()
        assert request is not None
        assert request.priority == PriorityLevel.NORMAL
    
    def test_resumes_low_priority_after_recovery(self, priority_queue: PriorityQueueManager) -> None:
        """Should resume LOW priority processing after recovery."""
        priority_queue.add_request(Request("low1", "data", PriorityLevel.LOW))
        
        # Degrade
        priority_queue.set_degraded(True)
        request = priority_queue.get_next_request()
        assert request is None
        
        # Recover
        priority_queue.set_degraded(False)
        request = priority_queue.get_next_request()
        assert request is not None
        assert request.priority == PriorityLevel.LOW
    
    def test_degrades_and_recovers_state(self, priority_queue: PriorityQueueManager) -> None:
        """Should track degradation state changes."""
        assert priority_queue.is_degraded() is False
        
        priority_queue.set_degraded(True)
        assert priority_queue.is_degraded() is True
        
        priority_queue.set_degraded(False)
        assert priority_queue.is_degraded() is False


# ============================================================================
# CATEGORY 7: METRICS COLLECTION (3/3)
# ============================================================================

class TestMetricsCollection:
    """Test metrics collection and reporting."""
    
    def test_tracks_processed_requests(self, priority_queue: PriorityQueueManager) -> None:
        """Should track processed requests."""
        request = Request("req1", "data")
        priority_queue.add_request(request)
        
        priority_queue.process_request(request)
        
        metrics = priority_queue.get_metrics()
        assert metrics["processed_requests"] == 1
    
    def test_tracks_skipped_requests(self, priority_queue: PriorityQueueManager) -> None:
        """Should track skipped requests."""
        request = Request("req1", "data", PriorityLevel.LOW)
        priority_queue.add_request(request)
        
        priority_queue.skip_request(request)
        
        metrics = priority_queue.get_metrics()
        assert metrics["skipped_requests"] == 1
    
    def test_reports_queue_depth_by_priority(self, priority_queue: PriorityQueueManager) -> None:
        """Should report queue depth by priority."""
        priority_queue.add_request(Request("high1", "data", PriorityLevel.HIGH))
        priority_queue.add_request(Request("high2", "data", PriorityLevel.HIGH))
        priority_queue.add_request(Request("normal1", "data", PriorityLevel.NORMAL))
        
        metrics = priority_queue.get_metrics()
        assert metrics["high_priority_count"] == 2
        assert metrics["normal_priority_count"] == 1
        assert metrics["queue_size"] == 3


# ============================================================================
# CATEGORY 8: QUEUE OPERATIONS (3/3)
# ============================================================================

class TestQueueOperations:
    """Test queue-level operations."""
    
    def test_drains_queue_in_priority_order(self, priority_queue: PriorityQueueManager) -> None:
        """Should drain queue respecting priority order."""
        priority_queue.add_request(Request("low1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("high1", "data", PriorityLevel.HIGH))
        priority_queue.add_request(Request("normal1", "data", PriorityLevel.NORMAL))
        
        requests = priority_queue.drain_queue()
        
        # Should be in priority order: HIGH, NORMAL, LOW
        assert len(requests) == 3
        assert requests[0].priority == PriorityLevel.HIGH
        assert requests[1].priority == PriorityLevel.NORMAL
        assert requests[2].priority == PriorityLevel.LOW
    
    def test_queue_empty_after_drain(self, priority_queue: PriorityQueueManager) -> None:
        """Should empty queue after drain."""
        priority_queue.add_request(Request("req1", "data"))
        priority_queue.add_request(Request("req2", "data"))
        
        priority_queue.drain_queue()
        
        assert priority_queue.get_total_queue_depth() == 0
    
    def test_gets_total_queue_depth(self, priority_queue: PriorityQueueManager) -> None:
        """Should return total queue depth."""
        priority_queue.add_request(Request("req1", "data", PriorityLevel.HIGH))
        priority_queue.add_request(Request("req2", "data", PriorityLevel.NORMAL))
        priority_queue.add_request(Request("req3", "data", PriorityLevel.LOW))
        
        assert priority_queue.get_total_queue_depth() == 3


# ============================================================================
# CATEGORY 9: CONCURRENT OPERATIONS (2/2)
# ============================================================================

class TestConcurrentOperations:
    """Test concurrent queue operations."""
    
    def test_handles_concurrent_add_requests(
        self,
        configured_queue: PriorityQueueManager,
    ) -> None:
        """Should handle concurrent add operations."""
        results: List[bool] = []
        lock = threading.Lock()
        
        def worker(req_id: int) -> None:
            request = Request(f"req{req_id}", "data", PriorityLevel.NORMAL)
            result = configured_queue.add_request(request)
            with lock:
                results.append(result)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 10
        assert all(results)
    
    def test_thread_safe_priority_boosting(self, configured_queue: PriorityQueueManager) -> None:
        """Should safely boost priority from multiple threads."""
        for i in range(5):
            configured_queue.add_request(Request(f"req{i}", "data", PriorityLevel.LOW))
        
        def worker(req_id: int) -> None:
            configured_queue.boost_priority(f"req{req_id}", PriorityLevel.HIGH)
        
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = configured_queue.get_metrics()
        assert metrics["high_priority_count"] == 5
        assert metrics["low_priority_count"] == 0


# ============================================================================
# CATEGORY 10: INTEGRATION PATTERNS (3/3)
# ============================================================================

class TestIntegrationPatterns:
    """Test integration with other resilience patterns."""
    
    def test_integrates_with_graceful_degradation(
        self,
        priority_queue: PriorityQueueManager,
    ) -> None:
        """Should integrate with graceful degradation."""
        # Add mixed priority requests
        priority_queue.add_request(Request("critical", "data", PriorityLevel.HIGH))
        priority_queue.add_request(Request("normal", "data", PriorityLevel.NORMAL))
        priority_queue.add_request(Request("background", "data", PriorityLevel.LOW))
        
        # Simulate degradation
        priority_queue.set_degraded(True)
        
        # Skip LOW priority
        priority_queue.get_next_request()  # Get HIGH
        priority_queue.get_next_request()  # Get NORMAL
        
        # LOW should be skipped
        request = priority_queue.get_next_request()
        assert request is None
    
    def test_coordinates_priority_during_recovery(self, priority_queue: PriorityQueueManager) -> None:
        """Should coordinate priority changes during recovery."""
        # Add requests during degradation
        priority_queue.set_degraded(True)
        priority_queue.add_request(Request("req1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("req2", "data", PriorityLevel.NORMAL))
        
        # Recover
        priority_queue.set_degraded(False)
        
        # Now process normally
        req = priority_queue.get_next_request()
        assert req is not None
    
    def test_handles_cascading_priority_adjustments(
        self,
        priority_queue: PriorityQueueManager,
    ) -> None:
        """Should handle cascading priority adjustments."""
        # Add requests
        priority_queue.add_request(Request("req1", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("req2", "data", PriorityLevel.LOW))
        priority_queue.add_request(Request("req3", "data", PriorityLevel.NORMAL))
        
        # Boost all LOWs to NORMAL
        priority_queue.boost_priority("req1", PriorityLevel.NORMAL)
        priority_queue.boost_priority("req2", PriorityLevel.NORMAL)
        
        metrics = priority_queue.get_metrics()
        assert metrics["normal_priority_count"] == 3
        assert metrics["low_priority_count"] == 0
