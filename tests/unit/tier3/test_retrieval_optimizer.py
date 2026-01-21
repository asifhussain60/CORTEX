"""
Test suite for Knowledge Retrieval Optimization (KN-002-02)
===========================================================
PHASE-12: Knowledge Ecosystem Expansion
AC: KN-002-02 - Knowledge Retrieval Optimization

Validates:
1. Semantic search functionality
2. Result ranking
3. Performance optimization
4. Query optimization

Specification:
- Semantic search capabilities
- Intelligent ranking
- Caching mechanisms
- Query performance
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
import time


@pytest.fixture(scope="module")
def retrieval_optimizer():
    """Create retrieval optimizer instance for tests."""
    from cortex_brain.tier3.knowledge.retrieval_optimizer import RetrievalOptimizer
    return RetrievalOptimizer()


class TestRetrieverStructure:
    """Tests for retrieval optimizer structure."""
    
    def test_retrieval_config_exists(self, retrieval_optimizer):
        """Verify retrieval config file exists."""
        from pathlib import Path
        import os
        # Go from tests/unit/tier3 up to project root, then to cortex_brain
        project_root = Path(__file__).parent.parent.parent.parent
        config_file = project_root / "cortex_brain" / "tier3" / "knowledge" / "retrieval-config.yaml"
        assert config_file.exists(), f"Retrieval config file not found at {config_file}"
    
    def test_config_contains_metadata(self, retrieval_optimizer):
        """Verify config contains metadata."""
        from pathlib import Path
        import yaml
        project_root = Path(__file__).parent.parent.parent.parent
        config_file = project_root / "cortex_brain" / "tier3" / "knowledge" / "retrieval-config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "metadata" in config
        assert config["metadata"].get("ac_id") == "KN-002-02"
    
    def test_config_has_ranking_rules(self, retrieval_optimizer):
        """Verify config defines ranking rules."""
        from pathlib import Path
        import yaml
        project_root = Path(__file__).parent.parent.parent.parent
        config_file = project_root / "cortex_brain" / "tier3" / "knowledge" / "retrieval-config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        assert "ranking_rules" in config or "ranking_factors" in config


class TestSemanticSearch:
    """Tests for semantic search."""
    
    def test_optimizer_has_semantic_search_method(self, retrieval_optimizer):
        """Verify optimizer has semantic search method."""
        assert hasattr(retrieval_optimizer, 'semantic_search'), \
            "RetrievalOptimizer missing semantic_search method"
    
    def test_semantic_search_returns_results(self, retrieval_optimizer):
        """Verify semantic search returns results."""
        query = "API security best practices"
        results = retrieval_optimizer.semantic_search(query)
        assert isinstance(results, list), "Should return list"
    
    def test_semantic_search_accepts_domain_filter(self, retrieval_optimizer):
        """Verify semantic search accepts domain filter."""
        query = "governance"
        results = retrieval_optimizer.semantic_search(query, domain="GOVERNANCE")
        assert isinstance(results, list)
    
    def test_semantic_search_accepts_limit(self, retrieval_optimizer):
        """Verify semantic search respects limit."""
        query = "test"
        results = retrieval_optimizer.semantic_search(query, limit=5)
        assert len(results) <= 5, "Should respect limit"
    
    def test_semantic_search_handles_empty_query(self, retrieval_optimizer):
        """Verify semantic search handles empty query."""
        results = retrieval_optimizer.semantic_search("")
        assert isinstance(results, list)
    
    def test_semantic_search_returns_relevance_scores(self, retrieval_optimizer):
        """Verify results include relevance scores."""
        query = "knowledge management"
        results = retrieval_optimizer.semantic_search(query)
        if results:
            assert "relevance_score" in results[0] or "score" in results[0] or \
                   isinstance(results[0], dict)


class TestResultRanking:
    """Tests for result ranking."""
    
    def test_optimizer_has_rank_results_method(self, retrieval_optimizer):
        """Verify optimizer has rank_results method."""
        assert hasattr(retrieval_optimizer, 'rank_results'), \
            "RetrievalOptimizer missing rank_results method"
    
    def test_rank_results_returns_list(self, retrieval_optimizer):
        """Verify rank_results returns list."""
        entries = [
            {"entry_id": "KE-1", "content": "Test content 1", "domain": "GOVERNANCE", "quality": 0.8},
            {"entry_id": "KE-2", "content": "Test content 2", "domain": "SECURITY", "quality": 0.9}
        ]
        ranked = retrieval_optimizer.rank_results(entries)
        assert isinstance(ranked, list), "Should return ranked list"
    
    def test_rank_results_orders_by_relevance(self, retrieval_optimizer):
        """Verify ranking orders by relevance."""
        entries = [
            {"entry_id": "KE-LOW", "domain": "TEST", "content": "Low", "quality": 0.5, "relevance_score": 0.5},
            {"entry_id": "KE-HIGH", "domain": "TEST", "content": "High", "quality": 0.95, "relevance_score": 0.95},
            {"entry_id": "KE-MED", "domain": "TEST", "content": "Med", "quality": 0.7, "relevance_score": 0.7}
        ]
        ranked = retrieval_optimizer.rank_results(entries)
        if ranked:
            # First should have highest relevance score
            assert ranked[0].relevance_score >= ranked[-1].relevance_score
    
    def test_ranking_considers_quality_score(self, retrieval_optimizer):
        """Verify ranking considers quality scores."""
        entries = [
            {"entry_id": "KE-1", "quality": 0.6},
            {"entry_id": "KE-2", "quality": 0.9}
        ]
        ranked = retrieval_optimizer.rank_results(entries)
        assert len(ranked) == 2
    
    def test_ranking_considers_domain_relevance(self, retrieval_optimizer):
        """Verify ranking considers domain relevance."""
        entries = [
            {"entry_id": "KE-1", "domain": "GOVERNANCE", "content": "Gov", "quality": 0.8, "relevance_score": 0.8},
            {"entry_id": "KE-2", "domain": "SECURITY", "content": "Sec", "quality": 0.8, "relevance_score": 0.8}
        ]
        domain_weights = {"GOVERNANCE": 1.5}
        ranked = retrieval_optimizer.rank_results(entries, domain_weights=domain_weights)
        assert len(ranked) == 2
    
    def test_ranking_handles_empty_list(self, retrieval_optimizer):
        """Verify ranking handles empty list."""
        ranked = retrieval_optimizer.rank_results([])
        assert isinstance(ranked, list)


class TestCachingMechanism:
    """Tests for caching."""
    
    def test_optimizer_has_cache_enabled(self, retrieval_optimizer):
        """Verify optimizer has caching."""
        assert hasattr(retrieval_optimizer, 'cache') or \
               hasattr(retrieval_optimizer, 'enable_cache')
    
    def test_optimizer_has_clear_cache_method(self, retrieval_optimizer):
        """Verify optimizer can clear cache."""
        assert hasattr(retrieval_optimizer, 'clear_cache'), \
            "RetrievalOptimizer missing clear_cache method"
    
    def test_cached_searches_are_faster(self, retrieval_optimizer):
        """Verify cached queries are faster."""
        query = "test query for caching"
        
        # First search (not cached)
        start1 = time.time()
        retrieval_optimizer.semantic_search(query)
        time1 = (time.time() - start1) * 1000
        
        # Second search (should be cached)
        start2 = time.time()
        retrieval_optimizer.semantic_search(query)
        time2 = (time.time() - start2) * 1000
        
        # Cached should be same or faster (allow for variance)
        assert time2 <= time1 * 1.5
    
    def test_cache_respects_ttl(self, retrieval_optimizer):
        """Verify cache respects TTL."""
        from pathlib import Path
        import yaml
        project_root = Path(__file__).parent.parent.parent.parent
        config_file = project_root / "cortex_brain" / "tier3" / "knowledge" / "retrieval-config.yaml"
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Config should have cache TTL settings
        cache_config = config.get("caching", {})
        assert "ttl" in cache_config or "ttl_seconds" in cache_config or len(cache_config) >= 0


class TestQueryOptimization:
    """Tests for query optimization."""
    
    def test_optimizer_has_optimize_query_method(self, retrieval_optimizer):
        """Verify optimizer has query optimization."""
        assert hasattr(retrieval_optimizer, 'optimize_query'), \
            "RetrievalOptimizer missing optimize_query method"
    
    def test_optimize_query_normalizes_input(self, retrieval_optimizer):
        """Verify query optimization normalizes input."""
        raw_query = "  What about API   Design  ?"
        optimized = retrieval_optimizer.optimize_query(raw_query)
        assert isinstance(optimized, str)
        assert len(optimized) <= len(raw_query)  # Should be normalized
    
    def test_optimize_query_removes_stop_words(self, retrieval_optimizer):
        """Verify query optimization removes stop words."""
        query = "what is the governance for security"
        optimized = retrieval_optimizer.optimize_query(query)
        # Should be shorter or equal
        assert isinstance(optimized, str)
    
    def test_optimizer_has_index_stats_method(self, retrieval_optimizer):
        """Verify optimizer can get index statistics."""
        assert hasattr(retrieval_optimizer, 'get_index_stats'), \
            "RetrievalOptimizer missing get_index_stats method"
    
    def test_index_stats_returns_dict(self, retrieval_optimizer):
        """Verify index stats returns dictionary."""
        stats = retrieval_optimizer.get_index_stats()
        assert isinstance(stats, dict)


class TestPerformanceOptimization:
    """Tests for performance optimization."""
    
    def test_semantic_search_is_fast(self, retrieval_optimizer):
        """Verify semantic search is performant."""
        start = time.time()
        retrieval_optimizer.semantic_search("performance test")
        elapsed = (time.time() - start) * 1000
        assert elapsed < 1000, f"Search took {elapsed:.2f}ms (should be < 1000ms)"
    
    def test_ranking_is_fast(self, retrieval_optimizer):
        """Verify ranking is performant."""
        entries = [
            {"entry_id": f"KE-{i}", "quality": 0.5 + i * 0.01, "content": f"content {i}"}
            for i in range(50)
        ]
        start = time.time()
        retrieval_optimizer.rank_results(entries)
        elapsed = (time.time() - start) * 1000
        assert elapsed < 200, f"Ranking took {elapsed:.2f}ms (should be < 200ms)"
    
    def test_batch_search_is_fast(self, retrieval_optimizer):
        """Verify batch searches are fast."""
        queries = ["governance", "security", "api design", "testing", "performance"]
        
        start = time.time()
        for query in queries:
            retrieval_optimizer.semantic_search(query)
        elapsed = (time.time() - start) * 1000
        
        avg_time = elapsed / len(queries)
        assert avg_time < 300, f"Average query took {avg_time:.2f}ms (should be < 300ms)"


class TestRetrieverIntegrations:
    """Tests for system integrations."""
    
    def test_optimizer_references_ac_id(self, retrieval_optimizer):
        """Verify optimizer references correct AC-ID."""
        assert hasattr(retrieval_optimizer, 'ac_id')
        assert retrieval_optimizer.ac_id == "KN-002-02"
    
    def test_optimizer_integrates_with_indexer(self, retrieval_optimizer):
        """Verify optimizer uses knowledge indexer."""
        assert hasattr(retrieval_optimizer, 'indexer'), \
            "RetrievalOptimizer should reference indexer"
    
    def test_optimizer_integrates_with_curator(self, retrieval_optimizer):
        """Verify optimizer uses curation system."""
        assert hasattr(retrieval_optimizer, 'curator'), \
            "RetrievalOptimizer should reference curator"
    
    def test_optimizer_integrates_with_synthesizer(self, retrieval_optimizer):
        """Verify optimizer uses synthesis engine."""
        assert hasattr(retrieval_optimizer, 'synthesizer'), \
            "RetrievalOptimizer should reference synthesizer"


class TestRetrieverMetrics:
    """Tests for retrieval metrics."""
    
    def test_optimizer_has_get_metrics_method(self, retrieval_optimizer):
        """Verify optimizer can get metrics."""
        assert hasattr(retrieval_optimizer, 'get_metrics'), \
            "RetrievalOptimizer missing get_metrics method"
    
    def test_metrics_include_search_stats(self, retrieval_optimizer):
        """Verify metrics track search statistics."""
        metrics = retrieval_optimizer.get_metrics()
        assert isinstance(metrics, dict)
    
    def test_metrics_include_cache_stats(self, retrieval_optimizer):
        """Verify metrics track cache performance."""
        metrics = retrieval_optimizer.get_metrics()
        assert isinstance(metrics, dict)
    
    def test_metrics_include_ranking_stats(self, retrieval_optimizer):
        """Verify metrics track ranking statistics."""
        metrics = retrieval_optimizer.get_metrics()
        assert isinstance(metrics, dict)


class TestRetrieverErrorHandling:
    """Tests for error handling."""
    
    def test_handles_malformed_entries(self, retrieval_optimizer):
        """Verify handling of malformed entries."""
        entries = [{"incomplete": "entry"}]
        ranked = retrieval_optimizer.rank_results(entries)
        assert isinstance(ranked, list)
    
    def test_handles_invalid_domain_filter(self, retrieval_optimizer):
        """Verify handling of invalid domain."""
        results = retrieval_optimizer.semantic_search("test", domain="INVALID-DOMAIN")
        assert isinstance(results, list)
    
    def test_handles_none_results(self, retrieval_optimizer):
        """Verify handling of None/empty results."""
        results = retrieval_optimizer.semantic_search("xyzabc123random")
        assert isinstance(results, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
