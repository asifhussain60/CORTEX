"""
CORTEX 3.0 Phase 2 - Intelligent Query Cache
============================================

High-performance caching layer for brain queries with adaptive intelligence.
Optimizes query response times through smart caching strategies.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Brain Performance Optimization (Task 2)
Integration: Query Cache + Performance Engine + Brain Tiers
"""

import time
import hashlib
import json
import threading
from typing import Dict, Any, Optional, List, Tuple, NamedTuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import OrderedDict
import pickle
import logging
from enum import Enum
from pathlib import Path


class CacheStrategy(Enum):
    """Cache strategy types."""
    LRU = "lru"              # Least Recently Used
    LFU = "lfu"              # Least Frequently Used  
    TTL = "ttl"              # Time To Live
    ADAPTIVE = "adaptive"    # Adaptive based on query patterns


class QueryType(Enum):
    """Query type classification."""
    TIER1_CONVERSATION = "tier1_conversation"
    TIER2_PATTERN = "tier2_pattern"
    TIER3_CONTEXT = "tier3_context"
    BRAIN_HEALTH = "brain_health"
    GENERAL = "general"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    query_type: QueryType
    timestamp: datetime
    access_count: int
    last_accessed: datetime
    size_bytes: int
    ttl_seconds: int
    performance_impact: float  # Query time saved


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    hits: int
    misses: int
    hit_rate: float
    total_requests: int
    average_response_time_ms: float
    memory_usage_mb: float
    entries_count: int
    evictions: int


