"""
CORTEX LENSContextProvider Service

Selective LENS intelligence injection with company knowledge integration.
Provides caching, intent-based activation, and fail-safe fallback.

Authority: Phase 20 Component #1 (AC_LENS_COMPANY_001)
Rule: CORE-035 (Single Implementation)
"""

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from cortex.lens.orchestrator import LENSOrchestrator


@dataclass
class CacheEntry:
    """Cache entry with TTL tracking."""
    value: Dict[str, Any]
    timestamp: float
    ttl: int
    size_bytes: int


class LENSCache:
    """
    TTL-based cache for LENS contexts.

    Features:
        - 5-minute default TTL
        - Memory-limited (max 100MB)
        - Automatic eviction on expiration
        - Size tracking

    Authority: Phase 20 Component #1
    """

    def __init__(self, max_size_mb: int = 100):
        """
        Initialize cache.

        Args:
            max_size_mb: Maximum cache size in megabytes
        """
        self.max_size_mb = max_size_mb
        self._cache: Dict[str, CacheEntry] = {}
        self._total_size_bytes = 0

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check TTL expiration
        if time.time() - entry.timestamp > entry.ttl:
            # Expired - remove entry
            self._evict(key)
            return None

        return entry.value

    def set(self, key: str, value: Dict[str, Any], ttl: int) -> None:
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        # Estimate size (rough approximation)
        size_bytes = sys.getsizeof(str(value))

        # Check if adding this would exceed limit
        if self._total_size_bytes + size_bytes > self.max_size_mb * 1024 * 1024:
            # Evict oldest entries until space available
            self._evict_oldest_to_fit(size_bytes)

        # Remove old entry if exists
        if key in self._cache:
            self._evict(key)

        # Add new entry
        entry = CacheEntry(
            value=value,
            timestamp=time.time(),
            ttl=ttl,
            size_bytes=size_bytes
        )

        self._cache[key] = entry
        self._total_size_bytes += size_bytes

    def invalidate(self, key: str) -> None:
        """
        Invalidate specific cache entry.

        Args:
            key: Cache key to invalidate
        """
        if key in self._cache:
            self._evict(key)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._total_size_bytes = 0

    def get_size(self) -> float:
        """
        Get current cache size in MB.

        Returns:
            Size in megabytes
        """
        return self._total_size_bytes / (1024 * 1024)

    def _evict(self, key: str) -> None:
        """Evict specific entry and update size."""
        if key in self._cache:
            self._total_size_bytes -= self._cache[key].size_bytes
            del self._cache[key]

    def _evict_oldest_to_fit(self, needed_bytes: int) -> None:
        """Evict oldest entries until enough space available."""
        if not self._cache:
            return

        # Sort by timestamp (oldest first)
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].timestamp
        )

        for key, _ in sorted_entries:
            self._evict(key)

            # Check if we have enough space now
            available = (self.max_size_mb * 1024 * 1024) - self._total_size_bytes
            if available >= needed_bytes:
                break


