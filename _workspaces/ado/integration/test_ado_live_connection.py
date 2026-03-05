"""
Live ADO Connection Test — _workspaces/ado/integration/
════════════════════════════════════════════════════════════════════════════════

Purpose:
    Verify REAL connectivity to Azure DevOps using the ADOWorkItemProvider
    implementation.  Fetches work item #692945 from the V5 project and
    asserts that all mapped fields are populated correctly.

    This test makes LIVE HTTP calls and requires a valid PAT.
    It is automatically SKIPPED when:
        • ADO_PAT env var is missing
        • ADO_PAT is the golden-suite test placeholder ("test-pat-golden-suite")
        • ADO_SKIP_LIVE_TESTS=true is set (for CI pipelines)

Run manually:
    $env:ADO_PAT = "<your-pat>"
    python -m pytest _workspaces/ado/integration/ -v -s

Authority: CORE-008 (TDD) · CORE-049 (silent exec) · CORE-011 (type hints)
Target story: https://dev.azure.com/HQY01/V5/_workitems/edit/692945
"""

from __future__ import annotations

import os
import re
from datetime import datetime

import pytest

# ── Skip guard ─────────────────────────────────────────────────────────────────
_PAT = os.environ.get("ADO_PAT", "")
_SKIP_REASON = ""

if not _PAT:
    _SKIP_REASON = "ADO_PAT env var is not set — set it to a valid PAT and re-run"
elif _PAT == "test-pat-golden-suite":
    _SKIP_REASON = "ADO_PAT is the mock placeholder — set a real PAT to run live tests"
elif os.environ.get("ADO_SKIP_LIVE_TESTS", "").lower() == "true":
    _SKIP_REASON = "ADO_SKIP_LIVE_TESTS=true — live tests disabled for this run"

live = pytest.mark.skipif(bool(_SKIP_REASON), reason=_SKIP_REASON or "live ADO unavailable")

# ── Constants ─────────────────────────────────────────────────────────────────
ORG_URL = "https://dev.azure.com/HQY01"
PROJECT = "V5"
STORY_ID = "692945"
STORY_WEB_URL_PATTERN = re.compile(
    r"https://dev\.azure\.com/HQY01/V5/_workitems/edit/692945",
    re.IGNORECASE,
)


# ── Shared provider fixture ───────────────────────────────────────────────────

@pytest.fixture(scope="module")
def provider():
    """Real ADOWorkItemProvider — live credentials, no mocks."""
    from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
    return ADOWorkItemProvider(org_url=ORG_URL, pat=_PAT, project=PROJECT)


@pytest.fixture(scope="module")
def story_context(provider):
    """Fetch story #692945 once for the entire module; all tests share it."""
    return provider.fetch_story_context(STORY_ID)


# ════════════════════════════════════════════════════════════════════════════════
# Live connection tests
# ════════════════════════════════════════════════════════════════════════════════

