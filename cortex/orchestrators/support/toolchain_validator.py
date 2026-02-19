"""Toolchain Validator — verify development tool health.

Validates that required development tools (pytest, mypy, ruff, git) are
available and functional in the target workspace.

AC: PHASE-DEPLOYMENT-002 AC-DEP-002-03
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ToolResult:
    """Result of a single tool validation check."""

    tool: str
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None


@dataclass
class HealthReport:
    """Aggregated toolchain health report."""

    tools: List[ToolResult] = field(default_factory=list)
    all_healthy: bool = True

    def as_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "all_healthy": self.all_healthy,
            "tools": [
                {
                    "tool": t.tool,
                    "available": t.available,
                    "version": t.version,
                    "error": t.error,
                }
                for t in self.tools
            ],
        }


class ToolchainValidator:
    """Validate that all required dev-tools are installed and functional.

    Args:
        workspace: Path to the project workspace root.
    """

    def __init__(self, workspace: Path) -> None:
        """Initialize validator for the given workspace.

        Args:
            workspace: Root directory of the project.
        """
        self.workspace = workspace

    # ------------------------------------------------------------------
    # Individual tool validators
    # ------------------------------------------------------------------

    def validate_pytest(self) -> ToolResult:
        """Validate pytest availability.

        Returns:
            ToolResult indicating whether pytest is available.
        """
        return self._check_tool("pytest", ["pytest", "--version"])

    def validate_mypy(self) -> ToolResult:
        """Validate mypy availability.

        Returns:
            ToolResult indicating whether mypy is available.
        """
        return self._check_tool("mypy", ["mypy", "--version"])

    def validate_ruff(self) -> ToolResult:
        """Validate ruff availability.

        Returns:
            ToolResult indicating whether ruff is available.
        """
        return self._check_tool("ruff", ["ruff", "--version"])

    def validate_git(self) -> ToolResult:
        """Validate git availability.

        Returns:
            ToolResult indicating whether git is available.
        """
        return self._check_tool("git", ["git", "--version"])

    # ------------------------------------------------------------------
    # Report generation
    # ------------------------------------------------------------------

    def generate_health_report(self) -> HealthReport:
        """Generate a comprehensive toolchain health report.

        Returns:
            HealthReport with results for all tools.
        """
        checkers = [
            self.validate_pytest,
            self.validate_mypy,
            self.validate_ruff,
            self.validate_git,
        ]

        results: List[ToolResult] = [checker() for checker in checkers]
        all_healthy = all(r.available for r in results)

        return HealthReport(tools=results, all_healthy=all_healthy)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_tool(self, name: str, cmd: List[str]) -> ToolResult:
        """Run a tool version check and return a ToolResult.

        Args:
            name: Human-readable tool name.
            cmd: Command list to execute.

        Returns:
            ToolResult with availability and version info.
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version = (result.stdout or result.stderr or "").strip().splitlines()[0]
                return ToolResult(tool=name, available=True, version=version or None)
            return ToolResult(tool=name, available=False, error=result.stderr.strip())
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return ToolResult(tool=name, available=False, error=str(exc))
