# AC_START: AC-PHASE59-S1-001
# Tests for Pattern Embedding Model (Phase 59, Stage 1)
# Purpose: Validate pattern feature extraction and embedding functionality

import pytest
import numpy as np
from pathlib import Path
from cortex.lens.ml_patterns.pattern_embedder import (
    PatternEmbedder,
    PatternFeatures,
    EmbeddingModel,
)


class TestPatternFeatures:
    """Test suite for pattern feature extraction."""
    
    def test_extract_basic_features(self):
        """T1: Extract basic statistical features from pattern data."""
        features = PatternFeatures(
            pattern_type="architecture",
            lines_of_code=1500,
            cyclomatic_complexity=8.5,
            modularity_score=0.78,
            coupling_score=0.45,
            cohesion_score=0.82,
        )
        
        assert features.pattern_type == "architecture"
        assert features.lines_of_code == 1500
        assert features.cyclomatic_complexity == 8.5
        assert features.modularity_score == 0.78
        
    def test_normalize_features(self):
        """T2: Normalize features to [0, 1] range."""
        features = PatternFeatures(
            pattern_type="design_pattern",
            lines_of_code=2000,
            cyclomatic_complexity=12.0,
            modularity_score=0.85,
            coupling_score=0.30,
            cohesion_score=0.90,
        )
        
        embedder = PatternEmbedder()
        normalized = embedder.normalize_features(features)
        
        # All normalized values should be in [0, 1]
        assert 0 <= normalized["lines_of_code"] <= 1
        assert 0 <= normalized["cyclomatic_complexity"] <= 1
        assert 0 <= normalized["modularity_score"] <= 1
        
    def test_invalid_feature_range(self):
        """T3: Reject features outside valid ranges."""
        with pytest.raises(ValueError):
            PatternFeatures(
                pattern_type="invalid_type",
                lines_of_code=-100,  # Invalid
                cyclomatic_complexity=5.0,
                modularity_score=0.5,
                coupling_score=0.5,
                cohesion_score=0.5,
            )


class TestPatternEmbedding:
    """Test suite for pattern embedding generation."""
    
    def test_generate_embedding_vector(self):
        """T4: Generate embedding vector from features."""
        embedder = PatternEmbedder()
        features = PatternFeatures(
            pattern_type="architecture",
            lines_of_code=1500,
            cyclomatic_complexity=8.5,
            modularity_score=0.78,
            coupling_score=0.45,
            cohesion_score=0.82,
        )
        
        embedding = embedder.embed_pattern(features)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0  # Non-empty vector
        assert np.all((embedding >= -1) & (embedding <= 1))  # Normalized
        
    def test_embedding_dimensionality(self):
        """T5: Verify embedding dimensionality is consistent."""
        embedder = PatternEmbedder(embedding_dim=32)
        
        features1 = PatternFeatures(
            pattern_type="architecture",
            lines_of_code=1000,
            cyclomatic_complexity=5.0,
            modularity_score=0.7,
            coupling_score=0.4,
            cohesion_score=0.8,
        )
        
        features2 = PatternFeatures(
            pattern_type="design",
            lines_of_code=2000,
            cyclomatic_complexity=10.0,
            modularity_score=0.8,
            coupling_score=0.3,
            cohesion_score=0.9,
        )
        
        embed1 = embedder.embed_pattern(features1)
        embed2 = embedder.embed_pattern(features2)
        
        assert embed1.shape == embed2.shape
        assert embed1.shape[0] == 32  # Custom dimension
        
    def test_similar_patterns_similar_embeddings(self):
        """T6: Similar patterns should have similar embeddings."""
        embedder = PatternEmbedder()
        
        # Very similar features
        features1 = PatternFeatures(
            pattern_type="architecture",
            lines_of_code=1500,
            cyclomatic_complexity=8.0,
            modularity_score=0.78,
            coupling_score=0.45,
            cohesion_score=0.82,
        )
        
        features2 = PatternFeatures(
            pattern_type="architecture",
            lines_of_code=1510,
            cyclomatic_complexity=8.1,
            modularity_score=0.77,
            coupling_score=0.46,
            cohesion_score=0.81,
        )
        
        embed1 = embedder.embed_pattern(features1)
        embed2 = embedder.embed_pattern(features2)
        
        # Calculate cosine similarity
        similarity = np.dot(embed1, embed2) / (
            np.linalg.norm(embed1) * np.linalg.norm(embed2)
        )
        
        assert similarity > 0.9  # Should be very similar
        
    def test_different_patterns_different_embeddings(self):
        """T7: Different patterns should have different embeddings."""
        embedder = PatternEmbedder()
        
        features1 = PatternFeatures(
            pattern_type="architecture",
            lines_of_code=500,
            cyclomatic_complexity=3.0,
            modularity_score=0.9,
            coupling_score=0.1,
            cohesion_score=0.95,
        )
        
        features2 = PatternFeatures(
            pattern_type="design",
            lines_of_code=5000,
            cyclomatic_complexity=20.0,
            modularity_score=0.5,
            coupling_score=0.8,
            cohesion_score=0.4,
        )
        
        embed1 = embedder.embed_pattern(features1)
        embed2 = embedder.embed_pattern(features2)
        
        similarity = np.dot(embed1, embed2) / (
            np.linalg.norm(embed1) * np.linalg.norm(embed2)
        )
        
        assert similarity < 0.7  # Should be different


class TestEmbeddingModel:
    """Test suite for ML embedding model."""
    
    def test_initialize_embedding_model(self):
        """T8: Initialize ML embedding model."""
        model = EmbeddingModel(embedding_dim=64, dropout=0.1)
        
        assert model.embedding_dim == 64
        assert model.dropout == 0.1
        
    def test_model_forward_pass(self):
        """T9: Test model forward pass with feature vectors."""
        model = EmbeddingModel(embedding_dim=32)
        
        # Create batch of feature vectors
        features_batch = [
            [0.5, 0.3, 0.7, 0.4, 0.8],
            [0.6, 0.2, 0.8, 0.5, 0.7],
            [0.4, 0.4, 0.6, 0.3, 0.9],
        ]
        
        embeddings = model.embed_batch(np.array(features_batch))
        
        assert embeddings.shape == (3, 32)
        assert np.all((embeddings >= -1) & (embeddings <= 1))
        
    def test_model_persistence(self):
        """T10: Save and load embedding model."""
        import tempfile
        import os
        
        model = EmbeddingModel(embedding_dim=32)
        
        # Create temp directory (not file)
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, "model.pt")
            model.save(model_path)
            
            # Load model
            loaded_model = EmbeddingModel.load(model_path)
            
            assert loaded_model.embedding_dim == 32
            
            # Clean up
            if os.path.exists(model_path):
                os.remove(model_path)


# AC_COMPLETE: AC-PHASE59-S1-001 ✅ 10/10 tests
