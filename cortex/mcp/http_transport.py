"""
MCP HTTP Transport — FastAPI-based HTTP layer over the CORTEX MCP server.

Provides:
- GET  /health        — unauthenticated liveness probe (K8s / load-balancer)
- GET  /health/ready  — unauthenticated readiness probe
- GET  /tools/list    — authenticated list of all registered MCP tools
- POST /tools/call    — authenticated MCP tool invocation

Authentication is enforced on all /tools/* routes via ApiKeyAuthMiddleware.
Health routes are intentionally public (no auth required).

Authority: Phase 99-C (Secure MCP wiring)
AC-ID: AC-P99-C-001
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from cortex.mcp.auth_middleware import ApiKeyAuthMiddleware, AuthenticationError

logger = logging.getLogger(__name__)


# ============================================================================
# FACTORY
# ============================================================================


def create_app(
    secrets_manager: Any,
    *,
    header_name: str = "X-API-Key",
    title: str = "CORTEX MCP HTTP Transport",
    version: str = "1.0.0",
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        secrets_manager: A ``SecretsManager`` instance used to validate API keys.
        header_name: HTTP header carrying the API key (default ``"X-API-Key"``).
        title: OpenAPI title for the app.
        version: OpenAPI version string.

    Returns:
        A configured ``FastAPI`` instance ready to serve.
    """
    app = FastAPI(title=title, version=version)
    auth = ApiKeyAuthMiddleware(secrets_manager=secrets_manager, header_name=header_name)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _require_auth(request: Request) -> None:
        """Raise HTTPException(401) if the request fails authentication."""
        raw = dict(request.headers)
        # FastAPI lowercases header names; normalise to the configured key
        normalised_key = header_name.lower()
        # Rebuild headers dict in original case expected by middleware
        headers = {header_name: raw.get(normalised_key, raw.get(header_name, ""))}
        try:
            auth.enforce({"headers": headers})
        except AuthenticationError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    # ------------------------------------------------------------------
    # Health routes — public, no auth
    # ------------------------------------------------------------------

    @app.get("/health", tags=["health"], summary="Liveness probe")
    async def health_liveness() -> JSONResponse:
        """Return HTTP 200 with ``{"status": "ok"}`` — no auth required."""
        return JSONResponse({"status": "ok", "service": "cortex-mcp"})

    @app.get("/health/ready", tags=["health"], summary="Readiness probe")
    async def health_readiness() -> JSONResponse:
        """Return HTTP 200 when the service is ready to serve traffic."""
        return JSONResponse({"status": "ok", "ready": True})

    # ------------------------------------------------------------------
    # Tools routes — authentication required
    # ------------------------------------------------------------------

    @app.get("/tools/list", tags=["tools"], summary="List all MCP tools")
    async def tools_list(request: Request) -> JSONResponse:
        """Return metadata for all registered MCP tools.

        Requires a valid ``X-API-Key`` header.

        Returns:
            JSON array of tool metadata objects.
        """
        _require_auth(request)
        try:
            from cortex.mcp.mcp_registry import get_registry

            registry = get_registry()
            tools: List[Dict[str, Any]] = registry.to_mcp_schema()
            return JSONResponse(tools)
        except Exception as exc:  # pragma: no cover
            logger.error("tools/list error: %s", exc)
            raise HTTPException(status_code=500, detail="Internal error listing tools") from exc

    @app.post("/tools/call", tags=["tools"], summary="Invoke an MCP tool")
    async def tools_call(request: Request) -> JSONResponse:
        """Invoke a named MCP tool with the given parameters.

        Requires a valid ``X-API-Key`` header.

        Expected JSON body::

            {"tool": "<tool_name>", "params": {...}}

        Returns:
            JSON result from the tool, or an error response.
        """
        _require_auth(request)
        try:
            body: Dict[str, Any] = await request.json()
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid JSON body")

        tool_name: Optional[str] = body.get("tool")
        params: Dict[str, Any] = body.get("params", {})

        if not tool_name:
            raise HTTPException(status_code=422, detail="'tool' field is required")

        try:
            from cortex.mcp.mcp_registry import get_registry

            registry = get_registry()
            tool = registry.get(tool_name)
            if tool is None:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

            result = await tool.execute(params) if hasattr(tool, "execute") else tool.run(params)
            return JSONResponse({"tool": tool_name, "result": result})
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover
            logger.error("tools/call '%s' error: %s", tool_name, exc)
            raise HTTPException(status_code=500, detail=f"Tool execution failed: {exc}") from exc

    return app
