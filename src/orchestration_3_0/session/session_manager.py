"""
Session Manager for CORTEX 4.0 Orchestrators

Provides workflow state persistence and recovery capabilities.
Enables orchestrators to resume after crashes or interruptions.

Author: Asif Hussain
Date: December 10, 2025
"""

import sqlite3
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status values."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


@dataclass
class WorkflowSession:
    """Represents a workflow execution session."""
    session_id: str
    orchestrator_name: str
    tenant_id: str
    project_id: str
    user_id: str
    current_state: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    checkpoint_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'orchestrator_name': self.orchestrator_name,
            'tenant_id': self.tenant_id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'current_state': self.current_state,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': json.dumps(self.metadata),
            'checkpoint_data': json.dumps(self.checkpoint_data)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowSession':
        """Create from dictionary."""
        return cls(
            session_id=data['session_id'],
            orchestrator_name=data['orchestrator_name'],
            tenant_id=data['tenant_id'],
            project_id=data['project_id'],
            user_id=data['user_id'],
            current_state=data['current_state'],
            status=SessionStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=json.loads(data['metadata']) if isinstance(data['metadata'], str) else data['metadata'],
            checkpoint_data=json.loads(data['checkpoint_data']) if isinstance(data['checkpoint_data'], str) else data['checkpoint_data']
        )


