"""
Phase 57-d RED — AC marker coverage tests for domain orchestrators.

GAP-57-06: planning_orchestrator.py and domain_orchestrator.py must emit
           AC_START and AC_COMPLETE markers in their public methods.

AC-ID: AC-PHASE57-D-001
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
from pathlib import Path

import pytest


def _grep_ac_marker(file_path: Path, marker: str) -> list[str]:
    """Return all lines in file containing *marker*."""
    return [
        line.strip()
        for line in file_path.read_text().splitlines()
        if marker in line
    ]


class TestDomainACMarkers:
    """Verify AC_START / AC_COMPLETE markers exist in domain orchestrator source files."""

    REPO_ROOT = Path(__file__).parent.parent.parent.parent

    def test_planning_orchestrator_emits_ac_start(self) -> None:
        """planning_orchestrator.py must contain at least one AC_START marker."""
        path = self.REPO_ROOT / "cortex" / "orchestrators" / "domain" / "planning_orchestrator.py"
        hits = _grep_ac_marker(path, "AC_START")
        assert len(hits) >= 1, (
            "planning_orchestrator.py has no AC_START markers — GAP-57-06 not fixed."
        )

    def test_planning_orchestrator_emits_ac_complete_on_success(self) -> None:
        """planning_orchestrator.py must contain at least one AC_COMPLETE marker."""
        path = self.REPO_ROOT / "cortex" / "orchestrators" / "domain" / "planning_orchestrator.py"
        hits = _grep_ac_marker(path, "AC_COMPLETE")
        assert len(hits) >= 1, (
            "planning_orchestrator.py has no AC_COMPLETE markers."
        )

    def test_domain_orchestrator_emits_ac_start(self) -> None:
        """domain_orchestrator.py must contain at least one AC_START marker."""
        path = self.REPO_ROOT / "cortex" / "orchestrators" / "domain" / "domain_orchestrator.py"
        hits = _grep_ac_marker(path, "AC_START")
        assert len(hits) >= 1, (
            "domain_orchestrator.py has no AC_START markers — GAP-57-06 not fixed."
        )

    def test_domain_orchestrator_emits_ac_complete_on_success(self) -> None:
        """domain_orchestrator.py must contain at least two AC_COMPLETE markers (success + failure)."""
        path = self.REPO_ROOT / "cortex" / "orchestrators" / "domain" / "domain_orchestrator.py"
        hits = _grep_ac_marker(path, "AC_COMPLETE")
        assert len(hits) >= 2, (
            f"domain_orchestrator.py has only {len(hits)} AC_COMPLETE marker(s) — "
            "need ≥2 (success + failure path)."
        )


class TestDomainACMarkersRuntime:
    """Runtime verification: public methods must actually log AC markers."""

    def test_planning_orchestrator_process_logs_ac_start(self, caplog: pytest.LogCaptureFixture) -> None:
        """PlanningOrchestrator.process() must log AC_START at entry."""
        from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator  # noqa: PLC0415
        inst = PlanningOrchestrator()
        with caplog.at_level(logging.INFO):
            inst.process({"phases": []})
        assert any("AC_START" in r.message for r in caplog.records), (
            "PlanningOrchestrator.process() did not log AC_START."
        )

    def test_domain_orchestrator_execute_logs_ac_start(self, caplog: pytest.LogCaptureFixture) -> None:
        """DomainOrchestrator.execute() must log AC_START at entry."""
        from cortex.orchestrators.domain.domain_orchestrator import DomainOrchestrator  # noqa: PLC0415
        inst = DomainOrchestrator()
        with caplog.at_level(logging.INFO):
            inst.execute("d1", "create", {"domain": "test", "target": "x"})
        assert any("AC_START" in r.message for r in caplog.records), (
            "DomainOrchestrator.execute() did not log AC_START."
        )
