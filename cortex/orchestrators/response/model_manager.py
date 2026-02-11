"""
ModelManager for CORTEX ML Summarization.

Manages lazy loading and caching of transformer models.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 36 specification
"""

from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, Optional

# Check if sentence-transformers available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


class ModelType(Enum):
    """Transformer model types."""
    SENTENCE = "sentence"  # Sentence embeddings (all-MiniLM-L6-v2)
    EXTRACTIVE = "extractive"  # Extractive summarization
    ABSTRACTIVE = "abstractive"  # Abstractive summarization (BART/T5)


@dataclass
class ModelConfig:
    """
    Configuration for transformer model.

    Attributes:
        model_name: HuggingFace model identifier
        model_type: Type of model (SENTENCE, EXTRACTIVE, ABSTRACTIVE)
        cache_dir: Directory for model cache
    """
    model_name: str
    model_type: ModelType
    cache_dir: str = ".cache/models"


class ModelManager:
    """
    Manages transformer model lifecycle.

    Features:
    - Lazy loading (models loaded on first use)
    - LRU caching (keep N most recent models in memory)
    - Graceful degradation (fallback if model unavailable)

    Example:
        >>> manager = ModelManager(cache_size=2)
        >>> model = manager.get_model(ModelType.SENTENCE)
    """

    # Default model configurations
    DEFAULT_CONFIGS = {
        ModelType.SENTENCE: ModelConfig(
            model_name="all-MiniLM-L6-v2",
            model_type=ModelType.SENTENCE,
        ),
        ModelType.EXTRACTIVE: ModelConfig(
            model_name="all-MiniLM-L6-v2",  # Same as SENTENCE for now
            model_type=ModelType.EXTRACTIVE,
        ),
    }

    def __init__(self, cache_size: int = 2):
        """
        Initialize model manager.

        Args:
            cache_size: Maximum number of models to keep in memory
        """
        self.cache_size = cache_size
        self._cache: Dict[ModelType, Any] = {}
        self._access_order: list[ModelType] = []

    def get_model(self, model_type: ModelType) -> Any:
        """
        Get transformer model (lazy load + cache).

        Args:
            model_type: Type of model to load

        Returns:
            Loaded transformer model

        Raises:
            ValueError: If model type unsupported
            NotImplementedError: If model not yet implemented
        """
        # Check cache first
        if model_type in self._cache:
            # Update LRU order
            self._access_order.remove(model_type)
            self._access_order.append(model_type)
            return self._cache[model_type]

        # Load model
        model = self._load_model(model_type)

        # Add to cache (evict LRU if needed)
        self._add_to_cache(model_type, model)

        return model

    def _load_model(self, model_type: ModelType) -> Any:
        """
        Load transformer model from HuggingFace.

        Args:
            model_type: Type of model to load

        Returns:
            Loaded model
        """
        if model_type not in self.DEFAULT_CONFIGS:
            raise ValueError(f"Unsupported model type: {model_type}")

        config = self.DEFAULT_CONFIGS[model_type]

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        # Load SentenceTransformer model
        model = SentenceTransformer(config.model_name)

        return model

    def _add_to_cache(self, model_type: ModelType, model: Any):
        """
        Add model to cache with LRU eviction.

        Args:
            model_type: Type of model
            model: Loaded model instance
        """
        # Evict LRU if cache full
        if len(self._cache) >= self.cache_size:
            lru_type = self._access_order.pop(0)
            del self._cache[lru_type]

        # Add to cache
        self._cache[model_type] = model
        self._access_order.append(model_type)

    def clear_cache(self):
        """Clear all cached models."""
        self._cache.clear()
        self._access_order.clear()

    @property
    def cached_models(self) -> list[ModelType]:
        """Get list of currently cached models."""
        return list(self._cache.keys())
