"""Stage 2: Intent Routing — Knowledge synthesis and orchestrator selection.

Implements the second stage of the Master Orchestrator 4-stage pipeline.
Routes requests via IntentRouter with LENS auto-fetch and unified
intelligence synthesis (Phase 20 + 20.5).

CORE Governance:
    CORE-008: TDD mandatory
    CORE-011: Type hints on all functions
    CORE-012: Docstrings on all public APIs
    CORE-027: Audit trail logging
    CORE-035: Single canonical implementation — extracted from master_orchestrator.py (F2)

Authority: AC-PHASE-20-COMPONENT-4, AC-KNOWLEDGE-SYNTHESIS-001 (Phase 20.5)
Phase: Phase 57 (F2 MasterOrchestrator decomposition)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin

logger = logging.getLogger(__name__)


class MasterOrchestratorStage2(OrchestratorProtocolMixin):
    """Stage 2 handler: Intent routing with knowledge synthesis.

    Extracted from :class:`~cortex.orchestrators.core.master_orchestrator.MasterOrchestrator`
    as part of F2 decomposition (Phase 57) to reduce the god-object footprint.

    Delegates back to ``master_orchestrator`` state via ``self._host`` so that
    no behaviour is changed — only the physical file boundary moves.

    Usage (inside MasterOrchestrator)::

        self._stage_2 = MasterOrchestratorStage2(host=self)
        result = self._stage_2.route(request)
    """

    def __init__(self, host: Any) -> None:
        """Bind to the MasterOrchestrator instance that owns this stage.

        Args:
            host: The owning ``MasterOrchestrator`` instance. Provides access to
                ``host.intent_router``, ``host._synthesis_engine``,
                ``host.logger``, and the violation-filter helpers.
        """
        self._host = host

    # -------------------------------------------------------------------------
    # Public entry point
    # -------------------------------------------------------------------------

    def route(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Stage 2: route request with unified intelligence synthesis.

        Phase 20 Component #4: MasterOrchestrator LENS Integration
        Phase 20.5 Component #3: Knowledge Synthesis at Stage 2

        Workflow:
            1. Classify intent via IntentRouter
            2. Fetch LENS context (Phase 20)
            3. Synthesize unified intelligence (Phase 20.5)
            4. Detect critical violations early (block on P0)
            5. Return enhanced routing result with citations and guidance

        Args:
            request: Request dict with keys:
                operation, description, file_path, company_name, domain, keywords, context.

        Returns:
            Routing result dict with intent, target_orchestrator, confidence_score,
            reasoning, context, unified_intelligence, cited_rules, violations, guidance.
        """
        # Phase 58: activate cross-cutting hooks (LENS + knowledge synthesis)
        self._activate_cross_cutting_hooks(
            operation=request.get("operation", "route"),
            orchestrator_context=request.get("orchestrator_context"),
            unified_context=request.get("unified_context"),
        )
        host = self._host
        logger.debug("Stage 2: routing request operation=%r", request.get("operation"))

        try:
            # Ensure IntentRouter is initialised
            if not host.intent_router:
                from cortex.orchestrators.core.intent_router import IntentRouter
                host.intent_router = IntentRouter()

            routing_request = {
                "intent": request.get("operation", ""),
                "description": request.get("description", ""),
                "file_path": request.get("file_path"),
                "company_name": request.get("company_name"),
                "domain": request.get("domain"),
                "keywords": request.get("keywords"),
                "context": request.get("context", {}),
            }

            # Phase 20.5: Pre-synthesize unified intelligence
            unified_context = self._pre_synthesize(request)

            # Call IntentRouter with LENS auto-fetch + pre-synthesized intelligence
            result = host.intent_router.route_with_lens_auto_fetch(
                routing_request,
                unified_intelligence=unified_context,
            )
            intent_type = result.get("intent", "UNKNOWN")

            # Phase 20.5: Post-synthesis with LENS data returned by IntentRouter
            result = self._post_synthesize(request, result, unified_context, intent_type)

            # Log LENS integration activity
            host.logger.log_operation_complete(
                ac_id="AC-PHASE-20-COMPONENT-4",
                operation="STAGE_2_LENS_INTEGRATION",
                success=True,
                details={
                    "intent": result.get("intent"),
                    "target_orchestrator": result.get("target_orchestrator"),
                    "lens_fetched": "lens_insights" in result.get("context", {}),
                    "company_name": request.get("company_name"),
                    "file_path": request.get("file_path"),
                },
            )
            return result

        except Exception as exc:
            host.logger.log_operation_complete(
                ac_id="AC-PHASE-20-COMPONENT-4",
                operation="STAGE_2_LENS_INTEGRATION_FAILED",
                success=False,
                details={"error": str(exc)},
            )
            return {
                "intent": request.get("operation", "UNKNOWN"),
                "target_orchestrator": "MasterOrchestrator",
                "confidence_score": 0.0,
                "reasoning": f"Stage 2 error: {exc}",
                "context": request.get("context", {}),
            }

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    def _pre_synthesize(self, request: Dict[str, Any]) -> Optional[Any]:
        """Pre-synthesize unified intelligence before IntentRouter call.

        Returns the ``UnifiedIntelligenceContext`` or ``None`` on failure.

        Args:
            request: Original request dict.
        """
        host = self._host
        try:
            from cortex.intelligence.knowledge.unified_intelligence_context import (
                CompanyKnowledge,
                LENSIntelligence,
            )

            intent_str = request.get("operation", "")
            file_path = request.get("file_path")

            lens_intelligence = LENSIntelligence(
                git_analysis={},
                ast_analysis={},
                comment_analysis={},
            )
            company_knowledge = CompanyKnowledge(
                domain_rules={},
                compliance_standards=[],
                precedence="OVERRIDE",
            )

            unified_context = host._synthesis_engine.synthesize_unified_context(
                intent_type=intent_str,
                lens_intelligence=lens_intelligence,
                company_knowledge=company_knowledge,
                file_path=file_path,
            )

            host.logger.log_operation_complete(
                ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                operation="STAGE_2_PRE_SYNTHESIS",
                success=True,
                details={
                    "intent": intent_str,
                    "cited_rules_count": len(unified_context.get_cited_rules()),
                    "cortex_practices_loaded": len(
                        unified_context.cortex_knowledge.best_practices
                    ),
                },
            )
            return unified_context

        except Exception as err:
            host.logger.log_operation_complete(
                ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                operation="STAGE_2_PRE_SYNTHESIS_FAILED",
                success=False,
                details={"error": str(err)},
            )
            return None

    def _post_synthesize(
        self,
        request: Dict[str, Any],
        result: Dict[str, Any],
        unified_context: Optional[Any],
        intent_type: str,
    ) -> Dict[str, Any]:
        """Re-synthesize with LENS data returned by IntentRouter and check violations.

        Args:
            request: Original request dict.
            result: Raw routing result from IntentRouter.
            unified_context: Pre-synthesized context (may be None).
            intent_type: Detected intent string.

        Returns:
            Enriched routing result dict.
        """
        host = self._host
        try:
            lens_context = result.get("context", {}).get("lens_insights", {})
            if lens_context and unified_context:
                from cortex.intelligence.knowledge.unified_intelligence_context import (
                    CompanyKnowledge,
                    LENSIntelligence,
                )

                lens_intelligence = LENSIntelligence(
                    git_analysis=lens_context.get("git_analysis", {}),
                    ast_analysis=lens_context.get("ast_analysis", {}),
                    comment_analysis=lens_context.get("comment_analysis", {}),
                )
                company_ctx = lens_context.get("company_knowledge", {})
                company_knowledge = CompanyKnowledge(
                    domain_rules=company_ctx.get("domain_rules", {}),
                    compliance_standards=company_ctx.get("compliance_standards", []),
                    precedence="OVERRIDE",
                )
                unified_context = host._synthesis_engine.synthesize_unified_context(
                    intent_type=intent_type,
                    lens_intelligence=lens_intelligence,
                    company_knowledge=company_knowledge,
                    file_path=request.get("file_path"),
                )

            if unified_context:
                result["unified_intelligence"] = unified_context.to_dict()
                result["cited_rules"] = unified_context.get_cited_rules()
                result["violations"] = unified_context.get_violations()
                result["guidance"] = unified_context.get_guidance()

                host.logger.log_operation_complete(
                    ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                    operation="STAGE_2_UNIFIED_SYNTHESIS",
                    success=True,
                    details={
                        "intent": intent_type,
                        "cited_rules_count": len(unified_context.get_cited_rules()),
                        "violations_count": len(unified_context.get_violations()),
                        "guidance_count": len(unified_context.get_guidance()),
                        "cortex_practices_loaded": len(
                            unified_context.cortex_knowledge.best_practices
                        ),
                    },
                )

                violations = unified_context.get_violations()
                if violations:
                    critical = host._filter_critical_violations(violations)
                    if critical:
                        summary = host._format_violation_summary(critical, unified_context)
                        host.logger.log_operation_complete(
                            ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                            operation="STAGE_2_VIOLATION_BLOCK",
                            success=True,
                            details={
                                "intent": intent_type,
                                "critical_violations": len(critical),
                                "total_violations": len(violations),
                                "action": "BLOCKED",
                            },
                        )
                        return {
                            "intent": intent_type,
                            "target_orchestrator": "BLOCKED",
                            "confidence_score": 0.0,
                            "reasoning": "Execution blocked due to critical violations",
                            "context": result.get("context", {}),
                            "violations": violations,
                            "critical_violations": critical,
                            "violation_summary": summary,
                            "guidance": unified_context.get_guidance(),
                            "status": "BLOCKED",
                            "error": (
                                "Critical CORE rule violations detected. "
                                "Please address violations before proceeding."
                            ),
                        }
                    else:
                        host.logger.log_operation_complete(
                            ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                            operation="STAGE_2_VIOLATION_WARNING",
                            success=True,
                            details={
                                "intent": intent_type,
                                "non_critical_violations": len(violations),
                                "action": "WARNING",
                            },
                        )

        except Exception as err:
            host.logger.log_operation_complete(
                ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                operation="STAGE_2_POST_SYNTHESIS_FAILED",
                success=False,
                details={"error": str(err)},
            )

        return result
