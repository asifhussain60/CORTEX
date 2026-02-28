"""tech_intelligence_orchestrator.py — Tech Intelligence Orchestrator.

Provides technology intelligence analysis and recommendations by inspecting
workspace context for language, framework, and dependency signals
(Phase 84-d, GAP-84-15). Produces structured insights for refactoring and
upgrade guidance.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations
from typing import Any
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94f


class TechIntelligenceOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Provides technology intelligence analysis and recommendations."""

    orchestrator_name = "TechIntelligenceOrchestrator"
    domain = "intelligence"

    # Phase 94f — advisory: intelligence analysis tool, not a code-execution entry point.
    # Invoked by domain orchestrators. Gateway routing deferred.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        """Initialise TechIntelligenceOrchestrator."""
        self._request_count = 0
        self._success_count = 0

    def analyse(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyse technical context for intelligence insights and recommendations.

        Inspects workspace context for language, framework, and dependency
        signals, then produces structured upgrade and refactoring insights.

        Args:
            context: Workspace or code context dictionary.

        Returns:
            Intelligence analysis result with insights and recommendations.
        """
        self._activate_cross_cutting_hooks(operation="analyse")
        self._request_count += 1
        insights: list[str] = []
        recommendations: list[str] = []

        language = context.get("language") or context.get("detected_language")
        if language:
            insights.append(f"Primary language detected: {language}")
            if language == "python":
                recommendations.append("Ensure pyproject.toml declares all dependencies")
            elif language in ("javascript", "typescript"):
                recommendations.append("Review package.json for outdated dependencies")

        frameworks = context.get("frameworks") or []
        for fw in frameworks:
            insights.append(f"Framework in use: {fw}")

        deps = context.get("dependencies") or []
        if deps:
            insights.append(f"{len(deps)} dependencies discovered")
            recommendations.append("Run dependency drift check: cortex_check_dependency_drift")

        if not insights:
            insights.append("No specific tech signals detected — provide richer context")

        self._success_count += 1
        return {"insights": insights, "recommendations": recommendations, "language": language, "status": "ok"}

    def health_check(self) -> dict[str, Any]:
        """Return orchestrator health status."""
        return {
            "status": "healthy",
            "orchestrator": self.orchestrator_name,
            "uptime_requests": self._request_count,
            "success_count": self._success_count,
            "last_success": None,
        }