class QueryCacheEngine:
    """
    Intelligent query cache with adaptive strategies.
    
    Features:
    - Multi-strategy caching (LRU, LFU, TTL, Adaptive)
    - Query type-specific optimization
    - Memory-aware eviction
    - Performance monitoring
    - Thread-safe operations
    """
    
    def __init__(self, max_size_mb: int = 50, strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        """
        Initialize query cache.
        
        Args:
            max_size_mb: Maximum cache size in MB
            strategy: Caching strategy to use
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.strategy = strategy
        
        # Cache storage
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        
        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.total_response_time = 0.0
        self.total_requests = 0
        
        # Strategy-specific data
        self.frequency_map: Dict[str, int] = {}
        self.query_patterns: Dict[QueryType, Dict[str, Any]] = {}
        
        # TTL settings per query type
        self.default_ttl = {
            QueryType.TIER1_CONVERSATION: 300,  # 5 minutes
            QueryType.TIER2_PATTERN: 1800,      # 30 minutes  
            QueryType.TIER3_CONTEXT: 900,       # 15 minutes
            QueryType.BRAIN_HEALTH: 60,         # 1 minute
            QueryType.GENERAL: 600               # 10 minutes
        }
        
        # Size tracking
        self.current_size_bytes = 0
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"Query cache initialized: {max_size_mb}MB, strategy={strategy.value}")
    
    def get(self, query: str, query_type: QueryType = QueryType.GENERAL) -> Optional[Any]:
        """
        Get cached query result.
        
        Args:
            query: Query string
            query_type: Type of query for optimization
            
        Returns:
            Cached result or None if not found
        """
        cache_key = self._generate_cache_key(query, query_type)
        
        with self.lock:
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                # Check TTL expiration
                if self._is_expired(entry):
                    self._remove_entry(cache_key)
                    self.misses += 1
                    return None
                
                # Update access metadata
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                # Move to end for LRU
                if self.strategy in [CacheStrategy.LRU, CacheStrategy.ADAPTIVE]:
                    self.cache.move_to_end(cache_key)
                
                # Update frequency map
                self.frequency_map[cache_key] = entry.access_count
                
                self.hits += 1
                return entry.value
            else:
                self.misses += 1
                return None
    
    def put(self, query: str, result: Any, query_type: QueryType = QueryType.GENERAL,
            execution_time_ms: float = 0.0) -> bool:
        """
        Cache query result.
        
        Args:
            query: Query string
            result: Query result to cache
            query_type: Type of query
            execution_time_ms: Original query execution time
            
        Returns:
            True if cached successfully
        """
        cache_key = self._generate_cache_key(query, query_type)
        
        # Calculate entry size
        size_bytes = self._calculate_size(result)
        
        # Don't cache if too large (>10% of total cache)
        if size_bytes > self.max_size_bytes * 0.1:
            self.logger.warning(f"Query result too large to cache: {size_bytes} bytes")
            return False
        
        with self.lock:
            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                value=result,
                query_type=query_type,
                timestamp=datetime.now(),
                access_count=1,
                last_accessed=datetime.now(),
                size_bytes=size_bytes,
                ttl_seconds=self.default_ttl.get(query_type, 600),
                performance_impact=execution_time_ms
            )
            
            # Remove if already exists
            if cache_key in self.cache:
                self._remove_entry(cache_key)
            
            # Make room if needed
            while (self.current_size_bytes + size_bytes > self.max_size_bytes and 
                   len(self.cache) > 0):
                if not self._evict_entry():
                    break  # Could not evict anything
            
            # Add new entry
            self.cache[cache_key] = entry
            self.current_size_bytes += size_bytes
            self.frequency_map[cache_key] = 1
            
            # Update query patterns for adaptive strategy
            self._update_query_patterns(query_type, query, execution_time_ms)
            
            return True
    
    def invalidate(self, query: str = None, query_type: QueryType = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            query: Specific query to invalidate (optional)
            query_type: Query type to invalidate (optional)
            
        Returns:
            Number of entries invalidated
        """
        invalidated = 0
        
        with self.lock:
            if query:
                # Invalidate specific query
                cache_key = self._generate_cache_key(query, query_type or QueryType.GENERAL)
                if cache_key in self.cache:
                    self._remove_entry(cache_key)
                    invalidated = 1
            elif query_type:
                # Invalidate all entries of specific type
                to_remove = [
                    key for key, entry in self.cache.items()
                    if entry.query_type == query_type
                ]
                for key in to_remove:
                    self._remove_entry(key)
                    invalidated += 1
            else:
                # Invalidate all
                invalidated = len(self.cache)
                self.cache.clear()
                self.frequency_map.clear()
                self.current_size_bytes = 0
        
        self.logger.info(f"Invalidated {invalidated} cache entries")
        return invalidated
    
    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        removed = 0
        
        with self.lock:
            to_remove = [
                key for key, entry in self.cache.items()
                if self._is_expired(entry)
            ]
            
            for key in to_remove:
                self._remove_entry(key)
                removed += 1
        
        if removed > 0:
            self.logger.info(f"Cleaned up {removed} expired cache entries")
        
        return removed
    
    def get_metrics(self) -> CacheMetrics:
        """Get cache performance metrics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / max(total_requests, 1)
            avg_response_time = self.total_response_time / max(total_requests, 1)
            memory_usage_mb = self.current_size_bytes / (1024 * 1024)
            
            return CacheMetrics(
                hits=self.hits,
                misses=self.misses,
                hit_rate=hit_rate,
                total_requests=total_requests,
                average_response_time_ms=avg_response_time,
                memory_usage_mb=memory_usage_mb,
                entries_count=len(self.cache),
                evictions=self.evictions
            )
    
    def get_top_queries(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed queries."""
        with self.lock:
            sorted_queries = sorted(
                self.frequency_map.items(),
                key=lambda x: x[1],
                reverse=True
            )
            return sorted_queries[:limit]
    
    def optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance."""
        optimizations = []
        
        with self.lock:
            # Clean up expired entries
            expired_cleaned = self.cleanup_expired()
            if expired_cleaned > 0:
                optimizations.append(f"Cleaned {expired_cleaned} expired entries")
            
            # Analyze cache efficiency
            metrics = self.get_metrics()
            
            # Adjust strategy if needed
            if metrics.hit_rate < 0.6:  # Low hit rate
                if self.strategy == CacheStrategy.LRU:
                    # Consider switching to LFU for better hit rate
                    optimizations.append("Consider LFU strategy for better hit rate")
                elif self.strategy == CacheStrategy.TTL:
                    # Increase TTL for better retention
                    for query_type in self.default_ttl:
                        self.default_ttl[query_type] = int(self.default_ttl[query_type] * 1.2)
                    optimizations.append("Increased TTL for better retention")
            
            # Memory optimization
            if metrics.memory_usage_mb > self.max_size_bytes * 0.9 / (1024 * 1024):
                # Aggressive eviction for memory pressure
                evicted = 0
                target_size = self.max_size_bytes * 0.7
                
                while self.current_size_bytes > target_size and len(self.cache) > 10:
                    if not self._evict_entry():
                        break
                    evicted += 1
                
                if evicted > 0:
                    optimizations.append(f"Evicted {evicted} entries for memory pressure")
            
            # Pattern analysis for adaptive optimization
            if self.strategy == CacheStrategy.ADAPTIVE:
                self._optimize_adaptive_strategy()
                optimizations.append("Optimized adaptive caching patterns")
        
        return {
            'optimizations_applied': optimizations,
            'cache_metrics': asdict(self.get_metrics()),
            'query_patterns': dict(self.query_patterns)
        }
    
    def _generate_cache_key(self, query: str, query_type: QueryType) -> str:
        """Generate cache key for query."""
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Create key with query type prefix
        key_data = f"{query_type.value}:{normalized_query}"
        
        # Hash for consistent key length
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _calculate_size(self, obj: Any) -> int:
        """Calculate object size in bytes."""
        try:
            return len(pickle.dumps(obj))
        except Exception:
            # Fallback estimation
            if isinstance(obj, str):
                return len(obj.encode('utf-8'))
            elif isinstance(obj, dict):
                return sum(len(str(k)) + len(str(v)) for k, v in obj.items())
            elif isinstance(obj, list):
                return sum(len(str(item)) for item in obj)
            else:
                return len(str(obj).encode('utf-8'))
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if entry.ttl_seconds <= 0:
            return False  # No expiration
        
        age_seconds = (datetime.now() - entry.timestamp).total_seconds()
        return age_seconds > entry.ttl_seconds
    
    def _remove_entry(self, key: str) -> None:
        """Remove entry from cache."""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size_bytes -= entry.size_bytes
            del self.cache[key]
            
        if key in self.frequency_map:
            del self.frequency_map[key]
    
    def _evict_entry(self) -> bool:
        """Evict one entry based on strategy."""
        if not self.cache:
            return False
        
        key_to_evict = None
        
        if self.strategy == CacheStrategy.LRU:
            # Evict least recently used (first in OrderedDict)
            key_to_evict = next(iter(self.cache))
        
        elif self.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            min_frequency = min(self.frequency_map.values())
            for key, freq in self.frequency_map.items():
                if freq == min_frequency:
                    key_to_evict = key
                    break
        
        elif self.strategy == CacheStrategy.TTL:
            # Evict oldest entry
            oldest_key = None
            oldest_time = datetime.now()
            for key, entry in self.cache.items():
                if entry.timestamp < oldest_time:
                    oldest_time = entry.timestamp
                    oldest_key = key
            key_to_evict = oldest_key
        
        elif self.strategy == CacheStrategy.ADAPTIVE:
            # Evict based on adaptive scoring
            key_to_evict = self._get_adaptive_eviction_candidate()
        
        if key_to_evict:
            self._remove_entry(key_to_evict)
            self.evictions += 1
            return True
        
        return False
    
    def _get_adaptive_eviction_candidate(self) -> Optional[str]:
        """Get best eviction candidate using adaptive strategy."""
        if not self.cache:
            return None
        
        # Score each entry for eviction (lower score = better candidate)
        scores = {}
        
        for key, entry in self.cache.items():
            score = 0.0
            
            # Age factor (older = higher score)
            age_hours = (datetime.now() - entry.timestamp).total_seconds() / 3600
            score += age_hours * 0.1
            
            # Frequency factor (less frequent = higher score)  
            max_frequency = max(self.frequency_map.values()) if self.frequency_map else 1
            frequency_ratio = entry.access_count / max_frequency
            score += (1.0 - frequency_ratio) * 0.4
            
            # Size factor (larger = higher score)
            max_size = max(e.size_bytes for e in self.cache.values())
            size_ratio = entry.size_bytes / max(max_size, 1)
            score += size_ratio * 0.2
            
            # Performance impact factor (higher impact = lower score)
            if entry.performance_impact > 0:
                score -= (entry.performance_impact / 100) * 0.3
            
            scores[key] = score
        
        # Return key with highest score (best eviction candidate)
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def _update_query_patterns(self, query_type: QueryType, query: str, execution_time_ms: float):
        """Update query patterns for adaptive optimization."""
        if query_type not in self.query_patterns:
            self.query_patterns[query_type] = {
                'total_queries': 0,
                'avg_execution_time': 0.0,
                'common_patterns': set(),
                'performance_threshold': 100.0  # Cache queries taking longer than this
            }
        
        pattern_data = self.query_patterns[query_type]
        
        # Update averages
        pattern_data['total_queries'] += 1
        pattern_data['avg_execution_time'] = (
            (pattern_data['avg_execution_time'] * (pattern_data['total_queries'] - 1) + execution_time_ms) /
            pattern_data['total_queries']
        )
        
        # Extract common patterns (simple keyword analysis)
        words = query.lower().split()
        if len(words) > 0:
            pattern_data['common_patterns'].add(words[0])  # First word as pattern
        
        # Adjust performance threshold
        if execution_time_ms > pattern_data['avg_execution_time'] * 1.5:
            pattern_data['performance_threshold'] = min(
                pattern_data['performance_threshold'],
                execution_time_ms * 0.8
            )
    
    def _optimize_adaptive_strategy(self):
        """Optimize adaptive caching strategy based on patterns."""
        for query_type, pattern_data in self.query_patterns.items():
            # Adjust TTL based on query frequency
            if pattern_data['total_queries'] > 100:  # Enough data
                if pattern_data['avg_execution_time'] > 50:  # Slow queries
                    # Increase TTL for expensive queries
                    self.default_ttl[query_type] = int(self.default_ttl[query_type] * 1.5)
                elif pattern_data['avg_execution_time'] < 10:  # Fast queries
                    # Decrease TTL for quick queries
                    self.default_ttl[query_type] = max(60, int(self.default_ttl[query_type] * 0.7))


class SmartQueryCache:
    """
    High-level interface for smart query caching.
    
    Features:
    - Automatic cache key generation
    - Query type detection
    - Performance monitoring
    - Integration with optimization engine
    """
    
    def __init__(self, cache_size_mb: int = 50):
        """Initialize smart query cache."""
        self.cache_engine = QueryCacheEngine(cache_size_mb, CacheStrategy.ADAPTIVE)
        self.query_classifier = self._build_query_classifier()
        
    def cached_query(self, query: str, execute_func, *args, **kwargs) -> Any:
        """
        Execute query with intelligent caching.
        
        Args:
            query: Query string
            execute_func: Function to execute if not cached
            *args, **kwargs: Arguments for execute_func
            
        Returns:
            Query result (cached or fresh)
        """
        # Classify query type
        query_type = self._classify_query(query)
        
        # Try cache first
        cached_result = self.cache_engine.get(query, query_type)
        if cached_result is not None:
            return cached_result
        
        # Execute and cache
        start_time = time.time()
        result = execute_func(*args, **kwargs)
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Cache result
        self.cache_engine.put(query, result, query_type, execution_time_ms)
        
        return result
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify query type for optimal caching."""
        query_lower = query.lower()
        
        # CORTEX brain health queries
        if any(term in query_lower for term in ['brain', 'health', 'tier', 'status', 'cortex']):
            return QueryType.BRAIN_HEALTH
        
        # Conversation queries
        elif any(term in query_lower for term in ['conversation', 'message', 'chat', 'talk']):
            return QueryType.TIER1_CONVERSATION
        
        # Pattern/knowledge graph queries
        elif any(term in query_lower for term in ['pattern', 'relationship', 'knowledge', 'graph']):
            return QueryType.TIER2_PATTERN
        
        # Development context queries
        elif any(term in query_lower for term in ['context', 'development', 'code', 'file', 'project']):
            return QueryType.TIER3_CONTEXT
        
        # Default
        else:
            return QueryType.GENERAL
    
    def _build_query_classifier(self) -> Dict[str, QueryType]:
        """Build query classification patterns."""
        return {
            'brain_patterns': [
                'cortex', 'brain', 'tier', 'health', 'status', 'performance',
                'optimization', 'memory', 'cache', 'system'
            ],
            'conversation_patterns': [
                'conversation', 'message', 'chat', 'talk', 'discuss', 'history',
                'recent', 'last', 'previous'
            ],
            'pattern_patterns': [
                'pattern', 'relationship', 'knowledge', 'graph', 'connection',
                'link', 'network', 'semantic', 'similarity'
            ],
            'context_patterns': [
                'context', 'development', 'code', 'file', 'project', 'workspace',
                'implementation', 'technical', 'programming'
            ]
        }
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        metrics = self.cache_engine.get_metrics()
        top_queries = self.cache_engine.get_top_queries(5)
        
        return {
            'performance_metrics': asdict(metrics),
            'top_queries': top_queries,
            'optimization_status': self.cache_engine.optimize_cache()
        }


if __name__ == "__main__":
    # Test the query cache system
    print("🚀 CORTEX 3.0 Phase 2 - Query Cache System Test")
    print("=" * 60)
    
    # Initialize cache
    cache = SmartQueryCache(cache_size_mb=10)
    
    # Mock query function
    def mock_brain_query(query: str, tier: str = "tier1"):
        """Mock brain query with simulated delay."""
        time.sleep(0.05)  # Simulate 50ms query
        return {
            'query': query,
            'tier': tier,
            'timestamp': datetime.now().isoformat(),
            'results': [f"Result {i} for '{query}'" for i in range(3)]
        }
    
    # Test caching
    test_queries = [
        "CORTEX brain health status",
        "Show recent conversations", 
        "Find pattern relationships",
        "Get development context",
        "CORTEX brain health status",  # Duplicate
        "Show recent conversations"    # Duplicate
    ]
    
    print("\n1. Testing Query Caching:")
    for query in test_queries:
        start_time = time.time()
        result = cache.cached_query(query, mock_brain_query, query, "tier1")
        response_time = (time.time() - start_time) * 1000
        
        print(f"   Query: '{query[:30]}...'")
        print(f"   Response Time: {response_time:.1f}ms")
        print(f"   Results: {len(result['results'])} items")
        print()
    
    # Get cache statistics
    print("2. Cache Performance Statistics:")
    stats = cache.get_cache_stats()
    metrics = stats['performance_metrics']
    
    print(f"   Hit Rate: {metrics['hit_rate']*100:.1f}%")
    print(f"   Total Requests: {metrics['total_requests']}")
    print(f"   Memory Usage: {metrics['memory_usage_mb']:.1f}MB")
    print(f"   Cache Entries: {metrics['entries_count']}")
    
    print("\n3. Top Cached Queries:")
    for i, (query_hash, frequency) in enumerate(stats['top_queries'], 1):
        print(f"   {i}. {query_hash[:12]}... (accessed {frequency} times)")
    
    print("\n✅ Query Cache System Test Complete!")
    print("🎯 Ready for integration with Brain Optimization Engine")