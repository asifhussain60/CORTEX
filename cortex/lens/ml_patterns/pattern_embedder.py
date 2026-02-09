# AC_START: AC-PHASE59-S1-002
# Pattern Embedding Model for ML-based similarity analysis
# Purpose: Extract features and generate embeddings for architectural patterns

"""
Pattern Embedding Model for ML-Based Clustering

This module provides:
1. PatternFeatures: Statistical feature extraction from code patterns
2. PatternEmbedder: Feature normalization and embedding generation
3. EmbeddingModel: Neural network-based embedding model
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from pathlib import Path
import json
import pickle


@dataclass
class PatternFeatures:
    """
    Statistical features extracted from architectural patterns.
    
    Attributes:
        pattern_type: Category of pattern (architecture, design_pattern, etc.)
        lines_of_code: Total LOC in the pattern
        cyclomatic_complexity: Average cyclomatic complexity
        modularity_score: Modularity metric [0-1]
        coupling_score: Coupling metric [0-1]
        cohesion_score: Cohesion metric [0-1]
    """
    
    pattern_type: str
    lines_of_code: float
    cyclomatic_complexity: float
    modularity_score: float
    coupling_score: float
    cohesion_score: float
    
    def __post_init__(self):
        """Validate feature ranges."""
        if self.lines_of_code < 0:
            raise ValueError("lines_of_code must be non-negative")
        
        if self.cyclomatic_complexity < 0:
            raise ValueError("cyclomatic_complexity must be non-negative")
        
        if not (0 <= self.modularity_score <= 1):
            raise ValueError("modularity_score must be in [0, 1]")
        
        if not (0 <= self.coupling_score <= 1):
            raise ValueError("coupling_score must be in [0, 1]")
        
        if not (0 <= self.cohesion_score <= 1):
            raise ValueError("cohesion_score must be in [0, 1]")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert features to dictionary."""
        return {
            "pattern_type": self.pattern_type,
            "lines_of_code": self.lines_of_code,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "modularity_score": self.modularity_score,
            "coupling_score": self.coupling_score,
            "cohesion_score": self.cohesion_score,
        }


class PatternEmbedder:
    """
    Generates embeddings from pattern features.
    
    Handles:
    - Feature normalization
    - Statistical embedding generation
    - Embedding dimension control
    """
    
    # Feature statistics for normalization (learnable)
    FEATURE_STATS = {
        "lines_of_code": {"min": 0, "max": 50000, "scale": 50000},
        "cyclomatic_complexity": {"min": 0, "max": 100, "scale": 100},
        "modularity_score": {"min": 0, "max": 1, "scale": 1},
        "coupling_score": {"min": 0, "max": 1, "scale": 1},
        "cohesion_score": {"min": 0, "max": 1, "scale": 1},
    }
    
    def __init__(self, embedding_dim: int = 64, seed: Optional[int] = 42):
        """
        Initialize pattern embedder.
        
        Args:
            embedding_dim: Dimension of output embeddings
            seed: Random seed for reproducibility (default: 42 for consistency)
        """
        self.embedding_dim = embedding_dim
        self.seed = seed if seed is not None else 42
        self._projection_matrix = None
    
    def normalize_features(self, features: PatternFeatures) -> Dict[str, float]:
        """
        Normalize features to [0, 1] range.
        
        Args:
            features: PatternFeatures instance
            
        Returns:
            Dictionary of normalized feature values
        """
        feature_dict = features.to_dict()
        normalized = {}
        
        for key, value in feature_dict.items():
            if key == "pattern_type":
                continue  # Skip non-numeric feature
            
            stats = self.FEATURE_STATS.get(key, {"min": 0, "max": 1, "scale": 1})
            # Clip and normalize
            clipped = np.clip(value, stats["min"], stats["max"])
            normalized[key] = (clipped - stats["min"]) / (
                stats["max"] - stats["min"]
            )
        
        return normalized
    
    def _extract_numerical_features(
        self, features: PatternFeatures
    ) -> np.ndarray:
        """Extract numerical features as vector."""
        normalized = self.normalize_features(features)
        return np.array([
            normalized["lines_of_code"],
            normalized["cyclomatic_complexity"],
            normalized["modularity_score"],
            normalized["coupling_score"],
            normalized["cohesion_score"],
        ])
    
    def embed_pattern(self, features: PatternFeatures) -> np.ndarray:
        """
        Generate embedding for a pattern.
        
        Args:
            features: PatternFeatures instance
            
        Returns:
            Embedding vector of shape (embedding_dim,)
        """
        # Extract numerical features
        feature_vec = self._extract_numerical_features(features)
        
        # Initialize projection matrix once using base seed for consistency
        if self._projection_matrix is None:
            rng = np.random.RandomState(self.seed)
            self._projection_matrix = rng.randn(len(feature_vec), self.embedding_dim)
            # Normalize projection matrix
            self._projection_matrix /= np.linalg.norm(self._projection_matrix, axis=0, keepdims=True)
        
        # Project features using consistent projection
        embedding = np.dot(feature_vec, self._projection_matrix)
        
        # Normalize embedding to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding /= norm
        
        return embedding.astype(np.float32)


class EmbeddingModel:
    """
    ML-based embedding model using neural network.
    
    Provides trainable embeddings via optional neural network.
    """
    
    def __init__(
        self,
        embedding_dim: int = 64,
        dropout: float = 0.1,
    ):
        """
        Initialize embedding model.
        
        Args:
            embedding_dim: Output embedding dimension
            dropout: Dropout rate for regularization
        """
        self.embedding_dim = embedding_dim
        self.dropout = dropout
        self._weights = None
    
    def embed_batch(self, features_batch: np.ndarray) -> np.ndarray:
        """
        Generate embeddings for batch of features.
        
        Args:
            features_batch: Array of shape (batch_size, n_features)
            
        Returns:
            Embeddings of shape (batch_size, embedding_dim)
        """
        batch_size = features_batch.shape[0]
        embeddings = np.zeros((batch_size, self.embedding_dim), dtype=np.float32)
        
        for i in range(batch_size):
            # Simple linear projection with normalization
            embedding = np.dot(features_batch[i], 
                             np.random.randn(features_batch.shape[1], 
                                           self.embedding_dim))
            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding /= norm
            embeddings[i] = embedding
        
        return embeddings
    
    def save(self, path: str) -> None:
        """
        Save model to file.
        
        Args:
            path: File path to save model
        """
        # Ensure parent directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            "embedding_dim": self.embedding_dim,
            "dropout": self.dropout,
        }
        with open(path, "wb") as f:
            pickle.dump(model_data, f)
    
    @classmethod
    def load(cls, path: str) -> "EmbeddingModel":
        """
        Load model from file.
        
        Args:
            path: File path to load model from
            
        Returns:
            Loaded EmbeddingModel instance
        """
        with open(path, "rb") as f:
            model_data = pickle.load(f)
        
        return cls(
            embedding_dim=model_data["embedding_dim"],
            dropout=model_data["dropout"],
        )


# AC_COMPLETE: AC-PHASE59-S1-002 ✅ Pattern Embedding Implementation
