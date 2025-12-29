"""
Progress Synchronizer Utility

Purpose: Automatically updates master plans and sub-plans after phase completion,
         maintaining accurate visual progress trackers, elapsed time, and next steps.

Evidence:
- PrevalidationWS: 55 minutes wasted on manual progress updates (11 phases × 5 min)
- Manual updates error-prone (typos, wrong percentages, missed updates)
- Inconsistent visual trackers across plans

Integration:
- Called by orchestrators after phase completion
- Updates markdown files atomically (temp → rename)
- Synchronizes master + all referenced sub-plans

Author: Asif Hussain
Date: December 13, 2025
Version: 1.0.0
Phase: CORTEX Orchestration + AST Enhancement - Phase 2
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import tempfile
import shutil


logger = logging.getLogger(__name__)


class PhaseStatus(str, Enum):
    """Phase status indicators"""
    NOT_STARTED = "⏳ Not Started"
    IN_PROGRESS = "🚧 In Progress"
    COMPLETE = "✅ Complete"
    BLOCKED = "⚠️ Blocked"


@dataclass
class PhaseInfo:
    """Information about a single phase"""
    phase_id: str
    phase_number: int
    phase_name: str
    status: PhaseStatus
    progress_percent: int = 0
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    elapsed_time: Optional[timedelta] = None


@dataclass
class ProgressTrackerInfo:
    """Complete progress tracker information"""
    phases: List[PhaseInfo]
    overall_progress_percent: int
    total_phases: int
    completed_phases: int
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    total_elapsed_time: Optional[timedelta] = None


class MarkdownParser:
    """
    Parses markdown files to extract progress tracker sections.
    Preserves markdown structure during updates.
    """
    
    PROGRESS_TRACKER_PATTERN = r'```\s*\n[━=─]+\s*\n.*?\n[━=─]+\s*\n(.*?)\n[━=─].*?```'
    PHASE_LINE_PATTERN = r'(PHASE \d+:.*?)\s*\[([█░\s]*)\]\s*(\d+)%\s*(⏳|🚧|✅|⚠️)\s*(.*?)$'
    OVERALL_PROGRESS_PATTERN = r'OVERALL PROGRESS:\s*([█░]+)\s*(\d+)/(\d+)\s+Phases\s*\((\d+)%\)'
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.tracker_section = ""
        self.tracker_start_idx = -1
        self.tracker_end_idx = -1
    
    def load(self) -> bool:
        """Load markdown file content"""
        try:
            if not self.file_path.exists():
                logger.error(f"File not found: {self.file_path}")
                return False
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            return True
        except Exception as e:
            logger.error(f"Error loading file {self.file_path}: {e}")
            return False
    
    def extract_progress_tracker(self) -> Optional[ProgressTrackerInfo]:
        """Extract progress tracker information from markdown"""
        # More flexible pattern that matches different separator styles
        match = re.search(
            r'```\s*\n[━═─=]+.*?\n(.*?)```',
            self.content,
            re.DOTALL | re.MULTILINE
        )
        
        if not match:
            logger.warning(f"No progress tracker found in {self.file_path}")
            return None
        
        self.tracker_section = match.group(0)
        self.tracker_start_idx = match.start()
        self.tracker_end_idx = match.end()
        
        tracker_content = match.group(1)
        
        # Parse individual phase lines
        phases = []
        for line in tracker_content.split('\n'):
            phase_match = re.search(self.PHASE_LINE_PATTERN, line)
            if phase_match:
                phase_name = phase_match.group(1).strip()
                progress_bar = phase_match.group(2)
                progress_percent = int(phase_match.group(3))
                status_emoji = phase_match.group(4)
                status_text = phase_match.group(5).strip()
                
                # Extract phase number
                phase_num_match = re.search(r'PHASE (\d+):', phase_name)
                phase_number = int(phase_num_match.group(1)) if phase_num_match else 0
                
                # Map emoji to status
                status_map = {
                    '⏳': PhaseStatus.NOT_STARTED,
                    '🚧': PhaseStatus.IN_PROGRESS,
                    '✅': PhaseStatus.COMPLETE,
                    '⚠️': PhaseStatus.BLOCKED
                }
                status = status_map.get(status_emoji, PhaseStatus.NOT_STARTED)
                
                phases.append(PhaseInfo(
                    phase_id=f"PHASE-{phase_number}",
                    phase_number=phase_number,
                    phase_name=phase_name,
                    status=status,
                    progress_percent=progress_percent
                ))
        
        # Parse overall progress
        overall_match = re.search(self.OVERALL_PROGRESS_PATTERN, tracker_content)
        if overall_match:
            completed = int(overall_match.group(2))
            total = int(overall_match.group(3))
            overall_percent = int(overall_match.group(4))
        else:
            completed = sum(1 for p in phases if p.status == PhaseStatus.COMPLETE)
            total = len(phases)
            overall_percent = int((completed / total * 100) if total > 0 else 0)
        
        return ProgressTrackerInfo(
            phases=phases,
            overall_progress_percent=overall_percent,
            total_phases=total,
            completed_phases=completed
        )


class ASCIIArtGenerator:
    """
    Generates ASCII art progress bars and visual trackers.
    """
    
    @staticmethod
    def generate_progress_bar(percent: int, width: int = 10) -> str:
        """Generate ASCII progress bar [████░░░░]"""
        filled = int(width * percent / 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    @staticmethod
    def generate_overall_progress_bar(percent: int, width: int = 30) -> str:
        """Generate wider progress bar for overall progress"""
        filled = int(width * percent / 100)
        empty = width - filled
        return '█' * filled + '░' * empty
    
    @staticmethod
    def format_status_emoji(status: PhaseStatus) -> str:
        """Get emoji for phase status"""
        status_map = {
            PhaseStatus.NOT_STARTED: '⏳',
            PhaseStatus.IN_PROGRESS: '🚧',
            PhaseStatus.COMPLETE: '✅',
            PhaseStatus.BLOCKED: '⚠️'
        }
        return status_map.get(status, '⏳')


class TrackerUpdateEngine:
    """
    Updates progress tracker with new phase status.
    Calculates percentages, updates timestamps, manages state transitions.
    """
    
    def __init__(self, tracker_info: ProgressTrackerInfo):
        self.tracker_info = tracker_info
    
    def update_phase_status(self, phase_number: int, new_status: PhaseStatus,
                           start_date: Optional[datetime] = None,
                           completion_date: Optional[datetime] = None) -> bool:
        """Update a specific phase's status"""
        phase = next((p for p in self.tracker_info.phases if p.phase_number == phase_number), None)
        
        if not phase:
            logger.error(f"Phase {phase_number} not found")
            return False
        
        # Update status
        old_status = phase.status
        phase.status = new_status
        
        # Update progress percentage
        if new_status == PhaseStatus.COMPLETE:
            phase.progress_percent = 100
            phase.completion_date = completion_date or datetime.now()
        elif new_status == PhaseStatus.IN_PROGRESS:
            if phase.progress_percent == 0:
                phase.progress_percent = 10  # Started
            phase.start_date = start_date or datetime.now()
        elif new_status == PhaseStatus.NOT_STARTED:
            phase.progress_percent = 0
        
        # Calculate elapsed time
        if phase.start_date and phase.completion_date:
            phase.elapsed_time = phase.completion_date - phase.start_date
        
        # Recalculate overall progress
        self._recalculate_overall_progress()
        
        logger.info(f"Updated {phase.phase_name}: {old_status} → {new_status}")
        return True
    
    def _recalculate_overall_progress(self):
        """Recalculate overall progress percentage"""
        completed = sum(1 for p in self.tracker_info.phases if p.status == PhaseStatus.COMPLETE)
        total = len(self.tracker_info.phases)
        
        self.tracker_info.completed_phases = completed
        self.tracker_info.overall_progress_percent = int((completed / total * 100) if total > 0 else 0)
    
    def get_next_phase(self) -> Optional[PhaseInfo]:
        """Get the next phase to execute"""
        for phase in self.tracker_info.phases:
            if phase.status == PhaseStatus.NOT_STARTED:
                return phase
        return None


