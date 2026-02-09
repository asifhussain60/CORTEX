"""
Intelligence Gateway Middleware.

Enforces intelligence synthesis at MCP boundary - ALL tool calls must pass
through IntelligenceGate to receive enriched UnifiedIntelligenceContext.

Authority: Phase 54 - Intelligence Layer Enforcement & MCP Gateway
Pattern: Follows OnboardingGate (proven MCP middleware enforcement)

Features:
- Mandatory intelligence synthesis (no bypasses)
- Context caching (5 min TTL)
- Graceful degradation on synthesis failure
- AC audit trail logging
- Defense-in-depth with @mcp_tool decorator

CORE Rules:
- CORE-008: TDD (tests before code)
- CORE-011: Type hints required
- CORE-012: Google-style docstrings
- CORE-027: Audit trail (AC_START → AC_COMPLETE)
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from cortex.brain.knowledge.unified_intelligence_context import UnifiedIntelligenceContext
from cortex.brain.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine

logger = logging.getLogger(__name__)


@dataclass
class IntelligenceContextCache:
    """Cached intelligence context with TTL."""

    context: UnifiedIntelligenceContext
    created_at: float
    ttl_seconds: int = 300  # 5 min default

    def is_stale(self) -> bool:
        """Check if cache entry is stale."""
        return (time.time() - self.created_at) > self.ttl_seconds

    def is_fresh(self) -> bool:
        """Check if cache entry is still fresh."""
        return not self.is_stale()


class IntelligenceGate:
    """
    MCP middleware for mandatory intelligence synthesis.

    Enforces that every MCP tool call receives enriched UnifiedIntelligenceContext.
    Prevents bypasses by blocking execution if synthesis fails.

    Pattern: Follows OnboardingGate interface for consistency.

    Usage:
        gate = IntelligenceGate()
        gate.process_request(tool_name, kwargs)  # Returns modified kwargs
    """

    def __init__(self, cache_ttl_seconds: int = 300):
        """
        Initialize IntelligenceGate.

        Args:
            cache_ttl_seconds: Cache TTL for synthesized contexts (default 300s)
        """
        self.logger = logging.getLogger(f"{__name__}.IntelligenceGate")
        self.cache: Dict[str, IntelligenceContextCache] = {}
        self.cache_ttl = cache_ttl_seconds
        self.synthesis_engine = KnowledgeSynthesisEngine()
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "synthesis_failures": 0,
            "total_requests": 0,
        }

        self.logger.info(
            "AC_START: AC-PHASE54-S1-001 | IntelligenceGate initialized"
        )

    def process_request(
        self, tool_name: str, kwargs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process MCP request through intelligence gate.

        This is the enforcement point: ALL MCP tools pass through here.

        Args:
            tool_name: Name of MCP tool being invoked
            kwargs: Tool arguments

        Returns:
            Modified kwargs with 'unified_intelligence' key injected

        Raises:
            ValueError: If synthesis fails (prevents tool execution)
        """
        self.stats["total_requests"] += 1

        # Check if context already provided (from CCL or decorator)
        if "unified_intelligence" in kwargs:
            cached_ctx = kwargs.get("unified_intelligence")
            if isinstance(cached_ctx, UnifiedIntelligenceContext):
                self.logger.debug(
                    f"Tool {tool_name}: Using provided intelligence context"
                )
                return kwargs

        # Generate cache key from request context
        request_id = kwargs.get("request_id", str(uuid4()))
        cache_key = f"{tool_name}:{request_id}"

        # Try to get from cache first
        cached_entry = self.cache.get(cache_key)
        if cached_entry and cached_entry.is_fresh():
            self.stats["cache_hits"] += 1
            kwargs["unified_intelligence"] = cached_entry.context
            self.logger.debug(f"Tool {tool_name}: Cache hit for {cache_key}")
            return kwargs

        self.stats["cache_misses"] += 1

        # Synthesize fresh context
        try:
            synthesis_start = time.time()

            # Extract synthesis inputs from kwargs
            intent = kwargs.get("operation", "UNKNOWN")
            file_path = kwargs.get("target")
            user_context = {
                k: v
                for k, v in kwargs.items()
                if k not in ["unified_intelligence", "request_id"]
            }

            # Call synthesis engine
            unified_context = self.synthesis_engine.synthesize_unified_context(
                intent=intent,
                file_path=file_path,
                user_context=user_context,
                force_refresh=False,
            )

            synthesis_duration = time.time() - synthesis_start

            # Cache result
            self.cache[cache_key] = IntelligenceContextCache(
                context=unified_context, created_at=time.time(), ttl_seconds=self.cache_ttl
            )

            # Inject into kwargs
            kwargs["unified_intelligence"] = unified_context

            self.logger.info(
                f"AC_PHASE54-S1-001: Tool={tool_name} | "
                f"Synthesis={synthesis_duration:.2f}ms | "
                f"Coverage={unified_context.coverage_score:.2%}"
            )

            return kwargs

        except Exception as synthesis_error:
            self.stats["synthesis_failures"] += 1
            error_msg = (
                f"Intelligence synthesis failed for {tool_name}: "
                f"{str(synthesis_error)}"
            )
            self.logger.error(error_msg, exc_info=True)

            self.logger.error(
                f"AC_PHASE54-S1-003Union[BLOCKED, Tool]={tool_name} | "
                f"Error={str(synthesis_error)[:100]}"
            )

            raise ValueError(
                f"Intelligence synthesis required but failed: {str(synthesis_error)}. "
                f"Check logs for details. This is a blocking error to ensure "
                f"all operations use enriched intelligence context."
            ) from synthesis_error

    def __call__(self, tool_name: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Callable interface (middleware protocol).

        Args:
            tool_name: Name of tool
            kwargs: Tool arguments

        Returns:
            Modified kwargs with intelligence context

        Raises:
            ValueError: If synthesis fails
        """
        return self.process_request(tool_name, kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get gate statistics.

        Returns:
            Statistics dictionary with cache hits/misses/failures
        """
        total = self.stats["total_requests"]
        return {
            **self.stats,
            "cache_hit_rate": (
                self.stats["cache_hits"] / total if total > 0 else 0.0
            ),
            "synthesis_failure_rate": (
                self.stats["synthesis_failures"] / total if total > 0 else 0.0
            ),
        }

    def clear_cache(self) -> int:
        """
        Clear all cached contexts.

        Returns:
            Number of entries cleared
        """
        count = len(self.cache)
        self.cache.clear()
        self.logger.info(f"Cleared {count} cached intelligence contexts")
        return count

    def cleanup_stale(self) -> int:
        """
        Remove stale entries from cache.

        Returns:
            Number of entries removed
        """
        stale_keys = [
            k for k, v in self.cache.items() if v.is_stale()
        ]
        for key in stale_keys:
            del self.cache[key]
        self.logger.debug(f"Cleaned up {len(stale_keys)} stale cache entries")
        return len(stale_keys)
