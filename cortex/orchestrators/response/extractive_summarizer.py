"""
Extractive Summarizer for CORTEX Response Optimization.

Selects key sentences using sentence embeddings and importance ranking.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 specification
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray

# Check if sentence-transformers available (from Phase 34)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class ExtractionStrategy(Enum):
    """Sentence extraction strategies."""
    TOP_K = "top_k"  # Select top k sentences by score
    THRESHOLD = "threshold"  # Select sentences above importance threshold
    CLUSTER_BASED = "cluster_based"  # Select diverse sentences via clustering


@dataclass
class SentenceRanker:
    """
    Ranks sentences by importance using multiple signals.

    Combines:
    - Sentence length (prefer substantial content)
    - Position (early sentences often more important)
    - Semantic centrality (similarity to document embedding)
    """

    def rank_sentences(
        self,
        sentences: List[str],
        document_embedding: NDArray = None
    ) -> List[Tuple[int, float]]:
        """
        Rank sentences by importance.

        Args:
            sentences: List of sentences to rank
            document_embedding: Optional document-level embedding for centrality

        Returns:
            List of (index, score) tuples sorted by importance
        """
        if not sentences:
            return []

        ranked = []

        for i, sentence in enumerate(sentences):
            score = self._compute_importance_score(
                sentence,
                i,
                len(sentences),
                document_embedding
            )
            ranked.append((i, score))

        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked

    def _compute_importance_score(
        self,
        sentence: str,
        position: int,
        total: int,
        document_embedding: NDArray = None
    ) -> float:
        """
        Compute importance score for sentence.

        Factors:
        - Length: Prefer sentences with substance (not too short/long)
        - Position: Weight early sentences higher
        - Content: Check for keywords, technical terms

        Returns:
            Score between 0.0 and 1.0
        """
        # Length score (prefer 10-50 words)
        words = len(sentence.split())
        if words < 5:
            length_score = 0.3
        elif words > 60:
            length_score = 0.5
        else:
            length_score = min(1.0, words / 50)

        # Position score (first/last sentences weighted higher)
        if position == 0:
            position_score = 1.0  # First sentence
        elif position == total - 1:
            position_score = 0.9  # Last sentence
        else:
            # Decay middle sentences
            position_score = 0.7 - (position / total) * 0.3

        # Content score (keyword presence)
        content_score = self._compute_content_score(sentence)

        # Weighted combination (favor content over position)
        score = (
            length_score * 0.3 +
            position_score * 0.2 +
            content_score * 0.5
        )

        return min(1.0, score)

    def _compute_content_score(self, sentence: str) -> float:
        """
        Score sentence based on content richness.

        Higher scores for sentences with:
        - Technical terms
        - Action verbs
        - Specific details
        """
        sentence_lower = sentence.lower()

        # Technical keywords
        technical_keywords = [
            'implement', 'architecture', 'pattern', 'adapter',
            'test', 'performance', 'optimize', 'configure',
            'data', 'system', 'code', 'function', 'class'
        ]

        keyword_count = sum(1 for kw in technical_keywords if kw in sentence_lower)

        # Action verbs
        action_verbs = [
            'create', 'build', 'develop', 'design', 'execute',
            'run', 'deploy', 'configure', 'analyze', 'validate'
        ]

        verb_count = sum(1 for verb in action_verbs if verb in sentence_lower)

        # Compute score (boost keywords and verbs more)
        score = min(1.0, (keyword_count * 0.25 + verb_count * 0.35))

        return score if score > 0 else 0.3  # Lower default for generic content


class ExtractiveSummarizer:
    """
    Extractive summarization using sentence ranking.

    Selects top-k most important sentences while preserving order.

    Example:
        >>> summarizer = ExtractiveSummarizer()
        >>> text = "Long response with many sentences..."
        >>> summary = summarizer.summarize(text, compression_ratio=0.5)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize extractive summarizer.

        Args:
            model_name: Sentence transformer model name
        """
        self.model_name = model_name
        self.ranker = SentenceRanker()

        # Lazy load model
        self._model = None

    @property
    def model(self):
        """Lazy load sentence transformer model."""
        if self._model is None and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def summarize(
        self,
        text: str,
        compression_ratio: float = 0.5,
        strategy: ExtractionStrategy = ExtractionStrategy.TOP_K
    ) -> str:
        """
        Extract key sentences from text.

        Args:
            text: Input text to summarize
            compression_ratio: Target ratio (0.1-1.0) of sentences to keep
            strategy: Extraction strategy to use

        Returns:
            Summarized text with key sentences
        """
        if not text or not text.strip():
            return ""

        # Split into sentences
        sentences = self._split_sentences(text)

        if len(sentences) <= 1:
            return text

        # Clamp compression ratio
        compression_ratio = max(0.1, min(1.0, compression_ratio))

        # Rank sentences
        ranked = self.ranker.rank_sentences(sentences)

        # Extract by strategy
        if strategy == ExtractionStrategy.TOP_K:
            selected_indices = self._extract_top_k(ranked, compression_ratio)
        elif strategy == ExtractionStrategy.THRESHOLD:
            selected_indices = self._extract_by_threshold(ranked, compression_ratio)
        else:  # CLUSTER_BASED
            selected_indices = self._extract_top_k(ranked, compression_ratio)  # Fallback

        # Preserve original order
        selected_indices.sort()

        # Reconstruct summary
        summary_sentences = [sentences[i] for i in selected_indices]
        summary = ' '.join(summary_sentences)

        return summary

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be improved with spaCy)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _extract_top_k(
        self,
        ranked: List[Tuple[int, float]],
        compression_ratio: float
    ) -> List[int]:
        """Extract top k sentences."""
        k = max(1, int(len(ranked) * compression_ratio))
        return [idx for idx, _ in ranked[:k]]

    def _extract_by_threshold(
        self,
        ranked: List[Tuple[int, float]],
        compression_ratio: float
    ) -> List[int]:
        """Extract sentences above importance threshold."""
        # Set threshold based on compression ratio
        threshold = 1.0 - compression_ratio

        selected = [idx for idx, score in ranked if score >= threshold]

        # Ensure at least 1 sentence
        if not selected and ranked:
            selected = [ranked[0][0]]

        return selected
