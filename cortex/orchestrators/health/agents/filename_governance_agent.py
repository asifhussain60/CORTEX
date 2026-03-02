"""Filename Governance Agent

Detects CORE-028 violations: SCREAMING_CASE filenames that should use kebab-case.

Authority: CORE-028 (Intelligent File Naming)
Author: CORTEX Framework
Created: 2026-02-17
"""

import re
from pathlib import Path
from typing import List

from .base_agent import BaseHealthAgent, HealthCheckResult, HealthIssue, HealthIssueSeverity, HealthIssueCategory


class FilenameGovernanceAgent(BaseHealthAgent):
    """Detects filename governance violations (CORE-028).

    CORE-028 Rules:
    - Python: snake_case.py ✅
    - Scripts: kebab-case.py ✅
    - NO SCREAMING_CASE.py ❌
    - NO mixedCase.py ❌

    Exceptions:
    - __init__.py, __main__.py (stdlib convention)
    - README.md, LICENSE (universal convention)
    """

    def __init__(self) -> None:
        """Initialize filename governance agent."""
        super().__init__(
            name="FilenameGovernanceAgent",
            description="Detects CORE-028 violations (SCREAMING_CASE)",
        )

        # SCREAMING_CASE pattern (5+ uppercase with underscores)
        self.screaming_pattern = re.compile(r"^[A-Z_]{5,}\.py$")

        # Allowed exceptions (stdlib/universal conventions)
        self.exceptions = {
            "__init__.py",
            "__main__.py",
            "__pycache__",
            "README.md",
            "LICENSE",
            "Makefile",
        }

        # Excluded directories
        self.excluded_dirs = {
            ".venv",
            ".git",
            "_archives",
            ".archive",
            "node_modules",
        }

    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run filename governance check.

        Args:
            workspace_root: Root path of workspace

        Returns:
            HealthCheckResult with CORE-028 violations
        """
        issues: List[HealthIssue] = []
        files_scanned = 0

        # Scan all Python files
        for py_file in workspace_root.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in py_file.parts for excluded in self.excluded_dirs):
                continue

            files_scanned += 1

            # Skip exceptions
            if py_file.name in self.exceptions:
                continue

            # Check for SCREAMING_CASE
            if self.screaming_pattern.match(py_file.name):
                rel_path = py_file.relative_to(workspace_root)
                kebab_name = self._to_kebab_case(py_file.stem) + ".py"

                issues.append(HealthIssue(
                    category=HealthIssueCategory.CONFIGURATION,
                    severity=HealthIssueSeverity.HIGH,
                    file_path=py_file,
                    description=(
                        f"File '{rel_path}' uses SCREAMING_CASE which violates CORE-028. "
                        f"Python files should use snake_case or kebab-case. "
                        f"SCREAMING_CASE is reserved for constants within code, not filenames."
                    ),
                    suggested_fix=f"Rename to: {kebab_name}",
                ))

        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=0.0,
        )

    def _to_kebab_case(self, screaming_name: str) -> str:
        """Convert SCREAMING_CASE to kebab-case.

        Args:
            screaming_name: SCREAMING_CASE name

        Returns:
            kebab-case name
        """
        return screaming_name.lower().replace("_", "-")


__all__ = ["FilenameGovernanceAgent"]
