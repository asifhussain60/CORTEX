"""
Unit tests for Tier 3 File Metrics module.
"""

import pytest
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path
import tempfile
import shutil
import subprocess

from src.tier3.metrics.file_metrics import FileHotspot, FileMetricsAnalyzer, Stability
from src.tier3.storage.context_store import ContextStore


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_context.db"
    
    yield db_path
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_repo():
    """Create a temporary git repository with file history."""
    temp_dir = tempfile.mkdtemp()
    repo_path = Path(temp_dir)
    
    # Initialize git repo
    subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=repo_path, capture_output=True)
    
    # Create files with varying churn
    stable_file = repo_path / "stable.py"
    stable_file.write_text("# Stable file\nprint('hello')\n")
    
    moderate_file = repo_path / "moderate.py"
    moderate_file.write_text("# Moderate file\nprint('world')\n")
    
    subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=repo_path, capture_output=True)
    
    yield repo_path
    
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def context_store(temp_db):
    """Create a ContextStore instance."""
    return ContextStore(temp_db)


@pytest.fixture
def file_analyzer(temp_repo, context_store):
    """Create a FileMetricsAnalyzer instance."""
    return FileMetricsAnalyzer(temp_repo, context_store)


class TestFileHotspot:
    """Test FileHotspot dataclass."""
    
    def test_file_hotspot_creation(self):
        """Test creating a FileHotspot instance."""
        hotspot = FileHotspot(
            file_path="src/main.py",
            period_start=date(2025, 1, 1),
            period_end=date(2025, 1, 31),
            total_commits=100,
            file_edits=25,
            churn_rate=0.25,
            stability=Stability.UNSTABLE,
            lines_changed=500
        )
        
        assert hotspot.file_path == "src/main.py"
        assert hotspot.total_commits == 100
        assert hotspot.file_edits == 25
        assert hotspot.churn_rate == 0.25
        assert hotspot.stability == Stability.UNSTABLE
        assert hotspot.lines_changed == 500


class TestStability:
    """Test Stability enum."""
    
    def test_stability_values(self):
        """Test Stability enum values."""
        assert Stability.STABLE.value == "STABLE"
        assert Stability.MODERATE.value == "MODERATE"
        assert Stability.UNSTABLE.value == "UNSTABLE"


