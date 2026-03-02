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

    # ------------------------------------------------------------------
    # wire_state_and_logging
    # ------------------------------------------------------------------

    def wire_state_and_logging(self) -> None:
        """StateManager, orchestrator_registry, operation tracking."""
        from cortex.core.state_manager import get_state_manager

        h = self._h
        h._state_manager = get_state_manager()
        h.logger.log_operation_complete(
            ac_id="AC-REM-011-05",
            operation="STATE_MANAGER_INIT",
            success=True,
            details={"manager": "StateManager initialized for cross-phase consistency"},
        )

        # Stage placeholder attributes used throughout coordinate_operation
        h.interaction_orchestrator = None
        h.intent_router = None
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
        # It is DISTINCT from:
        #   - .cortex-runtime/traces/governance.db  (SharedAuditTrail — cross-repo events)
        #   - .cortex-runtime/state/cortex_brain/state/governance.db  (LEGACY — dissolved
        #     cortex/brain/ package; this path is written to by ConversationProtocol/AuditMixin
        #     but receives 0 rows if cortex_brain is not instantiated. Safe to ignore; it is
        #     VACUUM'd by refresh_prompt_suite.py --db-cleanup after 30-day retention.)
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
            get_synthesis_engine,
        )

        h = self._h

        # Phase 62-H: Unified Knowledge Registry Proxy
        h._knowledge_proxy = None
        try:
            from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy
            h._knowledge_proxy = KnowledgeRegistryProxy()
            h.logger.log_operation_complete(
                ac_id="AC-PHASE62-H-001",
                operation="UNIFIED_KNOWLEDGE_PROXY_INIT",
                success=True,
                details={
                    "entry_count": h._knowledge_proxy.entry_count(),
                    "domains": h._knowledge_proxy.domains(),
                    "sources": h._knowledge_proxy.sources(),
                },
            )
        except Exception as exc:
            h.logger.log_operation_complete(
                ac_id="AC-PHASE62-H-001",
                operation="UNIFIED_KNOWLEDGE_PROXY_INIT",
                success=False,
                details={"error": str(exc)},
            )

        # Phase 65 S4: UnifiedIntelligenceProvider (unconditional — CORE-035)
        from cortex.intelligence.provider import get_intelligence_provider
        h._intelligence_provider = get_intelligence_provider()
        h.logger.log_operation_complete(
            ac_id="AC-PHASE65-S4-001",
            operation="UNIFIED_INTELLIGENCE_PROVIDER_INIT",
            success=True,
            details={"provider": "UnifiedIntelligenceProvider singleton initialized (CORE-035)"},
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

        # AC-PHASE-90-STAGE-4-001: ContextAwareSynthesisGateway
        h.synthesis_gateway = None
        try:
            from cortex.orchestrators.synthesis.context_aware_synthesis import (
                ContextAwareSynthesisGateway,
            )
            repo_path = Path.cwd()
            company_path = repo_path / "cortex-registry" / "company" / "domains"
            h.synthesis_gateway = ContextAwareSynthesisGateway(
                repo_path=repo_path,
                company_path=company_path if company_path.exists() else None,
            )
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
        from cortex.orchestrators.core.intent_router.challenge_generator import (
            ChallengeGenerator,
        )
        from cortex.orchestrators.core.holistic_context_builder import (
            HolisticContextBuilder,
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
            from cortex.orchestrators.response.ascii_progress_bar import (
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
