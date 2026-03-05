"""
Sub-phase 129-c RED tests — CortexDistill MCP tool.

TDD contract (CORE-008): tests MUST fail before implementation.
Run RED gate:  python3 -m pytest tests/mcp/test_cortex_distill_tool.py -v
Run GREEN gate: same after creating cortex/mcp/tools/cortex_distill_tool.py
"""

from __future__ import annotations

import pytest


def _import_tool():
    from cortex.mcp.tools.cortex_distill_tool import CortexDistill
    return CortexDistill


class TestCortexDistillToolImport:
    """CortexDistill must be importable and satisfy ConsolidatedTool contract."""

    def test_tool_importable(self):
        """CortexDistill must be importable from cortex.mcp.tools.cortex_distill_tool."""
        CortexDistill = _import_tool()
        assert CortexDistill is not None

    def test_tool_inherits_consolidated_tool(self):
        """CortexDistill must extend ConsolidatedTool."""
        from cortex.mcp.mcp_tool_base import ConsolidatedTool
        CortexDistill = _import_tool()
        assert issubclass(CortexDistill, ConsolidatedTool)


class TestCortexDistillToolProperties:
    """Verify the MCP metadata properties required by the framework."""

    def test_name_property(self):
        CortexDistill = _import_tool()
        tool = CortexDistill()
        assert tool.name == "cortex_distill"

    def test_description_property(self):
        CortexDistill = _import_tool()
        tool = CortexDistill()
        assert "distill" in tool.description.lower() or "conversation" in tool.description.lower()

    def test_parameters_property_returns_list(self):
        CortexDistill = _import_tool()
        tool = CortexDistill()
        assert isinstance(tool.parameters, list)

    def test_parameters_includes_conversation_param(self):
        CortexDistill = _import_tool()
        tool = CortexDistill()
        param_names = [p.name for p in tool.parameters]
        assert "conversation" in param_names, (
            f"'conversation' parameter missing; found: {param_names}"
        )

    def test_category_property(self):
        from cortex.mcp.mcp_tool_base import ToolCategory
        CortexDistill = _import_tool()
        tool = CortexDistill()
        assert isinstance(tool.category, ToolCategory)


class TestCortexDistillToolExecution:
    """Verify execute() returns a ToolResult."""

    def test_execute_returns_tool_result(self):
        from cortex.mcp.mcp_tool_base import ToolResult
        CortexDistill = _import_tool()
        tool = CortexDistill()
        result = tool.execute({"conversation": "User: I want a REST API.\nAgent: Sure."})
        assert isinstance(result, ToolResult)

    def test_execute_empty_conversation_returns_error(self):
        from cortex.mcp.mcp_tool_base import ToolResult
        CortexDistill = _import_tool()
        tool = CortexDistill()
        result = tool.execute({"conversation": ""})
        assert isinstance(result, ToolResult)
        assert result.success is False

    def test_execute_missing_conversation_returns_error(self):
        from cortex.mcp.mcp_tool_base import ToolResult
        CortexDistill = _import_tool()
        tool = CortexDistill()
        result = tool.execute({})
        assert isinstance(result, ToolResult)
        assert result.success is False
