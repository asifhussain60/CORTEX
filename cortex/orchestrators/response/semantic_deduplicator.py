"""
Semantic Deduplicator for CORTEX Response Optimization.

Removes semantically redundant sentences from responses using
sentence embeddings and similarity analysis.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import re
import time
from typing import List, Tuple, Dict, Any, Optional
from collections import OrderedDict
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None  # type: ignore
    cosine_similarity = None  # type: ignore


class EmbeddingCache:
    """
    LRU cache for sentence embeddings.
    
    Caches computed embeddings to avoid redundant model inference.
    Uses OrderedDict for LRU eviction policy.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize embedding cache.
        
        Args:
            max_size: Maximum number of embeddings to cache
        """
        self.max_size = max_size
        self._cache: OrderedDict[str, NDArray] = OrderedDict()
        self._hits = 0
        self._misses = 0
    
    def get(self, sentence: str) -> Optional[NDArray]:
        """
        Retrieve embedding from cache.
        
        Args:
            sentence: Sentence to look up
            
        Returns:
            Cached embedding or None if not found
        """
        if sentence in self._cache:
            self._hits += 1
            # Move to end (most recently used)
            self._cache.move_to_end(sentence)
            return self._cache[sentence]
        else:
            self._misses += 1
            return None
    
    def set(self, sentence: str, embedding: NDArray) -> None:
        """
        Store embedding in cache.
        
        Args:
            sentence: Sentence key
            embedding: Sentence embedding vector
        """
        if sentence in self._cache:
            # Update and move to end
            self._cache.move_to_end(sentence)
        else:
            # Add new entry
            self._cache[sentence] = embedding
            
            # Evict oldest if over capacity
            if len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with hits, misses, hit_rate, size
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "size": len(self._cache),
            "max_size": self.max_size
        }


@dataclass
class DeduplicationMetrics:
    """
    Metrics for deduplication performance tracking.
    
    Tracks reduction rates, call counts, and performance stats.
    """
    
    total_calls: int = 0
    total_original_length: int = 0
    total_deduplicated_length: int = 0
    reduction_rates: List[float] = field(default_factory=list)
    
    def record_deduplication(
        self,
        original_length: int,
        deduplicated_length: int
    ) -> None:
        """
        Record deduplication operation.
        
        Args:
            original_length: Length of original text
            deduplicated_length: Length after deduplication
        """
        self.total_calls += 1
        self.total_original_length += original_length
        self.total_deduplicated_length += deduplicated_length
        
        reduction_rate = (original_length - deduplicated_length) / original_length
        self.reduction_rates.append(reduction_rate)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get deduplication statistics.
        
        Returns:
            Dict with reduction metrics
        """
        if not self.reduction_rates:
            return {
                "total_calls": 0,
                "reduction_rate": 0.0,
                "average_reduction": 0.0
            }
        
        return {
            "total_calls": self.total_calls,
            "reduction_rate": self.reduction_rates[-1],
            "average_reduction": np.mean(self.reduction_rates),
            "total_original_length": self.total_original_length,
            "total_deduplicated_length": self.total_deduplicated_length
        }


