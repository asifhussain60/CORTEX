"""
CortexContext MCP Tool — Phase 113 GAP-07.

AC_START: AC-113-MCP-CONTEXT-001

Exposes RequestLogManager via MCP so Copilot Chat and any MCP client can:
- Query prior requests for a session (op=query_prior)
- Retrieve the full ordered session chain (op=get_session)
- Search request history by keyword (op=search_history)

This closes the Phase 113 audit trail loop: requests are logged pre-API by
MasterOrchestrator and retrievable via this tool without direct DB access.

Author: GitHub Copilot
Date: 2026-03-02
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Any, Dict, List, Optional

from cortex.mcp.mcp_tool_base import (
    Tool,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolResult,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = ".cortex-runtime/state/conversations.db"


class CortexContext(Tool):
    """
    MCP tool exposing the Phase 113 Request Sequence Persistence layer.

    Operations:
    - query_prior   : Return prior requests for a session (newest-first, limited)
    - get_session   : Return full session chain ordered by sequence_number ascending
    - search_history: Keyword search across all user_request text (case-insensitive)
    """

    _PARAMETERS: List[ToolParameter] = [
        ToolParameter(
            name="op",
            type="string",
            description=(
                "Operation to perform: "
                "'query_prior' (recent requests for a session, newest-first), "
                "'get_session' (full ordered session chain), "
                "'search_history' (keyword search across all request text)"
            ),
            required=True,
            enum=["query_prior", "get_session", "search_history"],
        ),
        ToolParameter(
            name="session_id",
            type="string",
            description=(
                "Session identifier — required for query_prior and get_session. "
                "Optional filter for search_history."
            ),
            required=False,
        ),
        ToolParameter(
            name="limit",
            type="integer",
            description="Maximum number of records to return (default: 10). Applies to query_prior.",
            required=False,
        ),
        ToolParameter(
            name="keyword",
            type="string",
            description=(
                "Keyword to search for in user_request text (required for search_history, "
                "case-insensitive LIKE match)."
            ),
            required=False,
        ),
    ]

    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Initialise CortexContext tool.

        Args:
            db_path: Path to the SQLite database. Defaults to the canonical
                     runtime path used by RequestLogManager.
        """
        self._db_path: str = db_path or _DEFAULT_DB_PATH

    # -------------------------------------------------------------------------
    # Tool ABC requirements
    # -------------------------------------------------------------------------

    @property
    def definition(self) -> ToolDefinition:
        """MCP-compliant tool definition."""
        return ToolDefinition(
            name="cortex_context",
            description=(
                "Phase 113 — Request Sequence Persistence context tool. "
                "Query the CORTEX request audit trail: retrieve prior requests for a session, "
                "explore the full session chain, or search request history by keyword. "
                "Use to build awareness of what has been asked in this session."
            ),
            category=ToolCategory.INTELLIGENCE,
            parameters=self._PARAMETERS,
        )

    @property
    def name(self) -> str:
        """Tool name exposed to MCP clients."""
        return self.definition.name

    @property
    def description(self) -> str:
        """Human-readable description."""
        return self.definition.description

    @property
    def category(self) -> ToolCategory:
        """Tool category for MCP routing."""
        return self.definition.category

    # -------------------------------------------------------------------------
    # Execute dispatcher
    # -------------------------------------------------------------------------

    def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute a context operation.

        Args:
            **kwargs: Must include 'op'. Additional params depend on op.

        Returns:
            ToolResult with operation outcome.
        """
        op = kwargs.get("op", "")

        try:
            if op == "query_prior":
                return self._op_query_prior(kwargs)
            elif op == "get_session":
                return self._op_get_session(kwargs)
            elif op == "search_history":
                return self._op_search_history(kwargs)
            else:
                return ToolResult(
                    success=False,
                    data={},
                    error=f"Unknown op '{op}'. Valid ops: query_prior, get_session, search_history.",
                )
        except Exception as exc:
            logger.exception("CortexContext.execute error for op=%r", op)
            return ToolResult(success=False, data={}, error=str(exc))

    # -------------------------------------------------------------------------
    # Op implementations
    # -------------------------------------------------------------------------

    def _op_query_prior(self, kwargs: Dict[str, Any]) -> ToolResult:
        """
        Return recent requests for a session (newest-first).

        Required kwargs: session_id
        Optional kwargs: limit (default 10)
        """
        session_id: Optional[str] = kwargs.get("session_id")
        if not session_id:
            return ToolResult(
                success=False,
                data={},
                error="query_prior requires 'session_id' parameter.",
            )

        limit: int = int(kwargs.get("limit") or 10)

        try:
            rlm = self._get_request_log_manager()
            prior = rlm.get_prior_requests(session_id=session_id, limit=limit)
            return ToolResult(
                success=True,
                data={
                    "op": "query_prior",
                    "session_id": session_id,
                    "prior_requests": prior,
                    "count": len(prior),
                },
            )
        except Exception as exc:
            # Fallback: direct SQLite query so tool works even if RLM unavailable
            return self._fallback_query_prior(session_id, limit, str(exc))

    def _op_get_session(self, kwargs: Dict[str, Any]) -> ToolResult:
        """
        Return full session chain ordered by sequence_number ascending.

        Required kwargs: session_id
        """
        session_id: Optional[str] = kwargs.get("session_id")
        if not session_id:
            return ToolResult(
                success=False,
                data={},
                error="get_session requires 'session_id' parameter.",
            )

        try:
            rows = self._query_session_chain(session_id)
            return ToolResult(
                success=True,
                data={
                    "op": "get_session",
                    "session_id": session_id,
                    "session_chain": rows,
                    "count": len(rows),
                },
            )
        except Exception as exc:
            return ToolResult(success=False, data={}, error=str(exc))

    def _op_search_history(self, kwargs: Dict[str, Any]) -> ToolResult:
        """
        Keyword search across all request history (case-insensitive LIKE).

        Required kwargs: keyword
        Optional kwargs: session_id (filter by session), limit (default 20)
        """
        keyword: Optional[str] = kwargs.get("keyword")
        if not keyword:
            return ToolResult(
                success=False,
                data={},
                error="search_history requires 'keyword' parameter.",
            )

        session_id: Optional[str] = kwargs.get("session_id")
        limit: int = int(kwargs.get("limit") or 20)

        try:
            rows = self._query_keyword_search(keyword, session_id, limit)
            return ToolResult(
                success=True,
                data={
                    "op": "search_history",
                    "keyword": keyword,
                    "session_id": session_id,
                    "matches": rows,
                    "count": len(rows),
                },
            )
        except Exception as exc:
            return ToolResult(success=False, data={}, error=str(exc))

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _get_request_log_manager(self) -> Any:
        """Lazy-load RequestLogManager pointed at the configured DB path."""
        from cortex.orchestrators.core.request_log_manager import RequestLogManager
        return RequestLogManager(db_path=self._db_path)

    def _query_session_chain(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Query request_log for all rows in a session, ordered by sequence_number ASC.

        Returns:
            List of dicts with request_id, user_request, sequence_number,
            intent_type, received_at, status.
        """
        import os
        if not os.path.exists(self._db_path):
            return []

        with sqlite3.connect(self._db_path, timeout=10.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT request_id, user_request, sequence_number,
                       intent_type, received_at, status
                FROM   request_log
                WHERE  session_id = ?
                ORDER  BY sequence_number ASC
                """,
                (session_id,),
            ).fetchall()
        return [dict(r) for r in rows]

    def _query_keyword_search(
        self,
        keyword: str,
        session_id: Optional[str],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """
        LIKE search on user_request across all sessions (or one session).

        Returns:
            List of matching dicts with request_id, user_request,
            session_id, sequence_number, received_at.
        """
        import os
        if not os.path.exists(self._db_path):
            return []

        pattern = f"%{keyword}%"
        with sqlite3.connect(self._db_path, timeout=10.0) as conn:
            conn.row_factory = sqlite3.Row
            if session_id:
                rows = conn.execute(
                    """
                    SELECT request_id, user_request, session_id,
                           sequence_number, received_at
                    FROM   request_log
                    WHERE  user_request LIKE ? COLLATE NOCASE
                      AND  session_id = ?
                    ORDER  BY received_at DESC
                    LIMIT  ?
                    """,
                    (pattern, session_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT request_id, user_request, session_id,
                           sequence_number, received_at
                    FROM   request_log
                    WHERE  user_request LIKE ? COLLATE NOCASE
                    ORDER  BY received_at DESC
                    LIMIT  ?
                    """,
                    (pattern, limit),
                ).fetchall()
        return [dict(r) for r in rows]

    def _fallback_query_prior(
        self, session_id: str, limit: int, original_error: str
    ) -> ToolResult:
        """
        Direct SQLite fallback for query_prior when RequestLogManager is unavailable.

        Returns empty list (not an error) — the table may simply not exist yet.
        """
        import os
        try:
            if not os.path.exists(self._db_path):
                return ToolResult(
                    success=True,
                    data={
                        "op": "query_prior",
                        "session_id": session_id,
                        "prior_requests": [],
                        "count": 0,
                    },
                )
            with sqlite3.connect(self._db_path, timeout=10.0) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT request_id, user_request, sequence_number,
                           intent_type, received_at, status
                    FROM   request_log
                    WHERE  session_id = ?
                    ORDER  BY sequence_number DESC
                    LIMIT  ?
                    """,
                    (session_id, limit),
                ).fetchall()
            return ToolResult(
                success=True,
                data={
                    "op": "query_prior",
                    "session_id": session_id,
                    "prior_requests": [dict(r) for r in rows],
                    "count": len(rows),
                },
            )
        except Exception:
            # If DB doesn't have the table yet, return empty (not an error)
            return ToolResult(
                success=True,
                data={
                    "op": "query_prior",
                    "session_id": session_id,
                    "prior_requests": [],
                    "count": 0,
                },
            )


# AC_COMPLETE: AC-113-MCP-CONTEXT-001 ✅ CortexContext MCP tool created
