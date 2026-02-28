"""
Phase 89-b: PostRefactorLintGate - Toolchain Integration
RED → GREEN → REFACTOR

AC-ID: AC-PHASE-89B-LINT-GATE
Purpose: Post-refactor linter/formatter gate per file extension
Gap: GAP-89-04, GAP-89-05, GAP-89-06

Governance:
- CORE-008: TDD mandatory (this is RED phase)
- CORE-011: Type hints on all functions
- CORE-012: Docstrings on all public APIs
- CORE-049: Silent autonomous execution (progress bars only)
"""

import pytest
from typing import Dict, List, Optional
from pathlib import Path
from unittest.mock import MagicMock, patch

from cortex.orchestrators.workflow.toolchain_executor import (
    ToolchainExecutor,
    LintResult,
    ToolchainCommand,
)


class TestToolchainExecutorMapping:
    """
    Cluster 1: Verify file extension → linter/formatter mappings.
    
    Each file type must map to its canonical toolchain command.
    """

    @pytest.fixture
    def executor(self) -> ToolchainExecutor:
        """Create ToolchainExecutor instance."""
        return ToolchainExecutor()

    @pytest.mark.parametrize("extension,expected_tool", [
        (".py", "ruff"),
        (".cs", "dotnet"),
        (".ts", "eslint"),
        (".tsx", "eslint"),
        (".html", "htmlhint"),
        (".css", "stylelint"),
        (".js", "eslint"),
        (".jsx", "eslint"),
    ])
    def test_extension_maps_to_correct_tool(
        self, executor: ToolchainExecutor, extension: str, expected_tool: str
    ) -> None:
        """File extensions map to their canonical linter/formatter."""
        command = executor.get_command_for_extension(extension)
        assert command is not None, f"No command for {extension}"
        assert command.tool == expected_tool, (
            f"{extension} maps to {command.tool}, expected {expected_tool}"
        )

    def test_python_files_use_ruff_check_and_format(
        self, executor: ToolchainExecutor
    ) -> None:
        """Python files use 'ruff check --fix' + 'ruff format'."""
        command = executor.get_command_for_extension(".py")
        assert command is not None
        assert command.tool == "ruff"
        assert "check" in command.args or "format" in command.args

    def test_csharp_files_use_dotnet_format(
        self, executor: ToolchainExecutor
    ) -> None:
        """C# files use 'dotnet format'."""
        command = executor.get_command_for_extension(".cs")
        assert command is not None
        assert command.tool == "dotnet"
        assert "format" in command.args

    def test_typescript_files_use_eslint_fix(
        self, executor: ToolchainExecutor
    ) -> None:
        """TypeScript files use 'eslint --fix'."""
        command = executor.get_command_for_extension(".ts")
        assert command is not None
        assert command.tool == "eslint"
        assert "--fix" in command.args


