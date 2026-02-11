"""
Orchestrator Composite - Coordinates multiple orchestrators.

Routes requests to conversation, domain, and workflow orchestrators.
"""

from datetime import datetime
from typing import Any, Dict, List

from cortex.domain_orchestrators.domain_orchestrator import DomainOrchestrator
from cortex.orchestrators.conversation_orchestrator import ConversationOrchestrator
from cortex.orchestrators.core.workflow_orchestrator import WorkflowOrchestrator


class OrchestratorComposite:
    """
    Composite that coordinates multiple orchestrators.
    """

    def __init__(self) -> None:
        """Initialize the composite orchestrator."""
        self.conversation_orch = ConversationOrchestrator()
        self.domain_orch = DomainOrchestrator()
        self.workflow_orch = WorkflowOrchestrator()
        self.orchestrators: List[str] = ["conversation", "domain", "workflow"]
        self.request_count = 0

    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request by routing to appropriate orchestrator.

        Args:
            request: Request with type field indicating orchestrator.

        Returns:
            Response from appropriate orchestrator.
        """
        self.request_count += 1
        request_type = request.get("type", "unknown")

        if request_type == "conversation":
            return self.conversation_orch.process_turn(request)
        elif request_type == "domain":
            return self.domain_orch.route_request(request)
        elif request_type == "workflow":
            return self._handle_workflow_request(request)
        else:
            return {
                "error": f"Unknown request type: {request_type}",
                "timestamp": datetime.now().isoformat(),
            }

    def _handle_workflow_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a workflow request."""
        workflow_id = request.get("workflow_id", "unknown")
        action = request.get("action")

        if action == "create":
            steps = request.get("steps", [])
            self.workflow_orch.create_workflow(str(workflow_id), steps)
            return {"status": "created", "workflow_id": workflow_id}
        elif action == "execute":
            return self.workflow_orch.execute_workflow(str(workflow_id))
        else:
            return {"error": f"Unknown workflow action: {action}"}

    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from all orchestrators.

        Returns:
            Combined metrics from all orchestrators.
        """
        conv_history = len(self.conversation_orch.conversation_history)
        domain_metrics = self.domain_orch.get_metrics()
        workflow_count = len(self.workflow_orch.active_workflows)

        return {
            "total_requests": self.request_count,
            "conversation_turns": conv_history,
            "domain_requests": domain_metrics.get("total_requests", 0),
            "workflow_count": workflow_count,
            "timestamp": datetime.now().isoformat(),
        }
