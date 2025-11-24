"""
CORTEX Tier 1: Work State Manager
Tracks in-progress work to enable seamless "continue" functionality.

Purpose:
- Record current task being worked on
- Track files being modified
- Monitor last activity timestamp
- Persist state across sessions
- Enable proactive resume prompts

Usage:
    from src.tier1.work_state_manager import WorkStateManager
    
    wsm = WorkStateManager()
    
    # Start tracking a new task
    wsm.start_task("Implement user authentication", ["src/auth.py", "tests/test_auth.py"])
    
    # Update progress
    wsm.update_progress("Added login endpoint", files_touched=["src/auth.py"])
    
    # Check if there's incomplete work
    if wsm.has_incomplete_work():
        state = wsm.get_current_state()
        print(f"Resume: {state.task_description}")
    
    # Mark task complete
    wsm.complete_task()
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


class WorkStatus(Enum):
    """Status of work session."""
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


@dataclass
class WorkState:
    """Represents the current state of in-progress work."""
    session_id: str
    task_description: str
    status: WorkStatus
    started_at: datetime
    last_activity: datetime
    files_touched: List[str]
    progress_notes: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "task_description": self.task_description,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "files_touched": self.files_touched,
            "progress_notes": self.progress_notes,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkState":
        """Create WorkState from dictionary."""
        return cls(
            session_id=data["session_id"],
            task_description=data["task_description"],
            status=WorkStatus(data["status"]),
            started_at=datetime.fromisoformat(data["started_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            files_touched=data["files_touched"],
            progress_notes=data["progress_notes"],
            metadata=data["metadata"]
        )
    
    def is_stale(self, hours: int = 24) -> bool:
        """Check if work state is stale (no activity for N hours)."""
        threshold = datetime.now() - timedelta(hours=hours)
        return self.last_activity < threshold
    
    def duration_minutes(self) -> float:
        """Calculate duration of work session in minutes."""
        return (self.last_activity - self.started_at).total_seconds() / 60


class WorkStateManager:
    """
    Manages work state tracking for seamless continuation.
    
    Provides:
    - Start/stop tracking work sessions
    - Update progress with file changes
    - Retrieve current state for resume
    - Auto-detect stale sessions
    - Integration with Tier 1 database
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize work state manager.
        
        Args:
            db_path: Path to SQLite database. If None, uses Tier 1 default.
        """
        if db_path is None:
            db_path = Path("cortex-brain/tier1/working_memory.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize work state tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Work sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                task_description TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Work progress table (detailed tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                progress_note TEXT,
                files_touched TEXT,
                FOREIGN KEY (session_id) REFERENCES work_sessions(session_id)
            )
        """)
        
        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_sessions_status 
            ON work_sessions(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_progress_session 
            ON work_progress(session_id)
        """)
        
        conn.commit()
        conn.close()
    
    def start_task(
        self,
        task_description: str,
        files: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start tracking a new work task.
        
        Args:
            task_description: Human-readable description of the task
            files: Initial list of files being worked on
            metadata: Additional context (branch, conversation_id, etc.)
        
        Returns:
            session_id: Unique identifier for this work session
        """
        # Generate unique session ID with microseconds and counter
        import secrets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        random_suffix = secrets.token_hex(2)
        session_id = f"work_{timestamp}_{random_suffix}"
        
        files = files or []
        metadata = metadata or {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        # Insert work session
        cursor.execute("""
            INSERT INTO work_sessions 
            (session_id, task_description, status, started_at, last_activity, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            task_description,
            WorkStatus.IN_PROGRESS.value,
            now,
            now,
            json.dumps(metadata)
        ))
        
        # Record initial progress entry
        if files:
            cursor.execute("""
                INSERT INTO work_progress (session_id, progress_note, files_touched)
                VALUES (?, ?, ?)
            """, (
                session_id,
                "Task started",
                json.dumps(files)
            ))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def update_progress(
        self,
        progress_note: str,
        files_touched: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> None:
        """
        Update progress on current work session.
        
        Args:
            progress_note: Description of what was just done
            files_touched: Files modified in this progress step
            session_id: Specific session to update (defaults to current)
        """
        if session_id is None:
            session_id = self._get_current_session_id()
            if session_id is None:
                raise ValueError("No active work session found")
        
        files_touched = files_touched or []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        # Update last activity on session
        cursor.execute("""
            UPDATE work_sessions 
            SET last_activity = ?
            WHERE session_id = ?
        """, (now, session_id))
        
        # Record progress entry
        cursor.execute("""
            INSERT INTO work_progress (session_id, progress_note, files_touched)
            VALUES (?, ?, ?)
        """, (
            session_id,
            progress_note,
            json.dumps(files_touched)
        ))
        
        conn.commit()
        conn.close()
    
    def complete_task(self, session_id: Optional[str] = None) -> None:
        """
        Mark current work session as completed.
        
        Args:
            session_id: Specific session to complete (defaults to current)
        """
        if session_id is None:
            session_id = self._get_current_session_id()
            if session_id is None:
                return  # No active session, nothing to complete
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute("""
            UPDATE work_sessions 
            SET status = ?, completed_at = ?, last_activity = ?
            WHERE session_id = ?
        """, (WorkStatus.COMPLETED.value, now, now, session_id))
        
        conn.commit()
        conn.close()
    
    def pause_task(self, session_id: Optional[str] = None) -> None:
        """
        Pause current work session (e.g., switching contexts).
        
        Args:
            session_id: Specific session to pause (defaults to current)
        """
        if session_id is None:
            session_id = self._get_current_session_id()
            if session_id is None:
                return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE work_sessions 
            SET status = ?, last_activity = ?
            WHERE session_id = ?
        """, (WorkStatus.PAUSED.value, datetime.now(), session_id))
        
        conn.commit()
        conn.close()
    
    def abandon_task(self, session_id: Optional[str] = None, reason: Optional[str] = None) -> None:
        """
        Mark work session as abandoned (not completed).
        
        Args:
            session_id: Specific session to abandon (defaults to current)
            reason: Optional reason for abandonment
        """
        if session_id is None:
            session_id = self._get_current_session_id()
            if session_id is None:
                return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE work_sessions 
            SET status = ?, last_activity = ?
            WHERE session_id = ?
        """, (WorkStatus.ABANDONED.value, datetime.now(), session_id))
        
        if reason:
            cursor.execute("""
                INSERT INTO work_progress (session_id, progress_note)
                VALUES (?, ?)
            """, (session_id, f"Abandoned: {reason}"))
        
        conn.commit()
        conn.close()
    
    def get_current_state(self) -> Optional[WorkState]:
        """
        Get the current active work state.
        
        Returns:
            WorkState if there's active work, None otherwise
        """
        session_id = self._get_current_session_id()
        if session_id is None:
            return None
        
        return self.get_state(session_id)
    
    def get_state(self, session_id: str) -> Optional[WorkState]:
        """
        Get work state for a specific session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            WorkState if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session info
        cursor.execute("""
            SELECT task_description, status, started_at, last_activity, metadata
            FROM work_sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if row is None:
            conn.close()
            return None
        
        task_description, status, started_at, last_activity, metadata = row
        
        # Get all progress entries
        cursor.execute("""
            SELECT progress_note, files_touched
            FROM work_progress
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        
        progress_rows = cursor.fetchall()
        conn.close()
        
        # Aggregate files touched
        all_files = set()
        progress_notes = []
        
        for note, files_json in progress_rows:
            if note:
                progress_notes.append(note)
            if files_json:
                files = json.loads(files_json)
                all_files.update(files)
        
        return WorkState(
            session_id=session_id,
            task_description=task_description,
            status=WorkStatus(status),
            started_at=datetime.fromisoformat(started_at),
            last_activity=datetime.fromisoformat(last_activity),
            files_touched=sorted(all_files),
            progress_notes=progress_notes,
            metadata=json.loads(metadata) if metadata else {}
        )
    
    def has_incomplete_work(self) -> bool:
        """
        Check if there's any incomplete work to resume.
        
        Returns:
            True if there's in-progress or paused work
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM work_sessions
            WHERE status IN (?, ?)
        """, (WorkStatus.IN_PROGRESS.value, WorkStatus.PAUSED.value))
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def get_incomplete_sessions(self, include_stale: bool = False) -> List[WorkState]:
        """
        Get all incomplete work sessions.
        
        Args:
            include_stale: Include sessions with no activity in 24+ hours
        
        Returns:
            List of WorkState objects for incomplete work
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id
            FROM work_sessions
            WHERE status IN (?, ?)
            ORDER BY last_activity DESC
        """, (WorkStatus.IN_PROGRESS.value, WorkStatus.PAUSED.value))
        
        session_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        states = [self.get_state(sid) for sid in session_ids]
        states = [s for s in states if s is not None]
        
        if not include_stale:
            states = [s for s in states if not s.is_stale()]
        
        return states
    
    def cleanup_stale_sessions(self, hours: int = 24) -> int:
        """
        Mark stale sessions as abandoned.
        
        Args:
            hours: Consider sessions stale after this many hours of inactivity
        
        Returns:
            Number of sessions marked as abandoned
        """
        threshold = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE work_sessions
            SET status = ?
            WHERE status IN (?, ?)
            AND last_activity < ?
        """, (
            WorkStatus.ABANDONED.value,
            WorkStatus.IN_PROGRESS.value,
            WorkStatus.PAUSED.value,
            threshold
        ))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def get_recent_completed(self, limit: int = 10) -> List[WorkState]:
        """
        Get recently completed work sessions.
        
        Args:
            limit: Maximum number of sessions to return
        
        Returns:
            List of completed WorkState objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id
            FROM work_sessions
            WHERE status = ?
            ORDER BY completed_at DESC
            LIMIT ?
        """, (WorkStatus.COMPLETED.value, limit))
        
        session_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_state(sid) for sid in session_ids if self.get_state(sid) is not None]
    
    def _get_current_session_id(self) -> Optional[str]:
        """Get the session_id of the most recent in-progress work."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id
            FROM work_sessions
            WHERE status = ?
            ORDER BY last_activity DESC
            LIMIT 1
        """, (WorkStatus.IN_PROGRESS.value,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about work sessions.
        
        Returns:
            Dictionary with counts and metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count by status
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM work_sessions
            GROUP BY status
        """)
        
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average duration of completed tasks
        cursor.execute("""
            SELECT AVG((julianday(completed_at) - julianday(started_at)) * 24 * 60)
            FROM work_sessions
            WHERE status = ?
        """, (WorkStatus.COMPLETED.value,))
        
        avg_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "status_counts": status_counts,
            "average_completion_minutes": round(avg_duration, 1),
            "has_incomplete_work": self.has_incomplete_work(),
            "total_sessions": sum(status_counts.values())
        }
