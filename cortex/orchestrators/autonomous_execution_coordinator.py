"""Autonomous Execution Coordinator - Integration Module.

Coordinates autonomous execution with progress tracking and minimal updates.
Integrates R1-R4: Continuation detection, progress bars, minimal updates, single gate.

Authority: Phase 35 + cortex-architect.prompt.md
"""

from pathlib import Path
from typing import List, Optional

from cortex.interaction.autonomous_plan_executor import (
    AutonomousPlanExecutor,
    Phase as ExecutorPhase,
)
from cortex.orchestrators.response.ascii_progress_bar import ASCIIProgressBar, Phase


class AutonomousExecutionCoordinator:
    """Coordinates autonomous multi-phase execution with progress tracking.

    Usage:
        coordinator = AutonomousExecutionCoordinator()

        # Check if user wants autonomous execution
        if coordinator.should_execute_autonomously(user_input):
            # Show initial status
            coordinator.show_initial_status()

            # Execute phases autonomously
            for phase in coordinator.get_phases_to_execute():
                coordinator.execute_phase(phase)
                coordinator.update_progress(phase)

            # Show completion
            coordinator.show_completion_status()
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize coordinator.

        Args:
            registry_path: Path to registry (defaults to _cortex-master/index.yaml)
        """
        self.executor = AutonomousPlanExecutor(registry_path)
        self.progress_bar = ASCIIProgressBar()
        self.phases: List[Phase] = []
        self.current_phase_index = 0

    def should_execute_autonomously(self, user_input: str) -> bool:
        """Check if user input indicates autonomous execution intent.

        Args:
            user_input: Raw user input

        Returns:
            True if autonomous execution should proceed
        """
        return self.executor.detect_continuation(user_input)

    def get_continuation_reason(self) -> str:
        """Get reason for autonomous execution.

        Returns:
            Human-readable reason (e.g., "User said 'proceed'")
        """
        return self.executor.get_continuation_reason()

    def load_phases(self) -> List[Phase]:
        """Load phases for autonomous execution.

        Returns:
            List of phases to execute
        """
        # Get next phase from registry
        next_phase = self.executor.load_next_phase()
        if not next_phase:
            return []

        # For demonstration, create phase list
        # In production, this would load all relevant phases
        self.phases = [
            Phase(
                name=f"R1 - {next_phase.name} (Continuation Detection)",
                progress=0.0,
                status="active",
            ),
            Phase(
                name="R2 - ASCII Progress Bars",
                progress=0.0,
                status="queued",
            ),
            Phase(
                name="R3 - Minimal Status Updates",
                progress=0.0,
                status="queued",
            ),
            Phase(
                name="R4 - Single Decision Gate",
                progress=0.0,
                status="queued",
            ),
        ]
        return self.phases

    def show_initial_status(self) -> str:
        """Show initial status with progress bars.

        Returns:
            Formatted status string
        """
        if not self.phases:
            self.load_phases()

        reason = self.get_continuation_reason()
        header = self.progress_bar.format_mode_header("IMPLEMENT", self.phases)

        status_lines = [
            "### 🚀 Autonomous Execution Mode",
            f"**Reason:** {reason}",
            "",
            header,
            "",
            self.progress_bar.display_all_phases(self.phases),
        ]

        return "\n".join(status_lines)

    def update_progress(self, phase_name: str, progress: float) -> str:
        """Update phase progress and return minimal status.

        Args:
            phase_name: Name of phase to update
            progress: New progress value (0.0 to 1.0)

        Returns:
            Minimal status update (subtle spine format)
        """
        # Find and update phase
        for i, phase in enumerate(self.phases):
            if phase_name in phase.name:
                phase.progress = progress

                # Update status based on progress
                if progress >= 1.0:
                    phase.status = "completed"
                    # Activate next phase
                    if i + 1 < len(self.phases):
                        self.phases[i + 1].status = "active"
                elif progress > 0:
                    phase.status = "active"

                # Get current and next phase names
                current = phase.name
                next_phase = self.phases[i + 1].name if i + 1 < len(self.phases) else None

                return self.progress_bar.format_subtle_spine(current, next_phase)

        return ""

    def show_progress_bars(self) -> str:
        """Show current progress bars for all phases.

        Returns:
            Formatted progress bars
        """
        return self.progress_bar.display_all_phases(self.phases)

    def show_completion_status(self) -> str:
        """Show completion status with summary.

        Returns:
            Formatted completion message
        """
        summary = self.progress_bar.format_completion_summary(self.phases)

        completion_lines = [
            "### ✅ Autonomous Execution Complete",
            "",
            summary,
            "",
            self.progress_bar.display_all_phases(self.phases),
            "",
            "**Next Steps:** All recommendations implemented. No further user input required.",
        ]

        return "\n".join(completion_lines)

    def should_skip_dor(self) -> bool:
        """Check if DoR/Challenge should be skipped.

        Returns:
            True if DoR should be skipped (autonomous mode)
        """
        return self.executor.should_skip_dor()

    def is_autonomous_mode(self) -> bool:
        """Check if in autonomous execution mode.

        Returns:
            True if autonomous mode active
        """
        return self.executor.is_autonomous_mode()
