"""LENS caching layer - transparent cache wrapping for LENS orchestrator.

Provides:
- Multiple cache backends (memory, Redis)
- Deterministic cache key generation
- TTL-based expiration
- Pattern-based invalidation
- Cache statistics tracking
"""

from .lens_cache import LENSCache, CacheEntry, CacheKey
from .cache_key_builder import build_cache_key, get_repo_state_hash, CacheKeyConfig
from .memory_backend import MemoryBackend
from .redis_backend import RedisBackend


def get_lens_cache(backend: str = "memory", **kwargs) -> LENSCache:
    """Factory function to get appropriate cache backend.
    
    Args:
        backend: 'memory' (default) or 'redis'
        **kwargs: Backend-specific configuration
        
    Returns:
        LENSCache implementation (MemoryBackend or RedisBackend)
        
    Example:
        >>> cache = get_lens_cache()  # Development: MemoryBackend
        >>> cache = get_lens_cache("redis", url="redis://localhost:6379/0")
    """
    if backend == "redis":
        return RedisBackend(**kwargs)
    elif backend == "memory":
        return MemoryBackend(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}. Use 'memory' or 'redis'")


__all__ = [
    # Core interfaces
    "LENSCache",
    "CacheEntry",
    "CacheKey",
    "CacheKeyConfig",
    
    # Backends
    "MemoryBackend",
    "RedisBackend",
    
    # Utilities
    "build_cache_key",
    "get_repo_state_hash",
    "get_lens_cache",
]
