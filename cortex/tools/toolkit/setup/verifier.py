"""
Setup Verifier - Cross-Platform Environment Verification

Consolidates setup verification logic from multiple scripts.

**Source Scripts:**
- .cortex-runtime/verify-setup.py
- .cortex-runtime/verify-autonomous-setup.py
- .cortex-runtime/setup-mcp.py (verify functions)

**Authority:** Phase 90 S-90-04
**Author:** Asif Hussain
**Created:** 2026-02-16
"""
# CORE-035 — domain-scoped; class name appropriate for this module

import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class VerificationResult:  # CORE-035-scoped — domain-specific variant
    """Result of a verification check."""

    check_name: str
    passed: bool
    message: str
    details: Optional[Dict] = None
    severity: str = "INFO"  # INFO, WARNING, ERROR


class SetupVerifier:  # CORE-035-scoped — domain-specific variant
    """
    Cross-platform setup verifier.

    Consolidates setup verification logic with platform-aware checks
    for Windows, macOS, and Linux environments.
    """

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        """
        Initialize setup verifier.

        Args:
            workspace_root: Root directory of CORTEX workspace.
                           Defaults to current working directory.
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.platform = platform.system()  # Windows, Darwin, Linux
        self.results: List[VerificationResult] = []

    def verify_environment(self) -> List[VerificationResult]:
        """
        Run comprehensive environment verification.

        Returns:
            List of verification results.
        """
        self.results = []

        self._check_python_version()
        self._check_virtual_environment()
        self._check_dependencies()
        self._check_vscode_settings()
        self._check_mcp_configuration()
        self._check_git_configuration()

        return self.results

    def _check_python_version(self) -> None:
        """Check Python version meets requirements."""
        min_version = (3, 9)
        current_version = sys.version_info[:2]

        passed = current_version >= min_version

        result = VerificationResult(
            check_name="Python Version",
            passed=passed,
            message=f"Python {current_version[0]}.{current_version[1]} {'✓' if passed else '✗ (requires 3.9+)'}",
            details={
                "version": f"{current_version[0]}.{current_version[1]}.{sys.version_info[2]}",
                "executable": sys.executable,
                "platform": self.platform,
            },
        )

        if not passed:
            result.severity = "ERROR"

        self.results.append(result)

    def _check_virtual_environment(self) -> None:
        """Check virtual environment configuration."""
        venv_paths = self._get_venv_paths()

        venv_found = None
        for path in venv_paths:
            if path.exists():
                venv_found = path
                break

        # Check if currently running in venv
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

        result = VerificationResult(
            check_name="Virtual Environment",
            passed=venv_found is not None,
            message="Virtual environment configured" if venv_found else "Virtual environment NOT FOUND",
            details={
                "venv_path": str(venv_found) if venv_found else None,
                "in_venv": in_venv,
                "platform": self.platform,
                "searched_paths": [str(p) for p in venv_paths],
            },
        )

        if not venv_found:
            result.severity = "ERROR"
        elif not in_venv:
            result.severity = "WARNING"
            result.message += " (not currently activated)"

        self.results.append(result)

    def _check_dependencies(self) -> None:
        """Check required dependencies are installed."""
        required_packages = [
            "pytest",
            "pydantic",
            "pyyaml",
            "fastapi",
        ]

        missing = []
        installed = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                installed.append(package)
            except ImportError:
                missing.append(package)

        passed = len(missing) == 0

        result = VerificationResult(
            check_name="Dependencies",
            passed=passed,
            message=f"{len(installed)}/{len(required_packages)} required packages installed",
            details={
                "installed": installed,
                "missing": missing,
            },
        )

        if not passed:
            result.severity = "ERROR"

        self.results.append(result)

    def _check_vscode_settings(self) -> None:
        """Check VS Code settings configuration."""
        settings_path = self.workspace_root / ".vscode" / "settings.json"

        if not settings_path.exists():
            self.results.append(
                VerificationResult(
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

            has_mcp = "github.copilot.chat.mcpServers" in settings
            has_cortex = False

            if has_mcp:
                mcp_config = settings["github.copilot.chat.mcpServers"]
                has_cortex = "cortex" in mcp_config

            passed = has_cortex

            result = VerificationResult(
                check_name="VS Code Settings",
                passed=passed,
                message="MCP server configured" if passed else "MCP server NOT configured",
                details={
                    "has_mcp_config": has_mcp,
                    "has_cortex_server": has_cortex,
                },
            )

            if not passed:
                result.severity = "ERROR"

            self.results.append(result)

        except json.JSONDecodeError:
            self.results.append(
                VerificationResult(
                    check_name="VS Code Settings",
                    passed=False,
                    message="Invalid JSON in settings.json",
                    severity="ERROR",
                )
            )

    def _check_mcp_configuration(self) -> None:
        """Check MCP server configuration."""
        # Check if MCP module is importable
        try:
            import cortex.mcp  # noqa: F401

            result = VerificationResult(
                check_name="MCP Configuration",
                passed=True,
                message="MCP module available",
            )
        except ImportError:
            result = VerificationResult(
                check_name="MCP Configuration",
                passed=False,
                message="MCP module NOT importable",
                severity="ERROR",
            )

        self.results.append(result)

    def _check_git_configuration(self) -> None:
        """Check git configuration."""
        git_dir = self.workspace_root / ".git"

        if not git_dir.exists():
            self.results.append(
                VerificationResult(
                    check_name="Git Configuration",
                    passed=False,
                    message="Not a git repository",
                    severity="WARNING",
                )
            )
            return

        try:
            # Check git hooks
            hooks_path = self.workspace_root / ".githooks"
            has_hooks = hooks_path.exists()

            # Check git config
            result_proc = subprocess.run(
                ["git", "config", "core.hooksPath"],
                capture_output=True,
                text=True,
                cwd=str(self.workspace_root),
            )

            hooks_configured = result_proc.returncode == 0 and ".githooks" in result_proc.stdout

            passed = has_hooks and hooks_configured

            result = VerificationResult(
                check_name="Git Configuration",
                passed=passed,
                message="Git hooks configured" if passed else "Git hooks NOT configured",
                details={
                    "hooks_exist": has_hooks,
                    "hooks_configured": hooks_configured,
                },
            )

            if not passed:
                result.severity = "WARNING"

            self.results.append(result)

        except Exception as e:
            self.results.append(
                VerificationResult(
                    check_name="Git Configuration",
                    passed=False,
                    message=f"Git check failed: {e}",
                    severity="WARNING",
                )
            )

    def _get_venv_paths(self) -> List[Path]:
        """Get platform-specific virtual environment paths."""
        if self.platform == "Windows":
            return [
                self.workspace_root / ".venv" / "Scripts" / "python.exe",
            ]
        else:  # macOS, Linux
            return [
                self.workspace_root / ".venv" / "bin" / "python",
            ]

    def generate_report(self) -> str:
        """
        Generate formatted verification report.

        Returns:
            Formatted text report of all verification results.
        """
        lines = []
        lines.append("=" * 80)
        lines.append("CORTEX SETUP VERIFICATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        passed_count = sum(1 for r in self.results if r.passed)
        total_count = len(self.results)

        lines.append(f"Platform: {self.platform}")
        lines.append(f"Workspace: {self.workspace_root}")
        lines.append(f"Status: {passed_count}/{total_count} checks passed")
        lines.append("")

        for i, result in enumerate(self.results, 1):
            status = "✅" if result.passed else "❌"
            lines.append(f"{i}. {status} {result.check_name}")
            lines.append(f"   {result.message}")

            if result.severity != "INFO":
                lines.append(f"   Severity: {result.severity}")

            lines.append("")

        lines.append("=" * 80)

        if passed_count == total_count:
            lines.append("✅ ENVIRONMENT READY")
            lines.append("")
            lines.append("Next Steps:")
            lines.append("1. Reload VS Code: Command Palette → Developer: Reload Window")
            lines.append("2. Start development")
        else:
            lines.append(f"⚠️  {total_count - passed_count} CHECK(S) FAILED")
            lines.append("")
            lines.append("Resolution:")
            lines.append("1. Review failed checks above")
            lines.append("2. Run: python .cortex-runtime/setup-mcp.py")
            lines.append("3. Re-run verification")

        lines.append("=" * 80)

        return "\n".join(lines)

    def all_passed(self) -> bool:
        """Check if all verifications passed."""
        return all(r.passed for r in self.results)

    def get_failed_checks(self) -> List[VerificationResult]:
        """Get list of failed verification checks."""
        return [r for r in self.results if not r.passed]
