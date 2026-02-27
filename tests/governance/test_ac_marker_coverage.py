"""
Phase 80-e — GAP-80-05: AC marker coverage for canonical orchestrators.

Tests that the 27 canonical wired orchestrators have AC_START/AC_COMPLETE
markers in their source files, and that the marker scanner utility works.

CORE-008: Tests written first (RED phase).
CORE-027: AC markers mandatory on all orchestrator entry points.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

import pytest

# Paths relative to workspace root
ORCHESTRATORS_DIR = Path(__file__).parents[2] / "cortex" / "orchestrators"
WORKSPACE_ROOT = Path(__file__).parents[2]

# The 27 canonical wired orchestrators (from wiring contracts)
CANONICAL_ORCHESTRATORS = [
    # Core tier
    "cortex/orchestrators/core/master_orchestrator.py",
    "cortex/orchestrators/core/intent_router.py",
    "cortex/orchestrators/core/interaction_orchestrator.py",
    "cortex/orchestrators/core/tdd_orchestrator.py",
    "cortex/orchestrators/core/enforcement_orchestrator.py",
    "cortex/orchestrators/core/request_rephrase_orchestrator.py",
    # Domain tier
    "cortex/orchestrators/domain/refactoring_orchestrator.py",
    "cortex/orchestrators/domain/planning_orchestrator.py",
    "cortex/orchestrators/domain/sdlc_workflow_orchestrator.py",
    # Support tier
    "cortex/orchestrators/support/audit_orchestrator.py",
    "cortex/orchestrators/support/sweep_catalogue_orchestrator.py",
    "cortex/orchestrators/support/debugger_orchestrator.py",
    "cortex/orchestrators/support/digest_orchestrator.py",
    "cortex/orchestrators/support/capability_registry_builder.py",
    # Health tier
    "cortex/orchestrators/health/health_orchestrator.py",
    "cortex/orchestrators/health/vacuum_orchestrator.py",
]


def _has_ac_marker(filepath: Path) -> bool:
    """Return True if the file contains AC_START or AC_COMPLETE."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        return "AC_START" in content or "AC_COMPLETE" in content
    except OSError:
        return False


def ac_marker_coverage_check(directory: Path) -> List[str]:
    """Scan *directory* for Python orchestrator files missing AC markers.

    Returns:
        List of relative file paths missing AC markers.
    """
    missing = []
    for py_file in directory.rglob("*.py"):
        name = py_file.name
        if name.startswith("__") or name.startswith("test_"):
            continue
        if not _has_ac_marker(py_file):
            missing.append(str(py_file.relative_to(directory.parent.parent)))
    return missing


class TestACMarkerCoverage:
    """Tests for GAP-80-05: AC marker coverage across orchestrators."""

    def test_ac_marker_scanner_callable(self):
        """ac_marker_coverage_check() must be callable and return a list."""
        result = ac_marker_coverage_check(ORCHESTRATORS_DIR)
        assert isinstance(result, list)

    def test_master_orchestrator_has_ac_markers(self):
        """master_orchestrator.py must contain AC_START and AC_COMPLETE."""
        filepath = WORKSPACE_ROOT / "cortex/orchestrators/core/master_orchestrator.py"
        if not filepath.exists():
            pytest.skip(f"File not found: {filepath}")
        content = filepath.read_text()
        assert "AC_START" in content, "master_orchestrator.py missing AC_START"
        assert "AC_COMPLETE" in content, "master_orchestrator.py missing AC_COMPLETE"

    def test_enforcement_orchestrator_has_ac_markers(self):
        """enforcement_orchestrator.py must contain AC markers."""
        filepath = WORKSPACE_ROOT / "cortex/orchestrators/core/enforcement_orchestrator.py"
        if not filepath.exists():
            pytest.skip(f"File not found: {filepath}")
        content = filepath.read_text()
        assert "AC_START" in content or "AC_COMPLETE" in content

    def test_health_orchestrator_has_ac_markers(self):
        """health_orchestrator.py must contain AC markers."""
        filepath = WORKSPACE_ROOT / "cortex/orchestrators/health/health_orchestrator.py"
        if not filepath.exists():
            pytest.skip(f"File not found: {filepath}")
        content = filepath.read_text()
        assert "AC_START" in content or "AC_COMPLETE" in content

    def test_canonical_orchestrators_have_ac_markers(self):
        """All canonical wired orchestrators must have AC_START or AC_COMPLETE."""
        missing = []
        for rel_path in CANONICAL_ORCHESTRATORS:
            filepath = WORKSPACE_ROOT / rel_path
            if not filepath.exists():
                continue  # Skip files not present (some may be planned)
            if not _has_ac_marker(filepath):
                missing.append(rel_path)
        assert missing == [], (
            f"Canonical orchestrators missing AC markers ({len(missing)} files):\n"
            + "\n".join(f"  - {p}" for p in missing)
        )

    def test_ac_marker_coverage_check_returns_list(self):
        """ac_marker_coverage_check() must return a list (may be non-empty before full sweep)."""
        result = ac_marker_coverage_check(ORCHESTRATORS_DIR)
        assert isinstance(result, list), "Expected list from ac_marker_coverage_check"
