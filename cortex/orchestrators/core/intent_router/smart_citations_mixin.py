"""
SmartCitationsMixin — Phase 103-b GAP-103-02.

Smart rule citations, LENS auto-fetch routing, intelligence matrix lookup,
and business wisdom book references extracted from IntentRouter.

Responsibility: Enrich routing results with governance citations,
LENS auto-fetch, and intelligence matrix orchestrator chain selection.
SRP: Zero keyword logic, zero LENS analysis, zero registry intelligence — enrichment only.

CORE-011: Type hints on all functions.
CORE-012: Docstrings on all public APIs.
CORE-028: snake_case naming.
"""
from typing import Any, Dict, List, Optional


class SmartCitationsMixin:
    """Mixin providing smart citations and intelligence enrichment for IntentRouter.

    Designed for cooperative multiple inheritance. Assumes the following
    instance attributes are set by ``IntentRouter.__init__``:
        - self.logger  (EnhancedAuditLogger)
    """

    def _intelligence_matrix_lookup(
        self, intent: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Look up the best orchestrator chain via the intelligence matrix.

        Phase 78 GAP-78-A-06: Replace keyword-only routing with matrix-aware
        selection that consults IntelligenceFacade for context-informed selection.

        Args:
            intent: Classified intent string (e.g. "IMPLEMENT", "AUDIT").
            context: Full routing context dict.

        Returns:
            Dict with 'primary_orchestrator', 'chain', 'confidence_boost' keys.
        """
        try:
            from cortex.intelligence.facade import get_intelligence_facade  # noqa: PLC0415
            facade = get_intelligence_facade()
            bp = facade.synthesize(query=f"routing:{intent.lower()}")
            return {
                "primary_orchestrator": bp.get("recommended_orchestrator", ""),
                "chain": bp.get("orchestrator_chain", []),
                "confidence_boost": bp.get("confidence_boost", 0.0),
            }
        except Exception:
            return {"primary_orchestrator": "", "chain": [], "confidence_boost": 0.0}

    def _select_best_orchestrator_chain(
        self, intent: str, context: Dict[str, Any]
    ) -> list:
        """Select best orchestrator chain for intent using matrix lookup.

        Phase 78 GAP-78-A-06: Convenience wrapper over _intelligence_matrix_lookup.

        Args:
            intent: Classified intent string.
            context: Full routing context dict.

        Returns:
            List of orchestrator names in execution order.
        """
        result = self._intelligence_matrix_lookup(intent, context)
        return result.get("chain", [])

    def _get_intent_applicable_rules(
        self,
        intent: str,
        cited_rules: List[str],
        unified_intelligence: Any,
    ) -> List[str]:
        """Filter cited rules to only those applicable to the current intent.

        Phase 20.5 Component #4: Smart Citations Helper.

        Args:
            intent: Current intent type (IMPLEMENT, FIX, etc.).
            cited_rules: All cited rule IDs from synthesis.
            unified_intelligence: Full UnifiedIntelligenceContext.

        Returns:
            List[str]: Filtered rule IDs with titles (e.g. "CORE-008: TDD Required").
        """
        intent_priorities = {
            "IMPLEMENT": ["CORE-008", "CORE-011", "CORE-012", "CORE-026"],
            "FIX": ["CORE-013", "CORE-027", "CORE-008"],
            "REFACTOR": ["CORE-011", "CORE-012", "CORE-035"],
            "ANALYZE": ["CORE-030", "CORE-036"],
            "TEST": ["CORE-008", "CORE-013"],
        }
        priority_rules = intent_priorities.get(intent, [])
        applicable = [rule for rule in cited_rules if rule in priority_rules]

        result = []
        try:
            merged = unified_intelligence.synthesis_result.merged_rules
            for rule_id in applicable:
                if rule_id in merged:
                    title = merged[rule_id].get("title", rule_id)
                    result.append(f"{rule_id}: {title}")
                else:
                    result.append(rule_id)
        except Exception:
            result = applicable

        return result

    def _format_routing_message_with_books(self, rule_id: str) -> str:
        """Format routing message with authoritative book citation.

        AC-PHASE-06-S2-002: IntentRouter book reference enrichment.

        Args:
            rule_id: CORE rule ID (e.g. "CORE-008").

        Returns:
            Formatted string with book reference, or rule_id on failure.
        """
        try:
            from cortex.orchestrators.core.business_wisdom_formatter import (  # noqa: PLC0415
                BusinessWisdomFormatter,
            )
            formatter = BusinessWisdomFormatter()
            markdown = formatter.format_governance_with_books(
                rule_ids=[rule_id], max_display=1, include_icon=False
            )
            if markdown:
                for line in markdown.split("\n"):
                    if line.startswith("- "):
                        return line[2:].strip()
            return rule_id
        except Exception:
            return rule_id

    def route_with_lens_auto_fetch(
        self,
        request: Dict[str, Any],
        unified_intelligence: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Route request with automatic LENS context fetching and smart rule citations.

        Phase 20 Component #3: IntentRouter LENS Auto-Fetch.
        Phase 20.5 Component #4: Smart Rule Citations.

        Args:
            request: Request dict with intent, description, file_path, company_name, context.
            unified_intelligence: Optional UnifiedIntelligenceContext from MasterOrchestrator.

        Returns:
            Dict with intent, target_orchestrator, confidence_score, reasoning, context,
            and optionally cited_rules.
        """
        try:
            intent_str = request.get("intent", "")
            file_path = request.get("file_path")
            company_name = request.get("company_name")
            context = request.get("context", {})

            has_lens_context = "lens_insights" in context
            should_fetch = (
                not has_lens_context
                and intent_str in ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE"]
                and file_path is not None
            )

            if should_fetch:
                try:
                    from cortex.orchestrators.core.lens_context_provider import (  # noqa: PLC0415
                        get_lens_context_provider,
                    )
                    provider = get_lens_context_provider()
                    lens_data = provider.get_context(
                        intent=intent_str,
                        file_path=file_path,
                        company_name=company_name,
                    )
                    context.update(lens_data)
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-20-COMPONENT-3",
                        operation="LENS_AUTO_FETCH",
                        success=True,
                        details={
                            "intent": intent_str,
                            "file_path": file_path,
                            "company_name": company_name,
                            "context_size": len(str(lens_data)),
                        },
                    )
                except Exception as e:
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-20-COMPONENT-3",
                        operation="LENS_AUTO_FETCH_FAILED",
                        success=False,
                        details={"error": str(e)},
                    )

            routing_context = {
                "operation": request.get("description", ""),
                "description": request.get("description"),
                "domain": request.get("domain"),
                "keywords": request.get("keywords"),
                "user_intent": intent_str,
                "lens_context": context.get("lens_insights"),
            }

            decision = self.route(routing_context)  # type: ignore[attr-defined]

            enhanced_reasoning = decision.reasoning
            cited_rules: List[str] = []

            if unified_intelligence:
                try:
                    cited_rules = unified_intelligence.synthesis_result.citations
                    if cited_rules:
                        intent_rules = self._get_intent_applicable_rules(
                            intent_str, cited_rules, unified_intelligence
                        )
                        if intent_rules:
                            rule_text = ", ".join(intent_rules[:3])
                            enhanced_reasoning = (
                                f"{decision.reasoning} (Cited: {rule_text})"
                            )
                    violations = unified_intelligence.synthesis_result.violations
                    if violations:
                        enhanced_reasoning += f" ⚠️ {len(violations)} violation(s) detected"
                    self.logger.log_operation_complete(
                        ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                        operation="SMART_CITATIONS_APPLIED",
                        success=True,
                        details={
                            "intent": intent_str,
                            "cited_rules_count": len(cited_rules),
                            "violations_count": len(violations),
                        },
                    )
                except Exception as citation_err:
                    self.logger.log_operation_complete(
                        ac_id="AC-KNOWLEDGE-SYNTHESIS-001",
                        operation="SMART_CITATIONS_FAILED",
                        success=False,
                        details={"error": str(citation_err)},
                    )

            result: Dict[str, Any] = {
                "intent": decision.intent_type.value,
                "target_orchestrator": decision.target_handler,
                "confidence_score": decision.confidence_score,
                "reasoning": enhanced_reasoning,
                "context": context,
            }
            if cited_rules:
                result["cited_rules"] = cited_rules

            return result

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-20-COMPONENT-3",
                operation="ROUTING_WITH_AUTO_FETCH_ERROR",
                success=False,
                details={"error": str(e)},
            )
            return {
                "intent": request.get("intent", "UNKNOWN"),
                "target_orchestrator": "MasterOrchestrator",
                "confidence_score": 0.0,
                "reasoning": f"Error during routing: {str(e)}",
                "context": request.get("context", {}),
            }
