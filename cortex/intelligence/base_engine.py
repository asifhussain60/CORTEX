"""BaseIntelligenceEngine: Foundational pattern for all intelligence modules

This is the core abstraction for the LENS/Intelligence Hybrid Architecture.
All intelligence engines inherit from this base class.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from cortex.brain.core.result import Err, Ok


@dataclass
class EngineMetrics:
    """Metrics for an intelligence engine"""
    invocations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    errors: int = 0


class BaseIntelligenceEngine:
    """
    Base class for all intelligence engines in the LENS/Intelligence Hybrid.

    Provides:
    - Standard interface for all engines
    - Caching mechanism
    - Metrics collection
    - Error handling
    - Version management
    """

    def __init__(
        self,
        name: str,
        version: str,
        description: str = "",
        cache_ttl: int = 300,
        enabled: bool = True
    ):
        """
        Initialize BaseIntelligenceEngine

        Args:
            name: Engine identifier (e.g., "RelationshipTraversal")
            version: Semantic version (e.g., "1.0.0")
            description: Engine description
            cache_ttl: Cache time-to-live in seconds
            enabled: Whether engine is enabled
        """
        self.name = name
        self.version = version
        self.description = description
        self.cache_ttl = cache_ttl
        self.enabled = enabled

        # Caching
        self._cache: Dict[str, tuple] = {}  # key -> (value, timestamp)
        self._metrics = EngineMetrics()

    def analyze(self, context: Dict[str, Any]) -> Union[Ok, Err]:
        """
        Analyze input context and return results

        Args:
            context: Input data for analysis

        Returns:
            Ok: Analysis results as Dict
            Err: Error message
        """
        if not self.enabled:
            return Err(f"Engine {self.name} is disabled")

        try:
            # Check cache
            cache_key = self._make_cache_key(context)
            cached = self._get_cached(cache_key)
            if cached is not None:
                self._metrics.cache_hits += 1
                return Ok(cached)

            self._metrics.cache_misses += 1

            # Execute analysis
            start = time.time()
            result = self._execute(context)
            elapsed_ms = (time.time() - start) * 1000

            # Update metrics
            self._metrics.invocations += 1
            self._metrics.total_time_ms += elapsed_ms
            self._metrics.avg_time_ms = self._metrics.total_time_ms / self._metrics.invocations

            # Cache result if successful
            if result.is_ok():
                self._cache_result(cache_key, result.unwrap())

            return result

        except Exception as e:
            self._metrics.errors += 1
            return Err(f"Engine {self.name} error: {str(e)}")

    def _execute(self, context: Dict[str, Any]) -> Union[Ok, Err]:
        """
        Execute the engine's analysis logic (implemented by subclasses)

        Args:
            context: Input data

        Returns:
            Analysis results or error
        """
        return Ok({"status": "not_implemented"})

    def is_enabled(self) -> bool:
        """Check if engine is enabled"""
        return self.enabled

    def enable(self) -> None:
        """Enable the engine"""
        self.enabled = True

    def disable(self) -> None:
        """Disable the engine"""
        self.enabled = False

    def clear_cache(self) -> None:
        """Clear all cached results"""
        self._cache.clear()

    def get_metrics(self) -> EngineMetrics:
        """Get engine metrics"""
        return self._metrics

    def reset_metrics(self) -> None:
        """Reset metrics counters"""
        self._metrics = EngineMetrics()

    def _make_cache_key(self, context: Dict[str, Any]) -> str:
        """Create a cache key from context"""
        # Simple implementation - can be overridden
        import hashlib
        import json

        try:
            json_str = json.dumps(context, sort_keys=True, default=str)
            return hashlib.md5(json_str.encode()).hexdigest()
        except:
            return str(hash(frozenset(context.items())))

    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached result if still valid"""
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]

        # Check TTL
        if time.time() - timestamp > self.cache_ttl:
            del self._cache[key]
            return None

        return value

    def _cache_result(self, key: str, value: Dict) -> None:
        """Cache a result"""
        self._cache[key] = (value, time.time())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, version={self.version}, enabled={self.enabled})"
