"""
database_transaction_manager.py

Transaction management for atomic operation execution + audit logging.

Implements ACID transaction handling for orchestrator operations where
both the operation execution and audit logging occur in a single
atomic transaction boundary.

CORE-027 COMPLIANCE:
- AC_START, AC_EXECUTE, AC_COMPLETE are all logged within transaction
- Transaction rolls back if audit logging fails
- Savepoints for nested operations maintain isolation

CORE-008 COMPLIANCE:
- Uses context managers for deterministic resource management
- All transaction boundaries explicit
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional, Any, Dict, Callable, TypeVar, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.core.result import Result, Ok, Err


T = TypeVar('T')


@dataclass
class TransactionContext:
    """Context for a transaction including savepoints."""
    connection: sqlite3.Connection
    savepoint_stack: List[str]
    transaction_id: str
    start_time: datetime
    
    def create_savepoint(self, name: str) -> None:
        """Create named savepoint for nested operations."""
        self.connection.execute(f"SAVEPOINT {name}")
        self.savepoint_stack.append(name)
    
    def release_savepoint(self, name: str) -> None:
        """Release (commit) a savepoint."""
        if name in self.savepoint_stack:
            self.connection.execute(f"RELEASE SAVEPOINT {name}")
            self.savepoint_stack.remove(name)
    
    def rollback_to_savepoint(self, name: str) -> None:
        """Rollback to a savepoint."""
        if name in self.savepoint_stack:
            self.connection.execute(f"ROLLBACK TO SAVEPOINT {name}")
            self.savepoint_stack.remove(name)


class DatabaseTransactionManager:
    """
    Manages atomic transactions for orchestrator operations.
    
    Ensures that operation execution and audit logging occur in a single
    transaction, providing ACID guarantees.
    
    Usage:
    ```python
    manager = DatabaseTransactionManager(db_path)
    with manager.atomic_operation("AC-FIX-001-01", "execute_orchestrator") as txn:
        # Execute orchestrator operation
        result = orchestrator.execute()
        # Audit logging within transaction
        txn.log_entry("AC_EXECUTE", {"result": result})
        return result
    ```
    """
    
    def __init__(self, db_path: str, timeout: float = 5.0):
        """
        Initialize transaction manager.
        
        Args:
            db_path: Path to SQLite database
            timeout: Transaction timeout in seconds
        """
        self.db_path = db_path
        self.timeout = timeout
        self._connection: Optional[sqlite3.Connection] = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, timeout=self.timeout)
            # Enable WAL mode for concurrency
            self._connection.execute("PRAGMA journal_mode=WAL")
            # Enable foreign key constraints
            self._connection.execute("PRAGMA foreign_keys=ON")
        return self._connection
    
    @contextmanager
    def atomic_operation(
        self,
        ac_id: str,
        operation_name: str,
        user: str = "builder"
    ):
        """
        Context manager for atomic operation + audit logging.
        
        Ensures that both operation execution and audit logging occur
        within a single transaction boundary. On success, commits.
        On exception, rolls back completely.
        
        Args:
            ac_id: Acceptance Criteria ID (e.g., "AC-FIX-001-01")
            operation_name: Name of operation (e.g., "execute_orchestrator")
            user: User performing operation
            
        Yields:
            TransactionContext for operation and audit logging
            
        Usage:
        ```python
        try:
            with manager.atomic_operation("AC-FIX-001-01", "execute") as txn:
                result = orchestrator.execute()
                txn.log_entry("AC_EXECUTE", {"success": True, "result": result})
        except Exception as e:
            # Transaction rolled back automatically
            print(f"Operation failed and rolled back: {e}")
        ```
        """
        conn = self._get_connection()
        transaction_id = f"{ac_id}_{operation_name}_{datetime.now().isoformat()}"
        
        try:
            # Start transaction (BEGIN implicit in sqlite3)
            conn.execute("BEGIN IMMEDIATE")  # Use IMMEDIATE for exclusive access
            
            # Create transaction context
            context = TransactionContext(
                connection=conn,
                savepoint_stack=[],
                transaction_id=transaction_id,
                start_time=datetime.now()
            )
            
            # Log AC_START within transaction
            self._log_audit_entry(
                conn, ac_id, operation_name, user,
                "AC_START", {"transaction_id": transaction_id}
            )
            
            # Yield context to caller for operation execution
            yield context
            
            # Log AC_COMPLETE within transaction (if no exception)
            self._log_audit_entry(
                conn, ac_id, operation_name, user,
                "AC_COMPLETE", {"transaction_id": transaction_id}
            )
            
            # Commit transaction (both operation and audit logging)
            conn.commit()
            
        except Exception as e:
            # Rollback entire transaction (operation + audit entries)
            conn.rollback()
            
            # Log failure AFTER rollback (separate transaction)
            try:
                conn.execute("BEGIN")
                self._log_audit_entry(
                    conn, ac_id, operation_name, user,
                    "AC_EXECUTE_FAILED",
                    {"error": str(e), "transaction_id": transaction_id}
                )
                conn.commit()
            except Exception as log_e:
                conn.rollback()
                raise Exception(f"Failed to log error: {str(log_e)}") from e
            
            # Re-raise the original exception
            raise
    
    def _log_audit_entry(
        self,
        conn: sqlite3.Connection,
        ac_id: str,
        operation: str,
        user: str,
        status: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Log audit entry within a transaction.
        
        Args:
            conn: Active database connection in transaction
            ac_id: Acceptance Criteria ID
            operation: Operation name
            user: User performing operation
            status: Status (AC_START, AC_EXECUTE, AC_COMPLETE, AC_EXECUTE_FAILED)
            details: Operation details
        """
        timestamp = datetime.utcnow().isoformat()
        
        # This will fail if audit_log table doesn't exist, which is expected
        # in new environments. Handle gracefully or ensure table exists.
        try:
            conn.execute(
                """
                INSERT INTO audit_log (timestamp, ac_id, operation, status, user_id, details)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (timestamp, ac_id, operation, status, user, str(details))
            )
        except sqlite3.OperationalError as e:
            # If table doesn't exist, create it
            if "no such table" in str(e):
                self._create_audit_table(conn)
                conn.execute(
                    """
                    INSERT INTO audit_log (timestamp, ac_id, operation, status, user_id, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (timestamp, ac_id, operation, status, user, str(details))
                )
            else:
                raise
    
    def _create_audit_table(self, conn: sqlite3.Connection) -> None:
        """Create audit_log table if it doesn't exist."""
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                user_id TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ac_id ON audit_log(ac_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)"
        )
    
    @contextmanager
    def nested_operation(self, context: TransactionContext, name: str):
        """
        Create a savepoint for nested operations within a transaction.
        
        Allows partial rollback of nested operations without
        rolling back the entire transaction.
        
        Args:
            context: Current TransactionContext
            name: Savepoint name
            
        Usage:
        ```python
        with manager.atomic_operation("AC-001", "master") as txn:
            result1 = call_nested_1()
            with manager.nested_operation(txn, "nested_1") as nested:
                result2 = call_nested_2()  # If this fails, only nested_2 rolls back
        ```
        """
        try:
            context.create_savepoint(name)
            yield context
            context.release_savepoint(name)
        except Exception as e:
            context.rollback_to_savepoint(name)
            raise


