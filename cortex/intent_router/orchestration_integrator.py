"""Orchestration Integrator - Integrates intent routing with orchestrators.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OrchestratorType(Enum):
    """Types of orchestrators."""
    MASTER = "master"
    PLANNING = "planning"
    EXECUTION = "execution"
    ANALYSIS = "analysis"


@dataclass
class OrchestrationRequest:
    """Request to an orchestrator."""
    
    orchestrator_type: OrchestratorType
    operation: str
    parameters: Dict[str, Any]
    priority: int = 0
    timeout_ms: int = 30000


@dataclass
class OrchestrationResponse:
    """Response from an orchestrator."""
    
    success: bool
    result: Any
    error: Optional[str] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.metadata is None:
            self.metadata = {}


class OrchestrationIntegrator:
    """Integrates intent routing with CORTEX orchestrators."""
    
    def __init__(self):
        """Initialize orchestration integrator."""
        self.registered_orchestrators: Dict[OrchestratorType, Any] = {}
        self.request_history: List[OrchestrationRequest] = []
        self.response_history: List[OrchestrationResponse] = []
    
    def register_orchestrator(
        self,
        orchestrator_type: OrchestratorType,
        orchestrator: Any
    ) -> None:
        """Register an orchestrator.
        
        Args:
            orchestrator_type: Type of orchestrator
            orchestrator: The orchestrator instance
        """
        self.registered_orchestrators[orchestrator_type] = orchestrator
        logger.info(f"Registered orchestrator: {orchestrator_type.value}")
    
    def route_to_orchestrator(
        self,
        request: OrchestrationRequest
    ) -> OrchestrationResponse:
        """Route a request to the appropriate orchestrator.
        
        Args:
            request: The orchestration request
            
        Returns:
            OrchestrationResponse with the result
        """
        self.request_history.append(request)
        
        orchestrator = self.registered_orchestrators.get(request.orchestrator_type)
        
        if not orchestrator:
            response = OrchestrationResponse(
                success=False,
                result=None,
                error=f"No orchestrator registered for type: {request.orchestrator_type.value}"
            )
        else:
            try:
                # Stub: In real implementation, call orchestrator
                result = self._execute_orchestrator(orchestrator, request)
                response = OrchestrationResponse(
                    success=True,
                    result=result,
                    metadata={"orchestrator_type": request.orchestrator_type.value}
                )
            except Exception as e:
                response = OrchestrationResponse(
                    success=False,
                    result=None,
                    error=str(e)
                )
        
        self.response_history.append(response)
        return response
    
    def _execute_orchestrator(
        self,
        orchestrator: Any,
        request: OrchestrationRequest
    ) -> Any:
        """Execute orchestrator operation.
        
        Args:
            orchestrator: The orchestrator instance
            request: The request
            
        Returns:
            Operation result
        """
        # Stub implementation
        logger.debug(f"Executing {request.operation} on {request.orchestrator_type.value}")
        return {
            "status": "completed",
            "operation": request.operation,
            "orchestrator": request.orchestrator_type.value
        }
    
    def get_orchestrator_status(
        self,
        orchestrator_type: OrchestratorType
    ) -> Dict[str, Any]:
        """Get status of an orchestrator.
        
        Args:
            orchestrator_type: Type of orchestrator
            
        Returns:
            Status dictionary
        """
        orchestrator = self.registered_orchestrators.get(orchestrator_type)
        
        if not orchestrator:
            return {
                "registered": False,
                "type": orchestrator_type.value
            }
        
        return {
            "registered": True,
            "type": orchestrator_type.value,
            "requests_handled": sum(
                1 for r in self.request_history 
                if r.orchestrator_type == orchestrator_type
            )
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get integration statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_requests = len(self.request_history)
        successful = sum(1 for r in self.response_history if r.success)
        
        by_orchestrator = {}
        for request in self.request_history:
            orch_type = request.orchestrator_type.value
            if orch_type not in by_orchestrator:
                by_orchestrator[orch_type] = 0
            by_orchestrator[orch_type] += 1
        
        return {
            "total_requests": total_requests,
            "successful": successful,
            "failed": total_requests - successful,
            "success_rate": successful / total_requests if total_requests > 0 else 0,
            "by_orchestrator": by_orchestrator,
            "registered_orchestrators": list(self.registered_orchestrators.keys())
        }


__all__ = [
    "OrchestrationIntegrator",
    "OrchestratorType",
    "OrchestrationRequest",
    "OrchestrationResponse"
]
