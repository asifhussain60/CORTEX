"""
MCP Adapter for EducationalOrchestrator

Generated adapter for EducationalOrchestrator.
AC-ID: AC-PHASE2B-009
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.education.educational_orchestrator import EducationalOrchestrator
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


class EducationalOrchestratorAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for EducationalOrchestrator.
    
    Exposes capabilities:
    - provide_guidance: Provide educational guidance
    - assess_understanding: Assess user understanding
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[EducationalOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("EducationalOrchestrator")
        self.name = "EducationalOrchestratorAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="provide_guidance",
                orchestrator="provide",
                description="Provide educational guidance",
                input_schema={'topic': {'type': 'string', 'description': 'topic parameter'}, 'level': {'type': 'string', 'description': 'level parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["provide_guidance", "provide guidance"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="assess_understanding",
                orchestrator="assess",
                description="Assess user understanding",
                input_schema={'topic': {'type': 'string', 'description': 'topic parameter'}, 'responses': {'type': 'string', 'description': 'responses parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["assess_understanding", "assess understanding"],
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
                    orchestrator="educationalorchestrator",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "provide_guidance":
                result = self.orchestrator.provide_guidance(topic=parameters.get('topic'), level=parameters.get('level'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "assess_understanding":
                result = self.orchestrator.assess_understanding(topic=parameters.get('topic'), responses=parameters.get('responses'))
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
                orchestrator="educationalorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="educationalorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
