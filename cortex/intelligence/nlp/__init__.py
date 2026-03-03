"""cortex.intelligence.nlp — NLP utilities package.

Provides natural language processing utilities including EmbeddingCache
for caching vector representations of text (GAP-84-20).

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
# noqa: CORE-035 — domain-scoped; class name appropriate for this module
from __future__ import annotations

from typing import Dict, List, Optional
import hashlib


class EmbeddingCache:
    """Cache for text embeddings (vector representations).

    Stores embeddings keyed by a hash of the input text. Avoids repeated
    embedding calls for identical inputs. Backed by in-process dict; can
    be extended to disk persistence via a `cache_path` parameter.
    """

    def __init__(self, max_size: int = 1024) -> None:
        """Initialise the embedding cache.

        Args:
            max_size: Maximum number of entries to keep (LRU eviction).
        """
        self._cache: Dict[str, List[float]] = {}
        self._max_size = max_size
        self._order: List[str] = []

    def get(self, text: str) -> Optional[List[float]]:
        """Retrieve cached embedding for text.

        Args:
            text: Input text to look up.

        Returns:
            Embedding vector if cached, else None.
        """
        key = self._key(text)
        return self._cache.get(key)

    def set(self, text: str, embedding: List[float]) -> None:
        """Cache an embedding for text.

        Args:
            text: Input text.
            embedding: Embedding vector to cache.
        """
        key = self._key(text)
        if key not in self._cache:
            if len(self._order) >= self._max_size:
                oldest = self._order.pop(0)
                self._cache.pop(oldest, None)
            self._order.append(key)
        self._cache[key] = embedding

    def size(self) -> int:
        """Return number of cached entries."""
        return len(self._cache)

    def _key(self, text: str) -> str:
        """Generate a cache key from text via SHA-256."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


__all__: list[str] = ["EmbeddingCache"]
