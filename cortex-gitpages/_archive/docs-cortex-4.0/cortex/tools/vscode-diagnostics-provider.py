"""
VS Code Governance Diagnostics Provider.

Provides real-time governance violation diagnostics in VS Code editor.
Displays violations inline as developers code, with quick-fix suggestions.

Features:
- Real-time diagnostics on file open/save
- Inline violation markers
- Quick-fix suggestions
- Severity levels (error, warning, info)
- Configurable severity thresholds
"""

import json
import logging
import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DiagnosticSeverity(Enum):
    """Diagnostic severity levels (VSCode compatible)."""

    ERROR = 0
    WARNING = 1
    INFORMATION = 2
    HINT = 3


class GovernanceDiagnostic:
    """Represents a single governance diagnostic."""

    def __init__(
        self,
        line: int,
        column: int,
        message: str,
        rule_id: str,
        severity: DiagnosticSeverity,
        fix_suggestion: Optional[str] = None,
    ):
        """
        Initialize a diagnostic.

        Args:
            line: Line number (0-indexed)
            column: Column number (0-indexed)
            message: Violation message
            rule_id: Governance rule ID (e.g., CORE-008)
            severity: Diagnostic severity
            fix_suggestion: Optional fix suggestion
        """
        self.line = line
        self.column = column
        self.message = message
        self.rule_id = rule_id
        self.severity = severity
        self.fix_suggestion = fix_suggestion

    def to_vscode_diagnostic(self) -> Dict[str, Any]:
        """
        Convert to VSCode diagnostic format.

        Returns:
            VSCode diagnostic dict
        """
        return {
            "range": {
                "start": {"line": self.line, "character": self.column},
                "end": {"line": self.line, "character": self.column + 1},
            },
            "message": f"[{self.rule_id}] {self.message}",
            "severity": self.severity.value,
            "source": "cortex-governance",
            "code": self.rule_id,
        }


class GovernanceDiagnosticsProvider:
    """
    Provides governance diagnostics for VS Code.

    Analyzes Python files and returns governance violations as diagnostics.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize diagnostics provider.

        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.cli_script = (
            Path(__file__).parent.parent / "src" / "tools" / "governance-cli.py"
        )

    def analyze_file(self, file_path: Path) -> List[GovernanceDiagnostic]:
        """
        Analyze a single file for governance violations.

        Args:
            file_path: Path to file to analyze

        Returns:
            List of diagnostics
        """
        diagnostics: List[GovernanceDiagnostic] = []

        if not file_path.exists():
            return diagnostics

        if file_path.suffix != ".py":
            return diagnostics

        try:
            # Run validation via CLI
            if self.cli_script.exists():
                result = subprocess.run(
                    ["python3", str(self.cli_script), "validate", str(file_path), "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.stdout.strip():
                    try:
                        data = json.loads(result.stdout)
                        violations = data.get("violations", [])
                        diagnostics = self._convert_violations_to_diagnostics(violations)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse validation JSON for {file_path}")

        except subprocess.TimeoutExpired:
            logger.warning(f"Validation timeout for {file_path}")
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")

        return diagnostics

    def _convert_violations_to_diagnostics(
        self, violations: List[Dict[str, Any]]
    ) -> List[GovernanceDiagnostic]:
        """
        Convert validation violations to diagnostics.

        Args:
            violations: List of violation dicts

        Returns:
            List of diagnostics
        """
        diagnostics = []

        for violation in violations:
            # Determine severity
            severity_str = violation.get("severity", "warning").lower()
            if severity_str == "blocked":
                severity = DiagnosticSeverity.ERROR
            elif severity_str == "warning":
                severity = DiagnosticSeverity.WARNING
            else:
                severity = DiagnosticSeverity.INFORMATION

            # Extract line number
            line = 0
            if "line" in violation:
                line = int(violation["line"]) - 1  # Convert to 0-indexed

            diagnostic = GovernanceDiagnostic(
                line=line,
                column=0,
                message=violation.get("message", "Governance violation"),
                rule_id=violation.get("rule_id", "UNKNOWN"),
                severity=severity,
                fix_suggestion=violation.get("fix_suggestion"),
            )

            diagnostics.append(diagnostic)

        return diagnostics


class VSCodeDiagnosticsServer:
    """
    Simple server that provides diagnostics to VS Code extensions.

    Listens for file analysis requests and returns diagnostics.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize diagnostics server.

        Args:
            workspace_root: Root directory of workspace
        """
        self.provider = GovernanceDiagnosticsProvider(workspace_root)
        self.diagnostics_cache: Dict[str, List[GovernanceDiagnostic]] = {}

    def get_diagnostics_for_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Get diagnostics for a specific file.

        Args:
            file_path: Path to file

        Returns:
            List of VSCode-compatible diagnostics
        """
        file_path_obj = Path(file_path)

        # Check cache
        if file_path in self.diagnostics_cache:
            diagnostics = self.diagnostics_cache[file_path]
        else:
            # Analyze file
            diagnostics = self.provider.analyze_file(file_path_obj)
            self.diagnostics_cache[file_path] = diagnostics

        return [d.to_vscode_diagnostic() for d in diagnostics]

    def clear_cache(self, file_path: Optional[str] = None) -> None:
        """
        Clear diagnostics cache.

        Args:
            file_path: Specific file to clear, or None for all files
        """
        if file_path:
            self.diagnostics_cache.pop(file_path, None)
        else:
            self.diagnostics_cache.clear()


def main() -> int:
    """
    Main entry point for diagnostics server.

    Accepts commands via stdin and outputs diagnostics via stdout.
    """
    server = VSCodeDiagnosticsServer()

    try:
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                command = request.get("command")

                if command == "analyze":
                    file_path = request.get("file")
                    diagnostics = server.get_diagnostics_for_file(file_path)
                    response = {
                        "command": "analyze",
                        "file": file_path,
                        "diagnostics": diagnostics,
                    }
                    print(json.dumps(response))

                elif command == "clear_cache":
                    file_path = request.get("file")
                    server.clear_cache(file_path)
                    response = {"command": "clear_cache", "status": "ok"}
                    print(json.dumps(response))

            except json.JSONDecodeError:
                logger.error("Failed to parse request")
            except Exception as e:
                logger.error(f"Error processing request: {e}")

    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
