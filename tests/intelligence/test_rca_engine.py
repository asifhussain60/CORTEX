"""
Phase 87 — RCA Engine Tests (RED phase — CORE-008)
Tests for RCAEngine — four analysis methodologies + method selection.

AC-PHASE87-002: RCAEngine tests
CORE-008: TDD mandatory
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock


class TestRCAEngineImport:
    """Tests that RCAEngine is importable and correctly structured."""

    def test_rca_engine_is_importable(self) -> None:
        """RCAEngine must be importable from the learning module."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        assert RCAEngine is not None

    def test_rca_engine_has_analyze_five_whys(self) -> None:
        """RCAEngine must expose analyze_five_whys() method."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        assert hasattr(RCAEngine, "analyze_five_whys")

    def test_rca_engine_has_analyze_fishbone(self) -> None:
        """RCAEngine must expose analyze_fishbone() method."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        assert hasattr(RCAEngine, "analyze_fishbone")

    def test_rca_engine_has_generate_prevention_rule(self) -> None:
        """RCAEngine must expose generate_prevention_rule() method."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        assert hasattr(RCAEngine, "generate_prevention_rule")

    def test_rca_engine_has_select_methodology(self) -> None:
        """RCAEngine must expose select_methodology() for auto-selection."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        assert hasattr(RCAEngine, "select_methodology")

    def test_rca_engine_has_analyze(self) -> None:
        """RCAEngine must expose top-level analyze() that dispatches to the right methodology."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        assert hasattr(RCAEngine, "analyze")


class TestRCAEngineMethodSelection:
    """Tests for RCAEngine.select_methodology() — auto-selection based on category."""

    def test_technology_category_selects_five_whys(self) -> None:
        """TECHNOLOGY category should default to FIVE_WHYS methodology."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory, RCATemplate
        engine = RCAEngine()
        result = engine.select_methodology(RCACategory.TECHNOLOGY)
        assert result == RCATemplate.FIVE_WHYS

    def test_process_category_selects_fishbone(self) -> None:
        """PROCESS category should default to FISHBONE methodology."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory, RCATemplate
        engine = RCAEngine()
        result = engine.select_methodology(RCACategory.PROCESS)
        assert result == RCATemplate.FISHBONE

    def test_people_category_selects_fishbone(self) -> None:
        """PEOPLE category should default to FISHBONE methodology."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory, RCATemplate
        engine = RCAEngine()
        result = engine.select_methodology(RCACategory.PEOPLE)
        assert result == RCATemplate.FISHBONE

    def test_data_category_selects_causal_chain(self) -> None:
        """DATA category should default to CAUSAL_CHAIN methodology."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory, RCATemplate
        engine = RCAEngine()
        result = engine.select_methodology(RCACategory.DATA)
        assert result == RCATemplate.CAUSAL_CHAIN


class TestRCAEngineFiveWhys:
    """Tests for RCAEngine.analyze_five_whys()."""

    def test_five_whys_returns_rca_analysis(self) -> None:
        """analyze_five_whys must return an RCAAnalysis dataclass."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCAAnalysis, RCACategory
        engine = RCAEngine()
        result = engine.analyze_five_whys(
            failure_id="OPJ-test-001",
            symptom="AttributeError in response handler",
            category=RCACategory.TECHNOLOGY,
        )
        assert isinstance(result, RCAAnalysis)

    def test_five_whys_sets_methodology_correctly(self) -> None:
        """analyze_five_whys must set methodology=FIVE_WHYS."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory, RCATemplate
        engine = RCAEngine()
        result = engine.analyze_five_whys(
            failure_id="OPJ-test-002",
            symptom="Test failure on async endpoint",
            category=RCACategory.TECHNOLOGY,
        )
        assert result.methodology == RCATemplate.FIVE_WHYS

    def test_five_whys_analysis_data_has_whys_key(self) -> None:
        """analyze_five_whys analysis_data must contain 'whys' list."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory
        engine = RCAEngine()
        result = engine.analyze_five_whys(
            failure_id="OPJ-test-003",
            symptom="NullPointerException on startup",
            category=RCACategory.TECHNOLOGY,
        )
        assert "whys" in result.analysis_data
        assert isinstance(result.analysis_data["whys"], list)

    def test_five_whys_assigns_unique_id(self) -> None:
        """analyze_five_whys must assign a non-empty id starting with 'RCA-'."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory
        engine = RCAEngine()
        result = engine.analyze_five_whys(
            failure_id="OPJ-test-004",
            symptom="Import error on module load",
            category=RCACategory.TECHNOLOGY,
        )
        assert result.id.startswith("RCA-")
        assert len(result.id) > 4

    def test_five_whys_sets_confidence_in_valid_range(self) -> None:
        """analyze_five_whys confidence must be between 0.0 and 1.0."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory
        engine = RCAEngine()
        result = engine.analyze_five_whys(
            failure_id="OPJ-test-005",
            symptom="Type error in handler",
            category=RCACategory.TECHNOLOGY,
        )
        assert 0.0 <= result.confidence <= 1.0


