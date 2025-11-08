"""
Integration tests for Tier 3 Context Intelligence.
Tests the full system working together.
"""

import pytest
import sqlite3
from datetime import date, timedelta
from pathlib import Path
import tempfile
import shutil
import subprocess

from src.tier3.context_intelligence import ContextIntelligence
from src.tier3.metrics.git_metrics import GitMetric
from src.tier3.metrics.file_metrics import FileHotspot, Stability


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_context.db"
    
    yield db_path
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_repo():
    """Create a temporary git repository for integration testing."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, capture_output=True)
    
    # Create files and commits
    for i in range(5):
        test_file = repo_path / f"file{i}.py"
        test_file.write_text(f"# File {i}\nprint('test')\n")
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', f'Commit {i}'], cwd=repo_path, capture_output=True)
    
    yield repo_path
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def context_intelligence(temp_repo, temp_db):
    """Create a ContextIntelligence instance."""
    return ContextIntelligence(temp_repo, temp_db)


class TestContextIntelligenceIntegration:
    """Integration tests for full Context Intelligence system."""
    
    def test_full_system_initialization(self, context_intelligence):
        """Test that full system initializes correctly."""
        assert context_intelligence.store is not None
        assert context_intelligence.git_collector is not None
        assert context_intelligence.file_analyzer is not None
        assert context_intelligence.velocity_analyzer is not None
        assert context_intelligence.insight_generator is not None
    
    def test_end_to_end_git_metrics_workflow(self, context_intelligence):
        """Test complete workflow: collect, save, retrieve, analyze git metrics."""
        # Collect metrics
        metrics = context_intelligence.collect_git_metrics(days=30, force=True)
        assert isinstance(metrics, list)
        
        # Retrieve metrics
        retrieved = context_intelligence.get_git_metrics(days=30)
        assert isinstance(retrieved, list)
        
        # Calculate velocity
        velocity = context_intelligence.calculate_velocity(days=30)
        assert isinstance(velocity, dict)
        assert 'avg_commits_per_day' in velocity
    
    def test_end_to_end_file_hotspots_workflow(self, context_intelligence):
        """Test complete workflow: analyze, save, retrieve file hotspots."""
        # Analyze hotspots
        hotspots = context_intelligence.analyze_file_hotspots(days=30, force=True)
        assert isinstance(hotspots, list)
        
        # Retrieve hotspots
        retrieved = context_intelligence.get_file_hotspots(days=30)
        assert isinstance(retrieved, list)
        
        # Get unstable files
        unstable = context_intelligence.get_unstable_files(days=30)
        assert isinstance(unstable, list)
    
    def test_end_to_end_insights_workflow(self, context_intelligence):
        """Test complete workflow: collect data and generate insights."""
        # Collect all data
        context_intelligence.collect_git_metrics(days=30, force=True)
        context_intelligence.analyze_file_hotspots(days=30, force=True)
        
        # Generate insights
        insights = context_intelligence.generate_insights(days=30)
        assert isinstance(insights, list)
        
        # Generate specific insight types
        velocity_insights = context_intelligence.generate_velocity_insights(days=30)
        hotspot_insights = context_intelligence.generate_hotspot_insights(days=30)
        
        assert isinstance(velocity_insights, list)
        assert isinstance(hotspot_insights, list)
    
    def test_refresh_all_functionality(self, context_intelligence):
        """Test refresh_all convenience method."""
        results = context_intelligence.refresh_all(days=30, force=True)
        
        assert isinstance(results, dict)
        assert 'git_metrics' in results
        assert 'file_hotspots' in results
        assert 'insights' in results
        assert 'database_size' in results
        
        # All counts should be non-negative
        assert results['git_metrics'] >= 0
        assert results['file_hotspots'] >= 0
        assert results['insights'] >= 0
        assert results['database_size'] > 0
    
    def test_get_summary_functionality(self, context_intelligence):
        """Test get_summary convenience method."""
        # Populate some data first
        context_intelligence.collect_git_metrics(days=30, force=True)
        context_intelligence.analyze_file_hotspots(days=30, force=True)
        
        summary = context_intelligence.get_summary(days=30)
        
        assert isinstance(summary, dict)
        assert 'velocity' in summary
        assert 'hotspot_count' in summary
        assert 'unstable_count' in summary
        assert 'insight_count' in summary
        assert 'database_size' in summary
        assert 'table_counts' in summary
    
    def test_database_operations(self, context_intelligence):
        """Test database utility operations."""
        # Get size
        size = context_intelligence.get_database_size()
        assert isinstance(size, int)
        assert size > 0
        
        # Get table counts
        counts = context_intelligence.get_table_counts()
        assert isinstance(counts, dict)
        assert len(counts) == 4  # 4 tables
        
        # Vacuum and analyze
        context_intelligence.vacuum_database()
        context_intelligence.analyze_database()
    
    def test_multi_day_analysis_consistency(self, context_intelligence):
        """Test that multi-day analysis maintains consistency."""
        # Collect data for different time periods
        metrics_7 = context_intelligence.collect_git_metrics(days=7, force=True)
        metrics_30 = context_intelligence.collect_git_metrics(days=30, force=True)
        
        # 30-day should include 7-day data
        assert len(metrics_30) >= len(metrics_7)
        
        # Velocity calculations should be consistent
        velocity_7 = context_intelligence.calculate_velocity(days=7)
        velocity_30 = context_intelligence.calculate_velocity(days=30)
        
        assert isinstance(velocity_7, dict)
        assert isinstance(velocity_30, dict)
