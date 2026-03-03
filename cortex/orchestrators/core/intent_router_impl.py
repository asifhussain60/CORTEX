"""
Intent Router Orchestrator — Routes operations based on intent type.

Phase 103-b: Decomposed from 2,895L → ≤500L via 4 extracted mixin modules:
  - keyword_registry.py          — All IntentType keyword lists
  - lens_analysis_mixin.py       — LENS confidence boosts
  - registry_intelligence_mixin.py — Capability/governance registry logic
  - routing_core_mixin.py        — Core routing pipeline
  - smart_citations_mixin.py     — Rule citations + LENS auto-fetch

AC-PROD-001-02: Intent Router — basic structure and routing logic.
Resolves ISSUE-001: Intent Router missing (Master Stage 2 routing broken).

CORE Governance Rules Applied:
  - CORE-008: TDD (tests created first, RED → GREEN pattern)
  - CORE-011: Type hints mandatory on all functions
  - CORE-012: Google-style docstrings on all public methods
  - CORE-013: Specific exception handling (no bare except)
  - CORE-027: Audit trail logging (AC_START → AC_EXECUTE → AC_COMPLETE)
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from cortex.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.core.orchestrator_lookup import OrchestratorLookup
from cortex.orchestrators.core.routing_enforcement import RoutingEnforcementEngine
from cortex.orchestrators.core.intent_router import (
    WorkflowComplexityRouter,
    Intent as ComplexityIntent,
)
from cortex.orchestrators.core.intent_classifier import IntentClassifier as _IntentClassifier
from cortex.governance import GoldenHammerRules
from cortex.intelligence.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
)

# Phase 103-b mixins (extracted from this file)
from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
from cortex.orchestrators.core.intent_router.lens_analysis_mixin import LensAnalysisMixin
from cortex.orchestrators.core.intent_router.registry_intelligence_mixin import RegistryIntelligenceMixin
from cortex.orchestrators.core.intent_router.routing_core_mixin import RoutingCoreMixin
from cortex.orchestrators.core.intent_router.smart_citations_mixin import SmartCitationsMixin

# Optional dependencies (graceful degradation)
try:
    from cortex.intelligence.reasoning.strategy_selector import StrategySelector as _StrategySelector
    _routing_strategy_selector = _StrategySelector()
except ImportError:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "Optional cortex dependency unavailable: "
        "cortex.intelligence.reasoning.strategy_selector — feature degraded"
    )
    _routing_strategy_selector = None  # type: ignore[assignment]

try:
    from cortex.intelligence.learning.registry_intelligence_agent import (
        get_registry_intelligence_agent,
    )
except ImportError:
    get_registry_intelligence_agent = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Data models — kept in this file (public API, referenced by callers)
# ---------------------------------------------------------------------------

@dataclass
class RoutingDecision:  # noqa: CORE-035-scoped — domain-specific routing decision model
    """Represents a routing decision made by the IntentRouter.

    Attributes:
        intent_type: Detected operation intent (IMPLEMENT, FIX, REFACTOR, …)
        target_handler: Name of target handler/orchestrator.
        confidence_score: Confidence of routing decision (0.0–1.0).
        reasoning: Human-readable explanation of routing decision.
        metadata: Additional routing context metadata.
        timestamp: When routing decision was made.
        composite_intents: Detected secondary intents (AC-FUTURE-005).
        target_orchestrator: Actual orchestrator instance (Phase 8.2).
        fallback_orchestrators: Ranked alternative orchestrators (Phase 8.2).
        keyword_matches: Keywords that matched routing config (Phase 8.2).
        confidence_breakdown: Detailed confidence scoring (Phase 8.2).
    """

    intent_type: IntentType
    target_handler: str
    confidence_score: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    composite_intents: List[IntentType] = field(default_factory=list)
    target_orchestrator: Optional[IOrchestrator] = None
    fallback_orchestrators: List[IOrchestrator] = field(default_factory=list)
    keyword_matches: List[str] = field(default_factory=list)
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialise compatibility aliases after dataclass fields are set."""
        pass

    @property
    def confidence(self) -> float:
        """Alias for confidence_score — IntentRoutingResult API compatibility."""
        return self.confidence_score

    @property
    def primary_agent_id(self) -> Optional[str]:
        """Alias for target_handler — IntentRoutingResult API compatibility."""
        return self.target_handler or None


