"""
D3.js Git Timeline Renderer.

Generates D3.js force-directed timeline visualization data for Git commit history.
Provides temporal analysis with commit categorization and impact assessment.

AC-ID: LENS-DASH-008
Author: Asif Hussain
Phase: 14
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class TimelineCommit:
    """Represents a commit on the timeline."""

    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimelineCommit":
        """
        Create TimelineCommit from dictionary.

        Args:
            data: Dictionary with commit data

        Returns:
            TimelineCommit instance

        Example:
            >>> commit = TimelineCommit.from_dict({
            ...     "hash": "abc123",
            ...     "author": "Alice",
            ...     "date": "2026-01-01T10:00:00",
            ...     "message": "feat: Add feature",
            ...     "files_changed": 5,
            ...     "insertions": 120,
            ...     "deletions": 30,
            ... })
        """
        return cls(
            hash=data["hash"],
            author=data["author"],
            date=datetime.fromisoformat(data["date"]),
            message=data["message"],
            files_changed=data["files_changed"],
            insertions=data["insertions"],
            deletions=data["deletions"],
        )

    @property
    def category(self) -> str:
        """
        Detect commit category from message prefix.

        Returns:
            Category: feature, bugfix, security, refactor, documentation,
                     test, maintenance, or other

        Example:
            >>> commit.message = "feat: Add feature"
            >>> commit.category
            'feature'
        """
        message_lower = self.message.lower()

        if message_lower.startswith(("feat:", "feature:")):
            return "feature"
        elif message_lower.startswith(("fix:", "bugfix:")):
            return "bugfix"
        elif message_lower.startswith("security:"):
            return "security"
        elif message_lower.startswith("refactor:"):
            return "refactor"
        elif message_lower.startswith(("docs:", "doc:")):
            return "documentation"
        elif message_lower.startswith("test:"):
            return "test"
        elif message_lower.startswith(("chore:", "build:", "ci:")):
            return "maintenance"
        else:
            return "other"

    @property
    def impact(self) -> str:
        """
        Calculate commit impact score.

        Impact is based on:
        - Number of files changed
        - Total lines changed (insertions + deletions)

        Returns:
            Impact level: low, medium, or high

        Example:
            >>> commit.files_changed = 15
            >>> commit.insertions = 300
            >>> commit.deletions = 200
            >>> commit.impact
            'high'
        """
        total_lines_changed = self.insertions + self.deletions

        # High impact: 10+ files OR 300+ lines
        if self.files_changed >= 10 or total_lines_changed >= 300:
            return "high"
        # Medium impact: 3+ files OR 50+ lines
        elif self.files_changed >= 3 or total_lines_changed >= 50:
            return "medium"
        # Low impact: everything else
        else:
            return "low"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation

        Example:
            >>> commit.to_dict()
            {
                "hash": "abc123",
                "short_hash": "abc123",
                "author": "Alice",
                "date": "2026-01-01T10:00:00",
                "message": "feat: Add feature",
                "files_changed": 5,
                "insertions": 120,
                "deletions": 30,
                "category": "feature",
                "impact": "medium"
            }
        """
        return {
            "hash": self.hash,
            "short_hash": self.hash[:7],
            "author": self.author,
            "date": self.date.isoformat(),
            "message": self.message,
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "category": self.category,
            "impact": self.impact,
        }


