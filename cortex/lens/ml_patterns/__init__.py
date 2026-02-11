# ML-based Pattern Analysis Module
# Purpose: Embeddings, similarity metrics, clustering for architectural patterns

from cortex.lens.ml_patterns.pattern_embedder import (
    EmbeddingModel,
    PatternEmbedder,
    PatternFeatures,
)
from cortex.lens.ml_patterns.repository_fingerprinting import (
    FingerprintComponent,
    RepositoryFingerprint,
    RepositoryFingerprinter,
)
from cortex.lens.ml_patterns.similarity_clustering import (
    ClusteringEngine,
    ClusterResult,
    SimilarityAnalyzer,
)

__all__ = [
    "PatternEmbedder",
    "PatternFeatures",
    "EmbeddingModel",
    "SimilarityAnalyzer",
    "ClusteringEngine",
    "ClusterResult",
    "RepositoryFingerprinter",
    "RepositoryFingerprint",
    "FingerprintComponent",
]
