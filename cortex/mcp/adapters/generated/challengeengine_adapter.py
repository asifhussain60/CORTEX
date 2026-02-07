"""
MCP Adapter for ChallengeEngine

Generated adapter for ChallengeEngine.
AC-ID: AC-PHASE2B-008
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.core.challenge_engine import ChallengeEngine
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


class ChallengeEngineAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for ChallengeEngine.
    
    Exposes capabilities:
    - generate_challenge: Generate design challenge
    - evaluate_response: Evaluate challenge response
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[ChallengeEngine] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("ChallengeEngine")
        self.name = "ChallengeEngineAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="generate_challenge",
                orchestrator="generate",
                description="Generate design challenge",
                input_schema={'design_data': {'type': 'string', 'description': 'design_data parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["generate_challenge", "generate challenge"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="evaluate_response",
                orchestrator="evaluate",
                description="Evaluate challenge response",
                input_schema={'challenge_id': {'type': 'string', 'description': 'challenge_id parameter'}, 'response': {'type': 'string', 'description': 'response parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["evaluate_response", "evaluate response"],
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
                    orchestrator="challengeengine",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "generate_challenge":
                result = self.orchestrator.generate_challenge(design_data=parameters.get('design_data'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "evaluate_response":
                result = self.orchestrator.evaluate_response(challenge_id=parameters.get('challenge_id'), response=parameters.get('response'))
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
                orchestrator="challengeengine",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="challengeengine",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
