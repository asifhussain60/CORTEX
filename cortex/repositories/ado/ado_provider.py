"""
ADOWorkItemProvider — Azure DevOps concrete implementation of WorkItemProvider.

This is the company-supplied adapter layer. The stub below satisfies the
WorkItemProvider Protocol contract with correct signatures and docstrings.
Companies replace the body of each method with their actual HTTP calls,
authentication (PAT, OAuth2, managed identity), and field mapping.

Configuration (via environment variables):
    ADO_ORG_URL   — e.g. "https://dev.azure.com/your-org"
    ADO_PAT       — Personal Access Token (or leave blank for managed identity)
    ADO_PROJECT   — Default project name

The ``raw`` field on every WorkItem carries the full unmodified ADO API
response. Company-specific fields (Area Path, Sprint, Custom.*) survive
intact and are accessible as ``item.raw["fields"]["Custom.YourField"]``.

Authority: CORE-011 (type hints) · CORE-012 (docstrings) · CORE-028 (snake_case)
Phase: Phase 15 — Work Item Provider
AC-IDs: AC-P15-003, AC-P15-010
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from cortex.repositories.work_item_provider import WorkItem, WorkItemProvider

logger = logging.getLogger(__name__)


class ADOWorkItemProvider:
    """
    Azure DevOps implementation of WorkItemProvider.

    Satisfies the WorkItemProvider Protocol. Companies fill in the HTTP
    client calls and field mappings in ``fetch_user_stories``,
    ``fetch_by_id``, and the private ``_map`` helper.

    All provider-specific auth and connection details are read from
    environment variables; no credentials are stored in this file.

    Args:
        org_url: Azure DevOps organisation URL
                 (e.g. "https://dev.azure.com/your-org").
        pat: Personal Access Token for authentication. When empty,
             the implementation should fall back to managed identity
             or other auth mechanism provided by the company.
        project: Default project name used when ``project`` arg is omitted.
    """

    def __init__(
        self,
        org_url: str,
        pat: str,
        project: str,
    ) -> None:
        """Initialise ADO provider with connection details."""
        self._org_url = org_url.rstrip("/")
        self._pat = pat
        self._default_project = project
        logger.debug("ADOWorkItemProvider initialised for org: %s", self._org_url)

    # ------------------------------------------------------------------
    # Protocol implementation
    # ------------------------------------------------------------------

    def fetch_user_stories(self, project: str, **kwargs: Any) -> List[WorkItem]:
        """
        Fetch user stories from Azure DevOps for the given project.

        Companies replace this stub with their ADO REST call:
        ``POST /{org}/{project}/_apis/wit/wiql?api-version=7.1``
        followed by a batch ``GET`` for item details.

        Args:
            project: ADO project name. Falls back to ``ADO_PROJECT`` env var
                     if an empty string is supplied.
            **kwargs: Optional filters forwarded to the ADO query
                      (e.g. ``sprint``, ``area_path``, ``state``).

        Returns:
            List of WorkItem instances mapped from ADO work item payloads.
            Returns an empty list when the project has no user stories.
        """
        effective_project = project or self._default_project
        logger.debug(
            "fetch_user_stories called: project=%s kwargs=%s",
            effective_project,
            kwargs,
        )
        # ----------------------------------------------------------------
        # COMPANY IMPLEMENTATION POINT
        # Replace the lines below with your ADO REST client calls.
        #
        # Example pattern:
        #   wiql = f"SELECT [System.Id] FROM WorkItems WHERE ..."
        #   ids  = self._run_wiql(wiql, effective_project)
        #   raw_items = self._batch_get(ids, effective_project)
        #   return [self._map(r) for r in raw_items]
        # ----------------------------------------------------------------
        return []

    def fetch_by_id(self, item_id: str) -> WorkItem:
        """
        Fetch a single Azure DevOps work item by its numeric ID.

        Companies replace this stub with:
        ``GET /{org}/{project}/_apis/wit/workitems/{id}?$expand=all``

        Args:
            item_id: The ADO work item ID as a string (e.g. "42").

        Returns:
            A WorkItem populated from the ADO work item payload.

        Raises:
            KeyError: If the item does not exist in the ADO project.
        """
        logger.debug("fetch_by_id called: item_id=%s", item_id)
        # ----------------------------------------------------------------
        # COMPANY IMPLEMENTATION POINT
        # Replace with: raw = self._get(f"{self._base_url}/workitems/{item_id}")
        #               return self._map(raw)
        # ----------------------------------------------------------------
        raise NotImplementedError(
            f"ADOWorkItemProvider.fetch_by_id is a stub. "
            f"Implement the ADO REST call for item_id={item_id!r}."
        )

    def health_check(self) -> bool:
        """
        Verify the ADO organisation endpoint is reachable.

        Companies replace this stub with a lightweight connectivity check:
        ``GET /{org}/_apis/projects?api-version=7.1&$top=1``

        Returns:
            True if the ADO organisation is reachable, False otherwise.
        """
        logger.debug("health_check called for org: %s", self._org_url)
        # ----------------------------------------------------------------
        # COMPANY IMPLEMENTATION POINT
        # Replace with: response = requests.get(f"{self._org_url}/_apis/projects",
        #                                        headers=self._auth_headers(), timeout=5)
        #               return response.status_code == 200
        # ----------------------------------------------------------------
        return False

    # ------------------------------------------------------------------
    # Private helpers (company fills these in)
    # ------------------------------------------------------------------

    def _map(self, raw: Dict[str, Any]) -> WorkItem:
        """
        Map a raw ADO work item API response to a WorkItem dataclass.

        The ``raw`` field on the returned WorkItem carries the full
        unmodified response so company-specific fields (Area Path,
        Sprint, Custom.*) are accessible without schema changes.

        Args:
            raw: The raw ADO work item dict from the REST API response.

        Returns:
            A WorkItem populated from the ADO response fields.
        """
        fields_: Dict[str, Any] = raw.get("fields", {})
        tags_raw: str = fields_.get("System.Tags", "") or ""
        tags: List[str] = [t.strip() for t in tags_raw.split(";") if t.strip()]

        return WorkItem(
            id=str(raw.get("id", "")),
            title=fields_.get("System.Title", ""),
            description=fields_.get("System.Description", ""),
            state=fields_.get("System.State", ""),
            type=fields_.get("System.WorkItemType", ""),
            tags=tags,
            url=raw.get("_links", {}).get("html", {}).get("href", ""),
            raw=raw,
        )

    def _auth_headers(self) -> Dict[str, str]:
        """
        Build authentication headers for ADO REST API calls.

        Returns:
            Dict of HTTP headers including Authorization.
        """
        import base64
        token = base64.b64encode(f":{self._pat}".encode()).decode()
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }
