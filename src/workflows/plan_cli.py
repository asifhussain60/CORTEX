"""
Plan CLI commands for interacting with plan registry.

This module provides command-line interface for plan operations:
list, show, search, update.
"""

from pathlib import Path
from typing import Optional
from src.workflows.plan_registry import PlanRegistry
from src.workflows.plan_index_generator import PlanIndexGenerator


class PlanCLI:
    """
    Command-line interface for plan operations.
    
    Provides commands:
    - list: List plans with optional filters
    - show: Display plan details
    - search: Search plans by keyword
    - update: Update plan status
    """
    
    # Valid statuses
    VALID_STATUSES = {"proposed", "approved", "in-progress", "completed", "cancelled"}
    
    def __init__(self, brain_path: Path):
        """
        Initialize plan CLI.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.registry = PlanRegistry(brain_path)
        self.index_generator = PlanIndexGenerator(brain_path)
    
    def list_plans(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> str:
        """
        List plans with optional filters.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            
        Returns:
            Formatted table output
        """
        plans = self.registry.list_plans(status=status, priority=priority)
        
        if not plans:
            return "No plans found."
        
        # Format as table
        lines = [
            "Plan ID          | Title                    | Status        | Priority",
            "-" * 75
        ]
        
        for plan in plans:
            lines.append(
                f"{plan['plan_id']:<16} | {plan['title'][:24]:<24} | "
                f"{plan['status']:<13} | {plan['priority']}"
            )
        
        return "\n".join(lines)
    
    def show_plan(self, plan_id: str) -> str:
        """
        Display plan details.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Formatted plan details
        """
        plan = self.registry.get_plan(plan_id)
        
        if not plan:
            return f"Plan '{plan_id}' not found."
        
        # Format details
        lines = [
            f"Plan ID: {plan['plan_id']}",
            f"Title: {plan['title']}",
            f"Status: {plan['status']}",
            f"Priority: {plan['priority']}",
            f"Created: {plan['created_date']}",
            f"Estimated Hours: {plan['estimated_hours']}",
        ]
        
        if plan.get("updated_date"):
            lines.append(f"Updated: {plan['updated_date']}")
        
        if plan.get("actual_hours"):
            lines.append(f"Actual Hours: {plan['actual_hours']}")
        
        if plan.get("completion_percentage"):
            lines.append(f"Completion: {plan['completion_percentage']}%")
        
        if plan.get("assigned_to"):
            lines.append(f"Assigned To: {plan['assigned_to']}")
        
        lines.append(f"File: {plan['file_path']}")
        
        return "\n".join(lines)
    
    def search_plans(self, query: str) -> str:
        """
        Search plans by keyword.
        
        Args:
            query: Search term
            
        Returns:
            Formatted search results
        """
        plans = self.registry.search_plans(query)
        
        if not plans:
            return f"No plans found matching '{query}'."
        
        # Format as table (same as list)
        lines = [
            f"Search results for '{query}':",
            "",
            "Plan ID          | Title                    | Status        | Priority",
            "-" * 75
        ]
        
        for plan in plans:
            lines.append(
                f"{plan['plan_id']:<16} | {plan['title'][:24]:<24} | "
                f"{plan['status']:<13} | {plan['priority']}"
            )
        
        return "\n".join(lines)
    
    def update_plan_status(self, plan_id: str, new_status: str) -> str:
        """
        Update plan status.
        
        Args:
            plan_id: Plan identifier
            new_status: New status value
            
        Returns:
            Status message
        """
        # Validate status
        if new_status not in self.VALID_STATUSES:
            valid_list = ", ".join(sorted(self.VALID_STATUSES))
            return f"Invalid status '{new_status}'. Valid values: {valid_list}"
        
        # Update in registry
        success = self.registry.update_plan_status(plan_id, new_status)
        
        if not success:
            return f"Plan '{plan_id}' not found."
        
        # Regenerate index
        self.index_generator.generate(self.registry)
        
        return f"Plan '{plan_id}' status updated to '{new_status}'."
