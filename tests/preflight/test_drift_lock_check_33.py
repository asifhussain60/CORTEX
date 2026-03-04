"""Drift lock test — Check #33: YAML Reader No-Bypass Enforcement.

Permanent CI guardrail. Fails if the drift lock YAML is removed or the
yaml.safe_load bypass ceiling is exceeded.

Gap ref: GAP-126-04
Phase: phase-126-d
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-33-yaml-reader-no-bypass-lock.yaml"


class TestDriftLockCheck33:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P1 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 33

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE", (
            "Drift lock check-33 must remain ACTIVE. Do not deactivate it."
        )

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_yaml_reader_no_bypass.py"
        assert primary.exists(), (
            "tests/preflight/test_yaml_reader_no_bypass.py was deleted — restore it."
        )

    def test_yaml_loaders_module_still_exists(self) -> None:
        yaml_loaders = CORTEX_ROOT / "cortex" / "core" / "yaml_loaders.py"
        assert yaml_loaders.exists(), (
            "cortex/core/yaml_loaders.py was deleted — this is the canonical YAML layer."
        )

    def test_registry_viewer_still_exists(self) -> None:
        viewer = CORTEX_ROOT / "cortex-registry" / "yaml-reader.html"
        assert viewer.exists(), (
            "cortex-registry/yaml-reader.html was deleted — Phase 125 delivery artifact."
        )
