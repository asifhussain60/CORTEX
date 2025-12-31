#!/usr/bin/env python3
"""
CORTEX Toolkit: Progress Bar Generator

Generates standardized progress bars following CORTEX progress_bar_standard.
Part of Orchestrator Composable Template System.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

from typing import Literal


# Standard configuration (from response-templates-v4.yaml)
PROGRESS_BAR_CONFIG = {
    "width": 10,
    "filled_char": "█",
    "empty_char": "░",
    "status_icons": {
        "completed": "✅",
        "in_progress": "🔄",
        "pending": "⏳",
        "failed": "❌",
        "paused": "⏸️"
    }
}


StatusType = Literal["completed", "in_progress", "pending", "failed", "paused"]


def generate_progress_bar(
    current: int,
    total: int,
    status: StatusType = "in_progress",
    show_percentage: bool = True,
    show_counts: bool = True
) -> str:
    """
    Generate a standardized CORTEX progress bar.
    
    Args:
        current: Current progress value
        total: Total/maximum value
        status: Status type (completed, in_progress, pending, failed, paused)
        show_percentage: Include percentage in output
        show_counts: Include current/total counts in output
    
    Returns:
        Formatted progress bar string
    
    Examples:
        >>> generate_progress_bar(3, 8)
        '🔄 ███░░░░░░░ 37.5% (3/8)'
        
        >>> generate_progress_bar(8, 8, status="completed")
        '✅ ██████████ 100.0% (8/8)'
        
        >>> generate_progress_bar(0, 5, status="pending", show_percentage=False)
        '⏳ ░░░░░░░░░░ (0/5)'
    """
    # Calculate percentage
    percentage = (current / total * 100) if total > 0 else 0
    
    # Calculate filled blocks
    filled_blocks = int((current / total) * PROGRESS_BAR_CONFIG["width"]) if total > 0 else 0
    empty_blocks = PROGRESS_BAR_CONFIG["width"] - filled_blocks
    
    # Build bar
    bar = (
        PROGRESS_BAR_CONFIG["filled_char"] * filled_blocks +
        PROGRESS_BAR_CONFIG["empty_char"] * empty_blocks
    )
    
    # Get status icon
    icon = PROGRESS_BAR_CONFIG["status_icons"].get(status, "🔄")
    
    # Build output parts
    parts = [icon, bar]
    
    if show_percentage:
        parts.append(f"{percentage:.1f}%")
    
    if show_counts:
        parts.append(f"({current}/{total})")
    
    return " ".join(parts)


def generate_phase_tracker(
    phases: list[tuple[str, StatusType]],
    current_phase: int = None
) -> str:
    """
    Generate a multi-phase progress tracker.
    
    Args:
        phases: List of (phase_name, status) tuples
        current_phase: Index of current phase (0-based), None if not tracking
    
    Returns:
        Multi-line formatted phase tracker
    
    Example:
        >>> phases = [
        ...     ("Discovery", "completed"),
        ...     ("Analysis", "in_progress"),
        ...     ("Implementation", "pending"),
        ...     ("Validation", "pending")
        ... ]
        >>> print(generate_phase_tracker(phases, 1))
        ✅ Discovery
        🔄 Analysis (Current)
        ⏳ Implementation
        ⏳ Validation
    """
    lines = []
    
    for idx, (phase_name, status) in enumerate(phases):
        icon = PROGRESS_BAR_CONFIG["status_icons"].get(status, "⏳")
        
        if current_phase is not None and idx == current_phase:
            lines.append(f"{icon} {phase_name} (Current)")
        else:
            lines.append(f"{icon} {phase_name}")
    
    return "\n".join(lines)


def generate_orchestrator_progress(
    orchestrator_name: str,
    phases: list[dict],
    show_details: bool = False
) -> str:
    """
    Generate orchestrator-specific progress display.
    
    Args:
        orchestrator_name: Name of orchestrator
        phases: List of phase dicts with keys: name, status, tasks_completed, tasks_total
        show_details: Include task progress bars for each phase
    
    Returns:
        Formatted orchestrator progress display
    
    Example:
        >>> phases = [
        ...     {"name": "Phase 1", "status": "completed", "tasks_completed": 5, "tasks_total": 5},
        ...     {"name": "Phase 2", "status": "in_progress", "tasks_completed": 2, "tasks_total": 4}
        ... ]
        >>> print(generate_orchestrator_progress("Planning", phases, show_details=True))
        ## 🧠 Planning Orchestrator Progress
        
        ✅ Phase 1
           ██████████ 100.0% (5/5)
        
        🔄 Phase 2
           █████░░░░░ 50.0% (2/4)
    """
    lines = [f"## 🧠 {orchestrator_name} Orchestrator Progress", ""]
    
    for phase in phases:
        icon = PROGRESS_BAR_CONFIG["status_icons"].get(phase["status"], "⏳")
        lines.append(f"{icon} {phase['name']}")
        
        if show_details and "tasks_completed" in phase and "tasks_total" in phase:
            bar = generate_progress_bar(
                phase["tasks_completed"],
                phase["tasks_total"],
                status=phase["status"],
                show_percentage=True,
                show_counts=True
            )
            # Remove icon from bar since we already have phase icon
            bar_without_icon = " ".join(bar.split()[1:])
            lines.append(f"   {bar_without_icon}")
        
        lines.append("")
    
    return "\n".join(lines)


def calculate_overall_progress(phases: list[dict]) -> tuple[int, int, float]:
    """
    Calculate overall progress across multiple phases.
    
    Args:
        phases: List of phase dicts with keys: tasks_completed, tasks_total
    
    Returns:
        (total_completed, total_tasks, percentage)
    
    Example:
        >>> phases = [
        ...     {"tasks_completed": 5, "tasks_total": 5},
        ...     {"tasks_completed": 2, "tasks_total": 4},
        ...     {"tasks_completed": 0, "tasks_total": 3}
        ... ]
        >>> calculate_overall_progress(phases)
        (7, 12, 58.33333333333334)
    """
    total_completed = sum(p.get("tasks_completed", 0) for p in phases)
    total_tasks = sum(p.get("tasks_total", 0) for p in phases)
    percentage = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
    
    return total_completed, total_tasks, percentage


# Example usage and test cases
def demo():
    """Demonstrate progress bar generator capabilities."""
    print("# CORTEX Progress Bar Generator Demo")
    print()
    
    print("## Basic Progress Bars")
    print()
    print("0/10:", generate_progress_bar(0, 10, status="pending"))
    print("3/10:", generate_progress_bar(3, 10, status="in_progress"))
    print("7/10:", generate_progress_bar(7, 10, status="in_progress"))
    print("10/10:", generate_progress_bar(10, 10, status="completed"))
    print("Failed:", generate_progress_bar(4, 10, status="failed"))
    print()
    
    print("## Phase Tracker")
    print()
    phases = [
        ("Discovery", "completed"),
        ("Analysis", "completed"),
        ("Implementation", "in_progress"),
        ("Testing", "pending"),
        ("Documentation", "pending")
    ]
    print(generate_phase_tracker(phases, current_phase=2))
    print()
    
    print("## Orchestrator Progress")
    print()
    orchestrator_phases = [
        {
            "name": "Phase 1: Setup",
            "status": "completed",
            "tasks_completed": 5,
            "tasks_total": 5
        },
        {
            "name": "Phase 2: Implementation",
            "status": "in_progress",
            "tasks_completed": 3,
            "tasks_total": 7
        },
        {
            "name": "Phase 3: Validation",
            "status": "pending",
            "tasks_completed": 0,
            "tasks_total": 4
        }
    ]
    print(generate_orchestrator_progress("Planning", orchestrator_phases, show_details=True))
    
    # Calculate overall
    completed, total, percentage = calculate_overall_progress(orchestrator_phases)
    print(f"**Overall Progress:** {generate_progress_bar(completed, total, status='in_progress')}")


if __name__ == "__main__":
    demo()
