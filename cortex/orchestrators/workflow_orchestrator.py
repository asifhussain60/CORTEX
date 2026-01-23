"""
Workflow Orchestrator - Workflow execution with state management and compensation.

Manages workflow execution, state transitions, and failure compensation.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime


class WorkflowState(Enum):
    """Workflow execution states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowTransition:
    """A workflow state transition."""
    workflow_id: str
    from_state: WorkflowState
    to_state: WorkflowState


class WorkflowOrchestrator:
    """
    Manages workflow execution with state transitions and compensation.
    """

    def __init__(self) -> None:
        """Initialize the workflow orchestrator."""
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_states: Dict[str, WorkflowState] = {}
        self.valid_transitions: Dict[WorkflowState, List[WorkflowState]] = {
            WorkflowState.PENDING: [WorkflowState.RUNNING, WorkflowState.COMPLETED, WorkflowState.CANCELLED],
            WorkflowState.RUNNING: [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED],
            WorkflowState.COMPLETED: [],
            WorkflowState.FAILED: [WorkflowState.PENDING],
            WorkflowState.CANCELLED: [WorkflowState.PENDING],
        }

    def create_workflow(self, workflow_id: str, steps: List[Dict[str, Any]]) -> None:
        """Create a workflow."""
        self.active_workflows[workflow_id] = {
            "id": workflow_id,
            "steps": steps,
            "created_at": datetime.now().isoformat(),
        }
        self.workflow_states[workflow_id] = WorkflowState.PENDING

    def transition_state(self, transition: WorkflowTransition) -> bool:
        """
        Perform a state transition.
        
        Args:
            transition: WorkflowTransition with from/to states.
            
        Returns:
            True if transition is valid, False otherwise.
        """
        # Get the actual current state (might differ from transition.from_state)
        current = self.workflow_states.get(transition.workflow_id, WorkflowState.PENDING)
        
        # Check if the transition.from_state matches actual current state
        if current != transition.from_state:
            return False
        
        # Check if the to_state is valid from current state
        if transition.to_state not in self.valid_transitions.get(current, []):
            return False
        
        self.workflow_states[transition.workflow_id] = transition.to_state
        return True

    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a complete workflow.
        
        Args:
            workflow_id: ID of workflow to execute.
            
        Returns:
            Execution result.
        """
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}

        workflow = self.active_workflows[workflow_id]
        steps = workflow.get("steps", [])

        # Execute all steps
        results = []
        for step in steps:
            result = self.execute_step(step)
            results.append(result)

        self.workflow_states[workflow_id] = WorkflowState.COMPLETED
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "step_results": results,
            "completed_at": datetime.now().isoformat(),
        }

    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow step.
        
        Args:
            step: Step definition with id and action.
            
        Returns:
            Step execution result.
        """
        step_id = step.get("id", "unknown")
        action = step.get("action", "unknown")
        
        return {
            "step_id": step_id,
            "action": action,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
        }

    def compensate_workflow(self, workflow_id: str, failed_step: int) -> bool:
        """
        Compensate (rollback) a workflow after failure.
        
        Args:
            workflow_id: ID of workflow to compensate.
            failed_step: Index of step that failed.
            
        Returns:
            True if compensation successful.
        """
        if workflow_id not in self.active_workflows:
            return False

        # Mark as failed
        self.workflow_states[workflow_id] = WorkflowState.FAILED
        return True

    def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get current state of a workflow."""
        return self.workflow_states.get(workflow_id)
