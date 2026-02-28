"""Engagement Renderer — BLOCK-ENGAGEMENT-BREADCRUMB and BLOCK-ENGAGEMENT-TIMELINE.

Renders orchestrator engagement visibility blocks for MCP tool responses.
Phase 85 defined the templates; Phase 89-c wires the renderer.

GAP-89-07: BLOCK-ENGAGEMENT-BREADCRUMB rendering
GAP-89-08: BLOCK-ENGAGEMENT-TIMELINE rendering
"""

from __future__ import annotations

from typing import Any


class EngagementRenderer:
    """Renders engagement breadcrumb and timeline for MCP responses.
    
    Thread-safe, stateless renderer that formats orchestrator routing chains
    and execution timelines according to Phase 85 response template standards.
    """

    def render_breadcrumb(self, chain: list[str]) -> str:
        """Render BLOCK-ENGAGEMENT-BREADCRUMB as single-line markdown.
        
        Args:
            chain: List of orchestrator/template names in routing order
            
        Returns:
            Single-line markdown breadcrumb with arrow separators
            
        Example:
            >>> renderer = EngagementRenderer()
            >>> renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
            '**Routing:** IntentRouter → TDDOrchestrator'
        """
        if not chain:
            return ""
        
        # Join with arrow separator
        routing_path = " → ".join(chain)
        
        # Return single-line markdown (Phase 85 standard)
        return f"**Routing:** {routing_path}"

    def render_timeline(self, stages: list[dict[str, Any]]) -> str | None:
        """Render BLOCK-ENGAGEMENT-TIMELINE as collapsible details block.
        
        Args:
            stages: List of dicts with 'name' and 'duration_ms' keys
            
        Returns:
            Collapsible HTML details block with stage timing, or None if empty
            
        Example:
            >>> renderer = EngagementRenderer()
            >>> stages = [
            ...     {"name": "Intent Classification", "duration_ms": 45},
            ...     {"name": "LENS Analysis", "duration_ms": 120}
            ... ]
            >>> timeline = renderer.render_timeline(stages)
            >>> "<details>" in timeline
            True
        """
        if not stages:
            return None
        
        # Build timeline rows
        rows: list[str] = []
        for stage in stages:
            name = stage.get("name", "Unknown")
            duration_ms = stage.get("duration_ms", 0)
            rows.append(f"  • {name}: {duration_ms}ms")
        
        timeline_body = "\n".join(rows)
        
        # Wrap in collapsible details (Phase 85 standard)
        return f"""<details>
<summary>📊 Execution Timeline</summary>

{timeline_body}

</details>"""
