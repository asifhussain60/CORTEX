"""
Visual Feedback Mixin - AC-VISUAL-FEEDBACK-002

Provides progress reporting capabilities for long-running CORTEX processes.

Key Features:
- ASCII progress bar generation
- Real-time progress updates with carriage return
- Status icons (✅ DONE, 🔵 IN PROGRESS, ⚪ PENDING, ❌ FAIL)
- Batch/stage progress tracking
- Time estimation
- Completion summaries

CORE Compliance:
- CORE-011: Type hints (mypy --strict)
- CORE-012: Google-style docstrings
- CORE-013: Specific exceptions

Usage:
    class MyOrchestrator(VisualFeedbackMixin):
        def process_items(self, items: List[Any]) -> Result:
            self.start_progress("Processing items", total=len(items))

            for idx, item in enumerate(items):
                # Do work
                self.update_progress(current=idx+1, message=f"Item {idx+1}")

            self.complete_progress("All items processed")
"""

import sys
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from cortex.orchestrators.response.ascii_progress_bar import ASCIIProgressBar, Phase


@dataclass
class ProgressState:
    """Current progress state for tracking.

    Attributes:
        operation_name: Name of current operation
        total_items: Total items to process
        current_item: Current item index
        start_time: When operation started
        last_update_time: Last progress update timestamp
        status: Current status (running, completed, failed)
    """
    operation_name: str
    total_items: int
    current_item: int = 0
    start_time: float = 0.0
    last_update_time: float = 0.0
    status: str = "running"


