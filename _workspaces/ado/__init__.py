"""
cortex.repositories.ado — Azure DevOps Integration Package.

══════════════════════════════════════════════════════════════════════════════
CORTEX ADO INTEGRATION — HOLISTIC PLAN & CONNECTION SPECIFICATION
══════════════════════════════════════════════════════════════════════════════

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-012 (docstrings)
           CORE-028 (snake_case) · CORE-035 (single canonical) · CORE-049 (silent exec)
Phase: Phase 15 — Work Item Provider (ADO full implementation)
Status: PLAN COMPLETE — Implementation pending TDD RED phase


──────────────────────────────────────────────────────────────────────────────
1. PACKAGE CONTENTS (CANONICAL)
──────────────────────────────────────────────────────────────────────────────

    cortex/repositories/ado/
    ├── __init__.py              ← This file — master plan & connection spec
    ├── ado_provider.py          ← WorkItemProvider concrete implementation
    │                               (satisfies cortex.repositories.work_item_provider.WorkItemProvider)
    └── ado_orchestrator.py      ← OrchestratorBase subclass — full ADO workflow
                                    orchestration entry point for CORTEX pipelines


──────────────────────────────────────────────────────────────────────────────
2. INTEGRATION ARCHITECTURE
──────────────────────────────────────────────────────────────────────────────

    MasterOrchestrator (Stage 4)
        └─ ADOOrchestrator  [ado_orchestrator.py]          ← OrchestratorBase lifecycle
               └─ ADOWorkItemProvider  [ado_provider.py]   ← WorkItemProvider Protocol
                       ├─ Direct ADO REST API  (no proxy — Python has no CORS constraint)
                       ├─ Auth: PAT via Basic Auth  (managed identity fallback planned)
                       └─ Field mapping → WorkItem + UserStoryContext dataclasses

    Config comes from env vars (CORE-049: silent, no manual proxy server required):
        ADO_ORG_URL  = "https://dev.azure.com/<org>"
        ADO_PAT      = "<personal-access-token>"
        ADO_PROJECT  = "<default-project-name>"

    Provider is registered in:
        cortex/repositories/provider_factory.py
        WORK_ITEM_SOURCE=ado  (default, no additional env var needed)


──────────────────────────────────────────────────────────────────────────────
3. ADO REST API CONNECTION DETAILS
──────────────────────────────────────────────────────────────────────────────

    Base URL:        https://dev.azure.com/{organization}
    API Version:     7.1  (stable; not preview — production safe)
    Auth header:     Authorization: Basic {base64(":"+PAT)}
    Content-Type:    application/json

    REQUIRED PAT SCOPES:
        Work Items       →  Read (fetch stories, tasks, bugs, test cases)
        Work Items       →  Write (optional — for future state transitions)
        Project and Team →  Read (resolve project/team names from IDs)
        Test Management  →  Read (link test cases to user stories)
        Build            →  Read (optional — pipeline run associations)
        Code             →  Read (optional — commit linkage)

    KEY ENDPOINTS (used / planned):

    ┌─────────────────────────────────────────────────────────────────────┐
    │ ENDPOINT                                          │ PURPOSE          │
    ├─────────────────────────────────────────────────────────────────────┤
    │ GET  /_apis/projects                              │ list projects    │
    │ GET  /_apis/projects/{id}                         │ project details  │
    │ GET  /_apis/projects/{id}/teams                   │ team list        │
    │ GET  /_apis/projects/{id}/teams/{teamId}          │ team details     │
    │ POST /{project}/_apis/wit/wiql                    │ WIQL bulk query  │
    │ GET  /_apis/wit/workitems?ids={ids}               │ batch fetch      │
    │ GET  /_apis/wit/workitems/{id}?$expand=all        │ SINGLE STORY ★   │
    │ GET  /_apis/wit/workitems/{id}/updates            │ history/audit    │
    │ GET  /_apis/wit/fields                            │ field catalogue  │
    │ GET  /_apis/testplan/plans                        │ test plans       │
    │ GET  /_apis/test/plans/{p}/suites/{s}/points      │ test points      │
    │ GET  /{project}/_apis/build/builds                │ pipeline runs    │
    │ GET  /{project}/_apis/git/repositories            │ repositories     │
    └─────────────────────────────────────────────────────────────────────┘

    ★ PRIMARY FETCH STRATEGY for single user story:
        GET /_apis/wit/workitems/{id}?$expand=all&api-version=7.1
        → Returns fields + relations + links in ONE round-trip
        → No WIQL intermediary needed
        → expand=all captures: parent, children, test case links, PR links

    BULK FETCH STRATEGY (matches QEMetricsCollection proven pattern):
        Step 1: POST /{project}/_apis/wit/wiql
                Body: { "query": "SELECT [System.Id] FROM WorkItems WHERE ..." }
                → Returns list of { id, url } (IDs only, fast)
        Step 2: POST /_apis/wit/workitemsbatch
                Body: { "ids": [...], "fields": [...] }
                Max 200 IDs per batch (ADO hard limit)
                → Returns full field payloads in batch

    WIQL PATTERNS FOR COMMON QUERIES:
        User Story by ID:
            SELECT [System.Id] FROM WorkItems
            WHERE [System.Id] = {id}

        User Stories in project (active):
            SELECT [System.Id] FROM WorkItems
            WHERE [System.TeamProject] = '{project}'
              AND [System.WorkItemType] = 'User Story'
              AND [System.State] NOT IN ('Removed', 'Cut')
            ORDER BY [System.ChangedDate] DESC

        User Stories for sprint:
            SELECT [System.Id] FROM WorkItems
            WHERE [System.TeamProject] = '{project}'
              AND [System.WorkItemType] = 'User Story'
              AND [System.IterationPath] = '{project}\\{sprint}'

        Test cases linked to story {id}:
            SELECT [System.Id] FROM WorkItemLinks
            WHERE [System.Links.LinkType] = 'Microsoft.VSTS.Common.TestedBy-Forward'
              AND [Source].[System.Id] = {id}
            MODE (MustContain)

    IMPORTANT ADO LIMITS:
        WIQL result cap:     20,000 items (hard limit, returns VS402337 error)
        Batch GET max IDs:   200 per request
        Rate limit:          No documented hard limit; throttle at 429 responses
        Response timeout:    30s recommended
        Field name format:   "System.Title", "Microsoft.VSTS.Common.AcceptanceCriteria"


──────────────────────────────────────────────────────────────────────────────
4. FIELD MAPPING SPECIFICATION
──────────────────────────────────────────────────────────────────────────────

    ADO REST Field Name                              → CORTEX Field
    ─────────────────────────────────────────────────────────────────
    System.Id                                        → id (str)
    System.Title                                     → title (str)
    System.Description                               → description (str)
    System.State                                     → state (str)
    System.WorkItemType                              → type (str)
    System.Tags                                      → tags (List[str])  semicolon-split
    _links.html.href                                 → url (str)
    System.AssignedTo.displayName                    → assignee (str | None)
    Microsoft.VSTS.Scheduling.StoryPoints            → story_points (float | None)
    Microsoft.VSTS.Common.Priority                   → priority (int | None)
    Microsoft.VSTS.Common.AcceptanceCriteria         → acceptance_criteria (str)
    System.AreaPath                                  → area_path (str)
    System.IterationPath                             → iteration_path (str)
    System.CreatedDate                               → created_at (datetime)
    System.ChangedDate                               → updated_at (datetime)
    relations[].rel == "System.LinkTypes.Hierarchy-Reverse" → parent_id (int | None)
    relations[].rel == "System.LinkTypes.Hierarchy-Forward" → child_ids (List[int])
    relations[].rel == "Microsoft.VSTS.Common.TestedBy"     → test_case_ids (List[int])
    raw (entire response dict)                       → raw (Dict[str, Any])  — preserved


──────────────────────────────────────────────────────────────────────────────
5. UserStoryContext DATACLASS (extended WorkItem)
──────────────────────────────────────────────────────────────────────────────

    Defined in ado_provider.py — extends WorkItem with ADO-specific fields:

    @dataclass
    class UserStoryContext:
        # Core (from WorkItem)
        id: str
        title: str
        description: str
        state: str
        type: str
        tags: List[str]
        url: str
        raw: Dict[str, Any]
        # ADO-specific enrichment
        assignee: str | None
        story_points: float | None
        priority: int | None
        acceptance_criteria: str
        area_path: str
        iteration_path: str
        created_at: datetime | None
        updated_at: datetime | None
        parent_id: int | None
        child_task_ids: List[int]
        linked_test_case_ids: List[int]
        linked_pr_ids: List[int]


──────────────────────────────────────────────────────────────────────────────
6. ADOOrchestrator — OrchestratorBase LIFECYCLE PLAN
──────────────────────────────────────────────────────────────────────────────

    Inherits OrchestratorBase 5-step lifecycle:

    setup()        → Instantiate ADOWorkItemProvider via provider_factory.
                     Validate env vars (ADO_ORG_URL, ADO_PAT, ADO_PROJECT).
                     Confirm health_check() == True.

    govern()       → Validate story_id is a positive integer.
                     Return GovernanceDecision(allowed=True) if valid.
                     Block and log if ID is invalid or out of range.

    execute()      → Dispatch based on operation mode:
                     MODE "fetch_story"         → provider.fetch_by_id(story_id)
                     MODE "fetch_bulk"          → provider.fetch_user_stories(project, **filters)
                     MODE "fetch_with_children" → fetch_by_id + child task IDs resolved
                     MODE "fetch_linked_tests"  → fetch test cases linked to story
                     MODE "search_wiql"         → raw WIQL passthrough for power users

    validate()     → Assert returned UserStoryContext has non-empty id and title.
                     Verify URL is well-formed.
                     Log field coverage (% of expected fields populated).

    teardown()     → Log execution summary to audit trail (CORE-049).
                     Clear any temp caches.

    Public API surface (entry points called by MasterOrchestrator):

        get_user_story(story_id: int) -> UserStoryContext
        get_user_story_with_children(story_id: int) -> dict
        get_linked_test_cases(story_id: int) -> List[UserStoryContext]
        fetch_user_stories(project: str, **filters) -> List[UserStoryContext]
        search_wiql(query: str, project: str) -> List[UserStoryContext]
        health_check() -> bool


──────────────────────────────────────────────────────────────────────────────
7. MCP TOOL SURFACE (future — wired via cortex/mcp/tools/)
──────────────────────────────────────────────────────────────────────────────

    Tool name                     │ Maps to ADOOrchestrator method
    ──────────────────────────────────────────────────────────────
    cortex_ado_get_story          │ get_user_story(story_id)
    cortex_ado_get_story_full     │ get_user_story_with_children(story_id)
    cortex_ado_get_linked_tests   │ get_linked_test_cases(story_id)
    cortex_ado_search             │ search_wiql(query, project)
    cortex_ado_bulk_stories       │ fetch_user_stories(project, **filters)
    cortex_ado_health             │ health_check()

    MCP tools live in: cortex/mcp/tools/ado_tools.py  (to be created)
    Each wraps ADOOrchestrator.coordinate_operation() — no direct provider calls.


──────────────────────────────────────────────────────────────────────────────
8. TDD IMPLEMENTATION ORDER (CORE-008 — RED → GREEN → REFACTOR)
──────────────────────────────────────────────────────────────────────────────

    Tests mirror cortex/ structure:
        tests/repositories/ado/test_ado_provider.py
        tests/orchestrators/domain/test_ado_orchestrator.py
        tests/mcp/test_ado_tools.py  (after orchestrator is green)

    RED phase test sequence:
     1. test_fetch_by_id_returns_user_story_context
     2. test_fetch_by_id_raises_key_error_on_missing_id
     3. test_fetch_by_id_maps_acceptance_criteria_field
     4. test_fetch_by_id_maps_parent_id_from_relations
     5. test_fetch_by_id_maps_child_task_ids_from_relations
     6. test_fetch_by_id_maps_linked_test_case_ids_from_relations
     7. test_fetch_user_stories_returns_list_of_work_items
     8. test_fetch_user_stories_respects_sprint_filter
     9. test_fetch_user_stories_respects_state_filter
    10. test_health_check_returns_true_on_reachable_org
    11. test_health_check_returns_false_on_bad_url
    12. test_ado_orchestrator_lifecycle_setup_validates_env
    13. test_ado_orchestrator_govern_blocks_invalid_story_id
    14. test_ado_orchestrator_execute_dispatches_fetch_story
    15. test_ado_orchestrator_validate_asserts_fields_populated


──────────────────────────────────────────────────────────────────────────────
9. DEPENDENCY SPECIFICATION
──────────────────────────────────────────────────────────────────────────────

    OPTION A — azure-devops Python SDK (RECOMMENDED):
        pip install azure-devops msrest
        from azure.devops.connection import Connection
        from msrest.authentication import BasicAuthentication
        Pros: typed, SDK-negotiated auth, no manual URL building
        Cons: heavier dependency (~10 MB)

    OPTION B — requests (CORTEX-native, already in requirements.txt):
        import requests
        Pros: zero new dependencies, already present, transparent
        Cons: manual URL construction, manual auth header encoding
        Auth: requests.auth.HTTPBasicAuth("", pat)

    DECISION: OPTION B (requests) — CORTEX already has it; keeps the package
    footprint stable. SDK can be added later behind a feature flag if needed.
    Both patterns documented in ado_provider.py implementation points.


──────────────────────────────────────────────────────────────────────────────
10. HOW QEMetricsCollection CONNECTS TO AZURE DEVOPS
──────────────────────────────────────────────────────────────────────────────

    Source: C:\PROJECTS\QEMetricsCollection
    Analysed: 2026-02-25

    ─── 10.1 ARCHITECTURE ────────────────────────────────────────────────────

    QEMetricsCollection uses a dual-path browser → ADO connection:

        Browser (AzureDevOpsClient)
            │
            ├─ checkProxy() → GET http://localhost:3001/health (2s timeout)
            │       ↓ 200 OK                    ↓ Error / timeout
            │
            ├─ PROXY PATH ──────────────────────────────────────────────────
            │   URL:     http://localhost:3001/api/ado/{organization}/...
            │   server.js strips "/api/ado/" prefix, forwards to:
            │            https://dev.azure.com/{organization}/...
            │   Purpose: CORS bypass (browsers block direct cross-origin ADO calls)
            │   Headers: forwarded verbatim (Authorization, Accept, Content-Type)
            │        + CORS headers injected by server.js on response
            │
            └─ DIRECT PATH (fallback — may fail in browser due to CORS) ────
                URL:     https://dev.azure.com/{organization}/...
                Used when proxy is not running (developer workstation w/o server)

    server.js process (C:\PROJECTS\QEMetricsCollection\server.js):
        - Express 4.x, port 3001 (or $PORT env var)
        - Route:   app.all('/api/ado/*', ...)
        - Timeout: 30,000 ms per upstream request
        - CORS:    Access-Control-Allow-Origin: * on all responses
        - CORS preflight (OPTIONS) handled before route matching
        - Graceful shutdown on SIGTERM / SIGINT

    ─── 10.2 AUTHENTICATION ──────────────────────────────────────────────────

    JavaScript (browser):
        headers["Authorization"] = `Basic ${btoa(":" + token)}`
        // ":" prefix = empty username; ADO PAT auth requires username field absent

    Python equivalent (ado_provider.py _auth_headers):
        token = base64.b64encode(f":{self._pat}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"

    ⚠️  Empty username is mandatory.  base64("username:token") will fail with HTTP 401.
    The PAT itself is sufficient — ADO does NOT use the username field for PAT auth.

    ─── 10.3 API VERSION ORDERING QUIRK ─────────────────────────────────────

    QEMetricsCollection enforces api-version=7.1 as the FIRST query parameter.
    ado-client.js apiCall() explicitly reorders query params if api-version is
    not first:

        // WRONG:   /_apis/wit/workitems/42?$expand=all&api-version=7.1
        // CORRECT: /_apis/wit/workitems/42?api-version=7.1&$expand=all

    CORTEX pattern: always pass api-version via requests params dict — requests
    serialises params in insertion order, so put api-version first:

        params = {"api-version": ADO_API_VERSION, "$expand": "all"}
        # → ?api-version=7.1&$expand=all  ✓

    Failure mode: ADO returns HTTP 203 (Non-Authoritative) or silently drops
    the api-version when it is not first in some endpoint paths.

    ─── 10.4 CREDENTIALS & CONFIG ───────────────────────────────────────────

    QEMetricsCollection:
        File:   config.json  (not committed — in .gitignore)
        Schema: { "organization": "<org>", "token": "<PAT>" }
        Template: config.template.json (committed — shows schema + PAT scope docs)

        PAT scopes required (documented in config.template.json):
            Work Items (Read)
            Project and Team (Read)
            Test Management (Read)

    CORTEX equivalent (env vars — CORE-049 silent, no config.json):
        ADO_ORG_URL  = "https://dev.azure.com/<org>"
        ADO_PAT      = "<PAT>"            same scopes as above
        ADO_PROJECT  = "<project-name>"

        CI/test overrides:
            ADO_SKIP_HEALTH_CHECK = "true"   (prevents HTTP calls in unit tests)
            ADO_ORG_URL / ADO_PAT / ADO_PROJECT set to dummy values for fixtures

    ─── 10.5 BULK FETCH PATTERN (proven in QEMetricsCollection) ─────────────

    Both systems use the identical two-step WIQL → batch-GET pattern:

        Step 1 — WIQL to get IDs (light, fast):
            POST /{project}/_apis/wit/wiql?api-version=7.1
            Body: { "query": "SELECT [System.Id] FROM WorkItems WHERE ..." }
            Response: { "workItems": [{"id": N, "url": "..."}, ...] }

        Step 2 — Batch GET for full fields (max 200 IDs per call):
            POST /_apis/wit/workitemsbatch?api-version=7.1
            Body: { "ids": [1..200], "fields": [...] }
            Response: { "count": N, "value": [{work item}, ...] }

        WIQL hard cap: 20,000 items → VS402337 error if exceeded.
        Mitigation: apply restrictive date / sprint / area_path filter and retry.

        QEMetricsCollection constants (validated against live ADO, use as-is):
            MAX_WORK_ITEMS:  15,000   (safe ceiling below 20K limit)
            BATCH_SIZE:      200      (ADO hard limit per workitemsbatch call)
            ADO_WIQL_LIMIT:  20,000   (ADO hard WIQL cap — triggers VS402337)
            REQUEST_TIMEOUT: 30,000 ms

    ─── 10.6 WHAT CORTEX DOES DIFFERENTLY ───────────────────────────────────

    1. No proxy server — Python has no CORS constraint; direct HTTPS to ADO.

    2. $expand=all on single-item GET — QEMetricsCollection skips relations
       (dashboard only needs metrics fields).  CORTEX NEEDS RELATIONS for:
           - parent_id (Epic/Feature context)
           - child_task_ids (related tasks in scope)
           - linked_test_case_ids (existing coverage gate for AuditCoordinator)
           - linked_pr_ids (associated code changes)
       → GET /_apis/wit/workitems/{id}?api-version=7.1&$expand=all

    3. UserStoryContext dataclass — richer than QEMetricsCollection's raw dict;
       typed fields, relation tree pre-parsed, acceptance_criteria extracted.

    4. Managed identity fallback — PAT works for local dev; Azure workloads can
       swap _auth_headers() for an Azure credential token (planned Phase 15+1).

    5. WIQL injection guard — QEMetricsCollection builds WIQL client-side;
       CORTEX sanitises all kwargs (strip single quotes, validate iteration path
       format) before string-interpolating into WIQL queries.
"""

from cortex.repositories.ado.ado_provider import ADOWorkItemProvider, UserStoryContext
from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator

__all__ = [
    "ADOWorkItemProvider",
    "UserStoryContext",
    "ADOOrchestrator",
]
