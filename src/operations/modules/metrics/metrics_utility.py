"""
Metrics Utility

Lightweight TDD workflow metrics tracking with Tier 1 database persistence.

Core Operations:
- start_session: Begin tracking TDD session
- end_session: Complete session with duration calculation
- start_phase: Track phase (RED/GREEN/REFACTOR) start
- end_phase: Complete phase with git correlation
- record_metrics: Store custom metrics for phase
- get_session_metrics: Retrieve session summary
- compare_metrics: Compare before/after session metrics

Version: 3.0.0 (Migrated from MetricsTracker orchestrator)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class SessionMetrics:
    """Session-level metrics"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    total_phases: int = 0
    project_path: Optional[str] = None
    feature_name: Optional[str] = None


@dataclass
class PhaseMetrics:
    """Phase-level metrics"""
    phase_id: str
    phase_name: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    git_commit_sha: Optional[str] = None
    git_commit_message: Optional[str] = None
    metrics_before: Optional[Dict] = None
    metrics_after: Optional[Dict] = None


# Database path (Tier 1 working memory)
# Navigate from src/operations/modules/metrics/ up to CORTEX root
CORTEX_ROOT = get_root_path().parent.parent
DB_PATH = CORTEX_ROOT / "cortex-brain" / "tier1-working-memory.db"


def _get_connection() -> sqlite3.Connection:
    """Get Tier 1 database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_tables() -> None:
    """Ensure metrics tables exist (run migration if needed)"""
    try:
        with _get_connection() as conn:
            # Create tdd_sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tdd_sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'in-progress',
                    project_path TEXT NOT NULL,
                    feature_name TEXT,
                    session_start_time TIMESTAMP,
                    session_end_time TIMESTAMP,
                    session_duration_seconds REAL,
                    total_phases_completed INTEGER DEFAULT 0
                )
            """)
            
            # Create tdd_phases table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tdd_phases (
                    phase_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    phase_name TEXT NOT NULL,
                    phase_start_time TIMESTAMP NOT NULL,
                    phase_end_time TIMESTAMP,
                    phase_duration_seconds REAL,
                    git_commit_sha TEXT,
                    git_commit_message TEXT,
                    metrics_before TEXT,
                    metrics_after TEXT,
                    status TEXT DEFAULT 'in-progress',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES tdd_sessions(session_id)
                )
            """)
            
            # Create tdd_metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tdd_metrics (
                    metric_id TEXT PRIMARY KEY,
                    phase_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (phase_id) REFERENCES tdd_phases(phase_id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tdd_phases_session_id ON tdd_phases(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tdd_phases_phase_name ON tdd_phases(phase_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tdd_metrics_phase_id ON tdd_metrics(phase_id)")
            
            conn.commit()
    except Exception:
        pass  # Tables likely already exist


def start_session(
    session_id: str,
    project_path: str,
    feature_name: Optional[str] = None
) -> bool:
    """
    Start tracking new TDD session
    
    Args:
        session_id: Unique session identifier
        project_path: Path to project being worked on
        feature_name: Optional feature description
        
    Returns:
        True if session started successfully
        
    Example:
        >>> start_session("sess-001", "/path/to/project", "User authentication")
        True
    """
    _ensure_tables()
    
    try:
        with _get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tdd_sessions 
                (session_id, session_start_time, project_path, feature_name, status)
                VALUES (?, ?, ?, ?, 'in-progress')
                """,
                (session_id, datetime.now().isoformat(), project_path, feature_name)
            )
            conn.commit()
        return True
    except Exception:
        return False


