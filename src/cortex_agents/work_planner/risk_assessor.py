"""Risk assessment for tasks."""

from typing import Dict, Any, List


class RiskAssessor:
    """Assesses execution risks for tasks."""
    
    def assess(
        self,
        tasks: List[Dict[str, Any]],
        complexity: str,
        file_count: int
    ) -> List[Dict[str, Any]]:
        """
        Assess risks for task execution.
        
        Args:
            tasks: List of tasks
            complexity: Overall complexity level
            file_count: Number of files involved
        
        Returns:
            Tasks with risk assessments added
        """
        risk_factors = []
        
        # Complexity-based risks
        if complexity == "complex":
            risk_factors.append("High complexity may lead to unexpected challenges")
            risk_factors.append("Consider architecture review before implementation")
        
        # Multi-file risks
        if file_count > 5:
            risk_factors.append(f"Multiple files ({file_count}) increase coordination overhead")
            risk_factors.append("Ensure proper testing across all modified files")
        
        # Task count risks
        if len(tasks) > 10:
            risk_factors.append("Large number of tasks may indicate scope creep")
            risk_factors.append("Consider breaking into smaller milestones")
        
        # Add risks to each task
        for task in tasks:
            task["risks"] = []
            
            # Long duration tasks are risky
            if task.get("estimated_hours", 0) > 4:
                task["risks"].append("Long duration - consider splitting")
            
            # Tasks with many dependencies
            if len(task.get("dependencies", [])) > 2:
                task["risks"].append("Multiple dependencies may cause delays")
        
        return tasks, risk_factors
