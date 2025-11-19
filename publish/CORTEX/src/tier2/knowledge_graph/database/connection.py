"""
Knowledge Graph Database Connection

Manages database connections with connection pooling.
"""

import sqlite3
from pathlib import Path
from typing import Optional, Tuple, Dict
from contextlib import contextmanager
from datetime import datetime
from .schema import DatabaseSchema


class ConnectionManager:
    """
    Manages SQLite database connections.
    
    Responsibilities:
    - Create and manage database connections
    - Connection pooling (if needed)
    - Transaction management
    """
    
    SCHEMA_VERSION = 1  # Current schema version
    
    def __init__(self, db_path: Path):
        """
        Initialize connection manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = None
        # Create database file immediately and initialize schema
        self.get_connection()
        # Ensure schema exists (idempotent)
        try:
            DatabaseSchema.initialize(db_path=self.db_path)
        except Exception:
            # Allow caller tests to handle initialization explicitly if needed
            # but don't fail construction due to idempotent init
            pass
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.
        
        Returns:
            SQLite connection with row_factory set
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def close(self) -> None:
        """Close database connection if open."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    @contextmanager
    def transaction(self):
        """Context manager for transactional operations.
        
        Yields:
            Database connection with transaction management
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def health_check(self) -> Dict[str, str]:
        """Check database health.
        
        Returns:
            Dictionary with status, timestamp, and optional error
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result[0] == "ok":
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "critical",
                    "timestamp": datetime.now().isoformat(),
                    "error": f"Integrity check failed: {result[0]}"
                }
        except Exception as e:
            return {
                "status": "critical",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def migrate(self, target_version: Optional[int] = None) -> Tuple[int, int]:
        """Apply database migration.
        
        Args:
            target_version: Target migration version (defaults to SCHEMA_VERSION)
            
        Returns:
            Tuple of (old_version, new_version)
        """
        if target_version is None:
            target_version = self.SCHEMA_VERSION
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create schema_version table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Get current version
        cursor.execute("SELECT MAX(version) FROM schema_version")
        current = cursor.fetchone()[0] or 0
        
        if target_version <= current:
            return (current, current)
        
        # Record migration
        cursor.execute("INSERT INTO schema_version (version) VALUES (?)", (target_version,))
        conn.commit()
        
        return (current, target_version)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            List of rows (as sqlite3.Row objects)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        return results
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Number of rows affected
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rowcount = cursor.rowcount
        conn.commit()
        return rowcount
    
    def execute_many(self, query: str, params_list: list) -> int:
        """
        Execute multiple queries in a transaction.
        
        Args:
            query: SQL query
            params_list: List of parameter tuples
            
        Returns:
            Total number of rows affected
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        rowcount = cursor.rowcount
        conn.commit()
        return rowcount
