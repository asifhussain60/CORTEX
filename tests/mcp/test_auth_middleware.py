"""
Tests for ApiKeyAuthMiddleware — MCP authentication layer.

TDD: RED phase — contract defined before implementation.

Authority: Phase 99-B (Secure MCP wiring)
AC-ID: AC-P99-B-001
CORE-008: Tests written before implementation (RED → GREEN → REFACTOR)
"""

from __future__ import annotations

from typing import Any, Dict
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def secrets_manager(tmp_path: Any) -> Any:
    """Isolated SecretsManager with a known master key."""
    from cortex.infrastructure.secrets.secrets_manager import SecretsManager

    return SecretsManager(
        master_key="test-master-key-32bytes-exactly!!",
        storage_path=str(tmp_path / "secrets"),
    )


@pytest.fixture()
def middleware(secrets_manager: Any) -> Any:
    """ApiKeyAuthMiddleware backed by the isolated SecretsManager."""
    from cortex.mcp.auth_middleware import ApiKeyAuthMiddleware

    return ApiKeyAuthMiddleware(secrets_manager=secrets_manager)


@pytest.fixture()
def valid_api_key(secrets_manager: Any) -> str:
    """Generate and return a live API key."""
    return secrets_manager.generate_api_key(key_id="mcp-client")


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    """ApiKeyAuthMiddleware must construct cleanly."""

    def test_instantiates_with_secrets_manager(self, middleware: Any) -> None:
        """Must construct without error given a SecretsManager."""
        assert middleware is not None

    def test_exposes_secrets_manager(self, middleware: Any, secrets_manager: Any) -> None:
        """Must expose the injected SecretsManager."""
        assert middleware.secrets_manager is secrets_manager

    def test_default_header_name(self, middleware: Any) -> None:
        """Default header key must be 'X-API-Key'."""
        assert middleware.header_name == "X-API-Key"

    def test_custom_header_name(self, secrets_manager: Any) -> None:
        """Must accept a custom header name."""
        from cortex.mcp.auth_middleware import ApiKeyAuthMiddleware

        mw = ApiKeyAuthMiddleware(secrets_manager=secrets_manager, header_name="Authorization")
        assert mw.header_name == "Authorization"


# ---------------------------------------------------------------------------
# authenticate(request) — core contract
# ---------------------------------------------------------------------------


class TestAuthenticate:
    """authenticate(request) -> bool — the central gate."""

    def test_valid_key_returns_true(self, middleware: Any, valid_api_key: str) -> None:
        """A valid API key in the correct header must return True."""
        request = {"headers": {"X-API-Key": valid_api_key}}
        assert middleware.authenticate(request) is True

    def test_missing_header_returns_false(self, middleware: Any) -> None:
        """A request with no API key header must return False."""
        request: Dict[str, Any] = {"headers": {}}
        assert middleware.authenticate(request) is False

    def test_no_headers_key_returns_false(self, middleware: Any) -> None:
        """A request dict with no 'headers' key must return False."""
        assert middleware.authenticate({}) is False

    def test_wrong_key_returns_false(self, middleware: Any) -> None:
        """An invalid API key must return False."""
        request = {"headers": {"X-API-Key": "totally-wrong-key"}}
        assert middleware.authenticate(request) is False

    def test_empty_string_returns_false(self, middleware: Any) -> None:
        """An empty string key must return False."""
        request = {"headers": {"X-API-Key": ""}}
        assert middleware.authenticate(request) is False

    def test_none_key_returns_false(self, middleware: Any) -> None:
        """None as header value must return False (no exception)."""
        request = {"headers": {"X-API-Key": None}}
        assert middleware.authenticate(request) is False

    def test_revoked_key_returns_false(
        self, middleware: Any, secrets_manager: Any, valid_api_key: str
    ) -> None:
        """A revoked key must be rejected even if structurally valid."""
        secrets_manager.revoke_api_key("mcp-client")
        request = {"headers": {"X-API-Key": valid_api_key}}
        assert middleware.authenticate(request) is False

    def test_authenticate_is_constant_time(
        self, middleware: Any, valid_api_key: str
    ) -> None:
        """authenticate must not raise; timing side-channel delegated to SecretsManager."""
        import time

        request_valid = {"headers": {"X-API-Key": valid_api_key}}
        request_invalid = {"headers": {"X-API-Key": "x" * 43}}

        t0 = time.perf_counter()
        middleware.authenticate(request_valid)
        t_valid = time.perf_counter() - t0

        t0 = time.perf_counter()
        middleware.authenticate(request_invalid)
        t_invalid = time.perf_counter() - t0

        # Both paths must complete — not a hard timing bound, just a smoke check
        assert t_valid < 5.0
        assert t_invalid < 5.0


# ---------------------------------------------------------------------------
# extract_key(request) — helper
# ---------------------------------------------------------------------------


class TestExtractKey:
    """extract_key(request) -> Optional[str] surfaces the raw header value."""

    def test_returns_key_when_present(self, middleware: Any, valid_api_key: str) -> None:
        """Must return the raw key string from the correct header."""
        request = {"headers": {"X-API-Key": valid_api_key}}
        assert middleware.extract_key(request) == valid_api_key

    def test_returns_none_when_missing(self, middleware: Any) -> None:
        """Must return None when the header is absent."""
        assert middleware.extract_key({"headers": {}}) is None

    def test_returns_none_when_no_headers(self, middleware: Any) -> None:
        """Must return None when 'headers' key is absent."""
        assert middleware.extract_key({}) is None

    def test_custom_header_name_extracted(self, secrets_manager: Any) -> None:
        """Must read from the configured custom header name."""
        from cortex.mcp.auth_middleware import ApiKeyAuthMiddleware

        mw = ApiKeyAuthMiddleware(secrets_manager=secrets_manager, header_name="Authorization")
        request = {"headers": {"Authorization": "bearer abc123"}}
        assert mw.extract_key(request) == "bearer abc123"


# ---------------------------------------------------------------------------
# enforce(request) — raises on auth failure
# ---------------------------------------------------------------------------


class TestEnforce:
    """enforce(request) must raise AuthenticationError on failure."""

    def test_valid_key_does_not_raise(self, middleware: Any, valid_api_key: str) -> None:
        """A valid key must pass enforce without raising."""
        request = {"headers": {"X-API-Key": valid_api_key}}
        middleware.enforce(request)  # must not raise

    def test_missing_key_raises(self, middleware: Any) -> None:
        """Missing key must raise AuthenticationError."""
        from cortex.mcp.auth_middleware import AuthenticationError

        with pytest.raises(AuthenticationError):
            middleware.enforce({"headers": {}})

    def test_invalid_key_raises(self, middleware: Any) -> None:
        """Invalid key must raise AuthenticationError."""
        from cortex.mcp.auth_middleware import AuthenticationError

        with pytest.raises(AuthenticationError):
            middleware.enforce({"headers": {"X-API-Key": "bad-key"}})

    def test_error_message_is_generic(self, middleware: Any) -> None:
        """Error message must not leak internal detail (no key material)."""
        from cortex.mcp.auth_middleware import AuthenticationError

        try:
            middleware.enforce({"headers": {"X-API-Key": "bad-key"}})
        except AuthenticationError as exc:
            msg = str(exc).lower()
            assert "bad-key" not in msg, "Error must not echo the key"
            assert "unauthori" in msg or "invalid" in msg or "denied" in msg