class SessionManager:
    """
    Manages workflow session persistence and recovery.
    
    Features:
    - SQLite-based persistence
    - Automatic checkpoint creation
    - Recovery from interruption
    - Session history tracking
    - Tenant-scoped session isolation
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize session manager.
        
        Args:
            db_path: Path to SQLite database file (defaults to cortex-brain/sessions.db)
        """
        if db_path is None:
            # Default location
            db_path = Path("cortex-brain/sessions.db")
        elif isinstance(db_path, str):
            # Convert string to Path
            db_path = Path(db_path)
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        logger.info(f"SessionManager initialized with database: {self.db_path}")
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    orchestrator_name TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    current_state TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    checkpoint_data TEXT NOT NULL
                )
            """)
            
            # Create indexes for common queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tenant_project 
                ON sessions(tenant_id, project_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_orchestrator_status 
                ON sessions(orchestrator_name, status)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_user 
                ON sessions(user_id)
            """)
            
            conn.commit()
    
    def create_session(
        self,
        session_id: str,
        orchestrator_name: str,
        tenant_id: str,
        project_id: str,
        user_id: str,
        initial_state: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowSession:
        """
        Create a new workflow session.
        
        Args:
            session_id: Unique session identifier
            orchestrator_name: Name of orchestrator
            tenant_id: Tenant identifier
            project_id: Project identifier
            user_id: User identifier
            initial_state: Starting state name
            metadata: Optional metadata dictionary
            
        Returns:
            Created WorkflowSession
        """
        now = datetime.now()
        session = WorkflowSession(
            session_id=session_id,
            orchestrator_name=orchestrator_name,
            tenant_id=tenant_id,
            project_id=project_id,
            user_id=user_id,
            current_state=initial_state,
            status=SessionStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
            checkpoint_data={}
        )
        
        self._save_session(session)
        logger.info(f"Created session: {session_id} for {orchestrator_name}")
        return session
    
    def update_session_state(
        self,
        session_id: str,
        new_state: str,
        checkpoint_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update session state and checkpoint data.
        
        Args:
            session_id: Session identifier
            new_state: New state name
            checkpoint_data: Optional checkpoint data to persist
        """
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        
        session.current_state = new_state
        session.updated_at = datetime.now()
        
        if checkpoint_data:
            session.checkpoint_data.update(checkpoint_data)
        
        self._save_session(session)
        logger.debug(f"Updated session {session_id} to state: {new_state}")
    
    def complete_session(
        self,
        session_id: str,
        final_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Mark session as completed.
        
        Args:
            session_id: Session identifier
            final_metadata: Optional final metadata to store
        """
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        
        session.status = SessionStatus.COMPLETED
        session.updated_at = datetime.now()
        
        if final_metadata:
            session.metadata.update(final_metadata)
        
        self._save_session(session)
        logger.info(f"Completed session: {session_id}")
    
    def fail_session(
        self,
        session_id: str,
        error_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Mark session as failed.
        
        Args:
            session_id: Session identifier
            error_info: Optional error information
        """
        session = self.get_session(session_id)
        if session is None:
            raise ValueError(f"Session not found: {session_id}")
        
        session.status = SessionStatus.FAILED
        session.updated_at = datetime.now()
        
        if error_info:
            session.metadata['error'] = error_info
        
        self._save_session(session)
        logger.warning(f"Failed session: {session_id}")
    
    def get_session(self, session_id: str) -> Optional[WorkflowSession]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            WorkflowSession if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return WorkflowSession.from_dict(dict(row))
    
    def get_active_sessions(
        self,
        tenant_id: Optional[str] = None,
        orchestrator_name: Optional[str] = None
    ) -> List[WorkflowSession]:
        """
        Get all active sessions.
        
        Args:
            tenant_id: Optional filter by tenant
            orchestrator_name: Optional filter by orchestrator
            
        Returns:
            List of active WorkflowSessions
        """
        query = "SELECT * FROM sessions WHERE status = ?"
        params = [SessionStatus.ACTIVE.value]
        
        if tenant_id:
            query += " AND tenant_id = ?"
            params.append(tenant_id)
        
        if orchestrator_name:
            query += " AND orchestrator_name = ?"
            params.append(orchestrator_name)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [WorkflowSession.from_dict(dict(row)) for row in rows]
    
    def get_session_history(
        self,
        tenant_id: str,
        project_id: Optional[str] = None,
        limit: int = 100
    ) -> List[WorkflowSession]:
        """
        Get session history for tenant/project.
        
        Args:
            tenant_id: Tenant identifier
            project_id: Optional project identifier
            limit: Maximum number of sessions to return
            
        Returns:
            List of WorkflowSessions ordered by created_at desc
        """
        query = "SELECT * FROM sessions WHERE tenant_id = ?"
        params = [tenant_id]
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [WorkflowSession.from_dict(dict(row)) for row in rows]
    
    def cleanup_old_sessions(
        self,
        days: int = 30,
        keep_failed: bool = True
    ) -> int:
        """
        Clean up old completed/abandoned sessions.
        
        Args:
            days: Delete sessions older than this many days
            keep_failed: If True, keep failed sessions
            
        Returns:
            Number of sessions deleted
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        cutoff_iso = datetime.fromtimestamp(cutoff).isoformat()
        
        query = "DELETE FROM sessions WHERE updated_at < ? AND status IN (?, ?)"
        params = [cutoff_iso, SessionStatus.COMPLETED.value, SessionStatus.ABANDONED.value]
        
        if keep_failed:
            # Don't delete failed sessions
            pass
        else:
            # Also delete failed sessions
            params.append(SessionStatus.FAILED.value)
            query = query.replace("(?, ?)", "(?, ?, ?)")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            deleted = cursor.rowcount
            conn.commit()
        
        logger.info(f"Cleaned up {deleted} old sessions")
        return deleted
    
    def _save_session(self, session: WorkflowSession) -> None:
        """Save session to database."""
        data = session.to_dict()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['session_id'],
                data['orchestrator_name'],
                data['tenant_id'],
                data['project_id'],
                data['user_id'],
                data['current_state'],
                data['status'],
                data['created_at'],
                data['updated_at'],
                data['metadata'],
                data['checkpoint_data']
            ))
            conn.commit()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"SessionManager(db={self.db_path})"


# Global session manager instance
_global_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    Get global session manager.
    
    Returns:
        Global SessionManager instance
    """
    global _global_session_manager
    if _global_session_manager is None:
        _global_session_manager = SessionManager()
    return _global_session_manager


def create_session_manager(db_path: Path) -> SessionManager:
    """
    Create a new session manager with custom database path.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        SessionManager instance
    """
    return SessionManager(db_path)
