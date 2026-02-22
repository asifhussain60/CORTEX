"""
cortex_query_opj — MCP Tool for querying the Operational Pattern Journal.

Exposes the OPJ to Copilot Chat, enabling queries like:
  "What failed last time DigestSessionOrchestrator processed markdown?"
  "What patterns worked for TDDOrchestrator red_phase?"

MCP Tool #26 — Phase 52 Stage C

AC-ID: AC-OPJ-PHASE52-MCP
CORE: CORE-002 (inline output), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-050 (MCP-first exposure)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_REGISTRY = _WORKSPACE_ROOT / "cortex-registry"


def cortex_query_opj(
    orchestrator: Optional[str],
    operation: Optional[str] = None,
    outcome_filter: str = "all",
    limit: int = 5,
    registry_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query the Operational Pattern Journal for prior success/failure patterns.

    Use this BEFORE implementing any operation to check whether it has been
    attempted before and what succeeded or failed. Results are ranked by
    confidence descending.

    Args:
        orchestrator: Orchestrator class name to filter by.
                      Pass None to query across all orchestrators.
        operation: Operation name to filter by.
                   Pass None to query all operations for the orchestrator.
        outcome_filter: One of 'success', 'failure', 'all' (default 'all').
        limit: Maximum number of entries to return (default 5).
        registry_root: Override registry path (used in tests). Omit in production.

    Returns:
        Dict with keys:
          entries      — list of OPJ entry dicts ranked by confidence
          total_found  — count of matching entries
          orchestrator — echoed filter
          operation    — echoed filter
          outcome_filter — echoed filter

    Example::

        result = cortex_query_opj(
            orchestrator="DigestSessionOrchestrator",
            operation="process",
            outcome_filter="failure",
            limit=3,
        )
        for e in result["entries"]:
            print(e["error"], "→", e.get("avoid_in_future"))
    """
    root = Path(registry_root) if registry_root else _DEFAULT_REGISTRY

    try:
        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=root)

        if outcome_filter == "failure":
            entries = reader.query_failures(orchestrator=orchestrator, operation=operation, limit=limit)
        elif outcome_filter == "success":
            entries = reader.query_successes(orchestrator=orchestrator, operation=operation, limit=limit)
        else:
            entries = reader.query_patterns(orchestrator=orchestrator, operation=operation, limit=limit)

        return {
            "entries": entries,
            "total_found": len(entries),
            "orchestrator": orchestrator,
            "operation": operation,
            "outcome_filter": outcome_filter,
            "registry_root": str(root),
        }

    except Exception as exc:
        logger.error("cortex_query_opj: error — %s", exc)
        return {
            "entries": [],
            "total_found": 0,
            "orchestrator": orchestrator,
            "operation": operation,
            "outcome_filter": outcome_filter,
            "error": str(exc),
        }
