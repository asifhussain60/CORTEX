"""
ML Summarization Engine for CORTEX.

Provides semantic session summarization using ML embeddings,
context synthesis, and learning extraction.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 1 specification
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from numpy.typing import NDArray

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics.pairwise import cosine_similarity
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    SentenceTransformer = None  # type: ignore
    AgglomerativeClustering = None  # type: ignore
    cosine_similarity = None  # type: ignore

logger = logging.getLogger(__name__)


class SummaryQuality(Enum):
    """Summary quality levels."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SessionContext:
    """
    Session context tracking.

    Attributes:
        turn_count: Number of conversation turns
        total_tokens: Total tokens in session
        key_decisions: List of key decisions made
        key_implementations: List of key implementations
        key_fixes: List of key fixes applied
    """
    turn_count: int
    total_tokens: int
    key_decisions: List[str]
    key_implementations: List[str] = field(default_factory=list)
    key_fixes: List[str] = field(default_factory=list)


@dataclass
class SummaryResult:
    """
    Summarization result.

    Attributes:
        summary: Generated summary text
        key_points: Extracted key points
        quality: Summary quality level
        confidence: Confidence score (0-1)
        token_reduction: Token reduction ratio (0-1)
        session_context: Optional session context
    """
    summary: str
    key_points: List[str]
    quality: SummaryQuality
    confidence: float
    token_reduction: float
    session_context: Optional[SessionContext] = None


@dataclass
class ClusterConfig:
    """
    Clustering configuration.

    Attributes:
        min_clusters: Minimum number of clusters
        max_clusters: Maximum number of clusters
        similarity_threshold: Similarity threshold for clustering
    """
    min_clusters: int = 2
    max_clusters: int = 10
    similarity_threshold: float = 0.7


@dataclass
class SummarizationConfig:
    """
    Summarization configuration.

    Attributes:
        max_summary_length: Maximum summary length
        min_quality_score: Minimum quality score
        extract_key_points: Whether to extract key points
        include_context: Whether to include session context
    """
    max_summary_length: int = 500
    min_quality_score: float = 0.7
    extract_key_points: bool = True
    include_context: bool = True


