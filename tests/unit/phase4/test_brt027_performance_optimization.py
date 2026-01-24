"""
BRT-027: Performance Optimization

Implements performance optimization strategies and caching mechanisms
for resilience patterns.

Test Infrastructure (RED phase - Tests Before Implementation per CORE-008)
"""

import pytest
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Tuple
from threading import Lock
import time
from enum import Enum
from collections import OrderedDict


class CacheEvictionPolicy(Enum):
    """Cache eviction policies."""
    LRU = "lru"  # Least Recently Used
    FIFO = "fifo"  # First In First Out
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live


@dataclass
class CacheEntry:
    """Cache entry."""
    key: str
    value: Any
    created_at_ms: float = field(default_factory=lambda: time.time() * 1000)
    last_accessed_ms: float = field(default_factory=lambda: time.time() * 1000)
    access_count: int = 0
    ttl_ms: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_ms is None:
            return False
        
        return time.time() * 1000 - self.created_at_ms > self.ttl_ms


class Cache:
    """Generic cache with configurable eviction policies."""
    
    def __init__(
        self,
        max_size: int = 1000,
        eviction_policy: CacheEvictionPolicy = CacheEvictionPolicy.LRU
    ):
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                return None
            
            # Update access info
            entry.last_accessed_ms = time.time() * 1000
            entry.access_count += 1
            
            return entry.value
    
    def put(self, key: str, value: Any, ttl_ms: Optional[int] = None) -> bool:
        """Put value in cache."""
        with self._lock:
            if len(self._cache) >= self.max_size:
                self._evict_one()
            
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_ms=ttl_ms
            )
            self._cache[key] = entry
            return True
    
    def remove(self, key: str) -> bool:
        """Remove value from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> int:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count
    
    def get_size(self) -> int:
        """Get current cache size."""
        with self._lock:
            return len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_accesses = sum(e.access_count for e in self._cache.values())
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "total_accesses": total_accesses,
                "entries": len(self._cache)
            }
    
    def _evict_one(self):
        """Evict one entry based on policy."""
        if not self._cache:
            return
        
        if self.eviction_policy == CacheEvictionPolicy.LRU:
            # Remove least recently used
            lru_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].last_accessed_ms
            )
            del self._cache[lru_key]
        
        elif self.eviction_policy == CacheEvictionPolicy.FIFO:
            # Remove oldest
            oldest_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].created_at_ms
            )
            del self._cache[oldest_key]
        
        elif self.eviction_policy == CacheEvictionPolicy.LFU:
            # Remove least frequently used
            lfu_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].access_count
            )
            del self._cache[lfu_key]
        
        elif self.eviction_policy == CacheEvictionPolicy.TTL:
            # Remove expired entries, or oldest if none expired
            expired = [k for k, v in self._cache.items() if v.is_expired()]
            if expired:
                del self._cache[expired[0]]
            else:
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k].created_at_ms
                )
                del self._cache[oldest_key]


class QueryOptimizer:
    """Optimizes query patterns."""
    
    def __init__(self, cache: Cache):
        self.cache = cache
        self._query_patterns: Dict[str, int] = {}
        self._lock = Lock()
    
    def record_query(self, query: str) -> None:
        """Record query pattern."""
        with self._lock:
            self._query_patterns[query] = self._query_patterns.get(query, 0) + 1
    
    def get_frequent_queries(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get most frequent queries."""
        with self._lock:
            return sorted(
                self._query_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]
    
    def suggest_caching(self) -> List[str]:
        """Suggest queries to cache."""
        frequent = self.get_frequent_queries(5)
        return [q for q, count in frequent if count > 5]


class ConnectionPoolOptimizer:
    """Optimizes connection pool usage."""
    
    def __init__(self, max_pool_size: int = 100):
        self.max_pool_size = max_pool_size
        self._idle_connections = 0
        self._active_connections = 0
        self._lock = Lock()
    
    def acquire_connection(self) -> bool:
        """Acquire connection."""
        with self._lock:
            if self._active_connections >= self.max_pool_size:
                return False
            
            self._active_connections += 1
            return True
    
    def release_connection(self) -> bool:
        """Release connection."""
        with self._lock:
            if self._active_connections > 0:
                self._active_connections -= 1
                self._idle_connections += 1
                return True
            return False
    
    def get_utilization(self) -> float:
        """Get pool utilization percentage."""
        with self._lock:
            total = self._active_connections + self._idle_connections
            if total == 0:
                return 0.0
            return (self._active_connections / total) * 100
    
    def get_idle_connections(self) -> int:
        """Get number of idle connections."""
        with self._lock:
            return self._idle_connections


