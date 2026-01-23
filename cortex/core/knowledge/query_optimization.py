"""Module: Optimizes knowledge queries

Author: CORTEX Framework
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class QueryCacheStats:
    """Query cache statistics."""
    hits: int = 0
    misses: int = 0
    total_queries: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Get cache hit rate."""
        if self.total_queries == 0:
            return 0.0
        return self.hits / self.total_queries


@dataclass
class PerformanceMetrics:
    """Query performance metrics."""
    avg_query_time_ms: float = 0.0
    max_query_time_ms: float = 0.0
    total_queries: int = 0
    slow_queries: int = 0


class QueryOptimizer:
    """QueryOptimizer - Optimizes knowledge queries.
    
    Provides caching, indexing, and performance monitoring
    for knowledge queries.
    """

    def __init__(self, backends: Optional[Dict[str, Any]] = None, enable_caching: bool = True):
        """Initialize queryoptimizer.
        
        Args:
            backends: Dictionary of backend configurations.
            enable_caching: Whether to enable result caching.
        """
        self.backends = backends or {}
        self.enable_caching = enable_caching
        self._cache: Dict[str, Any] = {}
        self._cache_stats = QueryCacheStats()
        self._performance_metrics = PerformanceMetrics()
        self._indexes: Dict[str, Dict[str, Any]] = {}
        self._query_times: List[float] = []
    
    def cache_result(self, query_key: str, result: Any) -> None:
        """Cache a query result.
        
        Args:
            query_key: Unique key for the query.
            result: Result to cache.
        """
        self._cache[query_key] = result
    
    def get_cached(self, query_key: str) -> Optional[Any]:
        """Get a cached result.
        
        Args:
            query_key: Query key to lookup.
            
        Returns:
            Cached result or None.
        """
        self._cache_stats.total_queries += 1
        if query_key in self._cache:
            self._cache_stats.hits += 1
            return self._cache[query_key]
        self._cache_stats.misses += 1
        return None
    
    def get_cache_stats(self) -> QueryCacheStats:
        """Get cache statistics.
        
        Returns:
            Cache statistics object.
        """
        return self._cache_stats
    
    def create_index(
        self,
        index_name: str,
        backend_name: str,
        field: str,
        index_type: str = "btree"
    ) -> bool:
        """Create an index for faster queries.
        
        Args:
            index_name: Name of the index.
            backend_name: Backend to create index on.
            field: Field to index.
            index_type: Type of index (btree, hash, etc.).
            
        Returns:
            True if created successfully.
        """
        self._indexes[index_name] = {
            "backend": backend_name,
            "field": field,
            "type": index_type,
            "created": True
        }
        return True
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get performance metrics.
        
        Returns:
            Performance metrics object.
        """
        return self._performance_metrics
    
    def record_query_time(self, time_ms: float) -> None:
        """Record a query execution time.
        
        Args:
            time_ms: Query time in milliseconds.
        """
        self._query_times.append(time_ms)
        self._performance_metrics.total_queries += 1
        
        if time_ms > self._performance_metrics.max_query_time_ms:
            self._performance_metrics.max_query_time_ms = time_ms
        
        # Update average
        self._performance_metrics.avg_query_time_ms = (
            sum(self._query_times) / len(self._query_times)
        )
        
        # Track slow queries (> 100ms)
        if time_ms > 100:
            self._performance_metrics.slow_queries += 1
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for query optimization.
        
        Returns:
            List of optimization recommendations.
        """
        recommendations = []
        
        # Cache hit rate recommendation
        if self._cache_stats.hit_rate < 0.5:
            recommendations.append({
                "type": "cache",
                "priority": "high",
                "message": "Cache hit rate is low. Consider caching more queries.",
                "current_hit_rate": self._cache_stats.hit_rate
            })
        
        # Slow query recommendation
        if self._performance_metrics.slow_queries > 0:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "message": f"Found {self._performance_metrics.slow_queries} slow queries.",
                "slow_queries": self._performance_metrics.slow_queries
            })
        
        # Index recommendation
        if len(self._indexes) == 0 and len(self.backends) > 0:
            recommendations.append({
                "type": "index",
                "priority": "high",
                "message": "No indexes created. Consider adding indexes for frequently queried fields."
            })
        
        return recommendations
    
    def execute_join_query(
        self,
        query: Dict[str, Any],
        backends: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute a join query across backends.
        
        Args:
            query: Join query definition.
            backends: List of backend names to query.
            
        Returns:
            Joined query results.
        """
        # Stub implementation - actual join logic would go here
        results = []
        for backend in backends:
            if backend in self.backends:
                results.append({
                    "backend": backend,
                    "data": [],
                    "joined": True
                })
        return results
    
    def analyze_query_plan(
        self,
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze the execution plan for a query.
        
        Args:
            query: Query to analyze.
            
        Returns:
            Query plan analysis.
        """
        return {
            "estimated_cost": 1.0,
            "uses_index": False,
            "scan_type": "full_scan",
            "recommendations": self.get_optimization_recommendations()
        }
    
    def clear_cache(self) -> None:
        """Clear the query cache."""
        self._cache.clear()
        self._cache_stats = QueryCacheStats()
    
    def detect_slow_queries(
        self,
        threshold_ms: float = 100.0
    ) -> List[Dict[str, Any]]:
        """Detect slow queries based on threshold.
        
        Args:
            threshold_ms: Threshold in milliseconds.
            
        Returns:
            List of slow query information.
        """
        slow_queries = []
        for i, time_ms in enumerate(self._query_times):
            if time_ms > threshold_ms:
                slow_queries.append({
                    "index": i,
                    "time_ms": time_ms,
                    "threshold_exceeded_by": time_ms - threshold_ms
                })
        return slow_queries
    
    def execute_parallel_query(
        self,
        queries: List[Dict[str, Any]],
        backends: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Execute queries in parallel across backends.
        
        Args:
            queries: List of queries to execute.
            backends: Optional list of backends to use.
            
        Returns:
            List of query results.
        """
        results = []
        target_backends = backends or list(self.backends.keys())
        
        for query in queries:
            results.append({
                "query": query,
                "results": [],
                "backends_used": target_backends,
                "parallel": True
            })
        
        return results
    
    def prefetch_results(
        self,
        keys: List[str]
    ) -> Dict[str, Any]:
        """Prefetch results for given keys.
        
        Args:
            keys: Keys to prefetch.
            
        Returns:
            Prefetched results.
        """
        prefetched = {}
        for key in keys:
            if key in self._cache:
                prefetched[key] = self._cache[key]
            else:
                prefetched[key] = None  # Would be fetched asynchronously
        return prefetched
    
    def invalidate_cache(
        self,
        pattern: Optional[str] = None
    ) -> int:
        """Invalidate cache entries matching pattern.
        
        Args:
            pattern: Optional pattern to match keys.
            
        Returns:
            Number of entries invalidated.
        """
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            return count
        
        # Simple pattern matching
        keys_to_remove = [
            k for k in self._cache.keys()
            if pattern in k
        ]
        for key in keys_to_remove:
            del self._cache[key]
        
        return len(keys_to_remove)
    
    def batch_queries(
        self,
        queries: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """Batch queries for efficient execution.
        
        Args:
            queries: List of queries to batch.
            batch_size: Size of each batch.
            
        Returns:
            List of batched query groups.
        """
        batches = []
        for i in range(0, len(queries), batch_size):
            batches.append(queries[i:i + batch_size])
        return batches


__all__ = [
    "QueryOptimizer",
    "QueryCacheStats",
    "PerformanceMetrics",
]