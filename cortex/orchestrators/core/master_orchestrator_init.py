"""
MasterOrchestratorInitialiser — Phase 80-A2 decomposition.

Extracts the 704-line __init__ body of MasterOrchestrator into named
wire_* methods so that the __init__ remains ≤ 20 AST statements.

All try/except ImportError soft-import blocks that previously lived at
module level in master_orchestrator.py are co-located here with the
components that depend on them (CORE-028 proximity principle).

AC: GAP-80-A-01 — __init__ body extraction
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator


class MasterOrchestratorInitialiser:
    """
    Handles the full subsystem wiring for MasterOrchestrator.__init__.

    Usage::

        def __init__(self) -> None:
            super().__init__()
            self.logger = EnhancedAuditLogger.instance()
            self.domain_orchestrators = {}
            self.operation_history = []
            self.render_markdown = False
            MasterOrchestratorInitialiser(self).wire_all()

    The host's attributes are set directly via ``self._h.<attr> = …``.
    """

    def __init__(self, host: "MasterOrchestrator") -> None:
        """Bind the initialiser to its host MasterOrchestrator instance."""
        self._h = host

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def wire_all(self) -> None:
        """Wire every subsystem in dependency order."""
        self.wire_state_and_logging()
        self.wire_governance()
        self.wire_infrastructure()
        self.wire_health()
        self.wire_knowledge()       # needs infrastructure (db_path)
        self.wire_stages()          # needs knowledge (synthesis engine)
        self.wire_intelligence()    # needs stages (tech intelligence)
        self.wire_capability_verification()  # Phase 137 — GAP-137-02: drift detection

    # ------------------------------------------------------------------
    # wire_state_and_logging
    # ------------------------------------------------------------------

    def wire_state_and_logging(self) -> None:
        """StateManager, RequestLogManager, orchestrator_registry, operation tracking."""
        from cortex.core.state_manager import get_state_manager
        from cortex.orchestrators.core.request_log_manager import RequestLogManager

        h = self._h
        h._state_manager = get_state_manager()
        h.logger.log_operation_complete(
            ac_id="AC-REM-011-05",
            operation="STATE_MANAGER_INIT",
            success=True,
            details={"manager": "StateManager initialized for cross-phase consistency"},
        )

        # Phase 113-B: Wire RequestLogManager for pre-API request persistence (CORE-064)
        try:
            h._request_log_manager = RequestLogManager()
            h.logger.log_operation_complete(
                ac_id="AC-113-B-001",
                operation="REQUEST_LOG_MANAGER_INIT",
                success=True,
                details={"db_path": str(h._request_log_manager.db_path)},
            )
        except Exception as _rlm_err:
            h._request_log_manager = None
            h.logger.log_operation_complete(
                ac_id="AC-113-B-001",
                operation="REQUEST_LOG_MANAGER_INIT",
                success=False,
                details={"error": str(_rlm_err), "fallback": "request logging disabled"},
            )

        # Phase 151-A: Holistic brain integration service (request + intelligence + registry + governance)
        try:
            from cortex.intelligence.holistic_brain_integrator import HolisticBrainIntegrator

            h._holistic_brain_integrator = HolisticBrainIntegrator()
            h.logger.log_operation_complete(
                ac_id="AC-P151-001",
                operation="HOLISTIC_BRAIN_INTEGRATOR_INIT",
                success=True,
                details={"service": "HolisticBrainIntegrator initialized"},
            )
        except Exception as _hbi_err:
            h._holistic_brain_integrator = None
            h.logger.log_operation_complete(
                ac_id="AC-P151-001",
                operation="HOLISTIC_BRAIN_INTEGRATOR_INIT",
                success=False,
                details={"error": str(_hbi_err), "fallback": "holistic context disabled"},
            )

        # Stage placeholder attributes used throughout coordinate_operation
        h.interaction_orchestrator = None
        h.intent_router = None
        h.intent_gateway = None
        h.execution_engine = None
        h.orchestrator_registry = {}
        h.current_operation = None
        h.current_phase = None
        h._turn_number = 0

    # ------------------------------------------------------------------
    # wire_governance
    # ------------------------------------------------------------------

    def wire_governance(self) -> None:
        """DoRApprovalGate, EnforcementOrchestrator, GovernanceRegistry, BoundaryRules."""
        h = self._h

        # AC-GOVE-DOR-WIRE-001
        h._dor_gate = None
        try:
            from cortex.orchestrators.core.dor_approval_gate import DoRApprovalGate
            h._dor_gate = DoRApprovalGate()
            h.logger.log_operation_complete(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="DOR_APPROVAL_GATE_INIT",
                success=True,
                details={"gate": "DoRApprovalGate initialized"},
            )
        except Exception as gate_err:
            h.logger.log_operation_complete(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="DOR_APPROVAL_GATE_INIT",
                success=False,
                details={"error": str(gate_err)},
            )

        # AC-PHASE-6C-001
        h._enforcement = None
        try:
            from cortex.orchestrators.core.enforcement_orchestrator import (
                EnforcementOrchestrator,
            )
            h._enforcement = EnforcementOrchestrator()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-6C-001",
                operation="ENFORCEMENT_ORCHESTRATOR_INIT",
                success=True,
                details={
                    "agent_count": len(h._enforcement.agents),
                    "coverage": "25/29 CORE rules (86%)",
                    "agents": [
                        "GovernanceEnforcementAgent",
                        "SecurityCheckpointAgent",
                        "ComplianceValidationAgent",
                        "FileNamingEnforcementAgent",
                        "IncrementalExecutionAgent",
                        "MarkdownSuppressionAgent",
                        "ArchitectureIntegrityAgent",
                    ],
                },
            )
        except Exception as enforcement_err:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-6C-001",
                operation="ENFORCEMENT_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(enforcement_err)},
            )

        # AC-REM-002-04
        h._governance_registry = None

        # AC-FIX-HALLUCINATION-001
        from cortex.intelligence.memory.tier2_adaptive.hallucination_prevention import (
            BehavioralBoundaryRules,
        )
        h._boundary_rules = BehavioralBoundaryRules()

    # ------------------------------------------------------------------
    # wire_infrastructure
    # ------------------------------------------------------------------

    def wire_infrastructure(self) -> None:
        """DatabaseTransactionManager, StandardsResolver, ResponseHeaderInjector."""
        from cortex.core.common.standards_resolver import StandardsResolver
        from cortex.core.response_header_config import HeaderConfigurationManager
        from cortex.core.response_header_injector import ResponseHeaderInjector
        from cortex.infrastructure.database_transaction_manager import (
            DatabaseTransactionManager,
        )

        h = self._h

        db_path = (
            Path(__file__).parent.parent.parent.parent
            / ".cortex-runtime"
            / "governance.db"
        )
        # P2-B NOTE: This governance.db is at .cortex-runtime/governance.db (root level),
        # used exclusively by DatabaseTransactionManager for scaffolder audit logging.
        # DB consolidation (Phase 104): traces/governance.db and
        # state/cortex_brain/state/governance.db were deleted (both 0 rows, ghost DBs).
        # SharedAuditTrail now writes to .cortex-runtime/audit.db.
        h.transaction_manager = DatabaseTransactionManager(str(db_path))

        h.standards_resolver = StandardsResolver()
        h.logger.log_operation_complete(
            ac_id="AC-PHASE-27-001",
            operation="STANDARDS_RESOLVER_INIT",
            success=True,
            details={"resolver": "StandardsResolver initialized"},
        )

        # AC-ENH-002-01: ResponseHeaderInjector
        h.header_injector = None
        try:
            config_manager = HeaderConfigurationManager.get_instance()
            config_manager.load_configuration("cortex-registry/core/response-headers.yaml")
            h.header_injector = ResponseHeaderInjector(
                template_engine=None,
                config_manager=config_manager,
            )
        except Exception as hdr_err:
            h.logger.log_operation_complete(
                ac_id="AC-ENH-002-01",
                operation="HEADER_INJECTOR_INIT",
                success=False,
                details={"error": str(hdr_err)},
            )

    # ------------------------------------------------------------------
    # wire_health
    # ------------------------------------------------------------------

    def wire_health(self) -> None:
        """ComponentHealthTracker, GracefulDegradationFramework, LifecycleHookSystem."""
        from cortex.orchestrators.core.component_health import (
            ComponentHealthTracker,
            ComponentType,
        )

        h = self._h

        # AC-PHASE-2-5-WIRE-001
        h._component_health_tracker = ComponentHealthTracker()
        for name, ctype in [
            ("MasterOrchestrator", ComponentType.CRITICAL),
            ("ChallengeGenerator", ComponentType.CRITICAL),
            ("HolisticContextBuilder", ComponentType.CRITICAL),
            ("KnowledgeRepository", ComponentType.OPTIONAL),
        ]:
            h._component_health_tracker.register_component(name, ctype)
        h.logger.log_operation_complete(
            ac_id="AC-PHASE-2-5-WIRE-001",
            operation="COMPONENT_HEALTH_TRACKER_INIT",
            success=True,
            details={"message": "Component health tracking initialized"},
        )

        # AC-PHASE-2-5-WIRE-002 — local import to avoid circular at module level
        from cortex.intelligence.memory.tier2_adaptive.resilience import (
            GracefulDegradationFramework,
        )
        h._graceful_degradation = GracefulDegradationFramework()
        h.logger.log_operation_complete(
            ac_id="AC-PHASE-2-5-WIRE-002",
            operation="GRACEFUL_DEGRADATION_INIT",
            success=True,
            details={"message": "Graceful degradation framework initialized"},
        )

        # ENH-092 Phase 53.3 — LifecycleHookSystem
        h._lifecycle_hook_system = None
        try:
            from cortex.orchestrators.core.lifecycle_hook_system import (
                LifecycleHookSystem,
            )
            h._lifecycle_hook_system = LifecycleHookSystem(vacuum_orchestrator=None)
            h.logger.log_operation_complete(
                ac_id="AC-ENH-092-001",
                operation="LIFECYCLE_HOOK_SYSTEM_INIT",
                success=True,
                details={"system": "LifecycleHookSystem initialized"},
            )
        except Exception as lifecycle_err:
            h.logger.log_operation_complete(
                ac_id="AC-ENH-092-001",
                operation="LIFECYCLE_HOOK_SYSTEM_INIT",
                success=False,
                details={"error": str(lifecycle_err)},
            )

    # ------------------------------------------------------------------
    # wire_knowledge
    # ------------------------------------------------------------------

    def wire_knowledge(self) -> None:
        """
        KnowledgeRegistryProxy, UnifiedIntelligenceProvider,
        KnowledgeRepository, BusinessKnowledgeRepository,
        IntelligentKnowledgeRouter, KnowledgeSynthesisEngine.
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        h = self._h

        # Phase 109: IntelligenceFacade replaces direct KnowledgeRegistryProxy
        # and direct provider init — single canonical entry point.
        # GAP-117-05 (Phase 117-b): use get_intelligence_facade() to ensure
        # the process-level singleton is used — no extra allocations.
        from cortex.intelligence.facade import get_intelligence_facade
        h._intelligence_facade = get_intelligence_facade()

        # Expose underlying delegates for backward compatibility:
        # - _knowledge_proxy: used by knowledge synthesis engine wiring below
        # - _intelligence_provider: used by _get_intelligence_context() tier calls
        h._knowledge_proxy = h._intelligence_facade._get_registry()
        h._intelligence_provider = h._intelligence_facade._get_provider()

        h.logger.log_operation_complete(
            ac_id="AC-PHASE109-A-001",
            operation="INTELLIGENCE_FACADE_INIT",
            success=True,
            details={
                "facade": "IntelligenceFacade (Phase 109 — diamond entry point)",
                "provider_type": type(h._intelligence_provider).__name__,
                "registry_type": type(h._knowledge_proxy).__name__,
            },
        )

        # AC-KN-002-01: KnowledgeRepository
        h._knowledge_repository = None
        try:
            from cortex.core.knowledge.knowledge_repository import KnowledgeRepository
            h._knowledge_repository = KnowledgeRepository()
            h.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_REPOSITORY_INIT",
                success=True,
                details={
                    "entry_count": h._knowledge_repository.entry_count,
                    "domains": h._knowledge_repository.domains,
                },
            )
        except FileNotFoundError as e:
            h.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_REPOSITORY_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-KN-003-01: BusinessKnowledgeRepository
        h._business_knowledge_repository = None
        try:
            from cortex.intelligence.domain_brain.business_knowledge_repository import (
                BusinessKnowledgeRepository,
            )
            h._business_knowledge_repository = BusinessKnowledgeRepository()
            h.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_REPOSITORY_INIT",
                success=True,
                details={
                    "domains": h._business_knowledge_repository.domains,
                    "entry_count": h._business_knowledge_repository.entry_count,
                },
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_REPOSITORY_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-IKP-002-02: IntelligentKnowledgeRouter
        h.router = None
        h._adaptive_router = None
        try:
            from cortex.core.knowledge.router import IntelligentKnowledgeRouter
            if h._knowledge_repository and h._business_knowledge_repository:
                h.router = IntelligentKnowledgeRouter(
                    tech_provider=h._knowledge_repository,
                    business_provider=h._business_knowledge_repository,
                    tech_confidence_threshold=70.0,
                    business_confidence_threshold=70.0,
                    fallback_threshold=50.0,
                )
                h._adaptive_router = h.router
                h.logger.log_operation_complete(
                    ac_id="AC-IKP-002-02",
                    operation="ROUTER_INIT",
                    success=True,
                    details={
                        "tech_provider": "KnowledgeRepository",
                        "business_provider": "BusinessKnowledgeRepository",
                    },
                )
            else:
                h.router = self._make_fallback_router(h)
                h.logger.log_operation_complete(
                    ac_id="AC-IKP-002-02",
                    operation="ROUTER_INIT",
                    success=False,
                    details={"error": "Using fallback router — one or both backends unavailable"},
                )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-IKP-002-02",
                operation="ROUTER_INIT",
                success=False,
                details={"error": str(e)},
            )
            # Ensure router is never None — fall back to FallbackRouter on any init error
            if h.router is None:
                h.router = self._make_fallback_router(h)

        # AC-PHASE-2-5-WIRE-003 placeholder log (router already set above)
        if h._adaptive_router is None:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-2-5-WIRE-003",
                operation="ADAPTIVE_ROUTER_PLACEHOLDER",
                success=True,
                details={"message": "Adaptive router unavailable (degraded)"},
            )

        # AC-HYBRID-KNOWLEDGE-005: KnowledgeSynthesisEngine
        h._synthesis_engine = None
        try:
            h._synthesis_engine = KnowledgeSynthesisEngine()
            h.logger.log_operation_complete(
                ac_id="AC-HYBRID-KNOWLEDGE-005",
                operation="SYNTHESIS_ENGINE_INIT",
                success=True,
                details={"message": "Knowledge synthesis engine initialized"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-HYBRID-KNOWLEDGE-005",
                operation="SYNTHESIS_ENGINE_INIT",
                success=False,
                details={"error": str(e)},
            )

    # ------------------------------------------------------------------
    # wire_stages
    # ------------------------------------------------------------------

    def wire_stages(self) -> None:
        """
        InteractionOrchestrator (with challenge system), IntentRouter,
        TDDOrchestrator, PlanOrchestrator, CortexMasterPlanOrchestrator,
        ContextAwareSynthesisGateway.
        """
        h = self._h

        # AC-CHALLENGE-SYSTEM-002 + AC-PERMANENT-FIX-006
        h.interaction_orchestrator_with_challenges = None
        try:
            from cortex.orchestrators.core.conversation_protocol import (
                ConversationProtocol as ConvProtocol,
            )
            from cortex.orchestrators.core.interaction_orchestrator import (
                InteractionOrchestrator as InteractionOrch,
            )
            protocol = ConvProtocol(orchestrator=h)
            h.interaction_orchestrator_with_challenges = InteractionOrch(
                conversation_protocol=protocol,
                enable_challenges=True,
            )
            h.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-006",
                operation="INTERACTION_ORCHESTRATOR_INIT",
                success=True,
                details={"enable_challenges": True, "stage": "Stage_1_comprehension"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-006",
                operation="INTERACTION_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # Wire Stage 1 — prefer challenge-enabled, fall back to Stage1 class
        if h.interaction_orchestrator_with_challenges:
            h.interaction_orchestrator = h.interaction_orchestrator_with_challenges
            h.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-006",
                operation="STAGE_1_CHALLENGE_SYSTEM_ACTIVE",
                success=True,
                details={"stage": "InteractionOrchestrator with challenge system"},
            )
        elif not h.interaction_orchestrator:
            try:
                from cortex.orchestrators.core.master_orchestrator_stage_1 import (
                    MasterOrchestrationStage1,
                )
                h.interaction_orchestrator = MasterOrchestrationStage1()
                h.logger.log_operation_complete(
                    ac_id="AC-REM-011-01",
                    operation="STAGE_1_FALLBACK_INIT",
                    success=True,
                    details={"stage": "MasterOrchestrationStage1 (fallback)"},
                )
            except Exception as e:
                h.logger.log_operation_complete(
                    ac_id="AC-REM-011-01",
                    operation="STAGE_1_INIT",
                    success=False,
                    details={"error": str(e)},
                )

        # Phase 113-C: Inject RequestLogManager into InteractionOrchestrator for context chain
        if h.interaction_orchestrator is not None and h._request_log_manager is not None:
            try:
                if hasattr(h.interaction_orchestrator, "set_request_log_manager"):
                    h.interaction_orchestrator.set_request_log_manager(h._request_log_manager)
                    h.logger.log_operation_complete(
                        ac_id="AC-113-C-001",
                        operation="INTERACTION_ORCHESTRATOR_CONTEXT_CHAIN_WIRED",
                        success=True,
                        details={"stage": "Prior-request context chain active (Phase 113-C)"},
                    )
            except Exception as _wire_err:
                h.logger.log_operation_complete(
                    ac_id="AC-113-C-001",
                    operation="INTERACTION_ORCHESTRATOR_CONTEXT_CHAIN_WIRED",
                    success=False,
                    details={"error": str(_wire_err)},
                )

        # Stage 2: IntentRouter
        try:
            from cortex.orchestrators.core.intent_router import IntentRouter
            h.intent_router = IntentRouter()
            h.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_2_INIT",
                success=True,
                details={"stage": "Intent Router initialized"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_2_INIT",
                success=False,
                details={"error": str(e)},
            )

        # Phase-M2-b: IntentGateway (consumer migration foundation)
        try:
            from cortex.core.intent_gateway import IntentGateway
            h.intent_gateway = IntentGateway()
            h.logger.log_operation_complete(
                ac_id="AC-V2-M2-B-001",
                operation="INTENT_GATEWAY_INIT",
                success=True,
                details={"stage": "IntentGateway initialized"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-V2-M2-B-001",
                operation="INTENT_GATEWAY_INIT",
                success=False,
                details={"error": str(e)},
            )

        # Phase-M2-c: ExecutionEngine (consumer migration foundation)
        try:
            from cortex.core.execution_engine import ExecutionEngine
            h.execution_engine = ExecutionEngine()
            h.logger.log_operation_complete(
                ac_id="AC-V2-M2-C-001",
                operation="EXECUTION_ENGINE_INIT",
                success=True,
                details={"stage": "ExecutionEngine initialized"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-V2-M2-C-001",
                operation="EXECUTION_ENGINE_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-REM-011-02: TDDOrchestrator
        h.tdd_orchestrator = None
        try:
            from cortex.orchestrators.core.tdd_orchestrator import (
                get_tdd_orchestrator,
            )
            h.tdd_orchestrator = get_tdd_orchestrator()
            tdd_status = h.tdd_orchestrator.get_tdd_status()
            h.logger.log_operation_complete(
                ac_id="AC-REM-011-02",
                operation="TDD_ORCHESTRATOR_INIT",
                success=True,
                details={
                    "status": "TDD Orchestrator initialized",
                    "knowledge_loaded": tdd_status.get("knowledge_loaded", {}),
                },
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-REM-011-02",
                operation="TDD_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-PHASE-25-STAGE-4-002: PlanOrchestrator
        h.plan_orchestrator = None
        try:
            from cortex.orchestrators.support.plan_orchestrator import PlanOrchestrator
            h.plan_orchestrator = PlanOrchestrator()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-25-STAGE-4-002",
                operation="PLAN_ORCHESTRATOR_INIT",
                success=True,
                details={"status": "PlanOrchestrator initialized"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-25-STAGE-4-002",
                operation="PLAN_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-PHASE-50-001: CortexMasterPlanOrchestrator
        h.master_plan_orchestrator = None
        try:
            from cortex.orchestrators.core.master_plan_orchestrator import (
                CortexMasterPlanOrchestrator,
            )
            h.master_plan_orchestrator = CortexMasterPlanOrchestrator()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-50-001",
                operation="MASTER_PLAN_ORCHESTRATOR_INIT",
                success=True,
                details={"status": "CortexMasterPlanOrchestrator initialized"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-50-001",
                operation="MASTER_PLAN_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # Phase 129: DistillationOrchestrator
        h._distillation_orchestrator = None
        try:
            from cortex.orchestrators.support.distillation_orchestrator import (
                DistillationOrchestrator,
            )
            h._distillation_orchestrator = DistillationOrchestrator()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-129-001",
                operation="DISTILLATION_ORCHESTRATOR_INIT",
                success=True,
                details={"status": "DistillationOrchestrator initialized for /distill routing"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-129-001",
                operation="DISTILLATION_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # Phase 130: ContentOptimizationOrchestrator
        h._content_optimization_orchestrator = None
        try:
            from cortex.orchestrators.support.content_optimization_orchestrator import (
                ContentOptimizationOrchestrator,
            )
            h._content_optimization_orchestrator = ContentOptimizationOrchestrator()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-130-001",
                operation="CONTENT_OPTIMIZATION_ORCHESTRATOR_INIT",
                success=True,
                details={"status": "ContentOptimizationOrchestrator initialized for /optimize routing"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-130-001",
                operation="CONTENT_OPTIMIZATION_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-PHASE-90-STAGE-4-001: ContextAwareSynthesisGateway
        h.synthesis_gateway = None
        try:
            from cortex.orchestrators.core.context_synthesis_gateway import get_gateway
            h.synthesis_gateway = get_gateway()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-90-STAGE-4-001",
                operation="SYNTHESIS_GATEWAY_INIT",
                success=True,
                details={"status": "ContextAwareSynthesisGateway initialized"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-90-STAGE-4-001",
                operation="SYNTHESIS_GATEWAY_INIT",
                success=False,
                details={"error": str(e)},
            )

    # ------------------------------------------------------------------
    # wire_intelligence
    # ------------------------------------------------------------------

    def wire_intelligence(self) -> None:
        """
        TechIntelligenceOrchestrator, AutonomousPlanExecutor,
        ASCIIProgressBar, ChallengeGenerator, HolisticContextBuilder.
        """
        from cortex.orchestrators.core.holistic_context_builder import (
            HolisticContextBuilder,
        )
        from cortex.orchestrators.core.intent_router.challenge_generator import (
            ChallengeGenerator,
        )

        h = self._h

        # AC-PHASE-2-WIRE-001 / AC-PHASE-2-WIRE-002 — always available (hard deps)
        h._challenge_generator = ChallengeGenerator()
        h._holistic_context_builder = HolisticContextBuilder()

        # AC-PHASE-34B-WEEK-3-INC-7: TechIntelligenceOrchestrator
        h.tech_intelligence_orchestrator = None
        try:
            from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import (
                TechIntelligenceOrchestrator,
            )
            h.tech_intelligence_orchestrator = TechIntelligenceOrchestrator()
            if h.tech_intelligence_orchestrator.initialize():
                h.logger.log_operation_complete(
                    ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                    operation="TECH_INTELLIGENCE_ORCHESTRATOR_INIT",
                    success=True,
                    details={"status": "TechIntelligenceOrchestrator initialized"},
                )
            else:
                h.logger.log_operation_complete(
                    ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                    operation="TECH_INTELLIGENCE_ORCHESTRATOR_INIT",
                    success=False,
                    details={"error": "initialize() returned failure"},
                )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-PHASE-35-001: AutonomousPlanExecutor
        h._autonomous_executor = None
        try:
            from cortex.orchestrators.core.autonomous_plan_executor import (
                AutonomousPlanExecutor,
            )
            h._autonomous_executor = AutonomousPlanExecutor()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-35-001",
                operation="AUTONOMOUS_EXECUTOR_INIT",
                success=True,
                details={"feature": "Continuation detection"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-35-001",
                operation="AUTONOMOUS_EXECUTOR_INIT",
                success=False,
                details={"error": str(e)},
            )

        # AC-PHASE-35-002: ASCIIProgressBar
        h._progress_bar = None
        try:
            from cortex.orchestrators.core.ascii_progress_bar import (
                ASCIIProgressBar,
            )
            h._progress_bar = ASCIIProgressBar()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-35-002",
                operation="ASCII_PROGRESS_BAR_INIT",
                success=True,
                details={"feature": "ASCII progress bars"},
            )
        except Exception as e:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE-35-002",
                operation="ASCII_PROGRESS_BAR_INIT",
                success=False,
                details={"error": str(e)},
            )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_fallback_router(host: "MasterOrchestrator") -> Any:
        """
        Return a FallbackRouter when full providers are not both available.

        Defined here (not inline inside __init__) to avoid the
        module-level dataclass-inside-function anti-pattern.
        """

        @dataclass
        class FallbackRouter:
            """Fallback router when knowledge backends unavailable."""

            backends: Dict[str, Any] = field(default_factory=dict)

            def route_query(self, query: str) -> Tuple[Any, float, Dict[str, Any]]:
                """Route a query to the first available backend, returning (backend, confidence, metadata)."""
                if self.backends:
                    key = list(self.backends.keys())[0]
                    backend = self.backends[key]
                else:
                    key = "fallback"
                    backend = None
                return backend, 0.3, {
                    "selected_backend": key,
                    "confidence": 0.3,
                    "degraded": True,
                    "reason": "One or both knowledge backends unavailable",
                }

        backends: Dict[str, Any] = {}
        if host._knowledge_repository is not None:
            backends["tech"] = host._knowledge_repository
        if host._business_knowledge_repository is not None:
            backends["business"] = host._business_knowledge_repository
        return FallbackRouter(backends=backends)

    # ------------------------------------------------------------------
    # wire_capability_verification — Phase 137 GAP-137-02
    # ------------------------------------------------------------------

    def wire_capability_verification(self) -> None:
        """Run import-time drift detection against capabilities-manifest.yaml.

        Calls verify_capabilities_manifest() and logs any unimportable
        orchestrator modules as P1 warnings. Non-blocking — drift is
        reported but does not prevent MasterOrchestrator from starting.

        Phase: 137 — GAP-137-02 (CORE-035: detect architecture drift at init-time)
        """
        try:
            from cortex.core.capability_verifier import verify_capabilities_manifest
            from pathlib import Path as _Path
            manifest_path = (
                _Path(__file__).resolve().parents[3]
                / "cortex-registry"
                / "core"
                / "capabilities-manifest.yaml"
            )
            if manifest_path.exists():
                drift = verify_capabilities_manifest(str(manifest_path))
                if drift:
                    self._h.logger.log_operation_complete(
                        ac_id="AC-137-B-001",
                        operation="CAPABILITY_DRIFT_DETECTED",
                        success=False,
                        details={
                            "drift_count": len(drift),
                            "drift_modules": [d["module"] for d in drift],
                            "severity": "P1",
                        },
                    )
                else:
                    self._h.logger.log_operation_complete(
                        ac_id="AC-137-B-001",
                        operation="CAPABILITY_VERIFICATION_COMPLETE",
                        success=True,
                        details={"drift_count": 0},
                    )
        except Exception as _exc:
            # Non-blocking fallback — drift detection failure must not crash init
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "wire_capability_verification: skipped — %s", _exc
            )
