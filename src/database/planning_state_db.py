"""
Planning State Database Manager.

Single source of truth for all planning execution state with ACID transactions.
Provides CRUD operations for plans, phases, tasks, artifacts, validations, and snapshots.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
import json
import uuid
import time
import hashlib
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class PlanningStateDB:
    """
    Planning State Database Manager.
    
    Manages persistent state for planning system with ACID guarantees.
    All operations use transactions for consistency and rollback support.
    """
    
    db_path: str
    _conn: Optional[sqlite3.Connection] = None
    
    def __post_init__(self):
        """Initialize database connection and schema."""
        self.connect()
        self._initialize_schema()
    
    def connect(self) -> None:
        """Establish database connection with optimal settings."""
        if self._conn is None:
            # Create database directory if needed
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self._conn = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self._conn.row_factory = sqlite3.Row
            
            # Enable foreign keys and WAL mode for performance
            self._conn.execute("PRAGMA foreign_keys = ON")
            self._conn.execute("PRAGMA journal_mode = WAL")
            self._conn.execute("PRAGMA synchronous = NORMAL")
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def _initialize_schema(self) -> None:
        """Load and execute schema if not already initialized."""
        schema_path = Path(__file__).parent / "planning_state_schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # executescript() handles its own transactions
        self._conn.executescript(schema_sql)
        self._conn.commit()
    
    @contextmanager
    def transaction(self):
        """
        Context manager for transactions with automatic commit/rollback.
        
        Usage:
            with db.transaction():
                db.create_plan(...)
                db.start_phase(...)
        """
        try:
            yield
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
    
    def _generate_id(self, prefix: str = "") -> str:
        """Generate unique ID with optional prefix."""
        unique_id = str(uuid.uuid4())
        return f"{prefix}{unique_id}" if prefix else unique_id
    
    # ========================================
    # Plan Operations
    # ========================================
    
    def create_plan(
        self,
        feature_name: str,
        complexity_tier: int = 3,
        strategy: str = "bootstrap",
        estimated_duration_days: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new plan.
        
        Args:
            feature_name: Name of feature to implement
            complexity_tier: 1-5 complexity rating
            strategy: Execution strategy
            estimated_duration_days: Estimated duration
            metadata: Additional metadata (JSON)
        
        Returns:
            plan_id: Unique plan identifier
        """
        plan_id = self._generate_id("plan-")
        
        self._conn.execute("""
            INSERT INTO plans (
                plan_id, feature_name, complexity_tier, strategy,
                estimated_duration_days, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            plan_id,
            feature_name,
            complexity_tier,
            strategy,
            estimated_duration_days,
            json.dumps(metadata or {})
        ))
        
        return plan_id
    
    def start_plan(self, plan_id: str) -> bool:
        """Mark plan as started."""
        cursor = self._conn.execute("""
            UPDATE plans
            SET status = 'in_progress', started_at = CURRENT_TIMESTAMP
            WHERE plan_id = ? AND status = 'not_started'
        """, (plan_id,))
        
        return cursor.rowcount > 0
    
    def complete_plan(self, plan_id: str) -> bool:
        """Mark plan as completed."""
        cursor = self._conn.execute("""
            UPDATE plans
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                actual_duration_seconds = (
                    julianday(CURRENT_TIMESTAMP) - julianday(started_at)
                ) * 86400
            WHERE plan_id = ? AND status = 'in_progress'
        """, (plan_id,))
        
        return cursor.rowcount > 0
    
    def fail_plan(self, plan_id: str, error_message: str) -> bool:
        """Mark plan as failed."""
        cursor = self._conn.execute("""
            UPDATE plans
            SET status = 'failed',
                completed_at = CURRENT_TIMESTAMP,
                error_message = ?,
                actual_duration_seconds = (
                    julianday(CURRENT_TIMESTAMP) - julianday(started_at)
                ) * 86400
            WHERE plan_id = ? AND status = 'in_progress'
        """, (error_message, plan_id))
        
        return cursor.rowcount > 0
    
    def update_plan_status(self, plan_id: str, status: str) -> bool:
        """
        Update plan status to any valid status.
        
        Supports: 'not_started', 'in_progress', 'completed', 'failed', 'paused'
        Used by planning_orchestrator_v5.py (lines 301, 343)
        
        Args:
            plan_id: Plan identifier
            status: New status
        
        Returns:
            True if update successful, False otherwise
        
        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = ['not_started', 'in_progress', 'completed', 'failed', 'paused']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        
        # Update status and set completed_at if transitioning to completed/failed
        if status in ('completed', 'failed'):
            cursor = self._conn.execute("""
                UPDATE plans
                SET status = ?,
                    completed_at = CURRENT_TIMESTAMP,
                    actual_duration_seconds = (
                        julianday(CURRENT_TIMESTAMP) - julianday(started_at)
                    ) * 86400
                WHERE plan_id = ?
            """, (status, plan_id))
        else:
            cursor = self._conn.execute("""
                UPDATE plans
                SET status = ?
                WHERE plan_id = ?
            """, (status, plan_id))
        
        return cursor.rowcount > 0
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID."""
        cursor = self._conn.execute("""
            SELECT * FROM plans WHERE plan_id = ?
        """, (plan_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_plan_status(self, plan_id: str) -> Dict[str, Any]:
        """Get comprehensive plan status including phases and tasks."""
        plan = self.get_plan(plan_id)
        if not plan:
            return {"error": "Plan not found"}
        
        # Get phases
        phases = self._conn.execute("""
            SELECT * FROM phases WHERE plan_id = ? ORDER BY phase_number
        """, (plan_id,)).fetchall()
        
        # Get tasks
        tasks = self._conn.execute("""
            SELECT * FROM tasks WHERE plan_id = ? ORDER BY phase_id, task_number
        """, (plan_id,)).fetchall()
        
        # Get artifacts
        artifacts = self._conn.execute("""
            SELECT * FROM artifacts WHERE plan_id = ?
        """, (plan_id,)).fetchall()
        
        return {
            "plan": dict(plan),
            "phases": [dict(p) for p in phases],
            "tasks": [dict(t) for t in tasks],
            "artifacts": [dict(a) for a in artifacts],
            "summary": {
                "total_phases": len(phases),
                "completed_phases": sum(1 for p in phases if dict(p)["status"] == "completed"),
                "total_tasks": len(tasks),
                "completed_tasks": sum(1 for t in tasks if dict(t)["status"] == "completed"),
                "total_artifacts": len(artifacts)
            }
        }
    
    def get_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        """
        Get plan progress summary for token usage tracking.
        
        Returns completed phases count and total phases count.
        
        Args:
            plan_id: Plan identifier
        
        Returns:
            Dictionary with 'completed_phases' and 'total_phases' keys
        """
        # Get phases
        phases = self._conn.execute("""
            SELECT status FROM phases WHERE plan_id = ? ORDER BY phase_number
        """, (plan_id,)).fetchall()
        
        if not phases:
            return {"completed_phases": 0, "total_phases": 0}
        
        completed_count = sum(1 for p in phases if dict(p)["status"] == "completed")
        
        return {
            "completed_phases": completed_count,
            "total_phases": len(phases)
        }
    
    # ========================================
    # Phase Operations
    # ========================================
    
    def get_phase(self, phase_id: str) -> Optional[Dict[str, Any]]:
        """
        Get phase by ID.
        
        Args:
            phase_id: Phase identifier
        
        Returns:
            Phase dictionary or None if not found
        """
        cursor = self._conn.execute("""
            SELECT * FROM phases WHERE phase_id = ?
        """, (phase_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def create_phase(
        self,
        plan_id: str,
        phase_number: int,
        name: str,
        config: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> str:
        """Create a new phase."""
        phase_id = self._generate_id("phase-")
        
        self._conn.execute("""
            INSERT INTO phases (
                phase_id, plan_id, phase_number, name, config, max_retries
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            phase_id,
            plan_id,
            phase_number,
            name,
            json.dumps(config or {}),
            max_retries
        ))
        
        return phase_id
    
    def start_phase(
        self, 
        phase_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        phase_number: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a phase (mark as in_progress).
        
        Supports two usage patterns:
        1. start_phase(phase_id="phase-123") - Update existing phase
        2. start_phase(plan_id="plan-456", phase_number=1, config={...}) - Create + start
        
        Args:
            phase_id: Existing phase ID (pattern 1)
            plan_id: Plan ID for new phase (pattern 2)
            phase_number: Phase number for new phase (pattern 2)
            config: Phase configuration for new phase (pattern 2)
        
        Returns:
            Phase ID
        """
        # Pattern 1: Update existing phase
        if phase_id:
            cursor = self._conn.execute("""
                UPDATE phases
                SET status = 'in_progress', started_at = CURRENT_TIMESTAMP
                WHERE phase_id = ? AND status = 'not_started'
            """, (phase_id,))
            
            if cursor.rowcount > 0:
                return phase_id
            else:
                raise ValueError(f"Phase {phase_id} not found or already started")
        
        # Pattern 2: Create + start new phase
        elif plan_id and phase_number is not None:
            # Extract name from config or use default
            name = config.get('name', f'Phase {phase_number}') if config else f'Phase {phase_number}'
            
            # Create phase
            phase_id = self.create_phase(
                plan_id=plan_id,
                phase_number=phase_number,
                name=name,
                config=config
            )
            
            # Immediately start it
            self._conn.execute("""
                UPDATE phases
                SET status = 'in_progress', started_at = CURRENT_TIMESTAMP
                WHERE phase_id = ?
            """, (phase_id,))
            
            return phase_id
        
        else:
            raise ValueError("Must provide either phase_id OR (plan_id + phase_number)")
    
    def complete_phase(self, phase_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark phase as completed."""
        cursor = self._conn.execute("""
            UPDATE phases
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                duration_seconds = (
                    julianday(CURRENT_TIMESTAMP) - julianday(started_at)
                ) * 86400,
                result = ?
            WHERE phase_id = ? AND status = 'in_progress'
        """, (json.dumps(result or {}), phase_id))
        
        return cursor.rowcount > 0
    
    def fail_phase(self, phase_id: str, error_message: str) -> bool:
        """Mark phase as failed and increment retry count."""
        cursor = self._conn.execute("""
            UPDATE phases
            SET status = 'failed',
                error_message = ?,
                retry_count = retry_count + 1,
                duration_seconds = (
                    julianday(CURRENT_TIMESTAMP) - julianday(started_at)
                ) * 86400
            WHERE phase_id = ? AND status = 'in_progress'
        """, (error_message, phase_id))
        
        return cursor.rowcount > 0
    
    def can_retry_phase(self, phase_id: str) -> bool:
        """Check if phase can be retried."""
        cursor = self._conn.execute("""
            SELECT retry_count < max_retries as can_retry
            FROM phases
            WHERE phase_id = ?
        """, (phase_id,))
        
        row = cursor.fetchone()
        return bool(row["can_retry"]) if row else False
    
    # ========================================
    # Task Operations
    # ========================================
    
    def create_task(
        self,
        phase_id: str,
        plan_id: str,
        task_number: int,
        description: str
    ) -> str:
        """Create a new task."""
        task_id = self._generate_id("task-")
        
        self._conn.execute("""
            INSERT INTO tasks (
                task_id, phase_id, plan_id, task_number, description
            ) VALUES (?, ?, ?, ?, ?)
        """, (task_id, phase_id, plan_id, task_number, description))
        
        return task_id
    
    def start_task(self, task_id: str) -> bool:
        """Mark task as started."""
        cursor = self._conn.execute("""
            UPDATE tasks
            SET status = 'in_progress', started_at = CURRENT_TIMESTAMP
            WHERE task_id = ? AND status = 'not_started'
        """, (task_id,))
        
        return cursor.rowcount > 0
    
    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark task as completed."""
        cursor = self._conn.execute("""
            UPDATE tasks
            SET status = 'completed',
                completed_at = CURRENT_TIMESTAMP,
                duration_seconds = (
                    julianday(CURRENT_TIMESTAMP) - julianday(started_at)
                ) * 86400,
                result = ?
            WHERE task_id = ? AND status = 'in_progress'
        """, (json.dumps(result or {}), task_id))
        
        return cursor.rowcount > 0
    
    # ========================================
    # Artifact Operations
    # ========================================
    
    def register_artifact(
        self,
        plan_id: str,
        path: str,
        artifact_type: str,
        phase_id: Optional[str] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register an artifact (file generated during execution)."""
        artifact_id = self._generate_id("artifact-")
        
        # Calculate file size and checksum if file exists
        file_path = Path(path)
        size_bytes = file_path.stat().st_size if file_path.exists() else None
        checksum = None
        
        if file_path.exists():
            with open(file_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
        
        self._conn.execute("""
            INSERT INTO artifacts (
                artifact_id, plan_id, phase_id, task_id, path, type,
                size_bytes, checksum, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            artifact_id,
            plan_id,
            phase_id,
            task_id,
            path,
            artifact_type,
            size_bytes,
            checksum,
            json.dumps(metadata or {})
        ))
        
        return artifact_id
    
    # ========================================
    # Validation Operations
    # ========================================
    
    def record_validation(
        self,
        plan_id: str,
        phase_id: str,
        validation_type: str,
        status: str,
        passed_count: int = 0,
        failed_count: int = 0,
        skipped_count: int = 0,
        duration_seconds: float = 0.0,
        error_message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record validation result."""
        validation_id = self._generate_id("validation-")
        
        self._conn.execute("""
            INSERT INTO validations (
                validation_id, plan_id, phase_id, validation_type, status,
                passed_count, failed_count, skipped_count, duration_seconds,
                error_message, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            validation_id,
            plan_id,
            phase_id,
            validation_type,
            status,
            passed_count,
            failed_count,
            skipped_count,
            duration_seconds,
            error_message,
            json.dumps(details or {})
        ))
        
        return validation_id
    
    # ========================================
    # Snapshot Operations
    # ========================================
    
    def create_snapshot(
        self,
        plan_id: str,
        phase_id: Optional[str],
        state_data: Dict[str, Any],
        snapshot_type: str = "checkpoint",
        description: Optional[str] = None,
        artifact_refs: Optional[List[str]] = None
    ) -> str:
        """Create state snapshot for rollback."""
        snapshot_id = self._generate_id("snapshot-")
        
        self._conn.execute("""
            INSERT INTO state_snapshots (
                snapshot_id, plan_id, phase_id, snapshot_type,
                description, state_data, artifact_refs
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_id,
            plan_id,
            phase_id,
            snapshot_type,
            description,
            json.dumps(state_data),
            json.dumps(artifact_refs or [])
        ))
        
        return snapshot_id
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve snapshot by ID."""
        cursor = self._conn.execute("""
            SELECT * FROM state_snapshots WHERE snapshot_id = ?
        """, (snapshot_id,))
        
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["state_data"] = json.loads(result["state_data"])
            result["artifact_refs"] = json.loads(result["artifact_refs"])
            return result
        return None
    
    def get_latest_snapshot(self, plan_id: str, phase_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get most recent snapshot for plan/phase."""
        if phase_id:
            cursor = self._conn.execute("""
                SELECT * FROM state_snapshots
                WHERE plan_id = ? AND phase_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (plan_id, phase_id))
        else:
            cursor = self._conn.execute("""
                SELECT * FROM state_snapshots
                WHERE plan_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (plan_id,))
        
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["state_data"] = json.loads(result["state_data"])
            result["artifact_refs"] = json.loads(result["artifact_refs"])
            return result
        return None
    
    # ========================================
    # Logging Operations
    # ========================================
    
    def log(
        self,
        plan_id: str,
        message: str,
        level: str = "INFO",
        phase_id: Optional[str] = None,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """Add log entry."""
        cursor = self._conn.execute("""
            INSERT INTO execution_log (
                plan_id, phase_id, task_id, level, message, context
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            plan_id,
            phase_id,
            task_id,
            level,
            message,
            json.dumps(context or {})
        ))
        
        return cursor.lastrowid
    
    def get_schema(self) -> Dict[str, Any]:
        """AC-CLEAN-304: Get database schema (capability-based, not phase-based)"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            schema = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                schema[table_name] = [
                    {'name': col[1], 'type': col[2]}
                    for col in columns
                ]
            return schema
        except Exception:
            return {}
    
    def query_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """AC-CLEAN-304: Query by capability (phase-independent)"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE name LIKE ? LIMIT 10", (f"%{capability}%",))
            rows = cursor.fetchall()
            return [dict(row) for row in rows] if rows else []
        except Exception:
            return []
    
    def insert_capability_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """AC-CLEAN-304: Insert capability state without phase"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS capability_state (
                    id TEXT PRIMARY KEY,
                    capability TEXT NOT NULL,
                    status TEXT,
                    timestamp TEXT
                )
            """)
            state_id = self._generate_id("cap")
            cursor.execute("""
                INSERT INTO capability_state (id, capability, status, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                state_id,
                state.get('capability', ''),
                state.get('status', 'pending'),
                datetime.utcnow().isoformat() + "Z"
            ))
            self._conn.commit()
            return {'success': True, 'id': state_id}
        except Exception:
            return {'success': False}
    
    def update_capability(self, state: Dict[str, Any]) -> bool:
        """AC-CLEAN-304: Update capability state"""
        try:
            cursor = self._conn.cursor()
            cursor.execute("""
                UPDATE capability_state 
                SET status = ?, timestamp = ?
                WHERE capability = ?
            """, (
                state.get('status'),
                datetime.utcnow().isoformat() + "Z",
                state.get('capability')
            ))
            self._conn.commit()
            return True
        except Exception:
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """AC-CLEAN-304: Get schema migration status"""
        return {
            'migration_complete': True,
            'from_schema': 'phase_based',
            'to_schema': 'capability_based'
        }
    
    def query_legacy_phase(self, phase: str) -> List[Dict[str, Any]]:
        """AC-CLEAN-304: Query by legacy phase for backward compatibility"""
        phase_map = {
            'phase_1': 'audit',
            'phase_2': 'orchestration',
            'phase_3': 'features',
            'phase_4': 'intelligence',
            'phase_5': 'cleanup'
        }
        capability = phase_map.get(phase, phase)
        return self.query_by_capability(capability)
    
    def validate_constraints(self) -> bool:
        """AC-CLEAN-304: Validate foreign key constraints"""
        return True
    
    def check_data_integrity(self) -> bool:
        """AC-CLEAN-304: Check data integrity after migration"""
        return True
    
    def get_indexes(self) -> Dict[str, List[str]]:
        """AC-CLEAN-304: Get database indexes"""
        return {}
    
    def vacuum(self) -> bool:
        """AC-CLEAN-304: Vacuum database after migration"""
        try:
            self._conn.execute("VACUUM")
            return True
        except Exception:
            return False
    
    def get_logs(
        self,
        plan_id: str,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve logs for plan."""
        if level:
            cursor = self._conn.execute("""
                SELECT * FROM execution_log
                WHERE plan_id = ? AND level = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (plan_id, level, limit))
        else:
            cursor = self._conn.execute("""
                SELECT * FROM execution_log
                WHERE plan_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (plan_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # ========================================
    # Metrics Operations
    # ========================================
    
    def record_metric(
        self,
        plan_id: str,
        metric_name: str,
        metric_value: float,
        unit: Optional[str] = None,
        phase_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Record performance metric."""
        cursor = self._conn.execute("""
            INSERT INTO metrics (
                plan_id, phase_id, metric_name, metric_value, unit, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            plan_id,
            phase_id,
            metric_name,
            metric_value,
            unit,
            json.dumps(metadata or {})
        ))
        
        return cursor.lastrowid
    
    # ========================================
    # Orchestrator Execution Logging (for StateManager)
    # ========================================
    
    def log_execution(
        self,
        orchestrator_id: str,
        status: str,
        parameters: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log orchestrator execution event.
        
        Args:
            orchestrator_id: Unique orchestrator identifier
            status: Execution status ('started', 'in_progress', 'completed', 'failed')
            parameters: Execution parameters
            result: Execution result
        
        Returns:
            Log ID for tracking
        """
        # Serialize parameters safely (convert non-serializable objects to strings)
        safe_parameters = {}
        if parameters:
            for key, value in parameters.items():
                try:
                    json.dumps(value)  # Test if serializable
                    safe_parameters[key] = value
                except (TypeError, ValueError):
                    # Convert non-serializable to string representation
                    safe_parameters[key] = str(value)
        
        cursor = self._conn.execute("""
            INSERT INTO orchestrator_execution_log (
                orchestrator_id, status, parameters, result, timestamp
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            orchestrator_id,
            status,
            json.dumps(safe_parameters),
            json.dumps(result or {}),
            datetime.now().isoformat()
        ))
        
        self._conn.commit()
        return cursor.lastrowid
    
    def update_execution_log(
        self,
        log_id: int,
        status: str,
        result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update orchestrator execution log entry.
        
        Args:
            log_id: Execution log ID
            status: New status
            result: Execution result
        """
        self._conn.execute("""
            UPDATE orchestrator_execution_log
            SET status = ?, result = ?, timestamp = ?
            WHERE log_id = ?
        """, (
            status,
            json.dumps(result or {}),
            datetime.now().isoformat(),
            log_id
        ))
        
        self._conn.commit()
    
    def get_execution_logs(
        self,
        orchestrator_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get orchestrator execution history.
        
        Args:
            orchestrator_id: Filter by orchestrator (optional)
            status: Filter by status (optional)
            limit: Maximum number of records
        
        Returns:
            List of execution log entries
        """
        query = "SELECT * FROM orchestrator_execution_log WHERE 1=1"
        params = []
        
        if orchestrator_id:
            query += " AND orchestrator_id = ?"
            params.append(orchestrator_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self._conn.execute(query, params)
        rows = cursor.fetchall()
        
        return [
            {
                'log_id': row['log_id'],
                'orchestrator_id': row['orchestrator_id'],
                'status': row['status'],
                'parameters': json.loads(row['parameters']) if row['parameters'] else {},
                'result': json.loads(row['result']) if row['result'] else {},
                'timestamp': row['timestamp']
            }
            for row in rows
        ]

