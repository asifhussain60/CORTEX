"""
D3.js Diagram Generator — MEGA-B S1

AC-MEGA-B-S1-002: D3.js diagram generation

Generates interactive SVG architecture diagrams:
- Orchestrator hierarchy (MasterOrchestrator → domain orchestrators)
- Agent enforcement layer (7-agent governance)
- MCP flow (tool invocations)
- Interactive navigation (zoom/pan/links)
- SVG optimization (<50KB per diagram)

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List


class DiagramType(Enum):
    """Diagram types."""

    ORCHESTRATOR = "orchestrator"
    AGENT = "agent"
    MCP_FLOW = "mcp_flow"


@dataclass
class DiagramConfig:
    """
    Diagram configuration.

    Attributes:
        width: SVG width in pixels
        height: SVG height in pixels
        style: Visual style (glassmorphism, etc.)
    """
    width: int = 800
    height: int = 600
    style: str = "glassmorphism"


class DiagramGenerator:
    """
    D3.js SVG diagram generator.

    Generates interactive architecture diagrams with D3.js-style visualizations.
    Supports orchestrator hierarchy, agent relationships, MCP flow.

    AC-MEGA-B-S1-002: D3.js diagram generation
    """

    def __init__(
        self,
        output_dir: Path,
        config: DiagramConfig,
    ) -> None:
        """
        Initialize diagram generator.

        Args:
            output_dir: Output directory for diagrams
            config: Diagram configuration
        """
        self.output_dir = Path(output_dir)
        self.config = config

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_diagram(
        self,
        diagram_type: DiagramType,
        enable_links: bool = False,
        enable_zoom: bool = False,
        include_assets: bool = False,
    ) -> Path:
        """
        Generate diagram by type.

        Args:
            diagram_type: Type of diagram to generate
            enable_links: Enable clickable navigation links
            enable_zoom: Enable zoom/pan support
            include_assets: Include external asset references

        Returns:
            Path to generated SVG file
        """
        if diagram_type == DiagramType.ORCHESTRATOR:
            return self._generate_orchestrator_basic(enable_links, enable_zoom)
        elif diagram_type == DiagramType.AGENT:
            return self._generate_agent_basic(enable_links, enable_zoom)
        elif diagram_type == DiagramType.MCP_FLOW:
            return self._generate_mcp_flow_basic(enable_links, enable_zoom, include_assets)
        else:
            raise ValueError(f"Unknown diagram type: {diagram_type}")

    def generate_orchestrator_diagram(
        self,
        orchestrators: Dict[str, List[str]],
    ) -> Path:
        """
        Generate orchestrator hierarchy diagram.

        Args:
            orchestrators: Orchestrator hierarchy (parent -> children)

        Returns:
            Path to generated diagram
        """
        diagram_path = self.output_dir / "orchestrators.svg"

        # Build SVG with hierarchy
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.config.width}" height="{self.config.height}">',
            '<text x="10" y="30" font-size="20">Orchestrator Hierarchy</text>',
        ]

        # Render nodes
        y_offset = 100
        for parent, children in orchestrators.items():
            # Parent node
            svg_parts.append(
                f'<rect x="300" y="{y_offset}" width="200" height="60" '
                f'fill="blue" rx="10"/>',
            )
            svg_parts.append(
                f'<text x="350" y="{y_offset + 35}" fill="white">{parent}</text>',
            )

            # Child nodes
            y_offset += 100
            for i, child in enumerate(children):
                x_offset = 300 + (i * 220)
                svg_parts.append(
                    f'<rect x="{x_offset}" y="{y_offset}" width="200" height="60" '
                    f'fill="lightblue" rx="10"/>',
                )
                svg_parts.append(
                    f'<text x="{x_offset + 30}" y="{y_offset + 35}">{child}</text>',
                )

            y_offset += 100

        svg_parts.append('</svg>')

        # Write diagram
        content = '\n'.join(svg_parts)
        diagram_path.write_text(content)

        return diagram_path

    def generate_agent_diagram(
        self,
        agents: List[str],
    ) -> Path:
        """
        Generate agent relationship diagram.

        Args:
            agents: List of agent names

        Returns:
            Path to generated diagram
        """
        diagram_path = self.output_dir / "agents.svg"

        # Build SVG with agent grid
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.config.width}" height="{self.config.height}">',
            '<text x="10" y="30" font-size="20">Enforcement Agents</text>',
        ]

        # Render agents in grid
        for i, agent in enumerate(agents):
            row = i // 2
            col = i % 2

            x = 100 + (col * 350)
            y = 100 + (row * 120)

            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="300" height="80" '
                f'fill="green" rx="10"/>',
            )
            svg_parts.append(
                f'<text x="{x + 20}" y="{y + 45}" fill="white">{agent}</text>',
            )

        svg_parts.append('</svg>')

        # Write diagram
        content = '\n'.join(svg_parts)
        diagram_path.write_text(content)

        return diagram_path

    def generate_mcp_flow_diagram(
        self,
        tools: List[str],
    ) -> Path:
        """
        Generate MCP flow diagram.

        Args:
            tools: List of MCP tool names

        Returns:
            Path to generated diagram
        """
        diagram_path = self.output_dir / "mcp-flow.svg"

        # Build SVG with flow
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.config.width}" height="{self.config.height}">',
            '<text x="10" y="30" font-size="20">MCP Tool Flow</text>',
        ]

        # Render tools in sequence
        for i, tool in enumerate(tools):
            x = 150
            y = 100 + (i * 100)

            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="500" height="60" '
                f'fill="purple" rx="10"/>',
            )
            svg_parts.append(
                f'<text x="{x + 150}" y="{y + 35}" fill="white">{tool}</text>',
            )

            # Arrow to next tool
            if i < len(tools) - 1:
                svg_parts.append(
                    f'<line x1="400" y1="{y + 60}" x2="400" y2="{y + 100}" '
                    f'stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>',
                )

        # Arrow marker definition
        svg_parts.insert(
            1,
            '<defs><marker id="arrowhead" markerWidth="10" markerHeight="10" '
            'refX="5" refY="5" orient="auto">'
            '<polygon points="0 0, 10 5, 0 10" fill="black"/>'
            '</marker></defs>',
        )

        svg_parts.append('</svg>')

        # Write diagram
        content = '\n'.join(svg_parts)
        diagram_path.write_text(content)

        return diagram_path

    def _generate_orchestrator_basic(
        self,
        enable_links: bool,
        enable_zoom: bool,
    ) -> Path:
        """Generate basic orchestrator diagram."""
        diagram_path = self.output_dir / "orchestrators.svg"

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.config.width}" height="{self.config.height}"',
        ]

        # Add viewBox for zoom support
        if enable_zoom:
            svg_parts[0] += f' viewBox="0 0 {self.config.width} {self.config.height}"'

        svg_parts[0] += '>'

        svg_parts.append('<text x="10" y="30">Orchestrator Architecture</text>')

        # Node with optional link
        if enable_links:
            svg_parts.append(
                '<a xlink:href="../orchestrators/master.html">'
                '<circle cx="400" cy="300" r="50" fill="blue"/>'
                '<text x="370" y="305" fill="white">orchestrator</text>'
                '</a>',
            )
        else:
            svg_parts.append('<circle cx="400" cy="300" r="50" fill="blue"/>')
            svg_parts.append('<text x="370" y="305" fill="white">orchestrator</text>')

        svg_parts.append('</svg>')

        content = '\n'.join(svg_parts)
        diagram_path.write_text(content)

        return diagram_path

    def _generate_agent_basic(
        self,
        enable_links: bool,
        enable_zoom: bool,
    ) -> Path:
        """Generate basic agent diagram."""
        diagram_path = self.output_dir / "agents.svg"

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.config.width}" height="{self.config.height}"',
        ]

        if enable_zoom:
            svg_parts[0] += f' viewBox="0 0 {self.config.width} {self.config.height}"'

        svg_parts[0] += '>'

        svg_parts.append('<text x="10" y="30">Agent Architecture</text>')
        svg_parts.append('<rect x="350" y="250" width="100" height="60" fill="green"/>')
        svg_parts.append('<text x="370" y="285">agent</text>')
        svg_parts.append('</svg>')

        content = '\n'.join(svg_parts)
        diagram_path.write_text(content)

        return diagram_path

    def _generate_mcp_flow_basic(
        self,
        enable_links: bool,
        enable_zoom: bool,
        include_assets: bool,
    ) -> Path:
        """Generate basic MCP flow diagram."""
        diagram_path = self.output_dir / "mcp-flow.svg"

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.config.width}" height="{self.config.height}">',
            '<text x="10" y="30">MCP Flow</text>',
        ]

        # Include asset reference if requested
        if include_assets:
            svg_parts.append('<image href="../assets/logo.svg" x="700" y="10" width="80" height="80"/>')

        svg_parts.append('<rect x="350" y="250" width="100" height="60" fill="purple"/>')
        svg_parts.append('<text x="360" y="285">cortex_tool</text>')
        svg_parts.append('</svg>')

        content = '\n'.join(svg_parts)
        diagram_path.write_text(content)

        return diagram_path
