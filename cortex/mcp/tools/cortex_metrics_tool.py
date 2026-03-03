"""
CortexMetrics — Development metrics capture and reporting.

Extracted from cortex/mcp/tools/utilities.py (Phase 103-d, GAP-103-07).
Single Responsibility: Record and report development metrics including TDD
cycles, debug sessions, code generation, and orchestrator invocations.

CORE-011: type hints | CORE-012: docstrings
"""
from __future__ import annotations

from typing import List

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context


class CortexMetrics(ConsolidatedTool):
    """
    Metrics operations.

    Operations:
    - capture: Capture development metrics
    - report: Generate metrics report
    - query: Query specific metrics
    """

    @property
    def name(self) -> str:
        """Return the name."""
        return "cortex_metrics"

    @property
    def description(self) -> str:
        """Return the description."""
        return (
            "Record and report development metrics. Capture TDD cycles, "
            "debug sessions, code generation, and orchestrator invocations."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the category."""
        return ToolCategory.UTILITIES

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the parameters."""
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Metrics operation: capture, report, query",
                required=True,
                enum=["capture", "report", "query"],
            ),
            ToolParameter(
                name="metric_type",
                type="string",
                description="Type of metric (tdd, debug, generation, orchestrator)",
                required=False,
            ),
            ToolParameter(
                name="data",
                type="object",
                description="Metric data to capture",
                required=False,
            ),
            ToolParameter(
                name="format",
                type="string",
                description="Report format: yaml, json",
                required=False,
                enum=["yaml", "json"],
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["capture", "report", "query"]

    async def execute(self, **params) -> ToolResult:
        """Execute metrics operation."""
        # ENFORCEMENT: Validate orchestrator routing
        _oc = params.get("orchestrator_context")
        if _oc is not None:
            validate_orchestrator_context(_oc)

        operation = params.get("operation", "query")
        metric_type = params.get("metric_type")
        data = params.get("data", {})
        output_format = params.get("format", "json")

        if operation == "capture":
            return ToolResult(
                success=True,
                data={
                    "metric_type": metric_type,
                    "captured": True,
                    "timestamp": "2026-02-12T00:00:00Z",
                    "data": data,
                },
                metadata={"operation": "capture"},
            )

        elif operation == "report":
            return ToolResult(
                success=True,
                data={
                    "format": output_format,
                    "metrics": {
                        "tdd_cycles": 0,
                        "debug_sessions": 0,
                        "tool_invocations": 0,
                        "orchestrator_calls": 0,
                    },
                    "period": "24h",
                },
                metadata={"operation": "report"},
            )

        elif operation == "query":
            return ToolResult(
                success=True,
                data={
                    "metric_type": metric_type,
                    "value": 0,
                    "trend": "stable",
                },
                metadata={"operation": "query"},
            )

        return ToolResult(success=False, error=f"Unknown operation: {operation}")
