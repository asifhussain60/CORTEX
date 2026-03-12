"""Sprint Capacity Calculator (GAP-129-10)."""

from __future__ import annotations

import math
import statistics
from typing import Any, Dict, List, Tuple


class SprintCapacityCalculator:
    """Calculates committed story point budget for sprint planning.

    Formula:
        available_days = Σ(member_days × focus_factor) for each team member
        capacity_points = (available_days / sprint_days) × velocity_baseline
        confidence_interval = capacity_points ± (1.96 × std_dev) if history provided
    """

    DEFAULT_SPRINT_DAYS: int = 10  # standard 2-week sprint

    def calculate(
        self,
        team_members: List[Dict[str, Any]],
        velocity_baseline: float,
        velocity_history: List[float] | None = None,
        sprint_days: int = DEFAULT_SPRINT_DAYS,
    ) -> Dict[str, Any]:
        """Compute sprint capacity and confidence interval.

        team_members: list of {"name": str, "available_days": float, "focus_factor": float}
        velocity_baseline: historical average velocity in story points
        velocity_history: optional list of past sprint velocities for CI computation
        sprint_days: working days in the sprint (default 10)

        Returns:
            committed_points (float),
            confidence_interval (tuple[float, float]),
            available_days (float),
            capacity_ratio (float) — fraction of full team capacity available
        """
        total_available = sum(
            float(m.get("available_days", 0)) * float(m.get("focus_factor", 1.0))
            for m in team_members
        )
        full_capacity = sprint_days * len(team_members)
        capacity_ratio = (total_available / full_capacity) if full_capacity else 0.0

        committed = round(velocity_baseline * capacity_ratio, 2)

        if velocity_history and len(velocity_history) >= 2:
            std_dev = statistics.stdev(velocity_history)
            margin = round(1.96 * std_dev * capacity_ratio, 2)
        else:
            margin = round(committed * 0.15, 2)  # default ±15% if no history

        confidence_interval: Tuple[float, float] = (
            round(max(0.0, committed - margin), 2),
            round(committed + margin, 2),
        )

        return {
            "committed_points": committed,
            "confidence_interval": confidence_interval,
            "available_days": round(total_available, 2),
            "capacity_ratio": round(capacity_ratio, 4),
        }
