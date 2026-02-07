"""
MCP Adapter for InteractionOrchestratorEnhancement

Generated adapter for InteractionOrchestratorEnhancement.
AC-ID: AC-PHASE2B-004
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.core.interaction_orchestrator_enhancement import InteractionOrchestratorEnhancement
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


class InteractionOrchestratorEnhancementAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for InteractionOrchestratorEnhancement.
    
    Exposes capabilities:
    - enhance_interaction: Enhance user interaction
    - analyze_patterns: Analyze interaction patterns
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[InteractionOrchestratorEnhancement] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("InteractionOrchestratorEnhancement")
        self.name = "InteractionOrchestratorEnhancementAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="enhance_interaction",
                orchestrator="enhance",
                description="Enhance user interaction",
                input_schema={'interaction_data': {'type': 'string', 'description': 'interaction_data parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["enhance_interaction", "enhance interaction"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="analyze_patterns",
                orchestrator="analyze",
                description="Analyze interaction patterns",
                input_schema={'session_id': {'type': 'string', 'description': 'session_id parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["analyze_patterns", "analyze patterns"],
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
                    orchestrator="interactionorchestratorenhancement",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "enhance_interaction":
                result = self.orchestrator.enhance_interaction(interaction_data=parameters.get('interaction_data'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "analyze_patterns":
                result = self.orchestrator.analyze_patterns(session_id=parameters.get('session_id'))
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
                orchestrator="interactionorchestratorenhancement",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="interactionorchestratorenhancement",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