class BatchProcessor:
    """Processes operations in batches for efficiency."""
    
    def __init__(self, batch_size: int = 100, timeout_ms: int = 5000):
        self.batch_size = batch_size
        self.timeout_ms = timeout_ms
        self._batch: List[Any] = []
        self._last_flush_ms = time.time() * 1000
        self._lock = Lock()
    
    def add(self, item: Any) -> bool:
        """Add item to batch."""
        with self._lock:
            self._batch.append(item)
            
            if len(self._batch) >= self.batch_size:
                return True  # Ready to flush
            
            now = time.time() * 1000
            if now - self._last_flush_ms > self.timeout_ms:
                return True  # Timeout reached
            
            return False
    
    def flush(self) -> List[Any]:
        """Flush batch."""
        with self._lock:
            batch = self._batch.copy()
            self._batch.clear()
            self._last_flush_ms = time.time() * 1000
            return batch
    
    def get_batch_size(self) -> int:
        """Get current batch size."""
        with self._lock:
            return len(self._batch)


class PerformanceMonitor:
    """Monitors performance metrics."""
    
    def __init__(self):
        self._operation_times: Dict[str, List[float]] = {}
        self._lock = Lock()
    
    def record_operation(self, operation_name: str, duration_ms: float) -> None:
        """Record operation timing."""
        with self._lock:
            if operation_name not in self._operation_times:
                self._operation_times[operation_name] = []
            
            self._operation_times[operation_name].append(duration_ms)
    
    def get_avg_duration(self, operation_name: str) -> Optional[float]:
        """Get average operation duration."""
        with self._lock:
            times = self._operation_times.get(operation_name)
            if not times:
                return None
            return sum(times) / len(times)
    
    def get_p95_duration(self, operation_name: str) -> Optional[float]:
        """Get 95th percentile duration."""
        with self._lock:
            times = self._operation_times.get(operation_name)
            if not times or len(times) < 20:
                return None
            
            sorted_times = sorted(times)
            idx = int(len(sorted_times) * 0.95)
            return sorted_times[idx]
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get stats for all operations."""
        with self._lock:
            stats = {}
            for op_name, times in self._operation_times.items():
                if times:
                    stats[op_name] = {
                        "avg": sum(times) / len(times),
                        "min": min(times),
                        "max": max(times),
                        "count": len(times)
                    }
            return stats


class ResourceOptimizer:
    """Optimizes resource usage."""
    
    def __init__(self):
        self._memory_usage = 0
        self._cpu_usage = 0
        self._resource_allocations: Dict[str, int] = {}
        self._lock = Lock()
    
    def allocate_resource(self, resource_type: str, amount: int) -> bool:
        """Allocate resource."""
        with self._lock:
            current = self._resource_allocations.get(resource_type, 0)
            self._resource_allocations[resource_type] = current + amount
            return True
    
    def deallocate_resource(self, resource_type: str, amount: int) -> bool:
        """Deallocate resource."""
        with self._lock:
            current = self._resource_allocations.get(resource_type, 0)
            if current < amount:
                return False
            
            self._resource_allocations[resource_type] = current - amount
            return True
    
    def get_resource_usage(self, resource_type: str) -> int:
        """Get resource usage."""
        with self._lock:
            return self._resource_allocations.get(resource_type, 0)
    
    def get_all_allocations(self) -> Dict[str, int]:
        """Get all resource allocations."""
        with self._lock:
            return self._resource_allocations.copy()


# ============================================================================
# TEST SUITE
# ============================================================================

class TestCache:
    """Test Cache functionality."""
    
    def test_cache_get_put(self):
        """Test cache get/put operations."""
        cache = Cache(max_size=100)
        
        cache.put("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = Cache()
        assert cache.get("nonexistent") is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction."""
        cache = Cache(max_size=2, eviction_policy=CacheEvictionPolicy.LRU)
        
        cache.put("key1", "value1")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        cache.put("key2", "value2")
        
        # Access key1 to make it recently used
        time.sleep(0.01)
        cache.get("key1")
        
        # Add key3, should evict key2 (least recently used)
        cache.put("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"
    
    def test_cache_fifo_eviction(self):
        """Test FIFO eviction."""
        cache = Cache(max_size=2, eviction_policy=CacheEvictionPolicy.FIFO)
        
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # key1 should be evicted (first in)
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_cache_ttl_expiration(self):
        """Test TTL expiration."""
        cache = Cache(eviction_policy=CacheEvictionPolicy.TTL)
        
        cache.put("key1", "value1", ttl_ms=100)
        assert cache.get("key1") == "value1"
        
        time.sleep(0.15)
        assert cache.get("key1") is None
    
    def test_cache_remove(self):
        """Test cache remove."""
        cache = Cache()
        cache.put("key1", "value1")
        
        assert cache.remove("key1")
        assert cache.get("key1") is None
    
    def test_cache_clear(self):
        """Test cache clear."""
        cache = Cache()
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        
        cleared = cache.clear()
        assert cleared == 2
        assert cache.get_size() == 0
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = Cache(max_size=100)
        cache.put("key1", "value1")
        cache.get("key1")
        cache.get("key1")
        
        stats = cache.get_stats()
        assert stats["entries"] == 1
        assert stats["total_accesses"] == 2


class TestQueryOptimizer:
    """Test QueryOptimizer functionality."""
    
    def test_record_query(self):
        """Test recording queries."""
        cache = Cache()
        optimizer = QueryOptimizer(cache)
        
        optimizer.record_query("SELECT * FROM users")
        optimizer.record_query("SELECT * FROM users")
        optimizer.record_query("SELECT * FROM orders")
        
        frequent = optimizer.get_frequent_queries()
        assert frequent[0][0] == "SELECT * FROM users"
        assert frequent[0][1] == 2
    
    def test_suggest_caching(self):
        """Test suggesting queries to cache."""
        cache = Cache()
        optimizer = QueryOptimizer(cache)
        
        for _ in range(10):
            optimizer.record_query("SELECT * FROM users")
        
        suggestions = optimizer.suggest_caching()
        assert "SELECT * FROM users" in suggestions


class TestConnectionPoolOptimizer:
    """Test ConnectionPoolOptimizer functionality."""
    
    def test_acquire_release(self):
        """Test acquiring and releasing connections."""
        optimizer = ConnectionPoolOptimizer(max_pool_size=10)
        
        assert optimizer.acquire_connection()
        assert optimizer.acquire_connection()
        assert optimizer.get_utilization() > 0
        
        assert optimizer.release_connection()
        assert optimizer.release_connection()
    
    def test_pool_exhaustion(self):
        """Test pool exhaustion."""
        optimizer = ConnectionPoolOptimizer(max_pool_size=2)
        
        assert optimizer.acquire_connection()
        assert optimizer.acquire_connection()
        assert not optimizer.acquire_connection()
    
    def test_utilization_calculation(self):
        """Test utilization calculation."""
        optimizer = ConnectionPoolOptimizer(max_pool_size=10)
        
        optimizer.acquire_connection()
        optimizer.acquire_connection()
        utilization = optimizer.get_utilization()
        
        assert 0 < utilization <= 100


class TestBatchProcessor:
    """Test BatchProcessor functionality."""
    
    def test_add_item(self):
        """Test adding items to batch."""
        processor = BatchProcessor(batch_size=3)
        
        assert not processor.add("item1")
        assert not processor.add("item2")
        assert processor.add("item3")
    
    def test_flush(self):
        """Test flushing batch."""
        processor = BatchProcessor(batch_size=5)
        
        processor.add("item1")
        processor.add("item2")
        
        batch = processor.flush()
        assert len(batch) == 2
        assert processor.get_batch_size() == 0
    
    def test_batch_timeout(self):
        """Test batch timeout."""
        processor = BatchProcessor(batch_size=100, timeout_ms=100)
        
        processor.add("item1")
        time.sleep(0.15)
        
        # Should be ready to flush due to timeout
        ready = processor.add("item2")
        assert ready


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""
    
    def test_record_operation(self):
        """Test recording operations."""
        monitor = PerformanceMonitor()
        
        monitor.record_operation("query", 100)
        monitor.record_operation("query", 150)
        monitor.record_operation("query", 200)
        
        avg = monitor.get_avg_duration("query")
        assert avg == 150
    
    def test_get_all_stats(self):
        """Test getting all stats."""
        monitor = PerformanceMonitor()
        
        monitor.record_operation("read", 50)
        monitor.record_operation("write", 100)
        
        stats = monitor.get_all_stats()
        assert "read" in stats
        assert "write" in stats


class TestResourceOptimizer:
    """Test ResourceOptimizer functionality."""
    
    def test_allocate_deallocate(self):
        """Test allocating and deallocating resources."""
        optimizer = ResourceOptimizer()
        
        assert optimizer.allocate_resource("memory", 100)
        assert optimizer.get_resource_usage("memory") == 100
        
        assert optimizer.deallocate_resource("memory", 50)
        assert optimizer.get_resource_usage("memory") == 50
    
    def test_deallocate_too_much(self):
        """Test deallocating too much."""
        optimizer = ResourceOptimizer()
        
        optimizer.allocate_resource("memory", 100)
        assert not optimizer.deallocate_resource("memory", 200)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