class TestADOLiveConnection:
    """
    Live integration tests for ADOWorkItemProvider against story #692945.

    All tests share a single HTTP fetch (module-scoped fixture) to avoid
    hammering the ADO API.
    """

    @live
    def test_health_check_returns_true_with_valid_pat(self, provider):
        """
        Health check must return True when PAT is valid.

        Verifies: GET /_apis/projects?api-version=7.1 responds with 200.
        """
        healthy = provider.health_check()
        assert healthy is True, (
            f"health_check() returned False.\n"
            f"Check ADO_PAT is valid and has 'Read' scope on the V5 project.\n"
            f"ORG_URL: {ORG_URL}"
        )

    @live
    def test_story_id_matches_requested_id(self, story_context):
        """Fetched story ID must match what was requested."""
        assert story_context.id == STORY_ID, (
            f"Expected id={STORY_ID!r}, got {story_context.id!r}"
        )

    @live
    def test_story_title_is_non_empty_string(self, story_context):
        """Title must be a non-empty string — confirms field mapping works."""
        assert isinstance(story_context.title, str)
        assert story_context.title.strip(), "title must not be blank"

    @live
    def test_story_state_is_known_ado_state(self, story_context):
        """
        State must be one of the standard ADO work item states.

        If this fails the story was moved to a custom state — update the set.
        """
        known_states = {
            "New", "Active", "Resolved", "Closed",
            "Removed", "In Progress", "Done", "To Do",
        }
        assert story_context.state in known_states, (
            f"Unexpected state {story_context.state!r}. "
            f"Known states: {sorted(known_states)}"
        )

    @live
    def test_story_type_is_user_story(self, story_context):
        """Work item type must be 'User Story'."""
        assert story_context.type == "User Story", (
            f"Expected type='User Story', got {story_context.type!r}"
        )

    @live
    def test_story_url_points_to_ado_web_interface(self, story_context):
        """
        URL must point to the ADO web interface for story 692945.

        This verifies _links.html.href was extracted (not fabricated).
        """
        assert STORY_WEB_URL_PATTERN.search(story_context.url), (
            f"story.url does not match expected ADO pattern.\n"
            f"Got: {story_context.url!r}"
        )

    @live
    def test_story_tags_are_a_list(self, story_context):
        """
        tags must be a Python list (not the raw semicolon-delimited string).

        Guards against regression where _map() returns the raw tags string.
        """
        assert isinstance(story_context.tags, list), (
            f"Expected list, got {type(story_context.tags)}: {story_context.tags!r}\n"
            f"Check that _map() splits on ';' and strips whitespace."
        )

    @live
    def test_acceptance_criteria_is_string(self, story_context):
        """
        acceptance_criteria must be a string (may be empty if unset in ADO).

        TDDOrchestrator reads this — must never be None.
        """
        assert isinstance(story_context.acceptance_criteria, str), (
            f"acceptance_criteria must be str, got {type(story_context.acceptance_criteria)}"
        )

    @live
    def test_iteration_path_is_non_empty(self, story_context):
        """
        iteration_path (Sprint) must be populated.

        If blank: verify the story has an assigned Sprint in ADO.
        """
        assert story_context.iteration_path, (
            "iteration_path is empty — story may not have an assigned Sprint in ADO"
        )

    @live
    def test_created_at_is_a_datetime_object(self, story_context):
        """
        created_at must be a datetime after ISO 8601 parse.

        Guards against returning the raw string from System.CreatedDate.
        """
        assert isinstance(story_context.created_at, datetime), (
            f"created_at must be datetime, got {type(story_context.created_at)}: "
            f"{story_context.created_at!r}"
        )

    @live
    def test_raw_contains_full_ado_response(self, story_context):
        """
        raw must contain the complete ADO response including 'fields' and 'relations'.

        This verifies $expand=all was correctly appended to the GET request.
        An expand=all response always includes the 'relations' key (even if []).
        """
        assert "fields" in story_context.raw, "raw must contain 'fields'"
        assert "relations" in story_context.raw, (
            "'relations' key absent — confirm $expand=all is in the GET URL"
        )

    @live
    def test_parent_id_is_int_or_none(self, story_context):
        """
        parent_id must be an integer (the Epic/Feature ID) or None.

        Never a string URL — confirms URL tail-segment extraction works.
        """
        assert story_context.parent_id is None or isinstance(story_context.parent_id, int), (
            f"parent_id must be int or None, got {type(story_context.parent_id)}: "
            f"{story_context.parent_id!r}"
        )

    @live
    def test_child_task_ids_are_all_ints(self, story_context):
        """
        child_task_ids must be a list of integers (not strings or dicts).

        Empty list is acceptable if the story has no children.
        """
        assert isinstance(story_context.child_task_ids, list)
        for item in story_context.child_task_ids:
            assert isinstance(item, int), (
                f"child_task_ids contains non-int: {item!r} ({type(item)})"
            )

    @live
    def test_fetch_by_id_returns_work_item_with_same_id(self, provider):
        """
        fetch_by_id() must return a WorkItem whose id matches the requested ID.

        Validates the canonical WorkItemProvider protocol method.
        """
        from cortex.repositories.work_item_provider import WorkItem
        wi = provider.fetch_by_id(STORY_ID)
        assert isinstance(wi, WorkItem)
        assert wi.id == STORY_ID

    @live
    def test_print_story_summary(self, story_context):
        """
        Informational: print a human-readable summary of the fetched story.

        Not a boolean assertion — always passes. Run with -s to see output.
        """
        print(f"\n{'═'*60}")
        print(f"  ADO Story #{story_context.id}")
        print(f"{'═'*60}")
        print(f"  Title      : {story_context.title}")
        print(f"  State      : {story_context.state}")
        print(f"  Type       : {story_context.type}")
        print(f"  Assignee   : {story_context.assignee or '(unassigned)'}")
        print(f"  Sprint     : {story_context.iteration_path}")
        print(f"  Area       : {story_context.area_path}")
        print(f"  Points     : {story_context.story_points}")
        print(f"  Priority   : {story_context.priority}")
        print(f"  Tags       : {story_context.tags}")
        print(f"  Parent ID  : {story_context.parent_id}")
        print(f"  Children   : {story_context.child_task_ids}")
        print(f"  Test Cases : {story_context.linked_test_case_ids}")
        print(f"  PR Links   : {story_context.linked_pr_ids}")
        print(f"  Created    : {story_context.created_at}")
        print(f"  Updated    : {story_context.updated_at}")
        print(f"  URL        : {story_context.url}")
        ac = story_context.acceptance_criteria
        if ac:
            preview = ac[:200].replace("\n", " ")
            print(f"  AC Preview : {preview}{'...' if len(ac) > 200 else ''}")
        print(f"{'═'*60}")
        assert True  # always passes
