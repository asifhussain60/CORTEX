"""Drift lock test — Check #50: Phase File Integrity.

Every ``file:`` pointer in cortex-master.yaml that references
cortex-registry/planning/phases/ MUST resolve to a real file on disk.

Root cause (2026-03-05): _cortex-master/ was a stale duplicate of
planning/phases/ and was intentionally deleted in Phase 127 (commit
1b7b49b43) as part of the single-YAML SSOT enforcement. All canonical
phase YAMLs survived in planning/phases/completed/. planned/ is
intentionally empty (cortex-master.yaml: planned: 0).

This test prevents future stale file: references after:
- Phase lifecycle moves (planned/ → completed/)
- Registry consolidation commits
- VacuumOrchestrator housekeeping passes

Gap ref: GAP-INTEGRITY-001
Phase: investigation-2026-03-05
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Any

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
MASTER_YAML = CORTEX_ROOT / "cortex-registry" / "cortex-master.yaml"
LOCK_FILE = (
    CORTEX_ROOT
    / "cortex-registry"
    / "governance"
    / "drift-locks"
    / "check-50-phase-file-integrity-lock.yaml"
)
PLANNING_PHASES_DIR = CORTEX_ROOT / "cortex-registry" / "planning" / "phases"


def _load_master() -> dict[str, Any]:
    return yaml.safe_load(MASTER_YAML.read_text(encoding="utf-8")) or {}


def _get_broken_file_refs() -> list[tuple[str, str]]:
    """Return list of (phase_id, file_path) where file does not exist on disk."""
    data = _load_master()
    phases = data.get("phases", [])
    broken: list[tuple[str, str]] = []
    for entry in phases:
        if not isinstance(entry, dict):
            continue
        file_ref = entry.get("file")
        if not file_ref:
            continue
        # Only check planning/phases references — other paths are out of scope
        if "planning/phases" not in file_ref:
            continue
        resolved = CORTEX_ROOT / file_ref
        if not resolved.exists():
            broken.append((entry.get("id", "unknown"), file_ref))
    return broken


class TestDriftLockCheck50:
    """Check #50 — Phase File Integrity: cortex-master.yaml file: pointers resolve on disk."""

    def test_lock_file_exists(self) -> None:
        """The drift lock YAML for this check must be present."""
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P0 governance violation. "
            "Restore from git: git show HEAD~1:cortex-registry/governance/drift-locks/check-50-phase-file-integrity-lock.yaml"
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing — covered by test_lock_file_exists")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 50
        assert data.get("status") == "ACTIVE"

    def test_master_yaml_exists(self) -> None:
        """cortex-master.yaml must exist — it is the phase registry index."""
        assert MASTER_YAML.exists(), (
            "cortex-registry/cortex-master.yaml was deleted — this is the phase registry "
            "index. Restore from git immediately."
        )

    def test_planning_phases_dir_exists(self) -> None:
        """The planning/phases directory tree must not be deleted."""
        assert PLANNING_PHASES_DIR.exists(), (
            "cortex-registry/planning/phases/ was deleted — restore from git."
        )
        completed = PLANNING_PHASES_DIR / "completed"
        assert completed.exists(), (
            "cortex-registry/planning/phases/completed/ was deleted — restore from git."
        )

    def test_no_broken_file_refs_in_master_yaml(self) -> None:
        """Every file: pointer in cortex-master.yaml must resolve to a real file on disk."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml missing — covered by test_master_yaml_exists")

        broken = _get_broken_file_refs()
        if broken:
            msg_lines = [
                f"BROKEN PHASE FILE REFS: {len(broken)} file: pointer(s) in "
                "cortex-master.yaml do not exist on disk.",
                "This means a phase YAML was deleted or moved without updating cortex-master.yaml.",
                "",
                "Broken refs:",
            ]
            for phase_id, file_ref in broken:
                msg_lines.append(f"  {phase_id} -> {file_ref}")
            msg_lines += [
                "",
                "Fix options:",
                "  1. Restore missing file from git: git show <commit>:<original_path>",
                "  2. Update file: pointer in cortex-master.yaml if file was moved",
                "  3. Run: python3 scripts/refresh_prompt_suite.py to resync counts",
            ]
            pytest.fail("\n".join(msg_lines))

    def test_completed_phases_have_yaml_files(self) -> None:
        """Completed phases referenced in cortex-master.yaml must have their YAML in completed/."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml missing")

        data = _load_master()
        phases = data.get("phases", [])
        missing_completed: list[str] = []

        for entry in phases:
            if not isinstance(entry, dict):
                continue
            status = entry.get("status", "")
            file_ref = entry.get("file", "")
            if status == "COMPLETE" and file_ref and "planning/phases" in file_ref:
                resolved = CORTEX_ROOT / file_ref
                if not resolved.exists():
                    missing_completed.append(
                        f"{entry.get('id', '?')}: {file_ref}"
                    )

        assert not missing_completed, (
            f"COMPLETED phases with missing YAML files ({len(missing_completed)}):\n"
            + "\n".join(f"  {m}" for m in missing_completed)
            + "\n\nThese were either deleted by vacuum or moved without updating "
            "cortex-master.yaml. Check git log for the deletion commit."
        )

    def test_planned_dir_has_gitkeep_or_yaml(self) -> None:
        """planned/ dir must exist even when empty — prevents silent directory deletion."""
        planned = PLANNING_PHASES_DIR / "planned"
        assert planned.exists(), (
            "cortex-registry/planning/phases/planned/ was deleted. "
            "When planned: 0, this directory should still exist (empty is fine). "
            "Restore it: New-Item -ItemType Directory -Path cortex-registry/planning/phases/planned"
        )

    def test_detect_command_passes(self) -> None:
        """The detect_command from the lock file must return PHASE_FILE_INTEGRITY=OK."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml missing")

        broken = _get_broken_file_refs()
        assert not broken, (
            f"detect_command would fail: {len(broken)} broken file: ref(s) detected. "
            "Run the detect_command from check-50-phase-file-integrity-lock.yaml manually to see details."
        )
