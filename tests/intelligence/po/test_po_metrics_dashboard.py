"""Tests for POMetricsDashboard, FeatureDependencyGraph, ExecutiveSummaryGenerator (GAP-129-e)."""

from __future__ import annotations

import pytest

from cortex.intelligence.po.po_metrics_dashboard import POMetricsDashboard
from cortex.intelligence.po.feature_dependency_graph import FeatureDependencyGraph
from cortex.intelligence.po.executive_summary_generator import ExecutiveSummaryGenerator

# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

SPRINT_HISTORY = [
    {"sprint_name": "Sprint 1", "completed_points": 30},
    {"sprint_name": "Sprint 2", "completed_points": 35},
    {"sprint_name": "Sprint 3", "completed_points": 28},
    {"sprint_name": "Sprint 4", "completed_points": 40},
]

WORK_ITEMS = [
    {"story_id": "S-001", "title": "Login feature", "cycle_time_days": 3.0, "tags": []},
    {"story_id": "S-002", "title": "blocked by API", "cycle_time_days": 8.0, "tags": ["blocked"]},
    {"story_id": "S-003", "title": "Export report", "cycle_time_days": 2.5, "tags": []},
]

FEATURES = [
    {"id": "F-001", "name": "Authentication", "depends_on": []},
    {"id": "F-002", "name": "Dashboard", "depends_on": ["F-001"]},
    {"id": "F-003", "name": "Export", "depends_on": ["F-001", "F-002"]},
]


# ---------------------------------------------------------------------------
# POMetricsDashboard
# ---------------------------------------------------------------------------


class TestPOMetricsDashboardBuild:
    def setup_method(self) -> None:
        self.dashboard = POMetricsDashboard()

    def test_build_returns_dict(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY)
        assert isinstance(result, dict)

    def test_build_contains_velocity_trend(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY)
        assert "velocity_trend" in result
        assert isinstance(result["velocity_trend"], list)

    def test_build_velocity_trend_length(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY)
        assert len(result["velocity_trend"]) == len(SPRINT_HISTORY)

    def test_build_velocity_trend_has_sprint_and_points(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY)
        for entry in result["velocity_trend"]:
            assert "sprint" in entry
            assert "points" in entry

    def test_build_contains_cycle_time_distribution(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY, WORK_ITEMS)
        assert "cycle_time_distribution" in result
        assert isinstance(result["cycle_time_distribution"], list)

    def test_cycle_time_distribution_has_story_id_and_days(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY, WORK_ITEMS)
        for entry in result["cycle_time_distribution"]:
            assert "story_id" in entry
            assert "days" in entry

    def test_build_contains_predictability_score(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY)
        assert "predictability_score" in result

    def test_predictability_score_is_float_in_range(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY)
        score = result["predictability_score"]
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_build_contains_blocked_themes(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY, WORK_ITEMS)
        assert "blocked_themes" in result
        assert isinstance(result["blocked_themes"], list)

    def test_blocked_themes_detected_from_tags(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY, WORK_ITEMS)
        # S-002 has "blocked" tag
        assert len(result["blocked_themes"]) >= 1

    def test_build_empty_sprint_history(self) -> None:
        result = self.dashboard.build([])
        assert result["velocity_trend"] == []
        assert result["predictability_score"] == 0.0

    def test_build_single_sprint_predictability_100(self) -> None:
        result = self.dashboard.build([{"sprint_name": "Sprint 1", "completed_points": 50}])
        assert result["predictability_score"] == 100.0

    def test_build_velocity_trend_points_are_floats(self) -> None:
        result = self.dashboard.build(SPRINT_HISTORY)
        for entry in result["velocity_trend"]:
            assert isinstance(entry["points"], float)


# ---------------------------------------------------------------------------
# FeatureDependencyGraph
# ---------------------------------------------------------------------------


