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

# Backward compatibility alias
InMemoryCacheBackend = MemoryBackend

# CacheStats placeholder (backward compatibility)
class CacheStats:
    """Cache statistics tracker."""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0

def reset_lens_cache():
    """Reset singleton cache instance (testing utility)."""
    # Clear singleton cache if implemented
    pass


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
    "CacheStats",
    
    # Backends
    "MemoryBackend",
    "InMemoryCacheBackend",  # Alias for backward compatibility
    "RedisBackend",
    
    # Utilities
    "get_lens_cache",
    "reset_lens_cache",
    "build_cache_key",
    "get_repo_state_hash",
]
