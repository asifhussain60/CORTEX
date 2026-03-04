"""Drift lock test — Check #34: No-Versioning-Anywhere Guardrail.

Permanent CI guardrail. Fails if the drift lock YAML is removed or version
fields reappear in governance/workflow/template YAML files.

Gap ref: GAP-126-05
Phase: phase-126-e
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-34-no-versioning-lock.yaml"


class TestDriftLockCheck34:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P0 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 34

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_no_versioning_anywhere.py"
        assert primary.exists(), (
            "tests/preflight/test_no_versioning_anywhere.py was deleted — restore it."
        )

    def test_atom_principle_has_no_version_field(self) -> None:
        """Regression: atom-principle.yaml must not re-acquire version: field."""
        import re  # noqa: PLC0415
        atom = (
            CORTEX_ROOT
            / "cortex-registry"
            / "templates"
            / "response"
            / "atoms"
            / "atom-principle.yaml"
        )
        if not atom.exists():
            pytest.skip("atom-principle.yaml not found")
        content = atom.read_text(encoding="utf-8")
        version_pattern = re.compile(r"^\s*version\s*:\s*\S", re.MULTILINE)
        assert not version_pattern.search(content), (
            "atom-principle.yaml re-acquired a version: field — remove it."
        )
