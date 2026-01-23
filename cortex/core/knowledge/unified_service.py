"""Unified Knowledge Service - Knowledge facade.

Provides unified query interface across multiple knowledge backends with
aggregation, deduplication, and source attribution.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from cortex.core.result import Result, Ok, Err


@dataclass
class KnowledgeResult:
    """Single knowledge result with attribution.

    Attributes:
        value: The knowledge result value.
        source: Backend source identifier.
        confidence: Confidence score (0.0-1.0).
        metadata: Additional metadata.
    """

    value: Any
    source: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize metadata if needed."""
        if self.metadata is None:
            self.metadata = {}


class UnifiedKnowledgeService:
    """Unified interface for knowledge backends.

    Attributes:
        router: IntelligentKnowledgeRouter instance.
        backends: Dictionary of backend implementations.
        _cache: Result cache for deduplication.
    """

    def __init__(
        self,
        router: Optional[Any] = None,
        backends: Optional[Dict[str, Any]] = None,
        enable_caching: bool = True,
    ) -> None:
        """Initialize unified service.

        Args:
            router: Optional knowledge router.
            backends: Dictionary of backend implementations.
            enable_caching: Whether to enable result caching.
        """
        self.router = router
        self.backends = backends or {}
        self._cache: Dict[str, List[KnowledgeResult]] = {}
        self.enable_caching = enable_caching

    def query(
        self, query_text: str, backends: Optional[List[str]] = None
    ) -> Any:
        """Execute unified query across backends.

        Args:
            query_text: Query string.
            backends: Optional list of specific backends to query.

        Returns:
            Result with list of knowledge results.
        """
        try:
            if not query_text:
                return Err("Query text cannot be empty")

            # Check cache
            cache_key = f"{query_text}:{','.join(sorted(backends or []))}"
            if cache_key in self._cache:
                return Ok(self._cache[cache_key])

            # Query backends
            results = []
            backends_to_query = backends or list(self.backends.keys())

            for backend_name in backends_to_query:
                if backend_name not in self.backends:
                    continue

                backend = self.backends[backend_name]
                if hasattr(backend, "query"):
                    try:
                        backend_results = backend.query(query_text)
                        if isinstance(backend_results, list):
                            for value in backend_results:
                                result = KnowledgeResult(
                                    value=value, source=backend_name
                                )
                                results.append(result)
                    except Exception:
                        pass

            # Deduplicate
            deduplicated = self.deduplicate_results(results)

            # Cache
            self._cache[cache_key] = deduplicated

            return Ok(deduplicated)
        except Exception as e:
            return Err(f"Query failed: {str(e)}")

    def aggregate_results(
        self, results: List[KnowledgeResult]
    ) -> Dict[str, Any]:
        """Aggregate results from multiple backends.

        Args:
            results: List of knowledge results.

        Returns:
            Aggregated result summary.
        """
        by_source: Dict[str, List[Any]] = {}

        for result in results:
            if result.source not in by_source:
                by_source[result.source] = []
            by_source[result.source].append(result.value)

        return {
            "by_source": by_source,
            "total_results": len(results),
            "sources": list(by_source.keys()),
        }

    def deduplicate_results(
        self, results: List[KnowledgeResult]
    ) -> List[KnowledgeResult]:
        """Remove duplicate results from multiple backends.

        Args:
            results: List of knowledge results.

        Returns:
            Deduplicated results.
        """
        seen: Set[str] = set()
        deduplicated = []

        for result in results:
            # Create key from value representation
            value_key = str(result.value)
            if value_key not in seen:
                seen.add(value_key)
                deduplicated.append(result)

        return deduplicated

    def get_source_attribution(
        self, result: KnowledgeResult
    ) -> Dict[str, Any]:
        """Get source attribution for a result.

        Args:
            result: Knowledge result.

        Returns:
            Attribution dictionary.
        """
        return {
            "source": result.source,
            "confidence": result.confidence,
            "timestamp": result.metadata.get("timestamp"),
        }

    def clear_cache(self) -> None:
        """Clear result cache."""
        self._cache.clear()

    def add_source_attribution(
        self,
        result: KnowledgeResult,
        source_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add source attribution information to a result.
        
        Args:
            result: Knowledge result to annotate.
            source_metadata: Additional metadata for the source.
        """
        if source_metadata:
            result.metadata.update(source_metadata)

    def query_by_domain(
        self,
        query_text: str,
        domain: str,
        backends: Optional[List[str]] = None
    ) -> Any:
        """Execute domain-aware query.
        
        Args:
            query_text: Query string.
            domain: Business domain for query routing.
            backends: Optional list of specific backends.
        
        Returns:
            Result with domain-filtered results.
        """
        # Execute normal query, optionally filtered by domain
        result = self.query(query_text, backends)
        
        if result.is_ok():
            # Filter results by domain if router supports it
            results = result.value
            if self.router and hasattr(self.router, 'route_to_domain'):
                filtered = self.router.route_to_domain(results, domain)
                return Ok(filtered)
            return result
        
        return result

    def get_result_confidence(
        self,
        result: KnowledgeResult
    ) -> float:
        """Get confidence score for a result.
        
        Args:
            result: Knowledge result.
        
        Returns:
            Confidence score between 0 and 1.
        """
        return result.confidence

    def rank_results(
        self,
        results: List[KnowledgeResult],
        criteria: str = "confidence"
    ) -> List[KnowledgeResult]:
        """Rank and filter results by specified criteria.
        
        Args:
            results: List of knowledge results.
            criteria: Ranking criteria ("confidence", "recency", "source").
        
        Returns:
            Ranked list of results.
        """
        if criteria == "confidence":
            return sorted(results, key=lambda r: r.confidence, reverse=True)
        elif criteria == "source":
            # Group by source, stable sort maintains relative order
            return sorted(results, key=lambda r: r.source)
        else:
            return results

    def query_batch(
        self,
        queries: List[str],
        backends: Optional[List[str]] = None
    ) -> List[Any]:
        """Execute batch queries efficiently.
        
        Args:
            queries: List of query strings.
            backends: Optional list of specific backends.
        
        Returns:
            List of results, one per query.
        """
        results = []
        for query_text in queries:
            result = self.query(query_text, backends)
            results.append(result)
        return results

    async def query_async(
        self,
        query_text: str,
        backends: Optional[List[str]] = None
    ) -> Any:
        """Execute async query across backends.
        
        Args:
            query_text: Query string.
            backends: Optional list of specific backends.
        
        Returns:
            Coroutine that returns result.
        """
        # For now, delegate to synchronous query
        # Production implementation would use async I/O
        return self.query(query_text, backends)

    def get_query_metrics(self) -> Dict[str, Any]:
        """Get metrics about query performance and cache usage.
        
        Returns:
            Dictionary with cache size, hit rate, etc.
        """
        return {
            "cache_size": len(self._cache),
            "backends_count": len(self.backends),
            "has_router": self.router is not None
        }

    def handle_backend_error(
        self,
        backend_name: str,
        error: Exception,
        query: Optional[str] = None
    ) -> None:
        """Handle errors from a backend gracefully.
        
        Args:
            backend_name: Name of backend that failed.
            error: Exception that occurred.
            query: Optional query that failed.
        """
        # Log the error without raising
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Backend {backend_name} failed: {str(error)}" +
            (f" for query: {query}" if query else "")
        )

    def get_result_lineage(
        self,
        result: KnowledgeResult
    ) -> Dict[str, Any]:
        """Get the lineage/provenance information for a result.
        
        Args:
            result: Knowledge result.
        
        Returns:
            Dictionary with source lineage information.
        """
        return {
            "source": result.source,
            "confidence": result.confidence,
            "metadata": result.metadata,
            "timestamp": result.metadata.get("timestamp")
        }

    def cache_results(
        self,
        key: str,
        results: List[KnowledgeResult]
    ) -> None:
        """Manually cache results with a given key.
        
        Args:
            key: Cache key.
            results: Results to cache.
        """
        if self.enable_caching:
            self._cache[key] = results


__all__ = ["UnifiedKnowledgeService", "KnowledgeResult"]
