"""
Tests for D3GitTimelineRenderer.

AC-ID: LENS-DASH-008
Author: Asif Hussain
Phase: 14
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cortex.visualization.renderers.d3_git_timeline_renderer import (
    D3GitTimelineRenderer,
    TimelineCommit,
    TimelineDay,
)


@pytest.fixture
def sample_commits() -> list[dict]:
    """Sample commit data for testing."""
    base_date = datetime(2026, 1, 1, 10, 0, 0)
    return [
        {
            "hash": "abc123",
            "author": "Alice",
            "date": base_date.isoformat(),
            "message": "feat: Add new feature",
            "files_changed": 5,
            "insertions": 120,
            "deletions": 30,
        },
        {
            "hash": "def456",
            "author": "Bob",
            "date": (base_date + timedelta(hours=2)).isoformat(),
            "message": "fix: Fix critical bug",
            "files_changed": 2,
            "insertions": 15,
            "deletions": 10,
        },
        {
            "hash": "ghi789",
            "author": "Alice",
            "date": (base_date + timedelta(days=1)).isoformat(),
            "message": "refactor: Improve code structure",
            "files_changed": 8,
            "insertions": 200,
            "deletions": 150,
        },
        {
            "hash": "jkl012",
            "author": "Charlie",
            "date": (base_date + timedelta(days=2)).isoformat(),
            "message": "docs: Update documentation",
            "files_changed": 3,
            "insertions": 50,
            "deletions": 5,
        },
    ]


@pytest.fixture
def renderer() -> D3GitTimelineRenderer:
    """Create renderer instance."""
    return D3GitTimelineRenderer()


class TestTimelineCommit:
    """Test TimelineCommit dataclass."""

    def test_from_dict(self) -> None:
        """Test creating TimelineCommit from dict."""
        commit_data = {
            "hash": "abc123",
            "author": "Alice",
            "date": "2026-01-01T10:00:00",
            "message": "feat: Add feature",
            "files_changed": 5,
            "insertions": 120,
            "deletions": 30,
        }
        
        commit = TimelineCommit.from_dict(commit_data)
        
        assert commit.hash == "abc123"
        assert commit.author == "Alice"
        assert commit.date == datetime(2026, 1, 1, 10, 0, 0)
        assert commit.message == "feat: Add feature"
        assert commit.files_changed == 5
        assert commit.insertions == 120
        assert commit.deletions == 30

    def test_category_detection(self) -> None:
        """Test commit category detection from message."""
        test_cases = [
            ("feat: New feature", "feature"),
            ("fix: Bug fix", "bugfix"),
            ("security: Fix vulnerability", "security"),
            ("refactor: Code improvement", "refactor"),
            ("docs: Update docs", "documentation"),
            ("test: Add tests", "test"),
            ("chore: Update dependencies", "maintenance"),
            ("Random commit message", "other"),
        ]
        
        for message, expected_category in test_cases:
            commit = TimelineCommit(
                hash="abc",
                author="Test",
                date=datetime.now(),
                message=message,
                files_changed=1,
                insertions=10,
                deletions=5,
            )
            assert commit.category == expected_category

    def test_impact_calculation(self) -> None:
        """Test commit impact score calculation."""
        # Low impact: 1 file, 10 lines changed
        low_commit = TimelineCommit(
            hash="abc",
            author="Test",
            date=datetime.now(),
            message="fix: Minor fix",
            files_changed=1,
            insertions=5,
            deletions=5,
        )
        assert low_commit.impact == "low"
        
        # Medium impact: 5 files, 100 lines changed
        medium_commit = TimelineCommit(
            hash="def",
            author="Test",
            date=datetime.now(),
            message="feat: New feature",
            files_changed=5,
            insertions=60,
            deletions=40,
        )
        assert medium_commit.impact == "medium"
        
        # High impact: 15 files, 500 lines changed
        high_commit = TimelineCommit(
            hash="ghi",
            author="Test",
            date=datetime.now(),
            message="refactor: Major refactor",
            files_changed=15,
            insertions=300,
            deletions=200,
        )
        assert high_commit.impact == "high"


class TestD3GitTimelineRenderer:
    """Test D3GitTimelineRenderer."""

    def test_initialization(self, renderer: D3GitTimelineRenderer) -> None:
        """Test renderer initialization."""
        assert renderer.width == 1200
        assert renderer.height == 600
        assert len(renderer.category_colors) == 8

    def test_group_commits_by_day(
        self, renderer: D3GitTimelineRenderer, sample_commits: list[dict]
    ) -> None:
        """Test grouping commits by day."""
        timeline_commits = [
            TimelineCommit.from_dict(c) for c in sample_commits
        ]
        
        days = renderer._group_commits_by_day(timeline_commits)
        
        assert len(days) == 3  # 3 unique days
        assert days[0].date.date() == datetime(2026, 1, 1).date()
        assert len(days[0].commits) == 2  # Alice and Bob on day 1
        assert days[0].total_commits == 2
        assert days[1].date.date() == datetime(2026, 1, 2).date()
        assert len(days[1].commits) == 1  # Alice on day 2

    def test_render_timeline(
        self, renderer: D3GitTimelineRenderer, sample_commits: list[dict]
    ) -> None:
        """Test rendering timeline JSON."""
        result = renderer.render_timeline(sample_commits)
        
        assert "config" in result
        assert "days" in result
        assert "categories" in result
        assert "stats" in result
        
        # Check config
        assert result["config"]["width"] == 1200
        assert result["config"]["height"] == 600
        
        # Check days
        assert len(result["days"]) == 3
        assert result["days"][0]["total_commits"] == 2
        
        # Check categories
        assert "feature" in result["categories"]
        assert "bugfix" in result["categories"]
        assert "refactor" in result["categories"]
        
        # Check stats
        assert result["stats"]["total_commits"] == 4
        assert result["stats"]["total_authors"] == 3
        assert result["stats"]["date_range"]["start"] == "2026-01-01"
        assert result["stats"]["date_range"]["end"] == "2026-01-03"

    def test_calculate_statistics(
        self, renderer: D3GitTimelineRenderer, sample_commits: list[dict]
    ) -> None:
        """Test statistics calculation."""
        timeline_commits = [
            TimelineCommit.from_dict(c) for c in sample_commits
        ]
        
        stats = renderer._calculate_statistics(timeline_commits)
        
        assert stats["total_commits"] == 4
        assert stats["total_authors"] == 3
        assert stats["total_files_changed"] == 18
        assert stats["total_insertions"] == 385
        assert stats["total_deletions"] == 195
        assert "Alice" in stats["commits_by_author"]
        assert stats["commits_by_author"]["Alice"] == 2

    def test_render_empty_commits(
        self, renderer: D3GitTimelineRenderer
    ) -> None:
        """Test rendering with no commits."""
        result = renderer.render_timeline([])
        
        assert result["stats"]["total_commits"] == 0
        assert len(result["days"]) == 0
        assert len(result["categories"]) == 8  # All categories still present

    def test_render_to_json_file(
        self, renderer: D3GitTimelineRenderer, sample_commits: list[dict], tmp_path: Path
    ) -> None:
        """Test rendering to JSON file."""
        output_file = tmp_path / "timeline.json"
        
        renderer.render_to_file(sample_commits, output_file)
        
        assert output_file.exists()
        
        # Verify JSON is valid
        with open(output_file) as f:
            data = json.load(f)
        
        assert "days" in data
        assert "stats" in data
        assert data["stats"]["total_commits"] == 4

    def test_commit_ordering_by_date(
        self, renderer: D3GitTimelineRenderer
    ) -> None:
        """Test commits are ordered chronologically."""
        commits = [
            {
                "hash": "abc",
                "author": "Alice",
                "date": "2026-01-03T10:00:00",
                "message": "Third",
                "files_changed": 1,
                "insertions": 10,
                "deletions": 5,
            },
            {
                "hash": "def",
                "author": "Bob",
                "date": "2026-01-01T10:00:00",
                "message": "First",
                "files_changed": 1,
                "insertions": 10,
                "deletions": 5,
            },
            {
                "hash": "ghi",
                "author": "Charlie",
                "date": "2026-01-02T10:00:00",
                "message": "Second",
                "files_changed": 1,
                "insertions": 10,
                "deletions": 5,
            },
        ]
        
        result = renderer.render_timeline(commits)
        
        # Days should be in chronological order
        assert result["days"][0]["date"] == "2026-01-01"
        assert result["days"][1]["date"] == "2026-01-02"
        assert result["days"][2]["date"] == "2026-01-03"

    def test_category_color_mapping(
        self, renderer: D3GitTimelineRenderer
    ) -> None:
        """Test category color mapping."""
        result = renderer.render_timeline([
            {
                "hash": "abc",
                "author": "Alice",
                "date": "2026-01-01T10:00:00",
                "message": "feat: Feature",
                "files_changed": 1,
                "insertions": 10,
                "deletions": 5,
            }
        ])
        
        assert result["categories"]["feature"]["color"] == "#4CAF50"
        assert result["categories"]["bugfix"]["color"] == "#F44336"
        assert result["categories"]["security"]["color"] == "#FF5722"
