"""
Metrics Tracker

Tracks timestamps, duration, and performance metrics for TDD workflow phases.

Features:
- Phase start/end timestamps (ISO 8601)
- Duration calculation
- Git commit SHA correlation
- Before/after metrics comparison
- Metrics persistence to Tier 1 database

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import uuid
import logging

logger = logging.getLogger(__name__)


class MetricsTracker:
    """
    Tracks TDD workflow metrics with timestamp precision.
    
    Provides:
    - ISO 8601 timestamp tracking
    - Duration calculation (seconds)
    - Git commit correlation
    - Before/after metrics storage
    - Session and phase-level metrics
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize MetricsTracker.
        
        Args:
            db_path: Path to Tier 1 database (working_memory.db)
        """
        self.db_path = Path(db_path)
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_tables(self) -> None:
        """Ensure metrics tables exist."""
        migration_sql = Path(__file__).parent.parent.parent / "cortex-brain" / "migrations" / "add_tdd_metrics.sql"
        
        if migration_sql.exists():
            with self._get_connection() as conn:
                try:
                    conn.executescript(migration_sql.read_text())
                    conn.commit()
                    logger.info("✅ Metrics tables initialized")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize metrics tables: {e}")
    
    def start_session(
        self,
        session_id: str,
        project_path: str,
        feature_name: Optional[str] = None
    ) -> bool:
        """
        Start tracking a new TDD session.
        
        Args:
            session_id: Unique session identifier
            project_path: Path to project being worked on
            feature_name: Optional feature description
            
        Returns:
            True if session started successfully
        """
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO tdd_sessions 
                    (session_id, session_start_time, project_path, feature_name, status)
                    VALUES (?, ?, ?, ?, 'in-progress')
                    """,
                    (session_id, datetime.now().isoformat(), project_path, feature_name)
                )
                conn.commit()
                logger.info(f"📊 Started session tracking: {session_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to start session: {e}")
            return False
    
    def end_session(self, session_id: str) -> bool:
        """
        End tracking for a TDD session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session ended successfully
        """
        try:
            with self._get_connection() as conn:
                # Get start time
                row = conn.execute(
                    "SELECT session_start_time FROM tdd_sessions WHERE session_id = ?",
                    (session_id,)
                ).fetchone()
                
                if not row:
                    logger.error(f"❌ Session not found: {session_id}")
                    return False
                
                start_time = datetime.fromisoformat(row["session_start_time"])
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Update session
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
                
                logger.info(f"✅ Session completed: {session_id} ({duration:.1f}s)")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to end session: {e}")
            return False
    
    def start_phase(
        self,
        session_id: str,
        phase_name: str,
        metrics_before: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Start tracking a phase (RED, GREEN, REFACTOR).
        
        Args:
            session_id: Parent session identifier
            phase_name: Phase name (RED, GREEN, REFACTOR, COMPLETE)
            metrics_before: Optional baseline metrics
            
        Returns:
            Phase ID or None if failed
        """
        phase_id = str(uuid.uuid4())
        
        try:
            with self._get_connection() as conn:
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
                logger.info(f"🎯 Started phase: {phase_name} ({phase_id[:8]})")
                return phase_id
        except Exception as e:
            logger.error(f"❌ Failed to start phase: {e}")
            return None
    
    def end_phase(
        self,
        phase_id: str,
        git_commit_sha: Optional[str] = None,
        git_commit_message: Optional[str] = None,
        metrics_after: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        End tracking for a phase.
        
        Args:
            phase_id: Phase identifier
            git_commit_sha: Git commit SHA for this phase
            git_commit_message: Git commit message
            metrics_after: Final metrics for this phase
            
        Returns:
            True if phase ended successfully
        """
        try:
            with self._get_connection() as conn:
                # Get start time
                row = conn.execute(
                    "SELECT phase_start_time, phase_name FROM tdd_phases WHERE phase_id = ?",
                    (phase_id,)
                ).fetchone()
                
                if not row:
                    logger.error(f"❌ Phase not found: {phase_id}")
                    return False
                
                start_time = datetime.fromisoformat(row["phase_start_time"])
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Update phase
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
                
                logger.info(f"✅ Phase completed: {row['phase_name']} ({duration:.1f}s)")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to end phase: {e}")
            return False
    
    def record_metric(
        self,
        phase_id: str,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None
    ) -> bool:
        """
        Record a specific metric for a phase.
        
        Args:
            phase_id: Phase identifier
            metric_name: Name of metric (e.g., "lines_added", "test_coverage")
            metric_value: Numeric value
            metric_unit: Optional unit (e.g., "lines", "percent")
            
        Returns:
            True if metric recorded successfully
        """
        metric_id = str(uuid.uuid4())
        
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO tdd_metrics
                    (metric_id, phase_id, metric_name, metric_value, metric_unit)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (metric_id, phase_id, metric_name, metric_value, metric_unit)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to record metric: {e}")
            return False
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get summary metrics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session metrics or None if not found
        """
        try:
            with self._get_connection() as conn:
                # Get session data
                session_row = conn.execute(
                    """
                    SELECT * FROM tdd_sessions WHERE session_id = ?
                    """,
                    (session_id,)
                ).fetchone()
                
                if not session_row:
                    return None
                
                # Get phases
                phases = conn.execute(
                    """
                    SELECT phase_name, phase_duration_seconds, git_commit_sha
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
                    "phases": [
                        {
                            "phase": phase["phase_name"],
                            "duration_seconds": phase["phase_duration_seconds"],
                            "commit_sha": phase["git_commit_sha"]
                        }
                        for phase in phases
                    ]
                }
        except Exception as e:
            logger.error(f"❌ Failed to get session summary: {e}")
            return None
    
    def get_phase_metrics(self, phase_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metrics for a phase.
        
        Args:
            phase_id: Phase identifier
            
        Returns:
            Dictionary with phase metrics or None if not found
        """
        try:
            with self._get_connection() as conn:
                phase_row = conn.execute(
                    """
                    SELECT * FROM tdd_phases WHERE phase_id = ?
                    """,
                    (phase_id,)
                ).fetchone()
                
                if not phase_row:
                    return None
                
                metrics = conn.execute(
                    """
                    SELECT metric_name, metric_value, metric_unit
                    FROM tdd_metrics
                    WHERE phase_id = ?
                    """,
                    (phase_id,)
                ).fetchall()
                
                return {
                    "phase_id": phase_id,
                    "phase_name": phase_row["phase_name"],
                    "start_time": phase_row["phase_start_time"],
                    "end_time": phase_row["phase_end_time"],
                    "duration_seconds": phase_row["phase_duration_seconds"],
                    "git_commit_sha": phase_row["git_commit_sha"],
                    "metrics_before": json.loads(phase_row["metrics_before"]) if phase_row["metrics_before"] else {},
                    "metrics_after": json.loads(phase_row["metrics_after"]) if phase_row["metrics_after"] else {},
                    "additional_metrics": {
                        metric["metric_name"]: {
                            "value": metric["metric_value"],
                            "unit": metric["metric_unit"]
                        }
                        for metric in metrics
                    }
                }
        except Exception as e:
            logger.error(f"❌ Failed to get phase metrics: {e}")
            return None
    
    def export_session_metrics(self, session_id: str, output_path: Path) -> bool:
        """
        Export session metrics to JSON file.
        
        Args:
            session_id: Session identifier
            output_path: Path to output JSON file
            
        Returns:
            True if export successful
        """
        try:
            summary = self.get_session_summary(session_id)
            if not summary:
                logger.error(f"❌ Session not found: {session_id}")
                return False
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(summary, indent=2))
            
            logger.info(f"✅ Exported metrics: {output_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to export metrics: {e}")
            return False
