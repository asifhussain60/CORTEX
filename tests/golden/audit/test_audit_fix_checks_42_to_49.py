"""Phase 128-i: Audit-Fix Checks #42-#49 Golden Test.

Authority: phase-128-i (Audit-Fix Mode Upgrade + Final Certification)
Governance: CORE-008 (TDD mandatory), CORE-064 (Sweep Completeness)
SSOT: cortex-registry/planning/phases/completed/phase-128-conflict-drift-eradication.yaml

Verifies that all 8 drift lock files for checks #42-#49 exist, are valid YAML,
have required fields, and reference test files that also exist.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
DRIFT_LOCKS_DIR = REPO_ROOT / "cortex-registry" / "governance" / "drift-locks"

# The 8 drift lock checks added by Phase 128 (checks #42-#49)
PHASE_128_CHECKS = list(range(42, 50))  # 42, 43, 44, 45, 46, 47, 48, 49

REQUIRED_FIELDS = {"id", "check_number", "status", "title", "test_file"}


def _find_drift_lock(check_number: int) -> Path | None:
    """Find the drift lock YAML for a given check number."""
    pattern = f"check-{check_number}-*-lock.yaml"
    matches = list(DRIFT_LOCKS_DIR.glob(pattern))
    return matches[0] if matches else None


def _load_drift_lock(path: Path) -> dict:
    """Load a drift lock YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestAuditFixChecks42To49:
    """Verify that all 8 Phase 128 drift locks exist and are well-formed."""

    def test_drift_locks_directory_exists(self) -> None:
        """The drift-locks directory must exist."""
        assert DRIFT_LOCKS_DIR.is_dir(), (
            f"Drift locks directory missing: {DRIFT_LOCKS_DIR}"
        )

    @pytest.mark.parametrize("check_num", PHASE_128_CHECKS)
    def test_drift_lock_file_exists(self, check_num: int) -> None:
        """Each check #42-#49 must have a drift lock YAML file."""
        lock_path = _find_drift_lock(check_num)
        assert lock_path is not None, (
            f"No drift lock file found for check-{check_num} "
            f"(expected check-{check_num}-*-lock.yaml in {DRIFT_LOCKS_DIR})"
        )

    @pytest.mark.parametrize("check_num", PHASE_128_CHECKS)
    def test_drift_lock_is_valid_yaml(self, check_num: int) -> None:
        """Each drift lock file must be parseable as valid YAML."""
        lock_path = _find_drift_lock(check_num)
        if lock_path is None:
            pytest.skip(f"check-{check_num} lock file not found")
        data = _load_drift_lock(lock_path)
        assert isinstance(data, dict), (
            f"{lock_path.name} did not parse as a YAML mapping"
        )

    @pytest.mark.parametrize("check_num", PHASE_128_CHECKS)
    def test_drift_lock_has_required_fields(self, check_num: int) -> None:
        """Each drift lock must contain required governance fields."""
        lock_path = _find_drift_lock(check_num)
        if lock_path is None:
            pytest.skip(f"check-{check_num} lock file not found")
        data = _load_drift_lock(lock_path)
        missing = REQUIRED_FIELDS - set(data.keys())
        assert not missing, (
            f"{lock_path.name} missing required fields: {missing}"
        )

    @pytest.mark.parametrize("check_num", PHASE_128_CHECKS)
    def test_drift_lock_status_is_active(self, check_num: int) -> None:
        """Each Phase 128 drift lock must have status ACTIVE."""
        lock_path = _find_drift_lock(check_num)
        if lock_path is None:
            pytest.skip(f"check-{check_num} lock file not found")
        data = _load_drift_lock(lock_path)
        assert data.get("status") == "ACTIVE", (
            f"{lock_path.name} has status '{data.get('status')}', expected 'ACTIVE'"
        )

    @pytest.mark.parametrize("check_num", PHASE_128_CHECKS)
    def test_drift_lock_test_file_exists(self, check_num: int) -> None:
        """Each drift lock must reference a test file that exists on disk."""
        lock_path = _find_drift_lock(check_num)
        if lock_path is None:
            pytest.skip(f"check-{check_num} lock file not found")
        data = _load_drift_lock(lock_path)
        test_file = data.get("test_file")
        if not test_file:
            pytest.skip(f"{lock_path.name} has no test_file field")
        test_path = REPO_ROOT / test_file
        assert test_path.exists(), (
            f"{lock_path.name} references test_file '{test_file}' which does not exist"
        )

    def test_all_eight_locks_present(self) -> None:
        """Summary assertion: all 8 locks must be present (no partial sweep)."""
        missing = [n for n in PHASE_128_CHECKS if _find_drift_lock(n) is None]
        assert not missing, (
            f"CORE-064 violation: {len(missing)} of 8 drift locks missing. "
            f"Missing check numbers: {missing}"
        )

    def test_check_numbers_match_file_content(self) -> None:
        """Each lock's check_number field must match the number in its filename."""
        mismatches = []
        for check_num in PHASE_128_CHECKS:
            lock_path = _find_drift_lock(check_num)
            if lock_path is None:
                continue
            data = _load_drift_lock(lock_path)
            actual = data.get("check_number")
            if actual != check_num:
                mismatches.append(
                    f"{lock_path.name}: filename says {check_num}, "
                    f"content says {actual}"
                )
        assert not mismatches, (
            "Check number mismatches between filename and content:\n"
            + "\n".join(f"  - {m}" for m in mismatches)
        )
