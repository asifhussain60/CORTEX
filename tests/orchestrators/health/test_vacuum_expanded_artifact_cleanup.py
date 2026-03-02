"""Tests for VacuumOrchestrator expanded build/test artifact cleanup.

Verifies that VacuumOrchestrator handles additional gitignore-covered ephemeral
items: htmlcov/, .tox/, .nox/, .benchmarks/, *.egg-info/, build/, dist/,
.testmondata, .coverage.

AC-ID: AC-VAC-EXPAND-001
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

from pathlib import Path

import pytest


class TestVacuumExpandedBuildArtifacts:
    """Verify VacuumOrchestrator cleans expanded build artifact directories."""

    def test_cleans_htmlcov_directory(self, tmp_path: Path) -> None:
        """htmlcov/ (coverage HTML) should be cleaned as build artifact."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        htmlcov = tmp_path / "htmlcov"
        htmlcov.mkdir()
        (htmlcov / "index.html").write_text("<html>coverage</html>")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not htmlcov.exists(), "htmlcov/ should be deleted"
        assert len(report) > 0

    def test_cleans_tox_directory(self, tmp_path: Path) -> None:
        """.tox/ (tox environments) should be cleaned as build artifact."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        tox_dir = tmp_path / ".tox"
        tox_dir.mkdir()
        (tox_dir / "py311" / "lib").mkdir(parents=True)

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not tox_dir.exists(), ".tox/ should be deleted"

    def test_cleans_nox_directory(self, tmp_path: Path) -> None:
        """.nox/ (nox environments) should be cleaned as build artifact."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        nox_dir = tmp_path / ".nox"
        nox_dir.mkdir()
        (nox_dir / "session-py311").mkdir()

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not nox_dir.exists(), ".nox/ should be deleted"

    def test_cleans_benchmarks_directory(self, tmp_path: Path) -> None:
        """.benchmarks/ (empty benchmark data) should be cleaned."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        bench = tmp_path / ".benchmarks"
        bench.mkdir()

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not bench.exists(), ".benchmarks/ should be deleted"

    def test_cleans_egg_info_directory(self, tmp_path: Path) -> None:
        """*.egg-info/ (setuptools metadata) should be cleaned."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        egg = tmp_path / "cortex.egg-info"
        egg.mkdir()
        (egg / "PKG-INFO").write_text("name: cortex")
        (egg / "top_level.txt").write_text("cortex")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not egg.exists(), "*.egg-info/ should be deleted"

    def test_cleans_root_build_directory(self, tmp_path: Path) -> None:
        """Root-level build/ directory should be cleaned."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        build_dir = tmp_path / "build"
        build_dir.mkdir()
        (build_dir / "lib" / "cortex").mkdir(parents=True)

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not build_dir.exists(), "build/ should be deleted"

    def test_cleans_root_dist_directory(self, tmp_path: Path) -> None:
        """Root-level dist/ directory should be cleaned."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        (dist_dir / "cortex-1.0.tar.gz").write_text("fake")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not dist_dir.exists(), "dist/ should be deleted"

    def test_does_not_clean_nested_build_dir(self, tmp_path: Path) -> None:
        """build/ and dist/ only cleaned at root level, not nested."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        # A nested 'build' dir inside source — NOT a setuptools output
        # Note: 'build' is only in _ROOT_BUILD_DIRS, not in _BUILD_DIR_NAMES
        # So it should not be cleaned when nested
        nested_build = tmp_path / "cortex" / "templates" / "build"
        nested_build.mkdir(parents=True)
        (nested_build / "config.yaml").write_text("template: true")

        vac = VacuumOrchestrator(tmp_path)
        vac.run_build_artifact_cleanup(dry_run=False)

        assert nested_build.exists(), "Nested build/ dir should NOT be deleted"


class TestVacuumEphemeralFiles:
    """Verify VacuumOrchestrator cleans ephemeral test files."""

    def test_cleans_testmondata(self, tmp_path: Path) -> None:
        """.testmondata should be cleaned as ephemeral test artifact."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        testmon = tmp_path / ".testmondata"
        testmon.write_text("testmon db content")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not testmon.exists(), ".testmondata should be deleted"
        assert any(r.source == testmon for r in report)

    def test_cleans_coverage_file(self, tmp_path: Path) -> None:
        """.coverage should be cleaned as ephemeral test artifact."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        cov = tmp_path / ".coverage"
        cov.write_text("coverage data")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=False)

        assert not cov.exists(), ".coverage should be deleted"
        assert any(r.source == cov for r in report)

    def test_dry_run_preserves_ephemeral_files(self, tmp_path: Path) -> None:
        """Dry-run should detect but not delete ephemeral files."""
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        testmon = tmp_path / ".testmondata"
        testmon.write_text("testmon db content")
        cov = tmp_path / ".coverage"
        cov.write_text("coverage data")

        vac = VacuumOrchestrator(tmp_path)
        report = vac.run_build_artifact_cleanup(dry_run=True)

        assert testmon.exists(), "Dry-run should preserve .testmondata"
        assert cov.exists(), "Dry-run should preserve .coverage"
        assert len(report) >= 2, "Should detect at least 2 ephemeral files"
        assert all(r.dry_run for r in report if r.source in {testmon, cov})
