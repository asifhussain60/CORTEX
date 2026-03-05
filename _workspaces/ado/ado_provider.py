"""
ADOWorkItemProvider — Azure DevOps concrete implementation of WorkItemProvider.

══════════════════════════════════════════════════════════════════════════════
IMPLEMENTATION PLAN & SPECIFICATION
══════════════════════════════════════════════════════════════════════════════

This module contains:
  1. UserStoryContext — enriched ADO dataclass (extends WorkItem fields)
  2. ADOWorkItemProvider — WorkItemProvider Protocol implementation
     with fully documented implementation points, field mappings,
     API endpoint specs, and WIQL patterns ready for TDD GREEN phase.

CONNECTION DETAILS:
    Base URL:     https://dev.azure.com/{organization}
    Auth:         Basic base64(":" + PAT)     [no username, PAT only]
    API Version:  7.1  (set per-request; no global override needed)
    HTTP Client:  requests  (already in CORTEX requirements.txt)
    No proxy:     Python has no CORS constraint — direct ADO calls only.

FETCH STRATEGY:
    Single story:  GET /_apis/wit/workitems/{id}?$expand=all&api-version=7.1
                   → 1 round-trip; returns fields + relations + links
    Bulk stories:  POST /{proj}/_apis/wit/wiql   → list of IDs
                   GET  /_apis/wit/workitemsbatch → fields (200 IDs/batch max)

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-012 (docstrings)
           CORE-028 (snake_case) · CORE-035 (single canonical)
Phase: Phase 15 — Work Item Provider
AC-IDs: AC-P15-003, AC-P15-010
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from cortex.repositories.work_item_provider import WorkItem, WorkItemProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ADO API Constants
# ---------------------------------------------------------------------------

ADO_API_VERSION = "7.1"
ADO_BATCH_SIZE = 200          # ADO hard limit per workitemsbatch request
ADO_WIQL_LIMIT = 20_000       # ADO hard WIQL result cap (VS402337 above this)
ADO_TIMEOUT_SECONDS = 30      # Request timeout; match QEMetricsCollection's 30s

# ---------------------------------------------------------------------------
# ADO Field Name Constants
# (Use these as keys into raw["fields"] to avoid typos)
# ---------------------------------------------------------------------------

# Standard system fields
F_ID = "System.Id"
F_TITLE = "System.Title"
F_DESCRIPTION = "System.Description"
F_STATE = "System.State"
F_WORK_ITEM_TYPE = "System.WorkItemType"
F_TAGS = "System.Tags"
F_ASSIGNED_TO = "System.AssignedTo"
F_AREA_PATH = "System.AreaPath"
F_ITERATION_PATH = "System.IterationPath"
F_CREATED_DATE = "System.CreatedDate"
F_CHANGED_DATE = "System.ChangedDate"
F_TEAM_PROJECT = "System.TeamProject"
F_HISTORY = "System.History"

# Microsoft VSTS fields (common ADO extensions)
F_STORY_POINTS = "Microsoft.VSTS.Scheduling.StoryPoints"
F_PRIORITY = "Microsoft.VSTS.Common.Priority"
F_ACCEPTANCE_CRITERIA = "Microsoft.VSTS.Common.AcceptanceCriteria"
F_AUTOMATED_TEST_NAME = "Microsoft.VSTS.TCM.AutomatedTestName"
F_AUTOMATED_TEST_ID = "Microsoft.VSTS.TCM.AutomatedTestId"

# Relation type strings (used in raw["relations"][i]["rel"])
REL_PARENT = "System.LinkTypes.Hierarchy-Reverse"
REL_CHILD = "System.LinkTypes.Hierarchy-Forward"
REL_TESTED_BY = "Microsoft.VSTS.Common.TestedBy-Forward"
REL_TESTS = "Microsoft.VSTS.Common.TestedBy-Reverse"
REL_RELATED = "System.LinkTypes.Related"
REL_PR = "ArtifactLink"  # Pull Request links (check .attributes.name == "Pull Request")

# Fields to request in batch GET (covers UserStoryContext mapping completely)
BATCH_FIELDS: List[str] = [
    F_ID, F_TITLE, F_DESCRIPTION, F_STATE, F_WORK_ITEM_TYPE,
    F_TAGS, F_ASSIGNED_TO, F_AREA_PATH, F_ITERATION_PATH,
    F_CREATED_DATE, F_CHANGED_DATE, F_STORY_POINTS, F_PRIORITY,
    F_ACCEPTANCE_CRITERIA, F_TEAM_PROJECT,
]


# ---------------------------------------------------------------------------
# UserStoryContext — enriched ADO dataclass
# ---------------------------------------------------------------------------

@dataclass
class UserStoryContext:
    """
    Enriched ADO work item representation for CORTEX orchestration.

    Extends the base WorkItem fields with ADO-specific data extracted from
    ``$expand=all`` responses.  The ``raw`` field preserves the complete
    unmodified ADO response for company-specific field access.

    Usage::

        ctx = provider.fetch_by_id("42")
        print(ctx.title, ctx.acceptance_criteria)
        print(ctx.parent_id, ctx.child_task_ids)
        # Access custom ADO fields:
        custom = ctx.raw["fields"].get("Custom.YourField", "")

    Attributes:
        id: ADO work item numeric ID as string (e.g. "42").
        title: Work item title / summary.
        description: HTML description body (may contain ADO HTML markup).
        state: Current ADO state (e.g. "Active", "Resolved", "Closed").
        type: Work item type (e.g. "User Story", "Bug", "Task", "Feature").
        tags: List of tag strings; split from semicolon-delimited ADO format.
        url: Direct browser URL to the work item in Azure DevOps.
        raw: Complete unmodified ADO REST API response dict.
        assignee: Display name of the assigned user; None if unassigned.
        story_points: Effort estimate in story points; None if not set.
        priority: ADO priority value (1=Critical, 2=High, 3=Medium, 4=Low).
        acceptance_criteria: HTML acceptance criteria body; empty string if absent.
        area_path: ADO area path (e.g. "MyProject\\TeamName\\SubArea").
        iteration_path: Sprint/iteration path (e.g. "MyProject\\Sprint 42").
        created_at: UTC datetime of work item creation; None if unparseable.
        updated_at: UTC datetime of last change; None if unparseable.
        parent_id: ID of the parent work item (Epic/Feature); None if no parent.
        child_task_ids: IDs of child Task/Story work items linked via Hierarchy-Forward.
        linked_test_case_ids: IDs of Test Case work items linked via TestedBy.
        linked_pr_ids: Pull Request artifact IDs linked to this story.
    """

    # Core WorkItem-compatible fields
    id: str
    title: str
    description: str
    state: str
    type: str
    tags: List[str]
    url: str
    raw: Dict[str, Any]

    # ADO-specific enrichment
    assignee: Optional[str] = None
    story_points: Optional[float] = None
    priority: Optional[int] = None
    acceptance_criteria: str = ""
    area_path: str = ""
    iteration_path: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    parent_id: Optional[int] = None
    child_task_ids: List[int] = field(default_factory=list)
    linked_test_case_ids: List[int] = field(default_factory=list)
    linked_pr_ids: List[int] = field(default_factory=list)

    def to_work_item(self) -> WorkItem:
        """Convert to base WorkItem for protocol compatibility."""
        return WorkItem(
            id=self.id,
            title=self.title,
            description=self.description,
            state=self.state,
            type=self.type,
            tags=self.tags,
            url=self.url,
            raw=self.raw,
        )


# ---------------------------------------------------------------------------
# ADOWorkItemProvider
# ---------------------------------------------------------------------------

class ADOWorkItemProvider:
    """
    Azure DevOps implementation of WorkItemProvider.

    Satisfies the WorkItemProvider Protocol.  All implementation points are
    fully annotated with the exact ADO REST endpoint, request shape, response
    shape, and mapping logic required.  This docstring + inline comments
    constitute the complete TDD specification for the GREEN phase.

    Configuration (env vars — never hardcode credentials):
        ADO_ORG_URL  : Full org URL, e.g. "https://dev.azure.com/HQY01"
        ADO_PAT      : Personal Access Token with scopes:
                         Work Items (Read), Project and Team (Read),
                         Test Management (Read), Build (Read, optional)
        ADO_PROJECT  : Default project name, e.g. "Quality Engineering"

    Auth pattern (identical to QEMetricsCollection, ported to Python):
        token = base64.b64encode(f":{pat}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
        # No username — ADO PAT auth requires empty username field

    Args:
        org_url: Azure DevOps organisation URL (trailing slash stripped).
        pat: Personal Access Token. Empty string triggers managed identity
             fallback path (company to implement in _auth_headers).
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
        # Cache: project_id/name → resolved name string (reduces API calls)
        self._project_name_cache: Dict[str, str] = {}
        logger.debug("ADOWorkItemProvider initialised for org: %s", self._org_url)

    # -----------------------------------------------------------------------
    # WorkItemProvider Protocol — public surface
    # -----------------------------------------------------------------------

    def fetch_user_stories(self, project: str, **kwargs: Any) -> List[WorkItem]:
        """
        Fetch User Story work items from ADO via WIQL + batch GET.

        This is the bulk fetch path.  For single-item lookup use
        ``fetch_by_id`` which is more efficient (1 round-trip).

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION — TWO-STEP PATTERN                               │
        │                                                                 │
        │ Step 1 — WIQL query to get IDs:                                 │
        │   POST {org_url}/{project}/_apis/wit/wiql?api-version=7.1      │
        │   Body: { "query": "<wiql_string>" }                           │
        │   Response: { "workItems": [{"id": 1, "url": "..."}, ...] }   │
        │                                                                 │
        │ Step 2 — Batch GET for full fields (200 IDs per request):      │
        │   POST {org_url}/_apis/wit/workitemsbatch?api-version=7.1     │
        │   Body: { "ids": [1,2,...200], "fields": BATCH_FIELDS }        │
        │   Response: { "count": N, "value": [{raw work item}, ...] }   │
        │                                                                 │
        │ WIQL TEMPLATE (filter by kwargs):                               │
        │   SELECT [System.Id] FROM WorkItems                            │
        │   WHERE [System.TeamProject] = '{project}'                     │
        │     AND [System.WorkItemType] = 'User Story'                   │
        │     AND [System.State] NOT IN ('Removed', 'Cut')               │
        │   ORDER BY [System.ChangedDate] DESC                           │
        │                                                                 │
        │ SUPPORTED kwargs → WIQL clause additions:                       │
        │   sprint      → AND [System.IterationPath] = '{project}\\{v}' │
        │   area_path   → AND [System.AreaPath] UNDER '{v}'             │
        │   state       → AND [System.State] = '{v}'                     │
        │   assignee    → AND [System.AssignedTo] = '{v}'                │
        │   changed_since → AND [System.ChangedDate] >= '{v}'           │
        │                                                                 │
        │ ERROR HANDLING:                                                 │
        │   VS402337 (>20K results) → apply restrictive date filter      │
        │   HTTP 203 / 401          → PAT expired or insufficient scope  │
        │   HTTP 404                → project name incorrect             │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            project: ADO project name. Falls back to ``ADO_PROJECT`` env var.
            **kwargs: Optional WIQL filters (sprint, area_path, state,
                      assignee, changed_since).

        Returns:
            List of WorkItem instances. Empty list if none found.
        """
        effective_project = project or self._default_project
        logger.debug(
            "fetch_user_stories called: project=%s kwargs=%s",
            effective_project,
            kwargs,
        )
        # ----------------------------------------------------------------
        # IMPLEMENTATION POINT — replace stub below
        #
        # wiql = self._build_user_story_wiql(effective_project, **kwargs)
        # ids = self._run_wiql(wiql, effective_project)   # → List[int]
        # raw_items = self._batch_get(ids)                 # → List[dict]
        # return [self._map(r) for r in raw_items]
        # ----------------------------------------------------------------
        return []

    def fetch_by_id(self, item_id: str) -> WorkItem:
        """
        Fetch a single ADO work item by numeric ID — returns WorkItem.

        For the enriched ``UserStoryContext`` call ``fetch_story_context``
        instead (returns full relation tree in one $expand=all call).

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION — SINGLE ROUND-TRIP                              │
        │                                                                 │
        │   GET {org_url}/_apis/wit/workitems/{id}                       │
        │       ?$expand=all&api-version=7.1                             │
        │   Headers: Authorization, Content-Type, Accept                 │
        │                                                                 │
        │ Response shape:                                                 │
        │   {                                                             │
        │     "id": 42,                                                   │
        │     "rev": 5,                                                   │
        │     "fields": {                                                 │
        │       "System.Title": "...",                                   │
        │       "System.State": "Active",                                │
        │       "Microsoft.VSTS.Common.AcceptanceCriteria": "<html>",   │
        │       ...                                                       │
        │     },                                                          │
        │     "relations": [                                              │
        │       { "rel": "System.LinkTypes.Hierarchy-Reverse",           │
        │         "url": ".../workItems/10" },                           │
        │       { "rel": "System.LinkTypes.Hierarchy-Forward",           │
        │         "url": ".../workItems/43" },                           │
        │       { "rel": "Microsoft.VSTS.Common.TestedBy-Forward",      │
        │         "url": ".../workItems/99" }                            │
        │     ],                                                          │
        │     "_links": { "html": { "href": "https://..." } }           │
        │   }                                                             │
        │                                                                 │
        │ ERROR HANDLING:                                                 │
        │   HTTP 404 → raise KeyError(f"Work item {item_id} not found") │
        │   HTTP 401 → raise PermissionError("ADO auth failed")         │
        │   HTTP 429 → sleep + retry (exponential back-off, max 3x)     │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            item_id: ADO numeric work item ID as string (e.g. "42").

        Returns:
            WorkItem populated from ADO fields (base Protocol return type).
            Use ``fetch_story_context(item_id)`` for the full enriched form.

        Raises:
            KeyError: Work item does not exist or is in 'Removed' state.
            PermissionError: PAT is invalid, expired, or has insufficient scope.
        """
        logger.debug("fetch_by_id called: item_id=%s", item_id)
        # ----------------------------------------------------------------
        # IMPLEMENTATION POINT — replace stub below
        #
        # raw = self._get_work_item_expand_all(int(item_id))
        # return self._map(raw)
        # ----------------------------------------------------------------
        raise NotImplementedError(
            f"ADOWorkItemProvider.fetch_by_id — implement the ADO REST call "
            f"for item_id={item_id!r}.  See docstring for endpoint spec."
        )

    def fetch_story_context(self, item_id: str) -> UserStoryContext:
        """
        Fetch a single ADO work item by ID as a ``UserStoryContext``.

        Same HTTP call as ``fetch_by_id`` but returns the enriched
        ``UserStoryContext`` dataclass with relations tree resolved
        (parent_id, child_task_ids, linked_test_case_ids).

        ┌─────────────────────────────────────────────────────────────────┐
        │ SAME ENDPOINT AS fetch_by_id — USE _map_to_context() INSTEAD   │
        │                                                                 │
        │   raw = self._get_work_item_expand_all(int(item_id))           │
        │   return self._map_to_context(raw)                             │
        │                                                                 │
        │ _map_to_context extracts:                                       │
        │   • Standard fields (title, state, tags, etc.)                 │
        │   • parent_id from relations where rel == REL_PARENT           │
        │   • child_task_ids from relations where rel == REL_CHILD       │
        │   • linked_test_case_ids from rel == REL_TESTED_BY             │
        │   • linked_pr_ids from rel == REL_PR + attribute check         │
        │                                                                 │
        │ ID extraction from relation URL:                                │
        │   url = "https://dev.azure.com/org/_apis/wit/workItems/42"    │
        │   id  = int(url.rstrip("/").split("/")[-1])                    │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            item_id: ADO numeric work item ID as string.

        Returns:
            UserStoryContext with full relation tree populated.

        Raises:
            KeyError: Work item does not exist.
            PermissionError: PAT auth failure.
        """
        logger.debug("fetch_story_context called: item_id=%s", item_id)
        # ----------------------------------------------------------------
        # IMPLEMENTATION POINT — replace stub below
        #
        # raw = self._get_work_item_expand_all(int(item_id))
        # return self._map_to_context(raw)
        # ----------------------------------------------------------------
        raise NotImplementedError(
            f"ADOWorkItemProvider.fetch_story_context — implement using "
            f"_get_work_item_expand_all + _map_to_context."
        )

    def health_check(self) -> bool:
        """
        Verify the ADO organisation endpoint is reachable and PAT is valid.

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION — LIGHTWEIGHT PING                               │
        │                                                                 │
        │   GET {org_url}/_apis/projects?api-version=7.1&$top=1         │
        │   Expect HTTP 200.  HTTP 401/403 = PAT issue.                  │
        │   Timeout: 5s (short — this is a connectivity check only)      │
        │                                                                 │
        │   import requests                                               │
        │   try:                                                          │
        │       r = requests.get(                                         │
        │           f"{self._org_url}/_apis/projects",                   │
        │           params={"api-version": ADO_API_VERSION, "$top": 1},  │
        │           headers=self._auth_headers(),                         │
        │           timeout=5,                                            │
        │       )                                                         │
        │       return r.status_code == 200                               │
        │   except requests.RequestException:                             │
        │       return False                                              │
        └─────────────────────────────────────────────────────────────────┘

        Returns:
            True if ADO is reachable and PAT authenticates successfully.
            False on network error, timeout, or auth failure.
        """
        logger.debug("health_check called for org: %s", self._org_url)
        # ----------------------------------------------------------------
        # IMPLEMENTATION POINT — replace stub below (see docstring above)
        # ----------------------------------------------------------------
        return False

    # -----------------------------------------------------------------------
    # Private: HTTP layer
    # -----------------------------------------------------------------------

    def _get_work_item_expand_all(self, item_id: int) -> Dict[str, Any]:
        """
        GET a single work item with $expand=all (fields + relations + links).

        ┌─────────────────────────────────────────────────────────────────┐
        │ ENDPOINT:                                                        │
        │   GET {org_url}/_apis/wit/workitems/{id}                       │
        │       ?$expand=all&api-version=7.1                             │
        │                                                                 │
        │ IMPLEMENTATION:                                                 │
        │   import requests                                               │
        │   url = f"{self._org_url}/_apis/wit/workitems/{item_id}"      │
        │   r = requests.get(                                             │
        │       url,                                                      │
        │       params={"$expand": "all", "api-version": ADO_API_VERSION},│
        │       headers=self._auth_headers(),                             │
        │       timeout=ADO_TIMEOUT_SECONDS,                              │
        │   )                                                             │
        │   if r.status_code == 404:                                      │
        │       raise KeyError(f"Work item {item_id} not found")         │
        │   if r.status_code == 401:                                      │
        │       raise PermissionError("ADO authentication failed")        │
        │   r.raise_for_status()                                          │
        │   return r.json()                                               │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            item_id: ADO numeric work item ID.

        Returns:
            Raw ADO API response dict with fields and relations.

        Raises:
            KeyError: Work item not found (HTTP 404).
            PermissionError: Auth failure (HTTP 401/403).
            requests.HTTPError: Other HTTP error.
        """
        raise NotImplementedError("_get_work_item_expand_all not yet implemented")

    def _run_wiql(self, wiql_query: str, project: str) -> List[int]:
        """
        Execute a WIQL query and return the resulting work item IDs.

        ┌─────────────────────────────────────────────────────────────────┐
        │ ENDPOINT:                                                        │
        │   POST {org_url}/{project}/_apis/wit/wiql?api-version=7.1     │
        │   Body: { "query": "<wiql>" }                                  │
        │   Response: { "workItems": [{"id": N, "url": "..."}, ...] }   │
        │                                                                 │
        │ ERROR HANDLING:                                                 │
        │   If response contains "VS402337" (>20K limit):                │
        │       Raise ValueError("WIQL result exceeds ADO 20K limit")    │
        │       Caller should retry with more restrictive WIQL.           │
        │                                                                 │
        │ IMPLEMENTATION:                                                 │
        │   encoded_project = quote(project)                              │
        │   url = f"{self._org_url}/{encoded_project}/_apis/wit/wiql"    │
        │   r = requests.post(url,                                        │
        │       params={"api-version": ADO_API_VERSION},                 │
        │       headers=self._auth_headers(),                             │
        │       json={"query": wiql_query},                               │
        │       timeout=ADO_TIMEOUT_SECONDS)                              │
        │   r.raise_for_status()                                          │
        │   return [wi["id"] for wi in r.json().get("workItems", [])]    │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            wiql_query: WIQL SELECT statement string.
            project: ADO project name (URL-encoded internally).

        Returns:
            List of integer work item IDs matching the query.

        Raises:
            ValueError: WIQL result exceeds the ADO 20,000-item hard limit.
            requests.HTTPError: API call failed.
        """
        raise NotImplementedError("_run_wiql not yet implemented")

    def _batch_get(self, item_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Batch-fetch full work item fields for a list of IDs.

        Splits IDs into ADO_BATCH_SIZE (200) chunks and POSTs each chunk
        to workitemsbatch.  Returns a flat list of raw work item dicts.

        ┌─────────────────────────────────────────────────────────────────┐
        │ ENDPOINT (per batch):                                            │
        │   POST {org_url}/_apis/wit/workitemsbatch?api-version=7.1     │
        │   Body: { "ids": [1,...200], "fields": BATCH_FIELDS }         │
        │   Response: { "count": N, "value": [{raw workitem}, ...] }    │
        │                                                                 │
        │ IMPLEMENTATION PATTERN:                                         │
        │   results = []                                                  │
        │   for chunk in _chunks(item_ids, ADO_BATCH_SIZE):              │
        │       r = requests.post(url,                                    │
        │           params={"api-version": ADO_API_VERSION},             │
        │           headers=self._auth_headers(),                         │
        │           json={"ids": chunk, "fields": BATCH_FIELDS},         │
        │           timeout=ADO_TIMEOUT_SECONDS)                          │
        │       r.raise_for_status()                                      │
        │       results.extend(r.json().get("value", []))                │
        │   return results                                                │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            item_ids: List of ADO work item IDs (any length; batched internally).

        Returns:
            Flat list of raw work item dicts with all BATCH_FIELDS populated.
        """
        raise NotImplementedError("_batch_get not yet implemented")

    # -----------------------------------------------------------------------
    # Private: WIQL builders
    # -----------------------------------------------------------------------

    def _build_user_story_wiql(self, project: str, **kwargs: Any) -> str:
        """
        Build a WIQL SELECT string for user story queries.

        Assembles WHERE clauses from kwargs:
            sprint       → AND [System.IterationPath] = '{project}\\{sprint}'
            area_path    → AND [System.AreaPath] UNDER '{area_path}'
            state        → AND [System.State] = '{state}'
            assignee     → AND [System.AssignedTo] = '{assignee}'
            changed_since → AND [System.ChangedDate] >= '{changed_since}'

        Always excludes 'Removed' and 'Cut' states to mirror the
        QEMetricsCollection proven WIQL pattern.

        WIQL INJECTION NOTE: ADO WIQL does not support parameterised queries.
        Sanitise all string inputs (strip single quotes, validate iterationPath
        format) before interpolating into the query string.

        Args:
            project: ADO project name (already validated by caller).
            **kwargs: Optional WIQL filter keys documented above.

        Returns:
            Complete WIQL SELECT statement as a string.
        """
        # Base query — mirrors QEMetricsCollection's proven working pattern
        base = (
            f"SELECT [System.Id] FROM WorkItems "
            f"WHERE [System.TeamProject] = '{project}' "
            f"  AND [System.WorkItemType] = 'User Story' "
            f"  AND [System.State] NOT IN ('Removed', 'Cut')"
        )
        clauses: List[str] = []

        if sprint := kwargs.get("sprint"):
            safe = sprint.replace("'", "")
            clauses.append(
                f"[System.IterationPath] = '{project}\\\\{safe}'"
            )
        if area_path := kwargs.get("area_path"):
            safe = area_path.replace("'", "")
            clauses.append(f"[System.AreaPath] UNDER '{safe}'")
        if state := kwargs.get("state"):
            safe = state.replace("'", "")
            clauses.append(f"[System.State] = '{safe}'")
        if assignee := kwargs.get("assignee"):
            safe = assignee.replace("'", "")
            clauses.append(f"[System.AssignedTo] = '{safe}'")
        if changed_since := kwargs.get("changed_since"):
            clauses.append(f"[System.ChangedDate] >= '{changed_since}'")

        if clauses:
            base += "  AND " + "  AND ".join(clauses)

        base += " ORDER BY [System.ChangedDate] DESC"
        return base

    # -----------------------------------------------------------------------
    # Private: Field mapping
    # -----------------------------------------------------------------------

    def _map(self, raw: Dict[str, Any]) -> WorkItem:
        """
        Map a raw ADO work item dict to a base ``WorkItem`` dataclass.

        Extracts the minimum set of fields required by the WorkItemProvider
        Protocol.  The full ``raw`` dict is preserved for downstream access
        to company-specific or unmapped fields.

        Args:
            raw: Raw ADO REST API work item dict.

        Returns:
            WorkItem with Protocol-required fields populated.
        """
        f = raw.get("fields", {})
        tags_raw: str = f.get(F_TAGS, "") or ""
        tags: List[str] = [t.strip() for t in tags_raw.split(";") if t.strip()]

        return WorkItem(
            id=str(raw.get("id", "")),
            title=f.get(F_TITLE, ""),
            description=f.get(F_DESCRIPTION, "") or "",
            state=f.get(F_STATE, ""),
            type=f.get(F_WORK_ITEM_TYPE, ""),
            tags=tags,
            url=raw.get("_links", {}).get("html", {}).get("href", ""),
            raw=raw,
        )

    def _map_to_context(self, raw: Dict[str, Any]) -> UserStoryContext:
        """
        Map a raw ADO ``$expand=all`` work item dict to ``UserStoryContext``.

        This is the enriched mapping used by ``fetch_story_context``.
        Relations are parsed to extract parent, children, test cases, and PR IDs.

        ┌─────────────────────────────────────────────────────────────────┐
        │ RELATION PARSING LOGIC:                                         │
        │                                                                 │
        │   for rel in raw.get("relations", []):                         │
        │       rel_type = rel.get("rel", "")                            │
        │       url = rel.get("url", "")                                 │
        │       rel_id = int(url.rstrip("/").split("/")[-1])             │
        │                                                                 │
        │       if rel_type == REL_PARENT:                                │
        │           parent_id = rel_id                                    │
        │       elif rel_type == REL_CHILD:                               │
        │           child_task_ids.append(rel_id)                        │
        │       elif rel_type == REL_TESTED_BY:                           │
        │           linked_test_case_ids.append(rel_id)                  │
        │       elif rel_type == REL_PR:                                  │
        │           # PR links have artifactId not /workItems/ URL        │
        │           # Check rel.get("attributes", {}).get("name") == "Pull Request" │
        │           linked_pr_ids.append(rel_id)                         │
        │                                                                 │
        │ DATETIME PARSING:                                               │
        │   datetime.fromisoformat(raw_str.replace("Z", "+00:00"))       │
        │   Wrap in try/except — ADO rarely returns null dates            │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            raw: Raw ADO REST API response with $expand=all (fields + relations).

        Returns:
            Fully populated UserStoryContext.
        """
        f = raw.get("fields", {})
        tags_raw: str = f.get(F_TAGS, "") or ""
        tags: List[str] = [t.strip() for t in tags_raw.split(";") if t.strip()]

        # Parse relations
        parent_id: Optional[int] = None
        child_task_ids: List[int] = []
        linked_test_case_ids: List[int] = []
        linked_pr_ids: List[int] = []

        for rel in raw.get("relations", []):
            rel_type = rel.get("rel", "")
            rel_url = rel.get("url", "")
            # ----------------------------------------------------------------
            # IMPLEMENTATION POINT — parse relation IDs from URLs
            # try:
            #     rel_id = int(rel_url.rstrip("/").split("/")[-1])
            # except (ValueError, IndexError):
            #     continue
            # if rel_type == REL_PARENT: parent_id = rel_id
            # elif rel_type == REL_CHILD: child_task_ids.append(rel_id)
            # elif rel_type == REL_TESTED_BY: linked_test_case_ids.append(rel_id)
            # ----------------------------------------------------------------

        # Parse datetime fields
        def _parse_dt(val: Optional[str]) -> Optional[datetime]:
            if not val:
                return None
            try:
                return datetime.fromisoformat(val.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None

        # Parse assignee (ADO returns an object, not a string)
        assignee_obj = f.get(F_ASSIGNED_TO)
        assignee: Optional[str] = (
            assignee_obj.get("displayName") if isinstance(assignee_obj, dict) else None
        )

        return UserStoryContext(
            id=str(raw.get("id", "")),
            title=f.get(F_TITLE, ""),
            description=f.get(F_DESCRIPTION, "") or "",
            state=f.get(F_STATE, ""),
            type=f.get(F_WORK_ITEM_TYPE, ""),
            tags=tags,
            url=raw.get("_links", {}).get("html", {}).get("href", ""),
            raw=raw,
            assignee=assignee,
            story_points=f.get(F_STORY_POINTS),
            priority=f.get(F_PRIORITY),
            acceptance_criteria=f.get(F_ACCEPTANCE_CRITERIA, "") or "",
            area_path=f.get(F_AREA_PATH, ""),
            iteration_path=f.get(F_ITERATION_PATH, ""),
            created_at=_parse_dt(f.get(F_CREATED_DATE)),
            updated_at=_parse_dt(f.get(F_CHANGED_DATE)),
            parent_id=parent_id,
            child_task_ids=child_task_ids,
            linked_test_case_ids=linked_test_case_ids,
            linked_pr_ids=linked_pr_ids,
        )

    # -----------------------------------------------------------------------
    # Private: Auth + utilities
    # -----------------------------------------------------------------------

    def _auth_headers(self) -> Dict[str, str]:
        """
        Build ADO REST API authentication headers.

        Uses PAT Basic Auth — the same encoding pattern as QEMetricsCollection:
            btoa(":" + token)  →  base64.b64encode(f":{pat}".encode()).decode()

        For managed identity (no PAT), the company implementation should
        replace this with an Azure credential token fetch.

        Returns:
            Dict of HTTP headers with Authorization, Content-Type, Accept.
        """
        token = base64.b64encode(f":{self._pat}".encode()).decode()
        return {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
            "Accept": f"application/json; api-version={ADO_API_VERSION}",
        }

    @staticmethod
    def _chunks(lst: List[Any], size: int):
        """Yield successive ``size``-length chunks from ``lst``."""
        for i in range(0, len(lst), size):
            yield lst[i : i + size]
