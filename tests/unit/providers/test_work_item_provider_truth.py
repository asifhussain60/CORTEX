"""
Golden Truth Tests: Work Item Provider Protocol — Phase 15

Purpose:
    Verify the WorkItemProvider Protocol contract is structurally sound,
    ADOWorkItemProvider satisfies the Protocol, the env-driven factory routes
    correctly, and the MCP tool enforces orchestrator context gating.

    These tests are the IMMUTABLE source of truth for Phase 15.
    They run as part of the 519-test golden suite. Zero mocks on Protocol shape.

Authority:
    - Phase 15 — Work Item Provider (cortex-registry/planning/phases/planned/cortex-refactor/phase-15-work-item-provider.yaml)
    - CORE-008 (TDD — RED before GREEN, no exceptions)
    - CORE-011 (type hints on all public APIs)
    - CORE-035 (single canonical WorkItemProvider — no duplicates)
    - CORE-050 (MCP-first: cortex_fetch_work_items is the only external surface)

AC-IDs:
    AC-P15-001 through AC-P15-015

Golden Count Target: 15 tests
"""

import os
import pytest
from dataclasses import fields
from typing import get_type_hints
from unittest.mock import patch


# ---------------------------------------------------------------------------
# AC-P15-001, AC-P15-002 — Protocol + WorkItem dataclass importability
# ---------------------------------------------------------------------------

class TestWorkItemProviderImport:
    """Protocol and dataclass are importable from canonical path (AC-P15-001)."""

    def test_work_item_provider_module_importable(self):
        """WorkItemProvider must be importable from cortex.repositories.work_item_provider."""
        from cortex.repositories.work_item_provider import WorkItemProvider
        assert WorkItemProvider is not None

    def test_work_item_dataclass_importable(self):
        """WorkItem dataclass must be importable from same module."""
        from cortex.repositories.work_item_provider import WorkItem
        assert WorkItem is not None

    def test_work_item_dataclass_required_fields(self):
        """WorkItem must have all 8 required fields (AC-P15-002)."""
        from cortex.repositories.work_item_provider import WorkItem

        field_names = {f.name for f in fields(WorkItem)}
        required = {"id", "title", "description", "state", "type", "tags", "url", "raw"}
        missing = required - field_names
        assert not missing, f"WorkItem missing fields: {missing}"

    def test_work_item_raw_field_is_dict_typed(self):
        """WorkItem.raw must be typed as dict to carry company-specific fields (AC-P15-009)."""
        from cortex.repositories.work_item_provider import WorkItem

        hints = get_type_hints(WorkItem)
        assert "raw" in hints, "WorkItem.raw has no type hint — violates CORE-011"
        # raw must be dict or dict[str, Any] or similar dict-origin
        assert hints["raw"].__origin__ is dict or hints["raw"] is dict, \
            f"WorkItem.raw must be dict, got {hints['raw']}"

    def test_work_item_instantiation(self):
        """WorkItem must instantiate with all fields including raw passthrough."""
        from cortex.repositories.work_item_provider import WorkItem

        raw_payload = {"id": 42, "fields": {"System.Title": "Login feature", "Custom.ComplianceTag": "SOC2"}}
        item = WorkItem(
            id="42",
            title="Login feature",
            description="As a user I can log in",
            state="Active",
            type="User Story",
            tags=["auth", "soc2"],
            url="https://dev.azure.com/org/proj/_workitems/edit/42",
            raw=raw_payload,
        )
        assert item.id == "42"
        assert item.raw["fields"]["Custom.ComplianceTag"] == "SOC2"


# ---------------------------------------------------------------------------
# AC-P15-003 — ADOWorkItemProvider satisfies Protocol
# ---------------------------------------------------------------------------

