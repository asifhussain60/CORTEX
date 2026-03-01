"""
Tests for SecretsManager API key generation and validation.

TDD: RED phase — these tests define the contract before implementation.

Authority: Phase 99-A (Secure MCP wiring)
AC-ID: AC-P99-A-001
CORE-008: Tests written before implementation (RED → GREEN → REFACTOR)
"""

from __future__ import annotations

import time
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def manager(tmp_path: Any) -> "SecretsManager":
    """Provide a SecretsManager with tmp storage for isolation."""
    from cortex.infrastructure.secrets.secrets_manager import SecretsManager

    return SecretsManager(
        master_key="test-master-key-32bytes-exactly!!",
        storage_path=str(tmp_path / "secrets"),
    )


# ---------------------------------------------------------------------------
# generate_api_key — contract tests
# ---------------------------------------------------------------------------

class TestGenerateApiKey:
    """AC-P99-A-001: generate_api_key produces secure, unique tokens."""

    def test_returns_string(self, manager: Any) -> None:
        """generate_api_key must return a str."""
        key = manager.generate_api_key()
        assert isinstance(key, str), "generate_api_key must return str"

    def test_minimum_length(self, manager: Any) -> None:
        """Generated key must be at least 43 chars (256-bit urlsafe-base64)."""
        key = manager.generate_api_key()
        assert len(key) >= 43, f"Key too short: {len(key)} chars"

    def test_keys_are_unique(self, manager: Any) -> None:
        """Two successive calls must produce different keys."""
        k1 = manager.generate_api_key()
        k2 = manager.generate_api_key()
        assert k1 != k2, "generate_api_key must never return the same value twice"

    def test_key_urlsafe_characters_only(self, manager: Any) -> None:
        """Key must contain only URL-safe base64 characters (no +, /, =)."""
        import re
        key = manager.generate_api_key()
        assert re.match(r'^[A-Za-z0-9_\-]+$', key), (
            f"Key contains non-URL-safe chars: {key!r}"
        )

    def test_prefix_option(self, manager: Any) -> None:
        """Caller may request a prefix (e.g. 'cx_live_') prepended."""
        key = manager.generate_api_key(prefix="cx_live_")
        assert key.startswith("cx_live_"), (
            f"Expected prefix 'cx_live_', got: {key!r}"
        )

    def test_stores_hashed_key_in_vault(self, manager: Any) -> None:
        """Generated key must be stored (hashed) so validate_api_key works."""
        key = manager.generate_api_key(key_id="mcp_gateway")
        stored = manager.list_api_keys()
        assert "mcp_gateway" in stored, (
            "generate_api_key must persist the key_id to the vault"
        )

    def test_bulk_generation_all_unique(self, manager: Any) -> None:
        """100 successive keys must all be unique."""
        keys = {manager.generate_api_key() for _ in range(100)}
        assert len(keys) == 100, "Collision detected in bulk generation"


# ---------------------------------------------------------------------------
# validate_api_key — contract tests
# ---------------------------------------------------------------------------

