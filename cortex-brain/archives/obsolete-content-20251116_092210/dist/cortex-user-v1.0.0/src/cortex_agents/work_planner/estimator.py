"""Time estimation adjuster."""

from typing import Dict, Any, List, Optional


class Estimator:
    """Adjusts task time estimates based on complexity and velocity."""
    
    def adjust_estimates(
        self,
        tasks: List[Dict[str, Any]],
        complexity: str,
        velocity_data: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Adjust task time estimates based on complexity and velocity.
        
        Args:
            tasks: List of tasks with base_hours
            complexity: Complexity level
            velocity_data: Velocity metrics from Tier 3
        
        Returns:
            Tasks with adjusted estimated_hours
        """
        # Base complexity multipliers
        complexity_multipliers = {
            "simple": 0.8,
            "medium": 1.0,
            "complex": 1.5
        }
        
        multiplier = complexity_multipliers.get(complexity, 1.0)
        
        # Adjust for team velocity if available
        if velocity_data:
            avg_velocity = velocity_data.get("average_velocity", 15.0)
            
            # If velocity is low, increase estimates
            if avg_velocity < 10:
                multiplier *= 1.2
            elif avg_velocity > 20:
                multiplier *= 0.9
        
        # Apply adjustments
        for task in tasks:
            base_hours = task.get("base_hours", 1.0)
            task["estimated_hours"] = round(base_hours * multiplier, 1)
            
            # Add buffer for complex tasks
            if complexity == "complex":
                task["buffer_hours"] = round(task["estimated_hours"] * 0.2, 1)
        
        return tasks
