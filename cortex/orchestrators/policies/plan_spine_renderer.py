"""
ASCII Plan Spine Renderer for CORTEX.

Renders compact progress visualization (≤8 lines) for autonomous execution.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 specification (AC-29-F4), Phase 31A (minimal spine)
"""

from typing import Any, Dict, List, Literal


class PlanSpineRenderer:
    """
    ASCII Plan Spine renderer for progress visualization.

    Renders compact horizontal format:
    [✓] Phase 1 | [→] Phase 2 | [ ] Phase 3

    Forbidden (SCREAMING format):
    [████████░░] 80% - Loading...  ❌

    Authority: Phase-31A Minimal Plan Spine Enhancement
    """

    GLYPHS = {
        "complete": "[✓]",
        "in_progress": "[→]",
        "pending": "[ ]",
        "blocked": "[!]",
        "skipped": "[~]",
    }

    def __init__(self, orientation: Literal["horizontal", "vertical"] = "horizontal"):
        """
        Initialize renderer.

        Args:
            orientation: Layout direction (horizontal = single line, vertical = stacked)
        """
        self.orientation = orientation

    def render(self, phases: List[Dict[str, Any]]) -> str:
        """
        Render ASCII Plan Spine.

        Args:
            phases: List of phase dicts with keys: name, status, progress (optional)

        Returns:
            Formatted Plan Spine string
        """
        if not phases:
            return ""

        if self.orientation == "horizontal":
            return self._render_horizontal(phases)
        else:
            return self._render_vertical(phases)

    def _render_horizontal(self, phases: List[Dict[str, Any]]) -> str:
        """
        Render horizontal single-line format.

        Example: [✓] Phase 1 | [→] Phase 2 | [ ] Phase 3
        """
        parts = []

        for phase in phases:
            status = phase.get("status", "pending")
            name = phase.get("name", "Unknown")

            glyph = self.GLYPHS.get(status, self.GLYPHS["pending"])
            parts.append(f"{glyph} {name}")

        return " | ".join(parts)

    def _render_vertical(self, phases: List[Dict[str, Any]]) -> str:
        """
        Render vertical stacked format.

        Example:
        ├─ [✓] Phase 1: Complete
        ├─ [→] Phase 2: In progress
        └─ [ ] Phase 3: Pending
        """
        lines = []

        for i, phase in enumerate(phases):
            status = phase.get("status", "pending")
            name = phase.get("name", "Unknown")

            glyph = self.GLYPHS.get(status, self.GLYPHS["pending"])

            # Tree characters
            if i == len(phases) - 1:
                prefix = "└─"
            else:
                prefix = "├─"

            lines.append(f"{prefix} {glyph} {name}")

        return "\n".join(lines)

    def render_with_progress(self, phases: List[Dict[str, Any]]) -> str:
        """
        Render with progress percentages (still compact).

        Example: [✓] Phase 1 100% | [→] Phase 2 60% | [ ] Phase 3 0%
        """
        parts = []

        for phase in phases:
            status = phase.get("status", "pending")
            name = phase.get("name", "Unknown")
            progress = phase.get("progress", 0)

            glyph = self.GLYPHS.get(status, self.GLYPHS["pending"])
            parts.append(f"{glyph} {name} {progress}%")

        return " | ".join(parts)
