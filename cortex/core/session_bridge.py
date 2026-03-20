"""SessionBridge for lightweight cross-orchestrator session state."""

from __future__ import annotations

from typing import Any, Dict, Optional


class SessionBridge:
    """Store and retrieve session-scoped key/value state."""

    def __init__(self) -> None:
        """Initialize in-memory session store."""
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def set_value(self, session_id: str, key: str, value: Any) -> None:
        """Set a key/value pair for a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        self._sessions[session_id][key] = value

    def get_value(self, session_id: str, key: str) -> Optional[Any]:
        """Get a value for a session key."""
        return self._sessions.get(session_id, {}).get(key)
