"""
Unit tests for SemanticDeduplicator.

Tests semantic deduplication using sentence embeddings to remove
redundant content from responses while preserving signal.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import pytest
import numpy as np
from typing import List

from cortex.orchestrators.response.semantic_deduplicator import (
    SemanticDeduplicator,
    EmbeddingCache,
    DeduplicationMetrics,
)


class TestSemanticDeduplicator:
    """Test semantic deduplication logic."""
    
    @pytest.fixture
    def deduplicator(self) -> SemanticDeduplicator:
        """Create deduplicator instance."""
        return SemanticDeduplicator(similarity_threshold=0.85)
    
    def test_deduplicate_removes_exact_duplicates(self, deduplicator):
        """Test that exact duplicate sentences are removed."""
        text = """
        This is a sentence.
        The system uses PostgreSQL for storage.
        This is a sentence.
        """
        
        result = deduplicator.deduplicate(text)
        
        # Should keep first occurrence, remove exact duplicate
        assert result.count("This is a sentence.") == 1
        assert "PostgreSQL" in result
    
    def test_deduplicate_removes_semantic_duplicates(self, deduplicator):
        """Test that semantically similar sentences are removed."""
        text = """
        The code implements authentication.
        Authentication is implemented in the code.
        The system performs error handling gracefully.
        """
        
        result = deduplicator.deduplicate(text)
        
        # Should remove one of the authentication sentences (they're semantically identical)
        # Should keep error handling sentence (distinct meaning)
        sentence_count = len([s for s in result.split('.') if s.strip()])
        assert sentence_count == 2  # Keep 2 out of 3 sentences
        assert "error handling" in result.lower()
    
    def test_deduplicate_preserves_distinct_content(self, deduplicator):
        """Test that distinct sentences are all preserved."""
        text = """
        The system uses PostgreSQL database.
        Redis handles caching layer.
        Nginx serves as reverse proxy.
        """
        
        result = deduplicator.deduplicate(text)
        
        # All sentences are distinct, should preserve all
        assert "PostgreSQL" in result
        assert "Redis" in result
        assert "Nginx" in result
    
    def test_deduplicate_preserves_order(self, deduplicator):
        """Test that sentence order is preserved after deduplication."""
        text = """
        First sentence about databases.
        Second sentence about caching.
        Third sentence about monitoring.
        Second sentence about caching.
        """
        
        result = deduplicator.deduplicate(text)
        
        # Should preserve order: First, Second, Third (duplicate removed)
        sentences = [s.strip() for s in result.split('.') if s.strip()]
        assert len(sentences) == 3
        assert "databases" in sentences[0].lower()
        assert "caching" in sentences[1].lower()
        assert "monitoring" in sentences[2].lower()
    
    def test_deduplicate_with_custom_threshold(self):
        """Test deduplication with different similarity thresholds."""
        # Lower threshold = more aggressive deduplication
        deduplicator_aggressive = SemanticDeduplicator(similarity_threshold=0.70)
        
        text = """
        The system handles errors.
        Error handling is implemented.
        The code has documentation.
        """
        
        result = deduplicator_aggressive.deduplicate(text)
        
        # With lower threshold, should remove more
        sentence_count = len([s for s in result.split('.') if s.strip()])
        assert sentence_count <= 2
    
    def test_deduplicate_empty_text(self, deduplicator):
        """Test deduplication with empty input."""
        result = deduplicator.deduplicate("")
        assert result == ""
    
    def test_deduplicate_single_sentence(self, deduplicator):
        """Test deduplication with single sentence."""
        text = "This is a single sentence."
        result = deduplicator.deduplicate(text)
        assert result == text
    
    def test_get_similarity_matrix(self, deduplicator):
        """Test pairwise similarity matrix computation."""
        sentences = [
            "The cat sat on the mat.",
            "A feline rested on the rug.",
            "The dog ran in the park."
        ]
        
        matrix = deduplicator.get_similarity_matrix(sentences)
        
        # Matrix should be square
        assert matrix.shape == (3, 3)
        
        # Diagonal should be 1.0 (self-similarity)
        assert np.allclose(np.diag(matrix), 1.0)
        
        # First two sentences more similar than first and third
        assert matrix[0, 1] > matrix[0, 2]
    
    def test_select_representative_sentences(self, deduplicator):
        """Test selection of representative sentences from clusters."""
        sentences = [
            "This is the first sentence.",
            "This is the first sentence.",  # Exact duplicate
            "Here is a different idea.",
            "Here is a different idea.",  # Exact duplicate
        ]
        
        selected = deduplicator.select_representative_sentences(sentences)
        
        # Should select 2 representatives (one per cluster)
        assert len(selected) == 2
        assert 0 in selected or 1 in selected  # First cluster
        assert 2 in selected or 3 in selected  # Second cluster
    
    def test_deduplicate_code_examples(self, deduplicator):
        """Test deduplication preserves code examples."""
        text = """
        Here is the implementation.
        ```python
        def example():
            pass
        ```
        This shows the implementation.
        """
        
        result = deduplicator.deduplicate(text)
        
        # Code block should be preserved
        assert "```python" in result
        assert "def example():" in result
    
    def test_deduplicate_performance_large_text(self, deduplicator):
        """Test deduplication performance on large text."""
        # Generate large text with some duplicates
        sentences = []
        for i in range(100):
            if i % 10 == 0:
                sentences.append("This is a duplicate sentence.")
            else:
                sentences.append(f"This is unique sentence number {i}.")
        
        text = " ".join(sentences)
        
        import time
        start = time.time()
        result = deduplicator.deduplicate(text)
        duration_ms = (time.time() - start) * 1000
        
        # First run includes model loading, subsequent runs much faster
        # Should complete in <1000ms (includes model loading overhead)
        assert duration_ms < 1000, f"Performance: {duration_ms:.1f}ms (expected <1000ms)"
        
        # Should remove duplicates
        assert result.count("This is a duplicate sentence.") == 1


class TestEmbeddingCache:
    """Test embedding caching for performance."""
    
    @pytest.fixture
    def cache(self) -> EmbeddingCache:
        """Create cache instance."""
        return EmbeddingCache(max_size=100)
    
    def test_cache_stores_embeddings(self, cache):
        """Test that cache stores and retrieves embeddings."""
        sentence = "Test sentence"
        embedding = np.array([0.1, 0.2, 0.3])
        
        cache.set(sentence, embedding)
        cached = cache.get(sentence)
        
        assert np.array_equal(cached, embedding)
    
    def test_cache_returns_none_for_missing(self, cache):
        """Test that cache returns None for cache miss."""
        result = cache.get("nonexistent")
        assert result is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = EmbeddingCache(max_size=3)
        
        # Add 4 items (should evict oldest)
        cache.set("a", np.array([1.0]))
        cache.set("b", np.array([2.0]))
        cache.set("c", np.array([3.0]))
        cache.set("d", np.array([4.0]))
        
        # "a" should be evicted
        assert cache.get("a") is None
        assert cache.get("d") is not None
    
    def test_cache_hit_rate_tracking(self, cache):
        """Test cache hit rate tracking."""
        cache.set("test", np.array([1.0]))
        
        cache.get("test")  # Hit
        cache.get("miss")  # Miss
        cache.get("test")  # Hit
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2/3


class TestDeduplicationMetrics:
    """Test deduplication metrics tracking."""
    
    @pytest.fixture
    def metrics(self) -> DeduplicationMetrics:
        """Create metrics instance."""
        return DeduplicationMetrics()
    
    def test_metrics_track_reduction_rate(self, metrics):
        """Test tracking of deduplication reduction rates."""
        metrics.record_deduplication(
            original_length=1000,
            deduplicated_length=750
        )
        
        stats = metrics.get_stats()
        assert stats["reduction_rate"] == 0.25  # 25% reduction
    
    def test_metrics_average_reduction(self, metrics):
        """Test calculation of average reduction rate."""
        metrics.record_deduplication(original_length=1000, deduplicated_length=800)
        metrics.record_deduplication(original_length=1000, deduplicated_length=600)
        
        stats = metrics.get_stats()
        # Average: (20% + 40%) / 2 = 30%
        assert abs(stats["average_reduction"] - 0.30) < 0.0001  # Floating point tolerance
    
    def test_metrics_track_call_count(self, metrics):
        """Test tracking of deduplication call count."""
        metrics.record_deduplication(original_length=100, deduplicated_length=80)
        metrics.record_deduplication(original_length=100, deduplicated_length=80)
        
        stats = metrics.get_stats()
        assert stats["total_calls"] == 2
