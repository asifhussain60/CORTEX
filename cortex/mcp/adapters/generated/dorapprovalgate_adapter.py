"""
MCP Adapter for DoRApprovalGate

Generated adapter for DoRApprovalGate.
AC-ID: AC-PHASE2B-007
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.core.dor_approval_gate import DoRApprovalGate
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


class DoRApprovalGateAdapter(IOrchestratorAdapter):
    """
    MCP Adapter for DoRApprovalGate.
    
    Exposes capabilities:
    - check_readiness: Check Definition of Ready
    - get_dor_status: Get DoR approval status
    
    CORE-035: Uses wiring system for orchestrator access (single execution path).
    """
    
    def __init__(self, orchestrator: Optional[DoRApprovalGate] = None):
        """Initialize adapter with orchestrator from wiring system."""
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("DoRApprovalGate")
        self.name = "DoRApprovalGateAdapter"
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all capabilities exposed by this orchestrator."""
        return [
            CapabilityMetadata(
                name="check_readiness",
                orchestrator="check",
                description="Check Definition of Ready",
                input_schema={'request_data': {'type': 'string', 'description': 'request_data parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["check_readiness", "check readiness"],
                tags={"generated", "phase2b"},
            ),
            CapabilityMetadata(
                name="get_dor_status",
                orchestrator="get",
                description="Get DoR approval status",
                input_schema={'request_id': {'type': 'string', 'description': 'request_id parameter'}},
                output_schema={"status": {"type": "string"}, "result": {"type": "object"}},
                routing_keywords=["get_dor_status", "get dor status"],
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
                    orchestrator="dorapprovalgate",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            if capability_name == "check_readiness":
                result = self.orchestrator.check_readiness(request_data=parameters.get('request_data'))
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result,
                    orchestrator="{orchestrator_name_lower}",
                    duration_ms=(time.time() - start) * 1000,
                )
            elif capability_name == "get_dor_status":
                result = self.orchestrator.get_dor_status(request_id=parameters.get('request_id'))
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
                orchestrator="dorapprovalgate",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error executing {capability_name}: {e}")
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                orchestrator="dorapprovalgate",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def validate_parameters(
        self, capability_name: str, parameters: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate parameters for a capability."""
        # Basic validation - can be enhanced per capability
        return True, None
