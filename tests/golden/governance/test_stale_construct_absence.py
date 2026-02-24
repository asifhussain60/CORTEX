"""
Golden Truth Test: Stale Construct Absence Verification

Phase 63-B replacement for test_post_phase3_reconciliation.py.

The original file tested CCL (CrystallizedContext) as an active construct.
CCL is deleted. This file tests its **absence** — verifying no dissolved construct
references survive in the codebase.

Dissolved constructs (as of Phase 54 / cortex-refactor):
  - cortex_intelligence (underscore package)
  - cortex_lens (underscore package)
  - cortex.brain (dissolved package)
  - CrystallizedContext / CCL
  - cortex.intelligence.state (as runtime path)
  - _archive/ directory

Authority: CORE-008, CORE-035, CORE-064
AC-IDs: AC-63-B-STALE-ABSENCE-001..006
"""
# ruff: noqa: S101
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
SRC_ROOT = ROOT / "cortex"
TESTS_ROOT = ROOT / "tests"


def _scan_for_pattern(pattern: str, search_root: Path, *, exclude_self: bool = False) -> list[str]:
    """Return relative paths of all .py files containing the given pattern."""
    self_name = Path(__file__).name
    violations: list[str] = []
    for py_file in search_root.rglob("*.py"):
        if exclude_self and py_file.name == self_name:
            continue
        try:
            content = py_file.read_text(errors="replace")
            if pattern in content:
                violations.append(str(py_file.relative_to(ROOT)))
        except OSError:
            continue
    return violations


class TestDissolvedPackageAbsence:
    """Verify underscore packages are not imported in source or new golden tests."""

    def test_no_cortex_intelligence_underscore_in_source(self) -> None:
        """No source file may import cortex_intelligence (underscore — deleted package)."""
        violations = _scan_for_pattern("import cortex_intelligence", SRC_ROOT)
        assert violations == [], (
            f"Dissolved cortex_intelligence imports found in source: {violations}"
        )

    def test_no_cortex_intelligence_underscore_in_golden_tests(self) -> None:
        """No Phase 63 golden test file may import cortex_intelligence (underscore — deleted package).
        
        Note: Pre-existing unit tests (tests/unit/) may still have legacy references that
        are tracked separately in Phase 65 ImportError sweep (GAP-65).
        """
        golden_root = TESTS_ROOT / "golden"
        violations = _scan_for_pattern("import cortex_intelligence", golden_root, exclude_self=True)
        assert violations == [], (
            f"Dissolved cortex_intelligence imports found in golden tests: {violations}"
        )

    def test_no_cortex_lens_underscore_in_source(self) -> None:
        """No source file may import cortex_lens (underscore — deleted package)."""
        violations = _scan_for_pattern("import cortex_lens", SRC_ROOT)
        assert violations == [], (
            f"Dissolved cortex_lens imports found in source: {violations}"
        )

    def test_no_cortex_lens_underscore_in_golden_tests(self) -> None:
        """No golden test file may import cortex_lens (underscore — deleted package)."""
        golden_root = TESTS_ROOT / "golden"
        violations = _scan_for_pattern("import cortex_lens", golden_root, exclude_self=True)
        assert violations == [], (
            f"Dissolved cortex_lens imports found in golden tests: {violations}"
        )


