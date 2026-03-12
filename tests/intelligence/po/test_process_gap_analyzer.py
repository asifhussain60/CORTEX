"""Tests — Process Gap Analyzer + Change Recommendation Engine + Risk Register."""

from __future__ import annotations

import pytest

from cortex.intelligence.po.change_recommendation_engine import ChangeRecommendationEngine
from cortex.intelligence.po.process_gap_analyzer import ProcessGapAnalyzer
from cortex.intelligence.po.risk_register import RiskRegister


# ─────────────────────────────────────────────────────────────────────────────
# ProcessGapAnalyzer
# ─────────────────────────────────────────────────────────────────────────────


class TestProcessGapAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return ProcessGapAnalyzer()

    def test_analyze_returns_three_categories(self, analyzer):
        result = analyzer.analyze([])
        assert set(result.keys()) == {"scope_creep", "cycle_time_spikes", "recurring_blocked"}

    def test_detects_scope_creep(self, analyzer):
        items = [
            {
                "story_id": "1", "title": "Feature A",
                "sprint_added_at": "2026-03-15T10:00:00",
                "sprint_started_at": "2026-03-10T09:00:00",
            }
        ]
        result = analyzer.analyze(items)
        assert len(result["scope_creep"]) == 1

    def test_no_scope_creep_if_added_before_sprint(self, analyzer):
        items = [
            {
                "story_id": "1", "title": "Feature A",
                "sprint_added_at": "2026-03-09T10:00:00",
                "sprint_started_at": "2026-03-10T09:00:00",
            }
        ]
        result = analyzer.analyze(items)
        assert len(result["scope_creep"]) == 0

    def test_detects_cycle_time_spikes(self, analyzer):
        items = [
            {"story_id": "1", "title": "A", "cycle_time_days": 2.0},
            {"story_id": "2", "title": "B", "cycle_time_days": 2.0},
            {"story_id": "3", "title": "C", "cycle_time_days": 10.0},  # spike: 10 > 2×2
        ]
        result = analyzer.analyze(items)
        assert len(result["cycle_time_spikes"]) == 1
        assert result["cycle_time_spikes"][0]["story_id"] == "3"

    def test_no_spike_if_all_similar(self, analyzer):
        items = [
            {"story_id": "1", "title": "A", "cycle_time_days": 3.0},
            {"story_id": "2", "title": "B", "cycle_time_days": 3.0},
        ]
        result = analyzer.analyze(items)
        assert len(result["cycle_time_spikes"]) == 0

    def test_detects_recurring_blocked_multi_sprint(self, analyzer):
        items = [
            {"story_id": "1", "title": "blocked feature", "description": "", "tags": "", "sprint_id": "S1"},
            {"story_id": "2", "title": "impediment story", "description": "", "tags": "", "sprint_id": "S2"},
        ]
        result = analyzer.analyze(items)
        assert len(result["recurring_blocked"]) == 2

    def test_summary_returns_counts(self, analyzer):
        counts = analyzer.summary([])
        assert isinstance(counts, dict)
        assert all(isinstance(v, int) for v in counts.values())

    def test_detects_at_least_three_anti_pattern_categories(self, analyzer):
        result = analyzer.analyze([])
        assert len(result) >= 3


# ─────────────────────────────────────────────────────────────────────────────
# ChangeRecommendationEngine
# ─────────────────────────────────────────────────────────────────────────────


