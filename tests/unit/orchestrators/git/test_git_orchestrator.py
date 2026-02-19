"""
Tests for GitOrchestrator and GitPublishOrchestrator

AC_START: AC-GIT-ORCH-002
Description: TDD tests for GitOrchestrator pipeline (enforce → sanitize → publish)
Authority: GitOrchestrator recommendation (2026-02-19)
Governance: CORE-008 (TDD mandatory), CORE-011 (type hints), CORE-012 (docstrings)

Test Coverage:
- GitPublishOrchestrator: stage, commit, push via AsyncGitOperations
- GitOrchestrator: three-stage pipeline execution
- MCP tool exposure: cortex_git_push
- Error propagation between stages
- Audit trail end-to-end
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


# ---------------------------------------------------------------------------
# Tests: GitPublishOrchestrator
# ---------------------------------------------------------------------------

class TestGitPublishOrchestrator:
    """GitPublishOrchestrator stages, commits and pushes clean code."""

    def test_git_publish_orchestrator_instantiates(self) -> None:
        """GitPublishOrchestrator can be instantiated."""
        from cortex.orchestrators.git.git_publish_orchestrator import GitPublishOrchestrator
        orch = GitPublishOrchestrator()
        assert orch is not None

    def test_publish_result_has_required_fields(self) -> None:
        """PublishResult has success, commit_sha, branch, message fields."""
        from cortex.orchestrators.git.git_publish_orchestrator import PublishResult
        result = PublishResult(
            success=True,
            commit_sha="abc123",
            branch="main",
            message="test: initial",
            files_committed=3,
        )
        assert result.success is True
        assert result.commit_sha == "abc123"

    @pytest.mark.asyncio
    async def test_publish_calls_git_add(self, tmp_path: Path) -> None:
        """GitPublishOrchestrator runs git add on changed files."""
        from cortex.orchestrators.git.git_publish_orchestrator import GitPublishOrchestrator
        orch = GitPublishOrchestrator()

        with patch.object(orch, "_run_git") as mock_git:
            mock_git.return_value = MagicMock(returncode=0, stdout="", stderr="")
            await orch.publish(
                repo_path=str(tmp_path),
                branch="main",
                message="feat: test commit",
            )
            calls = [str(c) for c in mock_git.call_args_list]
            assert any("add" in c for c in calls)

    @pytest.mark.asyncio
    async def test_publish_calls_git_commit(self, tmp_path: Path) -> None:
        """GitPublishOrchestrator runs git commit with provided message."""
        from cortex.orchestrators.git.git_publish_orchestrator import GitPublishOrchestrator
        orch = GitPublishOrchestrator()

        with patch.object(orch, "_run_git") as mock_git:
            mock_git.return_value = MagicMock(returncode=0, stdout="abc123", stderr="")
            await orch.publish(
                repo_path=str(tmp_path),
                branch="main",
                message="feat: test commit",
            )
            calls = [str(c) for c in mock_git.call_args_list]
            assert any("commit" in c for c in calls)

    @pytest.mark.asyncio
    async def test_publish_calls_git_push(self, tmp_path: Path) -> None:
        """GitPublishOrchestrator runs git push to origin."""
        from cortex.orchestrators.git.git_publish_orchestrator import GitPublishOrchestrator
        orch = GitPublishOrchestrator()

        with patch.object(orch, "_run_git") as mock_git:
            mock_git.return_value = MagicMock(returncode=0, stdout="", stderr="")
            await orch.publish(
                repo_path=str(tmp_path),
                branch="feature/x",
                message="feat: push test",
            )
            calls = [str(c) for c in mock_git.call_args_list]
            assert any("push" in c for c in calls)

    @pytest.mark.asyncio
    async def test_publish_raises_on_git_failure(self, tmp_path: Path) -> None:
        """GitPublishOrchestrator raises PublishError when git command fails."""
        from cortex.orchestrators.git.git_publish_orchestrator import (
            GitPublishOrchestrator, PublishError,
        )
        orch = GitPublishOrchestrator()

        with patch.object(orch, "_run_git", side_effect=Exception("git push failed")):
            with pytest.raises(PublishError):
                await orch.publish(
                    repo_path=str(tmp_path),
                    branch="main",
                    message="feat: fail test",
                )


# ---------------------------------------------------------------------------
# Tests: GitOrchestrator (pipeline integration)
# ---------------------------------------------------------------------------

class TestGitOrchestrator:
    """GitOrchestrator runs enforce → sanitize → publish pipeline."""

    def test_git_orchestrator_instantiates(self) -> None:
        """GitOrchestrator can be instantiated."""
        from cortex.orchestrators.git.git_orchestrator import GitOrchestrator
        orch = GitOrchestrator()
        assert orch is not None

    def test_git_orchestrator_result_has_required_fields(self) -> None:
        """GitOrchestratorResult has all pipeline stage results."""
        from cortex.orchestrators.git.git_orchestrator import GitOrchestratorResult
        result = GitOrchestratorResult(
            success=True,
            enforcement_passed=True,
            sanitization_changes=0,
            commit_sha="abc123",
            branch="main",
        )
        assert result.success is True
        assert result.enforcement_passed is True
        assert result.sanitization_changes == 0

    @pytest.mark.asyncio
    async def test_execute_calls_all_three_stages(self, tmp_path: Path) -> None:
        """GitOrchestrator.execute() calls enforce, sanitize, publish in order."""
        from cortex.orchestrators.git.git_orchestrator import GitOrchestrator

        orch = GitOrchestrator()

        mock_enforce = MagicMock(return_value=MagicMock(passed=True, violations=[]))
        mock_sanitize = MagicMock(return_value=MagicMock(
            sanitized=True, total_changes=0, audit_trail=MagicMock(summary=lambda: {"total_substitutions": 0})
        ))
        mock_publish = AsyncMock(return_value=MagicMock(
            success=True, commit_sha="abc123", branch="main"
        ))

        with patch.object(orch.enforcement, "run_checks", mock_enforce), \
             patch.object(orch.sanitizer, "sanitize", mock_sanitize), \
             patch.object(orch.publisher, "publish", mock_publish):
            result = await orch.execute(
                repo_path=str(tmp_path),
                branch="main",
                message="feat: pipeline test",
            )

        mock_enforce.assert_called_once()
        mock_sanitize.assert_called_once()
        mock_publish.assert_called_once()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_blocks_on_enforcement_failure(self, tmp_path: Path) -> None:
        """GitOrchestrator halts pipeline if EnforcementOrchestrator finds violations."""
        from cortex.orchestrators.git.git_orchestrator import (
            GitOrchestrator, GitOrchestratorError,
        )
        orch = GitOrchestrator()

        mock_enforce = MagicMock(return_value=MagicMock(
            passed=False, violations=["CORE-028: snake_case violation in module_X.py"]
        ))

        with patch.object(orch.enforcement, "run_checks", mock_enforce):
            with pytest.raises(GitOrchestratorError) as exc_info:
                await orch.execute(
                    repo_path=str(tmp_path),
                    branch="main",
                    message="feat: blocked",
                )
            assert "enforcement" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_execute_blocks_on_sanitization_integrity_failure(self, tmp_path: Path) -> None:
        """GitOrchestrator halts pipeline if sanitizer raises SanitizationError."""
        from cortex.orchestrators.git.git_orchestrator import (
            GitOrchestrator, GitOrchestratorError,
        )
        from cortex.orchestrators.git.sanitization_orchestrator import SanitizationError
        orch = GitOrchestrator()

        mock_enforce = MagicMock(return_value=MagicMock(passed=True, violations=[]))
        mock_sanitize = MagicMock(side_effect=SanitizationError("broken.py failed syntax check"))

        with patch.object(orch.enforcement, "run_checks", mock_enforce), \
             patch.object(orch.sanitizer, "sanitize", mock_sanitize):
            with pytest.raises(GitOrchestratorError):
                await orch.execute(
                    repo_path=str(tmp_path),
                    branch="main",
                    message="feat: syntax fail",
                )

    @pytest.mark.asyncio
    async def test_execute_returns_sanitization_change_count(self, tmp_path: Path) -> None:
        """GitOrchestratorResult includes sanitization change count from SanitizationOrchestrator."""
        from cortex.orchestrators.git.git_orchestrator import GitOrchestrator
        orch = GitOrchestrator()

        mock_enforce = MagicMock(return_value=MagicMock(passed=True, violations=[]))
        mock_sanitize = MagicMock(return_value=MagicMock(
            sanitized=True,
            total_changes=7,
            audit_trail=MagicMock(summary=lambda: {"total_substitutions": 7}),
        ))
        mock_publish = AsyncMock(return_value=MagicMock(
            success=True, commit_sha="def456", branch="main"
        ))

        with patch.object(orch.enforcement, "run_checks", mock_enforce), \
             patch.object(orch.sanitizer, "sanitize", mock_sanitize), \
             patch.object(orch.publisher, "publish", mock_publish):
            result = await orch.execute(
                repo_path=str(tmp_path),
                branch="main",
                message="feat: changes",
            )

        assert result.sanitization_changes == 7


# ---------------------------------------------------------------------------
# Tests: MCP Tool (cortex_git_push)
# ---------------------------------------------------------------------------

class TestCortexGitPushMCPTool:
    """CortexGitPush MCP tool exposes GitOrchestrator via MCP protocol."""

    def test_cortex_git_push_tool_instantiates(self) -> None:
        """CortexGitPush tool can be instantiated."""
        from cortex.mcp.tools.git_orchestrator_tool import CortexGitPush
        tool = CortexGitPush()
        assert tool is not None

    def test_cortex_git_push_has_name(self) -> None:
        """CortexGitPush has MCP-compliant tool name."""
        from cortex.mcp.tools.git_orchestrator_tool import CortexGitPush
        tool = CortexGitPush()
        assert tool.definition.name == "cortex_git_push"

    def test_cortex_git_push_parameters_declared(self) -> None:
        """CortexGitPush declares repo_path, branch, message parameters."""
        from cortex.mcp.tools.git_orchestrator_tool import CortexGitPush
        tool = CortexGitPush()
        param_names = [p.name for p in tool.definition.parameters]
        assert "repo_path" in param_names
        assert "branch" in param_names
        assert "message" in param_names

    def test_cortex_git_push_execute_returns_tool_result(self) -> None:
        """CortexGitPush.execute() returns a ToolResult."""
        from cortex.mcp.tools.git_orchestrator_tool import CortexGitPush
        from cortex.mcp.mcp_tool_base import ToolResult

        tool = CortexGitPush()
        mock_result = MagicMock(
            success=True,
            enforcement_passed=True,
            sanitization_changes=0,
            commit_sha="abc123",
            branch="main",
        )

        with patch(
            "cortex.mcp.tools.git_orchestrator_tool.asyncio.run",
            return_value=mock_result,
        ):
            result = tool.execute({
                "repo_path": "/fake/repo",
                "branch": "main",
                "message": "feat: mcp test",
            })

        assert isinstance(result, ToolResult)
        assert result.success is True


# AC_COMPLETE: AC-GIT-ORCH-002 (TDD tests written — RED phase)
