"""Preflight: MCP server + tool registry wiring tests.

Validates the MCP server module is importable and tools are registered.
Each test is < 50ms — pure import + attribute check, no server startup.

Tier: T0 (preflight) — runs in < 10s parallel.
"""
import pytest


class TestMCPServerImport:
    """Validate MCP server module imports."""

    def test_mcp_module_importable(self) -> None:
        """MCP module root is importable."""
        import cortex.mcp
        assert cortex.mcp is not None

    def test_mcp_tools_init_importable(self) -> None:
        """MCP tools __init__ is importable."""
        import cortex.mcp.tools
        assert cortex.mcp.tools is not None

    def test_mcp_registry_importable(self) -> None:
        """MCP registry module is importable."""
        from cortex.mcp import mcp_registry
        assert mcp_registry is not None


class TestMCPToolFiles:
    """Validate individual MCP tool files are importable."""

    def test_onboard_repository_tool(self) -> None:
        """Onboard repository tool file."""
        from cortex.mcp.tools import onboard_repository
        assert onboard_repository is not None

    def test_bulk_digest_tool(self) -> None:
        """Bulk digest tool file."""
        from cortex.mcp.tools import bulk_digest
        assert bulk_digest is not None

    def test_git_orchestrator_tool(self) -> None:
        """Git orchestrator tool file."""
        from cortex.mcp.tools import git_orchestrator_tool
        assert git_orchestrator_tool is not None

    def test_workflow_tools(self) -> None:
        """Workflow tools file."""
        from cortex.mcp.tools import workflow_tools
        assert workflow_tools is not None

    def test_coherence_tools(self) -> None:
        """Coherence tools file."""
        from cortex.mcp.tools import coherence_tools
        assert coherence_tools is not None

    def test_debug_tools(self) -> None:
        """Debug tools file."""
        from cortex.mcp.tools import debug_tools
        assert debug_tools is not None
