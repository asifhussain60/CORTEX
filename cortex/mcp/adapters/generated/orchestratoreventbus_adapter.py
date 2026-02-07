"""
MCP Adapter for OrchestratorEventBus

Generated adapter for OrchestratorEventBus.
AC-ID: AC-PHASE2B-003
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.infrastructure.orchestrator_event_bus import OrchestratorEventBus
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


class OrchestratorEventBusAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for OrchestratorEventBus.
    
    Exposes capabilities:
    - publish_event: Publish event to bus
    - subscribe: Subscribe to events
    - get_event_history: Get event history
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[OrchestratorEventBus] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("OrchestratorEventBus")
        self.name = "OrchestratorEventBusAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="publish_event",
                orchestrator="publish",
                description="Publish event to bus",
                input_schema={'event_type': {'type': 'string', 'description': 'event_type parameter'}, 'data': {'type': 'string', 'description': 'data parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["publish_event", "publish event"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="subscribe",
                orchestrator="subscribe",
                description="Subscribe to events",
                input_schema={'event_type': {'type': 'string', 'description': 'event_type parameter'}, 'handler': {'type': 'string', 'description': 'handler parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["subscribe", "subscribe"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="get_event_history",
                orchestrator="get",
                description="Get event history",
                input_schema={'filters': {'type': 'string', 'description': 'filters parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["get_event_history", "get event history"],
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
                    orchestrator="orchestratoreventbus",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "publish_event":
                result = self.orchestrator.publish_event(event_type=parameters.get('event_type'), data=parameters.get('data'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "subscribe":
                result = self.orchestrator.subscribe(event_type=parameters.get('event_type'), handler=parameters.get('handler'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "get_event_history":
                result = self.orchestrator.get_event_history(filters=parameters.get('filters'))
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
                orchestrator="orchestratoreventbus",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="orchestratoreventbus",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