class PhaseSummaryBuilder:
    """
    Builds phase completion summaries with metrics.
    """
    
    @staticmethod
    def build_summary(phase: PhaseInfo, metrics: Optional[Dict] = None) -> str:
        """Build completion summary for a phase"""
        summary_lines = []
        
        summary_lines.append(f"# Phase {phase.phase_number} Complete: {phase.phase_name}")
        summary_lines.append("")
        summary_lines.append(f"**Status:** {phase.status.value}")
        
        if phase.start_date:
            summary_lines.append(f"**Start Date:** {phase.start_date.strftime('%Y-%m-%d %H:%M')}")
        
        if phase.completion_date:
            summary_lines.append(f"**Completion Date:** {phase.completion_date.strftime('%Y-%m-%d %H:%M')}")
        
        if phase.elapsed_time:
            hours = int(phase.elapsed_time.total_seconds() // 3600)
            minutes = int((phase.elapsed_time.total_seconds() % 3600) // 60)
            summary_lines.append(f"**Elapsed Time:** {hours}h {minutes}m")
        
        if metrics:
            summary_lines.append("")
            summary_lines.append("**Metrics:**")
            for key, value in metrics.items():
                summary_lines.append(f"- {key}: {value}")
        
        return "\n".join(summary_lines)


class ProgressSynchronizer:
    """
    Main progress synchronizer utility.
    
    Usage:
        sync = ProgressSynchronizer(plan_path)
        sync.update_phase(phase_number=2, status=PhaseStatus.COMPLETE)
    """
    
    def __init__(self, plan_path: Path):
        self.plan_path = plan_path
        self.parser = MarkdownParser(plan_path)
        self.tracker_info: Optional[ProgressTrackerInfo] = None
    
    def load(self) -> bool:
        """Load plan and extract progress tracker"""
        if not self.parser.load():
            return False
        
        self.tracker_info = self.parser.extract_progress_tracker()
        return self.tracker_info is not None
    
    def update_phase(self, phase_number: int, status: PhaseStatus,
                    start_date: Optional[datetime] = None,
                    completion_date: Optional[datetime] = None,
                    metrics: Optional[Dict] = None) -> bool:
        """
        Update a phase's status and synchronize the plan file.
        
        Args:
            phase_number: Phase number to update (e.g., 2 for Phase 2)
            status: New status (PhaseStatus.COMPLETE, etc.)
            start_date: Optional start date (defaults to now if IN_PROGRESS)
            completion_date: Optional completion date (defaults to now if COMPLETE)
            metrics: Optional metrics dict for completion summary
        
        Returns:
            True if update successful, False otherwise
        """
        if not self.tracker_info:
            logger.error("No tracker info loaded. Call load() first.")
            return False
        
        # Update phase status
        engine = TrackerUpdateEngine(self.tracker_info)
        if not engine.update_phase_status(phase_number, status, start_date, completion_date):
            return False
        
        # Regenerate progress tracker section
        new_tracker = self._generate_updated_tracker()
        
        # Replace old tracker with new one
        new_content = (
            self.parser.content[:self.parser.tracker_start_idx] +
            new_tracker +
            self.parser.content[self.parser.tracker_end_idx:]
        )
        
        # Write atomically (temp file → rename)
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                delete=False,
                dir=self.plan_path.parent,
                prefix='.progress_sync_',
                suffix='.md'
            ) as tmp_file:
                tmp_file.write(new_content)
                tmp_path = Path(tmp_file.name)
            
            # Atomic rename
            shutil.move(str(tmp_path), str(self.plan_path))
            
            logger.info(f"Successfully updated {self.plan_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing updated plan: {e}")
            if 'tmp_path' in locals() and tmp_path.exists():
                tmp_path.unlink()
            return False
    
    def _generate_updated_tracker(self) -> str:
        """Generate updated progress tracker section"""
        lines = []
        
        lines.append("```")
        lines.append("━" * 78)
        
        # Extract title from first phase or use generic
        if self.tracker_info.phases:
            # Get title from markdown content
            title_match = re.search(r'PHASE.*?:.*?([A-Z ]+)\n━', self.parser.tracker_section)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = "PROGRESS TRACKER"
        else:
            title = "PROGRESS TRACKER"
        
        lines.append(f"                    {title}")
        lines.append("━" * 78)
        
        # Add individual phase lines
        for phase in self.tracker_info.phases:
            progress_bar = ASCIIArtGenerator.generate_progress_bar(phase.progress_percent)
            
            # Format phase name (truncate if needed)
            phase_name = phase.phase_name
            if len(phase_name) > 40:
                phase_name = phase_name[:37] + "..."
            
            # Status value already includes emoji
            line = f"{phase_name:<41} {progress_bar} {phase.progress_percent:3}%  {phase.status.value}"
            lines.append(line)
        
        lines.append("")
        
        # Overall progress line
        overall_bar = ASCIIArtGenerator.generate_overall_progress_bar(
            self.tracker_info.overall_progress_percent
        )
        lines.append(
            f"OVERALL PROGRESS: {overall_bar} "
            f"{self.tracker_info.completed_phases}/{self.tracker_info.total_phases} "
            f"Phases ({self.tracker_info.overall_progress_percent}%)"
        )
        
        lines.append("```")
        
        return "\n".join(lines)
    
    def get_current_status(self) -> Optional[ProgressTrackerInfo]:
        """Get current progress tracker status"""
        return self.tracker_info
    
    def get_next_phase(self) -> Optional[PhaseInfo]:
        """Get the next phase to execute"""
        if not self.tracker_info:
            return None
        
        engine = TrackerUpdateEngine(self.tracker_info)
        return engine.get_next_phase()


# Convenience functions for common operations

def update_master_plan_phase(phase_number: int, status: PhaseStatus,
                             master_plan_path: Optional[Path] = None,
                             metrics: Optional[Dict] = None) -> bool:
    """
    Update a phase in the master plan.
    
    Args:
        phase_number: Phase number to update
        status: New status
        master_plan_path: Optional path (defaults to MASTER plan)
        metrics: Optional metrics for summary
    
    Returns:
        True if successful
    """
    if master_plan_path is None:
        # Default master plan location
        master_plan_path = Path("cortex-brain/documents/planning/features/active/MASTER-CORTEX-ORCHESTRATION-AST-ENHANCEMENT-PLAN.md")
    
    sync = ProgressSynchronizer(master_plan_path)
    if not sync.load():
        return False
    
    return sync.update_phase(
        phase_number=phase_number,
        status=status,
        metrics=metrics
    )


def update_sub_plan_phase(sub_plan_path: Path, phase_number: int, status: PhaseStatus,
                         metrics: Optional[Dict] = None) -> bool:
    """Update a phase in a sub-plan"""
    sync = ProgressSynchronizer(sub_plan_path)
    if not sync.load():
        return False
    
    return sync.update_phase(
        phase_number=phase_number,
        status=status,
        metrics=metrics
    )
