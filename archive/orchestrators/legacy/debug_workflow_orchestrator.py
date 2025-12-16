"""
CORTEX Debug Workflow Orchestrator

Minimal debug workflow orchestrator focused on RCA (Root Cause Analysis) pattern capture.
Integrates with LearningObserver to automatically store bug resolutions in Tier 2.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.

Design:
    - Observer pattern (subscribe/unsubscribe/notify)
    - Session-based debugging (start → investigate → complete)
    - Automatic RCA pattern emission on completion
    - <50ms overhead for event emission

Usage:
    from src.orchestrators.debug_workflow_orchestrator import DebugWorkflowOrchestrator
    from src.orchestrators.learning_observer import LearningObserver
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    observer = LearningObserver(kg)
    debug_orchestrator = DebugWorkflowOrchestrator()
    
    debug_orchestrator.subscribe(observer)
    
    # Start debug session
    session_id = debug_orchestrator.start_debug_session(
        symptom="Application crashes on login",
        target="authentication_module"
    )
    
    # Complete with RCA
    debug_orchestrator.complete_debug_session(
        session_id=session_id,
        root_cause="Null pointer exception in session validation",
        fix_applied="Added null check before session access",
        prevention="Add unit tests for null session scenarios",
        recurrence_risk="low",
        affected_features=["authentication", "sessions"]
    )
    
    # Observer automatically stores RCA pattern in Tier 2
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class DebugWorkflowOrchestrator:
    """
    Orchestrator for debug workflows with RCA pattern capture.
    
    Responsibilities:
        - Manage debug session lifecycle (start → investigate → complete)
        - Track active debug sessions
        - Emit debug_session_completion events to observers
        - Provide session metadata for RCA analysis
    
    Events Emitted:
        - debug_session_completion: When debug session is completed with RCA
    
    Event Payload:
        {
            "session_id": str,
            "symptom": str,
            "target": str,
            "root_cause": str,
            "fix_applied": str,
            "prevention": str,
            "recurrence_risk": "high|medium|low",
            "affected_features": List[str],
            "duration_seconds": float,
            "started_at": str (ISO format),
            "completed_at": str (ISO format)
        }
    """
    
    def __init__(self):
        """Initialize debug workflow orchestrator."""
        self._observers: List[Any] = []
        self._sessions: Dict[str, Dict[str, Any]] = {}
    
    def subscribe(self, observer: Any) -> None:
        """
        Subscribe an observer to debug events.
        
        Args:
            observer: Observer instance with on_debug_session_completion() method
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Observer subscribed to debug orchestrator: {observer}")
    
    def unsubscribe(self, observer: Any) -> None:
        """
        Unsubscribe an observer from debug events.
        
        Args:
            observer: Observer instance to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Observer unsubscribed from debug orchestrator: {observer}")
    
    def start_debug_session(
        self,
        symptom: str,
        target: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new debug session.
        
        Args:
            symptom: Observable issue description
            target: Component/module being debugged
            metadata: Optional additional session metadata
        
        Returns:
            Session ID for tracking
        """
        session_id = str(uuid.uuid4())
        started_at = datetime.now()
        
        session = {
            "session_id": session_id,
            "symptom": symptom,
            "target": target,
            "status": "in_progress",
            "started_at": started_at.isoformat(),
            "metadata": metadata or {}
        }
        
        self._sessions[session_id] = session
        logger.info(f"Debug session started: {session_id} - {symptom}")
        
        return session_id
    
    def complete_debug_session(
        self,
        session_id: str,
        root_cause: str,
        fix_applied: str,
        prevention: str,
        recurrence_risk: str,
        affected_features: List[str]
    ) -> None:
        """
        Complete a debug session and emit RCA pattern event.
        
        Args:
            session_id: Session identifier from start_debug_session()
            root_cause: Identified root cause
            fix_applied: Fix that was implemented
            prevention: Strategy to prevent recurrence
            recurrence_risk: 'high', 'medium', or 'low'
            affected_features: List of affected features/components
        """
        if session_id not in self._sessions:
            logger.warning(f"Session not found: {session_id}")
            return
        
        session = self._sessions[session_id]
        completed_at = datetime.now()
        
        # Calculate duration
        started_at = datetime.fromisoformat(session['started_at'])
        duration_seconds = (completed_at - started_at).total_seconds()
        
        # Update session status
        session['status'] = "completed"
        session['completed_at'] = completed_at.isoformat()
        session['root_cause'] = root_cause
        session['fix_applied'] = fix_applied
        session['prevention'] = prevention
        session['recurrence_risk'] = recurrence_risk
        session['affected_features'] = affected_features
        session['duration_seconds'] = duration_seconds
        
        # Build event payload
        event = {
            "session_id": session_id,
            "symptom": session['symptom'],
            "target": session['target'],
            "root_cause": root_cause,
            "fix_applied": fix_applied,
            "prevention": prevention,
            "recurrence_risk": recurrence_risk,
            "affected_features": affected_features,
            "duration_seconds": duration_seconds,
            "started_at": session['started_at'],
            "completed_at": session['completed_at'],
            **session.get('metadata', {})
        }
        
        # Emit event to observers
        self._notify_observers(event)
        
        logger.info(f"Debug session completed: {session_id} - Root cause: {root_cause}")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session details by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session dict or None if not found
        """
        return self._sessions.get(session_id)
    
    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active (in-progress) debug sessions.
        
        Returns:
            List of active session dicts
        """
        return [s for s in self._sessions.values() if s['status'] == 'in_progress']
    
    def _notify_observers(self, event: Dict[str, Any]) -> None:
        """
        Notify all observers of debug_session_completion event.
        
        Args:
            event: Event payload with RCA details
        """
        for observer in self._observers:
            try:
                if hasattr(observer, 'on_debug_session_completion'):
                    observer.on_debug_session_completion(event)
                else:
                    logger.warning(f"Observer {observer} missing on_debug_session_completion() method")
            except Exception as e:
                logger.error(f"Error notifying observer {observer}: {e}", exc_info=True)


__all__ = ["DebugWorkflowOrchestrator"]
