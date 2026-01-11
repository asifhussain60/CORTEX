"""
CORTEX 6.0 Enhanced Audit Logger - Infrastructure Layer

Implements AC-AUDIT-001 through AC-AUDIT-007:
- SQLite + JSONL dual storage with <5ms latency
- 7 audit categories (governance, orchestrator, validation, infrastructure, mcp, brain, integration)
- AC-ID traceability for compliance tracking
- Memory buffer with configurable flush thresholds
- Per-repo database isolation
- Queryable by AC-ID, orchestrator, date range, level
- Automatic vacuum with level-based retention
- Hash chain integrity (AC-AUDIT-007): Tamper detection via event_hash + prev_event_hash

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import sqlite3
import threading
import time
import yaml
import hashlib
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging


# ==============================================================================
# Enumerations
# ==============================================================================

class AuditLevel(str, Enum):
    """Audit log levels with retention policies."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """7 audit categories for CORTEX 6.0."""
    GOVERNANCE = "governance"          # AC-GOV-* enforcement
    ORCHESTRATOR = "orchestrator"      # Orchestrator execution
    VALIDATION = "validation"          # AC validation & testing
    INFRASTRUCTURE = "infrastructure"  # System infrastructure
    MCP = "mcp"                        # MCP tool invocations
    BRAIN = "brain"                    # Knowledge base operations
    INTEGRATION = "integration"        # External integrations


# ==============================================================================
# Data Structures
# ==============================================================================

@dataclass
class AuditEntry:
    """Structured audit log entry with AC-ID traceability."""
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    component: str
    operation: str
    message: str
    ac_id: Optional[str] = None
    correlation_id: Optional[str] = None
    duration_ms: Optional[float] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['level'] = self.level.value
        result['category'] = self.category.value
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string for JSONL storage."""
        return json.dumps(self.to_dict(), default=str)


# ==============================================================================
# AC-AUDIT-001: Queryable Audit Storage
# ==============================================================================

