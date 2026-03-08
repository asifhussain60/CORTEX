"""Tests for ComplexityTriageEngine (CAPE sub-phase 136-a).

CDR (Complexity-Driven Routing) scoring engine — 5 weighted dimensions
(clarity / context / scope / risk / precedent) → ComplexityBand classification.

TDD RED phase: all imports will fail until implementation exists.
"""
import pytest


# ---------------------------------------------------------------------------
# Imports — will fail in RED phase (no module yet)
# ---------------------------------------------------------------------------
from cortex.orchestrators.core.complexity_triage_engine import (
    ComplexityBand,
    TriageResult,
    CDRScorer,
    ComplexityTriageEngine,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def scorer() -> CDRScorer:
    return CDRScorer()


@pytest.fixture()
def engine() -> ComplexityTriageEngine:
    return ComplexityTriageEngine()


@pytest.fixture()
def clean_input() -> dict:
    """Minimal input that produces low CDR score (SIMPLE band)."""
    return {
        "intent_confidence": 0.95,
        "lens_confidence": 1.0,
        "files_affected": 1,
        "circular_deps": 0,
        "coupling_score": 0.0,
        "rca_failures": 0,
    }


@pytest.fixture()
def complex_input() -> dict:
    """Input that produces high CDR score (COMPLEX band)."""
    return {
        "intent_confidence": 0.2,
        "lens_confidence": 0.3,
        "files_affected": 20,
        "circular_deps": 7,
        "coupling_score": 0.95,
        "rca_failures": 10,
    }


# ---------------------------------------------------------------------------
# CDRScorer — individual dimension scoring
# ---------------------------------------------------------------------------

class TestCDRScorerClarity:
    """score_clarity maps intent_confidence → clarity score."""

    def test_score_clarity_high_confidence(self, scorer: CDRScorer) -> None:
        score = scorer.score_clarity(intent_confidence=0.9)
        # high confidence → low complexity contribution → score near 0
        assert 0.0 <= score <= 0.2

    def test_score_clarity_low_confidence(self, scorer: CDRScorer) -> None:
        score = scorer.score_clarity(intent_confidence=0.3)
        # low confidence → high complexity contribution → score near 0.7
        assert score >= 0.6

    def test_score_clarity_perfect_confidence(self, scorer: CDRScorer) -> None:
        score = scorer.score_clarity(intent_confidence=1.0)
        assert score == pytest.approx(0.0, abs=0.01)

    def test_score_clarity_zero_confidence(self, scorer: CDRScorer) -> None:
        score = scorer.score_clarity(intent_confidence=0.0)
        assert score == pytest.approx(1.0, abs=0.01)


class TestCDRScorerContext:
    """score_context maps lens_confidence → context score."""

    def test_score_context_full_coverage(self, scorer: CDRScorer) -> None:
        score = scorer.score_context(lens_confidence=1.0)
        assert score == pytest.approx(0.0, abs=0.01)

    def test_score_context_zero_coverage(self, scorer: CDRScorer) -> None:
        score = scorer.score_context(lens_confidence=0.0)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_score_context_mid_coverage(self, scorer: CDRScorer) -> None:
        score = scorer.score_context(lens_confidence=0.5)
        assert 0.4 <= score <= 0.6


class TestCDRScorerScope:
    """score_scope maps files_affected count → scope score."""

    def test_score_scope_single_file(self, scorer: CDRScorer) -> None:
        score = scorer.score_scope(files_affected=1)
        assert score <= 0.2

    def test_score_scope_many_files(self, scorer: CDRScorer) -> None:
        score = scorer.score_scope(files_affected=15)
        assert score >= 0.8

    def test_score_scope_zero_files(self, scorer: CDRScorer) -> None:
        score = scorer.score_scope(files_affected=0)
        assert score == pytest.approx(0.0, abs=0.01)

    def test_score_scope_clamped_at_1(self, scorer: CDRScorer) -> None:
        score = scorer.score_scope(files_affected=100)
        assert score <= 1.0


class TestCDRScorerRisk:
    """score_risk maps circular_deps + coupling_score → risk score."""

    def test_score_risk_no_dependencies(self, scorer: CDRScorer) -> None:
        score = scorer.score_risk(circular_deps=0, coupling_score=0.0)
        assert score == pytest.approx(0.0, abs=0.01)

    def test_score_risk_high_coupling(self, scorer: CDRScorer) -> None:
        score = scorer.score_risk(circular_deps=5, coupling_score=0.9)
        assert score >= 0.7

    def test_score_risk_clamped_at_1(self, scorer: CDRScorer) -> None:
        score = scorer.score_risk(circular_deps=999, coupling_score=1.0)
        assert score <= 1.0


class TestCDRScorerPrecedent:
    """score_precedent maps rca_failures → precedent score."""

    def test_score_precedent_clean_history(self, scorer: CDRScorer) -> None:
        score = scorer.score_precedent(rca_failures=0)
        assert score == pytest.approx(0.0, abs=0.01)

    def test_score_precedent_repeat_failures(self, scorer: CDRScorer) -> None:
        score = scorer.score_precedent(rca_failures=15)
        assert score >= 0.8

    def test_score_precedent_clamped_at_1(self, scorer: CDRScorer) -> None:
        score = scorer.score_precedent(rca_failures=9999)
        assert score <= 1.0


class TestCDRScorerWeights:
    """CDR weight contract: all 5 weights must sum to exactly 1.0."""

    def test_composite_score_weights_sum_to_1(self, scorer: CDRScorer) -> None:
        total = sum(scorer.weights.values())
        assert total == pytest.approx(1.0, abs=1e-9)

    def test_composite_score_is_in_unit_interval(self, scorer: CDRScorer) -> None:
        score = scorer.composite_score(
            clarity=0.5, context=0.5, scope=0.5, risk=0.5, precedent=0.5
        )
        assert 0.0 <= score <= 1.0

    def test_composite_score_all_zeros(self, scorer: CDRScorer) -> None:
        score = scorer.composite_score(
            clarity=0.0, context=0.0, scope=0.0, risk=0.0, precedent=0.0
        )
        assert score == pytest.approx(0.0, abs=1e-9)

    def test_composite_score_all_ones(self, scorer: CDRScorer) -> None:
        score = scorer.composite_score(
            clarity=1.0, context=1.0, scope=1.0, risk=1.0, precedent=1.0
        )
        assert score == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# ComplexityTriageEngine — band classification + TriageResult
# ---------------------------------------------------------------------------

class TestComplexityTriageEngineBands:
    """triage() classifies inputs into SIMPLE / MODERATE / COMPLEX."""

    def test_triage_simple_band(self, engine: ComplexityTriageEngine, clean_input: dict) -> None:
        result: TriageResult = engine.triage(**clean_input)
        assert result.band == ComplexityBand.SIMPLE

    def test_triage_complex_band(self, engine: ComplexityTriageEngine, complex_input: dict) -> None:
        result: TriageResult = engine.triage(**complex_input)
        assert result.band == ComplexityBand.COMPLEX

    def test_triage_moderate_band(self, engine: ComplexityTriageEngine) -> None:
        result: TriageResult = engine.triage(
            intent_confidence=0.4,
            lens_confidence=0.4,
            files_affected=7,
            circular_deps=2,
            coupling_score=0.5,
            rca_failures=4,
        )
        assert result.band == ComplexityBand.MODERATE

    def test_triage_complex_band_many_files_override(
        self, engine: ComplexityTriageEngine
    ) -> None:
        """10+ files always forces at least COMPLEX (scope override)."""
        result: TriageResult = engine.triage(
            intent_confidence=0.9,
            lens_confidence=0.9,
            files_affected=10,
            circular_deps=0,
            coupling_score=0.0,
            rca_failures=0,
        )
        assert result.band == ComplexityBand.COMPLEX


class TestTriageResult:
    """TriageResult properties and structure."""

    def test_triage_result_needs_planning_complex(
        self, engine: ComplexityTriageEngine, complex_input: dict
    ) -> None:
        result: TriageResult = engine.triage(**complex_input)
        assert result.needs_planning is True

    def test_triage_result_needs_planning_simple_false(
        self, engine: ComplexityTriageEngine, clean_input: dict
    ) -> None:
        result: TriageResult = engine.triage(**clean_input)
        assert result.needs_planning is False

    def test_triage_result_has_cdr_score(
        self, engine: ComplexityTriageEngine, clean_input: dict
    ) -> None:
        result: TriageResult = engine.triage(**clean_input)
        assert 0.0 <= result.cdr_score <= 1.0

    def test_triage_result_has_dimension_scores(
        self, engine: ComplexityTriageEngine, clean_input: dict
    ) -> None:
        result: TriageResult = engine.triage(**clean_input)
        assert isinstance(result.dimension_scores, dict)
        assert set(result.dimension_scores.keys()) == {
            "clarity", "context", "scope", "risk", "precedent"
        }

    def test_triage_result_has_routing(
        self, engine: ComplexityTriageEngine, complex_input: dict
    ) -> None:
        result: TriageResult = engine.triage(**complex_input)
        assert isinstance(result.routing, str)
        assert len(result.routing) > 0

    def test_triage_result_edge_zero_files(
        self, engine: ComplexityTriageEngine
    ) -> None:
        """Zero files_affected must not raise."""
        result: TriageResult = engine.triage(
            intent_confidence=0.8,
            lens_confidence=0.8,
            files_affected=0,
            circular_deps=0,
            coupling_score=0.0,
            rca_failures=0,
        )
        assert result is not None
        assert result.band in (ComplexityBand.SIMPLE, ComplexityBand.MODERATE, ComplexityBand.COMPLEX)


class TestCDRResult:
    """CDRResult dataclass structure."""

    def test_cdr_result_has_score(self, engine: ComplexityTriageEngine, clean_input: dict) -> None:
        result: TriageResult = engine.triage(**clean_input)
        assert hasattr(result, "cdr_score")

    def test_cdr_result_score_in_range(
        self, engine: ComplexityTriageEngine, complex_input: dict
    ) -> None:
        result: TriageResult = engine.triage(**complex_input)
        assert 0.0 <= result.cdr_score <= 1.0


class TestComplexityBandEnum:
    """ComplexityBand enum values."""

    def test_simple_band_value(self) -> None:
        assert ComplexityBand.SIMPLE.value == "SIMPLE"

    def test_moderate_band_value(self) -> None:
        assert ComplexityBand.MODERATE.value == "MODERATE"

    def test_complex_band_value(self) -> None:
        assert ComplexityBand.COMPLEX.value == "COMPLEX"
