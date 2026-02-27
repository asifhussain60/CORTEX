"""
Phase 87 — RCA Memory Engine Tests (RED phase — CORE-008)
Tests for RCAAnalysis dataclass, RCATemplate enum, RCACategory enum.

AC-PHASE87-001: RCA model tests
CORE-008: TDD mandatory — RED phase (all tests fail before implementation)
CORE-011: Type hints on all test functions
CORE-012: Docstrings on all test functions
"""

from __future__ import annotations

import pytest


class TestRCATemplate:
    """Tests for RCATemplate enum — four analysis methodologies."""

    def test_rca_template_has_five_whys(self) -> None:
        """RCATemplate must include FIVE_WHYS methodology."""
        from cortex.intelligence.learning.rca_models import RCATemplate
        assert RCATemplate.FIVE_WHYS is not None

    def test_rca_template_has_fishbone(self) -> None:
        """RCATemplate must include FISHBONE (Ishikawa) methodology."""
        from cortex.intelligence.learning.rca_models import RCATemplate
        assert RCATemplate.FISHBONE is not None

    def test_rca_template_has_fault_tree(self) -> None:
        """RCATemplate must include FAULT_TREE methodology."""
        from cortex.intelligence.learning.rca_models import RCATemplate
        assert RCATemplate.FAULT_TREE is not None

    def test_rca_template_has_causal_chain(self) -> None:
        """RCATemplate must include CAUSAL_CHAIN methodology."""
        from cortex.intelligence.learning.rca_models import RCATemplate
        assert RCATemplate.CAUSAL_CHAIN is not None

    def test_rca_template_has_exactly_four_values(self) -> None:
        """RCATemplate must have exactly 4 methodologies — no more, no less."""
        from cortex.intelligence.learning.rca_models import RCATemplate
        assert len(list(RCATemplate)) == 4


class TestRCACategory:
    """Tests for RCACategory enum — four failure categories."""

    def test_rca_category_has_technology(self) -> None:
        """RCACategory must include TECHNOLOGY."""
        from cortex.intelligence.learning.rca_models import RCACategory
        assert RCACategory.TECHNOLOGY is not None

    def test_rca_category_has_process(self) -> None:
        """RCACategory must include PROCESS."""
        from cortex.intelligence.learning.rca_models import RCACategory
        assert RCACategory.PROCESS is not None

    def test_rca_category_has_people(self) -> None:
        """RCACategory must include PEOPLE."""
        from cortex.intelligence.learning.rca_models import RCACategory
        assert RCACategory.PEOPLE is not None

    def test_rca_category_has_data(self) -> None:
        """RCACategory must include DATA."""
        from cortex.intelligence.learning.rca_models import RCACategory
        assert RCACategory.DATA is not None

    def test_rca_category_has_exactly_four_values(self) -> None:
        """RCACategory must have exactly 4 categories."""
        from cortex.intelligence.learning.rca_models import RCACategory
        assert len(list(RCACategory)) == 4


class TestGateLevelEnum:
    """Tests for GateLevel enum — three prevention gate levels."""

    def test_gate_level_has_advisory(self) -> None:
        """GateLevel must include ADVISORY."""
        from cortex.intelligence.learning.rca_models import GateLevel
        assert GateLevel.ADVISORY is not None

    def test_gate_level_has_warning(self) -> None:
        """GateLevel must include WARNING."""
        from cortex.intelligence.learning.rca_models import GateLevel
        assert GateLevel.WARNING is not None

    def test_gate_level_has_blocking(self) -> None:
        """GateLevel must include BLOCKING."""
        from cortex.intelligence.learning.rca_models import GateLevel
        assert GateLevel.BLOCKING is not None

    def test_gate_level_has_pass(self) -> None:
        """GateLevel must include PASS (no match found)."""
        from cortex.intelligence.learning.rca_models import GateLevel
        assert GateLevel.PASS is not None