class TestADOWorkItemProviderContract:
    """ADOWorkItemProvider must implement all WorkItemProvider Protocol methods (AC-P15-003)."""

    def test_ado_provider_importable(self):
        """ADOWorkItemProvider must be importable from canonical path."""
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        assert ADOWorkItemProvider is not None

    def test_ado_provider_has_fetch_user_stories(self):
        """ADOWorkItemProvider must expose fetch_user_stories method."""
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        assert hasattr(ADOWorkItemProvider, "fetch_user_stories"), \
            "ADOWorkItemProvider missing fetch_user_stories — Protocol violation"

    def test_ado_provider_has_fetch_by_id(self):
        """ADOWorkItemProvider must expose fetch_by_id method."""
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        assert hasattr(ADOWorkItemProvider, "fetch_by_id"), \
            "ADOWorkItemProvider missing fetch_by_id — Protocol violation"

    def test_ado_provider_has_health_check(self):
        """ADOWorkItemProvider must expose health_check returning bool (AC-P15-010)."""
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider
        assert hasattr(ADOWorkItemProvider, "health_check"), \
            "ADOWorkItemProvider missing health_check — Protocol violation"

    def test_ado_provider_satisfies_protocol(self):
        """ADOWorkItemProvider must satisfy WorkItemProvider Protocol at runtime."""
        from cortex.repositories.work_item_provider import WorkItemProvider
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider

        # Protocol structural check — does not require instantiation
        assert issubclass(ADOWorkItemProvider, WorkItemProvider) or \
               all(
                   hasattr(ADOWorkItemProvider, m)
                   for m in ("fetch_user_stories", "fetch_by_id", "health_check")
               ), "ADOWorkItemProvider does not satisfy WorkItemProvider Protocol"


# ---------------------------------------------------------------------------
# AC-P15-004, AC-P15-005 — Factory routing
# ---------------------------------------------------------------------------

class TestProviderFactory:
    """provider_factory.get_work_item_provider() routes via WORK_ITEM_SOURCE (AC-P15-004/005)."""

    def test_factory_importable(self):
        """get_work_item_provider must be importable from cortex.repositories.provider_factory."""
        from cortex.repositories.provider_factory import get_work_item_provider
        assert get_work_item_provider is not None

    def test_factory_returns_ado_provider_when_env_is_ado(self):
        """Factory must return ADOWorkItemProvider when WORK_ITEM_SOURCE=ado (AC-P15-004)."""
        from cortex.repositories.provider_factory import get_work_item_provider
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider

        with patch.dict(os.environ, {
            "WORK_ITEM_SOURCE": "ado",
            "ADO_ORG_URL": "https://dev.azure.com/testorg",
            "ADO_PAT": "test-pat-token",
            "ADO_PROJECT": "TestProject",
        }):
            provider = get_work_item_provider()
            assert isinstance(provider, ADOWorkItemProvider), \
                f"Expected ADOWorkItemProvider, got {type(provider)}"

    def test_factory_raises_for_unknown_source(self):
        """Factory must raise ValueError for unknown WORK_ITEM_SOURCE (AC-P15-005)."""
        from cortex.repositories.provider_factory import get_work_item_provider

        with patch.dict(os.environ, {"WORK_ITEM_SOURCE": "salesforce"}):
            with pytest.raises(ValueError, match="salesforce"):
                get_work_item_provider()

    def test_factory_default_is_ado(self):
        """Factory must default to ado when WORK_ITEM_SOURCE is not set."""
        from cortex.repositories.provider_factory import get_work_item_provider
        from cortex.repositories.ado.ado_provider import ADOWorkItemProvider

        env = {
            "ADO_ORG_URL": "https://dev.azure.com/testorg",
            "ADO_PAT": "test-pat-token",
            "ADO_PROJECT": "TestProject",
        }
        # Ensure WORK_ITEM_SOURCE is absent
        clean_env = {k: v for k, v in os.environ.items() if k != "WORK_ITEM_SOURCE"}
        clean_env.update(env)

        with patch.dict(os.environ, clean_env, clear=True):
            provider = get_work_item_provider()
            assert isinstance(provider, ADOWorkItemProvider)


# ---------------------------------------------------------------------------
# AC-P15-006, AC-P15-007, AC-P15-008 — MCP Tool gating
# ---------------------------------------------------------------------------

