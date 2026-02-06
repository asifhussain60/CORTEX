"""ASCII Progress Bar Generator - Visual Progress Indicators.

Generates fixed-width ASCII progress bars for CODE-ACTION modes.
Format: [████████░░] 80% Phase 2: KSESSIONS Implementation

Authority: Phase 35 R2 + cortex-architect.prompt.md lines 268-310
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class Phase(BaseModel):
    """Phase representation for progress tracking."""

    name: str
    progress: float = Field(ge=0.0, le=1.0)  # 0.0 to 1.0
    status: str = "queued"  # queued, active, completed, blocked


class ASCIIProgressBar:
    """ASCII progress bar generator with fixed 10-block format.

    Usage:
        bar = ASCIIProgressBar()
        output = bar.generate_bar(0.8)  # [████████░░]
        formatted = bar.format_phase_progress(phase)  # [████████░░] 80% Phase Name
        all_phases = bar.display_all_phases([phase1, phase2, phase3])
    """

    FILLED_CHAR = "█"
    EMPTY_CHAR = "░"
    DEFAULT_WIDTH = 10

    # Status emoji indicators
    STATUS_ICONS = {
        "completed": "✅",
        "active": "🔵",
        "queued": "⚪",
        "blocked": "🔴",
    }

    def generate_bar(self, progress: float, width: int = DEFAULT_WIDTH) -> str:
        """Generate ASCII progress bar.

        Args:
            progress: Progress value (0.0 to 1.0)
            width: Bar width in characters (default: 10)

        Returns:
            ASCII bar string (e.g., "[████████░░]")

        Examples:
            >>> bar = ASCIIProgressBar()
            >>> bar.generate_bar(0.0)
            '[░░░░░░░░░░]'
            >>> bar.generate_bar(0.5)
            '[█████░░░░░]'
            >>> bar.generate_bar(1.0)
            '[██████████]'
        """
        # Clamp progress to 0.0-1.0
        progress = max(0.0, min(1.0, progress))

        filled_count = int(progress * width)
        empty_count = width - filled_count

        bar = (
            "["
            + (self.FILLED_CHAR * filled_count)
            + (self.EMPTY_CHAR * empty_count)
            + "]"
        )
        return bar

    def format_phase_progress(
        self, phase: Phase, show_status_icon: bool = True
    ) -> str:
        """Format phase progress with bar, percentage, and name.

        Args:
            phase: Phase with name, progress, and status
            show_status_icon: Include status emoji (default: True)

        Returns:
            Formatted string (e.g., "[████████░░] 80% Phase 2: Implementation")

        Examples:
            >>> bar = ASCIIProgressBar()
            >>> phase = Phase(name="KSESSIONS", progress=0.8, status="active")
            >>> bar.format_phase_progress(phase)
            '[████████░░]  80% Phase 2: KSESSIONS 🔵'
        """
        bar = self.generate_bar(phase.progress)
        percentage = int(phase.progress * 100)

        # Format percentage with right alignment (3 chars)
        percentage_str = f"{percentage:3d}%"

        # Add status icon if requested
        status_icon = ""
        if show_status_icon:
            status_icon = " " + self.STATUS_ICONS.get(phase.status, "")

        return f"{bar} {percentage_str} {phase.name}{status_icon}"

    def display_all_phases(
        self, phases: List[Phase], show_status_icons: bool = True
    ) -> str:
        """Display all phases with progress bars.

        Args:
            phases: List of phases to display
            show_status_icons: Include status emoji (default: True)

        Returns:
            Multi-line string with all phase progress bars

        Examples:
            >>> bar = ASCIIProgressBar()
            >>> phases = [
            ...     Phase(name="Phase 2: KSESSIONS", progress=0.8, status="active"),
            ...     Phase(name="Phase 3: MCP Gateway", progress=0.4, status="queued"),
            ...     Phase(name="Phase 4: Refactor", progress=0.0, status="queued"),
            ... ]
            >>> print(bar.display_all_phases(phases))
            [████████░░]  80% Phase 2: KSESSIONS 🔵
            [████░░░░░░]  40% Phase 3: MCP Gateway ⚪
            [░░░░░░░░░░]   0% Phase 4: Refactor ⚪
        """
        lines = []
        for phase in phases:
            lines.append(self.format_phase_progress(phase, show_status_icons))
        return "\n".join(lines)

    def format_completion_summary(self, phases: List[Phase]) -> str:
        """Format completion summary with counts.

        Args:
            phases: List of phases

        Returns:
            Summary string (e.g., "Completed: 2/3 phases (67%)")

        Examples:
            >>> bar = ASCIIProgressBar()
            >>> phases = [
            ...     Phase(name="Phase 1", progress=1.0, status="completed"),
            ...     Phase(name="Phase 2", progress=1.0, status="completed"),
            ...     Phase(name="Phase 3", progress=0.5, status="active"),
            ... ]
            >>> bar.format_completion_summary(phases)
            'Completed: 2/3 phases (67%)'
        """
        total = len(phases)
        if total == 0:
            return "No phases"

        completed = sum(1 for p in phases if p.status == "completed")
        percentage = int((completed / total) * 100)

        return f"Completed: {completed}/{total} phases ({percentage}%)"

    @staticmethod
    def format_subtle_spine(
        current_phase: str, next_phase: Optional[str] = None
    ) -> str:
        """Format subtle spine for inline display (Phase-31A style).

        Args:
            current_phase: Current phase name
            next_phase: Next phase name (optional)

        Returns:
            Inline string (e.g., "[→] Phase 2 | [ ] Phase 3")

        Examples:
            >>> ASCIIProgressBar.format_subtle_spine("Phase 2", "Phase 3")
            '[→] Phase 2 | [ ] Phase 3'
            >>> ASCIIProgressBar.format_subtle_spine("Phase 2")
            '[→] Phase 2'
        """
        if next_phase:
            return f"[→] {current_phase} | [ ] {next_phase}"
        return f"[→] {current_phase}"

    @staticmethod
    def format_mode_header(mode: str, phases: List[Phase]) -> str:
        """Format mode-specific header with progress indicator.

        Args:
            mode: Mode name (PLAN, TDD, IMPLEMENT, REFACTOR)
            phases: List of phases

        Returns:
            Header string with mode and phase count

        Examples:
            >>> phases = [
            ...     Phase(name="Phase 1", progress=1.0, status="completed"),
            ...     Phase(name="Phase 2", progress=0.5, status="active"),
            ... ]
            >>> ASCIIProgressBar.format_mode_header("IMPLEMENT", phases)
            '### 🎯 IMPLEMENT Mode - 2 phases tracked'
        """
        phase_count = len(phases)
        return f"### 🎯 {mode} Mode - {phase_count} phase{'s' if phase_count != 1 else ''} tracked"
