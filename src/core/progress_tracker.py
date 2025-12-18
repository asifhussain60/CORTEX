"""
CORTEX 4.0 Migration Progress Tracker
Updates MASTER-PLAN.md status visualization after phase completion.

Author: Asif Hussain
Version: 1.0
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class ProgressTracker:
    """Update MASTER-PLAN.md progress visualization."""
    
    MASTER_PLAN_PATH = Path(__file__).parent.parent.parent / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0" / "MASTER-PLAN.md"
    
    PHASE_NAMES = {
        "0": "Pre-Migration Cleanup",
        "1": "Foundation",
        "1.5": "Documentation & Visualization",
        "2": "Brain Enhancement + RAG",
        "3": "Orchestrator Consolidation",
        "4": "Operations Simplification",
        "5": "Testing & Validation",
        "6": "Documentation Finalization"
    }
    
    @staticmethod
    def _create_progress_bar(percentage: int, width: int = 12) -> str:
        """Create visual progress bar: [████░░░░] percentage%"""
        filled = int((percentage / 100) * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {percentage:3d}%"
    
    @staticmethod
    def _get_status_icon(percentage: int) -> str:
        """Get status icon based on completion."""
        if percentage == 100:
            return "✅ COMPLETE"
        elif percentage > 0:
            return "⏳ ACTIVE"
        else:
            return "☐ PENDING"
    
    @classmethod
    def update_progress(
        cls,
        phase: str,
        week: Optional[str] = None,
        completion_percentage: int = 0,
        week_completion: Optional[int] = None,
        milestone_completed: Optional[str] = None,
        metrics: Optional[Dict[str, any]] = None
    ) -> bool:
        """
        Update MASTER-PLAN.md progress tracker.
        
        Args:
            phase: Phase number (0, 1, 1.5, 2, 3, 4, 5, 6)
            week: Week number within phase (optional)
            completion_percentage: Phase completion % (0-100)
            week_completion: Week completion % if updating specific week
            milestone_completed: Milestone name if achieved
            metrics: Dict with orchestrators_migrated, test_coverage, docs_generated, lines_reduced
        
        Returns:
            True if update successful
        """
        if not cls.MASTER_PLAN_PATH.exists():
            print(f"❌ MASTER-PLAN.md not found at {cls.MASTER_PLAN_PATH}")
            return False
        
        content = cls.MASTER_PLAN_PATH.read_text(encoding="utf-8")
        
        # Update timestamp and current phase
        timestamp = datetime.now().strftime("%B %d, %Y")
        overall_completion = cls._calculate_overall_completion(content, phase, completion_percentage)
        
        content = re.sub(
            r"\*\*Last Updated:\*\* .+? \| \*\*Current Phase:\*\* .+? \| \*\*Week:\*\* .+? \| \*\*Overall:\*\* .+?%",
            f"**Last Updated:** {timestamp} | **Current Phase:** Phase {phase} ({cls.PHASE_NAMES[phase]}) | **Week:** {week or 'N/A'} | **Overall:** {overall_completion}% Complete",
            content
        )
        
        # Update phase progress bar
        phase_pattern = rf"(│ PHASE {re.escape(phase)}: {re.escape(cls.PHASE_NAMES[phase])}\s+)\[.+?\]\s+\d+%"
        phase_bar = cls._create_progress_bar(completion_percentage)
        content = re.sub(phase_pattern, rf"\1{phase_bar}", content)
        
        # Update phase status icon if 100%
        if completion_percentage == 100:
            status_pattern = rf"(│ PHASE {re.escape(phase)}:.+?)(?:⏳ ACTIVE|☐ PENDING)"
            content = re.sub(status_pattern, r"\1✅ COMPLETE", content)
        
        # Update week progress if specified
        if week and week_completion is not None:
            week_pattern = rf"(│ Week {re.escape(week)}:.+?)\[.+?\]\s+\d+%\s+(?:⏳ ACTIVE|☐ PENDING|✅ COMPLETE)"
            week_bar = cls._create_progress_bar(week_completion, width=5)
            week_status = cls._get_status_icon(week_completion)
            content = re.sub(week_pattern, rf"\1{week_bar}  {week_status}", content)
        
        # Update milestone if completed
        if milestone_completed:
            milestone_pattern = rf"(├─ ☐ {re.escape(milestone_completed)})"
            content = re.sub(milestone_pattern, rf"├─ ✅ {milestone_completed}", content)
        
        # Update metrics if provided
        if metrics:
            if "orchestrators_migrated" in metrics:
                content = re.sub(
                    r"├─ Orchestrators Migrated: \d+/\d+ \(\d+%\)",
                    f"├─ Orchestrators Migrated: {metrics['orchestrators_migrated']}/13 ({int(metrics['orchestrators_migrated']/13*100)}%)",
                    content
                )
            if "test_coverage" in metrics:
                content = re.sub(
                    r"├─ Test Coverage: .+",
                    f"├─ Test Coverage: {metrics['test_coverage']}",
                    content
                )
            if "docs_generated" in metrics:
                content = re.sub(
                    r"├─ Documentation: \d+/\d+\+ docs generated",
                    f"├─ Documentation: {metrics['docs_generated']}/200+ docs generated",
                    content
                )
            if "lines_reduced" in metrics:
                content = re.sub(
                    r"└─ Lines Reduced: .+",
                    f"└─ Lines Reduced: {metrics['lines_reduced']} (Target: -40% bloat)",
                    content
                )
        
        # Write updated content
        cls.MASTER_PLAN_PATH.write_text(content, encoding="utf-8")
        print(f"✅ Updated MASTER-PLAN.md progress: Phase {phase} = {completion_percentage}%")
        return True
    
    @staticmethod
    def _calculate_overall_completion(content: str, current_phase: str, phase_completion: int) -> int:
        """Calculate overall migration completion percentage."""
        # Phase weights (based on duration)
        weights = {
            "0": 5,   # 1 week
            "1": 15,  # 3 weeks
            "1.5": 5, # 1 week
            "2": 25,  # 5 weeks
            "3": 25,  # 5 weeks
            "4": 15,  # 3 weeks
            "5": 15,  # 3 weeks
            "6": 5    # 1 week
        }
        
        # Extract all phase percentages from content
        phase_percentages = {}
        for phase in weights.keys():
            match = re.search(rf"PHASE {re.escape(phase)}:.+?\[.+?\]\s+(\d+)%", content)
            if match:
                phase_percentages[phase] = int(match.group(1))
            else:
                phase_percentages[phase] = 0
        
        # Update current phase
        phase_percentages[current_phase] = phase_completion
        
        # Calculate weighted average
        total = sum(phase_percentages[p] * weights[p] for p in weights.keys())
        overall = total // sum(weights.values())
        return overall


def update_master_plan_progress(**kwargs):
    """Convenience function for orchestrators to call."""
    return ProgressTracker.update_progress(**kwargs)


if __name__ == "__main__":
    # Test update
    print("Testing progress tracker...")
    success = update_master_plan_progress(
        phase="1",
        week="1",
        completion_percentage=60,
        week_completion=60,
        metrics={
            "orchestrators_migrated": 0,
            "test_coverage": "10/10 foundation prerequisites passing",
            "docs_generated": 0,
            "lines_reduced": 0
        }
    )
    print(f"Update {'successful' if success else 'failed'}")
