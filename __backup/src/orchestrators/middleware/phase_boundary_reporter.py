"""
Phase Boundary Reporter
=======================
Reports progress only at phase boundaries (SKULL accessibility compliance).

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 3 Task: 3.3
"""

from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum


class PhaseEvent(Enum):
    """Phase lifecycle events"""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PhaseUpdate:
    """Phase update message"""
    phase_name: str
    event: PhaseEvent
    timestamp: str
    message: str
    tasks_completed: int = 0
    tasks_total: int = 0
    metadata: Optional[Dict] = None


class PhaseBoundaryReporter:
    """
    Reports progress only at phase boundaries.
    
    SKULL Compliance:
    - Suppresses mid-phase task updates
    - Reports only at phase start/completion
    - Reduces cognitive load for users
    
    Usage:
        reporter = PhaseBoundaryReporter()
        
        reporter.phase_started("Phase 1", total_tasks=5)
        reporter.task_completed("task1")  # Suppressed
        reporter.task_completed("task2")  # Suppressed
        reporter.phase_completed("Phase 1")  # Reports with summary
    """
    
    def __init__(self):
        """Initialize reporter"""
        self.current_phase: Optional[str] = None
        self.phase_task_count: Dict[str, int] = {}
        self.phase_total_tasks: Dict[str, int] = {}
        self.phase_updates: List[PhaseUpdate] = []
        self.suppressed_task_count: int = 0
    
    def phase_started(self, phase_name: str, total_tasks: int = 0, message: str = "") -> PhaseUpdate:
        """
        Report phase start (ALWAYS reported).
        
        Args:
            phase_name: Name of phase starting
            total_tasks: Expected number of tasks
            message: Optional custom message
            
        Returns:
            PhaseUpdate for the start event
        """
        from datetime import datetime
        
        self.current_phase = phase_name
        self.phase_task_count[phase_name] = 0
        self.phase_total_tasks[phase_name] = total_tasks
        self.suppressed_task_count = 0
        
        update = PhaseUpdate(
            phase_name=phase_name,
            event=PhaseEvent.STARTED,
            timestamp=datetime.now().isoformat(),
            message=message or f"Starting {phase_name}",
            tasks_total=total_tasks
        )
        
        self.phase_updates.append(update)
        return update
    
    def task_completed(self, task_id: str, silent: bool = True) -> Optional[PhaseUpdate]:
        """
        Track task completion (SUPPRESSED by default).
        
        Args:
            task_id: ID of completed task
            silent: If True, suppresses output (default)
            
        Returns:
            None if suppressed, PhaseUpdate otherwise
        """
        if not self.current_phase:
            return None
        
        self.phase_task_count[self.current_phase] = self.phase_task_count.get(self.current_phase, 0) + 1
        
        if silent:
            self.suppressed_task_count += 1
            return None
        
        from datetime import datetime
        update = PhaseUpdate(
            phase_name=self.current_phase,
            event=PhaseEvent.COMPLETED,
            timestamp=datetime.now().isoformat(),
            message=f"Task {task_id} completed",
            tasks_completed=self.phase_task_count[self.current_phase],
            tasks_total=self.phase_total_tasks.get(self.current_phase, 0)
        )
        
        self.phase_updates.append(update)
        return update
    
    def phase_completed(self, phase_name: str, message: str = "") -> PhaseUpdate:
        """
        Report phase completion (ALWAYS reported).
        
        Args:
            phase_name: Name of completed phase
            message: Optional custom message
            
        Returns:
            PhaseUpdate with completion summary
        """
        from datetime import datetime
        
        completed_count = self.phase_task_count.get(phase_name, 0)
        total_count = self.phase_total_tasks.get(phase_name, 0)
        
        default_message = f"Completed {phase_name}"
        if self.suppressed_task_count > 0:
            default_message += f" ({self.suppressed_task_count} task updates suppressed)"
        
        update = PhaseUpdate(
            phase_name=phase_name,
            event=PhaseEvent.COMPLETED,
            timestamp=datetime.now().isoformat(),
            message=message or default_message,
            tasks_completed=completed_count,
            tasks_total=total_count,
            metadata={"suppressed_updates": self.suppressed_task_count}
        )
        
        self.phase_updates.append(update)
        self.current_phase = None
        self.suppressed_task_count = 0
        
        return update
    
    def phase_failed(self, phase_name: str, error: str) -> PhaseUpdate:
        """
        Report phase failure (ALWAYS reported).
        
        Args:
            phase_name: Name of failed phase
            error: Error message
            
        Returns:
            PhaseUpdate with failure details
        """
        from datetime import datetime
        
        completed_count = self.phase_task_count.get(phase_name, 0)
        total_count = self.phase_total_tasks.get(phase_name, 0)
        
        update = PhaseUpdate(
            phase_name=phase_name,
            event=PhaseEvent.FAILED,
            timestamp=datetime.now().isoformat(),
            message=f"Phase failed: {error}",
            tasks_completed=completed_count,
            tasks_total=total_count,
            metadata={"error": error}
        )
        
        self.phase_updates.append(update)
        self.current_phase = None
        
        return update
    
    def get_phase_updates(self, phase_name: Optional[str] = None) -> List[PhaseUpdate]:
        """
        Get all phase updates or filter by phase.
        
        Args:
            phase_name: Optional phase name filter
            
        Returns:
            List of PhaseUpdates
        """
        if phase_name:
            return [u for u in self.phase_updates if u.phase_name == phase_name]
        return self.phase_updates.copy()
    
    def get_suppressed_count(self) -> int:
        """Get count of suppressed task updates"""
        return self.suppressed_task_count
    
    def reset(self) -> None:
        """Clear all state"""
        self.current_phase = None
        self.phase_task_count.clear()
        self.phase_total_tasks.clear()
        self.phase_updates.clear()
        self.suppressed_task_count = 0
