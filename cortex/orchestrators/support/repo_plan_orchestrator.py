"""RepoPlanOrchestrator wrapper for repository-scoped plan setup."""

from __future__ import annotations

from typing import Any, Dict, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.orchestrators.support.plan_orchestrator import PlanOrchestrator, PlanSetupResult


class RepoPlanOrchestrator(OrchestratorProtocolMixin):
    """Repository-scoped facade around PlanOrchestrator."""

    _orch_name = "RepoPlanOrchestrator"
    _orch_version = "1.0.0"

    def __init__(self, plan_orchestrator: Optional[PlanOrchestrator] = None) -> None:
        """Initialize wrapper.

        Args:
            plan_orchestrator: Optional injected PlanOrchestrator.
        """
        self._plan_orchestrator = plan_orchestrator if plan_orchestrator is not None else PlanOrchestrator()

    def setup_plan(self, plan_id: str, metadata: Optional[Dict[str, Any]] = None) -> PlanSetupResult:
        """Create a repository-scoped plan."""
        self._activate_cross_cutting_hooks(
            operation="setup_plan",
            orchestrator_context=metadata if isinstance(metadata, dict) else None,
        )
        return self._plan_orchestrator.setup_plan(plan_id, metadata)
