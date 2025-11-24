"""
Session Manager - Handles workspace session lifecycle and boundary detection.

Implements session-based conversation boundaries for CORTEX 3.0 Tier 1.
Sessions map to workspace contexts and provide natural conversation segmentation.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Session:
    """Represents a workspace session."""
    session_id: str
    workspace_path: str
    start_time: datetime
    end_time: Optional[datetime]
    conversation_count: int
    is_active: bool
    last_activity: datetime


class SessionManager:
    """Manages workspace session lifecycle and boundaries."""
    
    # Default idle threshold: 2 hours
    DEFAULT_IDLE_THRESHOLD_SECONDS = 7200
    
    def __init__(self, db_path: Path, idle_threshold_seconds: Optional[int] = None):
        """
        Initialize session manager.
        
        Args:
            db_path: Path to SQLite database
            idle_threshold_seconds: Idle gap threshold for session boundaries (default: 2 hours)
        """
        self.db_path = Path(db_path)
        self.idle_threshold = idle_threshold_seconds or self.DEFAULT_IDLE_THRESHOLD_SECONDS
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure sessions table exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                workspace_path TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                conversation_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                last_activity TEXT NOT NULL
            )
        """)
        
        # Create index for active sessions
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_active 
            ON sessions(is_active, workspace_path)
        """)
        
        # Create index for last activity (idle detection)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_last_activity 
            ON sessions(last_activity DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def detect_or_create_session(self, workspace_path: str) -> Session:
        """
        Detect existing active session or create new one.
        
        Creates new session if:
        - No active session exists for workspace
        - Last activity exceeds idle threshold (>2 hours default)
        - Previous session explicitly ended
        
        Args:
            workspace_path: Absolute path to workspace
        
        Returns:
            Active Session object
        """
        # Check for existing active session
        active_session = self.get_active_session(workspace_path)
        
        if active_session:
            # Check idle threshold
            time_since_activity = datetime.now() - active_session.last_activity
            
            if time_since_activity.total_seconds() > self.idle_threshold:
                # Idle threshold exceeded - end old session, create new
                self.end_session(active_session.session_id, reason="idle_timeout")
                return self._create_new_session(workspace_path)
            
            # Session still active and within threshold
            self._update_last_activity(active_session.session_id)
            return active_session
        
        # No active session - create new
        return self._create_new_session(workspace_path)
    
    def _create_new_session(self, workspace_path: str) -> Session:
        """
        Create a new workspace session.
        
        Args:
            workspace_path: Absolute path to workspace
        
        Returns:
            Created Session object
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        session_id = f"session_{now.strftime('%Y%m%d_%H%M%S')}_{abs(hash(workspace_path)) % 10000:04d}"
        
        cursor.execute("""
            INSERT INTO sessions 
            (session_id, workspace_path, start_time, last_activity, is_active, conversation_count)
            VALUES (?, ?, ?, ?, 1, 0)
        """, (
            session_id,
            workspace_path,
            now.isoformat(),
            now.isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return Session(
            session_id=session_id,
            workspace_path=workspace_path,
            start_time=now,
            end_time=None,
            conversation_count=0,
            is_active=True,
            last_activity=now
        )
    
    def get_active_session(self, workspace_path: str) -> Optional[Session]:
        """
        Get active session for workspace.
        
        Args:
            workspace_path: Absolute path to workspace
        
        Returns:
            Active Session or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, workspace_path, start_time, end_time, 
                   conversation_count, is_active, last_activity
            FROM sessions
            WHERE workspace_path = ? AND is_active = 1
            ORDER BY start_time DESC
            LIMIT 1
        """, (workspace_path,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Session(
            session_id=row[0],
            workspace_path=row[1],
            start_time=datetime.fromisoformat(row[2]),
            end_time=datetime.fromisoformat(row[3]) if row[3] else None,
            conversation_count=row[4],
            is_active=bool(row[5]),
            last_activity=datetime.fromisoformat(row[6])
        )
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session object or None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id, workspace_path, start_time, end_time,
                   conversation_count, is_active, last_activity
            FROM sessions
            WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Session(
            session_id=row[0],
            workspace_path=row[1],
            start_time=datetime.fromisoformat(row[2]),
            end_time=datetime.fromisoformat(row[3]) if row[3] else None,
            conversation_count=row[4],
            is_active=bool(row[5]),
            last_activity=datetime.fromisoformat(row[6])
        )
    
    def end_session(self, session_id: str, reason: str = "manual") -> None:
        """
        End a session.
        
        Args:
            session_id: Session to end
            reason: Reason for ending (manual, idle_timeout, workspace_close)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions
            SET is_active = 0,
                end_time = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def increment_conversation_count(self, session_id: str) -> None:
        """
        Increment conversation count for session.
        
        Args:
            session_id: Session to update
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions
            SET conversation_count = conversation_count + 1,
                last_activity = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def _update_last_activity(self, session_id: str) -> None:
        """
        Update last activity timestamp for session.
        
        Args:
            session_id: Session to update
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sessions
            SET last_activity = ?
            WHERE session_id = ?
        """, (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
    
    def get_recent_sessions(self, workspace_path: Optional[str] = None, limit: int = 10) -> List[Session]:
        """
        Get recent sessions.
        
        Args:
            workspace_path: Optional filter by workspace
            limit: Maximum number of sessions
        
        Returns:
            List of Session objects ordered by start time (newest first)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if workspace_path:
            cursor.execute("""
                SELECT session_id, workspace_path, start_time, end_time,
                       conversation_count, is_active, last_activity
                FROM sessions
                WHERE workspace_path = ?
                ORDER BY start_time DESC
                LIMIT ?
            """, (workspace_path, limit))
        else:
            cursor.execute("""
                SELECT session_id, workspace_path, start_time, end_time,
                       conversation_count, is_active, last_activity
                FROM sessions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            sessions.append(Session(
                session_id=row[0],
                workspace_path=row[1],
                start_time=datetime.fromisoformat(row[2]),
                end_time=datetime.fromisoformat(row[3]) if row[3] else None,
                conversation_count=row[4],
                is_active=bool(row[5]),
                last_activity=datetime.fromisoformat(row[6])
            ))
        
        return sessions
    
    def cleanup_old_sessions(self, retention_days: int = 90) -> int:
        """
        Cleanup sessions older than retention period.
        
        Args:
            retention_days: Number of days to retain sessions
        
        Returns:
            Number of sessions deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        cursor.execute("""
            DELETE FROM sessions
            WHERE start_time < ? AND is_active = 0
        """, (cutoff_date.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
