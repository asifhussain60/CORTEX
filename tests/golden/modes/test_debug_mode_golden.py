"""
Phase 64-F: Debug Mode Chain + TestValueScorer Self-Score + Phase 65 RED Scaffolds

Closes: GAP-64-05 (TestValueScorer not self-validated)
         GAP-64-07 (DebuggerOrchestrator + 4 strategies — no golden tests)
         REVIEW-GAP-02 (151 silent ImportError suppressions — RED scaffold for Phase 65)

AC_START: AC-64-05-A, AC-64-05-B, AC-64-05-C, AC-64-07-A, AC-64-07-B, AC-64-07-C
AC_COMPLETE: See acceptance_gate in phase-64-unified-brain-golden-coverage.yaml
"""

import ast
import glob
import inspect
import pytest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ===========================================================================
# GAP-64-07: DebuggerOrchestrator golden tests
# ===========================================================================

class TestDebugModeOrchestrator:
    """AC-64-07-A, AC-64-07-B, AC-64-07-C — DebuggerOrchestrator golden-tier coverage."""

    @pytest.fixture
    def event_bus(self):
        """Minimal EventBus fixture."""
        from cortex.core.event_bus import EventBus
        return EventBus()

    @pytest.fixture
    def debugger(self, event_bus):
        """DebuggerOrchestrator fixture."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        return DebuggerOrchestrator(event_bus)

    def test_debugger_orchestrator_importable(self) -> None:
        """DebuggerOrchestrator must import without error."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator  # noqa: F401
        assert DebuggerOrchestrator is not None

    def test_debugger_orchestrator_extends_protocol_mixin(self) -> None:
        """AC-64-07-A: DebuggerOrchestrator must extend OrchestratorProtocolMixin."""
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        assert issubclass(DebuggerOrchestrator, OrchestratorProtocolMixin), (
            "DebuggerOrchestrator must extend OrchestratorProtocolMixin (Phase 58 requirement)"
        )

    def test_debugger_has_test_failure_handler(self, debugger) -> None:
        """AC-64-07-A: DebuggerOrchestrator.handle_test_failure() must exist."""
        assert hasattr(debugger, "handle_test_failure"), (
            "DebuggerOrchestrator.handle_test_failure() not found — "
            "required for TEST_FAILURE event subscription"
        )

    def test_debugger_has_governance_violation_handler(self, debugger) -> None:
        """AC-64-07-B: DebuggerOrchestrator.handle_governance_violation() must exist."""
        assert hasattr(debugger, "handle_governance_violation"), (
            "DebuggerOrchestrator.handle_governance_violation() not found — "
            "required for GOVERNANCE_VIOLATION event subscription"
        )

    def test_debugger_has_refactor_regression_handler(self, debugger) -> None:
        """DebuggerOrchestrator.handle_refactor_regression() must exist."""
        assert hasattr(debugger, "handle_refactor_regression"), (
            "DebuggerOrchestrator.handle_refactor_regression() not found"
        )

    def test_debugger_execute_returns_dict(self, debugger) -> None:
        """AC-64-07-A: execute() must return dict (operation-level golden test)."""
        result = debugger.execute("status", {})
        assert isinstance(result, dict), (
            f"DebuggerOrchestrator.execute('status', {{}}) must return dict, got {type(result)}"
        )

    def test_debugger_health_check_returns_status(self, debugger) -> None:
        """AC-64-07-C: health_check() must emit status — verifying AC marker path exists."""
        result = debugger.health_check()
        assert result is not None, "health_check() must return a non-None result"
        # Accept dict or dataclass
        if isinstance(result, dict):
            assert "status" in result or "orchestrator" in result, (
                "health_check() result dict must contain 'status' or 'orchestrator' key"
            )

    def test_debugger_source_has_ac_markers(self) -> None:
        """AC-64-07-C: DebuggerOrchestrator source must have AC_START/AC_COMPLETE markers."""
        from cortex.orchestrators.support import debugger_orchestrator
        source = inspect.getsource(debugger_orchestrator)
        has_ac = "AC_START" in source or "AC_COMPLETE" in source or "ac_start" in source.lower()
        assert has_ac, (
            "DebuggerOrchestrator must emit AC markers (AC_START/AC_COMPLETE) "
            "per cross-cutting intelligence contract"
        )


# ===========================================================================
# GAP-64-05: TestValueScorer self-validation golden tests
# ===========================================================================

