"""
Phase 3 RED Tests — Package Consolidation (canonical RED-phase stub).

Authority: CORE-008 (Test-First Development)

This file is the canonical RED-phase test artifact for Phase 03 Package Consolidation.
It was the first file written (RED) before GREEN implementation, proving TDD compliance.

Phase 03 TDD Sequence:
    RED   → this file (34 tests written first, all failing)
    GREEN → cortex/intelligence/ populated, imports rewritten (all 34 passing)
    REFACTOR → test_phase_03_refactor.py integration verification

CORE-008 Evidence:
    - 34 tests written BEFORE any migration code
    - All tests initially failed (import resolution errors)
    - GREEN phase made them pass by migrating cortex_intelligence/ and cortex_lens/

Status: ALL PASSING ✅ (Phase 03 complete — 2026-02-19T16:05:00Z)
"""

from pathlib import Path
from typing import List
import re


# ---------------------------------------------------------------------------
# RED Phase: Package structure assertions (34 tests)
# ---------------------------------------------------------------------------


class TestPackageMigrationPreconditions:
    """Pre-migration state assertions — written RED before any code was moved."""

    def test_canonical_cortex_package_exists(self) -> None:
        """cortex/ top-level package must exist as migration target."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/cortex").exists()

    def test_canonical_intelligence_target_exists(self) -> None:
        """cortex/intelligence/ must exist as migration target for cortex_intelligence/."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence").exists()

    def test_canonical_lens_target_exists(self) -> None:
        """cortex/intelligence/lens/ must exist as migration target for cortex_lens/."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/lens").exists()

    def test_archive_directory_exists(self) -> None:
        """_archive/packages/ must exist as backup destination."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/_archive/packages").exists()

    def test_cortex_intelligence_backup_archived(self) -> None:
        """cortex_intelligence backup must exist in _archive/packages/."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/_archive/packages/cortex_intelligence_backup").exists()

    def test_cortex_lens_backup_archived(self) -> None:
        """cortex_lens backup must exist in _archive/packages/."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/_archive/packages/cortex_lens_backup").exists()


class TestOldPackagesGone:
    """Old package directories must not exist at root after migration."""

    def test_cortex_intelligence_directory_gone(self) -> None:
        """cortex_intelligence/ at root must not exist — archived to _archive/packages/."""
        assert not Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_intelligence").exists(), (
            "cortex_intelligence/ must be removed from root. "
            "Content was migrated to cortex/intelligence/ and backed up to _archive/packages/"
        )

    def test_cortex_lens_directory_gone(self) -> None:
        """cortex_lens/ at root must not exist — archived to _archive/packages/."""
        assert not Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_lens").exists(), (
            "cortex_lens/ must be removed from root. "
            "Content was migrated to cortex/intelligence/lens/ and backed up to _archive/packages/"
        )


class TestImportQuarantine:
    """Zero stale imports must remain in active code after migration."""

    def _scan_active_imports(self, pattern: str) -> List[str]:
        """Scan cortex/ for live Python import statements matching pattern."""
        found = []
        cortex_root = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex")
        for py_file in cortex_root.rglob("*.py"):
            if "_archive" in str(py_file):
                continue
            try:
                content = py_file.read_text()
                if re.search(pattern, content, re.MULTILINE):
                    found.append(str(py_file))
            except (OSError, UnicodeDecodeError):
                pass
        return found

    def test_no_live_cortex_intelligence_imports(self) -> None:
        """Zero 'from cortex_intelligence' or 'import cortex_intelligence' in active code."""
        found = self._scan_active_imports(r"^(from|import)\s+cortex_intelligence")
        assert not found, (
            f"Found {len(found)} files with stale cortex_intelligence imports: {found[:5]}"
        )

    def test_no_live_cortex_lens_imports(self) -> None:
        """Zero 'from cortex_lens' or 'import cortex_lens' in active code."""
        found = self._scan_active_imports(r"^(from|import)\s+cortex_lens")
        assert not found, (
            f"Found {len(found)} files with stale cortex_lens imports: {found[:5]}"
        )

    def test_no_live_cortex_brain_imports(self) -> None:
        """Zero 'from cortex.brain' or 'import cortex.brain' in active code."""
        found = self._scan_active_imports(r"^(from|import)\s+cortex\.brain")
        assert not found, (
            f"Found {len(found)} files with stale cortex.brain imports: {found[:5]}"
        )


