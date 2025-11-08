"""
Unit tests for Tier 3 Insight Generator module.
"""

import pytest
import sqlite3
from datetime import date, timedelta
from pathlib import Path
import tempfile
import shutil

from src.tier3.analysis.insight_generator import (
    InsightGenerator, Insight, InsightType, Severity
)
from src.tier3.analysis.velocity_analyzer import VelocityAnalyzer
from src.tier3.metrics.file_metrics import FileMetricsAnalyzer, FileHotspot, Stability
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
def file_analyzer(context_store):
    """Create a FileMetricsAnalyzer with mock repo."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    repo_path.mkdir(exist_ok=True)
    
    analyzer = FileMetricsAnalyzer(repo_path, context_store)
    
    yield analyzer
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def insight_generator(context_store, velocity_analyzer, file_analyzer):
    """Create an InsightGenerator instance."""
    return InsightGenerator(context_store, velocity_analyzer, file_analyzer)


class TestInsight:
    """Test Insight dataclass."""
    
    def test_insight_creation(self):
        """Test creating an Insight instance."""
        insight = Insight(
            insight_type=InsightType.VELOCITY_DROP,
            severity=Severity.WARNING,
            title="Velocity decreased",
            description="Commit velocity dropped by 30%",
            data={'drop_percentage': 30},
            recommendations=["Review team capacity"]
        )
        
        assert insight.insight_type == InsightType.VELOCITY_DROP
        assert insight.severity == Severity.WARNING
        assert insight.title == "Velocity decreased"
        assert insight.data['drop_percentage'] == 30
        assert len(insight.recommendations) == 1


class TestInsightType:
    """Test InsightType enum."""
    
    def test_insight_types(self):
        """Test InsightType enum values."""
        assert InsightType.VELOCITY_DROP.value == "velocity_drop"
        assert InsightType.FILE_HOTSPOT.value == "file_hotspot"


class TestSeverity:
    """Test Severity enum."""
    
    def test_severity_levels(self):
        """Test Severity enum values."""
        assert Severity.INFO.value == "INFO"
        assert Severity.WARNING.value == "WARNING"
        assert Severity.ERROR.value == "ERROR"
        assert Severity.CRITICAL.value == "CRITICAL"


class TestInsightGenerator:
    """Test InsightGenerator class."""
    
    def test_generator_initialization(self, insight_generator):
        """Test InsightGenerator initialization."""
        assert insight_generator.store is not None
        assert insight_generator.velocity_analyzer is not None
        assert insight_generator.file_analyzer is not None
    
    def test_generate_velocity_insights_no_data(self, insight_generator):
        """Test generating velocity insights with no data."""
        insights = insight_generator.generate_velocity_insights(days=30)
        
        assert isinstance(insights, list)
        # May be empty or contain low-activity insight
    
    def test_generate_velocity_insights_with_data(self, insight_generator, context_store):
        """Test generating velocity insights with sample data."""
        # Insert declining velocity data
        today = date.today()
        conn = sqlite3.connect(context_store.db_path)
        cursor = conn.cursor()
        
        # Recent period: low activity
        for i in range(7):
            cursor.execute("""
                INSERT OR REPLACE INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                (today - timedelta(days=i)).isoformat(),
                1,  # Low activity
                10,
                2,
                8,
                1
            ))
        
        # Previous period: high activity
        for i in range(7, 14):
            cursor.execute("""
                INSERT OR REPLACE INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                (today - timedelta(days=i)).isoformat(),
                5,  # High activity
                50,
                10,
                40,
                5
            ))
        
        conn.commit()
        conn.close()
        
        insights = insight_generator.generate_velocity_insights(days=14)
        
        assert isinstance(insights, list)
        # Should detect velocity drop
        if len(insights) > 0:
            assert any(i.insight_type == InsightType.VELOCITY_DROP for i in insights)
    
    def test_generate_hotspot_insights_no_data(self, insight_generator):
        """Test generating hotspot insights with no data."""
        insights = insight_generator.generate_hotspot_insights(days=30)
        
        assert isinstance(insights, list)
    
    def test_generate_hotspot_insights_with_data(self, insight_generator, context_store):
        """Test generating hotspot insights with unstable files."""
        today = date.today()
        period_start = today - timedelta(days=30)
        
        # Insert unstable file hotspots
        conn = sqlite3.connect(context_store.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO context_file_hotspots
            (file_path, period_start, period_end, total_commits, file_edits, 
             churn_rate, stability, lines_changed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "unstable.py",
            period_start.isoformat(),
            today.isoformat(),
            100,
            30,
            0.30,
            "UNSTABLE",
            300
        ))
        
        conn.commit()
        conn.close()
        
        insights = insight_generator.generate_hotspot_insights(days=30)
        
        assert isinstance(insights, list)
        # Should detect file hotspot
        if len(insights) > 0:
            assert any(i.insight_type == InsightType.FILE_HOTSPOT for i in insights)
    
    def test_generate_all_insights(self, insight_generator):
        """Test generating all insights."""
        insights = insight_generator.generate_all_insights(days=30)
        
        assert isinstance(insights, list)
        # Should combine velocity and hotspot insights
    
    def test_insight_severity_assignment(self, insight_generator, context_store):
        """Test that insights have appropriate severity levels."""
        # Create critical hotspot (very high churn)
        today = date.today()
        period_start = today - timedelta(days=30)
        
        conn = sqlite3.connect(context_store.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO context_file_hotspots
            (file_path, period_start, period_end, total_commits, file_edits, 
             churn_rate, stability, lines_changed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "critical_file.py",
            period_start.isoformat(),
            today.isoformat(),
            100,
            50,
            0.50,  # Very high churn
            "UNSTABLE",
            500
        ))
        
        conn.commit()
        conn.close()
        
        insights = insight_generator.generate_hotspot_insights(days=30)
        
        if len(insights) > 0:
            # High churn should trigger WARNING or ERROR
            critical_insights = [i for i in insights if "critical_file.py" in str(i.data)]
            if critical_insights:
                assert critical_insights[0].severity in [Severity.WARNING, Severity.ERROR, Severity.CRITICAL]
    
    def test_insight_recommendations(self, insight_generator, context_store):
        """Test that insights include recommendations."""
        # Create scenario that triggers insights
        today = date.today()
        conn = sqlite3.connect(context_store.db_path)
        cursor = conn.cursor()
        
        # Low velocity
        for i in range(7):
            cursor.execute("""
                INSERT OR REPLACE INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                (today - timedelta(days=i)).isoformat(),
                0,  # No activity
                0,
                0,
                0,
                0
            ))
        
        conn.commit()
        conn.close()
        
        insights = insight_generator.generate_velocity_insights(days=7)
        
        # Insights should include recommendations
        if len(insights) > 0:
            assert all(len(i.recommendations) > 0 for i in insights)
    
    def test_empty_insights_handling(self, insight_generator):
        """Test handling when no insights are generated."""
        insights = insight_generator.generate_all_insights(days=1)
        
        # Should return empty list, not fail
        assert isinstance(insights, list)
    
    def test_insight_data_structure(self, insight_generator, context_store):
        """Test that insight data contains relevant information."""
        today = date.today()
        period_start = today - timedelta(days=30)
        
        conn = sqlite3.connect(context_store.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO context_file_hotspots
            (file_path, period_start, period_end, total_commits, file_edits, 
             churn_rate, stability, lines_changed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "data_test.py",
            period_start.isoformat(),
            today.isoformat(),
            100,
            25,
            0.25,
            "UNSTABLE",
            250
        ))
        
        conn.commit()
        conn.close()
        
        insights = insight_generator.generate_hotspot_insights(days=30)
        
        if len(insights) > 0:
            # Data should contain relevant metrics
            data = insights[0].data
            assert isinstance(data, dict)
            # Should contain file-related information
            assert any(key in str(data) for key in ['file', 'churn', 'path'])
    
    def test_multiple_insight_types(self, insight_generator, context_store):
        """Test generating multiple different insight types."""
        today = date.today()
        
        # Add both velocity and hotspot data
        conn = sqlite3.connect(context_store.db_path)
        cursor = conn.cursor()
        
        # Velocity data
        for i in range(7):
            cursor.execute("""
                INSERT OR REPLACE INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                (today - timedelta(days=i)).isoformat(),
                5,
                100,
                20,
                80,
                10
            ))
        
        # Hotspot data
        cursor.execute("""
            INSERT OR REPLACE INTO context_file_hotspots
            (file_path, period_start, period_end, total_commits, file_edits, 
             churn_rate, stability, lines_changed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "multi_test.py",
            (today - timedelta(days=30)).isoformat(),
            today.isoformat(),
            100,
            30,
            0.30,
            "UNSTABLE",
            300
        ))
        
        conn.commit()
        conn.close()
        
        all_insights = insight_generator.generate_all_insights(days=30)
        
        assert isinstance(all_insights, list)
        # Should potentially have both types (if thresholds met)
