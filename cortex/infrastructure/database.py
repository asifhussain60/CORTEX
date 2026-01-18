"""
Database Manager - SQLite Governance Database (AR-002)

Production-grade SQLite database for:
- AC-ID tracking and status (ac_index)
- Audit log storage with hash chain (audit_log)
- Phase lock enforcement (phase_locks)

Features:
- WAL mode for concurrent access
- SHA-256 hash chain for audit integrity
- Query performance <1ms
- Result[T] pattern for error handling

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import hashlib
import json
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.brain.core.path_resolver import resolve_path
from cortex.brain.core.result import Result, Ok, Err


@dataclass
class DatabaseConfig:
    """Configuration for database manager."""
    db_path: Path = field(default_factory=lambda: resolve_path("cortex-brain", "state", "governance.db"))
    wal_mode: bool = True
    timeout: float = 30.0


class DatabaseManager:
    """
    SQLite database manager for governance data.
    
    Thread-safe with connection pooling per thread.
    Implements hash chain for audit log integrity.
    
    AC-FIX-BRITTLENESS-001: Added context manager support for connection lifecycle.
    """
    
    _local = threading.local()
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database manager.
        
        Args:
            config: Database configuration (uses defaults if None)
        """
        self.config = config or DatabaseConfig()
        self._last_audit_hash: Optional[str] = None
        self._lock = threading.Lock()
        self._closed = False
    
    @property
    def _connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = self._create_connection()
        return self._local.connection
    
    @contextmanager
    def get_connection(self):
        """
        Get a database connection as a context manager.
        
        AC-FIX-BRITTLENESS-001: Ensures connections are properly managed.
        
        Usage:
            with db.get_connection() as conn:
                conn.execute("SELECT 1")
        
        Yields:
            sqlite3.Connection: Active database connection
        """
        conn = self._connection
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
    
    def close(self) -> None:
        """
        Close database connections and release resources.
        
        AC-FIX-BRITTLENESS-001: Explicit cleanup method.
        """
        self._closed = True
        if hasattr(self._local, 'connection') and self._local.connection is not None:
            try:
                self._local.connection.close()
            except Exception:
                pass
            self._local.connection = None
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        # Ensure directory exists
        self.config.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(
            str(self.config.db_path),
            timeout=self.config.timeout,
            check_same_thread=False
        )
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Set WAL mode if configured
        if self.config.wal_mode:
            conn.execute("PRAGMA journal_mode = WAL")
        
        # Optimize for performance
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize(self) -> Result[None]:
        """
        Initialize database schema.
        
        Creates all required tables if they don't exist.
        
        Returns:
            Result indicating success or error
        """
        try:
            conn = self._connection
            
            # Create ac_index table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ac_index (
                    ac_id TEXT PRIMARY KEY,
                    phase TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING',
                    title TEXT NOT NULL,
                    description TEXT,
                    test_file TEXT,
                    evidence_hash TEXT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
            
            # Create index for phase queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ac_phase ON ac_index(phase)
            """)
            
            # Create index for status queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ac_status ON ac_index(status)
            """)
            
            # Create audit_log table with hash chain
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                    operation TEXT NOT NULL,
                    component TEXT NOT NULL,
                    level TEXT NOT NULL DEFAULT 'INFO',
                    message TEXT NOT NULL,
                    ac_id TEXT,
                    correlation_id TEXT,
                    metadata TEXT,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE
                )
            """)
            
            # Create indexes for audit queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_ac_id ON audit_log(ac_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_operation ON audit_log(operation)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)
            """)
            
            # Create phase_locks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS phase_locks (
                    phase_id TEXT PRIMARY KEY,
                    locked INTEGER NOT NULL DEFAULT 0,
                    locked_at TEXT,
                    locked_by TEXT,
                    git_checkpoint TEXT,
                    audit_verified INTEGER NOT NULL DEFAULT 0,
                    audit_entry_count INTEGER,
                    verified_at TEXT
                )
            """)
            
            conn.commit()
            
            # Initialize last audit hash
            self._init_last_audit_hash()
            
            return Ok(None)
            
        except sqlite3.Error as e:
            return Err(f"Database initialization failed: {e}")
    
    def _init_last_audit_hash(self) -> None:
        """Initialize last audit hash from existing entries."""
        cursor = self._connection.execute(
            "SELECT entry_hash FROM audit_log ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        self._last_audit_hash = row[0] if row else None
    
    def execute(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> Result[List[Tuple]]:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            Result containing list of rows or error
        """
        try:
            cursor = self._connection.execute(query, params or ())
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE", "CREATE")):
                self._connection.commit()
                return Ok([])
            return Ok(cursor.fetchall())
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
    
    def close(self) -> None:
        """
        Close the database connection.
        
        Properly cleans up thread-local connection resource.
        Safe to call multiple times.
        """
        try:
            if hasattr(self._local, 'connection') and self._local.connection:
                try:
                    self._local.connection.close()
                except sqlite3.Error:
                    pass  # Already closed or error closing
                finally:
                    self._local.connection = None
        except Exception:
            pass  # Ensure close never raises
    
    def __enter__(self) -> "DatabaseManager":
        """
        Context manager entry.
        
        Returns:
            self for use in with statement
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Context manager exit - closes connection.
        
        Args:
            exc_type: Exception type if one occurred
            exc_val: Exception value if one occurred
            exc_tb: Exception traceback if one occurred
        
        Returns:
            False to propagate exceptions
        """
        self.close()
        return False
    
    # =========================================================================
    # AC-ID Operations
    # =========================================================================
    
    def insert_ac(
        self,
        ac_id: str,
        phase: str,
        title: str,
        description: Optional[str] = None,
        test_file: Optional[str] = None
    ) -> Result[None]:
        """
        Insert a new AC-ID record.
        
        Args:
            ac_id: Acceptance criteria ID (e.g., "AC-AR-001-01")
            phase: Phase ID (e.g., "PHASE-01")
            title: AC title/description
            description: Optional detailed description
            test_file: Optional path to test file
        
        Returns:
            Result indicating success or error
        """
        try:
            self._connection.execute(
                """
                INSERT INTO ac_index (ac_id, phase, title, description, test_file)
                VALUES (?, ?, ?, ?, ?)
                """,
                (ac_id, phase, title, description, test_file)
            )
            self._connection.commit()
            return Ok(None)
        except sqlite3.IntegrityError:
            return Err(f"AC-ID already exists: {ac_id}")
        except sqlite3.Error as e:
            return Err(f"Insert failed: {e}")
    
    def get_ac(self, ac_id: str) -> Result[Dict[str, Any]]:
        """
        Get AC-ID record by ID.
        
        Args:
            ac_id: Acceptance criteria ID
        
        Returns:
            Result containing AC record dict or error
        """
        try:
            cursor = self._connection.execute(
                "SELECT * FROM ac_index WHERE ac_id = ?",
                (ac_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return Err(f"AC-ID not found: {ac_id}")
            return Ok(dict(row))
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
    
    def update_ac_status(
        self,
        ac_id: str,
        status: str,
        evidence_hash: Optional[str] = None
    ) -> Result[None]:
        """
        Update AC-ID status.
        
        Args:
            ac_id: Acceptance criteria ID
            status: New status (PENDING, IN_PROGRESS, COMPLETED, VERIFIED)
            evidence_hash: Optional hash of evidence bundle
        
        Returns:
            Result indicating success or error
        """
        valid_statuses = {"PENDING", "IN_PROGRESS", "BLOCKED", "COMPLETED", "VERIFIED"}
        if status not in valid_statuses:
            return Err(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        try:
            if evidence_hash:
                self._connection.execute(
                    """
                    UPDATE ac_index 
                    SET status = ?, evidence_hash = ?, updated_at = datetime('now')
                    WHERE ac_id = ?
                    """,
                    (status, evidence_hash, ac_id)
                )
            else:
                self._connection.execute(
                    """
                    UPDATE ac_index 
                    SET status = ?, updated_at = datetime('now')
                    WHERE ac_id = ?
                    """,
                    (status, ac_id)
                )
            self._connection.commit()
            return Ok(None)
        except sqlite3.Error as e:
            return Err(f"Update failed: {e}")
    
    def ac_exists(self, ac_id: str) -> Result[bool]:
        """
        Check if AC-ID exists.
        
        Args:
            ac_id: Acceptance criteria ID
        
        Returns:
            Result containing True if exists, False otherwise
        """
        try:
            cursor = self._connection.execute(
                "SELECT 1 FROM ac_index WHERE ac_id = ? LIMIT 1",
                (ac_id,)
            )
            return Ok(cursor.fetchone() is not None)
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
    
    def get_acs_by_phase(self, phase: str) -> Result[List[Dict[str, Any]]]:
        """
        Get all AC-IDs for a phase.
        
        Args:
            phase: Phase ID
        
        Returns:
            Result containing list of AC records
        """
        try:
            cursor = self._connection.execute(
                "SELECT * FROM ac_index WHERE phase = ? ORDER BY ac_id",
                (phase,)
            )
            return Ok([dict(row) for row in cursor.fetchall()])
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
    
    # =========================================================================
    # Phase Lock Operations
    # =========================================================================
    
    def lock_phase(
        self,
        phase_id: str,
        locked_by: str,
        git_checkpoint: Optional[str] = None,
        audit_entry_count: Optional[int] = None
    ) -> Result[None]:
        """
        Lock a phase to prevent reimplementation.
        
        Args:
            phase_id: Phase ID to lock
            locked_by: Identifier of who/what locked the phase
            git_checkpoint: Git commit hash at lock time
            audit_entry_count: Number of audit entries at lock time
        
        Returns:
            Result indicating success or error
        """
        try:
            self._connection.execute(
                """
                INSERT INTO phase_locks (phase_id, locked, locked_at, locked_by, git_checkpoint, audit_entry_count)
                VALUES (?, 1, datetime('now'), ?, ?, ?)
                ON CONFLICT(phase_id) DO UPDATE SET
                    locked = 1,
                    locked_at = datetime('now'),
                    locked_by = excluded.locked_by,
                    git_checkpoint = excluded.git_checkpoint,
                    audit_entry_count = excluded.audit_entry_count
                """,
                (phase_id, locked_by, git_checkpoint, audit_entry_count)
            )
            self._connection.commit()
            return Ok(None)
        except sqlite3.Error as e:
            return Err(f"Lock failed: {e}")
    
    def is_phase_locked(self, phase_id: str) -> Result[bool]:
        """
        Check if a phase is locked.
        
        Args:
            phase_id: Phase ID to check
        
        Returns:
            Result containing True if locked, False otherwise
        """
        try:
            cursor = self._connection.execute(
                "SELECT locked FROM phase_locks WHERE phase_id = ?",
                (phase_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return Ok(False)  # Non-existent phases are not locked
            return Ok(bool(row[0]))
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
    
    def get_phase_lock_info(self, phase_id: str) -> Result[Optional[Dict[str, Any]]]:
        """
        Get phase lock information.
        
        Args:
            phase_id: Phase ID
        
        Returns:
            Result containing lock info dict or None if not found
        """
        try:
            cursor = self._connection.execute(
                "SELECT * FROM phase_locks WHERE phase_id = ?",
                (phase_id,)
            )
            row = cursor.fetchone()
            if row is None:
                return Ok(None)
            return Ok(dict(row))
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
    
    # =========================================================================
    # Audit Log Operations (Hash Chain)
    # =========================================================================
    
    def insert_audit(
        self,
        operation: str,
        component: str,
        level: str,
        message: str,
        ac_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Result[str]:
        """
        Insert audit log entry with hash chain.
        
        Args:
            operation: Operation type (e.g., "AC_START", "AC_COMPLETE")
            component: Component name
            level: Log level (INFO, WARNING, ERROR)
            message: Log message
            ac_id: Optional AC-ID reference
            correlation_id: Optional correlation ID
            metadata: Optional metadata dict
        
        Returns:
            Result containing entry hash or error
        """
        try:
            with self._lock:
                timestamp = datetime.now(timezone.utc).isoformat()
                
                # Get previous hash
                previous_hash = self._last_audit_hash or "GENESIS"
                
                # Compute entry hash
                hash_input = f"{timestamp}|{operation}|{component}|{message}|{previous_hash}"
                entry_hash = hashlib.sha256(hash_input.encode()).hexdigest()
                
                # Serialize metadata
                metadata_json = json.dumps(metadata) if metadata else None
                
                self._connection.execute(
                    """
                    INSERT INTO audit_log 
                    (timestamp, operation, component, level, message, ac_id, 
                     correlation_id, metadata, previous_hash, entry_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (timestamp, operation, component, level, message, ac_id,
                     correlation_id, metadata_json, previous_hash, entry_hash)
                )
                self._connection.commit()
                
                # Update last hash
                self._last_audit_hash = entry_hash
                
                return Ok(entry_hash)
                
        except sqlite3.Error as e:
            return Err(f"Audit insert failed: {e}")
    
    def query_audit_by_ac_id(self, ac_id: str) -> Result[List[Dict[str, Any]]]:
        """
        Query audit entries for an AC-ID.
        
        Args:
            ac_id: Acceptance criteria ID
        
        Returns:
            Result containing list of audit entries
        """
        try:
            cursor = self._connection.execute(
                "SELECT * FROM audit_log WHERE ac_id = ? ORDER BY id",
                (ac_id,)
            )
            return Ok([dict(row) for row in cursor.fetchall()])
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
    
    def verify_hash_chain(self) -> Result[bool]:
        """
        Verify audit log hash chain integrity.
        
        Returns:
            Result containing True if valid, False if tampered
        """
        try:
            cursor = self._connection.execute(
                "SELECT timestamp, operation, component, message, previous_hash, entry_hash "
                "FROM audit_log ORDER BY id"
            )
            
            expected_prev = "GENESIS"
            for row in cursor:
                timestamp, operation, component, message, prev_hash, entry_hash = row
                
                # Verify previous hash links
                if prev_hash != expected_prev:
                    return Ok(False)
                
                # Verify entry hash
                hash_input = f"{timestamp}|{operation}|{component}|{message}|{prev_hash}"
                computed_hash = hashlib.sha256(hash_input.encode()).hexdigest()
                if computed_hash != entry_hash:
                    return Ok(False)
                
                expected_prev = entry_hash
            
            return Ok(True)
            
        except sqlite3.Error as e:
            return Err(f"Verification failed: {e}")
    
    def get_audit_count_for_phase(self, phase_prefix: str) -> Result[int]:
        """
        Count audit entries for AC-IDs in a phase.
        
        Args:
            phase_prefix: AC-ID prefix pattern (e.g., "AC-AR-001" for PHASE-01)
        
        Returns:
            Result containing count of audit entries
        """
        try:
            cursor = self._connection.execute(
                "SELECT COUNT(*) FROM audit_log WHERE ac_id LIKE ?",
                (f"{phase_prefix}%",)
            )
            return Ok(cursor.fetchone()[0])
        except sqlite3.Error as e:
            return Err(f"Query failed: {e}")
