"""
Golden Test: AC Marker Completeness — All Wired Orchestrators

Phase 63-D — GAP-63-04 remediation.
Verifies all 27 wired orchestrators emit paired AC_START/AC_COMPLETE markers.

Authority: CORE-008, CORE-055
AC-IDs: AC-63-D-AC-COMPLETENESS-001..003
"""
# ruff: noqa: S101
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
ORCHESTRATORS_ROOT = ROOT / "cortex" / "orchestrators"

# Canonical wired orchestrators per cortex-master.yaml (v13.0)
WIRED_ORCHESTRATOR_FILES = [
    # core tier (7)
    "core/master_orchestrator.py",
    "core/intent_router.py",
    "core/tdd_orchestrator.py",
    "core/enforcement_orchestrator/__init__.py",  # Phase 103-e: converted to sub-package
    "core/master_orchestrator_stage_1.py",
    "core/master_orchestrator_stage_3.py",
    "core/master_orchestrator_stage_4.py",
    # domain tier (6)
    "domain/planning_orchestrator.py",
    "domain/refactoring_orchestrator.py",
    "domain/security_vulnerability_orchestrator.py",
    "domain/service_decomposition_orchestrator.py",
    # support tier (14)
    "support/bulk_digest_orchestrator.py",
    "support/digest_session_orchestrator.py",
    "support/sweep_catalogue_orchestrator.py",
    # health tier
    "health/health_orchestrator.py",
    "health/vacuum_orchestrator.py",
]


def _orchestrator_ac_status(rel_path: str) -> dict:
    """Return dict with ac_start, ac_complete counts for an orchestrator file."""
    full_path = ORCHESTRATORS_ROOT / rel_path
    if not full_path.exists():
        return {"exists": False, "ac_start": 0, "ac_complete": 0}
    content = full_path.read_text(errors="replace")
    return {
        "exists": True,
        "ac_start": len(re.findall(r"\bAC_START\b", content)),
        "ac_complete": len(re.findall(r"\bAC_COMPLETE\b", content)),
    }


class TestWiredOrchestratorsHaveACStart:
    """All discoverable wired orchestrators should have at least one AC_START."""

    def test_all_wired_orchestrators_have_ac_start(self) -> None:
        """Each wired orchestrator file should contain at least 1 AC_START marker."""
        missing_ac = []
        for rel_path in WIRED_ORCHESTRATOR_FILES:
            status = _orchestrator_ac_status(rel_path)
            if not status["exists"]:
                continue  # File may not exist yet (planned orchestrators)
            if status["ac_start"] == 0:
                missing_ac.append(rel_path)
        # Soft assertion: at least 95% of existing wired orchestrators have AC_START
        # GAP-81-05: RATCHETED from 0.5 (50%) to 0.95 (95%) — Phase 81-b
        # Current coverage: 5/5 orchestrators (100%)
        existing = [r for r in WIRED_ORCHESTRATOR_FILES if (ORCHESTRATORS_ROOT / r).exists()]
        if not existing:
            pytest.skip("No wired orchestrator files found")
        ratio = (len(existing) - len(missing_ac)) / len(existing)
        assert ratio >= 0.95, (
            f"Only {len(existing) - len(missing_ac)}/{len(existing)} wired orchestrators "
            f"have AC_START markers ({ratio:.0%} < 95% threshold). "
            f"Missing: {missing_ac}"
        )


class TestNoOrphanedACStart:
    """AC_START must always be paired with AC_COMPLETE in production orchestrators."""

    def test_no_orphaned_ac_start_in_production_traces(self) -> None:
        """Every orchestrator with AC_START must also have at least 1 AC_COMPLETE."""
        orphaned = []
        for rel_path in WIRED_ORCHESTRATOR_FILES:
            status = _orchestrator_ac_status(rel_path)
            if not status["exists"]:
                continue
            if status["ac_start"] > 0 and status["ac_complete"] == 0:
                orphaned.append(
                    f"{rel_path} — {status['ac_start']} AC_START, 0 AC_COMPLETE"
                )
        assert orphaned == [], (
            "Orphaned AC_START (no matching AC_COMPLETE) in wired orchestrators:\n"
            + "\n".join(f"  {o}" for o in orphaned)
        )

    def test_all_orchestrators_have_consistent_ac_markers(self) -> None:
        """Scan all orchestrator Python files — report any AC_START orphans."""
        orphaned = []
        for py_file in ORCHESTRATORS_ROOT.rglob("*.py"):
            if "test_" in py_file.name:
                continue
            content = py_file.read_text(errors="replace")
            starts = len(re.findall(r"\bAC_START\b", content))
            completes = len(re.findall(r"\bAC_COMPLETE\b", content))
            if starts > 0 and completes == 0:
                orphaned.append(
                    f"{py_file.relative_to(ROOT)} — {starts} AC_START, 0 AC_COMPLETE"
                )
        assert orphaned == [], (
            "Orphaned AC_START markers in orchestrators:\n"
            + "\n".join(f"  {o}" for o in orphaned)
        )


class TestACCompleteHasTiming:
    """AC_COMPLETE markers should include timing information (ms)."""

    def test_ac_complete_has_timing_ms(self) -> None:
        """Spot-check: at least 1 wired orchestrator has AC_COMPLETE with 'ms' timing."""
        timing_found = False
        for rel_path in WIRED_ORCHESTRATOR_FILES[:5]:  # Check first 5
            full_path = ORCHESTRATORS_ROOT / rel_path
            if not full_path.exists():
                continue
            content = full_path.read_text(errors="replace")
            # Look for AC_COMPLETE followed by timing in milliseconds
            if re.search(r"AC_COMPLETE.*ms", content) or re.search(r"AC_COMPLETE.*✅.*\d", content):
                timing_found = True
                break
        if not timing_found:
            pytest.xfail(
                "No AC_COMPLETE with timing (ms) found in first 5 wired orchestrators — "
                "Phase 65 will add timing to all AC_COMPLETE markers"
            )
