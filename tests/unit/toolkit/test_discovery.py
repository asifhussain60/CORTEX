"""
Unit tests for toolkit discovery and categorization.

Tests the discovery process that scans scattered Python utilities
and categorizes them by function.

AC_START: AC-P90-S1-T1
"""

import pytest
from pathlib import Path
from typing import Dict, List
from cortex.toolkit.discovery import (
    ToolkitDiscovery,
    ToolCategory,
    ToolMetadata,
)


class TestToolkitDiscovery:
    """Test toolkit discovery scanning."""

    def test_discover_cortex_directory(self) -> None:
        """Test discovery scans .cortex-runtime/ directory."""
        discovery = ToolkitDiscovery()
        tools = discovery.discover_tools(Path(".cortex"))
        
        assert len(tools) >= 10, "Should find at least 10 tools in .cortex-runtime/"
        assert all(isinstance(t, ToolMetadata) for t in tools)

    def test_discover_scripts_directory(self) -> None:
        """Test discovery scans scripts/ directory."""
        discovery = ToolkitDiscovery()
        tools = discovery.discover_tools(Path("scripts"))
        
        assert len(tools) >= 15, "Should find at least 15 tools in scripts/"
        assert all(isinstance(t, ToolMetadata) for t in tools)

    def test_tool_metadata_extraction(self) -> None:
        """Test tool metadata is correctly extracted."""
        discovery = ToolkitDiscovery()
        tool = ToolMetadata(
            name="verify-mcp-setup",
            path=Path(".cortex-runtime/verify-mcp-setup.py"),
            category=ToolCategory.DIAGNOSTICS,
            description="Verify MCP server setup",
        )
        
        assert tool.name == "verify-mcp-setup"
        assert tool.category == ToolCategory.DIAGNOSTICS
        assert tool.path.name == "verify-mcp-setup.py"


class TestToolCategorization:
    """Test tool categorization logic."""

    def test_categorize_mcp_diagnostics(self) -> None:
        """Test MCP diagnostic tools are categorized correctly."""
        discovery = ToolkitDiscovery()
        
        # Test patterns that should match DIAGNOSTICS
        assert discovery.categorize_tool("verify-mcp-setup.py") == ToolCategory.DIAGNOSTICS
        assert discovery.categorize_tool("diagnose-mcp.py") == ToolCategory.DIAGNOSTICS
        assert discovery.categorize_tool("verify-mcp-tools.py") == ToolCategory.DIAGNOSTICS

    def test_categorize_setup_tools(self) -> None:
        """Test setup tools are categorized correctly."""
        discovery = ToolkitDiscovery()
        
        assert discovery.categorize_tool("setup-mcp.py") == ToolCategory.SETUP
        assert discovery.categorize_tool("verify-setup.py") == ToolCategory.SETUP
        assert discovery.categorize_tool("verify-autonomous-setup.py") == ToolCategory.SETUP

    def test_categorize_cleanup_tools(self) -> None:
        """Test cleanup tools are categorized correctly."""
        discovery = ToolkitDiscovery()
        
        assert discovery.categorize_tool("run_vacuum.py") == ToolCategory.CLEANUP
        assert discovery.categorize_tool("vacuum-runner.py") == ToolCategory.CLEANUP
        assert discovery.categorize_tool("phase-80-root-cleanup.py") == ToolCategory.CLEANUP

    def test_categorize_validation_tools(self) -> None:
        """Test validation tools are categorized correctly."""
        discovery = ToolkitDiscovery()
        
        assert discovery.categorize_tool("validate-production.py") == ToolCategory.VALIDATION
        assert discovery.categorize_tool("validate_governance_alignment.py") == ToolCategory.VALIDATION
        assert discovery.categorize_tool("execute_validation_suite.py") == ToolCategory.VALIDATION

    def test_categorize_automation_tools(self) -> None:
        """Test automation tools are categorized correctly."""
        discovery = ToolkitDiscovery()
        
        assert discovery.categorize_tool("batch_generate_tests.py") == ToolCategory.AUTOMATION
        assert discovery.categorize_tool("autonomous_phases_4_7.py") == ToolCategory.AUTOMATION
        assert discovery.categorize_tool("generate_batch_specs.py") == ToolCategory.AUTOMATION


class TestDuplicateDetection:
    """Test duplicate functionality detection."""

    def test_identify_mcp_verification_duplicates(self) -> None:
        """Test detection of overlapping MCP verification tools."""
        discovery = ToolkitDiscovery()
        tools = [
            ToolMetadata(
                name="verify-mcp-setup",
                path=Path(".cortex-runtime/verify-mcp-setup.py"),
                category=ToolCategory.DIAGNOSTICS,
                description="Verify MCP setup",
            ),
            ToolMetadata(
                name="verify-mcp-tools",
                path=Path(".cortex-runtime/verify-mcp-tools.py"),
                category=ToolCategory.DIAGNOSTICS,
                description="Verify MCP tools",
            ),
            ToolMetadata(
                name="diagnose-mcp",
                path=Path(".cortex-runtime/diagnose-mcp.py"),
                category=ToolCategory.DIAGNOSTICS,
                description="Diagnose MCP issues",
            ),
        ]
        
        duplicates = discovery.find_duplicates(tools)
        
        assert len(duplicates) >= 1
        assert any("mcp" in d.lower() for d in duplicates)

    def test_identify_vacuum_duplicates(self) -> None:
        """Test detection of vacuum cleanup duplicates."""
        discovery = ToolkitDiscovery()
        tools = [
            ToolMetadata(
                name="run_vacuum",
                path=Path(".cortex-runtime/run_vacuum.py"),
                category=ToolCategory.CLEANUP,
                description="Run vacuum cleanup",
            ),
            ToolMetadata(
                name="vacuum-runner",
                path=Path("scripts/vacuum-runner.py"),
                category=ToolCategory.CLEANUP,
                description="Vacuum runner",
            ),
        ]
        
        duplicates = discovery.find_duplicates(tools)
        
        assert len(duplicates) >= 1
        assert any("vacuum" in d.lower() for d in duplicates)


class TestCategorizationMatrix:
    """Test categorization matrix generation."""

    def test_generate_matrix(self) -> None:
        """Test categorization matrix generation."""
        discovery = ToolkitDiscovery()
        all_tools = discovery.discover_all()
        matrix = discovery.generate_matrix(all_tools)
        
        assert len(matrix) == 5  # 5 categories
        assert ToolCategory.DIAGNOSTICS in matrix
        assert ToolCategory.SETUP in matrix
        assert ToolCategory.CLEANUP in matrix
        assert ToolCategory.VALIDATION in matrix
        assert ToolCategory.AUTOMATION in matrix

    def test_matrix_tool_counts(self) -> None:
        """Test matrix contains expected tool counts."""
        discovery = ToolkitDiscovery()
        all_tools = discovery.discover_all()
        matrix = discovery.generate_matrix(all_tools)
        
        total_tools = sum(len(tools) for tools in matrix.values())
        assert total_tools >= 20, "Should find at least 20 tools total"


# AC_COMPLETE: AC-P90-S1-T1
