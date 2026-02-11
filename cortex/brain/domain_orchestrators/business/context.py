"""
AC-PHX-008-05: Domain Context Management

Context management for domain orchestrators providing isolation,
scoped data, and session management.

"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class DomainContext:
    """
    Domain execution context.

    Provides isolation and scoped data storage for domain operations.
    """
    domain: str
    operation: str
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    parent_context_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "domain": self.domain,
            "operation": self.operation,
            "session_id": self.session_id,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "user_id": self.user_id,
            "parent_context_id": self.parent_context_id,
        }


class DomainContextManager:
    """
    Manager for domain contexts.

    Provides:
    - Context creation and lifecycle management
    - Scoped data storage per context
    - Context isolation between domains
    - Cleanup and garbage collection
    """

    _instance: Optional['DomainContextManager'] = None

    def __init__(self) -> None:
        """Initialize context manager."""
        self._contexts: Dict[str, DomainContext] = {}
        self._scoped_data: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> 'DomainContextManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def create_context(
        self,
        domain: str,
        operation: str,
        parameters: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        parent_context_id: Optional[str] = None,
    ) -> DomainContext:
        """
        Create a new domain context.

        Args:
            domain: Domain name
            operation: Operation being performed
            parameters: Operation parameters
            user_id: User ID (for audit)
            parent_context_id: Parent context ID (for nested contexts)

        Returns:
            New domain context
        """
        context = DomainContext(
            domain=domain,
            operation=operation,
            parameters=parameters or {},
            user_id=user_id,
            parent_context_id=parent_context_id,
        )

        self._contexts[context.session_id] = context
        self._scoped_data[context.session_id] = {}

        return context

    def get_context(self, session_id: str) -> Optional[DomainContext]:
        """
        Get context by session ID.

        Args:
            session_id: Session ID

        Returns:
            Context or None if not found
        """
        return self._contexts.get(session_id)

    def set_scoped_data(
        self,
        session_id: str,
        key: str,
        value: Any
    ) -> None:
        """
        Set scoped data for a context.

        Args:
            session_id: Context session ID
            key: Data key
            value: Data value
        """
        if session_id in self._scoped_data:
            self._scoped_data[session_id][key] = value

    def get_scoped_data(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get scoped data for a context.

        Args:
            session_id: Context session ID
            key: Data key
            default: Default value if not found

        Returns:
            Data value or default
        """
        if session_id not in self._scoped_data:
            return default
        return self._scoped_data[session_id].get(key, default)

    def cleanup_context(self, session_id: str) -> bool:
        """
        Clean up a context and its scoped data.

        Args:
            session_id: Context session ID

        Returns:
            True if context was cleaned up, False if not found
        """
        if session_id not in self._contexts:
            return False

        del self._contexts[session_id]

        if session_id in self._scoped_data:
            del self._scoped_data[session_id]

        return True

    def list_active_contexts(self, domain: Optional[str] = None) -> list:
        """
        List active contexts.

        Args:
            domain: Filter by domain (optional)

        Returns:
            List of active contexts
        """
        contexts = list(self._contexts.values())
        if domain:
            contexts = [c for c in contexts if c.domain == domain]
        return contexts

    def cleanup_expired_contexts(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up expired contexts.

        Args:
            max_age_seconds: Maximum context age in seconds

        Returns:
            Number of contexts cleaned up
        """
        now = datetime.utcnow()
        expired = []

        for session_id, context in self._contexts.items():
            age = (now - context.created_at).total_seconds()
            if age > max_age_seconds:
                expired.append(session_id)

        for session_id in expired:
            self.cleanup_context(session_id)

        return len(expired)
