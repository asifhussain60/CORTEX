"""ROI Calculator — WSJF ranking for feature prioritization (GAP-129-04)."""

from __future__ import annotations

import math
from typing import Any, Dict, List


class ROICalculator:
    """Weighted Shortest Job First (WSJF) calculator for SAFe teams.

    WSJF = Cost of Delay / Job Duration
    Cost of Delay = Business Value + Time Criticality + Risk Reduction / Opportunity Enablement
    """

    def calculate_wsjf(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank features by WSJF score (highest first).

        Each feature dict must contain:
            name (str), business_value (float 1-10), time_criticality (float 1-10),
            rr_oe (float 1-10 — risk reduction / opportunity enablement),
            job_size (float 1-10 — implementation effort, Fibonacci preferred)

        Returns the input list augmented with a `wsjf_score` field, sorted descending.
        """
        scored = []
        for feature in features:
            job_size = float(feature.get("job_size", 1)) or 1.0
            cost_of_delay = (
                float(feature.get("business_value", 1))
                + float(feature.get("time_criticality", 1))
                + float(feature.get("rr_oe", 1))
            )
            wsjf = round(cost_of_delay / job_size, 4)
            scored.append({**feature, "wsjf_score": wsjf, "cost_of_delay": round(cost_of_delay, 4)})
        return sorted(scored, key=lambda f: f["wsjf_score"], reverse=True)

    def rank(self, features: List[Dict[str, Any]]) -> List[str]:
        """Return feature names ranked by WSJF score (highest first)."""
        ranked = self.calculate_wsjf(features)
        return [f.get("name", "") for f in ranked]

    def top_n(self, features: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
        """Return the top N features by WSJF score."""
        return self.calculate_wsjf(features)[:n]
