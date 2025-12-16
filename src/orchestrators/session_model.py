"""
Unified Session Model for CORTEX Orchestrators

Provides type-safe, consistent state management across all orchestrators.

Version: 1.0.0 (Extracted from archive)
Author: Asif Hussain
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class SessionStatus(Enum):
    """Standard session statuses across all orchestrators."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    AWAITING_APPROVAL = "awaiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    def is_active(self) -> bool:
        """Check if session is in active state."""
        return self in [SessionStatus.IN_PROGRESS, SessionStatus.AWAITING_APPROVAL]
    
    def is_terminal(self) -> bool:
        """Check if session is in terminal state."""
        return self in [SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.CANCELLED]


@dataclass
class BaseSession:
    """Base session model for all orchestrators."""
    session_id: str
    session_type: str
    status: SessionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Convert string status to enum if needed."""
        if isinstance(self.status, str):
            self.status = SessionStatus(self.status)
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        return data
    
    def complete(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark session as completed."""
        self.completed_at = datetime.now()
        if success:
            self.status = SessionStatus.COMPLETED
        else:
            self.status = SessionStatus.FAILED
            self.error_message = error_message


@dataclass
class PlanningSession(BaseSession):
    """Planning-specific session state."""
    plan_id: str = ""
    plan_title: str = ""
    plan_path: Optional[str] = None
    planning_mode_active: bool = False
    dor_items: List[str] = field(default_factory=list)
    dod_items: List[str] = field(default_factory=list)
    phases: List[Dict[str, Any]] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    approved: bool = False
    
    def __post_init__(self):
        """Initialize planning session."""
        super().__post_init__()
        self.session_type = "planning"
