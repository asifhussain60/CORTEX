"""
ADOOrchestrator — OrchestratorBase subclass for Azure DevOps operations.

Provides the 5-step lifecycle wrapper around ADOWorkItemProvider, exposing
ADO work item fetching as a first-class CORTEX orchestration operation.

This is the TERMINAL orchestrator (Layer 2). The primary entry into ADO
for automated enrichment uses ADOContextEnricher (Layer 3) instead.

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-012 (docstrings)
Phase: Phase 15 — Work Item Provider (ADO implementation)
AC-IDs: AC-ADO-O-001 through AC-ADO-O-015
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from cortex.core.orchestrator_base import GovernanceDecision, OrchestratorBase

logger = logging.getLogger(__name__)

# Six supported operation modes
OperationMode = Literal[
    "fetch_story",
    "fetch_story_full",
    "fetch_linked_tests",
    "fetch_bulk",
    "search_wiql",
    "health_check",
]

# Filters allowed for fetch_bulk and search operations
_ALLOWED_FILTERS = frozenset({"sprint", "area", "state", "assignee"})


@dataclass
class ADOResult:
    """
    Structured output from ADOOrchestrator.execute_operation().

    Attributes:
        mode: The OperationMode that produced this result.
        story: Single story context (fetch_story, fetch_story_full modes).
        stories: Multiple story contexts (fetch_bulk mode).
        healthy: Health check result (health_check mode).
        errors: Non-fatal error messages accumulated during execution.
        metadata: Arbitrary key/value metadata for audit trail.
    """

    mode: str
    story: Optional[Any] = None  # UserStoryContext
    stories: List[Any] = field(default_factory=list)  # List[UserStoryContext]
    healthy: Optional[bool] = None
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ADOOrchestrator(OrchestratorBase):
    """
    OrchestratorBase subclass for Azure DevOps work item operations.

    Lifecycle:
        setup()            — create ADOWorkItemProvider from env vars
        govern()           — validate story_id, project, mode, WIQL safety
        execute_operation()— dispatch to _do_fetch_story / _do_fetch_bulk etc.
        validate()         — check result completeness
        teardown()         — silent audit log (CORE-049)

    Public entry points (convenience wrappers):
        get_user_story(story_id)
        get_user_story_with_children(story_id)
        get_linked_test_cases(story_id)
        fetch_user_stories(project, **filters)
        search_wiql(project, wiql)
        health_check()
    """

    def __init__(
        self,
        story_id: Optional[int] = None,
        mode: OperationMode = "health_check",
        project: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        wiql: Optional[str] = None,
        org_url: Optional[str] = None,
        pat: Optional[str] = None,
    ) -> None:
        super().__init__(orchestrator_id="ado_orchestrator")
        self._story_id = story_id
        self._mode = mode
        self._project = project or os.environ.get("ADO_PROJECT", "")
        self._filters = filters or {}
        self._wiql = wiql or ""
        self._org_url = org_url or os.environ.get("ADO_ORG_URL", "")
        self._pat = pat or os.environ.get("ADO_PAT", "")
        self._provider: Any = None  # ADOWorkItemProvider (injected or built in setup)
        self._result: Optional[ADOResult] = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def setup(self) -> None:
        """Build ADOWorkItemProvider from env vars, unless already injected."""
        if self._provider is None:
            from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
            self._provider = ADOWorkItemProvider(
                org_url=self._org_url,
                pat=self._pat,
                project=self._project,
            )

    def govern(self) -> GovernanceDecision:
        """
        Governance gate: validate all inputs before ADO HTTP calls.

        Rules:
            - fetch_story / fetch_story_full / fetch_linked_tests: story_id must be > 0
            - fetch_bulk: project must not be empty; filters keys must be in _ALLOWED_FILTERS
            - search_wiql: project not empty; wiql must start with SELECT (case-insensitive)
            - health_check: no constraints
        """
        violations: List[str] = []

        single_story_modes = {"fetch_story", "fetch_story_full", "fetch_linked_tests"}

        if self._mode in single_story_modes:
            if self._story_id is None:
                violations.append(
                    f"story_id is required for mode '{self._mode}' but was not provided"
                )
            elif not isinstance(self._story_id, int) or isinstance(self._story_id, bool):
                violations.append(
                    f"story_id must be an integer, got {type(self._story_id).__name__!r}"
                )
            elif self._story_id <= 0:
                violations.append(
                    f"story_id must be > 0, got {self._story_id}"
                )

        if self._mode in {"fetch_bulk", "search_wiql"}:
            if not self._project:
                violations.append(
                    f"project is required for mode '{self._mode}' but was empty"
                )

        if self._mode == "fetch_bulk":
            bad_keys = set(self._filters.keys()) - _ALLOWED_FILTERS
            if bad_keys:
                violations.append(
                    f"Unknown filter keys: {sorted(bad_keys)}. "
                    f"Allowed: {sorted(_ALLOWED_FILTERS)}"
                )

        if self._mode == "search_wiql":
            if not self._wiql.strip().upper().startswith("SELECT"):
                violations.append(
                    "WIQL query must start with SELECT — "
                    f"got: {self._wiql[:40]!r}"
                )

        if violations:
            return GovernanceDecision(
                allowed=False,
                reason="; ".join(violations),
                violations=violations,
            )

        return GovernanceDecision(allowed=True, reason="All ADO inputs valid")

    def execute_operation(self) -> Dict[str, Any]:
        """Dispatch to mode-specific handler and return output dict."""
        dispatch = {
            "fetch_story": self._do_fetch_story,
            "fetch_story_full": self._do_fetch_story_full,
            "fetch_linked_tests": self._do_fetch_linked_tests,
            "fetch_bulk": self._do_fetch_bulk,
            "search_wiql": self._do_search_wiql,
            "health_check": self._do_health_check,
        }
        handler = dispatch.get(self._mode, self._do_health_check)
        self._result = handler()
        return {
            "mode": self._result.mode,
            "story": self._result.story,
            "stories": self._result.stories,
            "healthy": self._result.healthy,
            "errors": self._result.errors,
            "metadata": self._result.metadata,
        }

    def validate(self, output: Dict[str, Any] = None) -> bool:
        """Check that the expected output key is populated."""
        if output is None:
            return True
        if self._mode == "health_check":
            return output.get("healthy") is not None
        if self._mode in {"fetch_story", "fetch_story_full", "fetch_linked_tests"}:
            return output.get("story") is not None or bool(output.get("errors"))
        if self._mode == "fetch_bulk":
            return isinstance(output.get("stories"), list)
        return True

    def teardown(self, result=None) -> None:  # type: ignore[override]
        """Silent audit log per CORE-049."""
        if result and not result.success:
            logger.debug(
                "ado_orchestrator: execution failed (mode=%s, error=%s)",
                self._mode,
                result.error,
            )

    # ── Private mode handlers ─────────────────────────────────────────────────

    def _do_fetch_story(self) -> ADOResult:
        try:
            ctx = self._provider.fetch_story_context(str(self._story_id))
            return ADOResult(mode="fetch_story", story=ctx)
        except Exception as exc:
            return ADOResult(mode="fetch_story", errors=[str(exc)])

    def _do_fetch_story_full(self) -> ADOResult:
        return ADOResult(
            mode="fetch_story_full",
            errors=["RED: _do_fetch_story_full not yet implemented"],
        )

    def _do_fetch_linked_tests(self) -> ADOResult:
        return ADOResult(
            mode="fetch_linked_tests",
            errors=["RED: _do_fetch_linked_tests not yet implemented"],
        )

    def _do_fetch_bulk(self) -> ADOResult:
        return ADOResult(
            mode="fetch_bulk",
            stories=[],
            errors=["RED: _do_fetch_bulk not yet implemented"],
        )

    def _do_search_wiql(self) -> ADOResult:
        return ADOResult(
            mode="search_wiql",
            stories=[],
            errors=["RED: _do_search_wiql not yet implemented"],
        )

    def _do_health_check(self) -> ADOResult:
        healthy = self._provider.health_check() if self._provider else False
        return ADOResult(mode="health_check", healthy=healthy)

    # ── Public convenience API ────────────────────────────────────────────────

    def get_user_story(self, story_id: int) -> Any:
        """Fetch a single user story context."""
        self._story_id = story_id
        self._mode = "fetch_story"
        result = self.execute()
        return result.output.get("story")

    def get_user_story_with_children(self, story_id: int) -> Any:
        """Fetch story + child task IDs."""
        self._story_id = story_id
        self._mode = "fetch_story_full"
        result = self.execute()
        return result.output.get("story")

    def get_linked_test_cases(self, story_id: int) -> List[int]:
        """Return test case IDs linked to the story."""
        self._story_id = story_id
        self._mode = "fetch_linked_tests"
        result = self.execute()
        return result.output.get("story", {}) or []

    def fetch_user_stories(self, project: str, **filters: str) -> List[Any]:
        """Bulk fetch user stories for a project."""
        self._project = project
        self._filters = filters
        self._mode = "fetch_bulk"
        result = self.execute()
        return result.output.get("stories", [])

    def search_wiql(self, project: str, wiql: str) -> List[Any]:
        """Execute a raw WIQL query."""
        self._project = project
        self._wiql = wiql
        self._mode = "search_wiql"
        result = self.execute()
        return result.output.get("stories", [])
