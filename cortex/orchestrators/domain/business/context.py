"""Domain Context Management

Context management for domain-scoped operations.
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class DomainContext:
    """Domain execution context."""
    session_id: str
    domain: str
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DomainContextManager:
    """Manager for domain contexts."""

    def __init__(self):
        """Initialize context manager."""
        self._contexts: Dict[str, DomainContext] = {}
        self._scoped_data: Dict[str, Dict[str, Any]] = {}

    def create_context(
        self,
        domain: str,
        operation: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> DomainContext:
        """Create a new domain context.

        Args:
            domain: Domain name
            operation: Operation name
            parameters: Operation parameters

        Returns:
            Created context
        """
        session_id = str(uuid.uuid4())

        context = DomainContext(
            session_id=session_id,
            domain=domain,
            operation=operation,
            parameters=parameters or {}
        )

        self._contexts[session_id] = context
        self._scoped_data[session_id] = {}

        return context

    def set_scoped_data(self, session_id: str, key: str, value: Any) -> None:
        """Set scoped data for a context.

        Args:
            session_id: Session identifier
            key: Data key
            value: Data value
        """
        if session_id not in self._scoped_data:
            self._scoped_data[session_id] = {}

        self._scoped_data[session_id][key] = value

    def get_scoped_data(self, session_id: str, key: str) -> Optional[Any]:
        """Get scoped data for a context.

        Args:
            session_id: Session identifier
            key: Data key

        Returns:
            Data value or None
        """
        if session_id not in self._scoped_data:
            return None

        return self._scoped_data[session_id].get(key)

    def cleanup_context(self, session_id: str) -> None:
        """Clean up context data.

        Args:
            session_id: Session identifier
        """
        if session_id in self._contexts:
            del self._contexts[session_id]

        if session_id in self._scoped_data:
            del self._scoped_data[session_id]


__all__ = ["DomainContext", "DomainContextManager"]
