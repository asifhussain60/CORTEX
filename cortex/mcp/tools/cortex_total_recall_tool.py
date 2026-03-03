"""
CortexTotalRecall — Deprecated alias delegating to CortexToolsCatalog.

Extracted from cortex/mcp/tools/utilities.py (Phase 103-d, GAP-103-07).
Single Responsibility: Backward-compatibility shim so existing callers that
reference CortexTotalRecall directly continue to work. The MCP registry no
longer exposes a separate cortex_total_recall entry (WAVE-101 consolidation).

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
from cortex.mcp.tools.cortex_tools_catalog_tool import CortexToolsCatalog


class CortexTotalRecall(ConsolidatedTool):
    """
    DEPRECATED — delegated to CortexToolsCatalog (WAVE-101 consolidation).

    cortex_total_recall ops (discover, recall, search) are now served by
    cortex_tools_catalog.  This class is retained so that existing tests and
    callers that reference CortexTotalRecall directly continue to work without
    modification.  The MCP registry no longer exposes a separate
    cortex_total_recall entry.
    """

    @property
    def name(self) -> str:
        """Return the name."""
        return "cortex_total_recall"  # legacy alias — registry entry removed

    @property
    def description(self) -> str:
        """Return the description."""
        return "Deprecated alias — use cortex_tools_catalog with discover|recall ops."

    @property
    def category(self) -> ToolCategory:
        """Return the category."""
        return ToolCategory.UTILITIES

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the parameters."""
        return [
            ToolParameter(
                name="operation", type="string", required=True,
                description="Recall operation: discover, recall, search",
                enum=["discover", "recall", "search"],
            ),
            ToolParameter(name="feature", type="string", required=False,
                          description="Feature name or search query"),
            ToolParameter(name="category", type="string", required=False,
                          description="Feature category filter"),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["discover", "recall", "search"]

    async def execute(self, **params) -> ToolResult:
        """Delegate to CortexToolsCatalog."""
        # Map cortex_total_recall params → cortex_tools_catalog params
        op = params.get("operation", "discover")
        # "search" op in total_recall uses "feature" as query
        if op == "search" and "feature" in params and "query" not in params:
            params = dict(params, query=params["feature"])
        elif op == "recall" and "feature" in params and "query" not in params:
            params = dict(params, query=params["feature"])
        return await CortexToolsCatalog().execute(**params)
