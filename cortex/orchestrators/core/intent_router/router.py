# AC_START: AC-PHASE81-S3-003
# =============================================================================
# DEPRECATED: Enhanced IntentRouter (Phase 81)
# =============================================================================
# Status: DEPRECATED as of Phase 25 S2 (2026-02-15)
# Reason: Consolidation to single IntentRouter implementation (CORE-035)
#
# Migration: Use cortex.orchestrators.core.intent_router.IntentRouter
#
# This module is preserved for reference only. All imports should migrate to:
#   from cortex.orchestrators.core.intent_router import IntentRouter
#
# See: cortex/intent_router/DEPRECATED.md for full migration guide
# =============================================================================
"""
Enhanced IntentRouter with Capability-Based Agent Selection

Integrates capability_matcher and collaboration_coordinator for intelligent
multi-agent workflows with shared context optimization.

Module: cortex/intent_router/router_v2.py
Authority: Phase 81 S3 - IntentRouter Capability-Based Routing
Version: 2.0
"""

from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re
import logging

from .capability_matcher import CapabilityMatcher, IntentType
from .collaboration_coordinator import (
    AgentCollaborationCoordinator,
    CollaborationRequest,
    CollaborationPattern,
    AgentContext
)

try:
    from cortex.models.canonical_enums import IntentType as CanonicalIntentType
except ImportError:
    CanonicalIntentType = None

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin

logger = logging.getLogger(__name__)


@dataclass
class IntentRoutingRequest:
    """Request for intent routing."""
    request_id: str
    user_query: str
    intent: IntentType
    confidence: float
    context: Optional[Dict[str, Any]] = None


@dataclass
class IntentRoutingResult:
    """Result from enhanced intent routing."""
    request_id: str
    primary_agent_id: str
    secondary_agents: List[str]
    collaboration_pattern: CollaborationPattern
    mcp_tools: List[str]
    context: AgentContext
    confidence: float
    reasoning: str
    _routed_intent: Optional[Any] = field(default=None, repr=False)
    timestamp: Optional[str] = field(default=None, repr=False)
    confidence_breakdown: Optional[Dict[str, float]] = field(default=None, repr=False)

    @property
    def target_handler(self) -> str:
        """Backward-compat: primary agent as target handler."""
        return self.primary_agent_id

    @property
    def confidence_score(self) -> float:
        """Backward-compat: confidence with floor."""
        return max(self.confidence, 0.65)

    @property
    def intent_type(self) -> Any:
        """Backward-compat: canonical enum intent type."""
        if self._routed_intent is not None:
            intent_val = self._routed_intent.value if hasattr(self._routed_intent, 'value') else str(self._routed_intent)
            if CanonicalIntentType is not None:
                try:
                    return CanonicalIntentType(intent_val.lower())
                except (ValueError, KeyError):
                    pass
            return self._routed_intent
        return None

    @property
    def keyword_matches(self) -> List[str]:
        """Backward-compat: keywords from context."""
        if self.context and hasattr(self.context, 'extracted_data'):
            return self.context.extracted_data.get('keywords', [])
        return []

    @property
    def metadata(self) -> Dict[str, Any]:
        """Backward-compat: routing metadata from context."""
        meta: Dict[str, Any] = {}
        if self.context:
            if hasattr(self.context, 'extracted_data') and self.context.extracted_data:
                meta.update(self.context.extracted_data)
            if hasattr(self.context, 'phase_state') and self.context.phase_state:
                meta.update(self.context.phase_state)
        return meta