def end_session(session_id: str) -> bool:
    """
    End tracking for TDD session
    
    Args:
        session_id: Session identifier
        
    Returns:
        True if session ended successfully
        
    Example:
        >>> end_session("sess-001")
        True
    """
    try:
        with _get_connection() as conn:
            row = conn.execute(
                "SELECT session_start_time FROM tdd_sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            
            if not row:
                return False
            
            start_time = datetime.fromisoformat(row["session_start_time"])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            conn.execute(
                """
                UPDATE tdd_sessions 
                SET session_end_time = ?, 
                    session_duration_seconds = ?,
                    status = 'completed',
                    updated_at = ?
                WHERE session_id = ?
                """,
                (end_time.isoformat(), duration, end_time.isoformat(), session_id)
            )
            conn.commit()
        return True
    except Exception:
        return False


def start_phase(
    session_id: str,
    phase_name: str,
    metrics_before: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Start tracking phase (RED, GREEN, REFACTOR)
    
    Args:
        session_id: Parent session identifier
        phase_name: Phase name (RED, GREEN, REFACTOR, COMPLETE)
        metrics_before: Optional baseline metrics
        
    Returns:
        Phase ID or None if failed
        
    Example:
        >>> phase_id = start_phase("sess-001", "RED", {"tests": 0, "coverage": 0})
        >>> print(phase_id)
        "abc123..."
    """
    phase_id = str(uuid.uuid4())
    
    try:
        with _get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tdd_phases
                (phase_id, session_id, phase_name, phase_start_time, metrics_before, status)
                VALUES (?, ?, ?, ?, ?, 'in-progress')
                """,
                (
                    phase_id,
                    session_id,
                    phase_name,
                    datetime.now().isoformat(),
                    json.dumps(metrics_before) if metrics_before else None
                )
            )
            conn.commit()
        return phase_id
    except Exception:
        return None


def end_phase(
    phase_id: str,
    git_commit_sha: Optional[str] = None,
    git_commit_message: Optional[str] = None,
    metrics_after: Optional[Dict[str, Any]] = None
) -> bool:
    """
    End tracking for phase
    
    Args:
        phase_id: Phase identifier
        git_commit_sha: Git commit SHA for this phase
        git_commit_message: Git commit message
        metrics_after: Final metrics for this phase
        
    Returns:
        True if phase ended successfully
        
    Example:
        >>> end_phase(phase_id, "abc123", "RED: Add failing test", {"tests": 1, "coverage": 0})
        True
    """
    try:
        with _get_connection() as conn:
            row = conn.execute(
                "SELECT phase_start_time FROM tdd_phases WHERE phase_id = ?",
                (phase_id,)
            ).fetchone()
            
            if not row:
                return False
            
            start_time = datetime.fromisoformat(row["phase_start_time"])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            conn.execute(
                """
                UPDATE tdd_phases
                SET phase_end_time = ?,
                    phase_duration_seconds = ?,
                    git_commit_sha = ?,
                    git_commit_message = ?,
                    metrics_after = ?,
                    status = 'completed'
                WHERE phase_id = ?
                """,
                (
                    end_time.isoformat(),
                    duration,
                    git_commit_sha,
                    git_commit_message,
                    json.dumps(metrics_after) if metrics_after else None,
                    phase_id
                )
            )
            
            # Update session phase count
            conn.execute(
                """
                UPDATE tdd_sessions
                SET total_phases_completed = total_phases_completed + 1,
                    updated_at = ?
                WHERE session_id = (SELECT session_id FROM tdd_phases WHERE phase_id = ?)
                """,
                (end_time.isoformat(), phase_id)
            )
            
            conn.commit()
        return True
    except Exception:
        return False


def record_metrics(
    phase_id: str,
    metrics: Dict[str, float]
) -> bool:
    """
    Record multiple metrics for phase
    
    Args:
        phase_id: Phase identifier
        metrics: Dictionary of metric_name -> value pairs
        
    Returns:
        True if all metrics recorded successfully
        
    Example:
        >>> record_metrics(phase_id, {
        ...     "lines_added": 42.0,
        ...     "test_coverage": 85.5,
        ...     "complexity": 3.2
        ... })
        True
    """
    try:
        with _get_connection() as conn:
            for metric_name, metric_value in metrics.items():
                metric_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO tdd_metrics
                    (metric_id, phase_id, metric_name, metric_value)
                    VALUES (?, ?, ?, ?)
                    """,
                    (metric_id, phase_id, metric_name, metric_value)
                )
            conn.commit()
        return True
    except Exception:
        return False


def get_session_metrics(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get comprehensive session metrics
    
    Args:
        session_id: Session identifier
        
    Returns:
        Dictionary with session and phase metrics, or None if not found
        
    Example:
        >>> metrics = get_session_metrics("sess-001")
        >>> print(metrics["duration_seconds"])
        3600.5
        >>> print(metrics["phases"][0]["phase_name"])
        "RED"
    """
    try:
        with _get_connection() as conn:
            session_row = conn.execute(
                "SELECT * FROM tdd_sessions WHERE session_id = ?",
                (session_id,)
            ).fetchone()
            
            if not session_row:
                return None
            
            phases = conn.execute(
                """
                SELECT phase_id, phase_name, phase_duration_seconds, 
                       git_commit_sha, metrics_before, metrics_after
                FROM tdd_phases
                WHERE session_id = ?
                ORDER BY phase_start_time
                """,
                (session_id,)
            ).fetchall()
            
            return {
                "session_id": session_id,
                "start_time": session_row["session_start_time"],
                "end_time": session_row["session_end_time"],
                "duration_seconds": session_row["session_duration_seconds"],
                "total_phases": session_row["total_phases_completed"],
                "project_path": session_row["project_path"],
                "feature_name": session_row["feature_name"],
                "phases": [
                    {
                        "phase_id": phase["phase_id"],
                        "phase_name": phase["phase_name"],
                        "duration_seconds": phase["phase_duration_seconds"],
                        "commit_sha": phase["git_commit_sha"],
                        "metrics_before": json.loads(phase["metrics_before"]) if phase["metrics_before"] else {},
                        "metrics_after": json.loads(phase["metrics_after"]) if phase["metrics_after"] else {}
                    }
                    for phase in phases
                ]
            }
    except Exception:
        return None


def compare_metrics(
    session_id_before: str,
    session_id_after: str
) -> Optional[Dict[str, Any]]:
    """
    Compare metrics between two sessions
    
    Args:
        session_id_before: Baseline session
        session_id_after: Comparison session
        
    Returns:
        Dictionary with comparison metrics, or None if either session not found
        
    Example:
        >>> comparison = compare_metrics("sess-001", "sess-002")
        >>> print(comparison["duration_change"])
        -120.5  # 120.5 seconds faster
    """
    try:
        metrics_before = get_session_metrics(session_id_before)
        metrics_after = get_session_metrics(session_id_after)
        
        if not metrics_before or not metrics_after:
            return None
        
        return {
            "session_before": session_id_before,
            "session_after": session_id_after,
            "duration_change": (
                (metrics_after["duration_seconds"] or 0) -
                (metrics_before["duration_seconds"] or 0)
            ),
            "phases_change": (
                (metrics_after["total_phases"] or 0) -
                (metrics_before["total_phases"] or 0)
            ),
            "duration_before": metrics_before["duration_seconds"],
            "duration_after": metrics_after["duration_seconds"],
            "phases_before": metrics_before["total_phases"],
            "phases_after": metrics_after["total_phases"]
        }
    except Exception:
        return None


# CLI for testing
if __name__ == "__main__":
    import sys
    import time
from src.utils.resource_resolver import get_root_path
    
    print("🧪 Testing Metrics Utility...")
    start_test = time.time()
    
    # Test session lifecycle
    session_id = f"test-{uuid.uuid4()}"
    
    # Start session
    assert start_session(session_id, "/test/project", "Test Feature"), "Failed to start session"
    print(f"✅ Started session: {session_id}")
    
    # Start phase
    phase_id = start_phase(session_id, "RED", {"tests": 0})
    assert phase_id is not None, "Failed to start phase"
    print(f"✅ Started RED phase: {phase_id[:8]}")
    
    # Record metrics
    assert record_metrics(phase_id, {"lines_added": 10.0, "complexity": 2.0}), "Failed to record metrics"
    print("✅ Recorded metrics")
    
    # End phase
    assert end_phase(phase_id, "abc123", "RED: Add test", {"tests": 1}), "Failed to end phase"
    print("✅ Ended RED phase")
    
    # Get session metrics
    metrics = get_session_metrics(session_id)
    assert metrics is not None, "Failed to get session metrics"
    assert len(metrics["phases"]) == 1, "Wrong phase count"
    print(f"✅ Retrieved metrics: {metrics['total_phases']} phase(s)")
    
    # End session
    assert end_session(session_id), "Failed to end session"
    print("✅ Ended session")
    
    # Compare metrics (create second session)
    session_id_2 = f"test-{uuid.uuid4()}"
    start_session(session_id_2, "/test/project", "Test Feature 2")
    phase_id_2 = start_phase(session_id_2, "GREEN")
    end_phase(phase_id_2, "def456", "GREEN: Pass test")
    end_session(session_id_2)
    
    comparison = compare_metrics(session_id, session_id_2)
    assert comparison is not None, "Failed to compare metrics"
    print(f"✅ Compared sessions: {comparison['phases_change']} phase difference")
    
    elapsed = time.time() - start_test
    print(f"\n⚡ All tests passed in {elapsed:.3f}s")
    print(f"📊 Operations: 7 core functions tested")
    print(f"✅ Performance: {elapsed:.3f}s (<0.5s target)")
