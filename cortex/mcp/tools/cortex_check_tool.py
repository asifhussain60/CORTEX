"""
CortexCheck — Deprecated alias delegating to CortexVerify.

Extracted from cortex/mcp/tools/utilities.py (Phase 103-d, GAP-103-07).
Single Responsibility: Backward-compatibility shim so existing callers that
instantiate CortexCheck directly continue to work. The MCP registry no longer
exposes a separate cortex_check entry (WAVE-101 consolidation).

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
from cortex.mcp.tools.cortex_verify_tool import CortexVerify


class CortexCheck(ConsolidatedTool):
    """
    DEPRECATED — delegated to CortexVerify (WAVE-101 consolidation).

    cortex_check ops (dependencies, status, health, orchestrator_health) are
    now served by cortex_verify.  This class is retained purely so that any
    code that instantiates CortexCheck directly (tests, older callers) still
    works.  The MCP registry no longer exposes a separate cortex_check entry;
    all calls route through cortex_verify.
    """

    @property
    def name(self) -> str:
        """Return the name."""
        return "cortex_check"  # legacy alias — registry entry removed

    @property
    def description(self) -> str:
        """Return the description."""
        return "Deprecated alias — use cortex_verify with dependencies|status|health|orchestrator_health."

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
                description="Check operation: dependencies, status, health, orchestrator_health",
                required=True,
                enum=["dependencies", "status", "health", "orchestrator_health"],
            ),
            ToolParameter(name="operation_id", type="string", required=False,
                          description="Operation ID for status check"),
            ToolParameter(name="orchestrator", type="string", required=False,
                          description="Specific orchestrator name for health check"),
            ToolParameter(name="parallel", type="boolean", required=False,
                          description="Check all orchestrators in parallel"),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["dependencies", "status", "health", "orchestrator_health"]

    async def execute(self, **params) -> ToolResult:
        """Delegate to CortexVerify."""
        return await CortexVerify().execute(**params)
