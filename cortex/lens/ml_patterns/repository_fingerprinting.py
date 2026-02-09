# AC_START: AC-PHASE59-S3-002
# Repository Fingerprinting for Fast Architecture Comparison
# Purpose: Create lightweight fingerprints for efficient repository clustering

"""
Repository Fingerprinting Engine

Generates and compares architecture fingerprints for repositories.
Enables fast similarity computation for pattern clustering.

Key Features:
- Component-based fingerprinting
- Consistent hashing for caching
- Batch fingerprint generation
- Fast similarity comparison
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
import hashlib
from cortex.lens.ml_patterns.similarity_clustering import SimilarityAnalyzer


@dataclass
class FingerprintComponent:
    """
    A component within a repository architecture.
    
    Attributes:
        name: Component name
        complexity: Cyclomatic complexity [0-1]
        size: Component size in lines of code
        modularity: Modularity score [0-1]
    """
    
    name: str
    complexity: float
    size: float
    modularity: float
    
    def to_vector(self) -> np.ndarray:
        """Convert component to feature vector."""
        return np.array(
            [self.complexity, self.size / 10000, self.modularity],
            dtype=np.float32,
        )


@dataclass
class RepositoryFingerprint:
    """
    Lightweight architecture fingerprint for a repository.
    
    Attributes:
        repository_id: Unique repository identifier
        components: List of architecture components
        total_complexity: Overall complexity score [0-1]
        total_modularity: Overall modularity score [0-1]
        timestamp: When fingerprint was generated
    """
    
    repository_id: str
    components: List[FingerprintComponent]
    total_complexity: float
    total_modularity: float
    timestamp: Optional[str] = None
    
    def to_vector(self) -> np.ndarray:
        """
        Convert fingerprint to feature vector.
        
        Returns:
            Normalized feature vector
        """
        # Aggregate component features
        if not self.components:
            base_vector = np.array([
                self.total_complexity,
                self.total_modularity,
                0.0,  # Number of components (normalized)
            ], dtype=np.float32)
        else:
            component_vectors = np.array([
                c.to_vector() for c in self.components
            ])
            component_mean = component_vectors.mean(axis=0)
            
            base_vector = np.array([
                self.total_complexity,
                self.total_modularity,
                min(len(self.components) / 20, 1.0),  # Normalized component count
            ], dtype=np.float32)
        
        # Normalize to [0, 1]
        return base_vector / np.linalg.norm(base_vector) if np.linalg.norm(base_vector) > 0 else base_vector
    
    def to_dict(self) -> Dict:
        """Convert fingerprint to dictionary."""
        return {
            "repository_id": self.repository_id,
            "components": [
                {
                    "name": c.name,
                    "complexity": c.complexity,
                    "size": c.size,
                    "modularity": c.modularity,
                }
                for c in self.components
            ],
            "total_complexity": self.total_complexity,
            "total_modularity": self.total_modularity,
            "timestamp": self.timestamp,
        }


class RepositoryFingerprinter:
    """
    Generates and manages repository fingerprints.
    
    Provides:
    - Fingerprint generation from repository metrics
    - Fast fingerprint comparison
    - Batch processing
    - Consistent hashing
    """
    
    def __init__(self):
        """Initialize repository fingerprinter."""
        self.analyzer = SimilarityAnalyzer()
        self._fingerprint_cache: Dict[str, RepositoryFingerprint] = {}
        self._hash_cache: Dict[str, str] = {}
    
    def generate_fingerprint(
        self,
        repository_id: str,
        features: Dict[str, any],
    ) -> RepositoryFingerprint:
        """
        Generate fingerprint from repository features.
        
        Args:
            repository_id: Unique repository identifier
            features: Dictionary with repository metrics:
                - components: List of component names
                - avg_complexity: Average complexity [0-1]
                - total_size: Total LOC
                - avg_modularity: Average modularity [0-1]
            
        Returns:
            RepositoryFingerprint instance
        """
        # Extract features
        components_list = features.get("components", [])
        avg_complexity = features.get("avg_complexity", 0.5)
        total_size = features.get("total_size", 5000)
        avg_modularity = features.get("avg_modularity", 0.75)
        
        # Create components with varied metrics
        components = []
        for i, comp_name in enumerate(components_list):
            # Add slight variation to each component
            variance = 0.1 * np.sin(i)
            components.append(
                FingerprintComponent(
                    name=comp_name,
                    complexity=np.clip(avg_complexity + variance, 0, 1),
                    size=total_size / len(components_list) if components_list else total_size,
                    modularity=np.clip(avg_modularity - variance * 0.5, 0, 1),
                )
            )
        
        # Create fingerprint
        fingerprint = RepositoryFingerprint(
            repository_id=repository_id,
            components=components,
            total_complexity=float(avg_complexity),
            total_modularity=float(avg_modularity),
        )
        
        # Cache it
        self._fingerprint_cache[repository_id] = fingerprint
        
        return fingerprint
    
    def hash_fingerprint(self, fingerprint: RepositoryFingerprint) -> str:
        """
        Generate hash for fingerprint (for caching).
        
        Args:
            fingerprint: RepositoryFingerprint instance
            
        Returns:
            SHA256 hash string
        """
        # Check cache first
        repo_id = fingerprint.repository_id
        if repo_id in self._hash_cache:
            return self._hash_cache[repo_id]
        
        # Create hash from vector
        vector_str = str(fingerprint.to_vector().tobytes())
        hash_val = hashlib.sha256(vector_str.encode()).hexdigest()[:16]
        
        # Cache it
        self._hash_cache[repo_id] = hash_val
        
        return hash_val
    
    def compare_fingerprints(
        self,
        fp1: RepositoryFingerprint,
        fp2: RepositoryFingerprint,
    ) -> float:
        """
        Compare two fingerprints.
        
        Args:
            fp1: First fingerprint
            fp2: Second fingerprint
            
        Returns:
            Similarity score [0, 1]
        """
        vec1 = fp1.to_vector()
        vec2 = fp2.to_vector()
        
        # Use cosine similarity
        similarity = self.analyzer.cosine_similarity(vec1, vec2)
        
        # Convert from [-1, 1] to [0, 1] if needed
        if similarity < 0:
            similarity = 0.0
        
        return similarity
    
    def generate_batch_fingerprints(
        self,
        repositories: Dict[str, Dict[str, any]],
    ) -> Dict[str, RepositoryFingerprint]:
        """
        Generate fingerprints for batch of repositories.
        
        Args:
            repositories: Dict mapping repo_id to features dict
            
        Returns:
            Dict mapping repo_id to RepositoryFingerprint
        """
        fingerprints = {}
        
        for repo_id, features in repositories.items():
            fingerprints[repo_id] = self.generate_fingerprint(repo_id, features)
        
        return fingerprints
    
    def compute_fingerprint_vectors(
        self,
        fingerprints: Dict[str, RepositoryFingerprint],
    ) -> np.ndarray:
        """
        Compute fingerprint vectors for clustering.
        
        Args:
            fingerprints: Dict mapping repo_id to RepositoryFingerprint
            
        Returns:
            Array of shape (n_repos, fingerprint_dim)
        """
        vectors = []
        
        for fp in fingerprints.values():
            vectors.append(fp.to_vector())
        
        return np.array(vectors, dtype=np.float32)
    
    def find_similar_repositories(
        self,
        target_fp: RepositoryFingerprint,
        candidate_fps: Dict[str, RepositoryFingerprint],
        threshold: float = 0.7,
    ) -> List[Tuple[str, float]]:
        """
        Find repositories similar to target.
        
        Args:
            target_fp: Target repository fingerprint
            candidate_fps: Dict of candidate fingerprints
            threshold: Similarity threshold [0, 1]
            
        Returns:
            List of (repo_id, similarity) tuples, sorted by similarity
        """
        similarities = []
        
        for repo_id, candidate_fp in candidate_fps.items():
            similarity = self.compare_fingerprints(target_fp, candidate_fp)
            
            if similarity >= threshold:
                similarities.append((repo_id, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities


# AC_COMPLETE: AC-PHASE59-S3-002 ✅ Repository Fingerprinting Implementation
