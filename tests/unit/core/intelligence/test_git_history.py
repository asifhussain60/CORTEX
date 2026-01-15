# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-001-02 - Git History Intelligence Tests
"""
Tests for Git History Intelligence.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-001-02 - Git History Intelligence

Tests cover:
- Git log parsing and commit extraction
- Change frequency mapping (hot spots)
- Author context building
- Refactoring pattern detection
- Temporal context building
"""

import os
import subprocess
import tempfile
import textwrap
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def mock_git_log_output() -> str:
    """Mock git log output for testing."""
    return textwrap.dedent('''
        commit abc123def456
        Author: John Doe <john@example.com>
        Date:   2026-01-15 10:30:00 +0000
        
            feat: Add user authentication module
            
            - Implemented login/logout functionality
            - Added session management
            
        src/auth/login.py | 50 +++++
        src/auth/session.py | 30 +++++
        
        commit def789abc012
        Author: Jane Smith <jane@example.com>
        Date:   2026-01-14 15:45:00 +0000
        
            fix: Resolve database connection leak
            
        src/db/connection.py | 10 +++--
        
        commit 111222333444
        Author: John Doe <john@example.com>
        Date:   2026-01-13 09:00:00 +0000
        
            refactor: Extract utility functions
            
        src/utils/helpers.py | 100 ++++++++++
        src/core/main.py | 80 --------
    ''')


@pytest.fixture
def mock_git_blame_output() -> str:
    """Mock git blame output for testing."""
    return textwrap.dedent('''
        abc123de (John Doe  2026-01-15 10:30:00 +0000  1) def login(username: str) -> bool:
        abc123de (John Doe  2026-01-15 10:30:00 +0000  2)     """Authenticate user."""
        abc123de (John Doe  2026-01-15 10:30:00 +0000  3)     return True
        def789ab (Jane Smith 2026-01-14 15:45:00 +0000  4) 
        def789ab (Jane Smith 2026-01-14 15:45:00 +0000  5) def logout() -> None:
    ''')


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository for testing."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    
    # Configure git user for commits
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    
    # Create initial file and commit
    test_file = repo_path / "test.py"
    test_file.write_text("# Initial content\n")
    
    subprocess.run(
        ["git", "add", "."],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )
    
    return repo_path


# =============================================================================
# TEST CLASSES: GIT LOG PARSING
# =============================================================================


