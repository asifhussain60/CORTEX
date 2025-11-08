"""
CORTEX Tier 3: Context Intelligence Tests
"""

import pytest
import sqlite3
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch

from src.tier3.context_intelligence import (
    ContextIntelligence,
    GitMetric,
    FileHotspot,
    Stability,
    Insight,
    InsightType,
    Severity
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_context.db"
        yield db_path


@pytest.fixture
def context_intel(temp_db):
    """Create ContextIntelligence instance."""
    return ContextIntelligence(db_path=temp_db)


class TestDatabaseInitialization:
    """Test database schema creation."""
    
    def test_creates_database_file(self, temp_db):
        """Should create database file."""
        context = ContextIntelligence(db_path=temp_db)
        assert temp_db.exists()
    
    def test_creates_git_metrics_table(self, context_intel, temp_db):
        """Should create git metrics table with correct schema."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='context_git_metrics'
        """)
        assert cursor.fetchone() is not None
        conn.close()
    
    def test_creates_file_hotspots_table(self, context_intel, temp_db):
        """Should create file hotspots table."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='context_file_hotspots'
        """)
        assert cursor.fetchone() is not None
        conn.close()


class TestGitMetricsCollection:
    """Test git metrics collection."""
    
    def test_saves_git_metrics(self, context_intel):
        """Should save git metrics to database."""
        metrics = [
            GitMetric(
                metric_date=date.today(),
                commits_count=5,
                lines_added=120,
                lines_deleted=30,
                net_growth=90,
                files_changed=8,
                contributor="test_user"
            )
        ]
        
        context_intel.save_git_metrics(metrics)
        
        retrieved = context_intel.get_git_metrics(days=1, contributor="test_user")
        assert len(retrieved) == 1
        assert retrieved[0].commits_count == 5
        assert retrieved[0].lines_added == 120
    
    def test_aggregates_metrics_by_date(self, context_intel):
        """Should aggregate metrics across contributors."""
        metrics = [
            GitMetric(
                metric_date=date.today(),
                commits_count=3,
                lines_added=50,
                lines_deleted=10,
                net_growth=40,
                files_changed=5,
                contributor="user1"
            ),
            GitMetric(
                metric_date=date.today(),
                commits_count=2,
                lines_added=30,
                lines_deleted=5,
                net_growth=25,
                files_changed=3,
                contributor="user2"
            )
        ]
        
        context_intel.save_git_metrics(metrics)
        
        # Get aggregated metrics (no contributor filter)
        aggregated = context_intel.get_git_metrics(days=1)
        assert len(aggregated) == 1
        assert aggregated[0].commits_count == 5  # 3 + 2
        assert aggregated[0].lines_added == 80   # 50 + 30
    
    def test_filters_by_date_range(self, context_intel):
        """Should filter metrics by date range."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        metrics = [
            GitMetric(metric_date=today, commits_count=2, lines_added=20,
                     lines_deleted=5, net_growth=15, files_changed=3),
            GitMetric(metric_date=yesterday, commits_count=3, lines_added=30,
                     lines_deleted=10, net_growth=20, files_changed=5),
            GitMetric(metric_date=week_ago, commits_count=1, lines_added=10,
                     lines_deleted=2, net_growth=8, files_changed=2)
        ]
        
        context_intel.save_git_metrics(metrics)
        
        # Get last 2 days
        recent = context_intel.get_git_metrics(days=2)
        assert len(recent) == 2


class TestFileHotspotAnalysis:
    """Test file hotspot analysis."""
    
    def test_saves_file_hotspots(self, context_intel):
        """Should save file hotspots to database."""
        hotspots = [
            FileHotspot(
                file_path="src/test.py",
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_commits=100,
                file_edits=25,
                churn_rate=0.25,
                stability=Stability.UNSTABLE,
                lines_changed=500
            )
        ]
        
        context_intel.save_file_hotspots(hotspots)
        
        unstable = context_intel.get_unstable_files(limit=10)
        assert len(unstable) == 1
        assert unstable[0].file_path == "src/test.py"
        assert unstable[0].churn_rate == 0.25
    
    def test_classifies_stability_correctly(self, context_intel):
        """Should classify files by stability."""
        hotspots = [
            FileHotspot(
                file_path="stable.py",
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_commits=100,
                file_edits=5,
                churn_rate=0.05,
                stability=Stability.STABLE
            ),
            FileHotspot(
                file_path="moderate.py",
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_commits=100,
                file_edits=15,
                churn_rate=0.15,
                stability=Stability.MODERATE
            ),
            FileHotspot(
                file_path="unstable.py",
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_commits=100,
                file_edits=30,
                churn_rate=0.30,
                stability=Stability.UNSTABLE
            )
        ]
        
        context_intel.save_file_hotspots(hotspots)
        
        unstable = context_intel.get_unstable_files(limit=10)
        assert len(unstable) == 1
        assert unstable[0].file_path == "unstable.py"


class TestVelocityAnalysis:
    """Test commit velocity calculation."""
    
    def test_calculates_velocity_trend(self, context_intel):
        """Should calculate velocity trends correctly."""
        today = date.today()
        metrics = []
        
        # Current week: 10 commits
        for i in range(7):
            day = today - timedelta(days=i)
            metrics.append(GitMetric(
                metric_date=day,
                commits_count=10 if i < 7 else 5,
                lines_added=100,
                lines_deleted=20,
                net_growth=80,
                files_changed=10
            ))
        
        # Previous week: 5 commits
        for i in range(7, 14):
            day = today - timedelta(days=i)
            metrics.append(GitMetric(
                metric_date=day,
                commits_count=5,
                lines_added=50,
                lines_deleted=10,
                net_growth=40,
                files_changed=5
            ))
        
        context_intel.save_git_metrics(metrics)
        
        velocity = context_intel.calculate_commit_velocity(window_days=7)
        assert velocity['current_velocity'] > velocity['previous_velocity']
        assert velocity['trend'] == 'increasing'
    
    def test_detects_velocity_drop(self, context_intel):
        """Should detect velocity drops."""
        today = date.today()
        metrics = []
        
        # Current week: 2 commits (low)
        for i in range(7):
            day = today - timedelta(days=i)
            metrics.append(GitMetric(
                metric_date=day,
                commits_count=2,
                lines_added=20,
                lines_deleted=5,
                net_growth=15,
                files_changed=2
            ))
        
        # Previous week: 10 commits (high)
        for i in range(7, 14):
            day = today - timedelta(days=i)
            metrics.append(GitMetric(
                metric_date=day,
                commits_count=10,
                lines_added=100,
                lines_deleted=20,
                net_growth=80,
                files_changed=10
            ))
        
        context_intel.save_git_metrics(metrics)
        
        velocity = context_intel.calculate_commit_velocity(window_days=7)
        assert velocity['current_velocity'] < velocity['previous_velocity']
        assert velocity['trend'] == 'declining'


class TestInsightGeneration:
    """Test insight generation."""
    
    def test_generates_velocity_drop_insight(self, context_intel):
        """Should generate insight for velocity drops."""
        today = date.today()
        metrics = []
        
        # Create declining velocity
        for i in range(7):
            metrics.append(GitMetric(
                metric_date=today - timedelta(days=i),
                commits_count=2,
                lines_added=20,
                lines_deleted=5,
                net_growth=15,
                files_changed=2
            ))
        
        for i in range(7, 14):
            metrics.append(GitMetric(
                metric_date=today - timedelta(days=i),
                commits_count=10,
                lines_added=100,
                lines_deleted=20,
                net_growth=80,
                files_changed=10
            ))
        
        context_intel.save_git_metrics(metrics)
        
        insights = context_intel.generate_insights()
        velocity_insights = [i for i in insights if i.insight_type == InsightType.VELOCITY_DROP]
        assert len(velocity_insights) > 0
        assert velocity_insights[0].severity == Severity.WARNING
    
    def test_generates_file_hotspot_insight(self, context_intel):
        """Should generate insight for unstable files."""
        hotspots = [
            FileHotspot(
                file_path="src/unstable.py",
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_commits=100,
                file_edits=40,
                churn_rate=0.40,
                stability=Stability.UNSTABLE
            )
        ]
        
        context_intel.save_file_hotspots(hotspots)
        
        insights = context_intel.generate_insights()
        hotspot_insights = [i for i in insights if i.insight_type == InsightType.FILE_HOTSPOT]
        assert len(hotspot_insights) > 0
        assert "unstable.py" in hotspot_insights[0].title


class TestContextSummary:
    """Test context summary generation."""
    
    def test_generates_comprehensive_summary(self, context_intel):
        """Should generate comprehensive context summary."""
        # Add git metrics
        metrics = [
            GitMetric(
                metric_date=date.today(),
                commits_count=5,
                lines_added=100,
                lines_deleted=20,
                net_growth=80,
                files_changed=10
            )
        ]
        context_intel.save_git_metrics(metrics)
        
        # Add hotspots
        hotspots = [
            FileHotspot(
                file_path="src/test.py",
                period_start=date.today() - timedelta(days=30),
                period_end=date.today(),
                total_commits=100,
                file_edits=30,
                churn_rate=0.30,
                stability=Stability.UNSTABLE
            )
        ]
        context_intel.save_file_hotspots(hotspots)
        
        summary = context_intel.get_context_summary()
        
        assert 'git_metrics' in summary
        assert 'velocity' in summary
        assert 'unstable_files' in summary
        assert 'insights' in summary
        
        assert summary['git_metrics']['total_commits'] == 5
        assert len(summary['unstable_files']) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