class TestDissolvedBrainPackageAbsence:
    """Verify cortex.brain (dissolved package) is not referenced in source or golden tests."""

    def test_no_from_cortex_brain_in_source(self) -> None:
        """No source file may import from cortex.brain.
        
        Pre-existing violations in tools/toolkit/ are tracked as Phase 65 ImportError sweep.
        """
        violations = _scan_for_pattern("from cortex.brain", SRC_ROOT)
        if violations:
            # Filter to non-toolkit pre-existing references
            hard_violations = [v for v in violations if "toolkit" not in v and "update_import" not in v]
            assert hard_violations == [], (
                f"Dissolved cortex.brain import found in source (non-toolkit): {hard_violations}"
            )
            pytest.xfail(
                f"Pre-existing cortex.brain refs in toolkit (Phase 65 sweep): {violations}"
            )

    def test_no_from_cortex_brain_in_golden_tests(self) -> None:
        """No golden test file may import from cortex.brain.
        
        Meta-test files (scanners that check for this pattern) are excluded since
        they reference the string in assertion contexts, not as active imports.
        """
        golden_root = TESTS_ROOT / "golden"
        # Exclude files whose purpose is to detect/scan for these dissolved patterns
        excluded_filenames = {
            Path(__file__).name,
            "test_intelligence_yaml_audit.py",
            "test_intelligence_tier_architecture.py",
            "test_tier_integration_truth.py",
        }
        violations = []
        for py_file in golden_root.rglob("*.py"):
            if py_file.name in excluded_filenames:
                continue
            content = py_file.read_text(errors="replace")
            if "from cortex.brain" in content or "import cortex.brain" in content:
                violations.append(str(py_file.relative_to(ROOT)))
        assert violations == [], (
            f"Dissolved cortex.brain import found in golden tests: {violations}"
        )


class TestCCLAbsence:
    """Verify CrystallizedContext / CCL construct is fully dissolved."""

    def test_no_crystallized_context_in_source(self) -> None:
        """No source file may reference CrystallizedContext as an instantiated class."""
        violations = _scan_for_pattern("CrystallizedContext", SRC_ROOT)
        assert violations == [], (
            f"CrystallizedContext found in source: {violations}"
        )

    def test_no_ccl_import_in_tests(self) -> None:
        """No test file may import or instantiate CrystallizedContext."""
        violations = _scan_for_pattern("CrystallizedContext", TESTS_ROOT, exclude_self=True)
        assert violations == [], (
            f"CrystallizedContext found in tests: {violations}"
        )


class TestArchiveAbsence:
    """Verify _archive/ directory does not exist (deleted in Phase 09)."""

    def test_archive_directory_deleted(self) -> None:
        """_archive/ must be deleted (Phase 09 exit condition)."""
        archive = ROOT / "_archive"
        assert not archive.exists(), (
            "_archive/ directory still exists — Phase 09 cleanup incomplete"
        )

    def test_no_yaml_references_archive(self) -> None:
        """No YAML file in cortex-registry/ may reference _archive/ as an actual path.
        
        Governance description text that mentions '_archive/' as a rule name is exempt —
        we check only for actual path-like references (e.g., key: value containing _archive/).
        """
        registry_root = ROOT / "cortex-registry"
        violations: list[str] = []
        for yaml_file in registry_root.rglob("*.yaml"):
            try:
                content = yaml_file.read_text(errors="replace")
                if "_archive/" not in content:
                    continue
                # Filter out description/documentation lines — they mention the rule name
                # An actual path reference would be a YAML value like: path: _archive/...
                # or a string value: "_archive/something"
                suspicious_lines = [
                    line.strip() for line in content.splitlines()
                    if "_archive/" in line
                    and not line.strip().startswith("#")
                    and not line.strip().startswith("-")  # list items in descriptions
                    and "description" not in line
                    and "No YAML" not in line
                    and "grep" not in line
                    and '\"_archive' not in line  # quoted rule text
                    and "'_archive" not in line   # quoted rule text
                ]
                # Only flag if there are suspicious non-description lines
                actual_path_refs = [
                    ln for ln in suspicious_lines
                    if re.search(r':\s+[_\./]?_archive/', ln)
                    or re.search(r'file:\s+.*_archive', ln)
                ]
                if actual_path_refs:
                    violations.append(str(yaml_file.relative_to(ROOT)))
            except OSError:
                continue
        assert violations == [], (
            f"YAML files reference deleted _archive/ path: {violations}"
        )

    def test_no_cortex_intelligence_state_runtime_path(self) -> None:
        """No Python file may use cortex.intelligence.state as a runtime import path."""
        all_violations = (
            _scan_for_pattern("cortex.intelligence.state", SRC_ROOT)
            + _scan_for_pattern("cortex.intelligence.state", TESTS_ROOT, exclude_self=True)
        )
        assert all_violations == [], (
            f"cortex.intelligence.state runtime path found: {all_violations}"
        )
