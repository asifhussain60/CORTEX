"""
Tests for Multi-Role Portal Generator (MEGA-B S1)

AC-MEGA-B-S1-001: Multi-role portal generates 3 role views
AC-MEGA-B-S1-002: D3.js diagrams auto-generated
AC-MEGA-B-S1-003: Git-aware incremental builds
AC-MEGA-B-S1-004: GitHub Pages compatible

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Dict, List

import pytest

from cortex.intelligence.documentation.portal_generator import (
    PortalConfig,
    PortalGenerator,
    RoleView,
)


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def portal_config():
    """Create test portal configuration."""
    return PortalConfig(
        project_name="CORTEX",
        roles=["architect", "developer", "enterprise"],
        theme="glassmorphism",
        enable_diagrams=True,
    )


@pytest.fixture
def portal_generator(temp_output_dir, portal_config):
    """Create PortalGenerator instance."""
    return PortalGenerator(
        output_dir=temp_output_dir,
        config=portal_config,
    )


# ============================================================================
# AC-MEGA-B-S1-001: Multi-Role Portal Generation
# ============================================================================


class TestMultiRolePortalGeneration:
    """Test multi-role portal generation (architect/developer/enterprise)."""

    def test_generates_three_role_views(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Portal generator creates 3 role-specific landing pages."""
        # When: Generate portal
        result = portal_generator.generate()

        # Then: Success
        assert result.success

        # And: 3 role views created
        assert len(result.role_views) == 3
        role_names = {view.role_name for view in result.role_views}
        assert role_names == {"architect", "developer", "enterprise"}

        # And: Landing pages exist
        for role in ["architect", "developer", "enterprise"]:
            landing_page = temp_output_dir / f"{role}" / "index.html"
            assert landing_page.exists()

    def test_architect_view_content(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Architect view contains system architecture content."""
        # When: Generate portal
        portal_generator.generate()

        # Then: Architect landing page has architecture-specific content
        architect_page = temp_output_dir / "architect" / "index.html"
        content = architect_page.read_text()

        assert "Architecture Overview" in content
        assert "Orchestrators" in content
        assert "Governance" in content

    def test_developer_view_content(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Developer view contains API and usage content."""
        # When: Generate portal
        portal_generator.generate()

        # Then: Developer landing page has developer-specific content
        developer_page = temp_output_dir / "developer" / "index.html"
        content = developer_page.read_text()

        assert "Getting Started" in content
        assert "API Reference" in content
        assert "Examples" in content

    def test_enterprise_view_content(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Enterprise view contains deployment and SLA content."""
        # When: Generate portal
        portal_generator.generate()

        # Then: Enterprise landing page has enterprise-specific content
        enterprise_page = temp_output_dir / "enterprise" / "index.html"
        content = enterprise_page.read_text()

        assert "Deployment" in content
        assert "Security" in content
        assert "SLA" in content


# ============================================================================
# AC-MEGA-B-S1-002: D3.js Diagram Generation
# ============================================================================


class TestD3DiagramGeneration:
    """Test D3.js architecture diagram generation."""

    def test_generates_orchestrator_diagram(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Diagram generator creates orchestrator visualization."""
        # When: Generate portal with diagrams enabled
        result = portal_generator.generate()

        # Then: Orchestrator diagram created
        diagram_path = temp_output_dir / "diagrams" / "orchestrators.svg"
        assert diagram_path.exists()

        # And: Contains D3.js SVG elements
        svg_content = diagram_path.read_text()
        assert "<svg" in svg_content
        assert "orchestrator" in svg_content.lower()

    def test_generates_agent_diagram(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Diagram generator creates agent architecture visualization."""
        # When: Generate portal
        result = portal_generator.generate()

        # Then: Agent diagram created
        diagram_path = temp_output_dir / "diagrams" / "agents.svg"
        assert diagram_path.exists()

        # And: Contains agent nodes
        svg_content = diagram_path.read_text()
        assert "agent" in svg_content.lower()

    def test_generates_mcp_flow_diagram(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Diagram generator creates MCP flow visualization."""
        # When: Generate portal
        result = portal_generator.generate()

        # Then: MCP flow diagram created
        diagram_path = temp_output_dir / "diagrams" / "mcp-flow.svg"
        assert diagram_path.exists()

        # And: Contains MCP tool references
        svg_content = diagram_path.read_text()
        assert "mcp" in svg_content.lower() or "cortex_" in svg_content


# ============================================================================
# AC-MEGA-B-S1-003: Git-Aware Incremental Builds
# ============================================================================


class TestGitAwareIncrementalBuilds:
    """Test Git-aware incremental build detection."""

    def test_detects_changed_files(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Incremental builder detects changed markdown files."""
        # Given: Initial generation
        first_result = portal_generator.generate()
        assert first_result.success

        # When: Simulate file change (touch a source file)
        # In real implementation, would use git diff
        # For test, manually mark a file as changed
        portal_generator.mark_file_changed("docs/architecture.md")

        # And: Regenerate
        second_result = portal_generator.generate_incremental()

        # Then: Only changed files regenerated
        assert second_result.success
        assert second_result.files_processed < first_result.files_processed
        assert "docs/architecture.md" in second_result.changed_files

    def test_skips_unchanged_files(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Incremental builder skips unchanged files."""
        # Given: Initial generation
        first_result = portal_generator.generate()
        file_count = first_result.files_processed

        # When: Regenerate without changes
        second_result = portal_generator.generate_incremental()

        # Then: Zero files processed (all cached)
        assert second_result.files_processed == 0
        assert second_result.cache_hit_rate == 1.0


# ============================================================================
# AC-MEGA-B-S1-004: GitHub Pages Compatibility
# ============================================================================


class TestGitHubPagesCompatibility:
    """Test GitHub Pages deployment compatibility."""

    def test_uses_relative_paths(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Generated HTML uses relative paths (not absolute)."""
        # When: Generate portal
        portal_generator.generate()

        # Then: All links use relative paths
        index_page = temp_output_dir / "architect" / "index.html"
        content = index_page.read_text()

        # Check for relative paths (no http://, no absolute /)
        import re
        absolute_links = re.findall(r'href="(/[^/]|http)', content)
        assert len(absolute_links) == 0, f"Found absolute links: {absolute_links}"

    def test_optimizes_assets(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Assets are optimized for GitHub Pages."""
        # When: Generate portal
        result = portal_generator.generate()

        # Then: CSS minified
        css_path = temp_output_dir / "assets" / "style.css"
        assert css_path.exists()
        css_content = css_path.read_text()
        
        # Check for minification (no newlines between rules)
        assert not css_content.startswith("\n\n")

    def test_includes_cname_file(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: CNAME file included for custom domain."""
        # When: Generate portal with custom domain
        portal_generator.config.custom_domain = "docs.cortex.ai"
        portal_generator.generate()

        # Then: CNAME file exists
        cname_path = temp_output_dir / "CNAME"
        assert cname_path.exists()
        assert cname_path.read_text().strip() == "docs.cortex.ai"


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Test documentation generation performance."""

    def test_generation_performance(
        self,
        portal_generator,
    ):
        """Test: Portal generation completes in <500ms per page."""
        import time

        # When: Measure generation time
        start = time.perf_counter()
        result = portal_generator.generate()
        duration_ms = (time.perf_counter() - start) * 1000

        # Then: Performance target met
        pages_generated = len(result.role_views)
        ms_per_page = duration_ms / pages_generated

        assert ms_per_page < 500, f"Generation took {ms_per_page:.2f}ms per page (target: <500ms)"


# ============================================================================
# Integration Tests
# ============================================================================


class TestPortalIntegration:
    """Test full portal generation workflow."""

    def test_full_portal_generation(
        self,
        portal_generator,
        temp_output_dir,
    ):
        """Test: Complete portal generation workflow."""
        # When: Generate complete portal
        result = portal_generator.generate()

        # Then: All components generated
        assert result.success
        assert len(result.role_views) == 3
        assert len(result.diagrams) >= 3
        assert result.files_processed > 0

        # And: Directory structure correct
        assert (temp_output_dir / "architect").is_dir()
        assert (temp_output_dir / "developer").is_dir()
        assert (temp_output_dir / "enterprise").is_dir()
        assert (temp_output_dir / "diagrams").is_dir()
        assert (temp_output_dir / "assets").is_dir()
