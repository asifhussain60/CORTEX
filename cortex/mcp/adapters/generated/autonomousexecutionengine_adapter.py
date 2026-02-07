"""
MCP Adapter for AutonomousExecutionEngine

Generated adapter for AutonomousExecutionEngine.
AC-ID: AC-PHASE2B-002
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.domain.autonomous_execution_engine import AutonomousExecutionEngine
import logging
import time

logger = logging.getLogger(__name__)


def _get_orchestrator_from_wiring(name: str) -> Optional[Any]:
    """Get orchestrator from wiring system (CORE-035: Single execution path)."""
    try:
        from cortex.wiring import bootstrap_cortex
        registry = bootstrap_cortex()
        return registry.get_orchestrator(name)
    except Exception as e:
        logger.warning(f"Failed to get {name} from wiring: {e}")
        return None


class AutonomousExecutionEngineAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for AutonomousExecutionEngine.
    
    Exposes capabilities:
    - execute_autonomous: Execute autonomous operation
    - get_execution_plan: Generate execution plan
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[AutonomousExecutionEngine] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("AutonomousExecutionEngine")
        self.name = "AutonomousExecutionEngineAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="execute_autonomous",
                orchestrator="execute",
                description="Execute autonomous operation",
                input_schema={'task': {'type': 'string', 'description': 'task parameter'}, 'constraints': {'type': 'string', 'description': 'constraints parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["execute_autonomous", "execute autonomous"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="get_execution_plan",
                orchestrator="get",
                description="Generate execution plan",
                input_schema={'objective': {'type': 'string', 'description': 'objective parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["get_execution_plan", "get execution plan"],
                tags={"generated", "phase2b"},
            )
        ]
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> CapabilityResponse:
        """Execute a capability."""
        start = time.time()
        try:
            if not self.orchestrator:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    error="Orchestrator not available",
                    orchestrator="autonomousexecutionengine",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "execute_autonomous":
                result = self.orchestrator.execute_autonomous(task=parameters.get('task'), constraints=parameters.get('constraints'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "get_execution_plan":
                result = self.orchestrator.get_execution_plan(objective=parameters.get('objective'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=f"Unknown capability: {capability_name}",
                orchestrator="autonomousexecutionengine",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="autonomousexecutionengine",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
