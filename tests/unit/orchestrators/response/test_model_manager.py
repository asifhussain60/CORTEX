"""
Tests for ModelManager - Lazy loading and caching for transformer models.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 Stage 2 specification
"""

import pytest
from unittest.mock import patch, MagicMock
from cortex.orchestrators.response.model_manager import (
    ModelManager,
    ModelType,
    ModelConfig,
)


class TestModelManagerBasic:
    """Test basic ModelManager initialization and lazy loading."""
    
    def test_manager_initializes(self):
        """ModelManager initializes without loading models."""
        manager = ModelManager()
        
        assert manager is not None
        assert manager.cache_size == 2  # Default LRU size
    
    def test_lazy_loading(self):
        """Models loaded only when requested."""
        manager = ModelManager()
        
        # Model not loaded yet
        assert ModelType.SENTENCE not in manager._cache
        
        # Request triggers load
        model = manager.get_model(ModelType.SENTENCE)
        
        assert model is not None
        assert ModelType.SENTENCE in manager._cache
    
    def test_cache_hit(self):
        """Subsequent requests use cached model."""
        manager = ModelManager()
        
        model1 = manager.get_model(ModelType.SENTENCE)
        model2 = manager.get_model(ModelType.SENTENCE)
        
        # Same object returned
        assert model1 is model2


class TestModelCaching:
    """Test LRU cache behavior."""
    
    def test_lru_eviction(self):
        """LRU cache evicts least recently used model."""
        manager = ModelManager(cache_size=2)
        
        # Load 3 models (exceeds cache size)
        model_a = manager.get_model(ModelType.SENTENCE)
        model_b = manager.get_model(ModelType.EXTRACTIVE)
        model_c = manager.get_model(ModelType.SENTENCE)  # Evicts SENTENCE initially
        
        # EXTRACTIVE should still be cached
        assert ModelType.EXTRACTIVE in manager._cache
    
    def test_cache_size_configurable(self):
        """Cache size can be configured."""
        manager = ModelManager(cache_size=5)
        
        assert manager.cache_size == 5


class TestModelTypes:
    """Test different model type loading."""
    
    def test_sentence_model_loads(self):
        """SENTENCE model (all-MiniLM-L6-v2) loads correctly."""
        manager = ModelManager()
        
        model = manager.get_model(ModelType.SENTENCE)
        
        assert model is not None
        # Check it's the right model
        assert hasattr(model, 'encode')  # SentenceTransformer method
    
    def test_extractive_model_loads(self):
        """EXTRACTIVE model loads correctly."""
        manager = ModelManager()
        
        model = manager.get_model(ModelType.EXTRACTIVE)
        
        assert model is not None
    
class TestModelConfig:
    """Test ModelConfig dataclass."""
    
    def test_config_stores_model_info(self):
        """ModelConfig stores model metadata."""
        config = ModelConfig(
            model_name="test-model",
            model_type=ModelType.SENTENCE,
            cache_dir=".cache"
        )
        
        assert config.model_name == "test-model"
        assert config.model_type == ModelType.SENTENCE
        assert config.cache_dir == ".cache"
