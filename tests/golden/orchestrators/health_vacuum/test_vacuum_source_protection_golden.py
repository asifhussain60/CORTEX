"""Golden Tests — VacuumOrchestrator Source Protection (GV-012 .. GV-019)

Enforces that VacuumOrchestrator NEVER modifies files inside protected source
directories regardless of configuration or operating mode.

Phase: PHASE-141
CORE: CORE-008 (TDD), CORE-055 (golden test tier contract)
Source: GitHub Issue #17 — FB-2026-03-09-074435-002
"""

from pathlib import Path

import pytest

from cortex.orchestrators.health.constants import PROTECTED_DIRS
from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_workspace(tmp_path: Path) -> Path:
    """Build a minimal workspace with source dirs and some unprotected clutter."""
    # Protected source directories
    cortex_dir = tmp_path / "cortex"
    cortex_dir.mkdir()
    (cortex_dir / "__init__.py").write_text("")
    (cortex_dir / "some_module.py").write_text("x = 1\n")

    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_something.py").write_text("def test_pass(): pass\n")

    # Non-protected clutter that SHOULD be cleaned
    (tmp_path / "TEMP_FILE.txt").write_text("temp\n")
    junk_dir = tmp_path / "junk_orphan"
    junk_dir.mkdir()

    return tmp_path


# ─────────────────────────────────────────────────────────────────────────────
# GV-012: cortex/ source directory never modified by run()
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_012_cortex_source_directory_never_modified(tmp_path: Path) -> None:
    """GV-012: VacuumOrchestrator.run() must not rename/delete/move any file inside cortex/."""
    _make_workspace(tmp_path)
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    report = vac.run(dry_run=False)

    for op in report.operations:
        src = op.source
        if src is None:
            continue
        src_path = Path(src) if not isinstance(src, Path) else src
        try:
            rel = src_path.relative_to(tmp_path)
        except ValueError:
            continue
        assert rel.parts[0] != "cortex", (
            f"GV-012 FAIL: VacuumOrchestrator modified file inside cortex/: {src_path}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GV-013: cortex present in PROTECTED_DIRS constant
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_013_cortex_in_protected_dirs_constant() -> None:
    """GV-013: 'cortex' MUST appear in PROTECTED_DIRS."""
    assert "cortex" in PROTECTED_DIRS, (
        "GV-013 FAIL: 'cortex' is not in PROTECTED_DIRS — source protection invariant broken."
    )


# ─────────────────────────────────────────────────────────────────────────────
# GV-014: _plan_naming_fixes skips all files inside cortex/
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_014_naming_fixes_skip_cortex_files(tmp_path: Path) -> None:
    """GV-014: A file in cortex/ that would normally be renamed must be skipped."""
    cortex_dir = tmp_path / "cortex"
    cortex_dir.mkdir()
    # Uppercase filename that would normally be a naming violation
    (cortex_dir / "MY-MODULE.py").write_text("pass\n")

    vac = VacuumOrchestrator(workspace_root=tmp_path)
    report = vac.run(dry_run=True)

    for op in report.operations:
        if op.op_type != "rename":
            continue
        src = op.source
        if src is None:
            continue
        src_path = Path(src) if not isinstance(src, Path) else src
        try:
            rel = src_path.relative_to(tmp_path)
        except ValueError:
            continue
        assert rel.parts[0] != "cortex", (
            f"GV-014 FAIL: Naming fix planned for file inside cortex/: {src_path}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GV-015: Empty file cleanup never deletes inside cortex/
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_015_empty_cleanup_never_deletes_inside_cortex(tmp_path: Path) -> None:
    """GV-015: An empty file inside cortex/ must not be deleted by VacuumOrchestrator."""
    cortex_dir = tmp_path / "cortex"
    cortex_dir.mkdir()
    (cortex_dir / "__init__.py").write_text("")  # Empty __init__.py

    vac = VacuumOrchestrator(workspace_root=tmp_path)
    report = vac.run(dry_run=True)

    for op in report.operations:
        if op.op_type != "delete":
            continue
        src = op.source
        if src is None:
            continue
        src_path = Path(src) if not isinstance(src, Path) else src
        try:
            rel = src_path.relative_to(tmp_path)
        except ValueError:
            continue
        assert rel.parts[0] != "cortex", (
            f"GV-015 FAIL: Delete planned for file inside cortex/: {src_path}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GV-016: Markdown archival never moves files from cortex/
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_016_markdown_archival_never_moves_from_cortex(tmp_path: Path) -> None:
    """GV-016: A Markdown file inside cortex/ must not be archived/moved by Vacuum."""
    cortex_dir = tmp_path / "cortex"
    cortex_dir.mkdir()
    (cortex_dir / "design-notes.md").write_text("# Notes\n")

    vac = VacuumOrchestrator(workspace_root=tmp_path)
    report = vac.run(dry_run=True)

    for op in report.operations:
        if op.op_type not in {"archive", "move", "rename"}:
            continue
        src = op.source
        if src is None:
            continue
        src_path = Path(src) if not isinstance(src, Path) else src
        try:
            rel = src_path.relative_to(tmp_path)
        except ValueError:
            continue
        assert rel.parts[0] != "cortex", (
            f"GV-016 FAIL: Archive/move planned for markdown inside cortex/: {src_path}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GV-017: tests/ directory never modified by run()
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_017_tests_directory_never_modified(tmp_path: Path) -> None:
    """GV-017: VacuumOrchestrator.run() must not rename/delete/move any file inside tests/."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_example.py").write_text("def test_pass(): pass\n")

    vac = VacuumOrchestrator(workspace_root=tmp_path)
    report = vac.run(dry_run=False)

    for op in report.operations:
        src = op.source
        if src is None:
            continue
        src_path = Path(src) if not isinstance(src, Path) else src
        try:
            rel = src_path.relative_to(tmp_path)
        except ValueError:
            continue
        assert rel.parts[0] != "tests", (
            f"GV-017 FAIL: VacuumOrchestrator modified file inside tests/: {src_path}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GV-018: validate_safe_run() returns empty list for safe workspace
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_018_validate_safe_run_returns_empty_for_safe_workspace(tmp_path: Path) -> None:
    """GV-018: validate_safe_run() must return [] when workspace only has non-protected clutter."""
    # Only create non-protected clutter
    (tmp_path / "TEMP.txt").write_text("temp\n")
    orphan = tmp_path / "orphan"
    orphan.mkdir()

    vac = VacuumOrchestrator(workspace_root=tmp_path)
    warnings = vac.validate_safe_run()
    assert isinstance(warnings, list), "GV-018 FAIL: validate_safe_run() must return a list"
    assert len(warnings) == 0, (
        f"GV-018 FAIL: expected empty warnings for safe workspace, got: {warnings}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# GV-019: Non-protected files are still cleaned (no over-protection)
# ─────────────────────────────────────────────────────────────────────────────

def test_gv_019_non_protected_files_are_still_cleaned(tmp_path: Path) -> None:
    """GV-019: Vacuum must still process non-protected clutter after protection hardening."""
    # OS artifact at workspace root (reliably cleaned by _plan_os_artifact_ops)
    ds_store = tmp_path / ".DS_Store"
    ds_store.write_text("")

    vac = VacuumOrchestrator(workspace_root=tmp_path)
    report = vac.run(dry_run=True)

    # There should be at least one planned operation (the .DS_Store deletion)
    assert len(report.operations) > 0, (
        "GV-019 FAIL: Vacuum produced zero operations — non-protected clutter should still be "
        "processed. Protection hardening must not disable all cleanup."
    )
