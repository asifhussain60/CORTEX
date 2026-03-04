"""Drift lock test — Check #37: Response Template Canonicalization Enforcement.

Permanent CI guardrail. Fails if drift lock YAML is removed or composition
files are deleted/corrupted.

Gap ref: GAP-126-08
Phase: phase-126-h
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-37-response-template-lock.yaml"
COMPOSITIONS_DIR = (
    CORTEX_ROOT / "cortex-registry" / "templates" / "response" / "compositions"
)


class TestDriftLockCheck37:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P1 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 37

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "golden" / "test_response_template_format_canon.py"
        assert primary.exists(), (
            "tests/golden/test_response_template_format_canon.py was deleted — restore it."
        )

    def test_compositions_directory_still_exists(self) -> None:
        assert COMPOSITIONS_DIR.exists(), (
            "cortex-registry/templates/response/compositions/ was deleted — restore it."
        )

    def test_all_eight_compositions_still_exist(self) -> None:
        """Regression: all 8 Phase 120 compositions must remain present."""
        required = {
            "comp-implement-fix", "comp-refactor", "comp-audit-fix",
            "comp-health", "comp-vacuum", "comp-debug", "comp-query", "comp-introduce",
        }
        present = {p.stem for p in COMPOSITIONS_DIR.glob("comp-*.yaml")}
        missing = required - present
        assert not missing, (
            f"Phase 120 compositions deleted: {', '.join(sorted(missing))}"
        )
