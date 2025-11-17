"""Workflow pattern finder and extractor."""

from typing import Dict, Any, List
import logging
from ..base_agent import AgentRequest


class WorkflowFinder:
    """Finds similar workflow patterns from Tier 2."""
    
    def __init__(self, tier2_kg=None):
        """Initialize with Tier 2 knowledge graph."""
        self.tier2 = tier2_kg
        self.logger = logging.getLogger(__name__)
    
    def find_similar(self, request: AgentRequest, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar workflow patterns from Tier 2.
        
        Args:
            request: The agent request
            limit: Maximum number of patterns to return
        
        Returns:
            List of similar workflow patterns
        """
        if not self.tier2:
            return []
        
        try:
            # Search for workflow patterns
            results = self.tier2.search(
                f"workflow {request.user_message}",
                limit=limit
            )
            
            # Filter to workflow-type patterns
            workflows = [
                r for r in results
                if r.get("type") == "workflow"
            ]
            
            return workflows
        except Exception as e:
            self.logger.warning(f"Tier 2 workflow search failed: {str(e)}")
            return []
    
    def extract_tasks(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract tasks from a historical workflow pattern.
        
        Args:
            workflow: Workflow pattern from Tier 2
        
        Returns:
            List of tasks
        """
        # Workflow content should contain task list
        content = workflow.get("content", "")
        
        # Simple extraction - in real implementation, this would be more sophisticated
        tasks = []
        
        # Check if workflow has embedded task data
        if isinstance(content, dict) and "tasks" in content:
            tasks = content["tasks"]
        
        return tasks