class EnhancedIntentRouter(OrchestratorProtocolMixin):
    """
    IntentRouter v2 with capability-based agent selection.

    Features:
    - Intelligent agent selection via CapabilityMatcher
    - Multi-agent collaboration orchestration
    - Shared context optimization (LENS cache, phase state)
    - Dynamic collaboration pattern selection
    - Fallback chain support

    Architecture:
    1. Classify user intent (intent type, confidence)
    2. Match capabilities to available agents
    3. Determine collaboration pattern (sequential, parallel, hierarchical)
    4. Optimize for context reuse (avoid duplicate LENS analysis)
    5. Route to primary agent + secondary agents

    Example:
        >>> router = EnhancedIntentRouter()
        >>> routing_req = IntentRoutingRequest(
        ...     request_id="req-001",
        ...     user_query="implement feature X",
        ...     intent=IntentType.IMPLEMENT,
        ...     confidence=0.95
        ... )
        >>> result = router.route(routing_req)
        >>> print(f"Route: {result.primary_agent_id} + {len(result.secondary_agents)} collaborators")
    """

    def __init__(self) -> None:
        """Initialize enhanced intent router."""
        self.capability_matcher = CapabilityMatcher()
        self.collaboration_coordinator = AgentCollaborationCoordinator()
        self._lens_cache: Dict[str, Any] = {}
        self._registered_agents: List[Dict[str, Any]] = []
        self._register_default_agents()
        logger.info("EnhancedIntentRouter initialized (v2 with capability matching)")

    def register_agents(self, agents: List[Dict[str, Any]]) -> None:
        """Register all available agents in collaboration system."""
        self._registered_agents = agents
        for agent in agents:
            self.collaboration_coordinator.register_agent(
                agent_id=agent["agent_id"],
                capabilities=agent.get("capabilities", []),
                mcp_tools=agent.get("mcp_tools", []),
                priority=agent.get("priority", "P2")
            )
            logger.debug(f"Agent registered in routing system: {agent['agent_id']}")

    def route(self, request: Any) -> IntentRoutingResult:
        """Route user request to optimal agent(s). Accepts IntentRoutingRequest or dict."""
        # Dict coercion
        if isinstance(request, dict):
            original_dict = request
            intent = self._detect_intent_from_dict(original_dict)
            request = IntentRoutingRequest(
                request_id=f"dict-{id(original_dict)}",
                user_query=original_dict.get("description", original_dict.get("operation", "")),
                intent=intent,
                confidence=0.85,
                context=original_dict
            )
            gate_result = self._evaluate_complexity_gate(original_dict)
            gate_result["routing_source"] = "complexity_gate"

            # Use CapabilityMatcher for intent-aware agent selection
            available_agents = self._get_all_available_agents()
            if available_agents:
                try:
                    agent_rankings = self.capability_matcher.match_capabilities(
                        intent=intent,
                        user_request=request.user_query,
                        available_agents=available_agents,
                    )
                    agent_id = agent_rankings.primary_agent_id
                    reasoning = agent_rankings.reasoning
                    confidence = agent_rankings.confidence
                except Exception:
                    agent_id = "cortex-tdd-orchestrator"
                    reasoning = "Fallback: capability matching failed for dict input"
                    confidence = 0.5
            else:
                agent_id = "cortex-tdd-orchestrator"
                reasoning = "Fallback: no agents available for matching"
                confidence = 0.5

            # Override with workflow template if complexity gate triggers
            if gate_result.get("template_id"):
                agent_id = f"WorkflowTemplate:{gate_result['template_id']}"
                intent_name = intent.value.lower() if hasattr(intent, 'value') else str(intent).lower()
                reasoning = f"Complexity-gated {intent_name} workflow template routing"
                confidence = 0.85

            fallback_context = AgentContext(
                agent_id=agent_id,
                request_id=request.request_id,
                user_request=request.user_query,
                intent=intent.value
            )
            fallback_context.extracted_data.update(gate_result)
            for key in ("domain", "keywords", "urgency", "operation", "risk_level"):
                if key in original_dict:
                    fallback_context.extracted_data[key] = original_dict[key]

            return IntentRoutingResult(
                request_id=request.request_id,
                primary_agent_id=agent_id,
                secondary_agents=[],
                collaboration_pattern=CollaborationPattern.SEQUENTIAL,
                mcp_tools=["cortex_process_request"],
                context=fallback_context,
                confidence=confidence,
                reasoning=reasoning,
                _routed_intent=intent,
                timestamp=datetime.now().isoformat(),
            )

        logger.info(
            f"Routing request: id={request.request_id}, intent={request.intent.value}, "
            f"confidence={request.confidence:.2f}"
        )

        try:
            available_agents = self._get_all_available_agents()

            agent_rankings = self.capability_matcher.match_capabilities(
                intent=request.intent,
                user_request=request.user_query,
                available_agents=available_agents
            )

            primary_agent_id = agent_rankings.primary_agent_id
            secondary_agents = self._extract_secondary_agents(agent_rankings)

            pattern = self.collaboration_coordinator.determine_collaboration_pattern(
                primary_agent_id=primary_agent_id,
                secondary_agents=secondary_agents
            )

            context = self._build_shared_context(
                request=request,
                primary_agent_id=primary_agent_id,
                secondary_agents=secondary_agents
            )

            mcp_tools = self._collect_mcp_tools(primary_agent_id, secondary_agents)

            result = IntentRoutingResult(
                request_id=request.request_id,
                primary_agent_id=primary_agent_id,
                secondary_agents=secondary_agents,
                collaboration_pattern=pattern,
                mcp_tools=mcp_tools,
                context=context,
                confidence=agent_rankings.confidence,
                reasoning=agent_rankings.reasoning,
                _routed_intent=request.intent,
                timestamp=datetime.now().isoformat(),
            )

            logger.info(
                f"Routing resolved: agent={primary_agent_id}, pattern={pattern.value}, "
                f"confidence={result.confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Routing failed: {request.request_id}: {e}", exc_info=True)
            return self._fallback_routing(request)

    def coordinate_agents(self, routing_result: IntentRoutingResult) -> CollaborationRequest:
        """Create collaboration request from routing result."""
        collab_req = CollaborationRequest(
            request_id=routing_result.request_id,
            primary_agent_id=routing_result.primary_agent_id,
            secondary_agents=routing_result.secondary_agents,
            pattern=routing_result.collaboration_pattern,
            context=routing_result.context
        )
        logger.debug(
            f"Collaboration request created: {routing_result.request_id}, "
            f"pattern={routing_result.collaboration_pattern.value}"
        )
        return collab_req

    def _get_all_available_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents for matching."""
        return self._registered_agents if self._registered_agents else []

    def _extract_secondary_agents(self, rankings: Any) -> List[str]:
        """Extract secondary agent IDs from capability matcher rankings."""
        secondary = []
        if hasattr(rankings, 'secondary_agent_id') and rankings.secondary_agent_id:
            secondary.append(rankings.secondary_agent_id)
        if hasattr(rankings, 'fallback_chain') and rankings.fallback_chain:
            if len(rankings.fallback_chain) > 0:
                top_fallback = rankings.fallback_chain[0][0]
                if top_fallback not in secondary:
                    secondary.append(top_fallback)
        return secondary

    def _build_shared_context(
        self, request: IntentRoutingRequest,
        primary_agent_id: str, secondary_agents: List[str]
    ) -> AgentContext:
        """Build shared context with LENS cache optimization."""
        context = AgentContext(
            agent_id=primary_agent_id,
            request_id=request.request_id,
            user_request=request.user_query,
            intent=request.intent.value
        )
        if request.context:
            context.extracted_data.update(request.context.get("extracted_data", {}))
            if "phase_state" in request.context:
                context.phase_state = request.context["phase_state"]
        if "file_path" in context.extracted_data:
            lens_key = f"lens:{context.extracted_data['file_path']}"
            if lens_key not in self._lens_cache:
                self._lens_cache[lens_key] = {
                    "analysis_type": "ast",
                    "timestamp": datetime.now().isoformat()
                }
            context.add_lens_cache(lens_key, self._lens_cache[lens_key])
        logger.debug(
            f"Shared context built: request={request.request_id}, "
            f"lens_cache_size={len(context.lens_cache)}, "
            f"agents={len(secondary_agents) + 1}"
        )
        return context

    def _collect_mcp_tools(self, primary_agent_id: str, secondary_agents: List[str]) -> List[str]:
        """Collect all MCP tools needed by agents in workflow."""
        tools = []
        primary_tools = self._get_agent_mcp_tools(primary_agent_id)
        tools.extend(primary_tools)
        for agent_id in secondary_agents:
            secondary_tools = self._get_agent_mcp_tools(agent_id)
            for tool in secondary_tools:
                if tool not in tools:
                    tools.append(tool)
        logger.debug(f"MCP tools collected: {len(tools)} tools for {len(secondary_agents) + 1} agents")
        return tools

    def _get_agent_mcp_tools(self, agent_id: str) -> List[str]:
        """Get MCP tools for an agent (placeholder)."""
        agent_tools = {
            "cortex-phase-resolver": ["cortex_resolve_phase"],
            "cortex-master-plan-auditor": ["cortex_audit_plan", "cortex_sync_plan_status"],
            "cortex-meta-auditor": ["cortex_meta_audit", "cortex_validate_governance_health"],
            "cortex-auditor": ["cortex_audit_codebase"],
            "cortex-architect": ["cortex_design_proposal"],
        }
        return agent_tools.get(agent_id, ["cortex_process_request"])

    def _detect_intent_from_dict(self, d: Dict[str, Any]) -> IntentType:
        """Detect intent type from a dict-based request using keyword matching."""
        text = f"{d.get('operation', '')} {d.get('description', '')} {d.get('user_request', '')}".lower()
        # GAP-005: Check specific modes before generic fallbacks (priority order)
        # Most specific intents first, then broader ones
        if re.search(r'rephrase|reword|token.optim|compact this|make this concise', text):
            return IntentType.REPHRASE
        elif re.search(r'digest|summarize|summary|what happened|recap|tldr', text):
            return IntentType.DIGEST
        elif re.search(r'investigate|root cause|why is|what causes|deep analysis|trace the|debug why|find the cause', text):
            return IntentType.INVESTIGATE
        elif re.search(r'\bdesign\b|architect|blueprint|system design', text):
            return IntentType.DESIGN
        elif re.search(r'refactor|clean|improve|optimize|migrate|restructure|reorganize|rewrite|modernize', text):
            return IntentType.REFACTOR
        elif re.search(r'fix|bug|error|broken|debug|resolve|correct|patch|repair', text):
            return IntentType.FIX
        elif re.search(r'audit|scan repo|production readiness|health check|check repo|repo health', text):
            return IntentType.AUDIT
        elif re.search(r'implement|create|build|add|new', text):
            return IntentType.IMPLEMENT
        elif re.search(r'plan|organize|roadmap', text):
            return IntentType.PLAN
        else:
            return IntentType.ANALYZE

    def _evaluate_complexity_gate(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate complexity of a dict-based request for routing decisions."""
        files = d.get('target_files', [])
        deps = d.get('dependencies', [])
        risk = d.get('risk_level', 'LOW').upper()
        file_count = len(files)
        dep_count = len(deps)
        risk_map = {'LOW': 0.1, 'MEDIUM': 0.5, 'HIGH': 0.9, 'CRITICAL': 1.0}
        risk_score = risk_map.get(risk, 0.1)
        file_score = min(file_count / 20.0, 1.0)
        dep_score = min(dep_count / 10.0, 1.0)
        complexity_score = file_score * 0.35 + dep_score * 0.25 + risk_score * 0.4
        result: Dict[str, Any] = {
            'complexity_score': round(complexity_score, 4),
            'requires_confirmation': 0.35 <= complexity_score < 0.60,
            'template_id': None,
        }
        if complexity_score >= 0.60:
            result['template_id'] = 'workflow-complex-operation'
        return result

    def _register_default_agents(self) -> None:
        """Register default agents with capabilities aligned to INTENT_CAPABILITY_MAP."""
        defaults = [
            {
                "agent_id": "cortex-tdd-orchestrator",
                "capabilities": [
                    "testing_integration", "tdd", "implementation",
                    "code_generation", "test_coverage_analysis",
                ],
                "mcp_tools": ["cortex_process_request"],
                "priority": "P0",
            },
            {
                "agent_id": "cortex-auditor",
                "capabilities": [
                    "codebase_health_scanning", "security_validation",
                    "governance_compliance_checking", "auditing", "compliance",
                ],
                "mcp_tools": ["cortex_audit_codebase"],
                "priority": "P0",
            },
            {
                "agent_id": "cortex-lens-orchestrator",
                "capabilities": [
                    "code_analysis", "architecture_analysis",
                    "performance_analysis", "analysis", "code_review",
                ],
                "mcp_tools": ["cortex.lens_analyze"],
                "priority": "P1",
            },
            {
                "agent_id": "cortex-planner",
                "capabilities": [
                    "phase_management", "planning", "resource_allocation",
                    "roadmap",
                ],
                "mcp_tools": ["cortex_plan"],
                "priority": "P1",
            },
            {
                "agent_id": "cortex-debugger",
                "capabilities": [
                    "bug_fixing", "debugging", "test_coverage_analysis",
                    "fix",
                ],
                "mcp_tools": ["cortex_debug"],
                "priority": "P1",
            },
            {
                "agent_id": "cortex-refactorer",
                "capabilities": [
                    "code_refactoring", "architecture_analysis",
                    "performance_optimization", "refactoring", "optimization",
                ],
                "mcp_tools": ["cortex_refactor"],
                "priority": "P2",
            },
            {
                "agent_id": "cortex-architect",
                "capabilities": [
                    "challenge_generation", "architecture_analysis",
                    "alternative_proposal_generation", "design_pattern_analysis",
                    "architecture", "design",
                ],
                "mcp_tools": ["cortex_design_proposal"],
                "priority": "P2",
            },
            {
                "agent_id": "cortex-knowledge",
                "capabilities": [
                    "knowledge_retrieval", "pattern_recognition",
                    "knowledge", "documentation",
                ],
                "mcp_tools": ["cortex_knowledge"],
                "priority": "P2",
            },
        ]
        self.register_agents(defaults)

    def _format_routing_message_with_books(self, rule_id: str) -> str:
        """Format routing message enriched with book references.

        Uses BusinessWisdomFormatter to add book citations to governance rules.
        Falls back to raw rule_id if formatter is unavailable or raises.

        Args:
            rule_id: CORE rule identifier (e.g. "CORE-008").

        Returns:
            Enriched markdown string or raw rule_id on error.
        """
        try:
            from cortex.core.interaction.business_wisdom_formatter import (
                BusinessWisdomFormatter,
            )

            formatter = BusinessWisdomFormatter()
            return formatter.format_governance_with_books(
                rule_ids=[rule_id],
                max_display=1,
                include_icon=False,
            )
        except Exception:
            return rule_id

    def classify_intent_with_workflow_suggestion(
        self, context: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """Classify intent and suggest a workflow template if applicable.

        Examines attachments and keywords to recommend specialised
        workflow templates (e.g. frontend-visual TDD, API service, security).

        Args:
            context: Dict with ``description``, ``intent``, optional
                ``attachments`` and ``keywords``.

        Returns:
            Tuple of (intent_string, template_id_or_None).
        """
        intent = context.get("intent", "IMPLEMENT")
        attachments = context.get("attachments", [])
        keywords = context.get("keywords", [])
        description = context.get("description", "").lower()

        # Visual context → frontend-visual template
        has_visual = any(
            a.get("type", "").startswith("image/") for a in attachments
        )
        if has_visual:
            return intent, "tdd/frontend-visual"

        # Keyword-based template selection
        keyword_set = {k.lower() for k in keywords}
        desc_keywords = set(description.split())

        if intent == "AUDIT" and (
            "security" in keyword_set or "security" in desc_keywords
        ):
            return intent, "security/compliance-audit"

        if intent == "IMPLEMENT":
            if "api" in keyword_set or "endpoint" in keyword_set:
                return intent, "tdd/api-service"
            # Generic feature implementation
            return intent, "tdd/feature-implementation"

        return intent, None

    def _fallback_routing(self, request: IntentRoutingRequest) -> IntentRoutingResult:
        """Provide fallback routing when primary routing fails."""
        logger.warning(f"Using fallback routing for request: {request.request_id}")
        fallback_context = AgentContext(
            agent_id="cortex-tdd-orchestrator",
            request_id=request.request_id,
            user_request=request.user_query,
            intent=request.intent.value
        )
        return IntentRoutingResult(
            request_id=request.request_id,
            primary_agent_id="cortex-tdd-orchestrator",
            secondary_agents=[],
            collaboration_pattern=CollaborationPattern.SEQUENTIAL,
            mcp_tools=["cortex_process_request"],
            context=fallback_context,
            confidence=0.5,
            reasoning="Fallback routing used due to routing error",
            _routed_intent=request.intent,
            timestamp=datetime.now().isoformat(),
        )


# AC_COMPLETE: AC-PHASE81-S3-003
