"""Work Item Integration Foundation — unified ADO/Jira interface (GAP-129-07)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class WorkItemClient(ABC):
    """Abstract base class for work item tracker adapters.

    All PO intelligence components use this interface, making them
    work-tracker agnostic (ADO, Jira, or any future tracker).
    """

    @abstractmethod
    def fetch_story(self, story_id: str) -> Dict[str, Any]:
        """Fetch a single work item by ID.

        Returns a canonical dict with keys:
            story_id, title, description, status, priority,
            story_points, acceptance_criteria, tags
        """
        ...

    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search work items by keyword or WIQL/JQL query string.

        Returns a list of canonical work item dicts.
        """
        ...

    @abstractmethod
    def update_status(self, story_id: str, status: str) -> bool:
        """Update the status/state of a work item.

        Returns True on success, False on failure.
        """
        ...


class ADOWorkItemAdapter(WorkItemClient):
    """Azure DevOps work item adapter.

    Maps ADO REST API field names to the canonical WorkItemClient model.
    """

    def __init__(self, base_url: str = "", pat: str = "") -> None:
        self._base_url = base_url
        self._pat = pat

    def fetch_story(self, story_id: str) -> Dict[str, Any]:
        """Map ADO work item fields to canonical model."""
        # In production this calls ADO REST API. Stub returns canonical empty.
        return self._to_canonical(
            {
                "id": story_id,
                "fields": {
                    "System.Title": "",
                    "System.Description": "",
                    "System.State": "New",
                    "Microsoft.VSTS.Common.Priority": 2,
                    "Microsoft.VSTS.Scheduling.StoryPoints": 0,
                    "System.Tags": "",
                },
            }
        )

    def search(self, query: str) -> List[Dict[str, Any]]:  # noqa: ARG002
        """Return empty list stub — real impl calls ADO WIQL endpoint."""
        return []

    def update_status(self, story_id: str, status: str) -> bool:  # noqa: ARG002
        """Return True stub — real impl PATCHes the ADO work item state."""
        return True

    @staticmethod
    def _to_canonical(ado_item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert an ADO work item dict to the canonical model."""
        fields = ado_item.get("fields", {})
        return {
            "story_id": str(ado_item.get("id", "")),
            "title": fields.get("System.Title", ""),
            "description": fields.get("System.Description", ""),
            "status": fields.get("System.State", "New"),
            "priority": fields.get("Microsoft.VSTS.Common.Priority", 2),
            "story_points": fields.get("Microsoft.VSTS.Scheduling.StoryPoints", 0),
            "acceptance_criteria": fields.get(
                "Microsoft.VSTS.Common.AcceptanceCriteria", ""
            ),
            "tags": fields.get("System.Tags", ""),
        }


class JiraWorkItemAdapter(WorkItemClient):
    """Jira work item adapter.

    Maps Jira REST API field names to the canonical WorkItemClient model.
    """

    def __init__(self, base_url: str = "", api_token: str = "") -> None:
        self._base_url = base_url
        self._api_token = api_token

    def fetch_story(self, story_id: str) -> Dict[str, Any]:
        """Map Jira issue fields to canonical model."""
        return self._to_canonical(
            {
                "key": story_id,
                "fields": {
                    "summary": "",
                    "description": "",
                    "status": {"name": "To Do"},
                    "priority": {"name": "Medium"},
                    "story_points": 0,
                    "labels": [],
                },
            }
        )

    def search(self, query: str) -> List[Dict[str, Any]]:  # noqa: ARG002
        """Return empty list stub — real impl calls Jira JQL endpoint."""
        return []

    def update_status(self, story_id: str, status: str) -> bool:  # noqa: ARG002
        """Return True stub — real impl POSTs to Jira transitions endpoint."""
        return True

    @staticmethod
    def _to_canonical(jira_issue: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a Jira issue dict to the canonical model."""
        fields = jira_issue.get("fields", {})
        status_name = fields.get("status", {})
        if isinstance(status_name, dict):
            status_name = status_name.get("name", "To Do")
        priority = fields.get("priority", {})
        if isinstance(priority, dict):
            priority = priority.get("name", "Medium")
        return {
            "story_id": str(jira_issue.get("key", "")),
            "title": fields.get("summary", ""),
            "description": fields.get("description", ""),
            "status": status_name,
            "priority": priority,
            "story_points": fields.get("story_points", 0),
            "acceptance_criteria": fields.get("acceptance_criteria", ""),
            "tags": ",".join(fields.get("labels", [])),
        }
