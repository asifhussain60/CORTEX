"""Phase 128-g — Drift Lock System Integrity (drift lock #48).

The drift lock system itself (``cortex-registry/governance/drift-locks/``)
must stay internally consistent. This test validates:

1. Every drift lock file is parseable YAML
2. Every drift lock has the minimum required schema fields
3. The ``check_number`` in each file matches its filename (check-NN-*)
4. No duplicate ``check_number`` values exist across the registry
5. The ``test_file`` path (and ``primary_test_file`` if present) resolve to real files
6. ``status`` is one of the canonical values: ACTIVE | DEPRECATED | SUPERSEDED
7. ``enforcement_tier`` is one of: P0 | P1 | P2 | P3
8. ``ci_gate`` is a boolean when present
9. The drift lock count never drops below the established baseline (regression guard)
10. Sequential numbering: no gaps in check numbers (alerts when a lock is silently deleted)

This is the meta-lock — the lock that locks the locks.

Gap ref: GAP-128-07
Drift lock: cortex-registry/governance/drift-locks/check-48-drift-lock-system-integrity-lock.yaml
Tier: T1 (governance)
CORE rule: CORE-064 (Sweep Completeness Contract)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CORTEX_ROOT = Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"

# ---------------------------------------------------------------------------
# Schema constants
# ---------------------------------------------------------------------------

# Fields that EVERY drift lock must have
_REQUIRED_FIELDS: frozenset[str] = frozenset({
    "id",
    "check_number",
    "status",
    "enforcement_tier",
    "title",
    "test_file",
})

# Fields present in newer locks (check-39+) — required when present, valid values enforced
_CANONICAL_STATUSES: frozenset[str] = frozenset({"ACTIVE", "DEPRECATED", "SUPERSEDED"})
_CANONICAL_TIERS: frozenset[str] = frozenset({"P0", "P1", "P2", "P3"})

# Baseline guard: we must never drop below this many drift locks
# (current: 16 as of Phase 128-d). Increment this as new locks are added.
_MINIMUM_DRIFT_LOCK_COUNT: int = 16

# Check numbers that are known to have ci_gate + detect_command (check-39 onwards)
# Earlier locks (#30-38) predate these fields and are exempt.
_MODERN_LOCK_THRESHOLD: int = 39

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_drift_locks() -> list[Path]:
    """Return all check-NN-*.yaml files sorted by check number."""
    locks = [f for f in DRIFT_LOCKS_DIR.glob("check-*.yaml")]
    return sorted(locks, key=lambda f: _extract_check_number(f))


def _extract_check_number(f: Path) -> int:
    """Extract numeric check number from filename like check-42-foo-lock.yaml."""
    m = re.match(r"check-(\d+)-", f.name)
    if m:
        return int(m.group(1))
    return -1


def _load_all_locks() -> list[tuple[Path, dict[str, Any]]]:
    """Return (path, parsed_content) for each drift lock."""
    result = []
    for f in _all_drift_locks():
        content = yaml.safe_load(f.read_text())
        result.append((f, content))
    return result


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def all_locks() -> list[tuple[Path, dict[str, Any]]]:
    return _load_all_locks()


@pytest.fixture(scope="module")
def lock_paths() -> list[Path]:
    return _all_drift_locks()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_drift_locks_dir_exists():
    """The drift locks directory must exist."""
    assert DRIFT_LOCKS_DIR.exists(), f"Drift locks directory not found: {DRIFT_LOCKS_DIR}"
    assert DRIFT_LOCKS_DIR.is_dir(), f"Expected a directory at: {DRIFT_LOCKS_DIR}"


def test_minimum_drift_lock_count(lock_paths):
    """Baseline guard: drift lock count must not drop below the established minimum.

    A count drop signals unintentional deletion of a governance guardrail.
    """
    count = len(lock_paths)
    assert count >= _MINIMUM_DRIFT_LOCK_COUNT, (
        f"Drift lock count is {count} — expected ≥ {_MINIMUM_DRIFT_LOCK_COUNT}. "
        "A drift lock was likely deleted. Check git history."
    )


def test_all_drift_locks_are_parseable(lock_paths):
    """Every drift lock YAML file must be parseable without errors."""
    errors = []
    for f in lock_paths:
        try:
            content = yaml.safe_load(f.read_text())
            if not isinstance(content, dict):
                errors.append(f"{f.name}: not a YAML mapping (got {type(content).__name__})")
        except yaml.YAMLError as e:
            errors.append(f"{f.name}: YAML parse error — {e}")
    assert errors == [], "Drift lock parse errors:\n" + "\n".join(f"  {e}" for e in errors)


def test_all_drift_locks_have_required_fields(all_locks):
    """Every drift lock must contain the minimum required schema fields."""
    violations = []
    for f, content in all_locks:
        missing = _REQUIRED_FIELDS - set(content.keys())
        if missing:
            violations.append(f"{f.name}: missing fields {sorted(missing)}")
    assert violations == [], (
        f"{len(violations)} drift locks have missing required fields:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


def test_check_number_matches_filename(all_locks):
    """The ``check_number`` field in each file must match its filename's numeric prefix."""
    mismatches = []
    for f, content in all_locks:
        filename_num = _extract_check_number(f)
        yaml_num = content.get("check_number")
        if filename_num != -1 and yaml_num != filename_num:
            mismatches.append(
                f"{f.name}: filename implies check #{filename_num}, "
                f"but check_number field says {yaml_num!r}"
            )
    assert mismatches == [], (
        f"{len(mismatches)} check_number/filename mismatches:\n"
        + "\n".join(f"  {m}" for m in mismatches)
    )


