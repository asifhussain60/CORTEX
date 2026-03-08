"""ComplexityTriageEngine — CAPE sub-phase 136-a.

CDR (Complexity-Driven Routing) scoring engine.  Evaluates 5 weighted
dimensions (clarity / context / scope / risk / precedent) to produce a
composite CDR score in [0.0, 1.0] and classifies requests into
SIMPLE / MODERATE / COMPLEX bands.

CAPE uses this classification to select a roadmap template and drive
plan generation in sub-phases 136-b onwards.

Author: CORTEX Framework
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
             CORE-035 (single canonical implementation), CORE-064 (sweep)
AC-ID: AC-136-CAPE-001
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


# ---------------------------------------------------------------------------
# Public enum
# ---------------------------------------------------------------------------

class ComplexityBand(str, Enum):
    """Complexity band produced by the CDR triage."""

    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class CDRResult:
    """Raw CDR scoring output before band classification.

    Attributes:
        score:      Composite CDR score in [0.0, 1.0].
        routing:    Suggested routing label for downstream CAPE selection.
        dimensions: Per-dimension raw scores keyed by dimension name.
    """

    score: float
    routing: str
    dimensions: Dict[str, float] = field(default_factory=dict)


@dataclass
class TriageResult:
    """Full triage result returned by :class:`ComplexityTriageEngine`.

    Attributes:
        band:             Classified complexity band.
        cdr_score:        Composite CDR score in [0.0, 1.0].
        dimension_scores: Per-dimension scores
                          (clarity/context/scope/risk/precedent).
        routing:          Routing label derived from band.
        files_affected:   Number of files in scope (passed through for
                          downstream plan generation).
    """

    band: ComplexityBand
    cdr_score: float
    dimension_scores: Dict[str, float]
    routing: str
    files_affected: int

    @property
    def needs_planning(self) -> bool:
        """True when the request is COMPLEX and warrants full plan generation."""
        return self.band == ComplexityBand.COMPLEX


# ---------------------------------------------------------------------------
# CDR weight constants (must sum to 1.0 — CORE-035 invariant)
# ---------------------------------------------------------------------------

_WEIGHTS: Dict[str, float] = {
    "clarity":   0.25,
    "context":   0.20,
    "scope":     0.25,
    "risk":      0.20,
    "precedent": 0.10,
}

# Band thresholds
_SIMPLE_MAX: float = 0.35
_MODERATE_MAX: float = 0.65

# Scope override: force COMPLEX when ≥ this many files
_COMPLEX_FILE_OVERRIDE: int = 10

# Scope dimension: max files that map to score 1.0  (linear: 1 file → 0.067,
# 15 files → 1.0 → satisfies both ≤0.2 @ 1 file and ≥0.8 @ 15 files tests)
_SCOPE_MAX_FILES: int = 15

# Risk dimension: max circular deps that map to score 1.0
_RISK_MAX_DEPS: int = 10

# Precedent dimension: max rca_failures that map to score 1.0
_PRECEDENT_MAX_FAILURES: int = 10


# ---------------------------------------------------------------------------
# CDRScorer
# ---------------------------------------------------------------------------

class CDRScorer:
    """Stateless scorer that produces per-dimension CDR scores.

    Each ``score_*`` method returns a value in [0.0, 1.0] where
    **higher means more complex / risky** (contributes more to the
    composite CDR score).

    The five weights must always sum to 1.0 (``CORE-035`` invariant).
    This is asserted at construction time.
    """

    def __init__(self) -> None:
        self.weights: Dict[str, float] = dict(_WEIGHTS)
        total = sum(self.weights.values())
        assert abs(total - 1.0) < 1e-9, (
            f"CDR weights must sum to 1.0, got {total}"
        )

    # ------------------------------------------------------------------
    # Individual dimension scorers
    # ------------------------------------------------------------------

    def score_clarity(self, *, intent_confidence: float) -> float:
        """Invert intent confidence: high confidence → low complexity.

        Args:
            intent_confidence: Classifier confidence in [0.0, 1.0].

        Returns:
            Clarity dimension score in [0.0, 1.0].
        """
        return max(0.0, min(1.0, 1.0 - intent_confidence))

    def score_context(self, *, lens_confidence: float) -> float:
        """Invert LENS confidence: good context → low complexity.

        Args:
            lens_confidence: LENS coverage confidence in [0.0, 1.0].

        Returns:
            Context dimension score in [0.0, 1.0].
        """
        return max(0.0, min(1.0, 1.0 - lens_confidence))

    def score_scope(self, *, files_affected: int) -> float:
        """Map files-affected count to scope score (linearly normalised).

        Breakpoints:
          - 0 files  → 0.0
          - 1 file   → ≤ 0.20   (low complexity)
          - 15 files → ≥ 0.80   (high complexity)
          - ≥20 files → 1.0     (clamped)

        Args:
            files_affected: Number of files touched by the request.

        Returns:
            Scope dimension score in [0.0, 1.0].
        """
        if files_affected <= 0:
            return 0.0
        # Linear ramp: 1 → ~0.067, 15 → 1.0, clamped at 1.0
        raw = files_affected / _SCOPE_MAX_FILES
        return max(0.0, min(1.0, raw))

    def score_risk(self, *, circular_deps: int, coupling_score: float) -> float:
        """Combine circular dependency count and tight coupling score.

        Args:
            circular_deps:  Number of circular dependency cycles.
            coupling_score: Structural coupling score in [0.0, 1.0].

        Returns:
            Risk dimension score in [0.0, 1.0].
        """
        dep_component = min(1.0, circular_deps / max(1, _RISK_MAX_DEPS))
        raw = 0.5 * dep_component + 0.5 * max(0.0, min(1.0, coupling_score))
        return max(0.0, min(1.0, raw))

    def score_precedent(self, *, rca_failures: int) -> float:
        """Map historical RCA failures to precedent score.

        Args:
            rca_failures: Number of recorded RCA failure events.

        Returns:
            Precedent dimension score in [0.0, 1.0].
        """
        raw = min(1.0, rca_failures / max(1, _PRECEDENT_MAX_FAILURES))
        return max(0.0, min(1.0, raw))

    # ------------------------------------------------------------------
    # Composite score
    # ------------------------------------------------------------------

    def composite_score(
        self,
        *,
        clarity: float,
        context: float,
        scope: float,
        risk: float,
        precedent: float,
    ) -> float:
        """Compute weighted composite CDR score.

        Args:
            clarity:   Clarity dimension score.
            context:   Context dimension score.
            scope:     Scope dimension score.
            risk:      Risk dimension score.
            precedent: Precedent dimension score.

        Returns:
            Composite CDR score in [0.0, 1.0].
        """
        raw = (
            self.weights["clarity"]   * clarity
            + self.weights["context"]   * context
            + self.weights["scope"]     * scope
            + self.weights["risk"]      * risk
            + self.weights["precedent"] * precedent
        )
        return max(0.0, min(1.0, raw))


# ---------------------------------------------------------------------------
# ComplexityTriageEngine
# ---------------------------------------------------------------------------

_ROUTING_MAP: Dict[ComplexityBand, str] = {
    ComplexityBand.SIMPLE:   "linear-execution",
    ComplexityBand.MODERATE: "phased-roadmap",
    ComplexityBand.COMPLEX:  "epic-roadmap",
}


class ComplexityTriageEngine:
    """Entry point for CAPE complexity triage.

    Combines a :class:`CDRScorer` with band classification logic to
    produce a :class:`TriageResult` from raw request signals.

    Usage::

        engine = ComplexityTriageEngine()
        result = engine.triage(
            intent_confidence=0.8,
            lens_confidence=0.9,
            files_affected=3,
            circular_deps=0,
            coupling_score=0.1,
            rca_failures=1,
        )
        # result.band → ComplexityBand.SIMPLE
        # result.needs_planning → False
    """

    def __init__(self) -> None:
        self._scorer = CDRScorer()

    def triage(
        self,
        *,
        intent_confidence: float,
        lens_confidence: float,
        files_affected: int,
        circular_deps: int,
        coupling_score: float,
        rca_failures: int,
    ) -> TriageResult:
        """Run CDR triage on the supplied request signals.

        Args:
            intent_confidence: Classifier intent-recognition confidence [0,1].
            lens_confidence:   LENS workspace coverage confidence [0,1].
            files_affected:    Number of source files in scope.
            circular_deps:     Number of detected circular dependency cycles.
            coupling_score:    Structural coupling score [0,1].
            rca_failures:      Historical RCA failure event count.

        Returns:
            :class:`TriageResult` with band, CDR score, dimension scores,
            routing label, and files_affected passed through.
        """
        s = self._scorer

        dim: Dict[str, float] = {
            "clarity":   s.score_clarity(intent_confidence=intent_confidence),
            "context":   s.score_context(lens_confidence=lens_confidence),
            "scope":     s.score_scope(files_affected=files_affected),
            "risk":      s.score_risk(
                circular_deps=circular_deps, coupling_score=coupling_score
            ),
            "precedent": s.score_precedent(rca_failures=rca_failures),
        }

        cdr_score = s.composite_score(
            clarity=dim["clarity"],
            context=dim["context"],
            scope=dim["scope"],
            risk=dim["risk"],
            precedent=dim["precedent"],
        )

        band = self._classify_band(cdr_score=cdr_score, files_affected=files_affected)
        routing = _ROUTING_MAP[band]

        return TriageResult(
            band=band,
            cdr_score=cdr_score,
            dimension_scores=dim,
            routing=routing,
            files_affected=files_affected,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _classify_band(self, *, cdr_score: float, files_affected: int) -> ComplexityBand:
        """Map CDR score + file-count override to a :class:`ComplexityBand`.

        10 or more affected files always forces **COMPLEX** regardless of
        the numeric CDR score (scope override — see CAPE spec § 136-a).
        """
        if files_affected >= _COMPLEX_FILE_OVERRIDE:
            return ComplexityBand.COMPLEX
        if cdr_score <= _SIMPLE_MAX:
            return ComplexityBand.SIMPLE
        if cdr_score <= _MODERATE_MAX:
            return ComplexityBand.MODERATE
        return ComplexityBand.COMPLEX
