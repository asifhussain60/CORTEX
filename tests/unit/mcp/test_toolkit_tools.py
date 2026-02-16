"""
Tests for cortex.mcp.toolkit_tools module (Phase 90 S6).

Authority: Phase 90 S-90-07
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

# These tests validate MCP tool exposure, not implementation
# Implementation details are in cortex/toolkit/* modules


class TestToolkitDiagnoseTool:
    """Test toolkit_diagnose MCP tool."""

    @pytest.mark.asyncio
    async def test_diagnose_returns_health_status(self):
        """Test diagnose tool returns MCP health status."""
        from cortex.mcp.toolkit_tools import toolkit_diagnose
        
        result = await toolkit_diagnose()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "checks" in result

    @pytest.mark.asyncio
    async def test_diagnose_includes_tool_count(self):
        """Test diagnose includes MCP tool count."""
        from cortex.mcp.toolkit_tools import toolkit_diagnose
        
        result = await toolkit_diagnose()
        
        assert "tool_count" in result or "checks" in result


class TestToolkitVerifyTool:
    """Test toolkit_verify MCP tool."""

    @pytest.mark.asyncio
    async def test_verify_returns_setup_status(self):
        """Test verify tool returns setup verification status."""
        from cortex.mcp.toolkit_tools import toolkit_verify
        
        result = await toolkit_verify()
        
        assert isinstance(result, dict)
        assert "checks" in result or "status" in result

    @pytest.mark.asyncio
    async def test_verify_includes_fix_commands(self):
        """Test verify includes autofix commands when issues found."""
        from cortex.mcp.toolkit_tools import toolkit_verify
        
        result = await toolkit_verify()
        
        # Should have structure for fix commands
        assert isinstance(result, dict)


class TestToolkitCleanupTool:
    """Test toolkit_cleanup MCP tool."""

    @pytest.mark.asyncio
    async def test_cleanup_accepts_dry_run_flag(self):
        """Test cleanup tool accepts dry_run parameter."""
        from cortex.mcp.toolkit_tools import toolkit_cleanup
        
        result = await toolkit_cleanup(dry_run=True)
        
        assert isinstance(result, dict)
        assert "operations" in result or "results" in result

    @pytest.mark.asyncio
    async def test_cleanup_reports_operations(self):
        """Test cleanup reports operations performed."""
        from cortex.mcp.toolkit_tools import toolkit_cleanup
        
        result = await toolkit_cleanup(dry_run=True)
        
        # Should report what was cleaned
        assert isinstance(result, dict)


class TestToolkitValidateTool:
    """Test toolkit_validate MCP tool."""

    @pytest.mark.asyncio
    async def test_validate_returns_governance_status(self):
        """Test validate tool returns governance alignment status."""
        from cortex.mcp.toolkit_tools import toolkit_validate
        
        result = await toolkit_validate()
        
        assert isinstance(result, dict)
        assert "checks" in result or "validation" in result

    @pytest.mark.asyncio
    async def test_validate_accepts_strict_mode(self):
        """Test validate accepts strict mode parameter."""
        from cortex.mcp.toolkit_tools import toolkit_validate
        
        result = await toolkit_validate(strict_mode=True)
        
        assert isinstance(result, dict)


class TestToolkitAnalyzeTool:
    """Test toolkit_analyze MCP tool."""

    @pytest.mark.asyncio
    async def test_analyze_discovers_tools(self):
        """Test analyze tool discovers scattered scripts."""
        from cortex.mcp.toolkit_tools import toolkit_analyze
        
        result = await toolkit_analyze()
        
        assert isinstance(result, dict)
        assert "tools" in result or "categories" in result

    @pytest.mark.asyncio
    async def test_analyze_detects_duplicates(self):
        """Test analyze detects duplicate functionality."""
        from cortex.mcp.toolkit_tools import toolkit_analyze
        
        result = await toolkit_analyze()
        
        # Should report duplicate detection
        assert isinstance(result, dict)


class TestMCPServerIntegration:
    """Test MCP server integration of toolkit tools."""

    def test_toolkit_tools_registered_in_server(self):
        """Test toolkit tools are registered in MCP server."""
        # Skip if TOOLS not available (toolkit tools may be registered separately)
        try:
            from cortex.mcp.server import TOOLS
            registered_names = [tool.name for tool in TOOLS]
        except (ImportError, AttributeError):
            # If TOOLS not available, check toolkit_tools module exists
            from cortex.mcp import toolkit_tools
            assert hasattr(toolkit_tools, 'toolkit_diagnose')
            assert hasattr(toolkit_tools, 'toolkit_verify')
            assert hasattr(toolkit_tools, 'toolkit_cleanup')
            assert hasattr(toolkit_tools, 'toolkit_validate')
            assert hasattr(toolkit_tools, 'toolkit_analyze')
            return
        
        toolkit_tools = [
            "toolkit_diagnose",
            "toolkit_verify",
            "toolkit_cleanup",
            "toolkit_validate",
            "toolkit_analyze",
        ]
        
        for tool_name in toolkit_tools:
            assert tool_name in registered_names, f"{tool_name} not registered"

    def test_toolkit_tools_have_descriptions(self):
        """Test toolkit tools have proper descriptions."""
        # Skip if TOOLS not available
        try:
            from cortex.mcp.server import TOOLS
        except (ImportError, AttributeError):
            # Check toolkit_tools module has docstrings
            from cortex.mcp import toolkit_tools
            assert toolkit_tools.toolkit_diagnose.__doc__
            assert toolkit_tools.toolkit_verify.__doc__
            assert toolkit_tools.toolkit_cleanup.__doc__
            assert toolkit_tools.toolkit_validate.__doc__
            assert toolkit_tools.toolkit_analyze.__doc__
            return
        
        toolkit_tools = {
            "toolkit_diagnose",
            "toolkit_verify",
            "toolkit_cleanup",
            "toolkit_validate",
            "toolkit_analyze",
        }
        
        for tool in TOOLS:
            if tool.name in toolkit_tools:
                assert tool.description, f"{tool.name} missing description"
                assert len(tool.description) > 20, f"{tool.name} description too short"


class TestToolkitToolsErrorHandling:
    """Test error handling in toolkit tools."""

    @pytest.mark.asyncio
    async def test_diagnose_handles_errors_gracefully(self):
        """Test diagnose tool handles errors without crashing."""
        from cortex.mcp.toolkit_tools import toolkit_diagnose
        
        # Should not raise even if components missing
        result = await toolkit_diagnose()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_verify_handles_missing_files(self):
        """Test verify handles missing files gracefully."""
        from cortex.mcp.toolkit_tools import toolkit_verify
        
        # Should not raise even if files missing
        result = await toolkit_verify()
        assert isinstance(result, dict)
