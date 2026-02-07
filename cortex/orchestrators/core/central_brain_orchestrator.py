"""
Central Brain Orchestrator - Phase 38 Stage 8.

Multi-user brain collaboration coordinator with shared context management.

AC-PHASE38-021: CentralBrainOrchestrator with multi-user support
AC-PHASE38-022: Team collaboration MCP tools integration
AC-PHASE38-023: Multi-tenant brain state management

CORE-008: TDD-first implementation
CORE-011: Full type hints
CORE-012: Google-style docstrings
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class SharedContext:
    """Shared context data structure."""
    
    context_id: str
    owner_id: str
    scope: str  # session, project, global
    data: Dict[str, Any] = field(default_factory=dict)
    shared_with: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class UserSession:
    """User session data structure."""
    
    session_id: str
    user_id: str
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Learning:
    """Learning data structure."""
    
    pattern: str
    confidence: float
    user_id: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


class CentralBrainOrchestrator:
    """
    Central brain coordination for multi-user collaboration.
    
    Manages shared context, user sessions, and learning aggregation
    across multiple team members.
    
    Attributes:
        shared_store: SharedBrainStore instance for persistence
        contexts: In-memory shared contexts
        sessions: Active user sessions
        learnings: Learning database
    """

    def __init__(self) -> None:
        """Initialize CentralBrainOrchestrator."""
        from cortex.infrastructure.shared_brain_store import SharedBrainStore
        
        self.shared_store = SharedBrainStore()
        self.contexts: Dict[str, SharedContext] = {}
        self.sessions: Dict[str, UserSession] = {}
        self.learnings: List[Learning] = []

    def share_context(
        self,
        user_id: str,
        context_data: Dict[str, Any],
        scope: str = "project",
    ) -> str:
        """
        Share context from one user.
        
        Args:
            user_id: User sharing the context
            context_data: Context data to share
            scope: Sharing scope (session/project/global)
            
        Returns:
            Context ID
        """
        context_id = f"ctx_{uuid.uuid4().hex[:8]}"
        
        context = SharedContext(
            context_id=context_id,
            owner_id=user_id,
            scope=scope,
            data=context_data,
        )
        
        self.contexts[context_id] = context
        return context_id

    def get_shared_context(
        self,
        context_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get shared context by ID.
        
        Args:
            context_id: Context ID to retrieve
            user_id: Requesting user ID
            
        Returns:
            Context data
        """
        if context_id and context_id in self.contexts:
            return self.contexts[context_id].data
        return {}

    def create_session(self, user_id: str) -> Dict[str, Any]:
        """
        Create user session.
        
        Args:
            user_id: User ID
            
        Returns:
            Session info dict
        """
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
        )
        
        self.sessions[session_id] = session
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": session.created_at,
        }

    def access_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """
        Access user session with permission check.
        
        Args:
            session_id: Session ID
            user_id: Requesting user ID
            
        Returns:
            Session data
            
        Raises:
            PermissionError: If user doesn't own session
        """
        if session_id not in self.sessions:
            raise KeyError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        if session.user_id != user_id:
            raise PermissionError(f"User {user_id} cannot access session {session_id}")
        
        return session.data

    def add_learning(self, user_id: str, learning_data: Dict[str, Any]) -> None:
        """
        Add learning from user.
        
        Args:
            user_id: User ID
            learning_data: Learning data with pattern and confidence
        """
        learning = Learning(
            pattern=learning_data["pattern"],
            confidence=learning_data["confidence"],
            user_id=user_id,
        )
        
        self.learnings.append(learning)

    def get_aggregated_learnings(self, pattern: str) -> Dict[str, Any]:
        """
        Get aggregated learnings for pattern.
        
        Args:
            pattern: Learning pattern to aggregate
            
        Returns:
            Aggregated learning data
        """
        relevant = [l for l in self.learnings if l.pattern == pattern]
        
        if not relevant:
            return {"pattern": pattern, "confidence": 0, "contributor_count": 0}
        
        avg_confidence = sum(l.confidence for l in relevant) / len(relevant)
        contributors = len(set(l.user_id for l in relevant))
        
        return {
            "pattern": pattern,
            "confidence": avg_confidence,
            "contributor_count": contributors,
        }

    def create_shared_context(self, scope: str = "project") -> str:
        """
        Create shared context for collaboration.
        
        Args:
            scope: Context scope
            
        Returns:
            Context ID
        """
        context_id = f"ctx_{uuid.uuid4().hex[:8]}"
        
        context = SharedContext(
            context_id=context_id,
            owner_id="system",
            scope=scope,
        )
        
        self.contexts[context_id] = context
        return context_id

    def update_shared_context(
        self,
        context_id: str,
        user_id: str,
        updates: Dict[str, Any],
    ) -> None:
        """
        Update shared context (CRDT-based).
        
        Args:
            context_id: Context to update
            user_id: User making update
            updates: Update data
        """
        if context_id not in self.contexts:
            raise KeyError(f"Context {context_id} not found")
        
        context = self.contexts[context_id]
        
        # CRDT merge: Last-write-wins for simplicity
        context.data.update(updates)
        
        if user_id not in context.shared_with:
            context.shared_with.append(user_id)
