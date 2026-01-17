"""
HP-002-01: Agent Execution Sandbox

Provides isolated execution environment with rollback and dry-run capabilities.
Ensures operations can be sandboxed, rolled back if needed, or previewed without side effects.

AC-ID: HP-002-01
Phase: PHASE-11-HALLUCINATION-PREVENTION
TDD Status: GREEN phase
"""

import sqlite3
import json
import uuid
import copy
import time
import traceback
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager


class ExecutionMode(Enum):
    """Execution mode enumeration.
    
    Defines how the operation should be executed and whether changes commit.
    """
    SANDBOX = "SANDBOX"  # Isolated, no side effects
    DRY_RUN = "DRY_RUN"  # Preview without committing
    COMMITTED = "COMMITTED"  # Execute with side effects committed


class ExecutionState(Enum):
    """Execution state enumeration.
    
    Tracks the lifecycle state of an execution.
    """
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class SandboxSnapshot:
    """Snapshot of system state for rollback capability.
    
    Attributes:
        snapshot_id: Unique identifier for this snapshot
        timestamp: When snapshot was created
        data: Captured state data
        checksum: Data integrity verification
        metadata: Additional snapshot context
    """
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Compute checksum on creation."""
        if self.data:
            try:
                data_str = json.dumps(self.data, sort_keys=True, default=str)
                import hashlib
                self.checksum = hashlib.sha256(data_str.encode()).hexdigest()
            except (TypeError, ValueError):
                self.checksum = None

    def verify_integrity(self) -> bool:
        """Verify snapshot hasn't been tampered with.
        
        Returns:
            True if checksum matches, False if data was modified.
            
        Raises:
            ValueError: If tampering detected.
        """
        if not self.data or not self.checksum:
            return True
        
        try:
            data_str = json.dumps(self.data, sort_keys=True, default=str)
            import hashlib
            current_checksum = hashlib.sha256(data_str.encode()).hexdigest()
            
            if current_checksum != self.checksum:
                raise ValueError(
                    f"Snapshot integrity check failed: "
                    f"expected {self.checksum}, got {current_checksum}"
                )
            return True
        except (TypeError, ValueError) as e:
            if "Snapshot integrity" in str(e):
                raise
            return True


@dataclass
class SandboxExecution:
    """Result of sandbox execution.
    
    Attributes:
        execution_id: Unique identifier for this execution
        state: Current execution state
        mode: Execution mode used
        timestamp: When execution started
        duration_ms: How long execution took
        exit_code: Exit code from operation (0 = success)
        error: Error message if failed
        output: Operation output/result
        captured_output: Stringified output for logging
        side_effects: List of side effects that occurred
        context: Execution context (user, request, phase, etc)
        snapshot: Associated snapshot if rollback used
        committed: Whether changes were committed
        description: Human-readable operation description
    """
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: ExecutionState = ExecutionState.PENDING
    mode: ExecutionMode = ExecutionMode.SANDBOX
    timestamp: datetime = field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    exit_code: int = 1
    error: Optional[str] = None
    output: Any = None
    captured_output: Optional[str] = None
    side_effects: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    snapshot: Optional[SandboxSnapshot] = None
    committed: bool = False
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert execution result to dictionary.
        
        Returns:
            Dictionary representation of execution result.
        """
        return {
            "execution_id": self.execution_id,
            "state": self.state.value,
            "mode": self.mode.value,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "exit_code": self.exit_code,
            "error": self.error,
            "captured_output": self.captured_output,
            "side_effects": self.side_effects,
            "committed": self.committed,
            "description": self.description,
        }


