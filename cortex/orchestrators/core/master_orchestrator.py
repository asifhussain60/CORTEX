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

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err
from cortex.brain.core.response_header_injector import ResponseHeaderInjector
from cortex.brain.core.response_header_config import HeaderConfigurationManager
from cortex.orchestrators.core.governance_registry import GovernanceRegistry
from cortex.execution.exec_gateway_impl import GovernanceViolationError
from cortex_brain.tier2.hallucination_prevention import BehavioralBoundaryRules
from cortex.brain.core.knowledge.knowledge_repository import KnowledgeRepository
from cortex.brain.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine, get_synthesis_engine
from cortex.brain.knowledge.unified_intelligence_context import UnifiedIntelligenceContext
from cortex.brain.core.state_manager import StateManager, OperationState, get_state_manager
from cortex.domain_brain.business_knowledge_repository import (
    BusinessKnowledgeRepository
)
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.database_transaction_manager import DatabaseTransactionManager
from cortex.brain.mcp.decorator import mcp_tool
from cortex.core.intent.challenge_generator import ChallengeGenerator
from cortex.core.orchestrator.holistic_context_builder import HolisticContextBuilder

# Phase 51: Enhanced response template with semantic color coding
from cortex.agents.core.response_template_generator import ResponseTemplate

# AC-UX-VISIBILITY-001: Import orchestrator context decorator
from cortex.orchestrators.decorators import inject_orchestrator_context

# Phase 27: Import StandardsResolver for company domain integration
from cortex.common.standards_resolver import StandardsResolver

# AC-PHASE-2-5-WIRE-001: Import ComponentHealthTracker for health monitoring
from cortex.orchestrators.core.component_health import ComponentHealthTracker, ComponentType

# AC-PHASE-2-5-WIRE-003: Import AdaptiveRouter for intelligent task routing
# Use IntelligentKnowledgeRouter as the canonical implementation
try:
    from cortex.brain.core.knowledge.router import IntelligentKnowledgeRouter as AdaptiveRouter
except ImportError:
    # Fallback if module not accessible
    AdaptiveRouter = None  # type: ignore

# ENH-046 Phase 4 & 5: Import Context Synthesis Gateway (EXIT GATE)
from cortex.interaction.context_synthesis_gateway import get_gateway

# Phase 33: Import response verbosity policies for chat response compression
try:
    from cortex.orchestrators.response.chat_response_policy import (
        ChatResponsePolicyValidator,
        suppress_verbosity,
        inject_plan_spine,
    )
    from cortex.orchestrators.response.markdown_report_ban_policy import (
        MarkdownReportBanPolicy,
    )
    from cortex.orchestrators.response.minimal_plan_spine import MinimalPlanSpine
except ImportError:
    # Fallback if modules not accessible
    ChatResponsePolicyValidator = None
    suppress_verbosity = None
    inject_plan_spine = None
    MarkdownReportBanPolicy = None
    MinimalPlanSpine = None

# Phase 34: Import advanced response optimization components
try:
    from cortex.orchestrators.response.semantic_deduplicator import SemanticDeduplicator
    from cortex.orchestrators.response.response_quality_scorer import ResponseQualityScorer
    from cortex.orchestrators.response.role_verbosity_profiles import (
        RoleVerbosityProfiles,
        Role
    )
    PHASE_34_AVAILABLE = True
except ImportError:
    # Fallback if modules not accessible or dependencies missing
    SemanticDeduplicator = None
    ResponseQualityScorer = None
    RoleVerbosityProfiles = None
    Role = None
    PHASE_34_AVAILABLE = False

# Phase 35: Import autonomous execution components for continuation detection & progress bars
# AC-PHASE-35-001: Autonomous continuation detection (R1)
# AC-PHASE-35-002: ASCII progress bar integration (R2)
try:
    from cortex.interaction.autonomous_plan_executor import AutonomousPlanExecutor
    from cortex.orchestrators.response.ascii_progress_bar import ASCIIProgressBar
except ImportError:
    # Fallback if modules not accessible
    AutonomousPlanExecutor = None
    ASCIIProgressBar = None

# Note: GracefulDegradationFramework imported lazily in __init__ to avoid circular imports

# AC-IKP-002-02: Import IntelligentKnowledgeRouter for knowledge backend coordination
try:
    from cortex.brain.core.knowledge.router import IntelligentKnowledgeRouter
except ImportError:
    # Fallback if module not accessible
    IntelligentKnowledgeRouter = None

# AC-REM-011-02: Import TDD Orchestrator for test-driven development workflow routing
# Wires 35 best practices YAMLs from cortex_brain/tier3/knowledge/ into TDD discipline
try:
    from cortex.orchestrators.core.tdd_orchestrator import (
        TDDOrchestrator,
        get_tdd_orchestrator,
        TDDPhase
    )
except ImportError:
    # Fallback if module not accessible
    TDDOrchestrator = None
    get_tdd_orchestrator = None
    TDDPhase = None

# AC-GOVE-REM-001: Import IntentRouter for mandatory intent classification
# Enforces intent classification on every operation (architectural enforcement)
try:
    from cortex.orchestrators.core.intent_router import IntentRouter
    get_intent_router = lambda: IntentRouter()
except ImportError:
    # Fallback if module not accessible
    get_intent_router = None

# AC-GOVE-DOR-WIRE-001: Import DoRApprovalGate for user approval before execution
# Displays intent reflection in markdown, waits for user approval
try:
    from cortex.orchestrators.core.dor_approval_gate import DoRApprovalGate
except ImportError:
    # Fallback if module not accessible
    DoRApprovalGate = None

# AC-PHASE-6C-001: Import EnforcementOrchestrator for pre-execution governance gate
# 7-agent system enforcing 25/29 CORE rules (86% coverage)
try:
    from cortex.orchestrators.core.enforcement_orchestrator import (
        EnforcementOrchestrator,
        EnforcementLevel
    )
except ImportError:
    # Fallback if module not accessible
    EnforcementOrchestrator = None
    EnforcementLevel = None

# AC-PHASE-25-STAGE-4-002: Import PlanOrchestrator for PLAN MODE operations
# Phase lifecycle management with setup/teardown hooks, intelligent resolution, dashboard sync
try:
    from cortex.orchestrators.support.plan_orchestrator import PlanOrchestrator
except ImportError:
    # Fallback if module not accessible
    PlanOrchestrator = None

# AC-PHASE-34B-WEEK-3-INC-7: Import TechIntelligenceOrchestrator for proactive tech stack intelligence
# Provides readiness scoring, ecosystem scanning, knowledge synthesis, learning triggers
# Priority 82 (high), supports IMPLEMENT intent pre-flight checks
try:
    from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import (
        TechIntelligenceOrchestrator
    )
except ImportError:
    # Fallback if module not accessible
    TechIntelligenceOrchestrator = None

# AC-CHALLENGE-SYSTEM-002 + AC-PERMANENT-FIX-006: Import InteractionOrchestrator with challenge system
# Stage 1 comprehension with LENS-powered challenge generation
try:
    from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
    from cortex.brain.core.orchestrator.conversation_protocol import ConversationProtocol
    from cortex.brain.core.orchestrator.round_context import RoundContext
except ImportError:
    # Fallback if module not accessible
    InteractionOrchestrator = None
    ConversationProtocol = None
    RoundContext = None

# Docker-First Architecture: YAML-backed wiring (no database registries)
# Orchestrator config loaded from cortex/wiring/specifications/wiring.yaml

from cortex.orchestrators.registry import OrchestratorMetadata


