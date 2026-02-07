"""
MCP Adapter for OrchestratorVisibility

Generated adapter for OrchestratorVisibility.
AC-ID: AC-PHASE2B-015
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.support.orchestrator_visibility import OrchestratorVisibility
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


class OrchestratorVisibilityAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for OrchestratorVisibility.
    
    Exposes capabilities:
    - get_visibility_report: Get orchestrator visibility report
    - track_usage: Track orchestrator usage
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[OrchestratorVisibility] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("OrchestratorVisibility")
        self.name = "OrchestratorVisibilityAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="get_visibility_report",
                orchestrator="get",
                description="Get orchestrator visibility report",
                input_schema={'scope': {'type': 'string', 'description': 'scope parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["get_visibility_report", "get visibility report"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="track_usage",
                orchestrator="track",
                description="Track orchestrator usage",
                input_schema={'orchestrator_name': {'type': 'string', 'description': 'orchestrator_name parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["track_usage", "track usage"],
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
                    orchestrator="orchestratorvisibility",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "get_visibility_report":
                result = self.orchestrator.get_visibility_report(scope=parameters.get('scope'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "track_usage":
                result = self.orchestrator.track_usage(orchestrator_name=parameters.get('orchestrator_name'))
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
                orchestrator="orchestratorvisibility",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="orchestratorvisibility",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