class TestToolchainExecutorExecution:
    """
    Cluster 2: Verify toolchain execution and result handling.
    
    Tests actual execution of lint commands (or graceful degradation).
    """

    @pytest.fixture
    def executor(self) -> ToolchainExecutor:
        """Create ToolchainExecutor instance."""
        return ToolchainExecutor()

    @patch("subprocess.run")
    def test_execute_lint_runs_command(
        self, mock_run: MagicMock, executor: ToolchainExecutor
    ) -> None:
        """execute_lint() invokes subprocess.run with correct command."""
        def mock_run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == "which":
                return MagicMock(returncode=0, stdout="/usr/bin/ruff", stderr="")
            else:
                return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        result = executor.execute_lint(Path("test.py"))
        
        assert mock_run.called
        # Check that ruff was called (second call after 'which')
        assert mock_run.call_count >= 2

    @patch("subprocess.run")
    def test_execute_lint_returns_success_result(
        self, mock_run: MagicMock, executor: ToolchainExecutor
    ) -> None:
        """execute_lint() returns LintResult with success=True when tool exits 0."""
        def mock_run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == "which":
                return MagicMock(returncode=0, stdout="/usr/bin/ruff", stderr="")
            else:
                return MagicMock(returncode=0, stdout="All good", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        result = executor.execute_lint(Path("test.py"))
        
        assert result.success is True
        assert result.tool == "ruff"
        assert result.exit_code == 0

    @patch("subprocess.run")
    def test_execute_lint_returns_failure_result_on_nonzero_exit(
        self, mock_run: MagicMock, executor: ToolchainExecutor
    ) -> None:
        """execute_lint() returns LintResult with success=False when tool exits non-zero."""
        # Mock both the availability check and the lint execution
        def mock_run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == "which":
                # Tool is available
                return MagicMock(returncode=0, stdout="/usr/bin/ruff", stderr="")
            else:
                # Lint execution returns error
                return MagicMock(returncode=1, stdout="", stderr="Errors found")
        
        mock_run.side_effect = mock_run_side_effect
        
        result = executor.execute_lint(Path("test.py"))
        
        assert result.success is False
        assert result.exit_code == 1
        assert "Errors found" in result.stderr

    def test_execute_lint_graceful_degradation_when_tool_missing(
        self, executor: ToolchainExecutor
    ) -> None:
        """execute_lint() returns advisory warning when tool not installed."""
        # Use a file with extension that maps to non-existent tool
        result = executor.execute_lint(Path("test.xyz"))
        
        # Should return a result (not raise), with warning
        assert result is not None
        assert result.success is False or result.tool == "none"


class TestToolchainExecutorIntegration:
    """
    Cluster 3: Verify integration with RefactoringOrchestrator.
    
    Ensures lint gate is invoked after refactor operations.
    """

    @pytest.fixture
    def executor(self) -> ToolchainExecutor:
        """Create ToolchainExecutor instance."""
        return ToolchainExecutor()

    @patch("subprocess.run")
    def test_lint_multiple_files(
        self, mock_run: MagicMock, executor: ToolchainExecutor
    ) -> None:
        """execute_lint_batch() processes multiple files."""
        def mock_run_side_effect(cmd, *args, **kwargs):
            if cmd[0] == "which":
                return MagicMock(returncode=0, stdout="/usr/bin/tool", stderr="")
            else:
                return MagicMock(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = mock_run_side_effect
        
        files = [Path("test1.py"), Path("test2.py"), Path("test3.ts")]
        results = executor.execute_lint_batch(files)
        
        assert len(results) == 3
        assert all(r.success for r in results)

    def test_lint_results_have_timing_metadata(
        self, executor: ToolchainExecutor
    ) -> None:
        """LintResult includes duration_ms for performance tracking."""
        result = executor.execute_lint(Path("test.py"))
        
        assert hasattr(result, "duration_ms")
        assert isinstance(result.duration_ms, (int, float))

    def test_executor_supports_dry_run_mode(
        self, executor: ToolchainExecutor
    ) -> None:
        """ToolchainExecutor supports dry_run=True (no actual execution)."""
        result = executor.execute_lint(Path("test.py"), dry_run=True)
        
        assert result is not None
        assert result.tool == "ruff"
        # In dry run, should not actually execute


class TestLintResultDataclass:
    """
    Cluster 4: Verify LintResult dataclass structure.
    
    Ensures LintResult captures all necessary metadata.
    """

    def test_lint_result_has_required_fields(self) -> None:
        """LintResult has tool, success, exit_code, stdout, stderr, duration_ms."""
        result = LintResult(
            tool="ruff",
            success=True,
            exit_code=0,
            stdout="All clean",
            stderr="",
            duration_ms=123.45,
            file_path=Path("test.py"),
        )
        
        assert result.tool == "ruff"
        assert result.success is True
        assert result.exit_code == 0
        assert result.stdout == "All clean"
        assert result.stderr == ""
        assert result.duration_ms == 123.45
        assert result.file_path == Path("test.py")

    def test_lint_result_can_be_serialized_to_dict(self) -> None:
        """LintResult can be converted to dict for logging."""
        result = LintResult(
            tool="eslint",
            success=False,
            exit_code=1,
            stdout="",
            stderr="Linting errors",
            duration_ms=456.78,
            file_path=Path("test.ts"),
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["tool"] == "eslint"
        assert result_dict["success"] is False
        assert result_dict["exit_code"] == 1
        assert "file_path" in result_dict
