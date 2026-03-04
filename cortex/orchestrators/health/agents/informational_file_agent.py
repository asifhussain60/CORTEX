"""Informational File Drift Detection Agent

Detects straggling informational files (.md, .log, .txt, .json) outside
allowed directories. CORTEX should be YAML-heavy, not informational sprawl.

Authority: CORE-002 (No markdown sprawl), Phase 103 Enhancement
Author: CORTEX Framework
Created: 2026-02-17
"""

from pathlib import Path
from typing import List

from .base_agent import BaseHealthAgent, HealthCheckResult, HealthIssue, HealthIssueSeverity, HealthIssueCategory


class InformationalFileAgent(BaseHealthAgent):
    """Detects informational file drift (md/log/txt/json sprawl).

    Informational files should be:
    - YAML configurations in cortex-registry/
    - Documentation in cortex-docs/
    - Prompts in .github/prompts/
    - Root README.md only

    Everything else is drift/sprawl requiring cleanup.
    """

    def __init__(self) -> None:
        """Initialize informational file agent."""
        super().__init__(
            name="InformationalFileAgent",
            description="Detects straggling .md/.log/.txt/.json files",
        )

        # Informational file extensions to check
        self.extensions = {".md", ".log", ".txt"}

        # Allowed patterns (won't flag these)
        self.allowed_patterns = {
            ".github/prompts/",
            ".github/agents/",
            ".github/scripts/",
            "README.md",  # Root only
            "cortex-docs/",
            "cortex-registry/",
            "_workspaces/",  # EXCEPTION per request
            ".cortex-runtime/",
            "docs/",
            ".venv/",
            ".git/",
            "_archives/",  # Will be deleted separately
            ".archive/",   # Will be deleted separately
        }

        # Configuration files (allowed .txt extensions)
        self.config_files = {
            "requirements.txt",
            "pyproject.toml",
        }

    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run informational file drift detection.

        Args:
            workspace_root: Root path of workspace

        Returns:
            HealthCheckResult with detected drift issues
        """
        issues: List[HealthIssue] = []
        files_scanned = 0

        # Scan for informational files
        for ext in self.extensions:
            for file_path in workspace_root.rglob(f"*{ext}"):
                files_scanned += 1

                # Skip if in allowed directory
                if self._is_allowed(file_path, workspace_root):
                    continue

                # Skip configuration files
                if file_path.name in self.config_files:
                    continue

                # Flag as drift
                rel_path = file_path.relative_to(workspace_root)
                issues.append(HealthIssue(
                    category=HealthIssueCategory.PATH_DRIFT,
                    severity=HealthIssueSeverity.MEDIUM,
                    file_path=file_path,
                    description=(
                        f"File '{rel_path}' violates CORTEX YAML-heavy philosophy. "
                        f"Informational files should be in cortex-docs/, cortex-registry/, or .github/. "
                        f"Consider converting to YAML configuration or moving to documentation."
                    ),
                    suggested_fix="Move to cortex-docs/ or delete if obsolete",
                ))

        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=0.0,
        )

    def _is_allowed(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file is in allowed directory.

        Args:
            file_path: Path to file
            workspace_root: Workspace root

        Returns:
            True if allowed, False if drift
        """
        try:
            rel_path = str(file_path.relative_to(workspace_root))

            # Check against allowed patterns
            for pattern in self.allowed_patterns:
                if rel_path.startswith(pattern) or rel_path == pattern:
                    return True

            return False
        except ValueError:
            return False


__all__ = ["InformationalFileAgent"]
