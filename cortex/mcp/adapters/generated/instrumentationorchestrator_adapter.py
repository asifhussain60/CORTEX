"""
MCP Adapter for InstrumentationOrchestrator

Generated adapter for InstrumentationOrchestrator.
AC-ID: AC-PHASE2B-013
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
from cortex.orchestrators.support.instrumentation_orchestrator import (
    InstrumentationOrchestrator,
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


class InstrumentationOrchestratorAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for InstrumentationOrchestrator.

    Exposes capabilities:
    - instrument_code: Add instrumentation to code
    - collect_metrics: Collect instrumentation metrics

    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """

    def __init__(self, orchestrator: Optional[InstrumentationOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("InstrumentationOrchestrator")
        self.name = "InstrumentationOrchestratorAdapter"

    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="instrument_code",
                orchestrator="instrument",
                description="Add instrumentation to code",
                input_schema={'file_path': {'type': 'string', 'description': 'file_path parameter'}, 'config': {'type': 'string', 'description': 'config parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["instrument_code", "instrument code"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="collect_metrics",
                orchestrator="collect",
                description="Collect instrumentation metrics",
                input_schema={'scope': {'type': 'string', 'description': 'scope parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["collect_metrics", "collect metrics"],
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
                    orchestrator="instrumentationorchestrator",
                    duration_ms=(time.time() - start) * 1000,
                )

            if capability_name == "instrument_code":
                result = self.orchestrator.instrument_code(file_path=parameters.get('file_path'), config=parameters.get('config'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "collect_metrics":
                result = self.orchestrator.collect_metrics(scope=parameters.get('scope'))
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
                orchestrator="instrumentationorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="instrumentationorchestrator",
                duration_ms=(time.time() - start) * 1000,
            )

    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
