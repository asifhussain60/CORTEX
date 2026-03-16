"""Golden Tests — VACUUM_PROTECTED_ROOTS canonical root guard (Phase 151-a)

Enforces:
  - VACUUM_PROTECTED_ROOTS frozenset exists and is immutable (GV-028, GV-033)
  - VacuumOrchestrator._is_protected() fail-safe semantics (GV-029)
  - All protected trees are skipped during vacuum operations (GV-029)

Phase: PHASE-151-a
CORE: CORE-008, CORE-035, GV-028, GV-029, GV-033
Source: GitHub Issue #18 — FB-20260312-006
"""

from pathlib import Path

import pytest

from cortex.orchestrators.health.constants import VACUUM_PROTECTED_ROOTS
from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_workspace(tmp_path: Path) -> Path:
    """Build a minimal workspace with protected + unprotected trees."""
    # Protected source directories
    for d in ("cortex", "tests", ".github", "scripts", "cortex-registry"):
        sub = tmp_path / d
        sub.mkdir()
        (sub / "keep_me.py").write_text("# protected\n")

    # docs (canonical documentation root)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "index.html").write_text("<html/>")

    # Unprotected clutter that may be touched
    (tmp_path / "junk_orphan").mkdir()
    (tmp_path / "TEMP_NOTES.txt").write_text("temp\n")

    return tmp_path


# ─── 1. Constant shape ───────────────────────────────────────────────────────

def test_vacuum_protected_roots_is_frozenset() -> None:
    """GV-028: VACUUM_PROTECTED_ROOTS must be a frozenset (immutable)."""
    assert isinstance(VACUUM_PROTECTED_ROOTS, frozenset)


def test_vacuum_protected_roots_contains_cortex() -> None:
    """GV-028: 'cortex' must be in VACUUM_PROTECTED_ROOTS."""
    assert "cortex" in VACUUM_PROTECTED_ROOTS


def test_vacuum_protected_roots_contains_tests() -> None:
    """GV-028: 'tests' must be in VACUUM_PROTECTED_ROOTS."""
    assert "tests" in VACUUM_PROTECTED_ROOTS


def test_vacuum_protected_roots_contains_required_entries() -> None:
    """GV-033: All mandatory roots must be present."""
    required = {"cortex", "cortex-registry", "tests", ".github", "scripts", "docs"}
    assert required.issubset(VACUUM_PROTECTED_ROOTS)


# ─── 2. _is_protected() semantics ────────────────────────────────────────────

def test_is_protected_returns_true_for_cortex_subpath(tmp_path: Path) -> None:
    """GV-029: _is_protected(cortex/foo) returns True."""
    _make_workspace(tmp_path)
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    assert vac._is_protected(tmp_path / "cortex" / "foo.py") is True


def test_is_protected_returns_false_for_temp(tmp_path: Path) -> None:
    """GV-029: _is_protected on unprotected path returns False."""
    _make_workspace(tmp_path)
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    unprotected = tmp_path / "junk_orphan" / "something.txt"
    assert vac._is_protected(unprotected) is False


def test_is_protected_unknown_path_returns_true(tmp_path: Path) -> None:
    """GV-029 fail-safe: a path outside workspace root returns True (protected)."""
    _make_workspace(tmp_path)
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    # Path that cannot be made relative to workspace_root → ValueError → True
    outside = Path("/tmp/some_external_dir/file.txt")
    assert vac._is_protected(outside) is True


# ─── 3. Vacuum skips protected trees ─────────────────────────────────────────

def test_vacuum_skips_cortex_source_directory(tmp_path: Path) -> None:
    """GV-029: run() dry_run leaves cortex/ tree untouched."""
    _make_workspace(tmp_path)
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    vac.run(dry_run=True)
    assert (tmp_path / "cortex" / "keep_me.py").exists()


def test_vacuum_skips_tests_directory(tmp_path: Path) -> None:
    """GV-029: run() dry_run leaves tests/ tree untouched."""
    _make_workspace(tmp_path)
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    vac.run(dry_run=True)
    assert (tmp_path / "tests" / "keep_me.py").exists()


def test_vacuum_skips_github_directory(tmp_path: Path) -> None:
    """GV-029: run() dry_run leaves .github/ tree untouched."""
    _make_workspace(tmp_path)
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    vac.run(dry_run=True)
    assert (tmp_path / ".github" / "keep_me.py").exists()
