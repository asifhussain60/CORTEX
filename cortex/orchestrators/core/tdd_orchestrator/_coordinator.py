# AC-ID: ARCH-012-REFACTOR - TDDOrchestrator V2 with Base Protocol (Phase 103-c slim)
# CORE-035 — domain-scoped; class name appropriate for this module
"""
TDDOrchestrator — slim coordinator after Phase 103-c god-object decomposition.

Responsibilities kept in this file:
- Public data models re-exported for backward compatibility (90+ callers)
- TDDOrchestrator coordinator class (IOrchestrator interface + __init__ + MCP ops)

Extracted to ``cortex/orchestrators/core/tdd_orchestrator/``:
- ``tdd_models.py``         — TDDPhase enum + 5 dataclasses + TDDKnowledgeLoader
- ``tdd_execution_mixin.py`` — RED/GREEN/REFACTOR phase execution
- ``tdd_metrics_mixin.py``  — multi-cycle, quality gates, convergence loop
- ``tdd_batch_mixin.py``    — batched test runner + Chat progress

Phase 103-c: GAP-103-03 — tdd_orchestrator.py 2,121L -> <=750L
Line limit: 750L (data-driven; matches Phase 103-a precedent of 702L)

Governance:
- ARCH-012: Inherits OrchestratorBaseProtocol
- CORE-008: TDD (tests/orchestrators/core/test_tdd_orchestrator_decomposition.py)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- CORE-019: ALL implementation intents route through TDD-Master

Author: Asif Hussain
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Public data models — re-exported for backward compatibility (90+ callers)
# ---------------------------------------------------------------------------
from cortex.orchestrators.core.tdd_orchestrator.tdd_models import (  # noqa: E402
    CycleMetrics,
    GateResult,
    SuccessCriteria,
    TDDDisciplineRule,
    TDDImplementationGuidance,
    TDDKnowledgeLoader,
    TDDPhase,
)

# ---------------------------------------------------------------------------
# Mixin imports
# ---------------------------------------------------------------------------
from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin

# ---------------------------------------------------------------------------
# Framework imports
# ---------------------------------------------------------------------------
from cortex.core.common.standards_resolver import StandardsResolver
from cortex.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.knowledge_guidance_engine import KnowledgeGuidanceEngine
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.result import Err, Ok, Result
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
from cortex.intelligence.learning.opj_mixin import OPJMixin
from cortex.intelligence.learning.reinforcement_signal import SignalType

# Phase 58-C: DomainBrain + Memory tier wiring (optional)
try:
    from cortex.intelligence.domain_brain import DomainBrainAPI as _DomainBrainAPI  # type: ignore[attr-defined]
except Exception:
    _DomainBrainAPI = None  # type: ignore[assignment,misc]

try:
    from cortex.intelligence.memory.tier2_adaptive.hallucination_prevention import (  # type: ignore[import]
        BehavioralBoundaryRules as _TDDBehavioralBoundaryRules,
    )
except Exception:
    _TDDBehavioralBoundaryRules = None  # type: ignore[assignment]

try:
    from cortex.intelligence.memory.tier3_scratch import (  # type: ignore[import]
        get_scratch_space_path as _tdd_get_scratch_path,
    )
except Exception:
    _tdd_get_scratch_path = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# ===========================================================================
# TDDOrchestrator — coordinator
# ===========================================================================


class TDDOrchestrator(
    TDDExecutionMixin,
    TDDMetricsMixin,
    TDDBatchMixin,
    OPJMixin,
    OrchestratorProtocolMixin,
    WorkflowEnforcementMixin,
    WorkflowTemplateMixin,
    IOrchestrator,
):
    """TDD Orchestrator V2 — slim coordinator after Phase 103-c decomposition.

    AUTOMATIC PROTOCOL (inherited from base):
    1. LENS Context Building -> Understands request deeply
    2. Security Assessment -> Blocks vulnerable test/impl code
    3. Challenge Generation -> Suggests better TDD approaches
    4. DoR Confidence Gate -> Blocks <60% confidence requests
    5. TDD Domain Logic -> RED -> GREEN -> REFACTOR

    Phase 90b: WorkflowEnforcementMixin opt-in — all TDD operations route through
    WorkflowGateway -> tdd/tdd-workflow.yaml -> convergence loop.

    Usage:
        >>> orchestrator = TDDOrchestrator()
        >>> result = orchestrator.execute_with_protocol(
        ...     user_request="Implement authentication service",
        ...     context={"module_path": "cortex.auth.service"}
        ... )
    """

    # Phase 90b — Gateway opt-in
    PHASE90_GATEWAY_ENABLED: bool = True

    def __init__(self, knowledge_root: Optional[Path] = None) -> None:
        """Initialise TDD Orchestrator V2.

        Args:
            knowledge_root: Root path to knowledge repository.

        ARCH-012: Inherits protocol initialisation from base class.
        ENH-088: Adds multi-cycle tracking capability.
        """
        # Phase 27: StandardsResolver for company domain integration
        self.standards_resolver = StandardsResolver()

        # TDD-specific components
        self.knowledge_loader = TDDKnowledgeLoader(knowledge_root)
        self.guidance_engine = KnowledgeGuidanceEngine()

        # AC-PHASE24-005: BrittlenessScanner (Wave 7: consolidated, skip)
        self._brittleness_scanner = None

        # AC-PHASE24-007: PhaseCompletionOrchestrator (Wave 7: consolidated, skip)
        self._phase_completion_orchestrator = None

        # ENH-088: Multi-cycle tracking (required by TDDMetricsMixin)
        self._cycle_metrics_history: List[CycleMetrics] = []

        # Phase 07b: Wire canonical TestQualityGate
        from cortex.testing.quality_gate import TestQualityGate
        self.quality_gate = TestQualityGate()

        logger.info(
            f"TDD Orchestrator V2 initialized with base protocol + "
            f"{len(self.knowledge_loader.tdd_yamls)} knowledge YAMLs + "
            f"BrittlenessScanner (AC-PHASE24-005) + "
            f"PhaseCompletionOrchestrator (AC-PHASE24-007) + "
            f"StandardsResolver (Phase 27) + "
            f"TestQualityGate (Phase 07b)"
        )

    # =========================================================================
    # IOrchestrator Interface Implementation (WAVE-7-CLEANUP)
    # AC-WAVE-7-CLEANUP-S2-001: 7 required interface methods
    # =========================================================================

    def get_name(self) -> str:
        """Return orchestrator name identifier.

        Returns:
            Orchestrator name string.

        AC-WAVE-7-CLEANUP-S2-001: IOrchestrator interface compliance.
        """
        return "TDDOrchestrator"

    def get_recommended_template(self) -> Optional[str]:
        """Return the recommended workflow template for TDD operations.

        Returns:
            Template ID string: ``'tdd/tdd-workflow'``.

        Phase 90: Workflow Composer Mandatory Gateway (AC-P90-001).
        Phase 23: Workflow Template Injection (AC-P23-006).
        """
        return "tdd/tdd-workflow"

    def get_version(self) -> str:
        """Return orchestrator version string.

        Returns:
            Semver version string.

        AC-WAVE-7-CLEANUP-S2-001: IOrchestrator interface compliance.
        """
        return "2.0.0"

    def initialize(self) -> Result[str]:
        """Confirm orchestrator is initialised (Result-based interface method).

        Returns:
            Ok on success, Err on failure.

        AC-WAVE-7-CLEANUP-S2-001: IOrchestrator interface compliance.
        """
        try:
            if self.knowledge_loader and self.guidance_engine:
                return Ok("TDDOrchestrator initialized successfully")
            return Err("TDDOrchestrator initialization incomplete")
        except Exception as e:
            return Err(f"TDDOrchestrator initialization failed: {str(e)}")

    def get_mode(self) -> OperationMode:
        """Return operation mode (EXECUTION — TDD is execution-focused).

        Returns:
            OperationMode.EXECUTION.

        AC-WAVE-7-CLEANUP-S2-001: IOrchestrator interface compliance.
        """
        return OperationMode.EXECUTION

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Return exposed MCP tool definitions for TDD operations.

        Returns:
            Ok with MCP tool definition dict.

        AC-WAVE-7-CLEANUP-S2-001: IOrchestrator interface compliance.
        AC-AR-011-02: MCP tool exposure requirement.
        """
        try:
            tools = {
                "cortex_tdd_execute": {
                    "name": "cortex_tdd_execute",
                    "description": "Execute TDD workflow (RED->GREEN->REFACTOR)",
                    "parameters": {
                        "user_request": {"type": "string", "required": True},
                        "module_path": {"type": "string", "required": True},
                        "coverage_target": {"type": "number", "default": 0.8},
                    },
                },
                "cortex_tdd_multi_cycle": {
                    "name": "cortex_tdd_multi_cycle",
                    "description": "Execute multi-cycle TDD until success criteria met (ENH-088)",
                    "parameters": {
                        "user_request": {"type": "string", "required": True},
                        "module_path": {"type": "string", "required": True},
                        "success_criteria": {"type": "object", "required": True},
                    },
                },
                "cortex_tdd_guidance": {
                    "name": "cortex_tdd_guidance",
                    "description": "Get TDD guidance for module from knowledge base",
                    "parameters": {
                        "module_path": {"type": "string", "required": True},
                    },
                },
            }
            return Ok(tools)
        except Exception as e:
            return Err(f"Failed to get MCP tools: {str(e)}")

    # =========================================================================
    # Knowledge context helpers
    # =========================================================================

    def _inject_knowledge_context(self, context: str = "tdd") -> Dict[str, Any]:
        """Inject TDD best-practice knowledge context into cycle generation.

        Phase 78 GAP-78-A-02: Wire knowledge_context from tdd-best-practices.

        Args:
            context: Knowledge domain to query (default: "tdd").

        Returns:
            Dict with TDD strategy guidance from knowledge base.
        """
        try:
            from cortex.intelligence.facade import get_intelligence_facade
            # DESIGN CHOICE (GAP-117-07, Phase 117-b): TDDKnowledgeLoader is an
            # intentional domain-specific loader — NOT a bypass of IntelligenceFacade.
            # Two complementary paths exist:
            #   1. TDDKnowledgeLoader: loads TDD-strategy YAMLs at coordinator init
            #      (fast, offline, deterministic — used for structured guidance).
            #   2. IntelligenceFacade.synthesize(): delegates to the intelligence
            #      pipeline at runtime (context-aware, may call external systems).
            # _inject_knowledge_context() uses path (2) for live synthesis queries.
            facade = get_intelligence_facade()
            return facade.synthesize(query=f"tdd:{context}")
        except Exception:
            return {}

    def _get_tdd_best_practices(self) -> Dict[str, Any]:
        """Return TDD best-practices knowledge for current context.

        Returns:
            Dict with TDD strategy guidance (convenience wrapper).
        """
        return self._inject_knowledge_context(context="tdd")

    # =========================================================================
    # execute_operation — MCP gateway routing
    # =========================================================================

    @enforce_gateway
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute an MCP operation with audit logging.

        Routes to the appropriate TDD method based on operation_name.

        Args:
            operation_name: One of ``tdd_execute``, ``tdd_multi_cycle``,
                            ``tdd_guidance``.
            parameters: Operation parameters dict.

        Returns:
            Result with operation outcome.

        AC-WAVE-7-CLEANUP-S2-001: IOrchestrator interface compliance.
        AC-AR-011-03: Audit logging requirement.
        """
        import time as _time
        _ac_id = f"AC-TDD-{int(_time.time() * 1000)}"
        # AC_START: {_ac_id}
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        try:
            logger.info(f"TDDOrchestrator executing operation: {operation_name}")

            if operation_name == "tdd_execute":
                user_request = parameters.get("user_request", "")
                context = {
                    "module_path": parameters.get("module_path", ""),
                    "coverage_target": parameters.get("coverage_target", 0.8),
                    "source": "mcp_gateway",
                }
                return self._execute_domain_logic(user_request, None, context)

            elif operation_name == "tdd_multi_cycle":
                test_suite = parameters.get("test_suite", "")
                sc_dict = parameters.get("success_criteria", {})
                success_criteria = SuccessCriteria(
                    min_coverage=sc_dict.get("min_coverage", 0.8),
                    max_latency_ms=sc_dict.get("max_latency_ms", 100.0),
                    all_tests_pass=sc_dict.get("all_tests_pass", True),
                    max_complexity=sc_dict.get("max_complexity", 10),
                )
                result_dict = self.execute_multi_cycle(
                    test_suite=test_suite,
                    success_criteria=success_criteria,
                    max_cycles=parameters.get("max_cycles", 5),
                )
                return Ok(result_dict)

            elif operation_name == "tdd_guidance":
                module_path = parameters.get("module_path", "")
                guidance = self.guidance_engine.get_tdd_guidance_for_module(Path(module_path))
                return Ok(guidance)

            else:
                return Err(f"Unknown operation: {operation_name}")

        except Exception as e:
            logger.error(f"Operation {operation_name} failed: {str(e)}")
            # AC_COMPLETE: {_ac_id} failed
            return Err(f"Operation failed: {str(e)}")

        finally:
            # AC_COMPLETE: {_ac_id}
            pass

    # =========================================================================
    # Phase 83-d: URS signal emission
    # =========================================================================

    def _emit_tdd_cycle_signal(
        self,
        operation: str,
        success: bool,
        retries: int = 0,
    ) -> None:
        """Emit a URS reinforcement signal after a TDD cycle completes.

        Signal mapping:
        - GREEN on first try (retries=0)  -> STRONG_REWARD
        - GREEN after retries (retries>0) -> MILD_REWARD
        - Cycle failure                   -> MILD_PUNISHMENT

        Args:
            operation: The TDD operation that completed.
            success: Whether the cycle reached GREEN.
            retries: Number of retry attempts before success.
        """
        if success and retries == 0:
            signal = SignalType.STRONG_REWARD
        elif success:
            signal = SignalType.MILD_REWARD
        else:
            signal = SignalType.MILD_PUNISHMENT

        self._urs_emit_signal(
            signal_type=signal,
            pattern_id=operation,
            context={"success": success, "retries": retries},
        )

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Return audit trail with hash chain.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            Ok with list of audit entries (currently empty — future enhancement).

        AC-WAVE-7-CLEANUP-S2-001: IOrchestrator interface compliance.
        AC-AR-011-03: Hash chain audit logging.
        """
        try:
            return Ok([])
        except Exception as e:
            return Err(f"Failed to get audit trail: {str(e)}")


# ===========================================================================
# Singleton factory
# ===========================================================================


def get_tdd_orchestrator(knowledge_root: Optional[Path] = None) -> TDDOrchestrator:
    """Singleton factory for TDDOrchestrator.

    Args:
        knowledge_root: Root path to knowledge repository.

    Returns:
        Shared TDDOrchestrator instance.
    """
    if not hasattr(get_tdd_orchestrator, "_instance"):
        get_tdd_orchestrator._instance = TDDOrchestrator(knowledge_root)
    return get_tdd_orchestrator._instance


__all__ = [
    "TDDOrchestrator",
    "TDDPhase",
    "TDDDisciplineRule",
    "TDDImplementationGuidance",
    "TDDKnowledgeLoader",
    "SuccessCriteria",
    "CycleMetrics",
    "GateResult",
    "get_tdd_orchestrator",
]
