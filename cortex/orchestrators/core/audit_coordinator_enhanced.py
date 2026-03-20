"""AuditCoordinatorEnhanced bridges audit, session state, and RCA wrappers."""

from __future__ import annotations

from typing import Any, Dict, Optional

from cortex.core.session_bridge import SessionBridge
from cortex.intelligence.learning.rca_engine import RCAEngine
from cortex.intelligence.learning.rca_models import RCACategory
from cortex.orchestrators.core.audit_orchestrator import AuditOrchestrator


class AuditCoordinatorEnhanced(AuditOrchestrator):
    """Enhanced audit coordinator with RCA and session hooks."""

    def __init__(
        self,
        workspace_root: Optional[str] = None,
        session_bridge: Optional[SessionBridge] = None,
    ) -> None:
        """Initialize enhanced coordinator.

        Args:
            workspace_root: Optional workspace root.
            session_bridge: Optional session bridge.
        """
        super().__init__(workspace_root=workspace_root)
        self._session_bridge = session_bridge if session_bridge is not None else SessionBridge()
        self._rca_engine = RCAEngine()

    def run_rca(self, failure_id: str, symptom: str) -> Dict[str, Any]:
        """Run RCA using default technology-category selection.

        Args:
            failure_id: Failure identifier.
            symptom: Human-readable symptom.

        Returns:
            Serializable RCA summary.
        """
        analysis = self._rca_engine.analyze(
            failure_id=failure_id,
            symptom=symptom,
            category=RCACategory.TECHNOLOGY,
        )
        return {
            "failure_id": analysis.failure_id,
            "methodology": analysis.methodology.value,
            "root_cause": analysis.root_cause,
            "confidence": analysis.confidence,
        }
