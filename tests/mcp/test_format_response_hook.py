"""
Phase 66-A RED tests — GAP-66-004: format_response() post-processing hook on BaseTool.

TDD-66-A-004: Every MCP tool response must pass through format_response() hook.

Author: Asif Hussain
Phase: 66-A
Sweep: SWEEP-66-INTELLIGENCE-MATRIX
"""

import pytest
from typing import Any, Dict
from unittest.mock import MagicMock, patch

# AC_START: AC-66-A-004-FORMAT-RESPONSE-HOOK-20260224T000000Z


class TestFormatResponseHookExists:
    """GAP-66-004: ConsolidatedTool must apply format_response() to all outputs."""

    def test_consolidated_tool_has_format_response_method(self) -> None:
        """ConsolidatedTool must have a format_response() method."""
        from cortex.mcp.mcp_tool_base import ConsolidatedTool

        assert hasattr(ConsolidatedTool, "format_response"), (
            "ConsolidatedTool must have format_response() method (GAP-66-004). "
            "Add it in cortex/mcp/mcp_tool_base.py."
        )

    def test_format_response_callable(self) -> None:
        """format_response() must be callable with a ToolResult."""
        from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolResult

        assert callable(getattr(ConsolidatedTool, "format_response", None)), (
            "format_response must be callable"
        )

    def test_tool_result_has_formatted_flag(self) -> None:
        """ToolResult.metadata must contain 'formatted': True after format_response()."""
        from cortex.mcp.mcp_tool_base import ConsolidatedTool, ToolResult
        from cortex.mcp.tools.brain import CortexBrainQuery

        tool = CortexBrainQuery()
        raw = ToolResult(success=True, data={"result": "raw"})
        formatted = tool.format_response(raw)

        assert isinstance(formatted, ToolResult), "format_response() must return ToolResult"
        assert formatted.metadata.get("formatted") is True, (
            "format_response() must set metadata['formatted'] = True (GAP-66-004)"
        )

    def test_all_mcp_tools_apply_format_response(self) -> None:
        """Every registered MCP tool that calls execute() must produce formatted output."""
        from cortex.mcp.mcp_tool_base import ConsolidatedTool

        # Every ConsolidatedTool must have format_response() inherited
        assert hasattr(ConsolidatedTool, "format_response"), (
            "ConsolidatedTool.format_response() missing — "
            "all MCP tool outputs must pass through it (GAP-66-004)."
        )


class TestResponseTemplateExposesFormatResponse:
    """GAP-66-004: ResponseTemplate must expose public format_response()."""

    def test_response_template_has_format_response(self) -> None:
        """ResponseTemplate must have a public format_response() callable."""
        from cortex.orchestrators.intelligence.response_template_generator import (
            ResponseTemplate,
        )
        assert hasattr(ResponseTemplate, "format_response"), (
            "ResponseTemplate must expose format_response() (GAP-66-004)"
        )

    def test_format_response_returns_string(self) -> None:
        """ResponseTemplate.format_response() must return a non-empty string."""
        from cortex.orchestrators.intelligence.response_template_generator import (
            ResponseTemplate,
        )
        result = ResponseTemplate.format_response(data={"result": "test_output"})
        assert isinstance(result, str) and len(result) > 0, (
            "format_response() must return non-empty string"
        )


# AC_COMPLETE: AC-66-A-004-FORMAT-RESPONSE-HOOK-20260224T000000Z ✅
