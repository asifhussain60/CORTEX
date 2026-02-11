"""
MCP Adapter for VacuumOrchestrator

Generated adapter for VacuumOrchestrator.
AC-ID: AC-PHASE2B-012
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
from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator

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


class VacuumOrchestratorAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for VacuumOrchestrator.

    Exposes capabilities:
    - vacuum_artifacts: Clean up generated artifacts
    - get_cleanup_report: Get cleanup report

    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """

    def __init__(self, orchestrator: Optional[VacuumOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("VacuumOrchestrator")
        self.name = "VacuumOrchestratorAdapter"

    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="vacuum_artifacts",
                orchestrator="vacuum",
                description="Clean up generated artifacts",
                input_schema={'scope': {'type': 'string', 'description': 'scope parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["vacuum_artifacts", "vacuum artifacts"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="get_cleanup_report",
                orchestrator="get",
                description="Get cleanup report",
                input_schema={'session_id': {'type': 'string', 'description': 'session_id parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["get_cleanup_report", "get cleanup report"],
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
                    orchestrator="vacuumorchestrator",
                    duration_ms=(time.time() - start) * 1000,
                )

            if capability_name == "vacuum_artifacts":
                result = self.orchestrator.vacuum_artifacts(scope=parameters.get('scope'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "get_cleanup_report":
                result = self.orchestrator.get_cleanup_report(session_id=parameters.get('session_id'))
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
                orchestrator="vacuumorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="vacuumorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )

    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
