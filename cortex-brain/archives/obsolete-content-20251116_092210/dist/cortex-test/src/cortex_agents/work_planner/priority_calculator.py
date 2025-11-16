"""Task priority calculation."""

from typing import Dict, Any
from ..agent_types import Priority


class PriorityCalculator:
    """Calculates task priorities."""
    
    def calculate(self, task: Dict[str, Any], task_index: int, total_tasks: int) -> Priority:
        """
        Calculate task priority based on position and characteristics.
        
        Args:
            task: The task to prioritize
            task_index: Position in task list (0-based)
            total_tasks: Total number of tasks
        
        Returns:
            Priority level
        """
        # Early tasks are generally higher priority
        if task_index < total_tasks * 0.3:
            return Priority.HIGH
        elif task_index < total_tasks * 0.7:
            return Priority.MEDIUM
        else:
            return Priority.LOW
