"""
ENH-087 Track 5 Stage 3: Session State Persistence - GREEN Phase Implementation

Implements session state persistence orchestrator for LENS analysis workflow:
- Session creation with metadata tracking
- Session state serialization to YAML
- Session state validation
- Session recovery after process restart
- Session lifecycle management (create, read, update, delete, archive)

Physical Artifacts:
  cortex_brain/sessions/{session_id}.yaml - Session state file
  cortex_brain/sessions/archive/{session_id}.yaml - Archived session

Authority: ENH-087 Track 5 + YAML persistence pattern
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

AC_START: AC-ENH087-T5-S3-GREEN-001
Description: Session state orchestrator implementation with YAML persistence
"""

from __future__ import annotations

import logging
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Status of analysis session."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class SessionMetadata:
    """Metadata for analysis session."""
    orchestrator: str
    operation: str
    stage: int = 1
    analysis_type: str = "LENS"
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisSession:
    """Complete analysis session with state + metadata."""
    session_id: str
    repo_id: str
    repo_path: str
    status: SessionStatus = SessionStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: Optional[str] = None
    metadata: Optional[SessionMetadata] = None
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for YAML serialization."""
        return {
            "session_id": self.session_id,
            "repo_id": self.repo_id,
            "repo_path": self.repo_path,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": asdict(self.metadata) if self.metadata else None,
            "analysis_results": self.analysis_results,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> AnalysisSession:
        """Create session from dictionary (loaded from YAML)."""
        status_str = data.get("status", "pending")
        meta_data = data.get("metadata")
        
        metadata = None
        if meta_data:
            metadata = SessionMetadata(
                orchestrator=meta_data.get("orchestrator", ""),
                operation=meta_data.get("operation", ""),
                stage=meta_data.get("stage", 1),
                analysis_type=meta_data.get("analysis_type", "LENS"),
                custom_data=meta_data.get("custom_data", {}),
            )
        
        return AnalysisSession(
            session_id=data.get("session_id", ""),
            repo_id=data.get("repo_id", ""),
            repo_path=data.get("repo_path", ""),
            status=SessionStatus(status_str),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at"),
            metadata=metadata,
            analysis_results=data.get("analysis_results", {}),
        )


class SessionStateOrchestrator:
    """
    Orchestrates session state persistence for LENS analysis.
    
    Responsibilities:
    - Manage session lifecycle (create, read, update, archive, delete)
    - Persist session state to YAML files
    - Validate session integrity
    - Support session recovery after restart
    
    Physical Artifacts:
    - cortex_brain/sessions/{session_id}.yaml
    - cortex_brain/sessions/archive/{session_id}.yaml
    """
    
    def __init__(self, cortex_brain_path: Optional[Path] = None) -> None:
        """
        Initialize session state orchestrator.
        
        Args:
            cortex_brain_path: Path to cortex_brain directory
        """
        self.cortex_brain_path = cortex_brain_path or Path("cortex_brain")
        self.sessions_dir = self.cortex_brain_path / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir = self.sessions_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized SessionStateOrchestrator: {self.sessions_dir}")
    
    def create_session(
        self,
        session_id: str,
        repo_id: str,
        repo_path: str,
        orchestrator: str = "LENSOrchestrator",
        operation: str = "ANALYZE",
    ) -> Optional[AnalysisSession]:
        """
        Create new analysis session.
        
        Args:
            session_id: Unique session identifier
            repo_id: Repository identifier
            repo_path: Path to repository
            orchestrator: Orchestrator name
            operation: Operation type (ANALYZE, IMPLEMENT, etc.)
        
        Returns:
            AnalysisSession if successful, None otherwise
        """
        try:
            session = AnalysisSession(
                session_id=session_id,
                repo_id=repo_id,
                repo_path=repo_path,
                status=SessionStatus.ACTIVE,
                metadata=SessionMetadata(
                    orchestrator=orchestrator,
                    operation=operation,
                ),
            )
            
            # Write session file
            success = self.update_session(session_id, session)
            if success:
                logger.info(f"Created session: {session_id}")
                return session
            
            return None
        
        except Exception as e:
            logger.exception(f"Failed to create session {session_id}: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[AnalysisSession]:
        """
        Retrieve session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            AnalysisSession if found and valid, None otherwise
        """
        session_file = self.sessions_dir / f"{session_id}.yaml"
        
        if not session_file.exists():
            logger.warning(f"Session not found: {session_file}")
            return None
        
        try:
            with open(session_file) as f:
                data = yaml.safe_load(f)
            
            session = AnalysisSession.from_dict(data)
            logger.debug(f"Loaded session: {session_id}")
            return session
        
        except Exception as e:
            logger.exception(f"Failed to load session {session_id}: {e}")
            return None
    
    def update_session(
        self,
        session_id: str,
        session: AnalysisSession,
    ) -> bool:
        """
        Update session state.
        
        Args:
            session_id: Session identifier
            session: Updated session object
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update timestamp
            session.updated_at = datetime.utcnow().isoformat()
            
            # Write session file
            session_file = self.sessions_dir / f"{session_id}.yaml"
            with open(session_file, 'w') as f:
                yaml.dump(session.to_dict(), f, default_flow_style=False)
            
            logger.debug(f"Updated session: {session_id}")
            return True
        
        except Exception as e:
            logger.exception(f"Failed to update session {session_id}: {e}")
            return False
    
    def add_analysis_result(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> bool:
        """
        Add analysis result to session.
        
        Args:
            session_id: Session identifier
            key: Result key
            value: Result value
        
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session(session_id)
        if session is None:
            logger.error(f"Session not found: {session_id}")
            return False
        
        session.analysis_results[key] = value
        return self.update_session(session_id, session)
    
    def list_active_sessions(self) -> list[str]:
        """
        List all active sessions.
        
        Returns:
            List of active session IDs
        """
        active_sessions = []
        
        for session_file in self.sessions_dir.glob("*.yaml"):
            try:
                with open(session_file) as f:
                    data = yaml.safe_load(f)
                
                status = data.get("status", "")
                if status == SessionStatus.ACTIVE.value:
                    active_sessions.append(data.get("session_id", ""))
            
            except Exception as e:
                logger.warning(f"Failed to read session file {session_file}: {e}")
        
        return active_sessions
    
    def archive_session(self, session_id: str) -> bool:
        """
        Archive session (move to archive directory).
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.get_session(session_id)
            if session is None:
                logger.error(f"Session not found: {session_id}")
                return False
            
            # Update status
            session.status = SessionStatus.ARCHIVED
            
            # Read original file
            original_file = self.sessions_dir / f"{session_id}.yaml"
            content = original_file.read_text()
            
            # Write to archive
            archive_file = self.archive_dir / f"{session_id}.yaml"
            archive_file.write_text(content)
            
            # Remove original
            original_file.unlink()
            
            logger.info(f"Archived session: {session_id}")
            return True
        
        except Exception as e:
            logger.exception(f"Failed to archive session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if successful, False otherwise
        """
        try:
            session_file = self.sessions_dir / f"{session_id}.yaml"
            
            if not session_file.exists():
                logger.warning(f"Session not found: {session_id}")
                return False
            
            session_file.unlink()
            logger.info(f"Deleted session: {session_id}")
            return True
        
        except Exception as e:
            logger.exception(f"Failed to delete session {session_id}: {e}")
            return False
    
    def validate_session_integrity(self, session_id: str) -> bool:
        """
        Validate session file integrity.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if session is valid, False otherwise
        """
        session = self.get_session(session_id)
        
        if session is None:
            return False
        
        # Check required fields
        required_fields = ["session_id", "repo_id", "repo_path", "status", "created_at"]
        session_dict = session.to_dict()
        
        for field in required_fields:
            if field not in session_dict or session_dict[field] is None:
                logger.error(f"Session missing required field: {field}")
                return False
        
        logger.debug(f"Session integrity verified: {session_id}")
        return True


# AC_COMPLETE: AC-ENH087-T5-S3-GREEN-001 ✅ Session state orchestrator implementation
