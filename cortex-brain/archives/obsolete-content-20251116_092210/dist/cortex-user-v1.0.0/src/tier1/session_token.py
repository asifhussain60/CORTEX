"""
CORTEX Tier 1: Session Token Manager
Provides persistent conversation IDs across chat restarts.

Purpose:
- Generate unique, persistent session tokens
- Store token associations with conversations
- Enable "continue" to resume the exact same conversation
- Track session lifecycle (active, paused, completed)
- Bridge chat restarts with continuous context

Usage:
    from src.tier1.session_token import SessionTokenManager
    
    stm = SessionTokenManager()
    
    # Start a new session
    token = stm.create_session("Implementing auth feature")
    print(f"Session Token: {token}")  # SESSION_20251108_143022_a7b3
    
    # Record conversation association
    stm.associate_conversation(token, "github_copilot_conv_12345")
    
    # Later (even after restart)
    session = stm.get_active_session()
    if session:
        print(f"Resume: {session.description}")
        print(f"Conversation ID: {session.conversation_id}")
    
    # End session
    stm.complete_session(token)
"""

import sqlite3
import secrets
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class SessionStatus(Enum):
    """Status of a session."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"


@dataclass
class Session:
    """Represents a persistent session."""
    token: str
    description: str
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    conversation_id: Optional[str]
    work_session_id: Optional[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "token": self.token,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "conversation_id": self.conversation_id,
            "work_session_id": self.work_session_id,
            "metadata": self.metadata
        }
    
    def is_stale(self, hours: int = 24) -> bool:
        """Check if session is stale."""
        threshold = datetime.now() - timedelta(hours=hours)
        return self.last_activity < threshold
    
    def age_hours(self) -> float:
        """Get session age in hours."""
        return (datetime.now() - self.created_at).total_seconds() / 3600


class SessionTokenManager:
    """
    Manages persistent session tokens for conversation continuity.
    
    Features:
    - Generate unique session tokens
    - Track session lifecycle
    - Associate with conversations and work sessions
    - Auto-expire stale sessions
    - Enable seamless resume across restarts
    """
    
    TOKEN_LENGTH = 6  # Short hex string for readability
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize session token manager.
        
        Args:
            db_path: Path to SQLite database. If None, uses Tier 1 default.
        """
        if db_path is None:
            db_path = Path("cortex-brain/tier1/working_memory.db")
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize session tokens table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                last_activity TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                conversation_id TEXT,
                work_session_id TEXT,
                metadata TEXT
            )
        """)
        
        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_tokens_status 
            ON session_tokens(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_tokens_conversation 
            ON session_tokens(conversation_id)
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(
        self,
        description: str,
        conversation_id: Optional[str] = None,
        work_session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session token.
        
        Args:
            description: Human-readable session description
            conversation_id: Optional conversation ID to associate
            work_session_id: Optional work session ID to link
            metadata: Additional context
        
        Returns:
            token: Unique session token (e.g., SESSION_20251108_143022_a7b3)
        """
        # Generate unique token
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hex = secrets.token_hex(self.TOKEN_LENGTH // 2)
        token = f"SESSION_{timestamp}_{random_hex}"
        
        metadata = metadata or {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute("""
            INSERT INTO session_tokens 
            (token, description, status, created_at, last_activity, 
             conversation_id, work_session_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            token,
            description,
            SessionStatus.ACTIVE.value,
            now,
            now,
            conversation_id,
            work_session_id,
            str(metadata)
        ))
        
        conn.commit()
        conn.close()
        
        return token
    
    def get_session(self, token: str) -> Optional[Session]:
        """
        Retrieve session by token.
        
        Args:
            token: Session token
        
        Returns:
            Session if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT description, status, created_at, last_activity,
                   conversation_id, work_session_id, metadata
            FROM session_tokens
            WHERE token = ?
        """, (token,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        description, status, created_at, last_activity, conv_id, work_id, metadata = row
        
        return Session(
            token=token,
            description=description,
            status=SessionStatus(status),
            created_at=datetime.fromisoformat(created_at),
            last_activity=datetime.fromisoformat(last_activity),
            conversation_id=conv_id,
            work_session_id=work_id,
            metadata=eval(metadata) if metadata else {}
        )
    
    def get_active_session(self) -> Optional[Session]:
        """
        Get the most recent active session.
        
        Returns:
            Active Session if exists, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT token
            FROM session_tokens
            WHERE status = ?
            ORDER BY last_activity DESC
            LIMIT 1
        """, (SessionStatus.ACTIVE.value,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return self.get_session(row[0])
    
    def associate_conversation(self, token: str, conversation_id: str) -> None:
        """
        Associate a conversation ID with a session token.
        
        Args:
            token: Session token
            conversation_id: Conversation identifier from chat system
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE session_tokens
            SET conversation_id = ?, last_activity = ?
            WHERE token = ?
        """, (conversation_id, datetime.now(), token))
        
        conn.commit()
        conn.close()
    
    def associate_work_session(self, token: str, work_session_id: str) -> None:
        """
        Associate a work session ID with a session token.
        
        Args:
            token: Session token
            work_session_id: Work session identifier from WorkStateManager
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE session_tokens
            SET work_session_id = ?, last_activity = ?
            WHERE token = ?
        """, (work_session_id, datetime.now(), token))
        
        conn.commit()
        conn.close()
    
    def update_activity(self, token: str) -> None:
        """
        Update last activity timestamp for a session.
        
        Args:
            token: Session token
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE session_tokens
            SET last_activity = ?
            WHERE token = ?
        """, (datetime.now(), token))
        
        conn.commit()
        conn.close()
    
    def pause_session(self, token: str) -> None:
        """
        Pause a session (context switch).
        
        Args:
            token: Session token
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE session_tokens
            SET status = ?, last_activity = ?
            WHERE token = ?
        """, (SessionStatus.PAUSED.value, datetime.now(), token))
        
        conn.commit()
        conn.close()
    
    def resume_session(self, token: str) -> None:
        """
        Resume a paused session.
        
        Args:
            token: Session token
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE session_tokens
            SET status = ?, last_activity = ?
            WHERE token = ?
        """, (SessionStatus.ACTIVE.value, datetime.now(), token))
        
        conn.commit()
        conn.close()
    
    def complete_session(self, token: str) -> None:
        """
        Mark session as completed.
        
        Args:
            token: Session token
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now()
        
        cursor.execute("""
            UPDATE session_tokens
            SET status = ?, last_activity = ?, completed_at = ?
            WHERE token = ?
        """, (SessionStatus.COMPLETED.value, now, now, token))
        
        conn.commit()
        conn.close()
    
    def expire_session(self, token: str) -> None:
        """
        Mark session as expired (auto-cleanup).
        
        Args:
            token: Session token
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE session_tokens
            SET status = ?
            WHERE token = ?
        """, (SessionStatus.EXPIRED.value, token))
        
        conn.commit()
        conn.close()
    
    def get_all_active_sessions(self) -> List[Session]:
        """
        Get all active sessions.
        
        Returns:
            List of active Session objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT token
            FROM session_tokens
            WHERE status = ?
            ORDER BY last_activity DESC
        """, (SessionStatus.ACTIVE.value,))
        
        tokens = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return [self.get_session(token) for token in tokens if self.get_session(token) is not None]
    
    def cleanup_stale_sessions(self, hours: int = 24) -> int:
        """
        Expire stale sessions.
        
        Args:
            hours: Consider sessions stale after this many hours
        
        Returns:
            Number of sessions expired
        """
        threshold = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE session_tokens
            SET status = ?
            WHERE status IN (?, ?)
            AND last_activity < ?
        """, (
            SessionStatus.EXPIRED.value,
            SessionStatus.ACTIVE.value,
            SessionStatus.PAUSED.value,
            threshold
        ))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    def find_by_conversation(self, conversation_id: str) -> Optional[Session]:
        """
        Find session by conversation ID.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            Session if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT token
            FROM session_tokens
            WHERE conversation_id = ?
            ORDER BY last_activity DESC
            LIMIT 1
        """, (conversation_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return self.get_session(row[0])
    
    def find_by_work_session(self, work_session_id: str) -> Optional[Session]:
        """
        Find session by work session ID.
        
        Args:
            work_session_id: Work session identifier
        
        Returns:
            Session if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT token
            FROM session_tokens
            WHERE work_session_id = ?
            ORDER BY last_activity DESC
            LIMIT 1
        """, (work_session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return self.get_session(row[0])
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about sessions.
        
        Returns:
            Dictionary with counts and metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count by status
        cursor.execute("""
            SELECT status, COUNT(*)
            FROM session_tokens
            GROUP BY status
        """)
        
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Average session duration
        cursor.execute("""
            SELECT AVG((julianday(completed_at) - julianday(created_at)) * 24)
            FROM session_tokens
            WHERE status = ?
        """, (SessionStatus.COMPLETED.value,))
        
        avg_duration_hours = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "status_counts": status_counts,
            "average_duration_hours": round(avg_duration_hours, 2),
            "total_sessions": sum(status_counts.values()),
            "has_active_session": SessionStatus.ACTIVE.value in status_counts and status_counts[SessionStatus.ACTIVE.value] > 0
        }
