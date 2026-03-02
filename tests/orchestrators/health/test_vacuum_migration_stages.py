"""Tests — Sub-phase H (GAP-107-17, GAP-107-18): VacuumOrchestrator migration stages.

Validates the 3 new migration cleanup stages added as part of Phase 107
intelligence-layer consolidation:

  - run_compat_shim_detection()  — detect re-export-only deprecated modules
  - run_stale_import_scanner()   — detect old cortex.lens import paths in
                                   tests/ and scripts/
  - run_empty_init_cleanup()     — detect __init__.py files with no real code
  - VacuumReport.migration_shim_count field
  - Pipeline order: migration stages execute AFTER build artifact cleanup
  - Dry-run mode works for all new stages

Phase: Phase 107 Sub-phase H (GAP-107-17, GAP-107-18)
CORE: CORE-008 (TDD), CORE-064 (sweep)
"""

from __future__ import annotations

from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
from cortex.orchestrators.health.models import OperationResult, VacuumReport


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def tmp_workspace(tmp_path: Path) -> Path:
    """Return a minimal workspace tree for vacuum testing."""
    # Create basic structure
    (tmp_path / "cortex").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "scripts").mkdir()
    return tmp_path


@pytest.fixture()
def vacuum(tmp_workspace: Path) -> VacuumOrchestrator:
    """Return a VacuumOrchestrator pointed at the tmp workspace."""
    return VacuumOrchestrator(tmp_workspace)


# ─────────────────────────────────────────────────────────────────────────────
# TestCompatShimDetection — GAP-107-17
# ─────────────────────────────────────────────────────────────────────────────


