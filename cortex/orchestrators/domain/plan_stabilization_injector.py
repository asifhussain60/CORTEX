"""PlanStabilizationInjector — CAPE sub-phase 136-d.

Injects convergence-cleanup sub-phases after every implementation
phase and appends a single 9-check holistic stabilization final phase
that depends_on all predecessors.

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064, CORE-068
AC-ID: AC-136-CAPE-004b
"""

from __future__ import annotations

from typing import Any, Dict, List

_HOLISTIC_CHECKS: List[str] = [
    "regression",
    "threat-model",
    "quality",
    "security",
    "dead-code",
    "duplicates",
    "type-hints",
    "docstrings",
    "convergence",
]

assert len(_HOLISTIC_CHECKS) == 9, "Holistic stabilization must have exactly 9 checks"


class PlanStabilizationInjector:
    """Inject stabilization phases into a CAPE phase list.

    For each implementation phase a lightweight convergence-cleanup
    sub-phase is appended immediately after it.  A single holistic
    stabilization final phase (9 checks) is appended last, depending
    on every predecessor.

    Usage::

        injector = PlanStabilizationInjector()
        stabilized = injector.inject_stabilization(phases)
    """

    def inject_stabilization(
        self, phases: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build a stabilized phase list.

        Args:
            phases: Original list of phase dicts (each must have ``"id"``).

        Returns:
            New list with cleanup sub-phases after each implementation
            phase, followed by the holistic stabilization final phase.
        """
        result: List[Dict[str, Any]] = []
        for phase in phases:
            result.append(phase)
            result.append(self._create_convergence_cleanup(phase["id"]))

        all_ids = [p["id"] for p in result]
        result.append(self._create_holistic_stabilization(all_ids))
        return result

    # ------------------------------------------------------------------
    # Private builders
    # ------------------------------------------------------------------

    @staticmethod
    def _create_convergence_cleanup(impl_phase_id: str) -> Dict[str, Any]:
        """Build a convergence-cleanup sub-phase for one implementation phase.

        Args:
            impl_phase_id: ID of the implementation phase this follows.

        Returns:
            Phase dict for the cleanup sub-phase.
        """
        cleanup_id = f"{impl_phase_id}-cleanup"
        return {
            "id": cleanup_id,
            "title": f"Convergence Cleanup — post {impl_phase_id}",
            "priority": "P1",
            "status": "PLANNED",
            "depends_on": [impl_phase_id],
            "governance_authority": "CORE-064, CORE-068",
            "tdd_cycle": {
                "red":    {"action": "N/A — verification only"},
                "green":  {"action": "Run detect-fix-rescan loop until 0 P0/P1"},
                "refactor": {"action": "Confirm ruff clean + type hints + docstrings"},
            },
        }

    @staticmethod
    def _create_holistic_stabilization(all_predecessor_ids: List[str]) -> Dict[str, Any]:
        """Build the 9-check holistic stabilization final phase.

        Args:
            all_predecessor_ids: IDs of all phases that come before this one.

        Returns:
            Phase dict for the holistic stabilization phase.
        """
        return {
            "id": "holistic-stabilization",
            "title": "Holistic Stabilization — 9-check final gate",
            "priority": "P1",
            "status": "PLANNED",
            "depends_on": list(all_predecessor_ids),
            "governance_authority": "CORE-048, CORE-064, CORE-068",
            "checks": list(_HOLISTIC_CHECKS),
            "tdd_cycle": {
                "red":    {"action": "N/A — final verification gate"},
                "green":  {"action": "Execute all 9 checks; each must pass"},
                "refactor": {"action": "Document outcomes; mark phase COMPLETE"},
            },
        }
