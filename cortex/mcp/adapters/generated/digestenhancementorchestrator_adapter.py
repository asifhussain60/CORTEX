"""
MCP Adapter for DigestEnhancementOrchestrator

Generated adapter for DigestEnhancementOrchestrator.
AC-ID: AC-PHASE2B-016
"""

import logging
import time
from typing import Any, Dict, List, Optional

from cortex.mcp.orchestrator_mcp_server import (
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
    IOrchestratorAdapter,
)
from cortex.orchestrators.learning.digest_enhancement_orchestrator import (
    DigestEnhancementOrchestrator,
)

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


class DigestEnhancementOrchestratorAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for DigestEnhancementOrchestrator.

    Exposes capabilities:
    - digest_session: Digest session learnings
    - extract_patterns: Extract learning patterns

    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """

    def __init__(self, orchestrator: Optional[DigestEnhancementOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("DigestEnhancementOrchestrator")
        self.name = "DigestEnhancementOrchestratorAdapter"

    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="digest_session",
                orchestrator="digest",
                description="Digest session learnings",
                input_schema={'session_data': {'type': 'string', 'description': 'session_data parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["digest_session", "digest session"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="extract_patterns",
                orchestrator="extract",
                description="Extract learning patterns",
                input_schema={'digest_id': {'type': 'string', 'description': 'digest_id parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["extract_patterns", "extract patterns"],
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
                    orchestrator="digestenhancementorchestrator",
                    duration_ms=(time.time() - start) * 1000,
                )

            if capability_name == "digest_session":
                result = self.orchestrator.digest_session(session_data=parameters.get('session_data'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "extract_patterns":
                result = self.orchestrator.extract_patterns(digest_id=parameters.get('digest_id'))
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
                orchestrator="digestenhancementorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="digestenhancementorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )

    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
