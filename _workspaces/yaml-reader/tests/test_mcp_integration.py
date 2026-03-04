"""
Phase 123 — Registry Intelligence Engine
YAML Reader MCP Integration Tests (S5 — GAP-123-05)

Validates that the MCP_MODE flag and fetchFromMCP / loadFromMCP
wiring in app.js are present and structurally correct.

These are static-analysis / smoke tests only — no browser required.
CORE Rules: CORE-008 (TDD-first), CORE-011, CORE-012
AC_START: AC-123-YAML-READER-INTEGRATION
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

APP_JS = Path(__file__).parents[3] / "_workspaces" / "yaml-reader" / "app.js"


@pytest.fixture(scope="module")
def app_js_source() -> str:
    """Return the full source of app.js."""
    assert APP_JS.exists(), f"app.js not found at {APP_JS}"
    return APP_JS.read_text(encoding="utf-8")


class TestMCPModeFlagPresence:
    """MCP_MODE constant must be declared in app.js."""

    def test_mcp_mode_constant_declared(self, app_js_source: str) -> None:
        """app.js must declare MCP_MODE as a const."""
        assert "const MCP_MODE" in app_js_source, (
            "MCP_MODE constant not found in app.js — Phase 123 S5 wiring missing."
        )

    def test_mcp_mode_defaults_to_false(self, app_js_source: str) -> None:
        """MCP_MODE must default to false to preserve file:// workflow."""
        # Accept 'false' or 'False' — JS is case-sensitive so must be lowercase
        pattern = r"const\s+MCP_MODE\s*=\s*false"
        assert re.search(pattern, app_js_source), (
            "MCP_MODE must default to false (preserves file:// standalone workflow)."
        )


class TestFetchFromMCPFunction:
    """fetchFromMCP() async function must be present and well-formed."""

    def test_fetch_from_mcp_declared(self, app_js_source: str) -> None:
        """app.js must declare fetchFromMCP as an async function."""
        assert "async function fetchFromMCP" in app_js_source, (
            "fetchFromMCP async function not found in app.js."
        )

    def test_fetch_from_mcp_accepts_op_param(self, app_js_source: str) -> None:
        """fetchFromMCP must accept an 'op' parameter."""
        pattern = r"async function fetchFromMCP\s*\(\s*op"
        assert re.search(pattern, app_js_source), (
            "fetchFromMCP must accept 'op' as its first parameter."
        )

    def test_fetch_from_mcp_references_cortex_registry(self, app_js_source: str) -> None:
        """fetchFromMCP must reference 'cortex_registry' tool name."""
        assert "cortex_registry" in app_js_source, (
            "fetchFromMCP must reference 'cortex_registry' tool name."
        )

    def test_fetch_from_mcp_handles_vs_code_bridge(self, app_js_source: str) -> None:
        """fetchFromMCP must check for acquireVsCodeApi (VS Code webview bridge)."""
        assert "acquireVsCodeApi" in app_js_source, (
            "fetchFromMCP must handle VS Code webview bridge via acquireVsCodeApi."
        )

    def test_fetch_from_mcp_has_http_fallback(self, app_js_source: str) -> None:
        """fetchFromMCP must include an HTTP fallback (fetch() call)."""
        assert "fetch(" in app_js_source, (
            "fetchFromMCP must include an HTTP fetch() fallback for non-VS Code contexts."
        )


class TestLoadFromMCPFunction:
    """loadFromMCP() function must be present and wire all 5 ops."""

    def test_load_from_mcp_declared(self, app_js_source: str) -> None:
        """app.js must declare loadFromMCP as an async function."""
        assert "async function loadFromMCP" in app_js_source, (
            "loadFromMCP async function not found in app.js."
        )

    def test_load_from_mcp_calls_all_five_ops(self, app_js_source: str) -> None:
        """loadFromMCP must call all 5 registry ops."""
        required_ops = [
            "query_governance",
            "query_workflows",
            "query_patterns",
            "query_plans",
            "registry_index",
        ]
        for op in required_ops:
            assert op in app_js_source, (
                f"loadFromMCP must call fetchFromMCP('{op}') — op missing from app.js."
            )

    def test_load_from_mcp_uses_promise_all(self, app_js_source: str) -> None:
        """loadFromMCP should use Promise.all for concurrent fetching."""
        assert "Promise.all" in app_js_source, (
            "loadFromMCP should use Promise.all for concurrent MCP calls."
        )


class TestInitMCPModeBranch:
    """init() must call loadFromMCP() when MCP_MODE is true."""

    def test_init_checks_mcp_mode(self, app_js_source: str) -> None:
        """init() must have an if(MCP_MODE) branch."""
        assert "if (MCP_MODE)" in app_js_source or "if(MCP_MODE)" in app_js_source, (
            "init() must check MCP_MODE and call loadFromMCP() when true."
        )

    def test_init_calls_load_from_mcp(self, app_js_source: str) -> None:
        """init() must call loadFromMCP() inside the MCP_MODE branch."""
        assert "loadFromMCP()" in app_js_source, (
            "init() must call loadFromMCP() when MCP_MODE is enabled."
        )