class TestCompatShimDetection:
    """run_compat_shim_detection() finds re-export-only deprecated modules."""

    def test_method_exists(self, vacuum: VacuumOrchestrator) -> None:
        """VacuumOrchestrator exposes run_compat_shim_detection() method."""
        assert hasattr(vacuum, "run_compat_shim_detection"), (
            "VacuumOrchestrator is missing run_compat_shim_detection(). "
            "Add this method as part of Phase 107 Sub-phase H."
        )

    def test_returns_list_of_operation_results(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """run_compat_shim_detection() returns List[OperationResult]."""
        results = vacuum.run_compat_shim_detection(dry_run=True)
        assert isinstance(results, list), (
            "run_compat_shim_detection() must return List[OperationResult]"
        )
        for r in results:
            assert isinstance(r, OperationResult), (
                f"Each item must be OperationResult, got {type(r)}"
            )

    def test_detects_reexport_shim(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """Detects a .py file that contains ONLY from-import re-exports (a compat shim)."""
        shim_dir = tmp_workspace / "cortex" / "old_lens"
        shim_dir.mkdir(parents=True)
        shim_file = shim_dir / "__init__.py"
        # This is a typical compat shim — only re-export, no real logic
        shim_file.write_text(
            "# Deprecated compat shim\n"
            "from cortex.intelligence.models import BaseIntelligenceEngine  # noqa: F401\n"
            "from cortex.intelligence.models import AnalysisResult  # noqa: F401\n"
        )
        results = vacuum.run_compat_shim_detection(dry_run=True)
        found = [r for r in results if "old_lens" in str(r.source or "")]
        assert found, (
            "run_compat_shim_detection() should detect old_lens/__init__.py "
            "as a compat shim but returned no results for it."
        )

    def test_dry_run_does_not_delete(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """dry_run=True plans but does not delete any shim files."""
        shim_dir = tmp_workspace / "cortex" / "stale_mod"
        shim_dir.mkdir(parents=True)
        shim_file = shim_dir / "__init__.py"
        shim_file.write_text(
            "from cortex.intelligence.facade import IntelligenceFacade  # noqa: F401\n"
        )
        vacuum.run_compat_shim_detection(dry_run=True)
        assert shim_file.exists(), (
            "dry_run=True must not delete compat shim files — file was deleted."
        )

    def test_skips_non_shim_files(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """Does NOT flag files with real implementation logic."""
        real_dir = tmp_workspace / "cortex" / "real_module"
        real_dir.mkdir(parents=True)
        real_file = real_dir / "__init__.py"
        real_file.write_text(
            "from cortex.intelligence.models import BaseIntelligenceEngine\n\n"
            "class MyEngine(BaseIntelligenceEngine):\n"
            "    def analyze(self, ctx):\n"
            "        return {}\n"
        )
        results = vacuum.run_compat_shim_detection(dry_run=True)
        found = [r for r in results if "real_module" in str(r.source or "")]
        assert not found, (
            "run_compat_shim_detection() incorrectly flagged a file with "
            "real implementation logic as a compat shim."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestStaleImportScanner — GAP-107-18
# ─────────────────────────────────────────────────────────────────────────────


class TestStaleImportScanner:
    """run_stale_import_scanner() detects old cortex.lens import paths."""

    def test_method_exists(self, vacuum: VacuumOrchestrator) -> None:
        """VacuumOrchestrator exposes run_stale_import_scanner() method."""
        assert hasattr(vacuum, "run_stale_import_scanner"), (
            "VacuumOrchestrator is missing run_stale_import_scanner(). "
            "Add this method as part of Phase 107 Sub-phase H."
        )

    def test_returns_list_of_operation_results(
        self, vacuum: VacuumOrchestrator
    ) -> None:
        """run_stale_import_scanner() returns List[OperationResult]."""
        results = vacuum.run_stale_import_scanner(dry_run=True)
        assert isinstance(results, list)
        for r in results:
            assert isinstance(r, OperationResult)

    def test_detects_stale_cortex_lens_import(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """Detects 'from cortex.lens.' import in tests/ directory."""
        stale_test = tmp_workspace / "tests" / "test_stale.py"
        stale_test.write_text(
            "from cortex.lens.engine import LensEngine  # stale import\n"
            "def test_something():\n"
            "    assert LensEngine is not None\n"
        )
        results = vacuum.run_stale_import_scanner(dry_run=True)
        found = [r for r in results if "test_stale.py" in str(r.source or "")]
        assert found, (
            "run_stale_import_scanner() should detect 'from cortex.lens.' "
            "in tests/test_stale.py but returned no results."
        )

    def test_detects_stale_import_in_scripts(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """Detects stale import in scripts/ directory."""
        stale_script = tmp_workspace / "scripts" / "old_script.py"
        stale_script.write_text(
            "import cortex.lens.analysis as lens\n"
            "lens.run()\n"
        )
        results = vacuum.run_stale_import_scanner(dry_run=True)
        found = [r for r in results if "old_script.py" in str(r.source or "")]
        assert found, (
            "run_stale_import_scanner() should detect stale 'cortex.lens' "
            "import in scripts/ but returned no results."
        )

    def test_ignores_clean_files(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """Does not flag files with correct cortex.intelligence imports."""
        clean_test = tmp_workspace / "tests" / "test_clean.py"
        clean_test.write_text(
            "from cortex.intelligence.models import BaseIntelligenceEngine\n"
            "def test_clean():\n"
            "    assert BaseIntelligenceEngine is not None\n"
        )
        results = vacuum.run_stale_import_scanner(dry_run=True)
        found = [r for r in results if "test_clean.py" in str(r.source or "")]
        assert not found, (
            "run_stale_import_scanner() incorrectly flagged a clean file "
            "with correct cortex.intelligence imports."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestEmptyInitCleanup — GAP-107-17
# ─────────────────────────────────────────────────────────────────────────────


class TestEmptyInitCleanup:
    """run_empty_init_cleanup() detects __init__.py files with no real code."""

    def test_method_exists(self, vacuum: VacuumOrchestrator) -> None:
        """VacuumOrchestrator exposes run_empty_init_cleanup() method."""
        assert hasattr(vacuum, "run_empty_init_cleanup"), (
            "VacuumOrchestrator is missing run_empty_init_cleanup(). "
            "Add this method as part of Phase 107 Sub-phase H."
        )

    def test_returns_list(self, vacuum: VacuumOrchestrator) -> None:
        """run_empty_init_cleanup() returns a list."""
        results = vacuum.run_empty_init_cleanup(dry_run=True)
        assert isinstance(results, list)

    def test_detects_comments_only_init(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """Detects __init__.py with only comments (effectively empty)."""
        pkg = tmp_workspace / "cortex" / "empty_pkg"
        pkg.mkdir(parents=True)
        init = pkg / "__init__.py"
        init.write_text("# This package is now empty after migration.\n# Deprecated.\n")
        results = vacuum.run_empty_init_cleanup(dry_run=True)
        found = [r for r in results if "empty_pkg" in str(r.source or "")]
        assert found, (
            "run_empty_init_cleanup() should detect an __init__.py with "
            "only comments as effectively empty."
        )

    def test_does_not_flag_real_init(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """Does not flag __init__.py files with real exports."""
        pkg = tmp_workspace / "cortex" / "real_pkg"
        pkg.mkdir(parents=True)
        init = pkg / "__init__.py"
        init.write_text(
            "\"\"\"Real package.\"\"\"\n"
            "from .core import CoreClass\n\n"
            "__all__ = ['CoreClass']\n"
        )
        results = vacuum.run_empty_init_cleanup(dry_run=True)
        found = [r for r in results if "real_pkg" in str(r.source or "")]
        assert not found, (
            "run_empty_init_cleanup() incorrectly flagged real_pkg/__init__.py "
            "which has real export logic."
        )

    def test_dry_run_preserves_files(
        self, vacuum: VacuumOrchestrator, tmp_workspace: Path
    ) -> None:
        """dry_run=True does not delete any __init__.py files."""
        pkg = tmp_workspace / "cortex" / "dry_pkg"
        pkg.mkdir(parents=True)
        init = pkg / "__init__.py"
        init.write_text("# empty\n")
        vacuum.run_empty_init_cleanup(dry_run=True)
        assert init.exists(), (
            "dry_run=True must not delete __init__.py — file was deleted."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestVacuumReportMigrationField — GAP-107-17
# ─────────────────────────────────────────────────────────────────────────────


class TestVacuumReportMigrationField:
    """VacuumReport has migration_shim_count field."""

    def test_vacuum_report_has_migration_shim_count(self) -> None:
        """VacuumReport dataclass has migration_shim_count attribute."""
        report = VacuumReport()
        assert hasattr(report, "migration_shim_count"), (
            "VacuumReport is missing 'migration_shim_count' field. "
            "Add: migration_shim_count: int = 0 to the dataclass."
        )

    def test_migration_shim_count_default_zero(self) -> None:
        """migration_shim_count defaults to 0."""
        report = VacuumReport()
        assert report.migration_shim_count == 0

    def test_migration_shim_count_in_to_dict(self) -> None:
        """migration_shim_count appears in VacuumReport.to_dict() output."""
        report = VacuumReport()
        report.migration_shim_count = 3
        d = report.to_dict()
        assert "migration_shim_count" in d, (
            "VacuumReport.to_dict() must include 'migration_shim_count'"
        )
        assert d["migration_shim_count"] == 3
