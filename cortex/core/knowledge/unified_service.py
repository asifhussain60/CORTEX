"""Unified Knowledge Service - Knowledge facade.

Provides unified query interface across multiple knowledge backends with
aggregation, deduplication, and source attribution.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
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
    ) -> None:
        """Initialize unified service.

        Args:
            router: Optional knowledge router.
            backends: Dictionary of backend implementations.
        """
        self.router = router
        self.backends = backends or {}
        self._cache: Dict[str, List[KnowledgeResult]] = {}

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


__all__ = ["UnifiedKnowledgeService", "KnowledgeResult"]
