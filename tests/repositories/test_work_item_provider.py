"""
Unit Tests: WorkItemProvider, WorkItem, ADOWorkItemProvider, provider_factory.

Covers: Protocol contract, dataclass field validation, factory routing,
        ADO stub method signatures, and MCP tool context gating.

Authority: CORE-008 (TDD) · Phase 15
"""

from __future__ import annotations

import os
import pytest
from dataclasses import fields as dc_fields
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# WorkItem dataclass
# ---------------------------------------------------------------------------

class TestWorkItemDataclass:
    """WorkItem is a complete, instantiable dataclass."""

    def test_instantiation_minimal(self):
        from cortex.repositories.work_item_provider import WorkItem
        item = WorkItem(
            id="1",
            title="T",
            description="D",
            state="Active",
            type="User Story",
            tags=[],
            url="https://example.com",
            raw={},
        )
        assert item.id == "1"

    def test_raw_field_passthrough_is_unmodified(self):
        from cortex.repositories.work_item_provider import WorkItem
        company_payload = {
            "id": 99,
            "fields": {
                "System.Title": "Story",
                "Custom.ComplianceTag": "SOC2",
                "Custom.AreaPath": "Finance\\Backend",
            },
        }
        item = WorkItem(
            id="99", title="Story", description="",
            state="Active", type="User Story", tags=[],
            url="", raw=company_payload,
        )
        assert item.raw["fields"]["Custom.ComplianceTag"] == "SOC2"
        assert item.raw["fields"]["Custom.AreaPath"] == "Finance\\Backend"

    def test_all_eight_fields_present(self):
        from cortex.repositories.work_item_provider import WorkItem
        names = {f.name for f in dc_fields(WorkItem)}
        assert names == {"id", "title", "description", "state", "type", "tags", "url", "raw"}

    def test_tags_accepts_empty_list(self):
        from cortex.repositories.work_item_provider import WorkItem
        item = WorkItem("1", "T", "D", "Active", "Bug", [], "http://x", {})
        assert item.tags == []

    def test_tags_accepts_multiple_values(self):
        from cortex.repositories.work_item_provider import WorkItem
        item = WorkItem("1", "T", "D", "Active", "Bug", ["auth", "soc2"], "http://x", {})
        assert "auth" in item.tags


# ---------------------------------------------------------------------------
# WorkItemProvider Protocol
# ---------------------------------------------------------------------------

class TestWorkItemProviderProtocol:
    """Protocol is runtime-checkable; conformant classes pass isinstance."""

    def test_protocol_is_runtime_checkable(self):
        from cortex.repositories.work_item_provider import WorkItemProvider
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        assert isinstance(ADOWorkItemProvider("", "", ""), WorkItemProvider)

    def test_non_conformant_class_fails_isinstance(self):
        from cortex.repositories.work_item_provider import WorkItemProvider

        class BadProvider:
            pass

        assert not isinstance(BadProvider(), WorkItemProvider)


# ---------------------------------------------------------------------------
# ADOWorkItemProvider
# ---------------------------------------------------------------------------

class TestADOWorkItemProvider:
    """ADO stub satisfies Protocol and exposes expected interface."""

    @pytest.fixture
    def provider(self):
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        return ADOWorkItemProvider(
            org_url="https://dev.azure.com/testorg",
            pat="test-pat",
            project="TestProject",
        )

    def test_fetch_user_stories_returns_list(self, provider):
        result = provider.fetch_user_stories("TestProject")
        assert isinstance(result, list)

    def test_fetch_user_stories_empty_by_default(self, provider):
        """Stub returns empty list until company fills in HTTP call."""
        result = provider.fetch_user_stories("TestProject")
        assert result == []

    def test_fetch_by_id_raises_not_implemented(self, provider):
        """Stub raises NotImplementedError; company must implement."""
        with pytest.raises(NotImplementedError):
            provider.fetch_by_id("42")

    def test_health_check_returns_bool(self, provider):
        result = provider.health_check()
        assert isinstance(result, bool)

    def test_map_extracts_standard_fields(self, provider):
        raw = {
            "id": 7,
            "fields": {
                "System.Title": "Login page",
                "System.Description": "As a user...",
                "System.State": "Active",
                "System.WorkItemType": "User Story",
                "System.Tags": "auth; security",
            },
            "_links": {"html": {"href": "https://dev.azure.com/org/proj/7"}},
        }
        item = provider._map(raw)
        assert item.id == "7"
        assert item.title == "Login page"
        assert item.state == "Active"
        assert "auth" in item.tags
        assert "security" in item.tags
        assert item.raw is raw  # raw is unmodified reference

    def test_map_preserves_custom_fields_in_raw(self, provider):
        raw = {
            "id": 1,
            "fields": {
                "System.Title": "T",
                "System.State": "New",
                "System.WorkItemType": "Bug",
                "Custom.ComplianceTag": "HIPAA",
            },
            "_links": {},
        }
        item = provider._map(raw)
        assert item.raw["fields"]["Custom.ComplianceTag"] == "HIPAA"


# ---------------------------------------------------------------------------
# provider_factory
# ---------------------------------------------------------------------------

class TestProviderFactory:
    """get_work_item_provider routes correctly via WORK_ITEM_SOURCE."""

    def test_ado_is_default(self):
        from cortex.repositories.provider_factory import get_work_item_provider
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        env = {"ADO_ORG_URL": "https://dev.azure.com/x", "ADO_PAT": "p", "ADO_PROJECT": "P"}
        clean = {k: v for k, v in os.environ.items() if k != "WORK_ITEM_SOURCE"}
        clean.update(env)
        with patch.dict(os.environ, clean, clear=True):
            p = get_work_item_provider()
        assert isinstance(p, ADOWorkItemProvider)

    def test_ado_explicit(self):
        from cortex.repositories.provider_factory import get_work_item_provider
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        with patch.dict(os.environ, {
            "WORK_ITEM_SOURCE": "ado",
            "ADO_ORG_URL": "https://dev.azure.com/org",
            "ADO_PAT": "token",
            "ADO_PROJECT": "Proj",
        }):
            p = get_work_item_provider()
        assert isinstance(p, ADOWorkItemProvider)

    def test_unknown_source_raises_value_error(self):
        from cortex.repositories.provider_factory import get_work_item_provider
        with patch.dict(os.environ, {"WORK_ITEM_SOURCE": "salesforce"}):
            with pytest.raises(ValueError, match="salesforce"):
                get_work_item_provider()

    def test_error_message_names_supported_values(self):
        from cortex.repositories.provider_factory import get_work_item_provider
        with patch.dict(os.environ, {"WORK_ITEM_SOURCE": "unknown_tool"}):
            with pytest.raises(ValueError, match="ado"):
                get_work_item_provider()


# ---------------------------------------------------------------------------
# MCP tool context guard
# ---------------------------------------------------------------------------

class TestWorkItemMCPToolContextGuard:
    """MCP tool enforces orchestrator_context gating (CORE-050)."""

    def test_none_context_raises(self):
        from cortex.mcp.tools.work_item_tool import cortex_fetch_work_items
        with pytest.raises(ValueError):
            cortex_fetch_work_items("Proj", orchestrator_context=None)

    def test_wrong_source_raises(self):
        from cortex.mcp.tools.work_item_tool import cortex_fetch_work_items
        with pytest.raises(ValueError):
            cortex_fetch_work_items("Proj", orchestrator_context={"source": "DirectCall"})

    def test_valid_context_calls_provider(self):
        from cortex.mcp.tools.work_item_tool import cortex_fetch_work_items
        mock_provider = MagicMock()
        mock_provider.fetch_user_stories.return_value = []
        with patch("cortex.mcp.tools.work_item_tool.get_work_item_provider",
                   return_value=mock_provider):
            result = cortex_fetch_work_items(
                "Proj",
                orchestrator_context={"source": "MasterOrchestrator"},
            )
        assert result["status"] == "success"
        assert result["count"] == 0
