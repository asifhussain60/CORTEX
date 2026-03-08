"""TestPriorityClassifier — CAPE sub-phase 136-e.

Scores tests P0–P3 based on impact, likelihood, detection difficulty,
and domain-specific risk overrides.

Scoring:
  score = impact × 2 + likelihood × 2 + detection_difficulty
  P0: score ≥ 7
  P1: score 4–6
  P2: score 2–3
  P3: score < 2

Domain overrides (payment, auth, security, infrastructure) lift the
minimum priority to P1 regardless of raw score.

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064
AC-ID: AC-136-CAPE-005b
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

# ---------------------------------------------------------------------------
# Domain risk map — high-risk domains get a minimum priority of P1
# ---------------------------------------------------------------------------

DOMAIN_RISK_MAP: Dict[str, str] = {
    "payment":        "high_impact",
    "auth":           "high_impact",
    "security":       "high_impact",
    "infrastructure": "high_impact",
    "general":        "standard",
}

_HIGH_IMPACT_MIN_PRIORITY = "P1"

_P0_THRESHOLD = 7
_P1_THRESHOLD = 4
_P2_THRESHOLD = 2


@dataclass
class PriorityResult:
    """Result of :class:`TestPriorityClassifier`.

    Attributes:
        priority: Priority label — ``"P0"`` / ``"P1"`` / ``"P2"`` / ``"P3"``.
        score:    Raw numeric score used to derive the priority.
        domain:   Domain that was evaluated.
    """

    priority: str
    score: float
    domain: str


class TestPriorityClassifier:
    """Classify test priority using a scoring formula with domain overrides.

    Usage::

        classifier = TestPriorityClassifier()
        result = classifier.classify(
            domain="payment", impact=2, likelihood=2, detection_difficulty=1
        )
        # result.priority → "P1" (at minimum, due to payment domain override)
    """

    def classify(
        self,
        *,
        domain: str,
        impact: int,
        likelihood: int,
        detection_difficulty: int,
    ) -> PriorityResult:
        """Classify a test case's priority.

        Args:
            domain:               Knowledge domain (used for risk override).
            impact:               Impact score 0–3.
            likelihood:           Likelihood score 0–3.
            detection_difficulty: Detection difficulty score 0–1.

        Returns:
            :class:`PriorityResult` with ``priority``, ``score``, ``domain``.
        """
        score = float(impact * 2 + likelihood * 2 + detection_difficulty)
        priority = self._score_to_priority(score)

        # Apply domain override
        risk = DOMAIN_RISK_MAP.get(domain.lower(), "standard")
        if risk == "high_impact":
            priority = self._apply_domain_override(priority)

        return PriorityResult(priority=priority, score=score, domain=domain)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _score_to_priority(score: float) -> str:
        """Map numeric score to a P-level string."""
        if score >= _P0_THRESHOLD:
            return "P0"
        if score >= _P1_THRESHOLD:
            return "P1"
        if score >= _P2_THRESHOLD:
            return "P2"
        return "P3"

    @staticmethod
    def _apply_domain_override(priority: str) -> str:
        """Lift priority to at least P1 for high-impact domains."""
        order = ["P0", "P1", "P2", "P3"]
        min_idx = order.index(_HIGH_IMPACT_MIN_PRIORITY)
        current_idx = order.index(priority) if priority in order else len(order) - 1
        return order[min(min_idx, current_idx)]
