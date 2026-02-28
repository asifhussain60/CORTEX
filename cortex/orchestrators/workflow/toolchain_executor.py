"""
ToolchainExecutor - Post-Refactor Linter/Formatter Gate

AC-ID: AC-PHASE-89B-LINT-GATE
Purpose: Execute per-language linting/formatting after refactor operations

Governance:
- CORE-008: TDD first (tests in test_phase89b_post_refactor_lint_gate.py)
- CORE-011: Type hints on all functions
- CORE-012: Docstrings on all public APIs
- CORE-049: Silent autonomous execution (progress bars only)

Usage:
    executor = ToolchainExecutor()
    result = executor.execute_lint(Path("src/models.py"))
    if result.success:
        print(f"✅ Lint passed: {result.tool}")
"""

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ToolchainCommand:
    """Linter/formatter command configuration."""
    
    tool: str
    args: List[str]
    check_availability: bool = True
    
    def to_subprocess_args(self, file_path: Path) -> List[str]:
        """Convert to subprocess argument list."""
        return [self.tool] + self.args + [str(file_path)]


@dataclass
class LintResult:
    """Result of a lint/format operation."""
    
    tool: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    file_path: Path
    warning: Optional[str] = None
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for logging."""
        return {
            "tool": self.tool,
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "file_path": str(self.file_path),
            "warning": self.warning,
        }


class ToolchainExecutor:
    """
    Execute linters/formatters per file extension after refactor operations.
    
    Maps file extensions to their canonical toolchain commands and executes
    them with graceful degradation when tools are not installed.
    
    Phase 89-b: PostRefactorLintGate implementation.
    """
    
    # Extension → (tool, args) mapping
    EXTENSION_TOOL_MAP: Dict[str, ToolchainCommand] = {
        ".py": ToolchainCommand(tool="ruff", args=["check", "--fix"]),
        ".cs": ToolchainCommand(tool="dotnet", args=["format"]),
        ".ts": ToolchainCommand(tool="eslint", args=["--fix"]),
        ".tsx": ToolchainCommand(tool="eslint", args=["--fix"]),
        ".js": ToolchainCommand(tool="eslint", args=["--fix"]),
        ".jsx": ToolchainCommand(tool="eslint", args=["--fix"]),
        ".html": ToolchainCommand(tool="htmlhint", args=[]),
        ".css": ToolchainCommand(tool="stylelint", args=["--fix"]),
    }
    
    def __init__(self) -> None:
        """Initialize ToolchainExecutor."""
        self._tool_cache: Dict[str, bool] = {}  # Cache tool availability checks
    
    def get_command_for_extension(self, extension: str) -> Optional[ToolchainCommand]:
        """
        Get linter/formatter command for a file extension.
        
        Args:
            extension: File extension (e.g., ".py", ".ts")
            
        Returns:
            ToolchainCommand if extension is supported, None otherwise
        """
        return self.EXTENSION_TOOL_MAP.get(extension)
    
    def _is_tool_available(self, tool: str) -> bool:
        """
        Check if a tool is available on PATH.
        
        Args:
            tool: Tool name (e.g., "ruff", "eslint")
            
        Returns:
            True if tool is available, False otherwise
        """
        if tool in self._tool_cache:
            return self._tool_cache[tool]
        
        try:
            result = subprocess.run(
                ["which", tool],
                capture_output=True,
                text=True,
                timeout=5,
            )
            available = result.returncode == 0
            self._tool_cache[tool] = available
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self._tool_cache[tool] = False
            return False
    
    def execute_lint(
        self,
        file_path: Path,
        dry_run: bool = False,
    ) -> LintResult:
        """
        Execute linter/formatter for a single file.
        
        Args:
            file_path: Path to file to lint
            dry_run: If True, don't actually execute (return dry-run result)
            
        Returns:
            LintResult with execution outcome
        """
        start_time = time.perf_counter()
        
        # Get command for file extension
        extension = file_path.suffix
        command = self.get_command_for_extension(extension)
        
        if command is None:
            # No linter configured for this extension
            duration_ms = (time.perf_counter() - start_time) * 1000
            return LintResult(
                tool="none",
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                duration_ms=duration_ms,
                file_path=file_path,
                warning=f"No linter configured for {extension}",
            )
        
        # Dry run mode
        if dry_run:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return LintResult(
                tool=command.tool,
                success=True,
                exit_code=0,
                stdout="[DRY RUN]",
                stderr="",
                duration_ms=duration_ms,
                file_path=file_path,
                warning="Dry run mode - not executed",
            )
        
        # Check tool availability
        if not self._is_tool_available(command.tool):
            duration_ms = (time.perf_counter() - start_time) * 1000
            return LintResult(
                tool=command.tool,
                success=False,
                exit_code=-1,
                stdout="",
                stderr="",
                duration_ms=duration_ms,
                file_path=file_path,
                warning=f"Tool '{command.tool}' not installed (graceful degradation)",
            )
        
        # Execute linter/formatter
        try:
            cmd_args = command.to_subprocess_args(file_path)
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            return LintResult(
                tool=command.tool,
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=duration_ms,
                file_path=file_path,
            )
            
        except subprocess.TimeoutExpired:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return LintResult(
                tool=command.tool,
                success=False,
                exit_code=-1,
                stdout="",
                stderr="Timeout after 30s",
                duration_ms=duration_ms,
                file_path=file_path,
                warning="Lint command timed out",
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return LintResult(
                tool=command.tool,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=duration_ms,
                file_path=file_path,
                warning=f"Lint execution failed: {e}",
            )
    
    def execute_lint_batch(
        self,
        file_paths: List[Path],
        dry_run: bool = False,
    ) -> List[LintResult]:
        """
        Execute linter/formatter for multiple files.
        
        Args:
            file_paths: List of file paths to lint
            dry_run: If True, don't actually execute
            
        Returns:
            List of LintResult, one per file
        """
        results: List[LintResult] = []
        
        for file_path in file_paths:
            result = self.execute_lint(file_path, dry_run=dry_run)
            results.append(result)
        
        return results
