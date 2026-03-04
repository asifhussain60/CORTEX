"""Drift lock test — Check #40: Production Readiness Validation Suite Orchestrator.

Permanent CI guardrail. Fails if drift lock is removed or the preflight
orchestrator loses its evidence emission capability.

Gap ref: GAP-126-11
Phase: phase-126-k
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-40-production-readiness-orchestrator-lock.yaml"
RUN_TESTS_SCRIPT = CORTEX_ROOT / "scripts" / "run_tests.py"


class TestDriftLockCheck40:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P0 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 40

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_production_readiness_orchestrator.py"
        assert primary.exists(), (
            "tests/preflight/test_production_readiness_orchestrator.py was deleted — restore it."
        )

    def test_run_tests_script_still_has_preflight_mode(self) -> None:
        """Regression: scripts/run_tests.py must still have preflight mode."""
        assert RUN_TESTS_SCRIPT.exists(), "scripts/run_tests.py is missing."
        content = RUN_TESTS_SCRIPT.read_text(encoding="utf-8")
        assert "run_preflight" in content, (
            "scripts/run_tests.py lost its run_preflight function."
        )

    def test_run_tests_script_still_emits_evidence(self) -> None:
        """Regression: run_preflight must still call _emit_preflight_evidence."""
        assert RUN_TESTS_SCRIPT.exists(), "scripts/run_tests.py is missing."
        content = RUN_TESTS_SCRIPT.read_text(encoding="utf-8")
        assert "_emit_preflight_evidence" in content, (
            "scripts/run_tests.py lost evidence emission — restore _emit_preflight_evidence."
        )
