"""Knowledge search and discovery."""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Callable

@dataclass
class SearchResult:
    """Search result item."""
    backend: str
    knowledge_id: str
    data: Dict[str, Any]
    relevance_score: float

class SearchService:
    """Handles knowledge search and discovery."""

    def __init__(self, backends: Dict[str, Any]):
        """Initialize SearchService."""
        self.backends = backends
        self.indices: Dict[str, Dict[str, List[str]]] = {b: {} for b in backends}

    def full_text_search(self, query: str, backends: Optional[List[str]] = None) -> List[SearchResult]:
        """Full-text search across backends."""
        results = []
        targets = backends or list(self.backends.keys())
        
        for backend in targets:
            if backend in self.backends:
                # Simulate full-text search
                for key, docs in self.indices.get(backend, {}).items():
                    if query.lower() in key.lower():
                        for doc_id in docs:
                            results.append(SearchResult(
                                backend=backend,
                                knowledge_id=doc_id,
                                data={},
                                relevance_score=0.8
                            ))
        return results

    def semantic_search(self, query: str, backends: Optional[List[str]] = None) -> List[SearchResult]:
        """Semantic search with similarity."""
        results = []
        targets = backends or list(self.backends.keys())
        
        for backend in targets:
            if backend in self.backends:
                # Simulate semantic search
                for key, docs in self.indices.get(backend, {}).items():
                    score = self._compute_similarity(query, key)
                    if score > 0.2:
                        for doc_id in docs:
                            results.append(SearchResult(
                                backend=backend,
                                knowledge_id=doc_id,
                                data={},
                                relevance_score=score
                            ))
        return sorted(results, key=lambda r: r.relevance_score, reverse=True)

    def faceted_search(self, query: str, facets: Dict[str, Any], backends: Optional[List[str]] = None) -> List[SearchResult]:
        """Search with faceted filtering."""
        results = self.full_text_search(query, backends)
        
        # Apply facet filters
        for facet_key, facet_values in facets.items():
            results = [r for r in results if r.data.get(facet_key) in facet_values]
        
        return results

    def add_to_index(self, backend: str, key: str, doc_id: str) -> None:
        """Add document to search index."""
        if backend not in self.indices:
            self.indices[backend] = {}
        if key not in self.indices[backend]:
            self.indices[backend][key] = []
        self.indices[backend][key].append(doc_id)

    def _compute_similarity(self, query: str, text: str) -> float:
        """Compute similarity score."""
        common = len(set(query.lower().split()) & set(text.lower().split()))
        total = len(set(query.lower().split()) | set(text.lower().split()))
        return common / total if total > 0 else 0.0
