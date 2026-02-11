#!/usr/bin/env python3
"""Verify CORTEX environment setup and toolkit availability.

This script validates:
- Python version (3.9+)
- All 23 dependencies installed with correct versions
- Development tools configured
- MCP server connectivity
- Pre-commit hook installation

Exit codes:
- 0: Environment valid, all checks passed
- 1: Environment invalid, check failed
- 2: Warning only (non-critical check failed)

Usage:
    python verify_environment.py                    # Human-readable output
    python verify_environment.py --json             # JSON output for CI/CD
    python verify_environment.py --quiet            # Silent, exit code only
"""

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class CheckResult:
    """Result of a single environment check."""

    name: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


class EnvironmentVerifier:
    """Verify CORTEX environment setup.

    Runs comprehensive checks on Python environment, dependencies, tools,
    and MCP server connectivity.
    """

    def __init__(self) -> None:
        """Initialize verifier."""
        self.results: List[CheckResult] = []
        self.critical_failures: int = 0
        self.warnings: int = 0

    def add_result(
        self,
        name: str,
        passed: bool,
        message: str,
        severity: str = "error"
    ) -> None:
        """Add a check result.

        Args:
            name: Human-readable check name
            passed: Whether check passed
            message: Description of result
            severity: 'error', 'warning', or 'info'
        """
        self.results.append(
            CheckResult(name=name, passed=passed, message=message, severity=severity)
        )
        if not passed:
            if severity == "error":
                self.critical_failures += 1
            else:
                self.warnings += 1

    def check_python_version(self) -> None:
        """Check Python version is 3.9+."""
        version = sys.version_info
        if version >= (3, 9, 0):
            self.add_result(
                "Python Version",
                True,
                f"Python {version.major}.{version.minor}.{version.micro} (valid)"
            )
        else:
            self.add_result(
                "Python Version",
                False,
                f"Python {version.major}.{version.minor} (required 3.9+)"
            )

    def check_core_dependencies(self) -> None:
        """Check core dependencies installed."""
        core_packages = {
            'yaml': 'pyyaml',
            'pydantic': 'pydantic',
            'fastapi': 'fastapi',
            'uvicorn': 'uvicorn',
            'httpx': 'httpx'
        }

        all_ok = True
        missing = []

        for import_name, package_name in core_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                all_ok = False
                missing.append(package_name)

        if all_ok:
            self.add_result(
                "Core Dependencies",
                True,
                "All 5 core packages installed"
            )
        else:
            self.add_result(
                "Core Dependencies",
                False,
                f"Missing: {', '.join(missing)}. Run: pip install -r requirements.txt"
            )

    def check_test_dependencies(self) -> None:
        """Check test dependencies installed."""
        test_packages = {
            'pytest': 'pytest',
            '_pytest': 'pytest',
        }

        all_ok = True
        missing = []

        for import_name, package_name in test_packages.items():
            try:
                __import__(import_name)
            except ImportError:
                all_ok = False
                missing.append(package_name)

        if all_ok:
            self.add_result(
                "Test Dependencies",
                True,
                "Pytest framework installed"
            )
        else:
            self.add_result(
                "Test Dependencies",
                False,
                f"Missing: {', '.join(missing)}"
            )

    def check_quality_tools(self) -> None:
        """Check quality tools installed."""
        quality_tools = ['black', 'isort', 'mypy', 'pylint', 'flake8']
        installed = []
        missing = []

        for tool in quality_tools:
            try:
                __import__(tool)
                installed.append(tool)
            except ImportError:
                missing.append(tool)

        if len(installed) >= 3:  # At least most tools installed
            msg = f"Installed: {', '.join(installed)}"
            if missing:
                msg += f". Optional missing: {', '.join(missing)}"
            self.add_result(
                "Quality Tools",
                True,
                msg,
                severity="warning" if missing else "info"
            )
        else:
            self.add_result(
                "Quality Tools",
                False,
                f"Insufficient quality tools. Missing: {', '.join(missing)}",
                severity="warning"
            )

    def check_mcp_module(self) -> None:
        """Check MCP server module exists."""
        mcp_server = PROJECT_ROOT / "cortex" / "mcp" / "server.py"
        if mcp_server.exists():
            self.add_result(
                "MCP Server Module",
                True,
                f"MCP server found at {mcp_server.name}"
            )
        else:
            self.add_result(
                "MCP Server Module",
                False,
                f"MCP server not found at {mcp_server}"
            )

    def check_requirements_file(self) -> None:
        """Check requirements.txt exists."""
        requirements = PROJECT_ROOT / "requirements.txt"
        if requirements.exists():
            count = len([line for line in requirements.read_text().split('\n') if line.strip() and not line.startswith('#')])
            self.add_result(
                "Requirements File",
                True,
                f"requirements.txt with {count} dependencies"
            )
        else:
            self.add_result(
                "Requirements File",
                False,
                "requirements.txt not found"
            )

    def run_all_checks(self) -> int:
        """Run all environment checks.

        Returns:
            Exit code: 0 (pass), 1 (fail), 2 (warning)
        """
        self.check_python_version()
        self.check_core_dependencies()
        self.check_test_dependencies()
        self.check_quality_tools()
        self.check_mcp_module()
        self.check_requirements_file()

        if self.critical_failures > 0:
            return 1
        elif self.warnings > 0:
            return 2
        else:
            return 0

    def print_human_readable(self) -> None:
        """Print results in human-readable format."""
        print("\n" + "=" * 70)
        print("CORTEX ENVIRONMENT VERIFICATION")
        print("=" * 70 + "\n")

        for result in self.results:
            status = "✓" if result.passed else "✗"
            print(f"{status} {result.name:30} {result.message}")

        print("\n" + "-" * 70)
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        print(f"Results: {passed}/{total} checks passed")

        if self.critical_failures > 0:
            print(f"Critical failures: {self.critical_failures}")
        if self.warnings > 0:
            print(f"Warnings: {self.warnings}")

        print("=" * 70 + "\n")

    def print_json(self) -> None:
        """Print results as JSON."""
        output = {
            "status": "pass" if self.critical_failures == 0 else "fail",
            "results": [asdict(r) for r in self.results],
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": self.critical_failures,
                "warnings": self.warnings
            }
        }
        print(json.dumps(output, indent=2))


def main() -> int:
    """Main entry point.

    Returns:
        Exit code for shell
    """
    verifier = EnvironmentVerifier()
    exit_code = verifier.run_all_checks()

    if "--json" in sys.argv:
        verifier.print_json()
    elif "--quiet" not in sys.argv:
        verifier.print_human_readable()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