@dataclass
class RoutingContext:
    """Represents the full context for a routing decision.

    Attributes:
        operation: Operation name/identifier.
        description: Human-readable operation description.
        domain: Target domain (core, orchestrators, infrastructure, …).
        keywords: Keywords from operation description.
        urgency: Operation urgency level (low, medium, high, critical).
        user_intent: User's stated intent or goal.
        metadata: Additional context metadata.
    """

    operation: str
    description: Optional[str] = None
    domain: Optional[str] = None
    keywords: Optional[List[str]] = None
    urgency: str = "medium"
    user_intent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompositeIntentDetector:
    """Detects composite intents when a request spans multiple operation types.

    AC-FUTURE-005: Composite intent detection for multi-faceted requests.

    Patterns detected:
        1. AND patterns: "X and Y" or "X then Y"
        2. WITH patterns: "Implement with tests"
        3. SEQUENTIAL patterns: "Fix, then refactor"
        4. IMPLICIT patterns: "Fix bug" + "need tests"
    """

    AND_CONNECTORS = ["and", "with", "plus", "also", "then", ",", "&", "+"]
    THEN_CONNECTORS = ["then", "after that", "once", "before"]
    OR_CONNECTORS = ["or", "alternatively", "|"]
    IMPLICIT_PATTERNS = {
        "fix": ["test", "verify", "check"],
        "implement": ["test", "document", "type hints"],
        "refactor": ["test", "verify"],
    }

    @staticmethod
    def detect_composite_intents(
        request: str,
        primary_intent: IntentType,
    ) -> List[IntentType]:
        """Detect composite intents from request text.

        Args:
            request: User's natural language request.
            primary_intent: Primary intent already detected.

        Returns:
            List of intents including primary + any detected secondary intents.
        """
        intents = [primary_intent]
        request_lower = request.lower()

        for connector in CompositeIntentDetector.AND_CONNECTORS:
            if connector in request_lower:
                if "implement" in request_lower and "fix" in request_lower:
                    if IntentType.IMPLEMENT not in intents:
                        intents.append(IntentType.IMPLEMENT)
                    if IntentType.FIX not in intents:
                        intents.append(IntentType.FIX)
                if "refactor" in request_lower and "fix" in request_lower:
                    if IntentType.REFACTOR not in intents:
                        intents.append(IntentType.REFACTOR)
                    if IntentType.FIX not in intents:
                        intents.append(IntentType.FIX)
                if "implement" in request_lower and (
                    "document" in request_lower or "test" in request_lower
                ):
                    if IntentType.IMPLEMENT not in intents:
                        intents.append(IntentType.IMPLEMENT)
                    if (
                        IntentType.DOCUMENT not in intents
                        and "document" in request_lower
                    ):
                        intents.append(IntentType.DOCUMENT)

        for connector in CompositeIntentDetector.THEN_CONNECTORS:
            if connector in request_lower:
                parts = request_lower.split(connector)
                if len(parts) >= 2:
                    found: set = set(intents)
                    for part in parts:
                        if "implement" in part and IntentType.IMPLEMENT not in found:
                            found.add(IntentType.IMPLEMENT)
                        if "fix" in part and IntentType.FIX not in found:
                            found.add(IntentType.FIX)
                        if "refactor" in part and IntentType.REFACTOR not in found:
                            found.add(IntentType.REFACTOR)
                    intents = list(found)

        if primary_intent == IntentType.IMPLEMENT:
            if "document" in request_lower and IntentType.DOCUMENT not in intents:
                intents.append(IntentType.DOCUMENT)

        return list(set(intents))


# ---------------------------------------------------------------------------
# IntentRouter — slim coordination class (Phase 103-b, ≤500L)
# ---------------------------------------------------------------------------

