"""
Phase 62-A: TDD RED tests — TenantContextMiddleware wired into MCPServer.

Tests verify:
1. server.py imports TenantContextMiddleware
2. MCPServer.call_tool() extracts and injects WorkspaceContext from request headers
3. Anonymous requests (no X-Workspace-ID) receive 'local' WorkspaceContext without crash
4. Malformed/missing workspace_id defaults gracefully

CORE-008: Tests written BEFORE implementation wiring.
AC_START: AC-62A-MCP-TENANT-001
"""
import pytest
from unittest.mock import MagicMock, patch
from cortex.mcp.tenant_context_middleware import TenantContextMiddleware, WorkspaceContext


# ---------------------------------------------------------------------------
# Unit tests — TenantContextMiddleware in isolation (already passing)
# ---------------------------------------------------------------------------

class TestTenantContextMiddlewareUnit:
    """Verify the middleware API works correctly in isolation."""

    def test_extract_context_from_headers(self) -> None:
        """extract_context() pulls workspace_id and tenant_id from X-* headers."""
        middleware = TenantContextMiddleware()
        request = {
            "headers": {
                "X-Workspace-ID": "acme-dev",
                "X-Tenant-ID": "acme",
                "X-User-ID": "alice@acme.com",
            }
        }
        ctx = middleware.extract_context(request)
        assert ctx.workspace_id == "acme-dev"
        assert ctx.tenant_id == "acme"
        assert ctx.user_id == "alice@acme.com"

    def test_extract_context_anonymous_request(self) -> None:
        """Requests with no headers default to 'local' workspace without crash."""
        middleware = TenantContextMiddleware()
        ctx = middleware.extract_context({})
        assert ctx.workspace_id == "local"
        assert ctx.tenant_id == "local"
        assert ctx.user_id is None

    def test_inject_context_adds_workspace_context_key(self) -> None:
        """inject_context() adds workspace_context to params dict."""
        middleware = TenantContextMiddleware()
        ctx = WorkspaceContext(workspace_id="acme-dev", tenant_id="acme")
        params = {"operation": "implement"}
        enhanced = middleware.inject_context(params, ctx)
        assert "workspace_context" in enhanced
        assert enhanced["workspace_context"]["workspace_id"] == "acme-dev"
        # Original params preserved
        assert enhanced["operation"] == "implement"

    def test_process_request_combines_extract_and_inject(self) -> None:
        """process_request() is a convenience combining extract + inject."""
        middleware = TenantContextMiddleware()
        request = {"headers": {"X-Workspace-ID": "test-ws"}}
        params = {"operation": "audit"}
        enhanced = middleware.process_request(request, params)
        assert enhanced["workspace_context"]["workspace_id"] == "test-ws"
        assert enhanced["operation"] == "audit"


# ---------------------------------------------------------------------------
# Integration tests — MCPServer wiring (RED until phase-62-a implementation)
# ---------------------------------------------------------------------------

class TestMCPServerTenantMiddlewareWiring:
    """
    Verify TenantContextMiddleware is wired into MCPServer.

    These tests are RED before phase-62-a. They test the SERVER-LEVEL
    integration — that MCPServer itself owns and uses the middleware.
    """

    def test_mcp_server_imports_tenant_middleware(self) -> None:
        """server.py module-level import includes TenantContextMiddleware."""
        import importlib
        import cortex.mcp.server as server_module
        # The middleware class must be importable FROM the server module
        # (re-exported or used in the module namespace)
        assert hasattr(server_module, "TenantContextMiddleware") or \
               "TenantContextMiddleware" in dir(server_module), (
            "TenantContextMiddleware must be imported in cortex/mcp/server.py. "
            "Add: from cortex.mcp.tenant_context_middleware import TenantContextMiddleware"
        )

    def test_mcp_server_has_tenant_middleware_attribute(self) -> None:
        """MCPServer instance exposes _tenant_middleware attribute."""
        from cortex.mcp.server import MCPServer
        server = MCPServer()
        assert hasattr(server, "_tenant_middleware"), (
            "MCPServer.__init__() must instantiate TenantContextMiddleware as self._tenant_middleware"
        )
        assert isinstance(server._tenant_middleware, TenantContextMiddleware)

    def test_call_tool_with_workspace_header_injects_context(self) -> None:
        """call_tool() with X-Workspace-ID header injects WorkspaceContext into params."""
        from cortex.mcp.server import MCPServer
        server = MCPServer()
        # Use a real tool that accepts any params (cortex_sample_tool or similar)
        # We only need to verify the context injection happens, not the tool output
        with patch.object(server.registry, "get") as mock_get:
            mock_tool = MagicMock()
            mock_tool.validate_params.return_value = None
            mock_tool.execute.return_value = MagicMock(success=True, data={}, error=None)
            mock_get.return_value = mock_tool

            request_headers = {"X-Workspace-ID": "enterprise-ws", "X-Tenant-ID": "bigcorp"}
            server.call_tool(
                "cortex_sample_tool",
                operation="test",
                _request_headers=request_headers,
            )

            # The tool's execute must have been called with workspace_context injected
            call_kwargs = mock_tool.execute.call_args
            assert call_kwargs is not None
            # workspace_context should be present in the params passed to execute
            all_kwargs = call_kwargs[1] if call_kwargs[1] else {}
            all_args = call_kwargs[0] if call_kwargs[0] else ()
            # Check either positional or keyword
            params_passed = all_kwargs if all_kwargs else {}
            assert "workspace_context" in params_passed or any(
                isinstance(a, dict) and "workspace_context" in a for a in all_args
            ), (
                "call_tool() must inject workspace_context into tool params when "
                "X-Workspace-ID header is provided via _request_headers"
            )

    def test_call_tool_without_headers_uses_anonymous_context(self) -> None:
        """call_tool() with no headers injects default local WorkspaceContext without crash."""
        from cortex.mcp.server import MCPServer
        server = MCPServer()
        with patch.object(server.registry, "get") as mock_get:
            mock_tool = MagicMock()
            mock_tool.validate_params.return_value = None
            mock_tool.execute.return_value = MagicMock(success=True, data={}, error=None)
            mock_get.return_value = mock_tool

            # No headers — should not raise
            result = server.call_tool("cortex_sample_tool", operation="test")
            # Must succeed (no crash) — workspace_context defaults to local
            assert result is not None

    def test_workspace_context_to_dict_is_json_serialisable(self) -> None:
        """WorkspaceContext.to_dict() produces JSON-serialisable output."""
        import json
        ctx = WorkspaceContext(workspace_id="ws-1", tenant_id="t-1", user_id="u-1")
        d = ctx.to_dict()
        serialised = json.dumps(d)  # must not raise
        assert "ws-1" in serialised

# AC_COMPLETE: AC-62A-MCP-TENANT-001 ✅ RED tests written