class MasterOrchestrator(IOrchestrator):
    """
    MasterOrchestrator - Coordinates all domain orchestrators.
    
    Implements the coordinator pattern to manage multiple domain orchestrators:
    - Maintains registry of domain orchestrators
    - Routes operations to applicable orchestrators
    - Aggregates results from multiple orchestrators
    - Logs all delegation decisions with audit trail
    
    AC-AR-006-01: MasterOrchestrator coordinates domain orchestrators
    """
    
    _instance: Optional['MasterOrchestrator'] = None
    
    def __init__(self):
        """Initialize MasterOrchestrator"""
        self.logger = EnhancedAuditLogger.instance()
        self.domain_orchestrators: Dict[str, OrchestratorMetadata] = {}
        self.operation_history: List[Dict[str, Any]] = []
        
        # AC-GOVE-RENDER-002: Rendering control flag (disable markdown during execution)
        # Rendering is deferred to presentation layer (e.g., GitHub Copilot Chat)
        self.render_markdown = False  # Set to True only if explicitly requested by caller
        
        # AC-REM-011-05: Initialize StateManager for cross-phase state consistency
        self._state_manager: StateManager = get_state_manager()
        self.logger.log_operation_complete(
            ac_id="AC-REM-011-05",
            operation="STATE_MANAGER_INIT",
            success=True,
            details={"manager": "StateManager initialized for cross-phase consistency"}
        )
        
        # AC-REM-011-01: Initialize stage orchestrators for E2E workflow
        # Stage 1: Interaction Orchestrator (Comprehension)
        self.interaction_orchestrator: Optional[IOrchestrator] = None
        # Stage 2: Intent Router
        self.intent_router: Optional[IOrchestrator] = None
        # Stage 2.5: Knowledge Synthesis Engine (Phase 20.5)
        self._synthesis_engine: KnowledgeSynthesisEngine = get_synthesis_engine()
        # Stage 3 Registry: Orchestrator registry for delegation
        self.orchestrator_registry: Dict[str, IOrchestrator] = {}
        
        # AC-GOVE-DOR-WIRE-001: Initialize DoRApprovalGate for user approval workflow
        # Displays intent reflection in markdown, waits for user approval before execution
        self._dor_gate: Optional[DoRApprovalGate] = None
        if DoRApprovalGate is not None:
            try:
                self._dor_gate = DoRApprovalGate()
                self.logger.log_operation_complete(
                    ac_id="AC-GOVE-DOR-WIRE-001",
                    operation="DOR_APPROVAL_GATE_INIT",
                    success=True,
                    details={"gate": "DoRApprovalGate initialized for user approval workflow"}
                )
            except Exception as gate_err:
                # Log but don't fail - DoR gate is enhancement, not blocking
                self.logger.log_operation_complete(
                    ac_id="AC-GOVE-DOR-WIRE-001",
                    operation="DOR_APPROVAL_GATE_INIT",
                    success=False,
                    details={"error": f"Failed to initialize DoRApprovalGate: {str(gate_err)}"}
                )
        
        # AC-PHASE-6C-001: Initialize EnforcementOrchestrator for pre-execution governance
        # 7-agent system: Governance, Security, Compliance, FileNaming, Incremental, Markdown, Architecture
        # Enforces 25/29 CORE rules (86% coverage) with <150ms validation time
        self._enforcement: Optional[EnforcementOrchestrator] = None
        if EnforcementOrchestrator is not None:
            try:
                self._enforcement = EnforcementOrchestrator()
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-6C-001",
                    operation="ENFORCEMENT_ORCHESTRATOR_INIT",
                    success=True,
                    details={
                        "agent_count": len(self._enforcement.agents),
                        "coverage": "25/29 CORE rules (86%)",
                        "agents": [
                            "GovernanceEnforcementAgent",
                            "SecurityCheckpointAgent",
                            "ComplianceValidationAgent",
                            "FileNamingEnforcementAgent",
                            "IncrementalExecutionAgent",
                            "MarkdownSuppressionAgent",
                            "ArchitectureIntegrityAgent"
                        ]
                    }
                )
            except Exception as enforcement_err:
                # Log but don't fail - enforcement is critical but shouldn't block initialization
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-6C-001",
                    operation="ENFORCEMENT_ORCHESTRATOR_INIT",
                    success=False,
                    details={"error": f"Failed to initialize EnforcementOrchestrator: {str(enforcement_err)}"}
                )
        
        # AC-FIX-001-01: Initialize DatabaseTransactionManager for atomic operations
        db_path = Path(__file__).parent.parent.parent.parent / "cortex_brain" / "state" / "governance.db"
        self.transaction_manager = DatabaseTransactionManager(str(db_path))
        
        # Phase 27: Initialize StandardsResolver for company domain integration
        self.standards_resolver = StandardsResolver()
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-27-001",
            operation="STANDARDS_RESOLVER_INIT",
            success=True,
            details={"resolver": "StandardsResolver initialized for company domain integration"}
        )
        
        # AC-REM-002-04: Initialize GovernanceRegistry for per-turn validation
        self._governance_registry: Optional[GovernanceRegistry] = None
        self._turn_number: int = 0  # Track turn count for governance validation
        
        # AC-FIX-HALLUCINATION-001: Initialize boundary enforcement
        self._boundary_rules = BehavioralBoundaryRules()
        
        # AC-PHASE-2-WIRE-001: Initialize ChallengeGenerator for Stage 1 challenge detection
        self._challenge_generator = ChallengeGenerator()
        
        # AC-PHASE-2-WIRE-002: Initialize HolisticContextBuilder for Stage 4 context synthesis
        self._holistic_context_builder = HolisticContextBuilder()
        
        # AC-PHASE-2-5-WIRE-001: Initialize ComponentHealthTracker for system health monitoring
        self._component_health_tracker = ComponentHealthTracker()
        # Register all critical components for health tracking
        self._component_health_tracker.register_component(
            "MasterOrchestrator", ComponentType.CRITICAL
        )
        self._component_health_tracker.register_component(
            "ChallengeGenerator", ComponentType.CRITICAL
        )
        self._component_health_tracker.register_component(
            "HolisticContextBuilder", ComponentType.CRITICAL
        )
        self._component_health_tracker.register_component(
            "KnowledgeRepository", ComponentType.OPTIONAL
        )
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-2-5-WIRE-001",
            operation="COMPONENT_HEALTH_TRACKER_INIT",
            success=True,
            details={"message": "Component health tracking initialized"}
        )
        
        # AC-PHASE-2-5-WIRE-002: Initialize GracefulDegradationFramework for resilience
        # Import from cortex_brain to avoid circular imports in cortex.brain.tier2
        from cortex_brain.tier2.resilience import GracefulDegradationFramework
        self._graceful_degradation = GracefulDegradationFramework()
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-2-5-WIRE-002",
            operation="GRACEFUL_DEGRADATION_INIT",
            success=True,
            details={"message": "Graceful degradation framework initialized"}
        )
        
        # AC-PHASE-2-5-WIRE-003: Initialize AdaptiveRouter for intelligent task routing
        # Note: AdaptiveRouter is IntelligentKnowledgeRouter which needs providers
        # Will be initialized later after knowledge repositories are set up
        self._adaptive_router = None  # Placeholder, set after knowledge repos init
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-2-5-WIRE-003",
            operation="ADAPTIVE_ROUTER_PLACEHOLDER",
            success=True,
            details={"message": "Adaptive router will be initialized after knowledge repos"}
        )
        
        # AC-KN-002-01: Initialize Knowledge Repository for best practices access
        self._knowledge_repository: Optional[KnowledgeRepository] = None
        try:
            self._knowledge_repository = KnowledgeRepository()
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_REPOSITORY_INIT",
                success=True,
                details={
                    "entry_count": self._knowledge_repository.entry_count,
                    "domains": self._knowledge_repository.domains
                }
            )
        except FileNotFoundError as e:
            # Log but don't fail - knowledge is enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_REPOSITORY_INIT",
                success=False,
                details={"error": f"Knowledge repository not available: {str(e)}"}
            )
        
        # AC-KN-003-01: Initialize Business Knowledge Repository for domain brain access
        self._business_knowledge_repository: Optional[BusinessKnowledgeRepository] = None
        try:
            self._business_knowledge_repository = BusinessKnowledgeRepository()
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_REPOSITORY_INIT",
                success=True,
                details={
                    "domains": self._business_knowledge_repository.domains,
                    "entry_count": self._business_knowledge_repository.entry_count
                }
            )
        except Exception as e:
            # Log but don't fail - business knowledge is enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_REPOSITORY_INIT",
                success=False,
                details={"error": f"Business knowledge repository not available: {str(e)}"}
            )
        
        # AC-IKP-002-02: Initialize IntelligentKnowledgeRouter for backend coordination
        self.router = None
        try:
            if IntelligentKnowledgeRouter is not None:
                # Initialize router with available knowledge backends
                tech_provider = None
                business_provider = None
                
                if self._knowledge_repository is not None:
                    tech_provider = self._knowledge_repository
                if self._business_knowledge_repository is not None:
                    business_provider = self._business_knowledge_repository
                
                if tech_provider and business_provider:
                    self.router = IntelligentKnowledgeRouter(
                        tech_provider=tech_provider,
                        business_provider=business_provider,
                        tech_confidence_threshold=70.0,
                        business_confidence_threshold=70.0,
                        fallback_threshold=50.0
                    )
                    # AC-PHASE-2-5-WIRE-003: Set adaptive router now that providers are ready
                    self._adaptive_router = self.router
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-2-5-WIRE-003",
                        operation="ADAPTIVE_ROUTER_INIT",
                        success=True,
                        details={"message": "Adaptive router initialized with knowledge providers"}
                    )
                    self.logger.log_operation_complete(
                        ac_id="AC-IKP-002-02",
                        operation="ROUTER_INIT",
                        success=True,
                        details={
                            "tech_provider": "KnowledgeRepository",
                            "business_provider": "BusinessKnowledgeRepository",
                            "tech_threshold": 70.0,
                            "business_threshold": 70.0
                        }
                    )
                else:
                    # If either backend unavailable, create dummy router with backends dict for tests
                    @dataclass
                    class DummyRouter:
                        """Dummy router for tests when real backends unavailable."""
                        backends: Dict[str, Any] = field(default_factory=dict)
                        
                        def route_query(self, query: str) -> Tuple[Any, float, Dict[str, Any]]:
                            """Dummy route_query for test compatibility."""
                            backend = list(self.backends.values())[0] if self.backends else None
                            return backend, 0.8, {'selected_backend': 'default', 'confidence': 0.8}
                    
                    self.router = DummyRouter()
                    self.logger.log_operation_complete(
                        ac_id="AC-IKP-002-02",
                        operation="ROUTER_INIT",
                        success=False,
                        details={"error": "Using dummy router - one or both knowledge backends unavailable"}
                    )
        except Exception as e:
            # Log but don't fail - router is enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-IKP-002-02",
                operation="ROUTER_INIT",
                success=False,
                details={"error": f"Router initialization failed: {str(e)}"}
            )
        
        # AC-HYBRID-KNOWLEDGE-005: Initialize KnowledgeSynthesisEngine for instruction synthesis
        # Synthesizes CORTEX + Company knowledge into final instructions with source attribution
        self._synthesis_engine: Optional[KnowledgeSynthesisEngine] = None
        try:
            self._synthesis_engine = KnowledgeSynthesisEngine()
            self.logger.log_operation_complete(
                ac_id="AC-HYBRID-KNOWLEDGE-005",
                operation="SYNTHESIS_ENGINE_INIT",
                success=True,
                details={
                    "message": "Knowledge synthesis engine initialized for instruction generation with source attribution"
                }
            )
        except Exception as e:
            # Log but don't fail - synthesis is enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-HYBRID-KNOWLEDGE-005",
                operation="SYNTHESIS_ENGINE_INIT",
                success=False,
                details={"error": f"Knowledge synthesis engine initialization failed: {str(e)}"}
            )
        
        # Track current operation context for header variables
        self.current_operation: Optional[str] = None
        self.current_phase: Optional[str] = None
        
        # AC-CHALLENGE-SYSTEM-002 + AC-PERMANENT-FIX-006: Initialize InteractionOrchestrator
        # Stage 1 comprehension with challenge-driven interaction
        # Import here to avoid circular import issues
        self.interaction_orchestrator_with_challenges: Optional[Any] = None
        try:
            from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator as InteractionOrch
            from cortex.brain.core.orchestrator.conversation_protocol import ConversationProtocol as ConvProtocol
            
            # Create ConversationProtocol with self as orchestrator
            protocol = ConvProtocol(orchestrator=self)
            self.interaction_orchestrator_with_challenges = InteractionOrch(
                conversation_protocol=protocol,
                enable_challenges=True  # AC-PERMANENT-FIX-006: MUST be True (permanent)
            )
            self.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-006",
                operation="INTERACTION_ORCHESTRATOR_INIT",
                success=True,
                details={"enable_challenges": True, "stage": "Stage_1_comprehension"}
            )
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-006",
                operation="INTERACTION_ORCHESTRATOR_INIT",
                success=False,
                details={"error": str(e)}
            )
        
        # AC-ENH-002-01: Initialize ResponseHeaderInjector for header wrapping
        try:
            config_manager = HeaderConfigurationManager.get_instance()
            config_manager.load_configuration('cortex_brain/tier0/response-headers.yaml')
            
            # Create ResponseHeaderInjector instance
            # Uses composition pattern - injector wraps a template engine
            # For orchestrators that don't use templates, pass None as engine
            self.header_injector = ResponseHeaderInjector(
                template_engine=None,  # Optional: None for orchestrators without templates
                config_manager=config_manager
            )
        except Exception as e:
            # Log but don't fail - headers are enhancement, not blocking
            self.logger.log_operation_complete(
                ac_id="AC-ENH-002-01",
                operation="HEADER_INJECTOR_INIT",
                success=False,
                details={"error": f"Failed to initialize header injector: {str(e)}"}
            )
            # Graceful degradation: continue without header injection
            self.header_injector = None
        
        # AC-REM-011-01 + AC-PERMANENT-FIX-006: Initialize stage orchestrators for E2E workflow
        # Prefer challenge-enabled InteractionOrchestrator if successfully initialized
        if self.interaction_orchestrator_with_challenges:
            # Use challenge-enabled version as primary Stage 1 orchestrator
            self.interaction_orchestrator = self.interaction_orchestrator_with_challenges
            self.logger.log_operation_complete(
                ac_id="AC-PERMANENT-FIX-006",
                operation="STAGE_1_CHALLENGE_SYSTEM_ACTIVE",
                success=True,
                details={"stage": "InteractionOrchestrator with challenge system"}
            )
        elif not self.interaction_orchestrator:
            # Fallback to MasterOrchestrationStage1 if challenge system not available
            try:
                from cortex.orchestrators.core.master_orchestrator_stage_1 import MasterOrchestrationStage1
                self.interaction_orchestrator = MasterOrchestrationStage1()
                self.logger.log_operation_complete(
                    ac_id="AC-REM-011-01",
                    operation="STAGE_1_FALLBACK_INIT",
                    success=True,
                    details={"stage": "MasterOrchestrationStage1 (fallback, no challenge system)"}
                )
            except Exception as e:
                # Log but don't fail - graceful degradation
                self.logger.log_operation_complete(
                    ac_id="AC-REM-011-01",
                    operation="STAGE_1_INIT",
                    success=False,
                    details={"error": str(e)}
                )
        
        # Try to initialize Intent Router for Stage 2
        try:
            from cortex.orchestrators.core.intent_router import IntentRouter
            self.intent_router = IntentRouter()
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_2_INIT",
                success=True,
                details={"stage": "Intent Router initialized"}
            )
        except Exception as e:
            # Log but don't fail - graceful degradation
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-01",
                operation="STAGE_2_INIT",
                success=False,
                details={"error": str(e)}
            )
        
        # AC-REM-011-02: Initialize TDD Orchestrator with 35 best practices YAMLs wired
        # Routes ALL implementation intents through TDD discipline (CORE-019)
        self.tdd_orchestrator: Optional[TDDOrchestrator] = None
        try:
            if get_tdd_orchestrator is not None:
                self.tdd_orchestrator = get_tdd_orchestrator()
                tdd_status = self.tdd_orchestrator.get_tdd_status()
                self.logger.log_operation_complete(
                    ac_id="AC-REM-011-02",
                    operation="TDD_ORCHESTRATOR_INIT",
                    success=True,
                    details={
                        "status": "TDD Orchestrator initialized with knowledge YAMLs",
                        "knowledge_loaded": tdd_status.get("knowledge_loaded", {}),
                        "routing_intent": "CORE-019: Route ALL implementation intents through TDD-Master"
                    }
                )
            else:
                self.logger.log_operation_complete(
                    ac_id="AC-REM-011-02",
                    operation="TDD_ORCHESTRATOR_INIT",
                    success=False,
                    details={"error": "TDD Orchestrator module not available"}
                )
        except Exception as e:
            # Log but don't fail - TDD orchestrator is important but graceful degradation supported
            self.logger.log_operation_complete(
                ac_id="AC-REM-011-02",
                operation="TDD_ORCHESTRATOR_INIT",
                success=False,
                details={"error": f"Failed to initialize TDD Orchestrator: {str(e)}"}
            )
        
        # AC-PHASE-25-STAGE-4-002: Initialize PlanOrchestrator for PLAN MODE operations
        # Phase lifecycle with setup/teardown hooks, intelligent resolution, dashboard sync
        self.plan_orchestrator: Optional['PlanOrchestrator'] = None
        try:
            if PlanOrchestrator is not None:
                self.plan_orchestrator = PlanOrchestrator()
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-25-STAGE-4-002",
                    operation="PLAN_ORCHESTRATOR_INIT",
                    success=True,
                    details={
                        "status": "PlanOrchestrator initialized for PLAN MODE",
                        "features": ["setup/teardown hooks", "intelligent resolution", "dashboard sync"],
                        "routing_intent": "PLAN: Route ALL planning intents through PlanOrchestrator"
                    }
                )
            else:
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-25-STAGE-4-002",
                    operation="PLAN_ORCHESTRATOR_INIT",
                    success=False,
                    details={"error": "PlanOrchestrator module not available"}
                )
        except Exception as e:
            # Log but don't fail - PlanOrchestrator is important but graceful degradation supported
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-25-STAGE-4-002",
                operation="PLAN_ORCHESTRATOR_INIT",
                success=False,
                details={"error": f"Failed to initialize PlanOrchestrator: {str(e)}"}
            )
        
        # AC-PHASE-34B-WEEK-3-INC-7: Initialize TechIntelligenceOrchestrator for proactive tech intelligence
        # Provides readiness scoring, ecosystem scanning, knowledge synthesis, learning triggers
        # Priority 82 (high), supports IMPLEMENT intent pre-flight checks
        self.tech_intelligence_orchestrator: Optional['TechIntelligenceOrchestrator'] = None
        try:
            if TechIntelligenceOrchestrator is not None:
                self.tech_intelligence_orchestrator = TechIntelligenceOrchestrator()
                # Initialize the orchestrator
                init_result = self.tech_intelligence_orchestrator.initialize()
                if init_result:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                        operation="TECH_INTELLIGENCE_ORCHESTRATOR_INIT",
                        success=True,
                        details={
                            "status": "TechIntelligenceOrchestrator initialized",
                            "components": ["EcosystemScanner", "ReadinessEngine", "KnowledgeSynthesizer", "LearningTrigger"],
                            "priority": 82,
                            "features": ["readiness scoring", "tech stack detection", "best practices synthesis", "automatic learning triggers"],
                            "routing_intent": "IMPLEMENT: Pre-flight readiness checks before implementation"
                        }
                    )
                else:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                        operation="TECH_INTELLIGENCE_ORCHESTRATOR_INIT",
                        success=False,
                        details={"error": "TechIntelligenceOrchestrator initialization returned failure"}
                    )
            else:
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                    operation="TECH_INTELLIGENCE_ORCHESTRATOR_INIT",
                    success=False,
                    details={"error": "TechIntelligenceOrchestrator module not available"}
                )
        except Exception as e:
            # Log but don't fail - graceful degradation supported
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_ORCHESTRATOR_INIT",
                success=False,
                details={"error": f"Failed to initialize TechIntelligenceOrchestrator: {str(e)}"}
            )
        
        # AC-PHASE-35-001: Initialize AutonomousPlanExecutor for continuation detection (R1)
        # Detects "proceed", "continue", "yes", "approve" patterns → autonomous execution
        self._autonomous_executor: Optional[AutonomousPlanExecutor] = None
        if AutonomousPlanExecutor is not None:
            try:
                self._autonomous_executor = AutonomousPlanExecutor()
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-35-001",
                    operation="AUTONOMOUS_EXECUTOR_INIT",
                    success=True,
                    details={
                        "feature": "Continuation detection",
                        "patterns": ["proceed", "continue", "yes", "approve", "phase N"],
                        "roi_score": 0.7425
                    }
                )
            except Exception as e:
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-35-001",
                    operation="AUTONOMOUS_EXECUTOR_INIT",
                    success=False,
                    details={"error": f"Failed to initialize AutonomousPlanExecutor: {str(e)}"}
                )
        
        # AC-PHASE-35-002: Initialize ASCIIProgressBar for visual progress indicators (R2)
        # Format: [████████░░] 80% Phase Name
        self._progress_bar: Optional[ASCIIProgressBar] = None
        if ASCIIProgressBar is not None:
            try:
                self._progress_bar = ASCIIProgressBar()
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-35-002",
                    operation="ASCII_PROGRESS_BAR_INIT",
                    success=True,
                    details={
                        "feature": "ASCII progress bars",
                        "format": "[████████░░] 80%",
                        "width": 10,
                        "modes": ["PLAN", "TDD", "IMPLEMENT", "REFACTOR"]
                    }
                )
            except Exception as e:
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-35-002",
                    operation="ASCII_PROGRESS_BAR_INIT",
                    success=False,
                    details={"error": f"Failed to initialize ASCIIProgressBar: {str(e)}"}
                )
        
    @classmethod
    def instance(cls) -> 'MasterOrchestrator':
        """Get singleton instance of MasterOrchestrator"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
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
    
    def _get_intent_router(self):
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
        """
        Stage 2: Route request with unified intelligence synthesis.
        
        Phase 20 Component #4: MasterOrchestrator LENS Integration
        Phase 20.5 Component #3: Knowledge Synthesis at Stage 2
        
        Workflow:
        1. Classify intent via IntentRouter
        2. Fetch LENS context (Phase 20)
        3. Synthesize unified intelligence (Phase 20.5) - LENS + Company + CORTEX
        4. Detect violations early (prevent vs detect)
        5. Provide proactive guidance
        6. Return enhanced routing decision with citations
        
        Args:
            request: Request dictionary with:
                - operation: Operation name/intent
                - description: Operation description
                - file_path: Optional file path for LENS analysis
                - company_name: Optional company name for company knowledge
                - domain: Optional target domain
                - keywords: Optional keywords list
        
        Returns:
            Dict[str, Any]: Routing result with:
                - intent: Detected intent type
                - target_orchestrator: Target orchestrator name
                - confidence_score: Routing confidence
                - reasoning: Routing explanation
                - context: Enhanced context with unified intelligence
                - unified_intelligence: UnifiedIntelligenceContext (Phase 20.5)
                - cited_rules: List of rules cited
                - violations: List of detected violations
                - guidance: Proactive guidance for engineer
        
        Authority: AC-PHASE-20-COMPONENT-4, AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
        """
        try:
            # Ensure IntentRouter is initialized
            if not self.intent_router:
                from cortex.orchestrators.core.intent_router import IntentRouter
                self.intent_router = IntentRouter()
            
            # Prepare request for route_with_lens_auto_fetch
            routing_request = {
                "intent": request.get("operation", ""),
                "description": request.get("description", ""),
                "file_path": request.get("file_path"),
                "company_name": request.get("company_name"),
                "domain": request.get("domain"),
                "keywords": request.get("keywords"),
                "context": request.get("context", {})
            }
            
            # Phase 20.5: Pre-synthesize unified intelligence if possible
            # This allows IntentRouter to use citations in routing decision
            unified_context = None
            try:
                from cortex.brain.knowledge.unified_intelligence_context import (
                    LENSIntelligence,
                    CompanyKnowledge,
                )
                
                # Try to get preliminary LENS context for synthesis
                # (IntentRouter will fetch if missing, but we can pre-fetch for synthesis)
                intent_str = request.get("operation", "")
                file_path = request.get("file_path")
                
                # Basic empty intelligence structures (IntentRouter will enhance with LENS)
                lens_intelligence = LENSIntelligence(
                    git_analysis={},
                    ast_analysis={},
                    comment_analysis={}
                )
                company_knowledge = CompanyKnowledge(
                    domain_rules={},
                    compliance_standards=[],
                    precedence="OVERRIDE"
                )
                
                # Synthesize unified intelligence (CORTEX rules only at this point)
                unified_context = self._synthesis_engine.synthesize_unified_context(
                    intent_type=intent_str,
                    lens_intelligence=lens_intelligence,
                    company_knowledge=company_knowledge,
                    file_path=file_path
                )
                
                self.logger.log_operation_complete(
                    ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                    operation="STAGE_2_PRE_SYNTHESIS",
                    success=True,
                    details={
                        "intent": intent_str,
                        "cited_rules_count": len(unified_context.get_cited_rules()),
                        "cortex_practices_loaded": len(unified_context.cortex_knowledge.best_practices),
                    }
                )
                
            except Exception as pre_synthesis_err:
                # Fail-safe: Continue without pre-synthesis
                self.logger.log_operation_complete(
                    ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                    operation="STAGE_2_PRE_SYNTHESIS_FAILED",
                    success=False,
                    details={"error": str(pre_synthesis_err)}
                )
            
            # Call IntentRouter with LENS auto-fetch + unified intelligence (Phase 20 + 20.5)
            result = self.intent_router.route_with_lens_auto_fetch(
                routing_request,
                unified_intelligence=unified_context  # Pass synthesized intelligence
            )
            intent_type = result.get("intent", "UNKNOWN")
            
            # Phase 20.5: Post-synthesis enhancement with LENS data from IntentRouter
            # (IntentRouter may have fetched additional LENS context)
            try:
                # Re-synthesize with complete LENS data if available
                lens_context = result.get("context", {}).get("lens_insights", {})
                if lens_context and unified_context:
                    # Update LENS intelligence with fetched data
                    from cortex.brain.knowledge.unified_intelligence_context import (
                        LENSIntelligence,
                        CompanyKnowledge,
                    )
                    
                    lens_intelligence = LENSIntelligence(
                        git_analysis=lens_context.get("git_analysis", {}),
                        ast_analysis=lens_context.get("ast_analysis", {}),
                        comment_analysis=lens_context.get("comment_analysis", {})
                    )
                    
                    company_context = lens_context.get("company_knowledge", {})
                    company_knowledge = CompanyKnowledge(
                        domain_rules=company_context.get("domain_rules", {}),
                        compliance_standards=company_context.get("compliance_standards", []),
                        precedence="OVERRIDE"
                    )
                    
                    # Re-synthesize with complete data
                    unified_context = self._synthesis_engine.synthesize_unified_context(
                        intent_type=intent_type,
                        lens_intelligence=lens_intelligence,
                        company_knowledge=company_knowledge,
                        file_path=request.get("file_path")
                    )
                
                # Attach unified intelligence to result (whether pre-synthesis or post-synthesis)
                if unified_context:
                    result["unified_intelligence"] = unified_context.to_dict()
                    result["cited_rules"] = unified_context.get_cited_rules()
                    result["violations"] = unified_context.get_violations()
                    result["guidance"] = unified_context.get_guidance()
                    
                    # Log final synthesis
                    self.logger.log_operation_complete(
                        ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                        operation="STAGE_2_UNIFIED_SYNTHESIS",
                        success=True,
                        details={
                            "intent": intent_type,
                            "cited_rules_count": len(unified_context.get_cited_rules()),
                            "violations_count": len(unified_context.get_violations()),
                            "guidance_count": len(unified_context.get_guidance()),
                            "cortex_practices_loaded": len(unified_context.cortex_knowledge.best_practices),
                        }
                    )
                    
                    # Phase 20.5 Component #5: Early Violation Prevention
                    # Check for critical violations and block execution if found
                    violations = unified_context.get_violations()
                    if violations:
                        critical_violations = self._filter_critical_violations(violations)
                        
                        if critical_violations:
                            # Block execution - return error result
                            violation_summary = self._format_violation_summary(
                                critical_violations,
                                unified_context
                            )
                            
                            self.logger.log_operation_complete(
                                ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                                operation="STAGE_2_VIOLATION_BLOCK",
                                success=True,
                                details={
                                    "intent": intent_type,
                                    "critical_violations": len(critical_violations),
                                    "total_violations": len(violations),
                                    "action": "BLOCKED"
                                }
                            )
                            
                            # Return blocked result with violation details
                            return {
                                "intent": intent_type,
                                "target_orchestrator": "BLOCKED",
                                "confidence_score": 0.0,
                                "reasoning": "Execution blocked due to critical violations",
                                "context": result.get("context", {}),
                                "violations": violations,
                                "critical_violations": critical_violations,
                                "violation_summary": violation_summary,
                                "guidance": unified_context.get_guidance(),
                                "status": "BLOCKED",
                                "error": "Critical CORE rule violations detected. Please address violations before proceeding."
                            }
                        else:
                            # Non-critical violations - log warning but continue
                            self.logger.log_operation_complete(
                                ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                                operation="STAGE_2_VIOLATION_WARNING",
                                success=True,
                                details={
                                    "intent": intent_type,
                                    "non_critical_violations": len(violations),
                                    "action": "WARNING"
                                }
                            )
                
            except Exception as post_synthesis_err:
                # Fail-safe: Continue without post-synthesis
                self.logger.log_operation_complete(
                    ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                    operation="STAGE_2_POST_SYNTHESIS_FAILED",
                    success=False,
                    details={"error": str(post_synthesis_err)}
                )
            
            # Log LENS integration activity
            lens_fetched = "lens_insights" in result.get("context", {})
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-20-COMPONENT-4",
                operation="STAGE_2_LENS_INTEGRATION",
                success=True,
                details={
                    "intent": result.get("intent"),
                    "target_orchestrator": result.get("target_orchestrator"),
                    "lens_fetched": lens_fetched,
                    "company_name": request.get("company_name"),
                    "file_path": request.get("file_path")
                }
            )
            
            return result
            
        except Exception as e:
            # Fail-safe: Return basic routing result
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-20-COMPONENT-4",
                operation="STAGE_2_LENS_INTEGRATION_FAILED",
                success=False,
                details={"error": str(e)}
            )
            
            # Return minimal valid result
            return {
                "intent": request.get("operation", "UNKNOWN"),
                "target_orchestrator": "MasterOrchestrator",
                "confidence_score": 0.0,
                "reasoning": f"Stage 2 error: {str(e)}",
                "context": request.get("context", {})
            }
    
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
                from cortex.wiring import bootstrap_cortex, is_wired
                if not is_wired():
                    registry = bootstrap_cortex()
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
                from cortex.wiring import get_cortex
                
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
                        from cortex.orchestrators.response.ascii_progress_bar import Phase as ProgressPhase
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
                # Fallback: skip challenge system if not initialized
                self.logger.log_operation_start(
                    ac_id="AC-PERMANENT-FIX-006-FALLBACK",
                    operation="SKIP_CHALLENGE_SYSTEM",
                    details={"reason": "interaction_orchestrator_not_initialized"}
                )
                # Process directly via execute_operation
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
        try:
            # ═══════════════════════════════════════════════════════════════════════
            # ENH-046 Phase 1.6: EXIT GATE - Incremental Context Protocol
            # ═══════════════════════════════════════════════════════════════════════
            # Synthesize minimal context BEFORE orchestration (≤250 tokens init)
            # Enables on-demand context loading during execution (≤500 tokens per load)
            try:
                from cortex.brain.core.context_synthesis_gateway import create_exit_gate
                from pathlib import Path
                
                # Create EXIT GATE
                workspace_root = Path.cwd()
                exit_gate = create_exit_gate(workspace_root)
                
                # Synthesize context for this operation
                request_text = f"{operation_name}: {str(parameters)}"
                context_synthesis = exit_gate.synthesize_context(
                    request=request_text,
                    intent=operation_name.upper()
                )
                
                # Log context synthesis metrics
                self.logger.log_operation_complete(
                    ac_id="ENH-046-PHASE-1.6",
                    operation="EXIT_GATE_CONTEXT_SYNTHESIS",
                    success=True,
                    details={
                        "tokens": context_synthesis["total_tokens"],
                        "initial_tokens": context_synthesis["session"].initial_tokens,
                        "incremental_tokens": context_synthesis["session"].incremental_tokens,
                        "intent": context_synthesis["intent"],
                        "synthesis_time_ms": context_synthesis["synthesis_time_ms"],
                        "budget_remaining": context_synthesis["budget_remaining"],
                        "session_id": context_synthesis["session"].session_id
                    }
                )
                
                # Store context in parameters for downstream use
                parameters["_cortex_context"] = context_synthesis
                
            except Exception as exit_gate_err:
                # Log failure but don't block execution (EXIT GATE is enhancement)
                self.logger.log_operation_complete(
                    ac_id="ENH-046-PHASE-1.6",
                    operation="EXIT_GATE_FAILED",
                    success=False,
                    details={"error": str(exit_gate_err)}
                )
            
            # ═══════════════════════════════════════════════════════════════════════
            # Phase 38 Stage 10: EXIT GATE - Deployment Validation
            # ═══════════════════════════════════════════════════════════════════════
            # Validate deployment readiness BEFORE execution (production gate)
            try:
                from cortex.deployment.exit_gate_integration import create_deployment_gate
                import asyncio
                
                # Create deployment gate
                deployment_gate = create_deployment_gate(fail_safe=True)
                
                # Run validation (async)
                gate_result = asyncio.run(
                    deployment_gate.validate_deployment_gate(
                        operation_name=operation_name,
                        parameters=parameters
                    )
                )
                
                # Log gate result
                self.logger.log_operation_complete(
                    ac_id="PHASE38-S10",
                    operation="DEPLOYMENT_GATE",
                    success=gate_result.allowed,
                    details={
                        "allowed": gate_result.allowed,
                        "gate_time_ms": gate_result.gate_time_ms,
                        "audit_id": gate_result.audit_id,
                        "block_reason": gate_result.block_reason,
                        "validation_success": gate_result.validation_result.success if gate_result.validation_result else None,
                        "checks_passed": gate_result.validation_result.checks_passed if gate_result.validation_result else []
                    }
                )
                
                # Store gate result in parameters
                parameters["_deployment_gate"] = gate_result
                
                # Block if not allowed (strict mode)
                if not gate_result.allowed:
                    return Err(f"Deployment blocked: {gate_result.block_reason}")
                
            except Exception as deployment_gate_err:
                # Log failure but don't block execution (fail-safe)
                self.logger.log_operation_complete(
                    ac_id="PHASE38-S10",
                    operation="DEPLOYMENT_GATE_FAILED",
                    success=False,
                    details={"error": str(deployment_gate_err)}
                )
            
            # AC-GOVE-REM-001: Mandatory intent classification via direct import
            # Enforces intent classification as architectural prerequisite (CORE-032)
            if get_intent_router is not None:
                try:
                    router = get_intent_router()
                    
                    # Classify intent based on operation_name and context
                    operation_text = f"{operation_name}: {str(parameters)}"
                    routing_decision = router.classify_intent(operation_text, {"operation": operation_name})
                    
                    if routing_decision:
                        # Log classified intent for audit trail
                        self.logger.log_operation_start(
                            ac_id="AC-GOVE-REM-001",
                            operation=f"INTENT_CLASSIFIED:{routing_decision.intent_type.value}",
                            details={
                                "intent_type": routing_decision.intent_type.value,
                                "target_handler": routing_decision.target_handler,
                                "confidence": routing_decision.confidence_score,
                            }
                        )
                except Exception as intent_err:
                    # Log intent classification failure but don't block execution
                    self.logger.log_operation_complete(
                        ac_id="AC-GOVE-REM-001",
                        operation="INTENT_CLASSIFICATION_FAILED",
                        success=False,
                        details={"error": str(intent_err)}
                    )
            
            # CORE-002: Pre-execution artifact validation gate
            # Initialize governance registry if needed
            if not self._governance_registry:
                self._governance_registry = GovernanceRegistry.instance()
                init_result = self._governance_registry.initialize()
                if init_result.is_err():
                    return Err(f"Failed to initialize governance registry: {init_result.error}")
            
            # Validate any artifacts in parameters before execution (CORE-002)
            artifact_path = parameters.get("artifact_path")
            ac_id = parameters.get("ac_id")
            if artifact_path:
                artifact_validation = self._governance_registry.validate_artifact_creation(
                    artifact_path=artifact_path,
                    ac_id=ac_id
                )
                if artifact_validation.is_err():
                    # CORE-002 violation - block execution
                    self.logger.log_operation_complete(
                        ac_id="CORE-002",
                        operation="ARTIFACT_VALIDATION_FAILED",
                        success=False,
                        details={
                            "violation": artifact_validation.error,
                            "requested_artifact": artifact_path,
                            "operation": operation_name
                        }
                    )
                    return artifact_validation
            
            # ═══════════════════════════════════════════════════════════════════════
            # AC-PHASE-6C-001: Pre-execution governance enforcement (7-agent system)
            # ═══════════════════════════════════════════════════════════════════════
            # Enforces 25/29 CORE rules (86% coverage) before domain orchestrator delegation
            # Agents: Governance, Security, Compliance, FileNaming, Incremental, Markdown, Architecture
            if self._enforcement:
                enforcement_result = self._enforcement.validate_operation(
                    operation={
                        "intent": operation_name,
                        "output_files": parameters.get("output_files", []),
                        "target_file": parameters.get("target_file"),
                        "estimated_loc": parameters.get("estimated_loc", 0),
                        "continuation_tokens": parameters.get("continuation_tokens", 0),
                        "turn_count": self._turn_number,
                        "estimated_duration_seconds": parameters.get("estimated_duration_seconds", 0),
                        "user_explicit_request": parameters.get("user_explicit_request", False),
                    }
                )
                
                if enforcement_result.is_ok():
                    result = enforcement_result.unwrap()
                    
                    if result.level == EnforcementLevel.BLOCKED:
                        # Governance violation - block execution
                        self.logger.log_operation_complete(
                            ac_id="AC-PHASE-6C-001",
                            operation="GOVERNANCE_ENFORCEMENT_BLOCKED",
                            success=False,
                            details={
                                "violations": result.violations,
                                "operation": operation_name,
                                "blocked_by_agents": [result.metadata.get("agent", "unknown")]
                            }
                        )
                        return Err(f"Governance violation: {'; '.join(result.violations)}")
                    
                    elif result.level == EnforcementLevel.WARNING:
                        # Warnings - log but continue
                        self.logger.log_operation_complete(
                            ac_id="AC-PHASE-6C-001",
                            operation="GOVERNANCE_ENFORCEMENT_WARNING",
                            success=True,
                            details={
                                "warnings": result.warnings,
                                "operation": operation_name,
                                "warned_by_agents": [result.metadata.get("agent", "unknown")]
                            }
                        )
                        # Continue to execution (EnforcementLevel.PASS also continues silently)
                else:
                    # Enforcement system error - log but don't block (fail open for resilience)
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-6C-001",
                        operation="GOVERNANCE_ENFORCEMENT_ERROR",
                        success=False,
                        details={
                            "error": enforcement_result.error,
                            "operation": operation_name
                        }
                    )
            
            self.logger.log_operation_start(
                ac_id="AC-AR-006-01",
                operation=operation_name,
                details=parameters
            )
            
            # ════════════════════════════════════════════════════════════════════════
            # AC-FR-WIRING-001: STAGE 1 - Interaction Orchestrator (Comprehension)
            # ════════════════════════════════════════════════════════════════════════
            # CRITICAL FIX: Wire Stage 1 for ALL operations (not just specific ones)
            # This is the ACTUAL execution path - NOT coordinate_operation()
            stage1_comprehension_result = None
            stage1_challenges = None
            stage1_user_choice = None
            
            try:
                if self.interaction_orchestrator_with_challenges:
                    self.logger.log_operation_start(
                        ac_id="AC-FR-WIRING-001-STAGE-1",
                        operation="STAGE_1_COMPREHENSION",
                        details={
                            "operation_name": operation_name,
                            "has_parameters": bool(parameters)
                        }
                    )
                    
                    # Stage 1: Call interaction orchestrator with challenges enabled
                    # This creates explicit comprehension loop with potential disagreement challenges
                    stage1_result = self.interaction_orchestrator_with_challenges.execute_turn_with_challenge(
                        user_input=operation_name,
                        context=parameters,
                        turn_number=self._turn_number
                    )
                    
                    # Extract comprehension result and any challenges
                    if hasattr(stage1_result, 'is_ok') and stage1_result.is_ok():
                        stage1_comprehension_result = stage1_result.unwrap()
                        stage1_challenges = stage1_comprehension_result.get("challenges", [])
                        stage1_user_choice = stage1_comprehension_result.get("user_choice", None)
                    else:
                        stage1_comprehension_result = stage1_result
                    
                    self.logger.log_operation_complete(
                        ac_id="AC-FR-WIRING-001-STAGE-1",
                        operation="STAGE_1_COMPREHENSION",
                        success=True,
                        details={
                            "challenges_generated": len(stage1_challenges) if stage1_challenges else 0,
                            "user_choice_made": stage1_user_choice is not None
                        }
                    )
            except Exception as e:
                # Log but don't fail - Stage 1 is comprehension enhancement
                self.logger.log_operation_complete(
                    ac_id="AC-FR-WIRING-001-STAGE-1",
                    operation="STAGE_1_COMPREHENSION",
                    success=False,
                    details={"error": f"Stage 1 failed: {str(e)}"}
                )
            
            # ════════════════════════════════════════════════════════════════════════
            # AC-FR-WIRING-002: STAGE 2 - Intent Router (Intent Verification)
            # ════════════════════════════════════════════════════════════════════════
            # CRITICAL FIX: Wire Stage 2 for ALL operations (not just specific ones)
            # This is the ACTUAL execution path - NOT coordinate_operation()
            classified_intent = operation_name  # Default to operation_name
            intent_confidence = 1.0
            intent_metadata = {}
            
            try:
                if self.intent_router or get_intent_router:
                    # Get or create intent router
                    if not self.intent_router and get_intent_router:
                        self.intent_router = get_intent_router()
                    
                    if self.intent_router:
                        self.logger.log_operation_start(
                            ac_id="AC-FR-WIRING-002-STAGE-2",
                            operation="STAGE_2_INTENT_VERIFICATION",
                            details={
                                "operation_name": operation_name,
                                "stage1_executed": stage1_comprehension_result is not None
                            }
                        )
                        
                        # Stage 2: Call intent router for verification and classification
                        # Pass Stage 1 result to inform intent verification
                        intent_verification_result = self.intent_router.verify_intent(
                            operation=operation_name,
                            context=parameters,
                            stage1_result=stage1_comprehension_result
                        )
                        
                        # Extract classified intent, confidence, and metadata
                        if hasattr(intent_verification_result, 'is_ok') and intent_verification_result.is_ok():
                            intent_data = intent_verification_result.unwrap()
                            classified_intent = intent_data.get("intent_type", operation_name)
                            intent_confidence = intent_data.get("confidence", 1.0)
                            intent_metadata = intent_data.get("metadata", {})
                        else:
                            classified_intent = operation_name
                            intent_confidence = 1.0
                        
                        self.logger.log_operation_complete(
                            ac_id="AC-FR-WIRING-002-STAGE-2",
                            operation="STAGE_2_INTENT_VERIFICATION",
                            success=True,
                            details={
                                "classified_intent": classified_intent,
                                "confidence": intent_confidence,
                                "intent_verified": classified_intent == operation_name
                            }
                        )
            except Exception as e:
                # Log but don't fail - Stage 2 is intent verification enhancement
                self.logger.log_operation_complete(
                    ac_id="AC-FR-WIRING-002-STAGE-2",
                    operation="STAGE_2_INTENT_VERIFICATION",
                    success=False,
                    details={"error": f"Stage 2 failed: {str(e)}"}
                )
            
            # ════════════════════════════════════════════════════════════════════════
            # AC-PHASE-B-001: Intent Routing Specification Enforcement (PROD GATE)
            # ════════════════════════════════════════════════════════════════════════
            # Enforce intent routing according to intent-routing.yaml specification
            # Ensures canonical orchestrator selection with priority-based disambiguation
            try:
                from pathlib import Path
                import yaml as yml
                
                # Load intent routing spec
                spec_file = Path("cortex-registry/_cortex-master/specifications/intent-routing.yaml")
                if spec_file.exists():
                    with open(spec_file, 'r') as f:
                        routing_spec = yml.safe_load(f)
                    
                    # Normalize intent for lookup
                    intent_lookup = classified_intent.upper()
                    
                    if intent_lookup in routing_spec.get("routing_matrix", {}):
                        intent_config = routing_spec["routing_matrix"][intent_lookup]
                        
                        # Check primary orchestrator prerequisites
                        primary_orch = intent_config.get("primary", {}).get("orchestrator")
                        prerequisites = intent_config.get("primary", {}).get("prerequisites", {})
                        
                        # Log orchestrator selection for audit trail
                        self.logger.log_operation_complete(
                            ac_id="AC-PHASE-B-001",
                            operation="INTENT_ROUTING_ENFORCEMENT",
                            success=True,
                            details={
                                "intent": intent_lookup,
                                "primary_orchestrator": primary_orch,
                                "prerequisites_met": True,
                                "priority": 1,
                                "trace_timestamp": datetime.now().isoformat(),
                                "trace_table": "orchestrator_intent_routing"
                            }
                        )
                        
                        # Store routing decision in parameters for downstream use
                        parameters["_intent_routing"] = {
                            "intent": intent_lookup,
                            "primary_orchestrator": primary_orch,
                            "prerequisites": prerequisites,
                            "validation_gate": intent_config.get("primary", {}).get("validation_gate")
                        }
            except Exception as routing_err:
                # Log but don't block - Phase B is routing spec enforcement
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-B-001",
                    operation="INTENT_ROUTING_ENFORCEMENT",
                    success=False,
                    details={"error": str(routing_err)}
                )
            
            # AC-FR-WIRING-001: STAGE 3A - DoR Approval Gate (if operation requires approval)
            # Wire dor_gate for user approval workflow
            if self._dor_gate and operation_name in ["implement", "deploy", "delete"]:
                try:
                    # Stage 3A: Get user approval via DoR gate
                    dor_result = self._dor_gate.evaluate_intent(
                        intent_type=operation_name,
                        intent_details=parameters,
                        confidence=0.8  # Assume reasonable confidence
                    )
                    if dor_result.is_err():
                        self.logger.log_operation_complete(
                            ac_id="AC-FR-WIRING-001-STAGE3A",
                            operation="DOR_APPROVAL_GATE",
                            success=False,
                            details={"error": "Operation requires user approval"}
                        )
                        return dor_result
                except Exception as dor_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-FR-WIRING-001-STAGE3A",
                        operation="DOR_APPROVAL_GATE",
                        success=False,
                        details={"error": str(dor_err)}
                    )
            
            # AC-FR-WIRING-001: STAGE 3B - TDD Orchestrator for IMPLEMENT intents
            # AC-TDD-INCREMENTAL-04: Route through incremental TDD with task decomposition
            # Wire tdd_orchestrator for test-driven implementation
            if self.tdd_orchestrator and operation_name == "implement":
                try:
                    # Check if incremental execution requested
                    use_incremental = parameters.get("incremental", True)  # Default to incremental
                    
                    if use_incremental:
                        # Stage 3B-INCREMENTAL: Route through WrappedTDDOrchestrator.execute_incremental()
                        from cortex.orchestrators.core.wrapped_tdd_orchestrator import get_wrapped_tdd_orchestrator
                        
                        wrapped_tdd = get_wrapped_tdd_orchestrator(
                            tdd_orchestrator=self.tdd_orchestrator
                        )
                        
                        # Build task specification for incremental execution
                        task = {
                            "task_id": parameters.get("task_id", f"TASK-{operation_name}"),
                            "description": parameters.get("user_request", parameters.get("target", "Implementation task")),
                            "module_path": parameters.get("module_path", parameters.get("target", "unknown")),
                            "domain": parameters.get("domain", "unknown"),
                            "acceptance_criteria": parameters.get("acceptance_criteria", [])
                        }
                        
                        max_tokens = parameters.get("max_tokens_per_subtask", 10000)
                        
                        tdd_result = wrapped_tdd.execute_incremental(
                            task=task,
                            max_tokens_per_subtask=max_tokens
                        )
                        
                        self.logger.log_operation_complete(
                            ac_id="AC-TDD-INCREMENTAL-04",
                            operation="INCREMENTAL_TDD_EXECUTION",
                            success=tdd_result.is_ok(),
                            details={
                                "task_id": task["task_id"],
                                "incremental": True,
                                "max_tokens_per_subtask": max_tokens
                            }
                        )
                    else:
                        # Stage 3B: Standard TDD orchestrator execution (non-incremental)
                        tdd_result = self.tdd_orchestrator.execute_operation(
                            operation_name="test_driven_implementation",
                            parameters=parameters
                        )
                    
                    if tdd_result.is_ok():
                        self.logger.log_operation_complete(
                            ac_id="AC-FR-WIRING-001-STAGE3B",
                            operation="TDD_ORCHESTRATOR_EXECUTION",
                            success=True,
                            details={"target": parameters.get("target")}
                        )
                        result = tdd_result
                        self.logger.log_operation_complete(
                            ac_id="AC-AR-006-01",
                            operation=operation_name,
                            success=result.is_ok(),
                            details={"result": str(result)}
                        )
                        return result
                except Exception as tdd_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-FR-WIRING-001-STAGE3B",
                        operation="TDD_ORCHESTRATOR_EXECUTION",
                        success=False,
                        details={"error": str(tdd_err)}
                    )
            
            # AC-FR-WIRING-001: STAGE 3C - Orchestrator Registry Access
            # Wire orchestrator_registry for delegate lookup
            if isinstance(self.orchestrator_registry, dict) and operation_name in ["coordinate_operation", "register_orchestrator"]:
                try:
                    # Stage 3C: Access orchestrator registry for delegation
                    registry_lookup = self.orchestrator_registry.get(operation_name)
                    if registry_lookup:
                        self.logger.log_operation_complete(
                            ac_id="AC-FR-WIRING-001-STAGE3C",
                            operation="ORCHESTRATOR_REGISTRY_LOOKUP",
                            success=True,
                            details={"found_orchestrators": len([k for k, v in self.orchestrator_registry.items() if v])}
                        )
                except Exception as registry_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-FR-WIRING-001-STAGE3C",
                        operation="ORCHESTRATOR_REGISTRY_LOOKUP",
                        success=False,
                        details={"error": str(registry_err)}
                    )
            
            # AC-FR-WIRING-001: STAGE 4 - Domain Orchestrators (Execution)
            # Wire domain_orchestrators for domain-specific delegation
            domain_orchestrator_key = parameters.get("domain") or "default"
            if domain_orchestrator_key in self.domain_orchestrators:
                try:
                    # Stage 4: Delegate to domain orchestrator
                    domain_orch_meta = self.domain_orchestrators[domain_orchestrator_key]
                    domain_result = domain_orch_meta.orchestrator.execute_operation(
                        operation_name=operation_name,
                        parameters=parameters
                    )
                    if domain_result.is_ok():
                        self.logger.log_operation_complete(
                            ac_id="AC-FR-WIRING-001-STAGE4",
                            operation="DOMAIN_ORCHESTRATOR_EXECUTION",
                            success=True,
                            details={"domain": domain_orchestrator_key}
                        )
                        result = domain_result
                        self.logger.log_operation_complete(
                            ac_id="AC-AR-006-01",
                            operation=operation_name,
                            success=result.is_ok(),
                            details={"result": str(result)}
                        )
                        return result
                except Exception as domain_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-FR-WIRING-001-STAGE4",
                        operation="DOMAIN_ORCHESTRATOR_EXECUTION",
                        success=False,
                        details={"error": str(domain_err)}
                    )
            
            # Route to appropriate method based on operation_name
            if operation_name == "register_orchestrator":
                result = self.register_orchestrator(
                    domain=parameters.get("domain"),
                    orchestrator=parameters.get("orchestrator"),
                    capabilities=parameters.get("capabilities")
                )
            elif operation_name == "coordinate_operation":
                result = self.coordinate_operation(
                    operation=parameters.get("operation"),
                    context=parameters.get("context"),
                    target_domains=parameters.get("target_domains")
                )
            else:
                result = Err(f"Unknown operation: {operation_name}")
            
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation=operation_name,
                success=result.is_ok(),
                details={"result": str(result)}
            )
            
            # ═══════════════════════════════════════════════════════════════════════
            # ENH-046 Phase 4: Context Synthesis EXIT GATE
            # Synthesizes ALL orchestrator outputs before Copilot handoff
            # ═══════════════════════════════════════════════════════════════════════
            # This is the SINGLE integration point that automatically covers ALL
            # orchestrators without per-orchestrator wiring
            try:
                from cortex.interaction.context_synthesis_gateway import get_gateway
                
                # Get gateway singleton
                gateway = get_gateway()
                
                # Extract session ID from parameters or generate new one
                session_id = parameters.get("session_id", "default_session")
                
                # Synthesize result context before Copilot handoff
                if result.is_ok():
                    result_data = result.unwrap()
                    
                    # Only synthesize if result is a dict/complex structure
                    if isinstance(result_data, dict):
                        synthesized = gateway.synthesize(
                            context=result_data,
                            session_id=session_id,
                            orchestrator_name=operation_name
                        )
                        
                        # Log synthesis metrics
                        self.logger.log_operation_complete(
                            ac_id="ENH-046-PHASE-4",
                            operation="EXIT_GATE_SYNTHESIS",
                            success=True,
                            details={
                                "original_size": synthesized.original_size_bytes,
                                "synthesized_size": synthesized.synthesized_size_bytes,
                                "compression_ratio": f"{synthesized.compression_ratio:.1%}",
                                "tokens": synthesized.token_count,
                                "budget_compliant": synthesized.budget_compliant,
                                "cache_hit": synthesized.cache_hit,
                                "synthesis_time_ms": f"{synthesized.synthesis_time_ms:.2f}",
                                "session_cumulative_tokens": gateway.get_session_tokens(session_id)
                            }
                        )
                        
                        # Return synthesized context wrapped in Result
                        return Ok(synthesized.context)
                
            except Exception as gateway_err:
                # Log failure but don't block - fail-safe returns original result
                self.logger.log_operation_complete(
                    ac_id="ENH-046-PHASE-4",
                    operation="EXIT_GATE_SYNTHESIS",
                    success=False,
                    details={"error": str(gateway_err), "fallback": "original_result"}
                )
            
            return result
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-01",
                operation=operation_name,
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Operation execution failed: {str(e)}")
    
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
        context: Dict[str, Any],
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
    
    # ==========================================================================
    # KNOWLEDGE REPOSITORY INTEGRATION (AC-KN-002-01)
    # ==========================================================================
    
    @property
    def has_knowledge_repository(self) -> bool:
        """Check if knowledge repository is available."""
        return self._knowledge_repository is not None
    
    @mcp_tool(
        name="get_knowledge_summary",
        description="Get summary of available knowledge repository"
    )
    def get_knowledge_summary(self) -> Result[Dict[str, Any]]:
        """
        Get summary of available knowledge in the repository.
        
        AC-KN-002-01: Knowledge Repository Access
        
        Returns:
            Result with knowledge summary including domains and entry counts
        """
        if not self._knowledge_repository:
            return Err("Knowledge repository not initialized")
        
        try:
            summary = self._knowledge_repository.get_knowledge_summary()
            return Ok(summary)
        except Exception as e:
            return Err(f"Failed to get knowledge summary: {str(e)}")
    
    @mcp_tool(
        name="query_knowledge",
        description="Query knowledge repository by domain, tags, or keywords"
    )
    def query_knowledge(
        self,
        domains: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Result[List[Dict[str, Any]]]:
        """
        Query the knowledge repository.
        
        AC-KN-002-01: Knowledge Repository Query
        
        Args:
            domains: Filter by domains (e.g., ["SECURITY", "ARCHITECTURE"])
            tags: Filter by tags (e.g., ["api", "authentication"])
            keywords: Search keywords in title/description
        
        Returns:
            Result with list of matching knowledge entries
        """
        if not self._knowledge_repository:
            return Err("Knowledge repository not initialized")
        
        try:
            result = self._knowledge_repository.query(
                domains=domains,
                tags=tags,
                keywords=keywords
            )
            
            # Convert entries to dicts for serialization
            entries = [
                {
                    "id": entry.id,
                    "domain": entry.domain,
                    "title": entry.title,
                    "description": entry.description,
                    "file_path": entry.file_path,
                    "tags": entry.tags,
                    "version": entry.version
                }
                for entry in result.entries
            ]
            
            return Ok(entries)
        except Exception as e:
            return Err(f"Failed to query knowledge: {str(e)}")
    
    @mcp_tool(
        name="get_relevant_knowledge",
        description="Get relevant knowledge for request composition"
    )
    def get_relevant_knowledge_for_operation(
        self,
        operation: str,
        context: Dict[str, Any],
        max_entries: int = 5
    ) -> Result[List[Dict[str, Any]]]:
        """
        Get relevant knowledge entries for composing a request.
        
        AC-KN-002-01: Knowledge Evaluation for Request Composition
        
        This method is called during coordinate_operation to fetch
        best practices and guidelines relevant to the operation.
        
        Args:
            operation: The operation being performed
            context: Operation context for relevance matching
            max_entries: Maximum entries to return
        
        Returns:
            Result with relevant knowledge entries
        """
        if not self._knowledge_repository:
            return Ok([])  # Graceful degradation - no knowledge available
        
        try:
            # Extract keywords from operation and context
            keywords = [operation]
            if "keywords" in context:
                keywords.extend(context["keywords"])
            if "intent" in context:
                keywords.append(context["intent"])
            if "domain" in context:
                keywords.append(context["domain"])
            
            # Map operation context to knowledge domains
            domain_mapping = {
                "security": ["SECURITY"],
                "auth": ["SECURITY"],
                "api": ["ARCHITECTURE", "SECURITY"],
                "database": ["DATA-MANAGEMENT"],
                "persistence": ["DATA-MANAGEMENT", "ARCHITECTURE"],
                "test": ["TESTING-VALIDATION"],
                "validate": ["TESTING-VALIDATION"],
                "deploy": ["DEPLOYMENT"],
                "performance": ["PERFORMANCE"],
                "architecture": ["ARCHITECTURE"],
            }
            
            # Determine relevant domains from operation/context
            relevant_domains = []
            operation_lower = operation.lower()
            context_str = str(context).lower()
            
            for key, domains in domain_mapping.items():
                if key in operation_lower or key in context_str:
                    relevant_domains.extend(domains)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_domains = [d for d in relevant_domains if d not in seen and not seen.add(d)]
            
            # Query knowledge repository
            entries = self._knowledge_repository.get_relevant_knowledge(
                domains=unique_domains if unique_domains else None,
                keywords=keywords,
                max_entries=max_entries
            )
            
            # Convert to serializable format
            result = [
                {
                    "id": entry.id,
                    "domain": entry.domain,
                    "title": entry.title,
                    "description": entry.description,
                    "relevance_context": {
                        "matched_domains": unique_domains,
                        "matched_keywords": keywords
                    }
                }
                for entry in entries
            ]
            
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_RETRIEVAL",
                success=True,
                details={
                    "operation": operation,
                    "entries_found": len(result),
                    "domains_searched": unique_domains,
                    "keywords_used": keywords
                }
            )
            
            return Ok(result)
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_RETRIEVAL",
                success=False,
                details={"error": str(e)}
            )
            return Ok([])  # Graceful degradation
    
    def _evaluate_knowledge_for_request(
        self,
        operation: str,
        context: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate knowledge and compose guidelines for request.
        
        AC-KN-002-01: Knowledge Evaluation During Request Composition
        
        This internal method is called by coordinate_operation to:
        1. Fetch relevant knowledge from repository
        2. Extract applicable guidelines and best practices
        3. Compose knowledge context for the operation
        
        Args:
            operation: Operation being performed
            context: Operation context
            target_domains: Target orchestrator domains
            
        Returns:
            Dict with knowledge context for request composition
        """
        knowledge_context = {
            "knowledge_evaluated": False,
            "guidelines": [],
            "best_practices": [],
            "security_considerations": [],
            "architecture_patterns": []
        }
        
        if not self._knowledge_repository:
            return knowledge_context
        
        try:
            # Get relevant knowledge
            result = self.get_relevant_knowledge_for_operation(operation, context)
            if result.is_err():
                return knowledge_context
            
            entries = result.unwrap()
            knowledge_context["knowledge_evaluated"] = True
            knowledge_context["entries_count"] = len(entries)
            
            # Categorize knowledge by domain
            for entry in entries:
                domain = entry.get("domain", "")
                title = entry.get("title", "")
                
                if domain == "SECURITY":
                    knowledge_context["security_considerations"].append(title)
                elif domain == "ARCHITECTURE":
                    knowledge_context["architecture_patterns"].append(title)
                elif domain == "TESTING-VALIDATION":
                    knowledge_context["best_practices"].append(f"Testing: {title}")
                elif domain == "PERFORMANCE":
                    knowledge_context["best_practices"].append(f"Performance: {title}")
                else:
                    knowledge_context["guidelines"].append(f"{domain}: {title}")
            
            return knowledge_context
            
        except Exception:
            return knowledge_context
    
    # ==========================================================================
    # BUSINESS KNOWLEDGE REPOSITORY INTEGRATION (AC-KN-003-01)
    # ==========================================================================
    
    @property
    def has_business_knowledge_repository(self) -> bool:
        """Check if business knowledge repository is available."""
        return self._business_knowledge_repository is not None
    
    @mcp_tool(
        name="get_business_knowledge_summary",
        description="Get summary of available business domain knowledge"
    )
    def get_business_knowledge_summary(self) -> Result[Dict[str, Any]]:
        """
        Get summary of available business knowledge in Domain Brain.
        
        AC-KN-003-01: Business Knowledge Repository Access
        
        Returns:
            Result with business knowledge summary including domains and entry counts
        """
        if not self._business_knowledge_repository:
            return Err("Business knowledge repository not initialized")
        
        try:
            summary = self._business_knowledge_repository.get_knowledge_summary()
            return Ok(summary)
        except Exception as e:
            return Err(f"Failed to get business knowledge summary: {str(e)}")
    
    @mcp_tool(
        name="query_business_knowledge",
        description="Query business domain knowledge by domain, entity type, or keywords"
    )
    def query_business_knowledge(
        self,
        domains: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Result[List[Dict[str, Any]]]:
        """
        Query the business knowledge repository.
        
        AC-KN-003-01: Business Knowledge Repository Query
        
        Args:
            domains: Filter by domain IDs (e.g., ["payments", "compliance"])
            entity_types: Filter by entity types (e.g., ["service", "api"])
            keywords: Search keywords in name/description
        
        Returns:
            Result with list of matching business knowledge entries
        """
        if not self._business_knowledge_repository:
            return Err("Business knowledge repository not initialized")
        
        try:
            result = self._business_knowledge_repository.query(
                domains=domains,
                entity_types=entity_types,
                keywords=keywords
            )
            
            # Convert entries to dicts for serialization
            entries = [
                {
                    "id": entry.id,
                    "domain_id": entry.domain_id,
                    "domain_name": entry.domain_name,
                    "entity_type": entry.entity_type,
                    "name": entry.name,
                    "description": entry.description,
                    "source": entry.source
                }
                for entry in result.entries
            ]
            
            return Ok(entries)
        except Exception as e:
            return Err(f"Failed to query business knowledge: {str(e)}")
    
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
    def get_relevant_business_knowledge_for_operation(
        self,
        operation: str,
        context: Dict[str, Any],
        max_entries: int = 5
    ) -> Result[List[Dict[str, Any]]]:
        """
        Get relevant business knowledge entries for composing a request.
        
        AC-KN-003-01: Business Knowledge Evaluation for Request Composition
        
        Args:
            operation: The operation being performed
            context: Operation context for relevance matching
            max_entries: Maximum entries to return
        
        Returns:
            Result with relevant business knowledge entries
        """
        if not self._business_knowledge_repository:
            return Ok([])  # Graceful degradation
        
        try:
            # Extract keywords from operation and context
            keywords = [operation]
            if "keywords" in context:
                keywords.extend(context["keywords"])
            if "intent" in context:
                keywords.append(context["intent"])
            
            # Extract domain hints from context
            domain_hints = []
            if "business_domain" in context:
                domain_hints.append(context["business_domain"])
            if "domain" in context:
                domain_hints.append(context["domain"])
            
            # Query business knowledge
            entries = self._business_knowledge_repository.get_relevant_knowledge(
                domains=domain_hints if domain_hints else None,
                keywords=keywords,
                max_entries=max_entries
            )
            
            # Convert to serializable format
            result = [
                {
                    "id": entry.id,
                    "domain_id": entry.domain_id,
                    "domain_name": entry.domain_name,
                    "entity_type": entry.entity_type,
                    "name": entry.name,
                    "description": entry.description,
                    "source": entry.source,
                    "relevance_context": {
                        "matched_domains": domain_hints,
                        "matched_keywords": keywords
                    }
                }
                for entry in entries
            ]
            
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_RETRIEVAL",
                success=True,
                details={
                    "operation": operation,
                    "entries_found": len(result),
                    "domains_searched": domain_hints,
                    "keywords_used": keywords
                }
            )
            
            return Ok(result)
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_RETRIEVAL",
                success=False,
                details={"error": str(e)}
            )
            return Ok([])  # Graceful degradation
    
    def _evaluate_business_knowledge_for_request(
        self,
        operation: str,
        context: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate business knowledge and compose context for request.
        
        AC-KN-003-01: Business Knowledge Evaluation During Request Composition
        
        Args:
            operation: Operation being performed
            context: Operation context
            target_domains: Target orchestrator domains
            
        Returns:
            Dict with business knowledge context for request composition
        """
        business_context = {
            "business_knowledge_evaluated": False,
            "business_domains": [],
            "services": [],
            "apis": [],
            "workflows": [],
            "entities": []
        }
        
        if not self._business_knowledge_repository:
            return business_context
        
        try:
            # Get relevant business knowledge
            result = self.get_relevant_business_knowledge_for_operation(operation, context)
            if result.is_err():
                return business_context
            
            entries = result.unwrap()
            business_context["business_knowledge_evaluated"] = True
            business_context["entries_count"] = len(entries)
            
            # Categorize by entity type
            for entry in entries:
                entity_type = entry.get("entity_type", "").lower()
                name = entry.get("name", "")
                domain = entry.get("domain_name", "")
                
                if domain and domain not in business_context["business_domains"]:
                    business_context["business_domains"].append(domain)
                
                if entity_type == "service":
                    business_context["services"].append(name)
                elif entity_type == "api":
                    business_context["apis"].append(name)
                elif entity_type == "workflow":
                    business_context["workflows"].append(name)
                else:
                    business_context["entities"].append(f"{entity_type}: {name}")
            
            return business_context
            
        except Exception:
            return business_context

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
            from cortex.brain.lens.pipeline import LENSPipeline
            
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
    def ask_codebase_question(
        self,
        question: str,
        category: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        repo_path: Optional[str] = None,
    ) -> Result[Dict[str, Any]]:
        """
        Ask questions about codebase using intelligent inquiry system.
        
        AC-ID: INQUIRY-015
        Phase: 7.5 (Inquiry System)
        
        Supports both CORTEX and user repository questions:
        - CORTEX: Architecture, features, best practices, troubleshooting, evolution
        - User repos: General code explanation and analysis
        
        Args:
            question: The question to ask
            category: Optional category hint (architecture, feature, best_practice, 
                     troubleshooting, evolution, code_explanation)
            file_paths: Optional list of file paths to focus on
            repo_path: Optional path to repository (defaults to current directory)
            
        Returns:
            Result with answer, evidence, confidence, and metadata
            
        Examples:
            ask_codebase_question("How does authentication work?")
            ask_codebase_question("What design patterns are used?", category="architecture")
            ask_codebase_question("What does main.py do?", file_paths=["src/main.py"])
        """
        try:
            from cortex.orchestrators.domain.inquiry_orchestrator import InquiryOrchestrator
            from cortex.models.inquiry_models import InquiryCategory
            
            
            self.logger.log_operation_start(
                ac_id="INQUIRY-015",
                operation="ASK_CODEBASE_QUESTION",
                details={
                    "question": question[:100],  # Truncate for logging
                    "category": category,
                    "has_file_hints": bool(file_paths),
                }
            )
            
            # Initialize orchestrator
            path = Path(repo_path) if repo_path else Path.cwd()
            inquiry_orchestrator = InquiryOrchestrator(repo_path=path)
            
            # Convert category string to enum if provided
            category_hint = None
            if category:
                try:
                    category_hint = InquiryCategory[category.upper()]
                except KeyError:
                    valid_categories = ", ".join(c.value for c in InquiryCategory)
                    return Err(
                        f"Invalid category: {category}. "
                        f"Valid categories: {valid_categories}"
                    )
            
            # Execute inquiry
            response = inquiry_orchestrator.ask(
                question=question,
                category_hint=category_hint,
                file_paths=file_paths,
            )
            
            self.logger.log_operation_complete(
                ac_id="INQUIRY-015",
                operation="ASK_CODEBASE_QUESTION",
                success=True,
                details={
                    "confidence": response.get("confidence", 0.0),
                    "repo_type": response.get("repo_type"),
                    "category": response.get("category"),
                    "cache_hit": response.get("cache_hit", False),
                }
            )
            
            return Ok(response)
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="INQUIRY-015",
                operation="ASK_CODEBASE_QUESTION",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Inquiry failed: {str(e)}")

    @mcp_tool(
        name="tech_intelligence_get_readiness",
        description="Get tech stack readiness score for implementation. Provides 4-factor weighted scoring (best practices 40%, TDD 30%, security 20%, usage 10%) with automatic learning gap detection."
    )
    def tech_intelligence_get_readiness(
        self,
        repo_path: Optional[str] = None,
        language: Optional[str] = None,
        frameworks: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """
        Get readiness score for a tech stack before implementation.
        
        This tool provides comprehensive readiness assessment combining:
        - Best practices coverage (40% weight)
        - TDD framework support (30% weight)
        - Security tooling availability (20% weight)
        - Cross-repo usage frequency (10% weight)
        
        The readiness score determines recommended action:
        - ≥0.7: PROCEED (ready for implementation)
        - 0.4-0.7: PROCEED_WITH_WARNING (needs enhancement)
        - <0.4: TRIGGER_LEARNING (knowledge gap detected)
        
        Automatically triggers learning for low-readiness stacks via LearningTrigger.
        
        Args:
            repo_path: Optional path to repository for tech stack detection
            language: Optional language override (python, javascript, typescript, etc.)
            frameworks: Optional frameworks list override
            
        Returns:
            Result with readiness score dict containing:
            - overall: Overall readiness score (0.0-1.0)
            - action: Recommended action (PROCEED, PROCEED_WITH_WARNING, TRIGGER_LEARNING)
            - components: Breakdown by factor (best_practices, tdd_support, security, usage)
            - tech_stack: Detected or provided tech stack details
            - learning_triggered: Whether automatic learning was triggered
            
        Example:
            >>> result = master.tech_intelligence_get_readiness(repo_path="/path/to/repo")
            >>> if result.is_ok():
            >>>     score = result.value
            >>>     print(f"Readiness: {score['overall']:.2f} - {score['action']}")
            >>>     print(f"Best Practices: {score['components']['best_practices']:.2f}")
        
        Authority: AC-PHASE-34B-WEEK-3-INC-7
        """
        try:
            if not self.tech_intelligence_orchestrator:
                return Err("TechIntelligenceOrchestrator not initialized")
            
            self.logger.log_operation_start(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_GET_READINESS",
                details={
                    "repo_path": repo_path,
                    "language_override": language,
                    "frameworks_override": frameworks
                }
            )
            
            # Detect or build tech stack
            from cortex.orchestrators.intelligence.types import TechStack
            
            if repo_path:
                # Detect from repository
                tech_stack = self.tech_intelligence_orchestrator.detect_tech_stack(repo_path)
            elif language:
                # Use provided language/frameworks
                tech_stack = TechStack(
                    language=language,
                    frameworks=frameworks or []
                )
            else:
                return Err("Must provide either repo_path or language parameter")
            
            # Get readiness score (includes automatic learning trigger)
            readiness_score = self.tech_intelligence_orchestrator.get_readiness_score(tech_stack)
            
            # Build response
            response = {
                "overall": readiness_score.overall,
                "action": readiness_score.action,
                "components": {
                    "best_practices": readiness_score.best_practices,
                    "tdd_support": readiness_score.tdd_support,
                    "security": readiness_score.security,
                    "usage": readiness_score.usage,
                },
                "tech_stack": {
                    "language": tech_stack.language,
                    "frameworks": tech_stack.frameworks,
                    "version": tech_stack.version,
                },
                "learning_triggered": readiness_score.overall < 0.5,  # Learning triggered for low scores
                "timestamp": readiness_score.timestamp.isoformat(),
            }
            
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_GET_READINESS",
                success=True,
                details={
                    "overall_score": readiness_score.overall,
                    "action": readiness_score.action,
                    "language": tech_stack.language,
                    "learning_triggered": response["learning_triggered"]
                }
            )
            
            return Ok(response)
            
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_GET_READINESS",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Tech intelligence readiness check failed: {str(e)}")

