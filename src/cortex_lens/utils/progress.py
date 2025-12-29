"""
Progress Reporter for CORTEX Lens

User-facing progress updates to prevent "hung application" perception.
Provides real-time feedback during long-running operations.

Author: Asif Hussain
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Callable, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProgressPhase:
    """Single phase of work with progress tracking."""
    id: str
    name: str
    total_work: int
    completed_work: int = 0
    
    @property
    def percent(self) -> float:
        """Calculate completion percentage."""
        if self.total_work == 0:
            return 100.0
        return (self.completed_work / self.total_work) * 100


class ProgressReporter:
    """
    Multi-phase progress reporter with ETA calculation.
    
    Features:
    - Multi-phase tracking (Phase 1/6, Phase 2/6, etc.)
    - Sub-task visibility (current operation)
    - ETA calculation based on actual progress
    - Completion summary with metrics
    
    Example CLI Output:
        🔍 Scanning repository structure...
        📊 Detected 1,247 files
        ⏱️  Estimated analysis time: ~3m 45s
        💻 Using 7 parallel workers
        
        🔍 Repository Analysis: [1/6] 16.7% | ETA: 3m 12s | Classifying repository type
        🔍 Repository Analysis: [2/6] 33.3% | ETA: 2m 18s | health: Completed 3/5
        🔍 Repository Analysis: [3/6] 50.0% | ETA: 1m 45s | Analyzing Python files (batch 15/40)
        ✅ Repository Analysis: Complete in 3m 42s
    """
    
    def __init__(
        self,
        operation_name: str,
        total_phases: int,
        callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize progress reporter.
        
        Args:
            operation_name: Name of overall operation (e.g., "Repository Analysis")
            total_phases: Total number of phases
            callback: Optional callback for progress updates (receives formatted string)
        """
        self.operation_name = operation_name
        self.total_phases = total_phases
        self.callback = callback or self._default_callback
        
        self.phases: list[ProgressPhase] = []
        self.current_phase_index: int = 0
        self.start_time: datetime = datetime.now()
        self.last_update_time: datetime = datetime.now()
        
        self._update_interval_seconds = 1.0  # Min time between updates
    
    def start_phase(self, phase_id: str, phase_name: str, total_work: int):
        """
        Start a new phase.
        
        Args:
            phase_id: Unique phase identifier
            phase_name: Human-readable phase name
            total_work: Total work units in this phase
        """
        phase = ProgressPhase(phase_id, phase_name, total_work)
        self.phases.append(phase)
        self.current_phase_index = len(self.phases) - 1
        
        self._report_progress(f"Starting: {phase_name}")
    
    def update_phase(
        self,
        work_completed: int = 1,
        current_task: Optional[str] = None
    ):
        """
        Update current phase progress.
        
        Args:
            work_completed: Work units completed (incremental)
            current_task: Optional description of current task
        """
        if not self.phases:
            return
        
        phase = self.phases[self.current_phase_index]
        phase.completed_work += work_completed
        phase.completed_work = min(phase.completed_work, phase.total_work)
        
        # Throttle updates
        now = datetime.now()
        if (now - self.last_update_time).total_seconds() < self._update_interval_seconds:
            return
        
        self.last_update_time = now
        
        # Build progress message
        overall_percent = self._calculate_overall_progress()
        eta = self._calculate_eta()
        
        parts = [
            f"[{self.current_phase_index + 1}/{self.total_phases}]",
            f"{overall_percent:.1f}%"
        ]
        
        if eta:
            parts.append(f"ETA: {eta}")
        
        if current_task:
            parts.append(current_task)
        
        message = " | ".join(parts)
        self._report_progress(message)
    
    def complete_phase(self):
        """Mark current phase as complete."""
        if not self.phases:
            return
        
        phase = self.phases[self.current_phase_index]
        phase.completed_work = phase.total_work
        
        self._report_progress(f"Completed: {phase.name}")
    
    def complete(self, summary: Optional[str] = None):
        """
        Mark entire operation as complete.
        
        Args:
            summary: Optional completion summary
        """
        elapsed = datetime.now() - self.start_time
        elapsed_str = self._format_duration(elapsed)
        
        message = f"Complete in {elapsed_str}"
        if summary:
            message = f"{message} | {summary}"
        
        self.callback(f"✅ {self.operation_name}: {message}")
    
    def _calculate_overall_progress(self) -> float:
        """Calculate overall progress across all phases."""
        if not self.phases:
            return 0.0
        
        completed_phases = sum(1 for p in self.phases if p.completed_work >= p.total_work)
        current_phase = self.phases[self.current_phase_index]
        current_phase_progress = current_phase.percent / 100
        
        overall = (completed_phases + current_phase_progress) / self.total_phases * 100
        return min(overall, 100.0)
    
    def _calculate_eta(self) -> Optional[str]:
        """
        Calculate estimated time remaining.
        
        Returns:
            ETA string (e.g., "2m 15s") or None if not enough data
        """
        overall_progress = self._calculate_overall_progress()
        if overall_progress < 1:
            return None
        
        elapsed = datetime.now() - self.start_time
        elapsed_seconds = elapsed.total_seconds()
        
        # Estimate total time based on current progress
        total_estimated_seconds = elapsed_seconds / (overall_progress / 100)
        remaining_seconds = total_estimated_seconds - elapsed_seconds
        
        if remaining_seconds < 0:
            return None
        
        return self._format_duration(timedelta(seconds=remaining_seconds))
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format duration as human-readable string."""
        seconds = int(duration.total_seconds())
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _report_progress(self, message: str):
        """Send progress update to callback."""
        full_message = f"🔍 {self.operation_name}: {message}"
        self.callback(full_message)
    
    def _default_callback(self, message: str):
        """Default callback logs to console."""
        print(message, flush=True)
        logger.info(message)


# Convenience function for simple progress tracking
def track_progress(
    items: list,
    operation_name: str = "Processing",
    process_func: Optional[Callable[[Any], Any]] = None
) -> list:
    """
    Track progress while processing a list of items.
    
    Args:
        items: List of items to process
        operation_name: Name of operation
        process_func: Optional function to apply to each item
    
    Returns:
        Processed items (or original if no process_func)
    
    Example:
        results = track_progress(files, "Analyzing Files", analyze_file)
    """
    reporter = ProgressReporter(operation_name, total_phases=1)
    reporter.start_phase("process", "Processing items", len(items))
    
    results = []
    for i, item in enumerate(items):
        result = process_func(item) if process_func else item
        results.append(result)
        reporter.update_phase(1, f"Item {i+1}/{len(items)}")
    
    reporter.complete_phase()
    reporter.complete()
    
    return results