class StateAtomicityManager:
    """
    Manages AC state machine with atomic transitions.
    
    Ensures that state transitions (PENDING → EXECUTING → COMPLETE/FAILED)
    and audit logging occur atomically.
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        "PENDING": {"EXECUTING"},
        "EXECUTING": {"COMPLETE", "FAILED"},
        "COMPLETE": set(),  # Terminal state
        "FAILED": set(),    # Terminal state
    }
    
    def __init__(self, db_path: str):
        """Initialize state manager."""
        self.manager = DatabaseTransactionManager(db_path)
    
    def transition_ac_state(
        self,
        ac_id: str,
        from_state: str,
        to_state: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Result[None]:
        """
        Atomically transition AC state and log the transition.
        
        Args:
            ac_id: AC ID to transition
            from_state: Expected current state
            to_state: Target state
            details: Additional details
            
        Returns:
            Result[None] - success or error
        """
        # Validate transition
        if to_state not in self.VALID_TRANSITIONS.get(from_state, set()):
            return Err(
                f"Invalid transition: {from_state} → {to_state}. "
                f"Valid transitions: {self.VALID_TRANSITIONS.get(from_state, set())}"
            )
        
        try:
            with self.manager.atomic_operation(ac_id, "state_transition") as txn:
                # Update AC state in database
                conn = txn.connection
                conn.execute(
                    "UPDATE ac_status SET state = ? WHERE ac_id = ?",
                    (to_state, ac_id)
                )
                
                # Log state transition
                txn.log_entry("AC_STATE_TRANSITION", {
                    "ac_id": ac_id,
                    "from_state": from_state,
                    "to_state": to_state,
                    **(details or {})
                })
            
            return Ok(None)
        except Exception as e:
            return Err(f"Failed to transition state: {str(e)}")


if __name__ == "__main__":
    # Simple test
    db_path = Path(__file__).parent.parent.parent / "cortex-brain" / "state" / "test.db"
    manager = DatabaseTransactionManager(str(db_path))
    
    try:
        with manager.atomic_operation("AC-TEST-001", "test_operation") as txn:
            print(f"Transaction ID: {txn.transaction_id}")
            print("Operation successful")
    except Exception as e:
        print(f"Operation failed: {e}")
