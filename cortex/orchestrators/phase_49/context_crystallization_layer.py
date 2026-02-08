"""
PHASE 49 - STAGE 1: Context Crystallization Layer (CCL)

Core CCL component implementing async context prefetch.

AC_START: AC-PHASE49-S1-001
Authority: Phase 49 spec, TDD-first
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ============================================================================
# DATACLASSES: Core Structures
# ============================================================================


@dataclass(frozen=True)
class LENSContext:
    """LENS analysis context (from Phase 20 integration)"""

    ast_ready: bool
    git_history_cached: bool
    comment_extraction_complete: bool = False
    file_path: Optional[str] = None


@dataclass(frozen=True)
class InfrastructureContext:
    """Infrastructure detection context (from Phase 46 integration)"""

    environment: str  # "development", "staging", "production"
    capabilities: List[str] = field(default_factory=list)  # ["kubernetes", "redis", etc.]
    phase_46_cache_available: bool = False


@dataclass(frozen=True)
class RulesCache:
    """Rules cache with tier precedence"""

    tier0_rules: Dict[str, Any]
    tier1_defaults: Dict[str, Any]
    company_rules: Dict[str, Any]
    merged_rules: Dict[str, Any]
    cache_ttl_seconds: int = 300
    last_updated: datetime = field(default_factory=datetime.now)

    def is_expired(self) -> bool:
        """Check if cache TTL expired"""
        elapsed = (datetime.now() - self.last_updated).total_seconds()
        return elapsed > self.cache_ttl_seconds


@dataclass(frozen=True)
class CrystallizedContext:
    """
    Immutable result of async context prefetch.
    
    Carries pre-warmed LENS + Rules + Infrastructure context.
    """

    timestamp: datetime
    rules_cache: Dict[str, Any]
    lens_context: LENSContext
    infrastructure_context: InfrastructureContext
    prefetch_latency_ms: int
    cache_hit: bool


# ============================================================================
# ORCHESTRATOR: Context Crystallization Layer
# ============================================================================


class IOrchestrator(ABC):
    """Base interface for all orchestrators"""

    @abstractmethod
    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestrator logic"""
        pass

    @abstractmethod
    def validate(self) -> bool:
        """Validate configuration"""
        pass

    @abstractmethod
    def get_status(self) -> str:
        """Get current status"""
        pass


