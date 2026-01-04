"""
CORTEX 5.0 Feature Planner - Single-Plan Execution Engine

Purpose: Enhanced feature planner with HTML viewer generation and dual-mode integration.
         Maintains backward compatibility with existing planning system.

Version: 5.0.0
Author: Asif Hussain
Created: January 4, 2026

Features:
- Phase-based progress tracking
- HTML viewer generation
- Integration with existing PlanningOrchestrator
- Backward compatibility with 4.0 feature plans
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PhaseStatus(Enum):
    """Phase execution status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Phase:
    """Represents a single phase in a feature plan."""
    phase_number: int
    phase_name: str
    progress: float = 0.0
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    status_emoji: str = "⏳"
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    tasks_complete: int = 0
    total_tasks: int = 0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "phase_number": self.phase_number,
            "phase_name": self.phase_name,
            "progress": self.progress,
            "status": self.status.value,
            "status_emoji": self.status_emoji,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "tasks_complete": self.tasks_complete,
            "total_tasks": self.total_tasks,
            "start_date": self.start_date,
            "end_date": self.end_date
        }


@dataclass
class FeatureProgressTracker:
    """Feature-level progress tracking data."""
    schema_version: str = "1.0"
    plan_type: str = "feature"
    plan_id: str = ""
    plan_name: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    overall_progress: float = 0.0
    current_phase: int = -1  # -1 for Phase -1, 0+ for regular phases
    total_phases: int = 0
    completed_phases: int = 0
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    status: str = "not_started"
    phases: List[Phase] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "schema_version": self.schema_version,
            "plan_type": self.plan_type,
            "plan_id": self.plan_id,
            "plan_name": self.plan_name,
            "created_date": self.created_date,
            "last_updated": self.last_updated,
            "overall_progress": self.overall_progress,
            "current_phase": self.current_phase,
            "total_phases": self.total_phases,
            "completed_phases": self.completed_phases,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "status": self.status,
            "phases": [p.to_dict() for p in self.phases]
        }


