"""Tests for VacuumOrchestrator recency guard (GAP-130-01).

Files modified within VACUUM_RECENCY_GUARD_HOURS (24 h) must NEVER appear
in any vacuum deletion or archival plan — regardless of which plan stage
produces the operation.

AC-ID: AC-VAC-RECENCY-001
GAP-REF: GAP-130-01 (Phase 130-a — Foundation Backport)
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import List, Dict, Any

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _touch_old(path: Path, hours_ago: float = 30.0) -> None:
    """Set a file's mtime so that it appears *older* than the guard window."""
    path.write_text("")
    old_mtime = time.time() - (hours_ago * 3600)
    os.utime(path, (old_mtime, old_mtime))


def _touch_recent(path: Path, hours_ago: float = 0.5) -> None:
    """Set a file's mtime so that it appears *within* the guard window."""
    path.write_text("")
    recent_mtime = time.time() - (hours_ago * 3600)
    os.utime(path, (recent_mtime, recent_mtime))


def _sources(ops: List[Dict[str, Any]]) -> List[Path]:
    """Extract the 'source' paths from a list of planned ops."""
    return [op["source"] for op in ops]


# ---------------------------------------------------------------------------
# Constant export tests
# ---------------------------------------------------------------------------

class TestVacuumRecencyConstant:
    """VACUUM_RECENCY_GUARD_HOURS must be importable from constants."""

    def test_constant_exists(self) -> None:
        """VACUUM_RECENCY_GUARD_HOURS must be defined in constants module."""
        from cortex.orchestrators.health.constants import VACUUM_RECENCY_GUARD_HOURS  # noqa: F401

    def test_constant_is_int(self) -> None:
        """VACUUM_RECENCY_GUARD_HOURS must be a positive integer."""
        from cortex.orchestrators.health.constants import VACUUM_RECENCY_GUARD_HOURS

        assert isinstance(VACUUM_RECENCY_GUARD_HOURS, int)
        assert VACUUM_RECENCY_GUARD_HOURS > 0

    def test_constant_default_value(self) -> None:
        """Default value must be 24 hours."""
        from cortex.orchestrators.health.constants import VACUUM_RECENCY_GUARD_HOURS

        assert VACUUM_RECENCY_GUARD_HOURS == 24

    def test_constant_in_dunder_all(self) -> None:
        """VACUUM_RECENCY_GUARD_HOURS must be listed in __all__."""
        import cortex.orchestrators.health.constants as const_mod

        assert "VACUUM_RECENCY_GUARD_HOURS" in const_mod.__all__


# ---------------------------------------------------------------------------
# _is_recent() method tests
# ---------------------------------------------------------------------------

