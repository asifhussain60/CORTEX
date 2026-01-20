"""Query optimization with caching, indexing, and performance monitoring."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

@dataclass
class QueryStats:
    """Query statistics."""
    query: str
    count: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    last_executed: Optional[datetime] = None
    cache_hits: int = 0

@dataclass
class IndexMetadata:
    """Index metadata."""
    backend: str
    indexed_fields: List[str]
    created_at: datetime
    record_count: int = 0
    last_updated: Optional[datetime] = None

class QueryOptimizer:
    """Optimizes query execution with caching, indexing, and monitoring."""

    def __init__(self, backends: Dict[str, Any], enable_caching: bool = True):
        """Initialize QueryOptimizer."""
        self.backends = backends
        self.enable_caching = enable_caching
        self.query_cache: Dict[str, Any] = {}
        self.query_stats: Dict[str, QueryStats] = {}
        self.indices: Dict[str, IndexMetadata] = {}
        self.metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_query_time_ms': 0.0,
        }

    def cache_result(self, query: str, result: Any, ttl_seconds: int = 300) -> None:
        """Cache query result."""
        cache_key = self._get_cache_key(query)
        self.query_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now(),
            'ttl': ttl_seconds
        }

    def get_cached_result(self, query: str) -> Optional[Any]:
        """Get cached result if available."""
        cache_key = self._get_cache_key(query)
        if cache_key in self.query_cache:
            cached = self.query_cache[cache_key]
            if (datetime.now() - cached['timestamp']).total_seconds() < cached['ttl']:
                self.metrics['cache_hits'] += 1
                return cached['result']
            else:
                del self.query_cache[cache_key]
        self.metrics['cache_misses'] += 1
        return None

    def create_index(self, backend_name: str, fields: List[str]) -> None:
        """Create index for backend."""
        index_name = f"{backend_name}_{'_'.join(fields)}"
        self.indices[index_name] = IndexMetadata(
            backend=backend_name,
            indexed_fields=fields,
            created_at=datetime.now()
        )

    def execute_join_query(self, query: str, backends_to_join: List[str]) -> List[Dict]:
        """Execute join query across backends."""
        # Simplified join implementation
        results = []
        for backend_name in backends_to_join:
            backend = self.backends.get(backend_name)
            if backend and hasattr(backend, 'query'):
                try:
                    backend_results = backend.query(query)
                    results.extend(backend_results or [])
                except Exception:
                    pass
        return results

    def execute_parallel_query(self, query: str) -> List[Dict]:
        """Execute query in parallel across backends."""
        # Simplified parallel execution
        results = []
        for backend in self.backends.values():
            if hasattr(backend, 'query'):
                try:
                    backend_results = backend.query(query)
                    results.extend(backend_results or [])
                except Exception:
                    pass
        return results

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'total_queries': self.metrics['total_queries'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': (
                self.metrics['cache_hits'] / 
                max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1)
            ),
            'indices_count': len(self.indices),
            'cache_size': len(self.query_cache),
        }

    def get_optimization_recommendations(self) -> List[str]:
        """Get optimization recommendations."""
        recommendations = []
        if self.metrics['cache_hits'] < 5:
            recommendations.append("Consider adding frequently accessed queries to cache")
        if len(self.indices) == 0:
            recommendations.append("Create indices for frequently queried fields")
        return recommendations

    def analyze_query_plan(self, query: str) -> Dict[str, Any]:
        """Analyze query execution plan."""
        return {
            'query': query,
            'estimated_cost': 100,
            'uses_cache': query in self.query_cache,
            'uses_index': any(idx for idx in self.indices.keys()),
        }

    def detect_slow_queries(self, threshold_ms: float = 1000) -> List[str]:
        """Detect slow queries."""
        slow = []
        for query, stats in self.query_stats.items():
            if stats.avg_time_ms > threshold_ms:
                slow.append(query)
        return slow

    def prefetch_results(self, queries: List[str]) -> None:
        """Prefetch query results."""
        for query in queries:
            if self.get_cached_result(query) is None:
                # Prefetch by querying backends
                for backend in self.backends.values():
                    if hasattr(backend, 'query'):
                        try:
                            result = backend.query(query)
                            self.cache_result(query, result)
                            break
                        except Exception:
                            pass

    def invalidate_cache(self, pattern: Optional[str] = None) -> None:
        """Invalidate cache entries."""
        if pattern is None:
            self.query_cache.clear()
        else:
            keys_to_delete = [k for k in self.query_cache.keys() if pattern in k]
            for k in keys_to_delete:
                del self.query_cache[k]

    def batch_queries(self, queries: List[str]) -> List[Any]:
        """Batch multiple queries."""
        results = []
        for query in queries:
            cached = self.get_cached_result(query)
            if cached:
                results.append(cached)
            else:
                for backend in self.backends.values():
                    if hasattr(backend, 'query'):
                        try:
                            result = backend.query(query)
                            self.cache_result(query, result)
                            results.append(result)
                            break
                        except Exception:
                            pass
        return results

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'cached_queries': len(self.query_cache),
            'hits': self.metrics['cache_hits'],
            'misses': self.metrics['cache_misses'],
        }

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key."""
        return hashlib.md5(query.encode()).hexdigest()
