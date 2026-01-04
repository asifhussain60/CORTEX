"""
Progress Tracker - Unified progress tracking for orchestrators

Manages JSON-based progress state with automatic percentage calculation,
phase transition tracking, and milestone detection.

Author: Asif Hussain
Version: 1.0.0
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class ProgressState(Enum):
    """Progress states for phases and plans."""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    DEFERRED = "deferred"


@dataclass
class PhaseProgress:
    """Progress tracking for a single phase."""
    phase_number: int
    phase_name: str
    status: ProgressState
    progress_percentage: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: List[int] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)
    tasks_completed: int = 0
    tasks_total: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enum serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PhaseProgress':
        """Create from dictionary with enum deserialization."""
        data['status'] = ProgressState(data['status'])
        return cls(**data)


@dataclass
class PlanProgress:
    """Progress tracking for entire plan (epic or feature)."""
    plan_id: str
    plan_name: str
    plan_type: str  # "epic" or "feature"
    overall_progress: int = 0
    status: ProgressState = ProgressState.NOT_STARTED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    phases: List[PhaseProgress] = field(default_factory=list)
    child_plans: List['PlanProgress'] = field(default_factory=list)
    
    total_phases: int = 0
    completed_phases: int = 0
    estimated_duration_days: int = 0
    actual_duration_days: int = 0
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        data['phases'] = [p.to_dict() for p in self.phases]
        data['child_plans'] = [c.to_dict() for c in self.child_plans]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanProgress':
        """Create from dictionary with nested object reconstruction."""
        data['status'] = ProgressState(data['status'])
        data['phases'] = [PhaseProgress.from_dict(p) for p in data.get('phases', [])]
        data['child_plans'] = [cls.from_dict(c) for c in data.get('child_plans', [])]
        return cls(**data)


class ProgressTracker:
    """
    Unified progress tracker for planning and ADO orchestrators.
    
    Features:
    - Automatic percentage calculation
    - Phase dependency validation
    - Epic/feature mode support
    - JSON persistence
    - Real-time updates for HTML viewer
    """
    
    def __init__(self, tracking_file: Path, plan_type: str = "feature"):
        """
        Initialize progress tracker.
        
        Args:
            tracking_file: Path to progress-tracker.json
            plan_type: "epic" or "feature"
        """
        self.tracking_file = tracking_file
        self.plan_type = plan_type
        self.progress = self._load_or_create()
    
    def _load_or_create(self) -> PlanProgress:
        """Load existing progress or create new tracker."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return PlanProgress.from_dict(data)
            except Exception as e:
                logger.error(f"Failed to load progress tracker: {e}")
                return self._create_empty_progress()
        else:
            return self._create_empty_progress()
    
    def _create_empty_progress(self) -> PlanProgress:
        """Create empty progress structure."""
        plan_id = self.tracking_file.parent.parent.name
        return PlanProgress(
            plan_id=plan_id,
            plan_name=plan_id.replace('-', ' ').title(),
            plan_type=self.plan_type
        )
    
    def add_phase(self, phase: PhaseProgress) -> None:
        """Add a phase to tracking."""
        self.progress.phases.append(phase)
        self.progress.total_phases = len(self.progress.phases)
        self._recalculate_progress()
        self.save()
    
    def update_phase(
        self,
        phase_number: int,
        status: Optional[ProgressState] = None,
        progress: Optional[int] = None,
        tasks_completed: Optional[int] = None
    ) -> None:
        """Update phase progress."""
        for phase in self.progress.phases:
            if phase.phase_number == phase_number:
                if status:
                    phase.status = status
                    if status == ProgressState.IN_PROGRESS and not phase.started_at:
                        phase.started_at = datetime.now().isoformat()
                    elif status == ProgressState.COMPLETED and not phase.completed_at:
                        phase.completed_at = datetime.now().isoformat()
                        phase.progress_percentage = 100
                
                if progress is not None:
                    phase.progress_percentage = progress
                
                if tasks_completed is not None:
                    phase.tasks_completed = tasks_completed
                
                break
        
        self._recalculate_progress()
        self.save()
    
    def _recalculate_progress(self) -> None:
        """Recalculate overall progress percentage."""
        if not self.progress.phases:
            self.progress.overall_progress = 0
            return
        
        total_progress = sum(p.progress_percentage for p in self.progress.phases)
        self.progress.overall_progress = total_progress // len(self.progress.phases)
        
        # Count completed phases
        self.progress.completed_phases = sum(
            1 for p in self.progress.phases 
            if p.status == ProgressState.COMPLETED
        )
        
        # Update plan status
        if self.progress.completed_phases == 0:
            self.progress.status = ProgressState.NOT_STARTED
        elif self.progress.completed_phases == self.progress.total_phases:
            self.progress.status = ProgressState.COMPLETED
            if not self.progress.completed_at:
                self.progress.completed_at = datetime.now().isoformat()
        else:
            self.progress.status = ProgressState.IN_PROGRESS
            if not self.progress.started_at:
                self.progress.started_at = datetime.now().isoformat()
    
    def add_child_plan(self, child_progress: PlanProgress) -> None:
        """Add child plan (for epic mode)."""
        self.progress.child_plans.append(child_progress)
        self.save()
    
    def get_phase(self, phase_number: int) -> Optional[PhaseProgress]:
        """Get phase by number."""
        for phase in self.progress.phases:
            if phase.phase_number == phase_number:
                return phase
        return None
    
    def get_blocked_phases(self) -> List[PhaseProgress]:
        """Get all blocked phases."""
        return [p for p in self.progress.phases if p.status == ProgressState.BLOCKED]
    
    def get_next_phase(self) -> Optional[PhaseProgress]:
        """Get next phase to execute (first not started/in progress)."""
        for phase in sorted(self.progress.phases, key=lambda p: p.phase_number):
            if phase.status in [ProgressState.NOT_STARTED, ProgressState.IN_PROGRESS]:
                return phase
        return None
    
    def validate_dependencies(self, phase_number: int) -> tuple[bool, List[str]]:
        """
        Validate phase dependencies are met.
        
        Returns:
            (is_valid, blocking_phases)
        """
        phase = self.get_phase(phase_number)
        if not phase or not phase.dependencies:
            return (True, [])
        
        blocking = []
        for dep_num in phase.dependencies:
            dep_phase = self.get_phase(dep_num)
            if dep_phase and dep_phase.status != ProgressState.COMPLETED:
                blocking.append(f"Phase {dep_num}: {dep_phase.phase_name}")
        
        return (len(blocking) == 0, blocking)
    
    def save(self) -> None:
        """Save progress to JSON file."""
        self.progress.updated_at = datetime.now().isoformat()
        
        # Ensure tracking directory exists
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON with pretty formatting
        with open(self.tracking_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Progress saved to {self.tracking_file}")
    
    def get_progress_bar(self, width: int = 10) -> str:
        """
        Generate ASCII progress bar.
        
        Args:
            width: Number of characters in bar
        
        Returns:
            Progress bar string (e.g., "████░░░░░░")
        """
        filled = int((self.progress.overall_progress / 100) * width)
        empty = width - filled
        return "█" * filled + "░" * empty
    
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary for reporting."""
        return {
            "plan_id": self.progress.plan_id,
            "plan_name": self.progress.plan_name,
            "overall_progress": self.progress.overall_progress,
            "status": self.progress.status.value,
            "completed_phases": self.progress.completed_phases,
            "total_phases": self.progress.total_phases,
            "progress_bar": self.get_progress_bar(),
            "started_at": self.progress.started_at,
            "completed_at": self.progress.completed_at,
        }
