"""Golden Tests — VacuumOrchestrator (GV-001 .. GV-011)

Each test exercises real filesystem operations with rollback verification.

Phase: PHASE-51
CORE: CORE-008 (TDD), CORE-055 (golden test tier contract)
"""

from pathlib import Path
from typing import List

import pytest
import yaml

from cortex.orchestrators.health.models import OperationResult, VacuumReport


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """Workspace with files that vacuum should clean up."""
    # Normal Python file
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "cortex" / "good_module.py").write_text("def hello():\n    pass\n")

    # Screaming case → rename
    (tmp_path / "AUDIT_REPORT.txt").write_text("old report\n")

    # Empty file → delete
    (tmp_path / "empty.txt").write_text("")

    # Orphaned directory → delete
    (tmp_path / "orphaned_dir").mkdir()

    # Markdown in source → archive
    (tmp_path / "cortex" / "RANDOM_NOTES.md").write_text("# random\n")

    # Python file with kebab → rename to snake
    (tmp_path / "cortex" / "my-module.py").write_text("x = 1\n")

    # Root file that should be relocated
    (tmp_path / "scratch_notes.txt").write_text("some scratch\n")

    # Protected root files (should NOT be touched)
    (tmp_path / "README.md").write_text("# Project\n")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    (tmp_path / ".gitignore").write_text("__pycache__/\n")

    return tmp_path


class TestGV001RenameScreaming:
    """GV-001: Rename SCREAMING_CASE → kebab-case with atomic two-step."""

    def test_rename_screaming_file(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        result = vac.rename_file(
            workspace / "AUDIT_REPORT.txt", "audit-report.txt"
        )
        assert result.success is True
        assert (workspace / "audit-report.txt").exists()
        assert not (workspace / "AUDIT_REPORT.txt").exists()


class TestGV002DeleteEmpty:
    """GV-002: Delete empty files with rollback manifest entry."""

    def test_delete_empty_file(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        result = vac.delete_file(workspace / "empty.txt")
        assert result.success is True
        assert not (workspace / "empty.txt").exists()


class TestGV003RemoveOrphaned:
    """GV-003: Remove orphaned directories."""

    def test_remove_orphaned_dir(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        result = vac.delete_directory(workspace / "orphaned_dir")
        assert result.success is True
        assert not (workspace / "orphaned_dir").exists()


class TestGV004RootCleanup:
    """GV-004: Root cleanup — relocate non-protected files."""

    def test_relocate_root_file(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        dest = workspace / "misc"
        vac = VacuumOrchestrator(workspace)
        result = vac.relocate_file(workspace / "scratch_notes.txt", dest)
        assert result.success is True
        assert (dest / "scratch_notes.txt").exists()
        assert not (workspace / "scratch_notes.txt").exists()


class TestGV005NamingStandardization:
    """GV-005: Python → snake_case, non-Python → kebab-case."""

    def test_rename_python_kebab_to_snake(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        result = vac.rename_file(workspace / "cortex" / "my-module.py", "my_module.py")
        assert result.success is True
        assert (workspace / "cortex" / "my_module.py").exists()


class TestGV006MarkdownArchival:
    """GV-006: Archive stale markdown to .cortex-runtime/archived-docs/."""

    def test_archive_markdown(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
        from cortex.orchestrators.health.constants import ARCHIVE_DIR

        vac = VacuumOrchestrator(workspace)
        src = workspace / "cortex" / "RANDOM_NOTES.md"
        result = vac.relocate_file(src, workspace / ARCHIVE_DIR)
        assert result.success is True
        assert (workspace / ARCHIVE_DIR / "RANDOM_NOTES.md").exists()
        assert not src.exists()


class TestGV007DryRun:
    """GV-007: Dry-run mode — zero filesystem changes."""

    def test_dry_run_standalone(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        report = vac.run(dry_run=True)
        assert isinstance(report, VacuumReport)
        assert report.dry_run is True
        # No files should have changed
        assert (workspace / "AUDIT_REPORT.txt").exists()
        assert (workspace / "empty.txt").exists()


class TestGV008Rollback:
    """GV-008: Rollback — all operations reversed, files restored."""

    def test_rollback_rename(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        vac.rename_file(workspace / "AUDIT_REPORT.txt", "audit-report.txt")
        assert (workspace / "audit-report.txt").exists()

        manifest = workspace / "rollback-manifest.json"
        vac.save_rollback_manifest(manifest)
        vac.rollback(manifest)
        assert (workspace / "AUDIT_REPORT.txt").exists()
        assert not (workspace / "audit-report.txt").exists()


class TestGV009StandaloneRun:
    """GV-009: Standalone run() — quick-scan + execute without health scan."""

    def test_standalone_run(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        report = vac.run()
        assert isinstance(report, VacuumReport)
        assert report.total_operations > 0
        assert report.successful_operations > 0


class TestGV010StandaloneRootCleanup:
    """GV-010: Standalone run_root_cleanup() — relocate root files independently."""

    def test_run_root_cleanup(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        ops = vac.run_root_cleanup()
        assert isinstance(ops, list)
        # scratch_notes.txt should have been relocated
        assert not (workspace / "scratch_notes.txt").exists()


class TestGV011StandaloneNamingFix:
    """GV-011: Standalone run_naming_fix() — fix naming without health scan."""

    def test_run_naming_fix(self, workspace: Path) -> None:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace)
        ops = vac.run_naming_fix()
        assert isinstance(ops, list)
        # my-module.py should have been renamed to my_module.py
        assert (workspace / "cortex" / "my_module.py").exists()
        assert not (workspace / "cortex" / "my-module.py").exists()
