"""
Phase 123 — Registry Intelligence Engine
MCP Tool: CortexRegistry

Exposes all 5 IntelligenceFacade registry methods as a single MCP tool:
  - query_governance : load governance rules (optionally filtered by severity)
  - query_workflows  : load workflow templates (optionally filtered by category)
  - query_patterns   : load custom patterns (optionally filtered by tag)
  - query_plans      : load cortex-master.yaml phase index (optionally filtered by status)
  - registry_index   : full cortex-registry/ tree scan (optionally filtered by domain)

CORE Rules: CORE-008 (TDD-first), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-035 (single canonical implementation), CORE-049 (silent autonomous)

AC_START: AC-123-MCP-REGISTRY-TOOL
"""
from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context

logger = logging.getLogger(__name__)

_SUPPORTED_OPS = [
    "query_governance",
    "query_workflows",
    "query_patterns",
    "query_plans",
    "registry_index",
]


class CortexRegistry(ConsolidatedTool):
    """
    Registry intelligence MCP tool.

    Routes the ``op`` parameter to the matching :class:`IntelligenceFacade`
    method and returns a uniform :class:`ToolResult`.  Each successful result
    carries a single top-level key in ``data`` that matches what the caller
    expects (``rules``, ``templates``, ``patterns``, ``phases``, ``entries``).
    """

    # ------------------------------------------------------------------
    # ConsolidatedTool abstract properties
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the canonical MCP tool name."""
        return "cortex_registry"

    @property
    def description(self) -> str:
        """Return the tool description."""
        return (
            "Registry intelligence: query governance rules, workflow templates, "
            "patterns, plans, and the full cortex-registry/ index. "
            "op: query_governance | query_workflows | query_patterns | "
            "query_plans | registry_index. "
            "Optional 'filter' narrows by severity / category / tag / status / domain."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the governance category."""
        return ToolCategory.GOVERNANCE

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the tool parameter definitions."""
        return [
            ToolParameter(
                name="op",
                type="string",
                description=(
                    "Registry operation: query_governance | query_workflows | "
                    "query_patterns | query_plans | registry_index"
                ),
                required=True,
                enum=_SUPPORTED_OPS,
            ),
            ToolParameter(
                name="filter",
                type="string",
                description=(
                    "Optional filter value.  Semantics depend on op: "
                    "query_governance → severity (P0/P1/P2/P3), "
                    "query_workflows → category string, "
                    "query_patterns → tag string, "
                    "query_plans → status (PLANNED/IN_PROGRESS/COMPLETE), "
                    "registry_index → domain label."
                ),
                required=False,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the list of supported op values."""
        return _SUPPORTED_OPS

    # ------------------------------------------------------------------
    # Execution entry point
    # ------------------------------------------------------------------

    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Dispatch the registry operation and return a :class:`ToolResult`.

        Accepted kwargs
        ---------------
        params : dict
            Must contain ``"op"`` key.  Optional ``"filter"`` key.
        orchestrator_context : optional
            Validated when non-None (CORTEX routing guard).

        Returns
        -------
        ToolResult
            ``success=True`` with a payload dict keyed by result type, or
            ``success=False`` with an ``error`` string for unknown ops.
        """
        orchestrator_context = kwargs.get("orchestrator_context")
        if orchestrator_context is not None:
            validate_orchestrator_context(orchestrator_context)

        params: Dict[str, Any] = kwargs.get("params", {})
        op: str = params.get("op", "")
        filter_val: Optional[str] = params.get("filter")

        try:
            if op == "query_governance":
                return self._query_governance(filter_val)
            elif op == "query_workflows":
                return self._query_workflows(filter_val)
            elif op == "query_patterns":
                return self._query_patterns(filter_val)
            elif op == "query_plans":
                return self._query_plans(filter_val)
            elif op == "registry_index":
                return self._registry_index(filter_val)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown op: '{op}'. Supported: {_SUPPORTED_OPS}",
                )
        except Exception as exc:  # pragma: no cover — defensive catch
            logger.warning(
                "CortexRegistry op=%s raised: %s",
                op,
                exc,
                exc_info=True,
            )
            return ToolResult(success=False, error=str(exc))

    # ------------------------------------------------------------------
    # Private dispatch helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_facade():  # type: ignore[return]
        """Lazy-import IntelligenceFacade to avoid circular imports."""
        from cortex.intelligence.facade import IntelligenceFacade

        return IntelligenceFacade()

    def _query_governance(self, severity: Optional[str]) -> ToolResult:
        """Return governance rules, optionally filtered by severity."""
        facade = self._get_facade()
        rules: List[Dict[str, Any]] = facade.load_governance(severity=severity)
        return ToolResult(success=True, data={"rules": rules})

    def _query_workflows(self, category: Optional[str]) -> ToolResult:
        """Return workflow templates, optionally filtered by category."""
        facade = self._get_facade()
        templates: List[Dict[str, Any]] = facade.load_workflows(category=category)
        return ToolResult(success=True, data={"templates": templates})

    def _query_patterns(self, tag: Optional[str]) -> ToolResult:
        """Return custom patterns, optionally filtered by tag."""
        facade = self._get_facade()
        patterns: List[Dict[str, Any]] = facade.load_patterns(tag=tag)
        return ToolResult(success=True, data={"patterns": patterns})

    def _query_plans(self, status: Optional[str]) -> ToolResult:
        """Return phases from cortex-master.yaml, optionally filtered by status."""
        facade = self._get_facade()
        plan_index = facade.load_plans(status=status)
        phases = [asdict(p) for p in plan_index.phases]
        return ToolResult(
            success=True,
            data={"phases": phases},
            metadata={
                "source_line_count": plan_index.source_line_count,
                "source_path": plan_index.source_path,
            },
        )

    def _registry_index(self, domain: Optional[str]) -> ToolResult:
        """Return the cortex-registry/ tree index, optionally filtered by domain."""
        facade = self._get_facade()
        entries = facade.registry_index(domain=domain)
        return ToolResult(
            success=True,
            data={"entries": [asdict(e) for e in entries]},
        )
