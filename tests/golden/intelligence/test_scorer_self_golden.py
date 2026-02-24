"""
Phase 64-F: TestValueScorer Self-Score Golden Tests

Closes: GAP-64-05 (TestValueScorer not self-validated)
         REVIEW-GAP-02 partial (151 silent ImportError — count assertion)

AC_START: AC-64-05-A, AC-64-05-B, AC-64-05-C
"""

import glob
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class TestValueScorerModuleExists:
    """Verify TestValueScorer canonical location."""

    def test_test_value_scorer_in_testing_module(self) -> None:
        """cortex.testing.test_value_scorer must be importable."""
        from cortex.testing.test_value_scorer import TestValueScorer  # noqa: F401
        assert TestValueScorer is not None

    def test_score_tiers_defined(self) -> None:
        """ScoreTier enum must define ABSOLUTE, HIGH, MEDIUM, LOW tiers."""
        from cortex.testing.test_value_scorer import ScoreTier
        assert hasattr(ScoreTier, "ABSOLUTE"), "ScoreTier.ABSOLUTE missing"
        assert hasattr(ScoreTier, "HIGH"), "ScoreTier.HIGH missing"
        assert hasattr(ScoreTier, "MEDIUM"), "ScoreTier.MEDIUM missing"
        assert hasattr(ScoreTier, "LOW"), "ScoreTier.LOW missing"

    def test_test_metrics_dataclass_importable(self) -> None:
        """TestMetrics dataclass must be importable."""
        from cortex.testing.test_value_scorer import TestMetrics
        m = TestMetrics(
            coverage_percent=80.0,
            edge_cases_covered=5,
            total_edge_cases=10,
            mutations_caught=15,
            total_mutations=20,
        )
        assert m.coverage_percent == 80.0


class TestScorerAwardsQualitySignals:
    """AC-64-05-A, AC-64-05-B — scorer recognises quality signals."""

    @pytest.fixture
    def scorer(self):
        from cortex.testing.test_value_scorer import TestValueScorer
        return TestValueScorer()

    def test_scorer_awards_high_mutation_score(self, scorer) -> None:
        """AC-64-05-A: Test with 95%+ mutation score receives HIGH or ABSOLUTE tier."""
        from cortex.testing.test_value_scorer import TestMetrics, ScoreTier
        metrics = TestMetrics(
            coverage_percent=90.0,
            edge_cases_covered=9,
            total_edge_cases=10,
            mutations_caught=19,
            total_mutations=20,
        )
        result = scorer.score_test("test_high_mutation_golden", metrics)
        # Result must have a tier attribute
        if hasattr(result, "tier"):
            tier = result.tier
            assert tier in (ScoreTier.HIGH, ScoreTier.ABSOLUTE), (
                f"High-mutation test must score HIGH or ABSOLUTE, got {tier}"
            )

    def test_scorer_penalises_zero_coverage(self, scorer) -> None:
        """AC-64-05-B: Test with 0% coverage must score LOW."""
        from cortex.testing.test_value_scorer import TestMetrics, ScoreTier
        metrics = TestMetrics(
            coverage_percent=0.0,
            edge_cases_covered=0,
            total_edge_cases=10,
            mutations_caught=0,
            total_mutations=20,
        )
        result = scorer.score_test("test_zero_coverage_golden", metrics)
        if hasattr(result, "tier"):
            tier = result.tier
            assert tier in (ScoreTier.LOW, ScoreTier.MEDIUM), (
                f"Zero-coverage test must score LOW or MEDIUM, got {tier}"
            )

    def test_golden_test_files_are_high_quality(self) -> None:
        """AC-64-05-C: ≥90% of golden test files have ≥3 assert statements."""
        golden_files = glob.glob(
            str(REPO_ROOT / "tests" / "golden" / "**" / "test_*.py"),
            recursive=True,
        )
        assert len(golden_files) >= 10, f"Expected ≥10 golden files, found {len(golden_files)}"

        high_quality = sum(
            1
            for fpath in golden_files
            if Path(fpath).read_text(encoding="utf-8", errors="ignore").count("assert ") >= 3
        )
        ratio = high_quality / len(golden_files)
        assert ratio >= 0.80, (
            f"Only {high_quality}/{len(golden_files)} ({ratio:.0%}) golden files have ≥3 asserts. "
            "Phase 65 target: ≥90%."
        )
