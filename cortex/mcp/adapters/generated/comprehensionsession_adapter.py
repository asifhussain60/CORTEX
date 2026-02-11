"""
MCP Adapter for ComprehensionSession

Generated adapter for ComprehensionSession.
AC-ID: AC-PHASE2B-006
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
from cortex.orchestrators.core.comprehension_session import ComprehensionSession

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


class ComprehensionSessionAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for ComprehensionSession.

    Exposes capabilities:
    - start_session: Start comprehension session
    - track_understanding: Track user understanding

    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """

    def __init__(self, orchestrator: Optional[ComprehensionSession] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("ComprehensionSession")
        self.name = "ComprehensionSessionAdapter"

    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="start_session",
                orchestrator="start",
                description="Start comprehension session",
                input_schema={'context': {'type': 'string', 'description': 'context parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["start_session", "start session"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="track_understanding",
                orchestrator="track",
                description="Track user understanding",
                input_schema={'session_id': {'type': 'string', 'description': 'session_id parameter'}, 'metrics': {'type': 'string', 'description': 'metrics parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["track_understanding", "track understanding"],
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
                    orchestrator="comprehensionsession",
                    duration_ms=(time.time() - start) * 1000,
                )

            if capability_name == "start_session":
                result = self.orchestrator.start_session(context=parameters.get('context'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "track_understanding":
                result = self.orchestrator.track_understanding(session_id=parameters.get('session_id'), metrics=parameters.get('metrics'))
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
                orchestrator="comprehensionsession",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="comprehensionsession",
                duration_ms=(time.time() - start) * 1000,
            )

    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
