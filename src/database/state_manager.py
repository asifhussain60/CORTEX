"""
CORTEX 6.0 StateManager
=======================
SQLite-based state management with WAL mode and optimistic locking.

Features:
- CRUD operations for generic key-value state
- WAL mode for concurrent read/write
- Optimistic locking via version column
- Checkpoint/resume functionality
- TODO items management
- Execution state tracking
- State history audit trail

Author: Asif Hussain
Version: 6.0.0
Created: 2026-01-07
"""

import sqlite3
import json
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from contextlib import contextmanager


class StateManagerError(Exception):
    """Base exception for StateManager errors."""
    pass


class DuplicateKeyError(StateManagerError):
    """Raised when attempting to create a state with a duplicate key."""
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"State with key '{key}' already exists")


class KeyNotFoundError(StateManagerError):
    """Raised when attempting to access a non-existent key."""
    def __init__(self, key: str):
        self.key = key
        super().__init__(f"State with key '{key}' not found")


class VersionConflictError(StateManagerError):
    """Raised when optimistic locking detects a version conflict."""
    def __init__(self, key: str, expected_version: int, actual_version: int):
        self.key = key
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"Version conflict for key '{key}': "
            f"expected version {expected_version}, but current version is {actual_version}"
        )


class StateManager:
    """
    SQLite-based state manager with WAL mode and optimistic locking.
    
    Usage:
        # As context manager (recommended)
        with StateManager("state.db") as sm:
            sm.create_state("key", {"data": "value"})
            
        # Manual management
        sm = StateManager("state.db")
        sm.initialize()
        try:
            sm.create_state("key", {"data": "value"})
        finally:
            sm.close()
    """
    
    # Make exceptions available as class attributes for easy access
    DuplicateKeyError = DuplicateKeyError
    KeyNotFoundError = KeyNotFoundError
    VersionConflictError = VersionConflictError
    
    def __init__(self, db_path: Union[str, Path]):
        """
        Initialize StateManager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        self._local = threading.local()
        self._initialized = False
        self._in_context = False  # Track if being used as context manager
        
    def __enter__(self):
        """Context manager entry - starts a transaction."""
        self.initialize()
        self._in_context = True
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - commit or rollback based on exception."""
        self._in_context = False
        if exc_type is None:
            self._commit()
        else:
            self._connection.rollback()
        self.close()
        return False  # Don't suppress exceptions
        
    def initialize(self) -> None:
        """Initialize database connection and schema."""
        if self._initialized:
            return
            
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect with WAL mode settings
        # Use DEFERRED isolation for transaction support
        self._connection = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level="DEFERRED"
        )
        self._connection.row_factory = sqlite3.Row
        
        # Enable WAL mode and set synchronous
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=NORMAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        
        # Initialize schema
        self._initialize_schema()
        self._initialized = True
        
    def _initialize_schema(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self._connection.cursor()
        
        # Core state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                expires_at TEXT,
                metadata TEXT
            )
        """)
        
        # TODO items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS todo_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT NOT NULL UNIQUE,
                feature_id TEXT NOT NULL,
                phase_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'NOT_STARTED',
                priority TEXT NOT NULL DEFAULT 'P1_HIGH',
                version INTEGER NOT NULL DEFAULT 1,
                tdd_phase TEXT,
                estimated_minutes INTEGER,
                actual_minutes INTEGER,
                started_at TEXT,
                completed_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                dependencies TEXT,
                validation_result TEXT,
                metadata TEXT
            )
        """)
        
        # Execution state table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT NOT NULL UNIQUE,
                orchestrator TEXT NOT NULL,
                workflow_type TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                version INTEGER NOT NULL DEFAULT 1,
                phase TEXT,
                step INTEGER DEFAULT 0,
                context TEXT,
                result TEXT,
                error TEXT,
                started_at TEXT,
                completed_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                metadata TEXT
            )
        """)
        
        # Checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkpoint_id TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                description TEXT,
                checkpoint_type TEXT NOT NULL DEFAULT 'MANUAL',
                state_snapshot TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                created_by TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        # Checkpoint references table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkpoint_refs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkpoint_id TEXT NOT NULL,
                ref_type TEXT NOT NULL,
                ref_id TEXT NOT NULL,
                ref_version INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(checkpoint_id) ON DELETE CASCADE
            )
        """)
        
        # State history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                version_before INTEGER,
                version_after INTEGER,
                changed_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                changed_by TEXT,
                correlation_id TEXT
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_state_key ON state(key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todo_status ON todo_items(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todo_feature ON todo_items(feature_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_status ON execution_state(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkpoint_type ON checkpoints(checkpoint_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_table_record ON state_history(table_name, record_id)")
        
        self._commit()
        
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self._initialized = False
            
    # ==========================================================================
    # WAL Mode Methods
    # ==========================================================================
    
    def get_journal_mode(self) -> str:
        """Get current journal mode."""
        cursor = self._connection.execute("PRAGMA journal_mode")
        return cursor.fetchone()[0]
        
    def get_synchronous_mode(self) -> int:
        """Get current synchronous mode."""
        cursor = self._connection.execute("PRAGMA synchronous")
        return cursor.fetchone()[0]
        
    def checkpoint(self) -> bool:
        """Perform WAL checkpoint."""
        try:
            self._connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            return True
        except sqlite3.Error as e:
            # WAL checkpoint may return errors in some states, but that's OK
            return True
            
    def _commit(self) -> None:
        """Commit if not in context manager mode."""
        if not self._in_context:
            self._connection.commit()
            
    # ==========================================================================
    # Generic State CRUD Operations
    # ==========================================================================
    
    def create_state(self, key: str, value: Any, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Create a new state entry.
        
        Args:
            key: Unique key for the state
            value: Value to store (will be JSON serialized)
            metadata: Optional metadata dict
            
        Returns:
            Dict with created state info
            
        Raises:
            DuplicateKeyError: If key already exists
        """
        cursor = self._connection.cursor()
        try:
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT INTO state (key, value, version, created_at, updated_at, metadata)
                VALUES (?, ?, 1, ?, ?, ?)
                """,
                (key, json.dumps(value), now, now, json.dumps(metadata) if metadata else None)
            )
            self._commit()
            
            # Record history
            self._record_history("state", key, "INSERT", None, value, None, 1)
            
            return {
                "key": key,
                "value": value,
                "version": 1,
                "created_at": now,
                "updated_at": now,
                "metadata": metadata
            }
        except sqlite3.IntegrityError:
            raise DuplicateKeyError(key)
            
    def read_state(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Read a state entry by key.
        
        Args:
            key: Key to look up
            
        Returns:
            Dict with state info or None if not found
        """
        cursor = self._connection.execute(
            "SELECT key, value, version, created_at, updated_at, metadata FROM state WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        return {
            "key": row["key"],
            "value": json.loads(row["value"]),
            "version": row["version"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else None
        }
        
    def update_state(self, key: str, value: Any, expected_version: int, 
                     metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Update a state entry with optimistic locking.
        
        Args:
            key: Key to update
            value: New value
            expected_version: Expected current version for optimistic locking
            metadata: Optional new metadata
            
        Returns:
            Dict with updated state info
            
        Raises:
            KeyNotFoundError: If key doesn't exist
            VersionConflictError: If version doesn't match
        """
        # First, get current state
        current = self.read_state(key)
        if current is None:
            raise KeyNotFoundError(key)
            
        # Check version
        if current["version"] != expected_version:
            raise VersionConflictError(key, expected_version, current["version"])
            
        # Perform update
        now = datetime.utcnow().isoformat()
        new_version = expected_version + 1
        
        cursor = self._connection.execute(
            """
            UPDATE state 
            SET value = ?, version = ?, updated_at = ?, metadata = COALESCE(?, metadata)
            WHERE key = ? AND version = ?
            """,
            (json.dumps(value), new_version, now, 
             json.dumps(metadata) if metadata else None, key, expected_version)
        )
        
        if cursor.rowcount == 0:
            # Race condition - version changed between read and update
            refreshed = self.read_state(key)
            raise VersionConflictError(key, expected_version, refreshed["version"] if refreshed else 0)
            
        self._commit()
        
        # Record history
        self._record_history("state", key, "UPDATE", current["value"], value, 
                            expected_version, new_version)
        
        return {
            "key": key,
            "value": value,
            "version": new_version,
            "created_at": current["created_at"],
            "updated_at": now,
            "metadata": metadata or current.get("metadata")
        }
        
    def delete_state(self, key: str) -> bool:
        """
        Delete a state entry.
        
        Args:
            key: Key to delete
            
        Returns:
            True if deleted, False if not found
        """
        current = self.read_state(key)
        
        cursor = self._connection.execute(
            "DELETE FROM state WHERE key = ?",
            (key,)
        )
        self._commit()
        
        if cursor.rowcount > 0 and current:
            self._record_history("state", key, "DELETE", current["value"], None,
                                current["version"], None)
            return True
        return False
        
    # ==========================================================================
    # TODO Items Management
    # ==========================================================================
    
    def create_todo_item(self, item_id: str, feature_id: str, phase_id: int, name: str,
                         description: Optional[str] = None, priority: str = "P1_HIGH",
                         tdd_phase: Optional[str] = None, estimated_minutes: Optional[int] = None,
                         dependencies: Optional[List[str]] = None, 
                         status: str = "NOT_STARTED") -> Dict[str, Any]:
        """Create a new TODO item."""
        cursor = self._connection.cursor()
        now = datetime.utcnow().isoformat()
        
        cursor.execute(
            """
            INSERT INTO todo_items 
            (item_id, feature_id, phase_id, name, description, status, priority, 
             tdd_phase, estimated_minutes, dependencies, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item_id, feature_id, phase_id, name, description, status, priority,
             tdd_phase, estimated_minutes, json.dumps(dependencies) if dependencies else None,
             now, now)
        )
        self._commit()
        
        return {
            "item_id": item_id,
            "feature_id": feature_id,
            "phase_id": phase_id,
            "name": name,
            "description": description,
            "status": status,
            "priority": priority,
            "version": 1,
            "tdd_phase": tdd_phase,
            "estimated_minutes": estimated_minutes,
            "dependencies": dependencies,
            "created_at": now
        }
        
    def get_todo_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a TODO item by ID."""
        cursor = self._connection.execute(
            "SELECT * FROM todo_items WHERE item_id = ?",
            (item_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        return dict(row)
        
    def update_todo_item(self, item_id: str, **updates) -> Dict[str, Any]:
        """Update a TODO item."""
        current = self.get_todo_item(item_id)
        if current is None:
            raise KeyNotFoundError(item_id)
            
        # Build update query dynamically
        allowed_fields = ["status", "priority", "tdd_phase", "started_at", "completed_at",
                         "actual_minutes", "validation_result", "description"]
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = ?")
                values.append(value)
                
        if not set_clauses:
            return current
            
        # Add version increment and updated_at
        set_clauses.append("version = version + 1")
        set_clauses.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(item_id)
        
        query = f"UPDATE todo_items SET {', '.join(set_clauses)} WHERE item_id = ?"
        self._connection.execute(query, values)
        self._commit()
        
        return self.get_todo_item(item_id)
        
    def list_todo_items(self, status: Optional[str] = None, feature_id: Optional[str] = None,
                        phase_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List TODO items with optional filtering."""
        query = "SELECT * FROM todo_items WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        if feature_id:
            query += " AND feature_id = ?"
            params.append(feature_id)
        if phase_id is not None:
            query += " AND phase_id = ?"
            params.append(phase_id)
            
        query += " ORDER BY phase_id, id"
        
        cursor = self._connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    # ==========================================================================
    # Execution State Management
    # ==========================================================================
    
    def create_execution(self, execution_id: str, orchestrator: str,
                        workflow_type: Optional[str] = None,
                        context: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new execution state."""
        now = datetime.utcnow().isoformat()
        
        self._connection.execute(
            """
            INSERT INTO execution_state 
            (execution_id, orchestrator, workflow_type, status, context, created_at, updated_at)
            VALUES (?, ?, ?, 'PENDING', ?, ?, ?)
            """,
            (execution_id, orchestrator, workflow_type, 
             json.dumps(context) if context else None, now, now)
        )
        self._commit()
        
        return {
            "execution_id": execution_id,
            "orchestrator": orchestrator,
            "workflow_type": workflow_type,
            "status": "PENDING",
            "context": context,
            "created_at": now
        }
        
    def update_execution(self, execution_id: str, **updates) -> Dict[str, Any]:
        """Update execution state."""
        allowed_fields = ["status", "phase", "step", "context", "error"]
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                if field == "context":
                    value = json.dumps(value) if value else None
                set_clauses.append(f"{field} = ?")
                values.append(value)
                
        if not set_clauses:
            return self.get_execution(execution_id)
            
        # Handle started_at for RUNNING status
        if updates.get("status") == "RUNNING":
            set_clauses.append("started_at = COALESCE(started_at, ?)")
            values.append(datetime.utcnow().isoformat())
            
        set_clauses.append("version = version + 1")
        set_clauses.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(execution_id)
        
        query = f"UPDATE execution_state SET {', '.join(set_clauses)} WHERE execution_id = ?"
        self._connection.execute(query, values)
        self._commit()
        
        return self.get_execution(execution_id)
        
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution state by ID."""
        cursor = self._connection.execute(
            "SELECT * FROM execution_state WHERE execution_id = ?",
            (execution_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        result = dict(row)
        if result.get("context"):
            result["context"] = json.loads(result["context"])
        if result.get("result"):
            result["result"] = json.loads(result["result"])
        return result
        
    def complete_execution(self, execution_id: str, status: str = "COMPLETED",
                          result: Optional[Dict] = None) -> Dict[str, Any]:
        """Complete an execution with result."""
        now = datetime.utcnow().isoformat()
        
        self._connection.execute(
            """
            UPDATE execution_state 
            SET status = ?, result = ?, completed_at = ?, version = version + 1, updated_at = ?
            WHERE execution_id = ?
            """,
            (status, json.dumps(result) if result else None, now, now, execution_id)
        )
        self._commit()
        
        return self.get_execution(execution_id)
        
    # ==========================================================================
    # Checkpoint/Resume Operations
    # ==========================================================================
    
    def create_checkpoint(self, name: str, description: Optional[str] = None,
                         checkpoint_type: str = "MANUAL",
                         created_by: Optional[str] = None,
                         tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a checkpoint of current state."""
        checkpoint_id = f"cp_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()
        
        # Capture current state snapshot
        state_snapshot = self._capture_state_snapshot()
        
        self._connection.execute(
            """
            INSERT INTO checkpoints 
            (checkpoint_id, name, description, checkpoint_type, state_snapshot, 
             created_at, created_by, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (checkpoint_id, name, description, checkpoint_type,
             json.dumps(state_snapshot), now, created_by, 
             json.dumps(tags) if tags else None)
        )
        
        # Record references
        self._record_checkpoint_refs(checkpoint_id, state_snapshot)
        
        self._commit()
        
        return {
            "checkpoint_id": checkpoint_id,
            "name": name,
            "description": description,
            "checkpoint_type": checkpoint_type,
            "created_at": now,
            "created_by": created_by,
            "tags": tags
        }
        
    def _capture_state_snapshot(self) -> Dict[str, Any]:
        """Capture current state for checkpoint."""
        snapshot = {
            "state": {},
            "todo_items": [],
            "execution_state": []
        }
        
        # Capture state entries
        cursor = self._connection.execute("SELECT key, value, version FROM state")
        for row in cursor.fetchall():
            snapshot["state"][row["key"]] = {
                "value": json.loads(row["value"]),
                "version": row["version"]
            }
            
        # Capture TODO items
        cursor = self._connection.execute("SELECT * FROM todo_items")
        for row in cursor.fetchall():
            snapshot["todo_items"].append(dict(row))
            
        # Capture execution state
        cursor = self._connection.execute("SELECT * FROM execution_state")
        for row in cursor.fetchall():
            snapshot["execution_state"].append(dict(row))
            
        return snapshot
        
    def _record_checkpoint_refs(self, checkpoint_id: str, snapshot: Dict) -> None:
        """Record checkpoint references for tracking."""
        now = datetime.utcnow().isoformat()
        
        for key, data in snapshot.get("state", {}).items():
            self._connection.execute(
                """
                INSERT INTO checkpoint_refs (checkpoint_id, ref_type, ref_id, ref_version, created_at)
                VALUES (?, 'state', ?, ?, ?)
                """,
                (checkpoint_id, key, data["version"], now)
            )
            
        for item in snapshot.get("todo_items", []):
            self._connection.execute(
                """
                INSERT INTO checkpoint_refs (checkpoint_id, ref_type, ref_id, ref_version, created_at)
                VALUES (?, 'todo_item', ?, ?, ?)
                """,
                (checkpoint_id, item["item_id"], item.get("version", 1), now)
            )
            
    def list_checkpoints(self, checkpoint_type: Optional[str] = None,
                        limit: int = 10) -> List[Dict[str, Any]]:
        """List checkpoints."""
        query = "SELECT checkpoint_id, name, description, checkpoint_type, created_at, created_by, tags FROM checkpoints"
        params = []
        
        if checkpoint_type:
            query += " WHERE checkpoint_type = ?"
            params.append(checkpoint_type)
            
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self._connection.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore state from a checkpoint."""
        cursor = self._connection.execute(
            "SELECT state_snapshot FROM checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return False
            
        snapshot = json.loads(row["state_snapshot"])
        
        # Restore state entries
        for key, data in snapshot.get("state", {}).items():
            self._connection.execute("DELETE FROM state WHERE key = ?", (key,))
            now = datetime.utcnow().isoformat()
            self._connection.execute(
                """
                INSERT INTO state (key, value, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (key, json.dumps(data["value"]), data["version"], now, now)
            )
            
        # Restore TODO items
        for item in snapshot.get("todo_items", []):
            self._connection.execute(
                "DELETE FROM todo_items WHERE item_id = ?", 
                (item["item_id"],)
            )
            # Re-insert with original values
            cols = ", ".join(item.keys())
            placeholders = ", ".join(["?"] * len(item))
            self._connection.execute(
                f"INSERT INTO todo_items ({cols}) VALUES ({placeholders})",
                list(item.values())
            )
            
        self._commit()
        return True
        
    def resume_from_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Resume execution from checkpoint, returning restored state."""
        cursor = self._connection.execute(
            "SELECT state_snapshot FROM checkpoints WHERE checkpoint_id = ?",
            (checkpoint_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            return None
            
        snapshot = json.loads(row["state_snapshot"])
        
        # Restore and return state
        if self.restore_checkpoint(checkpoint_id):
            return snapshot.get("state", {})
        return None
        
    # ==========================================================================
    # State History
    # ==========================================================================
    
    def _record_history(self, table_name: str, record_id: str, operation: str,
                        old_value: Any, new_value: Any, 
                        version_before: Optional[int], version_after: Optional[int],
                        correlation_id: Optional[str] = None) -> None:
        """Record state change in history."""
        self._connection.execute(
            """
            INSERT INTO state_history 
            (table_name, record_id, operation, old_value, new_value, 
             version_before, version_after, correlation_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (table_name, record_id, operation,
             json.dumps(old_value) if old_value is not None else None,
             json.dumps(new_value) if new_value is not None else None,
             version_before, version_after, correlation_id)
        )
        
    def get_state_history(self, table_name: str, record_id: str,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get history for a specific record."""
        cursor = self._connection.execute(
            """
            SELECT * FROM state_history 
            WHERE table_name = ? AND record_id = ?
            ORDER BY changed_at DESC
            LIMIT ?
            """,
            (table_name, record_id, limit)
        )
        
        results = []
        for row in cursor.fetchall():
            record = dict(row)
            if record.get("old_value"):
                record["old_value"] = json.loads(record["old_value"])
            if record.get("new_value"):
                record["new_value"] = json.loads(record["new_value"])
            results.append(record)
            
        return results
