"""
Tests for MCP HTTP Transport — FastAPI-based HTTP/SSE layer over the MCP server.

TDD: RED phase — contract defined before implementation.

Authority: Phase 99-C (Secure MCP wiring)
AC-ID: AC-P99-C-001
CORE-008: Tests written before implementation (RED → GREEN → REFACTOR)
"""

from __future__ import annotations

from typing import Any
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def secrets_manager(tmp_path: Any) -> Any:
    """Isolated SecretsManager."""
    from cortex.infrastructure.secrets.secrets_manager import SecretsManager

    return SecretsManager(
        master_key="test-master-key-32bytes-exactly!!",
        storage_path=str(tmp_path / "secrets"),
    )


@pytest.fixture()
def api_key(secrets_manager: Any) -> str:
    """A live API key registered in the SecretsManager."""
    return secrets_manager.generate_api_key(key_id="http-client")


@pytest.fixture()
def app(secrets_manager: Any) -> Any:
    """Return the FastAPI app instance under test."""
    from cortex.mcp.http_transport import create_app

    return create_app(secrets_manager=secrets_manager)


@pytest.fixture()
def client(app: Any) -> Any:
    """Synchronous TestClient wrapping the FastAPI app."""
    from fastapi.testclient import TestClient

    return TestClient(app, raise_server_exceptions=True)


# ---------------------------------------------------------------------------
# create_app — construction
# ---------------------------------------------------------------------------


class TestCreateApp:
    """create_app() must return a usable FastAPI application."""

    def test_returns_fastapi_app(self, app: Any) -> None:
        """create_app must return a FastAPI instance."""
        from fastapi import FastAPI

        assert isinstance(app, FastAPI)

    def test_app_has_title(self, app: Any) -> None:
        """App title must reference CORTEX MCP."""
        assert "cortex" in app.title.lower() or "mcp" in app.title.lower()


# ---------------------------------------------------------------------------
# GET /health — unauthenticated liveness probe
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """GET /health must be accessible without an API key."""

    def test_health_returns_200(self, client: Any) -> None:
        """/health must return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_body_has_status(self, client: Any) -> None:
        """/health JSON body must contain a 'status' key."""
        response = client.get("/health")
        assert "status" in response.json()

    def test_health_status_is_ok(self, client: Any) -> None:
        """/health status value must indicate healthy."""
        body = client.get("/health").json()
        assert body["status"] in ("ok", "healthy", "UP")

    def test_health_no_auth_required(self, client: Any) -> None:
        """/health must succeed with no X-API-Key header."""
        response = client.get("/health", headers={})
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# GET /health/ready — unauthenticated readiness probe
# ---------------------------------------------------------------------------


class TestReadinessEndpoint:
    """GET /health/ready must be accessible without an API key."""

    def test_ready_returns_200(self, client: Any) -> None:
        """/health/ready must return HTTP 200."""
        response = client.get("/health/ready")
        assert response.status_code == 200

    def test_ready_body_has_status(self, client: Any) -> None:
        """/health/ready must contain a 'status' key."""
        assert "status" in client.get("/health/ready").json()


# ---------------------------------------------------------------------------
# POST /tools/call — authenticated tool invocation
# ---------------------------------------------------------------------------


class TestToolsCallEndpoint:
    """POST /tools/call must require a valid API key."""

    def test_missing_auth_returns_401(self, client: Any) -> None:
        """No API key must yield HTTP 401."""
        response = client.post("/tools/call", json={"tool": "ping", "params": {}})
        assert response.status_code == 401

    def test_invalid_auth_returns_401(self, client: Any) -> None:
        """An invalid API key must yield HTTP 401."""
        response = client.post(
            "/tools/call",
            json={"tool": "ping", "params": {}},
            headers={"X-API-Key": "invalid-key"},
        )
        assert response.status_code == 401

    def test_valid_auth_not_401(self, client: Any, api_key: str) -> None:
        """A valid API key must NOT yield 401 (tool may not exist → 404/422, but not 401)."""
        response = client.post(
            "/tools/call",
            json={"tool": "ping", "params": {}},
            headers={"X-API-Key": api_key},
        )
        assert response.status_code != 401

    def test_error_body_is_json(self, client: Any) -> None:
        """401 response must return a JSON body."""
        response = client.post("/tools/call", json={"tool": "ping", "params": {}})
        assert response.headers.get("content-type", "").startswith("application/json")


# ---------------------------------------------------------------------------
# GET /tools/list — authenticated tool listing
# ---------------------------------------------------------------------------


class TestToolsListEndpoint:
    """GET /tools/list must require a valid API key."""

    def test_missing_auth_returns_401(self, client: Any) -> None:
        """No key → 401."""
        assert client.get("/tools/list").status_code == 401

    def test_invalid_auth_returns_401(self, client: Any) -> None:
        """Bad key → 401."""
        assert (
            client.get("/tools/list", headers={"X-API-Key": "bad"}).status_code == 401
        )

    def test_valid_auth_returns_200(self, client: Any, api_key: str) -> None:
        """Valid key → 200 with tool list."""
        response = client.get("/tools/list", headers={"X-API-Key": api_key})
        assert response.status_code == 200

    def test_tools_list_body_is_list(self, client: Any, api_key: str) -> None:
        """Body must be a JSON array (or dict with a 'tools' list)."""
        response = client.get("/tools/list", headers={"X-API-Key": api_key})
        body = response.json()
        assert isinstance(body, list) or (isinstance(body, dict) and "tools" in body)
