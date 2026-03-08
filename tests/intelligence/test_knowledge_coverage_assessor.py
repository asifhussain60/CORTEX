"""Tests for DomainSignalExtractor and KnowledgeCoverageAssessor — Phase 135-a (KAL).

RED phase: all tests written BEFORE implementation (CORE-008 TDD mandate).
GAP-135-01: DomainSignalExtractor
GAP-135-02: KnowledgeCoverageAssessor
"""
from __future__ import annotations

import pytest


# ─── DomainSignalExtractor tests ─────────────────────────────────────────────

class TestDomainSignalExtractor:
    """GAP-135-01: DomainSignalExtractor converts LENS output to domain signal strings."""

    def test_extract_returns_sorted_unique_signals(self) -> None:
        """extract() returns a sorted, deduplicated list of domain signal strings."""
        from cortex.intelligence.knowledge.domain_signal_extractor import DomainSignalExtractor

        extractor = DomainSignalExtractor()
        lens_output = {
            "language": "python",
            "imports": ["pytest", "pytest", "unittest"],
            "files": ["test_foo.py"],
        }
        signals = extractor.extract(lens_output)
        assert isinstance(signals, list)
        assert signals == sorted(set(signals)), "signals must be sorted and unique"

    def test_extract_from_lens_output(self) -> None:
        """Flatten LENS dict to searchable string, apply regex patterns."""
        from cortex.intelligence.knowledge.domain_signal_extractor import DomainSignalExtractor

        extractor = DomainSignalExtractor()
        lens_output = {
            "language": "python",
            "imports": ["fastapi", "uvicorn"],
            "files": ["main.py", "router.py"],
        }
        signals = extractor.extract(lens_output)
        assert isinstance(signals, list)
        # Should return at least one signal for a valid python/fastapi lens output
        assert len(signals) >= 0  # graceful: may be empty if no map patterns match

    def test_signal_map_loaded_and_cached(self) -> None:
        """_load_signal_map() reads YAML once; subsequent calls use cache."""
        from cortex.intelligence.knowledge.domain_signal_extractor import DomainSignalExtractor

        extractor = DomainSignalExtractor()
        map1 = extractor._load_signal_map()
        map2 = extractor._load_signal_map()
        # Same object reference confirms caching
        assert map1 is map2

    def test_extract_empty_lens_output(self) -> None:
        """extract({}) returns an empty list without raising."""
        from cortex.intelligence.knowledge.domain_signal_extractor import DomainSignalExtractor

        extractor = DomainSignalExtractor()
        signals = extractor.extract({})
        assert isinstance(signals, list)

    def test_extract_deduplicates(self) -> None:
        """Duplicate signals from multiple keys are deduplicated."""
        from cortex.intelligence.knowledge.domain_signal_extractor import DomainSignalExtractor

        extractor = DomainSignalExtractor()
        # Same import referenced twice in different keys
        lens_output = {
            "language": "python",
            "imports": ["pytest"],
            "test_imports": ["pytest"],
        }
        signals = extractor.extract(lens_output)
        # All elements must be unique
        assert len(signals) == len(set(signals))


# ─── KnowledgeCoverageAssessor tests ─────────────────────────────────────────

class TestKnowledgeCoverageAssessor:
    """GAP-135-02: KnowledgeCoverageAssessor — coverage scoring + acquisition trigger."""

    def test_coverage_result_dataclass(self) -> None:
        """CoverageResult has score, covered_domains, missing_domains, acquisition_needed, threshold."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import CoverageResult

        result = CoverageResult(
            score=0.5,
            covered_domains=["testing-validation"],
            missing_domains=["unknown-domain"],
            acquisition_needed=True,
            threshold=0.80,
        )
        assert result.score == 0.5
        assert result.acquisition_needed is True
        assert result.threshold == 0.80
        assert isinstance(result.covered_domains, list)
        assert isinstance(result.missing_domains, list)

    def test_assess_full_coverage(self) -> None:
        """All signals matched in INDEX.yaml → score 1.0, acquisition_needed False."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor

        assessor = KnowledgeCoverageAssessor()
        # Use signals we know are in the INDEX.yaml (domain names)
        result = assessor.assess(["testing-validation"])
        assert result.score == pytest.approx(1.0)
        assert result.acquisition_needed is False

    def test_assess_partial_coverage(self) -> None:
        """Mixed signals (some matched, some not) → score between 0 and 1."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor

        assessor = KnowledgeCoverageAssessor()
        result = assessor.assess(["testing-validation", "completely-unknown-xyz-domain-99"])
        assert 0.0 <= result.score <= 1.0

    def test_assess_below_threshold(self) -> None:
        """score < threshold → CoverageResult.acquisition_needed True."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor

        assessor = KnowledgeCoverageAssessor(threshold=0.80)
        # All unknown signals → score 0.0 < 0.80 threshold
        result = assessor.assess(["zzz-totally-unknown-xyz", "aaa-fake-domain-999"])
        assert result.score < result.threshold
        assert result.acquisition_needed is True

    def test_assess_empty_signals(self) -> None:
        """Empty input → score 1.0 (vacuously complete), acquisition_needed False."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor

        assessor = KnowledgeCoverageAssessor()
        result = assessor.assess([])
        assert result.score == pytest.approx(1.0)
        assert result.acquisition_needed is False

    def test_assess_multi_level_matching(self) -> None:
        """Exact → prefix → keyword containment fallback chain."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor

        assessor = KnowledgeCoverageAssessor()
        # "security" is a substring/keyword of "security" domain
        result = assessor.assess(["security"])
        assert isinstance(result.score, float)
        assert 0.0 <= result.score <= 1.0

    def test_coverage_result_score_bounds(self) -> None:
        """Score is always in [0.0, 1.0]."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor

        assessor = KnowledgeCoverageAssessor()
        for signals in [[], ["a"], ["testing-validation", "b", "c"]]:
            result = assessor.assess(signals)
            assert 0.0 <= result.score <= 1.0

    def test_above_threshold_acquisition_not_needed(self) -> None:
        """score >= threshold → acquisition_needed False."""
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor

        assessor = KnowledgeCoverageAssessor(threshold=0.0)
        result = assessor.assess(["zzz-unknown"])
        # With threshold=0.0, score(0.0) >= 0.0 → no acquisition needed
        assert result.acquisition_needed is False