class FeaturePlanner:
    """
    Feature-level planner for single-plan tactical execution.
    
    Responsibilities:
    - Phase-based progress tracking
    - Task completion monitoring
    - HTML viewer generation
    - Integration with Planning Orchestrator 4.0
    """
    
    def __init__(self, feature_path: Path):
        """
        Initialize feature planner.
        
        Args:
            feature_path: Path to feature plan root directory
        """
        self.feature_path = feature_path
        self.tracking_dir = feature_path / "tracking"
        self.tracker_file = self.tracking_dir / "progress-tracker.json"
        
        # Create tracking directory if needed
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing tracker or create new
        self.tracker = self._load_or_create_tracker()
    
    def _load_or_create_tracker(self) -> FeatureProgressTracker:
        """Load existing progress tracker or create new one."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file) as f:
                    data = json.load(f)
                return self._deserialize_tracker(data)
            except Exception as e:
                logger.error(f"Failed to load tracker: {e}")
                return FeatureProgressTracker()
        else:
            return FeatureProgressTracker()
    
    def _deserialize_tracker(self, data: Dict) -> FeatureProgressTracker:
        """Deserialize JSON data to FeatureProgressTracker."""
        # Deserialize phases
        phases = []
        for p_data in data.get("phases", []):
            phase = Phase(
                phase_number=p_data["phase_number"],
                phase_name=p_data["phase_name"],
                progress=p_data.get("progress", 0.0),
                status=PhaseStatus(p_data.get("status", "not_started")),
                status_emoji=p_data.get("status_emoji", "⏳"),
                estimated_hours=p_data.get("estimated_hours", 0.0),
                actual_hours=p_data.get("actual_hours", 0.0),
                tasks_complete=p_data.get("tasks_complete", 0),
                total_tasks=p_data.get("total_tasks", 0),
                start_date=p_data.get("start_date"),
                end_date=p_data.get("end_date")
            )
            phases.append(phase)
        
        return FeatureProgressTracker(
            schema_version=data.get("schema_version", "1.0"),
            plan_type=data.get("plan_type", "feature"),
            plan_id=data.get("plan_id", ""),
            plan_name=data.get("plan_name", ""),
            created_date=data.get("created_date", ""),
            last_updated=data.get("last_updated", ""),
            overall_progress=data.get("overall_progress", 0.0),
            current_phase=data.get("current_phase", -1),
            total_phases=data.get("total_phases", 0),
            completed_phases=data.get("completed_phases", 0),
            estimated_hours=data.get("estimated_hours", 0.0),
            actual_hours=data.get("actual_hours", 0.0),
            status=data.get("status", "not_started"),
            phases=phases
        )
    
    def save_tracker(self) -> None:
        """Save progress tracker to disk."""
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump(self.tracker.to_dict(), f, indent=2)
            logger.info(f"Saved feature tracker: {self.tracker_file}")
        except Exception as e:
            logger.error(f"Failed to save tracker: {e}")
            raise
    
    def add_phase(self, phase: Phase) -> None:
        """
        Add a phase to the feature plan.
        
        Args:
            phase: Phase instance to add
        """
        # Check for duplicate phase number
        existing_numbers = [p.phase_number for p in self.tracker.phases]
        if phase.phase_number in existing_numbers:
            raise ValueError(f"Phase {phase.phase_number} already exists")
        
        self.tracker.phases.append(phase)
        self.tracker.total_phases = len(self.tracker.phases)
        self.tracker.estimated_hours += phase.estimated_hours
        self._recalculate_progress()
        logger.info(f"Added phase: {phase.phase_number} - {phase.phase_name}")
    
    def update_phase_progress(
        self,
        phase_number: int,
        progress: float,
        tasks_complete: Optional[int] = None,
        actual_hours: Optional[float] = None
    ) -> None:
        """
        Update progress for a phase.
        
        Args:
            phase_number: Phase number to update
            progress: New progress percentage (0-100)
            tasks_complete: Optional number of completed tasks
            actual_hours: Optional actual hours spent
        """
        phase = self._get_phase(phase_number)
        if not phase:
            raise ValueError(f"Phase {phase_number} not found")
        
        phase.progress = max(0.0, min(100.0, progress))
        
        if tasks_complete is not None:
            phase.tasks_complete = tasks_complete
        
        if actual_hours is not None:
            phase.actual_hours = actual_hours
        
        # Update status based on progress
        if phase.progress == 0:
            phase.status = PhaseStatus.NOT_STARTED
            phase.status_emoji = "⏳"
        elif phase.progress == 100:
            phase.status = PhaseStatus.COMPLETE
            phase.status_emoji = "✅"
            phase.end_date = datetime.now().isoformat()
        elif phase.status == PhaseStatus.NOT_STARTED:
            phase.status = PhaseStatus.IN_PROGRESS
            phase.status_emoji = "🔄"
            if not phase.start_date:
                phase.start_date = datetime.now().isoformat()
        
        self._recalculate_progress()
        logger.info(f"Updated phase {phase_number} progress: {progress}%")
    
    def _get_phase(self, phase_number: int) -> Optional[Phase]:
        """Get phase by number."""
        for phase in self.tracker.phases:
            if phase.phase_number == phase_number:
                return phase
        return None
    
    def _recalculate_progress(self) -> None:
        """Recalculate aggregate progress metrics."""
        if not self.tracker.phases:
            self.tracker.overall_progress = 0.0
            self.tracker.completed_phases = 0
            self.tracker.status = "not_started"
            return
        
        # Overall progress (average of all phases)
        total_progress = sum(p.progress for p in self.tracker.phases)
        self.tracker.overall_progress = round(
            total_progress / len(self.tracker.phases), 1
        )
        
        # Completed phases count
        self.tracker.completed_phases = sum(
            1 for p in self.tracker.phases
            if p.status == PhaseStatus.COMPLETE
        )
        
        # Actual hours total
        self.tracker.actual_hours = sum(p.actual_hours for p in self.tracker.phases)
        
        # Current phase (first non-complete phase)
        self.tracker.current_phase = -1  # Default to Phase -1
        for phase in sorted(self.tracker.phases, key=lambda p: p.phase_number):
            if phase.status != PhaseStatus.COMPLETE:
                self.tracker.current_phase = phase.phase_number
                break
        
        # Overall status
        if self.tracker.completed_phases == self.tracker.total_phases:
            self.tracker.status = "complete"
        elif any(p.status == PhaseStatus.FAILED for p in self.tracker.phases):
            self.tracker.status = "failed"
        elif any(p.status == PhaseStatus.IN_PROGRESS for p in self.tracker.phases):
            self.tracker.status = "in_progress"
        elif any(p.status == PhaseStatus.PAUSED for p in self.tracker.phases):
            self.tracker.status = "paused"
        elif self.tracker.completed_phases > 0:
            self.tracker.status = "in_progress"
        else:
            self.tracker.status = "not_started"
        
        # Update timestamp
        self.tracker.last_updated = datetime.now().isoformat()
    
    def start_phase(self, phase_number: int) -> None:
        """
        Start a phase (mark as in progress).
        
        Args:
            phase_number: Phase number to start
        """
        phase = self._get_phase(phase_number)
        if not phase:
            raise ValueError(f"Phase {phase_number} not found")
        
        if phase.status == PhaseStatus.COMPLETE:
            logger.warning(f"Phase {phase_number} already complete")
            return
        
        phase.status = PhaseStatus.IN_PROGRESS
        phase.status_emoji = "🔄"
        if not phase.start_date:
            phase.start_date = datetime.now().isoformat()
        
        self.tracker.current_phase = phase_number
        self._recalculate_progress()
        self.save_tracker()
        logger.info(f"Started phase {phase_number}: {phase.phase_name}")
    
    def complete_phase(self, phase_number: int) -> None:
        """
        Mark a phase as complete.
        
        Args:
            phase_number: Phase number to complete
        """
        self.update_phase_progress(phase_number, 100.0)
        logger.info(f"Completed phase {phase_number}")
    
    def get_next_phase(self) -> Optional[Phase]:
        """
        Get the next phase to execute (first non-complete phase).
        
        Returns:
            Next Phase instance or None if all complete
        """
        for phase in sorted(self.tracker.phases, key=lambda p: p.phase_number):
            if phase.status != PhaseStatus.COMPLETE:
                return phase
        return None
    
    def initialize_from_plan_data(self, plan_data: Dict) -> None:
        """
        Initialize feature tracker from existing plan data.
        
        Useful for migrating from Planning Orchestrator 4.0 plans.
        
        Args:
            plan_data: Dictionary containing plan metadata and phases
        """
        # Set metadata
        self.tracker.plan_id = plan_data.get("metadata", {}).get("plan_id", "")
        self.tracker.plan_name = plan_data.get("metadata", {}).get("title", "")
        self.tracker.estimated_hours = plan_data.get("metadata", {}).get("estimated_hours", 0.0)
        
        # Add phases
        for phase_data in plan_data.get("phases", []):
            phase = Phase(
                phase_number=phase_data.get("phase_number", 0),
                phase_name=phase_data.get("phase_name", ""),
                estimated_hours=phase_data.get("estimated_hours", 0.0),
                total_tasks=len(phase_data.get("tasks", []))
            )
            self.add_phase(phase)
        
        self.save_tracker()
        logger.info(f"Initialized feature tracker from plan data: {self.tracker.plan_id}")


# Export public API
__all__ = [
    "FeaturePlanner",
    "Phase",
    "FeatureProgressTracker",
    "PhaseStatus"
]
