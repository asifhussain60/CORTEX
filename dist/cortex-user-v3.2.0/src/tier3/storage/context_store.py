"""
CORTEX Tier 3: Context Store
Handles database initialization and schema management.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class ContextStore:
    """
    Manages context intelligence database schema and connections.
    
    Features:
    - Database initialization
    - Schema creation and migration
    - Index management
    - Connection handling
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize context store.
        
        Args:
            db_path: Path to SQLite database (default: cortex-brain/tier3/context.db)
        """
        if db_path is None:
            brain_dir = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "tier3"
            brain_dir.mkdir(parents=True, exist_ok=True)
            db_path = brain_dir / "context.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
    
    def _init_database(self):
        """Create database schema with all tables and indexes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Git metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_git_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                commits_count INTEGER NOT NULL DEFAULT 0,
                lines_added INTEGER NOT NULL DEFAULT 0,
                lines_deleted INTEGER NOT NULL DEFAULT 0,
                net_growth INTEGER NOT NULL DEFAULT 0,
                files_changed INTEGER NOT NULL DEFAULT 0,
                contributor TEXT,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date, contributor)
            )
        """)
        
        # Indexes for git metrics
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_git_date 
            ON context_git_metrics(metric_date DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_git_contributor 
            ON context_git_metrics(contributor)
        """)
        
        # File hotspots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_file_hotspots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                total_commits INTEGER NOT NULL DEFAULT 0,
                file_edits INTEGER NOT NULL DEFAULT 0,
                churn_rate REAL NOT NULL CHECK(churn_rate >= 0.0 AND churn_rate <= 1.0),
                stability TEXT NOT NULL CHECK(stability IN ('STABLE', 'MODERATE', 'UNSTABLE')),
                last_modified TIMESTAMP,
                lines_changed INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_path, period_start, period_end)
            )
        """)
        
        # Indexes for hotspots
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hotspot_file 
            ON context_file_hotspots(file_path)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hotspot_churn 
            ON context_file_hotspots(churn_rate DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hotspot_stability 
            ON context_file_hotspots(stability)
        """)
        
        # Test metrics table (for future expansion)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_test_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                test_type TEXT NOT NULL,
                tests_discovered INTEGER NOT NULL DEFAULT 0,
                tests_run INTEGER NOT NULL DEFAULT 0,
                tests_passed INTEGER NOT NULL DEFAULT 0,
                tests_failed INTEGER NOT NULL DEFAULT 0,
                tests_skipped INTEGER NOT NULL DEFAULT 0,
                pass_rate REAL NOT NULL CHECK(pass_rate >= 0.0 AND pass_rate <= 1.0),
                coverage_percentage REAL CHECK(coverage_percentage >= 0.0 AND coverage_percentage <= 100.0),
                avg_duration_seconds REAL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date, test_type)
            )
        """)
        
        # Build metrics table (for future expansion)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS context_build_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_date DATE NOT NULL,
                builds_total INTEGER NOT NULL DEFAULT 0,
                builds_successful INTEGER NOT NULL DEFAULT 0,
                builds_failed INTEGER NOT NULL DEFAULT 0,
                success_rate REAL NOT NULL CHECK(success_rate >= 0.0 AND success_rate <= 1.0),
                avg_build_time_seconds REAL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(metric_date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.
        
        Returns:
            SQLite connection object
        """
        return sqlite3.connect(self.db_path)
    
    def vacuum(self):
        """Vacuum the database to reclaim space and optimize performance."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("VACUUM")
        conn.close()
    
    def analyze(self):
        """Analyze the database to update statistics for query optimization."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("ANALYZE")
        conn.close()
    
    def get_database_size(self) -> int:
        """
        Get database file size in bytes.
        
        Returns:
            Size in bytes
        """
        return self.db_path.stat().st_size if self.db_path.exists() else 0
    
    def get_table_counts(self) -> dict:
        """
        Get row counts for all tables.
        
        Returns:
            Dictionary of table names to row counts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        counts = {}
        tables = ['context_git_metrics', 'context_file_hotspots', 
                 'context_test_metrics', 'context_build_metrics']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        conn.close()
        return counts
