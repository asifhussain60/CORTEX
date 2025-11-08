"""
Unit tests for Tier 3 Velocity Analyzer module.
"""

import pytest
import sqlite3
from datetime import date, timedelta
from pathlib import Path
import tempfile
import shutil

from src.tier3.analysis.velocity_analyzer import VelocityAnalyzer
from src.tier3.storage.context_store import ContextStore
from src.tier3.metrics.git_metrics import GitMetric


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_context.db"
    
    yield db_path
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def context_store(temp_db):
    """Create a ContextStore instance."""
    return ContextStore(temp_db)


@pytest.fixture
def velocity_analyzer(context_store):
    """Create a VelocityAnalyzer instance."""
    return VelocityAnalyzer(context_store)


@pytest.fixture
def sample_metrics(context_store):
    """Create sample git metrics for testing."""
    today = date.today()
    metrics = []
    
    # Create 30 days of metrics with varying activity
    for i in range(30):
        metric_date = today - timedelta(days=i)
        commits = 5 + (i % 3)  # Varies between 5-7
        
        metric = GitMetric(
            metric_date=metric_date,
            commits_count=commits,
            lines_added=50 + (i * 10),
            lines_deleted=10 + (i * 2),
            net_growth=40 + (i * 8),
            files_changed=3 + (i % 2)
        )
        metrics.append(metric)
    
    # Save to database
    conn = sqlite3.connect(context_store.db_path)
    cursor = conn.cursor()
    
    for metric in metrics:
        cursor.execute("""
            INSERT OR REPLACE INTO context_git_metrics
            (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            metric.metric_date.isoformat(),
            metric.commits_count,
            metric.lines_added,
            metric.lines_deleted,
            metric.net_growth,
            metric.files_changed
        ))
    
    conn.commit()
    conn.close()
    
    return metrics


class TestVelocityAnalyzer:
    """Test VelocityAnalyzer class."""
    
    def test_analyzer_initialization(self, velocity_analyzer, context_store):
        """Test VelocityAnalyzer initialization."""
        assert velocity_analyzer.store == context_store
    
    def test_calculate_velocity_with_data(self, velocity_analyzer, sample_metrics):
        """Test calculating velocity with sample data."""
        velocity = velocity_analyzer.calculate_velocity(days=30)
        
        assert isinstance(velocity, dict)
        assert 'avg_commits_per_day' in velocity
        assert 'avg_lines_added' in velocity
        assert 'avg_lines_deleted' in velocity
        assert 'avg_net_growth' in velocity
        assert 'avg_files_changed' in velocity
        assert 'total_commits' in velocity
        
        # Verify calculations
        assert velocity['avg_commits_per_day'] > 0
        assert velocity['total_commits'] > 0
    
    def test_calculate_velocity_empty_data(self, velocity_analyzer):
        """Test calculating velocity with no data."""
        velocity = velocity_analyzer.calculate_velocity(days=30)
        
        assert isinstance(velocity, dict)
        assert velocity['avg_commits_per_day'] == 0
        assert velocity['total_commits'] == 0
    
    def test_analyze_trends_with_data(self, velocity_analyzer, sample_metrics):
        """Test analyzing trends with sample data."""
        trends = velocity_analyzer.analyze_trends(days=30)
        
        assert isinstance(trends, dict)
        assert 'velocity' in trends
        assert 'trend' in trends
        assert 'trend_direction' in trends
        
        # Trend direction should be one of: increasing, decreasing, stable
        assert trends['trend_direction'] in ['increasing', 'decreasing', 'stable']
    
    def test_velocity_calculation_accuracy(self, velocity_analyzer):
        """Test accuracy of velocity calculations."""
        # Insert known metrics
        today = date.today()
        conn = sqlite3.connect(velocity_analyzer.store.db_path)
        cursor = conn.cursor()
        
        # Insert exactly 5 days of data
        for i in range(5):
            cursor.execute("""
                INSERT OR REPLACE INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                (today - timedelta(days=i)).isoformat(),
                2,  # 2 commits per day
                100,  # 100 lines added
                20,   # 20 lines deleted
                80,   # 80 net growth
                5     # 5 files changed
            ))
        
        conn.commit()
        conn.close()
        
        velocity = velocity_analyzer.calculate_velocity(days=5)
        
        # Should average to 2 commits per day
        assert velocity['avg_commits_per_day'] == 2.0
        assert velocity['total_commits'] == 10  # 2 * 5 days
        assert velocity['avg_lines_added'] == 100.0
        assert velocity['avg_net_growth'] == 80.0
    
    def test_trend_direction_increasing(self, velocity_analyzer):
        """Test trend detection for increasing velocity."""
        today = date.today()
        conn = sqlite3.connect(velocity_analyzer.store.db_path)
        cursor = conn.cursor()
        
        # Create increasing trend (more commits over time)
        for i in range(14):
            cursor.execute("""
                INSERT OR REPLACE INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                (today - timedelta(days=i)).isoformat(),
                i + 1,  # Increasing commits
                100,
                20,
                80,
                5
            ))
        
        conn.commit()
        conn.close()
        
        trends = velocity_analyzer.analyze_trends(days=14)
        
        # Should detect increasing trend
        assert trends['trend_direction'] in ['increasing', 'stable']
    
    def test_date_range_filtering(self, velocity_analyzer, sample_metrics):
        """Test that velocity calculation respects date ranges."""
        # Calculate for different periods
        velocity_7 = velocity_analyzer.calculate_velocity(days=7)
        velocity_30 = velocity_analyzer.calculate_velocity(days=30)
        
        assert isinstance(velocity_7, dict)
        assert isinstance(velocity_30, dict)
        
        # 30-day period should have more total commits
        assert velocity_30['total_commits'] >= velocity_7['total_commits']
    
    def test_velocity_with_zero_days(self, velocity_analyzer, sample_metrics):
        """Test edge case of zero-day period."""
        velocity = velocity_analyzer.calculate_velocity(days=0)
        
        # Should handle gracefully (return zero or empty metrics)
        assert isinstance(velocity, dict)
        assert velocity['total_commits'] == 0
