"""
Tests for BranchComparator.

Authority: CORE-008 (TDD)
Phase: 10 - LENS Remote Intelligence
Task: LENS-012
"""

import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from cortex.brain.analysis.branch_comparator import (
    BranchComparator,
    BranchComparison,
    FileDiff,
    ConflictInfo,
)
from cortex.brain.analysis.remote_git_adapter import (
    RemoteGitAdapter,
    RemoteCommit,
)
from cortex.brain.analysis.git_history_analyzer import GitCommit


class TestFileDiff:
    """Test FileDiff dataclass."""
    
    def test_file_diff_creation(self):
        """Test creating a FileDiff."""
        diff = FileDiff(
            file_path="test.py",
            status="modified",
            additions=10,
            deletions=5,
        )
        assert diff.file_path == "test.py"
        assert diff.status == "modified"
        assert diff.additions == 10
        assert diff.deletions == 5


class TestConflictInfo:
    """Test ConflictInfo dataclass."""
    
    def test_conflict_info_creation(self):
        """Test creating ConflictInfo."""
        conflict = ConflictInfo(
            file_path="conflicted.py",
            conflict_type="content",
            description="Content conflict detected",
        )
        assert conflict.file_path == "conflicted.py"
        assert conflict.conflict_type == "content"


class TestBranchComparison:
    """Test BranchComparison dataclass."""
    
    def test_branch_comparison_creation(self):
        """Test creating BranchComparison."""
        comparison = BranchComparison(
            base_branch="main",
            head_branch="feature",
            commits_ahead=5,
            commits_behind=2,
        )
        assert comparison.base_branch == "main"
        assert comparison.head_branch == "feature"
        assert comparison.commits_ahead == 5
        assert comparison.commits_behind == 2
        assert comparison.is_mergeable is True


class TestBranchComparatorLocal:
    """Test BranchComparator with local repositories."""
    
    @pytest.fixture
    def comparator(self, tmp_path: Path):
        """Create comparator with temp repository."""
        return BranchComparator(repo_path=tmp_path)
    
    def test_comparator_initialization(self, tmp_path: Path):
        """Test comparator initialization."""
        comparator = BranchComparator(repo_path=tmp_path)
        assert comparator.repo_path == tmp_path
        assert comparator.is_remote is False
    
    def test_comparator_requires_path_or_adapter(self):
        """Test that comparator requires path or adapter."""
        with pytest.raises(ValueError, match="Either repo_path or remote_adapter"):
            BranchComparator(repo_path=None, remote_adapter=None)
    
    @patch('subprocess.run')
    def test_compare_branches_local(self, mock_run, comparator: BranchComparator):
        """Test comparing branches in local repository."""
        # Mock ahead/behind counts
        mock_run.side_effect = [
            Mock(returncode=0, stdout="3\n"),  # ahead
            Mock(returncode=0, stdout="1\n"),  # behind
            Mock(returncode=0, stdout="abc123|John Doe|2026-01-27 10:00:00|feat: Add\ndef456|Jane|2026-01-26 15:00:00|fix: Bug\n"),  # commits
            Mock(returncode=0, stdout="10\t5\tfile1.py\n20\t3\tfile2.py\n"),  # diffs
            Mock(returncode=0, stdout=""),  # merge-tree (no conflicts)
        ]
        
        comparison = comparator.compare_branches("main", "feature")
        
        assert comparison.base_branch == "main"
        assert comparison.head_branch == "feature"
        assert comparison.commits_ahead == 3
        assert comparison.commits_behind == 1
        assert len(comparison.commits) == 2
        assert len(comparison.file_diffs) == 2
        assert comparison.total_additions == 30
        assert comparison.total_deletions == 8
        assert comparison.is_mergeable is True
    
    @patch('subprocess.run')
    def test_get_file_diffs_local(self, mock_run, comparator: BranchComparator):
        """Test getting file diffs."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="15\t0\tnew_file.py\n0\t20\told_file.py\n5\t5\tmodified.py\n",
        )
        
        diffs = comparator._get_file_diffs_local("main", "feature")
        
        assert len(diffs) == 3
        assert diffs[0].file_path == "new_file.py"
        assert diffs[0].status == "added"
        assert diffs[1].file_path == "old_file.py"
        assert diffs[1].status == "deleted"
        assert diffs[2].file_path == "modified.py"
        assert diffs[2].status == "modified"
    
    @patch('subprocess.run')
    def test_list_branches_local(self, mock_run, comparator: BranchComparator):
        """Test listing local branches."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="  main\n  feature\n  develop\n",
        )
        
        branches = comparator.list_branches()
        
        assert "main" in branches
        assert "feature" in branches
        assert "develop" in branches


