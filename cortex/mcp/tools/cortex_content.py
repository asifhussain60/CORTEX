"""CortexContent — Content Library MCP tool (GAP-130-03).

Provides MCP-accessible control surface for the ContentLibraryEngine —
allowing orchestrators and the Copilot Chat LLM to select, inspect, reset,
and stat the three response content pools (quotes, principles, ai_sparks).

Operations:
  select   — Draw the next item from a named pool (or select_across for mutual exclusion)
  history  — Return recent draw history for a pool
  reset    — Reset a pool's EpochShuffler to epoch 0
  stats    — Return per-pool statistics (epoch, history_size, pool_size)

Phase: 130 (GAP-130-03)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""

from __future__ import annotations

from typing import Any, Dict, List

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)


class CortexContent(ConsolidatedTool):
    """Content Library MCP tool — select, history, reset, stats.

    Provides the LLM and orchestrators with a clean MCP interface over
    :class:`~cortex.intelligence.content_library_engine.ContentLibraryEngine`.

    Supported operations:
        - ``select``  — draw next item from a pool
        - ``history`` — recent-draw history for a pool
        - ``reset``   — reset pool to epoch 0
        - ``stats``   — per-pool statistics
    """

    @property
    def name(self) -> str:
        """Return tool name."""
        return "cortex_content"

    @property
    def description(self) -> str:
        """Return tool description."""
        return (
            "Manage CORTEX response content pools (quotes, principles, ai_sparks) "
            "with epoch-based anti-repetition. "
            "Operations: select|history|reset|stats."
        )

    @property
    def category(self) -> ToolCategory:
        """Return tool category."""
        return ToolCategory.INTELLIGENCE

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return supported parameters."""
        return [
            ToolParameter(
                name="op",
                type="string",
                description="Operation: select | history | reset | stats",
                required=True,
                enum=["select", "history", "reset", "stats"],
            ),
            ToolParameter(
                name="pool",
                type="string",
                description=(
                    "Pool name: quotes | principles | ai_sparks. "
                    "For 'select', can be a comma-separated list to invoke select_across()."
                ),
                required=False,
                default="quotes",
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return supported operation names."""
        return ["select", "history", "reset", "stats"]

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a content library operation.

        Args:
            **kwargs: Must include 'op'. May include 'pool'.

        Returns:
            ToolResult with the operation output in ``data``.
        """
        op: str = kwargs.get("op", "")
        pool: str = kwargs.get("pool", "quotes")

        try:
            from cortex.intelligence.content_library_engine import get_content_library_engine
            engine = get_content_library_engine()

            if op == "select":
                # Support comma-separated pool list for select_across()
                pools = [p.strip() for p in pool.split(",") if p.strip()]
                if len(pools) > 1:
                    result = engine.select_across(pools)
                else:
                    result = engine.select(pools[0] if pools else "quotes")
                return ToolResult(success=True, data=result)

            elif op == "history":
                hist = engine.history(pool)
                return ToolResult(success=True, data={"pool": pool, "history": hist})

            elif op == "reset":
                engine.reset(pool)
                return ToolResult(success=True, data={"pool": pool, "reset": True})

            elif op == "stats":
                stats = engine.stats()
                return ToolResult(success=True, data=stats)

            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation '{op}'. Valid: select, history, reset, stats",
                    data={},
                )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc),
                data={"op": op, "pool": pool},
            )
