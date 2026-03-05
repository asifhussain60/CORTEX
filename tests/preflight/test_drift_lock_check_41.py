"""Drift lock test — Check #41: Drift Lock System Completeness.

Self-referential drift lock. Fails if the drift lock system itself is
compromised — missing lock YAMLs, missing test files, or invalid schemas.

Gap ref: GAP-126-12
Phase: phase-126-l
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-41-drift-lock-system-lock.yaml"

_REQUIRED_CHECK_NUMBERS = list(range(30, 51))  # 30–50 inclusive (30–41 production hardening, 42–50 integrity checks)


class TestDriftLockCheck41:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P0 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 41

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_drift_lock_system.py"
        assert primary.exists(), (
            "tests/preflight/test_drift_lock_system.py was deleted — restore it."
        )

    def test_drift_locks_directory_not_deleted(self) -> None:
        assert DRIFT_LOCKS_DIR.exists(), (
            "cortex-registry/governance/drift-locks/ was deleted — P0 governance violation."
        )

    def test_minimum_lock_count_maintained(self) -> None:
        """At least 21 drift lock YAMLs must exist (checks #30–#50)."""
        lock_files = list(DRIFT_LOCKS_DIR.glob("check-*.yaml"))
        assert len(lock_files) >= 21, (
            f"Only {len(lock_files)} drift lock YAMLs found — minimum is 21 (checks #30–#50)."
        )
