"""
Phase 86 — GAP-86-08: MarkerInjectionEngine strategy registration tests.

Verifies that all 8 strategies (3 existing + 5 new multi-stack) are registered
in MarkerInjectionEngine.strategies after __init__.

CORE-008: TDD — these tests were written before the wiring edit.
"""

import pytest
from cortex.orchestrators.support.debugging.marker_injection_engine import MarkerInjectionEngine


class TestMarkerInjectionEnginePhase86Registration:
    """Verify all 8 strategy keys are present after Phase 86 wiring."""

    def setup_method(self) -> None:
        self.engine = MarkerInjectionEngine()

    # ── Existing strategies (regression guard) ────────────────────────────
    def test_test_failure_strategy_registered(self) -> None:
        assert "test_failure" in self.engine.strategies

    def test_refactor_regression_strategy_registered(self) -> None:
        assert "refactor_regression" in self.engine.strategies

    def test_governance_violation_strategy_registered(self) -> None:
        assert "governance_violation" in self.engine.strategies

    # ── Phase 86 new strategies ───────────────────────────────────────────
    def test_frontend_console_strategy_registered(self) -> None:
        assert "frontend_console" in self.engine.strategies

    def test_html_vision_mapping_strategy_registered(self) -> None:
        assert "html_vision_mapping" in self.engine.strategies

    def test_api_trace_strategy_registered(self) -> None:
        assert "api_trace" in self.engine.strategies

    def test_sql_trace_strategy_registered(self) -> None:
        assert "sql_trace" in self.engine.strategies

    def test_dotnet_trace_strategy_registered(self) -> None:
        assert "dotnet_trace" in self.engine.strategies

    # ── Total count ───────────────────────────────────────────────────────
    def test_total_strategy_count_is_eight(self) -> None:
        """Engine must expose exactly 8 strategies after Phase 86."""
        assert len(self.engine.strategies) == 8

    # ── All registered values satisfy AbstractInjectionStrategy interface ─
    def test_all_strategies_have_analyze_method(self) -> None:
        for key, strategy in self.engine.strategies.items():
            assert callable(getattr(strategy, "analyze", None)), (
                f"Strategy '{key}' missing analyze()"
            )

    def test_all_strategies_have_format_marker_method(self) -> None:
        for key, strategy in self.engine.strategies.items():
            assert callable(getattr(strategy, "format_marker", None)), (
                f"Strategy '{key}' missing format_marker()"
            )
