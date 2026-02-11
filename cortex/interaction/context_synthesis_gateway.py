"""
Context Synthesis Gateway - EXIT GATE for all CORTEX responses.

ENH-046 Phase 4: Single integration point in MasterOrchestrator.execute_operation()
that automatically synthesizes ALL orchestrator outputs before Copilot handoff.

Architecture:
    User Request → MasterOrchestrator → [Orchestrators]
                                            ↓
                                    ContextSynthesisGateway (EXIT GATE)
                                            ↓
                                    Synthesized context → GitHub Copilot

Because MasterOrchestrator is the final aggregation point, this gateway
automatically covers ALL orchestrators without per-orchestrator integration.

Authority:
    - ENH-046 Phase 4 (Context Synthesis Gateway + Integration)
    - copilot-instructions.md v7.4 (CORE-002: No markdown file generation)
    - cortex-architect.prompt.md v14.2 (AUDIT P1 Infrastructure)

Author: CORTEX Context Synthesis System
Created: 2026-02-06
Updated: 2026-02-06 (v1.0 - Initial Implementation)
"""

import logging
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.brain.core.context_synthesizer import ContextSynthesizer
from cortex.brain.core.copilot_context_optimizer import CopilotContextOptimizer
from cortex.interaction.context_cache_layer import ContextCacheLayer
from cortex.interaction.context_metrics_collector import ContextMetricsCollector

logger = logging.getLogger(__name__)


@dataclass
class SynthesizedContext:
    """Result of context synthesis with metadata."""

    original_size_bytes: int
    synthesized_size_bytes: int
    compression_ratio: float
    synthesis_time_ms: float
    cache_hit: bool
    context: Dict[str, Any]
    session_id: str
    orchestrator_name: str
    token_count: int
    budget_compliant: bool