class TestRCAEngineFishbone:
    """Tests for RCAEngine.analyze_fishbone()."""

    def test_fishbone_returns_rca_analysis(self) -> None:
        """analyze_fishbone must return an RCAAnalysis dataclass."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCAAnalysis, RCACategory
        engine = RCAEngine()
        result = engine.analyze_fishbone(
            failure_id="OPJ-test-010",
            symptom="Multiple contributing factors to deployment failure",
            category=RCACategory.PROCESS,
        )
        assert isinstance(result, RCAAnalysis)

    def test_fishbone_sets_methodology_correctly(self) -> None:
        """analyze_fishbone must set methodology=FISHBONE."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory, RCATemplate
        engine = RCAEngine()
        result = engine.analyze_fishbone(
            failure_id="OPJ-test-011",
            symptom="Test environment mismatch",
            category=RCACategory.PROCESS,
        )
        assert result.methodology == RCATemplate.FISHBONE

    def test_fishbone_analysis_data_has_categories(self) -> None:
        """analyze_fishbone analysis_data must contain 'categories' dict."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory
        engine = RCAEngine()
        result = engine.analyze_fishbone(
            failure_id="OPJ-test-012",
            symptom="Build pipeline failure",
            category=RCACategory.PROCESS,
        )
        assert "categories" in result.analysis_data
        assert isinstance(result.analysis_data["categories"], dict)


class TestRCAEngineGeneratePreventionRule:
    """Tests for RCAEngine.generate_prevention_rule()."""

    def test_generate_prevention_rule_returns_prevention_rule(self) -> None:
        """generate_prevention_rule must return a PreventionRule dataclass."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import (
            RCAAnalysis, RCATemplate, RCACategory, PreventionRule
        )
        engine = RCAEngine()
        rca = RCAAnalysis(
            id="RCA-test-001",
            failure_id="OPJ-001",
            methodology=RCATemplate.FIVE_WHYS,
            category=RCACategory.TECHNOLOGY,
            root_cause="Missing async error boundary",
            confidence=0.85,
        )
        rule = engine.generate_prevention_rule(rca)
        assert isinstance(rule, PreventionRule)

    def test_generate_prevention_rule_links_to_rca(self) -> None:
        """generate_prevention_rule must set rca_id to the RCA's id."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import (
            RCAAnalysis, RCATemplate, RCACategory
        )
        engine = RCAEngine()
        rca = RCAAnalysis(
            id="RCA-test-002",
            failure_id="OPJ-002",
            methodology=RCATemplate.FIVE_WHYS,
            category=RCACategory.TECHNOLOGY,
            root_cause="Missing null check before attribute access",
            confidence=0.9,
        )
        rule = engine.generate_prevention_rule(rca)
        assert rule.rca_id == "RCA-test-002"

    def test_generate_prevention_rule_has_non_empty_rule_text(self) -> None:
        """generate_prevention_rule rule_text must be non-empty string."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import (
            RCAAnalysis, RCATemplate, RCACategory
        )
        engine = RCAEngine()
        rca = RCAAnalysis(
            id="RCA-test-003",
            failure_id="OPJ-003",
            methodology=RCATemplate.FISHBONE,
            category=RCACategory.PROCESS,
            root_cause="No CI validation of async patterns",
            confidence=0.8,
        )
        rule = engine.generate_prevention_rule(rca)
        assert isinstance(rule.rule_text, str)
        assert len(rule.rule_text) > 0

    def test_generate_prevention_rule_defaults_to_advisory(self) -> None:
        """generate_prevention_rule must default gate_level to ADVISORY for first rule."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import (
            RCAAnalysis, RCATemplate, RCACategory, GateLevel
        )
        engine = RCAEngine()
        rca = RCAAnalysis(
            id="RCA-test-004",
            failure_id="OPJ-004",
            methodology=RCATemplate.FIVE_WHYS,
            category=RCACategory.TECHNOLOGY,
            root_cause="Missing type annotation on async return",
            confidence=0.75,
        )
        rule = engine.generate_prevention_rule(rca)
        assert rule.gate_level == GateLevel.ADVISORY


class TestRCAEngineAnalyzeDispatch:
    """Tests for the top-level RCAEngine.analyze() dispatcher."""

    def test_analyze_dispatches_based_on_methodology(self) -> None:
        """analyze() with FIVE_WHYS must return an RCAAnalysis with FIVE_WHYS methodology."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory, RCATemplate
        engine = RCAEngine()
        result = engine.analyze(
            failure_id="OPJ-dispatch-001",
            symptom="Timeout error in integration test",
            category=RCACategory.TECHNOLOGY,
            methodology=RCATemplate.FIVE_WHYS,
        )
        assert result.methodology == RCATemplate.FIVE_WHYS

    def test_analyze_auto_selects_when_methodology_is_none(self) -> None:
        """analyze() with methodology=None must auto-select via select_methodology()."""
        from cortex.intelligence.learning.rca_engine import RCAEngine
        from cortex.intelligence.learning.rca_models import RCACategory
        engine = RCAEngine()
        result = engine.analyze(
            failure_id="OPJ-dispatch-002",
            symptom="Test fixture mismatch",
            category=RCACategory.DATA,
            methodology=None,
        )
        # DATA → CAUSAL_CHAIN
        from cortex.intelligence.learning.rca_models import RCATemplate
        assert result.methodology == RCATemplate.CAUSAL_CHAIN
