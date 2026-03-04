"""Preflight test — Check #41: Drift Lock System — Permanent CI Guardrail Completeness.

Validates that every Check (#30–#40) has:
1. A corresponding lock YAML in cortex-registry/governance/drift-locks/
2. A corresponding preflight test in tests/preflight/test_drift_lock_check_{N}.py
3. Each lock YAML is valid and parses correctly
4. The drift-locks directory itself exists and is properly structured

Gap ref: GAP-126-12
Check: #41
Phase: phase-126-l
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
PREFLIGHT_DIR = CORTEX_ROOT / "tests" / "preflight"

# All checks that must have lock YAMLs — #30 through #40
_REQUIRED_CHECK_NUMBERS = list(range(30, 41))  # 30, 31, ..., 40


def _get_lock_file(check_num: int) -> pathlib.Path | None:
    """Find the lock YAML for a given check number."""
    candidates = list(DRIFT_LOCKS_DIR.glob(f"check-{check_num}-*.yaml"))
    return candidates[0] if candidates else None


def _get_drift_lock_test(check_num: int) -> pathlib.Path:
    """Return the expected path for a drift lock test file."""
    return PREFLIGHT_DIR / f"test_drift_lock_check_{check_num}.py"


class TestDriftLockSystem:
    """Check #41: Drift Lock System completeness — all checks #30–#40 governed."""

    def test_drift_locks_directory_exists(self) -> None:
        """cortex-registry/governance/drift-locks/ must exist."""
        assert DRIFT_LOCKS_DIR.exists(), (
            "cortex-registry/governance/drift-locks/ was deleted — P0 governance violation."
        )

    def test_each_check_has_lock_yaml(self) -> None:
        """Checks #30–#40 must each have a corresponding lock YAML."""
        missing: list[int] = []
        for n in _REQUIRED_CHECK_NUMBERS:
            if _get_lock_file(n) is None:
                missing.append(n)
        assert not missing, (
            f"Missing lock YAML for checks: {missing}\n"
            f"Expected file pattern: cortex-registry/governance/drift-locks/check-{{N}}-*.yaml"
        )

    def test_each_lock_yaml_is_valid(self) -> None:
        """Each lock YAML must parse correctly and have required fields."""
        errors: list[str] = []
        for n in _REQUIRED_CHECK_NUMBERS:
            lock_file = _get_lock_file(n)
            if lock_file is None:
                errors.append(f"check-{n}: lock file missing")
                continue
            try:
                data = yaml.safe_load(lock_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                errors.append(f"check-{n}: YAML parse error — {e}")
                continue
            if data is None:
                errors.append(f"check-{n}: YAML is empty")
                continue
            for field in ("check_number", "status", "enforcement_tier"):
                if field not in data:
                    errors.append(f"check-{n}: missing required field '{field}'")
            if data.get("check_number") != n:
                errors.append(
                    f"check-{n}: check_number mismatch — expected {n}, got {data.get('check_number')}"
                )
        assert not errors, "Lock YAML validation errors:\n" + "\n".join(f"  - {e}" for e in errors)

    def test_each_check_has_drift_lock_test(self) -> None:
        """Checks #30–#40 must each have a corresponding drift lock test file."""
        missing: list[str] = []
        for n in _REQUIRED_CHECK_NUMBERS:
            test_file = _get_drift_lock_test(n)
            if not test_file.exists():
                missing.append(str(test_file.relative_to(CORTEX_ROOT)))
        assert not missing, (
            f"Missing drift lock test files:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_lock_count_matches_check_range(self) -> None:
        """There must be exactly 11 lock files for checks #30–#40."""
        existing = [
            n for n in _REQUIRED_CHECK_NUMBERS if _get_lock_file(n) is not None
        ]
        assert len(existing) == len(_REQUIRED_CHECK_NUMBERS), (
            f"Expected {len(_REQUIRED_CHECK_NUMBERS)} lock files, "
            f"found {len(existing)} (checks {existing})."
        )

    def test_all_lock_statuses_are_active(self) -> None:
        """All lock YAMLs must have status: ACTIVE."""
        inactive: list[str] = []
        for n in _REQUIRED_CHECK_NUMBERS:
            lock_file = _get_lock_file(n)
            if lock_file is None:
                continue
            try:
                data = yaml.safe_load(lock_file.read_text(encoding="utf-8"))
                if data and data.get("status") != "ACTIVE":
                    inactive.append(f"check-{n} ({lock_file.name}): status={data.get('status')}")
            except yaml.YAMLError:
                pass
        assert not inactive, (
            "These locks are not ACTIVE:\n" + "\n".join(f"  - {i}" for i in inactive)
        )

    @pytest.mark.skipif(
        not (DRIFT_LOCKS_DIR / "check-41-drift-lock-system-lock.yaml").exists(),
        reason="Drift lock not yet created (pre-GREEN)",
    )
    def test_drift_lock_check_41_exists_and_valid(self) -> None:
        """Drift lock YAML for Check #41 (self-reference) must exist and be valid."""
        lock = DRIFT_LOCKS_DIR / "check-41-drift-lock-system-lock.yaml"
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 41
        assert data.get("status") == "ACTIVE"