class VisualFeedbackMixin:
    """Mixin providing visual progress reporting for long-running operations.

    Provides:
    - ASCII progress bars with [████████░░] format
    - Real-time percentage display
    - Status icons (✅/🔵/⚪/❌)
    - Time estimation
    - Completion summaries

    Attributes:
        _progress_bar: ASCIIProgressBar instance
        _progress_state: Current progress state
        _show_progress: Whether to show progress (default: True)
        _progress_callback: Optional callback for progress updates
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize visual feedback mixin."""
        super().__init__(*args, **kwargs)
        self._progress_bar = ASCIIProgressBar()
        self._progress_state: Optional[ProgressState] = None
        self._show_progress = True
        self._progress_callback: Optional[Callable] = None

    def start_progress(
        self,
        operation_name: str,
        total: int,
        show_header: bool = True
    ) -> None:
        """Start progress tracking for an operation.

        Args:
            operation_name: Name of operation (e.g., "Processing files")
            total: Total number of items to process
            show_header: Whether to show operation header (default: True)
        """
        if not self._show_progress:
            return

        self._progress_state = ProgressState(
            operation_name=operation_name,
            total_items=total,
            start_time=time.time(),
            last_update_time=time.time()
        )

        if show_header:
            print(f"\n🔄 {operation_name}")
            print("━" * 60)

    def update_progress(
        self,
        current: int,
        message: Optional[str] = None,
        force_update: bool = False
    ) -> None:
        """Update progress display.

        Args:
            current: Current item index (1-based)
            message: Optional status message
            force_update: Force update even if too soon
        """
        if not self._show_progress or not self._progress_state:
            return

        # Throttle updates (every 50ms minimum)
        now = time.time()
        if not force_update and (now - self._progress_state.last_update_time) < 0.05:
            return

        self._progress_state.current_item = current
        self._progress_state.last_update_time = now

        # Calculate progress
        progress = current / self._progress_state.total_items if self._progress_state.total_items > 0 else 0.0
        progress = min(1.0, progress)  # Cap at 100%

        # Generate progress bar
        bar = self._progress_bar.generate_bar(progress)
        percentage = int(progress * 100)

        # Calculate ETA
        elapsed = now - self._progress_state.start_time
        if current > 0 and progress < 1.0:
            eta_seconds = (elapsed / current) * (self._progress_state.total_items - current)
            eta_str = self._format_time(eta_seconds)
        else:
            eta_str = "--"

        # Format message
        item_info = f"{current}/{self._progress_state.total_items}"
        status_line = f"{bar} {percentage:3d}% | {item_info}"

        if message:
            status_line += f" | {message}"

        status_line += f" | ETA: {eta_str}"

        # Print with carriage return (overwrites line)
        print(f"\r{status_line}", end="", flush=True)

        # Call callback if registered
        if self._progress_callback:
            self._progress_callback(current, self._progress_state.total_items, progress)

    def complete_progress(
        self,
        message: str = "Complete",
        success: bool = True
    ) -> None:
        """Mark progress as complete and show summary.

        Args:
            message: Completion message
            success: Whether operation succeeded
        """
        if not self._show_progress or not self._progress_state:
            return

        # Update to 100%
        self.update_progress(self._progress_state.total_items, force_update=True)

        # Move to new line
        print()

        # Calculate final stats
        elapsed = time.time() - self._progress_state.start_time
        elapsed_str = self._format_time(elapsed)

        # Show completion status
        icon = "✅" if success else "❌"
        print(f"{icon} {message} ({elapsed_str})")
        print("━" * 60)

        # Reset state
        self._progress_state = None

    def fail_progress(self, error_message: str) -> None:
        """Mark progress as failed.

        Args:
            error_message: Error description
        """
        self.complete_progress(f"Failed: {error_message}", success=False)

    def show_stage_progress(
        self,
        stage_num: int,
        total_stages: int,
        stage_name: str,
        stage_progress: float = 0.0
    ) -> None:
        """Show progress for staged operations (e.g., workflow stages).

        Args:
            stage_num: Current stage number (1-based)
            total_stages: Total number of stages
            stage_name: Name of current stage
            stage_progress: Progress within stage (0.0-1.0)
        """
        if not self._show_progress:
            return

        # Overall stage progress
        overall_progress = ((stage_num - 1) + stage_progress) / total_stages

        # Generate progress bar
        bar = self._progress_bar.generate_bar(overall_progress)
        percentage = int(overall_progress * 100)

        # Stage indicator
        stage_info = f"Stage {stage_num}/{total_stages}: {stage_name}"

        # Print with carriage return
        print(f"\r{bar} {percentage:3d}% | {stage_info}", end="", flush=True)

        # If stage complete, move to new line
        if stage_progress >= 1.0:
            print()  # New line after stage completes

    def show_batch_progress(
        self,
        batch_num: int,
        total_batches: int,
        batch_name: Optional[str] = None
    ) -> None:
        """Show progress for batch processing.

        Args:
            batch_num: Current batch number (1-based)
            total_batches: Total number of batches
            batch_name: Optional batch identifier
        """
        if not self._show_progress:
            return

        progress = batch_num / total_batches
        bar = self._progress_bar.generate_bar(progress)
        percentage = int(progress * 100)

        batch_info = f"Batch {batch_num}/{total_batches}"
        if batch_name:
            batch_info += f": {batch_name}"

        print(f"\r{bar} {percentage:3d}% | {batch_info}", end="", flush=True)

        if batch_num == total_batches:
            print()  # New line when all batches complete

    def set_progress_callback(self, callback: Callable) -> None:
        """Register callback for progress updates.

        Args:
            callback: Function(current, total, progress) -> None
        """
        self._progress_callback = callback

    def disable_progress(self) -> None:
        """Disable progress display (e.g., for tests)."""
        self._show_progress = False

    def enable_progress(self) -> None:
        """Enable progress display."""
        self._show_progress = True

    def _format_time(self, seconds: float) -> str:
        """Format seconds into human-readable time.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string (e.g., "2m 15s")
        """
        if seconds < 1:
            return "<1s"
        elif seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"


# AC_START: AC-VISUAL-FEEDBACK-002
# Description: Visual feedback mixin for all long-running CORTEX processes
# Features: Progress bars, stage tracking, batch tracking, ETA, completion summaries
# AC_COMPLETE: AC-VISUAL-FEEDBACK-002 ✅ Mixin implemented with full progress API
