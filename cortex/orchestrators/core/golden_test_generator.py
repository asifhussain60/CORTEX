"""GoldenTestGenerator — CAPE sub-phase 136-e.

Produces a balanced test plan across 7 categories:
  sunshine, rainy, edge, regression, performance, security, integration

Distribution rules:
  ≥30% sunshine, ≥20% rainy, ≥2 edge tests.
  When rca_failures > 0, regression tests are included.

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064
AC-ID: AC-136-CAPE-005a
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Category templates (7 categories as per CAPE spec)
# ---------------------------------------------------------------------------

_CATEGORY_TEMPLATES: Dict[str, List[str]] = {
    "sunshine": [
        "Happy-path: {context} succeeds with valid input",
        "Happy-path: {context} returns expected output",
        "Happy-path: {context} integrates correctly with downstream",
    ],
    "rainy": [
        "Rainy-path: {context} handles invalid input gracefully",
        "Rainy-path: {context} raises on missing required fields",
        "Rainy-path: {context} rejects malformed payload",
    ],
    "edge": [
        "Edge: {context} handles empty collection",
        "Edge: {context} handles zero / null boundary value",
        "Edge: {context} handles maximum allowed value",
    ],
    "regression": [
        "Regression guard: {context} does not reintroduce known RCA failure",
        "Regression guard: {context} preserves prior behaviour after change",
    ],
    "performance": [
        "Performance: {context} completes within SLA under normal load",
        "Performance: {context} degrades gracefully under heavy load",
    ],
    "security": [
        "Security: {context} rejects unauthorised access",
        "Security: {context} sanitises output to prevent injection",
    ],
    "integration": [
        "Integration: {context} communicates correctly with external dependency",
        "Integration: {context} handles dependency timeout gracefully",
    ],
}


class GoldenTestGenerator:
    """Generate a balanced, RCA-informed test plan.

    Usage::

        gen = GoldenTestGenerator()
        plan = gen.generate(
            domain="payment",
            context="Process refund",
            rca_failures=3,
            total_tests=10,
        )
        # plan is a list of dicts with "category" and "description" keys
    """

    def generate(
        self,
        *,
        domain: str,
        context: str,
        rca_failures: int,
        total_tests: int,
    ) -> List[Dict[str, Any]]:
        """Generate a test plan.

        Args:
            domain:       Knowledge domain (used for category weighting).
            context:      Human-readable description of the feature / change.
            rca_failures: Number of historical RCA failures (adds regression tests).
            total_tests:  Target number of test cases to generate.

        Returns:
            List of test dicts with ``"category"`` and ``"description"`` keys.
        """
        plan: List[Dict[str, Any]] = []

        # Minimum mandatory counts
        sunshine_min = max(1, math.ceil(total_tests * 0.30))
        rainy_min = max(1, math.ceil(total_tests * 0.20))
        edge_min = 2

        # Fill mandatory minimums first
        plan += self._pick("sunshine", context, sunshine_min)
        plan += self._pick("rainy", context, rainy_min)
        plan += self._pick("edge", context, edge_min)

        # Regression guard if failures present
        if rca_failures > 0:
            plan += self._pick("regression", context, max(1, min(rca_failures, 2)))

        # Fill remaining with performance, security, integration
        remaining = total_tests - len(plan)
        extras = ["performance", "security", "integration"]
        per_extra = max(1, remaining // max(1, len(extras)))
        for cat in extras:
            plan += self._pick(cat, context, per_extra)

        return plan

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _pick(category: str, context: str, count: int) -> List[Dict[str, Any]]:
        """Pick ``count`` test cases from the template for ``category``.

        Args:
            category: One of the 7 category keys in ``_CATEGORY_TEMPLATES``.
            context:  Feature context string to interpolate.
            count:    Number of test cases to produce.

        Returns:
            List of test dicts.
        """
        templates = _CATEGORY_TEMPLATES.get(category, [f"Test {category}: {{context}}"])
        results = []
        for i in range(count):
            tmpl = templates[i % len(templates)]
            results.append(
                {"category": category, "description": tmpl.format(context=context)}
            )
        return results