class ContextSynthesisGateway:
    """
    EXIT GATE: Synthesizes ALL orchestrator outputs before Copilot handoff.

    This is the single integration point that automatically covers:
    - InteractionOrchestrator (LENS context, challenges)
    - IntentRouter (intent classification)
    - ChallengeEngine (disagreement analysis)
    - EnforcementOrchestrator (governance validation)
    - TDDOrchestrator (test generation)
    - RefactoringOrchestrator (code improvements)
    - DocumentationOrchestrator (doc generation)
    - OnboardingOrchestrator (repo profiling)
    - PlanningOrchestrator (implementation plans)
    - MasterOrchestrator (final aggregation)

    Features:
    - Token budget enforcement (≤20K tokens per turn)
    - Intelligent per-orchestrator compression strategies
    - LRU cache with TTL (70% hit rate target)
    - Cumulative session token tracking (prevent acceleration)
    - Prometheus metrics integration
    - Fail-safe: Returns original context if synthesis errors

    Usage:
        gateway = ContextSynthesisGateway()
        result = gateway.synthesize(
            context=orchestrator_output,
            session_id="session_123",
            orchestrator_name="InteractionOrchestrator"
        )
    """

    def __init__(
        self,
        optimizer: Optional[CopilotContextOptimizer] = None,
        synthesizer: Optional[ContextSynthesizer] = None,
        cache: Optional[ContextCacheLayer] = None,
        metrics: Optional[ContextMetricsCollector] = None,
        token_budget: int = 20000,
        enable_cache: bool = True,
        fail_safe: bool = True
    ):
        """
        Initialize Context Synthesis Gateway.

        Args:
            optimizer: Copilot context optimizer (Phase 2)
            synthesizer: Context synthesizer (Phase 3)
            cache: Cache layer (Phase 4)
            metrics: Metrics collector (Phase 1)
            token_budget: Maximum tokens per turn (default: 20K)
            enable_cache: Enable LRU caching (default: True)
            fail_safe: Return original context on error (default: True)
        """
        self.optimizer = optimizer or CopilotContextOptimizer()
        self.synthesizer = synthesizer or ContextSynthesizer()
        self.cache = cache or ContextCacheLayer() if enable_cache else None
        self.metrics = metrics or ContextMetricsCollector()
        self.token_budget = token_budget
        self.enable_cache = enable_cache
        self.fail_safe = fail_safe

        # Session token tracking (prevent acceleration pattern)
        self._session_tokens: Dict[str, int] = {}

        logger.info(
            "ContextSynthesisGateway initialized (budget=%d tokens, cache=%s)",
            token_budget,
            "enabled" if enable_cache else "disabled"
        )

    def synthesize(
        self,
        context: Dict[str, Any],
        session_id: str,
        orchestrator_name: str
    ) -> SynthesizedContext:
        """
        Synthesize orchestrator output before Copilot handoff (EXIT GATE).

        Pipeline:
        1. Pre-synthesis validation (estimate raw tokens)
        2. Cache lookup (if enabled)
        3. Token optimization (CopilotContextOptimizer)
        4. Content synthesis (ContextSynthesizer)
        5. Post-synthesis verification (confirm compression targets)
        6. Cache store (if cache miss)
        7. Metrics recording (Prometheus)
        8. Session token tracking (cumulative)

        Args:
            context: Orchestrator output (raw context)
            session_id: Session identifier for cumulative tracking
            orchestrator_name: Name of source orchestrator

        Returns:
            SynthesizedContext with compressed context + metadata

        Raises:
            No exceptions if fail_safe=True (returns original context)
        """
        start_time = time.perf_counter()

        # Start metrics tracking
        self.metrics.start_synthesis(session_id)

        try:
            # Step 1: Measure original context
            original_size = self._calculate_size(context)
            logger.debug(
                "Gateway: Processing %s output (session=%s, size=%d bytes)",
                orchestrator_name,
                session_id,
                original_size
            )

            # Step 2: Check cache
            cache_key = None
            cache_hit = False
            if self.enable_cache and self.cache:
                cache_key = self._build_cache_key(context, orchestrator_name)
                cached = self.cache.get(cache_key)
                if cached:
                    cache_hit = True
                    logger.debug("Gateway: Cache HIT (key=%s)", cache_key)

                    # Update session tokens
                    self._update_session_tokens(session_id, cached.token_count)

                    # Record metrics for cache hit
                    synthesis_time_ms = (time.perf_counter() - start_time) * 1000
                    self.metrics.end_synthesis(
                        session_id=session_id,
                        size_before=original_size,
                        size_after=cached.synthesized_size_bytes,
                        cache_hits=1,
                        cache_misses=0,
                        token_budget=self.token_budget,
                        tokens_used=cached.token_count,
                        references_loaded=0,  # From cache
                        metadata={"cache_hit": True, "orchestrator": orchestrator_name}
                    )

                    # Return cached result with updated cache_hit flag
                    return replace(cached, cache_hit=True)

            # Step 3: Optimize for Copilot (Token Optimizer extension)
            # Add orchestrator metadata for compression strategy selection
            context_with_meta = context.copy() if isinstance(context, dict) else {}
            if orchestrator_name:
                context_with_meta["orchestrator"] = orchestrator_name

            optimized_result = self.optimizer.optimize_for_copilot(context_with_meta)

            # Handle both OptimizedContext (production) and dict (mocked tests)
            if hasattr(optimized_result, 'content'):
                # OptimizedContext from production
                optimized_content = optimized_result.content
            else:
                # Dict from mocked tests
                optimized_content = optimized_result

            # Step 4: Synthesize content (per-orchestrator strategies)
            # Convert optimized context to string for synthesizer
            content_str = str(optimized_content)
            filename = f"{orchestrator_name}_output.txt" if orchestrator_name else "output.txt"

            synthesized_result = self.synthesizer.synthesize_all(
                content=content_str,
                filename=filename,
                metadata={"orchestrator": orchestrator_name}
            )

            # Handle both SynthesisResult (production) and dict (mocked tests)
            if hasattr(synthesized_result, 'content'):
                # SynthesisResult from production
                synthesized_content = synthesized_result.content
                synthesized_size = synthesized_result.compressed_size
                compression_ratio = synthesized_result.compression_ratio
                synthesis_strategy = synthesized_result.strategy
                synthesis_metadata = synthesized_result.metadata
            else:
                # Dict from mocked tests
                synthesized_content = str(synthesized_result)
                synthesized_size = len(synthesized_content)
                compression_ratio = 1.0 - (synthesized_size / original_size) if original_size > 0 else 0.0
                synthesis_strategy = "mocked"
                synthesis_metadata = {}

            # Step 5: Post-synthesis verification
            token_count = self.optimizer.estimate_copilot_tokens(synthesized_content)
            budget_compliant = token_count <= self.token_budget

            # Ensure compression ratio is never negative (metadata overhead for small contexts)
            if compression_ratio < 0:
                compression_ratio = 0.0

            logger.info(
                "Gateway: Synthesis complete (orchestrator=%s, compression=%.1f%%, "
                "tokens=%d/%d, compliant=%s)",
                orchestrator_name,
                compression_ratio * 100,
                token_count,
                self.token_budget,
                "YES" if budget_compliant else "NO"
            )

            # Step 6: Store in cache
            # Reconstruct dict with synthesized content
            synthesized_dict = {
                "synthesized_content": synthesized_content,
                "original_orchestrator": orchestrator_name,
                "compression_strategy": synthesis_strategy,
                "metadata": synthesis_metadata
            }

            result = SynthesizedContext(
                original_size_bytes=original_size,
                synthesized_size_bytes=synthesized_size,
                compression_ratio=compression_ratio,
                synthesis_time_ms=(time.perf_counter() - start_time) * 1000,
                cache_hit=cache_hit,
                context=synthesized_dict,
                session_id=session_id,
                orchestrator_name=orchestrator_name,
                token_count=token_count,
                budget_compliant=budget_compliant
            )

            if self.enable_cache and self.cache and cache_key:
                self.cache.set(cache_key, result)

            # Step 7: Record metrics using end_synthesis
            self.metrics.end_synthesis(
                session_id=session_id,
                size_before=original_size,
                size_after=synthesized_size,
                cache_hits=1 if cache_hit else 0,
                cache_misses=0 if cache_hit else 1,
                token_budget=self.token_budget,
                tokens_used=token_count,
                references_loaded=1,
                metadata={
                    "orchestrator": orchestrator_name,
                    "compression_ratio": compression_ratio,
                    "budget_compliant": budget_compliant
                }
            )

            if not budget_compliant:
                logger.warning(
                    "Gateway: Budget violation (tokens=%d, budget=%d, overflow=%d)",
                    token_count,
                    self.token_budget,
                    token_count - self.token_budget
                )

            # Step 8: Update session cumulative tokens
            self._update_session_tokens(session_id, token_count)

            return result

        except Exception as e:
            logger.error(
                "Gateway: Synthesis error (orchestrator=%s, fail_safe=%s): %s",
                orchestrator_name,
                self.fail_safe,
                str(e),
                exc_info=True
            )

            if self.fail_safe:
                # Return original context (safety mechanism)
                logger.warning("Gateway: Returning original context (fail-safe)")
                original_size = self._calculate_size(context)
                return SynthesizedContext(
                    original_size_bytes=original_size,
                    synthesized_size_bytes=original_size,
                    compression_ratio=0.0,
                    synthesis_time_ms=(time.perf_counter() - start_time) * 1000,
                    cache_hit=False,
                    context=context,
                    session_id=session_id,
                    orchestrator_name=orchestrator_name,
                    token_count=self.optimizer.estimate_copilot_tokens(str(context)),
                    budget_compliant=False
                )
            else:
                raise

    def get_session_tokens(self, session_id: str) -> int:
        """
        Get cumulative token count for session.

        This prevents the ACCELERATION pattern seen in chat01.md where
        summarization events occurred closer together towards the end
        (200 → 18 → 8 lines between events).

        Args:
            session_id: Session identifier

        Returns:
            Cumulative token count across all turns
        """
        return self._session_tokens.get(session_id, 0)

    def reset_session(self, session_id: str):
        """
        Reset cumulative token tracking for session.

        Call this when starting a new conversation or after explicit
        user reset command.

        Args:
            session_id: Session identifier
        """
        if session_id in self._session_tokens:
            del self._session_tokens[session_id]
            logger.info("Gateway: Session reset (session=%s)", session_id)

    def _calculate_size(self, obj: Any) -> int:
        """Calculate approximate size in bytes."""
        return len(str(obj).encode('utf-8'))

    def _build_cache_key(self, context: Dict[str, Any], orchestrator: str) -> str:
        """Build cache key from context + orchestrator."""
        # Simple hash-based key (Phase 4 MVP)
        # Future: Content-addressable hashing for better cache hits
        context_str = str(sorted(context.items()))
        return f"{orchestrator}:{hash(context_str)}"

    def _update_session_tokens(self, session_id: str, tokens: int):
        """Update cumulative session token count."""
        current = self._session_tokens.get(session_id, 0)
        self._session_tokens[session_id] = current + tokens

        cumulative = self._session_tokens[session_id]
        logger.debug(
            "Gateway: Session tokens updated (session=%s, turn_tokens=%d, cumulative=%d)",
            session_id,
            tokens,
            cumulative
        )

        # Warn if cumulative tokens exceed thresholds (prevent acceleration)
        if cumulative > 100000:  # ~5 turns at 20K budget
            logger.warning(
                "Gateway: High cumulative tokens (session=%s, tokens=%d, "
                "acceleration_risk=HIGH)",
                session_id,
                cumulative
            )


# Singleton instance for easy import
_gateway_instance: Optional[ContextSynthesisGateway] = None


def get_gateway() -> ContextSynthesisGateway:
    """Get or create singleton ContextSynthesisGateway instance."""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = ContextSynthesisGateway()
    return _gateway_instance
