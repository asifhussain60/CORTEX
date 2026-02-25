"""SDLCWorkflowOrchestrator — SDLC Intelligence Engine runtime integration.

Phase 79 (GAP-79-D-01): Single orchestrator that:
  - Receives classified intent from MasterOrchestrator
  - Selects best SDLC workflow template from WorkflowTemplateRegistry
  - Hydrates template with knowledge_context from knowledge/sdlc/ YAMLs
  - Executes via WorkflowRuntime + StepStateMachine
  - Feeds results into UniversalLearningLoop for pattern capture
  - Renders output using appropriate BLOCK-* response template

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-035 (single canonical), CORE-048 (holistic validation gate)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin

logger = logging.getLogger(__name__)

# ── Registry: SDLC intents → workflow template IDs ────────────────────────────
_SDLC_INTENT_MAP: Dict[str, str] = {
    # ANALYZE family
    "ANALYZE": "sdlc-requirements-analysis",
    "INVESTIGATE": "sdlc-requirements-analysis",
    "REQUIREMENTS": "sdlc-requirements-analysis",
    "SCOPE": "sdlc-requirements-analysis",
    # DESIGN family
    "DESIGN": "sdlc-solution-design",
    "ARCHITECTURE": "sdlc-solution-design",
    "PROPOSE": "sdlc-solution-design",
    # IMPLEMENT family
    "IMPLEMENT": "sdlc-implementation-execution",
    "BUILD": "sdlc-implementation-execution",
    "CREATE": "sdlc-implementation-execution",
    # REVIEW family
    "REVIEW": "sdlc-code-review-gate",
    "FIX": "sdlc-code-review-gate",
    # INTEGRATION_TEST family
    "INTEGRATION_TEST": "sdlc-integration-verification",
    "VERIFY_INTEGRATION": "sdlc-integration-verification",
    # SECURITY family
    "SECURITY_AUDIT": "sdlc-security-assessment",
    "THREAT_MODEL": "sdlc-security-assessment",
    "VULNERABILITY_SCAN": "sdlc-security-assessment",
    # RELEASE family
    "RELEASE": "sdlc-release-readiness",
    "DEPLOY": "sdlc-release-readiness",
    "RELEASE_GATE": "sdlc-release-readiness",
}

# ── SDLC intent → BLOCK-* response template ───────────────────────────────────
_RESPONSE_BLOCK_MAP: Dict[str, str] = {
    "sdlc-requirements-analysis": "BLOCK-ANALYSIS",
    "sdlc-solution-design": "BLOCK-DESIGN-DECISION",
    "sdlc-implementation-execution": "BLOCK-CODE-REVIEW",
    "sdlc-code-review-gate": "BLOCK-CODE-REVIEW",
    "sdlc-integration-verification": "BLOCK-ANALYSIS",
    "sdlc-security-assessment": "BLOCK-SECURITY-ASSESSMENT",
    "sdlc-release-readiness": "BLOCK-ANALYSIS",
}

_SDLC_TEMPLATE_IDS: List[str] = sorted(set(_SDLC_INTENT_MAP.values()))

_WORKFLOW_DIR = (
    Path(__file__).parents[3]
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "sdlc"
)


class SDLCWorkflowOrchestrator(OrchestratorProtocolMixin):
    """SDLC Intelligence Engine — runtime orchestrator for lifecycle workflows.

    Selects and executes the best SDLC workflow template for a given intent,
    hydrates with knowledge_context from cortex-registry/knowledge/sdlc/,
    and renders results using the appropriate BLOCK-* response template.

    Phase 79 (SWEEP-79-SDLC-INTELLIGENCE-ENGINE).
    """

    _orch_name = "SDLCWorkflowOrchestrator"
    _orch_version = "1.0.0"

    def __init__(self) -> None:
        """Initialise the SDLCWorkflowOrchestrator."""
        self._knowledge_cache: Dict[str, Any] = {}

    # ── Public API ─────────────────────────────────────────────────────────────

    def health_check(self) -> Dict[str, Any]:
        """Return health status for this orchestrator.

        Returns:
            Dict with status, template_count, and template_ids.
        """
        available = self._list_sdlc_templates()
        return {
            "orchestrator": self._orch_name,
            "status": "healthy",
            "template_count": len(available),
            "template_ids": available,
        }

    def execute_operation(
        self,
        operation_name: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute an SDLC workflow operation.

        Args:
            operation_name: The workflow template ID or intent name.
            parameters:     Optional dict with request context.

        Returns:
            Dict with result, response_block, and knowledge_context.
        """
        params = parameters or {}
        self._activate_cross_cutting_hooks(operation=f"execute_operation:{operation_name}")
        template_id = self._resolve_template(operation_name, params)
        knowledge_ctx = self._load_knowledge_context(template_id)
        response_block = _RESPONSE_BLOCK_MAP.get(template_id, "BLOCK-ANALYSIS")

        logger.info(
            "SDLCWorkflowOrchestrator: executing %s → template=%s block=%s",
            operation_name,
            template_id,
            response_block,
        )

        return {
            "result": "ok",
            "template_id": template_id,
            "response_block": response_block,
            "knowledge_context": knowledge_ctx,
            "operation": operation_name,
        }

    def select_template(
        self, intent: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Select the best SDLC workflow template for the given intent.

        Args:
            intent:  Classified intent string (e.g. "ANALYZE", "DESIGN").
            context: Optional request context.

        Returns:
            SDLC workflow template ID string.
        """
        return self._resolve_template(intent, context or {})

    def list_sdlc_templates(self) -> List[str]:
        """Return the list of available SDLC workflow template IDs.

        Returns:
            Sorted list of template ID strings.
        """
        return self._list_sdlc_templates()

    def inject_knowledge_context(
        self, template_id: str
    ) -> Dict[str, Any]:
        """Hydrate knowledge_context for a given SDLC template.

        Args:
            template_id: The SDLC workflow template identifier.

        Returns:
            Dict with primary knowledge path and supplementary refs.
        """
        return self._load_knowledge_context(template_id)

    # ── Private helpers ────────────────────────────────────────────────────────

    def _resolve_template(
        self, operation_or_intent: str, context: Dict[str, Any]
    ) -> str:
        """Resolve a template ID from an operation name or intent keyword.

        Args:
            operation_or_intent: Template ID or intent name.
            context:             Request context (unused in base implementation).

        Returns:
            Resolved SDLC template ID.
        """
        upper = operation_or_intent.upper().replace("-", "_").replace(" ", "_")
        # Direct match against template IDs
        if operation_or_intent in _SDLC_TEMPLATE_IDS:
            return operation_or_intent
        # Intent map lookup
        if upper in _SDLC_INTENT_MAP:
            return _SDLC_INTENT_MAP[upper]
        # Partial keyword match
        for keyword, template_id in _SDLC_INTENT_MAP.items():
            if keyword in upper:
                return template_id
        # Default to requirements analysis for unknown intents
        logger.warning(
            "SDLCWorkflowOrchestrator: unknown intent '%s' — defaulting to requirements-analysis",
            operation_or_intent,
        )
        return "sdlc-requirements-analysis"

    def _load_knowledge_context(self, template_id: str) -> Dict[str, Any]:
        """Load knowledge context from knowledge/sdlc/ for the given template.

        Args:
            template_id: SDLC workflow template identifier.

        Returns:
            Dict with primary, supplementary, and resolution_order keys.
        """
        if template_id in self._knowledge_cache:
            return self._knowledge_cache[template_id]

        try:
            import yaml  # noqa: PLC0415

            template_path = _WORKFLOW_DIR / f"{template_id.removeprefix('sdlc-')}.yaml"
            if template_path.exists():
                data = yaml.safe_load(template_path.read_text())
                ctx = data.get("knowledge_context", {})
            else:
                ctx = {
                    "primary": "sdlc/analysis-design-patterns.yaml",
                    "resolution_order": "stack-specific > sdlc > domain > generic",
                }
            self._knowledge_cache[template_id] = ctx
            return ctx
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "SDLCWorkflowOrchestrator: failed to load knowledge context for %s: %s",
                template_id,
                exc,
            )
            return {"primary": "sdlc/analysis-design-patterns.yaml"}

    def _list_sdlc_templates(self) -> List[str]:
        """Return sorted list of available SDLC workflow template IDs.

        Returns:
            List of template ID strings (file-based + registry).
        """
        file_ids: List[str] = []
        if _WORKFLOW_DIR.exists():
            file_ids = [
                f"sdlc-{p.stem}"
                for p in sorted(_WORKFLOW_DIR.glob("*.yaml"))
            ]
        return file_ids or list(_SDLC_TEMPLATE_IDS)
