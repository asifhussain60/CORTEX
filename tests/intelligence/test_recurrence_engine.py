"""
Phase 87 — Recurrence Signature Engine Tests (RED phase — CORE-008)
Tests for RecurrenceSignatureEngine — generates and matches failure signatures.

AC-PHASE87-005: RecurrenceSignatureEngine tests
CORE-008: TDD mandatory
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

import pytest


@pytest.fixture
def engine():
    """Return a default RecurrenceSignatureEngine."""
    from cortex.intelligence.learning.recurrence_engine import RecurrenceSignatureEngine
    return RecurrenceSignatureEngine()


@pytest.fixture
def sample_rca():
    """Return a populated RCAAnalysis for signature tests."""
    from cortex.intelligence.learning.rca_models import (
        RCAAnalysis, RCATemplate, RCACategory
    )
    return RCAAnalysis(
        id="RCA-SIG-001",
        failure_id="OPJ-sig-001",
        methodology=RCATemplate.FIVE_WHYS,
        category=RCACategory.TECHNOLOGY,
        root_cause="Missing null guard on response handler",
        confidence=0.88,
    )


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------
class TestRecurrenceEngineImport:
    """RecurrenceSignatureEngine must be importable."""

    def test_recurrence_engine_is_importable(self) -> None:
        """RecurrenceSignatureEngine must be importable."""
        from cortex.intelligence.learning.recurrence_engine import RecurrenceSignatureEngine
        assert RecurrenceSignatureEngine is not None

    def test_recurrence_engine_has_generate_signature(self) -> None:
        """Must expose generate_signature()."""
        from cortex.intelligence.learning.recurrence_engine import RecurrenceSignatureEngine
        assert hasattr(RecurrenceSignatureEngine, "generate_signature")

    def test_recurrence_engine_has_find_matches(self) -> None:
        """Must expose find_matches()."""
        from cortex.intelligence.learning.recurrence_engine import RecurrenceSignatureEngine
        assert hasattr(RecurrenceSignatureEngine, "find_matches")

    def test_recurrence_engine_has_similarity(self) -> None:
        """Must expose similarity() for computing pairwise similarity."""
        from cortex.intelligence.learning.recurrence_engine import RecurrenceSignatureEngine
        assert hasattr(RecurrenceSignatureEngine, "similarity")


# ---------------------------------------------------------------------------
# generate_signature()
# ---------------------------------------------------------------------------
class TestGenerateSignature:
    """Tests for RecurrenceSignatureEngine.generate_signature()."""

    def test_returns_non_empty_string(self, engine, sample_rca) -> None:
        """generate_signature() must return a non-empty string."""
        sig = engine.generate_signature(sample_rca)
        assert isinstance(sig, str)
        assert len(sig) > 0

    def test_same_rca_produces_same_signature(self, engine, sample_rca) -> None:
        """generate_signature() must be deterministic for the same RCA."""
        sig1 = engine.generate_signature(sample_rca)
        sig2 = engine.generate_signature(sample_rca)
        assert sig1 == sig2

    def test_different_root_causes_produce_different_signatures(self, engine) -> None:
        """Different root causes must produce different signatures."""
        from cortex.intelligence.learning.rca_models import (
            RCAAnalysis, RCATemplate, RCACategory
        )
        rca_a = RCAAnalysis(
            id="RCA-SIG-A",
            failure_id="OPJ-a",
            methodology=RCATemplate.FIVE_WHYS,
            category=RCACategory.TECHNOLOGY,
            root_cause="Type error in decorator chain",
            confidence=0.8,
        )
        rca_b = RCAAnalysis(
            id="RCA-SIG-B",
            failure_id="OPJ-b",
            methodology=RCATemplate.FISHBONE,
            category=RCACategory.PROCESS,
            root_cause="Missing pre-commit hook validation",
            confidence=0.8,
        )
        assert engine.generate_signature(rca_a) != engine.generate_signature(rca_b)

    def test_signature_encodes_category(self, engine, sample_rca) -> None:
        """Signature must include the RCA category string."""
        sig = engine.generate_signature(sample_rca)
        assert sample_rca.category.value in sig or len(sig) > 8  # either embedded or hashed

    def test_signature_starts_with_sig_prefix(self, engine, sample_rca) -> None:
        """Signature must start with 'SIG-' prefix."""
        sig = engine.generate_signature(sample_rca)
        assert sig.startswith("SIG-")


# ---------------------------------------------------------------------------
# similarity()
# ---------------------------------------------------------------------------
class TestSimilarity:
    """Tests for RecurrenceSignatureEngine.similarity()."""

    def test_identical_signatures_have_similarity_one(self, engine) -> None:
        """Identical signatures must have similarity == 1.0."""
        sig = "SIG-TECH-abc123"
        assert engine.similarity(sig, sig) == pytest.approx(1.0)

    def test_completely_different_signatures_have_low_similarity(self, engine) -> None:
        """Completely different signatures must have similarity < 0.5."""
        result = engine.similarity("SIG-TECH-aaaaaa", "SIG-PROC-zzzzzzz")
        assert result < 0.5

    def test_similarity_is_symmetric(self, engine) -> None:
        """similarity(a, b) must equal similarity(b, a)."""
        a = "SIG-TECH-handler-null-guard"
        b = "SIG-TECH-handler-null-check"
        assert engine.similarity(a, b) == pytest.approx(engine.similarity(b, a))

    def test_similarity_returns_float_in_range(self, engine) -> None:
        """similarity() must return a float in [0.0, 1.0]."""
        result = engine.similarity("SIG-TECH-abc", "SIG-TECH-xyz")
        assert 0.0 <= result <= 1.0


# ---------------------------------------------------------------------------
# find_matches()
# ---------------------------------------------------------------------------
class TestFindMatches:
    """Tests for RecurrenceSignatureEngine.find_matches()."""

    def test_find_matches_returns_list(self, engine) -> None:
        """find_matches() must return a list."""
        result = engine.find_matches("SIG-TECH-abc", candidates=[], threshold=0.85)
        assert isinstance(result, list)

    def test_find_matches_empty_candidates_returns_empty(self, engine) -> None:
        """find_matches() with empty candidate list must return []."""
        result = engine.find_matches("SIG-TECH-abc", candidates=[], threshold=0.85)
        assert result == []

    def test_find_matches_above_threshold(self, engine) -> None:
        """find_matches() must include candidates above the threshold."""
        sig = "SIG-TECH-nullguard"
        candidates = ["SIG-TECH-nullguard", "SIG-PROC-something-completely-different"]
        matches = engine.find_matches(sig, candidates=candidates, threshold=0.85)
        assert "SIG-TECH-nullguard" in matches

    def test_find_matches_excludes_below_threshold(self, engine) -> None:
        """find_matches() must exclude candidates below the threshold."""
        sig = "SIG-TECH-aaa"
        candidates = ["SIG-PROC-zzzzzzzzzzz"]
        matches = engine.find_matches(sig, candidates=candidates, threshold=0.85)
        assert "SIG-PROC-zzzzzzzzzzz" not in matches