class TestFeatureDependencyGraphBuild:
    def setup_method(self) -> None:
        self.graph = FeatureDependencyGraph()

    def test_build_returns_dict(self) -> None:
        result = self.graph.build(FEATURES)
        assert isinstance(result, dict)

    def test_build_has_nodes_and_links(self) -> None:
        result = self.graph.build(FEATURES)
        assert "nodes" in result
        assert "links" in result

    def test_nodes_is_list(self) -> None:
        result = self.graph.build(FEATURES)
        assert isinstance(result["nodes"], list)

    def test_links_is_list(self) -> None:
        result = self.graph.build(FEATURES)
        assert isinstance(result["links"], list)

    def test_node_has_id_and_name(self) -> None:
        result = self.graph.build(FEATURES)
        for node in result["nodes"]:
            assert "id" in node
            assert "name" in node

    def test_link_has_source_and_target(self) -> None:
        result = self.graph.build(FEATURES)
        for link in result["links"]:
            assert "source" in link
            assert "target" in link

    def test_correct_node_count(self) -> None:
        result = self.graph.build(FEATURES)
        assert len(result["nodes"]) == 3

    def test_correct_link_count(self) -> None:
        # F-002 → F-001 (1 link) + F-003 → F-001 + F-003 → F-002 (2 links) = 3
        result = self.graph.build(FEATURES)
        assert len(result["links"]) == 3

    def test_build_empty_features(self) -> None:
        result = self.graph.build([])
        assert result == {"nodes": [], "links": []}

    def test_build_no_dependencies(self) -> None:
        features = [{"id": "A"}, {"id": "B"}, {"id": "C"}]
        result = self.graph.build(features)
        assert len(result["nodes"]) == 3
        assert len(result["links"]) == 0

    def test_build_adds_missing_dependency_as_node(self) -> None:
        features = [{"id": "A", "depends_on": ["B"]}]  # B not in features list
        result = self.graph.build(features)
        node_ids = [n["id"] for n in result["nodes"]]
        assert "B" in node_ids

    def test_critical_path_returns_list(self) -> None:
        result = self.graph.critical_path(FEATURES)
        assert isinstance(result, list)

    def test_critical_path_contains_all_ids(self) -> None:
        result = self.graph.critical_path(FEATURES)
        assert set(result) == {"F-001", "F-002", "F-003"}

    def test_critical_path_root_before_dependents(self) -> None:
        result = self.graph.critical_path(FEATURES)
        assert result.index("F-001") < result.index("F-002")
        assert result.index("F-001") < result.index("F-003")


# ---------------------------------------------------------------------------
# ExecutiveSummaryGenerator
# ---------------------------------------------------------------------------


class TestExecutiveSummaryGenerator:
    def setup_method(self) -> None:
        self.gen = ExecutiveSummaryGenerator()
        self.completed = [
            {"title": "Login feature", "story_points": 5},
            {"title": "Dashboard", "story_points": 8},
        ]
        self.velocity = {
            "committed_points": 30,
            "completed_points": 13,
            "predictability_score": 75,
        }

    def test_generate_returns_string(self) -> None:
        result = self.gen.generate("Sprint 4", self.completed, self.velocity)
        assert isinstance(result, str)

    def test_generate_contains_sprint_name(self) -> None:
        result = self.gen.generate("Sprint 4", self.completed, self.velocity)
        assert "Sprint 4" in result

    def test_generate_contains_velocity_section(self) -> None:
        result = self.gen.generate("Sprint 4", self.completed, self.velocity)
        assert "Velocity" in result

    def test_generate_contains_committed_points(self) -> None:
        result = self.gen.generate("Sprint 4", self.completed, self.velocity)
        assert "30" in result  # committed_points=30

    def test_generate_contains_completed_items(self) -> None:
        result = self.gen.generate("Sprint 4", self.completed, self.velocity)
        assert "Login feature" in result

    def test_generate_contains_risk_section(self) -> None:
        result = self.gen.generate("Sprint 4", self.completed, self.velocity)
        assert "Risk" in result

    def test_generate_high_risk_mentioned(self) -> None:
        risks = [{"story_id": "S-001", "title": "API Migration", "level": "HIGH"}]
        result = self.gen.generate("Sprint 4", self.completed, self.velocity, risks=risks)
        assert "HIGH" in result
        assert "API Migration" in result

    def test_generate_no_risks_shows_clean_status(self) -> None:
        result = self.gen.generate("Sprint 4", self.completed, self.velocity, risks=[])
        assert "No HIGH/MEDIUM" in result

    def test_generate_next_sprint_goals_shown(self) -> None:
        goals = ["Improve test coverage", "Migrate auth service"]
        result = self.gen.generate(
            "Sprint 4", self.completed, self.velocity, next_sprint_goals=goals
        )
        assert "Improve test coverage" in result

    def test_generate_empty_items(self) -> None:
        result = self.gen.generate("Sprint 4", [], {"committed_points": 0, "completed_points": 0})
        assert isinstance(result, str)
        assert "No items completed" in result

    def test_generate_does_not_write_files(self) -> None:
        """CORE-002: generate must return string, never produce file side-effects."""
        import os
        files_before = set(os.listdir("/tmp"))
        result = self.gen.generate("Sprint 1", self.completed, self.velocity)
        files_after = set(os.listdir("/tmp"))
        assert isinstance(result, str)
        # No new tmp files from generate
        new_files = files_after - files_before
        # Filter to only CORTEX-related files
        cortex_files = [f for f in new_files if "cortex" in f.lower() or "po_" in f.lower()]
        assert cortex_files == []