class SemanticDeduplicator:
    """
    Semantic deduplication using sentence embeddings.
    
    Removes semantically redundant sentences while preserving
    unique information and maintaining natural flow.
    
    Example:
        >>> deduplicator = SemanticDeduplicator(similarity_threshold=0.85)
        >>> text = "The code works. The implementation functions correctly."
        >>> result = deduplicator.deduplicate(text)
        >>> # Returns: "The code works." (removes semantic duplicate)
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.85,
        model_name: str = "all-MiniLM-L6-v2",
        cache_size: int = 1000
    ):
        """
        Initialize semantic deduplicator.
        
        Args:
            similarity_threshold: Similarity threshold for deduplication (0-1)
            model_name: SentenceTransformer model name
            cache_size: Maximum embeddings to cache
            
        Raises:
            ImportError: If sentence-transformers not installed
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        
        self.similarity_threshold = similarity_threshold
        self.model = SentenceTransformer(model_name)
        self.cache = EmbeddingCache(max_size=cache_size)
        self.metrics = DeduplicationMetrics()
    
    def deduplicate(self, text: str) -> str:
        """
        Remove semantically redundant sentences from text.
        
        Args:
            text: Input text to deduplicate
            
        Returns:
            Deduplicated text with redundant sentences removed
        """
        if not text or not text.strip():
            return text
        
        original_length = len(text)
        
        # Split into sentences (preserve code blocks)
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 1:
            return text
        
        # Select representative sentences
        selected_indices = self.select_representative_sentences(sentences)
        
        # Reconstruct text with selected sentences
        result = self._reconstruct_text(sentences, selected_indices)
        
        # Track metrics
        self.metrics.record_deduplication(
            original_length=original_length,
            deduplicated_length=len(result)
        )
        
        return result
    
    def get_similarity_matrix(self, sentences: List[str]) -> NDArray:
        """
        Compute pairwise similarity matrix for sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            NxN similarity matrix
        """
        # Get embeddings (use cache if available)
        embeddings = []
        uncached_sentences = []
        uncached_indices = []
        
        for i, sentence in enumerate(sentences):
            cached = self.cache.get(sentence)
            if cached is not None:
                embeddings.append(cached)
            else:
                # Track uncached sentences for batch encoding
                embeddings.append(None)  # Placeholder
                uncached_sentences.append(sentence)
                uncached_indices.append(i)
        
        # Batch encode uncached sentences (much faster than one-by-one)
        if uncached_sentences:
            batch_embeddings = self.model.encode(
                uncached_sentences,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Cache and insert batch embeddings
            for idx, sentence, embedding in zip(uncached_indices, uncached_sentences, batch_embeddings):
                self.cache.set(sentence, embedding)
                embeddings[idx] = embedding
        
        # Compute pairwise cosine similarity
        embeddings_array = np.array(embeddings)
        similarity_matrix = cosine_similarity(embeddings_array)
        
        return similarity_matrix
    
    def select_representative_sentences(self, sentences: List[str]) -> List[int]:
        """
        Select representative sentences from clusters.
        
        Uses greedy selection: keep first occurrence of each semantic cluster.
        
        Args:
            sentences: List of sentences
            
        Returns:
            Indices of selected sentences (in original order)
        """
        if len(sentences) <= 1:
            return list(range(len(sentences)))
        
        # Compute similarity matrix
        similarity_matrix = self.get_similarity_matrix(sentences)
        
        # Greedy selection: keep first occurrence, skip similar ones
        selected: List[int] = []
        for i in range(len(sentences)):
            # Check if similar to any already selected sentence
            is_redundant = False
            for j in selected:
                if similarity_matrix[i, j] >= self.similarity_threshold:
                    is_redundant = True
                    break
            
            if not is_redundant:
                selected.append(i)
        
        return selected
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences, preserving code blocks.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Preserve code blocks
        code_block_pattern = r'```[\s\S]*?```'
        code_blocks = re.findall(code_block_pattern, text)
        
        # Replace code blocks with placeholders
        text_with_placeholders = text
        for i, block in enumerate(code_blocks):
            placeholder = f"__CODE_BLOCK_{i}__"
            text_with_placeholders = text_with_placeholders.replace(block, placeholder)
        
        # Split on sentence boundaries
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text_with_placeholders)
        
        # Restore code blocks
        restored_sentences = []
        for sentence in sentences:
            restored = sentence
            for i, block in enumerate(code_blocks):
                placeholder = f"__CODE_BLOCK_{i}__"
                if placeholder in restored:
                    restored = restored.replace(placeholder, block)
            restored_sentences.append(restored)
        
        return [s.strip() for s in restored_sentences if s.strip()]
    
    def _reconstruct_text(
        self,
        sentences: List[str],
        selected_indices: List[int]
    ) -> str:
        """
        Reconstruct text from selected sentences.
        
        Args:
            sentences: Original sentences
            selected_indices: Indices of selected sentences
            
        Returns:
            Reconstructed text
        """
        selected_sentences = [sentences[i] for i in sorted(selected_indices)]
        return " ".join(selected_sentences)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get deduplication metrics.
        
        Returns:
            Dict with deduplication statistics
        """
        return self.metrics.get_stats()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get embedding cache statistics.
        
        Returns:
            Dict with cache performance stats
        """
        return self.cache.get_stats()
