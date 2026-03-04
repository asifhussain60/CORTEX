"""Drift lock test — Check #35: Repository Hygiene and Production Purity.

Permanent CI guardrail. Fails if the drift lock YAML is removed or repo
acquires backup/archive/dead-code artifacts.

Gap ref: GAP-126-06
Phase: phase-126-f
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-35-repo-hygiene-lock.yaml"


class TestDriftLockCheck35:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P1 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 35

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_repo_hygiene_purity.py"
        assert primary.exists(), (
            "tests/preflight/test_repo_hygiene_purity.py was deleted — restore it."
        )

    def test_vacuum_orchestrator_still_exists(self) -> None:
        """VacuumOrchestrator must not be deleted — it is the purity sweep anchor."""
        candidates = list(
            (CORTEX_ROOT / "cortex" / "orchestrators").rglob("*vacuum*orchestrator*.py")
        )
        assert candidates, "VacuumOrchestrator was deleted — restore it."
