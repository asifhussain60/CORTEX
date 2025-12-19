"""
CORTEX 4.0 Session Manager - Planning Execution State Persistence

Purpose: Manages planning execution session state for resuming interrupted workflows.
         Provides session persistence, restoration, and recovery capabilities.
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19 (Week 8 Day 3)

Key Features:
- Session state persistence (execution context, progress, metadata)
- Session restoration after interruptions (crash, logout, manual stop)
- Multi-session support (multiple concurrent plans)
- Session locking to prevent conflicts
- Automatic cleanup of stale sessions
- Session history and audit trail

Architecture:
- SessionManager: Main session coordinator
- SessionState: Execution state snapshot
- SessionLock: Prevents concurrent access
- SessionHistory: Audit trail

Integration Points:
- PlanExecutor: Execution engine
- PhaseManagerIntegration: Phase progress tracking
- GitCheckpointManager: Checkpoint coordination
"""

import logging
import fcntl
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import os

logger = logging.getLogger(__name__)


# ============================================================================
# Domain Models
# ============================================================================

class SessionStatus(Enum):
    """Session execution status."""
    ACTIVE = "active"                 # Currently executing
    PAUSED = "paused"                 # Paused manually
    INTERRUPTED = "interrupted"       # Interrupted (crash, logout)
    COMPLETED = "completed"           # Finished successfully
    FAILED = "failed"                 # Finished with errors


@dataclass
class SessionState:
    """
    Planning execution session state.
    
    Contains all information needed to resume execution from interruption point.
    """
    session_id: str
    plan_name: str
    plan_path: Path
    workspace_root: Path
    status: SessionStatus
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Execution state
    current_phase: Optional[str] = None
    completed_phases: List[str] = field(default_factory=list)
    phase_results: Dict[str, Any] = field(default_factory=dict)
    
    # Progress tracking
    progress_percent: float = 0.0
    execution_time_seconds: float = 0.0
    
    # Checkpoint tracking
    checkpoints: List[str] = field(default_factory=list)
    last_checkpoint_id: Optional[str] = None
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Execution configuration
    execution_mode: str = "supervised"
    auto_checkpoint: bool = True
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Session Manager
# ============================================================================

