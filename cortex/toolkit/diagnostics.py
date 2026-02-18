"""
MCP Diagnostics Module.

Consolidated MCP health checks and environment diagnostics.
Replaces scattered diagnostic scripts: verify-mcp-setup.py, diagnose-mcp.py, verify-mcp-tools.py

AC_START: AC-P90-S2-T1
"""

from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import subprocess


class DiagnosticLevel(str, Enum):
    """Diagnostic result severity levels."""
    
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check."""
    
    check_name: str
    passed: bool
    level: DiagnosticLevel
    message: str
    details: Optional[Dict[str, Any]] = None
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_name": self.check_name,
            "passed": self.passed,
            "level": self.level.value,
            "message": self.message,
            "details": self.details or {},
            "recommendation": self.recommendation,
        }


class MCPDiagnostics:
    """
    Consolidated MCP diagnostics.
    
    Provides comprehensive health checks for MCP server, tools,
    and VS Code integration.
    """
    
    def __init__(self, workspace_root: Path = Path.cwd()) -> None:
        """
        Initialize diagnostics.
        
        Args:
            workspace_root: CORTEX workspace root directory
        """
        self.workspace_root = workspace_root
    
    def check_server_running(self) -> DiagnosticResult:
        """
        Check if MCP server is running.
        
        Returns:
            Diagnostic result for server status
        """
        # Check for server process or connection
        # This is a simplified check - full implementation would use
        # actual MCP server health endpoint
        try:
            # Try to import MCP server module
            from cortex.mcp.server import MCPServer
            
            return DiagnosticResult(
                check_name="mcp_server_running",
                passed=True,
                level=DiagnosticLevel.OK,
                message="MCP server module available",
                details={"module": "cortex.mcp.server"},
            )
        except ImportError:
            return DiagnosticResult(
                check_name="mcp_server_running",
                passed=False,
                level=DiagnosticLevel.ERROR,
                message="MCP server module not found",
                recommendation="Run: python .cortex-runtime/setup-mcp.py",
            )
    
    def check_tools_available(self) -> DiagnosticResult:
        """
        Check if MCP tools are available.
        
        Returns:
            Diagnostic result for tools availability
        """
        try:
            from cortex.mcp.tools import TOOL_REGISTRY
            
            tool_count = len(TOOL_REGISTRY)
            
            if tool_count >= 10:
                return DiagnosticResult(
                    check_name="mcp_tools_available",
                    passed=True,
                    level=DiagnosticLevel.OK,
                    message=f"MCP tools available: {tool_count}",
                    details={"tool_count": tool_count},
                )
            else:
                return DiagnosticResult(
                    check_name="mcp_tools_available",
                    passed=False,
                    level=DiagnosticLevel.WARNING,
                    message=f"Limited tools: {tool_count} (expected 10+)",
                    details={"tool_count": tool_count},
                    recommendation="Check MCP tool registration",
                )
        except ImportError:
            return DiagnosticResult(
                check_name="mcp_tools_available",
                passed=False,
                level=DiagnosticLevel.ERROR,
                message="MCP tools module not found",
                recommendation="Run: python .cortex-runtime/setup-mcp.py",
            )
    
    def check_settings_configured(self) -> DiagnosticResult:
        """
        Check if .vscode/settings.json is configured.
        
        Returns:
            Diagnostic result for VS Code settings
        """
        settings_path = self.workspace_root / ".vscode" / "settings.json"
        
        if not settings_path.exists():
            return DiagnosticResult(
                check_name="settings_configured",
                passed=False,
                level=DiagnosticLevel.ERROR,
                message=".vscode/settings.json not found",
                recommendation="Run: python .cortex-runtime/setup-mcp.py",
            )
        
        try:
            with open(settings_path) as f:
                settings = json.load(f)
            
            # Check for MCP configuration
            if "mcp" in settings or "github.copilot" in settings:
                return DiagnosticResult(
                    check_name="settings_configured",
                    passed=True,
                    level=DiagnosticLevel.OK,
                    message="VS Code settings configured",
                    details={"path": str(settings_path)},
                )
            else:
                return DiagnosticResult(
                    check_name="settings_configured",
                    passed=False,
                    level=DiagnosticLevel.WARNING,
                    message="VS Code settings missing MCP config",
                    recommendation="Run: python .cortex-runtime/setup-mcp.py",
                )
        except json.JSONDecodeError:
            return DiagnosticResult(
                check_name="settings_configured",
                passed=False,
                level=DiagnosticLevel.ERROR,
                message="Invalid JSON in settings.json",
                recommendation="Fix JSON syntax or run setup-mcp.py",
            )
    
    def check_python_version(self) -> DiagnosticResult:
        """
        Check Python version compatibility.
        
        Returns:
            Diagnostic result for Python version
        """
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            version_str = result.stdout.strip()
            
            # Extract version number
            import re
            match = re.search(r"(\d+)\.(\d+)", version_str)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                
                if major >= 3 and minor >= 9:
                    return DiagnosticResult(
                        check_name="python_version",
                        passed=True,
                        level=DiagnosticLevel.OK,
                        message=f"Python version: {version_str}",
                        details={"version": version_str},
                    )
                else:
                    return DiagnosticResult(
                        check_name="python_version",
                        passed=False,
                        level=DiagnosticLevel.ERROR,
                        message=f"Python {major}.{minor} < 3.9 (required)",
                        recommendation="Upgrade to Python 3.9+",
                    )
            
            return DiagnosticResult(
                check_name="python_version",
                passed=False,
                level=DiagnosticLevel.WARNING,
                message="Could not parse Python version",
            )
            
        except Exception as e:
            return DiagnosticResult(
                check_name="python_version",
                passed=False,
                level=DiagnosticLevel.ERROR,
                message=f"Python check failed: {str(e)}",
            )
    
    def run_full_diagnostics(self) -> List[DiagnosticResult]:
        """
        Run full diagnostic suite.
        
        Returns:
            List of diagnostic results
        """
        return [
            self.check_python_version(),
            self.check_server_running(),
            self.check_tools_available(),
            self.check_settings_configured(),
        ]
    
    def generate_summary(
        self,
        results: List[DiagnosticResult]
    ) -> Dict[str, Any]:
        """
        Generate summary from diagnostic results.
        
        Args:
            results: List of diagnostic results
            
        Returns:
            Summary dictionary
        """
        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]
        warnings = [r for r in results if r.level == DiagnosticLevel.WARNING]
        errors = [r for r in results if r.level == DiagnosticLevel.ERROR]
        
        return {
            "total_checks": len(results),
            "passed_checks": len(passed),
            "failed_checks": len(failed),
            "warnings": len(warnings),
            "errors": len(errors),
            "overall_status": "ok" if len(failed) == 0 else "failed",
        }
    
    def generate_report(
        self,
        results: List[DiagnosticResult]
    ) -> Dict[str, Any]:
        """
        Generate full diagnostic report.
        
        Args:
            results: List of diagnostic results
            
        Returns:
            Complete report dictionary
        """
        summary = self.generate_summary(results)
        
        # Extract recommendations from failed checks
        recommendations = []
        for result in results:
            if not result.passed and result.recommendation:
                recommendations.append({
                    "check": result.check_name,
                    "recommendation": result.recommendation,
                })
        
        return {
            "summary": summary,
            "results": [r.to_dict() for r in results],
            "recommendations": recommendations,
        }


# AC_COMPLETE: AC-P90-S2-T1
