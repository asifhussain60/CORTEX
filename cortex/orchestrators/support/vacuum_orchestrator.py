"""
VacuumOrchestrator — support-tier protocol adapter.

Delegates all workspace-cleanup operations to the canonical
implementation in ``cortex.orchestrators.health.vacuum_orchestrator``.

This module exists so that ``cortex.orchestrators.support.vacuum_orchestrator``
satisfies the wiring contract in ``cortex/core/wiring/specifications/wiring.yaml``
(where VacuumOrchestrator is registered under the *support* tier) while keeping
the full implementation in the health module (CORE-035: single canonical implementation).

Phase: PHASE-13 (Base-Class Convergence)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-028 (naming), CORE-035 (single canonical)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.result import Ok, Result
from cortex.orchestrators.health.vacuum_orchestrator import (
    VacuumOrchestrator as _HealthVacuumOrchestrator,
)


class VacuumOrchestrator(_HealthVacuumOrchestrator):
    """Support-tier adapter for VacuumOrchestrator.

    Inherits the full standalone + companion remediation engine from
    :class:`cortex.orchestrators.health.vacuum_orchestrator.VacuumOrchestrator`
    and adds the orchestration protocol methods (``get_name``, ``get_version``,
    ``initialize``) required by the wiring contract.

    Usage::

        vac = VacuumOrchestrator(Path("/project"))
        report = vac.run()          # quick-scan + execute
        report = vac.run(dry_run=True)  # preview only
    """

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialise the VacuumOrchestrator.

        Args:
            workspace_root: Root of the workspace to clean.
                Defaults to the current working directory when omitted
                (allows zero-argument instantiation for protocol checks).
        """
        super().__init__(workspace_root or Path.cwd())

    # ──────────────────────────────────────────────────────────────────────────
    # Orchestration Protocol
    # ──────────────────────────────────────────────────────────────────────────

    def get_name(self) -> str:
        """Return the canonical orchestrator name.

        Returns:
            The string ``"VacuumOrchestrator"``.
        """
        return "VacuumOrchestrator"

    def get_version(self) -> str:
        """Return the orchestrator version string.

        Returns:
            Semantic version string.
        """
        return "1.0.0"

    def initialize(self) -> Any:
        """Initialise the orchestrator (setup already done in ``__init__``).

        Activates cross-cutting hooks (CORE-058 Phase 58 contract).

        Returns:
            A :class:`~cortex.core.result.Result` success value.
        """
        self._activate_cross_cutting_hooks(operation="initialize")
        return Ok("VacuumOrchestrator initialized")

    def health_check(self) -> Dict[str, Any]:
        """Return health status of this orchestrator.

        Returns:
            Mapping with ``status``, ``orchestrator``, and ``workspace_root`` keys.
        """
        return {
            "status": "healthy",
            "orchestrator": self.get_name(),
            "workspace_root": str(self.workspace_root),
        }


__all__ = ["VacuumOrchestrator"]
