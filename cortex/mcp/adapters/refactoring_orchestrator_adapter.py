"""
MCP Adapter for EnhancedRefactoringOrchestrator

Exposes refactoring capabilities via MCP gateway.
AC-ID: AC-PHASE76-S1.T3-REF-001

Capabilities:
- analyze_code: Analyze code for refactoring opportunities
- generate_refactoring_plan: Generate refactoring plan with confidence scoring
- apply_refactoring_strategy: Apply refactoring strategy
- get_pattern_cache_stats: Get pattern cache statistics
- get_circuit_breaker_status: Get circuit breaker status
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.domain.enhanced_refactoring_orchestrator import (
    EnhancedRefactoringOrchestrator,
)
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


class EnhancedRefactoringOrchestratorAdapter(IOrchestratorAdapter):
    """MCP Adapter for EnhancedRefactoringOrchestrator.
    
    Provides unified interface for refactoring operations:
    - Code analysis with LENS-based complexity scoring
    - Refactoring plan generation with confidence metrics
    - Strategy application with security-first approach
    - Pattern caching for performance optimization
    
    CORE-035: Uses wiring system for orchestrator access.
    """
    
    def __init__(self, orchestrator: Optional[EnhancedRefactoringOrchestrator] = None):
        """Initialize adapter with orchestrator from wiring system.
        
        Args:
            orchestrator: Optional pre-configured orchestrator instance
        """
        if orchestrator is not None:
            self.orchestrator = orchestrator
        else:
            self.orchestrator = _get_orchestrator_from_wiring("RefactoringOrchestrator")
        
        if self.orchestrator is None:
            self.orchestrator = EnhancedRefactoringOrchestrator.instance()
        
        self.name = "EnhancedRefactoringOrchestratorAdapter"
        self._start_time = time.time()
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all exposed capabilities.
        
        Returns:
            List of CapabilityMetadata for each exposed operation
        """
        return [
            CapabilityMetadata(
                name="analyze_code",
                orchestrator="refactoring",
                description="Analyze code for refactoring opportunities with LENS-based complexity classification",
                input_schema={
                    "file_path": {
                        "type": "string",
                        "description": "Path to file to analyze",
                    },
                    "code": {
                        "type": "string",
                        "description": "Code content to analyze",
                    },
                },
                output_schema={"analysis": {"type": "object"}, "violations": {"type": "array"}},
                tags={"refactoring", "analysis", "lens"},
            ),
            CapabilityMetadata(
                name="generate_refactoring_plan",
                orchestrator="refactoring",
                description="Generate refactoring plan with confidence scoring (AC-DOMAIN-REF-005)",
                input_schema={
                    "analysis_id": {
                        "type": "string",
                        "description": "ID of analysis to plan",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "File path for planning context",
                    },
                    "profile": {
                        "type": "string",
                        "description": "Refactoring profile (conservative/moderate/aggressive)",
                    },
                },
                output_schema={"plan": {"type": "object"}, "confidence": {"type": "number"}},
                tags={"refactoring", "planning"},
            ),
            CapabilityMetadata(
                name="apply_refactoring_strategy",
                orchestrator="refactoring",
                description="Apply refactoring strategy with security-first validation",
                input_schema={
                    "strategy": {
                        "type": "string",
                        "description": "Strategy name to apply",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Target file path",
                    },
                },
                output_schema={"status": {"type": "string"}, "changes": {"type": "array"}},
                tags={"refactoring", "execution"},
            ),
            CapabilityMetadata(
                name="get_pattern_cache_stats",
                orchestrator="refactoring",
                description="Get pattern cache statistics (60%+ hit rate target)",
                input_schema={},
                output_schema={"hit_rate": {"type": "number"}, "size": {"type": "integer"}},
                tags={"refactoring", "optimization"},
            ),
            CapabilityMetadata(
                name="get_circuit_breaker_status",
                orchestrator="refactoring",
                description="Get circuit breaker status for large class analysis",
                input_schema={},
                output_schema={"status": {"type": "string"}, "threshold": {"type": "integer"}},
                tags={"refactoring", "safety"},
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
            if capability_name == "analyze_code":
                result = self.orchestrator.execute_operation("analyze_code", parameters)
            elif capability_name == "generate_refactoring_plan":
                result = self.orchestrator.execute_operation(
                    "generate_refactoring_plan", parameters
                )
            elif capability_name == "apply_refactoring_strategy":
                result = self.orchestrator.execute_operation(
                    "apply_refactoring_strategy", parameters
                )
            elif capability_name == "get_pattern_cache_stats":
                result = self.orchestrator.execute_operation(
                    "get_pattern_cache_stats", {}
                )
            elif capability_name == "get_circuit_breaker_status":
                result = self.orchestrator.execute_operation(
                    "get_circuit_breaker_status", {}
                )
            else:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    result={"error": f"Unknown capability: {capability_name}"},
                    orchestrator="refactoring",
                    duration_ms=(time.time() - start) * 1000,
                )
            
            # Convert Result to CapabilityResponse
            if result.is_ok():
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=result.value,
                    orchestrator="refactoring",
                    duration_ms=(time.time() - start) * 1000,
                )
            else:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    result={"error": result.error},
                    orchestrator="refactoring",
                    duration_ms=(time.time() - start) * 1000,
                )
        
        except Exception as e:
            logger.error(f"Capability execution failed: {e}", exc_info=True)
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                result={"error": f"Execution error: {str(e)}"},
                orchestrator="refactoring",
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
                "name": "EnhancedRefactoringOrchestrator",
                "healthy": False,
                "error": str(e),
            }


__all__ = [
    "EnhancedRefactoringOrchestratorAdapter",
]
