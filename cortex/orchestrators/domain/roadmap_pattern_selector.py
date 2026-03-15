"""RoadmapPatternSelector — CAPE sub-phase 136-b.

Maps (ComplexityBand, intent) → one of 5 roadmap templates with a
max sub-phase cap. This drives template selection in AutoPlanGenerator.

Templates:
  1. linear-execution   — SIMPLE band, any implementation intent
  2. phased-roadmap     — MODERATE band, implementation
  3. epic-roadmap       — COMPLEX band, 10+ files
  4. parallel-execution — MODERATE/COMPLEX, parallel feasible intents
  5. sts-refactoring    — any band when intent is REFACTOR

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064
AC-ID: AC-136-CAPE-002a
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


# ---------------------------------------------------------------------------
# Complexity types (inlined — complexity classification is now LLM-native;
# these data structures support roadmap selection logic only).
# CORTEX-V2 phase-m1-c: complexity_triage_engine.py deleted per GAP-M1-08.
# ---------------------------------------------------------------------------


class ComplexityBand(str, Enum):
    """Complexity band used for roadmap template selection."""

    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"


@dataclass
class TriageResult:
    """Minimal triage result consumed by RoadmapPatternSelector.

    Attributes:
        band:    Classified complexity band.
        score:   Normalised score in [0.0, 1.0].
        routing: Suggested routing label.
        dimensions: Per-dimension scores (optional).
    """

    band: ComplexityBand
    score: float = 0.5
    routing: str = ""
    dimensions: Dict[str, float] = field(default_factory=dict)

# ---------------------------------------------------------------------------
# Template catalogue
# ---------------------------------------------------------------------------

_TEMPLATE_LIMITS: dict[str, int] = {
    "linear-execution":   3,
    "phased-roadmap":     8,
    "epic-roadmap":       15,
    "parallel-execution": 10,
    "sts-refactoring":    10,
}

_REFACTOR_INTENTS = frozenset({"REFACTOR", "CLEAN", "CLEANUP", "IMPROVE"})
_PLAN_INTENTS = frozenset({"PLAN", "DESIGN", "ROADMAP"})


@dataclass
class RoadmapSelection:
    """Result of :class:`RoadmapPatternSelector`.

    Attributes:
        template_name:   One of the 5 canonical CAPE template names.
        max_sub_phases:  Recommended cap on generated sub-phase count.
        band:            Complexity band that drove the selection.
        intent:          Intent string that was evaluated.
    """

    template_name: str
    max_sub_phases: int
    band: ComplexityBand
    intent: str


class RoadmapPatternSelector:
    """Select the appropriate roadmap template based on triage + intent.

    Priority rules (first match wins):
    1. REFACTOR intent → ``sts-refactoring``
    2. SIMPLE band → ``linear-execution``
    3. COMPLEX band → ``epic-roadmap``
    4. PLAN/DESIGN intent → ``phased-roadmap``
    5. MODERATE band → ``phased-roadmap`` (default moderate)

    Usage::

        selector = RoadmapPatternSelector()
        selection = selector.select(triage=triage_result, intent="IMPLEMENT")
        # selection.template_name → "linear-execution" / "epic-roadmap" / ...
    """

    def select(self, *, triage: TriageResult, intent: str) -> RoadmapSelection:
        """Select a roadmap template.

        Args:
            triage: :class:`TriageResult` from
                    :class:`~cortex.orchestrators.core.complexity_triage_engine.ComplexityTriageEngine`.
            intent: Upper-case intent string (e.g. ``"IMPLEMENT"``, ``"REFACTOR"``).

        Returns:
            :class:`RoadmapSelection` with the chosen template and cap.
        """
        upper_intent = intent.upper()
        template = self._pick_template(band=triage.band, intent=upper_intent)
        return RoadmapSelection(
            template_name=template,
            max_sub_phases=_TEMPLATE_LIMITS[template],
            band=triage.band,
            intent=upper_intent,
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _pick_template(self, *, band: ComplexityBand, intent: str) -> str:
        """Map band + intent to a template name (first-match priority)."""
        if intent in _REFACTOR_INTENTS:
            return "sts-refactoring"
        if band == ComplexityBand.SIMPLE:
            return "linear-execution"
        if band == ComplexityBand.COMPLEX:
            return "epic-roadmap"
        if intent in _PLAN_INTENTS:
            return "phased-roadmap"
        # MODERATE default
        return "phased-roadmap"
