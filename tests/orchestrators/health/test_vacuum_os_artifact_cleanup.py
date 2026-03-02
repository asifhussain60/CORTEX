"""Tests for VacuumOrchestrator OS artifact cleanup (.DS_Store, Thumbs.db).

Verifies that VacuumOrchestrator detects and removes OS-generated junk files
that accumulate on macOS (Finder metadata) and Windows (Explorer cache).

AC-ID: AC-VAC-OS-001
GAP-REF: GAP-104-05 (extended), Phase 104-b
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

from pathlib import Path

import pytest


class TestVacuumOsArtifactCleanup:
    """Verify VacuumOrchestrator.run_os_artifact_cleanup() behaviour."""

    def test_method_exists(self) -> None:
        """VacuumOrchestrator must expose run_os_artifact_cleanup()."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        assert hasattr(VacuumOrchestrator, "run_os_artifact_cleanup"), (
            "run_os_artifact_cleanup() missing from VacuumOrchestrator"
        )

    def test_dry_run_detects_ds_store(self, tmp_path: Path) -> None:
        """Dry-run must detect .DS_Store files without deleting them."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        # Create fake .DS_Store files in a nested structure
        (tmp_path / ".DS_Store").write_bytes(b"\x00" * 8)
        subdir = tmp_path / "cortex-docs" / "assets"
        subdir.mkdir(parents=True)
        (subdir / ".DS_Store").write_bytes(b"\x00" * 8)

        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        results = vacuum.run_os_artifact_cleanup(dry_run=True)

        # All results are dry-run planned
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        for r in results:
            assert r.dry_run is True
            assert r.success is True

        # Files NOT deleted
        assert (tmp_path / ".DS_Store").exists()
        assert (subdir / ".DS_Store").exists()

    def test_live_run_deletes_ds_store(self, tmp_path: Path) -> None:
        """Live run must delete all .DS_Store files in the workspace."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        ds1 = tmp_path / ".DS_Store"
        ds2 = tmp_path / "cortex" / ".DS_Store"
        ds2.parent.mkdir(parents=True)
        ds1.write_bytes(b"\x00" * 8)
        ds2.write_bytes(b"\x00" * 8)

        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        results = vacuum.run_os_artifact_cleanup(dry_run=False)

        assert len(results) == 2
        for r in results:
            assert r.success is True
            assert r.dry_run is False

        # Files deleted
        assert not ds1.exists()
        assert not ds2.exists()

    def test_live_run_deletes_thumbs_db(self, tmp_path: Path) -> None:
        """Live run must delete Windows Thumbs.db files."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        thumbs = tmp_path / "assets" / "Thumbs.db"
        thumbs.parent.mkdir(parents=True)
        thumbs.write_bytes(b"fake")

        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        results = vacuum.run_os_artifact_cleanup(dry_run=False)

        assert any(r.success for r in results)
        assert not thumbs.exists()

    def test_live_run_deletes_ds_store_case_variant(self, tmp_path: Path) -> None:
        """Live run must delete .ds-store (lowercase case variant)."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        ds_lower = tmp_path / ".ds-store"
        ds_lower.write_bytes(b"\x00" * 8)

        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        results = vacuum.run_os_artifact_cleanup(dry_run=False)

        assert len(results) == 1
        assert results[0].success is True
        assert not ds_lower.exists()

    def test_skips_git_and_venv_dirs(self, tmp_path: Path) -> None:
        """Must NOT touch .DS_Store inside .git/ or .venv/ directories."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        git_ds = tmp_path / ".git" / ".DS_Store"
        git_ds.parent.mkdir(parents=True)
        git_ds.write_bytes(b"\x00" * 8)

        venv_ds = tmp_path / ".venv" / "lib" / ".DS_Store"
        venv_ds.parent.mkdir(parents=True)
        venv_ds.write_bytes(b"\x00" * 8)

        # A legitimate one to delete
        real_ds = tmp_path / "cortex" / ".DS_Store"
        real_ds.parent.mkdir(parents=True)
        real_ds.write_bytes(b"\x00" * 8)

        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        results = vacuum.run_os_artifact_cleanup(dry_run=False)

        # Only the non-protected one is deleted
        assert len(results) == 1
        assert not real_ds.exists()
        assert git_ds.exists(), ".git/.DS_Store must not be deleted"
        assert venv_ds.exists(), ".venv DS_Store must not be deleted"

    def test_returns_empty_when_no_junk_files(self, tmp_path: Path) -> None:
        """Returns empty list when workspace has no OS junk files."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "module.py").write_text("# clean")

        vacuum = VacuumOrchestrator(workspace_root=tmp_path)
        results = vacuum.run_os_artifact_cleanup(dry_run=False)

        assert results == []

    def test_run_main_pipeline_includes_os_cleanup(self) -> None:
        """VacuumOrchestrator.run() pipeline must invoke run_os_artifact_cleanup."""
        vacuum_src = (
            Path(__file__).parent.parent.parent.parent
            / "cortex" / "orchestrators" / "health" / "vacuum_orchestrator.py"
        )
        content = vacuum_src.read_text()
        assert "run_os_artifact_cleanup" in content, (
            "run_os_artifact_cleanup must be called in VacuumOrchestrator.run() pipeline"
        )
