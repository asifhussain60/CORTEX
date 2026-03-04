"""Drift lock test — Check #38: cortex-registry Cohesion and Cross-Reference Integrity.

Permanent CI guardrail. Fails if drift lock is removed or registry cohesion
invariants are violated.

Gap ref: GAP-126-09
Phase: phase-126-i
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-38-registry-cohesion-lock.yaml"
MASTER_YAML = CORTEX_ROOT / "cortex-registry" / "cortex-master.yaml"


class TestDriftLockCheck38:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P1 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 38

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_registry_cohesion.py"
        assert primary.exists(), (
            "tests/preflight/test_registry_cohesion.py was deleted — restore it."
        )

    def test_master_yaml_still_within_limit(self) -> None:
        """Regression: cortex-master.yaml must remain ≤ 500 lines."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml not found")
        lines = len(MASTER_YAML.read_text(encoding="utf-8").splitlines())
        assert lines <= 500, (
            f"cortex-master.yaml grew to {lines} lines — Thin Index Contract violated (max 500)."
        )

    def test_drift_locks_directory_still_exists(self) -> None:
        assert DRIFT_LOCKS_DIR.exists(), (
            "cortex-registry/governance/drift-locks/ was deleted — restore it."
        )
