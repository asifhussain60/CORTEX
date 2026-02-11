"""LENS Orchestrator with transparent caching layer.

Wraps LENSOrchestrator to add cache layer without modifying base class.
Uses decorator pattern: cache checks before analysis, stores results after.

Features:
- Transparent caching (cache_enabled flag)
- Per-file caching with pattern invalidation
- Cache statistics (hits, misses, latency)
- TTL-based expiration (configurable)
- Multiple backend support (memory, Redis)
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.lens.cache import (
    CacheKeyConfig,
    LENSCache,
    build_cache_key,
    get_lens_cache,
)
from cortex.lens.orchestrator import LENSOrchestrator

logger = logging.getLogger(__name__)


class CachedLENSOrchestrator(LENSOrchestrator):
    """LENS Orchestrator with transparent caching.

    Adds cache layer to LENS analysis without modifying base orchestrator.
    Cache checks before full analysis pipeline, stores results after.

    Attributes:
        cache_enabled: Enable/disable caching (default: True)
        cache_ttl: Time-to-live in seconds (default: 300s = 5 minutes)
        cache: Backend cache implementation (memory or Redis)
        _cache_stats: Statistics tracking (hits, misses, latency)
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        cache_ttl: int = 300,
        cache_backend: str = "memory",
        **kwargs: Any
    ) -> None:
        """Initialize CachedLENSOrchestrator.

        Args:
            cache_enabled: Enable caching (default: True)
            cache_ttl: Time-to-live in seconds (default: 300)
            cache_backend: 'memory' (default) or 'redis'
            **kwargs: Additional args for base LENSOrchestrator or cache backend
        """
        super().__init__(**kwargs)
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl

        # Initialize cache backend
        if cache_enabled:
            self.cache: Optional[LENSCache] = get_lens_cache(
                backend=cache_backend
            )
            # Store ttl for later use if needed (cache handles internally)
            self.cache._ttl = cache_ttl
        else:
            self.cache = None

        # Statistics tracking
        self._cache_stats: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "total_latency_ms": 0,
            "analysis_count": 0,
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze single file with caching.

        Checks cache before running full LENS pipeline.
        Stores result in cache after analysis completes.

        Args:
            file_path: Path to file to analyze

        Returns:
            Dict with analysis results (git_analysis, ast_analysis, etc.)
        """
        if not self.cache_enabled or self.cache is None:
            # No caching: run full pipeline
            return super().analyze_file(file_path)

        # Generate cache key
        cache_key = self._generate_cache_key(str(file_path))

        # Try cache hit
        hit, cached_result = self._try_cache_hit(cache_key)
        if hit and cached_result is not None:
            self._cache_stats["hits"] += 1
            logger.debug(f"Cache hit for {file_path}")
            return cached_result

        # Cache miss: run full analysis
        self._cache_stats["misses"] += 1
        start_time = time.time()

        result = super().analyze_file(file_path)

        # Record latency and store in cache
        latency_ms = int((time.time() - start_time) * 1000)
        self._cache_stats["total_latency_ms"] += latency_ms
        self._cache_stats["analysis_count"] += 1

        # Store result in cache
        self._cache_result(cache_key, result)
        logger.debug(f"Cache miss for {file_path} ({latency_ms}ms analysis)")

        return result

    def analyze_batch(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """Analyze multiple files with per-file caching.

        Each file is cached independently.
        Cache hits avoid redundant analysis.

        Args:
            file_paths: List of paths to analyze

        Returns:
            List of analysis results (same order as input)
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.analyze_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Analysis failed for {file_path}: {e}")
                # Continue with remaining files

        return results

    def _try_cache_hit(self, cache_key: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Attempt to retrieve result from cache.

        Args:
            cache_key: Cache key generated from request

        Returns:
            (hit: bool, result: Optional[Dict[str, Any]])
            - (True, result) if cache hit found and valid
            - (False, None) if cache miss or expired
        """
        if self.cache is None:
            return False, None

        try:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return True, cached
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")

        return False, None

    def _cache_result(self, cache_key: str, context: Dict[str, Any]) -> None:
        """Store analysis result in cache.

        Args:
            cache_key: Cache key for this analysis
            context: Dict with analysis results to cache
        """
        if self.cache is None:
            return

        try:
            self.cache.set(cache_key, context, ttl=self.cache_ttl)
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")

    def _invalidate_file_cache(self, file_path: str) -> None:
        """Invalidate cache for specific file.

        Called when file content changes and cache needs refresh.

        Args:
            file_path: Path to file (pattern matching supported)
        """
        if self.cache is None:
            return

        try:
            cache_key = self._generate_cache_key(file_path)
            self.cache.invalidate(cache_key)
            logger.debug(f"Cache invalidated for {file_path}")
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")

    def _generate_cache_key(self, file_path: str) -> str:
        """Generate cache key for analysis request.

        Uses deterministic key generation based on:
        - File path
        - Repository state (git HEAD)
        - LENS version

        Args:
            file_path: Path to file being analyzed

        Returns:
            SHA256 hash cache key
        """
        repo_path = str(getattr(self, 'repo_path', '.'))
        return build_cache_key(
            user_request=file_path,
            repo_path=repo_path,
            lens_version="2.0",
        )

    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics.

        Returns:
            Dict with cache hits, misses, hit_rate, avg_latency_ms

        Example:
            >>> stats = orchestrator.get_cache_statistics()
            >>> print(f"Cache hit rate: {stats['hit_rate']:.1%}")
            Cache hit rate: 60.0%
        """
        total_accesses = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = (
            self._cache_stats["hits"] / total_accesses
            if total_accesses > 0
            else 0.0
        )
        avg_latency = (
            self._cache_stats["total_latency_ms"] / self._cache_stats["analysis_count"]
            if self._cache_stats["analysis_count"] > 0
            else 0
        )

        return {
            "hits": self._cache_stats["hits"],
            "misses": self._cache_stats["misses"],
            "hit_rate": hit_rate,
            "avg_latency_ms": avg_latency,
            "total_analyses": self._cache_stats["analysis_count"],
            "cache_enabled": self.cache_enabled,
        }

    def clear_cache(self) -> None:
        """Clear all cached results.

        Useful for full refresh or testing.
        """
        if self.cache is not None:
            try:
                self.cache.invalidate("*")  # Pattern: all keys
                self._cache_stats = {
                    "hits": 0,
                    "misses": 0,
                    "total_latency_ms": 0,
                    "analysis_count": 0,
                }
                logger.info("Cache cleared")
            except Exception as e:
                logger.warning(f"Cache clear failed: {e}")


__all__ = ["CachedLENSOrchestrator"]