class LENSContextProvider:
    """
    Provider service for LENS context with company knowledge integration.

    Features:
        - Intent-based activation (IMPLEMENT/FIX/REFACTOR/ANALYZE only)
        - 5-minute TTL cache per (file_path, company_name)
        - Fail-safe fallback if LENS unavailable
        - Performance: <200ms with cache, <500ms cold

    Usage:
        >>> provider = LENSContextProvider()
        >>> context = provider.get_context("/path/to/file.py", "acme-corp", "IMPLEMENT")
        >>> if context:
        ...     # Use LENS context for analysis
        ...     pass

    Authority: Phase 20 Component #1 (AC_LENS_COMPANY_001)
    """

    ACTIVE_INTENTS = {"IMPLEMENT", "FIX", "REFACTOR", "ANALYZE"}

    def __init__(self, cache_ttl: int = 300, max_cache_mb: int = 100):
        """
        Initialize LENSContextProvider.

        Args:
            cache_ttl: Cache time-to-live in seconds (default 300 = 5 minutes)
            max_cache_mb: Maximum cache size in megabytes
        """
        self.cache_ttl = cache_ttl
        self.cache = LENSCache(max_size_mb=max_cache_mb)
        self._lens_orchestrator: Optional[LENSOrchestrator] = None

    def get_context(
        self,
        file_path: str,
        company_name: str,
        intent_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get LENS context with company knowledge integration.

        Args:
            file_path: Path to file to analyze
            company_name: Company name for domain knowledge
            intent_type: Intent type (IMPLEMENT/FIX/REFACTOR/ANALYZE)

        Returns:
            LENS context dict or None if intent not active
        """
        # Check intent-based activation
        if not self._should_activate(intent_type):
            return None

        # Build cache key
        cache_key = self._make_cache_key(file_path, company_name)

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached:
            # Cache hit - add metadata
            cached["_metadata"]["cache_hit"] = True
            return cached

        # Cache miss - fetch fresh context
        try:
            context = self._fetch_lens_context(file_path, company_name)

            # Add metadata
            context["_metadata"] = {
                "cache_hit": False,
                "timestamp": time.time(),
                "file_path": file_path,
                "company_name": company_name,
                "intent_type": intent_type
            }

            # Cache result
            self.cache.set(cache_key, context, self.cache_ttl)

            return context

        except Exception as e:
            # Fail-safe: Return minimal context with error
            return {
                "git_analysis": {},
                "ast_analysis": {},
                "comment_analysis": {},
                "company_knowledge": {},
                "_metadata": {
                    "cache_hit": False,
                    "timestamp": time.time(),
                    "file_path": file_path,
                    "company_name": company_name,
                    "intent_type": intent_type,
                    "error": str(e)
                }
            }

    def invalidate_cache(self, file_path: str) -> None:
        """
        Invalidate all cache entries for a file.

        Args:
            file_path: File path to invalidate
        """
        # Invalidate all cache entries matching this file_path
        keys_to_invalidate = [
            key for key in self.cache._cache.keys()
            if file_path in key
        ]

        for key in keys_to_invalidate:
            self.cache.invalidate(key)

    def _should_activate(self, intent_type: str) -> bool:
        """
        Check if LENS should activate for this intent.

        Args:
            intent_type: Intent type to check

        Returns:
            True if LENS should activate
        """
        return intent_type in self.ACTIVE_INTENTS

    def _make_cache_key(self, file_path: str, company_name: str) -> str:
        """
        Build cache key from file path and company name.

        Args:
            file_path: File path
            company_name: Company name

        Returns:
            Cache key string
        """
        return f"{file_path}::{company_name}"

    def _fetch_lens_context(
        self,
        file_path: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Fetch fresh LENS context with company knowledge.

        Args:
            file_path: File path to analyze
            company_name: Company name for domain knowledge

        Returns:
            LENS context dict
        """
        # Lazy initialize LENS orchestrator
        if self._lens_orchestrator is None:
            self._lens_orchestrator = LENSOrchestrator()

        # Analyze file with LENS
        lens_context = self._lens_orchestrator.analyze_file(file_path)

        # TODO Phase 20 Component #2: Integrate company knowledge here
        # company_knowledge = self._fetch_company_knowledge(file_path, company_name)
        # lens_context["company_knowledge"] = company_knowledge

        # For now, add empty company knowledge placeholder
        lens_context["company_knowledge"] = {}

        return lens_context

    def _fetch_company_knowledge(
        self,
        file_path: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Fetch company domain knowledge (Phase 20 Component #2).

        Args:
            file_path: File path for context
            company_name: Company name

        Returns:
            Company knowledge dict
        """
        # Placeholder for Phase 20 Component #2
        return {
            "domains": [],
            "compliance_flags": [],
            "knowledge_precedence": {}
        }


# Singleton instance
_provider_instance: Optional[LENSContextProvider] = None


def get_lens_context_provider() -> LENSContextProvider:
    """
    Get singleton LENSContextProvider instance.

    Returns:
        LENSContextProvider instance
    """
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = LENSContextProvider()
    return _provider_instance
