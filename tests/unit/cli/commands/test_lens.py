"""
Tests for LENS CLI commands.

Authority: CORE-008 (TDD)
Phase: 10 - LENS Remote Intelligence
Task: LENS-015
"""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest
from click.testing import CliRunner

from cortex.cli.commands.lens import (
    lens,
    analyze_remote,
    compare_branches,
    cache_stats,
    cache_clear,
)


class TestAnalyzeRemoteCommand:
    """Test analyze-remote CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
    
    def test_analyze_remote_missing_token(self, runner):
        """Test error when token is missing."""
        result = runner.invoke(
            analyze_remote,
            ["owner/repo", "test.py"]
        )
        
        assert result.exit_code != 0
        assert "API token required" in result.output


class TestCompareBranchesCommand:
    """Test compare-branches CLI command."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
    
    @patch("cortex.orchestrators.support.lens_orchestrator.LENSOrchestrator")
    def test_compare_branches_local(self, mock_orchestrator_class, runner):
        """Test local branch comparison."""
        mock_orchestrator = Mock()
        mock_orchestrator.compare_branches.return_value = {
            "base_branch": "main",
            "head_branch": "feature",
            "commits_ahead": 3,
            "commits_behind": 1,
            "is_mergeable": True,
            "commits": [
                {
                    "hash": "abc123",
                    "message": "feat: add feature",
                }
            ],
            "file_diffs": [
                {
                    "file_path": "test.py",
                    "status": "modified",
                    "additions": 10,
                    "deletions": 5,
                }
            ],
            "total_additions": 10,
            "total_deletions": 5,
            "conflicts": [],
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        result = runner.invoke(
            compare_branches,
            ["main", "feature", "--local"]
        )
        
        assert result.exit_code == 0
        assert "Branch Comparison Results" in result.output
        assert "main" in result.output
        assert "feature" in result.output
        assert "✅ Yes" in result.output
    
    def test_compare_branches_remote_missing_token(self, runner):
        """Test error when remote comparison missing token."""
        result = runner.invoke(
            compare_branches,
            ["main", "feature", "--repo", "owner/repo"]
        )
        
        assert result.exit_code != 0
        assert "API token required" in result.output


# Skip cache tests if diskcache is not installed
_diskcache_available = pytest.importorskip("diskcache", reason="diskcache not installed")


class TestCacheCommands:
    """Test cache management commands."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
    
    @patch("cortex.brain.analysis.remote_cache.get_remote_cache")
    def test_cache_stats(self, mock_get_cache, runner):
        """Test cache stats command."""
        mock_cache = Mock()
        mock_stats = Mock()
        mock_stats.hits = 100
        mock_stats.misses = 25
        mock_stats.hit_rate = 80.0
        mock_stats.entries = 50
        mock_stats.size = 1024 * 100  # 100 KB
        mock_stats.evictions = 5
        
        mock_cache.stats.return_value = mock_stats
        mock_get_cache.return_value = mock_cache
        
        result = runner.invoke(cache_stats)
        
        assert result.exit_code == 0
        assert "Remote Cache Statistics" in result.output
        assert "Hits: 100" in result.output
        assert "Misses: 25" in result.output
        assert "80.0%" in result.output
        assert "Entries: 50" in result.output
    
    @patch("cortex.brain.analysis.remote_cache.get_remote_cache")
    def test_cache_clear(self, mock_get_cache, runner):
        """Test cache clear command."""
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache
        
        result = runner.invoke(cache_clear)
        
        assert result.exit_code == 0
        assert "cleared successfully" in result.output
        mock_cache.clear.assert_called_once()


class TestLensGroup:
    """Test LENS command group."""
    
    @pytest.fixture
    def runner(self):
        """Create Click test runner."""
        return CliRunner()
    
    def test_lens_group_exists(self, runner):
        """Test LENS command group exists."""
        result = runner.invoke(lens, ["--help"])
        
        assert result.exit_code == 0
        assert "LENS Remote Intelligence commands" in result.output
        assert "analyze-remote" in result.output
        assert "compare-branches" in result.output
        assert "cache-stats" in result.output
        assert "cache-clear" in result.output