class AuditStorage:
    """
    SQLite-based audit storage with queryable interface.
    
    Implements AC-AUDIT-001: Queryable by AC-ID, orchestrator, date range, level.
    """
    
    def __init__(self, db_path: Path):
        """Initialize audit storage."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._lock = threading.Lock()
    
    def _init_database(self):
        """Initialize SQLite database schema with hash chain support (AC-AUDIT-007)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    component TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    message TEXT NOT NULL,
                    ac_id TEXT,
                    correlation_id TEXT,
                    duration_ms REAL,
                    context TEXT,
                    metadata TEXT,
                    event_hash TEXT NOT NULL,
                    prev_event_hash TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Indexes for fast queries (AC-AUDIT-001)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ac_id ON audit_logs(ac_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_component ON audit_logs(component)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_level ON audit_logs(level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON audit_logs(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_correlation ON audit_logs(correlation_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON audit_logs(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_event_hash ON audit_logs(event_hash)")
            
            # Check if hash columns exist in existing database (migration support)
            cursor = conn.execute("PRAGMA table_info(audit_logs)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'event_hash' not in columns:
                conn.execute("ALTER TABLE audit_logs ADD COLUMN event_hash TEXT")
            if 'prev_event_hash' not in columns:
                conn.execute("ALTER TABLE audit_logs ADD COLUMN prev_event_hash TEXT")
            
            conn.commit()
    
    def _compute_event_hash(
        self,
        timestamp: str,
        level: str,
        category: str,
        component: str,
        operation: str,
        message: str,
        ac_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        prev_hash: Optional[str] = None
    ) -> str:
        """
        Compute SHA-256 hash of audit event (AC-AUDIT-007).
        
        Hash includes all critical fields to detect tampering.
        Must complete in <1ms (AC-AUDIT-007 performance requirement).
        
        Args:
            timestamp: Event timestamp
            level: Audit level
            category: Audit category
            component: Component name
            operation: Operation name
            message: Event message
            ac_id: Optional AC-ID
            correlation_id: Optional correlation ID
            prev_hash: Previous event hash (for chain linkage)
        
        Returns:
            64-character SHA-256 hex digest
        """
        # Concatenate critical fields
        hash_input = f"{timestamp}|{level}|{category}|{component}|{operation}|{message}"
        if ac_id:
            hash_input += f"|{ac_id}"
        if correlation_id:
            hash_input += f"|{correlation_id}"
        if prev_hash:
            hash_input += f"|{prev_hash}"
        
        # Compute SHA-256
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
    
    def _get_last_event_hash(self) -> Optional[str]:
        """
        Get the event_hash of the most recent audit entry (AC-AUDIT-007).
        
        Returns:
            Previous event hash or None if no events exist
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT event_hash FROM audit_logs ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return row[0] if row else None
    
    def log(
        self,
        level: AuditLevel,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        ac_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ):
        """
        Log an audit entry to SQLite with hash chain (AC-AUDIT-007).
        
        Args:
            level: Audit level (ERROR, INFO, etc.)
            category: Audit category (governance, orchestrator, etc.)
            component: Component name (planning, tdd, etc.)
            operation: Operation name (execute, validate, etc.)
            message: Human-readable message
            ac_id: Acceptance criteria ID (e.g., AC-GOV-001)
            correlation_id: Request correlation ID
            duration_ms: Operation duration in milliseconds
            context: Contextual data dictionary
            metadata: Additional metadata
            timestamp: Override timestamp (for testing)
        """
        ts = timestamp or datetime.now().isoformat()
        
        with self._lock:
            # Get previous event hash for chain linkage (AC-AUDIT-007)
            prev_hash = self._get_last_event_hash()
            
            # Compute event hash (AC-AUDIT-007)
            event_hash = self._compute_event_hash(
                timestamp=ts,
                level=level.value,
                category=category.value,
                component=component,
                operation=operation,
                message=message,
                ac_id=ac_id,
                correlation_id=correlation_id,
                prev_hash=prev_hash
            )
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO audit_logs 
                    (timestamp, level, category, component, operation, message, 
                     ac_id, correlation_id, duration_ms, context, metadata,
                     event_hash, prev_event_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ts,
                    level.value,
                    category.value,
                    component,
                    operation,
                    message,
                    ac_id,
                    correlation_id,
                    duration_ms,
                    json.dumps(context) if context else None,
                    json.dumps(metadata) if metadata else None,
                    event_hash,
                    prev_hash
                ))
                conn.commit()
    
    def query(
        self,
        ac_id: Optional[str] = None,
        component: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        category: Optional[AuditCategory] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
        order_by: str = "timestamp",
        order_dir: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs with filters.
        
        Implements AC-AUDIT-001: Queryable interface with pagination.
        
        Args:
            ac_id: Filter by acceptance criteria ID
            component: Filter by component name
            level: Filter by audit level
            category: Filter by audit category
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)
            page: Page number (1-indexed)
            page_size: Results per page
            order_by: Order by field (timestamp, level, etc.)
            order_dir: Order direction (ASC, DESC)
        
        Returns:
            List of matching audit entries
        """
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if ac_id:
            query += " AND ac_id = ?"
            params.append(ac_id)
        
        if component:
            query += " AND component = ?"
            params.append(component)
        
        if level:
            query += " AND level = ?"
            params.append(level.value)
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        # Order and pagination
        query += f" ORDER BY {order_by} {order_dir}"
        offset = (page - 1) * page_size
        query += f" LIMIT {page_size} OFFSET {offset}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                entry = dict(row)
                # Parse JSON fields
                if entry['context']:
                    entry['context'] = json.loads(entry['context'])
                if entry['metadata']:
                    entry['metadata'] = json.loads(entry['metadata'])
                results.append(entry)
            
            return results
    
    def count(
        self,
        ac_id: Optional[str] = None,
        component: Optional[str] = None,
        level: Optional[AuditLevel] = None,
        category: Optional[AuditCategory] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> int:
        """Count matching entries for pagination."""
        query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
        params = []
        
        if ac_id:
            query += " AND ac_id = ?"
            params.append(ac_id)
        
        if component:
            query += " AND component = ?"
            params.append(component)
        
        if level:
            query += " AND level = ?"
            params.append(level.value)
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()[0]
    
    def verify_chain(self) -> Tuple[bool, Optional[str]]:
        """
        Verify hash chain integrity (AC-AUDIT-007).
        
        Recalculates event_hash for each entry and verifies:
        1. event_hash matches recalculated hash
        2. prev_event_hash matches previous entry's event_hash
        
        Must complete in <10ms per 100 events (AC-AUDIT-007 performance requirement).
        
        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if chain is valid
            - (False, error_message) if tampering detected
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, timestamp, level, category, component, operation, message, "
                "ac_id, correlation_id, event_hash, prev_event_hash "
                "FROM audit_logs ORDER BY id ASC"
            )
            events = cursor.fetchall()
        
        if not events:
            return (True, None)  # Empty chain is valid
        
        prev_hash = None
        for event in events:
            # Verify prev_event_hash linkage
            if event['prev_event_hash'] != prev_hash:
                return (False, f"Chain broken at event {event['id']}: "
                              f"prev_event_hash mismatch (expected {prev_hash}, got {event['prev_event_hash']})")
            
            # Recalculate event_hash
            computed_hash = self._compute_event_hash(
                timestamp=event['timestamp'],
                level=event['level'],
                category=event['category'],
                component=event['component'],
                operation=event['operation'],
                message=event['message'],
                ac_id=event['ac_id'],
                correlation_id=event['correlation_id'],
                prev_hash=prev_hash
            )
            
            # Verify event_hash matches
            if event['event_hash'] != computed_hash:
                return (False, f"Tamper detected at event {event['id']}: "
                              f"event_hash mismatch (stored {event['event_hash']}, computed {computed_hash})")
            
            prev_hash = event['event_hash']
        
        return (True, None)
    
    def query_audit_trail(
        self,
        limit: int = 100,
        order: str = "DESC"
    ) -> List[Dict[str, Any]]:
        """
        Query audit trail for chain verification tests.
        
        Args:
            limit: Number of recent events to return
            order: Sort order ("ASC" or "DESC")
        
        Returns:
            List of audit entries with hash chain fields
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                f"SELECT * FROM audit_logs ORDER BY id {order} LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                entry = dict(row)
                # Parse JSON fields
                if entry.get('context'):
                    entry['context'] = json.loads(entry['context'])
                if entry.get('metadata'):
                    entry['metadata'] = json.loads(entry['metadata'])
                results.append(entry)
            
            return results


# ==============================================================================
# AC-AUDIT-002: Memory Buffer with Flush Thresholds
# ==============================================================================

class AuditMemoryBuffer:
    """
    In-memory buffer with configurable flush thresholds.
    
    Implements AC-AUDIT-002: Buffer size, memory limit, time threshold, error flush.
    """
    
    def __init__(
        self,
        storage_path: Path,
        max_entries: int = 1000,
        max_memory_mb: float = 10.0,
        flush_interval_seconds: int = 60
    ):
        """
        Initialize memory buffer.
        
        Args:
            storage_path: Path to SQLite database
            max_entries: Max entries before flush (default 1000)
            max_memory_mb: Max memory usage before flush (default 10MB)
            flush_interval_seconds: Auto-flush interval (default 60s)
        """
        self.storage = AuditStorage(storage_path)
        self.max_entries = max_entries
        self.max_memory_mb = max_memory_mb
        self.flush_interval_seconds = flush_interval_seconds
        
        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._last_flush = time.time()
        self._shutdown = False
        
        # Start background flush thread
        self._flush_thread = threading.Thread(target=self._auto_flush_loop, daemon=True)
        self._flush_thread.start()
    
    def log(
        self,
        level: AuditLevel,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        **kwargs
    ):
        """
        Log entry to buffer with automatic flush triggers.
        
        Implements AC-AUDIT-002: Immediate flush on ERROR level.
        """
        entry = {
            'level': level,
            'category': category,
            'component': component,
            'operation': operation,
            'message': message,
            **kwargs
        }
        
        with self._lock:
            self._buffer.append(entry)
            
            # Immediate flush on ERROR (AC-AUDIT-002)
            if level == AuditLevel.ERROR or level == AuditLevel.CRITICAL:
                self._flush_to_storage()
            # Flush if buffer size exceeded
            elif len(self._buffer) >= self.max_entries:
                self._flush_to_storage()
            # Flush if memory limit exceeded (approximation)
            elif self._estimate_memory_mb() >= self.max_memory_mb:
                self._flush_to_storage()
    
    def _flush_to_storage(self):
        """Flush buffer to storage (must hold lock)."""
        if not self._buffer:
            return
        
        for entry in self._buffer:
            self.storage.log(**entry)
        
        self._buffer.clear()
        self._last_flush = time.time()
    
    def flush(self):
        """Public flush method for manual flushing."""
        with self._lock:
            self._flush_to_storage()
    
    def shutdown(self):
        """Graceful shutdown with final flush."""
        self._shutdown = True
        with self._lock:
            self._flush_to_storage()
    
    def _auto_flush_loop(self):
        """Background thread for time-based flushing."""
        while not self._shutdown:
            time.sleep(1)
            
            with self._lock:
                elapsed = time.time() - self._last_flush
                if elapsed >= self.flush_interval_seconds and self._buffer:
                    self._flush_to_storage()
    
    def _estimate_memory_mb(self) -> float:
        """Estimate buffer memory usage in MB."""
        if not self._buffer:
            return 0.0
        
        # Rough estimate: JSON size of buffer
        json_size = len(json.dumps(self._buffer, default=str))
        return json_size / (1024 * 1024)


# ==============================================================================
# AC-AUDIT-003: Per-Repo Isolation
# ==============================================================================

class EnhancedAuditLogger:
    """
    Enhanced audit logger with per-repo isolation.
    
    Implements AC-AUDIT-003: Per-repo SQLite database isolation.
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize enhanced audit logger.
        
        Args:
            repo_path: Repository path (default: auto-detect)
        """
        self.repo_path = self._detect_repo(repo_path)
        self.db_path = self.repo_path / "cortex-brain" / "state" / "audit.db"
        self.buffer = AuditMemoryBuffer(
            storage_path=self.db_path,
            max_entries=1000,
            max_memory_mb=10.0,
            flush_interval_seconds=60
        )
    
    def _detect_repo(self, repo_path: Optional[Path]) -> Path:
        """Detect repository path from context."""
        if repo_path:
            return Path(repo_path)
        
        # Auto-detect from current working directory
        import os
        cwd = Path(os.getcwd())
        
        # Look for .git directory
        current = cwd
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        
        # Fallback to cwd
        return cwd
    
    def set_repo_context(self, repo_path: Path):
        """
        Switch repository context.
        
        Implements AC-AUDIT-003: Context switching.
        """
        # Flush current buffer
        self.buffer.shutdown()
        
        # Switch to new repo
        self.repo_path = Path(repo_path)
        self.db_path = self.repo_path / "cortex-brain" / "state" / "audit.db"
        self.buffer = AuditMemoryBuffer(
            storage_path=self.db_path,
            max_entries=1000,
            max_memory_mb=10.0,
            flush_interval_seconds=60
        )
    
    def log(
        self,
        level: AuditLevel,
        category: AuditCategory,
        component: str,
        operation: str,
        message: str,
        ac_id: Optional[str] = None,
        **kwargs
    ):
        """
        Log audit entry with AC-ID traceability.
        
        Implements AC-AUDIT-001, AC-AUDIT-002, AC-AUDIT-003.
        """
        self.buffer.log(
            level=level,
            category=category,
            component=component,
            operation=operation,
            message=message,
            ac_id=ac_id,
            **kwargs
        )
    
    def flush(self):
        """Flush buffer to storage."""
        self.buffer.flush()
    
    def query(self, **kwargs) -> List[Dict[str, Any]]:
        """Query audit logs from storage."""
        storage = AuditStorage(self.db_path)
        return storage.query(**kwargs)


# ==============================================================================
# AC-AUDIT-006: Retention Policy Configuration
# ==============================================================================

DEFAULT_RETENTION_POLICY = {
    "ERROR": 90,
    "CRITICAL": 90,
    "WARNING": 60,
    "INFO": 30,
    "DEBUG": 7,
    "TRACE": 7
}


def load_retention_policy(
    config_path: Path,
    override_path: Optional[Path] = None
) -> Dict[str, int]:
    """
    Load retention policy from configuration.
    
    Implements AC-AUDIT-006: Configurable retention policy.
    
    Args:
        config_path: Path to audit-config.yaml
        override_path: Optional repo-specific override config
    
    Returns:
        Retention policy dictionary (level -> days)
    """
    policy = DEFAULT_RETENTION_POLICY.copy()
    
    # Load base config
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if 'retention_policy' in config:
                policy.update(config['retention_policy'])
    
    # Apply repo-specific overrides
    if override_path and override_path.exists():
        with open(override_path, 'r') as f:
            override_config = yaml.safe_load(f)
            if 'retention_policy' in override_config:
                policy.update(override_config['retention_policy'])
    
    return policy


# ==============================================================================
# AC-AUDIT-005: Automatic Vacuum
# ==============================================================================

class AuditVacuum:
    """
    Automatic vacuum for audit log cleanup.
    
    Implements AC-AUDIT-005: Automatic vacuum with retention policy.
    """
    
    def __init__(self, storage: AuditStorage):
        """Initialize vacuum with storage."""
        self.storage = storage
    
    def run(self, retention_policy: Dict[str, int]) -> Dict[str, Any]:
        """
        Run vacuum to remove expired logs.
        
        Args:
            retention_policy: Retention policy (level -> days)
        
        Returns:
            Vacuum result with deleted_count and space_reclaimed_bytes
        """
        deleted_count = 0
        size_before = self.storage.db_path.stat().st_size
        
        with sqlite3.connect(self.storage.db_path) as conn:
            # Delete expired logs for each level
            for level, retention_days in retention_policy.items():
                cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
                
                # Handle both upper and lower case level names
                level_lower = level.lower()
                
                result = conn.execute(
                    "DELETE FROM audit_logs WHERE LOWER(level) = ? AND timestamp < ?",
                    (level_lower, cutoff_date)
                )
                deleted_count += result.rowcount
            
            conn.commit()
            
            # Run VACUUM to reclaim space
            conn.execute("VACUUM")
        
        size_after = self.storage.db_path.stat().st_size
        space_reclaimed = max(0, size_before - size_after)
        
        return {
            "deleted_count": deleted_count,
            "space_reclaimed_bytes": space_reclaimed,
            "size_before": size_before,
            "size_after": size_after
        }


# ==============================================================================
# AC-ID Implementation Tracking (Enhancement)
# ==============================================================================

class ACImplementationTracker:
    """
    Track AC-ID implementations with test evidence in audit logs.
    
    Provides clear audit trail of:
    - When AC-IDs were implemented
    - Test results (pass/fail counts)
    - Implementation status changes
    - Integration with progress tracking
    """
    
    def __init__(self, storage: AuditStorage):
        """Initialize tracker with audit storage."""
        self.storage = storage
    
    def log_ac_implementation(
        self,
        ac_id: str,
        status: str,
        tests_passed: int,
        tests_total: int,
        correlation_id: Optional[str] = None,
        phase: Optional[str] = None,
        component: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log AC-ID implementation with test evidence.
        
        Args:
            ac_id: Acceptance criteria ID (e.g., AC-ORCH-007)
            status: Implementation status (implemented, partial, planned)
            tests_passed: Number of tests that passed
            tests_total: Total number of tests
            correlation_id: Request correlation ID
            phase: Phase name (e.g., "Phase 2: Orchestration Core")
            component: Component name (e.g., "MasterOrchestrator")
            metadata: Additional metadata
        """
        pass_rate = round((tests_passed / tests_total * 100), 1) if tests_total > 0 else 0
        
        message = f"{ac_id} {status}: {tests_passed}/{tests_total} tests passing ({pass_rate}%)"
        
        context = {
            "ac_id": ac_id,
            "status": status,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "pass_rate": pass_rate,
            "phase": phase,
            "component": component
        }
        
        # Determine log level based on status
        if status == "implemented" and tests_passed == tests_total:
            level = AuditLevel.INFO
        elif status == "partial" or tests_passed < tests_total:
            level = AuditLevel.WARNING
        else:
            level = AuditLevel.INFO
        
        self.storage.log(
            level=level,
            category=AuditCategory.VALIDATION,
            component=component or "ACImplementation",
            operation="ac_implementation",
            message=message,
            ac_id=ac_id,
            correlation_id=correlation_id,
            context=context,
            metadata=metadata
        )
    
    def log_phase_completion(
        self,
        phase_number: str,
        phase_name: str,
        ac_ids_completed: int,
        ac_ids_total: int,
        tests_passed: int,
        tests_total: int,
        correlation_id: Optional[str] = None
    ):
        """
        Log phase completion milestone.
        
        Args:
            phase_number: Phase number (e.g., "2", "1.5")
            phase_name: Phase name (e.g., "Orchestration Core")
            ac_ids_completed: Number of AC-IDs completed
            ac_ids_total: Total AC-IDs in phase
            tests_passed: Total tests passing for phase
            tests_total: Total tests in phase
            correlation_id: Request correlation ID
        """
        completion_pct = round((ac_ids_completed / ac_ids_total * 100), 1)
        pass_rate = round((tests_passed / tests_total * 100), 1) if tests_total > 0 else 0
        
        message = (
            f"Phase {phase_number} ({phase_name}) complete: "
            f"{ac_ids_completed}/{ac_ids_total} AC-IDs ({completion_pct}%), "
            f"{tests_passed}/{tests_total} tests ({pass_rate}%)"
        )
        
        context = {
            "phase_number": phase_number,
            "phase_name": phase_name,
            "ac_ids_completed": ac_ids_completed,
            "ac_ids_total": ac_ids_total,
            "completion_percentage": completion_pct,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "pass_rate": pass_rate,
            "milestone": "phase_completion"
        }
        
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="PhaseManager",
            operation="phase_completion",
            message=message,
            correlation_id=correlation_id,
            context=context
        )
    
    def log_test_execution(
        self,
        ac_id: str,
        test_file: str,
        tests_passed: int,
        tests_failed: int,
        duration_ms: float,
        correlation_id: Optional[str] = None
    ):
        """
        Log test execution results for an AC-ID.
        
        Args:
            ac_id: Acceptance criteria ID
            test_file: Test file path
            tests_passed: Number of tests that passed
            tests_failed: Number of tests that failed
            duration_ms: Execution duration in milliseconds
            correlation_id: Request correlation ID
        """
        tests_total = tests_passed + tests_failed
        status = "✓ PASS" if tests_failed == 0 else "✗ FAIL"
        
        message = f"{ac_id} tests {status}: {tests_passed}/{tests_total} passing in {duration_ms:.0f}ms"
        
        context = {
            "ac_id": ac_id,
            "test_file": test_file,
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "tests_total": tests_total,
            "duration_ms": duration_ms
        }
        
        level = AuditLevel.INFO if tests_failed == 0 else AuditLevel.WARNING
        
        self.storage.log(
            level=level,
            category=AuditCategory.VALIDATION,
            component="TestRunner",
            operation="test_execution",
            message=message,
            ac_id=ac_id,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            context=context
        )
    
    def query_ac_history(
        self,
        ac_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Query complete implementation history for an AC-ID.
        
        Args:
            ac_id: Acceptance criteria ID
            limit: Maximum number of entries to return
        
        Returns:
            List of audit entries showing AC-ID implementation history
        """
        return self.storage.query(
            ac_id=ac_id,
            category=AuditCategory.VALIDATION,
            page_size=limit
        )
    
    def get_implementation_summary(self) -> Dict[str, Any]:
        """
        Get summary of all AC-ID implementations from audit logs.
        
        Returns:
            Summary with counts by status, recent implementations, etc.
        """
        with sqlite3.connect(self.storage.db_path) as conn:
            # Get all AC implementation entries
            cursor = conn.execute("""
                SELECT ac_id, context, timestamp
                FROM audit_logs
                WHERE category = 'validation' AND operation = 'ac_implementation'
                ORDER BY timestamp DESC
            """)
            
            implementations = {}
            for row in cursor.fetchall():
                ac_id = row[0]
                context = json.loads(row[1]) if row[1] else {}
                timestamp = row[2]
                
                if ac_id and ac_id not in implementations:
                    implementations[ac_id] = {
                        "ac_id": ac_id,
                        "status": context.get("status", "unknown"),
                        "tests_passed": context.get("tests_passed", 0),
                        "tests_total": context.get("tests_total", 0),
                        "pass_rate": context.get("pass_rate", 0),
                        "phase": context.get("phase"),
                        "last_updated": timestamp
                    }
        
        # Calculate summary statistics
        total_acs = len(implementations)
        implemented = sum(1 for ac in implementations.values() if ac["status"] == "implemented")
        partial = sum(1 for ac in implementations.values() if ac["status"] == "partial")
        
        return {
            "total_ac_ids": total_acs,
            "implemented": implemented,
            "partial": partial,
            "completion_rate": round((implemented / total_acs * 100), 1) if total_acs > 0 else 0,
            "implementations": list(implementations.values())
        }

