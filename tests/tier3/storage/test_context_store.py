"""
Unit tests for Tier 3 Context Store module.
"""

import pytest
import sqlite3
from pathlib import Path
import tempfile
import shutil

from src.tier3.storage.context_store import ContextStore


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


class TestContextStore:
    """Test ContextStore class."""
    
    def test_store_initialization(self, context_store, temp_db):
        """Test ContextStore initialization."""
        assert context_store.db_path == temp_db
        assert context_store.db_path.exists()
    
    def test_database_tables_created(self, context_store):
        """Test that all required tables are created."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        # Check for required tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'context_git_metrics' in tables
        assert 'context_file_hotspots' in tables
        assert 'context_test_metrics' in tables
        assert 'context_build_metrics' in tables
        
        conn.close()
    
    def test_git_metrics_schema(self, context_store):
        """Test git metrics table schema."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(context_git_metrics)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'metric_date' in columns
        assert 'commits_count' in columns
        assert 'lines_added' in columns
        assert 'lines_deleted' in columns
        assert 'net_growth' in columns
        assert 'files_changed' in columns
        assert 'contributor' in columns
        
        conn.close()
    
    def test_file_hotspots_schema(self, context_store):
        """Test file hotspots table schema."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(context_file_hotspots)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'file_path' in columns
        assert 'period_start' in columns
        assert 'period_end' in columns
        assert 'total_commits' in columns
        assert 'file_edits' in columns
        assert 'churn_rate' in columns
        assert 'stability' in columns
        assert 'lines_changed' in columns
        
        conn.close()
    
    def test_indexes_created(self, context_store):
        """Test that indexes are created for performance."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' 
            ORDER BY name
        """)
        
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Check for key indexes
        assert any('git_date' in idx for idx in indexes)
        assert any('hotspot_file' in idx or 'file' in idx for idx in indexes)
        
        conn.close()
    
    def test_get_connection(self, context_store):
        """Test getting database connection."""
        conn = context_store.get_connection()
        
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        
        conn.close()
    
    def test_vacuum(self, context_store):
        """Test vacuuming database."""
        # Should not raise exception
        context_store.vacuum()
    
    def test_analyze(self, context_store):
        """Test analyzing database."""
        # Should not raise exception
        context_store.analyze()
    
    def test_get_database_size(self, context_store):
        """Test getting database size."""
        size = context_store.get_database_size()
        
        assert isinstance(size, int)
        assert size > 0  # Should have some size after schema creation
    
    def test_get_table_counts(self, context_store):
        """Test getting table row counts."""
        counts = context_store.get_table_counts()
        
        assert isinstance(counts, dict)
        assert 'context_git_metrics' in counts
        assert 'context_file_hotspots' in counts
        assert 'context_test_metrics' in counts
        assert 'context_build_metrics' in counts
        
        # Initially should be zero
        assert all(isinstance(count, int) for count in counts.values())
    
    def test_unique_constraints(self, context_store):
        """Test unique constraints on tables."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        # Try inserting duplicate git metric
        cursor.execute("""
            INSERT INTO context_git_metrics
            (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed, contributor)
            VALUES ('2025-01-15', 5, 100, 20, 80, 3, 'test@example.com')
        """)
        
        # Try inserting same metric again - should fail
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO context_git_metrics
                (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed, contributor)
                VALUES ('2025-01-15', 5, 100, 20, 80, 3, 'test@example.com')
            """)
        
        conn.close()
    
    def test_check_constraints(self, context_store):
        """Test check constraints on tables."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        # Try inserting invalid churn_rate (must be 0.0-1.0)
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO context_file_hotspots
                (file_path, period_start, period_end, total_commits, file_edits, 
                 churn_rate, stability, lines_changed)
                VALUES ('test.py', '2025-01-01', '2025-01-31', 100, 25, 1.5, 'UNSTABLE', 250)
            """)
        
        # Try inserting invalid stability
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO context_file_hotspots
                (file_path, period_start, period_end, total_commits, file_edits, 
                 churn_rate, stability, lines_changed)
                VALUES ('test.py', '2025-01-01', '2025-01-31', 100, 25, 0.25, 'INVALID', 250)
            """)
        
        conn.close()
    
    def test_default_values(self, context_store):
        """Test default values in tables."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        # Insert minimal git metric
        cursor.execute("""
            INSERT INTO context_git_metrics (metric_date)
            VALUES ('2025-01-15')
        """)
        
        cursor.execute("""
            SELECT commits_count, lines_added, lines_deleted, net_growth, files_changed
            FROM context_git_metrics
            WHERE metric_date = '2025-01-15'
        """)
        
        row = cursor.fetchone()
        
        # Should have default values of 0
        assert row[0] == 0  # commits_count
        assert row[1] == 0  # lines_added
        assert row[2] == 0  # lines_deleted
        assert row[3] == 0  # net_growth
        assert row[4] == 0  # files_changed
        
        conn.close()
    
    def test_timestamp_columns(self, context_store):
        """Test that timestamp columns are populated."""
        conn = context_store.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO context_git_metrics
            (metric_date, commits_count, lines_added, lines_deleted, net_growth, files_changed)
            VALUES ('2025-01-15', 5, 100, 20, 80, 3)
        """)
        
        cursor.execute("""
            SELECT created_at FROM context_git_metrics
            WHERE metric_date = '2025-01-15'
        """)
        
        row = cursor.fetchone()
        assert row[0] is not None  # created_at should be set
        
        conn.close()
