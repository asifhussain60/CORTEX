"""Tests for VacuumOrchestrator build artifact cleanup.

Verifies that VacuumOrchestrator can detect and clean .NET build artifacts
(bin/, obj/) from Roslyn CLI directories and other gitignore-covered items.

AC-ID: AC-VAC-BUILD-001
GAP-REF: GAP-104-01, GAP-104-02
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

import pytest


class TestVacuumBuildArtifactCleanup:
    """Verify VacuumOrchestrator cleans build artifacts."""

    def test_vacuum_run_includes_build_artifact_step(self) -> None:
        """VacuumOrchestrator.run() must include build artifact cleanup step."""
        vacuum_src = (
            Path(__file__).parent.parent.parent.parent
            / "cortex"
            / "orchestrators"
            / "health"
            / "vacuum_orchestrator.py"
        )
        content = vacuum_src.read_text()
        assert "build_artifact" in content.lower() or "BuildArtifact" in content, (
            "VacuumOrchestrator does not reference build artifact cleanup. "
            "Wire BuildArtifactCleaner or _plan_build_artifact_cleanup."
        )

    def test_vacuum_run_build_artifact_cleanup_dry_run(self, tmp_path: Path) -> None:
        """Dry-run build artifact cleanup detects but doesn't delete artifacts."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        # Create fake roslyn bin/obj structure
        roslyn_bin = tmp_path / "cortex" / "intelligence" / "lens" / "dotnet" / "roslyn_cli" / "bin" / "Debug"
        roslyn_bin.mkdir(parents=True)
        (roslyn_bin / "test.dll").write_text("fake")
        (roslyn_bin / "test.pdb").write_text("fake")

        roslyn_obj = tmp_path / "cortex" / "intelligence" / "lens" / "dotnet" / "roslyn_cli" / "obj"
        roslyn_obj.mkdir(parents=True)
        (roslyn_obj / "project.assets.json").write_text("fake")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=True)

        assert len(report) > 0, "Expected build artifact cleanup to find artifacts"
        assert all(r.dry_run for r in report), "Dry-run should not delete"
        # Files should still exist
        assert (roslyn_bin / "test.dll").exists(), "Dry-run should preserve files"

    def test_vacuum_run_build_artifact_cleanup_execute(self, tmp_path: Path) -> None:
        """Execute build artifact cleanup deletes bin/obj directories."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        # Create fake build artifacts
        bin_dir = tmp_path / "cortex" / "some_project" / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "test.dll").write_text("fake")

        obj_dir = tmp_path / "cortex" / "some_project" / "obj"
        obj_dir.mkdir(parents=True)
        (obj_dir / "build.cache").write_text("fake")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert len(report) > 0, "Expected cleanup actions"
        assert not bin_dir.exists(), "bin/ should be deleted"
        assert not obj_dir.exists(), "obj/ should be deleted"

    def test_vacuum_build_artifact_skips_protected_dirs(self, tmp_path: Path) -> None:
        """Build artifact cleanup must not touch .venv, .git, _workspaces, cortex-docs."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        # Create build-like dirs inside protected areas
        venv_bin = tmp_path / ".venv" / "bin"
        venv_bin.mkdir(parents=True)
        (venv_bin / "python").write_text("fake")

        git_obj = tmp_path / ".git" / "objects"
        git_obj.mkdir(parents=True)
        (git_obj / "pack").write_text("fake")

        docs_cache = tmp_path / "cortex-docs" / "tests" / "__pycache__"
        docs_cache.mkdir(parents=True)
        (docs_cache / "view.cpython-313.pyc").write_bytes(b"fake")

        # Also create an actual build artifact to ensure we still clean
        real_bin = tmp_path / "cortex" / "project" / "bin"
        real_bin.mkdir(parents=True)
        (real_bin / "output.dll").write_text("fake")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert venv_bin.exists(), ".venv/bin must be protected"
        assert git_obj.exists(), ".git/objects must be protected"
        assert docs_cache.exists(), "cortex-docs/__pycache__ must be protected"
        assert not real_bin.exists(), "cortex/project/bin should be cleaned"


class TestGitignoreHardening:
    """Verify .gitignore covers all necessary patterns."""

    def test_gitignore_has_dll_pattern(self) -> None:
        """Gitignore must include *.dll pattern."""
        gitignore = Path(__file__).parent.parent.parent.parent / ".gitignore"
        content = gitignore.read_text()
        assert "*.dll" in content, ".gitignore missing *.dll pattern"

    def test_gitignore_has_pdb_pattern(self) -> None:
        """Gitignore must include *.pdb pattern."""
        gitignore = Path(__file__).parent.parent.parent.parent / ".gitignore"
        content = gitignore.read_text()
        assert "*.pdb" in content, ".gitignore missing *.pdb pattern"

    def test_gitignore_has_ds_store_lowercase(self) -> None:
        """Gitignore must include .ds-store (lowercase variant)."""
        gitignore = Path(__file__).parent.parent.parent.parent / ".gitignore"
        content = gitignore.read_text()
        assert ".ds-store" in content, ".gitignore missing .ds-store (lowercase) pattern"

    def test_gitignore_has_benchmarks(self) -> None:
        """Gitignore must include .benchmarks/ pattern."""
        gitignore = Path(__file__).parent.parent.parent.parent / ".gitignore"
        content = gitignore.read_text()
        assert ".benchmarks" in content, ".gitignore missing .benchmarks/ pattern"

    def test_ds_store_not_tracked(self) -> None:
        """No .ds-store variant should be tracked in git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", ".ds-store", ".DS_Store"],
            capture_output=True, text=True,
            cwd=Path(__file__).parent.parent.parent.parent,
        )
        tracked = [f for f in result.stdout.strip().split("\n") if f]
        assert len(tracked) == 0, f"DS_Store variants tracked in git: {tracked}"
