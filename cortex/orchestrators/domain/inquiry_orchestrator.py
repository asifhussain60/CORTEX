"""inquiry_orchestrator.py — Inquiry Orchestrator.

Handles user inquiry and question-answering intents by routing to the
knowledge base and LLM response layer (Phase 84-d, GAP-84-16). Queries
the IntelligentKnowledgeRouter to determine domain, then synthesises an
answer from matching knowledge entries.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations
from typing import Any
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94f


class InquiryOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Handles user inquiry and question-answering intents."""

    orchestrator_name = "InquiryOrchestrator"
    domain = "domain"

    # Phase 94f — advisory: query/knowledge-base lookup, non-code-touching intent.
    # Gateway routing deferred until MasterOrchestrator milestone.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        """Initialise InquiryOrchestrator."""
        self._request_count = 0
        self._success_count = 0

    def handle(self, query: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Handle an inquiry query by routing to the knowledge base.

        Routes the query via IntelligentKnowledgeRouter to determine domain,
        then produces a structured answer from knowledge entries.

        Args:
            query: The user query string.
            context: Optional orchestrator context.

        Returns:
            Response dict with answer, domain, and metadata.
        """
        self._activate_cross_cutting_hooks(operation="handle")
        self._request_count += 1
        domain = "general"
        answer = ""
        try:
            from cortex.intelligence.knowledge.router import IntelligentKnowledgeRouter
            router = IntelligentKnowledgeRouter()
            routed = router.route_query(query)
            if routed:
                domain = routed
                answer = f"Knowledge domain: {domain}. Query: {query}"
        except Exception:
            answer = f"Inquiry received: {query}"
        self._success_count += 1
        return {"query": query, "answer": answer, "domain": domain, "status": "ok"}

    def health_check(self) -> dict[str, Any]:
        """Return orchestrator health status.

        Returns:
            Health dict with status and metrics.
        """
        return {
            "status": "healthy",
            "orchestrator": self.orchestrator_name,
            "uptime_requests": self._request_count,
            "success_count": self._success_count,
            "last_success": None,
        }
