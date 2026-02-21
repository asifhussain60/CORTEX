"""cortex_sweep_status — MCP tool for CORE-064 Sweep Completeness Contract.

Exposes SweepCatalogueOrchestrator status queries to Copilot Chat via MCP,
enabling in-chat visibility of open sweep items without leaving the editor.

Phase: PHASE-16
CORE: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical),
      CORE-064 (Sweep Completeness Contract)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# CORE-064: intents that trigger sweep catalogues
_CATALOGUE_INTENTS = {"FIX", "REFACTOR", "AUDIT"}


def cortex_sweep_status(
    sweep_id: Optional[str] = None,
    intent: Optional[str] = None,
    scope_files: Optional[List[str]] = None,
    orchestrator_context: Optional[Any] = None,
) -> Dict[str, Any]:
    """Return the current status of an open CORE-064 sweep catalogue.

    Can be called with an explicit ``sweep_id`` (direct lookup) or with
    ``intent`` + ``scope_files`` to locate the most-recent open catalogue
    for that scope.

    Args:
        sweep_id:
            The sweep_id returned by ``open_catalogue()``. If supplied,
            ``intent`` and ``scope_files`` are ignored.
        intent:
            Intent string used when the catalogue was opened
            (``"FIX"``, ``"REFACTOR"``, or ``"AUDIT"``).
            Used only when ``sweep_id`` is None.
        scope_files:
            Ordered list of scope file paths used when the catalogue was
            opened. Used only when ``sweep_id`` is None.
        orchestrator_context:
            Optional MasterOrchestrator context for routing validation
            (may be None in direct tool invocation).

    Returns:
        Dict with keys:

        - ``sweep_id`` (str): identifier of the catalogue
        - ``intent`` (str): FIX / REFACTOR / AUDIT
        - ``open_items_count`` (int): number of unresolved items
        - ``scope_files`` (list[str]): files in scope
        - ``next_items`` (list[dict]): up to 5 open issues (file, description)
        - ``status`` (str): "EXHAUSTED" | "IN_PROGRESS"
        - ``created_at`` (float): epoch timestamp

    Raises:
        KeyError:
            If no open catalogue is found for the given sweep_id or scope.
        ValueError:
            If neither ``sweep_id`` nor (``intent`` + ``scope_files``) is supplied.
    """
    # CORE-064 guard — validate orchestrator context if provided
    if orchestrator_context is not None:
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

            if not isinstance(orchestrator_context, MasterOrchestrator):
                raise TypeError(
                    "orchestrator_context must be a MasterOrchestrator instance"
                )
        except ImportError:
            pass  # Guard is best-effort; don't fail if MO not importable

    try:
        from cortex.orchestrators.support.sweep_catalogue_orchestrator import (
            SweepCatalogueOrchestrator,
        )
    except ImportError as exc:
        return {"error": f"SweepCatalogueOrchestrator not available: {exc}"}

    sco = SweepCatalogueOrchestrator()

    # Resolve sweep_id
    resolved_sweep_id: Optional[str] = sweep_id
    if resolved_sweep_id is None:
        if not intent or scope_files is None:
            raise ValueError(
                "cortex_sweep_status requires either 'sweep_id' or both "
                "'intent' and 'scope_files'."
            )
        # Attempt to locate an existing open catalogue for this scope
        resolved_sweep_id = sco._find_open_catalogue(
            intent=intent.upper(), scope_files=scope_files
        )
        if resolved_sweep_id is None:
            raise KeyError(
                f"No open sweep catalogue found for intent={intent!r} "
                f"scope_files={scope_files!r}. "
                "Open one via SweepCatalogueOrchestrator.open_catalogue() first."
            )

    # Fetch manifest (raises KeyError if not found)
    manifest = sco.get_manifest(resolved_sweep_id)

    # Fetch up to 5 open issues for "next items" preview
    import sqlite3

    db_path = sco._db_path(resolved_sweep_id)
    next_items: List[Dict[str, str]] = []
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT file, description FROM issues "
                "WHERE sweep_id=? AND status='OPEN' LIMIT 5",
                (resolved_sweep_id,),
            ).fetchall()
            conn.close()
            next_items = [{"file": r["file"], "description": r["description"]} for r in rows]
        except Exception:
            pass

    open_count = manifest["open_count"]
    return {
        "sweep_id": resolved_sweep_id,
        "intent": manifest["intent"],
        "open_items_count": open_count,
        "scope_files": manifest["scope_files"],
        "next_items": next_items,
        "status": "EXHAUSTED" if open_count == 0 else "IN_PROGRESS",
        "created_at": manifest["created_at"],
    }