class TestBranchComparatorRemote:
    """Test BranchComparator with remote repositories."""
    
    @pytest.fixture
    def mock_adapter(self):
        """Create mock RemoteGitAdapter."""
        adapter = Mock(spec=RemoteGitAdapter)
        return adapter
    
    def test_remote_comparator_initialization(self, mock_adapter):
        """Test remote comparator initialization."""
        comparator = BranchComparator(
            repo_path=None,
            remote_adapter=mock_adapter,
            remote_repo="owner/repo",
        )
        assert comparator.is_remote is True
        assert comparator.remote_adapter == mock_adapter
    
    def test_compare_branches_remote(self, mock_adapter):
        """Test comparing branches remotely."""
        # Mock remote comparison
        mock_adapter.compare_branches.return_value = {
            "commits": [
                RemoteCommit(
                    sha="abc123",
                    message="feat: Add feature",
                    author="John Doe",
                    author_email="john@example.com",
                    date=datetime(2026, 1, 27, 10, 0, 0),
                    files_changed=["file1.py"],
                ),
            ],
            "files_changed": ["file1.py", "file2.py"],
            "additions": 15,
            "deletions": 5,
            "total_commits": 1,
        }
        
        comparator = BranchComparator(
            repo_path=None,
            remote_adapter=mock_adapter,
            remote_repo="owner/repo",
        )
        
        comparison = comparator.compare_branches("main", "feature")
        
        assert comparison.base_branch == "main"
        assert comparison.head_branch == "feature"
        assert comparison.commits_ahead == 1
        assert len(comparison.commits) == 1
        assert comparison.commits[0].hash == "abc123"
        assert len(comparison.file_diffs) == 2
        assert comparison.total_additions == 15
        assert comparison.total_deletions == 5
        assert comparison.is_mergeable is True
        assert comparison.metadata["mode"] == "remote"
        
        mock_adapter.compare_branches.assert_called_once_with(
            repo="owner/repo",
            base_branch="main",
            head_branch="feature",
        )
    
    def test_compare_branches_remote_error(self, mock_adapter):
        """Test remote comparison error handling."""
        mock_adapter.compare_branches.side_effect = Exception("API error")
        
        comparator = BranchComparator(
            repo_path=None,
            remote_adapter=mock_adapter,
            remote_repo="owner/repo",
        )
        
        comparison = comparator.compare_branches("main", "feature")
        
        assert comparison.is_mergeable is False
        assert "error" in comparison.metadata
    
    def test_list_branches_remote(self, mock_adapter):
        """Test listing remote branches."""
        mock_adapter.list_branches.return_value = ["main", "develop", "feature"]
        
        comparator = BranchComparator(
            repo_path=None,
            remote_adapter=mock_adapter,
            remote_repo="owner/repo",
        )
        
        branches = comparator.list_branches()
        
        assert len(branches) == 3
        assert "main" in branches
        
        mock_adapter.list_branches.assert_called_once_with("owner/repo")


class TestBranchComparatorHybrid:
    """Test BranchComparator mode detection."""
    
    def test_local_mode_detection(self, tmp_path: Path):
        """Test local mode detection."""
        comparator = BranchComparator(repo_path=tmp_path)
        assert comparator.is_remote is False
    
    def test_remote_mode_detection(self):
        """Test remote mode detection."""
        mock_adapter = Mock(spec=RemoteGitAdapter)
        comparator = BranchComparator(
            repo_path=None,
            remote_adapter=mock_adapter,
            remote_repo="owner/repo",
        )
        assert comparator.is_remote is True