class TestVacuumIsRecentMethod:
    """VacuumOrchestrator._is_recent() private guard method."""

    def test_method_exists(self) -> None:
        """VacuumOrchestrator must expose _is_recent()."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        assert hasattr(VacuumOrchestrator, "_is_recent"), (
            "_is_recent() missing from VacuumOrchestrator"
        )

    def test_recent_file_returns_true(self, tmp_path: Path) -> None:
        """A file touched <1 h ago must be flagged as recent."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        f = tmp_path / "recent.txt"
        _touch_recent(f, hours_ago=0.5)
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        assert vacuum._is_recent(f) is True

    def test_old_file_returns_false(self, tmp_path: Path) -> None:
        """A file touched 30 h ago must NOT be flagged as recent."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        f = tmp_path / "old.txt"
        _touch_old(f, hours_ago=30)
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        assert vacuum._is_recent(f) is False

    def test_exactly_on_boundary_is_not_recent(self, tmp_path: Path) -> None:
        """A file touched exactly 24 h ago is NOT recent (guard is strict <)."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        from cortex.orchestrators.health.constants import VACUUM_RECENCY_GUARD_HOURS

        f = tmp_path / "boundary.txt"
        boundary_mtime = time.time() - (VACUUM_RECENCY_GUARD_HOURS * 3600)
        f.write_text("")
        os.utime(f, (boundary_mtime, boundary_mtime))
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        assert vacuum._is_recent(f) is False

    def test_missing_file_returns_true(self, tmp_path: Path) -> None:
        """If stat fails (race condition / missing file), treat as recent (safe default)."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        f = tmp_path / "ghost.txt"  # never created
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        assert vacuum._is_recent(f) is True


# ---------------------------------------------------------------------------
# _plan_empty_cleanup guard
# ---------------------------------------------------------------------------

class TestRecencyGuardInEmptyCleanup:
    """Recent zero-byte files must be excluded from _plan_empty_cleanup."""

    def test_recent_empty_file_not_in_plan(self, tmp_path: Path) -> None:
        """A zero-byte file modified <24 h ago must NOT appear in the deletion plan."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        recent_empty = tmp_path / "recent_empty.txt"
        # Write empty bytes, then set mtime to 1 h ago
        recent_empty.write_bytes(b"")
        recent_mtime = time.time() - 1 * 3600
        os.utime(recent_empty, (recent_mtime, recent_mtime))

        ctx = FileContext(workspace_root=tmp_path, all_files=[recent_empty], directories=[])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_empty_cleanup(ctx)
        assert recent_empty not in _sources(ops), (
            "Recent empty file should be protected by recency guard"
        )

    def test_old_empty_file_is_in_plan(self, tmp_path: Path) -> None:
        """A zero-byte file modified 30 h ago MUST appear in the deletion plan."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        old_empty = tmp_path / "old_empty.txt"
        old_empty.write_bytes(b"")
        # Set mtime AFTER writing so the final mtime reflects 30 h ago
        old_mtime = time.time() - 30 * 3600
        os.utime(old_empty, (old_mtime, old_mtime))

        ctx = FileContext(workspace_root=tmp_path, all_files=[old_empty], directories=[])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_empty_cleanup(ctx)
        assert old_empty in _sources(ops), (
            "Old empty file must still be flagged for deletion"
        )


# ---------------------------------------------------------------------------
# _plan_orphan_cleanup guard
# ---------------------------------------------------------------------------

class TestRecencyGuardInOrphanCleanup:
    """Recently created orphan dirs must be protected from _plan_orphan_cleanup."""

    def test_recent_orphan_dir_not_in_plan(self, tmp_path: Path) -> None:
        """An empty dir modified <24 h ago must NOT be marked for rmdir."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        recent_dir = tmp_path / "orphan_new"
        recent_dir.mkdir()
        recent_mtime = time.time() - 0.5 * 3600
        os.utime(recent_dir, (recent_mtime, recent_mtime))

        ctx = FileContext(workspace_root=tmp_path, all_files=[], directories=[recent_dir])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_orphan_cleanup(ctx)
        assert recent_dir not in _sources(ops), (
            "Recently created orphan dir should be protected by recency guard"
        )

    def test_old_orphan_dir_is_in_plan(self, tmp_path: Path) -> None:
        """An empty dir modified 30 h ago MUST be marked for rmdir."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        old_dir = tmp_path / "orphan_old"
        old_dir.mkdir()
        old_mtime = time.time() - 30 * 3600
        os.utime(old_dir, (old_mtime, old_mtime))

        ctx = FileContext(workspace_root=tmp_path, all_files=[], directories=[old_dir])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_orphan_cleanup(ctx)
        assert old_dir in _sources(ops), (
            "Old orphan dir must still be flagged for rmdir"
        )


# ---------------------------------------------------------------------------
# _plan_markdown_archive guard
# ---------------------------------------------------------------------------

class TestRecencyGuardInMarkdownArchive:
    """Recently edited markdown files must be protected from _plan_markdown_archive."""

    def test_recent_markdown_not_in_plan(self, tmp_path: Path) -> None:
        """A .md file edited <24 h ago must NOT be scheduled for archival."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        # Place markdown in a non-protected, non-docs directory
        subdir = tmp_path / "scratch"
        subdir.mkdir()
        recent_md = subdir / "notes.md"
        _touch_recent(recent_md, hours_ago=2)

        ctx = FileContext(workspace_root=tmp_path, all_files=[recent_md], directories=[subdir])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_markdown_archive(ctx)
        assert recent_md not in _sources(ops), (
            "Recently edited markdown file should be protected by recency guard"
        )

    def test_old_markdown_is_in_plan(self, tmp_path: Path) -> None:
        """A .md file NOT edited in 30 h MUST be scheduled for archival."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        subdir = tmp_path / "scratch"
        subdir.mkdir()
        old_md = subdir / "stale.md"
        _touch_old(old_md, hours_ago=30)

        ctx = FileContext(workspace_root=tmp_path, all_files=[old_md], directories=[subdir])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_markdown_archive(ctx)
        assert old_md in _sources(ops), (
            "Stale markdown file must still be flagged for archival"
        )


# ---------------------------------------------------------------------------
# _plan_root_cleanup guard
# ---------------------------------------------------------------------------

class TestRecencyGuardInRootCleanup:
    """Recently created root-level clutter must be protected from _plan_root_cleanup."""

    def test_recent_root_file_not_in_plan(self, tmp_path: Path) -> None:
        """A root-level junk file modified <24 h ago must NOT be in the deletion plan."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        # Use a .tmp extension that vacuum would normally flag as root clutter
        recent_tmp = tmp_path / "scratch.tmp"
        _touch_recent(recent_tmp, hours_ago=1)

        ctx = FileContext(workspace_root=tmp_path, all_files=[recent_tmp], directories=[])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_root_cleanup(ctx)
        assert recent_tmp not in _sources(ops), (
            "Recent root-level file should be protected by recency guard"
        )

    def test_old_root_file_is_in_plan(self, tmp_path: Path) -> None:
        """A root-level junk file modified 30 h ago MUST be in the deletion plan."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator, FileContext

        old_tmp = tmp_path / "scratch.tmp"
        _touch_old(old_tmp, hours_ago=30)

        ctx = FileContext(workspace_root=tmp_path, all_files=[old_tmp], directories=[])
        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        ops = vacuum._plan_root_cleanup(ctx)
        assert old_tmp in _sources(ops), (
            "Old root-level junk file must still be flagged"
        )
