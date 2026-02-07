"""
MCP Adapter for DebuggingOrchestrator

Generated adapter for DebuggingOrchestrator.
AC-ID: AC-PHASE2B-014
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.support.debugging_orchestrator import DebuggingOrchestrator
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


class DebuggingOrchestratorAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for DebuggingOrchestrator.
    
    Exposes capabilities:
    - inject_debug_markers: Inject debug markers
    - analyze_debug_output: Analyze debug output
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[DebuggingOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("DebuggingOrchestrator")
        self.name = "DebuggingOrchestratorAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="inject_debug_markers",
                orchestrator="inject",
                description="Inject debug markers",
                input_schema={'file_path': {'type': 'string', 'description': 'file_path parameter'}, 'strategy': {'type': 'string', 'description': 'strategy parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["inject_debug_markers", "inject debug markers"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="analyze_debug_output",
                orchestrator="analyze",
                description="Analyze debug output",
                input_schema={'markers': {'type': 'string', 'description': 'markers parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["analyze_debug_output", "analyze debug output"],
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
                    orchestrator="debuggingorchestrator",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "inject_debug_markers":
                result = self.orchestrator.inject_debug_markers(file_path=parameters.get('file_path'), strategy=parameters.get('strategy'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "analyze_debug_output":
                result = self.orchestrator.analyze_debug_output(markers=parameters.get('markers'))
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
                orchestrator="debuggingorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="debuggingorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
