"""
ADOOrchestrator — Azure DevOps domain orchestrator for CORTEX pipelines.

══════════════════════════════════════════════════════════════════════════════
PLAN SPECIFICATION — READY FOR TDD RED PHASE
══════════════════════════════════════════════════════════════════════════════

This file contains the full ``ADOOrchestrator`` design:
  • OrchestratorBase 5-step lifecycle wired to ADOWorkItemProvider
  • All public methods with complete docstrings and implementation specs
  • Plug-in contract to MasterOrchestrator Stage 4 routing
  • MCP tool surface mapping

PLACEMENT:
    Source:  cortex/repositories/ado/ado_orchestrator.py  (this file)
    Tests:   tests/repositories/ado/test_ado_orchestrator.py
    MCP:     cortex/mcp/tools/ado_tools.py  (to be created after GREEN)

ROUTING (MasterOrchestrator Stage 2 → Stage 4):
    Intent "IMPLEMENT", scope contains "user story"  → ADOOrchestrator
    Intent "QUERY",     scope contains "ADO"         → ADOOrchestrator
    Direct: ADOOrchestrator(story_id=N, mode="fetch_story").execute()

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-012 (docstrings)
           CORE-028 (snake_case) · CORE-035 (single canonical) · CORE-049 (silent)
Phase: Phase 15 — Work Item Provider
AC-IDs: AC-P15-006, AC-P15-007, AC-P15-008
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from cortex.core.orchestrator_base import (
    ExecutionResult,
    GovernanceDecision,
    LifecycleStage,
    OrchestratorBase,
)
from cortex.repositories.ado.ado_provider import ADOWorkItemProvider, UserStoryContext
from cortex.repositories.work_item_provider import WorkItem

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Operation mode type alias
# ---------------------------------------------------------------------------

OperationMode = Literal[
    "fetch_story",          # Single story by ID — returns UserStoryContext
    "fetch_story_full",     # Single story + child tasks resolved
    "fetch_linked_tests",   # Test cases linked to a story
    "fetch_bulk",           # Bulk user stories via WIQL filters
    "search_wiql",          # Raw WIQL passthrough for power users
    "health_check",         # Verify ADO connectivity
]


# ---------------------------------------------------------------------------
# Result container for ADO operations
# ---------------------------------------------------------------------------

@dataclass
class ADOResult:
    """
    Container for ADO orchestrator results.

    Attributes:
        mode: The operation mode that produced this result.
        story: Single UserStoryContext result (fetch_story, fetch_story_full).
        stories: List of UserStoryContext (fetch_bulk, fetch_linked_tests, search_wiql).
        healthy: Health check result boolean (health_check mode).
        errors: List of error messages encountered during execution.
        metadata: Operation metadata (timing, item counts, WIQL used, etc.).
    """

    mode: OperationMode
    story: Optional[UserStoryContext] = None
    stories: List[UserStoryContext] = field(default_factory=list)
    healthy: Optional[bool] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# ADOOrchestrator
# ---------------------------------------------------------------------------

class ADOOrchestrator(OrchestratorBase):
    """
    CORTEX orchestrator for Azure DevOps work item operations.

    Wraps ``ADOWorkItemProvider`` in the OrchestratorBase 5-step lifecycle
    (setup → govern → execute → validate → teardown) and exposes a clean
    public API for all ADO operations.

    WIRING TO MasterOrchestrator:
        The MasterOrchestrator calls ``coordinate_operation()`` which delegates
        to OrchestratorBase.execute().  No direct provider calls bypass this
        lifecycle — all ADO access is gated through governance (CORE-050).

    TYPICAL USAGE (single story by ID)::

        from cortex.repositories.ado.ado_orchestrator import ADOOrchestrator

        orch = ADOOrchestrator(story_id=1234, mode="fetch_story")
        result = orch.execute()
        ctx = result.output["story"]  # UserStoryContext
        print(ctx.title, ctx.acceptance_criteria)

    TYPICAL USAGE (bulk with filters)::

        orch = ADOOrchestrator(
            mode="fetch_bulk",
            project="Quality Engineering",
            filters={"sprint": "Sprint 42", "state": "Active"},
        )
        result = orch.execute()
        stories = result.output["stories"]  # List[UserStoryContext]

    CONFIGURATION (env vars — never hardcode):
        ADO_ORG_URL  = "https://dev.azure.com/<org>"
        ADO_PAT      = "<personal-access-token>"
        ADO_PROJECT  = "<default-project>"

    Args:
        story_id: ADO work item ID for single-story operations.
                  Required for modes: fetch_story, fetch_story_full,
                  fetch_linked_tests.  Ignored for bulk/search/health modes.
        mode: Operation to perform.  Defaults to "fetch_story".
        project: ADO project name.  Falls back to ``ADO_PROJECT`` env var.
        filters: Dict of WIQL filter kwargs forwarded to fetch_user_stories
                 (sprint, area_path, state, assignee, changed_since).
        wiql: Raw WIQL query string for "search_wiql" mode.
        orchestrator_context: MasterOrchestrator routing context (optional).
                              When provided, triggers CORE-050 MCP gate check.
    """

    def __init__(
        self,
        story_id: Optional[int] = None,
        mode: OperationMode = "fetch_story",
        project: str = "",
        filters: Optional[Dict[str, Any]] = None,
        wiql: Optional[str] = None,
        orchestrator_context: Optional[Any] = None,
    ) -> None:
        """Initialise ADOOrchestrator with operation parameters."""
        super().__init__(orchestrator_id="ado_orchestrator")
        self._story_id = story_id
        self._mode: OperationMode = mode
        self._project = project or os.getenv("ADO_PROJECT", "")
        self._filters: Dict[str, Any] = filters or {}
        self._wiql = wiql
        self._orchestrator_context = orchestrator_context
        self._provider: Optional[ADOWorkItemProvider] = None
        self._ado_result: Optional[ADOResult] = None

    # -----------------------------------------------------------------------
    # OrchestratorBase lifecycle implementation
    # -----------------------------------------------------------------------

    def setup(self) -> None:
        """
        Instantiate and connect ADOWorkItemProvider.

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION:                                                  │
        │   1. Read env vars: ADO_ORG_URL, ADO_PAT, ADO_PROJECT          │
        │   2. Raise EnvironmentError if ADO_ORG_URL or ADO_PAT missing  │
        │   3. Instantiate ADOWorkItemProvider(org_url, pat, project)     │
        │   4. Call provider.health_check() — raise RuntimeError if False │
        │      (Skip health_check in test environments via env flag        │
        │       ADO_SKIP_HEALTH_CHECK=true to allow unit test injection)  │
        └─────────────────────────────────────────────────────────────────┘

        Raises:
            EnvironmentError: Required env vars ADO_ORG_URL or ADO_PAT not set.
            RuntimeError: ADO organisation is unreachable or PAT is invalid.
        """
        org_url = os.getenv("ADO_ORG_URL", "")
        pat = os.getenv("ADO_PAT", "")
        project = self._project or os.getenv("ADO_PROJECT", "")

        # ----------------------------------------------------------------
        # IMPLEMENTATION POINT
        #
        # if not org_url:
        #     raise EnvironmentError("ADO_ORG_URL environment variable is not set")
        # if not pat:
        #     raise EnvironmentError("ADO_PAT environment variable is not set")
        #
        # self._provider = ADOWorkItemProvider(
        #     org_url=org_url, pat=pat, project=project
        # )
        # self._project = project
        #
        # skip_health = os.getenv("ADO_SKIP_HEALTH_CHECK", "").lower() == "true"
        # if not skip_health and not self._provider.health_check():
        #     raise RuntimeError(
        #         f"ADO health check failed for org: {org_url}. "
        #         f"Verify ADO_ORG_URL and ADO_PAT are correct."
        #     )
        # ----------------------------------------------------------------
        logger.debug("ADOOrchestrator.setup() — provider instantiation pending implementation")

    def govern(self) -> GovernanceDecision:
        """
        Validate inputs and enforce governance gates before execution.

        ┌─────────────────────────────────────────────────────────────────┐
        │ GOVERNANCE RULES:                                               │
        │                                                                 │
        │ 1. CORE-050 MCP gate (when orchestrator_context is set):       │
        │    validate_orchestrator_context(self._orchestrator_context)    │
        │                                                                 │
        │ 2. Mode-specific input validation:                              │
        │    fetch_story / fetch_story_full / fetch_linked_tests:         │
        │      → story_id must be a positive integer                      │
        │      → story_id > 0 and story_id < 10_000_000 (reasonable cap) │
        │                                                                 │
        │    fetch_bulk:                                                   │
        │      → project must be non-empty string                         │
        │      → filters dict keys must be in ALLOWED_FILTERS set         │
        │                                                                 │
        │    search_wiql:                                                  │
        │      → wiql must be non-empty string                            │
        │      → wiql must start with "SELECT" (basic injection guard)    │
        │      → project must be non-empty                                │
        │                                                                 │
        │ 3. Return GovernanceDecision(allowed=True) if all pass          │
        │    Return GovernanceDecision(allowed=False, reason=...) if fail │
        └─────────────────────────────────────────────────────────────────┘

        Returns:
            GovernanceDecision with allowed=True if all gates pass.
        """
        violations: List[str] = []

        # CORE-050 MCP context check
        if self._orchestrator_context is not None:
            # ----------------------------------------------------------------
            # IMPLEMENTATION POINT
            # from cortex.mcp.orchestrator_context import validate_orchestrator_context
            # validate_orchestrator_context(self._orchestrator_context)
            # ----------------------------------------------------------------
            pass

        # Mode-specific validation
        single_story_modes = {"fetch_story", "fetch_story_full", "fetch_linked_tests"}
        if self._mode in single_story_modes:
            if not self._story_id or not isinstance(self._story_id, int):
                violations.append(
                    f"story_id must be a positive integer for mode '{self._mode}'; "
                    f"got {self._story_id!r}"
                )
            elif self._story_id <= 0 or self._story_id >= 10_000_000:
                violations.append(
                    f"story_id {self._story_id} is outside valid range (1 – 9,999,999)"
                )

        if self._mode == "fetch_bulk":
            if not self._project:
                violations.append("project must be non-empty for mode 'fetch_bulk'")
            allowed_filters = {"sprint", "area_path", "state", "assignee", "changed_since"}
            bad_keys = set(self._filters.keys()) - allowed_filters
            if bad_keys:
                violations.append(f"Unknown filter keys: {bad_keys}")

        if self._mode == "search_wiql":
            if not self._wiql:
                violations.append("wiql query string must be provided for mode 'search_wiql'")
            elif not self._wiql.strip().upper().startswith("SELECT"):
                violations.append("WIQL query must begin with SELECT")
            if not self._project:
                violations.append("project must be non-empty for mode 'search_wiql'")

        if violations:
            return GovernanceDecision(
                allowed=False,
                reason="ADOOrchestrator governance validation failed",
                violations=violations,
            )

        return GovernanceDecision(allowed=True, reason="All ADO governance gates passed")

    def execute(self) -> ExecutionResult:
        """
        Dispatch to the appropriate ADO operation based on ``mode``.

        This overrides OrchestratorBase.execute() to call the full
        5-step lifecycle — do NOT call this method's body directly.
        Call ``orch.execute()`` which calls setup → govern → this → validate.

        For direct execution, call the public convenience methods instead:
            get_user_story(), fetch_user_stories(), search_wiql(), etc.

        ┌─────────────────────────────────────────────────────────────────┐
        │ DISPATCH TABLE:                                                  │
        │   "fetch_story"        → _do_fetch_story()                     │
        │   "fetch_story_full"   → _do_fetch_story_full()                │
        │   "fetch_linked_tests" → _do_fetch_linked_tests()              │
        │   "fetch_bulk"         → _do_fetch_bulk()                      │
        │   "search_wiql"        → _do_search_wiql()                     │
        │   "health_check"       → _do_health_check()                    │
        └─────────────────────────────────────────────────────────────────┘

        Returns:
            ExecutionResult with output["story"] or output["stories"] set.
        """
        from datetime import datetime
        start = datetime.now()

        dispatch = {
            "fetch_story": self._do_fetch_story,
            "fetch_story_full": self._do_fetch_story_full,
            "fetch_linked_tests": self._do_fetch_linked_tests,
            "fetch_bulk": self._do_fetch_bulk,
            "search_wiql": self._do_search_wiql,
            "health_check": self._do_health_check,
        }

        handler = dispatch.get(self._mode)
        if not handler:
            return ExecutionResult(
                success=False,
                stage=LifecycleStage.EXECUTE,
                duration_ms=0,
                error=f"Unknown mode: {self._mode!r}",
            )

        self._ado_result = handler()
        duration = int((datetime.now() - start).total_seconds() * 1000)

        output: Dict[str, Any] = {"mode": self._mode}
        if self._ado_result.story:
            output["story"] = self._ado_result.story
        if self._ado_result.stories:
            output["stories"] = self._ado_result.stories
        if self._ado_result.healthy is not None:
            output["healthy"] = self._ado_result.healthy

        return ExecutionResult(
            success=not self._ado_result.errors,
            stage=LifecycleStage.EXECUTE,
            duration_ms=duration,
            output=output,
            metadata=self._ado_result.metadata,
        )

    def validate(self) -> None:
        """
        Assert execution result quality after execute().

        ┌─────────────────────────────────────────────────────────────────┐
        │ VALIDATION CHECKS:                                              │
        │                                                                 │
        │ For fetch_story / fetch_story_full:                             │
        │   • result.story is not None                                    │
        │   • result.story.id is non-empty                               │
        │   • result.story.title is non-empty                            │
        │   • result.story.url is well-formed (starts with "https://")   │
        │   • Log field coverage: % of optional fields populated         │
        │     (story_points, acceptance_criteria, iteration_path, etc.)  │
        │                                                                 │
        │ For fetch_bulk / search_wiql:                                   │
        │   • result.stories is a list (may be empty — not an error)     │
        │   • Each story in the list has non-empty id and title          │
        │                                                                 │
        │ For health_check:                                               │
        │   • result.healthy is a boolean (not None)                     │
        └─────────────────────────────────────────────────────────────────┘

        Raises:
            AssertionError: If a critical field is missing from the result.
        """
        if not self._ado_result:
            return  # execute() didn't run (governance blocked)

        single_story_modes = {"fetch_story", "fetch_story_full"}
        if self._mode in single_story_modes and self._ado_result.story:
            story = self._ado_result.story
            assert story.id, "ADO result: story.id must be non-empty"
            assert story.title, "ADO result: story.title must be non-empty"
            # Log field coverage (CORE-049 — silent, debug level only)
            populated = sum([
                bool(story.assignee),
                bool(story.story_points),
                bool(story.acceptance_criteria),
                bool(story.iteration_path),
                bool(story.area_path),
                bool(story.parent_id),
            ])
            total_optional = 6
            logger.debug(
                "ADO field coverage: %d/%d optional fields populated for story %s",
                populated, total_optional, story.id,
            )

    def teardown(self) -> None:
        """
        Log execution summary and clean up transient state.

        CORE-049: Silent — debug level logging only, no stdout output.
        """
        logger.debug(
            "ADOOrchestrator teardown: mode=%s story_id=%s errors=%s",
            self._mode,
            self._story_id,
            self._ado_result.errors if self._ado_result else [],
        )
        # Clear any per-execution state (not the provider — it's reusable)
        self._ado_result = None

    # -----------------------------------------------------------------------
    # Public convenience API (called directly or via MCP tools)
    # -----------------------------------------------------------------------

    def get_user_story(self, story_id: int) -> UserStoryContext:
        """
        Fetch a single user story by ADO ID — primary entry point.

        Convenience method that sets mode="fetch_story", runs the full
        5-step lifecycle, and returns the ``UserStoryContext`` directly.

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION:                                                  │
        │   1. self._story_id = story_id                                  │
        │   2. self._mode = "fetch_story"                                 │
        │   3. result = OrchestratorBase.execute(self)                    │
        │   4. return result.output["story"]                              │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            story_id: ADO work item numeric ID.

        Returns:
            UserStoryContext with all fields and relations populated.

        Raises:
            KeyError: Work item does not exist.
            PermissionError: ADO PAT auth failure.
            ValueError: story_id is not a valid positive integer.
        """
        self._story_id = story_id
        self._mode = "fetch_story"
        # ----------------------------------------------------------------
        # IMPLEMENTATION POINT
        # result = super().execute()
        # return result.output["story"]
        # ----------------------------------------------------------------
        raise NotImplementedError("get_user_story — implement after TDD RED phase")

    def get_user_story_with_children(self, story_id: int) -> Dict[str, Any]:
        """
        Fetch a user story plus its child task details.

        Returns the parent story context AND resolves child task IDs
        into full ``UserStoryContext`` instances (for Task type children).

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION:                                                  │
        │   1. parent = self.get_user_story(story_id)                     │
        │   2. children = [                                               │
        │          self._provider.fetch_story_context(str(cid))          │
        │          for cid in parent.child_task_ids                       │
        │      ]                                                          │
        │   3. Return {                                                   │
        │          "parent": parent,                                      │
        │          "children": children,                                  │
        │          "child_count": len(children),                          │
        │      }                                                          │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            story_id: ADO work item numeric ID of the parent story.

        Returns:
            Dict with keys: parent (UserStoryContext), children
            (List[UserStoryContext]), child_count (int).
        """
        raise NotImplementedError("get_user_story_with_children — pending TDD")

    def get_linked_test_cases(self, story_id: int) -> List[UserStoryContext]:
        """
        Fetch all test cases linked to a user story via TestedBy relation.

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION:                                                  │
        │   1. parent = self.get_user_story(story_id)                     │
        │   2. test_cases = [                                             │
        │          self._provider.fetch_story_context(str(tid))          │
        │          for tid in parent.linked_test_case_ids                 │
        │      ]                                                          │
        │   3. return test_cases                                          │
        └─────────────────────────────────────────────────────────────────┘

        Args:
            story_id: ADO work item ID of the user story.

        Returns:
            List of UserStoryContext instances for linked test cases.
            Empty list if no test cases are linked.
        """
        raise NotImplementedError("get_linked_test_cases — pending TDD")

    def fetch_user_stories(
        self,
        project: str = "",
        **filters: Any,
    ) -> List[UserStoryContext]:
        """
        Fetch all user stories matching the given filters.

        Wraps ``ADOWorkItemProvider.fetch_user_stories`` in the lifecycle.
        Returns ``UserStoryContext`` instances (not base ``WorkItem``).

        Supported filter kwargs:
            sprint:        Sprint/iteration name (e.g. "Sprint 42")
            area_path:     ADO area path string
            state:         Work item state (e.g. "Active")
            assignee:      Assignee display name
            changed_since: ISO date string (e.g. "2026-01-01")

        Args:
            project: ADO project name; falls back to ADO_PROJECT env var.
            **filters: WIQL filter kwargs (see above).

        Returns:
            List of UserStoryContext instances; empty if no matches.
        """
        raise NotImplementedError("fetch_user_stories — pending TDD")

    def search_wiql(
        self,
        query: str,
        project: str = "",
    ) -> List[UserStoryContext]:
        """
        Execute a raw WIQL query and return matching work items.

        Power-user escape hatch that delegates directly to the provider's
        ``_run_wiql`` + ``_batch_get`` pipeline.  Governance still applies:
        WIQL must begin with SELECT, project must be non-empty.

        Args:
            query: Complete WIQL SELECT statement.
            project: ADO project name.

        Returns:
            List of UserStoryContext instances matching the query.
        """
        raise NotImplementedError("search_wiql — pending TDD")

    def health_check(self) -> bool:
        """
        Verify ADO connectivity and PAT validity.

        Returns:
            True if ADO is reachable and PAT authenticates successfully.
        """
        raise NotImplementedError("health_check — pending TDD")

    # -----------------------------------------------------------------------
    # Private: mode dispatch handlers
    # -----------------------------------------------------------------------

    def _do_fetch_story(self) -> ADOResult:
        """
        Execute single story fetch by ID.

        ┌─────────────────────────────────────────────────────────────────┐
        │ IMPLEMENTATION:                                                  │
        │   try:                                                          │
        │       ctx = self._provider.fetch_story_context(str(self._story_id)) │
        │       return ADOResult(                                         │
        │           mode="fetch_story",                                   │
        │           story=ctx,                                            │
        │           metadata={"story_id": self._story_id},               │
        │       )                                                         │
        │   except KeyError as e:                                         │
        │       return ADOResult(mode="fetch_story",                      │
        │           errors=[f"Story {self._story_id} not found: {e}"])   │
        │   except PermissionError as e:                                  │
        │       return ADOResult(mode="fetch_story",                      │
        │           errors=[f"ADO auth error: {e}"])                     │
        └─────────────────────────────────────────────────────────────────┘
        """
        # IMPLEMENTATION POINT — replace stub
        return ADOResult(mode="fetch_story", errors=["_do_fetch_story not implemented"])

    def _do_fetch_story_full(self) -> ADOResult:
        """
        Execute story + children fetch.

        Calls _do_fetch_story first to get parent, then resolves all
        child_task_ids into full UserStoryContext instances.
        """
        return ADOResult(mode="fetch_story_full", errors=["_do_fetch_story_full not implemented"])

    def _do_fetch_linked_tests(self) -> ADOResult:
        """
        Execute linked test case fetch for a story.

        Calls _do_fetch_story first to get linked_test_case_ids,
        then resolves each into a full UserStoryContext.
        """
        return ADOResult(mode="fetch_linked_tests", errors=["_do_fetch_linked_tests not implemented"])

    def _do_fetch_bulk(self) -> ADOResult:
        """
        Execute bulk user story fetch via WIQL + batch GET.

        Delegates to provider.fetch_user_stories, then maps each
        WorkItem to UserStoryContext via provider._map_to_context
        (or re-fetches with expand=all if relations are needed).
        """
        return ADOResult(mode="fetch_bulk", errors=["_do_fetch_bulk not implemented"])

    def _do_search_wiql(self) -> ADOResult:
        """
        Execute raw WIQL query and return results as UserStoryContext list.

        Uses provider._run_wiql for ID list, then provider._batch_get
        for field data.  Validates WIQL starts with SELECT before calling.
        """
        return ADOResult(mode="search_wiql", errors=["_do_search_wiql not implemented"])

    def _do_health_check(self) -> ADOResult:
        """
        Execute ADO connectivity health check.

        Returns ADOResult with healthy=True/False and
        metadata["org_url"] set for diagnostic logging.
        """
        return ADOResult(mode="health_check", errors=["_do_health_check not implemented"])
