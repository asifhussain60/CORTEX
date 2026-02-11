"""
MCP Adapter for EnhancedPlanningOrchestrator

Exposes planning capabilities via MCP gateway.
AC-ID: AC-PHASE76-S1.T3-PLAN-001

Capabilities:
- estimate_phase: Estimate effort for a phase
- sort_phases: Sort phases by dependencies (topological ordering)
- check_resources: Check resource feasibility
- generate_risk_matrix: Generate risk assessment matrix
- execute_phases: Execute phases with parallel support
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
from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
    EnhancedPlanningOrchestrator,
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


class EnhancedPlanningOrchestratorAdapter(IOrchestratorAdapter):
    """MCP Adapter for EnhancedPlanningOrchestrator.

    Provides unified interface for phase planning operations:
    - Phase effort estimation with ML-based models
    - Topological dependency sorting (AC-DOMAIN-PLAN-003)
    - Resource constraint validation (AC-DOMAIN-PLAN-011)
    - Risk assessment matrix generation (AC-DOMAIN-PLAN-012)
    - Parallel phase execution (AC-DOMAIN-PLAN-010)

    CORE-035: Uses wiring system for orchestrator access.
    """

    def __init__(self, orchestrator: Optional[EnhancedPlanningOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system.

        Args:
            orchestrator: Optional pre-configured orchestrator instance
        """
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("PlanningOrchestrator")

        if self.orchestrator is None:
            self.orchestrator = EnhancedPlanningOrchestrator.instance()

        self.name = "EnhancedPlanningOrchestratorAdapter"
        self._start_time = time.time()

    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all exposed capabilities.

        Returns:
            List of CapabilityMetadata for each exposed operation
        """
        return [
            CapabilityMetadata(
                name="estimate_phase",
                description="Estimate effort for a phase using ML-based models (AC-DOMAIN-PLAN-009)",
                parameters={
                    "phase_name": {
                        "type": "str",
                        "description": "Name of phase to estimate",
                        "required": True,
                    },
                    "complexity": {
                        "type": "str",
                        "description": "Complexity level (trivial/simple/moderate/complex/critical)",
                        "required": False,
                    },
                },
                output_type="dict",
            ),
            CapabilityMetadata(
                name="sort_phases",
                description="Sort phases by dependencies using topological ordering (AC-DOMAIN-PLAN-003)",
                parameters={
                    "phases": {
                        "type": "dict",
                        "description": "Dictionary of phases with dependencies",
                        "required": True,
                    },
                },
                output_type="dict",
            ),
            CapabilityMetadata(
                name="check_resources",
                description="Check resource feasibility for a phase (AC-DOMAIN-PLAN-011)",
                parameters={
                    "phase_id": {
                        "type": "str",
                        "description": "ID of phase to check",
                        "required": True,
                    },
                    "required_capacity": {
                        "type": "float",
                        "description": "Required resource capacity",
                        "required": False,
                    },
                },
                output_type="dict",
            ),
            CapabilityMetadata(
                name="generate_risk_matrix",
                description="Generate risk assessment matrix (AC-DOMAIN-PLAN-012)",
                parameters={
                    "phase_id": {
                        "type": "str",
                        "description": "ID of phase to assess",
                        "required": True,
                    },
                },
                output_type="dict",
            ),
            CapabilityMetadata(
                name="execute_phases",
                description="Execute phases with parallel support where dependencies allow (AC-DOMAIN-PLAN-010)",
                parameters={
                    "phases": {
                        "type": "list",
                        "description": "List of phase IDs to execute",
                        "required": True,
                    },
                },
                output_type="dict",
            ),
        ]

    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> CapabilityResponse:
        """Execute a capability.

        Args:
            capability_name: Name of capability to execute
            parameters: Capability parameters
            context: Execution context

        Returns:
            CapabilityResponse with results or error
        """
        start = time.time()
        try:
            if capability_name == "estimate_phase":
                result = self.orchestrator.execute_operation("estimate_phase", parameters)
            elif capability_name == "sort_phases":
                result = self.orchestrator.execute_operation("sort_phases", parameters)
            elif capability_name == "check_resources":
                result = self.orchestrator.execute_operation(
                    "check_resources", parameters
                )
            elif capability_name == "generate_risk_matrix":
                result = self.orchestrator.execute_operation(
                    "generate_risk_matrix", parameters
                )
            elif capability_name == "execute_phases":
                result = self.orchestrator.execute_operation("execute_phases", parameters)
            else:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    result={"error": f"Unknown capability: {capability_name}"},
                    orchestrator="planning",
                    duration_ms=(time.time() - start) * 1000,
                )

            # Convert Result to CapabilityResponse
            if result.is_ok():
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result.value,
                    orchestrator="planning",
                    duration_ms=(time.time() - start) * 1000,
                )
            else:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    result={"error": result.error},
                    orchestrator="planning",
                    duration_ms=(time.time() - start) * 1000,
                )

        except Exception as e:
            logger.error(f"Capability execution failed: {e}", exc_info=True)
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                result={"error": f"Execution error: {str(e)}"},
                orchestrator="planning",
            )

    def is_healthy(self) -> bool:
        """Check if orchestrator is healthy.

        Returns:
            True if orchestrator is operational
        """
        try:
            # Check if orchestrator is initialized
            if self.orchestrator is None:
                return False

            # Try to get name (lightweight health check)
            name = self.orchestrator.get_name()
            return name is not None and len(name) > 0

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status.

        Returns:
            Status dictionary with health and metrics
        """
        try:
            uptime_seconds = time.time() - self._start_time

            return {
                "name": self.orchestrator.get_name(),
                "version": self.orchestrator.get_version(),
                "mode": self.orchestrator.get_mode().value,
                "healthy": self.is_healthy(),
                "uptime_seconds": uptime_seconds,
                "capabilities": len(self.get_capabilities()),
            }

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                "name": "EnhancedPlanningOrchestrator",
                "healthy": False,
                "error": str(e),
            }


__all__ = [
    "EnhancedPlanningOrchestratorAdapter",
]
