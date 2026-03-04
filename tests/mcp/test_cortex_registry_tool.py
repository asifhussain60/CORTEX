"""
Phase 123 — Registry Intelligence Engine
TDD Tests for CortexRegistry MCP tool (GAP-123-06).

Validates:
  - Tool name and category registration
  - All 5 ops: query_governance, query_workflows, query_patterns, query_plans, registry_index
  - Invalid op returns error ToolResult
  - validate_orchestrator_context guard applied correctly

CORE Rules: CORE-008 (TDD-first), CORE-011, CORE-012, CORE-035
AC_START: AC-123-REGISTRY-INTELLIGENCE-ENGINE
"""
from __future__ import annotations

import asyncio
import pytest


class TestCortexRegistryToolMeta:
    """Tests for CortexRegistry tool metadata and registration."""

    def test_cortex_registry_tool_name(self):
        """CortexRegistry().name must equal 'cortex_registry'."""
        from cortex.mcp.tools.cortex_registry_tool import CortexRegistry
        tool = CortexRegistry()
        assert tool.name == "cortex_registry", (
            f"Expected tool name 'cortex_registry', got '{tool.name}'"
        )

    def test_cortex_registry_tool_importable(self):
        """cortex_registry_tool module must be importable without error."""
        from cortex.mcp.tools import cortex_registry_tool  # noqa: F401

    def test_cortex_registry_tool_is_consolidated_tool(self):
        """CortexRegistry must subclass ConsolidatedTool."""
        from cortex.mcp.tools.cortex_registry_tool import CortexRegistry
        from cortex.mcp.mcp_tool_base import ConsolidatedTool
        assert issubclass(CortexRegistry, ConsolidatedTool), (
            "CortexRegistry must subclass ConsolidatedTool"
        )

    def test_cortex_registry_registered_in_mcp_registry(self):
        """'cortex_registry' must appear in PRODUCTION_TOOLS dict in mcp_registry.py."""
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        assert "cortex_registry" in PRODUCTION_TOOLS, (
            "cortex_registry not found in PRODUCTION_TOOLS — add thin entry to mcp_registry.py"
        )

    def test_cortex_registry_in_all_tools(self):
        """CortexRegistry must be in ALL_TOOLS list in cortex/mcp/tools/__init__.py."""
        from cortex.mcp.tools import ALL_TOOLS
        from cortex.mcp.tools.cortex_registry_tool import CortexRegistry
        tool_names = [t.__name__ if hasattr(t, "__name__") else str(t) for t in ALL_TOOLS]
        assert "CortexRegistry" in tool_names, (
            f"CortexRegistry not found in ALL_TOOLS. Tools: {tool_names}"
        )


class TestCortexRegistryToolOps:
    """Tests for CortexRegistry tool operation dispatch."""

    def _run_op(self, op: str, **kwargs):
        """Helper: instantiate tool and execute an op (sync wrapper for async execute)."""
        from cortex.mcp.tools.cortex_registry_tool import CortexRegistry
        tool = CortexRegistry()
        params = {"op": op, **kwargs}
        return asyncio.run(tool.execute(params=params, orchestrator_context=None))

    def test_op_query_governance_returns_rules_key(self):
        """op='query_governance' must return a result with 'rules' key."""
        result = self._run_op("query_governance")
        assert not result.is_error, f"Expected success, got error: {result.content}"
        assert "rules" in result.content, (
            f"Expected 'rules' key in result.content, got keys: {list(result.content.keys())}"
        )

    def test_op_query_governance_rules_is_list(self):
        """op='query_governance' result['rules'] must be a list."""
        result = self._run_op("query_governance")
        assert isinstance(result.content["rules"], list), (
            f"Expected list, got {type(result.content['rules'])}"
        )

    def test_op_query_workflows_returns_templates_key(self):
        """op='query_workflows' must return a result with 'templates' key."""
        result = self._run_op("query_workflows")
        assert not result.is_error, f"Expected success, got error: {result.content}"
        assert "templates" in result.content, (
            f"Expected 'templates' key, got keys: {list(result.content.keys())}"
        )

    def test_op_query_workflows_templates_is_list(self):
        """op='query_workflows' result['templates'] must be a list."""
        result = self._run_op("query_workflows")
        assert isinstance(result.content["templates"], list), (
            f"Expected list, got {type(result.content['templates'])}"
        )

    def test_op_query_patterns_returns_patterns_key(self):
        """op='query_patterns' must return a result with 'patterns' key."""
        result = self._run_op("query_patterns")
        assert not result.is_error, f"Expected success, got error: {result.content}"
        assert "patterns" in result.content, (
            f"Expected 'patterns' key, got keys: {list(result.content.keys())}"
        )

    def test_op_query_patterns_patterns_is_list(self):
        """op='query_patterns' result['patterns'] must be a list."""
        result = self._run_op("query_patterns")
        assert isinstance(result.content["patterns"], list), (
            f"Expected list, got {type(result.content['patterns'])}"
        )

    def test_op_query_plans_returns_phases_key(self):
        """op='query_plans' must return a result with 'phases' key."""
        result = self._run_op("query_plans")
        assert not result.is_error, f"Expected success, got error: {result.content}"
        assert "phases" in result.content, (
            f"Expected 'phases' key, got keys: {list(result.content.keys())}"
        )

    def test_op_query_plans_phases_is_list(self):
        """op='query_plans' result['phases'] must be a list."""
        result = self._run_op("query_plans")
        assert isinstance(result.content["phases"], list), (
            f"Expected list, got {type(result.content['phases'])}"
        )

    def test_op_registry_index_returns_entries_key(self):
        """op='registry_index' must return a result with 'entries' key."""
        result = self._run_op("registry_index")
        assert not result.is_error, f"Expected success, got error: {result.content}"
        assert "entries" in result.content, (
            f"Expected 'entries' key, got keys: {list(result.content.keys())}"
        )

    def test_op_registry_index_entries_is_list(self):
        """op='registry_index' result['entries'] must be a non-empty list."""
        result = self._run_op("registry_index")
        assert isinstance(result.content["entries"], list), (
            f"Expected list, got {type(result.content['entries'])}"
        )
        assert len(result.content["entries"]) > 0, (
            "registry_index must return at least 1 entry"
        )

    def test_invalid_op_returns_error(self):
        """op='unknown_op' must return a ToolResult with is_error=True."""
        result = self._run_op("unknown_op")
        assert result.is_error, (
            f"Expected error ToolResult for unknown op, got success: {result.content}"
        )

    def test_validate_context_guard_allows_none_context(self):
        """orchestrator_context=None must not raise — test invocation must be safe."""
        from cortex.mcp.tools.cortex_registry_tool import CortexRegistry
        tool = CortexRegistry()
        # Must not raise even with orchestrator_context=None
        result = asyncio.run(tool.execute(
            params={"op": "query_governance"},
            orchestrator_context=None,
        ))
        assert result is not None, "execute() must return a ToolResult"
