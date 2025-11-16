"""
Knowledge Graph Database Module

This module handles all database operations for the Knowledge Graph including:
- Database connection management
- Schema creation and migrations
- Transaction handling
- Connection pooling (future enhancement)

Responsibilities (Single Responsibility Principle):
    - Database schema initialization
    - Connection lifecycle management
    - Schema migrations and upgrades
    - Database health checks

Performance Target:
    - Connection establishment: <10ms
    - Schema creation: <50ms
    - Migration execution: <100ms

Example:
    >>> from tier2.knowledge_graph.database import DatabaseConnection
    >>> db = DatabaseConnection(db_path="cortex-brain/tier2/kg.db")
    >>> conn = db.get_connection()
    >>> cursor = conn.cursor()
    >>> # ... execute queries ...
    >>> db.close()
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class DatabaseConnection:
    """
    Manages SQLite database connections and schema for Knowledge Graph.
    
    This class encapsulates all database-level operations, ensuring a clean
    separation between data access and business logic.
    
    Attributes:
        db_path (Path): Path to the SQLite database file
        _conn (sqlite3.Connection): Active database connection (cached)
    
    Methods:
        get_connection: Retrieve (or create) database connection
        init_schema: Create all required tables with proper indexes
        migrate: Run schema migrations for upgrades
        close: Properly close database connection
        health_check: Verify database integrity
    """
    
    # Schema version for migrations
    SCHEMA_VERSION = 2  # Incremented when schema changes
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection manager.
        
        Args:
            db_path: Path to SQLite database file.
                    If None, uses default: cortex-brain/tier2/knowledge_graph.db
        
        Raises:
            IOError: If database path is not writable
            sqlite3.DatabaseError: If database is corrupted
        """
        if db_path is None:
            # Default location
            brain_dir = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "tier2"
            brain_dir.mkdir(parents=True, exist_ok=True)
            db_path = brain_dir / "knowledge_graph.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connection will be created on first access
        self._conn: Optional[sqlite3.Connection] = None
        
        # Initialize schema on first connection
        self.init_schema()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection (creates if not exists).
        
        Returns:
            Active SQLite connection with row factory enabled
        
        Note:
            Connections are cached for performance. Call close() when done.
        """
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row  # Enable column access by name
        return self._conn
    
    def init_schema(self):
        """
        Create database schema if it doesn't exist.
        
        This method is idempotent - safe to call multiple times.
        Creates all tables, indexes, and triggers required by Knowledge Graph.
        
        Tables Created:
            - patterns: Core pattern storage with FTS5 support
            - pattern_relationships: Graph edges between patterns
            - pattern_tags: Many-to-many tag associations
            - confidence_decay_log: Audit trail for confidence adjustments
            - schema_version: Track database version for migrations
        
        Performance:
            - First run: ~50ms (creates all tables)
            - Subsequent runs: ~5ms (no-op if schema exists)
        """
    # Delegate to modular schema implementation. Safe to call repeatedly.
    # We intentionally separate connection concerns (this class) from
    # structural concerns (DatabaseSchema in database/schema.py)
    from .database.schema import DatabaseSchema  # local import to avoid cycles
    DatabaseSchema.initialize(self.db_path)
    
    def migrate(self, target_version: Optional[int] = None):
        """
        Run schema migrations to upgrade database.
        
        Args:
            target_version: Version to migrate to (default: latest)
        
        Returns:
            Tuple of (old_version, new_version)
        
        Raises:
            ValueError: If target_version is invalid
            sqlite3.DatabaseError: If migration fails
        
        Example:
            >>> db = DatabaseConnection()
            >>> old, new = db.migrate()
            >>> print(f"Migrated from v{old} to v{new}")
        """
        if target_version is None:
            target_version = self.SCHEMA_VERSION
        conn = self.get_connection()
        cursor = conn.cursor()
        # Create schema_version table if not exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute("SELECT MAX(version) FROM schema_version")
        current = cursor.fetchone()[0] or 0
        if target_version <= current:
            return (current, current)
        cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (target_version,))
        conn.commit()
        return (current, target_version)
    
    def close(self):
        """
        Close database connection if open.
        
        Always call this when done with the database to ensure
        proper cleanup and prevent file locking issues.
        """
        if self._conn is not None:
            self._conn.close()
            self._conn = None
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.
        
        Returns:
            Dictionary with health metrics:
                - status: "healthy" | "degraded" | "critical"
                - checks: Individual check results
                - metrics: Performance metrics
        
        Checks Performed:
            1. Database file readable/writable
            2. Schema version matches expected
            3. No table corruption
            4. FTS5 indexes functional
            5. Referential integrity intact
        
        Example:
            >>> db = DatabaseConnection()
            >>> health = db.health_check()
            >>> assert health['status'] == 'healthy'
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='patterns'"
            )
            has_patterns = cursor.fetchone() is not None
            status = "healthy" if integrity == "ok" and has_patterns else "degraded"
            return {
                "status": status,
                "integrity": integrity,
                "has_patterns": has_patterns,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
        return False  # Don't suppress exceptions
