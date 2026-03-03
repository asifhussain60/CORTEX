"""
Tests for Phase 113 GAP-07 — cortex_context MCP tool.

Verifies:
1. CortexContext class exists and satisfies the Tool ABC
2. Tool name is 'cortex_context'
3. Supported ops: query_prior, get_session, search_history
4. query_prior returns list of prior requests for a session
5. get_session returns full session chain (sequence-ordered)
6. search_history returns keyword-matched requests
7. Missing session_id returns graceful error (no crash)
8. Unknown op returns graceful error result

TDD sequence (RED → GREEN → REFACTOR).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


def _make_log_manager(db_path: str) -> Any:
    from cortex.orchestrators.core.request_log_manager import RequestLogManager
    return RequestLogManager(db_path=db_path)


class TestCortexContextToolDefinition:
    """CortexContext must satisfy Tool ABC with correct name and ops."""

    def test_cortex_context_module_importable(self) -> None:
        """cortex.mcp.tools.cortex_context must be importable."""
        import cortex.mcp.tools.cortex_context  # noqa: F401

    def test_cortex_context_class_exists(self) -> None:
        """CortexContext class must exist in the module."""
        from cortex.mcp.tools.cortex_context import CortexContext
        assert CortexContext is not None

    def test_tool_name_is_cortex_context(self) -> None:
        """Tool name must be 'cortex_context' (MCP client identifier)."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        assert tool.name == "cortex_context"

    def test_tool_definition_has_op_parameter(self) -> None:
        """Tool definition must declare 'op' as a required parameter."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        param_names = {p.name for p in tool.definition.parameters}
        assert "op" in param_names

    def test_tool_definition_op_enum_covers_all_ops(self) -> None:
        """op parameter enum must include query_prior, get_session, search_history."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        op_param = next(p for p in tool.definition.parameters if p.name == "op")
        required_ops = {"query_prior", "get_session", "search_history"}
        assert required_ops.issubset(set(op_param.enum or []))

    def test_tool_has_execute_method(self) -> None:
        """CortexContext must implement execute()."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        assert callable(tool.execute)


class TestCortexContextQueryPrior:
    """op=query_prior must return prior request list from RequestLogManager."""

    def test_query_prior_returns_tool_result(self, tmp_path: Path) -> None:
        """op=query_prior must return a ToolResult (not raise)."""
        from cortex.mcp.tools.cortex_context import CortexContext
        from cortex.mcp.mcp_tool_base import ToolResult
        tool = CortexContext()
        result = tool.execute(op="query_prior", session_id="test-sess-001")
        assert isinstance(result, ToolResult)

    def test_query_prior_empty_session_returns_empty_list(self, tmp_path: Path) -> None:
        """New session with no history should return empty prior list."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        result = tool.execute(op="query_prior", session_id="brand-new-session-xyz")
        assert result.success is True
        data = result.data
        assert isinstance(data.get("prior_requests"), list)
        assert len(data["prior_requests"]) == 0

    def test_query_prior_returns_logged_requests(self, tmp_path: Path) -> None:
        """query_prior must return requests logged by RequestLogManager."""
        db = str(tmp_path / "ctx.db")
        rlm = _make_log_manager(db)
        rlm.log_request(session_id="sess-q1", user_request="Build login page")
        rlm.log_request(session_id="sess-q1", user_request="Add OAuth support")

        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext(db_path=db)
        result = tool.execute(op="query_prior", session_id="sess-q1", limit=10)
        assert result.success is True
        priors = result.data.get("prior_requests", [])
        assert len(priors) == 2

    def test_query_prior_missing_session_id_returns_error(self) -> None:
        """op=query_prior without session_id must return error ToolResult, not raise."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        result = tool.execute(op="query_prior")
        assert result.success is False
        assert "session_id" in str(result.error).lower()


class TestCortexContextGetSession:
    """op=get_session must return full sequence-ordered session chain."""

    def test_get_session_returns_ordered_by_sequence(self, tmp_path: Path) -> None:
        """get_session must return requests ordered by sequence_number ascending."""
        db = str(tmp_path / "ctx.db")
        rlm = _make_log_manager(db)
        rlm.log_request(session_id="sess-gs1", user_request="First request")
        rlm.log_request(session_id="sess-gs1", user_request="Second request")
        rlm.log_request(session_id="sess-gs1", user_request="Third request")

        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext(db_path=db)
        result = tool.execute(op="get_session", session_id="sess-gs1")
        assert result.success is True
        chain = result.data.get("session_chain", [])
        assert len(chain) == 3
        # Ascending sequence order
        seqs = [r.get("sequence_number", 0) for r in chain]
        assert seqs == sorted(seqs)

    def test_get_session_includes_metadata_fields(self, tmp_path: Path) -> None:
        """Each record in session_chain must have required fields."""
        db = str(tmp_path / "ctx.db")
        rlm = _make_log_manager(db)
        rlm.log_request(session_id="sess-meta1", user_request="Query metadata")

        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext(db_path=db)
        result = tool.execute(op="get_session", session_id="sess-meta1")
        chain = result.data.get("session_chain", [])
        assert len(chain) == 1
        record = chain[0]
        assert "request_id" in record
        assert "user_request" in record
        assert "sequence_number" in record


class TestCortexContextSearchHistory:
    """op=search_history must return keyword-matched requests."""

    def test_search_history_finds_matching_request(self, tmp_path: Path) -> None:
        """search_history must return rows where user_request contains the keyword."""
        db = str(tmp_path / "ctx.db")
        rlm = _make_log_manager(db)
        rlm.log_request(session_id="sess-sh1", user_request="Implement JWT authentication")
        rlm.log_request(session_id="sess-sh1", user_request="Add password hashing with bcrypt")
        rlm.log_request(session_id="sess-sh2", user_request="JWT token refresh logic")

        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext(db_path=db)
        result = tool.execute(op="search_history", keyword="JWT")
        assert result.success is True
        matches = result.data.get("matches", [])
        assert len(matches) == 2  # Both JWT requests
        for match in matches:
            assert "JWT" in match.get("user_request", "")

    def test_search_history_no_match_returns_empty_list(self, tmp_path: Path) -> None:
        """search_history with non-matching keyword returns empty matches list."""
        db = str(tmp_path / "ctx.db")
        rlm = _make_log_manager(db)
        rlm.log_request(session_id="sess-sh2", user_request="Build a dashboard")

        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext(db_path=db)
        result = tool.execute(op="search_history", keyword="xyz_nonexistent_keyword")
        assert result.success is True
        assert result.data.get("matches") == []

    def test_search_history_missing_keyword_returns_error(self) -> None:
        """op=search_history without keyword must return error ToolResult."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        result = tool.execute(op="search_history")
        assert result.success is False
        assert "keyword" in str(result.error).lower()


class TestCortexContextUnknownOp:
    """Unknown op must return error ToolResult, not raise."""

    def test_unknown_op_returns_error_result(self) -> None:
        """Unrecognized op must not raise — return ToolResult(success=False)."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        result = tool.execute(op="does_not_exist")
        assert result.success is False

    def test_no_op_returns_error_result(self) -> None:
        """Missing op must not raise — return ToolResult(success=False)."""
        from cortex.mcp.tools.cortex_context import CortexContext
        tool = CortexContext()
        result = tool.execute()
        assert result.success is False
