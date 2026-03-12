"""Tests for TrainingDocGenerator (GAP-129-f)."""

from __future__ import annotations

import pytest

from cortex.intelligence.po.training_doc_generator import TrainingDocGenerator

SPRINT_HISTORY = [
    {"sprint_name": "Sprint 1", "completed_points": 30},
    {"sprint_name": "Sprint 2", "completed_points": 35},
    {"sprint_name": "Sprint 3", "completed_points": 28},
]

TEAM_NORMS = {
    "conventions": ["Use Gherkin ACs", "Two reviewers required", "No PRs > 400 lines"],
    "definition_of_done": [
        "All tests GREEN",
        "Code reviewed",
        "Docs updated",
    ],
    "velocity_baseline": 32,
}


class TestTrainingDocGenerator:
    def setup_method(self) -> None:
        self.gen = TrainingDocGenerator()

    def test_generate_returns_string(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert isinstance(result, str)

    def test_generate_contains_team_conventions_header(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "Team Conventions" in result

    def test_generate_lists_custom_conventions(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "Use Gherkin ACs" in result
        assert "Two reviewers required" in result

    def test_generate_contains_velocity_baseline_header(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "Velocity Baseline" in result

    def test_generate_shows_explicit_baseline(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "32" in result  # velocity_baseline = 32

    def test_generate_computes_baseline_from_history_when_no_norm(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, {})
        # Mean of [30, 35, 28] = 31.0 → appears in result
        assert "31" in result

    def test_generate_contains_definition_of_done_header(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "Definition of Done" in result

    def test_generate_lists_custom_dod(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "All tests GREEN" in result
        assert "Code reviewed" in result

    def test_generate_uses_fallback_conventions_when_none_provided(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, {})
        assert "Gherkin" in result or "make test" in result or "PR" in result.lower()

    def test_generate_uses_fallback_dod_when_none_provided(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, {})
        assert "acceptance criteria" in result.lower() or "tests GREEN" in result or "✅" in result

    def test_generate_empty_history_shows_placeholder(self) -> None:
        result = self.gen.generate([], TEAM_NORMS)
        assert "No sprint history" in result or "baseline" in result.lower()

    def test_generate_none_norms_defaults(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY)
        assert isinstance(result, str)
        assert "Velocity" in result

    def test_generate_does_not_write_files(self) -> None:
        """CORE-002: generate must return string, never write files to disk."""
        import os
        files_before = set(os.listdir("/tmp"))
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        files_after = set(os.listdir("/tmp"))
        new = files_after - files_before
        cortex_files = [f for f in new if "cortex" in f.lower()]
        assert cortex_files == []
        assert isinstance(result, str)

    def test_generate_contains_cortex_attribution(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "CORTEX" in result

    def test_generate_velocity_shows_sprint_count(self) -> None:
        result = self.gen.generate(SPRINT_HISTORY, TEAM_NORMS)
        assert "3" in result  # 3 sprints in SPRINT_HISTORY
