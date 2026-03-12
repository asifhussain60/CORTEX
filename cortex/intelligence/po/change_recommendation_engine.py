"""Change Recommendation Engine — impact analysis for scope changes (GAP-129-05)."""

from __future__ import annotations

from typing import Any, Dict, Literal

Verdict = Literal["ACCEPT", "DEFER", "REJECT"]


class ChangeRecommendationEngine:
    """Evaluates mid-sprint scope changes and produces ACCEPT/DEFER/REJECT verdicts.

    Scoring:
        capacity_score (0–40): remaining capacity vs change effort
        dependency_score (0–30): blocking dependencies for this change
        risk_score (0–30): risk register entries related to this change

    Verdict thresholds:
        score >= 60 → ACCEPT
        score >= 30 → DEFER
        score < 30  → REJECT
    """

    ACCEPT_THRESHOLD: int = 60
    DEFER_THRESHOLD: int = 30

    def evaluate(
        self,
        change_request: Dict[str, Any],
        sprint_capacity: Dict[str, Any],
        risk_register: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Produce a structured ACCEPT/DEFER/REJECT recommendation.

        Args:
            change_request: dict with:
                name (str), effort_points (float), priority (str: high/medium/low)
            sprint_capacity: output of SprintCapacityCalculator.calculate()
            risk_register: optional dict with "high_risks" (int count) field

        Returns:
            verdict (str), justification (str), score (float), details (dict)
        """
        # If committed capacity is zero, no change can be accommodated → REJECT
        if float(sprint_capacity.get("committed_points", 0)) <= 0:
            return {
                "verdict": "REJECT",
                "justification": f"REJECT: Sprint has no committed capacity. '{change_request.get('name', 'this change')}' cannot be scheduled.",
                "score": 0.0,
                "details": {"capacity_score": 0, "dependency_score": 0, "risk_score": 0},
            }

        capacity_score = self._score_capacity(change_request, sprint_capacity)
        dependency_score = self._score_dependencies(change_request)
        risk_score_val = self._score_risk(risk_register)

        total_score = capacity_score + dependency_score + risk_score_val

        verdict: Verdict = (
            "ACCEPT" if total_score >= self.ACCEPT_THRESHOLD
            else "DEFER" if total_score >= self.DEFER_THRESHOLD
            else "REJECT"
        )

        justification = self._build_justification(
            verdict, capacity_score, dependency_score, risk_score_val, change_request
        )

        return {
            "verdict": verdict,
            "justification": justification,
            "score": round(total_score, 2),
            "details": {
                "capacity_score": capacity_score,
                "dependency_score": dependency_score,
                "risk_score": risk_score_val,
            },
        }

    @staticmethod
    def _score_capacity(
        change_request: Dict[str, Any], sprint_capacity: Dict[str, Any]
    ) -> float:
        """0–40 based on effort vs remaining committed capacity."""
        effort = float(change_request.get("effort_points", 0))
        committed = float(sprint_capacity.get("committed_points", 0))
        if committed <= 0:
            return 0.0
        headroom_ratio = max(0.0, (committed - effort) / committed)
        return round(headroom_ratio * 40, 2)

    @staticmethod
    def _score_dependencies(change_request: Dict[str, Any]) -> float:
        """0–30: fewer blocking dependencies = higher score."""
        deps = int(change_request.get("blocking_dependencies", 0))
        if deps == 0:
            return 30.0
        if deps == 1:
            return 20.0
        if deps == 2:
            return 10.0
        return 0.0

    @staticmethod
    def _score_risk(risk_register: Dict[str, Any] | None) -> float:
        """0–30: fewer high risks = higher score."""
        if not risk_register:
            return 20.0  # neutral if no risk data
        high_risks = int(risk_register.get("high_risks", 0))
        if high_risks == 0:
            return 30.0
        if high_risks <= 2:
            return 15.0
        return 0.0

    @staticmethod
    def _build_justification(
        verdict: Verdict,
        capacity: float,
        dependency: float,
        risk: float,
        change_request: Dict[str, Any],
    ) -> str:
        name = change_request.get("name", "this change")
        if verdict == "ACCEPT":
            return (
                f"ACCEPT: '{name}' fits within sprint capacity (score {capacity:.0f}/40), "
                f"has manageable dependencies (score {dependency:.0f}/30), and "
                f"acceptable risk profile (score {risk:.0f}/30)."
            )
        if verdict == "DEFER":
            return (
                f"DEFER: '{name}' has borderline capacity or dependency constraints. "
                f"Recommend scheduling for the next sprint when conditions are clearer."
            )
        return (
            f"REJECT: '{name}' cannot be safely accommodated. Capacity ({capacity:.0f}/40), "
            f"dependencies ({dependency:.0f}/30), or risk ({risk:.0f}/30) are prohibitive."
        )
