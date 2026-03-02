"""
cortex_fetch_work_items — MCP Tool for Work Item Provider access.

Exposes WorkItemProvider to Copilot Chat via the standard MCP surface.
All requests MUST route through MasterOrchestrator; direct invocations
are rejected by the ``validate_orchestrator_context`` guard (CORE-050).

Usage from Copilot Chat (via MasterOrchestrator routing):
    cortex_fetch_work_items(project="MyProject",
                            orchestrator_context={"source": "MasterOrchestrator"})

The underlying provider is selected by the ``WORK_ITEM_SOURCE`` environment
variable (default: "ado"). Companies set this once in their deployment config;
the MCP tool surface is identical regardless of which system is behind it.

Authority: CORE-011 (type hints) · CORE-012 (docstrings) · CORE-050 (MCP-first)
Phase: Phase 15 — Work Item Provider
AC-IDs: AC-P15-006, AC-P15-007, AC-P15-008
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from cortex.mcp.tools._shared import validate_orchestrator_context
from cortex.repositories.provider_factory import get_work_item_provider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP Tool Schema — registered with the MCP server at startup
# ---------------------------------------------------------------------------

TOOL_SCHEMA: Dict[str, Any] = {
    "name": "cortex_fetch_work_items",
    "description": (
        "Fetch work items (user stories, bugs, tasks) from the configured "
        "ticketing system (ADO, Jira, custom). Provider selected via "
        "WORK_ITEM_SOURCE env var. Returns a list of WorkItem dicts with "
        "id, title, description, state, type, tags, url, and raw fields."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "project": {
                "type": "string",
                "description": "Project name or identifier in the source system.",
            },
            "item_id": {
                "type": "string",
                "description": (
                    "Optional. When supplied, fetch a single work item by ID "
                    "instead of fetching all user stories."
                ),
            },
            "filters": {
                "type": "object",
                "description": (
                    "Optional provider-specific filter dict "
                    "(e.g. {\"sprint\": \"Sprint 42\", \"state\": \"Active\"})."
                ),
            },
        },
        "required": ["project"],
    },
}


# ---------------------------------------------------------------------------
# Tool function
# ---------------------------------------------------------------------------

def cortex_fetch_work_items(
    project: str,
    orchestrator_context: Optional[Dict[str, Any]] = None,
    item_id: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Fetch work items from the configured ticketing system.

    This is the single MCP-exposed surface for all work item access.
    The concrete provider (ADO, Jira, custom) is selected at runtime by
    the ``WORK_ITEM_SOURCE`` environment variable — this tool is unaware
    of which system it is calling.

    Args:
        project: Project name or identifier in the source system.
        orchestrator_context: Routing context from MasterOrchestrator.
            Must be ``{"source": "MasterOrchestrator"}`` or the call is
            rejected (CORE-050).
        item_id: When supplied, fetches a single work item by ID instead
            of all user stories for the project.
        filters: Optional provider-specific filter dict forwarded verbatim
            to the provider (e.g. ``{"sprint": "Sprint 42"}``).

    Returns:
        Dict with keys:
            - ``status``: ``"success"`` or ``"error"``
            - ``project``: echo of the project argument
            - ``items``: list of work item dicts (empty on error)
            - ``count``: number of items returned
            - ``error``: error message string (only present on failure)

    Raises:
        ValueError: When ``orchestrator_context`` is missing or its
            ``source`` is not ``"MasterOrchestrator"`` (CORE-050).
    """
    # Governance gate — CORE-050: MCP-first, MasterOrchestrator only
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)
    else:
        validate_orchestrator_context(orchestrator_context)  # raises ValueError

    filters = filters or {}
    logger.info(
        "cortex_fetch_work_items: project=%r item_id=%r filters=%s",
        project,
        item_id,
        filters,
    )

    try:
        provider = get_work_item_provider()

        if item_id:
            work_item = provider.fetch_by_id(item_id)
            items = [_serialise(work_item)]
        else:
            work_items = provider.fetch_user_stories(project, **filters)
            items = [_serialise(wi) for wi in work_items]

        return {
            "status": "success",
            "project": project,
            "items": items,
            "count": len(items),
        }

    except Exception as exc:  # noqa: BLE001
        logger.error("cortex_fetch_work_items error: %s", exc)
        return {
            "status": "error",
            "project": project,
            "items": [],
            "count": 0,
            "error": str(exc),
        }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _serialise(work_item: Any) -> Dict[str, Any]:
    """
    Convert a WorkItem dataclass to a JSON-serialisable dict.

    Args:
        work_item: A WorkItem instance from any provider.

    Returns:
        Dict with all WorkItem fields, suitable for JSON serialisation.
    """
    return {
        "id": work_item.id,
        "title": work_item.title,
        "description": work_item.description,
        "state": work_item.state,
        "type": work_item.type,
        "tags": work_item.tags,
        "url": work_item.url,
        "raw": work_item.raw,
    }
