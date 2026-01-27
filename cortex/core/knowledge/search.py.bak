"""Knowledge search service with multi-backend support and semantic ranking."""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib


@dataclass
class SearchResult:
    """Data class for search results with relevance scoring.
    
    Attributes:
        doc_id: Document identifier.
        content: Document content/keyword.
        relevance_score: Relevance score between 0 and 1.
        backend: Source backend name.
        facets: Associated facets (optional).
    """
    doc_id: str = ""
    content: str = ""
    relevance_score: float = 0.0
    backend: str = ""
    facets: Dict[str, List[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate relevance score is in valid range."""
        if not 0 <= self.relevance_score <= 1:
            self.relevance_score = min(1.0, max(0.0, self.relevance_score))

    @property
    def knowledge_id(self) -> str:
        """Alias for doc_id for backwards compatibility."""
        return self.doc_id


class SearchService:
    """Multi-backend search service with full-text, semantic, and faceted search.
    
    Supports multiple search backends with keyword indexing and relevance ranking.
    """

    def __init__(self, backends: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize search service with configured backends.
        
        Args:
            backends: Dictionary mapping backend names to backend configurations.
        
        Raises:
            TypeError: If backends is not a dict or None.
        """
        if backends is None:
            backends = {}
        if not isinstance(backends, dict):
            raise TypeError(f"backends must be dict, got {type(backends)}")
        
        self.backends = backends
        self.indices: Dict[str, Dict[str, List[str]]] = {
            backend: {} for backend in backends.keys()
        }

    def add_to_index(self, backend: str, keyword: str, doc_id: str) -> None:
        """Add document to search index for a backend.
        
        Args:
            backend: Backend name.
            keyword: Search keyword/content.
            doc_id: Document identifier.
        """
        if backend not in self.indices:
            self.indices[backend] = {}
        
        if keyword not in self.indices[backend]:
            self.indices[backend][keyword] = []
        
        if doc_id not in self.indices[backend][keyword]:
            self.indices[backend][keyword].append(doc_id)

    def full_text_search(
        self,
        query: str,
        backends: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search using full-text matching across backends.
        
        Args:
            query: Search query string.
            backends: Optional list of specific backends to search. If None, searches all.
        
        Returns:
            List of SearchResult objects ranked by relevance.
        """
        if not query or not query.strip():
            return []
        
        results: List[SearchResult] = []
        search_backends = backends or list(self.indices.keys())
        query_terms = set(query.lower().split())
        
        for backend in search_backends:
            if backend not in self.indices:
                continue
            
            for keyword, doc_ids in self.indices[backend].items():
                keyword_terms = set(keyword.lower().split())
                overlap = len(query_terms & keyword_terms)
                
                if overlap > 0:
                    relevance = overlap / len(query_terms | keyword_terms)
                    
                    for doc_id in doc_ids:
                        result = SearchResult(
                            doc_id=doc_id,
                            content=keyword,
                            relevance_score=relevance,
                            backend=backend
                        )
                        results.append(result)
        
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results

    def semantic_search(
        self,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """Semantic search with similarity-based ranking.
        
        Args:
            query: Search query string.
            limit: Maximum number of results to return.
        
        Returns:
            List of SearchResult objects ranked by semantic similarity.
        """
        if not query or not query.strip():
            return []
        
        results: List[SearchResult] = []
        
        for backend, keywords_index in self.indices.items():
            for keyword, doc_ids in keywords_index.items():
                similarity = self._compute_similarity(query, keyword)
                
                if similarity > 0.3:  # Relevance threshold
                    for doc_id in doc_ids:
                        result = SearchResult(
                            doc_id=doc_id,
                            content=keyword,
                            relevance_score=similarity,
                            backend=backend
                        )
                        results.append(result)
        
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:limit]

    def faceted_search(
        self,
        query: str,
        facets: Dict[str, List[str]]
    ) -> List[SearchResult]:
        """Search with facet filtering.
        
        Args:
            query: Search query string.
            facets: Dictionary mapping facet names to allowed values.
        
        Returns:
            List of SearchResult objects matching both query and facets.
        """
        # First perform full-text search
        results = self.full_text_search(query)
        
        # Filter by facets if present
        if not facets:
            return results
        
        filtered_results = []
        for result in results:
            matches_facets = True
            for facet_name, facet_values in facets.items():
                if facet_name not in result.facets:
                    # If facet not in result, consider it a non-match
                    matches_facets = False
                    break
                
                result_facet_values = set(result.facets[facet_name])
                if not any(v in result_facet_values for v in facet_values):
                    matches_facets = False
                    break
            
            if matches_facets:
                filtered_results.append(result)
        
        return filtered_results

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts using Jaccard distance.
        
        Args:
            text1: First text string.
            text2: Second text string.
        
        Returns:
            Similarity score between 0 and 1.
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0


class KnowledgeSearchEngine:
    """High-level knowledge search engine with advanced indexing and retrieval.
    
    Builds on SearchService to provide domain-specific search capabilities.
    """

    def __init__(self, backends: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """Initialize knowledge search engine.
        
        Args:
            backends: Dictionary mapping backend names to backend configurations.
        """
        self.search_service = SearchService(backends or {})

    def search(
        self,
        query: str,
        search_type: str = "full_text",
        **kwargs: Any
    ) -> List[SearchResult]:
        """Execute search with specified strategy.
        
        Args:
            query: Search query string.
            search_type: Type of search ("full_text", "semantic", "faceted").
            **kwargs: Additional arguments for specific search types.
        
        Returns:
            List of SearchResult objects.
        
        Raises:
            ValueError: If search_type is not recognized.
        """
        if search_type == "full_text":
            return self.search_service.full_text_search(
                query,
                backends=kwargs.get("backends")
            )
        elif search_type == "semantic":
            return self.search_service.semantic_search(
                query,
                limit=kwargs.get("limit", 10)
            )
        elif search_type == "faceted":
            facets = kwargs.get("facets", {})
            return self.search_service.faceted_search(query, facets)
        else:
            raise ValueError(f"Unknown search type: {search_type}")


__all__ = [
    "SearchResult",
    "SearchService",
    "KnowledgeSearchEngine",
]