def test_no_duplicate_check_numbers(all_locks):
    """No two drift locks may share the same check_number."""
    seen: dict[int, str] = {}
    dupes = []
    for f, content in all_locks:
        num = content.get("check_number")
        if num is None:
            continue
        if num in seen:
            dupes.append(f"check #{num}: {seen[num]} AND {f.name}")
        else:
            seen[num] = f.name
    assert dupes == [], (
        f"Duplicate check numbers detected:\n" + "\n".join(f"  {d}" for d in dupes)
    )


def test_all_test_files_exist(all_locks):
    """The ``test_file`` pointer in every drift lock must resolve to a real file."""
    missing = []
    for f, content in all_locks:
        test_file = content.get("test_file", "")
        if not test_file:
            missing.append(f"{f.name}: test_file field is empty")
            continue
        test_path = CORTEX_ROOT / test_file
        if not test_path.exists():
            missing.append(f"{f.name}: test_file '{test_file}' does not exist")
    assert missing == [], (
        f"{len(missing)} drift locks have missing test files:\n"
        + "\n".join(f"  {m}" for m in missing)
    )


def test_primary_test_files_exist_when_present(all_locks):
    """When ``primary_test_file`` is declared, it must resolve to a real file."""
    missing = []
    for f, content in all_locks:
        primary = content.get("primary_test_file", "")
        if not primary:
            continue
        primary_path = CORTEX_ROOT / primary
        if not primary_path.exists():
            missing.append(f"{f.name}: primary_test_file '{primary}' does not exist")
    assert missing == [], (
        f"{len(missing)} drift locks have missing primary_test_file paths:\n"
        + "\n".join(f"  {m}" for m in missing)
    )


def test_all_statuses_are_canonical(all_locks):
    """Every drift lock's ``status`` must be one of: ACTIVE | DEPRECATED | SUPERSEDED."""
    violations = []
    for f, content in all_locks:
        status = content.get("status", "")
        if status not in _CANONICAL_STATUSES:
            violations.append(f"{f.name}: invalid status {status!r} (expected one of {sorted(_CANONICAL_STATUSES)})")
    assert violations == [], (
        f"{len(violations)} drift locks have invalid status values:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


def test_all_enforcement_tiers_are_canonical(all_locks):
    """Every drift lock's ``enforcement_tier`` must be one of: P0 | P1 | P2 | P3."""
    violations = []
    for f, content in all_locks:
        tier = content.get("enforcement_tier", "")
        if tier not in _CANONICAL_TIERS:
            violations.append(
                f"{f.name}: invalid enforcement_tier {tier!r} "
                f"(expected one of {sorted(_CANONICAL_TIERS)})"
            )
    assert violations == [], (
        f"{len(violations)} drift locks have invalid enforcement_tier values:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


def test_ci_gate_is_boolean_when_present(all_locks):
    """When ``ci_gate`` is declared, it must be a boolean (True/False), not a string."""
    violations = []
    for f, content in all_locks:
        ci_gate = content.get("ci_gate")
        if ci_gate is not None and not isinstance(ci_gate, bool):
            violations.append(f"{f.name}: ci_gate must be boolean, got {type(ci_gate).__name__}({ci_gate!r})")
    assert violations == [], (
        f"{len(violations)} drift locks have non-boolean ci_gate:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


def test_modern_locks_have_ci_gate_and_detect_command(all_locks):
    """Drift locks with check_number >= 39 must declare ci_gate and detect_command.

    These fields were introduced with check-39 as part of CI automation.
    Older checks (#30–#38) are exempt.
    """
    violations = []
    for f, content in all_locks:
        num = content.get("check_number", 0)
        if not isinstance(num, int) or num < _MODERN_LOCK_THRESHOLD:
            continue
        if "ci_gate" not in content:
            violations.append(f"{f.name}: missing ci_gate (required for check >= {_MODERN_LOCK_THRESHOLD})")
        if not content.get("detect_command", ""):
            violations.append(f"{f.name}: missing detect_command (required for check >= {_MODERN_LOCK_THRESHOLD})")
    assert violations == [], (
        f"{len(violations)} modern drift locks missing required CI fields:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


def test_no_sequential_gaps_in_check_numbers(all_locks):
    """Check numbers must be sequential with no unexpected gaps.

    A gap (e.g. 30, 31, 33 — missing 32) means a drift lock was silently deleted.
    This test alerts when any existing check number is removed.
    """
    nums = sorted(
        content.get("check_number")
        for _, content in all_locks
        if isinstance(content.get("check_number"), int)
    )
    if len(nums) < 2:
        return  # nothing to check

    expected_min = nums[0]
    gaps = [
        n for n in range(expected_min, nums[-1] + 1)
        if n not in nums
    ]
    assert gaps == [], (
        f"Missing check numbers — drift locks were likely deleted: {gaps}\n"
        f"Existing: {nums}\n"
        "If the deletion was intentional, mark the lock DEPRECATED instead of removing the file."
    )


def test_all_ids_match_filename(all_locks):
    """The ``id`` field must match the filename stem (without .yaml extension)."""
    mismatches = []
    for f, content in all_locks:
        expected_id = f.stem  # e.g. "check-42-master-yaml-path-contract-lock"
        actual_id = content.get("id", "")
        if actual_id != expected_id:
            mismatches.append(f"{f.name}: id={actual_id!r}, expected {expected_id!r}")
    assert mismatches == [], (
        f"{len(mismatches)} drift locks have id/filename mismatches:\n"
        + "\n".join(f"  {m}" for m in mismatches)
    )
