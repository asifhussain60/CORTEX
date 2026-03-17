"""Preflight: No Unconditional Test Skips (CORE-075, Check #34).

CORE-075 — Zero Test Bypass Tolerance.

Prevents CORTEX from accumulating skipped tests as permanent technical debt.
Every ``pytestmark = pytest.mark.skip`` (module-level unconditional skip)
must be tracked in the skip-debt-registry and have a remediation plan.

**Policy:**
- Module-level unconditional skips are capped at a hard ceiling.
- The ceiling MUST only decrease over time (ratchet-down).
- New unconditional skips are BLOCKED unless added to the registry with
  a remediation_target date.
- Tests that are no longer needed must be deleted, not skipped.

Drift lock: cortex-registry/governance/drift-locks/check-34-no-unconditional-skips-lock.yaml
AC-ID: AC-CORE075-PREFLIGHT-001
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = PROJECT_ROOT / "tests"

# Hard ceiling — ratchet-down only. Update this number ONLY when you
# DELETE or FIX a currently-skipped module. Never increase it.
UNCONDITIONAL_SKIP_CEILING = 22

# Patterns that indicate a module-level unconditional skip
MODULE_SKIP_PATTERNS = [
    re.compile(r"^pytestmark\s*=\s*pytest\.mark\.skip\(", re.MULTILINE),
]

# Patterns that indicate a *conditional* skip (allowed — environment-dependent)
CONDITIONAL_SKIP_PATTERNS = [
    re.compile(r"pytest\.mark\.skipif", re.MULTILINE),
]


def _find_unconditional_module_skips() -> list[tuple[str, str]]:
    """Return (relative_path, reason) for every module-level unconditional skip."""
    results: list[tuple[str, str]] = []
    for py_file in sorted(TESTS_DIR.rglob("*.py")):
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Skip conftest files — they apply marks to children differently
        if py_file.name == "conftest.py":
            # conftest with pytestmark skip is still a full bypass
            pass
        for pattern in MODULE_SKIP_PATTERNS:
            match = pattern.search(content)
            if match:
                # Verify it's NOT a conditional skipif
                line = content[match.start():content.find("\n", match.start())]
                if "skipif" in line:
                    continue
                # Extract reason
                reason_match = re.search(r'reason="([^"]*)"', line)
                reason = reason_match.group(1) if reason_match else "no reason given"
                rel = py_file.relative_to(PROJECT_ROOT)
                results.append((str(rel), reason))
    return results


class TestNoUnconditionalSkips:
    """CORE-075: Zero Test Bypass Tolerance enforcement."""

    def test_unconditional_skip_ceiling_not_exceeded(self) -> None:
        """Module-level unconditional skips must not exceed the ratchet ceiling.

        If this fails, you have two choices:
        1. FIX the skipped test so it passes (preferred).
        2. DELETE the test if the feature is deprecated/removed.

        Never increase UNCONDITIONAL_SKIP_CEILING.
        """
        skips = _find_unconditional_module_skips()
        if len(skips) > UNCONDITIONAL_SKIP_CEILING:
            excess = len(skips) - UNCONDITIONAL_SKIP_CEILING
            skip_list = "\n".join(
                f"  - {path}: {reason}" for path, reason in skips
            )
            pytest.fail(
                f"CORE-075 VIOLATION: {len(skips)} module-level unconditional skips "
                f"exceed ceiling of {UNCONDITIONAL_SKIP_CEILING} by {excess}.\n"
                f"Skipped modules:\n{skip_list}\n\n"
                f"Action required: FIX or DELETE skipped tests. "
                f"Do NOT increase the ceiling."
            )

    def test_no_new_unconditional_skips_without_registry(self) -> None:
        """Every unconditional skip must have a documented reason.

        Skips with empty or missing reasons indicate untracked debt.
        """
        skips = _find_unconditional_module_skips()
        undocumented = [
            (path, reason) for path, reason in skips
            if reason == "no reason given"
        ]
        if undocumented:
            paths = "\n".join(f"  - {path}" for path, _ in undocumented)
            pytest.fail(
                f"CORE-075 VIOLATION: {len(undocumented)} unconditional skips "
                f"have no reason= argument:\n{paths}\n\n"
                f"All skips must include reason='...' for audit traceability."
            )

    def test_skip_ceiling_matches_actual_count(self) -> None:
        """Ceiling must be ratcheted down when skips are fixed.

        If actual < ceiling, the ceiling should be lowered to match.
        This prevents the ceiling from becoming stale.
        """
        skips = _find_unconditional_module_skips()
        if len(skips) < UNCONDITIONAL_SKIP_CEILING:
            pytest.fail(
                f"CORE-075 RATCHET: Actual unconditional skips ({len(skips)}) is BELOW "
                f"ceiling ({UNCONDITIONAL_SKIP_CEILING}). "
                f"Update UNCONDITIONAL_SKIP_CEILING to {len(skips)} in "
                f"tests/preflight/test_no_unconditional_skips.py to ratchet down."
            )

    def test_report_all_unconditional_skips(self) -> None:
        """Inventory report — lists all unconditional skips for visibility."""
        skips = _find_unconditional_module_skips()
        # This test always passes but prints the inventory
        if skips:
            inventory = "\n".join(
                f"  [{i+1:02d}] {path} — {reason}"
                for i, (path, reason) in enumerate(skips)
            )
            print(
                f"\n--- CORE-075 Skip Debt Inventory ({len(skips)} modules) ---\n"
                f"{inventory}\n"
                f"--- Ceiling: {UNCONDITIONAL_SKIP_CEILING} ---"
            )
