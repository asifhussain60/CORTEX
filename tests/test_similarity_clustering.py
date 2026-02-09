# AC_START: AC-PHASE59-S2-001
# Tests for Similarity Metrics & Clustering (Phase 59, Stage 2)
# Purpose: Validate similarity analysis and clustering algorithms

import pytest
import numpy as np
from cortex.lens.ml_patterns.similarity_clustering import (
    SimilarityAnalyzer,
    ClusteringEngine,
    ClusterResult,
)


class TestSimilarityAnalyzer:
    """Test suite for similarity metric calculations."""
    
    def test_cosine_similarity(self):
        """T1: Calculate cosine similarity between embeddings."""
        analyzer = SimilarityAnalyzer()
        
        # Create two similar embeddings
        emb1 = np.array([1, 0, 0, 1], dtype=np.float32)
        emb2 = np.array([1, 0, 0, 1], dtype=np.float32)
        
        similarity = analyzer.cosine_similarity(emb1, emb2)
        
        assert isinstance(similarity, (float, np.floating))
        assert -1.01 <= similarity <= 1.01  # Allow small floating-point error
        assert similarity == pytest.approx(1.0, abs=1e-4)
    
    def test_cosine_similarity_orthogonal(self):
        """T2: Cosine similarity for orthogonal vectors."""
        analyzer = SimilarityAnalyzer()
        
        emb1 = np.array([1, 0, 0, 0], dtype=np.float32)
        emb2 = np.array([0, 1, 0, 0], dtype=np.float32)
        
        similarity = analyzer.cosine_similarity(emb1, emb2)
        
        assert similarity == pytest.approx(0.0, abs=1e-4)
    
    def test_euclidean_distance(self):
        """T3: Calculate Euclidean distance between embeddings."""
        analyzer = SimilarityAnalyzer()
        
        emb1 = np.array([0, 0, 0], dtype=np.float32)
        emb2 = np.array([3, 4, 0], dtype=np.float32)
        
        distance = analyzer.euclidean_distance(emb1, emb2)
        
        assert distance == pytest.approx(5.0, abs=1e-5)
    
    def test_similarity_matrix(self):
        """T4: Generate similarity matrix for embeddings batch."""
        analyzer = SimilarityAnalyzer()
        
        embeddings = np.array([
            [1, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ], dtype=np.float32)
        
        sim_matrix = analyzer.similarity_matrix(embeddings)
        
        assert sim_matrix.shape == (3, 3)
        assert sim_matrix[0, 0] == pytest.approx(1.0, abs=1e-5)
        assert sim_matrix[0, 2] == pytest.approx(0.0, abs=1e-4)
        
    def test_distance_matrix(self):
        """T5: Generate distance matrix for embeddings batch."""
        analyzer = SimilarityAnalyzer()
        
        embeddings = np.array([
            [0, 0],
            [3, 4],
        ], dtype=np.float32)
        
        dist_matrix = analyzer.distance_matrix(embeddings)
        
        assert dist_matrix.shape == (2, 2)
        assert dist_matrix[0, 1] == pytest.approx(5.0, abs=1e-5)
        assert dist_matrix[1, 0] == pytest.approx(5.0, abs=1e-5)


class TestClusteringEngine:
    """Test suite for clustering algorithms."""
    
    def test_hierarchical_clustering(self):
        """T6: Perform hierarchical clustering."""
        engine = ClusteringEngine()
        
        embeddings = np.array([
            [1, 0, 0],  # Group 1
            [1, 0, 0],  # Group 1
            [0, 1, 0],  # Group 2
            [0, 1, 0],  # Group 2
        ], dtype=np.float32)
        
        result = engine.hierarchical_clustering(
            embeddings, n_clusters=2
        )
        
        assert isinstance(result, ClusterResult)
        assert len(result.labels) == 4
        assert len(set(result.labels)) == 2
    
    def test_kmeans_clustering(self):
        """T7: Perform K-means clustering."""
        engine = ClusteringEngine()
        
        embeddings = np.array([
            [0, 0],
            [0.1, 0.1],
            [10, 10],
            [10.1, 10.1],
        ], dtype=np.float32)
        
        result = engine.kmeans_clustering(
            embeddings, n_clusters=2
        )
        
        assert isinstance(result, ClusterResult)
        assert len(result.labels) == 4
        # First two should be in same cluster, last two in another
        assert result.labels[0] == result.labels[1]
        assert result.labels[2] == result.labels[3]
    
    def test_dbscan_clustering(self):
        """T8: Perform DBSCAN clustering."""
        engine = ClusteringEngine()
        
        embeddings = np.array([
            [0, 0],
            [0.1, 0.1],
            [10, 10],
            [10.1, 10.1],
        ], dtype=np.float32)
        
        result = engine.dbscan_clustering(
            embeddings, eps=1.0, min_samples=2
        )
        
        assert isinstance(result, ClusterResult)
        assert len(result.labels) == 4
    
    def test_cluster_result_metadata(self):
        """T9: Verify ClusterResult contains all metadata."""
        labels = np.array([0, 0, 1, 1])
        centers = np.array([[0.5, 0.5], [10.5, 10.5]], dtype=np.float32)
        n_clusters = 2
        silhouette = 0.85
        
        result = ClusterResult(
            labels=labels,
            centers=centers,
            n_clusters=n_clusters,
            silhouette_score=silhouette,
        )
        
        assert result.n_clusters == 2
        assert result.silhouette_score == 0.85
        assert len(result.centers) == 2
    
    def test_cluster_assignment(self):
        """T10: Assign samples to existing cluster centers."""
        engine = ClusteringEngine()
        
        centers = np.array([[0, 0], [10, 10]], dtype=np.float32)
        samples = np.array([
            [0.1, 0.1],
            [10.1, 10.1],
        ], dtype=np.float32)
        
        labels = engine.assign_to_clusters(samples, centers)
        
        assert len(labels) == 2
        assert labels[0] != labels[1]
    
    def test_silhouette_score(self):
        """T11: Calculate silhouette score for clustering."""
        engine = ClusteringEngine()
        
        embeddings = np.array([
            [0, 0],
            [0.1, 0.1],
            [10, 10],
            [10.1, 10.1],
        ], dtype=np.float32)
        
        labels = np.array([0, 0, 1, 1])
        
        score = engine.calculate_silhouette_score(embeddings, labels)
        
        assert isinstance(score, float)
        assert -1 <= score <= 1
    
    def test_optimal_clusters(self):
        """T12: Find optimal number of clusters using elbow method."""
        engine = ClusteringEngine()
        
        embeddings = np.array([
            [0, 0],
            [0.1, 0.1],
            [10, 10],
            [10.1, 10.1],
        ], dtype=np.float32)
        
        optimal_k = engine.find_optimal_clusters(
            embeddings, max_k=3
        )
        
        assert isinstance(optimal_k, (int, np.integer))
        assert 1 <= optimal_k <= 3


# AC_COMPLETE: AC-PHASE59-S2-001 ✅ 12/12 tests
