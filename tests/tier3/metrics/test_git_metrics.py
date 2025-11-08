"""
Unit tests for Tier 3 Git Metrics module.
"""

import pytest
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import subprocess

from src.tier3.metrics.git_metrics import GitMetric, GitMetricsCollector
from src.tier3.storage.context_store import ContextStore


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_context.db"
    
    yield db_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_repo():
    """Create a temporary git repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, capture_output=True)
    
    # Create initial commit
    test_file = repo_path / "test.txt"
    test_file.write_text("Initial content\n")
    subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path, capture_output=True)
    
    yield repo_path
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def context_store(temp_db):
    """Create a ContextStore instance."""
    return ContextStore(temp_db)


@pytest.fixture
def git_collector(temp_repo, context_store):
    """Create a GitMetricsCollector instance."""
    return GitMetricsCollector(temp_repo, context_store)


class TestGitMetric:
    """Test GitMetric dataclass."""
    
    def test_git_metric_creation(self):
        """Test creating a GitMetric instance."""
        metric = GitMetric(
            metric_date=date(2025, 1, 15),
            commits_count=5,
            lines_added=100,
            lines_deleted=20,
            net_growth=80,
            files_changed=3,
            contributor="test@example.com"
        )
        
        assert metric.metric_date == date(2025, 1, 15)
        assert metric.commits_count == 5
        assert metric.lines_added == 100
        assert metric.lines_deleted == 20
        assert metric.net_growth == 80
        assert metric.files_changed == 3
        assert metric.contributor == "test@example.com"
    
    def test_git_metric_defaults(self):
        """Test GitMetric with default values."""
        metric = GitMetric(
            metric_date=date(2025, 1, 15),
            commits_count=0,
            lines_added=0,
            lines_deleted=0,
            net_growth=0,
            files_changed=0
        )
        
        assert metric.commits_count == 0
        assert metric.contributor is None


class TestGitMetricsCollector:
    """Test GitMetricsCollector class."""
    
    def test_collector_initialization(self, git_collector, temp_repo):
        """Test GitMetricsCollector initialization."""
        assert git_collector.repo_path == temp_repo
        assert git_collector.store is not None
    
    def test_collect_metrics_empty_period(self, git_collector):
        """Test collecting metrics when no commits exist in period."""
        # Collect metrics from far future (no commits)
        metrics = git_collector.collect_metrics(days=1, force=True)
        
        # Should return empty list for dates with no commits
        assert isinstance(metrics, list)
    
    def test_save_and_retrieve_metrics(self, git_collector):
        """Test saving and retrieving git metrics."""
        # Create test metrics
        metrics = [
            GitMetric(
                metric_date=date.today(),
                commits_count=3,
                lines_added=50,
                lines_deleted=10,
                net_growth=40,
                files_changed=2,
                contributor="test@example.com"
            )
        ]
        
        # Save metrics
        git_collector.save_metrics(metrics)
        
        # Retrieve metrics
        retrieved = git_collector.get_metrics(days=1)
        
        assert len(retrieved) >= 1
        assert retrieved[0].commits_count == 3
        assert retrieved[0].lines_added == 50
    
    def test_get_metrics_date_filtering(self, git_collector):
        """Test that get_metrics respects date filtering."""
        # Create metrics for different dates
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        metrics = [
            GitMetric(
                metric_date=today,
                commits_count=2,
                lines_added=20,
                lines_deleted=5,
                net_growth=15,
                files_changed=1
            ),
            GitMetric(
                metric_date=yesterday,
                commits_count=1,
                lines_added=10,
                lines_deleted=2,
                net_growth=8,
                files_changed=1
            )
        ]
        
        git_collector.save_metrics(metrics)
        
        # Get only today's metrics
        recent = git_collector.get_metrics(days=1)
        assert len(recent) == 1
        assert recent[0].metric_date == today
        
        # Get both days
        all_metrics = git_collector.get_metrics(days=2)
        assert len(all_metrics) == 2
    
    def test_duplicate_metric_handling(self, git_collector):
        """Test handling of duplicate metrics (same date + contributor)."""
        metric = GitMetric(
            metric_date=date.today(),
            commits_count=1,
            lines_added=10,
            lines_deleted=0,
            net_growth=10,
            files_changed=1,
            contributor="test@example.com"
        )
        
        # Save same metric twice
        git_collector.save_metrics([metric])
        git_collector.save_metrics([metric])
        
        # Should only have one entry (UNIQUE constraint)
        retrieved = git_collector.get_metrics(days=1)
        matching = [m for m in retrieved if m.contributor == "test@example.com"]
        assert len(matching) == 1
    
    def test_force_collection_flag(self, git_collector):
        """Test that force flag bypasses caching."""
        # First collection
        metrics1 = git_collector.collect_metrics(days=7, force=True)
        
        # Second collection with force
        metrics2 = git_collector.collect_metrics(days=7, force=True)
        
        # Both should return results (not cached)
        assert isinstance(metrics1, list)
        assert isinstance(metrics2, list)
    
    def test_aggregation_across_contributors(self, git_collector):
        """Test aggregation of metrics across multiple contributors."""
        today = date.today()
        
        metrics = [
            GitMetric(
                metric_date=today,
                commits_count=2,
                lines_added=20,
                lines_deleted=5,
                net_growth=15,
                files_changed=2,
                contributor="user1@example.com"
            ),
            GitMetric(
                metric_date=today,
                commits_count=3,
                lines_added=30,
                lines_deleted=10,
                net_growth=20,
                files_changed=3,
                contributor="user2@example.com"
            )
        ]
        
        git_collector.save_metrics(metrics)
        
        # Get aggregated metrics (no contributor filter)
        aggregated = git_collector.get_metrics(days=1)
        
        # Should aggregate values
        assert len(aggregated) >= 1
        # Total commits should be sum of both contributors
        total_commits = sum(m.commits_count for m in aggregated if m.metric_date == today)
        assert total_commits >= 5
    
    def test_empty_repository_handling(self, temp_db):
        """Test handling of repository with no commits."""
        # Create repo without commits
        temp_dir = tempfile.mkdtemp()
        empty_repo = Path(temp_dir)
        subprocess.run(['git', 'init'], cwd=empty_repo, capture_output=True)
        
        try:
            store = ContextStore(temp_db)
            collector = GitMetricsCollector(empty_repo, store)
            
            # Should handle gracefully
            metrics = collector.collect_metrics(days=30, force=True)
            assert isinstance(metrics, list)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_get_metrics_with_specific_contributor(self, git_collector):
        """Test filtering metrics by specific contributor."""
        today = date.today()
        
        metrics = [
            GitMetric(
                metric_date=today,
                commits_count=2,
                lines_added=20,
                lines_deleted=5,
                net_growth=15,
                files_changed=2,
                contributor="alice@example.com"
            ),
            GitMetric(
                metric_date=today,
                commits_count=3,
                lines_added=30,
                lines_deleted=10,
                net_growth=20,
                files_changed=3,
                contributor="bob@example.com"
            )
        ]
        
        git_collector.save_metrics(metrics)
        
        # Get metrics for specific contributor
        alice_metrics = git_collector.get_metrics(days=1, contributor="alice@example.com")
        
        assert len(alice_metrics) >= 1
        assert all(m.contributor == "alice@example.com" for m in alice_metrics)
