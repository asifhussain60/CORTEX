"""Tests — ROI Calculator + Sprint Capacity Calculator (GAP-129-04, GAP-129-10)."""

from __future__ import annotations

import pytest

from cortex.intelligence.po.roi_calculator import ROICalculator
from cortex.intelligence.po.sprint_capacity_calculator import SprintCapacityCalculator


# ─────────────────────────────────────────────────────────────────────────────
# ROICalculator — WSJF ranking
# ─────────────────────────────────────────────────────────────────────────────


FEATURES = [
    {"name": "Login", "business_value": 10, "time_criticality": 8, "rr_oe": 5, "job_size": 3},
    {"name": "Dashboard", "business_value": 5, "time_criticality": 3, "rr_oe": 2, "job_size": 8},
    {"name": "Export", "business_value": 8, "time_criticality": 6, "rr_oe": 4, "job_size": 2},
]


class TestROICalculator:
    @pytest.fixture
    def calc(self):
        return ROICalculator()

    def test_calculate_wsjf_returns_list(self, calc):
        result = calc.calculate_wsjf(FEATURES)
        assert isinstance(result, list)
        assert len(result) == len(FEATURES)

    def test_calculate_wsjf_adds_score(self, calc):
        result = calc.calculate_wsjf(FEATURES)
        for item in result:
            assert "wsjf_score" in item
            assert item["wsjf_score"] >= 0

    def test_calculate_wsjf_sorted_descending(self, calc):
        result = calc.calculate_wsjf(FEATURES)
        scores = [r["wsjf_score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_calculate_wsjf_formula(self, calc):
        # Export: CoD = 8+6+4 = 18, job_size=2 → WSJF=9.0
        result = calc.calculate_wsjf(FEATURES)
        export = next(r for r in result if r["name"] == "Export")
        assert export["wsjf_score"] == pytest.approx(9.0)

    def test_rank_returns_names_in_order(self, calc):
        names = calc.rank(FEATURES)
        assert isinstance(names, list)
        assert names[0] == "Export"  # highest WSJF

    def test_top_n_returns_at_most_n(self, calc):
        result = calc.top_n(FEATURES, n=2)
        assert len(result) == 2

    def test_top_n_first_is_highest_wsjf(self, calc):
        result = calc.top_n(FEATURES, n=1)
        assert result[0]["name"] == "Export"

    def test_job_size_zero_does_not_divide_by_zero(self, calc):
        features = [{"name": "A", "business_value": 5, "time_criticality": 5, "rr_oe": 5, "job_size": 0}]
        result = calc.calculate_wsjf(features)
        assert result[0]["wsjf_score"] == pytest.approx(15.0)  # job_size coerced to 1

    def test_empty_features_returns_empty_list(self, calc):
        assert calc.calculate_wsjf([]) == []

    def test_cost_of_delay_included_in_result(self, calc):
        result = calc.calculate_wsjf(FEATURES)
        for item in result:
            assert "cost_of_delay" in item


# ─────────────────────────────────────────────────────────────────────────────
# SprintCapacityCalculator
# ─────────────────────────────────────────────────────────────────────────────


TEAM = [
    {"name": "Alice", "available_days": 10, "focus_factor": 0.8},
    {"name": "Bob",   "available_days":  8, "focus_factor": 0.9},
]


class TestSprintCapacityCalculator:
    @pytest.fixture
    def calc(self):
        return SprintCapacityCalculator()

    def test_returns_dict_with_required_keys(self, calc):
        result = calc.calculate(TEAM, velocity_baseline=30.0)
        assert "committed_points" in result
        assert "confidence_interval" in result
        assert "available_days" in result
        assert "capacity_ratio" in result

    def test_committed_points_is_positive(self, calc):
        result = calc.calculate(TEAM, velocity_baseline=30.0)
        assert result["committed_points"] > 0

    def test_confidence_interval_is_tuple_or_list(self, calc):
        result = calc.calculate(TEAM, velocity_baseline=30.0)
        ci = result["confidence_interval"]
        assert len(ci) == 2
        assert ci[0] <= ci[1]

    def test_ci_lower_bound_non_negative(self, calc):
        result = calc.calculate(TEAM, velocity_baseline=5.0)
        assert result["confidence_interval"][0] >= 0

    def test_uses_velocity_history_for_ci(self, calc):
        result_no_history = calc.calculate(TEAM, velocity_baseline=30.0)
        result_with_history = calc.calculate(
            TEAM, velocity_baseline=30.0, velocity_history=[25.0, 30.0, 35.0, 28.0]
        )
        # Both should have confidence intervals — just verify structure
        assert len(result_no_history["confidence_interval"]) == 2
        assert len(result_with_history["confidence_interval"]) == 2

    def test_full_availability_equals_baseline(self, calc):
        full_team = [{"name": "A", "available_days": 10, "focus_factor": 1.0}]
        result = calc.calculate(full_team, velocity_baseline=20.0, sprint_days=10)
        assert result["committed_points"] == pytest.approx(20.0)

    def test_half_availability_halves_committed(self, calc):
        half_team = [{"name": "A", "available_days": 5, "focus_factor": 1.0}]
        result = calc.calculate(half_team, velocity_baseline=20.0, sprint_days=10)
        assert result["committed_points"] == pytest.approx(10.0)

    def test_zero_velocity_baseline_returns_zero(self, calc):
        result = calc.calculate(TEAM, velocity_baseline=0.0)
        assert result["committed_points"] == 0.0

    def test_capacity_ratio_between_zero_and_one(self, calc):
        result = calc.calculate(TEAM, velocity_baseline=30.0)
        assert 0.0 <= result["capacity_ratio"] <= 1.0
