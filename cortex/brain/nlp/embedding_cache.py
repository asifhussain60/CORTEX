"""
Phase 8.4: Lightweight Embedding Cache

Simple in-memory cache for text embeddings to avoid redundant computations.
Optional component for semantic ranking enhancement.

AC-ID: AC-PHASE-8.4-01 (Task NLP-001)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from typing import List, Dict, Any, Optional
import hashlib
import time
from dataclasses import dataclass
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class CacheEntry:
    """
    Cache entry for text embedding.
    
    Attributes:
        text: Original text
        embedding: Computed embedding vector
        timestamp: Cache creation timestamp
        hits: Number of cache hits
    """
    text: str
    embedding: List[float]
    timestamp: float
    hits: int = 0


class EmbeddingCache:
    """
    In-memory cache for text embeddings.
    
    Features:
    - Hash-based lookup
    - LRU eviction
    - Hit rate tracking
    - TTL expiration
    
    Example:
        cache = EmbeddingCache(max_size=1000, ttl_seconds=3600)
        
        # Check cache
        embedding = cache.get("implement feature")
        if embedding is None:
            embedding = compute_embedding("implement feature")
            cache.set("implement feature", embedding)
        
        # Get statistics
        stats = cache.get_stats()
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int = 3600,
    ) -> None:
        """
        Initialize embedding cache.
        
        Args:
            max_size: Maximum cache entries
            ttl_seconds: Time-to-live for cache entries
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.logger = EnhancedAuditLogger.instance()
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.4-01",
            operation="EMBEDDING_CACHE_INIT",
            success=True,
            details={
                "max_size": max_size,
                "ttl_seconds": ttl_seconds,
            },
        )
    
    def _hash_text(self, text: str) -> str:
        """Create hash key for text."""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """
        Get embedding from cache.
        
        AC-PHASE-8.4-01: Cache lookup with TTL check
        
        Args:
            text: Text to lookup
        
        Returns:
            Optional[List[float]]: Cached embedding or None
        """
        key = self._hash_text(text)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check TTL
            if time.time() - entry.timestamp < self.ttl_seconds:
                entry.hits += 1
                self.hits += 1
                return entry.embedding
            else:
                # Expired - remove
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, text: str, embedding: List[float]) -> None:
        """
        Store embedding in cache.
        
        AC-PHASE-8.4-01: Cache storage with LRU eviction
        
        Args:
            text: Original text
            embedding: Computed embedding vector
        """
        key = self._hash_text(text)
        
        # Evict if at max size
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_lru()
        
        self.cache[key] = CacheEntry(
            text=text,
            embedding=embedding,
            timestamp=time.time(),
            hits=0,
        )
    
    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.cache:
            return
        
        # Find entry with oldest timestamp and lowest hits
        lru_key = min(
            self.cache.keys(),
            key=lambda k: (self.cache[k].hits, self.cache[k].timestamp),
        )
        
        del self.cache[lru_key]
        self.evictions += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict: Cache stats including hit rate
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "evictions": self.evictions,
        }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
