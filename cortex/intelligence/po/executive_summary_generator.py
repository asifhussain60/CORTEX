"""Executive Summary Generator — produces a 1-page sprint summary (GAP-129-08)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ExecutiveSummaryGenerator:
    """Generates a structured executive summary for stakeholders.

    Output is a plain-text string (never written to disk — CORE-002).
    """

    def generate(
        self,
        sprint_name: str,
        completed_items: List[Dict[str, Any]],
        velocity: Dict[str, Any],
        risks: Optional[List[Dict[str, Any]]] = None,
        next_sprint_goals: Optional[List[str]] = None,
    ) -> str:
        """Build a 1-page executive summary string.

        Args:
            sprint_name: Human-readable sprint label, e.g. "Sprint 12".
            completed_items: Work items completed this sprint — each has
                ``title`` and ``story_points`` keys.
            velocity: Dict with ``committed_points``, ``completed_points``,
                and optional ``predictability_score`` keys.
            risks: Optional list of risk dicts from RiskRegister.scan().
            next_sprint_goals: Optional list of goal strings for the next sprint.

        Returns:
            Formatted executive summary string.
        """
        sections: List[str] = []

        # Header
        sections.append(f"# Executive Summary — {sprint_name}")
        sections.append("=" * 60)

        # Velocity section
        committed = velocity.get("committed_points", 0)
        completed = velocity.get("completed_points", sum(
            float(i.get("story_points", 0) or 0) for i in completed_items
        ))
        pct = (completed / committed * 100) if committed else 0.0
        predictability = velocity.get("predictability_score", round(pct, 1))

        sections.append("\n## Velocity")
        sections.append(f"- Committed: {committed} points")
        sections.append(f"- Completed: {completed} points ({pct:.0f}% delivery)")
        sections.append(f"- Predictability Score: {predictability}/100")

        # Completed items
        sections.append("\n## Completed Work Items")
        if completed_items:
            for item in completed_items:
                title = item.get("title", "Untitled")
                pts = item.get("story_points", "?")
                sections.append(f"  - {title} ({pts} pts)")
        else:
            sections.append("  (No items completed this sprint.)")

        # Risks
        sections.append("\n## Risk Summary")
        risks = risks or []
        high = [r for r in risks if r.get("level") == "HIGH"]
        medium = [r for r in risks if r.get("level") == "MEDIUM"]
        if high:
            sections.append(f"  ⚠️  HIGH ({len(high)}): " + ", ".join(
                r.get("title", r.get("story_id", "?")) for r in high[:5]
            ))
        if medium:
            sections.append(f"  ⚡ MEDIUM ({len(medium)}): " + ", ".join(
                r.get("title", r.get("story_id", "?")) for r in medium[:5]
            ))
        if not high and not medium:
            sections.append("  ✅ No HIGH/MEDIUM risks identified.")

        # Next sprint goals
        sections.append("\n## Next Sprint Goals")
        next_goals = next_sprint_goals or []
        if next_goals:
            for goal in next_goals:
                sections.append(f"  - {goal}")
        else:
            sections.append("  (Goals to be defined in Sprint Planning.)")

        sections.append("\n" + "=" * 60)
        return "\n".join(sections)
