"""Toolchain validator for development environment health checks.

This module provides the ToolchainValidator class that validates
the development toolchain (pytest, mypy, ruff, git).

PHASE-DEPLOYMENT-002: AC-DEP-002-03
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class ToolValidationResult:
    """Result of tool validation.

    Attributes:
        available: Whether the tool is available.
        version: Tool version if available.
        working: Whether the tool works correctly.
        error: Error message if validation failed.
    """
    available: bool = False
    version: Optional[str] = None
    working: bool = False
    error: str = ""


@dataclass
class HealthReport:
    """Complete toolchain health report.

    Attributes:
        tools: Dict of tool name → validation result.
        overall_healthy: Whether all tools are healthy.
        timestamp: When the report was generated.
    """
    tools: Dict[str, ToolValidationResult] = field(default_factory=dict)
    overall_healthy: bool = True
    timestamp: str = ""


class ToolchainValidator:
    """Validates development toolchain health.

    Checks that all required tools (pytest, mypy, ruff, git) are
    available and working correctly.

    Attributes:
        workspace: Path to the workspace root.
    """

    REQUIRED_TOOLS = ["pytest", "mypy", "ruff", "git"]

    def __init__(self, workspace: Path) -> None:
        """Initialize the validator.

        Args:
            workspace: Path to the workspace root.
        """
        self.workspace = Path(workspace)

    def _run_command(self, command: List[str]) -> tuple[bool, str]:
        """Run a command and capture output.

        Args:
            command: Command and arguments to run.

        Returns:
            Tuple of (success, output).
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0, result.stdout or result.stderr
        except FileNotFoundError:
            return False, "Command not found"
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def _extract_version(self, output: str) -> Optional[str]:
        """Extract version number from command output.

        Args:
            output: Command output.

        Returns:
            Version string or None.
        """
        import re
        match = re.search(r'(\d+\.\d+(?:\.\d+)?)', output)
        return match.group(1) if match else None

    def validate_pytest(self) -> ToolValidationResult:
        """Validate pytest is available and working.

        Returns:
            ToolValidationResult for pytest.
        """
        result = ToolValidationResult()

        # Check version
        success, output = self._run_command(["python", "-m", "pytest", "--version"])

        if success:
            result.available = True
            result.version = self._extract_version(output)
            result.working = True
        else:
            # Try direct command
            success, output = self._run_command(["pytest", "--version"])
            if success:
                result.available = True
                result.version = self._extract_version(output)
                result.working = True
            else:
                result.error = output

        return result

    def validate_mypy(self) -> ToolValidationResult:
        """Validate mypy is available and working.

        Returns:
            ToolValidationResult for mypy.
        """
        result = ToolValidationResult()

        success, output = self._run_command(["python", "-m", "mypy", "--version"])

        if success:
            result.available = True
            result.version = self._extract_version(output)
            result.working = True
        else:
            success, output = self._run_command(["mypy", "--version"])
            if success:
                result.available = True
                result.version = self._extract_version(output)
                result.working = True
            else:
                result.error = output

        return result

    def validate_ruff(self) -> ToolValidationResult:
        """Validate ruff is available and working.

        Returns:
            ToolValidationResult for ruff.
        """
        result = ToolValidationResult()

        success, output = self._run_command(["ruff", "--version"])

        if success:
            result.available = True
            result.version = self._extract_version(output)
            result.working = True
        else:
            result.error = output

        return result

    def validate_git(self) -> ToolValidationResult:
        """Validate git is available and repo is valid.

        Returns:
            ToolValidationResult for git.
        """
        result = ToolValidationResult()

        success, output = self._run_command(["git", "--version"])

        if success:
            result.available = True
            result.version = self._extract_version(output)

            # Check if we're in a git repo
            repo_success, _ = self._run_command(["git", "rev-parse", "--git-dir"])
            result.working = repo_success

            if not repo_success:
                result.error = "Not in a git repository"
        else:
            result.error = output

        return result

    def validate_all(self) -> Dict[str, ToolValidationResult]:
        """Validate all tools.

        Returns:
            Dict of tool name → validation result.
        """
        return {
            "pytest": self.validate_pytest(),
            "mypy": self.validate_mypy(),
            "ruff": self.validate_ruff(),
            "git": self.validate_git(),
        }

    def generate_health_report(self) -> HealthReport:
        """Generate tool_health.yaml report.

        Returns:
            HealthReport with all tool validations.
        """
        from datetime import datetime

        tools = self.validate_all()

        report = HealthReport(
            tools=tools,
            overall_healthy=all(t.available and t.working for t in tools.values()),
            timestamp=datetime.now().isoformat(),
        )

        # Write to file
        report_path = self.workspace / "tool_health.yaml"
        report_dict = {
            "timestamp": report.timestamp,
            "overall_healthy": report.overall_healthy,
            "tools": {
                name: {
                    "available": result.available,
                    "version": result.version,
                    "working": result.working,
                    "error": result.error or None,
                }
                for name, result in report.tools.items()
            }
        }
        report_path.write_text(yaml.dump(report_dict, default_flow_style=False))

        return report


def main() -> int:
    """CLI entry point for toolchain validator.

    Returns:
        Exit code.
    """
    workspace = Path.cwd()

    validator = ToolchainValidator(workspace)
    report = validator.generate_health_report()

    print(f"Toolchain Health Report ({report.timestamp})")
    print("=" * 50)

    for name, result in report.tools.items():
        status = "✅" if result.available and result.working else "❌"
        version = f"v{result.version}" if result.version else "unknown"
        print(f"  {status} {name}: {version}")
        if result.error:
            print(f"      Error: {result.error}")

    print("=" * 50)
    print(f"Overall: {'✅ Healthy' if report.overall_healthy else '❌ Issues found'}")

    return 0 if report.overall_healthy else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
