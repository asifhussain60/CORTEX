"""
Progress Renderer for Copilot Chat

Renders visual progress bars and phase transitions for autonomous execution.
Designed for real-time visibility during long-running orchestrator operations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0

Features:
- Emoji-rich progress bars (🔄 ✅ ⏱️ 📋)
- Task-level progress updates (<10ms overhead)
- Phase transition markers
- Git checkpoint status display
- Terminal width adaptation

Usage:
    from src.operations.utilities.progress_renderer import ProgressRenderer
    
    renderer = ProgressRenderer()
    
    # After each task completion
    progress_msg = renderer.render_task_progress(
        current=5,
        total=10,
        phase_name="Development",
        current_phase=2,
        total_phases=4,
        task_name="Implement authentication",
        elapsed_time="2m 15s"
    )
    print(progress_msg)
    
    # Between phases
    transition_msg = renderer.render_phase_transition(
        from_phase="Foundation",
        to_phase="Development",
        completed_tasks=5,
        duration="3m 10s",
        checkpoint_created=True,
        checkpoint_name="cortex-checkpoint-phase-1-foundation-20251213-143022"
    )
    print(transition_msg)
"""

import logging
import shutil
from typing import Optional

logger = logging.getLogger(__name__)


class ProgressRenderer:
    """
    Renders visual progress bars for Copilot Chat autonomous execution.
    
    Provides real-time feedback during long-running operations with:
    - Task-level progress bars
    - Phase transition markers
    - Git checkpoint status
    - Emoji-rich formatting
    
    Performance: <10ms per render
    """
    
    def __init__(self, bar_width: int = 10):
        """
        Initialize progress renderer.
        
        Args:
            bar_width: Width of progress bar in characters (default: 10)
        """
        self.bar_width = bar_width
        self.terminal_width = self._get_terminal_width()
    
    @staticmethod
    def _get_terminal_width() -> int:
        """
        Get terminal width for adaptive rendering.
        
        Returns:
            Terminal width in characters (default: 80 if not detectable)
        """
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80  # Default fallback
    
    def _generate_progress_bar(
        self,
        current: int,
        total: int,
        width: Optional[int] = None
    ) -> str:
        """
        Generate emoji-based progress bar.
        
        Args:
            current: Current progress (completed items)
            total: Total items
            width: Bar width (uses default if None)
        
        Returns:
            Progress bar string like "[████████░░]"
        """
        if width is None:
            width = self.bar_width
        
        if total == 0:
            percentage = 0
        else:
            percentage = min(100, int((current / total) * 100))
        
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        
        return f"[{bar}]"
    
    def render_task_progress(
        self,
        current: int,
        total: int,
        phase_name: str,
        current_phase: int,
        total_phases: int,
        task_name: str,
        elapsed_time: str,
        bar_width: Optional[int] = None
    ) -> str:
        """
        Render task-level progress update.
        
        Args:
            current: Current task number (1-based)
            total: Total tasks
            phase_name: Name of current phase
            current_phase: Current phase number (1-based)
            total_phases: Total phases
            task_name: Current task name
            elapsed_time: Elapsed time string (e.g., "2m 15s")
            bar_width: Optional override for bar width
        
        Returns:
            Formatted progress string for Copilot Chat
        
        Example Output:
            🔄 Phase 2 of 4: Development
            [████████░░] 80% (8/10 tasks) | ⏱️ 2m 15s | 📋 Current: Implement authentication
        """
        progress_bar = self._generate_progress_bar(current, total, bar_width)
        percentage = int((current / total) * 100) if total > 0 else 0
        
        output = (
            f"\n🔄 **Phase {current_phase} of {total_phases}: {phase_name}**\n"
            f"{progress_bar} {percentage}% ({current}/{total} tasks) | "
            f"⏱️ {elapsed_time} | 📋 Current: {task_name}\n"
        )
        
        return output
    
    def render_phase_transition(
        self,
        from_phase: str,
        to_phase: str,
        completed_tasks: int,
        duration: str,
        checkpoint_created: bool = False,
        checkpoint_name: str = ""
    ) -> str:
        """
        Render phase completion and transition to next phase.
        
        Args:
            from_phase: Name of completed phase
            to_phase: Name of next phase
            completed_tasks: Number of tasks completed in phase
            duration: Phase duration string (e.g., "3m 10s")
            checkpoint_created: Whether git checkpoint was created
            checkpoint_name: Name of checkpoint (if created)
        
        Returns:
            Formatted transition string for Copilot Chat
        
        Example Output:
            ✅ Phase 1: Foundation Complete! (5 tasks, 3m 10s)
            ✅ Git checkpoint created: cortex-checkpoint-phase-1-foundation-20251213-143022
            🔄 Starting Phase 2: Development...
        """
        output = (
            f"\n✅ **{from_phase} Complete!** ({completed_tasks} tasks, {duration})\n"
        )
        
        if checkpoint_created and checkpoint_name:
            output += f"✅ Git checkpoint created: `{checkpoint_name}`\n"
        
        output += f"🔄 **Starting {to_phase}**...\n"
        
        return output
    
    def render_checkpoint_status(
        self,
        success: bool,
        checkpoint_name: str = "",
        error_message: str = ""
    ) -> str:
        """
        Render git checkpoint creation status.
        
        Args:
            success: Whether checkpoint was created successfully
            checkpoint_name: Name of checkpoint (if successful)
            error_message: Error message (if failed)
        
        Returns:
            Formatted checkpoint status string
        
        Example Output (Success):
            ✅ Git checkpoint created: cortex-checkpoint-phase-1-foundation-20251213-143022
        
        Example Output (Failure):
            ⚠️ Git checkpoint failed: No changes to commit
        """
        if success:
            return f"✅ Git checkpoint created: `{checkpoint_name}`\n"
        else:
            return f"⚠️ Git checkpoint failed: {error_message}\n"
    
    def render_completion_summary(
        self,
        total_phases: int,
        total_tasks: int,
        total_duration: str,
        checkpoints_created: int
    ) -> str:
        """
        Render final completion summary.
        
        Args:
            total_phases: Total phases executed
            total_tasks: Total tasks completed
            total_duration: Total execution time (e.g., "15m 30s")
            checkpoints_created: Number of git checkpoints created
        
        Returns:
            Formatted completion summary
        
        Example Output:
            🎉 Autonomous Execution Complete!
            ✅ Phases: 4/4
            ✅ Tasks: 47/47
            ⏱️ Duration: 15m 30s
            📍 Checkpoints: 4
        """
        output = (
            f"\n🎉 **Autonomous Execution Complete!**\n"
            f"✅ Phases: {total_phases}/{total_phases}\n"
            f"✅ Tasks: {total_tasks}/{total_tasks}\n"
            f"⏱️ Duration: {total_duration}\n"
            f"📍 Checkpoints: {checkpoints_created}\n"
        )
        
        return output


def format_elapsed_time(seconds: float) -> str:
    """
    Format elapsed time for display.
    
    Args:
        seconds: Elapsed time in seconds
    
    Returns:
        Formatted time string (e.g., "2m 15s", "1h 5m", "45s")
    
    Examples:
        format_elapsed_time(45) -> "45s"
        format_elapsed_time(135) -> "2m 15s"
        format_elapsed_time(3725) -> "1h 2m"
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"