class TestGitLogParsing:
    """Tests for git log parsing functionality."""

    def test_parse_commit_history(
        self, temp_git_repo: Path
    ) -> None:
        """Test parsing commit history from a git repository."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        commits = analyzer.get_commit_history()
        
        assert len(commits) >= 1
        assert commits[0].message is not None

    def test_extract_commit_metadata(
        self, temp_git_repo: Path
    ) -> None:
        """Test extracting commit metadata (author, date, hash)."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        commits = analyzer.get_commit_history()
        
        first_commit = commits[0]
        assert first_commit.hash is not None
        assert first_commit.author is not None
        assert first_commit.date is not None

    def test_parse_commit_message(
        self, temp_git_repo: Path
    ) -> None:
        """Test parsing commit messages."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        commits = analyzer.get_commit_history()
        
        assert "Initial commit" in commits[0].message

    def test_get_file_history(
        self, temp_git_repo: Path
    ) -> None:
        """Test getting history for a specific file."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        # Create and commit a second version
        test_file = temp_git_repo / "test.py"
        test_file.write_text("# Updated content\ndef foo(): pass\n")
        
        subprocess.run(
            ["git", "add", "."],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Update test.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        file_history = analyzer.get_file_history(Path("test.py"))
        
        assert len(file_history) >= 2
        assert "Update test.py" in file_history[0].message

    def test_get_commit_diff(
        self, temp_git_repo: Path
    ) -> None:
        """Test getting diff for a specific commit."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        commits = analyzer.get_commit_history()
        
        diff = analyzer.get_commit_diff(commits[0].hash)
        
        assert diff is not None
        assert isinstance(diff, str)

    def test_handles_empty_repo(
        self, tmp_path: Path
    ) -> None:
        """Test handling of repository with no commits."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        empty_repo = tmp_path / "empty_repo"
        empty_repo.mkdir()
        
        subprocess.run(
            ["git", "init"],
            cwd=empty_repo,
            capture_output=True,
            check=True,
        )
        
        analyzer = GitHistoryAnalyzer(repo_path=empty_repo)
        commits = analyzer.get_commit_history()
        
        assert commits == []


# =============================================================================
# TEST CLASSES: CHANGE FREQUENCY
# =============================================================================


class TestChangeFrequency:
    """Tests for change frequency (hot spot) identification."""

    def test_identify_hot_spots(
        self, temp_git_repo: Path
    ) -> None:
        """Test identification of frequently changed files."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        from src.core.intelligence.change_frequency import ChangeFrequencyMapper
        
        # Create multiple commits to build history
        test_file = temp_git_repo / "hot_file.py"
        for i in range(3):
            test_file.write_text(f"# Version {i}\ndef foo(): return {i}\n")
            subprocess.run(
                ["git", "add", "."],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Update {i}"],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        mapper = ChangeFrequencyMapper(analyzer)
        
        hot_spots = mapper.get_hot_spots()
        
        # hot_file.py should be the most frequently changed
        assert len(hot_spots) > 0
        assert hot_spots[0].file_path == "hot_file.py"

    def test_calculate_change_count(
        self, temp_git_repo: Path
    ) -> None:
        """Test calculation of change count for files."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        from src.core.intelligence.change_frequency import ChangeFrequencyMapper
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        mapper = ChangeFrequencyMapper(analyzer)
        
        change_count = mapper.get_change_count(Path("test.py"))
        
        assert change_count >= 1

    def test_temporal_hot_spots(
        self, temp_git_repo: Path
    ) -> None:
        """Test hot spot identification within time window."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        from src.core.intelligence.change_frequency import ChangeFrequencyMapper
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        mapper = ChangeFrequencyMapper(analyzer)
        
        # Get hot spots from last 30 days
        hot_spots = mapper.get_hot_spots(days=30)
        
        assert isinstance(hot_spots, list)


# =============================================================================
# TEST CLASSES: AUTHOR MAPPING
# =============================================================================


class TestAuthorMapping:
    """Tests for author context building."""

    def test_map_authors_to_files(
        self, temp_git_repo: Path
    ) -> None:
        """Test mapping authors to files they've modified."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        from src.core.intelligence.author_context import AuthorContextBuilder
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        builder = AuthorContextBuilder(analyzer)
        
        author_files = builder.get_author_files("Test User")
        
        assert "test.py" in author_files

    def test_identify_file_experts(
        self, temp_git_repo: Path
    ) -> None:
        """Test identification of experts for specific files."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        from src.core.intelligence.author_context import AuthorContextBuilder
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        builder = AuthorContextBuilder(analyzer)
        
        experts = builder.get_file_experts(Path("test.py"))
        
        assert len(experts) >= 1
        assert experts[0].name == "Test User"

    def test_calculate_author_contribution(
        self, temp_git_repo: Path
    ) -> None:
        """Test calculation of author contribution percentage."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        from src.core.intelligence.author_context import AuthorContextBuilder
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        builder = AuthorContextBuilder(analyzer)
        
        contribution = builder.get_author_contribution("Test User")
        
        assert contribution.commit_count >= 1
        assert contribution.files_touched >= 1


# =============================================================================
# TEST CLASSES: REFACTORING DETECTION
# =============================================================================


class TestRefactoringDetection:
    """Tests for refactoring pattern detection from git history."""

    def test_detect_file_rename(
        self, temp_git_repo: Path
    ) -> None:
        """Test detection of file rename operations."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        # Create a file and rename it
        old_file = temp_git_repo / "old_name.py"
        old_file.write_text("# Content\n")
        
        subprocess.run(
            ["git", "add", "."],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add old_name.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        
        # Rename file
        new_file = temp_git_repo / "new_name.py"
        subprocess.run(
            ["git", "mv", "old_name.py", "new_name.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Rename old_name.py to new_name.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        renames = analyzer.detect_renames()
        
        assert len(renames) >= 1
        assert renames[0].old_path == "old_name.py"
        assert renames[0].new_path == "new_name.py"

    def test_detect_file_move(
        self, temp_git_repo: Path
    ) -> None:
        """Test detection of file move operations."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        # Create directory and file
        src_dir = temp_git_repo / "src"
        src_dir.mkdir()
        
        file_path = temp_git_repo / "module.py"
        file_path.write_text("# Module content\n")
        
        subprocess.run(
            ["git", "add", "."],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add module.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        
        # Move file to src/
        subprocess.run(
            ["git", "mv", "module.py", "src/module.py"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Move module.py to src/"],
            cwd=temp_git_repo,
            capture_output=True,
            check=True,
        )
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        moves = analyzer.detect_moves()
        
        assert len(moves) >= 1


# =============================================================================
# TEST CLASSES: TEMPORAL CONTEXT
# =============================================================================


class TestTemporalContext:
    """Tests for temporal context building."""

    def test_build_file_timeline(
        self, temp_git_repo: Path
    ) -> None:
        """Test building a timeline of changes for a file."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        # Create multiple commits
        test_file = temp_git_repo / "timeline.py"
        for i in range(3):
            test_file.write_text(f"# Version {i}\n")
            subprocess.run(
                ["git", "add", "."],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Timeline update {i}"],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        timeline = analyzer.get_file_timeline(Path("timeline.py"))
        
        assert len(timeline) >= 3
        # Timeline should be in reverse chronological order
        for i in range(len(timeline) - 1):
            assert timeline[i].date >= timeline[i + 1].date

    def test_get_recent_changes(
        self, temp_git_repo: Path
    ) -> None:
        """Test getting recent changes within time window."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        recent = analyzer.get_recent_changes(days=7)
        
        assert len(recent) >= 1
        # Verify all commits are recent (within 7 days)
        # Note: commit.date is naive datetime from git log parsing
        now = datetime.now()
        for c in recent:
            diff = now - c.date
            assert diff.days <= 7, f"Commit {c.hash} is {diff.days} days old"


# =============================================================================
# TEST CLASSES: ERROR HANDLING
# =============================================================================


class TestGitHistoryErrorHandling:
    """Tests for error handling in git history analysis."""

    def test_handles_non_git_directory(
        self, tmp_path: Path
    ) -> None:
        """Test handling of non-git directory."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        non_git_dir = tmp_path / "not_a_repo"
        non_git_dir.mkdir()
        
        analyzer = GitHistoryAnalyzer(repo_path=non_git_dir)
        
        assert analyzer.is_git_repo() is False
        assert analyzer.get_commit_history() == []

    def test_handles_missing_file(
        self, temp_git_repo: Path
    ) -> None:
        """Test handling of history request for non-existent file."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        history = analyzer.get_file_history(Path("nonexistent.py"))
        
        assert history == []


# =============================================================================
# TEST CLASSES: INTEGRATION
# =============================================================================


class TestGitHistoryIntegration:
    """Integration tests for git history analysis."""

    def test_full_analysis_pipeline(
        self, temp_git_repo: Path
    ) -> None:
        """Test complete git history analysis pipeline."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        from src.core.intelligence.change_frequency import ChangeFrequencyMapper
        from src.core.intelligence.author_context import AuthorContextBuilder
        
        # Build up some history
        for i in range(3):
            test_file = temp_git_repo / f"module_{i}.py"
            test_file.write_text(f"# Module {i}\n")
            subprocess.run(
                ["git", "add", "."],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Add module_{i}"],
                cwd=temp_git_repo,
                capture_output=True,
                check=True,
            )
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        
        # Verify commit history
        commits = analyzer.get_commit_history()
        assert len(commits) >= 4  # Initial + 3 modules
        
        # Verify change frequency
        freq_mapper = ChangeFrequencyMapper(analyzer)
        hot_spots = freq_mapper.get_hot_spots()
        assert len(hot_spots) >= 1
        
        # Verify author context
        author_builder = AuthorContextBuilder(analyzer)
        contribution = author_builder.get_author_contribution("Test User")
        assert contribution.commit_count >= 4

    def test_serialization_to_dict(
        self, temp_git_repo: Path
    ) -> None:
        """Test serialization of git analysis results."""
        from src.core.intelligence.git_history_analyzer import GitHistoryAnalyzer
        
        analyzer = GitHistoryAnalyzer(repo_path=temp_git_repo)
        commits = analyzer.get_commit_history()
        
        serialized = commits[0].to_dict()
        
        assert "hash" in serialized
        assert "author" in serialized
        assert "date" in serialized
        assert "message" in serialized
