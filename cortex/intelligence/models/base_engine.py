"""
Canonical BaseIntelligenceEngine — Phase 107 Sub-Phase A.

Merged base class satisfying BOTH prior contracts:
  - base.py (ABC):        abstract analyze(AnalysisContext), validate_context(), _create_result(), _error_result()
  - base_engine.py (concrete): caching, metrics (EngineMetrics), enable/disable, _execute()

Single source of truth for BaseIntelligenceEngine and EngineMetrics.
Authority: GAP-107-01 (CORE-035 — single canonical implementation)
SSOT:      cortex/intelligence/models/base_engine.py
Compat:    cortex/intelligence/base.py and cortex/intelligence/base_engine.py re-export from here
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from __future__ import annotations

import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Re-export Ok/Err if available (base_engine.py used these); graceful fallback for tests
try:
    from cortex.core.result import Err, Ok
except ImportError:  # pragma: no cover — fallback for isolated test runs
    class Ok:  # type: ignore[no-redef]  # CORE-035-scoped — domain-specific variant
        """Minimal Ok wrapper for environments without cortex.core.result."""

        def __init__(self, value: Any) -> None:
            self._value = value

        def is_ok(self) -> bool:
            """Return True (always Ok)."""
            return True

        def unwrap(self) -> Any:
            """Unwrap the value."""
            return self._value

    class Err:  # type: ignore[no-redef]  # CORE-035-scoped — domain-specific variant
        """Minimal Err wrapper for environments without cortex.core.result."""

        def __init__(self, message: str) -> None:
            self._message = message

        def is_ok(self) -> bool:
            """Return False (always Err)."""
            return False

        def unwrap(self) -> str:
            """Unwrap the error message."""
            return self._message


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Canonical dataclasses (GAP-107-02)
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AnalysisContext:
    """Context for intelligence analysis.

    Attributes:
        file_path: Primary file being analyzed.
        workspace_root: Root of workspace.
        additional_files: Related files for cross-file analysis.
        config: Engine-specific configuration.
        cache_key: Optional cache key for results.
    """

    file_path: Path
    workspace_root: Path
    additional_files: List[Path] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    cache_key: Optional[str] = None


@dataclass
class AnalysisResult:
    """Result from intelligence analysis.

    Attributes:
        engine_name: Name of engine that produced result.
        data: Analysis data (engine-specific).
        metadata: Timing, errors, warnings.
        cache_hit: Whether result came from cache.
    """

    engine_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    cache_hit: bool = False


@dataclass
class EngineMetrics:
    """Metrics for an intelligence engine.

    Attributes:
        invocations: Total number of analysis calls.
        cache_hits: Number of results served from cache.
        cache_misses: Number of results computed fresh.
        total_time_ms: Cumulative execution time in milliseconds.
        avg_time_ms: Rolling average execution time in milliseconds.
        errors: Number of failed analysis calls.
    """

    invocations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_time_ms: float = 0.0
    avg_time_ms: float = 0.0
    errors: int = 0


# ─────────────────────────────────────────────────────────────────────────────
# Merged BaseIntelligenceEngine — honours both prior contracts simultaneously
# ─────────────────────────────────────────────────────────────────────────────


class BaseIntelligenceEngine(ABC):
    """Merged abstract base class for all intelligence engines.

    Satisfies BOTH prior contracts simultaneously:
    - base.py ABC:        abstract analyze(AnalysisContext), validate_context()
    - base_engine.py:     caching, metrics, enable/disable, _execute()

    All intelligence engines must:
    1. Inherit from BaseIntelligenceEngine (this class — CORE-035 single definition)
    2. Implement analyze(AnalysisContext) → AnalysisResult
    3. Implement validate_context(AnalysisContext) → bool
    4. Support both sync and async modes
    5. Never import from cortex.lens (prevents circular deps)
    6. Return AnalysisResult with standardized format

    Args:
        name: Engine identifier (e.g. "RelationshipTraversal"). Stored as ``self.name``
              and also as ``self.engine_name`` for backward compatibility.
        version: Semantic version string (e.g. "1.0.0").
        description: Human-readable description of what the engine does.
        cache_ttl: Cache time-to-live in seconds (default: 300).
        enabled: Whether engine is active on construction (default: True).
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        cache_ttl: int = 300,
        enabled: bool = True,
    ) -> None:
        """Initialise BaseIntelligenceEngine.

        Args:
            name: Engine identifier.
            version: Semantic version.
            description: Engine description.
            cache_ttl: Cache TTL in seconds.
            enabled: Whether engine starts enabled.
        """
        # Dual attribute: self.name (base_engine.py compat) + self.engine_name (base.py compat)
        self.name = name
        self.engine_name = name  # backward-compat alias
        self.version = version
        self.description = description
        self.cache_ttl = cache_ttl
        self.enabled = enabled

        # Caching
        self._cache: Dict[str, tuple] = {}  # key → (value, timestamp)
        self._metrics = EngineMetrics()
        self.logger = logging.getLogger(f"{__name__}.{name}")

    # ── Abstract interface (from base.py ABC) ─────────────────────────────

    @abstractmethod
    def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """Analyse code and return intelligence.

        Args:
            context: Analysis context with file path, workspace, config.

        Returns:
            AnalysisResult with standardised data format.

        Raises:
            ValueError: If context validation fails.
        """

    @abstractmethod
    def validate_context(self, context: AnalysisContext) -> bool:
        """Validate that context is suitable for analysis.

        Args:
            context: Analysis context to validate.

        Returns:
            True if context is valid.

        Raises:
            ValueError: If context is invalid.
        """

    # ── Caching + metrics interface (from base_engine.py) ─────────────────

    def is_enabled(self) -> bool:
        """Return whether engine is currently enabled."""
        return self.enabled

    def enable(self) -> None:
        """Enable the engine."""
        self.enabled = True

    def disable(self) -> None:
        """Disable the engine."""
        self.enabled = False

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self._cache.clear()

    def get_metrics(self) -> EngineMetrics:
        """Return current engine metrics."""
        return self._metrics

    def reset_metrics(self) -> None:
        """Reset all metric counters to zero."""
        self._metrics = EngineMetrics()

    # ── Async variant (from base.py) ──────────────────────────────────────

    def analyze_async(self, context: AnalysisContext) -> AnalysisResult:
        """Async version of analyze() — delegates to sync by default.

        Override for true async implementations.

        Args:
            context: Analysis context.

        Returns:
            AnalysisResult.
        """
        return self.analyze(context)

    # ── Protected helpers (from base.py) ──────────────────────────────────

    def _create_result(
        self,
        data: Dict[str, Any],
        cache_hit: bool = False,
    ) -> AnalysisResult:
        """Create standardised AnalysisResult.

        Args:
            data: Engine-specific analysis data.
            cache_hit: Whether this result came from cache.

        Returns:
            AnalysisResult with metadata.
        """
        return AnalysisResult(
            engine_name=self.engine_name,
            data=data,
            metadata={
                "engine": self.engine_name,
                "timestamp": time.time(),
            },
            cache_hit=cache_hit,
        )

    def _error_result(self, error: Exception) -> AnalysisResult:
        """Create error AnalysisResult.

        Args:
            error: Exception that occurred.

        Returns:
            AnalysisResult with error metadata.
        """
        self.logger.error("Analysis error: %s", error, exc_info=True)
        return AnalysisResult(
            engine_name=self.engine_name,
            data={"error": str(error)},
            metadata={
                "engine": self.engine_name,
                "error": str(error),
                "timestamp": time.time(),
            },
        )

    # ── Cache helpers (from base_engine.py) ───────────────────────────────

    def _make_cache_key(self, context: Union[Dict[str, Any], AnalysisContext]) -> str:
        """Create a deterministic cache key from context.

        Args:
            context: Analysis context or raw dict.

        Returns:
            MD5 hex digest string.
        """
        if isinstance(context, AnalysisContext):
            raw: Dict[str, Any] = {
                "file_path": str(context.file_path),
                "workspace_root": str(context.workspace_root),
                "cache_key": context.cache_key,
                "config": context.config,
            }
        else:
            raw = dict(context)

        try:
            json_str = json.dumps(raw, sort_keys=True, default=str)
            return hashlib.md5(json_str.encode()).hexdigest()  # nosec: used for caching only
        except (TypeError, ValueError, AttributeError):
            return str(hash(str(raw)))

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Return cached result if still within TTL.

        Args:
            key: Cache key.

        Returns:
            Cached dict or None if expired/missing.
        """
        if key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.cache_ttl:
            del self._cache[key]
            return None
        return value  # type: ignore[return-value]

    def _cache_result(self, key: str, value: Dict[str, Any]) -> None:
        """Store result in cache with current timestamp.

        Args:
            key: Cache key.
            value: Result dict to store.
        """
        self._cache[key] = (value, time.time())

    def __repr__(self) -> str:
        """Return developer-readable representation."""
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"version={self.version!r}, "
            f"enabled={self.enabled})"
        )