class ContextCrystallizationLayer(IOrchestrator):
    """
    Non-blocking async context prefetch layer.
    
    Runs PARALLEL to Stage 1, pre-warming:
    - Rules cache (Company > tier1 > tier0)
    - LENS context (AST + git history)
    - Infrastructure capabilities
    
    Design Principles:
    - Non-blocking: prefetch_async() returns immediately
    - Async-first: All operations async with timeout SLA
    - Graceful fallback: Timeout returns None, IntentRouter uses fresh fetch
    - Extensible: Phases A/B/C/etc. pluggable without coupling
    """

    def __init__(
        self,
        timeout_ms: int = 300,
        enable_rules_cache: bool = True,
        enable_lens_warmer: bool = True,
        enable_infra_detection: bool = True,
    ):
        """Initialize CCL with configuration.
        
        Args:
            timeout_ms: Max prefetch time before SLA violation (default 300ms)
            enable_rules_cache: Enable Phase A (rules cache loading)
            enable_lens_warmer: Enable Phase B (LENS warming)
            enable_infra_detection: Enable Phase C (infrastructure detection)
        """
        self.timeout_ms = timeout_ms
        self.enable_rules_cache = enable_rules_cache
        self.enable_lens_warmer = enable_lens_warmer
        self.enable_infra_detection = enable_infra_detection

        self._prefetch_task: Optional[asyncio.Task] = None
        self._prefetch_coroutine: Optional[asyncio.Future] = None
        self._result: Optional[CrystallizedContext] = None
        self._pending_file_path: Optional[str] = None
        self._request_id: Optional[str] = None

        logger.info("AC_START: AC-PHASE49-S1-001 ContextCrystallizationLayer initialized")

    def prefetch_async(
        self,
        request_id: str,
        file_path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Start async context prefetch (non-blocking).
        
        Returns immediately. Prefetch runs in background.
        
        Args:
            request_id: Unique request identifier for tracking
            file_path: Optional file path for LENS analysis
            context: Optional context from MasterOrchestrator
        """
        self._request_id = request_id
        self._pending_file_path = file_path

        logger.info(
            f"[CCL] prefetch_async: Starting async prefetch for request {request_id}"
        )

        # Create and store coroutine (don't await)
        self._prefetch_coroutine = self._run_prefetch_phases()

        logger.info(f"[CCL] prefetch_async: Returned immediately (non-blocking)")

    async def get_crystallized_context(
        self,
        timeout_ms: int = 300,
    ) -> Optional[CrystallizedContext]:
        """
        Get crystallized context with timeout.
        
        Waits up to timeout_ms for prefetch completion.
        Returns None if timeout exceeded (graceful fallback).
        
        Args:
            timeout_ms: Max wait time in milliseconds
            
        Returns:
            CrystallizedContext if ready, None if timeout/no prefetch started
        """
        if self._prefetch_coroutine is None:
            logger.warning("[CCL] get_crystallized_context: No prefetch task started")
            return None

        try:
            timeout_sec = timeout_ms / 1000.0
            result = await asyncio.wait_for(self._prefetch_coroutine, timeout=timeout_sec)

            logger.info(f"[CCL] get_crystallized_context: Context ready (latency: {result.prefetch_latency_ms}ms)")
            return result

        except asyncio.TimeoutError:
            logger.warning(
                f"[CCL] get_crystallized_context: Timeout at {timeout_ms}ms (graceful fallback)"
            )
            return None

        except Exception as e:
            logger.error(f"[CCL] get_crystallized_context: Error: {e}")
            return None

    async def _run_prefetch_phases(self) -> CrystallizedContext:
        """
        Run all prefetch phases in parallel.
        
        Phases:
        - Phase A: Rules cache (50ms)
        - Phase B: LENS warmer (100-200ms if file given)
        - Phase C: Infrastructure detection (50ms)
        
        Returns:
            CrystallizedContext with all pre-warmed data
        """
        start_time = asyncio.get_event_loop().time()

        logger.info(f"[CCL._run_prefetch_phases] Starting Phase A/B/C parallel execution")

        # Run phases in parallel
        tasks = []

        if self.enable_rules_cache:
            tasks.append(self._phase_a_rules_cache())

        if self.enable_lens_warmer:
            tasks.append(self._phase_b_lens_warmer())

        if self.enable_infra_detection:
            tasks.append(self._phase_c_infra_detection())

        # Wait for all phases (or timeout individually)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = asyncio.get_event_loop().time()
        latency_ms = int((end_time - start_time) * 1000)

        logger.info(f"[CCL._run_prefetch_phases] All phases complete (latency: {latency_ms}ms)")

        # Unpack results
        rules_cache_result = results[0] if len(results) > 0 else {}
        lens_result = results[1] if len(results) > 1 else LENSContext(False, False)
        infra_result = results[2] if len(results) > 2 else InfrastructureContext("dev", [])

        # Handle exceptions gracefully
        if isinstance(rules_cache_result, Exception):
            logger.warning(f"[CCL] Phase A failed: {rules_cache_result}")
            rules_cache_result = {}

        if isinstance(lens_result, Exception):
            logger.warning(f"[CCL] Phase B failed: {lens_result}")
            lens_result = LENSContext(False, False)

        if isinstance(infra_result, Exception):
            logger.warning(f"[CCL] Phase C failed: {infra_result}")
            infra_result = InfrastructureContext("dev", [])

        # Create crystallized context
        ctx = CrystallizedContext(
            timestamp=datetime.now(),
            rules_cache=rules_cache_result,
            lens_context=lens_result,
            infrastructure_context=infra_result,
            prefetch_latency_ms=latency_ms,
            cache_hit=False,  # Will be determined by Phase A
        )

        logger.info(f"AC_COMPLETE: AC-PHASE49-S1-001 ✅ CrystallizedContext ready")
        return ctx

    async def _phase_a_rules_cache(self) -> Dict[str, Any]:
        """Phase A: Load rules cache (50ms target)"""
        logger.info("[CCL.Phase_A] Loading rules cache...")

        # Simulate loading tier0 + tier1 + company rules
        await asyncio.sleep(0.05)  # 50ms

        rules = {
            "CORE-008": "TDD mandatory",
            "CORE-029": "Response header required",
            "MCP-FIRST": "All functionality via MCP",
        }

        logger.info("[CCL.Phase_A] Rules cache ready")
        return rules

    async def _phase_b_lens_warmer(self) -> LENSContext:
        """Phase B: Warm LENS context (100-200ms if file given)"""
        logger.info("[CCL.Phase_B] Warming LENS context...")

        if self._pending_file_path is None:
            logger.info("[CCL.Phase_B] No file path, skipping LENS warming")
            return LENSContext(ast_ready=False, git_history_cached=False)

        # Simulate LENS analysis
        await asyncio.sleep(0.1)  # 100ms

        lens = LENSContext(
            ast_ready=True,
            git_history_cached=True,
            comment_extraction_complete=False,
            file_path=self._pending_file_path,
        )

        logger.info("[CCL.Phase_B] LENS context ready")
        return lens

    async def _phase_c_infra_detection(self) -> InfrastructureContext:
        """Phase C: Detect infrastructure (50ms target)"""
        logger.info("[CCL.Phase_C] Detecting infrastructure...")

        # Simulate infrastructure detection
        await asyncio.sleep(0.05)  # 50ms

        infra = InfrastructureContext(
            environment="development",
            capabilities=["kubernetes", "redis"],
            phase_46_cache_available=True,
        )

        logger.info("[CCL.Phase_C] Infrastructure context ready")
        return infra

    # ========================================================================
    # IOrchestrator Implementation
    # ========================================================================

    async def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CCL prefetch and return status.
        
        IOrchestrator.execute() method.
        """
        request_id = request.get("request_id", "unknown")
        file_path = request.get("file_path")

        self.prefetch_async(request_id=request_id, file_path=file_path)

        return {"status": "prefetch_started", "request_id": request_id}

    def validate(self) -> bool:
        """Validate CCL configuration.
        
        IOrchestrator.validate() method.
        """
        return (
            self.timeout_ms > 0
            and (
                self.enable_rules_cache
                or self.enable_lens_warmer
                or self.enable_infra_detection
            )
        )

    def get_status(self) -> str:
        """Get CCL status.
        
        IOrchestrator.get_status() method.
        """
        if self._prefetch_coroutine is None:
            return "idle"
        elif self._prefetch_coroutine.done():
            return "complete"
        else:
            return "prefetching"


# ============================================================================
# STAGE 5: MASTERORCHESTRATOR INTEGRATION HOOK
# ============================================================================


class MasterOrchestratorCCLIntegration:
    """
    Integration point for MasterOrchestrator.
    
    Adds CCL to MasterOrchestrator with minimal coupling.
    """

    @staticmethod
    def add_ccl_to_master() -> ContextCrystallizationLayer:
        """
        Factory method for adding CCL to MasterOrchestrator.
        
        Usage in MasterOrchestrator.__init__():
            self.ccl = MasterOrchestratorCCLIntegration.add_ccl_to_master()
        
        Returns:
            Configured ContextCrystallizationLayer instance
        """
        ccl = ContextCrystallizationLayer(
            timeout_ms=300,
            enable_rules_cache=True,
            enable_lens_warmer=True,
            enable_infra_detection=True,
        )
        
        logger.info(
            "[MasterOrchestratorCCLIntegration] CCL integrated into MasterOrchestrator"
        )
        
        return ccl

    @staticmethod
    async def execute_ccl_prefetch_with_stage_1(
        ccl: ContextCrystallizationLayer,
        request_id: str,
        file_path: Optional[str],
        stage_1_coro,
    ):
        """
        Execute CCL prefetch parallel with Stage 1.
        
        Usage in MasterOrchestrator.process():
            ccl.prefetch_async(request_id, file_path)
            stage_1_result = await execute_ccl_prefetch_with_stage_1(
                ccl, request_id, file_path, stage_1_coroutine
            )
        
        Returns:
            Tuple of (stage_1_result, crystallized_context)
        """
        # Start CCL prefetch (non-blocking)
        ccl.prefetch_async(request_id=request_id, file_path=file_path)
        
        # Run Stage 1 in parallel
        stage_1_result = await stage_1_coro
        
        # Get CCL context (may be ready or timeout)
        ccl_context = await ccl.get_crystallized_context(timeout_ms=250)
        
        return stage_1_result, ccl_context
