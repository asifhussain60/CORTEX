"""
CentralBrainOrchestrator — Multi-user shared brain orchestration.

AC-PHASE38-021: CentralBrainOrchestrator with multi-user support
AC-PHASE38-022: Team collaboration MCP tools
AC-PHASE38-023: Multi-tenant brain state management
"""
from __future__ import annotations

import uuid
from typing import Any, Dict, List

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94f


class CentralBrainOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Orchestrates shared brain state across multiple users."""

    # Phase 94f — advisory: shared-brain state manager, not a code-execution entry point.
    # Gateway routing deferred until MasterOrchestrator milestone.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        """Initialize instance."""
        from cortex.infrastructure.shared_brain_store import SharedBrainStore
        self.shared_store: SharedBrainStore = SharedBrainStore()
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._learnings: List[Dict[str, Any]] = []
        self._shared_contexts: Dict[str, Dict[str, Any]] = {}

    def share_context(
        self,
        user_id: str,
        context_data: Dict[str, Any],
        scope: str = "project",
    ) -> str:
        """Share context data for a user. Returns context_id."""
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation="share_context",
            orchestrator_context=context_data,
        )
        context_id = str(uuid.uuid4())
        self._shared_contexts[context_id] = {
            "owner": user_id,
            "data": context_data,
            "scope": scope,
        }
        return context_id

    def get_shared_context(
        self, context_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Retrieve shared context by id."""
        ctx = self._shared_contexts.get(context_id, {})
        return ctx.get("data", {})

    def create_session(self, user_id: str) -> Dict[str, Any]:
        """Create an isolated session for a user."""
        session_id = str(uuid.uuid4())
        session = {"session_id": session_id, "user_id": user_id}
        self._sessions[session_id] = session
        return session

    def access_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Access a session — raises PermissionError if user doesn't own it."""
        session = self._sessions.get(session_id)
        if session is None or session["user_id"] != user_id:
            raise PermissionError(
                f"User {user_id!r} cannot access session {session_id!r}"
            )
        return session

    def add_learning(
        self, user_id: str, learning_data: Dict[str, Any]
    ) -> None:
        """Add a learning entry from a user."""
        self._learnings.append({"user_id": user_id, **learning_data})

    def get_aggregated_learnings(self, pattern: str) -> Dict[str, Any]:
        """Aggregate learnings for a given pattern."""
        matches = [l for l in self._learnings if l.get("pattern") == pattern]
        if not matches:
            return {"pattern": pattern, "confidence": 0.0, "contributor_count": 0}
        avg_conf = sum(m.get("confidence", 0) for m in matches) / len(matches)
        return {
            "pattern": pattern,
            "confidence": avg_conf,
            "contributor_count": len(matches),
        }

    def merge_concurrent_writes(
        self, context_id: str, writes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Merge concurrent writes using last-write-wins CRDT."""
        merged: Dict[str, Any] = {}
        for write in writes:
            merged.update(write)
        return merged


# Phase 102-a — GAP-102-04: Domain-appropriate alias (brain → collaboration naming)
# CORE-035: CentralBrainOrchestrator remains canonical; CollaborationOrchestrator is the forward path.
CollaborationOrchestrator = CentralBrainOrchestrator  # noqa: CORE-035