class MLSummarizer:
    """
    ML-based session summarizer.

    Uses sentence embeddings and clustering for semantic summarization.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        config: Optional[SummarizationConfig] = None,
    ):
        """
        Initialize ML summarizer.

        Args:
            model_name: SentenceTransformer model name
            config: Summarization configuration

        Raises:
            ImportError: If dependencies not installed
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError(
                "Required dependencies not installed. "
                "Install with: pip install sentence-transformers scikit-learn"
            )

        self.model = SentenceTransformer(model_name)
        self.config = config or SummarizationConfig()

        logger.info(f"MLSummarizer initialized with model: {model_name}")

    def summarize(
        self,
        conversation: List[str],
        extract_key_points: Optional[bool] = None,
    ) -> SummaryResult:
        """
        Summarize conversation.

        Args:
            conversation: List of conversation turns
            extract_key_points: Override config for key point extraction

        Returns:
            SummaryResult: Summarization result
        """
        if not conversation:
            return SummaryResult(
                summary="",
                key_points=[],
                quality=SummaryQuality.LOW,
                confidence=0.0,
                token_reduction=0.0,
            )

        # Single turn - return as-is with low quality
        if len(conversation) == 1:
            return SummaryResult(
                summary=conversation[0],
                key_points=[conversation[0]] if extract_key_points else [],
                quality=SummaryQuality.LOW,
                confidence=0.5,
                token_reduction=0.0,
            )

        # Generate embeddings
        embeddings = self.model.encode(conversation)

        # Cluster similar content
        clusters = self._cluster_embeddings(embeddings, conversation)

        # Extract representative sentences from each cluster
        summary_sentences = self._select_representatives(clusters, embeddings, conversation)

        # Generate summary
        summary = " ".join(summary_sentences)

        # Truncate if needed
        if len(summary) > self.config.max_summary_length:
            summary = summary[:self.config.max_summary_length].rsplit(" ", 1)[0] + "..."

        # Extract key points if requested
        should_extract = extract_key_points if extract_key_points is not None else self.config.extract_key_points
        key_points = self.extract_key_points(conversation) if should_extract else []

        # Calculate quality
        original_text = " ".join(conversation)
        quality, confidence = self.calculate_quality(original_text, summary)

        # Calculate token reduction
        token_reduction = self.calculate_token_reduction(original_text, summary)

        return SummaryResult(
            summary=summary,
            key_points=key_points,
            quality=quality,
            confidence=confidence,
            token_reduction=token_reduction,
        )

    def cluster_texts(
        self,
        texts: List[str],
        config: Optional[ClusterConfig] = None,
    ) -> List[List[int]]:
        """
        Cluster texts by semantic similarity.

        Args:
            texts: List of texts to cluster
            config: Clustering configuration

        Returns:
            List[List[int]]: List of clusters (each cluster is list of indices)
        """
        if not texts:
            return []

        config = config or ClusterConfig()

        # Generate embeddings
        embeddings = self.model.encode(texts)

        # Determine number of clusters
        n_texts = len(texts)
        n_clusters = min(max(config.min_clusters, n_texts // 3), config.max_clusters, n_texts)

        if n_clusters < 2:
            return [[i for i in range(n_texts)]]

        # Perform clustering
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='cosine',
            linkage='average',
        )
        labels = clustering.fit_predict(embeddings)

        # Group by cluster
        clusters = []
        for i in range(n_clusters):
            cluster_indices = [idx for idx, label in enumerate(labels) if label == i]
            if cluster_indices:
                clusters.append(cluster_indices)

        return clusters

    def extract_key_points(
        self,
        conversation: List[str],
        max_points: int = 5,
    ) -> List[str]:
        """
        Extract key points from conversation.

        Args:
            conversation: List of conversation turns
            max_points: Maximum number of key points

        Returns:
            List[str]: Extracted key points
        """
        if not conversation:
            return []

        # Generate embeddings
        embeddings = self.model.encode(conversation)

        # Calculate centrality scores (average similarity to all other texts)
        similarity_matrix = cosine_similarity(embeddings)
        centrality_scores = similarity_matrix.mean(axis=1)

        # Select top N most central sentences as key points
        top_indices = np.argsort(centrality_scores)[-max_points:][::-1]

        # Preserve original order
        top_indices_sorted = sorted(top_indices)

        return [conversation[i] for i in top_indices_sorted]

    def calculate_quality(
        self,
        original: str,
        summary: str,
    ) -> Tuple[SummaryQuality, float]:
        """
        Calculate summary quality.

        Args:
            original: Original text
            summary: Summary text

        Returns:
            Tuple[SummaryQuality, float]: Quality level and confidence score
        """
        if not summary:
            return SummaryQuality.LOW, 0.0

        # Generate embeddings
        embeddings = self.model.encode([original, summary])

        # Calculate semantic similarity
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

        # Calculate compression ratio
        compression = 1 - (len(summary) / max(len(original), 1))

        # Quality score combines similarity and compression
        # High similarity + good compression = high quality
        quality_score = (similarity * 0.7) + (compression * 0.3)

        # Determine quality level
        if quality_score >= 0.8:
            quality = SummaryQuality.HIGH
        elif quality_score >= 0.6:
            quality = SummaryQuality.MEDIUM
        else:
            quality = SummaryQuality.LOW

        return quality, float(quality_score)

    def calculate_token_reduction(
        self,
        original: str,
        summary: str,
    ) -> float:
        """
        Calculate token reduction ratio.

        Args:
            original: Original text
            summary: Summary text

        Returns:
            float: Reduction ratio (0-1)
        """
        if not original:
            return 0.0

        # Simple approximation: tokens ≈ words
        original_tokens = len(original.split())
        summary_tokens = len(summary.split())

        if original_tokens == 0:
            return 0.0

        reduction = 1 - (summary_tokens / original_tokens)
        return max(0.0, min(1.0, reduction))

    def _cluster_embeddings(
        self,
        embeddings: NDArray,
        texts: List[str],
    ) -> List[List[int]]:
        """
        Cluster embeddings by similarity.

        Args:
            embeddings: Text embeddings
            texts: Original texts

        Returns:
            List[List[int]]: Cluster indices
        """
        n_texts = len(texts)

        # Determine number of clusters (aim for 30-50% reduction)
        n_clusters = max(2, min(n_texts // 2, 10))

        if n_clusters >= n_texts:
            return [[i] for i in range(n_texts)]

        # Perform clustering
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            metric='cosine',
            linkage='average',
        )
        labels = clustering.fit_predict(embeddings)

        # Group by cluster
        clusters = []
        for i in range(n_clusters):
            cluster_indices = [idx for idx, label in enumerate(labels) if label == i]
            if cluster_indices:
                clusters.append(cluster_indices)

        return clusters

    def _select_representatives(
        self,
        clusters: List[List[int]],
        embeddings: NDArray,
        texts: List[str],
    ) -> List[str]:
        """
        Select representative sentence from each cluster.

        Args:
            clusters: Cluster indices
            embeddings: Text embeddings
            texts: Original texts

        Returns:
            List[str]: Representative sentences
        """
        representatives = []

        for cluster_indices in clusters:
            if not cluster_indices:
                continue

            # Get cluster embeddings
            cluster_embeddings = embeddings[cluster_indices]

            # Calculate centroid
            centroid = cluster_embeddings.mean(axis=0)

            # Find most central sentence
            similarities = cosine_similarity([centroid], cluster_embeddings)[0]
            most_central_idx = cluster_indices[np.argmax(similarities)]

            representatives.append(texts[most_central_idx])

        return representatives