class TestValidateApiKey:
    """AC-P99-A-002: validate_api_key enforces constant-time comparison."""

    def test_valid_key_returns_true(self, manager: Any) -> None:
        """A key just generated must validate successfully."""
        key = manager.generate_api_key(key_id="test_key")
        assert manager.validate_api_key(key) is True

    def test_invalid_key_returns_false(self, manager: Any) -> None:
        """A random string must not validate."""
        assert manager.validate_api_key("not-a-real-key") is False

    def test_empty_string_returns_false(self, manager: Any) -> None:
        """Empty string must never validate (guards header-absent case)."""
        assert manager.validate_api_key("") is False

    def test_modified_key_returns_false(self, manager: Any) -> None:
        """Tampered key (one char changed) must not validate."""
        key = manager.generate_api_key(key_id="tamper_test")
        tampered = key[:-1] + ("X" if key[-1] != "X" else "Y")
        assert manager.validate_api_key(tampered) is False

    def test_revoked_key_returns_false(self, manager: Any) -> None:
        """Key revoked via revoke_api_key must no longer validate."""
        key = manager.generate_api_key(key_id="revoke_me")
        manager.revoke_api_key("revoke_me")
        assert manager.validate_api_key(key) is False

    def test_constant_time_comparison(self, manager: Any) -> None:
        """
        Validate runs in constant time regardless of key validity.

        Timing attack resistance: difference between valid and invalid key
        validation must be < 5ms (not statistically distinguishable over
        10 iterations).  This is a smoke-level check, not a crypto proof.
        """
        key = manager.generate_api_key(key_id="timing_key")

        valid_times = []
        for _ in range(10):
            start = time.perf_counter()
            manager.validate_api_key(key)
            valid_times.append(time.perf_counter() - start)

        invalid_times = []
        for _ in range(10):
            start = time.perf_counter()
            manager.validate_api_key("completely-invalid-key-string-xxxx")
            invalid_times.append(time.perf_counter() - start)

        avg_valid = sum(valid_times) / len(valid_times)
        avg_invalid = sum(invalid_times) / len(invalid_times)
        diff_ms = abs(avg_valid - avg_invalid) * 1000

        assert diff_ms < 10, (
            f"Timing difference {diff_ms:.2f}ms exceeds 10ms threshold — "
            "possible timing oracle vulnerability"
        )

    def test_none_returns_false(self, manager: Any) -> None:
        """None input must not raise — return False gracefully."""
        assert manager.validate_api_key(None) is False  # type: ignore[arg-type]

    def test_key_from_different_manager_instance_validates(self, manager: Any, tmp_path: Any) -> None:
        """Key generated by one manager instance validates in another sharing the same vault."""
        from cortex.infrastructure.secrets.secrets_manager import SecretsManager

        vault_dir = str(tmp_path / "shared_vault")
        mgr1 = SecretsManager(
            master_key="test-master-key-32bytes-exactly!!",
            storage_path=vault_dir,
        )
        mgr2 = SecretsManager(
            master_key="test-master-key-32bytes-exactly!!",
            storage_path=vault_dir,
        )
        key = mgr1.generate_api_key(key_id="shared_key")
        assert mgr2.validate_api_key(key) is True


# ---------------------------------------------------------------------------
# list_api_keys / revoke_api_key — lifecycle tests
# ---------------------------------------------------------------------------

class TestApiKeyLifecycle:
    """AC-P99-A-003: Full API key lifecycle — generate, list, revoke."""

    def test_list_returns_key_ids(self, manager: Any) -> None:
        """list_api_keys returns the key_ids, never the raw keys."""
        manager.generate_api_key(key_id="key_alpha")
        manager.generate_api_key(key_id="key_beta")
        ids = manager.list_api_keys()
        assert "key_alpha" in ids
        assert "key_beta" in ids

    def test_list_never_returns_raw_key(self, manager: Any) -> None:
        """list_api_keys must not expose raw key material."""
        raw = manager.generate_api_key(key_id="secret_key")
        ids = manager.list_api_keys()
        for entry in ids.values():
            assert raw not in str(entry), (
                "list_api_keys must never expose raw key material"
            )

    def test_revoke_removes_from_list(self, manager: Any) -> None:
        """Revoked key_id must disappear from list_api_keys."""
        manager.generate_api_key(key_id="ephemeral")
        manager.revoke_api_key("ephemeral")
        assert "ephemeral" not in manager.list_api_keys()

    def test_revoke_nonexistent_raises(self, manager: Any) -> None:
        """Revoking an unknown key_id must raise SecretsError."""
        from cortex.infrastructure.secrets.errors import SecretsError

        with pytest.raises(SecretsError):
            manager.revoke_api_key("does_not_exist")

    def test_audit_trail_records_generation(self, manager: Any) -> None:
        """generate_api_key must append to the audit trail."""
        manager.generate_api_key(key_id="audit_gen")
        trail = manager.get_audit_trail()
        events = trail.get("events", [])
        ops = [e.get("operation", "") for e in events]
        assert any("generate_api_key" in op or "API_KEY_GENERATED" in op for op in ops), (
            "Audit trail must record API key generation events"
        )

    def test_audit_trail_records_revocation(self, manager: Any) -> None:
        """revoke_api_key must append to the audit trail."""
        manager.generate_api_key(key_id="audit_rev")
        manager.revoke_api_key("audit_rev")
        trail = manager.get_audit_trail()
        events = trail.get("events", [])
        ops = [e.get("operation", "") for e in events]
        assert any("revoke_api_key" in op or "API_KEY_REVOKED" in op for op in ops), (
            "Audit trail must record API key revocation events"
        )
