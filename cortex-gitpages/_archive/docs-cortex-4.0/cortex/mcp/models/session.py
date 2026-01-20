"""
MCP Session Context and Management.

Implements MCPSession dataclass and SessionManager singleton for per-connection
session management, enabling repo_id context injection into orchestrator calls
and automatic audit trail tagging.

Key components:
- MCPSession: Represents a single MCP server connection with repo context
- SessionManager: Singleton managing session lifecycle

Each connected repo gets unique session_id with repo_id isolation metadata.
All orchestrator calls receive __cortex_session__ with isolation context.
Audit entries automatically tagged with repo_id + session_id.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid
from threading import Lock


@dataclass
class MCPSession:
    """Represents a single MCP server connection session.

    Attributes:
        session_id: Unique identifier for this session (UUID string)
        repo_id: Associated repository ID for isolation context
        repo_path: File system path to repository (isolation boundary)
        created_at: Timestamp when session was created
        metadata: Optional arbitrary metadata dict for orchestrator context
        last_activity: Last activity timestamp (for timeout tracking)
    """

    session_id: str
    repo_id: str
    repo_path: str
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    last_activity: Optional[datetime] = field(default=None)

    def __post_init__(self):
        """Initialize session fields after dataclass construction."""
        if self.last_activity is None:
            self.last_activity = self.created_at
        if self.metadata is None:
            self.metadata = {}

    def age_seconds(self) -> float:
        """Calculate session age in seconds.

        Returns:
            float: Session age in seconds since creation

        Example:
            >>> session = MCPSession(..., created_at=datetime.now() - timedelta(hours=1))
            >>> age = session.age_seconds()
            >>> assert age > 3600
        """
        return (datetime.now() - self.created_at).total_seconds()

    def is_expired(self, ttl_seconds: int = 86400) -> bool:
        """Check if session has expired.

        Args:
            ttl_seconds: Time-to-live in seconds (default: 24 hours)

        Returns:
            bool: True if session age > ttl_seconds

        Example:
            >>> session = MCPSession(..., created_at=datetime.now() - timedelta(hours=25))
            >>> assert session.is_expired(86400)  # 24 hours
        """
        return self.age_seconds() > ttl_seconds

    def to_context_dict(self) -> Dict[str, Any]:
        """Convert session to orchestrator context dict.

        Returns:
            Dict containing __cortex_session__ with isolation context

        Example:
            >>> session = MCPSession(...)
            >>> context = session.to_context_dict()
            >>> assert "__cortex_session__" in context
            >>> assert context["__cortex_session__"]["repo_id"] is not None
        """
        return {
            "__cortex_session__": {
                "session_id": self.session_id,
                "repo_id": self.repo_id,
                "repo_path": self.repo_path,
                "created_at": self.created_at.isoformat(),
                "metadata": self.metadata,
            }
        }

    def update_activity(self) -> None:
        """Update last activity timestamp.

        Called whenever session is used to track idle time.
        """
        self.last_activity = datetime.now()


class SessionManager:
    """Singleton managing session lifecycle for MCP connections.

    Provides:
    - Session creation with unique session_id per repo
    - Session retrieval by session_id
    - Session deletion/cleanup
    - Session listing and expiration detection

    Thread-safe with lock protection for concurrent access.

    Example:
        >>> manager = SessionManager()
        >>> session = manager.create_session(repo_id="repo-1", repo_path="/path/1")
        >>> assert manager.get_session(session.session_id) is not None
        >>> manager.delete_session(session.session_id)
        >>> assert manager.get_session(session.session_id) is None
    """

    _instance: Optional["SessionManager"] = None
    _lock: Lock = Lock()
    _sessions: Dict[str, MCPSession] = {}
    _session_lock: Lock = Lock()

    def __new__(cls) -> "SessionManager":
        """Implement singleton pattern with double-checked locking.

        Returns:
            SessionManager: Singleton instance

        Thread-safe instantiation using locking.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def create_session(
        self,
        repo_id: str,
        repo_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MCPSession:
        """Create new session for connected repository.

        Args:
            repo_id: Repository identifier
            repo_path: File system path to repository
            metadata: Optional context metadata (orchestrator type, phase, etc.)

        Returns:
            MCPSession: Newly created session with unique session_id

        Raises:
            ValueError: If repo_id or repo_path is empty

        Example:
            >>> manager = SessionManager()
            >>> session = manager.create_session(
            ...     repo_id="repo-test",
            ...     repo_path="/path/to/repo",
            ...     metadata={"orchestrator": "IMPLEMENT"}
            ... )
            >>> assert session.session_id is not None
        """
        if not repo_id or not repo_path:
            raise ValueError("repo_id and repo_path must be non-empty")

        session_id = str(uuid.uuid4())
        now = datetime.now()

        session = MCPSession(
            session_id=session_id,
            repo_id=repo_id,
            repo_path=repo_path,
            created_at=now,
            metadata=metadata or {},
        )

        with self._session_lock:
            self._sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[MCPSession]:
        """Retrieve session by session_id.

        Args:
            session_id: Session identifier

        Returns:
            MCPSession if found, None otherwise

        Example:
            >>> manager = SessionManager()
            >>> session = manager.create_session("repo-1", "/path/1")
            >>> retrieved = manager.get_session(session.session_id)
            >>> assert retrieved is not None
            >>> assert retrieved.repo_id == "repo-1"
        """
        with self._session_lock:
            return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete session on disconnect.

        Args:
            session_id: Session identifier

        Returns:
            bool: True if session was deleted, False if not found

        Example:
            >>> manager = SessionManager()
            >>> session = manager.create_session("repo-1", "/path/1")
            >>> deleted = manager.delete_session(session.session_id)
            >>> assert deleted is True
            >>> assert manager.get_session(session.session_id) is None
        """
        with self._session_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def list_sessions(self) -> List[MCPSession]:
        """List all active sessions.

        Returns:
            List[MCPSession]: All currently active sessions

        Example:
            >>> manager = SessionManager()
            >>> manager.create_session("repo-1", "/path/1")
            >>> manager.create_session("repo-2", "/path/2")
            >>> sessions = manager.list_sessions()
            >>> assert len(sessions) >= 2
        """
        with self._session_lock:
            return list(self._sessions.values())

    def get_sessions_by_repo(self, repo_id: str) -> List[MCPSession]:
        """Get all sessions for specific repo.

        Args:
            repo_id: Repository identifier

        Returns:
            List[MCPSession]: Sessions for repo_id

        Example:
            >>> manager = SessionManager()
            >>> manager.create_session("repo-1", "/path/1")
            >>> manager.create_session("repo-1", "/path/1-alt")
            >>> sessions = manager.get_sessions_by_repo("repo-1")
            >>> assert len(sessions) >= 1
        """
        with self._session_lock:
            return [s for s in self._sessions.values() if s.repo_id == repo_id]

    def cleanup_expired_sessions(self, ttl_seconds: int = 86400) -> int:
        """Clean up expired sessions.

        Args:
            ttl_seconds: Time-to-live in seconds (default: 24 hours)

        Returns:
            int: Number of sessions cleaned up

        Removes sessions older than ttl_seconds from the registry.

        Example:
            >>> manager = SessionManager()
            >>> session = manager.create_session("repo-1", "/path/1")
            >>> # Simulate old session
            >>> session.created_at = datetime.now() - timedelta(hours=25)
            >>> cleaned = manager.cleanup_expired_sessions(86400)
            >>> assert cleaned >= 1
        """
        expired_ids = []
        with self._session_lock:
            for session_id, session in self._sessions.items():
                if session.is_expired(ttl_seconds):
                    expired_ids.append(session_id)

            for session_id in expired_ids:
                del self._sessions[session_id]

        return len(expired_ids)

    def clear_all(self) -> None:
        """Clear all sessions.

        Used for testing and cleanup. Use with caution in production.

        Example:
            >>> manager = SessionManager()
            >>> manager.create_session("repo-1", "/path/1")
            >>> manager.clear_all()
            >>> assert len(manager.list_sessions()) == 0
        """
        with self._session_lock:
            self._sessions.clear()

    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session as orchestrator context dict.

        Args:
            session_id: Session identifier

        Returns:
            Dict with __cortex_session__ context, or None if session not found

        Example:
            >>> manager = SessionManager()
            >>> session = manager.create_session("repo-1", "/path/1")
            >>> context = manager.get_session_context(session.session_id)
            >>> assert context["__cortex_session__"]["repo_id"] == "repo-1"
        """
        session = self.get_session(session_id)
        if session is None:
            return None
        return session.to_context_dict()
