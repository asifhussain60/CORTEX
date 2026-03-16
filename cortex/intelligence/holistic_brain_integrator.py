"""HolisticBrainIntegrator — unify request, intelligence, governance, and registry context.

Provides a single integration point for composing:
- Current request + prior session requests
- LENS/knowledge intelligence synthesis
- Governance policy signals
- Registry/workflow artifact awareness

The output is designed for runtime orchestration context and architecture-level
traceability so implementation and documentation stay aligned.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from cortex.intelligence.facade import get_intelligence_facade


class HolisticBrainIntegrator:
    """Build a unified execution context across CORTEX brain tiers and registry artifacts.

    Args:
        intelligence_facade: Optional injected facade for tests or alternate wiring.
            When omitted, uses the canonical ``get_intelligence_facade()`` singleton.
    """

    def __init__(self, intelligence_facade: Optional[Any] = None) -> None:
        self._intelligence_facade: Any = intelligence_facade or get_intelligence_facade()

    def build_unified_context(
        self,
        current_request: str,
        session_id: str,
        intent: str,
        execution_stages: Optional[list[str]] = None,
        request_log_manager: Optional[Any] = None,
        file_path: str = "",
    ) -> Dict[str, Any]:
        """Return a holistic runtime context for one request.

        Args:
            current_request: The active user request.
            session_id: Session identifier for prior-request lookup.
            intent: Classified or expected intent label.
            execution_stages: Optional stage list from orchestrator pipeline.
            request_log_manager: Optional ``RequestLogManager``-compatible object.
            file_path: Optional focal file path for intelligence analysis.

        Returns:
            Dict containing unified request, intelligence, governance, registry,
            and execution contract sections. Includes degradation metadata when
            non-fatal failures occur.
        """
        degradation_reasons: list[str] = []

        prior_requests = self._safe_get_prior_requests(
            request_log_manager=request_log_manager,
            session_id=session_id,
            limit=5,
        )

        intelligence_analysis = self._safe_analyze(
            file_path=file_path,
            intent=intent,
            degradation_reasons=degradation_reasons,
        )
        synthesis = self._safe_synthesize(
            query=current_request,
            degradation_reasons=degradation_reasons,
        )

        governance_rules = self._safe_load_governance(degradation_reasons=degradation_reasons)
        workflow_templates = self._safe_load_workflows(degradation_reasons=degradation_reasons)
        registry_entries = self._safe_registry_index(degradation_reasons=degradation_reasons)

        blocked_rules = [rule for rule in governance_rules if rule.get("severity") == "blocked"]
        warning_rules = [rule for rule in governance_rules if rule.get("severity") == "warning"]

        status = "ok" if len(degradation_reasons) == 0 else "degraded"
        return {
            "status": status,
            "request_context": {
                "session_id": session_id,
                "current_request": current_request,
                "intent": intent,
                "prior_request_count": len(prior_requests),
                "prior_requests": prior_requests,
            },
            "brain_tiers": {
                "interaction": {
                    "phase": "Stage 1 comprehension",
                    "source": "InteractionOrchestrator",
                },
                "intelligence": {
                    "analysis": intelligence_analysis,
                    "synthesis": synthesis,
                },
                "execution": {
                    "phase": "MasterOrchestrator execution pipeline",
                    "stages": execution_stages or [],
                },
            },
            "governance_policy": {
                "total_rules": len(governance_rules),
                "blocked_rules": len(blocked_rules),
                "warning_rules": len(warning_rules),
            },
            "registry_artifacts": {
                "workflow_templates": len(workflow_templates),
                "registry_entries": len(registry_entries),
            },
            "execution_contract": {
                "stages": execution_stages or [],
                "quality_security_embedded": True,
            },
            "degradation_reasons": degradation_reasons,
        }

    def _safe_get_prior_requests(
        self,
        request_log_manager: Optional[Any],
        session_id: str,
        limit: int,
    ) -> list[Dict[str, Any]]:
        """Safely fetch prior requests from the request log manager."""
        if request_log_manager is None:
            return []
        try:
            return list(request_log_manager.get_prior_requests(session_id=session_id, limit=limit))
        except Exception:
            return []

    def _safe_analyze(
        self,
        file_path: str,
        intent: str,
        degradation_reasons: list[str],
    ) -> Dict[str, Any]:
        """Safely run intelligence analysis through the facade."""
        try:
            return dict(self._intelligence_facade.analyze(file_path=file_path, intent=intent))
        except Exception as exc:
            degradation_reasons.append(f"analyze:{exc}")
            return {"status": "error", "analysis": {}}

    def _safe_synthesize(self, query: str, degradation_reasons: list[str]) -> Dict[str, Any]:
        """Safely run synthesis through the facade."""
        try:
            return dict(self._intelligence_facade.synthesize(query=query))
        except Exception as exc:
            degradation_reasons.append(f"synthesize:{exc}")
            return {"status": "error", "synthesis": {}}

    def _safe_load_governance(self, degradation_reasons: list[str]) -> list[Dict[str, Any]]:
        """Safely load governance rules through the facade."""
        try:
            return list(self._intelligence_facade.load_governance())
        except Exception as exc:
            degradation_reasons.append(f"load_governance:{exc}")
            return []

    def _safe_load_workflows(self, degradation_reasons: list[str]) -> list[Dict[str, Any]]:
        """Safely load workflow templates through the facade."""
        try:
            return list(self._intelligence_facade.load_workflows())
        except Exception as exc:
            degradation_reasons.append(f"load_workflows:{exc}")
            return []

    def _safe_registry_index(self, degradation_reasons: list[str]) -> list[Any]:
        """Safely load registry index entries through the facade."""
        try:
            return list(self._intelligence_facade.registry_index())
        except Exception as exc:
            degradation_reasons.append(f"registry_index:{exc}")
            return []