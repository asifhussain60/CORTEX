"""PhaseFileScaffolder — CAPE sub-phase 136-b.

Generates a CORTEX-compliant phase YAML string from a triage result
and a list of gap dicts.  Each gap becomes a sub-phase block with
``tdd_cycle``, ``convergence_gate``, and ``completion_gate``.

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064, CORE-068
AC-ID: AC-136-CAPE-002b
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import yaml

from cortex.orchestrators.core.complexity_triage_engine import TriageResult

_GOVERNANCE_AUTHORITY = "CORE-008, CORE-011, CORE-012, CORE-035, CORE-064, CORE-068"


class PhaseFileScaffolder:
    """Generate a CORTEX-standard phase YAML document.

    Produces a full phase YAML string suitable for writing to
    ``cortex-registry/planning/phases/planned/<phase-id>.yaml``.

    Usage::

        scaffolder = PhaseFileScaffolder()
        yaml_str = scaffolder.scaffold(
            phase_id="phase-auto-001",
            title="My Feature",
            triage=triage_result,
            gaps=[{"id": "GAP-001", "title": "First gap"}],
        )
    """

    def scaffold(
        self,
        *,
        phase_id: str,
        title: str,
        triage: TriageResult,
        gaps: List[Dict[str, Any]],
    ) -> str:
        """Build the phase YAML document.

        Args:
            phase_id: Unique phase identifier (e.g. ``"phase-auto-001"``).
            title:    Human-readable phase title.
            triage:   :class:`TriageResult` produced by
                      :class:`~cortex.orchestrators.core.complexity_triage_engine.ComplexityTriageEngine`.
            gaps:     List of gap dicts with at minimum ``id`` and ``title`` keys.

        Returns:
            YAML string representing the full phase document.
        """
        sub_phases = [
            self._build_sub_phase(gap=gap, phase_id=phase_id, index=i + 1)
            for i, gap in enumerate(gaps)
        ]

        doc: Dict[str, Any] = {
            "id": phase_id,
            "title": title,
            "created": str(date.today()),
            "status": "PLANNED",
            "priority": "P1",
            "complexity_band": triage.band.value,
            "cdr_score": round(triage.cdr_score, 4),
            "governance_authority": _GOVERNANCE_AUTHORITY,
            "sweep_catalogue": [
                {"id": gap["id"], "title": gap["title"], "status": "OPEN"}
                for gap in gaps
            ],
            "phases": sub_phases,
        }
        return yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_sub_phase(
        self, *, gap: Dict[str, Any], phase_id: str, index: int
    ) -> Dict[str, Any]:
        """Build one sub-phase block for a single gap.

        Args:
            gap:      Gap dict with ``id`` and ``title`` keys.
            phase_id: Parent phase identifier.
            index:    1-based sub-phase index within the parent.

        Returns:
            Dict representing one sub-phase YAML block.
        """
        sub_id = f"{phase_id}-{chr(ord('a') + index - 1)}"
        return {
            "id": sub_id,
            "title": gap.get("title", f"Sub-phase {index}"),
            "priority": "P1",
            "status": "PLANNED",
            "gap_refs": [gap["id"]],
            "governance_authority": _GOVERNANCE_AUTHORITY,
            "tdd_cycle": {
                "red": {
                    "action": f"Write ALL failing tests for {gap['id']}",
                    "gate": "make test-changed — ALL listed tests must FAIL",
                    "blocker": "Do NOT write implementation code until every listed test fails",
                },
                "green": {
                    "action": f"Implement production code for {gap['id']}",
                    "gate": "make test-changed — ALL tests must PASS",
                    "blocker": "Do NOT begin REFACTOR until every test passes",
                },
                "refactor": {
                    "action": "Type hints, docstrings, CORE-035 check",
                    "gate": "make test-smoke — zero regressions",
                    "blocker": "Do NOT mark sub-phase COMPLETE until REFACTOR gate passes",
                },
            },
            "convergence_gate": {
                "detect_step": "make test-smoke + ruff check --select=F401,F811",
                "fix_step": "Apply targeted fixes",
                "success_predicate": "p0_count == 0 and p1_count == 0 and new_failures == 0",
                "max_cycles": 3,
                "blocks_ac_complete": True,
            },
            "completion_gate": {
                "test_runner_command": "make test-changed",
                "zero_new_failures": True,
                "all_gap_refs_closed": True,
                "blocks_next_sub_phase": True,
            },
        }
