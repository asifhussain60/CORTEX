"""PO Metrics Dashboard — velocity, cycle-time, and predictability metrics (GAP-129-09)."""

from __future__ import annotations

import statistics
from typing import Any, Dict, List, Optional


class POMetricsDashboard:
    """Transforms raw sprint/work-item data into a D3-ready metrics payload.

    Output schema (po-metrics-schema.json):
    {
        "velocity_trend":           [{"sprint": str, "points": float}],
        "cycle_time_distribution":  [{"story_id": str, "days": float}],
        "predictability_score":     float,   # 0-100
        "blocked_themes":           [str],
    }
    """

    def build(
        self,
        sprint_history: List[Dict[str, Any]],
        work_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Build PO metrics payload from sprint history and work items.

        Args:
            sprint_history: List of sprint dicts with ``sprint_name`` and
                ``completed_points`` keys.
            work_items: Optional list of work-item dicts with ``story_id``,
                ``cycle_time_days``, and optional ``blocked`` keys.

        Returns:
            Metrics dict matching po-metrics-schema.json.
        """
        velocity_trend = self._velocity_trend(sprint_history)
        cycle_time_dist = self._cycle_time_distribution(work_items or [])
        predictability = self._predictability_score(sprint_history)
        blocked_themes = self._blocked_themes(work_items or [])

        return {
            "velocity_trend": velocity_trend,
            "cycle_time_distribution": cycle_time_dist,
            "predictability_score": predictability,
            "blocked_themes": blocked_themes,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _velocity_trend(self, sprint_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "sprint": s.get("sprint_name", f"Sprint {i+1}"),
                "points": float(s.get("completed_points", 0)),
            }
            for i, s in enumerate(sprint_history)
        ]

    def _cycle_time_distribution(
        self, work_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "story_id": item.get("story_id", ""),
                "days": float(item.get("cycle_time_days", 0)),
            }
            for item in work_items
            if item.get("cycle_time_days") is not None
        ]

    def _predictability_score(self, sprint_history: List[Dict[str, Any]]) -> float:
        """Ratio of sprints that met or exceeded velocity baseline.

        Returns a 0-100 score.
        """
        if not sprint_history:
            return 0.0
        points_list = [float(s.get("completed_points", 0)) for s in sprint_history]
        if len(points_list) < 2:
            return 100.0
        mean_velocity = statistics.mean(points_list)
        met = sum(1 for p in points_list if p >= mean_velocity * 0.9)
        return round((met / len(points_list)) * 100, 1)

    def _blocked_themes(self, work_items: List[Dict[str, Any]]) -> List[str]:
        _BLOCKED_KEYWORDS = {"blocked", "impediment", "waiting", "dependency", "hold"}
        themes: set[str] = set()
        for item in work_items:
            tags = item.get("tags", [])
            title = (item.get("title") or "").lower()
            description = (item.get("description") or "").lower()
            combined = title + " " + description + " " + " ".join(
                t.lower() for t in (tags if isinstance(tags, list) else [])
            )
            for kw in _BLOCKED_KEYWORDS:
                if kw in combined:
                    theme = item.get("theme") or item.get("component") or kw
                    themes.add(str(theme))
        return sorted(themes)
