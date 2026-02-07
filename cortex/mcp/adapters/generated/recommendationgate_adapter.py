"""
MCP Adapter for RecommendationGate

Generated adapter for RecommendationGate.
AC-ID: AC-PHASE2B-011
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.core.recommendation_gate import RecommendationGate
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


class RecommendationGateAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for RecommendationGate.
    
    Exposes capabilities:
    - validate_recommendation: Validate recommendation safety
    - check_rejection_history: Check rejection history
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[RecommendationGate] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("RecommendationGate")
        self.name = "RecommendationGateAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="validate_recommendation",
                orchestrator="validate",
                description="Validate recommendation safety",
                input_schema={'recommendation': {'type': 'string', 'description': 'recommendation parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["validate_recommendation", "validate recommendation"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="check_rejection_history",
                orchestrator="check",
                description="Check rejection history",
                input_schema={'recommendation_id': {'type': 'string', 'description': 'recommendation_id parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["check_rejection_history", "check rejection history"],
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
                    orchestrator="recommendationgate",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "validate_recommendation":
                result = self.orchestrator.validate_recommendation(recommendation=parameters.get('recommendation'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "check_rejection_history":
                result = self.orchestrator.check_rejection_history(recommendation_id=parameters.get('recommendation_id'))
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
                orchestrator="recommendationgate",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="recommendationgate",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
