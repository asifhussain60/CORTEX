"""COMPAT shim — core.context_cache_layer → core.core_context_cache_layer (Phase 60 duplicate resolution).

Canonical: cortex/core/core_context_cache_layer.py
The orchestrators.core version uses different constructor params (ttl_seconds vs default_ttl).
90-day retention: created 2026-02-24, expires 2026-05-24.
"""
from .core_context_cache_layer import (  # noqa: F401
    CacheEntry,
    CacheStats,
    ContextCacheLayer,
)
from .core_context_cache_layer import *  # noqa: F401, F403
