"""Phase M13 closure contract tests."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_phase_m13_cleanup_contract_is_complete() -> None:
    """Phase M13 closes all gaps and captures expected dependencies."""
    phase = yaml.safe_load(
        (REPO_ROOT / "cortex-registry/planning/phases/v2/phase-m13-repo-cleanup.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert phase["id"] == "phase-m13"
    assert phase["status"] == "COMPLETE"
    assert phase["depends_on"] == ["phase-m12", "phase-m14", "phase-m15"]
    assert all(item["status"] == "CLOSED" for item in phase["sweep_catalogue"])


def test_phase_m13_release_report_completion_marker() -> None:
    """Release report records a terminal M13 completion marker."""
    report = yaml.safe_load(
        (REPO_ROOT / "cortex-registry/planning/phases/v2/phase-m13-release-report.yaml").read_text(
            encoding="utf-8"
        )
    )

    release_report = report["release_report"]
    assert release_report["completion_marker"] == "✅ Phase M13 complete."
    assert "All migration phases complete" in release_report["next_phase"]
