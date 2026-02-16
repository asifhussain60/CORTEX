"""
Setup Verification Module.

Consolidated setup verification and environment configuration.
Replaces: verify-setup.py, verify-autonomous-setup.py, setup-mcp.py checks

AC_START: AC-P90-S3-T1
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import sys
import platform
import subprocess


class SetupCheck(str, Enum):
    """Setup verification checks."""
    
    VIRTUAL_ENV = "virtual_env"
    DEPENDENCIES = "dependencies"
    MCP_CONFIG = "mcp_config"
    VSCODE_SETTINGS = "vscode_settings"
    PYTHON_VERSION = "python_version"


@dataclass
class SetupResult:
    """Result of a setup verification check."""
    
    check: SetupCheck
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    autofix_available: bool = False
    fix_command: Optional[str] = None


class SetupVerifier:
    """
    Consolidated setup verification.
    
    Verifies Python environment, dependencies, MCP configuration,
    and VS Code settings. Provides auto-fix recommendations.
    """
    
    def __init__(self, workspace_root: Path = Path.cwd()) -> None:
        """
        Initialize setup verifier.
        
        Args:
            workspace_root: CORTEX workspace root directory
        """
        self.workspace_root = workspace_root
    
    def check_virtual_environment(self) -> SetupResult:
        """
        Check if virtual environment is activated.
        
        Returns:
            Setup result for virtual environment check
        """
        # Check if running in venv
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        if in_venv:
            return SetupResult(
                check=SetupCheck.VIRTUAL_ENV,
                passed=True,
                message=f"Virtual environment active: {sys.prefix}",
                details={"venv_path": sys.prefix},
            )
        else:
            return SetupResult(
                check=SetupCheck.VIRTUAL_ENV,
                passed=False,
                message="Virtual environment not activated",
                autofix_available=True,
                fix_command="source venv/bin/activate  # macOS/Linux\nvenv\\Scripts\\activate  # Windows",
            )
    
    def check_dependencies(self) -> SetupResult:
        """
        Check if required dependencies are installed.
        
        Returns:
            Setup result for dependencies check
        """
        required_packages = ["yaml", "pytest", "jinja2"]
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            return SetupResult(
                check=SetupCheck.DEPENDENCIES,
                passed=True,
                message="All required dependencies installed",
                details={"required": required_packages},
            )
        else:
            return SetupResult(
                check=SetupCheck.DEPENDENCIES,
                passed=False,
                message=f"Missing dependencies: {', '.join(missing)}",
                details={"missing": missing},
                autofix_available=True,
                fix_command=f"pip install {' '.join(missing)}",
            )
    
    def check_mcp_configuration(self) -> SetupResult:
        """
        Check if MCP server is configured.
        
        Returns:
            Setup result for MCP configuration check
        """
        try:
            from cortex.mcp.server import MCPServer
            
            return SetupResult(
                check=SetupCheck.MCP_CONFIG,
                passed=True,
                message="MCP server configured",
                details={"module": "cortex.mcp.server"},
            )
        except ImportError:
            return SetupResult(
                check=SetupCheck.MCP_CONFIG,
                passed=False,
                message="MCP server not configured",
                autofix_available=True,
                fix_command="python .cortex/setup-mcp.py",
            )
    
    def check_vscode_settings(self) -> SetupResult:
        """
        Check if VS Code settings.json exists and is valid.
        
        Returns:
            Setup result for VS Code settings check
        """
        settings_path = self.workspace_root / ".vscode" / "settings.json"
        
        if not settings_path.exists():
            return SetupResult(
                check=SetupCheck.VSCODE_SETTINGS,
                passed=False,
                message="VS Code settings.json not found",
                autofix_available=True,
                fix_command="python .cortex/setup-mcp.py",
            )
        
        try:
            import json
            with open(settings_path) as f:
                settings = json.load(f)
            
            return SetupResult(
                check=SetupCheck.VSCODE_SETTINGS,
                passed=True,
                message="VS Code settings.json valid",
                details={"path": str(settings_path)},
            )
        except json.JSONDecodeError:
            return SetupResult(
                check=SetupCheck.VSCODE_SETTINGS,
                passed=False,
                message="Invalid JSON in settings.json",
                autofix_available=True,
                fix_command="python .cortex/setup-mcp.py",
            )
    
    def check_python_version(self) -> SetupResult:
        """
        Check Python version compatibility.
        
        Returns:
            Setup result for Python version check
        """
        version_info = sys.version_info
        
        if version_info.major >= 3 and version_info.minor >= 9:
            return SetupResult(
                check=SetupCheck.PYTHON_VERSION,
                passed=True,
                message=f"Python {version_info.major}.{version_info.minor}.{version_info.micro}",
                details={"version": f"{version_info.major}.{version_info.minor}.{version_info.micro}"},
            )
        else:
            return SetupResult(
                check=SetupCheck.PYTHON_VERSION,
                passed=False,
                message=f"Python {version_info.major}.{version_info.minor} < 3.9",
                autofix_available=False,
                fix_command="Upgrade to Python 3.9+",
            )
    
    def run_full_verification(self) -> List[SetupResult]:
        """
        Run full setup verification suite.
        
        Returns:
            List of setup results
        """
        return [
            self.check_python_version(),
            self.check_virtual_environment(),
            self.check_dependencies(),
            self.check_mcp_configuration(),
            self.check_vscode_settings(),
        ]
    
    def generate_fix_commands(self, result: SetupResult) -> List[str]:
        """
        Generate fix commands for a failed check.
        
        Args:
            result: Setup result that failed
            
        Returns:
            List of fix commands
        """
        if not result.autofix_available or not result.fix_command:
            return []
        
        # Split multi-line commands
        commands = [cmd.strip() for cmd in result.fix_command.split("\n")]
        return [cmd for cmd in commands if cmd and not cmd.startswith("#")]
    
    def generate_report(self, results: List[SetupResult]) -> Dict[str, Any]:
        """
        Generate setup verification report.
        
        Args:
            results: List of setup results
            
        Returns:
            Complete report dictionary
        """
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]
        
        # Gather recommendations
        recommendations = []
        for result in failed:
            if result.autofix_available and result.fix_command:
                recommendations.append({
                    "check": result.check.value,
                    "command": result.fix_command,
                })
        
        # Environment info
        environment = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "platform_version": platform.version(),
            "workspace": str(self.workspace_root),
        }
        
        return {
            "summary": {
                "total_checks": len(results),
                "passed": len(passed),
                "failed": len(failed),
                "status": "ok" if len(failed) == 0 else "failed",
            },
            "checks": [
                {
                    "check": r.check.value,
                    "passed": r.passed,
                    "message": r.message,
                }
                for r in results
            ],
            "recommendations": recommendations,
            "environment": environment,
        }


# AC_COMPLETE: AC-P90-S3-T1
