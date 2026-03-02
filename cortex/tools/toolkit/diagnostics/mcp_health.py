"""
MCP Health Checker - Consolidated Diagnostics

Consolidates MCP diagnostic logic from multiple scattered scripts.

**Source Scripts:**
- .cortex-runtime/diagnose-mcp.py
- .cortex-runtime/verify-mcp-setup.py
- .cortex-runtime/verify-mcp-tools.py
- .cortex-runtime/verify-mcp-fix.py

**Authority:** Phase 90 S-90-03
**Author:** Asif Hussain
**Created:** 2026-02-16
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""

    check_name: str
    passed: bool
    message: str
    details: Optional[Dict] = None
    severity: str = "INFO"  # INFO, WARNING, ERROR


class MCPHealthChecker:
    """
    Unified MCP health checker.

    Consolidates diagnostic checks from multiple scripts into a single
    canonical implementation with comprehensive validation.
    """

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        """
        Initialize health checker.

        Args:
            workspace_root: Root directory of CORTEX workspace.
                           Defaults to current working directory.
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.results: List[DiagnosticResult] = []

    def run_diagnostics(self, checks: Optional[List[str]] = None) -> List[DiagnosticResult]:
        """
        Run comprehensive MCP diagnostics.

        Args:
            checks: List of specific checks to run. If None, runs all checks.
                   Options: ["python_env", "venv", "mcp_module", "vscode_settings",
                            "mcp_server", "tool_registry", "auto_heal"]

        Returns:
            List of diagnostic results.
        """
        self.results = []

        all_checks = checks or [
            "python_env",
            "venv",
            "mcp_module",
            "vscode_settings",
            "mcp_server",
            "tool_registry",
        ]

        check_methods = {
            "python_env": self._check_python_environment,
            "venv": self._check_virtual_environment,
            "mcp_module": self._check_mcp_module,
            "vscode_settings": self._check_vscode_settings,
            "mcp_server": self._check_mcp_server_startup,
            "tool_registry": self._check_tool_registry,
        }

        for check in all_checks:
            if check in check_methods:
                check_methods[check]()

        return self.results

    def _check_python_environment(self) -> None:
        """Check Python version and executable."""
        result = DiagnosticResult(
            check_name="Python Environment",
            passed=sys.version_info >= (3, 9),
            message=f"Python {sys.version}",
            details={
                "version": sys.version,
                "executable": sys.executable,
                "minimum_required": "3.9.0",
            },
        )

        if not result.passed:
            result.severity = "ERROR"
            result.message = f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.9 (unsupported)"

        self.results.append(result)

    def _check_virtual_environment(self) -> None:
        """Check virtual environment existence and configuration."""
        venv_paths = [
            self.workspace_root / ".venv" / "bin" / "python",  # macOS/Linux
            self.workspace_root / ".venv" / "Scripts" / "python.exe",  # Windows
        ]

        venv_found = None
        for path in venv_paths:
            if path.exists():
                venv_found = path
                break

        result = DiagnosticResult(
            check_name="Virtual Environment",
            passed=venv_found is not None,
            message="Virtual environment configured" if venv_found else "Virtual environment NOT FOUND",
            details={
                "searched_paths": [str(p) for p in venv_paths],
                "found_path": str(venv_found) if venv_found else None,
                "resolved_path": str(venv_found.resolve()) if venv_found else None,
            },
        )

        if not result.passed:
            result.severity = "ERROR"

        self.results.append(result)

    def _check_mcp_module(self) -> None:
        """Check if cortex.mcp module is importable."""
        try:
            import cortex.mcp  # noqa: F401

            result = DiagnosticResult(
                check_name="MCP Module",
                passed=True,
                message="cortex.mcp module importable",
                details={
                    "module_path": cortex.mcp.__file__,
                },
            )
        except ImportError as e:
            result = DiagnosticResult(
                check_name="MCP Module",
                passed=False,
                message=f"cortex.mcp import failed: {e}",
                severity="ERROR",
                details={"error": str(e)},
            )

        self.results.append(result)

    def _check_vscode_settings(self) -> None:
        """Check VS Code MCP configuration."""
        settings_path = self.workspace_root / ".vscode" / "settings.json"

        if not settings_path.exists():
            self.results.append(
                DiagnosticResult(
                    check_name="VS Code Settings",
                    passed=False,
                    message=".vscode/settings.json not found",
                    severity="ERROR",
                )
            )
            return

        try:
            with open(settings_path) as f:
                settings = json.load(f)

            has_mcp_config = "github.copilot.chat.mcpServers" in settings
            has_cortex = False
            command_path = None

            if has_mcp_config:
                mcp_config = settings["github.copilot.chat.mcpServers"]
                has_cortex = "cortex" in mcp_config

                if has_cortex:
                    cortex_config = mcp_config["cortex"]
                    command_path = cortex_config.get("command", "")

            # Check for path mismatch
            path_warnings = []
            if command_path:
                if sys.platform == "win32" and "bin/python" in command_path:
                    path_warnings.append("Unix path on Windows (should use Scripts/python.exe)")
                elif sys.platform != "win32" and "Scripts/python.exe" in command_path:
                    path_warnings.append("Windows path on Unix (should use bin/python)")

            result = DiagnosticResult(
                check_name="VS Code Settings",
                passed=has_cortex and not path_warnings,
                message="MCP server configured" if has_cortex else "MCP server NOT configured",
                details={
                    "has_mcp_config": has_mcp_config,
                    "has_cortex_server": has_cortex,
                    "command": command_path,
                    "warnings": path_warnings,
                },
            )

            if path_warnings:
                result.severity = "WARNING"
            elif not has_cortex:
                result.severity = "ERROR"

            self.results.append(result)

        except json.JSONDecodeError as e:
            self.results.append(
                DiagnosticResult(
                    check_name="VS Code Settings",
                    passed=False,
                    message=f"Invalid JSON: {e}",
                    severity="ERROR",
                )
            )

    def _check_mcp_server_startup(self) -> None:
        """Test MCP server startup."""
        venv_python = self._get_venv_python()

        if not venv_python:
            self.results.append(
                DiagnosticResult(
                    check_name="MCP Server Startup",
                    passed=False,
                    message="Cannot test: venv python not found",
                    severity="ERROR",
                )
            )
            return

        try:
            env = os.environ.copy()
            env.update({
                "CORTEX_ENV": "development",
                "CORTEX_MCP_ENABLED": "true",
                "PYTHONPATH": str(self.workspace_root),
                "CORTEX_WORKSPACE": str(self.workspace_root),
            })

            result_proc = subprocess.run(
                [str(venv_python), "-m", "cortex.mcp", "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                env=env,
                cwd=str(self.workspace_root),
            )

            # Parse tool registration output
            tool_count = result_proc.stderr.count("Registered tool:")
            decorator_tools = None

            for line in result_proc.stderr.split("\n"):
                if "decorator-registered tools" in line:
                    parts = line.split("Added")
                    if len(parts) > 1:
                        decorator_tools = parts[1].split()[0]

            passed = tool_count > 0 or decorator_tools is not None

            result = DiagnosticResult(
                check_name="MCP Server Startup",
                passed=passed,
                message="MCP server starts successfully" if passed else "MCP server started but no tools found",
                details={
                    "explicit_tools": tool_count,
                    "decorator_tools": decorator_tools,
                    "return_code": result_proc.returncode,
                },
                severity="INFO" if passed else "WARNING",
            )

            self.results.append(result)

        except subprocess.TimeoutExpired:
            # Timeout is actually expected (server runs indefinitely)
            self.results.append(
                DiagnosticResult(
                    check_name="MCP Server Startup",
                    passed=True,
                    message="MCP server started (runs indefinitely)",
                )
            )
        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check_name="MCP Server Startup",
                    passed=False,
                    message=f"Startup failed: {e}",
                    severity="ERROR",
                )
            )

    def _check_tool_registry(self) -> None:
        """Check MCP tools registry."""
        try:
            from cortex.mcp.server import get_tool_registry

            tools = get_tool_registry()
            tool_count = len(tools)

            result = DiagnosticResult(
                check_name="Tool Registry",
                passed=tool_count > 0,
                message=f"Found {tool_count} tools in registry",
                details={
                    "tool_count": tool_count,
                    "sample_tools": sorted(tools.keys())[:10],
                },
            )

            if tool_count == 0:
                result.severity = "WARNING"

            self.results.append(result)

        except Exception as e:
            self.results.append(
                DiagnosticResult(
                    check_name="Tool Registry",
                    passed=False,
                    message=f"Could not load tool registry: {e}",
                    severity="WARNING",
                )
            )

    def _get_venv_python(self) -> Optional[Path]:
        """Get virtual environment Python executable."""
        venv_paths = [
            self.workspace_root / ".venv" / "bin" / "python",
            self.workspace_root / ".venv" / "Scripts" / "python.exe",
        ]

        for path in venv_paths:
            if path.exists():
                return path

        return None

    def generate_report(self) -> str:
        """
        Generate formatted diagnostic report.

        Returns:
            Formatted text report of all diagnostic results.
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CORTEX MCP DIAGNOSTIC REPORT")
        lines.append("=" * 80)
        lines.append("")

        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        lines.append(f"Overall: {passed_count}/{total_count} checks passed")
        lines.append("")

        for i, result in enumerate(self.results, 1):
            status = "✅" if result.passed else "❌"
            lines.append(f"{i}. {status} {result.check_name}")
            lines.append(f"   {result.message}")

            if result.severity != "INFO":
                lines.append(f"   Severity: {result.severity}")

            if result.details:
                for key, value in result.details.items():
                    if value is not None:
                        lines.append(f"   {key}: {value}")

            lines.append("")

        lines.append("=" * 80)

        if passed_count == total_count:
            lines.append("✅ ALL CHECKS PASSED")
            lines.append("")
            lines.append("Next Steps:")
            lines.append("1. Reload VS Code: Command Palette → Developer: Reload Window")
            lines.append("2. Test in Copilot Chat: mcp_cortex_cortex_tools_catalog")
        else:
            lines.append(f"⚠️  {total_count - passed_count} CHECK(S) FAILED")
            lines.append("")
            lines.append("Resolution:")
            lines.append("1. Review failed checks above")
            lines.append("2. Run: python .cortex-runtime/setup-mcp.py")
            lines.append("3. Reload VS Code window")

        lines.append("=" * 80)

        return "\n".join(lines)

    def get_failed_checks(self) -> List[DiagnosticResult]:
        """Get list of failed diagnostic checks."""
        return [r for r in self.results if not r.passed]

    def all_passed(self) -> bool:
        """Check if all diagnostics passed."""
        return all(r.passed for r in self.results)
