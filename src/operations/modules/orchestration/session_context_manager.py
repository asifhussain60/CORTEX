"""
Session Context Manager - Automatic Context Continuity
======================================================

Manages active planning sessions and automatic context loading.

Purpose:
- Track active planning sessions
- Automatic context association (no manual file references)
- Session-based context loading
- User never needs to reference temp plan files explicitly

SKULL Enforcement:
- CONTEXT_CONTINUITY_ENFORCEMENT: Automatic context tracking

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from src.operations.modules.orchestration.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


@dataclass
class PlanningSession:
    """Active planning session tracking."""
    session_id: str
    plan_id: str
    user_request: str
    created_at: str
    last_updated: str
    status: str  # "drafting", "awaiting_approval", "approved"
    complexity_tier: int
    temp_plan_path: str
    iteration_count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanningSession':
        """Create from dictionary."""
        return cls(**data)


class SessionContextManager:
    """
    Manages automatic context continuity for planning sessions.
    
    Features:
    - Automatic session creation
    - Context association without manual file references
    - Session persistence
    - Automatic cleanup
    
    User Experience:
    - User: "Add authentication"
      → Creates session-12345, associates with temp-plans/auth/
    - User: "Use OAuth for Google"
      → Automatically loads session-12345 context, updates plan
    - User: "approve"
      → Closes session, promotes plan
    
    No manual file references needed!
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize session context manager.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.sessions_file = self.project_root / "cortex-brain" / "active-sessions.json"
        self.active_sessions: Dict[str, PlanningSession] = {}
        
        # Load existing sessions
        self._load_sessions()
        
        logger.info("✅ SessionContextManager initialized")
    
    def create_session(
        self,
        plan_id: str,
        user_request: str,
        complexity_tier: int,
        temp_plan_path: Path
    ) -> PlanningSession:
        """
        Create new planning session.
        
        Args:
            plan_id: Plan identifier
            user_request: User's original request
            complexity_tier: Complexity tier (1-4)
            temp_plan_path: Path to temp plan folder
            
        Returns:
            PlanningSession object
        """
        session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        session = PlanningSession(
            session_id=session_id,
            plan_id=plan_id,
            user_request=user_request,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            status="drafting",
            complexity_tier=complexity_tier,
            temp_plan_path=str(temp_plan_path),
            iteration_count=1
        )
        
        self.active_sessions[session_id] = session
        self._persist_sessions()
        
        logger.info(f"✅ Created planning session: {session_id}")
        
        # Audit: Session started
        audit_logger.log_event(
            event_type="session_started",
            session_id=session_id,
            plan_id=plan_id,
            orchestrator="SessionContextManager",
            user_request=user_request,
            phase="initialization",
            metadata={
                "complexity_tier": complexity_tier,
                "temp_plan_path": str(temp_plan_path)
            }
        )
        
        return session
    
    def get_active_session_for_plan(self, plan_id: str) -> Optional[PlanningSession]:
        """
        Get active session for plan ID.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            PlanningSession if found, None otherwise
        """
        for session in self.active_sessions.values():
            if session.plan_id == plan_id and session.status in ["drafting", "awaiting_approval"]:
                return session
        return None
    
    def update_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        iteration_count: Optional[int] = None
    ):
        """
        Update session metadata.
        
        Args:
            session_id: Session ID
            status: New status (optional)
            iteration_count: New iteration count (optional)
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session not found: {session_id}")
            return
        
        session = self.active_sessions[session_id]
        
        if status:
            session.status = status
        if iteration_count is not None:
            session.iteration_count = iteration_count
        
        session.last_updated = datetime.now().isoformat()
        
        self._persist_sessions()
        logger.info(f"✅ Updated session: {session_id}")
    
    def close_session(self, session_id: str):
        """
        Close planning session.
        
        Args:
            session_id: Session ID
        """
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Calculate duration
            created_at = datetime.fromisoformat(session.created_at)
            duration_seconds = (datetime.now() - created_at).total_seconds()
            
            session.status = "completed"
            session.last_updated = datetime.now().isoformat()
            
            # Audit: Session closed
            audit_logger.log_event(
                event_type="session_closed",
                session_id=session_id,
                plan_id=session.plan_id,
                orchestrator="SessionContextManager",
                phase="completion",
                metadata={
                    "final_status": session.status,
                    "duration_seconds": duration_seconds,
                    "total_iterations": session.iteration_count
                }
            )
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            self._persist_sessions()
            logger.info(f"✅ Closed session: {session_id}")
    
    def get_all_active_sessions(self) -> Dict[str, PlanningSession]:
        """Get all active sessions."""
        return self.active_sessions
    
    def load_context_for_request(self, user_request: str) -> Optional[PlanningSession]:
        """
        Automatically load context for user request.
        
        This is the KEY method for automatic context continuity.
        When user provides feedback without referencing the plan,
        this method finds the active session automatically.
        
        Args:
            user_request: User's new request/feedback
            
        Returns:
            PlanningSession if active session found, None otherwise
        """
        # Find most recent active session
        active_sessions = [
            s for s in self.active_sessions.values()
            if s.status in ["drafting", "awaiting_approval"]
        ]
        
        if not active_sessions:
            return None
        
        # Return most recent (by last_updated)
        return max(active_sessions, key=lambda s: s.last_updated)
    
    def _load_sessions(self):
        """Load sessions from persistence."""
        if not self.sessions_file.exists():
            return
        
        try:
            data = json.loads(self.sessions_file.read_text(encoding='utf-8'))
            self.active_sessions = {
                sid: PlanningSession.from_dict(sdata)
                for sid, sdata in data.items()
            }
            logger.info(f"✅ Loaded {len(self.active_sessions)} active sessions")
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.active_sessions = {}
    
    def _persist_sessions(self):
        """Persist sessions to file."""
        try:
            data = {
                sid: session.to_dict()
                for sid, session in self.active_sessions.items()
            }
            self.sessions_file.write_text(
                json.dumps(data, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"Failed to persist sessions: {e}")
