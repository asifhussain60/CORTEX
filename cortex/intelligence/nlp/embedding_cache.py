"""embedding_cache.py — Embedding Cache — LRU cache for text embeddings."""
from __future__ import annotations
from typing import Any


class EmbeddingCache:
    """Caches text embeddings for reuse across requests."""

    def __init__(self) -> None:
        """Initialise empty embedding cache."""
        self._cache: dict[str, list[float]] = {}

    def get(self, text: str) -> list[float] | None:
        """Get cached embedding for text.

        Args:
            text: Input text string.

        Returns:
            Cached embedding or None.
        """
        return self._cache.get(text)

    def set(self, text: str, embedding: list[float]) -> None:
        """Cache an embedding for text.

        Args:
            text: Input text string.
            embedding: Embedding vector.
        """
        self._cache[text] = embedding
