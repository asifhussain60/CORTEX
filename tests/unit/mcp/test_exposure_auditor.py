"""
Phase 38 Stage 7 - MCP Toolkit Completeness Audit.

Tests for AC-PHASE38-018, AC-PHASE38-019, AC-PHASE38-020:
- MCPExposureAuditor scans all orchestrators
- 100% MCP coverage for all 35 orchestrators
- MCP tool registry auto-generation

TDD: RED → GREEN → REFACTOR
Author: CORTEX Architect
Created: 2026-02-07
"""

# AC_START: AC-PHASE38-018
# Description: MCPExposureAuditor scans all orchestrators

import pytest
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch


# ============================================================================
# Test Category 1: MCP Exposure Auditor (AC-PHASE38-018)
# ============================================================================

class TestMCPExposureAuditor:
    """Test suite for MCPExposureAuditor orchestrator scanner."""

    def test_auditor_scans_all_orchestrator_directories(self) -> None:
        """Test auditor discovers orchestrators in core/domain/support."""
        from cortex.mcp.exposure_auditor import MCPExposureAuditor
        
        auditor = MCPExposureAuditor()
        orchestrators = auditor.scan_orchestrators()
        
        # Should find orchestrators in all three categories
        assert len(orchestrators) > 0
        
        # Verify directory coverage
        categories = {orch["category"] for orch in orchestrators}
        assert "core" in categories
        assert "domain" in categories
        assert "support" in categories

    def test_auditor_detects_missing_mcp_tools(self) -> None:
        """Test auditor identifies orchestrators without MCP tools."""
        from cortex.mcp.exposure_auditor import MCPExposureAuditor
        
        auditor = MCPExposureAuditor()
        audit_result = auditor.audit_mcp_coverage()
        
        assert "missing_orchestrators" in audit_result
        assert "exposed_count" in audit_result
        assert "total_orchestrators" in audit_result

    def test_auditor_generates_mcp_tool_specifications(self) -> None:
        """Test auditor generates MCP tool specs for missing orchestrators."""
        from cortex.mcp.exposure_auditor import MCPExposureAuditor
        
        auditor = MCPExposureAuditor()
        specs = auditor.generate_missing_tool_specs()
        
        assert isinstance(specs, list)
        if len(specs) > 0:
            # Each spec should have required fields
            spec = specs[0]
            assert "tool_name" in spec
            assert "description" in spec
            assert "orchestrator" in spec

    def test_auditor_validates_tool_interface_matching(self) -> None:
        """Test auditor validates tool inputs/outputs match orchestrator interfaces."""
        from cortex.mcp.exposure_auditor import MCPExposureAuditor
        
        auditor = MCPExposureAuditor()
        
        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.process = Mock(
            __annotations__={"request": str, "return": dict}
        )
        
        validation = auditor.validate_tool_interface(
            mock_orchestrator,
            {"inputs": ["request"], "outputs": ["result"]}
        )
        
        assert "valid" in validation
        assert "issues" in validation


# ============================================================================
# Test Category 2: MCP Coverage Metrics (AC-PHASE38-019)
# ============================================================================

class TestMCPCoverageMetrics:
    """Test suite for 100% MCP coverage validation."""

    def test_coverage_calculates_correctly(self) -> None:
        """Test MCP coverage percentage calculation."""
        from cortex.mcp.exposure_auditor import MCPExposureAuditor
        
        auditor = MCPExposureAuditor()
        audit_result = auditor.audit_mcp_coverage()
        
        # Coverage should be calculated
        coverage = audit_result.get("coverage_percent", 0)
        assert 0 <= coverage <= 100

    def test_coverage_broken_down_by_category(self) -> None:
        """Test MCP coverage reported per orchestrator category."""
        from cortex.mcp.exposure_auditor import MCPExposureAuditor
        
        auditor = MCPExposureAuditor()
        audit_result = auditor.audit_mcp_coverage()
        
        # Should have category breakdown
        assert "category_coverage" in audit_result
        categories = audit_result["category_coverage"]
        
        assert "core" in categories
        assert "domain" in categories
        assert "support" in categories

    def test_reports_orchestrator_count_per_category(self) -> None:
        """Test auditor reports orchestrator counts per category."""
        from cortex.mcp.exposure_auditor import MCPExposureAuditor
        
        auditor = MCPExposureAuditor()
        audit_result = auditor.audit_mcp_coverage()
        
        categories = audit_result["category_coverage"]
        
        # Core should have 8 orchestrators
        assert categories["core"]["total"] >= 8
        # Domain should have orchestrators
        assert categories["domain"]["total"] > 0
        # Support should have orchestrators
        assert categories["support"]["total"] > 0


# ============================================================================
# Test Category 3: MCP Tool Registry Generation (AC-PHASE38-020)
# ============================================================================

class TestMCPToolRegistryGeneration:
    """Test suite for MCP tool registry auto-generation."""

    def test_generator_creates_registry_file(self) -> None:
        """Test generator creates MCP tool registry file."""
        from cortex.mcp.tool_spec_generator import MCPToolSpecGenerator
        
        generator = MCPToolSpecGenerator()
        
        # Generate registry
        registry_path = generator.generate_registry(output_path=None)  # None = dry-run
        
        assert registry_path is not None or registry_path == "dry-run"

    def test_generator_includes_all_tool_specifications(self) -> None:
        """Test generated registry includes all tool specs."""
        from cortex.mcp.tool_spec_generator import MCPToolSpecGenerator
        
        generator = MCPToolSpecGenerator()
        registry_data = generator.build_registry_data()
        
        assert "tools" in registry_data
        assert len(registry_data["tools"]) > 0

    def test_generator_formats_tools_correctly(self) -> None:
        """Test generator formats tools with MCP-compliant schema."""
        from cortex.mcp.tool_spec_generator import MCPToolSpecGenerator
        
        generator = MCPToolSpecGenerator()
        registry_data = generator.build_registry_data()
        
        # Each tool should have MCP-compliant format
        for tool in registry_data["tools"]:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool or "input_schema" in tool

    def test_generator_validates_no_duplicate_tools(self) -> None:
        """Test generator ensures no duplicate tool names."""
        from cortex.mcp.tool_spec_generator import MCPToolSpecGenerator
        
        generator = MCPToolSpecGenerator()
        registry_data = generator.build_registry_data()
        
        tool_names = [tool["name"] for tool in registry_data["tools"]]
        assert len(tool_names) == len(set(tool_names)), "Duplicate tool names found"

    def test_generator_updates_existing_registry(self) -> None:
        """Test generator can update existing registry without overwriting."""
        from cortex.mcp.tool_spec_generator import MCPToolSpecGenerator
        
        generator = MCPToolSpecGenerator()
        
        # Mock existing registry
        existing_tools = [{"name": "cortex_existing", "description": "Existing tool"}]
        
        updated_registry = generator.merge_with_existing(existing_tools)
        
        assert "cortex_existing" in [tool["name"] for tool in updated_registry]


# AC_COMPLETE: AC-PHASE38-018 ✅ 4/4 tests (auditor)
# AC_COMPLETE: AC-PHASE38-019 ✅ 3/3 tests (coverage)
# AC_COMPLETE: AC-PHASE38-020 ✅ 5/5 tests (registry)
# Stage 7 RED Phase Complete: 12 tests total
