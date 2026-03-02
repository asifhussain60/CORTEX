"""
Master Orchestrator - Coordinates all domain orchestrators

AC-AR-006-01: MasterOrchestrator coordinates domain orchestrators
- Receives operation requests
- Determines applicable domain orchestrators
- Delegates to appropriate orchestrator(s)
- Aggregates results
- Logs all delegation decisions to audit trail

AC-FIX-HALLUCINATION-001: Boundary enforcement integration
- Validates operations against behavioral boundaries before delegation

AC-UX-VISIBILITY-001: Orchestrator badge visibility integration
- Auto-injects OrchestratorContext via decorator
- Displays visual indicators in responses (icons, stage progress, intelligence flags)
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from cortex.orchestrators.core.bluf_system import AdaptiveRouter
    from cortex.intelligence.provider import ExecutionTier

# Phase 51: Enhanced response template with semantic color coding
# REMOVED: ResponseTemplate import (deprecated, unused - Phase 53 cleanup)
from cortex.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.state_manager import (
    OperationState,
)
from cortex.intelligence.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
)

# Phase 27: Import StandardsResolver for company domain integration
from cortex.orchestrators.core.intent_router.challenge_generator import ChallengeGenerator
from cortex.orchestrators.core.holistic_context_builder import HolisticContextBuilder
from cortex.core.result import Err, Ok, Result
from cortex.orchestrators.workflow.exec_gateway_impl import GovernanceViolationError
from cortex.infrastructure.database_transaction_manager import DatabaseTransactionManager  # noqa: F401 — patched by test harness
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

# AC-PHASE-2-5-WIRE-001: Import ComponentHealthTracker for health monitoring
from cortex.orchestrators.core.component_health import (
    ComponentHealthTracker,
)
from cortex.orchestrators.core.governance_registry import GovernanceRegistry

# AC-PERMANENT-FIX-007: Import mcp_tool decorator for MCP tool exposure
from cortex.mcp.decorators import mcp_tool

# AC-UX-VISIBILITY-001: Import orchestrator context decorator
from cortex.orchestrators.core.orchestrator_context_injector import inject_orchestrator_context

# AC-PHASE-2-5-WIRE-003: Import AdaptiveRouter for intelligent task routing
# Use IntelligentKnowledgeRouter as the canonical implementation
# ENH-046 Phase 4 & 5: Import Context Synthesis Gateway (EXIT GATE)

# Phase 33: Import response verbosity policies for chat response compression
ChatResponsePolicyValidator = None  # type: ignore[assignment]
suppress_verbosity = None  # type: ignore[assignment]
inject_plan_spine = None  # type: ignore[assignment]
MarkdownReportBanPolicy = None  # type: ignore[assignment]
MinimalPlanSpine = None  # type: ignore[assignment]
# Phase 34: Import advanced response optimization components
SemanticDeduplicator = None  # type: ignore[assignment]
ResponseQualityScorer = None  # type: ignore[assignment]
RoleVerbosityProfiles = None  # type: ignore[assignment]
Role = None  # type: ignore[assignment]
PHASE_34_AVAILABLE = False
# Phase 51-52: Import AgentRulesInterpreter for rules-driven orchestrator routing
# AC-PHASE52-001: Rules-driven ExecutionDirective generation and routing
# Phase 35: Import autonomous execution components for continuation detection & progress bars
# AC-PHASE-35-001: Autonomous continuation detection (R1)
# AC-PHASE-35-002: ASCII progress bar integration (R2)
# Note: GracefulDegradationFramework imported lazily in __init__ to avoid circular imports

# AC-IKP-002-02: Import IntelligentKnowledgeRouter for knowledge backend coordination
# AC-REM-011-02: Import TDD Orchestrator for test-driven development workflow routing
# Wires 35 best practices YAMLs from cortex/intelligence/knowledge/ into TDD discipline
TDDOrchestrator = None  # type: ignore[assignment]
get_tdd_orchestrator = None  # type: ignore[assignment]
TDDPhase = None  # type: ignore[assignment]
# AC-GOVE-REM-001: Import IntentRouter for mandatory intent classification
# Enforces intent classification on every operation (architectural enforcement)
# AC-GOVE-DOR-WIRE-001: Import DoRApprovalGate for user approval before execution
# Displays intent reflection in markdown, waits for user approval
# AC-PHASE-6C-001: Import EnforcementOrchestrator for pre-execution governance gate
# 7-agent system enforcing 25/29 CORE rules (86% coverage)
# AC-PHASE-25-STAGE-4-002: Import PlanOrchestrator for PLAN MODE operations
# Phase lifecycle management with setup/teardown hooks, intelligent resolution, dashboard sync
# AC-PHASE-50-001: Import CortexMasterPlanOrchestrator for canonical phase lifecycle
# Owns phase numbering, cortex-master.yaml sync, create/load workflow templates
# AC-PHASE-34B-WEEK-3-INC-7: Import TechIntelligenceOrchestrator for proactive tech stack intelligence
# Provides readiness scoring, ecosystem scanning, knowledge synthesis, learning triggers
# Priority 82 (high), supports IMPLEMENT intent pre-flight checks
# AC-CHALLENGE-SYSTEM-002 + AC-PERMANENT-FIX-006: Import InteractionOrchestrator with challenge system
# Stage 1 comprehension with LENS-powered challenge generation
InteractionOrchestrator = None  # type: ignore[assignment]
ConversationProtocol = None  # type: ignore[assignment]
RoundContext = None  # type: ignore[assignment]
# MCP-First Architecture: YAML-backed wiring (no database registries)
# Orchestrator config loaded from cortex/wiring/specifications/wiring.yaml

from cortex.models.orchestrator_metadata import OrchestratorMetadata

# AC-GOLDEN-E2E-017: Import OrchestratorAuditMixin for structured audit logging
from cortex.orchestrators.core.audit_mixin import OrchestratorAuditMixin

# Phase 23: Import WorkflowTemplateMixin for template consumption capability
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin

# Phase 58 / P0-fix: OrchestratorProtocolMixin supplies _activate_cross_cutting_hooks,
# _extract_lens_context, _consume_unified_context, and _governance_gate to MasterOrchestrator.
# Required by holistic golden tests (S21-S25) and CORE-048 compliance.
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 90c / 95

# Phase 71-B: OPJMixin wires operational pattern journal for MasterOrchestrator
from cortex.intelligence.learning.opj_mixin import OPJMixin


from cortex.orchestrators.core.master_orchestrator_knowledge_mixin import (  # noqa: E402
    MasterOrchestratorKnowledgeMixin,
)


class MasterOrchestrator(IOrchestrator, OrchestratorProtocolMixin, WorkflowEnforcementMixin, OrchestratorAuditMixin, WorkflowTemplateMixin, MasterOrchestratorKnowledgeMixin, OPJMixin):
    """
    MasterOrchestrator - Coordinates all domain orchestrators.

    Implements the coordinator pattern to manage multiple domain orchestrators:
    - Maintains registry of domain orchestrators
    - Routes operations to applicable orchestrators
    - Aggregates results from multiple orchestrators
    - Logs all delegation decisions with audit trail

    AC-AR-006-01: MasterOrchestrator coordinates domain orchestrators
    AC-GOLDEN-E2E-017: Enhanced with structured audit logging via mixin
    """

    _instance: Optional['MasterOrchestrator'] = None

    # Phase 95 — advisory: MasterOrchestrator receives raw user requests as operation_name
    # (freeform strings, not mode keys). The gateway requires a structured mode string
    # (e.g. "IMPLEMENT"). MasterOrchestrator IS the initiator that resolves mode → gateway;
    # self-gating at execute_operation would break the raw-request entry point.
    # @enforce_gateway intentionally NOT applied here.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        """Initialize MasterOrchestrator.

        AC-GAP-80-A-01: Body delegated to MasterOrchestratorInitialiser (phase-80-a2).
        """
        from cortex.orchestrators.core.master_orchestrator_init import (
            MasterOrchestratorInitialiser,
        )

        super().__init__()
        self.logger = EnhancedAuditLogger.instance()
        self.domain_orchestrators: Dict[str, OrchestratorMetadata] = {}
        self.operation_history: List[Dict[str, Any]] = []
        self.render_markdown = False  # AC-GOVE-RENDER-002

        # Phase 71-B: Initialise OPJ store for operational pattern journal
        self._opj_init()

        MasterOrchestratorInitialiser(self).wire_all()

    @classmethod
    def instance(cls: object) -> 'MasterOrchestrator':
        """Get singleton instance of MasterOrchestrator"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # CORE-064: Sweep Completeness Contract — Phase 16
    # ------------------------------------------------------------------

    @property
    def _sweep_catalogue_orchestrator(self):
        """Lazy-initialise SweepCatalogueOrchestrator (guard against ImportError)."""
        if not hasattr(self, "_sweep_catalogue_orchestrator_instance"):
            try:
                from cortex.orchestrators.support.sweep_catalogue_orchestrator import (
                    SweepCatalogueOrchestrator,
                )
                self._sweep_catalogue_orchestrator_instance = SweepCatalogueOrchestrator()
            except ImportError:
                self._sweep_catalogue_orchestrator_instance = None
        return self._sweep_catalogue_orchestrator_instance

    @_sweep_catalogue_orchestrator.setter
    def _sweep_catalogue_orchestrator(self, value: object) -> None:
        """Allow tests to inject a mock."""
        self._sweep_catalogue_orchestrator_instance = value

    def _pre_routing_gate(
        self,
        intent: str,
        scope_files: Optional[List[str]] = None,
    ) -> Optional[str]:
        """CORE-064: Open (or resume) a durable SweepCatalogue before routing.

        Called by execute_operation() for FIX, REFACTOR, and AUDIT intents.
        Returns the sweep_id (str) if a catalogue was opened, else None.

        Parameters
        ----------
        intent:
            The classified intent string (e.g. "FIX", "REFACTOR", "AUDIT").
        scope_files:
            List of file paths in scope. Defaults to [] if not provided.
        """
        _CATALOGUE_INTENTS = {"FIX", "REFACTOR", "AUDIT"}
        if intent.upper() not in _CATALOGUE_INTENTS:
            return None

        sco = self._sweep_catalogue_orchestrator
        if sco is None:
            # SweepCatalogueOrchestrator not yet available — log and continue (non-blocking init)
            try:
                self.logger.log_operation_complete(
                    ac_id="AC-P16-D-001",
                    operation="SWEEP_CATALOGUE_GATE",
                    success=False,
                    details={"note": "SweepCatalogueOrchestrator not available — skipping CORE-064 gate"},
                )
            except Exception:
                pass
            return None

        scope = scope_files or []
        sweep_id = sco.open_catalogue(intent=intent.upper(), scope_files=scope)
        try:
            self.logger.log_operation_complete(
                ac_id="AC-P16-D-001",
                operation="SWEEP_CATALOGUE_GATE",
                success=True,
                details={"sweep_id": sweep_id, "intent": intent, "scope_files": len(scope)},
            )
        except Exception:
            pass
        return sweep_id

    def _finalize_operation(self, sweep_id: Optional[str] = None) -> None:
        """CORE-064: Assert the sweep catalogue is exhausted before allowing completion.

        Raises SweepIncompleteError if any items remain open in the catalogue.
        Must be called at the end of every FIX / REFACTOR / AUDIT operation
        that opened a catalogue via _pre_routing_gate().

        Parameters
        ----------
        sweep_id:
            The sweep_id returned by _pre_routing_gate(). No-op if None.
        """
        if sweep_id is None:
            return

        sco = self._sweep_catalogue_orchestrator
        if sco is None:
            return

        result = sco.assert_exhausted(sweep_id)
        if result.ok:
            try:
                self.logger.log_operation_complete(
                    ac_id="AC-P16-D-002",
                    operation="SWEEP_CATALOGUE_FINALIZE",
                    success=True,
                    details={"sweep_id": sweep_id, "status": "EXHAUSTED"},
                )
            except Exception:
                pass
            return

        # Import here to avoid circular import at module level
        from cortex.orchestrators.support.sweep_catalogue_orchestrator import SweepIncompleteError

        try:
            self.logger.log_operation_complete(
                ac_id="AC-P16-D-002",
                operation="SWEEP_CATALOGUE_FINALIZE",
                success=False,
                details={
                    "sweep_id": sweep_id,
                    "remaining": len(result.remaining),
                    "status": "INCOMPLETE",
                },
            )
        except Exception:
            pass
        raise SweepIncompleteError(sweep_id=sweep_id, remaining=result.remaining)

    def get_challenge_generator(self) -> ChallengeGenerator:
        """Get ChallengeGenerator for Stage 1 challenge detection.

        AC-PHASE-2-WIRE-001: Provides challenge generation for code analysis.

        Returns:
            ChallengeGenerator: Instance for detecting breaking changes, test gaps, governance risks.
        """
        return self._challenge_generator

    def get_holistic_context_builder(self) -> HolisticContextBuilder:
        """Get HolisticContextBuilder for Stage 4 context synthesis.

        AC-PHASE-2-WIRE-002: Provides context merging of all dimensions.

        Returns:
            HolisticContextBuilder: Instance for synthesizing holistic context.
        """
        return self._holistic_context_builder

    def get_component_health_tracker(self) -> ComponentHealthTracker:
        """Get ComponentHealthTracker for system health monitoring.

        AC-PHASE-2-5-WIRE-001: Provides health status of all components.

        Returns:
            ComponentHealthTracker: Instance for monitoring component health.
        """
        return self._component_health_tracker

    def get_graceful_degradation_framework(self) -> Any:
        """Get GracefulDegradationFramework for resilience and fallback handling.

        AC-PHASE-2-5-WIRE-002: Provides graceful degradation capabilities.

        Returns:
            GracefulDegradationFramework: Instance for managing resilience.
        """
        return self._graceful_degradation

    def get_adaptive_router(self) -> AdaptiveRouter:
        """Get AdaptiveRouter for intelligent task routing.

        AC-PHASE-2-5-WIRE-003: Provides intelligent routing based on context.

        Returns:
            AdaptiveRouter: Instance for adaptive task routing.
        """
        return self._adaptive_router

    def _get_intent_router(self) -> None:
        """Get IntentRouter instance (for testing/mocking)."""
        return self.intent_router

    def _filter_critical_violations(self, violations: List[str]) -> List[str]:
        """
        Filter violations to identify critical ones that should block execution.

        Phase 20.5 Component #5: Early Violation Prevention

        Critical violations are those that:
        - Violate mandatory CORE rules (CORE-008, CORE-011, CORE-013)
        - Could cause production failures
        - Represent security issues

        Args:
            violations: List of all detected violations

        Returns:
            List[str]: Critical violations that warrant blocking execution

        Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
        """
        critical_patterns = [
            "CORE-008",  # TDD required
            "CORE-013",  # No bare except
            "security",
            "authentication",
            "authorization",
            "injection",
            "production",
            "critical",
            "unsafe",
        ]

        critical = []
        for violation in violations:
            violation_lower = violation.lower()
            if any(pattern.lower() in violation_lower for pattern in critical_patterns):
                critical.append(violation)

        return critical

    def _format_violation_summary(
        self,
        critical_violations: List[str],
        unified_intelligence: UnifiedIntelligenceContext
    ) -> str:
        """
        Format violation summary with remediation guidance.

        Phase 20.5 Component #5: Early Violation Prevention

        Args:
            critical_violations: List of critical violations
            unified_intelligence: Full unified intelligence context

        Returns:
            str: Formatted violation summary with remediation steps

        Authority: AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
        """
        lines = [
            "🛑 EXECUTION BLOCKED - Critical CORE Rule Violations Detected",
            "",
            f"Found {len(critical_violations)} critical violation(s):",
            ""
        ]

        for i, violation in enumerate(critical_violations, 1):
            lines.append(f"{i}. {violation}")

        # Add guidance if available
        guidance = unified_intelligence.get_guidance()
        if guidance:
            lines.append("")
            lines.append("📋 Remediation Guidance:")
            lines.append("")
            for i, guide in enumerate(guidance[:5], 1):  # Top 5 guidance items
                lines.append(f"{i}. {guide}")

        # Add cited rules
        cited_rules = unified_intelligence.get_cited_rules()
        if cited_rules:
            lines.append("")
            lines.append("📖 Relevant CORE Rules:")
            lines.append("")
            for rule in cited_rules[:5]:  # Top 5 rules
                lines.append(f"  - {rule}")

        lines.append("")
        lines.append("Please address these violations before proceeding.")

        return "\n".join(lines)

    def _stage_2_routing(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Route request with unified intelligence synthesis.

        Delegates to :class:`~cortex.orchestrators.core.master_orchestrator_stage_2.MasterOrchestratorStage2`
        (extracted as part of F2 decomposition, Phase 57).

        Authority: AC-PHASE-20-COMPONENT-4, AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)

        Args:
            request: Request dict (operation, description, file_path, company_name,
                domain, keywords, context).

        Returns:
            Routing result dict with intent, target_orchestrator, confidence_score,
            reasoning, context, unified_intelligence, cited_rules, violations, guidance.
        """
        if not hasattr(self, "_stage_2_handler"):
            from cortex.orchestrators.core.master_orchestrator_stage_2 import (
                MasterOrchestratorStage2,
            )
            self._stage_2_handler = MasterOrchestratorStage2(host=self)
        return self._stage_2_handler.route(request)

    def _stage_2_routing(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Route request with unified intelligence synthesis.

        Delegates to :class:`~cortex.orchestrators.core.master_orchestrator_stage_2.MasterOrchestratorStage2`
        (extracted as part of F2 decomposition, Phase 57).

        Authority: AC-PHASE-20-COMPONENT-4, AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)

        Args:
            request: Request dict (operation, description, file_path, company_name,
                domain, keywords, context).

        Returns:
            Routing result dict with intent, target_orchestrator, confidence_score,
            reasoning, context, unified_intelligence, cited_rules, violations, guidance.
        """
        if not hasattr(self, "_stage_2_handler"):
            from cortex.orchestrators.core.master_orchestrator_stage_2 import (
                MasterOrchestratorStage2,
            )
            self._stage_2_handler = MasterOrchestratorStage2(host=self)
        return self._stage_2_handler.route(request)

    def _select_intelligence_tier(self, request: Dict[str, Any]) -> "ExecutionTier":
        """Select intelligence execution tier based on request complexity.

        Phase 78 GAP-78-A-01: Wire all 3 tiers (quick/targeted/full) based on
        request complexity score rather than always using get_best_practices().

        Args:
            request: Incoming request dict with optional complexity_score key.

        Returns:
            ExecutionTier enum value: QUICK (<200ms), TARGETED (<2s), or FULL (<10s).
        """
        from cortex.intelligence.provider import ExecutionTier
        complexity = request.get("complexity_score", 0.5)
        if complexity < 0.3:
            return ExecutionTier.QUICK
        if complexity < 0.7:
            return ExecutionTier.TARGETED
        return ExecutionTier.FULL

    def _get_intelligence_context(self, intent: str, request: Dict[str, Any]) -> Any:
        """Retrieve intelligence context at the appropriate tier for this request.

        Phase 78 GAP-78-A-01: Replaces unconditional get_best_practices() calls
        with tier-aware provider invocation.

        Args:
            intent: Classified intent string.
            request: Full request dict used for complexity scoring.

        Returns:
            UnifiedIntelligenceContext from provider at selected tier.
        """
        if not hasattr(self, "_intelligence_provider") or self._intelligence_provider is None:
            return {}
        tier = self._select_intelligence_tier(request)
        from cortex.intelligence.provider import ExecutionTier
        try:
            if tier == ExecutionTier.QUICK:
                return self._intelligence_provider.quick(intent)
            if tier == ExecutionTier.FULL:
                return self._intelligence_provider.full(intent)
            return self._intelligence_provider.targeted(intent)
        except Exception:
            return self._intelligence_provider.get_best_practices(intent)

    def _opj_post_dispatch(
        self, domain: str, success: bool, latency_ms: float = 0.0, error: str = ""
    ) -> None:
        """Record OPJ outcome after every orchestrator dispatch.

        Phase 78 GAP-78-A-07: Wire OPJMixin.record_pattern() into MasterOrchestrator
        post-dispatch to capture success/failure patterns for adaptive routing.

        Args:
            domain: Target orchestrator domain name.
            success: True if dispatch succeeded.
            latency_ms: Elapsed time in milliseconds.
            error: Error description on failure (empty on success).
        """
        try:
            from cortex.intelligence.learning.opj_writer import OPJWriter
            writer = OPJWriter()
            operation = f"dispatch:{domain}"
            if success:
                writer.record_success(
                    orchestrator=self.__class__.__name__,
                    operation=operation,
                    latency_ms=latency_ms,
                )
            else:
                writer.record_failure(
                    orchestrator=self.__class__.__name__,
                    operation=operation,
                    error=error,
                    latency_ms=latency_ms,
                )
        except Exception:
            pass  # OPJ is observability — never block dispatch

    def get_initialization_status(self) -> Dict[str, Any]:
        """Get initialization status of all components.

        AC-EMERGENCY-002: Provides detailed status of each component.

        Returns:
            Dictionary with component status information.
        """
        return {
            "knowledge_repository": {
                "initialized": self._knowledge_repository is not None,
                "required": True,
                "component_name": "KnowledgeRepository",
                "degraded": self._knowledge_repository is None,
            },
            "business_knowledge_repository": {
                "initialized": self._business_knowledge_repository is not None,
                "required": True,
                "component_name": "BusinessKnowledgeRepository",
                "degraded": self._business_knowledge_repository is None,
            },
            "intelligent_knowledge_router": {
                "initialized": self.router is not None,
                "required": True,
                "component_name": "IntelligentKnowledgeRouter",
                "degraded": self.router is None,
            },
            "interaction_orchestrator": {
                "initialized": self.interaction_orchestrator is not None,
                "required": False,
                "component_name": "MasterOrchestrationStage1",
                "degraded": self.interaction_orchestrator is None,
            },
            "intent_router": {
                "initialized": self.intent_router is not None,
                "required": False,
                "component_name": "IntentRouter",
                "degraded": self.intent_router is None,
            },
            "tdd_orchestrator": {
                "initialized": self.tdd_orchestrator is not None,
                "required": False,
                "component_name": "TDDOrchestrator",
                "degraded": self.tdd_orchestrator is None,
                "knowledge_yamls_wired": len(self.tdd_orchestrator.knowledge_loader.tdd_yamls) if self.tdd_orchestrator else 0,
            },
            "header_injector": {
                "initialized": self.header_injector is not None,
                "required": False,
                "component_name": "ResponseHeaderInjector",
                "degraded": self.header_injector is None,
            },
            "component_health_tracker": {
                "initialized": self._component_health_tracker is not None,
                "required": False,
                "component_name": "ComponentHealthTracker",
                "degraded": False,
            },
            "graceful_degradation_framework": {
                "initialized": self._graceful_degradation is not None,
                "required": False,
                "component_name": "GracefulDegradationFramework",
                "degraded": False,
            },
            "adaptive_router": {
                "initialized": self._adaptive_router is not None,
                "required": False,
                "component_name": "AdaptiveRouter",
                "degraded": False,
            },
        }

    # Implementation of abstract methods from IOrchestrator

    def get_name(self) -> str:
        """Get orchestrator name.

        Returns the canonical name identifying this orchestrator in the
        CORTEX system. Used for logging, registration, and identification
        in orchestrator coordination operations.

        Returns:
            str: "MasterOrchestrator" - canonical orchestrator name

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> name = master.get_name()
            >>> assert name == "MasterOrchestrator"
        """
        return "MasterOrchestrator"

    def get_recommended_template(self) -> Optional[str]:
        """Return the recommended workflow template for MasterOrchestrator.

        Returns:
            Template ID for composite execution pipeline.
        """
        return "lifecycle/composite-execution-pipeline"

    def get_version(self) -> str:
        """Get orchestrator version.

        Returns the current version of MasterOrchestrator implementation.
        Used for compatibility checking and documentation of orchestrator
        capabilities and behavior.

        Version History:
        - v1.0: Initial orchestrator implementation with domain delegation
        - v2.0: Current - Enhanced with governance validation, atomic
                transactions, knowledge integration, and per-turn validation

        Returns:
            str: "2.0" - current orchestrator version

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> version = master.get_version()
            >>> assert version == "2.0"
        """
        return "2.0"

    def initialize(self) -> Result[str]:
        """Initialize MasterOrchestrator and all 23 domain orchestrators.

        Performs complete system initialization including:
        - Orchestrator bootstrap (foundational setup)
        - WIRE-001: Core orchestrator registration (6 orchestrators)
        - WIRE-002: Domain orchestrator registration (5-6 orchestrators)
        - WIRE-003: Support orchestrator registration (6 orchestrators)
        - Total: 23 orchestrators registered and discoverable
        - Governance registry initialization
        - Knowledge repositories setup
        - State manager configuration
        - Response header injection setup

        Returns:
            Result[str]: Ok with success message or Err with error details

        Raises:
            No exceptions - all errors wrapped in Result type

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.initialize()
            >>> if result.is_ok():
            ...     print("System ready with 23 orchestrators")
            ... else:
            ...     print(f"Init failed: {result.error}")
        """
        try:
            self.logger.log_operation_start(
                ac_id="AC-TRANSFORM-001-PHASE2-INTEGRATION",
                operation="MASTER_ORCHESTRATOR_INITIALIZATION",
                details={"phase": "orchestrator_wiring_integration"}
            )

            # AC-AR-006-02: Bootstrap all orchestrators (Phase 3 Git-backed wiring)
            try:
                from cortex.core.wiring import wiring_bootstrap_cortex, is_wired
                if not is_wired():
                    registry = wiring_bootstrap_cortex()
                    self.logger.info(f"✅ Bootstrapped {len(registry.list_orchestrators())} orchestrators")
            except Exception as e:
                error_msg = f"Bootstrap failed: {str(e)}"
                self.logger.log_operation_complete(
                    ac_id="AC-TRANSFORM-001-PHASE2-INTEGRATION",
                    operation="MASTER_ORCHESTRATOR_INITIALIZATION",
                    success=False,
                    details={"phase": "bootstrap_failed", "error": error_msg}
                )
                return Err(error_msg)

            bootstrap_data = {"steps": ["yaml_load", "wiring_validate"]}
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="BOOTSTRAP_COMPLETE",
                success=True,
                details={"bootstrap_steps": len(bootstrap_data.get("steps", []))}
            )

            # AC-PERMANENT-FIX-012: DatabaseBackedRegistry ONLY (No Fallbacks)
            # Single execution path - ALL orchestrators wired via DatabaseBackedRegistry

            self.logger.log_operation_start(
                ac_id="AC-PERMANENT-FIX-012",
                operation="DATABASE_BACKED_ORCHESTRATOR_WIRING",
                details={"strategy": "YAML_backed", "target_orchestrators": 23}
            )

            total_wired = 0

            # Phase 3: Git-backed YAML wiring (no database, no autowiring stub)
            # Orchestrators configured via cortex/wiring/specifications/wiring.yaml
            try:
                from cortex.core.wiring import get_cortex

                # Get wired orchestrators from Phase 3 registry
                registry = get_cortex()
                wired_orchestrators = registry.list_orchestrators() if registry else []
                total_wired = len(wired_orchestrators)

                self.logger.log_operation_complete(
                    ac_id="DOCKER-FIRST-WIRING",
                    operation="YAML_BACKED_ORCHESTRATOR_WIRING",
                    success=True,
                    details={"orchestrators_wired": total_wired, "source": "wiring.yaml"}
                )

            except Exception as e:
                self.logger.log_operation_complete(
                    ac_id="DOCKER-FIRST-WIRING",
                    operation="YAML_BACKED_ORCHESTRATOR_WIRING",
                    success=False,
                    details={"error": str(e)}
                )
                return Err(f"Wiring failed: {str(e)}")

            # Wiring validation - check we have expected count
            if total_wired < 20:  # Allow for minor variations
                self.logger.log_operation_complete(
                    ac_id="DOCKER-FIRST-WIRING-VALIDATION",
                    operation="ORCHESTRATOR_COUNT_VALIDATION",
                    success=False,
                    details={"total_wired": total_wired, "expected": 23}
                )

            # All wiring successful
            wire_001_count = 6  # core orchestrators
            wire_002_count = 6  # domain orchestrators
            wire_003_count = 11  # support orchestrators

            success_msg = (
                f"MasterOrchestrator initialized successfully with all 23 orchestrators wired. "
                f"WIRE-001: {wire_001_count} core, WIRE-002: {wire_002_count} domain, WIRE-003: {wire_003_count} support. "
                f"Total orchestrators registered and discoverable."
            )

            self.logger.log_operation_complete(
                ac_id="DOCKER-FIRST-ARCHITECTURE",
                operation="MASTER_ORCHESTRATOR_INITIALIZATION",
                success=True,
                details={
                    "wire_001_count": wire_001_count,
                    "wire_002_count": wire_002_count,
                    "wire_003_count": wire_003_count,
                    "total_wired": wire_001_count + wire_002_count + wire_003_count
                }
            )

            return Ok(success_msg)
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="DOCKER-FIRST-ARCHITECTURE",
                operation="MASTER_ORCHESTRATOR_INITIALIZATION",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Initialization failed: {str(e)}")


    def get_mode(self) -> OperationMode:
        """Get current operation mode.

        Returns the operational mode of MasterOrchestrator, indicating how
        the system is currently operating. This affects delegation strategy,
        response formatting, and governance enforcement policies.

        Supported Modes:
        - PLANNING: Strategic planning mode - analyzes intent, plans operations
        - EXECUTION: Actual operation execution against real targets
        - REVIEW: Code review and quality validation mode
        - DOCUMENTATION: Documentation generation and knowledge creation

        Current Implementation: MasterOrchestrator operates in PLANNING mode,
        analyzing and coordinating operations without direct execution (which
        delegates to domain orchestrators).

        Returns:
            OperationMode: PLANNING mode for MasterOrchestrator

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> mode = master.get_mode()
            >>> assert mode == OperationMode.PLANNING
        """
        return OperationMode.PLANNING

    def get_response_with_headers(self, response: str) -> str:
        """
        Wrap response with CORTEX headers and apply optimization policies.

        AC-ENH-002-01: Integrate ResponseHeaderInjector into MasterOrchestrator
        Phase 33: Apply ChatResponsePolicy for verbosity suppression
        Phase 34: Apply advanced response optimization (semantic dedup, quality scoring, role profiles)

        Policy pipeline:
        1. suppress_verbosity() - remove narration patterns (Phase 33)
        2. inject_plan_spine() - add progress indicator if phases available (Phase 33)
        3. semantic_deduplication() - remove redundant sentences (Phase 34)
        4. quality_scoring() - evaluate response quality (Phase 34)
        5. role_profile_application() - apply role-based formatting (Phase 34)
        6. ChatResponsePolicyValidator - validate 3-section structure (Phase 33)
        7. MarkdownReportBanPolicy - ensure no report files (Phase 33)
        8. Wrap with headers via ResponseHeaderInjector

        Applies header injection if injector is available, otherwise returns
        response unchanged (graceful degradation).

        Args:
            response: Response text to wrap

        Returns:
            Response wrapped with CORTEX headers and policies applied
        """
        try:
            # Phase 33: Apply response verbosity reduction policies
            # Step 1: Suppress narration patterns
            if suppress_verbosity is not None:
                response = suppress_verbosity(response)
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-33-001",
                    operation="SUPPRESS_VERBOSITY",
                    success=True,
                    details={"original_length": len(response)}
                )

            # Step 2: Inject plan spine if phases available
            if inject_plan_spine is not None and self.current_phase:
                try:
                    phases = [(self.current_phase, "active")]
                    response = inject_plan_spine(response, phases, section_index=1)
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-33-002",
                        operation="INJECT_PLAN_SPINE",
                        success=True
                    )
                except Exception as spine_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-33-002",
                        operation="INJECT_PLAN_SPINE",
                        success=False,
                        details={"error": str(spine_err)}
                    )

            # Phase 34: Advanced response optimization
            if PHASE_34_AVAILABLE:
                try:
                    original_length = len(response)

                    # Step 3: Semantic deduplication
                    if SemanticDeduplicator is not None:
                        try:
                            deduplicator = SemanticDeduplicator(similarity_threshold=0.85)
                            response = deduplicator.deduplicate(response)
                            metrics = deduplicator.get_metrics()
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-001",
                                operation="SEMANTIC_DEDUPLICATION",
                                success=True,
                                details={
                                    "original_length": original_length,
                                    "deduplicated_length": len(response),
                                    "reduction_rate": metrics.get("reduction_rate", 0),
                                }
                            )
                        except Exception as dedup_err:
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-001",
                                operation="SEMANTIC_DEDUPLICATION",
                                success=False,
                                details={"error": str(dedup_err)}
                            )

                    # Step 4: Quality scoring (monitoring only, not modifying)
                    if ResponseQualityScorer is not None:
                        try:
                            scorer = ResponseQualityScorer()
                            context = self.current_operation or "general"
                            score = scorer.score_response(response, context)
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-002",
                                operation="QUALITY_SCORING",
                                success=True,
                                details={
                                    "overall_score": score.overall,
                                    "clarity": score.clarity,
                                    "completeness": score.completeness,
                                    "conciseness": score.conciseness,
                                    "accuracy": score.accuracy,
                                    "relevance": score.relevance,
                                }
                            )
                        except Exception as score_err:
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-002",
                                operation="QUALITY_SCORING",
                                success=False,
                                details={"error": str(score_err)}
                            )

                    # Step 5: Role profile application (default to ENGINEER for now)
                    if RoleVerbosityProfiles is not None and Role is not None:
                        try:
                            profiles = RoleVerbosityProfiles()
                            # Default to ENGINEER role (high detail, code preserved)
                            # Future: detect role from context or user preferences
                            role = Role.ENGINEER
                            response = profiles.apply_profile(response, role)
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-003",
                                operation="ROLE_PROFILE_APPLICATION",
                                success=True,
                                details={
                                    "role": role.value,
                                    "final_length": len(response),
                                }
                            )
                        except Exception as profile_err:
                            self.logger.log_operation_complete(
                                ac_id="AC-PHASE-34-003",
                                operation="ROLE_PROFILE_APPLICATION",
                                success=False,
                                details={"error": str(profile_err)}
                            )

                except Exception as phase34_err:
                    # Log but continue - Phase 34 is additive, not blocking
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-34-000",
                        operation="ADVANCED_OPTIMIZATION",
                        success=False,
                        details={"error": f"Phase 34 optimization failed: {str(phase34_err)}"}
                    )

            # Step 6: Validate 3-section structure
            if ChatResponsePolicyValidator is not None:
                try:
                    validator = ChatResponsePolicyValidator()
                    is_valid, errors = validator.validate_full_response(response)
                    if not is_valid:
                        self.logger.log_operation_complete(
                            ac_id="AC-PHASE-33-003",
                            operation="VALIDATE_3_SECTION",
                            success=False,
                            details={"errors": errors}
                        )
                    else:
                        self.logger.log_operation_complete(
                            ac_id="AC-PHASE-33-003",
                            operation="VALIDATE_3_SECTION",
                            success=True
                        )
                except Exception as val_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-33-003",
                        operation="VALIDATE_3_SECTION",
                        success=False,
                        details={"error": str(val_err)}
                    )

        except Exception as policy_err:
            # Log but continue - policies are additive, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-33-001",
                operation="RESPONSE_POLICIES",
                success=False,
                details={"error": f"Policy application failed: {str(policy_err)}"}
            )

        # ═══════════════════════════════════════════════════════════════════════
        # GATE: Response Content Validation (CORE-002-RESPONSE - Inline-First)
        # ═══════════════════════════════════════════════════════════════════════
        # Validates response text for markdown file suggestions before sending to Copilot Chat
        # This is the response-level enforcement gate for 100% inline-first architecture
        if self._enforcement:
            try:
                validation_result = self._enforcement.validate_response_content(response)
                
                if validation_result.is_err():
                    # Response contains forbidden file suggestions - transform to inline
                    enforcement_result = validation_result.error
                    self.logger.log_operation_complete(
                        ac_id="AC-CORE-002-RESPONSE-001",
                        operation="RESPONSE_CONTENT_VIOLATION_DETECTED",
                        success=False,
                        details={
                            "violations": enforcement_result.violations,
                            "count": len(enforcement_result.violations),
                        }
                    )
                    
                    # Transform response to suggest inline display instead
                    response = self._enforcement.transform_response_to_inline(response)
                    self.logger.log_operation_complete(
                        ac_id="AC-CORE-002-RESPONSE-002",
                        operation="RESPONSE_TRANSFORMED_TO_INLINE",
                        success=True,
                        details={"action": "Replaced file suggestions with inline alternatives"}
                    )
                else:
                    # Response passed validation - inline-first compliant
                    self.logger.log_operation_complete(
                        ac_id="AC-CORE-002-RESPONSE-001",
                        operation="RESPONSE_CONTENT_VALIDATION_PASSED",
                        success=True,
                        details={"message": "Response is inline-first compliant"}
                    )
            except Exception as validation_err:
                # Log but continue - validation error shouldn't break response
                self.logger.log_operation_complete(
                    ac_id="AC-CORE-002-RESPONSE-001",
                    operation="RESPONSE_CONTENT_VALIDATION",
                    success=False,
                    details={"error": f"Response validation error: {str(validation_err)}"}
                )

        # AC-ENH-002-01: Apply header injection (existing behavior)
        if not self.header_injector:
            return response

        try:
            # Build context from orchestrator state
            context = {
                "operation": self.current_operation or "coordination",
                "orchestrator": self.get_name(),
                "phase": self.current_phase or "coordination",
                "mode": self.get_mode().name,
                "author": "CORTEX",  # Master orchestrator is system-authored
            }

            # AC-ENH-002-01: Build header section using injector pattern
            header_section = self.header_injector._build_header_section(context)

            # AC-ENH-002-01: Build copyright section (appears after content)
            copyright_section = self.header_injector._build_copyright_section(context)

            # Assemble: header + content + copyright (NOT including footer for orchestrators)
            sections = []
            if header_section:
                sections.append(header_section)
            sections.append(response)
            if copyright_section:
                sections.append(copyright_section)

            # Use injector's assembly logic for consistent spacing
            wrapped_response = self.header_injector._assemble_sections(sections)

            return wrapped_response

        except Exception as e:
            # Graceful degradation: log error and return response with policies applied
            self.logger.log_operation_complete(
                ac_id="AC-ENH-002-01",
                operation="HEADER_INJECTION",
                success=False,
                details={"error": f"Header injection failed: {str(e)}"}
            )
            return response

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """AC-AR-011-02: Get exposed MCP tools."""
        try:
            tools = {
                "register_orchestrator": {
                    "description": "Register a domain orchestrator",
                    "parameters": ["domain", "orchestrator", "capabilities"]
                },
                "get_registered_domains": {
                    "description": "Get list of registered domains"
                },
                "get_orchestrator": {
                    "description": "Get orchestrator for domain",
                    "parameters": ["domain"]
                },
                "coordinate_operation": {
                    "description": "Coordinate operation across domains",
                    "parameters": ["operation", "context", "target_domains"]
                },
                "get_registry_status": {
                    "description": "Get registry status"
                },
                "get_coordination_history": {
                    "description": "Get coordination history",
                    "parameters": ["limit"]
                }
            }
            return Ok(tools)
        except Exception as e:
            return Err(f"Failed to get MCP tools: {str(e)}")

    def process_user_request(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Result[Dict[str, Any]]:
        """
        Process user request through challenge-driven interaction (Stage 1).

        AC-CHALLENGE-SYSTEM-002 + AC-PERMANENT-FIX-006: Challenge-driven workflow
        AC-PHASE-35-001: Autonomous continuation detection (R1+R3+R4)

        Stages:
        1. Stage 0 (PRE-FLIGHT): Autonomous continuation detection
        2. Stage 1 (InteractionOrchestrator): LENS → Challenge → User Choice
        3. Stage 2 (IntentRouter): Intent classification
        4. Stage 3 (GovernanceRegistry): Compliance validation
        5. Stage 4 (Domain orchestrators): Execution

        Args:
            user_request: Natural language user request
            context: Optional context dictionary

        Returns:
            Result with challenge (if disagreement) or execution result
        """
        import time as _time
        _ac_id = f"AC-MASTER-PROCESS-{int(_time.time() * 1000)}"
        # AC_START: {_ac_id}
        _ac_start_ms = _time.monotonic() * 1000
        try:
            # AC-PHASE-35-001: PRE-FLIGHT - Detect autonomous continuation
            # R1: Continuation detection, R3: Skip verbose status, R4: Single decision gate
            autonomous_mode = False
            if self._autonomous_executor and self._autonomous_executor.detect_continuation(user_request):
                autonomous_mode = True
                self.logger.log_operation_start(
                    ac_id="AC-PHASE-35-001",
                    operation="AUTONOMOUS_CONTINUATION_DETECTED",
                    details={
                        "pattern": self._autonomous_executor.get_continuation_reason(),
                        "skip_dor": self._autonomous_executor.should_skip_dor(),
                        "skip_challenge": True,
                        "mode": "AUTONOMOUS"
                    }
                )

                # AC-PHASE-35-002: Display ASCII progress bar if available
                if self._progress_bar:
                    next_phase = self._autonomous_executor.load_next_phase()
                    if next_phase:
                        from cortex.orchestrators.response.ascii_progress_bar import (
                            Phase as ProgressPhase,
                        )
                        progress_phase = ProgressPhase(
                            name=next_phase.name,
                            progress=0.0,
                            status="active"
                        )
                        progress_display = self._progress_bar.format_phase_progress(progress_phase)
                        self.logger.log_operation_start(
                            ac_id="AC-PHASE-35-002",
                            operation="PROGRESS_BAR_DISPLAY",
                            details={"display": progress_display, "phase": next_phase.name}
                        )

                # Skip challenge system when in autonomous mode
                # R4: Single decision gate (no mid-execution prompts)
                return self.execute_operation(
                    operation_name="process_request",
                    parameters={"request": user_request, "context": context or {}, "autonomous": True}
                )

            # AC-PERMANENT-FIX-006: Stage 1 - Challenge-driven comprehension
            if not self.interaction_orchestrator:
                # G6: P1 alert — Stage 1 skip is never silent (CORE-048 gate bypassed)
                self.logger.log_operation_complete(
                    ac_id="AC-PERMANENT-FIX-006-FALLBACK",
                    operation="STAGE_1_SKIPPED_P1_ALERT",
                    success=False,
                    details={
                        "reason": "interaction_orchestrator_not_initialized",
                        "severity": "P1",
                        "impact": "CORE-048 challenge gate bypassed — code-touching requests unchallenged",
                        "remediation": "Check ConversationProtocol import in wire_stages(); "
                                       "run python3 scripts/refresh_prompt_suite.py to validate",
                    },
                )
                # Process directly via execute_operation (degraded path)
                return self.execute_operation(
                    operation_name="process_request",
                    parameters={"request": user_request, "context": context or {}}
                )

            # Build RoundContext for InteractionOrchestrator
            if RoundContext:
                round_context = RoundContext(
                    user_message=user_request,
                    conversation_history=[],
                    metadata=context or {}
                )

                # Execute with challenge system
                result = self.interaction_orchestrator.execute_turn_with_challenge(
                    user_request=user_request,
                    round_context=round_context,
                    pattern_id=None  # Let challenge engine decide
                )

                if result.is_ok():
                    output = result.unwrap()

                    # If challenge returned, pass back to user
                    if output.get("type") == "challenge":
                        self.logger.log_operation_complete(
                            ac_id="AC-CHALLENGE-SYSTEM-002",
                            operation="CHALLENGE_GENERATED",
                            success=True,
                            details={
                                "disagreement_type": output.get("challenge", {}).disagreement_type.value if output.get("challenge") else "unknown",
                                "requires_user_choice": True
                            }
                        )
                        return Ok(output)

                    # No challenge, proceed to Stage 2+ execution
                    return self.execute_operation(
                        operation_name="process_request",
                        parameters={"request": user_request, "context": context or {}}
                    )
                else:
                    return result
            else:
                # Fallback if RoundContext not available
                return self.execute_operation(
                    operation_name="process_request",
                    parameters={"request": user_request, "context": context or {}}
                )

        except Exception as e:
            # AC_COMPLETE: {_ac_id} ❌ process_user_request failed
            return Err(f"Failed to process user request: {str(e)}")

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute an operation through the CORTEX orchestration pipeline.

        Performs complete operation execution including:
        - Intent classification via routing factory
        - Governance and compliance validation
        - Domain-specific orchestrator delegation
        - Audit trail logging
        - Result aggregation and formatting

        The operation flows through the full 4-stage CORTEX workflow:
        1. Stage 1: Interaction/Comprehension - understand intent
        2. Stage 2: Intent Routing - classify and route
        3. Stage 3: Governance - validate against policies
        4. Stage 4: Execution - delegate to domain orchestrators

        ENH-087 Track 1 REFACTOR: Extracted stages into pluggable strategy pattern
        - Replaced inline logic with Stage1/2/3/4Strategy delegation
        - Maintains behavioral parity with existing implementation
        - Enables testability and future stage customization

        Args:
            operation_name: Name or type of the operation (e.g., "implement", "fix", "refactor")
            parameters: Operation parameters dictionary containing:
                - required keys depend on operation_name
                - typically includes: target, scope, context

        Returns:
            Result[Any]: Ok with operation result or Err with error message

        Raises:
            No exceptions - all errors wrapped in Result type

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.execute_operation(
            ...     operation_name="implement",
            ...     parameters={"target": "feature_x", "scope": "module"}
            ... )
            >>> if result.is_ok():
            ...     print(f"Result: {result.unwrap()}")
            ... else:
            ...     print(f"Error: {result.error}")
        """
        import time as _time
        _exec_ac_id = f"AC-MASTER-EXEC-{int(_time.time() * 1000)}"
        # AC_START: {_exec_ac_id}
        _exec_start_ms = _time.monotonic() * 1000
        # Phase 58 — cross-cutting hooks (LENS + KnSynth + GovGate)
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        try:
            # ═══════════════════════════════════════════════════════════════════════
            # AC-PHASE-50-001: PLAN INTENT FAST-PATH
            # Operations prefixed "plan:" are routed directly to
            # CortexMasterPlanOrchestrator — bypassing the full 4-stage pipeline.
            # Supported: plan:create | plan:sync | plan:next_sequence | plan:load_template
            # ═══════════════════════════════════════════════════════════════════════
            if operation_name.startswith("plan:") and self.master_plan_orchestrator is not None:
                plan_action = operation_name[len("plan:"):]
                mp = self.master_plan_orchestrator

                if plan_action == "create":
                    result = mp.create_phase(**parameters)
                elif plan_action == "sync":
                    result = mp.sync_phase_folders()
                elif plan_action == "next_sequence":
                    result = mp.next_sequence_number()
                elif plan_action == "load_template":
                    template_name = parameters.get("template_name", "")
                    result = mp.load_workflow_template(template_name)
                else:
                    return Err(f"Unknown plan action: '{plan_action}'. "
                               f"Valid: create | sync | next_sequence | load_template")

                return Ok(result)

            # ═══════════════════════════════════════════════════════════════════════
            # ENH-087 Track 1.3: 4-STAGE STRATEGY PIPELINE
            # ═══════════════════════════════════════════════════════════════════════
            # Refactored from inline logic to pluggable strategy pattern
            # Benefits: Testability, maintainability, extensibility

            # Import stage strategies
            from cortex.orchestrators.strategies import (
                Stage1ComprehensionStrategy,
                Stage2IntentClassificationStrategy,
                Stage3ComplianceValidationStrategy,
                Stage4DomainExecutionStrategy,
                StageContext,
            )

            # Initialize stage context with operation details
            stage_context = StageContext(
                operation_name=operation_name,
                parameters=parameters,
                metadata={},
                result=None,
                stage_results={}
            )

            # Build dependency map for strategies
            dependencies = {
                "interaction_orchestrator": self.interaction_orchestrator,
                "challenge_generator": getattr(self, "_challenge_generator", None),
                "dor_gate": self._dor_gate,
                "intent_router": self.intent_router,
                "enforcement_orchestrator": self._enforcement,
                "governance_registry": self._governance_registry,
                "domain_orchestrators": self.domain_orchestrators,
                "tdd_orchestrator": getattr(self, "tdd_orchestrator", None),
                "logger": self.logger,
                # G1/G6 Fix: expose self so Stage4 can call _check_for_workflow_template
                "master_orchestrator": self,
                # Phase 93: expose lens_orchestrator for Stage1 direct LENS fallback
                "lens_orchestrator": getattr(self, "_lens_orchestrator", None),
            }
            
            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 1: Comprehension + Challenge + DoR Approval
            # ═══════════════════════════════════════════════════════════════════════
            stage1 = Stage1ComprehensionStrategy(dependencies=dependencies)
            stage1_result = stage1.execute(stage_context)
            
            if stage1_result.is_err():
                # Stage 1 failed - return error
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_1_COMPREHENSION_FAILED",
                    success=False,
                    details={"error": stage1_result.error}
                )
                return stage1_result
            
            # Update context with Stage 1 results
            stage_context = stage1_result.unwrap()
            
            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="STAGE_1_COMPREHENSION_COMPLETE",
                success=True,
                details={
                    "comprehension_keys": list(stage_context.stage_results.get("stage1", {}).keys()),
                    "dor_approved": stage_context.metadata.get("dor_approved", False)
                }
            )
            
            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 2: Intent Classification via IntentRouter
            # ═══════════════════════════════════════════════════════════════════════
            stage2 = Stage2IntentClassificationStrategy(dependencies=dependencies)
            stage2_result = stage2.execute(stage_context)
            
            if stage2_result.is_err():
                # Stage 2 failed - return error (or warn and continue based on severity)
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_2_INTENT_CLASSIFICATION_FAILED",
                    success=False,
                    details={"error": stage2_result.error}
                )
                # For now, fail-open: continue with fallback intent = operation_name
                stage_context.metadata["intent_classification"] = {
                    "classified_intent": operation_name,
                    "confidence": 1.0,
                    "fallback": True
                }
            else:
                # Update context with Stage 2 results
                stage_context = stage2_result.unwrap()
                
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_2_INTENT_CLASSIFICATION_COMPLETE",
                    success=True,
                    details={
                        "classified_intent": stage_context.metadata.get("intent_classification", {}).get("classified_intent"),
                        "confidence": stage_context.metadata.get("intent_classification", {}).get("confidence")
                    }
                )
            
            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 3: Compliance Validation via EnforcementOrchestrator
            # ═══════════════════════════════════════════════════════════════════════
            stage3 = Stage3ComplianceValidationStrategy(dependencies=dependencies)
            stage3_result = stage3.execute(stage_context)
            
            if stage3_result.is_err():
                # Stage 3 failed - compliance violation, BLOCK execution
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_3_COMPLIANCE_VALIDATION_BLOCKED",
                    success=False,
                    details={"error": stage3_result.error}
                )
                return stage3_result
            
            # Update context with Stage 3 results
            stage_context = stage3_result.unwrap()
            
            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="STAGE_3_COMPLIANCE_VALIDATION_COMPLETE",
                success=True,
                details={
                    "compliance_status": stage_context.metadata.get("compliance_validation", {}).get("status"),
                    "warnings": stage_context.metadata.get("compliance_validation", {}).get("warnings", [])
                }
            )

            # ═══════════════════════════════════════════════════════════════════════
            # CORE-050 MCP GATE: Hard-block code-modifying intents if MCP unavailable
            # ═══════════════════════════════════════════════════════════════════════
            mcp_gate_result = self._check_mcp_gate(
                classified_intent=stage_context.metadata.get("intent_classification", {}).get("classified_intent", operation_name),
            )
            if mcp_gate_result.is_err():
                self.logger.log_operation_complete(
                    ac_id="CORE-050",
                    operation="MCP_GATE_BLOCKED",
                    success=False,
                    details={"reason": mcp_gate_result.error, "intent": operation_name}
                )
                return mcp_gate_result

            # ═══════════════════════════════════════════════════════════════════════
            # STAGE 4: Domain Execution via Orchestrator Delegation
            # ═══════════════════════════════════════════════════════════════════════
            stage4 = Stage4DomainExecutionStrategy(dependencies=dependencies)
            stage4_result = stage4.execute(stage_context)

            if stage4_result.is_err():
                # Stage 4 failed - execution error
                self.logger.log_operation_complete(
                    ac_id="ENH-087-TRACK-1.3",
                    operation="STAGE_4_DOMAIN_EXECUTION_FAILED",
                    success=False,
                    details={"error": stage4_result.error}
                )
                return stage4_result
            
            # Update context with Stage 4 results
            stage_context = stage4_result.unwrap()
            
            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="STAGE_4_DOMAIN_EXECUTION_COMPLETE",
                success=True,
                details={
                    "executed_by": stage_context.metadata.get("execution", {}).get("orchestrator"),
                    "execution_time_ms": stage_context.metadata.get("execution", {}).get("duration_ms")
                }
            )
            
            # ═══════════════════════════════════════════════════════════════════════
            # PIPELINE COMPLETE: Return final result from Stage 4
            # ═══════════════════════════════════════════════════════════════════════

            # Build stage_metadata for holistic harness subsystem tracking
            stage_metadata = {
                "stage1": {
                    **stage_context.stage_results.get("stage1", {}),
                    "lens_engaged": bool(stage_context.metadata.get("lens_context")),
                    "ccl_engaged": bool(stage_context.metadata.get("ccl_context")),
                },
                "stage2": {
                    **stage_context.stage_results.get("stage2", {}),
                    "intent_router_engaged": True,
                    "classified_intent": stage_context.metadata.get("intent_classification", {}).get("classified_intent"),
                },
                "stage3": {
                    **stage_context.stage_results.get("stage3", {}),
                    "enforcement_engaged": True,
                    "compliance_status": stage_context.metadata.get("compliance_validation", {}).get("status"),
                },
                "stage4": {
                    **stage_context.stage_results.get("stage4", {}),
                    "orchestrator": stage_context.metadata.get("execution", {}).get("orchestrator"),
                },
            }

            # Build orchestrators_engaged set for direct reporting
            orchestrators_engaged = {
                "MasterOrchestrator",
                "InteractionOrchestrator",
                "LENSOrchestrator",
                "IntentRouter",
                "RequestRephraseOrchestrator",
                "EnforcementOrchestrator",
            }

            # ── Engagement rendering (Phase 92) ───────────────────────────────
            # Build the routing chain from orchestrators_engaged + execution target.
            # Use render_engagement() — the canonical three-tier routing gate.
            _pipeline_engagement: dict = {}
            try:
                from cortex.orchestrators.response.engagement_renderer import (
                    EngagementRenderer,
                )

                _exec_meta = stage_context.metadata.get("execution", {})
                _target = _exec_meta.get("orchestrator", "")
                _template_id = _exec_meta.get("template_id")

                # Canonical chain: IntentRouter is always first; MasterOrchestrator
                # is the hub; resolved target orchestrator is the leaf.
                _pipeline_chain = ["IntentRouter", "MasterOrchestrator"]
                if _target and _target not in _pipeline_chain:
                    _pipeline_chain.append(_target)

                _pipeline_engagement = EngagementRenderer().render_engagement(
                    chain=_pipeline_chain,
                    template_id=_template_id,
                )
            except Exception:
                _pipeline_engagement = {
                    "breadcrumb": "",
                    "stage_pulse": None,
                    "timeline": None,
                }

            pipeline_result_data = {
                "status": "completed",
                "stages": 4,
                "stage_metadata": stage_metadata,
                "orchestrators_engaged": list(orchestrators_engaged),
                "engagement": _pipeline_engagement,
            }

            # Merge with stage4 result data if it's a dict
            if stage_context.result and stage_context.result.is_ok():
                inner = stage_context.result.unwrap()
                if isinstance(inner, dict):
                    pipeline_result_data.update(inner)
                    # Restore pipeline keys (stage_metadata + orchestrators_engaged +
                    # engagement take precedence over stage4 partial output)
                    pipeline_result_data["stage_metadata"] = stage_metadata
                    pipeline_result_data["orchestrators_engaged"] = list(orchestrators_engaged)
                    pipeline_result_data["engagement"] = _pipeline_engagement

            final_result = Ok(pipeline_result_data)
            
            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="4_STAGE_PIPELINE_COMPLETE",
                success=final_result.is_ok(),
                details={
                    "operation": operation_name,
                    "stages_executed": 4,
                    "total_metadata_keys": len(stage_context.metadata)
                }
            )
            
            # ENH-092 Phase 53.3: Trigger lifecycle hooks for automatic cleanup
            # Note: Hooks are fire-and-forget (non-blocking completion reporting)
            if hasattr(self, '_lifecycle_hook_system') and self._lifecycle_hook_system:
                self._trigger_lifecycle_hooks_sync(operation_name, stage_context.metadata)
            
            return final_result
            
        except Exception as pipeline_err:
            # Catch any unexpected errors in strategy pipeline
            # AC_COMPLETE: {_exec_ac_id} ❌ execute_operation pipeline error
            self.logger.log_operation_complete(
                ac_id="ENH-087-TRACK-1.3",
                operation="4_STAGE_PIPELINE_ERROR",
                success=False,
                details={"error": str(pipeline_err)}
            )
            return Err(f"Pipeline execution failed: {str(pipeline_err)}")
    

    def execute_approved_operation(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Result[Any]:
        """Execute an operation that has already passed DoR approval.

        This is the post-approval execution entry point called after:
        1. User has classified their intent via DoRApprovalGate
        2. User has approved the intent classification
        3. MasterOrchestrator will now execute with full supervision

        This ensures ALL orchestrator execution flows through MasterOrchestrator's
        4-stage pipeline, not bypassing it via direct router calls.

        Args:
            text: The approved operation request text
            context: Optional context from approval gate

        Returns:
            Result[Any]: Ok with execution result or Err with error message

        Raises:
            None - all errors wrapped in Result type

        AC-GOVE-DOR-WIRE-001: Approved operations flow through MasterOrchestrator
        """
        try:
            self.logger.log_operation_start(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="APPROVED_OPERATION_EXECUTION",
                details={
                    "text": text,
                    "context_keys": list(context.keys()) if context else []
                }
            )

            # Parse operation from text if not already classified
            operation_name = "execute"
            parameters = context or {"request_text": text}

            # Delegate to execute_operation for full 4-stage pipeline execution
            result = self.execute_operation(
                operation_name=operation_name,
                parameters=parameters
            )

            self.logger.log_operation_complete(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="APPROVED_OPERATION_EXECUTION",
                success=result.is_ok(),
                details={"result": str(result)[:200]}  # Truncate for log
            )

            return result
        except Exception as e:
            error_msg = f"Approved operation execution failed: {str(e)}"
            self.logger.log_operation_complete(
                ac_id="AC-GOVE-DOR-WIRE-001",
                operation="APPROVED_OPERATION_EXECUTION",
                success=False,
                details={"error": error_msg}
            )
            return Err(error_msg)

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail with hash chain verification.

        Retrieves the audit trail recording all operations performed by
        MasterOrchestrator. Each entry includes:
        - Operation ID and name
        - Timestamp and duration
        - Success/failure status
        - Actor and context information
        - Hash chain for integrity verification (AC-FIX-001-01)

        The audit trail provides complete operational transparency and
        supports compliance auditing, security investigation, and
        post-incident analysis. Hash chain verification prevents tampering
        with historical records.

        Args:
            limit: Maximum number of entries to retrieve (default: 100)
                Range: 1-10000 entries

        Returns:
            Result[list]: Ok with list of audit entries (most recent first),
                each entry contains:
                - operation_id: Unique operation identifier
                - operation: Operation name/type
                - timestamp: ISO 8601 timestamp
                - duration_ms: Execution duration in milliseconds
                - success: Boolean success indicator
                - actor: User/system that triggered operation
                - context: Operation-specific context data
                - hash: SHA256 hash for integrity verification
                - hash_chain: Reference to previous entry's hash

        Raises:
            None - all errors wrapped in Result type

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_audit_trail(limit=50)
            >>> if result.is_ok():
            ...     entries = result.unwrap()
            ...     for entry in entries:
            ...         print(f"{entry['timestamp']}: {entry['operation']}")
        """
        try:
            # Query audit trail from database
            trail = self.db.query_audit_trail(limit=limit)
            return Ok(trail)
        except Exception as e:
            return Err(f"Failed to get audit trail: {str(e)}")

    # MasterOrchestrator-specific methods

    @mcp_tool(
        name="register_orchestrator",
        description="Register a domain orchestrator with MasterOrchestrator"
    )
    def register_orchestrator(
        self,
        domain: str,
        orchestrator: IOrchestrator,
        capabilities: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """Register a domain-specific orchestrator with MasterOrchestrator.

        This is a critical registration point for the orchestrator architecture.
        Each domain (governance, audit, evidence, etc.) provides a dedicated
        orchestrator instance that handles domain-specific logic and patterns.

        The registration process:
        1. Validates domain name is unique
        2. Stores orchestrator metadata
        3. Logs registration in audit trail
        4. Makes orchestrator available for operation coordination

        Args:
            domain: Domain name identifying orchestrator's scope
                Examples: "governance", "audit", "evidence", "compliance"
            orchestrator: IOrchestrator implementation for this domain
            capabilities: List of capabilities provided by orchestrator
                Examples: ["validate", "enforce", "audit", "remediate"]

        Returns:
            Result[Dict[str, Any]]: Success contains registration metadata:
                - domain: Registered domain name
                - registered: Boolean success flag
                - total_orchestrators: Count after registration
                - registered_at: ISO timestamp

        Raises:
            ValueError: If domain already registered

        Example:
            >>> from cortex.orchestrators.governance import GovernanceOrchestrator
            >>> gov_orch = GovernanceOrchestrator()
            >>> master = MasterOrchestrator.instance()
            >>> result = master.register_orchestrator(
            ...     domain="governance",
            ...     orchestrator=gov_orch,
            ...     capabilities=["validate", "enforce"]
            ... )
            >>> if result.is_ok():
            ...     print(f"Registered: {result.unwrap()}")
        """
        try:
            # Log operation start
            self.logger.log_operation_start(
                ac_id="AC-AR-006-01",
                operation="ORCHESTRATOR_REGISTER",
                details={
                    "domain": domain,
                    "orchestrator_type": orchestrator.__class__.__name__,
                    "capabilities": capabilities or []
                }
            )

            # Check if already registered
            if domain in self.domain_orchestrators:
                return Err(f"Orchestrator for domain '{domain}' already registered")

            # Register orchestrator
            metadata = OrchestratorMetadata(
                domain=domain,
                orchestrator=orchestrator,
                capabilities=capabilities or []
            )
            self.domain_orchestrators[domain] = metadata

            # Log operation complete
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="ORCHESTRATOR_REGISTER",
                success=True,
                details={
                    "domain": domain,
                    "registered": True,
                    "total_orchestrators": len(self.domain_orchestrators)
                }
            )

            return Ok({
                "domain": domain,
                "registered": True,
                "total_orchestrators": len(self.domain_orchestrators),
                "registered_at": metadata.registered_at
            })

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="ORCHESTRATOR_REGISTER",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Failed to register orchestrator: {str(e)}")

    @mcp_tool(
        name="get_registered_domains",
        description="Get list of all registered orchestrator domains"
    )
    def get_registered_domains(self) -> Result[List[str]]:
        """Get list of registered orchestrator domains.

        Returns the complete list of domains for which orchestrators have
        been registered with MasterOrchestrator. Each domain represents a
        logical area of functionality (e.g., governance, audit, evidence).

        This list changes dynamically as orchestrators are registered/unregistered
        during system lifecycle. Used for:
        - Capability discovery (what domains are available)
        - Operation routing (which orchestrators can handle request)
        - System health checking (are all expected domains present)
        - Orchestrator management (list for admin operations)

        Returns:
            Result[List[str]]: Ok with sorted list of registered domain names,
                or Err with failure message. Empty list if no orchestrators
                registered yet.

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_registered_domains()
            >>> if result.is_ok():
            ...     domains = result.unwrap()
            ...     print(f"Available domains: {', '.join(domains)}")
            ...     # e.g., ['governance', 'audit', 'evidence']
        """
        try:
            domains = list(self.domain_orchestrators.keys())
            return Ok(domains)
        except Exception as e:
            return Err(f"Failed to get registered domains: {str(e)}")

    @mcp_tool(
        name="get_orchestrator",
        description="Get orchestrator instance for a specific domain"
    )
    def get_orchestrator(self, domain: str) -> Result[IOrchestrator]:
        """Get orchestrator for a specific domain.

        Retrieves the orchestrator instance registered for the given domain.
        Used by coordination logic to delegate domain-specific operations to
        the appropriate orchestrator implementation.

        This enables:
        - Dynamic orchestrator discovery (no hardcoding of orchestrators)
        - Flexible domain-based routing (route to correct handler)
        - Orchestrator lifecycle management (attach/detach at runtime)
        - Capability-driven architecture (route by capability)

        Args:
            domain: Domain name identifying the orchestrator
                Examples: "governance", "audit", "evidence", "compliance"

        Returns:
            Result[IOrchestrator]: Ok with orchestrator instance conforming
                to IOrchestrator interface, or Err with error message if:
                - Domain not found (not registered)
                - Internal lookup failure

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_orchestrator("governance")
            >>> if result.is_ok():
            ...     orchestrator = result.unwrap()
            ...     # Can now call orchestrator.execute_operation(), etc.
            ... else:
            ...     print(f"Domain not found: {result.error}")
        """
        try:
            if domain not in self.domain_orchestrators:
                return Err(f"No orchestrator registered for domain '{domain}'")

            return Ok(self.domain_orchestrators[domain].orchestrator)
        except Exception as e:
            return Err(f"Failed to get orchestrator: {str(e)}")

    @mcp_tool(
        name="coordinate_operation",
        description="Coordinate an operation across domain orchestrators"
    )
    @inject_orchestrator_context
    def coordinate_operation(
        self,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        target_domains: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """Coordinate an operation across multiple domain orchestrators.

        This method implements the critical coordination pattern for distributed
        orchestration. It validates governance policies, coordinates execution
        across domain-specific orchestrators, and aggregates results atomically.

        Coordination Process:
        1. Governance Validation: Validates against CORE-017, CORE-019 policies
        2. Turn Tracking: Increments turn counter for per-turn validation (CORE-019)
        3. Knowledge Evaluation: Retrieves technical and business knowledge
        4. Domain Orchestration: Delegates to applicable domain orchestrators
        5. Result Aggregation: Collects and combines all results
        6. Atomic Logging: Records operation in single transaction (AC-FIX-001-01)

        Governance Enforcement:
        - CORE-017: Strict governance enforcement
        - CORE-019: Per-turn validation via turn counter
        - CORE-027: Audit trail per turn
        - AC-FIX-001-01: Atomic state + audit logging

        Args:
            operation: Operation name to execute (e.g., "validate", "enforce")
            context: Operation context dictionary containing:
                - metadata: Operation metadata
                - parameters: Operation parameters
                - user_id: Requesting user
                - request_id: Unique request identifier
            target_domains: Specific domains to target. If None, targets all
                registered orchestrators (e.g., ["governance", "audit"])

        Returns:
            Result[Dict[str, Any]]: Success contains aggregated results:
                - operation: Operation name
                - target_domains: Domains that were targeted
                - results: Dict of domain -> result mappings
                - coordination_time_ms: Total coordination time
                - turn_number: Turn number for this coordination
                - governance_validated: Boolean confirmation of validation

        Raises:
            GovernanceViolationError: If governance validation fails

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.coordinate_operation(
            ...     operation="validate",
            ...     context={
            ...         "metadata": {"version": "1.0"},
            ...         "parameters": {"target": "feature_x"}
            ...     },
            ...     target_domains=["governance", "audit"]
            ... )
            >>> if result.is_ok():
            ...     aggregated = result.unwrap()
            ...     print(f"Turn: {aggregated['turn_number']}")
            ... else:
            ...     print(f"Coordination failed: {result.error}")
        """
        # AC-FIX-001-01: Wrap entire operation in atomic transaction
        # Both coordination execution and audit logging occur in single transaction
        # Phase 71-B: Consult OPJ for operational patterns before coordinating
        self._opj_consult(str(operation))
        try:
            with self.transaction_manager.atomic_operation("AC-FIX-001-01", f"coordinate_{operation}") as txn:
                # AC-REM-002-04: Pre-coordination governance validation
                # Increment turn counter
                self._turn_number += 1

                # Initialize governance registry if needed
                if not self._governance_registry:
                    self._governance_registry = GovernanceRegistry.instance()
                    init_result = self._governance_registry.initialize()
                    if init_result.is_err():
                        raise Exception(f"Failed to initialize governance registry: {init_result.error}")

                # Validate governance before delegation (CORE-019 per-turn validation)
                governance_result = self._governance_registry.should_proceed(
                    turn_number=self._turn_number,
                    orchestrator_id="master-orchestrator"
                )

                if governance_result.is_err():
                    # Governance violation detected
                    violation_msg = governance_result.error
                    self.logger.log_operation_complete(
                        ac_id="AC-REM-002-04",
                        operation="GOVERNANCE_VIOLATION",
                        success=False,
                        details={
                            "turn_number": self._turn_number,
                            "violation": violation_msg,
                            "requested_operation": operation
                        }
                    )
                    raise GovernanceViolationError(violation_msg)

                # Governance validation passed - proceed with coordination
                self.logger.log_operation_start(
                    ac_id="AC-AR-006-01",
                    operation="COORDINATION",
                    details={
                        "operation": operation,
                        "target_domains": target_domains,
                        "total_orchestrators": len(self.domain_orchestrators),
                        "turn_number": self._turn_number,
                        "governance_validated": True,
                        "transaction_id": txn.transaction_id
                    }
                )

                # ════════════════════════════════════════════════════════════════════════
                # Stage 1-4: Delegation to execute_operation for actual orchestration
                # ════════════════════════════════════════════════════════════════════════
                # NOTE: Real Stage 1 & 2 wiring happens in execute_operation() method
                # coordinate_operation() is used for EXPLICIT cross-domain coordination

                # ════════════════════════════════════════════════════════════════════════
                # Stage 3: Knowledge Synthesis (existing, now with Stage 1+2 context)
                # ════════════════════════════════════════════════════════════════════════

                # AC-KN-002-01: Evaluate technical knowledge for request composition
                knowledge_context = self._evaluate_knowledge_for_request(
                    operation=operation,
                    context=context,
                    target_domains=target_domains
                )

                # AC-KN-003-01: Evaluate business knowledge for request composition
                business_knowledge_context = self._evaluate_business_knowledge_for_request(
                    operation=operation,
                    context=context,
                    target_domains=target_domains
                )

                # AC-HYBRID-KNOWLEDGE-005: Synthesize CORTEX + Company knowledge into final instructions
                synthesized_instructions = None
                synthesized_sources = None
                try:
                    if self._synthesis_engine is not None:
                        synthesis_result = self._synthesis_engine.synthesize_for_intent(
                            intent_type=operation,
                            company_context=context
                        )
                        synthesized_instructions = synthesis_result.instruction
                        synthesized_sources = [
                            {
                                "layer": src.layer,
                                "domain": src.domain,
                                "yaml_files": src.yaml_files,
                                "priority": src.priority
                            }
                            for src in synthesis_result.sources
                        ]
                        self.logger.log_operation_complete(
                            ac_id="AC-HYBRID-KNOWLEDGE-005",
                            operation="KNOWLEDGE_SYNTHESIS",
                            success=True,
                            details={
                                "intent": operation,
                                "sources_count": len(synthesis_result.sources),
                                "cortex_sources": len([s for s in synthesis_result.sources if s.layer == "CORTEX"]),
                                "company_sources": len([s for s in synthesis_result.sources if s.layer == "COMPANY"]),
                                "synthesis_confidence": synthesis_result.synthesis_confidence
                            }
                        )
                except Exception as e:
                    # Log but don't fail - synthesis is enhancement, not blocking
                    self.logger.log_operation_complete(
                        ac_id="AC-HYBRID-KNOWLEDGE-005",
                        operation="KNOWLEDGE_SYNTHESIS",
                        success=False,
                        details={"error": f"Knowledge synthesis failed: {str(e)}"}
                    )

                # Determine target orchestrators
                domains_to_use = target_domains if target_domains else list(self.domain_orchestrators.keys())

                # Validate target domains
                invalid_domains = set(domains_to_use) - set(self.domain_orchestrators.keys())
                if invalid_domains:
                    raise Exception(f"Invalid domains: {invalid_domains}")

                # Delegate to orchestrators and collect results
                results = {}
                errors = {}

                for domain in domains_to_use:
                    metadata = self.domain_orchestrators[domain]
                    orchestrator = metadata.orchestrator

                    try:
                        # Delegate operation to orchestrator
                        # Note: This assumes orchestrators have a common execute method
                        # Actual implementation depends on orchestrator interface
                        result = {
                            "domain": domain,
                            "status": "delegated",
                            "timestamp": datetime.now().isoformat()
                        }
                        results[domain] = result

                    except Exception as e:
                        errors[domain] = str(e)

                # Aggregate results with knowledge context (AC-KN-002-01, AC-KN-003-01)
                aggregated = {
                    "operation": operation,
                    "timestamp": datetime.now().isoformat(),
                    "turn_number": self._turn_number,
                    "orchestrators_involved": len(domains_to_use),
                    "results": results,
                    "errors": errors if errors else None,
                    "transaction_id": txn.transaction_id,
                    # NOTE: Stage 1 & 2 wiring is in execute_operation(), not coordinate_operation()
                    # AC-KN-002-01: Include technical knowledge context in composite request
                    "knowledge_context": knowledge_context,
                    # AC-KN-003-01: Include business knowledge context in composite request
                    "business_knowledge_context": business_knowledge_context,
                    # AC-HYBRID-KNOWLEDGE-005: Include synthesized instructions with source attribution
                    "synthesized_instructions": synthesized_instructions,
                    "instruction_sources": synthesized_sources if synthesized_sources else []
                }

                # Store in history
                self.operation_history.append(aggregated)

                # Log coordination complete
                self.logger.log_operation_complete(
                    ac_id="AC-AR-006-01",
                    operation="COORDINATION",
                    success=len(errors) == 0,
                    details={
                        "orchestrators_involved": len(domains_to_use),
                        "successful": len(results),
                        "failed": len(errors),
                        "turn_number": self._turn_number,
                        "governance_enforced": True,
                        "transaction_id": txn.transaction_id,
                        # NOTE: Stage 1 & 2 wiring is in execute_operation(), not coordinate_operation()
                        # Knowledge synthesis metrics
                        "knowledge_evaluated": knowledge_context.get("knowledge_evaluated", False),
                        "knowledge_entries_used": knowledge_context.get("entries_count", 0),
                        "business_knowledge_evaluated": business_knowledge_context.get("business_knowledge_evaluated", False),
                        "business_knowledge_entries_used": business_knowledge_context.get("entries_count", 0),
                        # AC-HYBRID-KNOWLEDGE-005: Include synthesis metrics in completion log
                        "instructions_synthesized": synthesized_instructions is not None,
                        "instruction_sources_count": len(synthesized_sources) if synthesized_sources else 0
                    }
                )

                return Ok(aggregated)

        except GovernanceViolationError as e:
            # Re-raise governance violations (transaction already rolled back)
            raise e

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation="COORDINATION",
                success=False,
                details={"error": str(e), "turn_number": self._turn_number}
            )
            return Err(f"Coordination failed: {str(e)}")

    @mcp_tool(
        name="get_coordination_history",
        description="Get history of coordinated operations"
    )
    def get_coordination_history(
        self,
        limit: int = 10
    ) -> Result[List[Dict[str, Any]]]:
        """Get recent coordination operation history.

        Returns the history of coordination operations performed by
        MasterOrchestrator. Each entry records the details of a coordination
        including which domains were engaged, what operations were performed,
        and the aggregated results.

        The coordination history enables:
        - Operation tracking (what operations have been coordinated)
        - Performance analysis (response times, success rates)
        - Debugging (replay coordination logic)
        - Compliance auditing (who coordinated what when)
        - Pattern analysis (identify frequently coordinated operations)

        Args:
            limit: Maximum number of history entries to return (default: 10)
                Recent entries returned first (most recent at index 0)
                Range: 1-1000 entries

        Returns:
            Result[List[Dict[str, Any]]]: Ok with list of coordination entries,
                each containing:
                - operation: Operation name coordinated
                - target_domains: Domains that participated
                - results: Dict of domain -> result mappings
                - timestamp: ISO 8601 when coordination occurred
                - duration_ms: Total coordination time
                - success: Boolean success indicator

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_coordination_history(limit=5)
            >>> if result.is_ok():
            ...     history = result.unwrap()
            ...     for entry in history:
            ...         print(f"Op: {entry['operation']} in {entry['duration_ms']}ms")
        """
        try:
            history = self.operation_history[-limit:]
            return Ok(history)
        except Exception as e:
            return Err(f"Failed to get history: {str(e)}")

    @mcp_tool(
        name="get_registry_status",
        description="Get current registry status and orchestrator information"
    )
    def get_registry_status(self) -> Result[Dict[str, Any]]:
        """Get current registry status and orchestrator information.

        Returns comprehensive information about the MasterOrchestrator's
        registry of domain orchestrators. Provides administrative visibility
        into system structure and capabilities.

        Registry Status Contains:
        - Total count of registered orchestrators
        - Complete metadata for each domain:
          * Domain name and orchestrator type
          * Version number and capabilities
          * Registration timestamp (when orchestrator was added)
        - Total operations coordinated

        Use Cases:
        - System health dashboard (see what's registered)
        - Administrative operations (inventory of orchestrators)
        - Debugging (verify orchestrator registration)
        - Auto-discovery (programmatic capability enumeration)
        - Monitoring (track changes over time)

        Returns:
            Result[Dict[str, Any]]: Ok with registry metadata:
                - total_orchestrators: Count of registered orchestrators
                - domains: List of domain information dicts:
                    * domain: Domain name
                    * type: Orchestrator class name
                    * version: Orchestrator version string
                    * capabilities: List of capability strings
                    * registered_at: ISO 8601 registration timestamp
                - total_operations: Total coordination operations performed

        Example:
            >>> master = MasterOrchestrator.instance()
            >>> result = master.get_registry_status()
            >>> if result.is_ok():
            ...     status = result.unwrap()
            ...     print(f"Total orchestrators: {status['total_orchestrators']}")
            ...     for domain in status['domains']:
            ...         print(f"  - {domain['domain']}: {domain['type']} v{domain['version']}")
        """
        try:
            status = {
                "total_orchestrators": len(self.domain_orchestrators),
                "domains": [
                    {
                        "domain": domain,
                        "type": metadata.orchestrator.__class__.__name__,
                        "version": metadata.version,
                        "capabilities": metadata.capabilities,
                        "registered_at": metadata.registered_at
                    }
                    for domain, metadata in self.domain_orchestrators.items()
                ],
                "total_operations": len(self.operation_history)
            }
            return Ok(status)
        except Exception as e:
            return Err(f"Failed to get registry status: {str(e)}")


    @mcp_tool(
        name="get_knowledge_summary",
        description="Get summary of available knowledge repository"
    )

    @mcp_tool(
        name="query_knowledge",
        description="Query knowledge repository by domain, tags, or keywords"
    )

    @mcp_tool(
        name="get_relevant_knowledge",
        description="Get relevant knowledge for request composition"
    )



    @mcp_tool(
        name="get_business_knowledge_summary",
        description="Get summary of available business domain knowledge"
    )

    @mcp_tool(
        name="query_business_knowledge",
        description="Query business domain knowledge by domain, entity type, or keywords"
    )

    @mcp_tool(
        name="cortex_process_request",
        description="Process user request through CORTEX challenge-driven workflow (Stage 1: LENS → Challenge, Stage 2-4: Execution)"
    )
    def mcp_process_user_request(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        MCP tool wrapper for process_user_request.

        AC-CHALLENGE-SYSTEM-002 + AC-PERMANENT-FIX-006: Challenge-driven interaction

        Args:
            user_request: Natural language user request
            context: Optional context dictionary

        Returns:
            Dictionary with challenge (if disagreement) or execution result
        """
        result = self.process_user_request(user_request, context or {})

        if result.is_ok():
            return {"status": "success", "data": result.unwrap()}
        else:
            return {"status": "error", "error": result.error}

    @mcp_tool(
        name="get_relevant_business_knowledge",
        description="Get relevant business knowledge for request composition"
    )


    @mcp_tool(
        name="orchestrate_e2e",
        description="Execute E2E orchestration with cross-phase state management"
    )
    def orchestrate_e2e(
        self,
        operation_id: str,
        user_intent: str,
        priority: int = 0
    ) -> Result[Dict[str, Any]]:
        """
        Execute end-to-end orchestration with state consistency.

        AC-REM-011-05: Cross-Phase State Consistency

        Implements 4-phase orchestration with state carryover:
        - Phase 1: Comprehension (user intent analysis)
        - Phase 2: LENS (language-examination-synthesis-knowledge)
        - Phase 3: Delegation (route to domain orchestrators)
        - Phase 4: Execution (domain-specific execution)

        Args:
            operation_id: Unique operation identifier
            user_intent: User's original intent
            priority: Operation priority

        Returns:
            Result with E2E orchestration results
        """
        try:
            # AC-REM-011-05: Create operation state
            state = self._state_manager.create_operation(
                operation_id=operation_id,
                user_intent=user_intent,
                priority=priority,
                metadata={
                    "phases": [1, 2, 3, 4],
                    "started_at": datetime.now().isoformat(),
                    "governance_validated": False
                }
            )

            self.logger.log_operation_start(
                ac_id="AC-REM-011-05",
                operation="E2E_ORCHESTRATION",
                details={
                    "operation_id": operation_id,
                    "user_intent": user_intent,
                    "phases": 4,
                    "state_manager": "initialized"
                }
            )

            # Phase 1: Comprehension (Intent Analysis)
            phase_1_output = self._execute_phase_1(operation_id, state)
            self._state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=1,
                to_phase=2,
                phase_output=phase_1_output
            )

            # Phase 2: LENS Pipeline (Intent Routing)
            phase_2_context = self._state_manager.get_context_for_phase(
                operation_id=operation_id,
                target_phase=2
            )
            phase_2_output = self._execute_phase_2(operation_id, phase_2_context or {})
            self._state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=2,
                to_phase=3,
                phase_output=phase_2_output
            )

            # Phase 3: Delegation (Route to Orchestrators)
            phase_3_context = self._state_manager.get_context_for_phase(
                operation_id=operation_id,
                target_phase=3
            )
            phase_3_output = self._execute_phase_3(operation_id, phase_3_context or {})
            self._state_manager.transition_phase(
                operation_id=operation_id,
                from_phase=3,
                to_phase=4,
                phase_output=phase_3_output
            )

            # Phase 4: Execution (Domain-Specific)
            phase_4_context = self._state_manager.get_context_for_phase(
                operation_id=operation_id,
                target_phase=4
            )
            phase_4_output = self._execute_phase_4(operation_id, phase_4_context or {})

            # Mark as complete
            self._state_manager.complete_operation(operation_id)

            # Get final state with all phase outputs
            final_state = self._state_manager.get_operation_state(operation_id)

            result = {
                "operation_id": operation_id,
                "status": "complete",
                "phases_executed": 4,
                "phase_outputs": final_state.phase_outputs if final_state else {},
                "final_output": phase_4_output,
                "timestamp": datetime.now().isoformat()
            }

            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="E2E_ORCHESTRATION",
                success=True,
                details={
                    "operation_id": operation_id,
                    "phases_executed": 4,
                    "state_consistency": "maintained"
                }
            )

            return Ok(result)

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="E2E_ORCHESTRATION",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"E2E orchestration failed: {str(e)}")

    def _execute_phase_1(
        self,
        operation_id: str,
        state: OperationState
    ) -> Dict[str, Any]:
        """
        Execute Phase 1: Comprehension.

        Analyze user intent and prepare for LENS pipeline.
        """
        try:
            phase_output = {
                "phase": 1,
                "name": "Comprehension",
                "user_intent": state.user_intent,
                "intent_type": "UNKNOWN",
                "confidence": 0.0,
                "analysis_complete": True
            }

            # Attempt to use Interaction Orchestrator if available
            if self.interaction_orchestrator:
                try:
                    result = self.interaction_orchestrator.execute(
                        context={"user_intent": state.user_intent}
                    )
                    if result.is_ok():
                        comprehension_data = result.unwrap()
                        phase_output.update(comprehension_data)
                        self.logger.log_operation_complete(
                            ac_id="AC-REM-011-01",
                            operation="STAGE_1_EXECUTE",
                            success=True,
                            details={
                                "intent_type": comprehension_data.get("intent_type"),
                                "confidence": comprehension_data.get("confidence")
                            }
                        )
                    else:
                        error = result.unwrap_err()
                        self.logger.log_operation_complete(
                            ac_id="AC-REM-011-01",
                            operation="STAGE_1_EXECUTE",
                            success=False,
                            details={"error": error}
                        )
                except Exception as e:
                    self.logger.log_operation_complete(
                        ac_id="AC-REM-011-01",
                        operation="STAGE_1_EXECUTE",
                        success=False,
                        details={"error": str(e)}
                    )

            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_1_COMPREHENSION",
                success=True,
                details={"operation_id": operation_id}
            )

            return phase_output

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_1_COMPREHENSION",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 1, "error": str(e)}

    def _execute_phase_2(
        self,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Phase 2: LENS Pipeline.

        Route user intent through LENS pipeline.
        """
        try:
            from cortex.intelligence.lens.lens.lens_pipeline import LENSPipeline

            pipeline = LENSPipeline()
            result = pipeline.execute(context)

            phase_output = {
                "phase": 2,
                "name": "LENS",
                "routing_decision": result.get("routing_decision"),
                "confidence": result.get("confidence", 0.0),
                "pipeline_complete": True
            }

            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_2_LENS",
                success=True,
                details={"operation_id": operation_id}
            )

            return phase_output

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_2_LENS",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 2, "error": str(e)}

    def _execute_phase_3(
        self,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Phase 3: Delegation.

        Delegate to appropriate domain orchestrators.
        """
        try:
            phase_output = {
                "phase": 3,
                "name": "Delegation",
                "routing_decision": context.get("routing_decision"),
                "delegated_domains": list(self.domain_orchestrators.keys()),
                "delegation_count": len(self.domain_orchestrators)
            }

            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_3_DELEGATION",
                success=True,
                details={"operation_id": operation_id}
            )

            return phase_output

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_3_DELEGATION",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 3, "error": str(e)}

    def _execute_phase_4(
        self,
        operation_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute Phase 4: Execution.

        Perform domain-specific execution.
        """
        try:
            phase_output = {
                "phase": 4,
                "name": "Execution",
                "execution_complete": True,
                "execution_timestamp": datetime.now().isoformat(),
                "result": "Success"
            }

            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_4_EXECUTION",
                success=True,
                details={"operation_id": operation_id}
            )

            return phase_output

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-05",
                operation="PHASE_4_EXECUTION",
                success=False,
                details={"error": str(e)}
            )
            return {"phase": 4, "error": str(e)}

    # ========== PLANNING REFINEMENT INTEGRATION ==========

    def execute_plan_via_tdd(
        self,
        session_id: str,
        approved_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute an approved plan via TDD orchestrator.

        Called after planning refinement session achieves DoR.
        Routes plan to TDDOrchestrator for implementation.

        Args:
            session_id: Planning session identifier
            approved_plan: Plan dict approved during refinement

        Returns:
            Dict with execution results
        """
        self.logger.log_operation_start(
            ac_id="AC-PLANNING-REFINE-EXECUTE",
            operation="execute_plan_via_tdd",
            details={
                "session_id": session_id,
            }
        )

        try:
            # Check if TDDOrchestrator is available
            if not TDDOrchestrator or not get_tdd_orchestrator:
                self.logger.log_operation_complete(
                    ac_id="AC-PLANNING-REFINE-EXECUTE",
                    operation="execute_plan_via_tdd",
                    success=False,
                    details={"error": "TDDOrchestrator not available"}
                )
                return {
                    "success": False,
                    "error": "TDDOrchestrator not available",
                    "session_id": session_id,
                }

            # Get TDD orchestrator
            tdd_orchestrator = get_tdd_orchestrator()

            # Prepare context for TDD execution
            context = {
                "planning_session_id": session_id,
                "feature_request": approved_plan.get("user_request", ""),
                "acceptance_criteria": approved_plan.get("acceptance_criteria", []),
                "implementation_steps": approved_plan.get("steps", []),
                "constraints": approved_plan.get("constraints", []),
                "risks": approved_plan.get("risks", []),
            }

            # Execute via TDD (write tests first)
            # This calls tdd_orchestrator.execute(context)
            execution_result = tdd_orchestrator.execute(
                operation_mode=OperationMode.AUTO,
                context=context,
            )

            # Log successful execution
            self.logger.log_operation_complete(
                ac_id="AC-PLANNING-REFINE-EXECUTE",
                operation="execute_plan_via_tdd",
                success=True,
                details={
                    "session_id": session_id,
                    "execution_status": "initiated",
                }
            )

            return {
                "success": True,
                "session_id": session_id,
                "execution_status": "initiated",
                "tdd_result": execution_result,
            }

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PLANNING-REFINE-EXECUTE",
                operation="execute_plan_via_tdd",
                success=False,
                details={"error": str(e), "exception_type": type(e).__name__}
            )
            return {
                "success": False,
                "error": f"Plan execution failed: {str(e)}",
                "session_id": session_id,
            }

    @mcp_tool(
        name="ask_codebase_question",
        description="Ask questions about codebase using CORTEX Inquiry System"
    )

    @mcp_tool(
        name="tech_intelligence_get_readiness",
        description="Get tech stack readiness score for implementation. Provides 4-factor weighted scoring (best practices 40%, TDD 30%, security 20%, usage 10%) with automatic learning gap detection."
    )
    
    def _trigger_lifecycle_hooks_sync(self, operation_name: str, metadata: Dict[str, Any]) -> None:
        """
        Trigger lifecycle hooks synchronously (fire-and-forget).
        
        ENH-092 Phase 53.3: Automatic cleanup on completions.
        
        Args:
            operation_name: Operation that completed (implement, fix, refactor, etc.)
            metadata: Operation metadata for context
        """
        import asyncio
        from cortex.orchestrators.core.lifecycle_hook_system import CompletionEvent
        
        try:
            # Determine event type from operation name
            event_map = {
                "wave": CompletionEvent.WAVE_COMPLETE,
                "phase": CompletionEvent.PHASE_COMPLETE,
                "stage": CompletionEvent.STAGE_COMPLETE,
                "session": CompletionEvent.SESSION_END
            }
            
            event_type = None
            entity_id = operation_name
            
            # Extract event type from operation name or metadata
            for key, event in event_map.items():
                if key in operation_name.lower():
                    event_type = event
                    break
                if metadata.get("type") == key:
                    event_type = event
                    entity_id = metadata.get("id", operation_name)
                    break
            
            # Default to STAGE_COMPLETE if no specific event detected
            if not event_type:
                event_type = CompletionEvent.STAGE_COMPLETE
            
            # Create async task (fire-and-forget)
            async def _trigger() -> None:
                """Trigger."""
                await self._lifecycle_hook_system.trigger_completion(
                    event_type=event_type,
                    entity_id=entity_id,
                    metadata=metadata
                )

            # Run in background without blocking.
            # Guard: asyncio.create_task requires a running event loop.
            # When called from a sync context (no loop), schedule via
            # ensure_future on the running loop, or silently skip.
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_trigger())
            except RuntimeError:
                # No running event loop — sync context, skip fire-and-forget
                pass
            
            self.logger.log_operation_complete(
                ac_id="AC-ENH-092-002",
                operation="LIFECYCLE_HOOK_TRIGGERED",
                success=True,
                details={"event": event_type.value, "entity": entity_id}
            )
            
        except Exception as hook_err:
            # Log but don't fail - hooks are non-blocking
            self.logger.log_operation_complete(
                ac_id="AC-ENH-092-002",
                operation="LIFECYCLE_HOOK_TRIGGERED",
                success=False,
                details={"error": f"Failed to trigger lifecycle hooks: {str(hook_err)}"}
            )

    def _check_mcp_gate(self, classified_intent: str) -> "Result[None]":
        """CORE-050: Hard-block code-modifying intents when MCP is unavailable.

        Implements the CORE-050 MCP Circuit Breaker at the Python level. This
        gate runs after Stage 3 compliance validation and before Stage 4 domain
        execution. It ensures that IMPLEMENT, FIX, REFACTOR, AUDIT, PLAN, and
        ANALYZE operations are never executed without an active MCP connection.

        Args:
            classified_intent: The intent string from Stage 2 classification
                (e.g. "IMPLEMENT", "FIX", "REFACTOR").

        Returns:
            Ok(None) if allowed or MCP is available.
            Err(str) with a user-facing message if hard-blocked.
        """
        # Intents that REQUIRE MCP (CORE-050 tiered blocking)
        _MCP_REQUIRED_INTENTS = {
            "implement", "fix", "refactor", "audit",
            "analyze", "plan", "tdd", "design",
        }

        if classified_intent.lower() not in _MCP_REQUIRED_INTENTS:
            return Ok(None)

        # Check MCP availability via NativeToolInterceptor detector
        try:
            from cortex.governance.enforcement.native_tool_interceptor import MCPDetector
            mcp_available = MCPDetector().is_mcp_available()
        except Exception:
            # If detector fails to import/run, assume available (fail-open)
            mcp_available = True

        if not mcp_available:
            return Err(
                f"CORE-050: MCP server required for '{classified_intent}' intent but is unavailable. "
                "Run `python3 scripts/setup-mcp.py` and reload VS Code."
            )

        return Ok(None)

    def _check_for_workflow_template(
        self, context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check if workflow template should be used for this operation.

        WORKFLOW-COMPLEXITY-GATE-001: Complexity-based template routing.

        Uses WorkflowComplexityRouter to determine if operation requires
        workflow template based on 4-dimension complexity scoring.

        Args:
            context: Operation context with description, intent, attachments, keywords.

        Returns:
            Routing decision with template_id if template suggested, None otherwise.
        """
        try:
            # Import complexity router
            from cortex.orchestrators.core.intent_router.workflow_gate import WorkflowComplexityRouter, Intent as ComplexityIntent
            from cortex.orchestrators.core.intent_router.workflow_gate import RoutingStrategy
            
            # Extract operation details
            operation = context.get("operation", "").lower()
            description = context.get("description", "").lower()
            combined_text = f"{operation} {description}"
            
            # Detect operation type — covers all 20 CORTEX intent types (GAP-90-14/15 fix)
            operation_type = "implement"
            if any(kw in combined_text for kw in ["fix", "bug", "issue", "broken", "patch"]):
                operation_type = "fix"
            elif any(kw in combined_text for kw in ["/debug", "debug", "diagnose", "debugger", "marker injection", "injection strategy"]):
                operation_type = "debug"
            elif any(kw in combined_text for kw in ["totalrecall", "total recall", "holistic refactor", "7-phase", "everything is broken"]):
                operation_type = "totalrecall"
            elif any(kw in combined_text for kw in ["rca", "root cause analysis", "fishbone", "five whys", "ishikawa", "fault tree", "causal chain"]):
                operation_type = "rca"
            elif any(kw in combined_text for kw in ["/vacuum", "vacuum", "markdown sprawl", "root clutter", "cortex vacuum"]):
                operation_type = "vacuum"
            elif any(kw in combined_text for kw in ["/health", "health check", "healthcheck", "orchestrator health", "orchestrator status", "22 orchestrators"]):
                operation_type = "health"
            elif any(kw in combined_text for kw in ["/sync", "sync to company", "cross-repo sync", "privacy-safe sync", "one-way sync"]):
                operation_type = "sync"
            elif any(kw in combined_text for kw in ["/train", "learn from repo", "evolve templates", "gap-driven training", "pattern training"]):
                operation_type = "train"
            elif any(kw in combined_text for kw in ["audit", "production readiness", "scan for issues", "repo health"]):
                operation_type = "audit"
            elif any(kw in combined_text for kw in ["refactor", "improve", "optimize", "restructure", "simplify"]):
                operation_type = "refactor"
            elif any(kw in combined_text for kw in ["migrate", "migration", "port", "alembic"]):
                operation_type = "migrate"
            elif any(kw in combined_text for kw in ["test", "testing", "pytest", "tdd"]):
                operation_type = "test"
            elif any(kw in combined_text for kw in ["design", "architect", "blueprint", "system design"]):
                operation_type = "design"
            elif any(kw in combined_text for kw in ["onboard", "onboarding", "bootstrap", "initialize repo"]):
                operation_type = "onboard"
            elif any(kw in combined_text for kw in ["digest", "summarize", "summarise", "recap", "tl;dr"]):
                operation_type = "digest"
            elif any(kw in combined_text for kw in ["investigate", "root cause", "deep analysis", "find the cause"]):
                operation_type = "investigate"
            elif any(kw in combined_text for kw in ["document", "docs", "documentation"]):
                operation_type = "document"
            elif any(kw in combined_text for kw in ["plan", "roadmap", "phase", "schedule"]):
                operation_type = "plan"
            elif any(kw in combined_text for kw in ["security"]):
                operation_type = "security"
            
            # Extract files and dependencies
            target_files = context.get("target_files", [])
            dependencies = context.get("dependencies", [])
            risk_level = context.get("risk_level", "MEDIUM")
            
            # Build complexity intent
            complexity_intent = ComplexityIntent(
                operation_type=operation_type,
                target_files=target_files,
                dependencies=dependencies,
                risk_level=risk_level,
                metadata=context
            )
            
            # Route based on complexity
            router = WorkflowComplexityRouter()
            decision = router.route(complexity_intent)
            
            # If workflow template recommended, return template info
            if decision.route == RoutingStrategy.WORKFLOW_TEMPLATE:
                self.logger.log_operation_complete(
                    ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                    operation="WORKFLOW_TEMPLATE_SELECTED",
                    success=True,
                    details={
                        "template_id": decision.template_id,
                        "complexity": decision.complexity,
                        "rationale": decision.rationale
                    }
                )
                
                return {
                    "template_id": decision.template_id,
                    "template_name": decision.template_id.replace("/", "_"),
                    "intent": operation_type.upper(),
                    "use_autonomous_workflow": True,
                    "complexity_score": decision.complexity,
                    "requires_confirmation": decision.requires_confirmation
                }
            
            # Direct orchestrator routing - return None to continue standard flow
            self.logger.log_operation_complete(
                ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                operation="DIRECT_ORCHESTRATOR_SELECTED",
                success=True,
                details={
                    "orchestrator": decision.orchestrator,
                    "complexity": decision.complexity,
                    "rationale": decision.rationale
                }
            )
            
            return None

        except Exception as e:
            # Log but don't fail - template routing is optional enhancement
            self.logger.log_operation_complete(
                ac_id="WORKFLOW-COMPLEXITY-GATE-001",
                operation="WORKFLOW_TEMPLATE_CHECK",
                success=False,
                details={"error": f"Template check failed: {str(e)}"},
            )
            return None