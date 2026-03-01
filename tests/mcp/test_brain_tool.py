"""
Phase 66-A RED tests — GAP-66-002: CortexBrainQuery MCP tool registration.

TDD-66-A-002: cortex_brain_query must be in ALL_TOOLS and return T1/T2/T3 memories.

Author: Asif Hussain
Phase: 66-A
Sweep: SWEEP-66-INTELLIGENCE-MATRIX
"""

import pytest
from typing import Any

# AC_START: AC-66-A-002-CORTEX-BRAIN-QUERY-MCP-TOOL-20260224T000000Z


class TestCortexBrainQueryExists:
    """GAP-66-002: CortexBrainQuery MCP tool must be importable and registered."""

    def test_brain_tool_module_importable(self) -> None:
        """cortex.mcp.tools.brain must import without error."""
        from cortex.mcp.tools.brain import CortexBrainQuery  # noqa: F401

    def test_cortex_brain_query_registered_in_all_tools(self) -> None:
        """CortexBrainQuery must appear in ALL_TOOLS list."""
        from cortex.mcp.tools import ALL_TOOLS
        from cortex.mcp.tools.brain import CortexBrainQuery

        assert CortexBrainQuery in ALL_TOOLS, (
            "CortexBrainQuery must be registered in ALL_TOOLS (GAP-66-002). "
            "Add it to the Intelligence section in cortex/mcp/tools/__init__.py"
        )

    def test_brain_query_is_consolidated_tool(self) -> None:
        """CortexBrainQuery must extend ConsolidatedTool."""
        from cortex.mcp.tools.brain import CortexBrainQuery
        from cortex.mcp.mcp_tool_base import ConsolidatedTool

        assert issubclass(CortexBrainQuery, ConsolidatedTool), (
            "CortexBrainQuery must extend ConsolidatedTool for multi-op support"
        )

    def test_brain_query_definition_has_name(self) -> None:
        """CortexBrainQuery.definition must have name='cortex_brain_query'."""
        from cortex.mcp.tools.brain import CortexBrainQuery

        tool = CortexBrainQuery()
        assert tool.definition.name == "cortex_brain_query", (
            f"CortexBrainQuery.definition.name must be 'cortex_brain_query', "
            f"got '{tool.definition.name}'"
        )

    def test_brain_query_supports_query_operation(self) -> None:
        """CortexBrainQuery must support op='query' returning brain tier memories."""
        from cortex.mcp.tools.brain import CortexBrainQuery
        from cortex.mcp.mcp_tool_base import ToolResult

        tool = CortexBrainQuery()
        result = tool.execute(op="query", tier="T1")

        assert isinstance(result, ToolResult), "execute() must return ToolResult"
        assert result.success is True, f"op=query must succeed, got: {result.error}"
        assert result.data is not None, "op=query must return non-None data"

    def test_brain_query_supports_all_tiers(self) -> None:
        """CortexBrainQuery must handle T1, T2, T3 tier queries."""
        from cortex.mcp.tools.brain import CortexBrainQuery

        tool = CortexBrainQuery()
        for tier in ("T1", "T2", "T3"):
            result = tool.execute(op="query", tier=tier)
            assert result.success is True, (
                f"Brain query tier={tier} must succeed, got: {result.error}"
            )

    def test_expected_tool_count_updated(self) -> None:
        """test_mcp_schema_fix._EXPECTED_TOOL_COUNT must reflect CortexBrainQuery addition."""
        from cortex.mcp.tools import ALL_TOOLS
        from cortex.mcp.tools.brain import CortexBrainQuery

        assert CortexBrainQuery in ALL_TOOLS, (
            "CortexBrainQuery must be in ALL_TOOLS — update _EXPECTED_TOOL_COUNT in "
            "tests/mcp/test_mcp_schema_fix.py to match."
        )
        # WAVE-101 consolidation: CortexProcessRequest (deprecated) removed from ALL_TOOLS.
        # CortexIntelligenceMatrix restored — supported_operations abstract method now implemented.
        # Net count: 39 → 37 → 38 (Matrix restored).
        assert len(ALL_TOOLS) == 38, (
            f"ALL_TOOLS must have 38 tools after CortexIntelligenceMatrix restoration, got {len(ALL_TOOLS)}. "
            "Update this count if further tools are added/removed."
        )


# AC_COMPLETE: AC-66-A-002-CORTEX-BRAIN-QUERY-MCP-TOOL-20260224T000000Z ✅
