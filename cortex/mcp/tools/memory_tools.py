"""
CortexBrainQuery MCP Tool — T1/T2/T3 brain tier query interface.

Authority: GAP-66-002 | Phase 66-A | SWEEP-66-INTELLIGENCE-MATRIX
CORE-011: type hints on all functions
CORE-012: docstrings on all public APIs

Operations:
  - query: Query a specific brain tier (T1, T2, T3)
  - build:  Build/refresh the brain tier index
  - persist: Persist tier data to .cortex-runtime/
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.file_factory import get_file_factory
from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)

# AC_START: AC-66-A-002-CORTEX-BRAIN-QUERY-MCP-TOOL-20260224T000000Z

_BRAIN_TIERS: Dict[str, str] = {
    "T1": "cortex/intelligence/tier1",
    "T2": "cortex/intelligence/tier2",
    "T3": "cortex/intelligence/tier3",
}


class CortexBrainQuery(ConsolidatedTool):
    """MCP tool for querying CORTEX brain tier memory stores.

    Provides structured access to T1 (operational), T2 (tactical), and
    T3 (knowledge) brain tiers, enabling cross-tier intelligence retrieval
    directly from Copilot Chat.

    Operations:
        - ``query``: Query memory entries from a specific brain tier.
        - ``build``:  Refresh/rebuild the brain tier index.
        - ``persist``: Persist tier index to ``.cortex-runtime/brain/``.

    Authority: GAP-66-002 | Phase 66-A
    """

    def __init__(self) -> None:
        """Initialise CortexBrainQuery."""
        super().__init__()

    @property
    def name(self) -> str:
        """Return the MCP tool name."""
        return "cortex_brain_query"

    @property
    def description(self) -> str:
        """Return the tool description."""
        return (
            "Query CORTEX brain tier memory stores (T1/T2/T3). "
            "Supports tier-specific intelligence retrieval, index building, "
            "and persistence to .cortex-runtime/brain/. "
            "Use op=query to retrieve memories, op=build to refresh the index."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the tool category."""
        return ToolCategory.INTELLIGENCE

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return tool parameters."""
        return [
            ToolParameter(
                name="op",
                type="string",
                description="Operation: 'query' (retrieve tier memories), 'build' (refresh index), 'persist' (save to disk)",
                required=True,
                enum=["query", "build", "persist"],
            ),
            ToolParameter(
                name="tier",
                type="string",
                description="Brain tier to target: 'T1' (operational), 'T2' (tactical), 'T3' (knowledge)",
                required=False,
                enum=["T1", "T2", "T3"],
            ),
            ToolParameter(
                name="orchestrator_context",
                type="object",
                description="MasterOrchestrator routing context (optional)",
                required=False,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return list of supported operation names."""
        return ["query", "build", "persist"]

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute a brain tier operation.

        Args:
            op: Operation to perform — 'query', 'build', or 'persist'.
            tier: Target brain tier — 'T1', 'T2', or 'T3' (default: all).
            orchestrator_context: Optional MasterOrchestrator routing context.

        Returns:
            :class:`~cortex.mcp.mcp_tool_base.ToolResult` with tier data or
            error details.
        """
        # AC_START: AC-66-A-002-EXEC-20260224T000000Z
        from cortex.mcp.tools._shared import validate_orchestrator_context

        orchestrator_context = kwargs.get("orchestrator_context")
        if orchestrator_context is not None:
            try:
                validate_orchestrator_context(orchestrator_context)
            except Exception:
                pass

        op = kwargs.get("op", "query")
        tier = kwargs.get("tier")

        if op == "query":
            result = self._query_tier(tier)
            # AC_COMPLETE: AC-66-A-002-EXEC-20260224T000000Z ✅
            return ToolResult(
                success=True,
                data=result,
                metadata={"op": "query", "tier": tier or "all", "formatted": True},
            )

        elif op == "build":
            result = self._build_index(tier)
            # AC_COMPLETE: AC-66-A-002-EXEC-20260224T000000Z ✅
            return ToolResult(
                success=True,
                data=result,
                metadata={"op": "build", "tier": tier or "all", "formatted": True},
            )

        elif op == "persist":
            result = self._persist_tier(tier)
            # AC_COMPLETE: AC-66-A-002-EXEC-20260224T000000Z ✅
            return ToolResult(
                success=True,
                data=result,
                metadata={"op": "persist", "tier": tier or "all", "formatted": True},
            )

        # AC_COMPLETE: AC-66-A-002-EXEC-20260224T000000Z ❌ unknown op
        return ToolResult(
            success=False,
            error=f"Unknown operation '{op}'. Supported: {self.supported_operations}",
            metadata={"op": op},
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _query_tier(self, tier: Optional[str]) -> Dict[str, Any]:
        """Query memory entries from one or all brain tiers.

        Args:
            tier: Specific tier ('T1', 'T2', 'T3') or None for all.

        Returns:
            Dict mapping tier keys to their module listing.
        """
        tiers = {tier: _BRAIN_TIERS[tier]} if tier and tier in _BRAIN_TIERS else _BRAIN_TIERS
        memories: Dict[str, Any] = {}
        for tier_key, tier_path in tiers.items():
            tier_dir = Path(tier_path)
            if tier_dir.exists():
                entries = [p.name for p in tier_dir.iterdir() if not p.name.startswith("__")]
                memories[tier_key] = {"path": str(tier_dir), "entries": entries}
            else:
                memories[tier_key] = {"path": str(tier_dir), "entries": [], "note": "directory not found"}
        return memories

    def _build_index(self, tier: Optional[str]) -> Dict[str, Any]:
        """Refresh brain tier index.

        Args:
            tier: Specific tier to rebuild or None for all.

        Returns:
            Dict with indexed tier counts.
        """
        tiers = {tier: _BRAIN_TIERS[tier]} if tier and tier in _BRAIN_TIERS else _BRAIN_TIERS
        indexed: Dict[str, int] = {}
        for tier_key, tier_path in tiers.items():
            tier_dir = Path(tier_path)
            if tier_dir.exists():
                count = sum(1 for _ in tier_dir.rglob("*.py"))
                indexed[tier_key] = count
            else:
                indexed[tier_key] = 0
        return {"indexed": indexed, "status": "built"}

    def _persist_tier(self, tier: Optional[str]) -> Dict[str, Any]:
        """Persist brain tier index to .cortex-runtime/brain/.

        Args:
            tier: Specific tier to persist or None for all.

        Returns:
            Dict with persisted file paths.
        """
        from datetime import datetime

        runtime_dir = Path(".cortex-runtime/brain")
        runtime_dir.mkdir(parents=True, exist_ok=True)

        data = self._query_tier(tier)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out_filename = f"brain-tier-index-{timestamp}.json"
        out_path = runtime_dir / out_filename

        ff = get_file_factory()
        ff.create_file(str(out_path), json.dumps(data, indent=2))

        return {"persisted_to": str(out_path), "tiers": list(data.keys())}


# AC_COMPLETE: AC-66-A-002-CORTEX-BRAIN-QUERY-MCP-TOOL-20260224T000000Z ✅
