"""
Golden Truth Tests: ADO Provider Layer
══════════════════════════════════════════════════════════════════════════════

Purpose:
    Verify ADOWorkItemProvider satisfies the WorkItemProvider Protocol,
    UserStoryContext carries all required fields, field mapping is correct,
    and authentication headers are correctly encoded.

    These tests cover Layer 1 of the ADO integration.
    ALL 15 TESTS MUST FAIL (RED) before implementation begins (CORE-008).

Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-035 (single canonical)
Phase: Phase 15 — Work Item Provider (ADO implementation)

AC-IDs: AC-ADO-P-001 through AC-ADO-P-015
Golden count target: 15 tests
"""

from __future__ import annotations

import base64
from dataclasses import fields
from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-P-001, AC-ADO-P-002 — Importability from canonical paths
# ──────────────────────────────────────────────────────────────────────────────

class TestADOProviderImport:
    """Layer 1 imports must resolve from canonical cortex.repositories.ado paths."""

    def test_ado_provider_importable_from_canonical_path(self):
        """
        AC-ADO-P-001: ADOWorkItemProvider must import from cortex.repositories.ado.ado_provider.

        RED: ImportError if module not created.
        GREEN: Module exists and class is present.
        """
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        assert ADOWorkItemProvider is not None

    def test_user_story_context_importable_from_canonical_path(self):
        """
        AC-ADO-P-002: UserStoryContext must import from cortex.repositories.ado.ado_provider.

        RED: ImportError if dataclass not defined.
        GREEN: Dataclass exists with correct module path.
        """
        from cortex.repositories.ado.ado_provider import UserStoryContext
        assert UserStoryContext is not None


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-P-003 — UserStoryContext field completeness
# ──────────────────────────────────────────────────────────────────────────────

class TestUserStoryContextShape:
    """UserStoryContext must have all 18 required fields for full story context."""

    def test_user_story_context_has_all_required_fields(self):
        """
        AC-ADO-P-003: UserStoryContext must carry all core + ADO-specific fields.

        RED: Missing fields if dataclass definition is incomplete.
        GREEN: All 18 fields present.
        """
        from cortex.repositories.ado.ado_provider import UserStoryContext

        field_names = {f.name for f in fields(UserStoryContext)}
        required = {
            # Core (WorkItem-compatible)
            "id", "title", "description", "state", "type",
            "tags", "url", "raw",
            # ADO-specific enrichment
            "assignee", "story_points", "priority", "acceptance_criteria",
            "area_path", "iteration_path", "created_at", "updated_at",
            "parent_id", "child_task_ids", "linked_test_case_ids", "linked_pr_ids",
        }
        missing = required - field_names
        assert not missing, (
            f"UserStoryContext missing fields: {missing}\n"
            f"Present fields: {field_names}"
        )

    def test_user_story_context_child_task_ids_defaults_to_empty_list(self):
        """
        AC-ADO-P-004: child_task_ids must default to [] — never None.

        RED: AttributeError or default=None if field not correctly defined.
        GREEN: Default factory produces empty list.
        """
        from cortex.repositories.ado.ado_provider import UserStoryContext

        ctx = UserStoryContext(
            id="1", title="t", description="d", state="s", type="User Story",
            tags=[], url="https://example.com", raw={}
        )
        assert ctx.child_task_ids == []
        assert ctx.linked_test_case_ids == []
        assert ctx.linked_pr_ids == []

    def test_user_story_context_to_work_item_returns_work_item(self):
        """
        AC-ADO-P-005: to_work_item() must return a valid WorkItem.

        RED: AttributeError if method not implemented.
        GREEN: Returns WorkItem with matching id and title.
        """
        from cortex.repositories.ado.ado_provider import UserStoryContext
        from cortex.repositories.work_item_provider import WorkItem

        ctx = UserStoryContext(
            id="42", title="Test story", description="desc", state="Active",
            type="User Story", tags=["auth"], url="https://dev.azure.com/org/proj/_workitems/edit/42",
            raw={"id": 42, "fields": {}}
        )
        wi = ctx.to_work_item()
        assert isinstance(wi, WorkItem)
        assert wi.id == "42"
        assert wi.title == "Test story"


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-P-006 — Protocol satisfaction
# ──────────────────────────────────────────────────────────────────────────────

class TestADOProviderProtocol:
    """ADOWorkItemProvider must satisfy WorkItemProvider protocol (no isinstance hack)."""

    def test_provider_satisfies_work_item_provider_protocol(self):
        """
        AC-ADO-P-006: ADOWorkItemProvider must satisfy the WorkItemProvider Protocol.

        RED: isinstance check fails if methods are missing or wrongly typed.
        GREEN: Protocol runtime check passes.
        """
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        from cortex.repositories.work_item_provider import WorkItemProvider

        provider = ADOWorkItemProvider(
            org_url="https://dev.azure.com/HQY01",
            pat="test-pat",
            project="V5",
        )
        assert isinstance(provider, WorkItemProvider), (
            "ADOWorkItemProvider does not satisfy WorkItemProvider Protocol. "
            "Ensure fetch_user_stories, fetch_by_id, and health_check are all present."
        )


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-P-007, AC-ADO-P-008 — Auth header encoding
# ──────────────────────────────────────────────────────────────────────────────

