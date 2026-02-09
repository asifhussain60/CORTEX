# ML-based Pattern Analysis Module
# Purpose: Embeddings, similarity metrics, clustering for architectural patterns

from cortex.lens.ml_patterns.pattern_embedder import (
    PatternEmbedder,
    PatternFeatures,
    EmbeddingModel,
)

from cortex.lens.ml_patterns.similarity_clustering import (
    SimilarityAnalyzer,
    ClusteringEngine,
    ClusterResult,
)

from cortex.lens.ml_patterns.repository_fingerprinting import (
    RepositoryFingerprinter,
    RepositoryFingerprint,
    FingerprintComponent,
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