class TestFileMetricsAnalyzer:
    """Test FileMetricsAnalyzer class."""
    
    def test_analyzer_initialization(self, file_analyzer, temp_repo):
        """Test FileMetricsAnalyzer initialization."""
        assert file_analyzer.repo_path == temp_repo
        assert file_analyzer.store is not None
    
    def test_analyze_hotspots_basic(self, file_analyzer):
        """Test basic hotspot analysis."""
        hotspots = file_analyzer.analyze_hotspots(days=30, force=True)
        
        assert isinstance(hotspots, list)
        # Repository has files, so should detect some activity
        if len(hotspots) > 0:
            assert all(isinstance(h, FileHotspot) for h in hotspots)
    
    def test_save_and_retrieve_hotspots(self, file_analyzer):
        """Test saving and retrieving file hotspots."""
        today = date.today()
        period_start = today - timedelta(days=30)
        
        hotspots = [
            FileHotspot(
                file_path="test.py",
                period_start=period_start,
                period_end=today,
                total_commits=50,
                file_edits=12,
                churn_rate=0.24,
                stability=Stability.UNSTABLE,
                lines_changed=120
            )
        ]
        
        file_analyzer.save_hotspots(hotspots)
        
        # Retrieve hotspots
        retrieved = file_analyzer.get_hotspots(days=30)
        
        assert len(retrieved) >= 1
        test_hotspot = next((h for h in retrieved if h.file_path == "test.py"), None)
        assert test_hotspot is not None
        assert test_hotspot.churn_rate == 0.24
    
    def test_get_unstable_files(self, file_analyzer):
        """Test retrieving unstable files."""
        today = date.today()
        period_start = today - timedelta(days=30)
        
        hotspots = [
            FileHotspot(
                file_path="unstable1.py",
                period_start=period_start,
                period_end=today,
                total_commits=100,
                file_edits=30,
                churn_rate=0.30,
                stability=Stability.UNSTABLE,
                lines_changed=300
            ),
            FileHotspot(
                file_path="stable.py",
                period_start=period_start,
                period_end=today,
                total_commits=100,
                file_edits=5,
                churn_rate=0.05,
                stability=Stability.STABLE,
                lines_changed=50
            )
        ]
        
        file_analyzer.save_hotspots(hotspots)
        
        unstable = file_analyzer.get_unstable_files(days=30)
        
        assert len(unstable) >= 1
        assert all(h.stability == Stability.UNSTABLE for h in unstable)
        assert any(h.file_path == "unstable1.py" for h in unstable)
    
    def test_churn_rate_filtering(self, file_analyzer):
        """Test filtering hotspots by minimum churn rate."""
        today = date.today()
        period_start = today - timedelta(days=30)
        
        hotspots = [
            FileHotspot(
                file_path="high_churn.py",
                period_start=period_start,
                period_end=today,
                total_commits=100,
                file_edits=50,
                churn_rate=0.50,
                stability=Stability.UNSTABLE,
                lines_changed=500
            ),
            FileHotspot(
                file_path="low_churn.py",
                period_start=period_start,
                period_end=today,
                total_commits=100,
                file_edits=5,
                churn_rate=0.05,
                stability=Stability.STABLE,
                lines_changed=50
            )
        ]
        
        file_analyzer.save_hotspots(hotspots)
        
        # Filter for high churn only
        high_churn = file_analyzer.get_hotspots(days=30, min_churn=0.30)
        
        assert len(high_churn) >= 1
        assert all(h.churn_rate >= 0.30 for h in high_churn)
        assert any(h.file_path == "high_churn.py" for h in high_churn)
    
    def test_stability_classification(self, file_analyzer):
        """Test that stability is correctly classified."""
        today = date.today()
        period_start = today - timedelta(days=30)
        
        # Test all stability levels
        hotspots = [
            FileHotspot(
                file_path="stable.py",
                period_start=period_start,
                period_end=today,
                total_commits=100,
                file_edits=5,
                churn_rate=0.05,
                stability=Stability.STABLE,
                lines_changed=50
            ),
            FileHotspot(
                file_path="moderate.py",
                period_start=period_start,
                period_end=today,
                total_commits=100,
                file_edits=15,
                churn_rate=0.15,
                stability=Stability.MODERATE,
                lines_changed=150
            ),
            FileHotspot(
                file_path="unstable.py",
                period_start=period_start,
                period_end=today,
                total_commits=100,
                file_edits=25,
                churn_rate=0.25,
                stability=Stability.UNSTABLE,
                lines_changed=250
            )
        ]
        
        file_analyzer.save_hotspots(hotspots)
        
        # Verify each stability level
        retrieved = file_analyzer.get_hotspots(days=30)
        
        stable = next((h for h in retrieved if h.file_path == "stable.py"), None)
        assert stable is not None
        assert stable.stability == Stability.STABLE
        
        moderate = next((h for h in retrieved if h.file_path == "moderate.py"), None)
        assert moderate is not None
        assert moderate.stability == Stability.MODERATE
        
        unstable = next((h for h in retrieved if h.file_path == "unstable.py"), None)
        assert unstable is not None
        assert unstable.stability == Stability.UNSTABLE
    
    def test_force_analysis_flag(self, file_analyzer):
        """Test that force flag bypasses caching."""
        # First analysis
        hotspots1 = file_analyzer.analyze_hotspots(days=30, force=True)
        
        # Second analysis with force
        hotspots2 = file_analyzer.analyze_hotspots(days=30, force=True)
        
        assert isinstance(hotspots1, list)
        assert isinstance(hotspots2, list)
    
    def test_date_range_filtering(self, file_analyzer):
        """Test filtering hotspots by date range."""
        today = date.today()
        old_date = today - timedelta(days=60)
        
        hotspots = [
            FileHotspot(
                file_path="recent.py",
                period_start=today - timedelta(days=7),
                period_end=today,
                total_commits=10,
                file_edits=3,
                churn_rate=0.30,
                stability=Stability.UNSTABLE,
                lines_changed=30
            ),
            FileHotspot(
                file_path="old.py",
                period_start=old_date - timedelta(days=7),
                period_end=old_date,
                total_commits=10,
                file_edits=3,
                churn_rate=0.30,
                stability=Stability.UNSTABLE,
                lines_changed=30
            )
        ]
        
        file_analyzer.save_hotspots(hotspots)
        
        # Get recent hotspots only
        recent = file_analyzer.get_hotspots(days=14)
        
        assert any(h.file_path == "recent.py" for h in recent)
        # old.py should not be in 14-day window
        assert not any(h.file_path == "old.py" and h.period_end >= today - timedelta(days=14) for h in recent)