class TestADOProviderAuth:
    """Auth headers must use the same PAT Basic encoding as QEMetricsCollection."""

    def test_auth_header_uses_pat_basic_encoding(self, ado_provider):
        """
        AC-ADO-P-007: Authorization header must be Basic base64(":<PAT>").

        RED: AttributeError if _auth_headers not implemented.
        GREEN: Header exactly matches expected encoding.
        """
        headers = ado_provider._auth_headers()
        pat = "test-pat-golden-suite"
        expected_token = base64.b64encode(f":{pat}".encode()).decode()
        assert headers["Authorization"] == f"Basic {expected_token}", (
            "ADO auth encoding mismatch. Must encode ':<PAT>' (empty username) "
            "to match QEMetricsCollection's btoa(':' + token) pattern."
        )

    def test_auth_header_empty_pat_produces_valid_base64(self):
        """
        AC-ADO-P-008: Empty PAT must still produce valid base64 (not crash).

        RED: Exception if _auth_headers doesn't handle empty PAT.
        GREEN: Returns Authorization header with base64(':').
        """
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider

        provider = ADOWorkItemProvider(org_url="https://dev.azure.com/HQY01", pat="", project="V5")
        headers = provider._auth_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")


# ──────────────────────────────────────────────────────────────────────────────
# AC-ADO-P-009 through AC-ADO-P-012 — _map and _map_to_context correctness
# ──────────────────────────────────────────────────────────────────────────────

class TestADOFieldMapping:
    """Field mapping must extract all values correctly from raw ADO API payloads."""

    def test_map_extracts_title_and_state_from_fields(self, ado_provider, raw_story_692945):
        """
        AC-ADO-P-009: _map() must extract title and state from fields dict.

        RED: Returns empty strings if field constants are wrong.
        GREEN: title == expected title, state == "Active".
        """
        wi = ado_provider._map(raw_story_692945)
        assert wi.title == "User can reset password via email"
        assert wi.state == "Active"
        assert wi.id == "692945"

    def test_map_extracts_tags_from_semicolon_delimited_string(self, ado_provider, raw_story_692945):
        """
        AC-ADO-P-010: _map() must split semicolon-delimited tags into a list.

        RED: Returns ["auth; security; password-reset"] as single element.
        GREEN: Returns ["auth", "security", "password-reset"] (3 elements, stripped).
        """
        wi = ado_provider._map(raw_story_692945)
        assert "auth" in wi.tags
        assert "security" in wi.tags
        assert "password-reset" in wi.tags
        assert all(";" not in tag for tag in wi.tags), "Tags must not contain semicolons"

    def test_map_to_context_extracts_parent_id_from_relations(self, ado_provider, raw_story_692945):
        """
        AC-ADO-P-011: _map_to_context() must extract parent_id from Hierarchy-Reverse relation.

        RED: parent_id=None if relation parsing is not implemented.
        GREEN: parent_id == 689000.
        """
        ctx = ado_provider._map_to_context(raw_story_692945)
        assert ctx.parent_id == 689000, (
            f"Expected parent_id=689000, got {ctx.parent_id}. "
            f"Check REL_PARENT constant and URL integer extraction."
        )

    def test_map_to_context_extracts_child_task_ids(self, ado_provider, raw_story_692945):
        """
        AC-ADO-P-012: _map_to_context() must extract child_task_ids from Hierarchy-Forward relations.

        RED: child_task_ids=[] if relation parsing is not implemented.
        GREEN: child_task_ids == [692946, 692947].
        """
        ctx = ado_provider._map_to_context(raw_story_692945)
        assert 692946 in ctx.child_task_ids
        assert 692947 in ctx.child_task_ids
        assert len(ctx.child_task_ids) == 2

    def test_map_to_context_extracts_linked_test_case_ids(self, ado_provider, raw_story_692945):
        """
        AC-ADO-P-013: _map_to_context() must extract linked_test_case_ids from TestedBy-Forward.

        RED: linked_test_case_ids=[] if TestedBy relation not parsed.
        GREEN: linked_test_case_ids == [700100, 700101].
        """
        ctx = ado_provider._map_to_context(raw_story_692945)
        assert 700100 in ctx.linked_test_case_ids
        assert 700101 in ctx.linked_test_case_ids
        assert len(ctx.linked_test_case_ids) == 2

    def test_map_to_context_extracts_assignee_display_name(self, ado_provider, raw_story_692945):
        """
        AC-ADO-P-014: _map_to_context() must extract assignee.displayName from the nested object.

        RED: assignee=None or assignee="..." the dict if not dereferenced.
        GREEN: assignee == "Jane Doe".

        IMPORTANT: ADO returns AssignedTo as a dict, not a string.
        """
        ctx = ado_provider._map_to_context(raw_story_692945)
        assert ctx.assignee == "Jane Doe", (
            f"Expected assignee='Jane Doe', got {ctx.assignee!r}. "
            f"Check that _map_to_context reads .displayName from the AssignedTo dict."
        )

    def test_map_to_context_parses_iso_datetime_created_date(self, ado_provider, raw_story_692945):
        """
        AC-ADO-P-015: _map_to_context() must parse CreatedDate as datetime object.

        RED: created_at=None or created_at as raw string.
        GREEN: created_at is a datetime with year 2026.
        """
        from datetime import datetime
        ctx = ado_provider._map_to_context(raw_story_692945)
        assert isinstance(ctx.created_at, datetime), (
            f"Expected created_at to be datetime, got {type(ctx.created_at)}"
        )
        assert ctx.created_at.year == 2026