class TestRCAAnalysis:
    """Tests for RCAAnalysis dataclass."""

    def test_rca_analysis_is_dataclass(self) -> None:
        """RCAAnalysis must be importable as a dataclass."""
        from cortex.intelligence.learning.rca_models import RCAAnalysis
        import dataclasses
        assert dataclasses.is_dataclass(RCAAnalysis)

    def test_rca_analysis_has_required_fields(self) -> None:
        """RCAAnalysis must have id, failure_id, methodology, category, root_cause, confidence."""
        from cortex.intelligence.learning.rca_models import RCAAnalysis, RCATemplate, RCACategory
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RCAAnalysis)}
        required = {"id", "failure_id", "methodology", "category", "root_cause", "confidence"}
        assert required.issubset(field_names), f"Missing fields: {required - field_names}"

    def test_rca_analysis_can_be_constructed(self) -> None:
        """RCAAnalysis must be constructable with required fields."""
        from cortex.intelligence.learning.rca_models import RCAAnalysis, RCATemplate, RCACategory
        rca = RCAAnalysis(
            id="RCA-test-001",
            failure_id="OPJ-failure-001",
            methodology=RCATemplate.FIVE_WHYS,
            category=RCACategory.TECHNOLOGY,
            root_cause="Missing async error boundary in response handler",
            confidence=0.85,
        )
        assert rca.id == "RCA-test-001"
        assert rca.methodology == RCATemplate.FIVE_WHYS
        assert rca.confidence == 0.85

    def test_rca_analysis_has_analysis_data_field(self) -> None:
        """RCAAnalysis must have analysis_data dict for methodology-specific data."""
        from cortex.intelligence.learning.rca_models import RCAAnalysis
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RCAAnalysis)}
        assert "analysis_data" in field_names

    def test_rca_analysis_has_prevention_rule_field(self) -> None:
        """RCAAnalysis must carry an optional prevention_rule."""
        from cortex.intelligence.learning.rca_models import RCAAnalysis
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RCAAnalysis)}
        assert "prevention_rule" in field_names


class TestPreventionRule:
    """Tests for PreventionRule dataclass."""

    def test_prevention_rule_is_dataclass(self) -> None:
        """PreventionRule must be a dataclass."""
        from cortex.intelligence.learning.rca_models import PreventionRule
        import dataclasses
        assert dataclasses.is_dataclass(PreventionRule)

    def test_prevention_rule_has_required_fields(self) -> None:
        """PreventionRule must have id, rca_id, rule_text, gate_level."""
        from cortex.intelligence.learning.rca_models import PreventionRule
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PreventionRule)}
        required = {"id", "rca_id", "rule_text", "gate_level"}
        assert required.issubset(field_names)

    def test_prevention_rule_defaults_active_true(self) -> None:
        """PreventionRule must default active=True."""
        from cortex.intelligence.learning.rca_models import PreventionRule, GateLevel
        rule = PreventionRule(
            id="PREV-001",
            rca_id="RCA-001",
            rule_text="Always await before accessing .data",
            gate_level=GateLevel.ADVISORY,
        )
        assert rule.active is True


class TestPreventionGateResult:
    """Tests for PreventionGateResult dataclass."""

    def test_prevention_gate_result_is_dataclass(self) -> None:
        """PreventionGateResult must be a dataclass."""
        from cortex.intelligence.learning.rca_models import PreventionGateResult
        import dataclasses
        assert dataclasses.is_dataclass(PreventionGateResult)

    def test_prevention_gate_result_has_gate_level(self) -> None:
        """PreventionGateResult must carry a gate_level."""
        from cortex.intelligence.learning.rca_models import PreventionGateResult
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PreventionGateResult)}
        assert "gate_level" in field_names

    def test_prevention_gate_result_has_matched_rule(self) -> None:
        """PreventionGateResult must carry optional matched_rule."""
        from cortex.intelligence.learning.rca_models import PreventionGateResult
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PreventionGateResult)}
        assert "matched_rule" in field_names
