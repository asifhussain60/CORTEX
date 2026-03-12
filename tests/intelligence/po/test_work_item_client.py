"""Tests — Work Item Integration Foundation (GAP-129-07)."""

from __future__ import annotations

import pytest

from cortex.intelligence.po.work_item_client import (
    ADOWorkItemAdapter,
    JiraWorkItemAdapter,
    WorkItemClient,
)


CANONICAL_KEYS = {"story_id", "title", "description", "status", "priority",
                  "story_points", "acceptance_criteria", "tags"}


# ─────────────────────────────────────────────────────────────────────────────
# WorkItemClient ABC contract
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkItemClientABC:
    """WorkItemClient is abstract — cannot be instantiated directly."""

    def test_is_abstract(self):
        with pytest.raises(TypeError):
            WorkItemClient()  # type: ignore[abstract]

    def test_abc_enforces_fetch_story(self):
        class BadAdapter(WorkItemClient):
            def search(self, query):
                return []
            def update_status(self, story_id, status):
                return True
        with pytest.raises(TypeError):
            BadAdapter()

    def test_abc_enforces_search(self):
        class BadAdapter(WorkItemClient):
            def fetch_story(self, story_id):
                return {}
            def update_status(self, story_id, status):
                return True
        with pytest.raises(TypeError):
            BadAdapter()

    def test_abc_enforces_update_status(self):
        class BadAdapter(WorkItemClient):
            def fetch_story(self, story_id):
                return {}
            def search(self, query):
                return []
        with pytest.raises(TypeError):
            BadAdapter()


# ─────────────────────────────────────────────────────────────────────────────
# ADOWorkItemAdapter
# ─────────────────────────────────────────────────────────────────────────────


class TestADOWorkItemAdapter:
    """ADO adapter maps ADO fields to canonical model."""

    @pytest.fixture
    def adapter(self):
        return ADOWorkItemAdapter()

    def test_is_work_item_client(self, adapter):
        assert isinstance(adapter, WorkItemClient)

    def test_fetch_story_returns_canonical_keys(self, adapter):
        result = adapter.fetch_story("123")
        assert CANONICAL_KEYS.issubset(result.keys())

    def test_fetch_story_story_id_matches(self, adapter):
        result = adapter.fetch_story("456")
        assert result["story_id"] == "456"

    def test_search_returns_list(self, adapter):
        result = adapter.search("test query")
        assert isinstance(result, list)

    def test_update_status_returns_bool(self, adapter):
        result = adapter.update_status("123", "Active")
        assert isinstance(result, bool)

    def test_to_canonical_maps_title(self):
        ado_item = {
            "id": "99",
            "fields": {
                "System.Title": "My Story",
                "System.State": "Active",
                "System.Description": "desc",
                "Microsoft.VSTS.Common.Priority": 1,
                "Microsoft.VSTS.Scheduling.StoryPoints": 5,
                "System.Tags": "backend",
            },
        }
        canonical = ADOWorkItemAdapter._to_canonical(ado_item)
        assert canonical["title"] == "My Story"
        assert canonical["status"] == "Active"
        assert canonical["story_points"] == 5
        assert canonical["tags"] == "backend"

    def test_to_canonical_missing_fields_uses_defaults(self):
        canonical = ADOWorkItemAdapter._to_canonical({"id": "1", "fields": {}})
        assert canonical["story_id"] == "1"
        assert canonical["status"] == "New"
        assert canonical["priority"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# JiraWorkItemAdapter
# ─────────────────────────────────────────────────────────────────────────────


class TestJiraWorkItemAdapter:
    """Jira adapter maps Jira issue fields to canonical model."""

    @pytest.fixture
    def adapter(self):
        return JiraWorkItemAdapter()

    def test_is_work_item_client(self, adapter):
        assert isinstance(adapter, WorkItemClient)

    def test_fetch_story_returns_canonical_keys(self, adapter):
        result = adapter.fetch_story("PROJ-42")
        assert CANONICAL_KEYS.issubset(result.keys())

    def test_fetch_story_story_id_matches(self, adapter):
        result = adapter.fetch_story("PROJ-42")
        assert result["story_id"] == "PROJ-42"

    def test_search_returns_list(self, adapter):
        result = adapter.search("component = auth")
        assert isinstance(result, list)

    def test_update_status_returns_bool(self, adapter):
        result = adapter.update_status("PROJ-42", "In Progress")
        assert isinstance(result, bool)

    def test_to_canonical_maps_summary(self):
        jira_issue = {
            "key": "PROJ-1",
            "fields": {
                "summary": "Login feature",
                "description": "As a user...",
                "status": {"name": "In Progress"},
                "priority": {"name": "High"},
                "story_points": 3,
                "labels": ["auth", "frontend"],
            },
        }
        canonical = JiraWorkItemAdapter._to_canonical(jira_issue)
        assert canonical["title"] == "Login feature"
        assert canonical["status"] == "In Progress"
        assert canonical["story_points"] == 3
        assert "auth" in canonical["tags"]

    def test_to_canonical_handles_missing_status_dict(self):
        jira_issue = {"key": "T-1", "fields": {"status": "Open"}}
        canonical = JiraWorkItemAdapter._to_canonical(jira_issue)
        assert canonical["status"] == "Open"
