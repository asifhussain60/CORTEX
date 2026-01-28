"""
RecommendationEngine MCP Adapter (Phase 8.4-8.5).

Exposes RecommendationEngine capabilities via MCP interface.
- Security threat recommendations
- SOLID principle guidance
- Performance optimization suggestions
- Compliance framework advisories

AC-ID: AC-MCP-ADAPTER-PHASE-8
Authority: AC-SECURITY-FRAMEWORK-001
Date: 2026-01-28
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.orchestrator_mcp_server import (
    IOrchestratorAdapter,
    CapabilityMetadata,
    CapabilityResponse,
    ExecutionContext,
)
from cortex.orchestrators.support.recommendation_engine import (
    get_recommendation_engine,
    RecommendationEngine,
)
from cortex.brain.analysis.security_threat_analyzer import (
    ThreatSeverity,
)
import logging
import time
from dataclasses import asdict

logger = logging.getLogger(__name__)


class RecommendationEngineAdapter(IOrchestratorAdapter):
    """MCP Adapter for RecommendationEngine (Phase 8.4-8.5).
    
    Exposes security-first recommendations through MCP interface.
    Supports threat analysis, SOLID guidance, performance optimization,
    and compliance advisory.
    
    Authority: AC-SECURITY-FRAMEWORK-001
    """
    
    def __init__(self):
        """Initialize adapter with RecommendationEngine singleton."""
        self.engine: RecommendationEngine = get_recommendation_engine()
        self._health_check_cache: Optional[Dict[str, Any]] = None
        self._last_health_check: float = 0
        self._health_check_ttl: float = 5.0  # 5 second TTL
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Get all RecommendationEngine capabilities.
        
        Returns:
            List of exposed MCP capabilities
        """
        return [
            # ================================================================
            # Security Recommendations
            # ================================================================
            CapabilityMetadata(
                name="recommend_security_fix",
                orchestrator="recommendation_engine",
                description="Get security recommendations for a specific CWE vulnerability",
                input_schema={
                    "type": "object",
                    "properties": {
                        "cwe_id": {"type": "string", "description": "CWE ID (e.g., 'CWE-94')"},
                        "context": {
                            "type": "object",
                            "description": "Optional context about the threat"
                        },
                    },
                    "required": ["cwe_id"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "cwe_id": {"type": "string"},
                        "severity": {"type": "string"},
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "remediation_effort": {"type": "string"},
                                }
                            }
                        },
                        "summary": {"type": "string"},
                    }
                },
                routing_keywords=["security", "recommendation", "cwe", "threat", "fix"],
                tags={"security", "recommendation", "threat-response"},
            ),
            
            # ================================================================
            # SOLID Recommendations
            # ================================================================
            CapabilityMetadata(
                name="recommend_solid_fix",
                orchestrator="recommendation_engine",
                description="Get SOLID principle recommendations for code violations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "violation_type": {
                            "type": "string",
                            "description": "SOLID violation type (e.g., 'SRP_VIOLATION')"
                        },
                        "context": {
                            "type": "object",
                            "description": "Optional context about the violation"
                        },
                    },
                    "required": ["violation_type"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "violation_type": {"type": "string"},
                        "principle": {"type": "string"},
                        "recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "code_example": {"type": "string"},
                                }
                            }
                        },
                        "summary": {"type": "string"},
                    }
                },
                routing_keywords=["solid", "principle", "code-design", "refactor", "architecture"],
                tags={"architecture", "recommendation", "design-patterns"},
            ),
            
            # ================================================================
            # Performance Recommendations
            # ================================================================
            CapabilityMetadata(
                name="recommend_performance_fix",
                orchestrator="recommendation_engine",
                description="Get performance optimization recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "performance_issue": {
                            "type": "string",
                            "description": "Type of performance issue detected"
                        },
                        "context": {
                            "type": "object",
                            "description": "Optional context about the issue"
                        },
                    },
                    "required": ["performance_issue"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "issue": {"type": "string"},
                        "recommendations": {"type": "array"},
                        "summary": {"type": "string"},
                    }
                },
                routing_keywords=["performance", "optimization", "speed", "efficiency"],
                tags={"performance", "recommendation", "optimization"},
            ),
            
            # ================================================================
            # Compliance Recommendations
            # ================================================================
            CapabilityMetadata(
                name="recommend_compliance_fix",
                orchestrator="recommendation_engine",
                description="Get compliance framework recommendations",
                input_schema={
                    "type": "object",
                    "properties": {
                        "framework": {
                            "type": "string",
                            "description": "Compliance framework (e.g., 'SOC2', 'ISO27001')"
                        },
                        "violation": {
                            "type": "object",
                            "description": "Optional compliance violation details"
                        },
                    },
                    "required": ["framework"],
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "framework": {"type": "string"},
                        "recommendations": {"type": "array"},
                        "summary": {"type": "string"},
                    }
                },
                routing_keywords=["compliance", "soc2", "iso", "audit", "governance"],
                tags={"compliance", "recommendation", "governance"},
            ),
        ]
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext,
    ) -> CapabilityResponse:
        """Execute a recommendation capability.
        
        Args:
            capability_name: Name of capability to execute
            parameters: Input parameters
            context: Execution context
            
        Returns:
            CapabilityResponse with results
        """
        start = time.time()
        request_id = context.session_id
        
        try:
            if capability_name == "recommend_security_fix":
                return self._recommend_security_fix(parameters, request_id, start)
            elif capability_name == "recommend_solid_fix":
                return self._recommend_solid_fix(parameters, request_id, start)
            elif capability_name == "recommend_performance_fix":
                return self._recommend_performance_fix(parameters, request_id, start)
            elif capability_name == "recommend_compliance_fix":
                return self._recommend_compliance_fix(parameters, request_id, start)
            else:
                return CapabilityResponse(
                    request_id=request_id,
                    success=False,
                    error=f"Unknown capability: {capability_name}",
                    error_code="UNKNOWN_CAPABILITY",
                    orchestrator="recommendation_engine",
                    duration_ms=(time.time() - start) * 1000,
                )
        except Exception as e:
            logger.error(f"Error executing capability {capability_name}: {e}", exc_info=True)
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                error_code="EXECUTION_ERROR",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def _recommend_security_fix(
        self,
        parameters: Dict[str, Any],
        request_id: str,
        start: float,
    ) -> CapabilityResponse:
        """Recommend security fix for CWE.
        
        Args:
            parameters: Input parameters with cwe_id
            request_id: Request ID for tracking
            start: Start time for duration calculation
            
        Returns:
            CapabilityResponse with security recommendations
        """
        cwe_id = parameters.get("cwe_id")
        if not cwe_id:
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error="Missing required parameter: cwe_id",
                error_code="INVALID_INPUT",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        
        try:
            result = self.engine.recommend_for_security(cwe_id)
            
            output = {
                "success": True,
                "cwe_id": cwe_id,
                "severity": result.severity or "UNKNOWN",
                "recommendations": [
                    asdict(rec) for rec in result.recommendations
                ] if result.recommendations else [],
                "summary": result.summary or f"Security recommendations for {cwe_id}",
            }
            
            logger.info(f"Generated {len(result.recommendations or [])} security recommendations for {cwe_id}")
            
            return CapabilityResponse(
                request_id=request_id,
                success=True,
                result=output,
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error generating security recommendations for {cwe_id}: {e}")
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                error_code="RECOMMENDATION_ERROR",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def _recommend_solid_fix(
        self,
        parameters: Dict[str, Any],
        request_id: str,
        start: float,
    ) -> CapabilityResponse:
        """Recommend SOLID principle fix.
        
        Args:
            parameters: Input parameters with violation_type
            request_id: Request ID for tracking
            start: Start time for duration calculation
            
        Returns:
            CapabilityResponse with SOLID recommendations
        """
        violation_type = parameters.get("violation_type")
        if not violation_type:
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error="Missing required parameter: violation_type",
                error_code="INVALID_INPUT",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        
        try:
            result = self.engine.recommend_for_solid(violation_type)
            
            output = {
                "success": True,
                "violation_type": violation_type,
                "principle": result.principle or "UNKNOWN",
                "recommendations": [
                    asdict(rec) for rec in result.recommendations
                ] if result.recommendations else [],
                "summary": result.summary or f"SOLID recommendations for {violation_type}",
            }
            
            logger.info(f"Generated {len(result.recommendations or [])} SOLID recommendations for {violation_type}")
            
            return CapabilityResponse(
                request_id=request_id,
                success=True,
                result=output,
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error generating SOLID recommendations for {violation_type}: {e}")
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                error_code="RECOMMENDATION_ERROR",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def _recommend_performance_fix(
        self,
        parameters: Dict[str, Any],
        request_id: str,
        start: float,
    ) -> CapabilityResponse:
        """Recommend performance optimization.
        
        Args:
            parameters: Input parameters with performance_issue
            request_id: Request ID for tracking
            start: Start time for duration calculation
            
        Returns:
            CapabilityResponse with performance recommendations
        """
        performance_issue = parameters.get("performance_issue")
        if not performance_issue:
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error="Missing required parameter: performance_issue",
                error_code="INVALID_INPUT",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        
        try:
            result = self.engine.recommend_for_performance(performance_issue)
            
            output = {
                "success": True,
                "issue": performance_issue,
                "recommendations": [
                    asdict(rec) for rec in result.recommendations
                ] if result.recommendations else [],
                "summary": result.summary or f"Performance recommendations for {performance_issue}",
            }
            
            logger.info(f"Generated {len(result.recommendations or [])} performance recommendations")
            
            return CapabilityResponse(
                request_id=request_id,
                success=True,
                result=output,
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error generating performance recommendations: {e}")
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                error_code="RECOMMENDATION_ERROR",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def _recommend_compliance_fix(
        self,
        parameters: Dict[str, Any],
        request_id: str,
        start: float,
    ) -> CapabilityResponse:
        """Recommend compliance framework fix.
        
        Args:
            parameters: Input parameters with framework
            request_id: Request ID for tracking
            start: Start time for duration calculation
            
        Returns:
            CapabilityResponse with compliance recommendations
        """
        framework = parameters.get("framework")
        if not framework:
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error="Missing required parameter: framework",
                error_code="INVALID_INPUT",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        
        try:
            result = self.engine.recommend_for_compliance(framework)
            
            output = {
                "success": True,
                "framework": framework,
                "recommendations": [
                    asdict(rec) for rec in result.recommendations
                ] if result.recommendations else [],
                "summary": result.summary or f"Compliance recommendations for {framework}",
            }
            
            logger.info(f"Generated {len(result.recommendations or [])} compliance recommendations for {framework}")
            
            return CapabilityResponse(
                request_id=request_id,
                success=True,
                result=output,
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
        except Exception as e:
            logger.error(f"Error generating compliance recommendations for {framework}: {e}")
            return CapabilityResponse(
                request_id=request_id,
                success=False,
                error=str(e),
                error_code="RECOMMENDATION_ERROR",
                orchestrator="recommendation_engine",
                duration_ms=(time.time() - start) * 1000,
            )
    
    def is_healthy(self) -> bool:
        """Check if RecommendationEngine is healthy.
        
        Returns:
            True if healthy and accessible
        """
        try:
            # Use cached result if fresh
            current_time = time.time()
            if self._health_check_cache and (current_time - self._last_health_check) < self._health_check_ttl:
                return self._health_check_cache.get("healthy", False)
            
            # Verify engine is accessible
            engine = get_recommendation_engine()
            if not engine:
                return False
            
            # Test advisor access
            advisors_ok = all([
                hasattr(engine, "_security_advisor"),
                hasattr(engine, "_solid_advisor"),
                hasattr(engine, "_performance_advisor"),
                hasattr(engine, "_compliance_advisor"),
            ])
            
            self._health_check_cache = {"healthy": advisors_ok}
            self._last_health_check = current_time
            
            return advisors_ok
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get RecommendationEngine status.
        
        Returns:
            Status dictionary with orchestrator information
        """
        try:
            engine = get_recommendation_engine()
            return {
                "name": "RecommendationEngine",
                "healthy": self.is_healthy(),
                "status": "operational" if self.is_healthy() else "degraded",
                "phase": "8.4-8.5",
                "advisors": {
                    "security": "enabled",
                    "solid": "enabled",
                    "performance": "enabled",
                    "compliance": "enabled",
                },
                "capabilities": len(self.get_capabilities()),
                "authority": "AC-SECURITY-FRAMEWORK-001",
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "name": "RecommendationEngine",
                "healthy": False,
                "status": "error",
                "error": str(e),
            }