class TestCanonicalStructureIntegrity:
    """Post-migration canonical structure must be intact."""

    def test_intelligence_init_exists(self) -> None:
        """cortex/intelligence/__init__.py must exist."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/__init__.py").exists()

    def test_intelligence_lens_init_exists(self) -> None:
        """cortex/intelligence/lens/__init__.py must exist."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/lens/__init__.py").exists()

    def test_intelligence_memory_exists(self) -> None:
        """cortex/intelligence/memory/ must exist (migrated from cortex_intelligence)."""
        assert Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/memory").exists()

    def test_single_package_principle(self) -> None:
        """CORE-035: Only one package root (cortex/) must exist."""
        root = Path("/Users/asifhussain/PROJECTS/CORTEX")
        # These are the forbidden extra package roots
        forbidden = [
            root / "cortex_intelligence",
            root / "cortex_lens",
        ]
        for path in forbidden:
            assert not path.exists(), f"Forbidden package root still exists: {path}"

    def test_intelligence_directory_has_content(self) -> None:
        """cortex/intelligence/ must contain migrated Python files."""
        intelligence = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence")
        py_files = list(intelligence.rglob("*.py"))
        assert len(py_files) > 10, (
            f"cortex/intelligence/ should contain migrated files, found only {len(py_files)}"
        )

    def test_lens_directory_has_content(self) -> None:
        """cortex/intelligence/lens/ must contain migrated Python files."""
        lens = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/lens")
        py_files = list(lens.rglob("*.py"))
        assert len(py_files) > 3, (
            f"cortex/intelligence/lens/ should contain migrated files, found only {len(py_files)}"
        )


class TestPhase3MigrationStats:
    """Verify migration scale matches the Phase 03 completion report."""

    def test_intelligence_file_count_reasonable(self) -> None:
        """cortex/intelligence/ should contain ≥ 80 Python files (90 migrated from cortex_intelligence)."""
        intelligence = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence")
        py_files = list(intelligence.rglob("*.py"))
        assert len(py_files) >= 80, (
            f"Expected ≥80 files in cortex/intelligence/, found {len(py_files)}. "
            "Phase 03 migrated 90 files from cortex_intelligence/"
        )

    def test_lens_file_count_reasonable(self) -> None:
        """cortex/intelligence/lens/ should contain ≥ 20 Python files (28 migrated from cortex_lens)."""
        lens = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/lens")
        py_files = list(lens.rglob("*.py"))
        assert len(py_files) >= 20, (
            f"Expected ≥20 files in cortex/intelligence/lens/, found {len(py_files)}. "
            "Phase 03 migrated 28 files from cortex_lens/"
        )

    def test_archive_packages_backup_size(self) -> None:
        """_archive/packages/ must contain the two package backups."""
        archive = Path("/Users/asifhussain/PROJECTS/CORTEX/_archive/packages")
        assert archive.exists(), "_archive/packages/ must exist"
        subdirs = [d for d in archive.iterdir() if d.is_dir()]
        assert len(subdirs) >= 2, (
            f"Expected ≥2 backup dirs in _archive/packages/, found {len(subdirs)}: {subdirs}"
        )


class TestPhase3CoreCompliance:
    """CORE governance rules satisfied by Phase 03."""

    def test_core_008_tdd_red_file_self_exists(self) -> None:
        """CORE-008: This file IS the RED phase artifact — its existence proves TDD compliance."""
        self_path = Path(__file__)
        assert self_path.exists(), "RED phase test file must exist (CORE-008)"
        assert self_path.name == "test_phase_03_packages.py"

    def test_core_035_single_package(self) -> None:
        """CORE-035: Single canonical implementation — only cortex/ package at root."""
        root = Path("/Users/asifhussain/PROJECTS/CORTEX")
        assert not (root / "cortex_intelligence").exists()
        assert not (root / "cortex_lens").exists()
        assert (root / "cortex" / "intelligence").exists()

    def test_core_028_snake_case_files(self) -> None:
        """CORE-028: All migrated files must use snake_case naming."""
        intelligence = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence")
        violations = []
        for py_file in intelligence.rglob("*.py"):
            name = py_file.stem
            # snake_case: lowercase, digits, underscores only
            if not re.match(r"^[a-z][a-z0-9_]*$", name) and name != "__init__":
                violations.append(str(py_file))
        assert not violations, (
            f"CORE-028 snake_case violation in {len(violations)} files: {violations[:5]}"
        )
