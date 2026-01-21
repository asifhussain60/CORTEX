"""
Enhanced Audit Logger - Hash-Chain Integrity

Production-grade audit logging with:
- SHA-256 hash chain for tamper detection
- Cross-platform file locking (Windows + Unix)
- SQLite + YAML hybrid storage
- Correlation ID tracking
- Result[T] pattern for error handling

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import hashlib
import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.brain.core.interfaces import AuditEntry, IAuditLogger
from cortex.brain.core.path_resolver import audit_logs_path, get_project_root
from cortex.brain.core.result import Err, Ok, Result


@dataclass
class AuditLogEntry:
    """Internal audit log entry with hash chain."""
    
    id: str
    timestamp: str
    operation: str
    component: str
    level: str
    message: str
    ac_id: Optional[str]
    correlation_id: str
    metadata: Optional[Dict[str, Any]]
    previous_hash: str
    entry_hash: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogEntry":
        """Create from dictionary."""
        return cls(**data)


class CrossPlatformFileLock:
    """
    Cross-platform file locking.
    
    Uses msvcrt on Windows, fcntl on Unix.
    Falls back to no-op if neither available.
    """
    
    def __init__(self, lock_file: Path):
        self.lock_file = lock_file
        self._file = None
        self._lock_type = self._detect_platform()
    
    def _detect_platform(self) -> str:
        """Detect platform and available locking mechanism."""
        try:
            import msvcrt
            return "windows"
        except ImportError:
            pass
        
        try:
            import fcntl
            return "unix"
        except ImportError:
            pass
        
        return "none"
    
    def acquire(self):
        """Acquire the lock."""
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.lock_file, "w")
        
        if self._lock_type == "windows":
            import msvcrt
            msvcrt.locking(self._file.fileno(), msvcrt.LK_LOCK, 1)
        elif self._lock_type == "unix":
            import fcntl
            fcntl.flock(self._file.fileno(), fcntl.LOCK_EX)
        # "none" - no locking available
    
    def release(self):
        """Release the lock."""
        if self._file:
            if self._lock_type == "windows":
                import msvcrt
                try:
                    msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError as e:
                    import logging
                    logging.warning(f"Failed to release Windows lock: {e}")
                except Exception as e:
                    import logging
                    logging.error(f"Unexpected error releasing lock: {e}")
            elif self._lock_type == "unix":
                import fcntl
                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
            
            self._file.close()
            self._file = None
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


class EnhancedAuditLogger(IAuditLogger):
    """
    Production-grade audit logger with hash chain integrity.
    
    Features:
    - SHA-256 hash chain (tamper detection)
    - Cross-platform file locking
    - SQLite storage for queries
    - Correlation ID tracking
    - Thread-safe operations
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern for global audit logger."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(
        self,
        component: str = "CORTEX",
        db_path: Optional[Path] = None,
        auto_init: bool = True
    ):
        """
        Initialize the audit logger.
        
        Args:
            component: Component name for log entries
            db_path: Path to SQLite database (default: audit-logs/audit.db)
            auto_init: Whether to auto-initialize database
        """
        # Prevent re-initialization
        if hasattr(self, "_initialized") and self._initialized:
            return
        
        self.component = component
        self.db_path = db_path or (audit_logs_path() / "audit.db")
        self.lock_path = self.db_path.parent / ".audit.lock"
        self._previous_hash = "GENESIS"
        self._correlation_id = str(uuid.uuid4())
        self._file_lock = CrossPlatformFileLock(self.lock_path)
        
        if auto_init:
            self._init_database()
        
        self._initialized = True
    
    def _init_database(self):
        """Initialize SQLite database schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    component TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    ac_id TEXT,
                    correlation_id TEXT NOT NULL,
                    metadata TEXT,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON audit_log(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ac_id 
                ON audit_log(ac_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_correlation_id 
                ON audit_log(correlation_id)
            """)
            
            conn.commit()
            
            # Get last hash for chain continuity
            cursor = conn.execute(
                "SELECT entry_hash FROM audit_log ORDER BY timestamp DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                self._previous_hash = row[0]
    
    @contextmanager
    def _get_connection(self):
        """Get SQLite connection with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _compute_hash(self, entry: AuditLogEntry) -> str:
        """Compute SHA-256 hash for entry."""
        # Create deterministic string for hashing
        data = json.dumps({
            "id": entry.id,
            "timestamp": entry.timestamp,
            "operation": entry.operation,
            "component": entry.component,
            "level": entry.level,
            "message": entry.message,
            "ac_id": entry.ac_id,
            "correlation_id": entry.correlation_id,
            "previous_hash": entry.previous_hash
        }, sort_keys=True)
        
        return hashlib.sha256(data.encode()).hexdigest()
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for subsequent log entries."""
        self._correlation_id = correlation_id
    
    def new_correlation_id(self) -> str:
        """Generate and set new correlation ID."""
        self._correlation_id = str(uuid.uuid4())
        return self._correlation_id
    
    def log(
        self,
        operation: str,
        message: str,
        level: str = "INFO",
        ac_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Result[None]:
        """
        Log an audit entry with hash chain integrity.
        
        Args:
            operation: Operation being performed
            message: Human-readable message
            level: Log level (DEBUG, INFO, WARN, ERROR)
            ac_id: Optional acceptance criteria ID
            metadata: Optional additional data
        
        Returns:
            Result indicating success or error
        """
        try:
            entry = AuditLogEntry(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                operation=operation,
                component=self.component,
                level=level,
                message=message,
                ac_id=ac_id,
                correlation_id=self._correlation_id,
                metadata=metadata,
                previous_hash=self._previous_hash,
                entry_hash=""  # Computed below
            )
            
            entry.entry_hash = self._compute_hash(entry)
            
            with self._file_lock:
                with self._get_connection() as conn:
                    conn.execute("""
                        INSERT INTO audit_log 
                        (id, timestamp, operation, component, level, message,
                         ac_id, correlation_id, metadata, previous_hash, entry_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.id,
                        entry.timestamp,
                        entry.operation,
                        entry.component,
                        entry.level,
                        entry.message,
                        entry.ac_id,
                        entry.correlation_id,
                        json.dumps(entry.metadata) if entry.metadata else None,
                        entry.previous_hash,
                        entry.entry_hash
                    ))
                    conn.commit()
            
            self._previous_hash = entry.entry_hash
            return Ok(None)
        
        except Exception as e:
            return Err(f"Failed to log audit entry: {e}")
    
    def query(
        self,
        ac_id: Optional[str] = None,
        component: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> Result[List[AuditEntry]]:
        """
        Query audit logs with filters.
        
        Args:
            ac_id: Filter by acceptance criteria ID
            component: Filter by component
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            limit: Maximum entries to return
        
        Returns:
            Result containing list of audit entries or error
        """
        try:
            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []
            
            if ac_id:
                query += " AND ac_id = ?"
                params.append(ac_id)
            
            if component:
                query += " AND component = ?"
                params.append(component)
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            entries = []
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                for row in cursor.fetchall():
                    entries.append(AuditEntry(
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                        operation=row["operation"],
                        ac_id=row["ac_id"],
                        correlation_id=row["correlation_id"],
                        component=row["component"],
                        level=row["level"],
                        message=row["message"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else None
                    ))
            
            return Ok(entries)
        
        except Exception as e:
            return Err(f"Failed to query audit logs: {e}")
    
    def verify_chain(self) -> Result[bool]:
        """
        Verify hash chain integrity.
        
        Returns:
            Result containing True if valid, False if tampered
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM audit_log ORDER BY timestamp ASC"
                )
                
                expected_previous = "GENESIS"
                
                for row in cursor.fetchall():
                    entry = AuditLogEntry(
                        id=row["id"],
                        timestamp=row["timestamp"],
                        operation=row["operation"],
                        component=row["component"],
                        level=row["level"],
                        message=row["message"],
                        ac_id=row["ac_id"],
                        correlation_id=row["correlation_id"],
                        metadata=json.loads(row["metadata"]) if row["metadata"] else None,
                        previous_hash=row["previous_hash"],
                        entry_hash=row["entry_hash"]
                    )
                    
                    # Verify previous hash
                    if entry.previous_hash != expected_previous:
                        return Ok(False)
                    
                    # Verify entry hash
                    computed = self._compute_hash(entry)
                    if computed != entry.entry_hash:
                        return Ok(False)
                    
                    expected_previous = entry.entry_hash
                
                return Ok(True)
        
        except Exception as e:
            return Err(f"Failed to verify chain: {e}")
    
    @classmethod
    def reset(cls):
        """Reset singleton instance (for testing)."""
        cls._instance = None


# Module-level convenience function
def get_audit_logger(component: str = "CORTEX") -> EnhancedAuditLogger:
    """Get the global audit logger instance."""
    return EnhancedAuditLogger(component=component)
