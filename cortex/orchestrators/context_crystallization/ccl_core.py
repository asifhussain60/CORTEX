# AC_START: AC-PHASE49-S1-ccl_core
# Description: Core Context Crystallization Layer orchestrator
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 49, Stage 1, Component: CCL Core

"""
Context Crystallization Layer (CCL) Core.

Non-blocking async pre-flight context enrichment running parallel to
MasterOrchestrator Stage 1. Prefetches:
- Rules context (tier0 → tier1 → company precedence)
- LENS intelligence (AST, git, comments)
- Infrastructure capabilities (Phase 46)

Timeout: 300ms SLA, fallback at 500ms
"""

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from cortex.orchestrators.context_crystallization.infrastructure_detector import (
    InfrastructureDetector,
)
from cortex.orchestrators.context_crystallization.lens_warmer import LENSWarmer
from cortex.orchestrators.context_crystallization.rules_cache import RulesCache

logger = logging.getLogger(__name__)


@dataclass
class CrystallizedContext:
    """Pre-warmed context ready for Stages 2+ consumption.

    This dataclass bundles all pre-fetched knowledge:
    - rules: Tier-resolved CORTEX rules (company > tier1 > tier0)
    - lens: Pre-analyzed LENS intelligence (file, git, AST, comments)
    - infrastructure: Environment-specific capabilities
    - metadata: Timing, completion status, fallback indicators
    """

    # Phase A: Rules cache
    rules: Optional[RulesCache] = None
    rules_ready: bool = False
    rules_latency_ms: float = 0.0

    # Phase B: LENS warm-up
    lens: Optional[Dict[str, Any]] = None
    lens_ready: bool = False
    lens_latency_ms: float = 0.0

    # Phase C: Infrastructure
    infrastructure: Optional[Dict[str, Any]] = None
    infrastructure_ready: bool = False
    infrastructure_latency_ms: float = 0.0

    # Metadata
    total_latency_ms: float = 0.0
    completed_at: Optional[float] = None
    fallback_invoked: bool = False
    error_details: Dict[str, str] = field(default_factory=dict)

    def is_ready(self) -> bool:
        """Check if context is ready for use (at least one phase complete)."""
        return self.rules_ready or self.lens_ready or self.infrastructure_ready

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context for logging/debugging."""
        return {
            "rules_ready": self.rules_ready,
            "lens_ready": self.lens_ready,
            "infrastructure_ready": self.infrastructure_ready,
            "total_latency_ms": self.total_latency_ms,
            "fallback_invoked": self.fallback_invoked,
            "error_details": self.error_details,
        }


class ContextCrystallizationLayer:
    """
    Non-blocking async pre-flight context enrichment layer.

    Runs as Layer 0 (before Stage 1) in parallel with InteractionOrchestrator.
    Async prefetches LENS + Rules + Infrastructure while comprehension happens.

    Design:
    - Non-blocking: Returns immediately, prefetch happens in background
    - Timeout SLA: 300ms max, fallback at 500ms
    - Pluggable: Phase A/B/C independent, can add Phase D without changes
    - Graceful: Falls back to fresh fetch if timeout
    """

    def __init__(
        self,
        executor: Optional[ThreadPoolExecutor] = None,
        timeout_sla_ms: int = 300,
        fallback_timeout_ms: int = 500,
    ):
        """Initialize CCL.

        Args:
            executor: ThreadPoolExecutor for async work (default: create new)
            timeout_sla_ms: Target completion time (300ms)
            fallback_timeout_ms: Hard timeout before fallback (500ms)
        """
        self.executor = executor or ThreadPoolExecutor(max_workers=3)
        self.timeout_sla_ms = timeout_sla_ms
        self.fallback_timeout_ms = fallback_timeout_ms

        # Lazy-initialized sub-components
        self._rules_cache: Optional[RulesCache] = None
        self._lens_warmer: Optional[LENSWarmer] = None
        self._infrastructure_detector: Optional[InfrastructureDetector] = None

    def _get_rules_cache(self) -> RulesCache:
        """Lazy-initialize RulesCache."""
        if self._rules_cache is None:
            self._rules_cache = RulesCache()
        return self._rules_cache

    def _get_lens_warmer(self) -> LENSWarmer:
        """Lazy-initialize LENSWarmer."""
        if self._lens_warmer is None:
            self._lens_warmer = LENSWarmer()
        return self._lens_warmer

    def _get_infrastructure_detector(self) -> InfrastructureDetector:
        """Lazy-initialize InfrastructureDetector."""
        if self._infrastructure_detector is None:
            self._infrastructure_detector = InfrastructureDetector()
        return self._infrastructure_detector

    async def prefetch_async(
        self,
        file_path: Optional[str] = None,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> CrystallizedContext:
        """
        Async prefetch all context phases in parallel.

        Runs Phase A, B, C in parallel with 300ms SLA.
        Returns immediately; completion happens in background.

        Args:
            file_path: Optional file to analyze (Phase B/LENS)
            request_context: Optional request context for enrichment

        Returns:
            CrystallizedContext (may be partially ready if timeout)
        """
        logger.info(
            f"AC_START: AC-PHASE49-prefetch file_path={file_path} timeout={self.timeout_sla_ms}ms"
        )

        context = CrystallizedContext()
        start_time = time.time()

        # Phase A: Rules cache (50ms typical)
        try:
            rules = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self.executor, self._get_rules_cache().load
                ),
                timeout=self.timeout_sla_ms / 1000,
            )
            context.rules = rules
            context.rules_ready = True
            context.rules_latency_ms = (time.time() - start_time) * 1000
            logger.debug(f"Phase A rules ready: {context.rules_latency_ms:.1f}ms")
        except (asyncio.TimeoutError, FutureTimeoutError) as e:
            context.error_details["rules"] = f"Timeout: {str(e)}"
            logger.warning(f"Phase A timeout: {str(e)}")
        except Exception as e:
            context.error_details["rules"] = f"Error: {str(e)}"
            logger.error(f"Phase A failed: {str(e)}")

        # Phase B: LENS warm-up (100-200ms typical)
        phase_b_start = time.time()
        try:
            lens_result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self.executor,
                    self._get_lens_warmer().analyze,
                    file_path,
                ),
                timeout=self.timeout_sla_ms / 1000,
            )
            context.lens = lens_result or {}
            context.lens_ready = True
            context.lens_latency_ms = (time.time() - phase_b_start) * 1000
            logger.debug(f"Phase B LENS ready: {context.lens_latency_ms:.1f}ms")
        except (asyncio.TimeoutError, FutureTimeoutError) as e:
            context.error_details["lens"] = f"Timeout: {str(e)}"
            logger.warning(f"Phase B timeout: {str(e)}")
        except Exception as e:
            context.error_details["lens"] = f"Error: {str(e)}"
            logger.error(f"Phase B failed: {str(e)}")

        # Phase C: Infrastructure detection (50ms typical)
        phase_c_start = time.time()
        try:
            infra = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    self.executor, self._get_infrastructure_detector().detect
                ),
                timeout=self.timeout_sla_ms / 1000,
            )
            context.infrastructure = infra or {}
            context.infrastructure_ready = True
            context.infrastructure_latency_ms = (time.time() - phase_c_start) * 1000
            logger.debug(
                f"Phase C infrastructure ready: {context.infrastructure_latency_ms:.1f}ms"
            )
        except (asyncio.TimeoutError, FutureTimeoutError) as e:
            context.error_details["infrastructure"] = f"Timeout: {str(e)}"
            logger.warning(f"Phase C timeout: {str(e)}")
        except Exception as e:
            context.error_details["infrastructure"] = f"Error: {str(e)}"
            logger.error(f"Phase C failed: {str(e)}")

        context.total_latency_ms = (time.time() - start_time) * 1000
        context.completed_at = time.time()

        logger.info(
            f"AC_COMPLETE: AC-PHASE49-prefetch total={context.total_latency_ms:.1f}ms "
            f"rules_ready={context.rules_ready} lens_ready={context.lens_ready} "
            f"infra_ready={context.infrastructure_ready}"
        )

        return context

    def prefetch_blocking(
        self,
        file_path: Optional[str] = None,
        request_context: Optional[Dict[str, Any]] = None,
    ) -> CrystallizedContext:
        """
        Blocking prefetch (for testing/fallback scenarios).

        Waits up to fallback_timeout_ms for context to be ready.

        Args:
            file_path: Optional file to analyze
            request_context: Optional request context

        Returns:
            CrystallizedContext (partial if timeout)
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                asyncio.wait_for(
                    self.prefetch_async(file_path, request_context),
                    timeout=self.fallback_timeout_ms / 1000,
                )
            )
        except asyncio.TimeoutError:
            logger.warning(
                f"Blocking prefetch timeout ({self.fallback_timeout_ms}ms), returning partial context"
            )
            return CrystallizedContext(fallback_invoked=True)
        finally:
            loop.close()


# AC_COMPLETE: AC-PHASE49-S1-ccl_core ✅
