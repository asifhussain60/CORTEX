"""
Diagram Generator Tests — MEGA-B S1

AC-MEGA-B-S1-002: D3.js diagram generation

Tests for D3.js SVG diagram generation:
- Orchestrator architecture diagrams
- Agent relationship diagrams
- MCP flow diagrams
- Interactive navigation
- SVG optimization

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD)
"""

from pathlib import Path
from typing import List

import pytest

from cortex.documentation.diagram_generator import (
    DiagramConfig,
    DiagramGenerator,
    DiagramType,
)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary output directory."""
    output_dir = tmp_path / "diagrams"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def diagram_config():
    """Standard diagram configuration."""
    return DiagramConfig(
        width=800,
        height=600,
        style="glassmorphism",
    )


@pytest.fixture
def diagram_generator(temp_output_dir, diagram_config):
    """Diagram generator instance."""
    return DiagramGenerator(
        output_dir=temp_output_dir,
        config=diagram_config,
    )


class TestOrchestratorDiagrams:
    """Test: Orchestrator architecture diagram generation."""
    
    def test_generates_orchestrator_diagram(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Generates orchestrator architecture diagram."""
        # When: Generate orchestrator diagram
        diagram_path = diagram_generator.generate_diagram(DiagramType.ORCHESTRATOR)
        
        # Then: Diagram created
        assert diagram_path.exists()
        assert diagram_path.name == "orchestrators.svg"
        
        # And: Contains expected elements
        content = diagram_path.read_text()
        assert "<svg" in content
        assert "orchestrator" in content.lower()
    
    def test_orchestrator_diagram_includes_hierarchy(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Orchestrator diagram shows hierarchy."""
        # When: Generate diagram with hierarchy data
        hierarchy = {
            "MasterOrchestrator": ["TDDOrchestrator", "LENSSynthesis"],
            "TDDOrchestrator": ["IncrementalTaskDecomposer"],
        }
        
        diagram_path = diagram_generator.generate_orchestrator_diagram(
            orchestrators=hierarchy,
        )
        
        # Then: Hierarchy rendered
        content = diagram_path.read_text()
        assert "MasterOrchestrator" in content
        assert "TDDOrchestrator" in content


class TestAgentDiagrams:
    """Test: Agent relationship diagram generation."""
    
    def test_generates_agent_diagram(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Generates agent relationship diagram."""
        # When: Generate agent diagram
        diagram_path = diagram_generator.generate_diagram(DiagramType.AGENT)
        
        # Then: Diagram created
        assert diagram_path.exists()
        assert diagram_path.name == "agents.svg"
        
        # And: Contains agent elements
        content = diagram_path.read_text()
        assert "agent" in content.lower()
    
    def test_agent_diagram_shows_enforcement_layer(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Agent diagram shows 7-agent enforcement layer."""
        # When: Generate with enforcement agents
        agents = [
            "GovernanceEnforcementAgent",
            "SecurityCheckpointAgent",
            "ComplianceValidationAgent",
        ]
        
        diagram_path = diagram_generator.generate_agent_diagram(
            agents=agents,
        )
        
        # Then: All agents rendered
        content = diagram_path.read_text()
        for agent in agents:
            assert agent in content


class TestMCPFlowDiagrams:
    """Test: MCP flow diagram generation."""
    
    def test_generates_mcp_flow_diagram(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Generates MCP flow diagram."""
        # When: Generate MCP flow
        diagram_path = diagram_generator.generate_diagram(DiagramType.MCP_FLOW)
        
        # Then: Diagram created
        assert diagram_path.exists()
        assert diagram_path.name == "mcp-flow.svg"
        
        # And: Shows MCP components
        content = diagram_path.read_text()
        assert "cortex" in content.lower()
    
    def test_mcp_flow_includes_tool_invocations(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: MCP flow shows tool invocations."""
        # When: Generate with tool flow
        tools = [
            "cortex_process_request",
            "cortex_lens_analyze",
            "cortex_challenge",
        ]
        
        diagram_path = diagram_generator.generate_mcp_flow_diagram(
            tools=tools,
        )
        
        # Then: Tools in flow
        content = diagram_path.read_text()
        for tool in tools:
            assert tool in content


class TestInteractiveDiagrams:
    """Test: Interactive diagram features."""
    
    def test_diagrams_include_navigation_links(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Diagrams include clickable navigation."""
        # When: Generate with links enabled
        diagram_path = diagram_generator.generate_diagram(
            DiagramType.ORCHESTRATOR,
            enable_links=True,
        )
        
        # Then: SVG has anchor tags
        content = diagram_path.read_text()
        assert "<a" in content or "xlink:href" in content
    
    def test_diagrams_support_zoom(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Diagrams support zoom/pan."""
        # When: Generate with zoom enabled
        diagram_path = diagram_generator.generate_diagram(
            DiagramType.AGENT,
            enable_zoom=True,
        )
        
        # Then: Zoom script included
        content = diagram_path.read_text()
        assert "viewBox" in content


class TestDiagramOptimization:
    """Test: Diagram SVG optimization."""
    
    def test_optimizes_svg_output(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Generated SVGs are optimized."""
        # When: Generate diagram
        diagram_path = diagram_generator.generate_diagram(DiagramType.ORCHESTRATOR)
        
        # Then: File size reasonable
        file_size = diagram_path.stat().st_size
        assert file_size < 50000  # <50KB
        
        # And: No unnecessary whitespace
        content = diagram_path.read_text()
        assert "  \n" not in content  # No double spaces before newline
    
    def test_diagrams_use_relative_paths(
        self,
        diagram_generator,
        temp_output_dir,
    ):
        """Test: Diagrams use relative paths (GitHub Pages compatible)."""
        # When: Generate with external resources
        diagram_path = diagram_generator.generate_diagram(
            DiagramType.MCP_FLOW,
            include_assets=True,
        )
        
        # Then: Relative paths only (excluding SVG namespace)
        content = diagram_path.read_text()
        
        # Check for absolute URLs in href/src attributes (not xmlns)
        import re
        href_pattern = r'(href|src)="(https?://[^"]+)"'
        absolute_urls = re.findall(href_pattern, content)
        assert len(absolute_urls) == 0, f"Found absolute URLs: {absolute_urls}"
        
        # Verify relative paths present
        assert "../assets/" in content or "./assets/" in content