class SessionManager:
    """
    Planning execution session manager.
    
    Responsibilities:
    - Create and persist session state
    - Restore interrupted sessions
    - Lock sessions to prevent conflicts
    - Clean up stale sessions
    - Maintain session history
    """
    
    def __init__(
        self,
        workspace_root: Path,
        session_dir: Optional[Path] = None,
        logger_instance: Optional[logging.Logger] = None
    ):
        """
        Initialize session manager.
        
        Args:
            workspace_root: User workspace root directory
            session_dir: Session storage directory (default: workspace_root/.cortex/sessions)
            logger_instance: Optional logger instance
        """
        self.workspace_root = Path(workspace_root)
        self.session_dir = Path(session_dir) if session_dir else self.workspace_root / ".cortex" / "sessions"
        self.logger = logger_instance or logger
        
        # Ensure session directory exists
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Session locks
        self._locks: Dict[str, Any] = {}  # session_id -> file lock
    
    def create_session(
        self,
        plan_name: str,
        plan_path: Path,
        execution_config: Optional[Dict[str, Any]] = None
    ) -> SessionState:
        """
        Create new planning execution session.
        
        Args:
            plan_name: Name of plan being executed
            plan_path: Path to plan file
            execution_config: Optional execution configuration
        
        Returns:
            SessionState with session ID and initial state
        """
        # Generate session ID
        session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create session state
        session = SessionState(
            session_id=session_id,
            plan_name=plan_name,
            plan_path=plan_path,
            workspace_root=self.workspace_root,
            status=SessionStatus.ACTIVE
        )
        
        # Apply execution config
        if execution_config:
            session.execution_mode = execution_config.get("execution_mode", "supervised")
            session.auto_checkpoint = execution_config.get("auto_checkpoint", True)
            session.metadata = execution_config.get("metadata", {})
        
        # Persist session
        self._persist_session(session)
        
        self.logger.info(f"✅ Session created: {session_id}")
        return session
    
    def update_session(self, session: SessionState) -> bool:
        """
        Update existing session state.
        
        Args:
            session: Session state to update
        
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Update timestamp
            session.updated_at = datetime.now()
            
            # Persist session
            self._persist_session(session)
            
            self.logger.debug(f"💾 Session updated: {session.session_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Failed to update session: {e}", exc_info=True)
            return False
    
    def restore_session(self, session_id: str) -> Optional[SessionState]:
        """
        Restore session from storage.
        
        Args:
            session_id: Session ID to restore
        
        Returns:
            SessionState or None if not found
        """
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            self.logger.warning(f"⚠️  Session not found: {session_id}")
            return None
        
        try:
            data = json.loads(session_file.read_text())
            
            session = SessionState(
                session_id=data["session_id"],
                plan_name=data["plan_name"],
                plan_path=Path(data["plan_path"]),
                workspace_root=Path(data["workspace_root"]),
                status=SessionStatus(data["status"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"]),
                current_phase=data.get("current_phase"),
                completed_phases=data.get("completed_phases", []),
                phase_results=data.get("phase_results", {}),
                progress_percent=data.get("progress_percent", 0.0),
                execution_time_seconds=data.get("execution_time_seconds", 0.0),
                checkpoints=data.get("checkpoints", []),
                last_checkpoint_id=data.get("last_checkpoint_id"),
                errors=data.get("errors", []),
                warnings=data.get("warnings", []),
                execution_mode=data.get("execution_mode", "supervised"),
                auto_checkpoint=data.get("auto_checkpoint", True),
                metadata=data.get("metadata", {})
            )
            
            self.logger.info(f"✅ Session restored: {session_id}")
            return session
        
        except Exception as e:
            self.logger.error(f"❌ Failed to restore session: {e}", exc_info=True)
            return None
    
    def find_active_sessions(self) -> List[SessionState]:
        """
        Find all active or paused sessions.
        
        Returns:
            List of SessionState objects
        """
        active_sessions = []
        
        for session_file in self.session_dir.glob("session-*.json"):
            try:
                data = json.loads(session_file.read_text())
                status = SessionStatus(data["status"])
                
                if status in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
                    session = self.restore_session(data["session_id"])
                    if session:
                        active_sessions.append(session)
            
            except Exception as e:
                self.logger.error(f"❌ Error reading session file {session_file}: {e}")
                continue
        
        return active_sessions
    
    def find_interrupted_sessions(self) -> List[SessionState]:
        """
        Find all interrupted sessions (candidates for restoration).
        
        Returns:
            List of SessionState objects
        """
        interrupted_sessions = []
        
        for session_file in self.session_dir.glob("session-*.json"):
            try:
                data = json.loads(session_file.read_text())
                status = SessionStatus(data["status"])
                
                if status == SessionStatus.INTERRUPTED:
                    session = self.restore_session(data["session_id"])
                    if session:
                        interrupted_sessions.append(session)
            
            except Exception as e:
                self.logger.error(f"❌ Error reading session file {session_file}: {e}")
                continue
        
        return interrupted_sessions
    
    def complete_session(self, session_id: str, success: bool = True) -> bool:
        """
        Mark session as completed or failed.
        
        Args:
            session_id: Session ID to complete
            success: Whether execution succeeded (default: True)
        
        Returns:
            True if completed successfully, False otherwise
        """
        session = self.restore_session(session_id)
        if not session:
            return False
        
        session.status = SessionStatus.COMPLETED if success else SessionStatus.FAILED
        session.updated_at = datetime.now()
        
        return self.update_session(session)
    
    def lock_session(self, session_id: str) -> bool:
        """
        Acquire lock on session to prevent concurrent access.
        
        Args:
            session_id: Session ID to lock
        
        Returns:
            True if lock acquired, False otherwise
        """
        lock_file = self.session_dir / f"{session_id}.lock"
        
        try:
            # Create lock file if doesn't exist
            lock_file.touch(exist_ok=True)
            
            # Acquire exclusive lock (non-blocking)
            lock_fd = open(lock_file, 'w')
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            
            # Store lock reference
            self._locks[session_id] = lock_fd
            
            self.logger.debug(f"🔒 Session locked: {session_id}")
            return True
        
        except IOError:
            # Lock already held by another process
            self.logger.warning(f"⚠️  Session already locked: {session_id}")
            return False
        
        except Exception as e:
            self.logger.error(f"❌ Failed to lock session: {e}", exc_info=True)
            return False
    
    def unlock_session(self, session_id: str) -> bool:
        """
        Release lock on session.
        
        Args:
            session_id: Session ID to unlock
        
        Returns:
            True if unlocked successfully, False otherwise
        """
        if session_id not in self._locks:
            return True  # Already unlocked
        
        try:
            lock_fd = self._locks[session_id]
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()
            
            # Remove lock file
            lock_file = self.session_dir / f"{session_id}.lock"
            if lock_file.exists():
                lock_file.unlink()
            
            del self._locks[session_id]
            
            self.logger.debug(f"🔓 Session unlocked: {session_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Failed to unlock session: {e}", exc_info=True)
            return False
    
    def cleanup_stale_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up stale sessions (inactive for max_age_hours).
        
        Args:
            max_age_hours: Maximum age in hours before cleanup (default: 24)
        
        Returns:
            Number of sessions cleaned up
        """
        cleaned = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for session_file in self.session_dir.glob("session-*.json"):
            try:
                data = json.loads(session_file.read_text())
                updated_at = datetime.fromisoformat(data["updated_at"])
                status = SessionStatus(data["status"])
                
                # Clean up old completed/failed sessions
                if status in [SessionStatus.COMPLETED, SessionStatus.FAILED]:
                    if updated_at < cutoff_time:
                        session_file.unlink()
                        cleaned += 1
                        self.logger.debug(f"🗑️  Cleaned up session: {data['session_id']}")
            
            except Exception as e:
                self.logger.error(f"❌ Error cleaning session file {session_file}: {e}")
                continue
        
        if cleaned > 0:
            self.logger.info(f"🗑️  Cleaned up {cleaned} stale sessions")
        
        return cleaned
    
    def _persist_session(self, session: SessionState) -> None:
        """Persist session state to disk."""
        session_file = self.session_dir / f"{session.session_id}.json"
        
        data = {
            "session_id": session.session_id,
            "plan_name": session.plan_name,
            "plan_path": str(session.plan_path),
            "workspace_root": str(session.workspace_root),
            "status": session.status.value,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "current_phase": session.current_phase,
            "completed_phases": session.completed_phases,
            "phase_results": session.phase_results,
            "progress_percent": session.progress_percent,
            "execution_time_seconds": session.execution_time_seconds,
            "checkpoints": session.checkpoints,
            "last_checkpoint_id": session.last_checkpoint_id,
            "errors": session.errors,
            "warnings": session.warnings,
            "execution_mode": session.execution_mode,
            "auto_checkpoint": session.auto_checkpoint,
            "metadata": session.metadata
        }
        
        session_file.write_text(json.dumps(data, indent=2))