@dataclass
class TimelineDay:
    """Represents a day on the timeline with aggregated commits."""

    date: datetime
    commits: list[TimelineCommit] = field(default_factory=list)

    @property
    def total_commits(self) -> int:
        """Get total commits on this day."""
        return len(self.commits)

    @property
    def total_files_changed(self) -> int:
        """Get total files changed on this day."""
        return sum(c.files_changed for c in self.commits)

    @property
    def total_lines_changed(self) -> int:
        """Get total lines changed on this day."""
        return sum(c.insertions + c.deletions for c in self.commits)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation with aggregated stats
        """
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "total_commits": self.total_commits,
            "total_files_changed": self.total_files_changed,
            "total_lines_changed": self.total_lines_changed,
            "commits": [c.to_dict() for c in self.commits],
        }


class D3GitTimelineRenderer:
    """
    Renders Git commit history as D3.js timeline visualization.

    Provides:
    - Temporal commit visualization with day grouping
    - Commit categorization (feature, bugfix, security, etc.)
    - Impact assessment (low, medium, high)
    - Author contribution tracking
    - Statistics aggregation

    Example:
        >>> renderer = D3GitTimelineRenderer()
        >>> timeline_data = renderer.render_timeline(commits)
        >>> renderer.render_to_file(commits, Path("timeline.json"))
    """

    def __init__(
        self,
        width: int = 1200,
        height: int = 600,
    ) -> None:
        """
        Initialize D3 Git Timeline Renderer.

        Args:
            width: SVG width in pixels
            height: SVG height in pixels
        """
        self.width = width
        self.height = height

        # Category color palette (Material Design colors)
        self.category_colors = {
            "feature": "#4CAF50",  # Green
            "bugfix": "#F44336",  # Red
            "security": "#FF5722",  # Deep Orange
            "refactor": "#2196F3",  # Blue
            "documentation": "#9C27B0",  # Purple
            "test": "#FF9800",  # Orange
            "maintenance": "#607D8B",  # Blue Grey
            "other": "#9E9E9E",  # Grey
        }

    def render_timeline(self, commits: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Render Git commit history as D3.js timeline data.

        Args:
            commits: List of commit dictionaries with keys:
                    - hash: Commit hash
                    - author: Author name
                    - date: ISO format date
                    - message: Commit message
                    - files_changed: Number of files changed
                    - insertions: Lines inserted
                    - deletions: Lines deleted

        Returns:
            Dictionary with D3.js timeline configuration:
            - config: Visualization configuration
            - days: Timeline days with commits
            - categories: Category metadata with colors
            - stats: Aggregated statistics

        Example:
            >>> commits = [
            ...     {
            ...         "hash": "abc123",
            ...         "author": "Alice",
            ...         "date": "2026-01-01T10:00:00",
            ...         "message": "feat: Add feature",
            ...         "files_changed": 5,
            ...         "insertions": 120,
            ...         "deletions": 30,
            ...     }
            ... ]
            >>> data = renderer.render_timeline(commits)
            >>> data["stats"]["total_commits"]
            1
        """
        # Convert to TimelineCommit objects
        timeline_commits = [TimelineCommit.from_dict(c) for c in commits]

        # Sort by date (oldest first)
        timeline_commits.sort(key=lambda c: c.date)

        # Group commits by day
        days = self._group_commits_by_day(timeline_commits)

        # Calculate statistics
        stats = self._calculate_statistics(timeline_commits)

        # Build category metadata
        categories = {
            category: {"color": color, "count": 0}
            for category, color in self.category_colors.items()
        }
        for commit in timeline_commits:
            categories[commit.category]["count"] += 1

        return {
            "config": {
                "width": self.width,
                "height": self.height,
                "type": "git_timeline",
            },
            "days": [day.to_dict() for day in days],
            "categories": categories,
            "stats": stats,
        }

    def _group_commits_by_day(
        self, commits: list[TimelineCommit]
    ) -> list[TimelineDay]:
        """
        Group commits by day.

        Args:
            commits: List of TimelineCommit objects (sorted by date)

        Returns:
            List of TimelineDay objects
        """
        if not commits:
            return []

        days: list[TimelineDay] = []
        current_day = TimelineDay(date=commits[0].date.replace(hour=0, minute=0, second=0))

        for commit in commits:
            commit_day = commit.date.replace(hour=0, minute=0, second=0)

            if commit_day != current_day.date:
                # Start new day
                days.append(current_day)
                current_day = TimelineDay(date=commit_day)

            current_day.commits.append(commit)

        # Add final day
        days.append(current_day)

        return days

    def _calculate_statistics(
        self, commits: list[TimelineCommit]
    ) -> dict[str, Any]:
        """
        Calculate aggregated statistics.

        Args:
            commits: List of TimelineCommit objects

        Returns:
            Dictionary with statistics:
            - total_commits: Total number of commits
            - total_authors: Unique authors count
            - total_files_changed: Sum of files changed
            - total_insertions: Sum of insertions
            - total_deletions: Sum of deletions
            - commits_by_author: Commit count per author
            - date_range: Start and end dates
        """
        if not commits:
            return {
                "total_commits": 0,
                "total_authors": 0,
                "total_files_changed": 0,
                "total_insertions": 0,
                "total_deletions": 0,
                "commits_by_author": {},
                "date_range": {"start": None, "end": None},
            }

        authors: set[str] = set()
        commits_by_author: dict[str, int] = {}

        total_files = 0
        total_insertions = 0
        total_deletions = 0

        for commit in commits:
            authors.add(commit.author)
            commits_by_author[commit.author] = (
                commits_by_author.get(commit.author, 0) + 1
            )
            total_files += commit.files_changed
            total_insertions += commit.insertions
            total_deletions += commit.deletions

        return {
            "total_commits": len(commits),
            "total_authors": len(authors),
            "total_files_changed": total_files,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "commits_by_author": commits_by_author,
            "date_range": {
                "start": commits[0].date.strftime("%Y-%m-%d"),
                "end": commits[-1].date.strftime("%Y-%m-%d"),
            },
        }

    def render_to_file(
        self, commits: list[dict[str, Any]], output_path: Path
    ) -> None:
        """
        Render timeline to JSON file.

        Args:
            commits: List of commit dictionaries
            output_path: Output file path (will be created if doesn't exist)

        Example:
            >>> renderer.render_to_file(commits, Path("timeline.json"))
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        timeline_data = self.render_timeline(commits)

        with open(output_path, "w") as f:
            json.dump(timeline_data, f, indent=2)
