"""
Brain Health Monitoring MCP Tool.

Exposes BrainHealthOrchestrator as MCP tool for Copilot integration.
Part of Phase 38 Stage 1.

Author: CORTEX Framework (Phase 38)
"""

import json
import logging
from typing import Dict, Any, Optional

from cortex.mcp.server import Tool, ToolDefinition, ToolParameter

logger = logging.getLogger(__name__)


class BrainHealthTool(Tool):
    """
    MCP tool for brain health monitoring.
    
    Provides real-time CORTEX brain health metrics across 5 dimensions:
    - Cache staleness
    - Orchestrator connectivity
    - Knowledge freshness
    - Governance coverage
    - Domain utilization
    """

    @property
    def definition(self) -> ToolDefinition:
        """Get tool definition."""
        return ToolDefinition(
            name="cortex_brain_health",
            description=(
                "Monitor CORTEX brain health across 5 critical dimensions. "
                "Returns health score (0-100), status (EXCELLENT/GOOD/FAIR/POOR/CRITICAL), "
                "dimension breakdowns, and actionable alerts."
            ),
            parameters=[
                ToolParameter(
                    name="format",
                    type="string",
                    required=False,
                    description="Output format: 'summary' (default), 'detailed', or 'prometheus'"
                ),
                ToolParameter(
                    name="include_recommendations",
                    type="boolean",
                    required=False,
                    description="Include remediation recommendations for unhealthy dimensions (default: true)"
                )
            ],
            metadata={
                "category": "observability",
                "version": "1.0",
                "phase": "Phase-38-Stage-1"
            }
        )

    def execute(
        self,
        format: str = "summary",
        include_recommendations: bool = True,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute brain health check.
        
        Args:
            format: Output format ('summary', 'detailed', 'prometheus')
            include_recommendations: Include remediation recommendations
            **kwargs: Additional arguments (ignored)
        
        Returns:
            Dict with health report or error
        """
        try:
            from cortex.orchestrators.support.brain_health_orchestrator import (
                BrainHealthOrchestrator
            )
            
            # Create orchestrator instance
            orchestrator = BrainHealthOrchestrator()
            
            # Generate health report
            report = orchestrator.calculate_health_score()
            
            # Format output based on requested format
            if format == "prometheus":
                return self._format_prometheus(orchestrator, report)
            elif format == "detailed":
                return self._format_detailed(report, include_recommendations)
            else:  # summary
                return self._format_summary(report, include_recommendations)
                
        except Exception as e:
            logger.error(f"Brain health check failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to generate brain health report: {str(e)}"
            }

    def _format_summary(
        self,
        report: Dict[str, Any],
        include_recommendations: bool
    ) -> Dict[str, Any]:
        """Format as summary view."""
        result = {
            "status": "success",
            "health_status": report['status'],
            "aggregate_score": round(report['aggregate_score'], 2),
            "timestamp": report['timestamp'],
            "dimensions": {
                "cache_staleness": f"{report['dimensions']['cache_staleness_ratio']:.2f}",
                "connectivity": f"{report['dimensions']['connectivity_score']:.1f}%",
                "knowledge_freshness": f"{report['dimensions']['knowledge_freshness']:.1f}%",
                "governance_coverage": f"{report['dimensions']['governance_coverage']:.1f}%",
                "domain_utilization": f"{report['dimensions']['domain_utilization']:.1f}%"
            }
        }
        
        if include_recommendations and report['alerts']:
            result["alerts_count"] = len(report['alerts'])
            result["top_recommendations"] = [
                alert['recommendation'] for alert in report['alerts'][:3]
            ]
        
        return result

    def _format_detailed(
        self,
        report: Dict[str, Any],
        include_recommendations: bool
    ) -> Dict[str, Any]:
        """Format as detailed view with full dimension breakdown."""
        result = {
            "status": "success",
            "health_status": report['status'],
            "aggregate_score": round(report['aggregate_score'], 2),
            "timestamp": report['timestamp'],
            "dimensions_detailed": {
                "cache_staleness_ratio": {
                    "value": report['dimensions']['cache_staleness_ratio'],
                    "threshold": 0.2,
                    "status": "healthy" if report['dimensions']['cache_staleness_ratio'] <= 0.2 else "warning"
                },
                "connectivity_score": {
                    "value": report['dimensions']['connectivity_score'],
                    "threshold": 90.0,
                    "status": "healthy" if report['dimensions']['connectivity_score'] >= 90.0 else "warning"
                },
                "knowledge_freshness": {
                    "value": report['dimensions']['knowledge_freshness'],
                    "threshold": 60.0,
                    "status": "healthy" if report['dimensions']['knowledge_freshness'] >= 60.0 else "warning"
                },
                "governance_coverage": {
                    "value": report['dimensions']['governance_coverage'],
                    "threshold": 80.0,
                    "status": "healthy" if report['dimensions']['governance_coverage'] >= 80.0 else "warning"
                },
                "domain_utilization": {
                    "value": report['dimensions']['domain_utilization'],
                    "threshold": 50.0,
                    "status": "healthy" if report['dimensions']['domain_utilization'] >= 50.0 else "warning"
                }
            }
        }
        
        if include_recommendations:
            result["alerts"] = report['alerts']
        
        return result

    def _format_prometheus(
        self,
        orchestrator: 'BrainHealthOrchestrator',
        report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format as Prometheus metrics."""
        try:
            metrics_output = orchestrator.export_prometheus_metrics(report['dimensions'])
            return {
                "status": "success",
                "format": "prometheus",
                "metrics": metrics_output
            }
        except Exception as e:
            logger.error(f"Prometheus export failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to export Prometheus metrics: {str(e)}"
            }


# Tool registration
def register_brain_health_tool():
    """Register brain health tool with MCP server."""
    from cortex.mcp.tool_registry import ToolRegistry
    
    registry = ToolRegistry.instance()
    registry.register(BrainHealthTool())
    
    logger.info("Brain health tool registered: cortex_brain_health")


# Auto-register on import
try:
    register_brain_health_tool()
except Exception as e:
    logger.warning(f"Failed to auto-register brain health tool: {e}")