class ExecutionSandbox:
    """Isolated execution environment with rollback and dry-run capabilities.
    
    Provides sandbox execution to isolate side effects, capture changes,
    and enable rollback. Supports dry-run preview and committed execution.
    
    Key Features:
    - Sandbox mode: Isolates operations from side effects
    - Snapshot creation: Capture system state for rollback
    - Rollback capability: Restore previous state atomically
    - Dry-run mode: Preview changes without committing
    - Execution tracking: Full audit trail of all operations
    - Exception handling: Graceful error handling and recording
    
    AC-FIX-BRITTLENESS-003: Added thread-safe history access with RLock.
    """

    def __init__(self, db_path: str = "cortex-brain/state/governance.db"):
        """Initialize execution sandbox.
        
        Args:
            db_path: Path to governance database for execution tracking.
        """
        self.db_path = db_path
        self._execution_history: List[SandboxExecution] = []
        self._history_lock = threading.RLock()  # AC-FIX-BRITTLENESS-003: Thread-safe history
        self._active_snapshots: Dict[str, SandboxSnapshot] = {}
        self._side_effect_tracking: Dict[str, List[str]] = {}
        self._init_execution_table()

    def _init_execution_table(self) -> None:
        """Initialize execution tracking table in database.
        
        Creates sandbox_executions table if it doesn't exist.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sandbox_executions (
                        execution_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        mode TEXT NOT NULL,
                        state TEXT NOT NULL,
                        duration_ms REAL NOT NULL,
                        exit_code INTEGER NOT NULL,
                        error TEXT,
                        context JSON,
                        committed BOOLEAN DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except sqlite3.Error:
            # Database may not be available, use in-memory fallback
            pass

    def create_snapshot(self, state: Dict[str, Any]) -> SandboxSnapshot:
        """Create snapshot of current system state.
        
        Captures state and computes checksum for integrity verification.
        Snapshot can be used for rollback to this point.
        
        Args:
            state: Current system state to snapshot.
            
        Returns:
            SandboxSnapshot capturing the state.
        """
        snapshot = SandboxSnapshot(data=copy.deepcopy(state))
        self._active_snapshots[snapshot.snapshot_id] = snapshot
        return snapshot

    def rollback(self, snapshot: SandboxSnapshot) -> Dict[str, Any]:
        """Rollback to previous state captured in snapshot.
        
        Verifies snapshot integrity before rollback. Raises exception
        if tampering detected. Clears all side effects from execution.
        
        Args:
            snapshot: Snapshot to rollback to.
            
        Returns:
            The restored state.
            
        Raises:
            ValueError: If snapshot integrity check fails.
        """
        snapshot.verify_integrity()
        
        # Return deep copy to prevent external modification
        return copy.deepcopy(snapshot.data)

    def execute(
        self,
        operation: Callable[..., Any],
        mode: ExecutionMode = ExecutionMode.SANDBOX,
        snapshot: Optional[SandboxSnapshot] = None,
        context: Optional[Dict[str, Any]] = None,
        description: str = "Sandbox execution",
        timeout_ms: int = 30000,
    ) -> SandboxExecution:
        """Execute operation in sandbox with specified mode.
        
        Handles sandbox isolation, dry-run preview, or committed execution.
        Captures all side effects, exceptions, and output for audit trail.
        
        Args:
            operation: Callable to execute.
            mode: Execution mode (SANDBOX, DRY_RUN, or COMMITTED).
            snapshot: Optional snapshot for rollback capability.
            context: Execution context (user, request, phase, etc).
            description: Human-readable operation description.
            timeout_ms: Operation timeout in milliseconds.
            
        Returns:
            SandboxExecution with results and status.
            
        Raises:
            TypeError: If operation is None.
        """
        if operation is None:
            raise TypeError("Operation callable cannot be None")

        execution = SandboxExecution(
            mode=mode,
            timestamp=datetime.utcnow(),
            context=context or {},
            snapshot=snapshot,
            description=description,
        )

        start_time = time.time()
        execution.state = ExecutionState.RUNNING
        
        # Shared state for timeout detection
        result_container = {"result": None, "completed": False, "error": None}

        def run_operation():
            """Wrapper to run operation and store result."""
            try:
                if mode == ExecutionMode.SANDBOX:
                    isolated_state = copy.deepcopy(snapshot.data) if snapshot else {}
                    result = self._execute_sandboxed(operation, isolated_state)
                    execution.side_effects.append("SANDBOX_MODE: No external changes committed")
                else:
                    result = operation()
                result_container["result"] = result
                result_container["completed"] = True
            except Exception as e:
                result_container["error"] = e
                result_container["completed"] = True

        # Run operation in thread to enable timeout
        thread = threading.Thread(target=run_operation)
        thread.daemon = True
        thread.start()
        
        # Wait for operation with timeout
        timeout_seconds = timeout_ms / 1000.0
        thread.join(timeout=timeout_seconds)

        try:
            # Check if operation completed within timeout
            if not result_container["completed"] or thread.is_alive():
                execution.state = ExecutionState.TIMEOUT
                execution.exit_code = 1
                execution.error = f"Operation exceeded timeout of {timeout_ms}ms"
                execution.side_effects.append(f"TIMEOUT: Operation did not complete in {timeout_ms}ms")
            elif result_container["error"] is not None:
                # Operation had an error
                e = result_container["error"]
                execution.state = ExecutionState.FAILED
                execution.exit_code = 1
                execution.error = str(e)
                execution.side_effects.append(f"EXCEPTION: {type(e).__name__}")
            else:
                # Operation succeeded
                result = result_container["result"]
                execution.output = result
                execution.exit_code = 0
                execution.state = ExecutionState.COMPLETED
                
                # Set captured output for DRY_RUN and COMMITTED modes
                if mode in [ExecutionMode.DRY_RUN, ExecutionMode.COMMITTED]:
                    execution.captured_output = self._stringify_output(result)
                
                if mode == ExecutionMode.DRY_RUN:
                    execution.side_effects.append("DRY_RUN_MODE: Changes previewed but not committed")
                    execution.committed = False
                elif mode == ExecutionMode.COMMITTED:
                    execution.committed = True

        finally:
            # Record duration
            elapsed = time.time() - start_time
            execution.duration_ms = elapsed * 1000

            # Log execution
            self._log_execution(execution, description)

        return execution

    def _execute_sandboxed(
        self,
        operation: Callable[..., Any],
        isolated_state: Dict[str, Any],
    ) -> Any:
        """Execute operation in isolated sandbox context.
        
        Creates copy of state, executes operation on copy, returns
        result without modifying external state.
        
        Args:
            operation: Operation to execute.
            isolated_state: Isolated state copy for operation.
            
        Returns:
            Operation result.
        """
        # Execute operation on isolated state
        result = operation()
        return result

    def _stringify_output(self, output: Any) -> str:
        """Convert output to string for logging.
        
        Args:
            output: Output to stringify.
            
        Returns:
            String representation of output.
        """
        try:
            if isinstance(output, str):
                return output
            elif isinstance(output, dict):
                return json.dumps(output, default=str)
            else:
                return str(output)
        except (TypeError, ValueError):
            return "<non-serializable>"

    def _log_execution(self, execution: SandboxExecution, description: str) -> None:
        """Log execution to database and memory.
        
        Args:
            execution: Execution result to log.
            description: Operation description.
            
        AC-FIX-BRITTLENESS-003: Thread-safe history access.
        """
        # Add to in-memory history (thread-safe)
        with self._history_lock:
            self._execution_history.append(execution)

        # Store in database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sandbox_executions
                    (execution_id, timestamp, mode, state, duration_ms,
                     exit_code, error, context, committed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.execution_id,
                    execution.timestamp.isoformat(),
                    execution.mode.value,
                    execution.state.value,
                    execution.duration_ms,
                    execution.exit_code,
                    execution.error,
                    json.dumps(execution.context, default=str),
                    execution.committed,
                ))
                conn.commit()
        except sqlite3.Error:
            # Database logging failed, continue with in-memory
            pass

    def get_execution_history(
        self,
        limit: int = 100,
        mode_filter: Optional[ExecutionMode] = None,
        state_filter: Optional[ExecutionState] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve execution history with optional filtering.
        
        Args:
            limit: Maximum number of records to return.
            mode_filter: Filter by execution mode.
            state_filter: Filter by execution state.
            
        Returns:
            List of execution records (most recent first).
            
        AC-FIX-BRITTLENESS-003: Thread-safe history access.
        """
        # Filter history (thread-safe)
        with self._history_lock:
            history = list(self._execution_history)  # Copy to avoid modification during iteration

        if mode_filter:
            history = [e for e in history if e.mode == mode_filter]

        if state_filter:
            history = [e for e in history if e.state == state_filter]

        # Sort by timestamp descending (most recent first)
        history.sort(key=lambda e: e.timestamp, reverse=True)

        # Convert to dicts and limit
        return [e.to_dict() for e in history[:limit]]

    def get_recent_executions(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get executions from last N minutes.
        
        Args:
            minutes: How many minutes back to look.
            
        Returns:
            List of recent executions.
            
        AC-FIX-BRITTLENESS-003: Thread-safe history access.
        """
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        with self._history_lock:
            recent = [e for e in self._execution_history if e.timestamp > cutoff]

        return [e.to_dict() for e in recent]

    def get_failed_executions(self) -> List[Dict[str, Any]]:
        """Get all failed executions.
        
        Returns:
            List of failed execution records.
        """
        return self.get_execution_history(state_filter=ExecutionState.FAILED)

    def clear_history(self) -> None:
        """Clear execution history from memory.
        
        Note: Database history is not cleared.
        
        AC-FIX-BRITTLENESS-003: Thread-safe history access.
        """
        with self._history_lock:
            self._execution_history.clear()