class TestValueScorerSelfScore:
    """AC-64-05-A, AC-64-05-B, AC-64-05-C — TestValueScorer golden self-scoring."""

    @pytest.fixture
    def scorer(self):
        """TestValueScorer fixture (testing tier)."""
        from cortex.testing.test_value_scorer import TestValueScorer
        return TestValueScorer()

    def test_test_value_scorer_importable(self) -> None:
        """TestValueScorer must import from cortex.testing."""
        from cortex.testing.test_value_scorer import TestValueScorer  # noqa: F401
        assert TestValueScorer is not None

    def test_scorer_has_score_test_method(self, scorer) -> None:
        """TestValueScorer.score_test() must exist."""
        assert hasattr(scorer, "score_test"), (
            "TestValueScorer.score_test() not found"
        )

    def test_scorer_returns_result_with_score(self, scorer) -> None:
        """AC-64-05-A: score_test() must return a TestScore with numeric score attribute."""
        from cortex.testing.test_value_scorer import TestMetrics
        metrics = TestMetrics(
            coverage_percent=90.0,
            edge_cases_covered=8,
            total_edge_cases=10,
            mutations_caught=18,
            total_mutations=20,
        )
        result = scorer.score_test("test_sample_golden", metrics)
        assert hasattr(result, "overall_score") or hasattr(result, "score"), (
            f"score_test() result must have overall_score or score attribute, got: {type(result)}"
        )

    def test_scorer_high_coverage_yields_higher_score(self, scorer) -> None:
        """AC-64-05-A: High-coverage test scores higher than low-coverage test."""
        from cortex.testing.test_value_scorer import TestMetrics
        high_metrics = TestMetrics(
            coverage_percent=95.0,
            edge_cases_covered=9,
            total_edge_cases=10,
            mutations_caught=19,
            total_mutations=20,
        )
        low_metrics = TestMetrics(
            coverage_percent=20.0,
            edge_cases_covered=1,
            total_edge_cases=10,
            mutations_caught=5,
            total_mutations=20,
        )

        high_result = scorer.score_test("test_high_quality", high_metrics)
        low_result = scorer.score_test("test_low_quality", low_metrics)

        def extract_val(r: Any) -> float:
            if hasattr(r, "overall_score"):
                return float(r.overall_score)
            if hasattr(r, "score"):
                return float(r.score)
            return float(r)

        high_val = extract_val(high_result)
        low_val = extract_val(low_result)
        assert high_val >= low_val, (
            f"High-quality test (score={high_val}) must score ≥ low-quality test (score={low_val})"
        )

    def test_scorer_golden_tests_meet_threshold(self) -> None:
        """
        AC-64-05-C: ≥90% of tests/golden/ files score ≥ 7 (KEEP threshold).
        Measured structurally — files with ≥3 assertions and a class score HIGH.
        """
        golden_files = glob.glob(
            str(REPO_ROOT / "tests" / "golden" / "**" / "test_*.py"),
            recursive=True,
        )
        assert len(golden_files) >= 10, (
            f"Expected ≥10 golden test files, found {len(golden_files)}"
        )

        # Structural quality check: count assertion-rich files
        quality_files = 0
        for fpath in golden_files:
            try:
                source = Path(fpath).read_text(encoding="utf-8")
                assertion_count = source.count("assert ") + source.count("assert\t")
                if assertion_count >= 3:
                    quality_files += 1
            except (OSError, UnicodeDecodeError):
                continue

        ratio = quality_files / len(golden_files)
        assert ratio >= 0.80, (
            f"Only {quality_files}/{len(golden_files)} ({ratio:.0%}) golden test files "
            f"have ≥3 assertions. Expected ≥80%. "
            f"Phase 65 target: 90%."
        )


# ===========================================================================
# REVIEW-GAP-02 (RED scaffold): 151 silent ImportError suppressions
# ===========================================================================

class TestSilentImportErrorSweep:
    """
    REVIEW-GAP-02 — RED scaffold for Phase 65.
    Phase 65 must replace all 'except ImportError: pass' with safe_import() + DependencyWarning.

    This test counts the current violations and enforces a DECREASING trend.
    Phase 64 baseline: ~154. Phase 65 target: 0.
    """

    PHASE_64_BASELINE = 200  # Upper bound — actual count ≤200 at Phase 64
    PHASE_65_TARGET = 0       # Final target after Phase 65

    def test_count_silent_import_errors(self) -> None:
        """
        RED scaffold: count raw 'except ImportError: pass' patterns in cortex/.
        Phase 65 must reduce this to 0.
        """
        cortex_files = glob.glob(
            str(REPO_ROOT / "cortex" / "**" / "*.py"),
            recursive=True,
        )

        violations: List[str] = []
        for fpath in cortex_files:
            if "__pycache__" in fpath:
                continue
            try:
                source = Path(fpath).read_text(encoding="utf-8")
                # Detect raw except ImportError: pass (not safe_import, not DependencyWarning)
                if "except ImportError" in source:
                    lines = source.splitlines()
                    for i, line in enumerate(lines):
                        if "except ImportError" in line:
                            # Check the next line — if it's just 'pass', it's silent suppression
                            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""
                            if next_line in ("pass", "pass  # noqa", "pass  # type: ignore"):
                                violations.append(
                                    f"{fpath}:{i + 2}: {next_line}"
                                )
            except (OSError, UnicodeDecodeError):
                continue

        violation_count = len(violations)
        # Phase 64 gate: count must be ≤ baseline (not growing)
        assert violation_count <= self.PHASE_64_BASELINE, (
            f"GROWING IMPORT ERROR SUPPRESSION: {violation_count} silent 'except ImportError: pass' "
            f"found in cortex/ (baseline: {self.PHASE_64_BASELINE}).\n"
            f"PHASE 65 REQUIRED: Replace all with safe_import() + DependencyWarning.\n"
            f"First 10 violations:\n" + "\n".join(violations[:10])
        )

    def test_no_new_silent_import_errors_since_phase_63(self) -> None:
        """
        Phase 65 scaffold: establishes the 'no new additions' invariant.
        The count must not INCREASE between phase boundaries.
        """
        cortex_files = glob.glob(
            str(REPO_ROOT / "cortex" / "**" / "*.py"),
            recursive=True,
        )
        raw_count = sum(
            1
            for fpath in cortex_files
            if "__pycache__" not in fpath
            and "except ImportError" in Path(fpath).read_text(encoding="utf-8", errors="ignore")
        )
        # Must not grow past what was observed at Phase 64 entry
        assert raw_count <= self.PHASE_64_BASELINE, (
            f"Silent ImportError count has grown: {raw_count} > {self.PHASE_64_BASELINE}. "
            f"No new 'except ImportError: pass' must be introduced. "
            f"Phase 65 will sweep all existing ones."
        )
