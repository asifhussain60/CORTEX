# AC_START: AC-PHASE59-S2-002
# Similarity Metrics & Clustering Engine (Phase 59, Stage 2)
# Purpose: Implement cosine similarity, hierarchical clustering, DBSCAN, K-means

"""
Similarity Metrics and Clustering Algorithms

Provides:
1. SimilarityAnalyzer: Cosine similarity, Euclidean distance, similarity matrices
2. ClusteringEngine: Hierarchical clustering, K-means, DBSCAN
3. ClusterResult: Structured clustering output with metadata
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score, silhouette_samples
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


@dataclass
class ClusterResult:
    """
    Result of clustering operation.
    
    Attributes:
        labels: Cluster assignment for each sample
        centers: Cluster center coordinates
        n_clusters: Number of clusters
        silhouette_score: Quality metric for clustering
    """
    labels: np.ndarray
    centers: np.ndarray
    n_clusters: int
    silhouette_score: Optional[float] = None


class SimilarityAnalyzer:
    """
    Computes similarity metrics between pattern embeddings.
    
    Supports:
    - Cosine similarity (normalized dot product)
    - Euclidean distance
    - Similarity/distance matrices
    """
    
    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Cosine similarity in range [-1, 1]
        """
        # Normalize vectors
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = float(np.dot(emb1, emb2) / (norm1 * norm2))
        
        return similarity
    
    def euclidean_distance(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two embeddings.
        
        Args:
            emb1: First embedding vector
            emb2: Second embedding vector
            
        Returns:
            Euclidean distance (non-negative)
        """
        return float(np.linalg.norm(emb1 - emb2))
    
    def similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Generate pairwise similarity matrix.
        
        Args:
            embeddings: Array of shape (n_samples, n_features)
            
        Returns:
            Similarity matrix of shape (n_samples, n_samples)
        """
        n_samples = embeddings.shape[0]
        sim_matrix = np.zeros((n_samples, n_samples), dtype=np.float32)
        
        for i in range(n_samples):
            for j in range(n_samples):
                sim_matrix[i, j] = self.cosine_similarity(
                    embeddings[i], embeddings[j]
                )
        
        return sim_matrix
    
    def distance_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Generate pairwise distance matrix.
        
        Args:
            embeddings: Array of shape (n_samples, n_features)
            
        Returns:
            Distance matrix of shape (n_samples, n_samples)
        """
        n_samples = embeddings.shape[0]
        dist_matrix = np.zeros((n_samples, n_samples), dtype=np.float32)
        
        for i in range(n_samples):
            for j in range(n_samples):
                dist_matrix[i, j] = self.euclidean_distance(
                    embeddings[i], embeddings[j]
                )
        
        return dist_matrix


class ClusteringEngine:
    """
    Performs clustering on pattern embeddings.
    
    Supports:
    - Hierarchical clustering (Ward linkage)
    - K-means clustering
    - DBSCAN (density-based)
    - Optimal cluster detection (elbow method)
    """
    
    def __init__(self, random_state: int = 42):
        """
        Initialize clustering engine.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.analyzer = SimilarityAnalyzer()
    
    def hierarchical_clustering(
        self, embeddings: np.ndarray, n_clusters: int = 3
    ) -> ClusterResult:
        """
        Perform hierarchical clustering.
        
        Args:
            embeddings: Array of shape (n_samples, n_features)
            n_clusters: Number of clusters to form
            
        Returns:
            ClusterResult with cluster assignments
        """
        # Calculate linkage matrix using Ward method
        linkage_matrix = linkage(embeddings, method="ward")
        
        # Cut dendrogram to get cluster labels
        labels = fcluster(linkage_matrix, n_clusters, criterion="maxclust") - 1
        
        # Calculate cluster centers
        centers = np.zeros((n_clusters, embeddings.shape[1]))
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                centers[i] = embeddings[mask].mean(axis=0)
        
        # Calculate silhouette score
        sil_score = silhouette_score(embeddings, labels)
        
        return ClusterResult(
            labels=labels,
            centers=centers,
            n_clusters=n_clusters,
            silhouette_score=sil_score,
        )
    
    def kmeans_clustering(
        self, embeddings: np.ndarray, n_clusters: int = 3
    ) -> ClusterResult:
        """
        Perform K-means clustering.
        
        Args:
            embeddings: Array of shape (n_samples, n_features)
            n_clusters: Number of clusters (K)
            
        Returns:
            ClusterResult with cluster assignments
        """
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=self.random_state,
            n_init=10,
        )
        labels = kmeans.fit_predict(embeddings)
        
        # Calculate silhouette score
        sil_score = silhouette_score(embeddings, labels)
        
        return ClusterResult(
            labels=labels,
            centers=kmeans.cluster_centers_.astype(np.float32),
            n_clusters=n_clusters,
            silhouette_score=sil_score,
        )
    
    def dbscan_clustering(
        self,
        embeddings: np.ndarray,
        eps: float = 0.5,
        min_samples: int = 5,
    ) -> ClusterResult:
        """
        Perform DBSCAN (density-based) clustering.
        
        Args:
            embeddings: Array of shape (n_samples, n_features)
            eps: Maximum distance between samples
            min_samples: Minimum samples in neighborhood
            
        Returns:
            ClusterResult with cluster assignments
        """
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(embeddings)
        
        # Adjust labels (-1 becomes separate cluster)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        # Calculate cluster centers (mean of each cluster)
        centers = np.zeros((n_clusters, embeddings.shape[1]))
        for i in range(n_clusters):
            mask = labels == i
            if np.any(mask):
                centers[i] = embeddings[mask].mean(axis=0)
        
        # Calculate silhouette score (ignore noise points)
        if n_clusters > 1 and len(set(labels[labels != -1])) > 1:
            valid_mask = labels != -1
            if np.sum(valid_mask) > 0:
                sil_score = silhouette_score(
                    embeddings[valid_mask], labels[valid_mask]
                )
            else:
                sil_score = -1.0
        else:
            sil_score = -1.0
        
        return ClusterResult(
            labels=labels,
            centers=centers,
            n_clusters=n_clusters,
            silhouette_score=sil_score,
        )
    
    def assign_to_clusters(
        self, samples: np.ndarray, centers: np.ndarray
    ) -> np.ndarray:
        """
        Assign samples to nearest cluster centers.
        
        Args:
            samples: Array of shape (n_samples, n_features)
            centers: Cluster centers of shape (n_clusters, n_features)
            
        Returns:
            Array of cluster assignments
        """
        distances = np.zeros((samples.shape[0], centers.shape[0]))
        
        for i, sample in enumerate(samples):
            for j, center in enumerate(centers):
                distances[i, j] = self.analyzer.euclidean_distance(
                    sample, center
                )
        
        return np.argmin(distances, axis=1)
    
    def calculate_silhouette_score(
        self, embeddings: np.ndarray, labels: np.ndarray
    ) -> float:
        """
        Calculate silhouette coefficient for clustering quality.
        
        Args:
            embeddings: Array of shape (n_samples, n_features)
            labels: Cluster assignments
            
        Returns:
            Silhouette score in range [-1, 1]
        """
        if len(set(labels)) < 2:
            return -1.0
        
        return float(silhouette_score(embeddings, labels))
    
    def find_optimal_clusters(
        self, embeddings: np.ndarray, max_k: int = 10
    ) -> int:
        """
        Find optimal number of clusters using elbow method.
        
        Args:
            embeddings: Array of shape (n_samples, n_features)
            max_k: Maximum number of clusters to try
            
        Returns:
            Optimal number of clusters
        """
        inertias = []
        
        for k in range(1, min(max_k + 1, embeddings.shape[0])):
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            kmeans.fit(embeddings)
            inertias.append(kmeans.inertia_)
        
        # Find elbow point (simple heuristic: max derivative change)
        if len(inertias) < 2:
            return int(1)
        
        # Calculate second derivative (changes in inertia slope)
        deltas = np.diff(inertias)
        second_deltas = np.diff(deltas)
        
        # Elbow is where second derivative is maximum
        if len(second_deltas) > 0:
            elbow_idx = int(np.argmax(second_deltas)) + 1
            return int(elbow_idx + 1)  # +1 because range starts at 1
        
        return int(2)


# AC_COMPLETE: AC-PHASE59-S2-002 ✅ Clustering Engine Implementation
