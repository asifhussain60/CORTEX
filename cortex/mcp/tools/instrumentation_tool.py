"""
MCP Tools for Instrumentation - Metrics capture and enhancement recommendations.

AC-ID: AC-PHASE-20.9-04 - Instrumentation MCP Tools Implementation
Author: Asif Hussain
Created: 2026-02-04

Provides MCP tools for:
- Recording development metrics
- Getting enhancement recommendations based on metrics
"""

from typing import Any, Literal

from cortex.mcp.decorators import mcp_tool
from cortex.orchestrators.support.instrumentation_orchestrator import (
    InstrumentationOrchestrator,
    get_instrumentation_orchestrator,
)


@mcp_tool(
    name="cortex_capture_metrics",
    description="Record development metrics for analysis. Captures TDD cycles, debug sessions, code generation, and orchestrator invocations.",
    category="observability",
)
def cortex_capture_metrics(
    operation_type: Literal["tdd", "debug", "codegen", "orchestrator"],
    operation_name: str,
    duration_ms: int,
    success: bool,
    metadata: Union[dict[str, Any], None] = None,
) -> dict[str, Any]:
    """
    Record development metrics for evidence-driven tool enhancement.

    Args:
        operation_type: Type of operation (tdd, debug, codegen, orchestrator)
        operation_name: Name/identifier of the operation
        duration_ms: Duration in milliseconds
        success: Whether the operation succeeded
        metadata: Additional metadata specific to operation type

    Returns:
        Result dictionary with success status and metric ID

    Example:
        >>> cortex_capture_metrics(
        ...     operation_type="tdd",
        ...     operation_name="test_example.py",
        ...     duration_ms=5000,
        ...     success=True,
        ...     metadata={"phase": "GREEN", "orchestrator": "TDDOrchestrator"}
        ... )
        {"success": True, "metric_id": "uuid-here", "message": "Metric recorded"}
    """
    orch = get_instrumentation_orchestrator()
    metadata = metadata or {}

    if operation_type == "tdd":
        result = orch.record_tdd_cycle(
            phase=metadata.get("phase", "GREEN"),
            orchestrator=metadata.get("orchestrator", "TDDOrchestrator"),
            test_file=operation_name,
            duration_ms=duration_ms,
            success=success,
            failure_reason=metadata.get("failure_reason"),
            retry_count=metadata.get("retry_count", 0),
        )
    elif operation_type == "debug":
        result = orch.record_debug_session(
            orchestrator=metadata.get("orchestrator", "DebuggingOrchestrator"),
            target_file=operation_name,
            duration_ms=duration_ms,
            resolved=success,
            resolution_method=metadata.get("resolution_method"),
            steps_taken=metadata.get("steps_taken", 0),
        )
    elif operation_type == "codegen":
        result = orch.record_codegen(
            template_name=operation_name,
            target_type=metadata.get("target_type", "component"),
            duration_ms=duration_ms,
            success=success,
            customizations_applied=metadata.get("customizations_applied", 0),
            manual_edits_needed=metadata.get("manual_edits_needed", False),
        )
    elif operation_type == "orchestrator":
        result = orch.record_orchestrator_invocation(
            orchestrator_name=operation_name,
            operation=metadata.get("operation", "execute"),
            duration_ms=duration_ms,
            success=success,
            error_type=metadata.get("error_type"),
        )
    else:
        return {
            "success": False,
            "metric_id": None,
            "message": f"Unknown operation type: {operation_type}",
        }

    return {
        "success": result.success,
        "metric_id": result.metric_id,
        "message": result.message or "Metric recorded successfully",
    }


@mcp_tool(
    name="cortex_get_enhancement_recommendations",
    description="Get enhancement recommendations based on captured metrics. Returns prioritized suggestions with evidence.",
    category="observability",
)
def cortex_get_enhancement_recommendations() -> dict[str, Any]:
    """
    Analyze captured metrics and return evidence-driven enhancement suggestions.

    Returns:
        Dictionary containing:
        - recommendations: List of enhancement recommendations with priority, evidence, effort
        - summary: Current metrics summary
        - thresholds: Active threshold configuration

    Example:
        >>> recommendations = cortex_get_enhancement_recommendations()
        >>> print(recommendations["recommendations"][0]["enhancement"])
        "TDD Orchestrator Acceleration"
    """
    orch = get_instrumentation_orchestrator()

    recommendations = orch.get_enhancement_recommendations()
    summary = orch.get_metrics_summary()

    return {
        "recommendations": [
            {
                "priority": rec.priority,
                "enhancement": rec.enhancement,
                "evidence": rec.evidence,
                "effort": rec.effort,
                "expected_impact": rec.expected_impact,
            }
            for rec in recommendations
        ],
        "summary": summary,
        "thresholds": orch.thresholds,
        "breached_count": len(recommendations),
    }


@mcp_tool(
    name="cortex_metrics_report",
    description="Export metrics report in YAML or JSON format for analysis.",
    category="observability",
)
def cortex_metrics_report(format: Literal["yaml", "json"] = "yaml") -> str:
    """
    Export current metrics as a formatted report.

    Args:
        format: Output format (yaml or json)

    Returns:
        Formatted metrics report string
    """
    orch = get_instrumentation_orchestrator()
    return orch.export_metrics_report(format=format)
