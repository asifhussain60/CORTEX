"""Drift lock test — Check #39: cortex-sync Non-Production Admin Tool Marker Enforcement.

Permanent CI guardrail. Fails if drift lock is removed or non-production marker
invariants are violated.

Gap ref: GAP-126-10
Phase: phase-126-j
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-39-sync-marker-lock.yaml"
SYNC_PROMPT = CORTEX_ROOT / ".github" / "prompts" / "cortex-sync.prompt.md"


class TestDriftLockCheck39:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P1 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 39

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_sync_non_production_markers.py"
        assert primary.exists(), (
            "tests/preflight/test_sync_non_production_markers.py was deleted — restore it."
        )

    def test_cortex_sync_still_has_production_files_key(self) -> None:
        """Regression: cortex-sync.prompt.md must still declare production_files."""
        if not SYNC_PROMPT.exists():
            pytest.skip("cortex-sync.prompt.md not found")
        content = SYNC_PROMPT.read_text(encoding="utf-8")
        assert "production_files:" in content, (
            "cortex-sync.prompt.md lost its 'production_files:' exclusion list — restore it."
        )

    def test_lock_declares_production_files(self) -> None:
        """Lock YAML must enumerate production_files."""
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert "production_files" in data, "Lock YAML must include production_files list."
        assert len(data["production_files"]) >= 6, (
            "production_files list must have at least 6 entries."
        )
