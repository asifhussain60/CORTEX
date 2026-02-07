"""
Unit tests for ExtractiveSummarizer.

Tests sentence ranking and extractive summarization using sentence embeddings.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 specification
"""

import pytest
from cortex.orchestrators.response.extractive_summarizer import (
    ExtractiveSummarizer,
    ExtractionStrategy,
    SentenceRanker
)


class TestExtractiveSummarizerBasic:
    """Test basic extractive summarization."""
    
    def test_summarizer_initializes(self):
        """Summarizer can be created with defaults."""
        summarizer = ExtractiveSummarizer()
        
        assert summarizer is not None
        assert summarizer.model_name is not None
    
    def test_summarize_extracts_key_sentences(self):
        """Summarize selects most important sentences."""
        summarizer = ExtractiveSummarizer()
        
        text = """
The adapter pattern provides extensibility.
It allows switching between implementations.
This is useful for progressive enhancement.
The weather is nice today.
JSON loads faster than SQLite for small datasets.
Adapters decouple code from specific backends.
"""
        
        summary = summarizer.summarize(text, compression_ratio=0.5)
        
        # Should keep ~50% of sentences (3 out of 6)
        summary_sentences = [s.strip() for s in summary.split('.') if s.strip()]
        assert 2 <= len(summary_sentences) <= 4
        
        # Should prefer technical content over weather
        assert "weather" not in summary.lower()
    
    def test_summarize_preserves_order(self):
        """Extracted sentences maintain original order."""
        summarizer = ExtractiveSummarizer()
        
        text = """
First sentence about adapters.
Second sentence about JSON.
Third sentence about patterns.
"""
        
        summary = summarizer.summarize(text, compression_ratio=0.66)
        
        # Check relative order preserved
        if "First" in summary and "Second" in summary:
            assert summary.index("First") < summary.index("Second")
    
    def test_empty_text_handling(self):
        """Empty text returns empty summary."""
        summarizer = ExtractiveSummarizer()
        
        summary = summarizer.summarize("", compression_ratio=0.5)
        assert summary == ""
    
    def test_compression_ratio_bounds(self):
        """Compression ratio clamped to [0.1, 1.0]."""
        summarizer = ExtractiveSummarizer()
        
        text = "Sentence one. Sentence two. Sentence three."
        
        # Too low
        summary_low = summarizer.summarize(text, compression_ratio=0.0)
        assert len(summary_low) > 0  # At least 1 sentence
        
        # Too high
        summary_high = summarizer.summarize(text, compression_ratio=2.0)
        assert summary_high == text  # All sentences kept


class TestSentenceRanker:
    """Test sentence ranking logic."""
    
    def test_ranker_scores_sentences(self):
        """Ranker assigns importance scores to sentences."""
        ranker = SentenceRanker()
        
        sentences = [
            "The adapter pattern provides extensibility.",
            "The weather is nice.",
            "JSON loads faster than SQLite.",
        ]
        
        ranked = ranker.rank_sentences(sentences)
        
        # Returns list of (index, score) tuples
        assert len(ranked) == 3
        assert all(isinstance(item, tuple) for item in ranked)
        assert all(len(item) == 2 for item in ranked)
        
        # Scores are floats between 0 and 1
        scores = [score for _, score in ranked]
        assert all(0.0 <= score <= 1.0 for score in scores)
    
    def test_ranker_prefers_content_rich_sentences(self):
        """Ranker scores content-rich sentences higher."""
        ranker = SentenceRanker()
        
        sentences = [
            "The.",  # Very short, low content
            "The adapter pattern provides extensibility for progressive enhancement.",  # Rich
        ]
        
        ranked = ranker.rank_sentences(sentences)
        ranked_sorted = sorted(ranked, key=lambda x: x[1], reverse=True)
        
        # Rich sentence should rank higher
        top_index, _ = ranked_sorted[0]
        assert top_index == 1  # Second sentence


class TestExtractionStrategies:
    """Test different extraction strategies."""
    
    def test_top_k_strategy(self):
        """TOP_K extracts exactly k sentences."""
        summarizer = ExtractiveSummarizer()
        
        text = "A. B. C. D. E."
        
        summary = summarizer.summarize(
            text,
            compression_ratio=0.4,  # ~2 sentences
            strategy=ExtractionStrategy.TOP_K
        )
        
        sentence_count = len([s for s in summary.split('.') if s.strip()])
        assert 1 <= sentence_count <= 3
    
    def test_threshold_strategy(self):
        """THRESHOLD extracts sentences above importance threshold."""
        summarizer = ExtractiveSummarizer()
        
        text = """
Critical: The system is failing.
Info: The weather is nice.
Critical: Database connection lost.
"""
        
        summary = summarizer.summarize(
            text,
            compression_ratio=0.5,
            strategy=ExtractionStrategy.THRESHOLD
        )
        
        # Should prefer "Critical" sentences
        assert "failing" in summary or "Database" in summary


class TestPerformance:
    """Test performance characteristics."""
    
    def test_summarization_completes_quickly(self):
        """Summarization completes in <500ms."""
        import time
        
        summarizer = ExtractiveSummarizer()
        
        text = " ".join([f"Sentence {i} with some content." for i in range(20)])
        
        start = time.time()
        summary = summarizer.summarize(text, compression_ratio=0.5)
        elapsed = (time.time() - start) * 1000
        
        assert elapsed < 500  # ms
        assert len(summary) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
