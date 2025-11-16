"""Pattern storage for workflow learning."""

from typing import Dict, Any, List
from datetime import datetime
import logging


class PatternStorage:
    """Stores workflow patterns in Tier 2 for learning."""
    
    def __init__(self, tier2_kg=None):
        """Initialize with Tier 2 knowledge graph."""
        self.tier2 = tier2_kg
        self.logger = logging.getLogger(__name__)
    
    def store(
        self,
        request_context: Dict[str, Any],
        tasks: List[Dict[str, Any]],
        complexity: str,
        total_hours: float
    ) -> None:
        """
        Store workflow pattern in Tier 2 for learning.
        
        Args:
            request_context: Original request context
            tasks: Generated task list
            complexity: Complexity level
            total_hours: Total estimated hours
        """
        if not self.tier2:
            return
        
        try:
            pattern_data = {
                "type": "workflow",
                "complexity": complexity,
                "task_count": len(tasks),
                "total_hours": total_hours,
                "timestamp": datetime.now().isoformat(),
                "tasks": [
                    {
                        "name": t.get("name"),
                        "hours": t.get("estimated_hours"),
                        "dependencies": t.get("dependencies", [])
                    }
                    for t in tasks
                ]
            }
            
            self.logger.debug(f"Storing workflow pattern: {pattern_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to store workflow pattern: {str(e)}")