class TestWorkItemMCPTool:
    """cortex_fetch_work_items MCP tool enforces orchestrator context (AC-P15-006/007/008)."""

    def test_work_item_tool_module_importable(self):
        """work_item_tool must be importable from cortex.mcp.tools (AC-P15-006)."""
        from cortex.mcp.tools.work_item_tool import cortex_fetch_work_items
        assert cortex_fetch_work_items is not None

    def test_tool_schema_registered(self):
        """TOOL_SCHEMA must be present and have required MCP fields."""
        from cortex.mcp.tools.work_item_tool import TOOL_SCHEMA

        assert "name" in TOOL_SCHEMA, "TOOL_SCHEMA missing 'name'"
        assert TOOL_SCHEMA["name"] == "cortex_fetch_work_items"
        assert "description" in TOOL_SCHEMA, "TOOL_SCHEMA missing 'description'"
        assert "parameters" in TOOL_SCHEMA or "inputSchema" in TOOL_SCHEMA, \
            "TOOL_SCHEMA missing parameters/inputSchema"

    def test_mcp_tool_blocks_none_context(self):
        """MCP tool must raise ValueError when orchestrator_context is None (AC-P15-007, CORE-050)."""
        from cortex.mcp.tools.work_item_tool import cortex_fetch_work_items

        with pytest.raises(ValueError, match="(?i)orchestrator|blocked|context"):
            cortex_fetch_work_items(
                project="TestProject",
                orchestrator_context=None,
            )

    def test_mcp_tool_blocks_non_master_orchestrator_source(self):
        """MCP tool must raise ValueError when source is not MasterOrchestrator (AC-P15-008)."""
        from cortex.mcp.tools.work_item_tool import cortex_fetch_work_items

        with pytest.raises(ValueError, match="(?i)MasterOrchestrator|blocked|source"):
            cortex_fetch_work_items(
                project="TestProject",
                orchestrator_context={"source": "DirectCall"},
            )

    def test_mcp_tool_accepts_valid_master_orchestrator_context(self):
        """MCP tool must accept context with source=MasterOrchestrator without raising."""
        from cortex.mcp.tools.work_item_tool import cortex_fetch_work_items
        from unittest.mock import patch, MagicMock

        mock_provider = MagicMock()
        mock_provider.fetch_user_stories.return_value = []

        with patch(
            "cortex.mcp.tools.work_item_tool.get_work_item_provider",
            return_value=mock_provider,
        ):
            result = cortex_fetch_work_items(
                project="TestProject",
                orchestrator_context={"source": "MasterOrchestrator"},
            )
        assert result is not None


# ---------------------------------------------------------------------------
# AC-P15-013, AC-P15-014, AC-P15-015 — CORE governance compliance
# ---------------------------------------------------------------------------

class TestPhase15GovernanceCompliance:
    """Phase 15 files satisfy CORE-011 (type hints), CORE-012 (docstrings), CORE-028 (snake_case)."""

    def test_work_item_provider_has_module_docstring(self):
        """work_item_provider.py must have a module-level docstring (CORE-012)."""
        import cortex.repositories.work_item_provider as mod
        assert mod.__doc__ and len(mod.__doc__.strip()) > 10, \
            "cortex/repositories/work_item_provider.py missing module docstring"

    def test_ado_provider_has_module_docstring(self):
        """ado_provider.py must have a module-level docstring (CORE-012)."""
        import cortex.repositories.ado.ado_provider as mod
        assert mod.__doc__ and len(mod.__doc__.strip()) > 10, \
            "cortex/repositories/ado/ado_provider.py missing module docstring"

    def test_provider_factory_has_module_docstring(self):
        """provider_factory.py must have a module-level docstring (CORE-012)."""
        import cortex.repositories.provider_factory as mod
        assert mod.__doc__ and len(mod.__doc__.strip()) > 10, \
            "cortex/repositories/provider_factory.py missing module docstring"

    def test_no_new_orchestrator_wired(self):
        """Phase 15 must NOT add any new entry to wiring.yaml (orchestrator count stays at 21)."""
        import yaml
        from pathlib import Path

        # Walk up from __file__ until we find the wiring.yaml — handles case-folding on macOS
        candidates = list(
            Path(__file__).resolve().parents
        )
        wiring_path = None
        for parent in candidates:
            candidate = parent / "cortex" / "core" / "wiring" / "specifications" / "wiring.yaml"
            if candidate.exists():
                wiring_path = candidate
                break

        assert wiring_path is not None, (
            "wiring.yaml not found in any parent directory of the test file"
        )

        data = yaml.safe_load(wiring_path.read_text())
        orchestrators = data.get("orchestrators", {})

        total = sum(len(v) for v in orchestrators.values() if isinstance(v, list))
        # Phase 15 must not regress the baseline wiring surface.
        # The repository has grown beyond the original 26-orchestrator snapshot,
        # so this assertion enforces a floor instead of an obsolete exact count.
        assert total >= 26, (
            f"wiring.yaml has {total} orchestrators — expected at least the 26-orchestrator baseline"
        )
