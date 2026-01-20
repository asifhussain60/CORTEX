"""
UnifiedKnowledgeService - Unified facade for knowledge querying.

Wraps IntelligentKnowledgeRouter and provides:
  - Single entry point for knowledge queries
  - Cross-backend aggregation and deduplication
  - Source attribution for all results
  - Domain-aware query routing
  - Confidence scoring and result ranking

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-028: Kebab-case module naming
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple, Callable, AsyncIterator
from datetime import datetime
from collections import defaultdict
import hashlib


@dataclass
class QueryResult:
    """Unified result from knowledge query."""
    
    id: str
    content: str
    source_backend: str
    domain: str
    confidence_score: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    lineage: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedQueryResult:
    """Aggregated results from multiple backends."""
    
    query: str
    total_results: int
    unique_results: int
    results: List[QueryResult] = field(default_factory=list)
    aggregation_time_ms: float = 0.0
    backend_sources: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedKnowledgeService:
    """
    Unified service for querying knowledge across multiple backends.
    
    Provides facade wrapping IntelligentKnowledgeRouter with aggregation,
    deduplication, and cross-backend result synthesis.
    """
    
    def __init__(
        self,
        router: Any,
        backends: Dict[str, Any],
        enable_caching: bool = True,
        dedup_strategy: str = 'exact'  # 'exact' or 'semantic'
    ):
        """
        Initialize UnifiedKnowledgeService.
        
        Args:
            router: IntelligentKnowledgeRouter instance.
            backends: Dictionary of knowledge backends.
            enable_caching: Enable result caching.
            dedup_strategy: Deduplication strategy (exact or semantic).
        """
        self.router = router
        self.backends = backends
        self.enable_caching = enable_caching
        self.dedup_strategy = dedup_strategy
        
        # Cache
        self.result_cache: Dict[str, AggregatedQueryResult] = {}
        
        # Metrics
        self.query_metrics = {
            'total_queries': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'aggregation_times': [],
            'queries_by_domain': defaultdict(int),
            'results_per_query': [],
            'deduplication_stats': {'total_duplicates': 0},
        }

    def query(
        self,
        query_text: str,
        domain: Optional[str] = None,
        limit: int = 10,
        min_confidence: float = 0.0
    ) -> AggregatedQueryResult:
        """
        Execute unified query across all backends.
        
        Args:
            query_text: Query text.
            domain: Optional domain filter.
            limit: Maximum results to return.
            min_confidence: Minimum confidence threshold.
            
        Returns:
            AggregatedQueryResult with deduplicated results.
        """
        start_time = datetime.now()
        
        # Check cache
        cache_key = self._get_cache_key(query_text, domain)
        if self.enable_caching and cache_key in self.result_cache:
            self.query_metrics['cache_hits'] += 1
            return self.result_cache[cache_key]
        
        self.query_metrics['cache_misses'] += 1
        self.query_metrics['total_queries'] += 1
        if domain:
            self.query_metrics['queries_by_domain'][domain] += 1
        
        # Query router
        try:
            router_results = self.router.route(query_text, domain=domain) if self.router else {}
        except Exception:
            router_results = {}
        
        # Aggregate from all backends
        all_results = []
        
        for backend_name, backend in self.backends.items():
            try:
                if hasattr(backend, 'query'):
                    backend_results = backend.query(query_text, domain=domain)
                    if backend_results:
                        for result in backend_results:
                            query_result = self._create_query_result(
                                result,
                                backend_name,
                                domain or 'general'
                            )
                            if query_result.confidence_score >= min_confidence:
                                all_results.append(query_result)
            except Exception:
                # Gracefully handle backend errors
                pass
        
        # Deduplicate
        unique_results = self.deduplicate_results(all_results)
        
        # Rank
        ranked_results = self.rank_results(unique_results)
        
        # Limit results
        final_results = ranked_results[:limit]
        
        # Create aggregated result
        aggregation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        aggregated = AggregatedQueryResult(
            query=query_text,
            total_results=len(all_results),
            unique_results=len(unique_results),
            results=final_results,
            aggregation_time_ms=aggregation_time,
            backend_sources=set(b.source_backend for b in final_results),
            metadata={'domain': domain}
        )
        
        # Cache result
        if self.enable_caching:
            self.result_cache[cache_key] = aggregated
        
        # Track metrics
        self.query_metrics['aggregation_times'].append(aggregation_time)
        self.query_metrics['results_per_query'].append(len(final_results))
        
        return aggregated

    def query_by_domain(
        self,
        query_text: str,
        domain: str,
        limit: int = 10
    ) -> AggregatedQueryResult:
        """
        Query specific domain.
        
        Args:
            query_text: Query text.
            domain: Target domain.
            limit: Maximum results.
            
        Returns:
            Aggregated results from domain.
        """
        return self.query(query_text, domain=domain, limit=limit)

    def query_batch(
        self,
        queries: List[str],
        domain: Optional[str] = None
    ) -> List[AggregatedQueryResult]:
        """
        Execute batch queries.
        
        Args:
            queries: List of query texts.
            domain: Optional domain filter.
            
        Returns:
            List of aggregated results.
        """
        results = []
        for query_text in queries:
            result = self.query(query_text, domain=domain)
            results.append(result)
        return results

    def query_async(
        self,
        query_text: str,
        domain: Optional[str] = None
    ) -> AsyncIterator[QueryResult]:
        """
        Asynchronous query execution.
        
        Args:
            query_text: Query text.
            domain: Optional domain filter.
            
        Yields:
            Individual query results as they arrive.
        """
        # Placeholder for async implementation
        # In real implementation, would use asyncio
        result = self.query(query_text, domain=domain)
        for item in result.results:
            yield item

    def aggregate_results(
        self,
        results_by_backend: Dict[str, List[Any]]
    ) -> List[QueryResult]:
        """
        Aggregate results from multiple backends.
        
        Args:
            results_by_backend: Results keyed by backend name.
            
        Returns:
            Aggregated QueryResult list.
        """
        aggregated = []
        
        for backend_name, results in results_by_backend.items():
            for result in results:
                query_result = self._create_query_result(result, backend_name, 'aggregated')
                aggregated.append(query_result)
        
        return aggregated

    def deduplicate_results(
        self,
        results: List[QueryResult]
    ) -> List[QueryResult]:
        """
        Deduplicate results across backends.
        
        Args:
            results: Results to deduplicate.
            
        Returns:
            Deduplicated results.
        """
        seen_hashes = set()
        unique_results = []
        duplicates_count = 0
        
        for result in results:
            # Create hash for deduplication
            if self.dedup_strategy == 'exact':
                result_hash = self._hash_result(result.content)
            else:  # semantic
                result_hash = self._semantic_hash(result.content)
            
            if result_hash not in seen_hashes:
                seen_hashes.add(result_hash)
                unique_results.append(result)
            else:
                duplicates_count += 1
        
        self.query_metrics['deduplication_stats']['total_duplicates'] += duplicates_count
        
        return unique_results

    def rank_results(
        self,
        results: List[QueryResult]
    ) -> List[QueryResult]:
        """
        Rank results by confidence score.
        
        Args:
            results: Results to rank.
            
        Returns:
            Ranked results (highest confidence first).
        """
        return sorted(
            results,
            key=lambda r: (r.confidence_score, r.timestamp),
            reverse=True
        )

    def add_source_attribution(
        self,
        result: QueryResult,
        source_backend: str,
        additional_metadata: Optional[Dict] = None
    ) -> QueryResult:
        """
        Add source attribution to result.
        
        Args:
            result: Query result.
            source_backend: Source backend name.
            additional_metadata: Optional additional metadata.
            
        Returns:
            Result with attribution.
        """
        result.source_backend = source_backend
        result.lineage = {
            'backend': source_backend,
            'timestamp': datetime.now().isoformat(),
            **(additional_metadata or {})
        }
        return result

    def get_result_confidence(self, result: QueryResult) -> float:
        """
        Get confidence score for result.
        
        Args:
            result: Query result.
            
        Returns:
            Confidence score (0-1).
        """
        return result.confidence_score

    def get_result_lineage(self, result: QueryResult) -> Dict[str, Any]:
        """
        Get result lineage information.
        
        Args:
            result: Query result.
            
        Returns:
            Lineage dictionary.
        """
        return result.lineage

    def get_query_metrics(self) -> Dict[str, Any]:
        """
        Get query metrics.
        
        Returns:
            Metrics dictionary.
        """
        avg_aggregation_time = (
            sum(self.query_metrics['aggregation_times']) /
            len(self.query_metrics['aggregation_times'])
            if self.query_metrics['aggregation_times'] else 0.0
        )
        
        avg_results_per_query = (
            sum(self.query_metrics['results_per_query']) /
            len(self.query_metrics['results_per_query'])
            if self.query_metrics['results_per_query'] else 0.0
        )
        
        return {
            'total_queries': self.query_metrics['total_queries'],
            'cache_hits': self.query_metrics['cache_hits'],
            'cache_misses': self.query_metrics['cache_misses'],
            'cache_hit_rate': (
                self.query_metrics['cache_hits'] /
                (self.query_metrics['cache_hits'] + self.query_metrics['cache_misses'])
                if (self.query_metrics['cache_hits'] + self.query_metrics['cache_misses']) > 0
                else 0.0
            ),
            'avg_aggregation_time_ms': avg_aggregation_time,
            'avg_results_per_query': avg_results_per_query,
            'queries_by_domain': dict(self.query_metrics['queries_by_domain']),
            'total_duplicates_removed': self.query_metrics['deduplication_stats']['total_duplicates'],
            'cache_size': len(self.result_cache),
        }

    def handle_backend_error(
        self,
        backend_name: str,
        error: Exception
    ) -> None:
        """
        Handle backend error gracefully.
        
        Args:
            backend_name: Backend that failed.
            error: Exception that occurred.
        """
        # Log error and continue with other backends
        pass

    def cache_results(
        self,
        query: str,
        result: AggregatedQueryResult
    ) -> None:
        """
        Manually cache query result.
        
        Args:
            query: Query text.
            result: Result to cache.
        """
        cache_key = self._get_cache_key(query, result.metadata.get('domain'))
        self.result_cache[cache_key] = result

    def clear_cache(self) -> None:
        """Clear result cache."""
        self.result_cache.clear()

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _create_query_result(
        self,
        backend_result: Any,
        source_backend: str,
        domain: str
    ) -> QueryResult:
        """Create QueryResult from backend result."""
        # Handle various result formats
        if isinstance(backend_result, dict):
            content = backend_result.get('content', str(backend_result))
            confidence = backend_result.get('confidence', 0.5)
            metadata = {k: v for k, v in backend_result.items() if k not in ['content', 'confidence']}
        else:
            content = str(backend_result)
            confidence = 0.5
            metadata = {}
        
        # Generate ID
        result_id = self._hash_result(content)
        
        return QueryResult(
            id=result_id,
            content=content,
            source_backend=source_backend,
            domain=domain,
            confidence_score=confidence,
            timestamp=datetime.now(),
            metadata=metadata,
            lineage={'source': source_backend}
        )

    def _get_cache_key(self, query: str, domain: Optional[str]) -> str:
        """Generate cache key."""
        key_parts = [query, domain or '']
        key = '|'.join(key_parts)
        return hashlib.md5(key.encode()).hexdigest()

    def _hash_result(self, content: str) -> str:
        """Generate hash for result content."""
        return hashlib.md5(content.encode()).hexdigest()

    def _semantic_hash(self, content: str) -> str:
        """Generate semantic hash (simplified - would use embeddings in real implementation)."""
        # For now, use same as exact hash
        return self._hash_result(content)


__all__ = [
    'UnifiedKnowledgeService',
    'QueryResult',
    'AggregatedQueryResult',
]
