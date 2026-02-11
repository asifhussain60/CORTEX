"""LENS caching layer - transparent cache wrapping for LENS orchestrator.

Provides:
- Multiple cache backends (memory, Redis)
- Deterministic cache key generation
- TTL-based expiration
- Pattern-based invalidation
- Cache statistics tracking
"""

from .cache_key_builder import CacheKeyConfig, build_cache_key, get_repo_state_hash
from .lens_cache import CacheEntry, CacheKey, LENSCache, get_lens_cache
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
    # Phase 65 S6: Reset canonical singleton
    import cortex.lens.cache.lens_cache as lens_cache_module
    lens_cache_module._lens_cache_instance = None


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
