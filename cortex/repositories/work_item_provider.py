"""
WorkItemProvider — Company-Pluggable Work Item Protocol + WorkItem Dataclass.

This module defines the SSOT Protocol for all work item integrations (ADO, Jira,
ServiceNow, custom company APIs). Companies implement WorkItemProvider once;
CORTEX routes all ticketing systems through the same MCP surface without
knowing which system is behind it.

Authority: CORE-011 (type hints) · CORE-012 (docstrings) · CORE-035 (single canonical)
Phase: Phase 15 — Work Item Provider
AC-IDs: AC-P15-001, AC-P15-002, AC-P15-009
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Protocol, runtime_checkable


@dataclass
class WorkItem:
    """
    Canonical work item representation across all ticketing systems.

    The ``raw`` field is the escape hatch for company-specific fields.
    CORTEX never parses ``raw``; all system-specific data (Area Path,
    Sprint, Custom.* ADO fields, Jira components, etc.) survives
    unmodified in ``raw`` for downstream consumers.

    Attributes:
        id: Unique identifier string as provided by the source system.
        title: Human-readable summary / title of the work item.
        description: Full description or acceptance criteria body.
        state: Current state (e.g. "Active", "Resolved", "To Do").
        type: Work item type (e.g. "User Story", "Bug", "Task", "Epic").
        tags: List of tag strings; empty list if none.
        url: Direct browser URL to the work item in the source system.
        raw: Complete unmodified API response dict from the source system.
             Access company-specific fields as ``item.raw["fields"]["Custom.Tag"]``.
    """

    id: str
    title: str
    description: str
    state: str
    type: str
    tags: List[str]
    url: str
    raw: Dict[str, Any]


@runtime_checkable
class WorkItemProvider(Protocol):
    """
    Protocol for company-pluggable work item sources.

    Implement this Protocol to connect any ticketing system to CORTEX.
    The three required methods are the complete integration contract —
    no other CORTEX internals need to change when a new provider is added.

    Example — implementing for a custom internal API::

        class MyCompanyProvider(WorkItemProvider):
            def fetch_user_stories(self, project: str, **kwargs) -> list[WorkItem]:
                items = my_internal_api.get_stories(project)
                return [self._map(i) for i in items]

            def fetch_by_id(self, item_id: str) -> WorkItem:
                return self._map(my_internal_api.get_item(item_id))

            def health_check(self) -> bool:
                return my_internal_api.ping()

    Then register in ``provider_factory.py`` and set
    ``WORK_ITEM_SOURCE=mycompany`` in your environment.
    """

    def fetch_user_stories(self, project: str, **kwargs: Any) -> List[WorkItem]:
        """
        Fetch user stories for the given project.

        Args:
            project: Project name or identifier as recognised by the source system.
            **kwargs: Provider-specific filters (sprint, area_path, state, etc.).

        Returns:
            List of WorkItem instances. Empty list if none found.
        """
        ...

    def fetch_by_id(self, item_id: str) -> WorkItem:
        """
        Fetch a single work item by its system identifier.

        Args:
            item_id: The unique identifier string for the work item.

        Returns:
            A WorkItem instance populated from the source system.

        Raises:
            KeyError: If the item does not exist in the source system.
        """
        ...

    def health_check(self) -> bool:
        """
        Verify the provider can reach the upstream system.

        Returns:
            True if the upstream system is reachable, False otherwise.
        """
        ...