class IntentRouter(
    LensAnalysisMixin,
    RegistryIntelligenceMixin,
    RoutingCoreMixin,
    SmartCitationsMixin,
    OrchestratorProtocolMixin,
    IOrchestrator,
):
    """Routes operations based on intent type and context.

    Implements Stage 2 (Routing) of the Master Orchestrator 4-stage workflow.
    Analyses operation context to determine the appropriate execution path.

    Responsibility clusters (Phase 103-b):
        LensAnalysisMixin           → LENS confidence boosts
        RegistryIntelligenceMixin   → Capability/governance discovery
        RoutingCoreMixin            → Core detection/cache/rules pipeline
        SmartCitationsMixin         → Rule citations + LENS auto-fetch
        OrchestratorProtocolMixin   → AC markers, cross-cutting hooks

    CORE Governance:
        CORE-008 · CORE-011 · CORE-012 · CORE-013 · CORE-027
    """

    # Backward-compatible class-level keyword lists (delegated to registry)
    IMPLEMENT_KEYWORDS = IntentKeywordRegistry.IMPLEMENT_KEYWORDS
    FIX_KEYWORDS = IntentKeywordRegistry.FIX_KEYWORDS
    REFACTOR_KEYWORDS = IntentKeywordRegistry.REFACTOR_KEYWORDS
    DOCUMENT_KEYWORDS = IntentKeywordRegistry.DOCUMENT_KEYWORDS
    ANALYZE_KEYWORDS = IntentKeywordRegistry.ANALYZE_KEYWORDS
    ONBOARD_KEYWORDS = IntentKeywordRegistry.ONBOARD_KEYWORDS
    PLAN_KEYWORDS = IntentKeywordRegistry.PLAN_KEYWORDS
    VACUUM_KEYWORDS = IntentKeywordRegistry.VACUUM_KEYWORDS
    AUDIT_KEYWORDS = IntentKeywordRegistry.AUDIT_KEYWORDS
    DESIGN_KEYWORDS = IntentKeywordRegistry.DESIGN_KEYWORDS
    DIGEST_KEYWORDS = IntentKeywordRegistry.DIGEST_KEYWORDS
    REPHRASE_KEYWORDS = IntentKeywordRegistry.REPHRASE_KEYWORDS
    INVESTIGATE_KEYWORDS = IntentKeywordRegistry.INVESTIGATE_KEYWORDS
    DEBUG_KEYWORDS = IntentKeywordRegistry.DEBUG_KEYWORDS
    HEALTH_KEYWORDS = IntentKeywordRegistry.HEALTH_KEYWORDS
    SYNC_KEYWORDS = IntentKeywordRegistry.SYNC_KEYWORDS
    TRAIN_KEYWORDS = IntentKeywordRegistry.TRAIN_KEYWORDS
    TOTALRECALL_KEYWORDS = IntentKeywordRegistry.TOTALRECALL_KEYWORDS
    RCA_KEYWORDS = IntentKeywordRegistry.RCA_KEYWORDS
    TEST_KEYWORDS = IntentKeywordRegistry.TEST_KEYWORDS
    DEPLOY_KEYWORDS = IntentKeywordRegistry.DEPLOY_KEYWORDS
    GOVERNANCE_KEYWORDS = IntentKeywordRegistry.GOVERNANCE_KEYWORDS
    QUERY_KEYWORDS = IntentKeywordRegistry.QUERY_KEYWORDS
    VALIDATE_KEYWORDS = IntentKeywordRegistry.VALIDATE_KEYWORDS
    MIGRATE_KEYWORDS = IntentKeywordRegistry.MIGRATE_KEYWORDS
    WORKFLOW_COMPOSE_KEYWORDS = IntentKeywordRegistry.WORKFLOW_COMPOSE_KEYWORDS
    GOLDEN_TEST_KEYWORDS = IntentKeywordRegistry.GOLDEN_TEST_KEYWORDS
    INTRODUCE_KEYWORDS = IntentKeywordRegistry.INTRODUCE_KEYWORDS

    def __init__(self) -> None:
        """Initialise IntentRouter orchestrator.

        Sets up operation type keyword mappings (via IntentKeywordRegistry),
        routing rules from YAML, decision cache, orchestrator lookup,
        enforcement engine, complexity router, and capability/governance registries.
        """
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()

        # Operation type detection mappings (delegated to keyword registry)
        self.operation_type_mappings: Dict[IntentType, List[str]] = (
            IntentKeywordRegistry.build_operation_type_mappings()
        )
        # Backward-compat alias kept for legacy callers
        self.vacuum_keywords = self.VACUUM_KEYWORDS

        # Routing config + rules (via RoutingCoreMixin methods)
        self.routing_rules_config: Dict[str, Any] = self._load_routing_config()
        self.routing_rules: Dict[Tuple[Optional[IntentType], Optional[str]], str] = (
            self._build_routing_rules()
        )

        # Decision cache
        self.cached_decisions: Dict[str, RoutingDecision] = {}

        # Complexity thresholds + fuzzy config
        self.complexity_thresholds = self.routing_rules_config.get(
            "complexity_thresholds",
            {"low": 0, "medium": 2, "high": 5, "critical": 8},
        )
        self.fuzzy_config = self.routing_rules_config.get(
            "fuzzy_matching",
            {"enabled": False, "algorithm": "levenshtein", "threshold": 0.75},
        )
        self.fuzzy_cache: Dict[str, List[str]] = {}

        # Orchestrator lookup + registry intelligence
        self.orchestrator_lookup: OrchestratorLookup = OrchestratorLookup()
        self.registry_agent = (
            get_registry_intelligence_agent()
            if get_registry_intelligence_agent
            else None
        )

        # Three-tier intent classifier (Phase 70 GAP-70-A4)
        self.intent_classifier: _IntentClassifier = _IntentClassifier(enable_llm=True)

        # Routing enforcement engine
        enforcement_config = self.routing_rules_config.get("enforcement", {})
        self.enforcement_engine: RoutingEnforcementEngine = RoutingEnforcementEngine(
            confidence_threshold=enforcement_config.get("confidence_threshold", 0.6),
            disambiguation_threshold=enforcement_config.get("disambiguation_threshold", 0.7),
            blocking_enabled=enforcement_config.get("blocking_enabled", True),
        )

        # Complexity router + governance rules
        self.complexity_router = WorkflowComplexityRouter()
        self.golden_hammer_rules = GoldenHammerRules()

        # Capability registry + governance registry (RegistryIntelligenceMixin)
        self.capability_registry = self._init_capability_registry()
        self._governance_registry: Optional[Any] = self._init_governance_registry()

        # Response engine stub (Wave H-S4)
        self._init_response_engine(
            intent_type=IntentType.QUERY,
            orchestrator_name="IntentRouter",
            enable=False,
        )

        self.logger.log_operation_complete(
            ac_id="AC-PROD-001-02",
            operation="INTENT_ROUTER_INIT",
            success=True,
            details={
                "operation_types": len(self.operation_type_mappings),
                "routing_rules": len(self.routing_rules),
                "cache_enabled": True,
                "fuzzy_matching_enabled": self.fuzzy_config.get("enabled", False),
                "yaml_config_loaded": "routing_rules" in self.routing_rules_config,
                "orchestrator_lookup_enabled": True,
                "enforcement_enabled": enforcement_config.get("blocking_enabled", True),
            },
        )

    # ------------------------------------------------------------------
    # IOrchestrator protocol — identity + lifecycle
    # ------------------------------------------------------------------

    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"

    def get_name(self) -> str:
        """Get orchestrator name."""
        return "IntentRouter"

    def get_mode(self) -> OperationMode:
        """Get operation mode."""
        return OperationMode.NORMAL

    def initialize(self) -> Result[str]:
        """Initialise the IntentRouter orchestrator."""
        try:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="INTENT_ROUTER_INITIALIZE",
                success=True,
                details={"status": "initialized"},
            )
            return Ok("IntentRouter initialized successfully")
        except Exception as e:
            return Err(f"IntentRouter initialization failed: {str(e)}")

    def validate_input(self, parameters: Dict[str, Any]) -> Result[bool]:
        """Validate input parameters for routing operations.

        Args:
            parameters: Input parameters to validate.

        Returns:
            Result[bool]: Ok(True) if valid, Err with message if invalid.
        """
        if not isinstance(parameters, dict):
            return Err("Parameters must be a dictionary")
        if not parameters:
            return Err("Parameters cannot be empty")
        if "operation" not in parameters and "description" not in parameters:
            return Err("Parameters must include 'operation' or 'description'")
        return Ok(True)

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail with hash chain.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            Result[list]: List of audit trail entries.
        """
        try:
            return Ok(self.logger.get_audit_trail(limit))
        except Exception as e:
            return Err(f"Failed to retrieve audit trail: {str(e)}")

    def _init_response_engine(
        self,
        intent_type: IntentType,
        orchestrator_name: str,
        enable: bool = False,
    ) -> None:
        """Stub for response engine initialisation (Wave H-S4 feature).

        Args:
            intent_type: Intent type for response formatting.
            orchestrator_name: Name of orchestrator.
            enable: Whether to enable (default False).
        """
        if enable:
            raise NotImplementedError("_init_response_engine not yet implemented")
        self._response_engine_enabled = False

    # ------------------------------------------------------------------
    # Primary routing entry point
    # ------------------------------------------------------------------

    def route(self, context: Dict[str, Any]) -> RoutingDecision:
        """Route an operation based on context (with decision caching).

        LENS Integration (LENS-002): accepts optional lens_context in context dict.

        Args:
            context: Dict with operation, description, domain, keywords,
                urgency, user_intent, lens_context.

        Returns:
            RoutingDecision: Routing decision with target handler.

        Raises:
            ValueError: If context is invalid or routing cannot be determined.
        """
        try:
            cache_key = self._get_cache_key(context)
            if cache_key in self.cached_decisions:
                return self.cached_decisions[cache_key]

            complexity_decision = self._check_workflow_complexity(context)
            if complexity_decision is not None:
                self.cached_decisions[cache_key] = complexity_decision
                return complexity_decision

            decision = self._route_internal(context)

            lens_context = context.get("lens_context")
            if lens_context:
                decision = self._enhance_with_lens(decision, lens_context)
                self.logger.log_operation_complete(
                    ac_id="LENS-002",
                    operation="LENS_ENHANCED_ROUTING",
                    success=True,
                    details={
                        "intent_type": decision.intent_type.value,
                        "confidence_boost_applied": decision.metadata.get(
                            "lens_confidence_boost", 0.0
                        ),
                    },
                )

            self.cached_decisions[cache_key] = decision
            return decision

        except (ValueError, KeyError, TypeError) as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="ROUTING_ERROR",
                success=False,
                details={"error": str(e)},
            )
            raise

    # ------------------------------------------------------------------
    # IOrchestrator execute / execute_operation
    # ------------------------------------------------------------------

    def execute(self, parameters: Dict[str, Any]) -> Result[str]:
        """Execute routing operation (IOrchestrator interface).

        Args:
            parameters: Operation parameters.

        Returns:
            Result[str]: Ok with routing decision JSON, or Err on failure.
        """
        self.logger.log_operation_start(
            ac_id="AC-PROD-001-02",
            operation="ROUTING_EXECUTE",
            details=parameters,
        )
        try:
            validation_result = self.validate_input(parameters)
            if validation_result.is_err():
                self.logger.log_operation_complete(
                    ac_id="AC-PROD-001-02",
                    operation="ROUTING_EXECUTE",
                    success=False,
                    details={"error": validation_result.unwrap_err()},
                )
                return validation_result  # type: ignore[return-value]

            decision = self.route(parameters)
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="ROUTING_EXECUTE",
                success=True,
                details={
                    "target_handler": decision.target_handler,
                    "confidence": decision.confidence_score,
                    "intent_type": decision.intent_type.value,
                },
            )
            return Ok(
                json.dumps({
                    "target_handler": decision.target_handler,
                    "intent_type": decision.intent_type.value,
                    "confidence": decision.confidence_score,
                    "reasoning": decision.reasoning,
                    "timestamp": decision.timestamp,
                })
            )
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="ROUTING_EXECUTE",
                success=False,
                details={"error": str(e)},
            )
            return Err(f"Routing execution failed: {str(e)}")

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute a named routing operation.

        Supports: analyze_and_route, route_operation, detect_intent,
        get_routing_rules.

        Args:
            operation_name: Name of the operation to execute.
            parameters: Operation parameters.

        Returns:
            Result[Any]: Operation result or Err on failure.
        """
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        try:
            if operation_name == "analyze_and_route":
                return self.execute(parameters)
            elif operation_name == "route_operation":
                return Ok(self.route(parameters))
            elif operation_name == "detect_intent":
                intent_type = self.detect_intent(parameters)
                return Ok({
                    "intent_type": intent_type.value,
                    "description": f"Detected {intent_type.value} operation",
                })
            elif operation_name == "get_routing_rules":
                rules_list = [
                    {"intent": intent.value if intent else None, "domain": domain, "handler": handler}
                    for (intent, domain), handler in self.routing_rules.items()
                ]
                return Ok({"routing_rules": rules_list})
            else:
                return Err(f"Unknown operation: {operation_name}")
        except Exception as e:
            return Err(f"Operation '{operation_name}' failed: {str(e)}")

    # ------------------------------------------------------------------
    # Additional public API
    # ------------------------------------------------------------------

    def classify_intent_with_workflow_suggestion(
        self, context: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """Classify intent and suggest a workflow template if applicable.

        Phase 100 Stage 3: Template suggestion based on context analysis.

        Args:
            context: Operation context dict.

        Returns:
            Tuple[str, Optional[str]]: (intent_type, Optional[template_id]).
        """
        intent = context.get("intent", "IMPLEMENT")
        attachments = context.get("attachments", [])
        has_visual = any(att.get("type", "").startswith("image/") for att in attachments)
        keywords = context.get("keywords", [])
        description = context.get("description", "").lower()

        template_id: Optional[str] = None
        if has_visual and intent in ["FIX", "IMPLEMENT"]:
            template_id = "tdd/frontend-visual"
        elif any(kw in description or kw in keywords for kw in ["api", "endpoint", "rest"]):
            if intent == "IMPLEMENT":
                template_id = "tdd/api-service"
        elif any(
            kw in description or kw in keywords
            for kw in ["security", "compliance", "audit"]
        ):
            if intent == "AUDIT":
                template_id = "security/compliance-audit"
        elif intent == "IMPLEMENT" and template_id is None:
            template_id = "tdd/feature-implementation"

        return intent, template_id

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get MCP tools exposed by this orchestrator.

        Returns:
            Result[Dict]: Dictionary of available MCP tools.
        """
        try:
            tools = {
                "route_operation": {
                    "description": "Route operation to appropriate handler based on intent",
                    "parameters": ["operation", "description", "domain", "keywords"],
                    "returns": "RoutingDecision with target_handler",
                },
                "analyze_and_route": {
                    "description": "Analyse operation context and route to handler",
                    "parameters": ["operation", "description", "domain", "keywords"],
                    "returns": "Routing decision result",
                },
                "detect_intent": {
                    "description": "Detect operation intent type",
                    "parameters": ["operation", "description", "keywords"],
                    "returns": "IntentType enum",
                },
                "get_routing_rules": {
                    "description": "Get available routing rules",
                    "parameters": [],
                    "returns": "List of routing rules",
                },
            }
            return Ok(tools)
        except Exception as e:
            return Err(f"Failed to get MCP tools: {str(e)}")


# Module-level exports
__all__ = [
    "IntentRouter",
    "IntentType",
    "RoutingDecision",
    "RoutingContext",
    "CompositeIntentDetector",
]
