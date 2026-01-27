"""
Tests for GitHistoryAnalyzer.

Authority: CORE-008 (TDD - Tests BEFORE code)
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

import pytest

from cortex.brain.analysis.git_history_analyzer import (
    GitHistoryAnalyzer,
    GitCommit,
    GitBlame,
    GitHistoryResult,
)


class TestGitCommit:
    """Test GitCommit dataclass."""
    
    def test_git_commit_creation(self):
        """Test creating a GitCommit."""
        commit = GitCommit(
            hash="abc123",
            author="John Doe",
            date=datetime(2026, 1, 27, 10, 0, 0),
            message="feat: Add feature",
            files_changed=["file.py"],
        )
        assert commit.hash == "abc123"
        assert commit.author == "John Doe"
        assert commit.message == "feat: Add feature"
        assert len(commit.files_changed) == 1


class TestGitBlame:
    """Test GitBlame dataclass."""
    
    def test_git_blame_creation(self):
        """Test creating a GitBlame entry."""
        blame = GitBlame(
            line_number=42,
            commit_hash="def456",
            author="Jane Smith",
            date=datetime(2026, 1, 20, 15, 30, 0),
            line_content="    return result",
        )
        assert blame.line_number == 42
        assert blame.commit_hash == "def456"
        assert blame.author == "Jane Smith"


class TestGitHistoryAnalyzer:
    """Test GitHistoryAnalyzer functionality."""
    
    @pytest.fixture
    def analyzer(self, tmp_path: Path):
        """Create analyzer with temp repository."""
        return GitHistoryAnalyzer(repo_path=tmp_path)
    
    def test_analyzer_initialization(self, tmp_path: Path):
        """Test analyzer initialization."""
        analyzer = GitHistoryAnalyzer(repo_path=tmp_path)
        assert analyzer.repo_path == tmp_path
        assert analyzer.max_commits == 100
    
    def test_analyzer_custom_max_commits(self, tmp_path: Path):
        """Test analyzer with custom max_commits."""
        analyzer = GitHistoryAnalyzer(repo_path=tmp_path, max_commits=50)
        assert analyzer.max_commits == 50
    
    @patch('subprocess.run')
    def test_get_file_history_success(self, mock_run, analyzer: GitHistoryAnalyzer):
        """Test getting file history successfully."""
        # Mock git log output
        mock_run.return_value = Mock(
            returncode=0,
            stdout=(
                "abc123|John Doe|2026-01-27 10:00:00|feat: Add feature\n"
                "def456|Jane Smith|2026-01-26 15:30:00|fix: Fix bug\n"
            ),
        )
        
        result = analyzer.get_file_history("test.py", max_commits=2)
        
        assert result.success is True
        assert len(result.commits) == 2
        assert result.commits[0].hash == "abc123"
        assert result.commits[0].author == "John Doe"
        assert result.commits[1].hash == "def456"
    
    @patch('subprocess.run')
    def test_get_file_history_no_file(self, mock_run, analyzer: GitHistoryAnalyzer):
        """Test getting history for non-existent file."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=128,
            cmd="git log",
            stderr="fatal: path not found",
        )
        
        result = analyzer.get_file_history("nonexistent.py")
        
        assert result.success is False
        assert len(result.commits) == 0
        assert "not found" in result.error.lower()
    
    @patch('subprocess.run')
    def test_get_blame_success(self, mock_run, analyzer: GitHistoryAnalyzer):
        """Test getting blame information successfully."""
        # Mock git blame porcelain output
        mock_run.return_value = Mock(
            returncode=0,
            stdout=(
                "abc1234567890123456789012345678901234567\n"
                "author John Doe\n"
                "author-time 1737968400\n"
                "\tdef hello():\n"
                "def4567890123456789012345678901234567890\n"
                "author Jane Smith\n"
                "author-time 1737882000\n"
                "\t    return 'world'\n"
            ),
        )
        
        result = analyzer.get_blame("test.py")
        
        assert result.success is True
        assert len(result.blame_info) == 2
        assert result.blame_info[0].line_number == 1
        assert result.blame_info[0].commit_hash == "abc1234"  # Short hash
        assert result.blame_info[1].author == "Jane Smith"
    
    @patch('subprocess.run')
    def test_get_recent_commits_success(self, mock_run, analyzer: GitHistoryAnalyzer):
        """Test getting recent commits successfully."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=(
                "abc123|John Doe|2026-01-27 10:00:00|feat: Add feature\n"
                "file1.py\n"
                "file2.py\n"
                "\n"
                "def456|Jane Smith|2026-01-26 15:30:00|fix: Fix bug\n"
                "file3.py\n"
            ),
        )
        
        result = analyzer.get_recent_commits(max_commits=2)
        
        assert result.success is True
        assert len(result.commits) == 2
        assert result.commits[0].hash == "abc123"
        assert len(result.commits[0].files_changed) == 2
        assert "file1.py" in result.commits[0].files_changed
    
    @patch('subprocess.run')
    def test_get_commits_by_author_success(self, mock_run, analyzer: GitHistoryAnalyzer):
        """Test getting commits by specific author."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=(
                "abc123|John Doe|2026-01-27 10:00:00|feat: Add feature\n"
                "file1.py\n"
            ),
        )
        
        result = analyzer.get_commits_by_author("John Doe", max_commits=10)
        
        assert result.success is True
        assert len(result.commits) == 1
        assert result.commits[0].author == "John Doe"
        
        # Verify git command included author filter
        call_args = mock_run.call_args[0][0]
        assert "--author=John Doe" in " ".join(call_args)
    
    @patch('subprocess.run')
    def test_search_commits_success(self, mock_run, analyzer: GitHistoryAnalyzer):
        """Test searching commits by message pattern."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout=(
                "abc123|John Doe|2026-01-27 10:00:00|feat: Add LENS feature\n"
                "file1.py\n"
            ),
        )
        
        result = analyzer.search_commits("LENS", max_commits=10)
        
        assert result.success is True
        assert len(result.commits) == 1
        assert "LENS" in result.commits[0].message
        
        # Verify git command included grep filter
        call_args = mock_run.call_args[0][0]
        assert "--grep=LENS" in " ".join(call_args)
    
    @patch('subprocess.run')
    def test_git_command_failure_handling(self, mock_run, analyzer: GitHistoryAnalyzer):
        """Test handling of git command failures."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="git log",
            stderr="fatal: Not a git repository",
        )
        
        result = analyzer.get_recent_commits()
        
        assert result.success is False
        assert "git repository" in result.error.lower()
    
    def test_parse_commit_line_valid(self, analyzer: GitHistoryAnalyzer):
        """Test parsing valid commit line."""
        line = "abc123|John Doe|2026-01-27 10:00:00|feat: Add feature"
        commit = analyzer._parse_commit_line(line)
        
        assert commit is not None
        assert commit.hash == "abc123"
        assert commit.author == "John Doe"
        assert commit.message == "feat: Add feature"
        assert len(commit.files_changed) == 0  # Files added separately
    
    def test_parse_commit_line_invalid(self, analyzer: GitHistoryAnalyzer):
        """Test parsing invalid commit line."""
        line = "invalid|format"
        commit = analyzer._parse_commit_line(line)
        
        assert commit is None
    
    def test_parse_blame_line_valid(self, analyzer: GitHistoryAnalyzer):
        """Test parsing valid blame line."""
        line = "abc123 (John Doe 2026-01-27 10:00:00 42)     return result"
        blame = analyzer._parse_blame_line(line, line_number=42)
        
        assert blame is not None
        assert blame.commit_hash == "abc123"
        assert blame.author == "John Doe"
        assert blame.line_number == 42
        assert "return result" in blame.line_content
    
    def test_parse_blame_line_invalid(self, analyzer: GitHistoryAnalyzer):
        """Test parsing invalid blame line."""
        line = "invalid blame format"
        blame = analyzer._parse_blame_line(line, line_number=1)
        
        assert blame is None


class TestGitHistoryIntegration:
    """Integration tests using real git commands (if available)."""
    
    @pytest.mark.integration
    def test_real_git_history(self, tmp_path: Path):
        """Test with real git repository (integration test)."""
        # Skip if not in git repository
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                check=True,
                capture_output=True,
                cwd=tmp_path.parent,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            pytest.skip("Not in a git repository")
        
        analyzer = GitHistoryAnalyzer(repo_path=tmp_path.parent)
        result = analyzer.get_recent_commits(max_commits=1)
        
        # Should successfully get at least one commit
        assert result.success is True
        if result.commits:
            assert result.commits[0].hash
            assert result.commits[0].author
