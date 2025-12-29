"""
Plan index generator for auto-generating INDEX.md.

This module generates planning/INDEX.md with plans grouped by status
in markdown table format.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List


class PlanIndexGenerator:
    """
    Generates planning index with status-grouped tables.
    
    Creates INDEX.md at planning/ root with:
    - Plans grouped by status (In Progress, Completed, Proposed, Cancelled)
    - Markdown table format: ID | Title | Priority | Link
    - Sorted by priority within each status
    """
    
    # Status display mapping
    STATUS_HEADERS = {
        "in-progress": "In Progress",
        "completed": "Completed",
        "proposed": "Proposed",
        "approved": "Approved",
        "cancelled": "Cancelled"
    }
    
    # Priority sorting order (high first)
    PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    
    def __init__(self, brain_path: Path):
        """
        Initialize index generator.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.planning_dir = self.brain_path / "documents" / "planning"
        self.index_path = self.planning_dir / "INDEX.md"
    
    def generate(self, registry) -> None:
        """
        Generate INDEX.md from plan registry.
        
        Args:
            registry: PlanRegistry instance
        """
        # Group plans by status
        plans_by_status = self._group_plans_by_status(registry)
        
        # Generate markdown content
        content = self._generate_markdown(plans_by_status)
        
        # Write to INDEX.md
        self.planning_dir.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(content)
    
    def _group_plans_by_status(self, registry) -> Dict[str, List[Dict]]:
        """
        Group plans by status.
        
        Args:
            registry: PlanRegistry instance
            
        Returns:
            Dictionary mapping status to list of plans
        """
        all_plans = registry.list_plans()
        
        grouped = {}
        for plan in all_plans:
            status = plan["status"]
            if status not in grouped:
                grouped[status] = []
            grouped[status].append(plan)
        
        # Sort each group by priority
        for status in grouped:
            grouped[status].sort(
                key=lambda p: self.PRIORITY_ORDER.get(p["priority"], 99)
            )
        
        return grouped
    
    def _generate_markdown(self, plans_by_status: Dict[str, List[Dict]]) -> str:
        """
        Generate markdown content for index.
        
        Args:
            plans_by_status: Plans grouped by status
            
        Returns:
            Markdown content string
        """
        lines = [
            "# Planning Index",
            "",
            f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Generate sections for each status
        for status, header in self.STATUS_HEADERS.items():
            if status not in plans_by_status or not plans_by_status[status]:
                continue  # Skip empty sections
            
            lines.append(f"## {header}")
            lines.append("")
            lines.append("| ID | Title | Priority | Link |")
            lines.append("|---|---|---|---|")
            
            for plan in plans_by_status[status]:
                # Extract filename from file_path for link
                file_path = Path(plan["file_path"])
                link = f"[View]({file_path.name})"
                
                lines.append(
                    f"| {plan['plan_id']} | {plan['title']} | "
                    f"{plan['priority']} | {link} |"
                )
            
            lines.append("")
        
        return "\n".join(lines)
