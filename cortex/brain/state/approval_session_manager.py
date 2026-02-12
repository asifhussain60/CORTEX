"""
Approval Session Manager - Stateful DoR approval across MCP calls.

AC-ID: AC-PHASE41-S1-001
Purpose: Enable multi-turn approval workflows with session persistence

Architecture:
- ApprovalSession: Serializable session containing DoR gate state
- ApprovalSessionManager: Singleton managing session lifecycle
- Thread-safe with lock protection
- TTL-based expiration (default: 5 minutes)

Usage:
    manager = ApprovalSessionManager()

    # Phase 1: Classify → Store
    gate = DoRApprovalGate()
    gate.classify_and_reflect("Implement auth", {})
    session = manager.create_session(gate, user_id="copilot-user")

    # Phase 2: Restore → Approve → Execute
    restored_gate = manager.restore_gate(session.session_id)
    restored_gate.approve()
    result = restored_gate.execute_if_approved()

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import ApprovalStatus
from cortex.orchestrators.core.dor_approval_gate import (
    ApprovalDecision,
    DoRApprovalGate,
    IntentReflection,
)


class SessionNotFoundError(Exception):
    """Raised when session ID not found."""
    pass


class SessionExpiredError(Exception):
    """Raised when session has expired."""
    pass


@dataclass
class ApprovalSession:
    """
    Approval session containing DoR gate state.

    Attributes:
        session_id: Unique session identifier (UUID)
        user_id: User who created the session
        created_at: Session creation timestamp
        gate_state: Serialized DoR gate state
        metadata: Optional arbitrary metadata
        last_activity: Last activity timestamp
    """
    session_id: str
    user_id: str
    created_at: datetime
    gate_state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default=None)  # type: ignore

    def __post_init__(self) -> None:
        """Initialize default values."""
        if self.last_activity is None:
            self.last_activity = self.created_at

    def age_seconds(self) -> float:
        """Calculate session age in seconds."""
        return (datetime.now() - self.created_at).total_seconds()

    def is_expired(self, ttl_seconds: int = 300) -> bool:
        """
        Check if session has expired.

        Args:
            ttl_seconds: Time-to-live in seconds (default: 5 minutes)

        Returns:
            True if session age > ttl_seconds
        """
        return self.age_seconds() > ttl_seconds


class ApprovalSessionManager:
    """
    Singleton manager for approval session lifecycle.

    Provides:
    - Session creation with unique session_id
    - Session retrieval by ID
    - Session deletion and cleanup
    - DoR gate state serialization/deserialization
    - TTL-based expiration

    Thread-safe with lock protection for concurrent access.
    """

    _instance: Optional["ApprovalSessionManager"] = None
    _lock: Lock = Lock()
    _sessions: Dict[str, ApprovalSession] = {}
    _session_lock: Lock = Lock()

    def __new__(cls) -> "ApprovalSessionManager":
        """Singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def create_session(
        self,
        gate: DoRApprovalGate,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApprovalSession:
        """
        Create new approval session from DoR gate.

        Args:
            gate: DoR approval gate with current state
            user_id: User identifier
            metadata: Optional session metadata

        Returns:
            ApprovalSession with unique session_id

        Example:
            >>> manager = ApprovalSessionManager()
            >>> gate = DoRApprovalGate()
            >>> gate.classify_and_reflect("Implement auth", {})
            >>> session = manager.create_session(gate, "user1")
            >>> assert len(session.session_id) == 36
        """
        session_id = str(uuid.uuid4())
        gate_state = self._serialize_gate(gate)

        session = ApprovalSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            gate_state=gate_state,
            metadata=metadata or {}
        )

        with self._session_lock:
            self._sessions[session_id] = session

        return session

    def get_session(
        self,
        session_id: str,
        enforce_ttl: bool = False,
        ttl_seconds: int = 300
    ) -> Optional[ApprovalSession]:
        """
        Retrieve session by ID.

        Args:
            session_id: Session identifier
            enforce_ttl: If True, raise SessionExpiredError for expired sessions
            ttl_seconds: TTL threshold for expiration check

        Returns:
            ApprovalSession if found, None otherwise

        Raises:
            SessionExpiredError: If enforce_ttl=True and session expired

        Example:
            >>> manager = ApprovalSessionManager()
            >>> session = manager.get_session("some-id")
            >>> if session:
            ...     print(f"Found session for {session.user_id}")
        """
        with self._session_lock:
            session = self._sessions.get(session_id)

        if session is None:
            return None

        if enforce_ttl and session.is_expired(ttl_seconds):
            raise SessionExpiredError(
                f"Session {session_id} expired "
                f"({session.age_seconds():.0f}s > {ttl_seconds}s)"
            )

        return session

    def restore_gate(self, session_id: str) -> Optional[DoRApprovalGate]:
        """
        Restore DoR gate from session state.

        Args:
            session_id: Session identifier

        Returns:
            DoRApprovalGate with restored state, None if session not found

        Example:
            >>> manager = ApprovalSessionManager()
            >>> gate = manager.restore_gate("session-123")
            >>> if gate and gate.is_approved:
            ...     result = gate.execute_if_approved()
        """
        session = self.get_session(session_id)
        if session is None:
            return None

        return self._deserialize_gate(session.gate_state)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session by ID.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found

        Example:
            >>> manager = ApprovalSessionManager()
            >>> deleted = manager.delete_session("session-123")
            >>> assert deleted
        """
        with self._session_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
        return False

    def list_sessions_by_user(self, user_id: str) -> List[ApprovalSession]:
        """
        List all sessions for a specific user.

        Args:
            user_id: User identifier

        Returns:
            List of ApprovalSession objects

        Example:
            >>> manager = ApprovalSessionManager()
            >>> sessions = manager.list_sessions_by_user("user1")
            >>> print(f"User has {len(sessions)} active sessions")
        """
        with self._session_lock:
            return [
                session for session in self._sessions.values()
                if session.user_id == user_id
            ]

    def cleanup_expired_sessions(self, ttl_seconds: int = 300) -> int:
        """
        Remove expired sessions.

        Args:
            ttl_seconds: TTL threshold (default: 5 minutes)

        Returns:
            Number of sessions removed

        Example:
            >>> manager = ApprovalSessionManager()
            >>> removed = manager.cleanup_expired_sessions(300)
            >>> print(f"Cleaned up {removed} expired sessions")
        """
        with self._session_lock:
            expired_ids = [
                sid for sid, session in self._sessions.items()
                if session.is_expired(ttl_seconds)
            ]
            for sid in expired_ids:
                del self._sessions[sid]

        return len(expired_ids)

    def _serialize_gate(self, gate: DoRApprovalGate) -> Dict[str, Any]:
        """
        Serialize DoR gate state to dict.

        Args:
            gate: DoR approval gate

        Returns:
            Serializable dict containing gate state
        """
        state: Dict[str, Any] = {
            "pending_text": gate._pending_text,
            "pending_context": gate._pending_context,
        }

        # Serialize current reflection
        if gate._current_reflection:
            reflection = gate._current_reflection
            state["current_reflection"] = {
                "intent_type": reflection.intent_type,
                "target_handler": reflection.target_handler,
                "dor_confidence": reflection.dor_confidence,
                "scope": reflection.scope,
                "key_entities": reflection.key_entities,
                "estimated_impact": reflection.estimated_impact,
                "business_principles": reflection.business_principles,
                "timestamp": reflection.timestamp,
            }

        # Serialize approval decision
        if gate._approval_decision:
            decision = gate._approval_decision
            state["approval_decision"] = {
                "status": decision.status.value,
                "timestamp": decision.timestamp,  # Already ISO string
                "feedback": decision.feedback,
            }

        return state

    def _deserialize_gate(self, state: Dict[str, Any]) -> DoRApprovalGate:
        """
        Deserialize DoR gate from state dict.

        Args:
            state: Serialized gate state

        Returns:
            DoRApprovalGate with restored state
        """
        gate = DoRApprovalGate()

        # Restore pending request
        gate._pending_text = state.get("pending_text")
        gate._pending_context = state.get("pending_context")

        # Restore reflection
        if "current_reflection" in state:
            reflection_data = state["current_reflection"]
            gate._current_reflection = IntentReflection(
                intent_type=reflection_data["intent_type"],
                target_handler=reflection_data["target_handler"],
                dor_confidence=reflection_data["dor_confidence"],
                scope=reflection_data["scope"],
                key_entities=reflection_data["key_entities"],
                estimated_impact=reflection_data["estimated_impact"],
                business_principles=reflection_data["business_principles"],
                timestamp=reflection_data["timestamp"],
            )

        # Restore approval decision
        if "approval_decision" in state:
            decision_data = state["approval_decision"]
            gate._approval_decision = ApprovalDecision(
                status=ApprovalStatus(decision_data["status"]),
                timestamp=decision_data["timestamp"],  # Already ISO string
                feedback=decision_data["feedback"],
            )

        return gate

    def clear_all(self) -> int:
        """
        Clear all sessions (for testing).

        Returns:
            Number of sessions cleared
        """
        with self._session_lock:
            count = len(self._sessions)
            self._sessions.clear()
        return count
