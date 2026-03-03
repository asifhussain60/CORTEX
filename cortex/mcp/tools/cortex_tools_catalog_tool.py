"""
CortexToolsCatalog — Tool discovery, catalog, and feature recall.

Extracted from cortex/mcp/tools/utilities.py (Phase 103-d, GAP-103-07).
Single Responsibility: List, search, describe MCP tools and discover/recall
CORTEX features and components (absorbs cortex_total_recall ops — WAVE-101).

CORE-011: type hints | CORE-012: docstrings
"""
from __future__ import annotations

from typing import List, Optional

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context


class CortexToolsCatalog(ConsolidatedTool):
    """
    Tool discovery, catalog, and feature recall.

    Consolidates cortex_tools_catalog (tool discovery) + cortex_total_recall
    (feature/component discovery) into one tool.

    Operations (catalog):
    - list: List all registered MCP tools
    - search: Search tools by keyword
    - describe: Get detailed tool description
    - categories: List tool categories

    Operations (recall — formerly cortex_total_recall):
    - discover: Discover CORTEX features and components
    - recall: Recall a specific named feature
    """

    @property
    def name(self) -> str:
        """Return the name."""
        return "cortex_tools_catalog"

    @property
    def description(self) -> str:
        """Return the description."""
        return (
            "Discover all MCP tools and CORTEX features. List, search, describe tools; "
            "discover and recall features and components."
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
                description="Operation: list | search | describe | categories | discover | recall",
                required=True,
                enum=["list", "search", "describe", "categories", "discover", "recall"],
            ),
            ToolParameter(
                name="query",
                type="string",
                description="Search query, tool name, or feature name",
                required=False,
            ),
            ToolParameter(
                name="category",
                type="string",
                description="Filter by category",
                required=False,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the supported operations."""
        return ["list", "search", "describe", "categories", "discover", "recall"]

    async def execute(self, **params) -> ToolResult:
        """Execute catalog or recall operation."""
        # ENFORCEMENT: Validate orchestrator routing
        _oc = params.get("orchestrator_context")
        if _oc is not None:
            validate_orchestrator_context(_oc)

        operation = params.get("operation", "list")
        query = params.get("query")
        category = params.get("category")

        # Import registry for actual tool data
        from cortex.mcp.mcp_registry import get_registry
        registry = get_registry()

        if operation == "list":
            all_metadata = registry.list_all()
            tools = [{"name": m.id, "description": m.description, "category": m.category.value} for m in all_metadata]
            if category:
                tools = [t for t in tools if t.get("category") == category]
            return ToolResult(
                success=True,
                data={
                    "tools": tools,
                    "total": len(tools),
                    "category_filter": category,
                },
                metadata={"operation": "list"},
            )

        elif operation == "search":
            if not query:
                return ToolResult(success=False, error="query required for search")
            all_metadata = registry.list_all()
            matching = [
                {"name": m.id, "description": m.description, "category": m.category.value}
                for m in all_metadata
                if query.lower() in m.id.lower()
                or query.lower() in m.description.lower()
            ]
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": matching,
                    "total": len(matching),
                },
                metadata={"operation": "search"},
            )

        elif operation == "describe":
            if not query:
                return ToolResult(success=False, error="tool name required for describe")
            tool_metadata = registry.get_metadata(query)
            if tool_metadata:
                return ToolResult(
                    success=True,
                    data={
                        "name": query,
                        "description": tool_metadata.description,
                        "category": tool_metadata.category.value,
                        "parameters": [p.to_schema() for p in tool_metadata.parameters],
                        "operations": tool_metadata.operations,
                    },
                    metadata={"operation": "describe"},
                )
            return ToolResult(success=False, error=f"Tool not found: {query}")

        elif operation == "categories":
            return ToolResult(
                success=True,
                data={
                    "categories": [
                        {"name": "CORE", "count": 4},
                        {"name": "INTELLIGENCE", "count": 4},
                        {"name": "GOVERNANCE", "count": 3},
                        {"name": "OPERATIONS", "count": 7},
                        {"name": "UTILITIES", "count": 7},
                    ],
                    "total": 25,
                },
                metadata={"operation": "categories"},
            )

        # ------------------------------------------------------------------
        # Recall operations (absorbed from cortex_total_recall — WAVE-101)
        # ------------------------------------------------------------------
        elif operation == "discover":
            features = self._get_features(category)
            return ToolResult(
                success=True,
                data={
                    "features": features,
                    "total": len(features),
                    "category_filter": category,
                },
                metadata={"operation": "discover"},
            )

        elif operation == "recall":
            if not query:
                return ToolResult(success=False, error="feature name required for recall")
            matching = [f for f in self._get_features() if query.lower() in f["name"].lower()]
            return ToolResult(
                success=True,
                data={
                    "feature": query,
                    "matches": matching,
                },
                metadata={"operation": "recall"},
            )

        return ToolResult(success=False, error=f"Unknown operation: {operation}")

    @staticmethod
    def _get_features(category: Optional[str] = None) -> list:
        """Return known CORTEX features, optionally filtered by category."""
        features = [
            {"name": "MCP Server", "category": "infrastructure", "status": "active"},
            {"name": "TDD Orchestrator", "category": "orchestration", "status": "active"},
            {"name": "LENS Analysis", "category": "intelligence", "status": "active"},
            {"name": "Governance Engine", "category": "enforcement", "status": "active"},
            {"name": "Challenge Engine", "category": "validation", "status": "active"},
            {"name": "RCA Memory Engine", "category": "intelligence", "status": "active"},
            {"name": "Debug Pipeline", "category": "operations", "status": "active"},
            {"name": "Vacuum Orchestrator", "category": "maintenance", "status": "active"},
        ]
        if category:
            features = [f for f in features if f["category"] == category]
        return features
