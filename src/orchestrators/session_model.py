"""
Unified Session Model for CORTEX Orchestrators

Provides type-safe, consistent state management across all orchestrators.
Eliminates Dict-based state management issues.

Version: 1.0.0
Author: Asif Hussain
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import uuid


# ============================================================================
# Session Status Enumeration
# ============================================================================

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


# ============================================================================
# Base Session Model
# ============================================================================

@dataclass
class BaseSession:
    """
    Base session model for all orchestrators.
    
    Provides common fields and serialization for all session types.
    """
    session_id: str
    session_type: str  # "tdd", "planning", "execution", "git_checkpoint"
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
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseSession':
        """Deserialize from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseSession':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def complete(self, success: bool = True, error_message: Optional[str] = None) -> None:
        """Mark session as completed."""
        self.completed_at = datetime.now()
        if success:
            self.status = SessionStatus.COMPLETED
        else:
            self.status = SessionStatus.FAILED
            self.error_message = error_message
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel session."""
        self.completed_at = datetime.now()
        self.status = SessionStatus.CANCELLED
        if reason:
            self.metadata["cancellation_reason"] = reason
    
    def pause(self) -> None:
        """Pause session."""
        self.status = SessionStatus.PAUSED
        self.metadata["paused_at"] = datetime.now().isoformat()
    
    def resume(self) -> None:
        """Resume paused session."""
        self.status = SessionStatus.IN_PROGRESS
        if "paused_at" in self.metadata:
            self.metadata["resumed_at"] = datetime.now().isoformat()


# ============================================================================
# TDD Session Model
# ============================================================================

class TDDPhase(Enum):
    """TDD workflow phases."""
    NOT_STARTED = "not_started"
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"
    COMPLETED = "completed"


@dataclass
class TDDSession(BaseSession):
    """
    TDD-specific session state.
    
    Tracks RED→GREEN→REFACTOR workflow, test/implementation files,
    checkpoints, and metrics.
    """
    feature_name: str = ""
    current_phase: TDDPhase = TDDPhase.NOT_STARTED
    phase_history: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: List[str] = field(default_factory=list)
    test_scope: List[str] = field(default_factory=list)
    implementation_scope: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    auto_debug_enabled: bool = True
    performance_refactoring_enabled: bool = True
    
    def __post_init__(self):
        """Initialize TDD session."""
        super().__post_init__()
        self.session_type = "tdd"
        if isinstance(self.current_phase, str):
            self.current_phase = TDDPhase(self.current_phase)
    
    def transition_to_phase(self, phase: TDDPhase, checkpoint_id: Optional[str] = None) -> None:
        """
        Transition to new TDD phase.
        
        Args:
            phase: Target phase
            checkpoint_id: Optional git checkpoint ID
        """
        old_phase = self.current_phase
        self.current_phase = phase
        
        # Record transition
        self.phase_history.append({
            "from_phase": old_phase.value,
            "to_phase": phase.value,
            "timestamp": datetime.now().isoformat(),
            "checkpoint_id": checkpoint_id
        })
        
        if checkpoint_id:
            self.checkpoints.append(checkpoint_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize with TDD-specific fields."""
        data = super().to_dict()
        data["current_phase"] = self.current_phase.value
        return data


# ============================================================================
# Planning Session Model
# ============================================================================

@dataclass
class PlanningSession(BaseSession):
    """
    Planning-specific session state.
    
    Tracks interactive planning workflow, DoR/DoD, phases, and validation.
    """
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
    
    def add_phase(self, phase_name: str, tasks: List[Dict[str, Any]]) -> None:
        """Add phase to plan."""
        self.phases.append({
            "name": phase_name,
            "tasks": tasks,
            "added_at": datetime.now().isoformat()
        })
    
    def validate_plan(self) -> bool:
        """
        Validate plan completeness.
        
        Returns:
            True if valid, False otherwise
        """
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # Check required fields
        if not self.plan_title:
            self.validation_errors.append("Plan title is required")
        
        if not self.phases:
            self.validation_errors.append("Plan must have at least one phase")
        
        if not self.dor_items:
            self.validation_warnings.append("Definition of Ready is empty")
        
        if not self.dod_items:
            self.validation_warnings.append("Definition of Done is empty")
        
        return len(self.validation_errors) == 0
    
    def approve(self) -> None:
        """Approve plan for execution."""
        if not self.validate_plan():
            raise ValueError(f"Cannot approve invalid plan: {self.validation_errors}")
        
        self.approved = True
        self.metadata["approved_at"] = datetime.now().isoformat()


# ============================================================================
# Execution Session Model
# ============================================================================

class ExecutionMode(Enum):
    """Execution modes."""
    APPROVAL_GATED = "approval_gated"  # Require approval per phase
    AUTONOMOUS = "autonomous"  # Execute all phases without approval
    DRY_RUN = "dry_run"  # Validate without executing


@dataclass
class PhaseExecution:
    """Single phase execution record."""
    phase_name: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.IN_PROGRESS
    tasks_completed: int = 0
    tasks_failed: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "phase_name": self.phase_name,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "error_message": self.error_message
        }


