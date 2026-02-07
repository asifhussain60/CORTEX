"""
MCP Adapter for DuplicationDetector

Generated adapter for DuplicationDetector.
AC-ID: AC-PHASE2B-010
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.support.duplication_detector_orchestrator import DuplicationDetectorOrchestrator
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


class DuplicationDetectorAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for DuplicationDetector.
    
    Exposes capabilities:
    - detect_duplicates: Detect code duplications
    - get_duplication_report: Get duplication report
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[DuplicationDetectorOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("DuplicationDetector")
        self.name = "DuplicationDetectorAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="detect_duplicates",
                orchestrator="detect",
                description="Detect code duplications",
                input_schema={'file_paths': {'type': 'string', 'description': 'file_paths parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["detect_duplicates", "detect duplicates"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="get_duplication_report",
                orchestrator="get",
                description="Get duplication report",
                input_schema={'scope': {'type': 'string', 'description': 'scope parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["get_duplication_report", "get duplication report"],
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
                    orchestrator="duplicationdetector",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "detect_duplicates":
                result = self.orchestrator.detect_duplicates(file_paths=parameters.get('file_paths'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "get_duplication_report":
                result = self.orchestrator.get_duplication_report(scope=parameters.get('scope'))
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
                orchestrator="duplicationdetector",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="duplicationdetector",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
