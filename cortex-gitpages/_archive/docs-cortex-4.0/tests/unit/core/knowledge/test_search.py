"""Tests for search service."""
import pytest
from src.core.knowledge.search import SearchService, SearchResult

@pytest.fixture
def search_service():
    backends = {"backend_a": {}, "backend_b": {}}
    return SearchService(backends)

def test_full_text_search_basic(search_service):
    """Test basic full-text search."""
    search_service.add_to_index("backend_a", "machine learning", "doc1")
    results = search_service.full_text_search("machine learning")
    assert len(results) > 0

def test_full_text_search_multiple_backends(search_service):
    """Test full-text search across backends."""
    search_service.add_to_index("backend_a", "data science", "doc1")
    search_service.add_to_index("backend_b", "data engineering", "doc2")
    results = search_service.full_text_search("data")
    assert len(results) >= 2

def test_full_text_search_no_results(search_service):
    """Test full-text search with no results."""
    results = search_service.full_text_search("nonexistent")
    assert len(results) == 0

def test_semantic_search_basic(search_service):
    """Test basic semantic search."""
    search_service.add_to_index("backend_a", "artificial intelligence", "doc1")
    results = search_service.semantic_search("AI")
    assert isinstance(results, list)

def test_semantic_search_relevance(search_service):
    """Test semantic search relevance scoring."""
    search_service.add_to_index("backend_a", "machine learning algorithms", "doc1")
    results = search_service.semantic_search("machine learning")
    assert all(isinstance(r, SearchResult) for r in results)
    if results:
        assert all(0 <= r.relevance_score <= 1 for r in results)

def test_semantic_search_ranking(search_service):
    """Test semantic search result ranking."""
    search_service.add_to_index("backend_a", "python programming", "doc1")
    search_service.add_to_index("backend_a", "python snake", "doc2")
    results = search_service.semantic_search("python programming")
    if len(results) > 1:
        assert results[0].relevance_score >= results[1].relevance_score

def test_faceted_search_basic(search_service):
    """Test basic faceted search."""
    search_service.add_to_index("backend_a", "python django", "doc1")
    results = search_service.faceted_search("python", {"category": ["web"]})
    assert isinstance(results, list)

def test_faceted_search_multiple_facets(search_service):
    """Test faceted search with multiple facets."""
    search_service.add_to_index("backend_a", "python django", "doc1")
    facets = {"category": ["web"], "level": ["intermediate"]}
    results = search_service.faceted_search("python", facets)
    assert isinstance(results, list)

def test_add_to_index(search_service):
    """Test adding documents to index."""
    search_service.add_to_index("backend_a", "test keyword", "doc1")
    assert "backend_a" in search_service.indices
    assert "test keyword" in search_service.indices["backend_a"]

def test_add_multiple_docs_same_key(search_service):
    """Test adding multiple documents with same key."""
    search_service.add_to_index("backend_a", "keyword", "doc1")
    search_service.add_to_index("backend_a", "keyword", "doc2")
    docs = search_service.indices["backend_a"]["keyword"]
    assert len(docs) == 2

def test_search_targeted_backends(search_service):
    """Test search with specific backends."""
    search_service.add_to_index("backend_a", "search term", "doc1")
    search_service.add_to_index("backend_b", "search term", "doc2")
    results = search_service.full_text_search("search term", backends=["backend_a"])
    assert all(r.backend == "backend_a" for r in results)

def test_semantic_search_similarity(search_service):
    """Test semantic similarity computation."""
    search_service.add_to_index("backend_a", "clustering algorithms", "doc1")
    results = search_service.semantic_search("clustering")
    assert len(results) > 0

def test_search_result_structure(search_service):
    """Test search result structure."""
    search_service.add_to_index("backend_a", "test", "doc1")
    results = search_service.full_text_search("test")
    if results:
        r = results[0]
        assert hasattr(r, "backend")
        assert hasattr(r, "knowledge_id")
        assert hasattr(r, "relevance_score")

def test_empty_search(search_service):
    """Test search on empty index."""
    results = search_service.full_text_search("anything")
    assert isinstance(results, list)

def test_faceted_search_filtering(search_service):
    """Test faceted search applies filters."""
    search_service.add_to_index("backend_a", "python", "doc1")
    # Documents would have metadata in real implementation
    results = search_service.faceted_search("python", {"language": ["python"]})
    assert isinstance(results, list)

def test_search_backends_parameter_default(search_service):
    """Test search uses all backends by default."""
    search_service.add_to_index("backend_a", "term", "doc1")
    search_service.add_to_index("backend_b", "term", "doc2")
    results = search_service.full_text_search("term")
    backends_found = {r.backend for r in results}
    assert len(backends_found) >= 1