@dataclass
class ExecutionSession(BaseSession):
    """
    Execution-specific session state.
    
    Tracks plan execution progress, phase completion, approval gates.
    """
    plan_path: str = ""
    execution_mode: ExecutionMode = ExecutionMode.APPROVAL_GATED
    phases_executed: List[PhaseExecution] = field(default_factory=list)
    awaiting_approval: bool = False
    current_phase_index: int = 0
    total_phases: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    
    def __post_init__(self):
        """Initialize execution session."""
        super().__post_init__()
        self.session_type = "execution"
        if isinstance(self.execution_mode, str):
            self.execution_mode = ExecutionMode(self.execution_mode)
    
    def start_phase(self, phase_name: str) -> PhaseExecution:
        """
        Start executing a phase.
        
        Args:
            phase_name: Phase name
            
        Returns:
            PhaseExecution record
        """
        phase_exec = PhaseExecution(
            phase_name=phase_name,
            started_at=datetime.now()
        )
        self.phases_executed.append(phase_exec)
        return phase_exec
    
    def complete_phase(self, success: bool, error_message: Optional[str] = None) -> None:
        """Complete current phase."""
        if not self.phases_executed:
            return
        
        current_phase = self.phases_executed[-1]
        current_phase.completed_at = datetime.now()
        current_phase.status = SessionStatus.COMPLETED if success else SessionStatus.FAILED
        
        if error_message:
            current_phase.error_message = error_message
        
        # Update counters
        self.total_tasks_completed += current_phase.tasks_completed
        self.total_tasks_failed += current_phase.tasks_failed
        self.current_phase_index += 1
    
    def request_approval(self) -> None:
        """Request user approval before continuing."""
        self.awaiting_approval = True
        self.status = SessionStatus.AWAITING_APPROVAL
    
    def grant_approval(self) -> None:
        """Grant approval to continue."""
        self.awaiting_approval = False
        self.status = SessionStatus.IN_PROGRESS
    
    def get_progress_percentage(self) -> float:
        """
        Calculate execution progress.
        
        Returns:
            Progress percentage (0-100)
        """
        if self.total_phases == 0:
            return 0.0
        return (self.current_phase_index / self.total_phases) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize with execution-specific fields."""
        data = super().to_dict()
        data["execution_mode"] = self.execution_mode.value
        data["phases_executed"] = [p.to_dict() for p in self.phases_executed]
        data["progress_percentage"] = self.get_progress_percentage()
        return data


# ============================================================================
# Git Checkpoint Session Model
# ============================================================================

@dataclass
class GitCheckpointSession(BaseSession):
    """
    Git checkpoint session state.
    
    Tracks git operations, commits, branches.
    """
    branch_name: str = ""
    commit_message: str = ""
    commit_sha: Optional[str] = None
    files_changed: List[str] = field(default_factory=list)
    rollback_available: bool = True
    
    def __post_init__(self):
        """Initialize git checkpoint session."""
        super().__post_init__()
        self.session_type = "git_checkpoint"
    
    def record_commit(self, commit_sha: str, files_changed: List[str]) -> None:
        """Record git commit."""
        self.commit_sha = commit_sha
        self.files_changed = files_changed
        self.metadata["committed_at"] = datetime.now().isoformat()


# ============================================================================
# Session Factory
# ============================================================================

class SessionFactory:
    """Factory for creating typed sessions."""
    
    @staticmethod
    def create_tdd_session(feature_name: str) -> TDDSession:
        """Create TDD session."""
        return TDDSession(
            session_id=uuid.uuid4().hex,
            session_type="tdd",
            status=SessionStatus.NOT_STARTED,
            started_at=datetime.now(),
            feature_name=feature_name
        )
    
    @staticmethod
    def create_planning_session(plan_title: str) -> PlanningSession:
        """Create planning session."""
        return PlanningSession(
            session_id=uuid.uuid4().hex,
            session_type="planning",
            status=SessionStatus.IN_PROGRESS,
            started_at=datetime.now(),
            plan_title=plan_title,
            planning_mode_active=True
        )
    
    @staticmethod
    def create_execution_session(
        plan_path: str,
        mode: ExecutionMode = ExecutionMode.APPROVAL_GATED
    ) -> ExecutionSession:
        """Create execution session."""
        return ExecutionSession(
            session_id=uuid.uuid4().hex,
            session_type="execution",
            status=SessionStatus.IN_PROGRESS,
            started_at=datetime.now(),
            plan_path=plan_path,
            execution_mode=mode
        )
    
    @staticmethod
    def create_git_checkpoint_session(commit_message: str) -> GitCheckpointSession:
        """Create git checkpoint session."""
        return GitCheckpointSession(
            session_id=uuid.uuid4().hex,
            session_type="git_checkpoint",
            status=SessionStatus.IN_PROGRESS,
            started_at=datetime.now(),
            commit_message=commit_message
        )


# ============================================================================
# Export Public API
# ============================================================================

__all__ = [
    # Enums
    "SessionStatus",
    "TDDPhase",
    "ExecutionMode",
    
    # Base models
    "BaseSession",
    
    # Session types
    "TDDSession",
    "PlanningSession",
    "ExecutionSession",
    "GitCheckpointSession",
    
    # Supporting models
    "PhaseExecution",
    
    # Factory
    "SessionFactory",
]
