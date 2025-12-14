"""
Progress Visualizer - Visual representations of operation progress.

Generates progress bars, phase timelines, and completion charts
for multi-phase operations.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProgressVisualizer:
    """Generate progress visualizations."""
    
    def generate_progress_bar(
        self,
        current: int,
        total: int,
        width: int = 50
    ) -> str:
        """
        Generate ASCII progress bar.
        
        Args:
            current: Current progress value
            total: Total progress value
            width: Bar width in characters
            
        Returns:
            ASCII progress bar string
        """
        percent = (current / total) * 100 if total > 0 else 0
        filled = int((current / total) * width) if total > 0 else 0
        bar = "█" * filled + "░" * (width - filled)
        
        return f"[{bar}] {percent:.0f}% ({current}/{total})"
        
    def generate_phase_timeline(
        self,
        phases: List[Dict[str, Any]]
    ) -> str:
        """
        Generate Gantt-style phase timeline.
        
        Args:
            phases: List of phase dicts with name, id, status, start, end
            
        Returns:
            Mermaid Gantt chart
        """
        lines = ["gantt"]
        lines.append("    title CORTEX Evolution - Phase Timeline")
        lines.append("    dateFormat HH:mm")
        lines.append("    section Phases")
        
        for phase in phases:
            status = phase.get('status', 'pending')
            
            if status == 'complete':
                status_mark = ":done"
            elif status == 'in_progress':
                status_mark = ":active"
            else:
                status_mark = ""
                
            start = phase.get('start', 'N/A')
            end = phase.get('end', 'N/A')
            name = phase.get('name', 'Unknown Phase')
            phase_id = phase.get('id', '0')
            
            if start != 'N/A' and end != 'N/A':
                lines.append(
                    f"    {name}{status_mark} :{phase_id}, {start}, {end}"
                )
            else:
                lines.append(f"    {name}{status_mark} :{phase_id}, 00:00, 01h")
                
        return "\n".join(lines)
        
    def generate_metrics_chart(
        self,
        metrics: Dict[str, Any]
    ) -> str:
        """
        Generate metrics visualization.
        
        Args:
            metrics: Dict of metric names to numeric values
            
        Returns:
            ASCII bar chart
        """
        lines = ["Metrics Summary:"]
        lines.append("=" * 50)
        
        # Filter numeric values only
        numeric_metrics = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
        
        if not numeric_metrics:
            lines.append("No numeric metrics available")
            return "\n".join(lines)
        
        max_value = max(numeric_metrics.values())
        
        for name, value in numeric_metrics.items():
            bar_length = int((value / max_value) * 30) if max_value > 0 else 0
            bar = "█" * bar_length
            lines.append(f"{name:.<30} {bar} {value}")
            
        return "\n".join(lines)
        
    def generate_completion_summary(
        self,
        total_phases: int,
        completed_phases: int,
        in_progress_phases: int,
        pending_phases: int
    ) -> str:
        """
        Generate visual completion summary.
        
        Args:
            total_phases: Total number of phases
            completed_phases: Number of completed phases
            in_progress_phases: Number of in-progress phases
            pending_phases: Number of pending phases
            
        Returns:
            Visual summary with progress bar and status breakdown
        """
        progress_bar = self.generate_progress_bar(completed_phases, total_phases, width=40)
        
        lines = ["Phase Completion Summary"]
        lines.append("=" * 50)
        lines.append(progress_bar)
        lines.append("")
        lines.append("Status Breakdown:")
        lines.append(f"  ✅ Completed:   {completed_phases:>3} phases")
        lines.append(f"  🟡 In Progress: {in_progress_phases:>3} phases")
        lines.append(f"  ⏳ Pending:     {pending_phases:>3} phases")
        lines.append(f"  📊 Total:       {total_phases:>3} phases")
        
        return "\n".join(lines)
