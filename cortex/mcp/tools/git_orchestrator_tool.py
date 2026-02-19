"""
CortexGitPush — MCP tool exposing GitOrchestrator as a single callable.

Replaces GitHub Actions workflows and .githooks shell scripts with one
MCP-first entry point:

    cortex_git_push(repo_path, branch, message, proprietary_terms?)

The tool orchestrates: CORE enforcement → sanitization → async git push.

AC_START: AC-GIT-ORCH-002
Authority: GitOrchestrator recommendation (2026-02-19)
Testing: tests/unit/orchestrators/git/test_git_orchestrator.py
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-028 (snake_case), CORE-035 (single canonical implementation)
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from cortex.mcp.mcp_tool_base import (
    Tool,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolResult,
)

logger = logging.getLogger(__name__)


class CortexGitPush(Tool):
    """MCP tool: cortex_git_push — Enforce → Sanitize → Push pipeline.

    Single MCP entry point that replaces all git hooks and GitHub Actions
    workflows. Calls :class:`~cortex.orchestrators.git.git_orchestrator.GitOrchestrator`
    which runs:

    1. CORE enforcement (naming, placement, type hints)
    2. Deep-file sanitization (secrets, PII, proprietary terms)
    3. Async git add → commit → push

    Parameters
    ----------
    repo_path : str
        Absolute path to the git repository root.
    branch : str
        Target branch to push to on the remote (e.g., ``main``).
    message : str
        Commit message.
    proprietary_terms : str, optional
        JSON-encoded mapping of proprietary term → generic replacement.
        Example: ``'{"acme-corp": "enterprise-client"}'``
    dry_run : bool, optional
        When ``true``, sanitization scans but does not write files or push.

    Example
    -------
    Via Copilot Chat::

        Use cortex_git_push with repo_path="/path/to/repo",
        branch="main", message="feat: sanitized push"
    """

    @property
    def definition(self) -> ToolDefinition:
        """Return MCP-compliant tool definition.

        Returns:
            :class:`~cortex.mcp.mcp_tool_base.ToolDefinition` for cortex_git_push.
        """
        return ToolDefinition(
            name="cortex_git_push",
            description=(
                "Enforce CORE rules, deep-sanitize proprietary/PII/secret data, "
                "then stage, commit and push to origin. Replaces git hooks and "
                "GitHub Actions workflows."
            ),
            category=ToolCategory.OPERATIONS,
            parameters=[
                ToolParameter(
                    name="repo_path",
                    type="string",
                    required=True,
                    description="Absolute path to the git repository root.",
                ),
                ToolParameter(
                    name="branch",
                    type="string",
                    required=True,
                    description="Target branch to push to (e.g., 'main').",
                ),
                ToolParameter(
                    name="message",
                    type="string",
                    required=True,
                    description="Commit message.",
                ),
                ToolParameter(
                    name="proprietary_terms",
                    type="string",
                    required=False,
                    description=(
                        "JSON object mapping proprietary terms to generic replacements. "
                        'Example: \'{"acme-corp": "enterprise-client"}\''
                    ),
                    default=None,
                ),
                ToolParameter(
                    name="dry_run",
                    type="boolean",
                    required=False,
                    description=(
                        "When true, scan and sanitize in-memory only — no file writes "
                        "or git push. Useful for previewing changes."
                    ),
                    default=False,
                ),
            ],
        )

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the enforce → sanitize → push pipeline.

        Args:
            params: Dict with keys: repo_path, branch, message,
                    optionally proprietary_terms (JSON str) and dry_run (bool).

        Returns:
            :class:`~cortex.mcp.mcp_tool_base.ToolResult` with pipeline outcome.
        """
        repo_path: str = params.get("repo_path", "")
        branch: str = params.get("branch", "main")
        message: str = params.get("message", "chore: cortex git push")
        dry_run: bool = bool(params.get("dry_run", False))

        # Parse proprietary_terms JSON string → dict
        proprietary_terms: Optional[Dict[str, str]] = None
        raw_terms = params.get("proprietary_terms")
        if raw_terms:
            try:
                proprietary_terms = json.loads(raw_terms)
            except (json.JSONDecodeError, TypeError) as exc:
                return ToolResult(
                    success=False,
                    error=f"Invalid proprietary_terms JSON: {exc}",
                )

        try:
            from cortex.orchestrators.git.git_orchestrator import (
                GitOrchestrator,
                GitOrchestratorError,
            )

            orchestrator = GitOrchestrator(
                proprietary_terms=proprietary_terms,
                sanitize_dry_run=dry_run,
            )

            result = asyncio.run(
                orchestrator.execute(
                    repo_path=repo_path,
                    branch=branch,
                    message=message,
                )
            )

            return ToolResult(
                success=result.success,
                data={
                    "enforcement_passed": result.enforcement_passed,
                    "sanitization_changes": result.sanitization_changes,
                    "commit_sha": result.commit_sha,
                    "branch": result.branch,
                    "audit_summary": result.audit_summary,
                    "dry_run": dry_run,
                },
            )

        except Exception as exc:
            logger.error("cortex_git_push failed: %s", exc)
            return ToolResult(success=False, error=str(exc))


__all__ = ["CortexGitPush"]

# AC_COMPLETE: AC-GIT-ORCH-002 ✅ CortexGitPush MCP tool implemented
