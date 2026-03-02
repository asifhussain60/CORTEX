"""Health Scan MCP Tool — Phase-51

Exposes HealthOrchestrator.scan() via MCP for Copilot Chat.
Supports operations: ``scan``, ``classify``, ``status``.

Phase: PHASE-51
CORE: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def cortex_health_scan(
    workspace_root: str,
    operation: str = "scan",
) -> Dict[str, Any]:
    """Run a holistic health scan on a CORTEX workspace.

    Args:
        workspace_root: Absolute path to the repository root.
        operation: One of:
            - ``"scan"`` — full scan returning score, totals, and issues.
            - ``"classify"`` — scan then group issues by category.
            - ``"status"`` — lightweight summary (score + totals only).

    Returns:
        Dict with scan results, or ``{"error": ...}`` on failure.

    Example::

        result = cortex_health_scan("/path/to/repo")
        print(result["health_score"])
    """
    workspace_path = Path(workspace_root)

    if not workspace_path.exists():
        return {"error": f"Workspace not found: {workspace_root}"}

    try:
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator

        orchestrator = HealthOrchestrator(workspace_path)
        scan_result = orchestrator.scan()
    except Exception as exc:
        logger.exception("Health scan failed")
        return {"error": f"Health scan failed: {exc}"}

    if operation == "scan":
        return _format_scan(scan_result)
    elif operation == "classify":
        return _format_classify(scan_result)
    elif operation == "status":
        return _format_status(scan_result)
    else:
        return {"error": f"Unknown operation: {operation}"}


# ── formatters ────────────────────────────────────────────────────────────


def _format_scan(scan_result: Any) -> Dict[str, Any]:
    """Full scan output with issue details."""
    data = scan_result.to_dict()
    # Limit issues to first 50 for MCP payload size
    if len(data.get("issues", [])) > 50:
        data["issues"] = data["issues"][:50]
        data["issues_truncated"] = True
    return data


def _format_classify(scan_result: Any) -> Dict[str, Any]:
    """Group issues by category."""
    categories: Dict[str, list] = defaultdict(list)
    for issue in scan_result.issues:
        cat = issue.category or "uncategorised"
        categories[cat].append({
            "check_id": issue.check_id,
            "path": str(issue.path),
            "severity": issue.severity.value,
            "description": issue.description,
        })
    return {
        "health_score": scan_result.health_score,
        "total_issues": scan_result.total_issues,
        "categories": {k: v for k, v in categories.items()},
    }


def _format_status(scan_result: Any) -> Dict[str, Any]:
    """Lightweight summary — score + severity counts."""
    return {
        "health_score": scan_result.health_score,
        "total_issues": scan_result.total_issues,
        "by_severity": {
            "critical": scan_result.critical_issues,
            "high": scan_result.high_issues,
            "medium": scan_result.medium_issues,
            "low": scan_result.low_issues,
            "info": scan_result.info_issues,
        },
        "files_scanned": scan_result.files_scanned,
    }


__all__ = ["cortex_health_scan"]
