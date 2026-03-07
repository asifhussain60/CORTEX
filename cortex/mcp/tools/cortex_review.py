"""CortexReview — PR code review MCP tool (GAP-132-02).

Provides MCP-accessible code review operations using the
CodeReviewOrchestrator 6-stage pipeline.

Operations:
  review   — Run full review pipeline; returns verdict + findings
  findings — List findings from the last review (stub)
  history  — PR review history (stub)
  patterns — Known vulnerability patterns from OWASP knowledge base
  health   — Review tool health check

Phase: 132 (GAP-132-02)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
🔒 Scope Lock: code-review
"""

from __future__ import annotations

from typing import Any, List, Optional

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)


class CortexReview(ConsolidatedTool):
    """PR code review MCP tool.

    Runs the CORTEX 6-stage code review pipeline against a unified diff and
    returns an APPROVE / REQUEST_CHANGES / BLOCK verdict with structured findings.

    Supported operations:
        - ``review``    — full 6-stage pipeline; returns verdict + findings
        - ``findings``  — findings from the last review in this session
        - ``history``   — PR review history (stub)
        - ``patterns``  — OWASP vulnerability pattern catalogue
        - ``health``    — tool health check
    """

    @property
    def name(self) -> str:
        """Return tool name."""
        return "cortex_review"

    @property
    def description(self) -> str:
        """Return tool description."""
        return (
            "PR code review pipeline — 6-stage OWASP-aligned analysis producing "
            "APPROVE / REQUEST_CHANGES / BLOCK verdict. "
            "Operations: review | findings | history | patterns | health."
        )

    @property
    def category(self) -> ToolCategory:
        """Return tool category."""
        return ToolCategory.INTELLIGENCE

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return tool parameter definitions."""
        return [
            ToolParameter(
                name="op",
                type="string",
                required=True,
                description="Operation: review | findings | history | patterns | health",
                enum=["review", "findings", "history", "patterns", "health"],
            ),
            ToolParameter(
                name="diff",
                type="string",
                required=False,
                description="Unified diff text of the PR (required for review)",
            ),
            ToolParameter(
                name="pr_title",
                type="string",
                required=False,
                description="Pull request title (optional context)",
            ),
            ToolParameter(
                name="author",
                type="string",
                required=False,
                description="PR author name (optional context)",
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return supported operation names (satisfies ConsolidatedTool abstract property)."""
        return ["review", "findings", "history", "patterns", "health"]

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the requested review operation.

        Args:
            **kwargs: Must include ``op`` (str).  Optional: ``diff`` (str),
                ``pr_title`` (str), ``author`` (str).

        Returns:
            :class:`ToolResult` with review output.
        """
        op = str(kwargs.get("op", ""))
        dispatch = {
            "review": self._review,
            "findings": self._findings,
            "history": self._history,
            "patterns": self._patterns,
            "health": self._health,
        }
        handler = dispatch.get(op)
        if handler is None:
            return ToolResult(
                success=False,
                data={},
                error=f"Unknown operation: {op!r}. Valid: {self.supported_operations}",
            )
        return handler(**kwargs)

    # ------------------------------------------------------------------
    # Operation handlers
    # ------------------------------------------------------------------

    def _review(self, **kwargs: Any) -> ToolResult:
        """Run the full 6-stage review pipeline."""
        diff: str = kwargs.get("diff", "")
        if not diff:
            return ToolResult(
                success=False,
                data={},
                error="'diff' parameter is required for the 'review' operation.",
            )
        context = {
            "pr_title": kwargs.get("pr_title", ""),
            "author": kwargs.get("author", ""),
        }
        try:
            from cortex.orchestrators.domain.code_review_orchestrator import CodeReviewOrchestrator
            result = CodeReviewOrchestrator().review(diff=diff, context=context)
            return ToolResult(success=True, data=result)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(success=False, data={}, error=str(exc))

    @staticmethod
    def _findings(**kwargs: Any) -> ToolResult:
        """Return findings stub."""
        return ToolResult(
            success=True,
            data={"findings": [], "note": "No cached review session — run 'review' first."},
        )

    @staticmethod
    def _history(**kwargs: Any) -> ToolResult:
        """Return review history stub."""
        return ToolResult(
            success=True,
            data={"history": [], "note": "Review history persistence coming in a future phase."},
        )

    @staticmethod
    def _patterns(**kwargs: Any) -> ToolResult:
        """Return the OWASP pattern catalogue."""
        return ToolResult(
            success=True,
            data={
                "owasp_top10": "cortex-registry/knowledge/security/owasp-top-10.yaml",
                "owasp_api_security": "cortex-registry/knowledge/security/owasp-api-security.yaml",
                "note": "Load YAMLs directly for full pattern catalogue.",
            },
        )

    def _health(self, **kwargs: Any) -> ToolResult:
        """Return health check result."""
        try:
            from cortex.mcp.mcp_registry import ToolRegistry
            registry = ToolRegistry()
            registered = any(t.id == "cortex_review" for t in registry.list_all())
            return ToolResult(
                success=True,
                data={
                    "status": "healthy",
                    "registered_in_registry": registered,
                    "supported_operations": self.supported_operations,
                },
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(success=False, data={}, error=str(exc))
