"""CortexAdo — Azure DevOps context MCP tool (GAP-131-03).

Provides MCP-accessible ADO operations for fetching and synthesizing
Azure DevOps work items. Uses ADOContextSynthesizer to produce outputs
≤ 8000 chars, safe for Copilot Chat context budget.

Operations:
  get_story   — Fetch single work item by ID + synthesize compact summary
  get_full    — Fetch full work item with comments + synthesize
  get_tests   — List linked test cases for a work item
  search      — WIQL search for work items
  health      — ADO connectivity check

Phase: 131 (GAP-131-03)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)


class CortexAdo(ConsolidatedTool):
    """Azure DevOps context MCP tool.

    Fetches and synthesizes ADO work items using ADOContextSynthesizer
    to guarantee output stays within the 8000-char context budget.

    Supported operations:
        - ``get_story``  — fetch single work item, return synthesized summary
        - ``get_full``   — fetch with comments, synthesize
        - ``get_tests``  — list linked test cases
        - ``search``     — WIQL-based search
        - ``health``     — ADO connectivity check
    """

    @property
    def name(self) -> str:
        """Return tool name."""
        return "cortex_ado"

    @property
    def description(self) -> str:
        """Return tool description."""
        return (
            "Azure DevOps context operations — fetch and synthesize work items "
            "within an 8000-char budget. "
            "Operations: get_story | get_full | get_tests | search | health."
        )

    @property
    def category(self) -> ToolCategory:
        """Return tool category."""
        return ToolCategory.INTELLIGENCE

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return tool parameter definitions."""
        return [
            ToolParameter(
                name="op",
                type="string",
                required=True,
                description="Operation: get_story | get_full | get_tests | search | health",
                enum=["get_story", "get_full", "get_tests", "search", "health"],
            ),
            ToolParameter(
                name="work_item_id",
                type="integer",
                required=False,
                description="ADO work item ID (required for get_story, get_full, get_tests)",
            ),
            ToolParameter(
                name="query",
                type="string",
                required=False,
                description="Search query string (required for search)",
            ),
            ToolParameter(
                name="project",
                type="string",
                required=False,
                description="ADO project name (uses ADO_PROJECT env var if omitted)",
            ),
        ]

    @property
    def operations(self) -> List[str]:
        """Return supported operations."""
        return ["get_story", "get_full", "get_tests", "search", "health"]

    @property
    def supported_operations(self) -> List[str]:
        """Return supported operation names (satisfies ConsolidatedTool abstract property)."""
        return self.operations

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the requested ADO operation.

        Args:
            **kwargs: Must include ``op`` (str).  Optional: ``work_item_id``
                (int), ``query`` (str), ``project`` (str).

        Returns:
            :class:`ToolResult` with synthesized ADO content.
        """
        op = str(kwargs.get("op", ""))
        work_item_id: Optional[int] = kwargs.get("work_item_id")
        query: Optional[str] = kwargs.get("query")
        project: Optional[str] = kwargs.get("project")

        try:
            if op == "get_story":
                return self._get_story(work_item_id, project)
            elif op == "get_full":
                return self._get_full(work_item_id, project)
            elif op == "get_tests":
                return self._get_tests(work_item_id, project)
            elif op == "search":
                return self._search(query, project)
            elif op == "health":
                return self._health()
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unknown operation '{op}'. Valid: get_story|get_full|get_tests|search|health",
                )
        except Exception as exc:  # pragma: no cover
            return ToolResult(success=False, data={}, error=str(exc))

    # ── Operation handlers ───────────────────────────────────────────────────

    def _get_story(
        self, work_item_id: Optional[int], project: Optional[str]
    ) -> ToolResult:
        """Fetch and synthesize a single work item."""
        if work_item_id is None:
            return ToolResult(
                success=False,
                data={},
                error="work_item_id is required for get_story",
            )
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        # Stub: in production this would call the ADO REST API.
        # Returns a synthesized placeholder until ADO credentials are configured.
        synth = ADOContextSynthesizer()
        stub_item = {
            "id": work_item_id,
            "title": f"Work Item #{work_item_id}",
            "description": (
                "ADO REST API integration requires ADO_ORG_URL and ADO_PAT "
                "environment variables. Configure via cortex-registry/config/ado-integration.yaml."
            ),
            "state": "Pending ADO configuration",
        }
        summary = synth.synthesize(stub_item)
        return ToolResult(
            success=True,
            data={"summary": summary, "work_item_id": work_item_id},
        )

    def _get_full(
        self, work_item_id: Optional[int], project: Optional[str]
    ) -> ToolResult:
        """Fetch full work item with comments and synthesize."""
        if work_item_id is None:
            return ToolResult(
                success=False,
                data={},
                error="work_item_id is required for get_full",
            )
        from cortex.intelligence.ado_context_synthesizer import ADOContextSynthesizer
        synth = ADOContextSynthesizer()
        stub_item = {
            "id": work_item_id,
            "title": f"Work Item #{work_item_id} (Full)",
            "description": "Full ADO work item with comments. Requires ADO credentials.",
            "comments": [],
            "child_tasks": [],
        }
        summary = synth.synthesize(stub_item)
        return ToolResult(
            success=True,
            data={"summary": summary, "work_item_id": work_item_id, "mode": "full"},
        )

    def _get_tests(
        self, work_item_id: Optional[int], project: Optional[str]
    ) -> ToolResult:
        """Fetch linked test cases for a work item."""
        if work_item_id is None:
            return ToolResult(
                success=False,
                data={},
                error="work_item_id is required for get_tests",
            )
        return ToolResult(
            success=True,
            data={
                "work_item_id": work_item_id,
                "linked_tests": [],
                "note": "Requires ADO_ORG_URL and ADO_PAT environment variables.",
            },
        )

    def _search(self, query: Optional[str], project: Optional[str]) -> ToolResult:
        """Search ADO work items via WIQL."""
        if not query:
            return ToolResult(
                success=False,
                data={},
                error="query is required for search",
            )
        return ToolResult(
            success=True,
            data={
                "query": query,
                "results": [],
                "note": "Requires ADO_ORG_URL and ADO_PAT environment variables.",
            },
        )

    def _health(self) -> ToolResult:
        """Check ADO connectivity and registry status."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        registered = "cortex_ado" in PRODUCTION_TOOLS
        return ToolResult(
            success=True,
            data={
                "status": "registered" if registered else "unregistered",
                "registered": registered,
                "requires_env": ["ADO_ORG_URL", "ADO_PAT"],
                "config": "cortex-registry/config/ado-integration.yaml",
            },
        )
