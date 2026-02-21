"""
Phase 20 Sub-Phase A — ADOContextMapper

Extracts structured sprint context from a list of WorkItem objects returned by
ADOWorkItemProvider.fetch_user_stories().  Maps raw ADO API fields (IterationPath,
AreaPath, State) to a typed sprint_context dict that is injected into
CompanyKnowledge.domain_rules["sprint_context"] in the FULL intelligence tier.

Authority: AC-P20-001, AC-P20-002, AC-P20-003, AC-P20-009, AC-P20-013
Rule: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from cortex.repositories.work_item_provider import WorkItem

logger = logging.getLogger(__name__)

# ADO field names (system fields)
_FIELD_ITERATION = "System.IterationPath"
_FIELD_AREA = "System.AreaPath"
_FIELD_STATE = "System.State"

# States considered "in progress" in ADO terminology
_IN_PROGRESS_STATES = {"Active", "In Progress", "Committed", "In Development"}


class ADOContextMapper:
    """
    Maps ADO WorkItem lists to structured sprint context dicts.

    All methods are class/static methods — no instantiation required.
    This makes the mapper easy to call from
    :meth:`~cortex.intelligence.provider.UnifiedIntelligenceProvider.full`
    without managing lifetime.

    Authority: AC-P20-001..AC-P20-003, AC-P20-009, AC-P20-013

    Example::

        from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper
        context = ADOContextMapper.map(stories)
        # context["sprint_name"]       → "Sprint 42"
        # context["stories"]           → [{"id": "1", "title": "...", ...}, ...]
        # context["open_count"]        → 3
        # context["in_progress_count"] → 2
    """

    @classmethod
    def map(cls, stories: List[WorkItem]) -> Dict[str, Any]:
        """
        Convert a list of WorkItem objects into a structured sprint context dict.

        Extracts sprint name from the first story's ``System.IterationPath`` field
        (taking the last path segment after ``\\``).  Counts stories by state.
        Handles missing or malformed ADO fields gracefully — never raises.

        Args:
            stories: List of :class:`~cortex.repositories.work_item_provider.WorkItem`
                     instances as returned by ``ADOWorkItemProvider.fetch_user_stories()``.
                     An empty list returns an empty context dict with zero counts.

        Returns:
            Dict with the following keys:

            - ``sprint_name`` (str): Sprint label extracted from IterationPath, or ``""``
              if unavailable.
            - ``stories`` (list[dict]): Per-story dicts with ``id``, ``title``,
              ``state``, and ``area_path`` keys.
            - ``open_count`` (int): Total number of stories in the list.
            - ``in_progress_count`` (int): Stories whose state is in
              ``{Active, In Progress, Committed, In Development}``.

        Example::

            from cortex.intelligence.knowledge.ado_context_mapper import ADOContextMapper
            ctx = ADOContextMapper.map([])
            assert ctx["open_count"] == 0
        """
        if not stories:
            return {
                "sprint_name": "",
                "stories": [],
                "open_count": 0,
                "in_progress_count": 0,
            }

        sprint_name = cls._extract_sprint_name(stories[0])

        mapped_stories: List[Dict[str, Any]] = []
        in_progress = 0

        for item in stories:
            state = cls._field(item, _FIELD_STATE) or item.state
            area = cls._field(item, _FIELD_AREA) or ""

            mapped_stories.append({
                "id": item.id,
                "title": item.title,
                "state": state,
                "area_path": area,
            })

            if state in _IN_PROGRESS_STATES:
                in_progress += 1

        logger.debug(
            "ADOContextMapper: sprint=%r, stories=%d, in_progress=%d",
            sprint_name,
            len(stories),
            in_progress,
        )

        return {
            "sprint_name": sprint_name,
            "stories": mapped_stories,
            "open_count": len(stories),
            "in_progress_count": in_progress,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _field(item: WorkItem, field_name: str) -> str:
        """
        Safely extract a field value from WorkItem.raw["fields"].

        Args:
            item: WorkItem instance.
            field_name: ADO system field name (e.g. ``"System.IterationPath"``).

        Returns:
            String value or empty string if absent / not a string.
        """
        try:
            value = item.raw.get("fields", {}).get(field_name, "")
            return str(value) if value else ""
        except Exception:  # noqa: BLE001
            return ""

    @classmethod
    def _extract_sprint_name(cls, item: WorkItem) -> str:
        """
        Extract the sprint label from a WorkItem's IterationPath.

        ADO stores iteration paths as backslash-delimited strings, e.g.
        ``"MyTeam\\Sprints\\Sprint 42"``.  This method returns the final
        segment (``"Sprint 42"``).  Falls back to the full path if no
        backslash separator is present.

        Args:
            item: WorkItem whose ``raw["fields"]["System.IterationPath"]`` is read.

        Returns:
            Sprint name string, or ``""`` if IterationPath is absent.
        """
        path = cls._field(item, _FIELD_ITERATION)
        if not path:
            return ""
        # Take the last segment after any backslash or forward-slash
        for sep in ("\\", "/"):
            if sep in path:
                return path.rsplit(sep, 1)[-1]
        return path
