"""PlanningCoordinator for M21 planning-boundary split."""

from __future__ import annotations

from typing import Optional

from cortex.core.registry.registry_index_manager import RegistryIndexManager
from cortex.orchestrators.support.repo_plan_orchestrator import RepoPlanOrchestrator


class PlanningCoordinator:
    """Coordinates plan orchestration and request-boundary classification."""

    def __init__(
        self,
        repo_plan_orchestrator: Optional[RepoPlanOrchestrator] = None,
        registry_index_manager: Optional[RegistryIndexManager] = None,
    ) -> None:
        """Initialize coordinator.

        Args:
            repo_plan_orchestrator: Optional repo plan orchestrator.
            registry_index_manager: Optional registry index manager.
        """
        self._repo_plan_orchestrator = repo_plan_orchestrator
        self._registry_index_manager = registry_index_manager

    def classify_request_boundary(self, request_text: str) -> str:
        """Classify whether a request is plan-focused or rephrase-focused.

        Args:
            request_text: User request text.

        Returns:
            "REPHRASE" when request is rephrase/compression oriented, else "PLAN".
        """
        lowered = request_text.lower()
        if "rephrase" in lowered or "rewrite" in lowered or "distill" in lowered:
            return "REPHRASE"
        return "PLAN"