class TestChangeRecommendationEngine:
    @pytest.fixture
    def engine(self):
        return ChangeRecommendationEngine()

    def test_evaluate_returns_required_keys(self, engine):
        result = engine.evaluate(
            {"name": "Feature X", "effort_points": 2},
            {"committed_points": 20},
        )
        assert "verdict" in result
        assert "justification" in result
        assert "score" in result
        assert "details" in result

    def test_accept_verdict_with_plenty_of_capacity(self, engine):
        result = engine.evaluate(
            {"name": "Tiny fix", "effort_points": 1, "blocking_dependencies": 0},
            {"committed_points": 30},
            risk_register={"high_risks": 0},
        )
        assert result["verdict"] == "ACCEPT"

    def test_reject_verdict_when_capacity_zero(self, engine):
        result = engine.evaluate(
            {"name": "Big feature", "effort_points": 100},
            {"committed_points": 0},
            risk_register={"high_risks": 5},
        )
        assert result["verdict"] == "REJECT"

    def test_defer_verdict_for_borderline_case(self, engine):
        result = engine.evaluate(
            {"name": "Medium feature", "effort_points": 8, "blocking_dependencies": 2},
            {"committed_points": 10},
            risk_register={"high_risks": 1},
        )
        # With tight capacity and deps, should be DEFER or REJECT
        assert result["verdict"] in {"DEFER", "REJECT"}

    def test_verdict_is_valid_enum(self, engine):
        result = engine.evaluate({"name": "X"}, {"committed_points": 10})
        assert result["verdict"] in {"ACCEPT", "DEFER", "REJECT"}

    def test_justification_is_nonempty_string(self, engine):
        result = engine.evaluate({"name": "X"}, {"committed_points": 10})
        assert isinstance(result["justification"], str)
        assert len(result["justification"]) > 10

    def test_score_is_numeric_in_range(self, engine):
        result = engine.evaluate({"name": "X", "effort_points": 3}, {"committed_points": 20})
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 100.0

    def test_details_has_three_score_components(self, engine):
        result = engine.evaluate({"name": "X"}, {"committed_points": 10})
        assert "capacity_score" in result["details"]
        assert "dependency_score" in result["details"]
        assert "risk_score" in result["details"]


# ─────────────────────────────────────────────────────────────────────────────
# RiskRegister
# ─────────────────────────────────────────────────────────────────────────────


class TestRiskRegister:
    @pytest.fixture
    def register(self):
        return RiskRegister()

    def test_scan_returns_list(self, register):
        result = register.scan([])
        assert isinstance(result, list)

    def test_detects_blocked_keyword(self, register):
        items = [{"story_id": "1", "title": "blocked item", "description": "", "tags": ""}]
        result = register.scan(items)
        assert len(result) > 0

    def test_detects_compliance_keyword(self, register):
        items = [{"story_id": "2", "title": "GDPR compliance", "description": "", "tags": ""}]
        result = register.scan(items)
        assert any(r["risk_signal"] == "compliance_tag" for r in result)

    def test_detects_security_concern(self, register):
        items = [{"story_id": "3", "title": "Auth permission check", "description": "", "tags": ""}]
        result = register.scan(items)
        assert any(r["risk_signal"] == "security_concern" for r in result)

    def test_scan_result_has_required_keys(self, register):
        items = [{"story_id": "1", "title": "blocked", "description": "", "tags": ""}]
        result = register.scan(items)
        for entry in result:
            assert {"story_id", "title", "risk_signal", "likelihood", "impact", "score", "level"}.issubset(entry.keys())

    def test_score_is_likelihood_times_impact(self, register):
        items = [{"story_id": "1", "title": "blocked", "description": "", "tags": ""}]
        result = register.scan(items)
        for entry in result:
            assert entry["score"] == entry["likelihood"] * entry["impact"]

    def test_results_sorted_by_score_descending(self, register):
        items = [
            {"story_id": "1", "title": "blocked gdpr security compliance vendor", "description": "", "tags": "compliance urgent"},
        ]
        result = register.scan(items)
        scores = [r["score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_high_risk_count_returns_int(self, register):
        count = register.high_risk_count([])
        assert isinstance(count, int)

    def test_summary_has_level_keys(self, register):
        summary = register.summary([])
        assert "HIGH" in summary
        assert "MEDIUM" in summary
        assert "LOW" in summary
        assert "total" in summary

    def test_level_classification_high(self, register):
        assert register._level(15) == "HIGH"
        assert register._level(25) == "HIGH"

    def test_level_classification_medium(self, register):
        assert register._level(6) == "MEDIUM"
        assert register._level(14) == "MEDIUM"

    def test_level_classification_low(self, register):
        assert register._level(5) == "LOW"
        assert register._level(1) == "LOW"
