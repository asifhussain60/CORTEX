"""Task dependency identification."""

from typing import Dict, Any, List


class DependencyManager:
    """Identifies and manages task dependencies."""
    
    def identify(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify dependencies between tasks.
        
        Args:
            tasks: List of tasks
        
        Returns:
            Tasks with dependency information added
        """
        # Common dependency patterns
        dependency_patterns = {
            "Define": [],  # Usually first
            "Design": [],
            "Create": ["Define", "Design"],
            "Implement": ["Create", "Define"],
            "Add": ["Create", "Implement"],
            "Write": ["Implement"],
            "Test": ["Implement", "Add"],
            "Update": ["Test"],
            "Document": ["Test"]
        }
        
        # Add dependencies based on task names
        for task in tasks:
            task["dependencies"] = []
            task_name = task.get("name", "")
            
            # Check for dependency keywords
            for keyword, deps in dependency_patterns.items():
                if keyword.lower() in task_name.lower():
                    task["dependencies"] = deps
                    break
        
        return tasks
