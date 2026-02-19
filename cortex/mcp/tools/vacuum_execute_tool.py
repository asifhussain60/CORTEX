"""Vacuum Execute MCP Tool — Phase-51

Exposes VacuumOrchestrator via MCP for Copilot Chat.
Supports operations: ``run``, ``preview``, ``naming_fix``,
``root_cleanup``, ``markdown_archive``, ``empty_cleanup``,
``execute`` (companion), ``rollback``.

Phase: PHASE-51
CORE: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def cortex_vacuum_execute(
    workspace_root: str,
    operation: str = "run",
    handoff_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute vacuum operations on a CORTEX workspace.

    Args:
        workspace_root: Absolute path to the repository root.
        operation: One of:
            - ``"run"`` — standalone: quick-scan + execute all ops.
            - ``"preview"`` — dry-run: plan operations without executing.
            - ``"naming_fix"`` — standalone: fix naming violations only.
            - ``"root_cleanup"`` — standalone: relocate root files.
            - ``"markdown_archive"`` — standalone: archive stale markdown.
            - ``"empty_cleanup"`` — standalone: delete empty files/dirs.
            - ``"execute"`` — companion: consume handoff YAML from health scan.
            - ``"rollback"`` — reverse previous vacuum operations.
        handoff_path: Path to ``health-issues.yaml`` (required for ``execute``
            and ``rollback`` operations).

    Returns:
        Dict with vacuum results, or ``{"error": ...}`` on failure.

    Example::

        result = cortex_vacuum_execute("/path/to/repo", operation="preview")
        print(result["total_operations"])
    """
    workspace_path = Path(workspace_root)

    if not workspace_path.exists():
        return {"error": f"Workspace not found: {workspace_root}"}

    try:
        from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

        vac = VacuumOrchestrator(workspace_path)

        if operation == "run":
            report = vac.run()
            return report.to_dict()

        elif operation == "preview":
            report = vac.run(dry_run=True)
            data = report.to_dict()
            data["dry_run"] = True
            return data

        elif operation == "naming_fix":
            results = vac.run_naming_fix()
            return _ops_to_dict(results, "naming_fix")

        elif operation == "root_cleanup":
            results = vac.run_root_cleanup()
            return _ops_to_dict(results, "root_cleanup")

        elif operation == "markdown_archive":
            results = vac.run_markdown_archive()
            return _ops_to_dict(results, "markdown_archive")

        elif operation == "empty_cleanup":
            results = vac.run_empty_cleanup()
            return _ops_to_dict(results, "empty_cleanup")

        elif operation == "execute":
            if not handoff_path:
                return {"error": "handoff_path is required for 'execute' operation"}
            hp = Path(handoff_path)
            if not hp.exists():
                return {"error": f"Handoff file not found: {handoff_path}"}
            report = vac.consume(hp)
            return report.to_dict()

        elif operation == "rollback":
            if not handoff_path:
                return {"error": "handoff_path is required for 'rollback' operation (path to rollback manifest)"}
            mp = Path(handoff_path)
            if not mp.exists():
                return {"error": f"Rollback manifest not found: {handoff_path}"}
            vac.rollback(mp)
            return {"status": "rollback_complete", "manifest": handoff_path}

        else:
            return {"error": f"Unknown operation: {operation}"}

    except Exception as exc:
        logger.exception("Vacuum execution failed")
        return {"error": f"Vacuum execution failed: {exc}"}


# ── helper ────────────────────────────────────────────────────────────────


def _ops_to_dict(
    results: list,
    operation_name: str,
) -> Dict[str, Any]:
    """Convert a list of OperationResult to a summary dict."""
    total = len(results)
    successes = sum(1 for r in results if r.success)
    return {
        "operation": operation_name,
        "total_operations": total,
        "successful_operations": successes,
        "failed_operations": total - successes,
        "operations": [r.to_dict() for r in results],
    }


__all__ = ["cortex_vacuum_execute"]
