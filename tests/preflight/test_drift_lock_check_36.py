"""Drift lock test — Check #36: Prompt/Governance Determinism Validation.

Permanent CI guardrail. Fails if the drift lock YAML is removed or agents
regress to hedging/non-imperative language.

Gap ref: GAP-126-07
Phase: phase-126-g
"""
from __future__ import annotations

import pathlib

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
DRIFT_LOCKS_DIR = CORTEX_ROOT / "cortex-registry" / "governance" / "drift-locks"
LOCK_FILE = DRIFT_LOCKS_DIR / "check-36-prompt-determinism-lock.yaml"


class TestDriftLockCheck36:
    def test_lock_file_exists(self) -> None:
        assert LOCK_FILE.exists(), (
            f"Drift lock {LOCK_FILE.name} was deleted — P1 governance violation."
        )

    def test_lock_file_is_valid_yaml(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 36

    def test_lock_status_is_active(self) -> None:
        if not LOCK_FILE.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        assert data.get("status") == "ACTIVE"

    def test_primary_test_file_exists(self) -> None:
        primary = CORTEX_ROOT / "tests" / "preflight" / "test_prompt_governance_determinism.py"
        assert primary.exists(), (
            "tests/preflight/test_prompt_governance_determinism.py was deleted — restore it."
        )

    def test_copilot_instructions_still_has_p0(self) -> None:
        """Regression: copilot-instructions.md must retain P0 governance rule."""
        instructions = CORTEX_ROOT / ".github" / "copilot-instructions.md"
        if not instructions.exists():
            pytest.skip("copilot-instructions.md not found")
        content = instructions.read_text(encoding="utf-8")
        assert "P0" in content, (
            "copilot-instructions.md lost its P0 governance rule reference."
        )
