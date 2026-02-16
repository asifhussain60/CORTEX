"""Shared fixtures for secrets tests."""

import os
import pytest


@pytest.fixture(autouse=True)
def _set_master_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure CORTEX_MASTER_KEY is set for all secrets tests."""
    monkeypatch.setenv(
        "CORTEX_MASTER_KEY",
        "test-master-key-for-unit-tests-only-32b",
    )
